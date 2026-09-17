"""PROCESAR los datos de MAL ya cargados: tablas `DataMal*` → entidades reales. No pide nada a ninguna API.

El crudo entra por `mal_dump_load` (archivo del dump → `DataMal*`). Aquí se lee ese JSON y se crea o actualiza
lo real, siempre por `mal_id` (idempotente), marcando `data_processed=True`:

    process_anime(mal_id)      DataMalAnime (registro del dump)     → Anime, taxonomías, compañías existentes, títulos, relaciones, canciones, imágenes pendientes
    process_manga(mal_id)      DataMalManga (+ personajes)          → Manga, revistas, autores, títulos, relaciones
    process_character(mal_id)  DataMalCharacter                     → Character
    process_person(mal_id)     DataMalPerson                        → Person + ficha MAL
    process_pending(limite)    todo lo pendiente de las cuatro tablas principales

Los personajes y personas a los que apunta una obra se crean al vuelo por su `mal_id`, así los enlaces resuelven
sin importar el orden de carga. La única descarga es la portada (CDN de imágenes de MAL), y si falla no corta nada.
"""
import re
from datetime import date

import requests
from django.core.files.base import ContentFile

from apps.catalogs.models import Language, RelationType
from apps.companies.models import Company
from apps.otaku.models import Anime, AnimeCharacter, AnimeSong, AnimeStaff, AnimeTitle, Character, CharacterVoice, CompanyMAL, DataMalAnime, DataMalCharacter, DataMalManga, DataMalMangaCharacter, DataMalPerson, Demographic, Genre, Manga, MangaAuthor, MangaCharacter, MangaTitle, OtakuLog, PersonMAL, Relation, Role, Source, Status, Theme, Type
from apps.otaku.services.personas import upsert_persona_mal
from core.shared.models.choices import AnimeSongType, LogLevel, MalCompanyKind, MalRating, MalSeason, RelationMedia
from core.shared.tasks.images import portada
from core.utils.importlog import log_to


TIMEOUT_PORTADA = 20
RATINGS = {"G": MalRating.G, "PG": MalRating.PG, "PG-13": MalRating.PG13, "R": MalRating.R17, "R+": MalRating.RPLUS, "RX": MalRating.RX}


def log(nivel, proceso, mensaje=""):
    """Escribe en OtakuLog."""
    return log_to(OtakuLog, nivel, proceso, mensaje)


# ----------------------------- traductores de campos -----------------------------
def _rating(texto):
    """«PG-13 - Teens 13 or older» → MalRating.PG13; lo que no casa, vacío."""
    return RATINGS.get((texto or "").split(" - ")[0].strip().upper(), "")


def _season(texto):
    return texto.strip().upper() if texto and texto.strip().upper() in MalSeason.values else ""


def _fecha(bloque, clave="from"):
    """`aired`/`published`: {"from": "1998-04-03T00:00:00+00:00", "to": …} → date."""
    valor = (bloque or {}).get(clave) or ""
    try:
        return date.fromisoformat(valor[:10]) if valor else None
    except ValueError:
        return None


def _cat(model, name):
    """Taxonomía (ModelBaseCategory) por nombre, o por ALIAS si el modelo los tiene; si no existe, se crea."""
    name = (name or "").strip()[:100]
    if not name:
        return None
    obj = model.objects.filter(name__iexact=name).first()
    if obj is None and hasattr(model, "aliases"):
        obj = model.objects.filter(aliases__name__iexact=name).first()
    return obj or model.objects.create(name=name)


def _company(entrada: dict, kind: str = MalCompanyKind.COMPANY) -> Company | None:
    """La compañía de un estudio / productora / licenciataria (`kind` COMPANY) o revista (MAGAZINE).
    Busca por su ficha MAL (kind, mal_id): MAL numera compañías y revistas por separado. Si no hay ficha, usa una
    compañía SIN ficha con ese nombre (la más antigua) y le pone la ficha; si tampoco hay, la crea con su ficha."""
    nombre = " ".join(str(entrada.get("name") or "").split())[:250]
    try:
        mal_id = int(entrada.get("mal_id"))
    except (TypeError, ValueError):
        mal_id = None
    if not nombre and mal_id is None:
        return None
    if mal_id is not None:
        ficha = CompanyMAL.objects.select_related("company").filter(kind=kind, mal_id=mal_id).first()
        if ficha is not None:
            return ficha.company
    if not nombre:
        return None
    compania = (Company.objects.filter(name__iexact=nombre, company_mal__isnull=True).order_by("pk").first()
                or Company.objects.create(name=nombre))
    if mal_id is not None:
        CompanyMAL.objects.get_or_create(kind=kind, mal_id=mal_id, defaults={"company": compania, "url": str(entrada.get("url") or "")[:500]})
    return compania


def _role(name):
    name = (name or "").strip()
    if not name:
        return None
    obj, _ = Role.objects.get_or_create(name=name[:100])
    return obj


def _lang(name):
    name = (name or "").strip()
    if not name:
        return None
    obj, _ = Language.objects.get_or_create(name=name[:100])
    return obj


def _person(pdata):
    """Persona referenciada (seiyū/staff/autor) creada al vuelo por su mal_id: persona neutra + ficha MAL."""
    pid = (pdata or {}).get("mal_id")
    if not pid:
        return None
    person, _ext, _ = upsert_persona_mal({"mal_id": pid, "name": pdata.get("name")})
    return person


def _relations(from_type, from_mal_id, relations):
    for rel in relations or []:
        rtype, _ = RelationType.objects.get_or_create(name=(rel.get("relation") or "Relación")[:100])
        for entry in rel.get("entry", []):
            kind = (entry.get("type") or "").lower()
            to_id = entry.get("mal_id")
            if kind not in ("anime", "manga") or not to_id:
                continue
            Relation.objects.get_or_create(
                from_type=from_type, from_mal_id=from_mal_id,
                to_type=kind.upper(), to_mal_id=to_id, relation_type=rtype)


def _titles(entity, title_model, fk_name, titles):
    for t in titles or []:
        text = (t.get("title") or "").strip()
        if not text:
            continue
        lang = _lang(t.get("type"))  # MAL usa "Default/Japanese/English/Synonym"
        if lang is None:
            continue
        title_model.objects.get_or_create(**{fk_name: entity, "title_lang": lang, "title": text[:500]})


def _mark(model, mal_id):
    model.objects.filter(mal_id=mal_id).update(data_processed=True)


def _cover(obj, raw):
    """Descarga la portada (images.webp/jpg) y la guarda. No pisa una imagen ya subida. Tolerante a fallos de red."""
    con_tabla = hasattr(obj, "images") and not hasattr(type(obj), "image")   # Anime/Manga/Person/Character: XImage
    if not con_tabla and getattr(obj, "image", None) and obj.image.name:
        return None
    if con_tabla and any(f.image and f.image.name for f in obj.images.all()):
        return None
    imgs = (raw or {}).get("images") or {}
    webp, jpg = imgs.get("webp") or {}, imgs.get("jpg") or {}
    # anime/manga usan large_image_url; personas/personajes usan image_url.
    url = (webp.get("large_image_url") or jpg.get("large_image_url")
           or webp.get("image_url") or jpg.get("image_url"))
    if not url:
        return None
    stem = getattr(obj, "slug", None) or getattr(obj, "mal_id", None) or obj.pk
    try:
        r = requests.get(url, timeout=TIMEOUT_PORTADA)
        if r.status_code != 200 or not r.content:
            log(LogLevel.WARNING, f"cover {obj}", f"HTTP {r.status_code}")
            return None
        ext = ".webp" if "webp" in url else ".jpg"
        if con_tabla:
            portada(obj, url, contenido=r.content, nombre=f"{stem}{ext}")
        else:
            obj.image.save(f"{stem}{ext}", ContentFile(r.content), save=True)
        return url
    except requests.RequestException as exc:
        log(LogLevel.WARNING, f"cover {obj}", exc)
        return None


# ----------------------------- ANIME (formato del dump) -----------------------------
# Regla: se ENLAZA lo que ya existe y lo que no, se omite (nada de compañías, personajes ni personas fantasma).
# Las relaciones con otras obras van por mal_id (Relation no apunta a la obra): valen aunque la otra aún no esté.
def _entero(valor):
    """«26» / 26 / «Unknown» → 26 / 26 / 0."""
    try:
        return max(int(str(valor).strip()), 0)
    except (TypeError, ValueError):
        return 0


def _fecha_partes(bloque):
    """`startDate`/`endDate` del dump: {"year": 1998, "month": 4, "day": 3} → date. Sin mes o día, el 1."""
    bloque = bloque or {}
    try:
        return date(int(bloque["year"]), int(bloque.get("month") or 1), int(bloque.get("day") or 1))
    except (KeyError, TypeError, ValueError):
        return None


def _nombres(lista):
    """Taxonomías del dump: lista de textos (o de objetos con `name`) → nombres limpios."""
    return [str(x.get("name") if isinstance(x, dict) else x).strip() for x in lista or [] if x]


def _id_mal(entrada, que):
    """El id de MAL de una referencia del dump: `<que>_mal_id` (formato actual) o `<que>_id`."""
    valor = entrada.get(f"{que}_mal_id", entrada.get(f"{que}_id"))
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


IDIOMAS_ALIAS = {"mandarin": "Chinese", "cantonese": "Chinese", "taiwanese": "Chinese"}


def _idiomas():
    """Buscador de idioma con caché por procesado: «Portuguese (BR)» → Portuguese; lo que no existe → None (no se crea)."""
    cache = {}

    def buscar(nombre):
        nombre = str(nombre or "").strip()
        if nombre not in cache:
            base = re.sub(r"\s*\(.*?\)\s*", "", nombre).strip()
            base = IDIOMAS_ALIAS.get(base.lower(), base)
            cache[nombre] = Language.objects.filter(name__iexact=base).first() if base else None
        return cache[nombre]
    return buscar


def _personajes_y_voces(anime, entradas):
    """`characters` del dump → AnimeCharacter (con su rol) y CharacterVoice (persona + idioma), SOLO con los personajes y
    personas que ya existen (se buscan todos los ids de una vez). Lo que falta se omite: al reprocesar se completa."""
    entradas = [e for e in entradas or [] if isinstance(e, dict) and _id_mal(e, "character")]
    ids_pj = {_id_mal(e, "character") for e in entradas}
    ids_voz = {_id_mal(v, "person") for e in entradas for v in e.get("voices") or [] if isinstance(v, dict)} - {None}
    personajes = {c.mal_id: c for c in Character.objects.filter(mal_id__in=ids_pj)}
    personas = dict(PersonMAL.objects.filter(mal_id__in=ids_voz).values_list("mal_id", "person_id"))
    idioma = _idiomas()
    enlazados = voces = 0
    for e in entradas:
        personaje = personajes.get(_id_mal(e, "character"))
        if personaje is None:
            continue
        AnimeCharacter.objects.get_or_create(anime=anime, character=personaje, role=_role(e.get("role")))
        enlazados += 1
        for v in e.get("voices") or []:
            persona, lengua = personas.get(_id_mal(v, "person")), idioma(v.get("language"))
            if persona and lengua:
                CharacterVoice.objects.get_or_create(person_id=persona, character=personaje, language=lengua)
                voces += 1
    return enlazados, len(entradas), voces


def _equipo(anime, entradas):
    """`staff` del dump → un AnimeStaff por cada cargo de `positions`, SOLO con las personas que ya existen."""
    entradas = [e for e in entradas or [] if isinstance(e, dict) and _id_mal(e, "person")]
    personas = dict(PersonMAL.objects.filter(mal_id__in={_id_mal(e, "person") for e in entradas}).values_list("mal_id", "person_id"))
    hechos = 0
    for e in entradas:
        persona = personas.get(_id_mal(e, "person"))
        if persona is None:
            continue
        for cargo in e.get("positions") or [None]:
            AnimeStaff.objects.get_or_create(anime=anime, person_id=persona, role=_role(cargo))
        hechos += 1
    return hechos, len(entradas)


def _companias_mal(entradas):
    """Compañías del dump ({"company_id", "name"}) → las que YA existen por su ficha MAL, en una consulta."""
    ids = [_id_mal(e, "company") for e in entradas or [] if isinstance(e, dict)]
    ids = [i for i in ids if i]
    if not ids:
        return []
    return list(Company.objects.filter(company_mal__kind=MalCompanyKind.COMPANY, company_mal__mal_id__in=ids))


def _titulos_dump(entity, title_model, fk_name, titles):
    """`titles` del dump: [{"lang": "english", "titles": [...]}]. El idioma se busca por nombre; si no existe, se omite."""
    for grupo in titles or []:
        lang = Language.objects.filter(name__iexact=str(grupo.get("lang") or "").strip()).first()
        if lang is None:
            continue
        for texto in grupo.get("titles") or []:
            texto = (texto or "").strip()
            if texto:
                title_model.objects.get_or_create(**{fk_name: entity, "title_lang": lang, "title": texto[:500]})


def _imagenes_pendientes(obj, portada_url, extras):
    """La portada (orden 0) y las extra, sin repetir, como filas con URL pendientes de descarga (no se baja nada aquí:
    las baja «Descargar imágenes pendientes», por lotes). Las que ya estaban no se duplican."""
    urls = [u for u in [portada_url, *(extras or [])] if u]
    ya = set(obj.images.values_list("image_url", flat=True))
    nuevas, vistas = [], set()
    for orden, url in enumerate(urls):
        if url in vistas or url in ya:
            continue
        vistas.add(url)
        nuevas.append(obj.images.model(**{obj.images.field.name: obj, "image_url": url[:2000], "order": orden}))
    obj.images.model.objects.bulk_create(nuevas)


def _canciones_dump(anime, ost):
    """`ost` del dump: {"openings": [{"number", "title", "artist"}], "endings": [...]}. Guarda el crédito del artista
    TAL CUAL (texto) y no enlaza artistas: con millones de canciones un enlace por nombre dejaría la masa mal enlazada;
    el enlace a Música se hace a mano desde la canción."""
    for clave, tipo in (("openings", AnimeSongType.OPENING), ("endings", AnimeSongType.ENDING)):
        for n, cancion in enumerate((ost or {}).get(clave) or [], 1):
            if not isinstance(cancion, dict):
                cancion = {"title": str(cancion or "")}
            titulo = (cancion.get("title") or "").strip()
            if titulo:
                AnimeSong.objects.update_or_create(anime=anime, type=tipo, song_id=_entero(cancion.get("number")) or n,
                                                   title=titulo[:255],
                                                   defaults={"artist_credit": (cancion.get("artist") or "").strip()[:500]})


def process_anime(mal_id):
    """DataMalAnime (registro del dump) → Anime, sus taxonomías, compañías existentes, títulos, relaciones,
    canciones e imágenes pendientes. Idempotente: reprocesar no duplica."""
    row = DataMalAnime.objects.filter(mal_id=mal_id, data_status=True).first()
    if not row:
        return None
    d = row.data or {}
    desde = _fecha_partes(d.get("startDate"))
    anime, _ = Anime.objects.update_or_create(mal_id=mal_id, defaults={
        "title": (d.get("title") or f"Anime {mal_id}")[:500],
        "title_eng": (d.get("english_title") or "")[:500],
        "synopsis": d.get("synopsis") or "",
        "episodes": _entero(d.get("episodes")),
        "year": desde.year if desde else None,
        "anime_type": _cat(Type, d.get("type")),
        "status": _cat(Status, d.get("status")),
        "source": _cat(Source, d.get("source")),
        "rating": _rating(d.get("rating")),
        "from_date": desde,                         # save() calcula la temporada
        "to_date": _fecha_partes(d.get("endDate")),
    })
    anime.genres.set([g for g in (_cat(Genre, n) for n in _nombres(d.get("genres"))) if g])
    anime.themes.set([t for t in (_cat(Theme, n) for n in _nombres(d.get("themes"))) if t])
    anime.demographics.set([x for x in (_cat(Demographic, n) for n in _nombres(d.get("demographics"))) if x])
    anime.studios.set(_companias_mal(d.get("studios")))
    anime.producers.set(_companias_mal(d.get("producers")))
    anime.licensors.set(_companias_mal(d.get("licensors")))
    _titulos_dump(anime, AnimeTitle, "anime", d.get("titles"))
    _relations(RelationMedia.ANIME, mal_id, d.get("relations"))
    _canciones_dump(anime, d.get("ost"))
    _imagenes_pendientes(anime, d.get("image_url"), d.get("images_extra"))
    pj, pj_total, voces = _personajes_y_voces(anime, d.get("characters"))
    eq, eq_total = _equipo(anime, d.get("staff"))
    row.data_processed = True
    row.save(update_fields=["data_processed", "updated_at"])
    log(LogLevel.INFO, f"process anime #{mal_id}", f"{anime.title} · personajes {pj}/{pj_total} ({voces} voces) · staff {eq}/{eq_total}"
                                                   + (" · faltan fichas: reprocesa cuando se carguen" if pj < pj_total or eq < eq_total else ""))
    return anime


# ----------------------------- MANGA -----------------------------
def process_manga(mal_id):
    """DataMalManga (+ su tabla de personajes) → Manga real y sus relaciones."""
    row = DataMalManga.objects.filter(mal_id=mal_id, data_status=True).first()
    if not row:
        return None
    full = row.data or {}
    manga, _ = Manga.objects.update_or_create(mal_id=mal_id, defaults={
        "title": (full.get("title") or f"Manga {mal_id}")[:500],
        "title_eng": (full.get("title_english") or "")[:500],
        "title_jap": (full.get("title_japanese") or "")[:500],
        "synopsis": full.get("synopsis") or "",
        "chapters": full.get("chapters") or 0,
        "volumes": full.get("volumes") or 0,
        "manga_type": _cat(Type, full.get("type")),
        "status": _cat(Status, full.get("status")),
        "from_date": _fecha(full.get("published")),        # save() calcula la temporada
        "to_date": _fecha(full.get("published"), "to"),
    })
    _cover(manga, full)
    for g in full.get("genres", []):
        manga.genres.add(_cat(Genre, g.get("name")))
    for t in full.get("themes", []):
        manga.themes.add(_cat(Theme, t.get("name")))
    for d in full.get("demographics", []):
        manga.demographics.add(_cat(Demographic, d.get("name")))
    for s in full.get("serializations", []):
        manga.serializations.add(_company(s, MalCompanyKind.MAGAZINE))
    _titles(manga, MangaTitle, "manga", full.get("titles"))
    _relations(RelationMedia.MANGA, mal_id, full.get("relations"))
    for author in full.get("authors", []):
        person = _person(author)
        if person:
            MangaAuthor.objects.get_or_create(manga=manga, person=person, role=None)
    crow = DataMalMangaCharacter.objects.filter(mal_id=mal_id, data_status=True).first()
    if crow:
        _manga_characters(manga, crow.data)
        _mark(DataMalMangaCharacter, mal_id)
    row.data_processed = True
    row.save(update_fields=["data_processed"])
    log(LogLevel.INFO, f"process manga #{mal_id}", manga.title)
    return manga


def _manga_characters(manga, chars):
    for c in chars or []:
        cdata = c.get("character") or {}
        cid = cdata.get("mal_id")
        if not cid:
            continue
        ch, _ = Character.objects.get_or_create(
            mal_id=cid, defaults={"full_name": (cdata.get("name") or f"Personaje {cid}")[:255]})
        MangaCharacter.objects.get_or_create(manga=manga, character=ch, role=_role(c.get("role")))


# ----------------------------- PERSONAJE -----------------------------
def process_character(mal_id):
    row = DataMalCharacter.objects.filter(mal_id=mal_id, data_status=True).first()
    if not row:
        return None
    d = row.data or {}
    ch, _ = Character.objects.update_or_create(mal_id=mal_id, defaults={
        "full_name": (d.get("name") or f"Personaje {mal_id}")[:255],
        "name_kanji": (d.get("name_kanji") or "")[:255],
        "biography": d.get("about") or "",
    })
    _cover(ch, d)
    _mark(DataMalCharacter, mal_id)
    return ch


# ----------------------------- PERSONA -----------------------------
def process_person(mal_id):
    row = DataMalPerson.objects.filter(mal_id=mal_id, data_status=True).first()
    if not row:
        return None
    d = row.data or {}
    # Servicio único (mismo que el formulario del panel): persona neutra (solo rellena lo vacío) + ficha MAL.
    p, _ext, _ = upsert_persona_mal({**d, "mal_id": mal_id})
    _cover(p, d)
    _mark(DataMalPerson, mal_id)
    return p


# ----------------------------- pendientes -----------------------------
LOTE = 500
PROCESADORES = {"anime": (DataMalAnime, process_anime), "manga": (DataMalManga, process_manga),
                "character": (DataMalCharacter, process_character), "person": (DataMalPerson, process_person)}


def pendientes(tipo):
    """Cuántas filas de ese tipo esperan proceso (fetch OK y sin procesar)."""
    return PROCESADORES[tipo][0].objects.filter(data_status=True, data_processed=False).count()


def procesar_lote(tipo, cantidad=0):
    """Procesa hasta `cantidad` pendientes de UN tipo (0 = todos), recorriendo por `mal_id` de a LOTE: nunca carga la
    lista entera. Entre lotes mira si pidieron cancelar (lo hecho queda hecho). Un error en una fila se anota y se sigue.
    Devuelve cuántas quedaron procesadas."""
    from core.shared.tasks.cancel import avance, cancelado

    modelo, fn = PROCESADORES[tipo]
    cantidad = max(int(cantidad or 0), 0)
    ultimo, hechos, errores, vistos = 0, 0, 0, 0
    total = pendientes(tipo) if cantidad == 0 else min(cantidad, pendientes(tipo))
    avance(0, total)
    while cantidad == 0 or vistos < cantidad:
        if cancelado():
            log(LogLevel.WARNING, f"procesar {tipo}", f"detenido por el usuario tras {vistos}; lo procesado se queda")
            break
        tope = LOTE if cantidad == 0 else min(LOTE, cantidad - vistos)
        ids = list(modelo.objects.filter(data_status=True, data_processed=False, mal_id__gt=ultimo)
                   .order_by("mal_id").values_list("mal_id", flat=True)[:tope])
        if not ids:
            break
        for mid in ids:
            try:
                if fn(mid) is not None:
                    hechos += 1
            except Exception as exc:  # noqa: BLE001 — no cortar el lote por una fila
                errores += 1
                log(LogLevel.ERROR, f"procesar {tipo} #{mid}", exc)
        vistos += len(ids)
        ultimo = ids[-1]
        avance(vistos, total)
    log(LogLevel.INFO, f"procesar {tipo}", f"{hechos} procesados de {vistos} · {errores} con error · quedan {pendientes(tipo)} pendientes")
    return hechos


def process_pending(limit_per_model=None):
    """Procesa lo pendiente de las cuatro tablas principales (hasta `limit_per_model` por tabla)."""
    return sum(procesar_lote(tipo, limit_per_model or 0) for tipo in ("person", "character", "anime", "manga"))
