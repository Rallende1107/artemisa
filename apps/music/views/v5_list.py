"""music · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.music import tasks
from apps.music.views.base import BaseAlbum, BaseAlbumImage, BaseAlbumType, BaseArtist, BaseArtistImage, BaseArtistMember, BaseArtistType, BaseDataDeezerAlbum, BaseDataDeezerArtist, BaseDataDeezerGenre, BaseDataDeezerTrack, BaseGenre, BaseGenreAlias, BaseGenreAliasContext, BaseMusicLog, BaseRole, BaseRoleContext, BaseSong, BaseSongComposer, BaseSongTranslation
from core.shared.views import imports as views_import
from core.shared.views.base import AdminListByView, AdminListView, PublicListView
from core.shared.views.imports import DataBulkMixin


# ==============================================================================
# Gestión
# ==============================================================================


# ---------------------------------------------------------------- «Imagen desde Deezer» (Género y Artista)


class _ImagenDeezer:
    """Acción masiva extra: traer la imagen desde el JSON de Deezer ya descargado (Data*)."""
    extra_bulk_actions = (("imagen-deezer", "Imagen desde Deezer (seleccionadas)"),)

    @classmethod
    def bulk_run(cls, request, accion, qs):
        if accion != "imagen-deezer":
            return False
        ids = list(qs.values_list("pk", flat=True))
        bg, result = views_import.run_task(tasks.images_from_deezer_task, qs.model._meta.model_name, ids)
        views_import.anotar_usuario(result, request.user)
        messages.success(request, f"Imagen desde Deezer para {len(ids)} fila(s): {'encolado' if bg else 'hecho'}.")
        return True


# Vistas FIJAS de «artista» (una URL, una card y un fondo por cada una; sin filtros en página).


class AlbumListView(BaseAlbum, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:album_data"
    create_url = "panel:album_create"
    title = _("Lista de álbumes")


class AlbumImageListView(BaseAlbumImage, AdminListView):
    home_url = "panel:music-home"
    buttons = (("panel:album-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:album-image_data"
    create_url = "panel:album-image_create"
    title = _("Lista de imágenes extra")


class AlbumTypeListView(BaseAlbumType, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:music-album-type_data"
    create_url = "panel:music-album-type_create"
    title = _("Lista de tipos de álbum")


class ArtistListView(BaseArtist, _ImagenDeezer, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:artist_data"
    create_url = "panel:artist_create"
    enable_cards = True   # extra de la vista: botones tarjetas/lista
    title = _("Lista de artistas")


class ArtistImageListView(BaseArtistImage, AdminListView):
    home_url = "panel:music-home"
    buttons = (("panel:artist-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:artist-image_data"
    create_url = "panel:artist-image_create"
    title = _("Lista de imágenes extra")


class ArtistMemberListView(BaseArtistMember, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:artist-member_data"
    create_url = "panel:artist-member_create"
    title = _("Lista de miembros")


class ArtistTypeListView(BaseArtistType, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:music-artist-type_data"
    create_url = "panel:music-artist-type_create"
    title = _("Lista de tipos de artista")


class DataDeezerAlbumListView(BaseDataDeezerAlbum, DataBulkMixin, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:data-deezer-album_data"
    process_url = "panel:deezer-procesar"   # botón «Procesar pendientes» (POST a su vista propia)
    import_url = "panel:deezer-album"   # botón «Importar» → su lanzador
    procesados_url = "panel:album_list"   # botón → las fichas ya procesadas; ahí deja «Procesar pendientes»
    procesados_label = _("Álbumes")
    bulk_process_task = tasks.process_music_pending_task
    bulk_kind = "album"
    bulk_ids_task = tasks.import_deezer_ids_task


# ------------------------ datos crudos de importación (Deezer; antes en apps/imports) ------------------------


class DataDeezerArtistListView(BaseDataDeezerArtist, DataBulkMixin, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:data-deezer-artist_data"
    process_url = "panel:deezer-procesar"   # botón «Procesar pendientes» (POST a su vista propia)
    import_url = "panel:deezer-artist"   # botón «Importar» → su lanzador
    procesados_url = "panel:artist_list"   # botón → las fichas ya procesadas; ahí deja «Procesar pendientes»
    procesados_label = _("Artistas")
    bulk_process_task = tasks.process_music_pending_task
    bulk_kind = "artista"
    bulk_ids_task = tasks.import_deezer_ids_task


class DataDeezerGenreListView(BaseDataDeezerGenre, DataBulkMixin, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:data-deezer-genre_data"
    process_url = "panel:deezer-procesar"   # botón «Procesar pendientes» (POST a su vista propia)
    import_url = "panel:deezer-genres"   # botón «Importar» → su lanzador
    procesados_url = "panel:music-genre_list"   # botón → las fichas ya procesadas
    procesados_label = _("Géneros")
    bulk_process_task = tasks.process_music_pending_task


class DataDeezerTrackListView(BaseDataDeezerTrack, DataBulkMixin, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:data-deezer-track_data"
    process_url = "panel:deezer-procesar"   # botón «Procesar pendientes» (POST a su vista propia)
    import_url = "panel:deezer-song"   # botón «Importar» → su lanzador
    procesados_url = "panel:song_list"   # botón → las fichas ya procesadas; ahí deja «Procesar pendientes»
    procesados_label = _("Canciones")
    bulk_process_task = tasks.process_music_pending_task


class GenreListView(BaseGenre, _ImagenDeezer, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:music-genre_data"
    create_url = "panel:music-genre_create"
    title = _("Lista de géneros")


class RoleListView(BaseRole, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:music-role_data"
    create_url = "panel:music-role_create"
    title = _("Lista de roles")


# Vistas FIJAS de «album» (una URL, una card y un fondo por cada una; sin filtros en página).


class SongListView(BaseSong, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:song_data"
    create_url = "panel:song_create"
    title = _("Lista de canciones")


class SongComposerListView(BaseSongComposer, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:song-composer_data"
    create_url = "panel:song-composer_create"
    title = _("Lista de compositores de canción")


class SongTranslationListView(BaseSongTranslation, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:song-translation_data"
    create_url = "panel:song-translation_create"
    title = _("Lista de traducciones de canción")


class MusicLogListView(BaseMusicLog, AdminListView):
    home_url = "panel:music-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:music-log_data"
    create_url = "panel:music-log_create"
    title = _("Lista de log de música")


# ==============================================================================
# Público
# ==============================================================================

# ==============================================================================
# Catálogos sobre la base NUEVA (PublicListView + PublicDataView por data_url)
# ==============================================================================


class AlbumPublicListView(BaseAlbum, PublicListView):
    data_url = "music:albums-catalog-data"
    background_image = "bg-music-album"
    background_fallback = "bg-music-home"
    section = "musica"
    title = _("Álbumes")
    icon = "bi-disc"
    home_url = "music:home"
    home_label = _("música")


class ArtistPublicListView(BaseArtist, PublicListView):
    data_url = "music:artists-catalog-data"
    background_image = "bg-music-artist"
    background_fallback = "bg-music-home"
    section = "musica"
    title = _("Artistas")
    icon = "bi-person-video2"
    home_url = "music:home"
    home_label = _("música")


class GenreAliasListView(BaseGenreAlias, AdminListView):
    home_url = "panel:music-home"
    data_url = "panel:music-genre-alias_data"
    create_url = "panel:music-genre-alias_create"
    title = _("Lista de alias de géneros")


class GenreAliasListByView(BaseGenreAliasContext, AdminListByView):
    """Alias acotados por su padre (`/music-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`."""
    home_url = "panel:music-home"
    create_url = "panel:music-genre-alias_create"
    data_url = "panel:music-genre-alias_data-by"
    full_list_url = "panel:music-genre-alias_list"
    by_url = "panel:music-genre-alias_by"


class RoleListByView(BaseRoleContext, AdminListByView):
    """Lista de roles acotada por familia (`/music-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`."""
    home_url = "panel:music-home"
    create_url = "panel:music-role_create"
    data_url = "panel:music-role_data-by"
    full_list_url = "panel:music-role_list"
    by_url = "panel:music-role_by"


class SongPublicListView(BaseSong, PublicListView):
    data_url = "music:songs-catalog-data"
    background_image = "bg-music-song"
    background_fallback = "bg-music-home"
    section = "musica"
    title = _("Canciones")
    icon = "bi-music-note-beamed"
    home_url = "music:home"
    home_label = _("música")
