"""Tareas Celery de otaku. Con CELERY_ENABLED van a background; si no, corren síncronas.

  · MAL: procesar lo ya cargado desde los dumps (`services/mal_dump_process.py`). De MAL no se descarga nada.
  · AniList: importar desde la API (`services/anilist.py`) a las tablas DataAnilist*.
"""
from celery import shared_task

from apps.otaku.services import mal_dump_process


# ----------------------------- MAL (procesar: tablas DataMal* → entidades) -----------------------------
@shared_task
def process_otaku_pending_task(limit=None):
    return mal_dump_process.process_pending(limit_per_model=limit)


@shared_task
def process_mal_task(kind, cantidad=0):
    """Procesa `cantidad` pendientes de UN tipo de MAL (0 = todos), por lotes y cancelable desde Tareas."""
    from apps.otaku.models import OtakuLog
    from core.utils.importlog import sin_ruido
    return sin_ruido(OtakuLog, f"procesar {kind} (MAL)", mal_dump_process.procesar_lote, kind, cantidad)


# ----------------------------- AniList (importar: API en vivo → tablas DataAnilist*) -----------------------------
@shared_task
def import_anilist_id_task(kind, anilist_id):
    """Un id de AniList al crudo."""
    from apps.otaku.models import OtakuLog
    from apps.otaku.services import anilist
    from core.utils.importlog import sin_ruido
    return sin_ruido(OtakuLog, f"anilist {kind} #{anilist_id}", anilist.importar_uno, kind, int(anilist_id),
                     peticiones=anilist.peticiones)


@shared_task
def import_anilist_range_task(kind, start, end):
    """Un rango de ids de AniList al crudo (de a 50 por petición; salta lo ya descargado)."""
    from apps.otaku.models import OtakuLog
    from apps.otaku.services import anilist
    from core.utils.importlog import sin_ruido
    return sin_ruido(OtakuLog, f"anilist rango {kind} [{start}-{end}]", anilist.importar_rango, kind, int(start), int(end),
                     peticiones=anilist.peticiones)


@shared_task
def import_anilist_ids_task(kind, ids):
    """Una lista de ids de AniList al crudo («Volver a descargar» de la lista)."""
    from apps.otaku.models import OtakuLog
    from apps.otaku.services import anilist
    from core.utils.importlog import sin_ruido
    return sin_ruido(OtakuLog, f"anilist {kind} ({len(ids)} ids)", anilist.importar_ids, kind, list(ids),
                     peticiones=anilist.peticiones)


@shared_task
def barrer_anilist_task(kind, desde_pagina=None, paginas=10):
    """BARRIDO por páginas de 50 del catálogo de `kind` (anime, manga, person, character). `desde_pagina` vacío = la
    del cursor «<kind>-pagina», que avanza PÁGINA A PÁGINA (si se cancela o se cae el worker, sigue donde quedó).
    `paginas=0` = hasta agotar el catálogo. Devuelve cuántas filas bajó."""
    from apps.otaku.models import OtakuLog
    from apps.otaku.services import anilist
    from core.utils.importlog import sin_ruido
    return sin_ruido(OtakuLog, f"anilist barrido {kind} desde {desde_pagina or 'el cursor'}", _barrer_anilist,
                     kind, desde_pagina, paginas, peticiones=anilist.peticiones)


def _barrer_anilist(kind, desde_pagina, paginas):
    from apps.otaku.services import anilist
    from core.shared.tasks.cancel import reentregada
    from core.shared.tasks.cursor import avanzar, siguiente
    cursor = f"{kind}-pagina"
    pagina = int(desde_pagina or siguiente("anilist", cursor))
    if reentregada() and siguiente("anilist", cursor) > pagina:      # reentregado tras caída: seguir por el cursor
        pagina = siguiente("anilist", cursor)
    guardados, _siguiente, _mas = anilist.barrer(kind, desde_pagina=pagina, paginas=int(paginas or 0),
                                                 al_avanzar=lambda prox: avanzar("anilist", cursor, prox - 1))
    return guardados


@shared_task
def import_anilist_next_batch_task(kind, cantidad=None):
    """El SIGUIENTE LOTE de ids de un tipo desde su cursor (system.ImportCursor «anilist»): lo lanza la tarea
    programada o «Lanzar lote ahora». Devuelve cuántos guardó."""
    from apps.otaku.models import OtakuLog
    from apps.otaku.services import anilist
    from core.shared.tasks.cursor import avanzar, cantidad_de, siguiente
    from core.utils.importlog import sin_ruido
    if kind not in anilist.TIPOS:
        return 0
    cantidad = cantidad_de("anilist", kind, cantidad)
    if cantidad < 1:
        return 0
    inicio = siguiente("anilist", kind)
    fin = inicio + int(cantidad) - 1
    hechos = sin_ruido(OtakuLog, f"anilist lote {kind} [{inicio}-{fin}]", anilist.importar_rango, kind, inicio, fin,
                       peticiones=anilist.peticiones)
    avanzar("anilist", kind, fin)
    return hechos
