"""REGISTRO del proyecto: los once logs, uno por app, cada uno con su entidad en su panel.
Lo usa la tarea de limpieza de logs informativos (cada log se ve en el home de su app)."""
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import CatalogsLog
from apps.collections.models import CollectionLog
from apps.games.models import GameLog
from apps.mailing.models import EmailLog
from apps.movies.models import MovieLog
from apps.music.models import MusicLog
from apps.otaku.models import OtakuLog
from apps.pages.models import PagesLog
from apps.people.models import PeopleLog
from apps.series.models import SerieLog
from apps.users.models import UserLog


# (etiqueta, ruta de su lista en el panel, modelo)
LOGS = [
    (_("Catálogos"), "panel:catalogs-log_list", CatalogsLog),
    (_("Colecciones"), "panel:collection-log_list", CollectionLog),
    (_("Correo"), "panel:email-log_list", EmailLog),
    (_("Juegos"), "panel:game-log_list", GameLog),
    (_("Música"), "panel:music-log_list", MusicLog),
    (_("Otaku"), "panel:otaku-log_list", OtakuLog),
    (_("Páginas"), "panel:pages-log_list", PagesLog),
    (_("Películas"), "panel:movie-log_list", MovieLog),
    (_("Personas"), "panel:people-log_list", PeopleLog),
    (_("Series"), "panel:serie-log_list", SerieLog),
    (_("Usuarios"), "panel:user-log_list", UserLog),
]


# Nombre LEGIBLE de cada tarea Celery (clave = nombre de la función). Lo usan Ejecuciones y Programadas.
NOMBRES_TAREAS = {
    "dispatch_scheduled_task": "Despachador de programadas (beat)",
    "purge_task_runs_task": "Limpiar ejecuciones terminadas",
    "purge_info_logs_task": "Limpiar logs informativos",
    "download_pending_images_task": "Descargar imágenes pendientes",
    "download_images_task": "Descargar imágenes (marcadas)",
    "upload_pending_to_cloud_task": "Subir imágenes a R2",
    "upload_to_cloud_task": "Subir a R2 (marcadas)",
    "process_music_pending_task": "Procesar pendientes · Deezer",
    "process_otaku_pending_task": "Procesar pendientes · MAL",
    "process_mal_task": "Procesar por tipo · MAL",
    "download_images_batch_task": "Descargar imágenes de una tabla",
    "process_vndb_task": "Procesar por tipo · VNDB",
    "process_games_pending_task": "Procesar pendientes · VNDB",
    "import_all_genres_task": "Importar géneros · Deezer",
    "import_genre_task": "Importar género · Deezer",
    "import_artist_task": "Importar artista · Deezer",
    "import_artist_albums_task": "Tanda de álbumes · Deezer",
    "import_album_task": "Importar álbum · Deezer",
    "import_deezer_range_task": "Lote por rango · Deezer",
    "import_deezer_ids_task": "Lote desde archivo · Deezer",
    "import_deezer_next_batch_task": "Siguiente lote · Deezer",
    "images_from_deezer_task": "Imagen desde Deezer",
    "import_game_task": "Importar juego · VNDB",
    "import_creator_task": "Importar creador · VNDB",
    "import_creator_games_task": "Juegos del creador · VNDB",
    "import_character_task": "Importar personaje · VNDB",
    "import_release_task": "Importar lanzamiento · VNDB",
    "import_vndb_range_task": "Lote por rango · VNDB",
    "barrer_vndb_task": "Barrido por páginas · VNDB",
    "import_vndb_ids_task": "Lote desde archivo · VNDB",
    "import_vndb_next_batch_task": "Siguiente lote · VNDB",
    "refresh_stale_games_task": "Re-obtener juegos viejos · VNDB",
    "process_otaku_pending_task": "Procesar pendientes · MAL",
    "import_anilist_id_task": "Importar por id · AniList",
    "import_anilist_range_task": "Lote por rango · AniList",
    "import_anilist_ids_task": "Lote desde archivo · AniList",
    "barrer_anilist_task": "Barrido por páginas · AniList",
    "import_anilist_next_batch_task": "Siguiente lote · AniList",
}


def nombre_tarea(ruta):
    """«apps.music.tasks.import_artist_task» → «Importar artista · Deezer» (o el nombre de la función si no está en la lista)."""
    corto = (ruta or "").rsplit(".", 1)[-1]
    return NOMBRES_TAREAS.get(corto, corto)
