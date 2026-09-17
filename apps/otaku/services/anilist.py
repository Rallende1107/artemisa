"""IMPORTAR desde AniList (API GraphQL, https://graphql.anilist.co) → tablas `DataAnilist*`. Solo DESCARGA: deja el
JSON crudo; convertirlo en Anime / Manga / Persona / Personaje es otro paso (procesar).

Tres formas, las mismas para los cuatro tipos (anime, manga, person = Staff, character):
  · `importar_uno(tipo, id)`            — un id (consulta completa, con personajes y staff de la obra).
  · `importar_rango(tipo, desde, hasta)` — un rango de ids, de a 50 por petición (`id_in`); salta lo ya descargado.
  · `barrer(tipo, desde_pagina, paginas)` — el catálogo por páginas de 50, ordenado por id.

Pensado para volumen: una petición trae 50 filas y se guardan con UN `bulk_create(update_conflicts=True)`.
AniList limita por minuto (90 documentados, a veces 30): se espera entre peticiones y, ante 429, se respeta
`Retry-After`. Cancelable entre peticiones desde Tareas.
"""
from __future__ import annotations

import time
from collections.abc import Iterable

import requests
from django.utils import timezone

from apps.otaku.models import DataAnilistAnime, DataAnilistCharacter, DataAnilistManga, DataAnilistPerson, OtakuLog
from core.shared.models.choices import LogLevel
from core.shared.tasks.cancel import cancelado
from core.utils.importlog import log_to


URL = "https://graphql.anilist.co"
TIMEOUT = 30
POR_PAGINA = 50                 # el máximo de AniList por página
ESPERA = 2.1                    # segundos entre peticiones: ~28 por minuto, bajo el límite reducido de 30
REINTENTOS = 5
_stats = {"peticiones": 0}
_ultima = {"t": 0.0}


def log(nivel: str, proceso: str, mensaje: object = "") -> OtakuLog:
    return log_to(OtakuLog, nivel, proceso, mensaje)


def peticiones() -> int:
    """Contador de peticiones (para el resumen de `sin_ruido`)."""
    return _stats["peticiones"]


# ------------------------------------------------------------------ campos por tipo
MEDIA = """
  id idMal type format status countryOfOrigin source isAdult siteUrl updatedAt
  title { romaji english native userPreferred } synonyms
  description(asHtml: false)
  startDate { year month day } endDate { year month day } season seasonYear
  episodes duration chapters volumes
  genres tags { name rank isAdult isMediaSpoiler }
  averageScore meanScore popularity favourites
  coverImage { extraLarge large color } bannerImage
  trailer { id site }
  studios { edges { isMain node { id name isAnimationStudio siteUrl } } }
  relations { edges { relationType(version: 2) node { id idMal type format } } }
  externalLinks { url site type language }
"""
MEDIA_COMPLETO = MEDIA + """
  characters(perPage: 25, sort: [ROLE, RELEVANCE]) { edges { role node { id } voiceActors { id languageV2 } } }
  staff(perPage: 25, sort: [RELEVANCE]) { edges { role node { id } } }
"""
STAFF = """
  id siteUrl languageV2 gender age bloodType homeTown yearsActive primaryOccupations favourites
  name { full native alternative userPreferred }
  image { large medium }
  description(asHtml: false)
  dateOfBirth { year month day } dateOfDeath { year month day }
"""
CHARACTER = """
  id siteUrl gender age bloodType favourites
  name { full native alternative alternativeSpoiler userPreferred }
  image { large medium }
  description(asHtml: false)
  dateOfBirth { year month day }
"""

TIPOS = {  # tipo → (modelo, campo raíz de Page, consulta de uno, filtro extra, campos, campos de la consulta de uno)
    "anime": (DataAnilistAnime, "media", "Media", "type: ANIME", MEDIA, MEDIA_COMPLETO),
    "manga": (DataAnilistManga, "media", "Media", "type: MANGA", MEDIA, MEDIA_COMPLETO),
    "person": (DataAnilistPerson, "staff", "Staff", "", STAFF, STAFF),
    "character": (DataAnilistCharacter, "characters", "Character", "", CHARACTER, CHARACTER),
}


def _extra(filtro: str) -> str:
    return f", {filtro}" if filtro else ""


def consulta_uno(tipo: str) -> str:
    _m, _raiz, uno, filtro, _campos, completos = TIPOS[tipo]
    return f"query ($id: Int) {{ {uno}(id: $id{_extra(filtro)}) {{ {completos} }} }}"


def consulta_pagina(tipo: str) -> str:
    _m, raiz, _uno, filtro, campos, _c = TIPOS[tipo]
    return ("query ($page: Int, $perPage: Int) { Page(page: $page, perPage: $perPage) { "
            "pageInfo { total currentPage lastPage hasNextPage perPage } "
            f"{raiz}(sort: ID{_extra(filtro)}) {{ {campos} }} }} }}")


def consulta_ids(tipo: str) -> str:
    _m, raiz, _uno, filtro, campos, _c = TIPOS[tipo]
    return ("query ($ids: [Int], $perPage: Int) { Page(page: 1, perPage: $perPage) { "
            f"{raiz}(id_in: $ids{_extra(filtro)}) {{ {campos} }} }} }}")


# ------------------------------------------------------------------ la petición
def _esperar() -> None:
    falta = ESPERA - (time.monotonic() - _ultima["t"])
    if falta > 0:
        time.sleep(falta)
    _ultima["t"] = time.monotonic()


def _pedir(query: str, variables: dict, quien: str) -> tuple[int, dict | None]:
    """POST GraphQL → (HTTP, data | None). 404 = no existe (no se reintenta); 429 y 5xx se reintentan."""
    pausa = ESPERA
    for intento in range(1, REINTENTOS + 1):
        _esperar()
        _stats["peticiones"] += 1
        try:
            r = requests.post(URL, json={"query": query, "variables": variables}, timeout=TIMEOUT,
                              headers={"Content-Type": "application/json", "Accept": "application/json"})
        except requests.RequestException as exc:
            if intento == REINTENTOS:
                log(LogLevel.ERROR, quien, f"{type(exc).__name__}: {exc} (tras {REINTENTOS} intentos)")
                return 0, None
            log(LogLevel.WARNING, quien, f"{type(exc).__name__}: {exc}; reintento {intento}/{REINTENTOS - 1} en {pausa:.0f} s")
            time.sleep(pausa)
            pausa *= 2
            continue
        if r.status_code == 200:
            cuerpo = r.json() or {}
            return 200, cuerpo.get("data")
        if r.status_code == 404:
            return 404, None
        if r.status_code == 429 or r.status_code >= 500:
            if intento == REINTENTOS:
                log(LogLevel.WARNING, quien, f"HTTP {r.status_code} tras {REINTENTOS} intentos")
                return r.status_code, None
            try:
                espera = float(r.headers.get("Retry-After") or pausa)
            except ValueError:
                espera = pausa
            log(LogLevel.WARNING, quien, f"HTTP {r.status_code}; reintento {intento}/{REINTENTOS - 1} en {espera:.0f} s")
            time.sleep(espera)
            pausa *= 2
            continue
        log(LogLevel.ERROR, quien, f"HTTP {r.status_code}: {r.text[:300]}")
        return r.status_code, None
    return 0, None


# ------------------------------------------------------------------ guardar (por lotes)
def _guardar(tipo: str, items: Iterable[dict], code: int) -> list[int]:
    """Upsert de las filas recibidas en UNA consulta. Lo re-descargado vuelve a quedar sin procesar."""
    modelo = TIPOS[tipo][0]
    ahora = timezone.now()
    filas = [modelo(anilist_id=it["id"], id_mal=it.get("idMal"), url=it.get("siteUrl") or "", data=it,
                    data_status=True, data_processed=False, status_code=code, updated_at=ahora)
             for it in items if isinstance(it, dict) and it.get("id")]
    if filas:
        modelo.objects.bulk_create(filas, batch_size=POR_PAGINA, update_conflicts=True, unique_fields=["anilist_id"],
                                   update_fields=["id_mal", "url", "data", "data_status", "data_processed", "status_code", "updated_at"])
    return [f.anilist_id for f in filas]


def _marcar_inexistentes(tipo: str, ids: Iterable[int], code: int) -> None:
    """Ids pedidos que AniList no devolvió: una fila sin datos (fetch KO) para no volver a pedirlos a ciegas."""
    modelo = TIPOS[tipo][0]
    modelo.objects.bulk_create([modelo(anilist_id=i, data_status=False, status_code=code) for i in ids],
                               batch_size=500, ignore_conflicts=True)


def ya_descargados(tipo: str, desde: int, hasta: int) -> set[int]:
    return set(TIPOS[tipo][0].objects.filter(anilist_id__range=(desde, hasta), data_status=True)
               .values_list("anilist_id", flat=True))


# ------------------------------------------------------------------ las tres formas
def importar_uno(tipo: str, anilist_id: int) -> int:
    """Un id, con la consulta completa. Devuelve 1 si lo guardó, 0 si no existe o falló."""
    quien = f"anilist {tipo} #{anilist_id}"
    code, data = _pedir(consulta_uno(tipo), {"id": anilist_id}, quien)
    item = (data or {}).get(TIPOS[tipo][2])
    if not item:
        _marcar_inexistentes(tipo, [anilist_id], code or 404)
        log(LogLevel.WARNING, quien, f"sin datos (HTTP {code})")
        return 0
    _guardar(tipo, [item], code)
    return 1


def importar_ids(tipo: str, ids: Iterable[int]) -> int:
    """Una lista de ids, de a 50 por petición. Devuelve cuántos guardó."""
    ids = sorted({int(i) for i in ids})
    guardados = 0
    for n in range(0, len(ids), POR_PAGINA):
        if cancelado():
            log(LogLevel.WARNING, f"anilist {tipo}", "detenido por el usuario; lo guardado se queda")
            break
        lote = ids[n:n + POR_PAGINA]
        code, data = _pedir(consulta_ids(tipo), {"ids": lote, "perPage": POR_PAGINA}, f"anilist {tipo} ids {lote[0]}-{lote[-1]}")
        if data is None:
            continue
        items = ((data.get("Page") or {}).get(TIPOS[tipo][1])) or []
        hechos = _guardar(tipo, items, code)
        _marcar_inexistentes(tipo, set(lote) - set(hechos), 404)
        guardados += len(hechos)
    return guardados


def importar_rango(tipo: str, desde: int, hasta: int) -> int:
    """Los ids [desde, hasta] que aún no estén descargados."""
    ya = ya_descargados(tipo, desde, hasta)
    faltan = [i for i in range(desde, hasta + 1) if i not in ya]
    if ya:
        log(LogLevel.INFO, f"anilist {tipo} [{desde}-{hasta}]", f"{len(ya)} ya descargados: se saltan")
    hechos = importar_ids(tipo, faltan)
    log(LogLevel.INFO, f"anilist {tipo} [{desde}-{hasta}]", f"{hechos} guardados de {len(faltan)} pedidos")
    return hechos


def barrer(tipo: str, desde_pagina: int = 1, paginas: int = 1, al_avanzar=None) -> tuple[int, int, bool]:
    """Páginas de 50 del catálogo ordenado por id. `paginas=0` = hasta agotar el catálogo.
    `al_avanzar(pagina)` se llama tras guardar cada página (para mover el cursor). → (guardados, siguiente página, quedan más)."""
    guardados, pagina, mas, hechas = 0, desde_pagina, True, 0
    while mas and (paginas == 0 or hechas < paginas):
        if cancelado():
            log(LogLevel.WARNING, f"anilist barrido {tipo}", f"detenido por el usuario en la página {pagina}; lo guardado se queda")
            break
        code, data = _pedir(consulta_pagina(tipo), {"page": pagina, "perPage": POR_PAGINA}, f"anilist barrido {tipo} página {pagina}")
        if data is None:
            log(LogLevel.WARNING, f"anilist barrido {tipo} página {pagina}", f"sin respuesta (HTTP {code})")
            break
        page = data.get("Page") or {}
        guardados += len(_guardar(tipo, page.get(TIPOS[tipo][1]) or [], code))
        mas = bool((page.get("pageInfo") or {}).get("hasNextPage"))
        pagina += 1
        hechas += 1
        if al_avanzar:
            al_avanzar(pagina)
    log(LogLevel.INFO, f"anilist barrido {tipo} páginas {desde_pagina}-{pagina - 1}",
        f"{guardados} filas al crudo · {'quedan más' if mas else 'catálogo agotado'}")
    return guardados, pagina, mas
