"""Cargador de music desde la API de Deezer (https://api.deezer.com), fetch → Data → process.

FLUJO «una fila por cosa» (paridad con Poseidon):
  artista   GET /artist/{id}           → DataDeezerArtist          (1 fila)
            GET /artist/{id}/albums    → la LISTA de ids de sus álbumes (todas las páginas; no se guarda:
                                          cada álbum queda en DataDeezerAlbum, que ya lleva su artista)
            y por cada álbum del listado:
  álbum     GET /album/{id}            → DataDeezerAlbum           (1 fila: ficha completa, con género, sello, colaboradores)
            GET /album/{id}/tracks     → DataDeezerTrack      (1 fila por pista, todas las páginas)
  género    GET /genre/{id}            → DataDeezerGenre
Deezer pagina de 25 en 25 con `next`: `_get_all` sigue todas las páginas. Entre llamadas se
espera un poco (límite de Deezer: 50 llamadas cada 5 s). El process crea Artist/Album/Song/Genre.
"""
import time

import requests

from apps.music.models import Album, AlbumType, Artist, ArtistImage, DataDeezerAlbum, DataDeezerArtist, DataDeezerGenre, DataDeezerTrack, Genre, MusicLog, Song
from core.shared.models.choices import LogLevel
from core.shared.tasks.cancel import cancelado
from core.shared.tasks.images import portada
from core.utils.importlog import log_to, sin_ruido


DEEZER = "https://api.deezer.com"
TIMEOUT = 20
MIN_INTERVAL = 0.12          # Deezer admite 50 llamadas cada 5 s: una cada 0,1 s; se deja margen
ALBUMES_EN_LINEA = 25        # álbumes que un artista trae EN LÍNEA; el resto va en tandas de este tamaño como tareas aparte
_last_call = {"t": 0.0}
_stats = {"peticiones": 0}   # peticiones HTTP hechas en este proceso (para medir: manage.py medir_import)

# Ids de Deezer que NO son géneros musicales (sondeo de GET /genre/{id}, 2026-09-10): «Todos», categorías de
# podcast (deportes, noticias, ciencia, true crime…), moods y actividades, audiolibros, selección editorial.
# Nunca se crean como Genre, vengan de /genre, de un álbum o de un artista.
DEEZER_NO_MUSICA = frozenset({
    0, 97, 210, 212, 214, 216, 218, 220, 222, 226, 228, 230, 232, 332, 370, 454, 456, 457, 462, 468, 474, 476,
    478, 480, 486, 537, 539, 541, 543, 552, 562, 572, 582, 592, 602, 612, 622, 632, 641, 651, 661, 681, 691,
})


def _wait():
    """Espera lo que falte para no pasar el límite de Deezer."""
    wait = MIN_INTERVAL - (time.monotonic() - _last_call["t"])
    if wait > 0:
        time.sleep(wait)
    _last_call["t"] = time.monotonic()


def log(code, process, message=""):
    """Escribe en MusicLog (log propio de música)."""
    return log_to(MusicLog, code, process, message)


def _get_url(url):
    """GET de una URL absoluta de Deezer → (status, payload|None). Un `error` en el JSON cuenta como None."""
    _wait()
    _stats["peticiones"] += 1
    try:
        r = requests.get(url, timeout=TIMEOUT)
        payload = r.json() if r.status_code == 200 else None
        if isinstance(payload, dict) and payload.get("error"):
            return r.status_code, None
        return r.status_code, payload
    except requests.RequestException as exc:
        log(LogLevel.ERROR, f"GET {url}", exc)
        return 0, None


def _get(path):
    return _get_url(f"{DEEZER}{path}")


def _get_all(path):
    """Listado PAGINADO (Deezer da 25 por página y un `next`): sigue todas las páginas y devuelve
    (status de la primera, todos los items). Sin esto, un artista con 36 álbumes se quedaba en 25."""
    url = f"{DEEZER}{path}"
    primero, items = 0, []
    while url:
        code, payload = _get_url(url)
        primero = primero or code
        if not payload:
            break
        items.extend(payload.get("data") or [])
        url = payload.get("next") or ""
    return primero, items


def _img(obj, url):
    """Descarga una imagen (jpg de Deezer) a obj.image. No pisa una ya subida."""
    from django.core.files.base import ContentFile
    if hasattr(obj, "images") and not hasattr(type(obj), "image"):      # Album: portada a su tabla (Poseidón)
        portada(obj, url)
        return
    if not url or (getattr(obj, "image", None) and obj.image.name):
        return
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200 and r.content:
            obj.image.save(f"{obj.slug or obj.deezer_id}.jpg", ContentFile(r.content), save=True)
        else:
            log(LogLevel.WARNING, f"img {obj}", f"HTTP {r.status_code}")
    except requests.RequestException as exc:
        log(LogLevel.WARNING, f"img {obj}", exc)


def _cat(model, name):
    name = (name or "").strip()
    if not name:
        return None
    obj, _ = model.objects.get_or_create(name=name[:100])
    return obj


# ----------------------------- GÉNERO -----------------------------
def fetch_genre(deezer_id):
    code, data = _get(f"/genre/{deezer_id}")
    ok = bool(data)
    row, _ = DataDeezerGenre.objects.update_or_create(
        deezer_id=deezer_id,
        defaults={"url": f"{DEEZER}/genre/{deezer_id}", "data": data,
                  "data_status": ok, "status_code": code})
    log(20 if ok else 40, f"fetch género #{deezer_id}", "OK" if ok else "sin datos")
    return row


def es_genero_musical(deezer_id):
    """False para «Todos» (0) y para las categorías de Deezer que no son música (podcasts, moods…)."""
    try:
        return int(deezer_id) not in DEEZER_NO_MUSICA
    except (TypeError, ValueError):
        return False


def process_genre(deezer_id):
    if not es_genero_musical(deezer_id):
        return None
    row = DataDeezerGenre.objects.filter(deezer_id=deezer_id, data_status=True).first()
    if not row:
        return None
    d = row.data or {}
    nombre = (d.get("name") or f"Género {deezer_id}")[:100]
    genre = Genre.objects.filter(deezer_id=deezer_id).first()
    if genre is None:
        # sin id: casa por nombre (Deezer responde en el idioma de la IP: «African Music» o «Música Africana»)
        from django.db.models import Q
        genre = Genre.objects.filter(Q(name__iexact=nombre) | Q(name_esp__iexact=nombre), deezer_id__isnull=True).first()
        if genre is not None:
            genre.deezer_id = deezer_id
            genre.save(update_fields=["deezer_id"])
        else:
            genre = Genre.objects.create(deezer_id=deezer_id, name=nombre)
            log(LogLevel.WARNING, f"género nuevo #{deezer_id}", f"«{nombre}» no estaba en el seed: revisa si es música y dale nombre en español")
    _img(genre, d.get("picture_xl") or d.get("picture_big") or d.get("picture_medium"))   # imagen del género
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    return genre


def _genre(deezer_id):
    """Devuelve el Genre real; si falta, lo trae y procesa on-demand. None si no es música."""
    if not es_genero_musical(deezer_id):
        return None
    genre = Genre.objects.filter(deezer_id=deezer_id).first()
    if genre:
        return genre
    fetch_genre(deezer_id)
    return process_genre(deezer_id)


# ----------------------------- ARTISTA (+ álbumes + pistas) -----------------------------
# ----------------------------- ÁLBUM (individual) -----------------------------
def _imagen_artista(artist, a):
    """La foto del artista entra como una imagen MÁS (ArtistImage, con la URL de picture_xl), detrás de las que ya
    tenga: no pisa ni mueve nada. El descargador la baja después (o la acción «Imagen desde Deezer»). Si esa URL
    ya está, no hace nada. Devuelve la fila nueva o None."""
    url = a.get("picture_xl") or a.get("picture_big") or a.get("picture_medium") or ""
    if not url or artist.images.filter(image_url=url).exists():
        return None
    return ArtistImage.objects.create(artist=artist, image_url=url)


def imagenes_desde_deezer(model_name, ids):
    """«Imagen desde Deezer» para filas marcadas de Género o Artista: usa el JSON ya descargado
    (Data*) y baja la imagen ahora. Devuelve cuántas quedaron con imagen."""
    from core.shared.tasks.images import descargar_fila
    hechas = 0
    if model_name == "genre":
        for g in Genre.objects.filter(pk__in=ids, deezer_id__isnull=False):
            row = DataDeezerGenre.objects.filter(deezer_id=g.deezer_id, data_status=True).first()
            d = (row.data if row else None) or {}
            _img(g, d.get("picture_xl") or d.get("picture_big") or d.get("picture_medium"))
            hechas += int(bool(g.image and g.image.name))
    elif model_name == "artist":
        for ar in Artist.objects.filter(pk__in=ids, deezer_id__isnull=False):
            row = DataDeezerArtist.objects.filter(deezer_id=ar.deezer_id, data_status=True).first()
            _imagen_artista(ar, (row.data if row else None) or {})
            for fila in ar.images.filter(image_downloaded=False).exclude(image_url=""):
                ok, _det = descargar_fila(fila)
            hechas += int(ar.images.filter(image_downloaded=True).exists())
    return hechas


# ----------------------------- ARTISTA -----------------------------
# Cadena completa: artista → TODOS sus álbumes (listado paginado) → ficha de cada álbum → sus pistas.
# Cada cosa en su tabla: DataDeezerArtist, DataDeezerAlbum, DataDeezerTrack.
def fetch_artist(deezer_id, en_linea=None):
    """Artista + listado de álbumes + ficha de cada álbum. Con `en_linea` = N, solo los primeros N álbumes se
    traen aquí; los demás quedan en `row.albumes_pendientes` para que `import_artist` los reparta en tandas."""
    code, artist = _get(f"/artist/{deezer_id}")
    if not artist:
        DataDeezerArtist.objects.update_or_create(
            deezer_id=deezer_id,
            defaults={"url": f"{DEEZER}/artist/{deezer_id}", "data": None,
                      "data_status": False, "status_code": code})
        log(LogLevel.WARNING, f"fetch artista #{deezer_id}", "sin datos")
        return None
    row, _ = DataDeezerArtist.objects.update_or_create(
        deezer_id=deezer_id,
        defaults={"url": f"{DEEZER}/artist/{deezer_id}", "data": artist,
                  "data_status": True, "status_code": code})
    albums = _get_all(f"/artist/{deezer_id}/albums")[1]
    # El listado solo da los IDS: el resumen que trae es un subconjunto de la ficha, y esa ficha
    # (DataDeezerAlbum, con su `deezer_id_artist`) es la que se guarda.
    ids = [album.get("id") for album in albums if album.get("id")]
    ahora, despues = (ids, []) if en_linea is None else (ids[:en_linea], ids[en_linea:])
    for album_id in ahora:                    # las FICHAS (álbum + pistas): lo caro
        if cancelado():                       # el usuario pidió cancelar desde el panel
            log(LogLevel.WARNING, "cancelada", "detenida por el usuario entre pasos; lo ya guardado se queda")
            break
        fetch_album(album_id, deezer_id_artist=deezer_id)
    row.albumes_pendientes = despues
    log(LogLevel.INFO, f"fetch artista #{deezer_id}", f"{artist.get('name')}: {len(ids)} álbumes (nb_album={artist.get('nb_album')}); "
                                           f"{len(ahora)} en línea, {len(despues)} en tandas aparte")
    return row


WIKIPEDIA = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{titulo}"


def biografia_wikipedia(nombre):
    """Resumen de Wikipedia del artista (español y, si no hay, inglés): la API de Deezer NO trae biografía
    (solo nombre, fotos y conteos), así que se completa desde aquí. "" si no hay artículo."""
    for lang in ("es", "en"):
        try:
            r = requests.get(WIKIPEDIA.format(lang=lang, titulo=requests.utils.quote(nombre.replace(" ", "_"))),
                             timeout=TIMEOUT, headers={"User-Agent": "Frikiverso/1.0 (importador de música)"})
            _stats["peticiones"] += 1
            if r.status_code == 200 and r.json().get("type") == "standard":
                texto = (r.json().get("extract") or "").strip()
                if texto:
                    return texto
        except requests.RequestException:
            continue
    return ""


def process_artist(deezer_id):
    row = DataDeezerArtist.objects.filter(deezer_id=deezer_id, data_status=True).first()
    if not row:
        return None
    a = row.data or {}
    artist, _ = Artist.objects.update_or_create(deezer_id=deezer_id, defaults={
        "name": (a.get("name") or f"Artista {deezer_id}")[:150]})
    _imagen_artista(artist, a)   # deja la URL de la foto; la baja el descargador (o «Imagen desde Deezer»)
    if not (artist.biography or "").strip():   # Deezer no la trae: Wikipedia (es → en)
        bio = biografia_wikipedia(artist.name)
        if bio:
            artist.biography = bio
            artist.save(update_fields=["biography"])
    listado = DataDeezerAlbum.objects.filter(deezer_id_artist=deezer_id, data_status=True)
    hechos = 0
    for fila in listado:
        if _process_album(fila.deezer_id, artist) is not None:
            hechos += 1
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    log(LogLevel.INFO, f"process artista #{deezer_id}", f"{artist.name}: {hechos}/{listado.count()} álbumes")
    return artist


# ----------------------------- ÁLBUM -----------------------------
def fetch_album(deezer_id, deezer_id_artist=None):
    """Ficha completa del álbum + TODAS sus pistas (paginadas), cada pista en su fila."""
    code, album = _get(f"/album/{deezer_id}")
    if not album:
        DataDeezerAlbum.objects.update_or_create(deezer_id=deezer_id, defaults={
            "url": f"{DEEZER}/album/{deezer_id}", "data": None, "deezer_id_artist": deezer_id_artist,
            "data_status": False, "status_code": code})
        log(LogLevel.WARNING, f"fetch álbum #{deezer_id}", "sin datos")
        return None
    artist_id = (album.get("artist") or {}).get("id") or deezer_id_artist
    row, _ = DataDeezerAlbum.objects.update_or_create(deezer_id=deezer_id, defaults={
        "url": f"{DEEZER}/album/{deezer_id}", "deezer_id_artist": artist_id,
        "data": album, "data_status": True, "status_code": code})
    code_t, tracks = _get_all(f"/album/{deezer_id}/tracks")
    for track in tracks:
        tid = track.get("id")
        if not tid:
            continue
        DataDeezerTrack.objects.update_or_create(deezer_id=tid, defaults={
            "url": f"{DEEZER}/album/{deezer_id}/tracks", "deezer_id_album": deezer_id,
            "data": track, "data_status": True, "status_code": code_t})
    log(LogLevel.INFO, f"fetch álbum #{deezer_id}", f"{album.get('title')}: {len(tracks)} pistas (nb_tracks={album.get('nb_tracks')})")
    return row


def _process_album(album_id, artist):
    """Álbum real desde su ficha (DataDeezerAlbum) y canciones desde sus pistas (DataDeezerTrack)."""
    if not album_id:
        return None
    row = DataDeezerAlbum.objects.filter(deezer_id=album_id, data_status=True).first()
    if not row:
        return None
    a = row.data or {}
    album, _ = Album.objects.update_or_create(deezer_id=album_id, defaults={
        "title": (a.get("title") or f"Álbum {album_id}")[:255],
        "artist": artist,
        "album_type": _cat(AlbumType, a.get("record_type")),
        "release_date": a.get("release_date") or None,
    })
    _img(album, a.get("cover_xl") or a.get("cover_big"))   # portada del álbum
    ids_genero = [g.get("id") for g in ((a.get("genres") or {}).get("data") or []) if g.get("id")]
    if not ids_genero and a.get("genre_id") not in (None, -1):
        ids_genero = [a.get("genre_id")]
    for gid in ids_genero:
        genre = _genre(gid)
        if genre:
            album.genres.add(genre)
            artist.genres.add(genre)
    anio = int(a["release_date"][:4]) if (a.get("release_date") or "")[:4].isdigit() else None
    pistas = DataDeezerTrack.objects.filter(deezer_id_album=album_id, data_status=True)
    for fila in pistas:
        t = fila.data or {}
        Song.objects.update_or_create(deezer_id=fila.deezer_id, defaults={
            "album": album,
            "album_song_id": t.get("track_position") or 0,
            "title": (t.get("title") or f"Pista {fila.deezer_id}")[:500],
            "title_short": (t.get("title_short") or "")[:255],
            "title_version": (t.get("title_version") or "")[:255],
            "release_year": anio,
        })
        fila.data_processed = True
        fila.save(update_fields=["data_processed"])
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    log(LogLevel.INFO, f"process álbum #{album_id}", f"{album.title}: {pistas.count()} canciones")
    return album


def process_album(deezer_id):
    row = DataDeezerAlbum.objects.filter(deezer_id=deezer_id, data_status=True).first()
    if not row:
        return None
    art = ((row.data or {}).get("artist") or {})
    art_id = art.get("id") or row.deezer_id_artist
    if not art_id:
        log(LogLevel.WARNING, f"process álbum #{deezer_id}", "sin artista, no se puede crear")
        return None
    artist, _ = Artist.objects.get_or_create(
        deezer_id=art_id, defaults={"name": (art.get("name") or f"Artista {art_id}")[:150]})
    return _process_album(deezer_id, artist)


# ----------------------------- BÚSQUEDA por nombre (solo lectura) -----------------------------
# Para importar «ONE OK ROCK» sin saber su id: GET /search/artist?q=… devuelve candidatos y el
# usuario elige cuál cargar. No escribe nada en la BD.
def _buscar(tipo, query, tope=300):
    """TODOS los candidatos de una búsqueda, siguiendo la paginación de Deezer (`next`), hasta `tope`."""
    query = (query or "").strip()
    if not query:
        return []
    from urllib.parse import quote
    filas, index, por_pagina = [], 0, 100
    while len(filas) < tope:
        _code, payload = _get(f"/search/{tipo}?q={quote(query)}&limit={por_pagina}&index={index}")
        lote = (payload or {}).get("data") or []
        filas.extend(lote)
        if not (payload or {}).get("next") or not lote:
            break
        index += por_pagina
    return filas[:tope]


def _miles(n):
    return f"{int(n or 0):,}".replace(",", ".")


def buscar_artistas(query):
    """TODOS los candidatos de artista por nombre: id, nombre, foto, nº de álbumes y fans, y si ya está descargado."""
    ya = set(DataDeezerArtist.objects.filter(data_status=True).values_list("deezer_id", flat=True))
    return [{
        "id": a.get("id"), "titulo": a.get("name") or "", "imagen": a.get("picture_medium") or a.get("picture") or "",
        "sub": f"{a.get('nb_album', 0)} álbumes · {_miles(a.get('nb_fan'))} fans",
        "link": a.get("link") or "", "ya": a.get("id") in ya,
    } for a in _buscar("artist", query)]


def buscar_albumes(query):
    """TODOS los candidatos de ÁLBUM por nombre. Admite los filtros de Deezer dentro de la consulta:
    `artist:"ONE OK ROCK" album:"Ambitions"` da el álbum exacto de ese artista."""
    ya = set(DataDeezerAlbum.objects.filter(data_status=True).values_list("deezer_id", flat=True))
    return [{
        "id": a.get("id"), "titulo": a.get("title") or "", "imagen": a.get("cover_medium") or a.get("cover") or "",
        "sub": " · ".join(x for x in ((a.get("artist") or {}).get("name") or "",
                                       f"{a.get('nb_tracks', 0)} pistas", a.get("record_type") or "") if x),
        "link": a.get("link") or "", "ya": a.get("id") in ya,
    } for a in _buscar("album", query)]


def buscar_canciones(query):
    """Candidatos de CANCIÓN por nombre. Una canción no se importa sola: vive dentro de su álbum, así que el
    `id` de cada candidato es el de su ÁLBUM. Marcar una canción trae el álbum entero (con su artista y todas
    sus pistas); dos canciones del mismo álbum son el mismo id y se importan una vez.
    OJO: en canciones Deezer NO acepta el filtro `artist:"…" track:"…"` (devuelve 0); se afina con palabras
    sueltas, «Nirvana Lithium». En álbumes el filtro sí funciona."""
    ya = set(DataDeezerAlbum.objects.filter(data_status=True).values_list("deezer_id", flat=True))
    filas = []
    for t in _buscar("track", query):
        album = t.get("album") or {}
        if not album.get("id"):
            continue
        filas.append({
            "id": album.get("id"), "titulo": t.get("title") or "",
            "imagen": album.get("cover_medium") or album.get("cover") or "",
            "sub": " · ".join(x for x in ((t.get("artist") or {}).get("name") or "",
                                           f"álbum «{album.get('title') or ''}»") if x),
            "link": t.get("link") or "", "ya": album.get("id") in ya,
        })
    return filas


def fetch_all_genres():
    """GET /genre trae los géneros principales de Deezer con id, nombre e imagen: una fila por género.
    El id 0 («Todos» / «All») NO es un género, es el comodín de la API: se descarta."""
    code, payload = _get("/genre")
    generos = [g for g in ((payload or {}).get("data") or []) if g.get("id") is not None and es_genero_musical(g.get("id"))]
    for g in generos:
        gid = g.get("id")
        DataDeezerGenre.objects.update_or_create(deezer_id=gid, defaults={
            "url": f"{DEEZER}/genre/{gid}", "data": g, "data_status": True, "status_code": code})
    log(20 if generos else 40, "fetch géneros", f"{len(generos)} géneros" if generos else "sin datos")
    return generos


def import_all_genres():
    def _todo():
        ids = [g.get("id") for g in fetch_all_genres() if g.get("id") is not None]
        return sum(1 for gid in ids if process_genre(gid) is not None)
    return _sin_ruido("import géneros", _todo)


# ----------------------------- conveniencia -----------------------------
def _sin_ruido(proceso, fn, *args):
    """Si la importación termina sin avisos, se lleva por delante sus líneas informativas (el helper común)."""
    return sin_ruido(MusicLog, proceso, fn, *args, peticiones=lambda: _stats["peticiones"])


def import_artist(deezer_id, en_linea=ALBUMES_EN_LINEA):
    """Artista completo. Los primeros `en_linea` álbumes se traen y procesan aquí; los demás se reparten en
    tandas de `en_linea` como tareas aparte (`import_artist_albums_task`), así un artista con 700 álbumes no
    frena el lote y otro proceso del worker avanza con sus tandas en paralelo."""
    def _todo():
        row = fetch_artist(deezer_id, en_linea=en_linea)
        artist = process_artist(deezer_id)
        pendientes = list(getattr(row, "albumes_pendientes", None) or [])
        if artist is not None and pendientes:
            from apps.music.tasks import import_artist_albums_task
            tandas = [pendientes[i:i + en_linea] for i in range(0, len(pendientes), en_linea)]
            for tanda in tandas:
                import_artist_albums_task.delay(deezer_id, tanda)
            log(LogLevel.INFO, f"import artista #{deezer_id}", f"{len(pendientes)} álbumes en {len(tandas)} tandas aparte")
        return artist
    return _sin_ruido(f"import artista #{deezer_id}", _todo)


def import_artist_albums(deezer_id_artist, album_ids):
    """UNA tanda de álbumes de un artista ya importado: ficha + pistas de cada uno y su proceso.
    Devuelve cuántos quedaron hechos."""
    def _todo():
        artist = Artist.objects.filter(deezer_id=deezer_id_artist).first()
        if artist is None:
            log(LogLevel.WARNING, f"tanda de álbumes #{deezer_id_artist}", "el artista no está importado")
            return 0
        hechos = 0
        for album_id in album_ids:
            if cancelado():
                log(LogLevel.WARNING, "cancelada", "detenida por el usuario entre álbumes; lo ya guardado se queda")
                break
            fetch_album(album_id, deezer_id_artist=deezer_id_artist)
            if _process_album(album_id, artist) is not None:
                hechos += 1
        return hechos
    return _sin_ruido(f"tanda de álbumes de artista #{deezer_id_artist} ({len(album_ids)})", _todo)


def import_album(deezer_id):
    def _todo():
        fetch_album(deezer_id)
        return process_album(deezer_id)
    return _sin_ruido(f"import álbum #{deezer_id}", _todo)


def import_track(deezer_id):
    """Una CANCIÓN por su id: Deezer no la guarda suelta en nuestras tablas (vive en su álbum), así que se lee
    `/track/{id}` solo para saber de qué álbum es, y se importa ese álbum entero con su artista."""
    def _todo():
        code, pista = _get(f"/track/{deezer_id}")
        album_id = ((pista or {}).get("album") or {}).get("id")
        if not album_id:
            log(LogLevel.WARNING, f"import canción #{deezer_id}", f"sin álbum (HTTP {code}): no existe o Deezer no la da")
            return None
        return import_album(album_id)
    return _sin_ruido(f"import canción #{deezer_id}", _todo)


def import_genre(deezer_id):
    def _todo():
        fetch_genre(deezer_id)
        return process_genre(deezer_id)
    return _sin_ruido(f"import género #{deezer_id}", _todo)


# ----------------------------- Post-procesador (music) -----------------------------
def process_pending(limit_per_model=None):
    """Procesa el crudo pendiente de música: género → artista (con sus álbumes y pistas) → álbumes
    sueltos (importados sin artista). Las pistas se procesan con su álbum."""
    total = 0
    for model, fn in ((DataDeezerGenre, process_genre), (DataDeezerArtist, process_artist),
                      (DataDeezerAlbum, process_album)):
        ids = list(model.objects.filter(data_status=True, data_processed=False)
                   .values_list("deezer_id", flat=True)[: limit_per_model or None])
        ok = 0
        for did in ids:
            try:
                if fn(did) is not None:
                    ok += 1
            except Exception as exc:  # noqa: BLE001
                log(LogLevel.ERROR, f"postprocess {model.__name__} #{did}", exc)
        total += ok
        if ids:
            log(LogLevel.INFO, f"postprocess {model.__name__}", f"{ok}/{len(ids)}")
    return total

# ----------------------------- Importación masiva (rango) -----------------------------
_BULK = {"artista": import_artist, "album": import_album, "cancion": import_track, "genero": import_genre}


def _tarea_de(kind):
    """La tarea Celery de UN elemento del tipo (artista / álbum / género)."""
    from apps.music import tasks
    return {"artista": tasks.import_artist_task, "album": tasks.import_album_task,
            "cancion": tasks.import_track_task, "genero": tasks.import_genre_task}.get(kind)


def encolar_ids(kind, ids, etiqueta):
    """LOTE = una tarea por id. Deezer limita por ventana de 5 s y no por día, así que los procesos del
    worker (2) importan artistas distintos A LA VEZ, cada uno con su propia espera; un lote de 1.000 artistas
    se reparte solo, se cancela artista por artista y ninguno espera a Mozart. Sin broker, cada `.delay`
    corre en el acto, uno tras otro. Devuelve cuántos se encolaron."""
    tarea = _tarea_de(kind)
    ids = [i for i in ids if i]
    if tarea is None or not ids:
        return 0
    encolados = 0
    for i in ids:
        if cancelado():                       # el usuario canceló el lote antes de repartirlo entero
            log(LogLevel.WARNING, "cancelada", f"lote detenido por el usuario: {encolados}/{len(ids)} encolados")
            break
        try:
            tarea.delay(i)
            encolados += 1
        except Exception as exc:  # noqa: BLE001
            log(LogLevel.ERROR, f"{etiqueta} #{i}", exc)
    log(LogLevel.INFO, etiqueta, f"{encolados}/{len(ids)} {kind}(s) encolados, uno por tarea")
    return encolados


def import_range(kind, start, end):
    """Rango de ids [start, end]: una tarea por id (ver `encolar_ids`)."""
    if _tarea_de(kind) is None:
        return 0
    return encolar_ids(kind, range(start, end + 1), f"bulk {kind} [{start}-{end}]")


def import_ids(kind, ids):
    """Lista de ids (cargada desde CSV / Excel / SQLite): una tarea por id (ver `encolar_ids`)."""
    if _tarea_de(kind) is None or not ids:
        return 0
    return encolar_ids(kind, list(ids), f"archivo {kind} ({len(ids)} ids)")

