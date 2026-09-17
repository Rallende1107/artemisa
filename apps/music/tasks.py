"""Tareas Celery de importación Deezer (antes en apps/imports/tasks.py). El servicio vive en
apps/music/services/deezer.py. Con CELERY_ENABLED van a background; si no, corren síncronas."""
from celery import shared_task

from apps.music.models import DataDeezerAlbum, DataDeezerArtist
from apps.music.services import deezer


@shared_task
def import_artist_task(deezer_id):
    return str(deezer.import_artist(deezer_id))


@shared_task
def import_artist_albums_task(deezer_id_artist, album_ids):
    """Una TANDA de álbumes de un artista (las reparte import_artist cuando pasa de 25): corre aparte."""
    return deezer.import_artist_albums(deezer_id_artist, list(album_ids))


@shared_task
def import_album_task(deezer_id):
    return str(deezer.import_album(deezer_id))


@shared_task
def import_track_task(deezer_id):
    """Una canción por id: trae su álbum entero (ver `deezer.import_track`)."""
    return str(deezer.import_track(deezer_id))


@shared_task
def import_genre_task(deezer_id):
    return str(deezer.import_genre(deezer_id))


@shared_task
def import_all_genres_task():
    """Los 25 géneros de Deezer de una sola llamada (GET /genre), sin ids."""
    return deezer.import_all_genres()


@shared_task
def import_deezer_range_task(kind, start, end):
    return deezer.import_range(kind, start, end)


@shared_task
def process_music_pending_task(limit=None):
    return deezer.process_pending(limit_per_model=limit)


@shared_task
def import_deezer_ids_task(kind, ids):
    """Lista de ids cargada desde un archivo (CSV / Excel / SQLite)."""
    return deezer.import_ids(kind, ids)


# ----------------------------- programable: «obtener datos de X una vez al día» -----------------------------
_SIGUIENTE = {"artista": DataDeezerArtist, "album": DataDeezerAlbum}     # tipo → tabla Data donde mirar por dónde íbamos


@shared_task
def import_deezer_next_batch_task(kind, cantidad=None):
    """El SIGUIENTE LOTE de un tipo: desde el cursor del lote (system.ImportCursor), `cantidad` ids
    (el «seguir donde me quedé» de Poseidon, pero programado: p. ej. 50 al día desde el panel de
    tareas programadas). Devuelve cuántos importó."""
    from core.shared.tasks.cursor import avanzar, cantidad_de, siguiente
    if kind not in _SIGUIENTE:
        return 0
    cantidad = cantidad_de("deezer", kind, cantidad)   # la de la programada o, si no, la del cursor
    if cantidad < 1:
        return 0
    inicio = siguiente("deezer", kind)            # el CURSOR del lote, no el mayor id descargado
    fin = inicio + int(cantidad) - 1
    hechos = deezer.import_range(kind, inicio, fin)
    avanzar("deezer", kind, fin)
    return hechos


@shared_task
def images_from_deezer_task(model_name, ids):
    """«Imagen desde Deezer» (acción masiva en Género y Artista): baja la imagen del JSON ya descargado."""
    return deezer.imagenes_desde_deezer(model_name, list(ids))
