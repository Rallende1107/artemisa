"""Tareas Celery de importación VNDB (antes en apps/imports/tasks.py). El servicio vive en
apps/games/services/vndb.py. Con CELERY_ENABLED van a background; si no, corren síncronas."""
from celery import shared_task

from apps.games.models import DataVndbCharacter, DataVndbCreator, DataVndbGame, DataVndbRelease, GameLog
from apps.games.services import vndb
from core.shared.models.choices import LogLevel
from core.utils.importlog import sin_ruido


@shared_task
def import_game_task(vndb_id):
    return str(vndb.import_game(vndb_id))


@shared_task
def import_creator_task(vndb_id, deep=False):
    """El creador; con `deep`, también todos sus juegos."""
    return str(vndb.import_creator(vndb_id, deep=deep))


@shared_task
def import_creator_games_task(vndb_ids):
    """Todos los juegos de cada creador marcado (acción masiva en Creadores)."""
    return vndb.import_creator_games(list(vndb_ids))


@shared_task
def import_character_task(vndb_id):
    return str(vndb.import_character(vndb_id))


@shared_task
def import_release_task(vndb_id):
    return str(vndb.import_release(vndb_id))


@shared_task
def refresh_stale_games_task(days=30, cantidad=20):
    """Re-obtiene juegos viejos de VNDB (con sus lanzamientos, personajes y editoras)."""
    return vndb.refrescar_juegos_viejos(days=days, cantidad=cantidad)


@shared_task
def import_vndb_range_task(kind, start, end):
    return sin_ruido(GameLog, f"rango {kind} [{start}-{end}]", vndb.import_range, kind, start, end,
                     peticiones=lambda: vndb._stats["peticiones"])


@shared_task
def barrer_vndb_task(kind, desde_pagina=None, paginas=10, procesar=True):
    """BARRIDO por páginas de 100 del catálogo de `kind` (juego, creador, lanzamiento, personaje). `desde_pagina` vacío
    = la próxima página del cursor «<kind>-pagina». El cursor avanza PÁGINA A PÁGINA (si se cancela, lo hecho queda
    anotado). Con `procesar` se procesa en local lo traído al terminar (devuelve cuántas quedaron armadas); sin él
    solo se deja en el crudo (devuelve cuántas filas bajó). `paginas=0` = sin tope, hasta agotar el catálogo."""
    return sin_ruido(GameLog, f"barrido {kind} desde {desde_pagina or 'el cursor'}",
                     _barrer, kind, desde_pagina, paginas, procesar,
                     peticiones=lambda: vndb._stats["peticiones"])


def _barrer(kind, desde_pagina, paginas, procesar):
    from core.shared.tasks.cancel import cancelado, reentregada
    from core.shared.tasks.cursor import avanzar, siguiente
    cursor = f"{kind}-pagina"
    pagina = int(desde_pagina or siguiente("vndb", cursor))
    if reentregada() and siguiente("vndb", cursor) > pagina:
        # el worker murió a mitad (acks_late) y Redis nos reentregó el mismo mensaje con la página ORIGINAL:
        # seguir por el cursor, que es hasta donde llegó de verdad, en vez de volver a barrer desde el principio
        vndb.log(LogLevel.INFO, f"barrido {kind}", f"reentregado tras caída del worker: sigue por la página {siguiente('vndb', cursor)}, no por la {pagina}")
        pagina = siguiente("vndb", cursor)
    total = 0
    paginas = int(paginas or 0)                  # 0 = «traerlos todos»: hasta que VNDB diga que no quedan más (o se cancele)
    hechas = 0
    while paginas == 0 or hechas < paginas:
        if cancelado():
            break
        hechas += 1
        nuevos, siguiente_pagina, mas = vndb.barrer(kind, desde_pagina=pagina, paginas=1)
        # con `procesar`, cada página se arma NADA MÁS bajarla (no al final de todas): lo hecho queda hecho si se cancela
        total += vndb.procesar_ids(kind, nuevos) if procesar else len(nuevos)
        if siguiente_pagina == pagina:           # sin respuesta: no avanzar
            break
        avanzar("vndb", cursor, pagina)           # próxima = pagina + 1
        pagina = siguiente_pagina
        if not mas:
            break
    return total


@shared_task
def process_vndb_task(kind, cantidad=0):
    """Procesa `cantidad` pendientes de UN tipo de VNDB (0 = todos), por lotes y cancelable desde Tareas."""
    return sin_ruido(GameLog, f"procesar {kind}", vndb.procesar_lote, kind, cantidad)


@shared_task
def process_games_pending_task(limit=None):
    return sin_ruido(GameLog, "procesar pendientes", vndb.process_pending, limit)


@shared_task
def import_vndb_ids_task(kind, ids):
    """Lista de ids cargada desde un archivo (CSV / Excel / SQLite)."""
    return sin_ruido(GameLog, f"lista {kind} ({len(ids)} ids)", vndb.import_ids, kind, ids,
                     peticiones=lambda: vndb._stats["peticiones"])


# ----------------------------- programable: «obtener datos de X una vez al día» -----------------------------
_SIGUIENTE = {"juego": DataVndbGame, "creador": DataVndbCreator, "personaje": DataVndbCharacter, "lanzamiento": DataVndbRelease}     # tipo → tabla Data donde mirar por dónde íbamos


@shared_task
def import_vndb_next_batch_task(kind, cantidad=None):
    """El SIGUIENTE LOTE de un tipo: desde el cursor del lote (system.ImportCursor), `cantidad` ids
    (el «seguir donde me quedé» de Poseidon, pero programado: p. ej. 50 al día desde el panel de
    tareas programadas). Devuelve cuántos importó."""
    from core.shared.tasks.cursor import avanzar, cantidad_de, siguiente
    if kind not in _SIGUIENTE:
        return 0
    cantidad = cantidad_de("vndb", kind, cantidad)   # la de la programada o, si no, la del cursor
    if cantidad < 1:
        return 0
    inicio = siguiente("vndb", kind)            # el CURSOR del lote, no el mayor id descargado
    fin = inicio + int(cantidad) - 1
    hechos = vndb.import_range(kind, inicio, fin)
    avanzar("vndb", kind, fin)
    return hechos
