"""
Cargador de juegos desde la API de VNDB (https://api.vndb.org/kana), fetch → Data → process.

VNDB usa POST con {filters, fields, page, results} y pagina con `more`. Ids con prefijo:
'v' = visual novel, 'p' = producer, 'r' = release, 'c' = character. Aquí todo va keyed por el
número (vndb_id, sin prefijo).

CADENA de un juego (como Deezer con el artista): fetch_game(id)
  POST /vn        (id = v<id>)        → DataVndbGame       (1 fila: la VN)
  POST /release   (vn = [id = v<id>]) → DataVndbRelease    (1 fila por lanzamiento, TODAS las páginas)
  POST /character (vn = [id = v<id>]) → DataVndbCharacter  (1 fila por personaje, todas las páginas)
  POST /producer  (vn = [id = v<id>]) → DataVndbCharacter  (1 fila por personaje, todas las páginas)
process_game(id): DataVndbGame → Game (portada, idiomas, plataformas, desarrolladores) y sus
lanzamientos suman plataformas, idiomas, editoras (productores con `publisher`) y la fecha más
antigua; los personajes pasan a Character (con rol por juego e imagen por URL).
Sueltos: import_character (c<id>) e import_release (r<id>) traen su juego si falta: no viven sin él.
Creator: fetch_creator/process_creator (POST /producer). Si a un juego le falta un desarrollador o
una editora, se trae ENTERO por su id (nada de stubs a medias).

Límite de VNDB: 200 peticiones cada 5 minutos, de una en una → `_wait` deja ~1 s entre llamadas.
"""
import datetime
import time

import requests
from django.db.models import Exists, OuterRef, Q

from apps.catalogs.models import Language
from apps.games.models import Character, CharacterImage, CharacterRole, Creator, CreatorLink, CreatorNickname, DataVndbCharacter, DataVndbCreator, DataVndbGame, DataVndbRelease, Game, GameImage, GameLog, Genre, Platform, Release, ReleaseImage, Tag
from core.shared.models.choices import CreatorType, GameStatus, GameType, LogLevel
from core.shared.tasks.cancel import cancelado
from core.shared.tasks.images import fila_imagen
from core.utils.importlog import log_to, sin_ruido


"""

  ┌───────────┬────────────────────────────────────────────────────┬────────────────────────────────────────────────┐
  │ Categoría │                     Qué agrupa                     │                    Ejemplos                    │
  ├───────────┼────────────────────────────────────────────────────┼────────────────────────────────────────────────┤
  │ cont      │ contenido: género, ambientación, temas, personajes │ Comedy, Fantasy, School Life, Male Protagonist │
  ├───────────┼────────────────────────────────────────────────────┼────────────────────────────────────────────────┤
  │ ero       │ contenido sexual                                   │ los tags de escenas y fetiches                 │
  ├───────────┼────────────────────────────────────────────────────┼────────────────────────────────────────────────┤
  │ tech      │ técnico: formato y mecánicas                       │ ADV, NVL, Multiple Endings, Voiced             │
  └───────────┴────────────────────────────────────────────────────┴────────────────────────────────────────────────┘


 devstatus en /vn tiene tres valores numéricos:
  ┌───────┬────────────────┬────────────────────────────────────────────────────────────────────────────────────┐
  │ Valor │     Estado     │                                    Significado                                     │
  ├───────┼────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
  │ 0     │ Finished       │ terminada: la novela está completa y publicada                                     │
  ├───────┼────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
  │ 1     │ In development │ en desarrollo: hay lanzamientos parciales o demos, la versión completa aún no sale │
  ├───────┼────────────────┼────────────────────────────────────────────────────────────────────────────────────┤
  │ 2     │ Cancelled      │ cancelada: el desarrollo se abandonó                                               │
  └───────┴────────────────┴────────────────────────────────────────────────────────────────────────────────────┘
"""


VNDB = "https://api.vndb.org/kana"
TIMEOUT = 120
MIN_INTERVAL = 2.0           # espera entre peticiones SUELTAS (un juego, un creador…): el límite de 200 / 5 min es una
                             # cada 1,5 s; 2,5 deja aire.
ESPERA_BARRIDO = 20.0        # espera entre PÁGINAS del barrido. Aquí el límite no es la cantidad sino el tiempo de
                             # ejecución de VNDB ("Throttled on query execution time"): solo nos deja gastar ~6 % del
                             # reloj, así que la espera es coste_de_la_página / 0,06. Medido el 2026-09-13: una página
                             # de juegos con la consulta recortada costaba 0,7 s (→ 12 s); con VN_FIELDS completo
                             # (staff, va, editions, extlinks de developers…) cuesta bastante más, de ahí los 30 s.
                             # Perilla: la línea de log de cada página dice cuánto tardó; divide ese número por 0,06
                             # y ese es el valor. Si aparecen 429 en el barrido, subir; si va limpio de sobra, bajar.
POR_PAGINA = 100             # máximo que admite `results`
REINTENTOS = 4               # 429 / 5xx / caída de red: se reintenta con espera creciente en vez de abandonar la tanda
ESPERA_REINTENTO = 30        # segundos de la 1ª espera (luego 60, 120): un 429 necesita que se rellene la ventana de
                             # 5 min, no basta con 10 s. Un Retry-After de VNDB manda sobre esto.
_stats = {"peticiones": 0}   # peticiones HTTP hechas en este proceso (para medir: manage.py medir_import)
_last_call = {"t": 0.0, "coste": 0.0}   # cuándo fue la última petición y cuánto tardó (solo para el log)


# VN_FIELDS = "id, title, alttitle, aliases, olang, devstatus, released, languages, platforms, description, titles.lang, titles.title, titles.latin, titles.official, titles.main, image.url, image.sexual, image.violence, screenshots.url, screenshots.sexual, screenshots.violence, developers.id, developers.name, relations.id,  relations.relation, relations.relation_official, tags.category, tags.id, tags.name, va.character.id, va.character.name, extlinks.id, extlinks.url, extlinks.label, extlinks.name"
VN_FIELDS = "id, title, alttitle, aliases, olang, devstatus, released, languages, platforms, description, titles.lang, titles.title, titles.latin, titles.official, titles.main, image.id, image.url, image.sexual, image.violence, screenshots.id, screenshots.url, screenshots.sexual, screenshots.violence, screenshots.release.id, screenshots.release.title, developers.id, developers.name, developers.original, developers.aliases, developers.type, developers.lang, developers.description, developers.extlinks.id, developers.extlinks.url, developers.extlinks.label, developers.extlinks.name, relations.id, relations.title, relations.released, relations.relation, relations.relation_official, tags.category, tags.id, tags.name, tags.rating, tags.spoiler, staff.id, staff.name, staff.original, staff.lang, staff.role, staff.note, staff.eid, va.staff.id, va.staff.name, va.staff.original, va.character.id, va.character.name, editions.eid, editions.lang, editions.name, editions.official, extlinks.id, extlinks.url, extlinks.label, extlinks.name"
PRODUCER_FIELDS = "id, name, original, type, lang, description, aliases, extlinks.url, extlinks.label, extlinks.name, extlinks.id"
RELEASE_FIELDS = "id, title, alttitle, released, languages.lang, languages.title, languages.latin, languages.mtl, languages.main, platforms, media.medium, vns.id, vns.rtype, producers.id, producers.name,producers.developer, producers.publisher, images.id, images.type, images.vn, images.languages, images.url, images.sexual, images.violence, minage, patch, official, freeware, uncensored, has_ero,engine, voiced, extlinks.id, extlinks.url, extlinks.label, extlinks.name"
CHARACTER_FIELDS = "id, name, original, description, aliases, sex, gender, age, birthday, blood_type, image.url, image.sexual, image.violence, vns.id, vns.role, vns.spoiler, vns.release.id"


def log(code, process, message=""):
    """Escribe en GameLog (log propio de juegos)."""
    return log_to(GameLog, code, process, message)


def _wait(intervalo=MIN_INTERVAL):
    """Deja pasar `intervalo` segundos desde la petición anterior antes de la siguiente."""
    wait = intervalo - (time.monotonic() - _last_call["t"])
    if wait > 0:
        time.sleep(wait)
    _last_call["t"] = time.monotonic()


# ----------------------------- transporte -----------------------------
def _post(endpoint, filters, fields, page=1, results=POR_PAGINA, sort=None, espera=MIN_INTERVAL):
    """POST a un endpoint de consulta → (status, payload | None). payload = {results, more}.
    Sin `filters` (lista vacía) trae el catálogo entero paginado; `sort` ordena (el barrido usa "id").
    `espera`: segundos desde la petición anterior (el barrido pasa ESPERA_BARRIDO)."""
    cuerpo = {"filters": filters, "fields": fields, "page": page, "results": results}
    if sort:
        cuerpo["sort"] = sort
    espera = ESPERA_REINTENTO
    for intento in range(1, REINTENTOS + 1):
        _wait(espera)
        _stats["peticiones"] += 1
        try:
            r = requests.post(f"{VNDB}/{endpoint}", timeout=TIMEOUT, json=cuerpo)
            _last_call["coste"] = r.elapsed.total_seconds()      # lo que tardó VNDB (sale en el log del barrido)
            if r.status_code == 200:
                return 200, (r.json() or {})
            # 429 (pasamos el presupuesto de VNDB) y 5xx: NO es fin de catálogo, es esperar y repetir
            if r.status_code == 429 or r.status_code >= 500:
                if intento == REINTENTOS:
                    log(LogLevel.WARNING, _quien(endpoint, page, cuerpo), f"HTTP {r.status_code} tras {REINTENTOS} intentos · {_respuesta(r)}")
                    return r.status_code, None
                pausa = _retry_after(r) or espera
                # 40 = Advertencia (esta escala NO es la de Python: 30 es Éxito)
                log(LogLevel.WARNING, _quien(endpoint, page, cuerpo), f"HTTP {r.status_code}; reintento {intento}/{REINTENTOS - 1} en {pausa:.0f} s · {_respuesta(r)}")
                time.sleep(pausa)
                espera *= 2
                continue
            log(LogLevel.WARNING, _quien(endpoint, page, cuerpo), f"HTTP {r.status_code} · {_respuesta(r)}")   # 4xx de verdad: no se reintenta
            return r.status_code, None
        except requests.RequestException as exc:
            if intento == REINTENTOS:
                log(LogLevel.ERROR, _quien(endpoint, page, cuerpo), f"{type(exc).__name__}: {exc} (tras {REINTENTOS} intentos)")
                return 0, None
            log(LogLevel.WARNING, _quien(endpoint, page, cuerpo), f"{type(exc).__name__}: {exc}; reintento {intento}/{REINTENTOS - 1} en {espera} s")
            time.sleep(espera)
            espera *= 2
    return 0, None


def _retry_after(respuesta):
    """Segundos que pide la cabecera `Retry-After` (si viene y es un número), o None."""
    try:
        return max(1.0, float(respuesta.headers.get("Retry-After", "")))
    except (TypeError, ValueError):
        return None


# cabeceras que VNDB usa para contar lo que nos queda de presupuesto; si algún día cambian, se ven igual en `otras`
_CABECERAS = ("Retry-After", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset")


def _quien(endpoint, page, cuerpo):
    """El «proceso» del log: qué endpoint y QUÉ página pedíamos (antes decía solo «POST vn []»)."""
    return f"POST {endpoint} p{page}x{cuerpo.get('results')}"


def _respuesta(r):
    """TODO lo que contestó el servidor: cuerpo tal cual y las cabeceras que explican un 429.
    Sin esto, un 429 solo dice «hubo 429» y no cuál de los dos presupuestos de VNDB reventamos."""
    partes = [f"{k}={r.headers[k]}" for k in _CABECERAS if k in r.headers]
    otras = [f"{k}={v}" for k, v in r.headers.items()
             if k.lower().startswith(("x-", "ratelimit")) and k not in _CABECERAS]
    cabeceras = " · ".join(partes + otras) or "sin cabeceras de cuota"
    cuerpo = " ".join((r.text or "").split())[:800] or "(cuerpo vacío)"
    return f"{cabeceras} · {r.elapsed.total_seconds():.1f} s · respuesta: {cuerpo}"


def _uno(endpoint, vndb_code, fields):
    """La entrada de un id ('v17', 'p1') → (status, dict | None)."""
    code, payload = _post(endpoint, ["id", "=", vndb_code], fields, results=1)
    results = (payload or {}).get("results") or []
    return code, (results[0] if results else None)


def _todos(endpoint, filters, fields):
    """Todas las páginas de una consulta (sigue `more`) → (status de la 1ª, lista)."""
    primero, items, page = 0, [], 1
    while True:
        code, payload = _post(endpoint, filters, fields, page=page)
        primero = primero or code
        if not payload:
            break
        items.extend(payload.get("results") or [])
        if not payload.get("more") or page >= 50:
            break
        page += 1
    return primero, items


def _num(vndb_code):
    """'v17' → 17, 'p24' → 24. None si no tiene pinta de id VNDB."""
    try:
        return int(str(vndb_code)[1:])
    except (TypeError, ValueError):
        return None


# ----------------------------- ayudas -----------------------------
def _img(obj, url):
    """Imagen: solo deja la FILA con su URL en la tabla de imágenes (Game → GameImage…), al final; NO descarga. Bajar es otro
    paso (descargador de imágenes pendientes: programado, o la acción masiva de la lista). Si el modelo tiene `image`
    propio (categorías), sí se baja aquí porque no tiene fila pendiente."""
    from django.core.files.base import ContentFile
    if hasattr(obj, "images") and not hasattr(type(obj), "image"):
        if url:
            fila_imagen(obj, url)
        return
    if not url or (getattr(obj, "image", None) and obj.image.name):
        return
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200 and r.content:
            ext = ".png" if url.lower().endswith(".png") else ".jpg"
            obj.image.save(f"{obj.slug or obj.vndb_id}{ext}", ContentFile(r.content), save=True)
        else:
            log(LogLevel.WARNING, f"img {obj}", f"HTTP {r.status_code}")
    except requests.RequestException as exc:
        log(LogLevel.WARNING, f"img {obj}", exc)


def _fecha(valor):
    """`released` de VNDB admite fechas PARCIALES ('1999', '1999-08') y 'TBA':
    completa con día/mes 01 o devuelve None si no hay año."""
    partes = (valor or "").strip().split("-")
    if not (partes[0].isdigit() and len(partes[0]) == 4):
        return None
    while len(partes) < 3:
        partes.append("01")
    if not (partes[1].isdigit() and partes[2].isdigit()):
        return None
    return "-".join(partes[:3])


def _tags_del_juego(game, tags):
    """TODOS los tags de VNDB del juego, sin umbral ni spoiler: categoría `tech` → `Tag` (etiqueta técnica), el resto
    (`cont`, `ero`) → `Genre`. Se crean al vuelo por `vndb_id` (el nombre puede cambiar en VNDB; el id no)."""
    generos, etiquetas = [], []
    for t in tags or []:
        if not isinstance(t, dict) or not t.get("name"):
            continue
        tid = _num(t.get("id"))
        modelo = Tag if t.get("category") == "tech" else Genre
        fila = modelo.objects.filter(vndb_id=tid).first() if tid else None
        if fila is None:
            fila = (modelo.objects.filter(name__iexact=t["name"][:100]).first()
                    or modelo.objects.filter(aliases__name__iexact=t["name"][:100]).first())   # por alias antes de crear
            if fila is None:
                fila = modelo.objects.create(name=t["name"][:100], vndb_id=tid)
            elif tid and not fila.vndb_id:
                fila.vndb_id = tid
                fila.save(update_fields=["vndb_id"])
        (etiquetas if modelo is Tag else generos).append(fila)
    if generos:
        game.genres.add(*generos)
    if etiquetas:
        game.tags.add(*etiquetas)


def _lang(code, crear=True):
    """Idioma del catálogo por su ISO 639-1 ('en', 'ja', 'zh-Hans' → 'zh'), sin importar mayúsculas;
    si no existe, se crea con el código como ISO (nunca con el código como nombre)."""
    code = (code or "").strip()
    if not code:
        return None
    base = code.split("-")[0]
    for filtro in ({"iso_639_1__iexact": code}, {"iso_639_1__iexact": base}, {"iso_639_2_t__iexact": code},
                   {"acronym__iexact": code}, {"name__iexact": code}):
        obj = Language.objects.filter(**filtro).order_by("pk").first()
        if obj:
            return obj
    if not crear:
        return None
    return Language.objects.create(name=code.upper()[:100], iso_639_1=base.upper()[:10])


# Nombres legibles para códigos VNDB que no estén en el catálogo (se crea con nombre y código)
_PLATAFORMAS_VNDB = {
    "win": "Windows", "lin": "Linux", "mac": "Mac OS", "and": "Android", "ios": "iOS (iPhone/iPad)", "web": "Web",
    "dos": "DOS", "swi": "Nintendo Switch", "psp": "PlayStation Portable", "psv": "PlayStation Vita", "ps1": "PlayStation 1",
    "ps2": "PlayStation 2", "ps3": "PlayStation 3", "ps4": "PlayStation 4", "ps5": "PlayStation 5", "xb1": "Xbox",
    "xb3": "Xbox 360", "xbo": "Xbox One", "xxs": "Xbox Series X/S", "nds": "Nintendo DS", "n3d": "Nintendo 3DS",
    "wii": "Wii", "wiu": "Wii U", "gba": "Game Boy Advance", "gbc": "Game Boy Color", "drc": "Dreamcast", "sat": "Sega Saturn",
    "pce": "PC Engine", "fm7": "FM-7", "fm8": "FM-8", "fmt": "FM Towns", "p88": "PC-88", "p98": "PC-98", "x68": "X68000",
    "msx": "MSX", "oth": "Otra",
}


def _platform(code, crear=True):
    """Plataforma del catálogo por su código VNDB ('win', 'lin', 'and'…), sin importar mayúsculas;
    si no existe, se crea con nombre legible y el código (nunca con el código como nombre)."""
    code = (code or "").strip()
    if not code:
        return None
    nombre = _PLATAFORMAS_VNDB.get(code.lower(), "")
    for filtro in ({"vndb_code__iexact": code}, {"name__iexact": nombre} if nombre else None, {"name__iexact": code}):
        if not filtro:
            continue
        obj = Platform.objects.filter(**filtro).order_by("pk").first()
        if obj:
            if not obj.vndb_code:
                obj.vndb_code = code.upper()[:15]
                obj.save(update_fields=["vndb_code"])
            return obj
    if not crear:
        return None
    return Platform.objects.create(name=(nombre or code.upper())[:100], vndb_code=code.upper()[:15])


# ----------------------------- CREATOR (producer) -----------------------------
def _crudo_creador(vndb_id, data, code):
    """UNA fila de staging por productor (la usan «uno», «rango» y el barrido)."""
    ok = bool(data)
    row, _ = DataVndbCreator.objects.update_or_create(
        vndb_id=vndb_id,
        defaults={"url": f"{VNDB}/producer", "data": data, "data_status": ok, "status_code": code})
    return row


def fetch_creator(vndb_id):
    code, data = _uno("producer", f"p{vndb_id}", PRODUCER_FIELDS)
    row = _crudo_creador(vndb_id, data, code)
    log(20 if row.data_status else 40, f"fetch creador p{vndb_id}", "OK" if row.data_status else "sin datos")
    return row


def process_creator(vndb_id):
    row = DataVndbCreator.objects.filter(vndb_id=vndb_id, data_status=True).first()
    if not row:
        return None
    d = row.data or {}
    nombre = (d.get("name") or f"Creador {vndb_id}")[:150]
    campos = {"name": nombre, "description": d.get("description") or "", "type": _creator_type(d.get("type"))}
    creator = Creator.objects.filter(vndb_id=vndb_id).first()
    if creator is None:                                   # ADOPTA el creador que ya exista con ese nombre y sin id
        creator = Creator.objects.filter(vndb_id__isnull=True, name__iexact=nombre).first()   # (seed, F95): sin duplicados
    if creator is None:
        creator = Creator.objects.create(vndb_id=vndb_id, **campos)
    else:
        creator.vndb_id = vndb_id
        for k, v in campos.items():
            setattr(creator, k, v)
        creator.save()
    _fundir_duplicados(creator)
    idioma = _lang(d.get("lang"))
    if idioma is not None:
        creator.languages.add(idioma)
    for alias in d.get("aliases") or []:                       # aliases → apodos
        alias = (alias or "").strip()[:100]
        if alias and alias.lower() != creator.name.lower():
            CreatorNickname.objects.get_or_create(creator=creator, nickname=alias)
    for link in d.get("extlinks") or []:                       # extlinks → enlaces con su fuente externa
        url = (link or {}).get("url") or ""
        fuente = _fuente_externa(link) if url else None
        if fuente is not None:
            CreatorLink.objects.update_or_create(creator=creator, source=fuente, external_id=str(link.get("id") or "")[:500],
                                                 defaults={"url": url})
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    return creator


def _fundir_duplicados(creator):
    """Si quedan OTROS creadores con el mismo nombre y sin id de VNDB (seed, F95, altas a mano), sus juegos, apodos y
    enlaces pasan al de VNDB y el duplicado se borra. Así una lista no muestra «07th Expansion» dos veces."""
    for dup in Creator.objects.filter(vndb_id__isnull=True, name__iexact=creator.name).exclude(pk=creator.pk):
        for g in dup.games.all():
            g.developers.add(creator)
        for g in dup.published_games.all():
            g.publishers.add(creator)
        for n in dup.nicknames.all():
            CreatorNickname.objects.get_or_create(creator=creator, nickname=n.nickname)
        for l in dup.links.all():
            CreatorLink.objects.get_or_create(creator=creator, source=l.source, external_id=l.external_id, defaults={"url": l.url})
        if not creator.description and dup.description:
            creator.description = dup.description
            creator.save(update_fields=["description"])
        log(LogLevel.INFO, f"creador p{creator.vndb_id}", f"fundido con el duplicado sin id #{dup.pk} «{dup.name}»")
        dup.delete()


# Clave de VNDB (`name` del extlink) → tipo de fuente externa; lo que no está aquí queda como «otro».
_FUENTE_KIND = {
    "website": "OFFICIAL",
    "patreon": "MONETIZATION", "subscribestar": "MONETIZATION", "fanbox": "MONETIZATION", "boosty": "MONETIZATION", "kofi": "MONETIZATION",
    "twitter": "SOCIAL", "bluesky": "SOCIAL", "facebook": "SOCIAL", "instagram": "SOCIAL", "youtube": "SOCIAL", "pixiv": "SOCIAL", "tumblr": "SOCIAL",
    "discord": "COMMUNITY", "reddit": "COMMUNITY",
    "wikidata": "DATABASE", "mobygames_company": "DATABASE", "gamefaqs_company": "DATABASE", "vgmdb": "DATABASE",
    "anidb": "DATABASE", "igdb": "DATABASE", "vndb": "DATABASE", "pcgamingwiki": "DATABASE",
}


def _fuente_externa(link):
    """La ExternalSource de un extlink de VNDB: casa por acrónimo (= la clave `name` de VNDB: patreon, jawiki…) o por
    nombre (= la etiqueta: «Patreon», «Wikipedia (ja)»); si no existe, se crea con su tipo y queda con el acrónimo
    para casar la próxima vez."""
    from apps.catalogs.models import ExternalSource
    clave = ((link or {}).get("name") or "").strip().lower()
    etiqueta = ((link or {}).get("label") or clave or "Enlace").strip()[:100]
    if not clave:
        return None
    fuente = ExternalSource.objects.filter(acronym__iexact=clave).first() or ExternalSource.objects.filter(name__iexact=etiqueta).first()
    if fuente is None:
        kind = _FUENTE_KIND.get(clave, "DATABASE" if "wiki" in clave else "OTHER")
        fuente = ExternalSource.objects.create(name=etiqueta, acronym=clave[:15], type=kind)
    elif not fuente.acronym:
        fuente.acronym = clave[:15]
        fuente.save(update_fields=["acronym"])
    return fuente


def _creator_type(codigo):
    """Tipo de creador por la clave de VNDB: co → CO (compañía), in → IN (individual), ng → NG (grupo amateur).
    Si no casa con `CreatorType`, queda vacío."""
    return {"CO": CreatorType.COMPANY, "IN": CreatorType.INDIVIDUAL, "NG": CreatorType.AMATEUR}.get((codigo or "").strip().upper(), "")


def _creator_del_juego(stub):
    """Productor de una VN o de un lanzamiento ({id:'p123', name}): si YA existe se enlaza tal
    cual; si NO, se trae COMPLETO de la API por su id (fetch → Data → process)."""
    vid = _num((stub or {}).get("id")) if str((stub or {}).get("id", "")).startswith("p") else None
    if vid is None:
        return None
    existente = Creator.objects.filter(vndb_id=vid).first()
    if existente:
        return existente
    if stub.get("type") or stub.get("lang"):          # viene COMPLETO anidado (barrido, VN_FIELDS): sin petición
        _crudo_creador(vid, stub, 200)
        return process_creator(vid)
    return import_creator(vid)


# ----------------------------- GAME (visual novel) + lanzamientos + personajes -----------------------------
def _primera_vn(data):
    """El vndb_id de la primera VN de un lanzamiento o personaje (columna `vndb_id_vn`; el resto queda en el JSON)."""
    for vn in (data or {}).get("vns") or []:
        vid = _num(vn.get("id"))
        if vid is not None:
            return vid
    return None


def _crudo_juego(vndb_id, data, code):
    ok = bool(data)
    row, _ = DataVndbGame.objects.update_or_create(
        vndb_id=vndb_id, defaults={"url": f"{VNDB}/vn", "data": data, "data_status": ok, "status_code": code})
    return row


def _crudo_lanzamiento(vndb_id, data, code, vn=None):
    ok = bool(data)
    row, _ = DataVndbRelease.objects.update_or_create(vndb_id=vndb_id, defaults={
        "vndb_id_prefix": (data or {}).get("id") or f"r{vndb_id}", "vndb_id_vn": vn if vn is not None else _primera_vn(data),
        "url": f"{VNDB}/release", "data": data, "data_status": ok, "status_code": code})
    return row


def _crudo_personaje(vndb_id, data, code, vn=None):
    ok = bool(data)
    row, _ = DataVndbCharacter.objects.update_or_create(vndb_id=vndb_id, defaults={
        "vndb_id_prefix": (data or {}).get("id") or f"c{vndb_id}", "vndb_id_vn": vn if vn is not None else _primera_vn(data),
        "url": f"{VNDB}/character", "data": data, "data_status": ok, "status_code": code})
    return row


def fetch_game(vndb_id):
    """La VN y, si existe, TODOS sus lanzamientos y personajes (paginados), cada uno en su tabla."""
    code, data = _uno("vn", f"v{vndb_id}", VN_FIELDS)
    row = _crudo_juego(vndb_id, data, code)
    if not row.data_status:
        log(LogLevel.WARNING, f"fetch juego v{vndb_id}", "sin datos")
        return row
    code_r, releases = _todos("release", ["vn", "=", ["id", "=", f"v{vndb_id}"]], RELEASE_FIELDS)
    for r in releases:
        if _num(r.get("id")) is not None:
            _crudo_lanzamiento(_num(r.get("id")), r, code_r, vn=vndb_id)
    code_c, characters = _todos("character", ["vn", "=", ["id", "=", f"v{vndb_id}"]], CHARACTER_FIELDS)
    for c in characters:
        if _num(c.get("id")) is not None:
            _crudo_personaje(_num(c.get("id")), c, code_c, vn=vndb_id)
    log(LogLevel.INFO, f"fetch juego v{vndb_id}", f"{data.get('title')}: {len(releases)} lanzamientos, {len(characters)} personajes")
    return row


def _extras_del_juego(game, items, que):
    """Imágenes del juego desde una lista de VNDB (capturas de la VN o artes de sus lanzamientos: caja, disco…):
    una fila por URL nueva, con `image_downloaded=False`. NO descarga: eso lo hace el descargador de pendientes."""
    nuevas = 0
    for item in items:
        url = (item or {}).get("url") or ""
        if not url:
            continue
        if not game.images.filter(image_url=url).exists():
            GameImage.objects.create(game=game, image_url=url)
            nuevas += 1
    return nuevas


def _estado(devstatus):
    """`devstatus` de VNDB (0 terminado, 1 en desarrollo, 2 cancelado) → `GameStatus`; sin código, desconocido."""
    return {0: GameStatus.COMPLETED, 1: GameStatus.DEVELOPING, 2: GameStatus.ABANDONED}.get(devstatus, GameStatus.UNKNOWN)


def process_game(vndb_id):
    row = DataVndbGame.objects.filter(vndb_id=vndb_id, data_status=True).first()
    if not row:
        return None
    d = row.data or {}
    fecha_vn = _fecha(d.get("released"))
    game, _ = Game.objects.update_or_create(vndb_id=vndb_id, defaults={
        "title": (d.get("title") or f"Juego {vndb_id}")[:255],
        "synopsis": d.get("description") or "",
        "release_date": datetime.date.fromisoformat(fecha_vn) if fecha_vn else None,
        "status": _estado(d.get("devstatus")),
        "type": GameType.VN,                       # todo lo de VNDB es novela visual
    })
    _img(game, (d.get("image") or {}).get("url"))   # portada del juego
    _extras_del_juego(game, d.get("screenshots") or [], "captura")   # capturas → imágenes extra del juego
    for lang in d.get("languages", []) or []:
        game.languages.add(_lang(lang))
    for plat in d.get("platforms", []) or []:
        game.platforms.add(_platform(plat))
    for dev in d.get("developers", []) or []:
        creator = _creator_del_juego(dev)
        if creator:
            game.developers.add(creator)
    _tags_del_juego(game, d.get("tags") or [])   # géneros (contenido) + etiquetas (técnicas), todos
    # Lanzamientos: editoras (productores con `publisher`), plataformas, idiomas y la fecha más antigua.
    menciona = Q(vndb_id_vn=vndb_id) | Q(data__vns__contains=[{"id": f"v{vndb_id}"}])
    lanzamientos = DataVndbRelease.objects.filter(menciona, data_status=True)
    for rel in lanzamientos:
        _aplicar_lanzamiento(game, rel.data or {})
        rel.data_processed = True
        rel.save(update_fields=["data_processed"])
    # Personajes: personajes REALES (Character) enlazados a este juego. Los otros juegos en los que
    # aparezcan NO se traen desde aquí (eso lo hace «importar personaje»): evita recorrer todo VNDB.
    personajes = DataVndbCharacter.objects.filter(menciona, data_status=True)
    for ch in personajes:
        _personaje_desde(ch.data or {}, traer_juegos=False)
        ch.data_processed = True
        ch.save(update_fields=["data_processed"])
    from django.utils import timezone
    game.vndb_fetched_at = timezone.now()      # última obtención: sirve para re-obtener los viejos
    game.save(update_fields=["vndb_fetched_at"])
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    log(LogLevel.INFO, f"process juego v{vndb_id}", f"{game.title}: {lanzamientos.count()} lanzamientos, {personajes.count()} personajes")
    return game


def _aplicar_lanzamiento(game, r):
    """Un lanzamiento REAL (Release) enlazado al juego, con sus plataformas, idiomas, editoras y
    desarrolladores; y lo que suma al juego: editoras, desarrolladores, plataformas, idiomas y la
    fecha oficial más antigua."""
    fecha = _fecha(r.get("released"))
    rid = _num(r.get("id"))
    release = None
    if rid is not None:
        release, _ = Release.objects.update_or_create(vndb_id=rid, defaults={
            "game": game, "title": (r.get("title") or f"Lanzamiento {rid}")[:255], "alttitle": (r.get("alttitle") or "")[:255],
            "released": datetime.date.fromisoformat(fecha) if fecha else None,
            "official": bool(r.get("official", True)), "patch": bool(r.get("patch")), "freeware": bool(r.get("freeware")),
            "minage": r.get("minage") if isinstance(r.get("minage"), int) else None,
        })
        for item in (r.get("images") or []):        # artes del lanzamiento (caja, disco…): filas con URL, sin descargar
            url = (item or {}).get("url") or ""
            if url and not release.images.filter(image_url=url).exists():
                ReleaseImage.objects.create(release=release, image_url=url, label=(item.get("type") or "")[:20])
    for prod in r.get("producers") or []:
        creator = _creator_del_juego(prod)
        if not creator:
            continue
        if prod.get("publisher"):
            game.publishers.add(creator)
            if release:
                release.publishers.add(creator)
        if prod.get("developer"):
            game.developers.add(creator)
            if release:
                release.developers.add(creator)
    for plat in r.get("platforms") or []:
        p = _platform(plat)
        game.platforms.add(p)
        if release:
            release.platforms.add(p)
    for lang in r.get("languages") or []:
        l = _lang(lang.get("lang") if isinstance(lang, dict) else lang)
        game.languages.add(l)
        if release:
            release.languages.add(l)
    if fecha and r.get("official", True) and not r.get("patch"):
        f = datetime.date.fromisoformat(fecha)
        if game.release_date is None or f < game.release_date:
            game.release_date = f
            game.save(update_fields=["release_date"])
    return release


def _personaje_desde(data, traer_juegos):
    """Character real desde el JSON de VNDB. Un personaje NO vive sin su juego: con
    `traer_juegos` se importan los juegos en los que aparece si faltan; si no, solo se enlaza a
    los que ya existen. La imagen queda como fila con URL (la baja el descargador)."""
    cid = _num(data.get("id"))
    if cid is None:
        return None
    sexo = data.get("sex")
    sexo = (sexo[0] if isinstance(sexo, (list, tuple)) and sexo else sexo) or ""
    cumple = data.get("birthday")
    cumple = f"{cumple[0]:02d}-{cumple[1]:02d}" if isinstance(cumple, (list, tuple)) and len(cumple) == 2 and all(cumple) else ""
    ch, _ = Character.objects.update_or_create(vndb_id=cid, defaults={
        "name": (data.get("name") or f"Personaje {cid}")[:255],
        "original": (data.get("original") or "")[:255],
        "description": data.get("description") or "",
        "sex": str(sexo)[:10], "age": data.get("age") if isinstance(data.get("age"), int) else None,
        "birthday": cumple,
    })
    for vn in data.get("vns") or []:
        gid = _num(vn.get("id"))
        if gid is None:
            continue
        game = Game.objects.filter(vndb_id=gid).first()
        if game is None and traer_juegos:
            game = import_game(gid)
        if game is not None:
            CharacterRole.objects.update_or_create(character=ch, game=game, defaults={"role": (vn.get("role") or "")[:20]})
    url = (data.get("image") or {}).get("url") or ""
    if url and not ch.images.filter(image_url=url).exists():
        CharacterImage.objects.create(character=ch, image_url=url)   # la baja el descargador
    return ch


# ----------------------------- CHARACTER suelto (trae su juego si falta) -----------------------------
def fetch_character(vndb_id):
    code, data = _uno("character", f"c{vndb_id}", CHARACTER_FIELDS)
    row = _crudo_personaje(vndb_id, data, code)
    log(20 if row.data_status else 40, f"fetch personaje c{vndb_id}", "OK" if row.data_status else "sin datos")
    return row


def _juegos_de(data):
    """Los Game que ya existen entre las VN de un lanzamiento o personaje (por su JSON `vns`)."""
    ids = [v for v in (_num(vn.get("id")) for vn in (data or {}).get("vns") or []) if v is not None]
    return list(Game.objects.filter(vndb_id__in=ids)) if ids else []


def process_character(vndb_id, traer_juegos=True):
    """Con `traer_juegos` (importar uno) baja los juegos que falten; en LOCAL (barrido, pendientes) un personaje sin
    ningún juego en la base se queda pendiente: lo consumirá process_game cuando llegue su juego."""
    row = DataVndbCharacter.objects.filter(vndb_id=vndb_id, data_status=True).first()
    if not row:
        return None
    if not traer_juegos and not _juegos_de(row.data):
        return None
    ch = _personaje_desde(row.data or {}, traer_juegos=traer_juegos)
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    return ch


# ----------------------------- RELEASE suelto (trae su juego si falta) -----------------------------
def fetch_release(vndb_id):
    code, data = _uno("release", f"r{vndb_id}", RELEASE_FIELDS)
    row = _crudo_lanzamiento(vndb_id, data, code)
    log(20 if row.data_status else 40, f"fetch lanzamiento r{vndb_id}", "OK" if row.data_status else "sin datos")
    return row


def process_release(vndb_id, traer_juego=True):
    """Un lanzamiento NO vive sin su juego. Con `traer_juego` (importar uno) baja el juego si falta; en LOCAL
    (barrido, pendientes) se vuelca solo a los juegos que ya existen y, si no hay ninguno, queda pendiente."""
    row = DataVndbRelease.objects.filter(vndb_id=vndb_id, data_status=True).first()
    if not row:
        return None
    r = row.data or {}
    juegos = []
    for vn in r.get("vns") or []:
        gid = _num(vn.get("id"))
        if gid is None:
            continue
        game = Game.objects.filter(vndb_id=gid).first() or (import_game(gid) if traer_juego else None)
        if game:
            _aplicar_lanzamiento(game, r)
            juegos.append(game)
    if not juegos:
        return None                                   # pendiente: lo consume process_game cuando llegue su juego
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    return juegos[0]


# ----------------------------- conveniencia -----------------------------
def _sin_ruido(proceso, fn, *args):
    """Si el proceso termina sin avisos, se lleva por delante sus líneas informativas (el helper común)."""
    return sin_ruido(GameLog, proceso, fn, *args, peticiones=lambda: _stats["peticiones"])


def import_game(vndb_id):
    def _todo():
        fetch_game(vndb_id)
        return process_game(vndb_id)
    return _sin_ruido(f"import juego v{vndb_id}", _todo)


def juegos_de_creador(vndb_id):
    """Ids de TODAS las VN desarrolladas por un productor (POST /vn filtrado por developer, paginado)."""
    _code, vns = _todos("vn", ["developer", "=", ["id", "=", f"p{vndb_id}"]], "id")
    return sorted({i for i in (_num(v.get("id")) for v in vns) if i is not None})


def import_creator(vndb_id, deep=False):
    """El creador y, con `deep`, TODOS sus juegos (cada uno con lanzamientos, personajes y editoras)."""
    def _todo():
        fetch_creator(vndb_id)
        creator = process_creator(vndb_id)
        if creator is not None and deep:
            ids = juegos_de_creador(vndb_id)
            hechos = import_ids("juego", ids)
            log(LogLevel.INFO, f"juegos del creador p{vndb_id}", f"{hechos}/{len(ids)} juegos")
        return creator
    return _sin_ruido(f"import creador p{vndb_id}", _todo)


def import_creator_games(vndb_ids):
    """Para varios creadores (acción masiva): todos los juegos de cada uno. Devuelve juegos importados."""
    total = 0
    for vid in vndb_ids:
        if cancelado():
            log(LogLevel.WARNING, "cancelada", "detenida por el usuario entre creadores")
            break
        ids = juegos_de_creador(vid)
        total += import_ids("juego", ids)
    return total


def import_character(vndb_id):
    def _todo():
        fetch_character(vndb_id)
        return process_character(vndb_id)
    return _sin_ruido(f"import personaje c{vndb_id}", _todo)


def import_release(vndb_id):
    def _todo():
        fetch_release(vndb_id)
        return process_release(vndb_id)
    return _sin_ruido(f"import lanzamiento r{vndb_id}", _todo)


def refrescar_juegos_viejos(days=30, cantidad=20):
    """Re-obtiene los juegos con más de `days` días desde su última obtención (o nunca): vuelven a
    traerse con sus lanzamientos, personajes y editoras. Hasta `cantidad` por tanda."""
    from datetime import timedelta
    from django.utils import timezone
    limite = timezone.now() - timedelta(days=days)
    viejos = (Game.objects.filter(vndb_id__isnull=False).filter(Q(vndb_fetched_at__isnull=True) | Q(vndb_fetched_at__lt=limite))
              .order_by("vndb_fetched_at", "pk").values_list("vndb_id", flat=True)[: max(int(cantidad), 0)])
    return import_ids("juego", list(viejos))


# ----------------------------- BÚSQUEDA por nombre (solo lectura) -----------------------------
def buscar_juegos(query):
    """TODOS los candidatos de novela visual por título (todas las páginas): id, título, año, desarrolladores y portada."""
    query = (query or "").strip()
    if not query:
        return []
    _code, items = _todos("vn", ["search", "=", query], "id, title, released, image.url, developers{name}")
    ya = set(DataVndbGame.objects.filter(data_status=True).values_list("vndb_id", flat=True))
    filas = []
    for v in items:
        vid = _num(v.get("id"))
        devs = ", ".join(d.get("name", "") for d in (v.get("developers") or []) if d.get("name"))
        filas.append({"id": vid, "titulo": v.get("title") or "", "imagen": (v.get("image") or {}).get("url") or "",
                      "sub": " · ".join(x for x in [(v.get("released") or "")[:4], devs] if x),
                      "link": f"https://vndb.org/{v.get('id')}", "ya": vid in ya})
    return filas


def buscar_creadores(query):
    """TODOS los candidatos de productor por nombre (todas las páginas): id, nombre, tipo e idioma."""
    query = (query or "").strip()
    if not query:
        return []
    _code, items = _todos("producer", ["search", "=", query], "id, name, original, type, lang")
    ya = set(DataVndbCreator.objects.filter(data_status=True).values_list("vndb_id", flat=True))
    return [{"id": _num(p.get("id")), "titulo": p.get("name") or "", "imagen": "",
             "sub": " · ".join(x for x in [p.get("original") or "", p.get("type") or "", p.get("lang") or ""] if x),
             "link": f"https://vndb.org/{p.get('id')}", "ya": _num(p.get("id")) in ya}
            for p in items]

def buscar_lanzamientos(query):
    """TODOS los candidatos de lanzamiento por título (todas las páginas): id, título, fecha y a qué VN pertenece."""
    query = (query or "").strip()
    if not query:
        return []
    _code, items = _todos("release", ["search", "=", query], "id, title, released, vns{title}")
    ya = set(DataVndbRelease.objects.filter(data_status=True).values_list("vndb_id", flat=True))
    filas = []
    for r in items:
        rid = _num(r.get("id"))
        juegos = ", ".join(v.get("title", "") for v in (r.get("vns") or []) if v.get("title"))
        filas.append({"id": rid, "titulo": r.get("title") or "", "imagen": "",
                      "sub": " · ".join(x for x in [(r.get("released") or "")[:4], juegos] if x),
                      "link": f"https://vndb.org/{r.get('id')}", "ya": rid in ya})
    return filas


def buscar_personajes(query):
    """TODOS los candidatos de personaje por nombre (todas las páginas): id, nombre, nombre original, foto y sus VN."""
    query = (query or "").strip()
    if not query:
        return []
    _code, items = _todos("character", ["search", "=", query], "id, name, original, image.url, vns{title}")
    ya = set(DataVndbCharacter.objects.filter(data_status=True).values_list("vndb_id", flat=True))
    filas = []
    for c in items:
        cid = _num(c.get("id"))
        juegos = ", ".join(v.get("title", "") for v in (c.get("vns") or []) if v.get("title"))
        filas.append({"id": cid, "titulo": c.get("name") or "", "imagen": (c.get("image") or {}).get("url") or "",
                      "sub": " · ".join(x for x in [c.get("original") or "", juegos] if x),
                      "link": f"https://vndb.org/{c.get('id')}", "ya": cid in ya})
    return filas


# ----------------------------- Post-procesador (juegos) -----------------------------
def process_pending(limit_per_model=None):
    """Procesa el crudo pendiente en orden de dependencia: creadores → juegos → lanzamientos → personajes. Los dos
    últimos solo los de juegos que YA existen (en local, sin peticiones); los demás siguen pendientes."""
    total = 0
    juegos = set(Game.objects.values_list("vndb_id", flat=True))
    pasos = ((DataVndbCreator, process_creator, None), (DataVndbGame, process_game, None),
             (DataVndbRelease, _PROCESAR["lanzamiento"], juegos), (DataVndbCharacter, _PROCESAR["personaje"], juegos))
    for model, fn, solo_de in pasos:
        qs = model.objects.filter(data_status=True, data_processed=False).order_by("vndb_id")   # en orden, de menor a mayor
        if solo_de is not None:
            qs = qs.filter(vndb_id_vn__in=solo_de)
        ids = list(qs.values_list("vndb_id", flat=True)[: limit_per_model or None])
        ok = 0
        for vid in ids:
            try:
                if fn(vid) is not None:
                    ok += 1
            except Exception as exc:  # noqa: BLE001
                log(LogLevel.ERROR, f"postprocess {model.__name__} #{vid}", exc)
        total += ok
        if ids:
            log(LogLevel.INFO, f"postprocess {model.__name__}", f"{ok}/{len(ids)}")
    return total


# ----------------------------- Procesar por lotes (vistas «Procesar») -----------------------------
LOTE_PROCESO = 500


def _pendientes_qs(kind):
    """Filas pendientes (fetch OK, sin procesar) de un tipo. Lanzamientos y personajes: solo los de juegos que YA existen
    (su juego se procesa antes; los demás siguen pendientes). EXISTS, sin traer los ids de juegos a memoria."""
    model = _DATA[kind]
    qs = model.objects.filter(data_status=True, data_processed=False)
    if kind in ("lanzamiento", "personaje"):
        qs = qs.filter(Exists(Game.objects.filter(vndb_id=OuterRef("vndb_id_vn"))))
    return qs


def pendientes(kind):
    """Cuántas filas de ese tipo se pueden procesar ahora."""
    return _pendientes_qs(kind).count()


def procesar_lote(kind, cantidad=0):
    """Procesa hasta `cantidad` pendientes de UN tipo (0 = todos) en local, recorriendo por `vndb_id` de a lotes: nunca
    carga la lista entera. Entre lotes mira si pidieron cancelar. Devuelve cuántas quedaron armadas."""
    from core.shared.tasks.cancel import avance
    cantidad = max(int(cantidad or 0), 0)
    ultimo, hechos, vistos = 0, 0, 0
    total = pendientes(kind) if cantidad == 0 else min(cantidad, pendientes(kind))
    avance(0, total)
    while cantidad == 0 or vistos < cantidad:
        if cancelado():
            log(LogLevel.WARNING, f"procesar {kind}", f"detenido por el usuario tras {vistos}; lo procesado se queda")
            break
        tope = LOTE_PROCESO if cantidad == 0 else min(LOTE_PROCESO, cantidad - vistos)
        ids = list(_pendientes_qs(kind).filter(vndb_id__gt=ultimo).order_by("vndb_id").values_list("vndb_id", flat=True)[:tope])
        if not ids:
            break
        hechos += procesar_ids(kind, ids)
        vistos += len(ids)
        ultimo = ids[-1]
        avance(vistos, total)
    log(LogLevel.INFO, f"procesar {kind}", f"{hechos} procesados de {vistos} · quedan {pendientes(kind)} pendientes")
    return hechos


# ----------------------------- BARRIDO por páginas (catálogo entero, 100 por petición) -----------------------------
# tipo → (endpoint, campos, guardar crudo). `page` avanza de 1 en 1 con `sort: "id"` y sin filtro: los ids nuevos
# entran al final y una baja solo repite una fila (el crudo es update_or_create), nunca salta.
# tipo → (endpoint, campos, guardar crudo). Cada página son SIEMPRE 100 filas (POR_PAGINA, el máximo de VNDB).
_BARRIDO = {"creador": ("producer", PRODUCER_FIELDS, _crudo_creador),
            "juego": ("vn", VN_FIELDS, _crudo_juego),
            "lanzamiento": ("release", RELEASE_FIELDS, _crudo_lanzamiento),
            "personaje": ("character", CHARACTER_FIELDS, _crudo_personaje)}


def barrer(kind, desde_pagina=1, paginas=1):
    """Barre `paginas` páginas de 100 del catálogo de `kind` desde `desde_pagina` → (ids guardados, próxima página, quedan más).
    No procesa (procesar_ids) ni mueve cursores (lo decide quien llama). Para si el usuario cancela o si no quedan más."""
    endpoint, fields, guardar = _BARRIDO[kind]
    ids, pagina, mas = [], desde_pagina, True
    for _ in range(paginas):
        if cancelado():
            log(LogLevel.WARNING, f"barrido {kind}", f"detenido por el usuario en la página {pagina}; lo guardado se queda")
            break
        code, payload = _post(endpoint, [], fields, page=pagina, results=POR_PAGINA, sort="id", espera=ESPERA_BARRIDO)
        if not payload:
            log(LogLevel.WARNING, f"barrido {kind} página {pagina}", f"sin respuesta (HTTP {code})")
            break
        for item in payload.get("results") or []:
            vid = _num(item.get("id"))
            if vid is not None:
                guardar(vid, item, code)
                ids.append(vid)
        mas = bool(payload.get("more"))
        pagina += 1
        if not mas:
            break
    log(LogLevel.INFO, f"barrido {kind} páginas {desde_pagina}-{pagina - 1}",
        f"{len(ids)} filas al crudo · {_last_call['coste']:.1f} s la última página · {'quedan más' if mas else 'catálogo agotado'}")
    return ids, pagina, mas


_PROCESAR = {"creador": process_creator, "juego": process_game,
             "lanzamiento": lambda vid: process_release(vid, traer_juego=False),
             "personaje": lambda vid: process_character(vid, traer_juegos=False)}


def procesar_ids(kind, ids):
    """Proceso LOCAL (sin peticiones) de las filas de staging de esos ids → cuántas quedaron armadas."""
    fn = _PROCESAR[kind]
    ok = 0
    for vid in ids:
        try:
            if fn(vid) is not None:
                ok += 1
        except Exception as exc:  # noqa: BLE001
            log(LogLevel.ERROR, f"procesar {kind} #{vid}", exc)
    return ok


# ----------------------------- Importación masiva (rango / lista) -----------------------------
_BULK = {"juego": import_game, "creador": import_creator, "personaje": import_character, "lanzamiento": import_release}


_DATA = {"juego": DataVndbGame, "creador": DataVndbCreator, "lanzamiento": DataVndbRelease, "personaje": DataVndbCharacter}


def ids_descargados(kind, start, end):
    """Ids del rango que YA están en la tabla de datos crudos (bajados por barrido, rango o uno a uno)."""
    modelo = _DATA.get(kind)
    if modelo is None:
        return set()
    return set(modelo.objects.filter(vndb_id__gte=start, vndb_id__lte=end, data_status=True).values_list("vndb_id", flat=True))


def siguiente_id_descargado(kind):
    """El id siguiente al mayor ya descargado de ese tipo (1 si no hay nada): lo que el rango sugiere como inicio."""
    modelo = _DATA.get(kind)
    mayor = modelo.objects.order_by("-vndb_id").values_list("vndb_id", flat=True).first() if modelo else None
    return (mayor or 0) + 1


def import_range(kind, start, end):
    """Baja los ids del rango que aún NO estén en el crudo (los ya descargados por el barrido o por otro rango se saltan)."""
    fn = _BULK.get(kind)
    if fn is None:
        return 0
    ok = 0
    ya = ids_descargados(kind, start, end)
    if ya:
        log(LogLevel.INFO, f"bulk {kind} [{start}-{end}]", f"{len(ya)} ya descargados: se saltan")
    for i in range(start, end + 1):
        if i in ya:
            continue
        if cancelado():                       # el usuario pidió cancelar desde el panel
            log(LogLevel.WARNING, "cancelada", "detenida por el usuario entre pasos; lo ya guardado se queda")
            break
        try:
            if fn(i) is not None:
                ok += 1
        except Exception as exc:  # noqa: BLE001
            log(LogLevel.ERROR, f"bulk {kind} #{i}", exc)
    log(LogLevel.INFO, f"bulk {kind} [{start}-{end}]", f"{ok}/{end - start + 1}")
    return ok


def import_ids(kind, ids):
    """Importa una LISTA de ids (cargada desde CSV / Excel / SQLite): mismo lote que import_range."""
    fn = _BULK.get(kind)
    if fn is None or not ids:
        return 0
    ok = 0
    for i in ids:
        if cancelado():                       # el usuario pidió cancelar desde el panel
            log(LogLevel.WARNING, "cancelada", "detenida por el usuario entre pasos; lo ya guardado se queda")
            break
        try:
            if fn(i) is not None:
                ok += 1
        except Exception as exc:  # noqa: BLE001
            log(LogLevel.ERROR, f"archivo {kind} #{i}", exc)
    log(LogLevel.INFO, f"archivo {kind} ({len(ids)} ids)", f"{ok}/{len(ids)}")
    return ok
