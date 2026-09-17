"""music · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.music.services import deezer
from apps.music.views.base import BaseAlbum, BaseAlbumImage, BaseAlbumType, BaseArtist, BaseArtistImage, BaseArtistMember, BaseArtistType, BaseDataDeezerAlbum, BaseDataDeezerArtist, BaseDataDeezerGenre, BaseDataDeezerTrack, BaseGenre, BaseGenreAlias, BaseMusicLog, BaseRole, BaseSong, BaseSongComposer, BaseSongTranslation
from core.shared.views.base import BaseAdminDetailView, BasePublicDetailView


# ==============================================================================
# Gestión
# ==============================================================================


class AlbumDetailView(BaseAlbum, BaseAdminDetailView):
    template_name = "music/detail/album.html"
    update_url = "panel:album_update"
    delete_url = "panel:album_delete"
    list_url = "panel:album_list"
    toggle_url = "panel:album_toggle"
    by_url = "panel:album_by"
    tabs = [("canciones", _("Canciones"), "panel:song_by", "album"),
            ("imagenes", _("Imágenes"), "panel:album-image_by", "album")]


class AlbumImageDetailView(BaseAlbumImage, BaseAdminDetailView):
    template_name = "music/detail/album_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:album-image_update"
    delete_url = "panel:album-image_delete"
    list_url = "panel:album-image_list"
    toggle_url = "panel:album-image_toggle"


class AlbumTypeDetailView(BaseAlbumType, BaseAdminDetailView):
    template_name = "music/detail/album_type.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:music-album-type_update"
    delete_url = "panel:music-album-type_delete"
    list_url = "panel:music-album-type_list"
    toggle_url = "panel:music-album-type_toggle"


class ArtistDetailView(BaseArtist, BaseAdminDetailView):
    template_name = "music/detail/artist.html"
    update_url = "panel:artist_update"
    delete_url = "panel:artist_delete"
    list_url = "panel:artist_list"
    toggle_url = "panel:artist_toggle"
    by_url = "panel:artist_by"
    tabs = [("albumes", _("Álbumes"), "panel:album_by", "artista"),
            ("integrantes", _("Integrantes"), "panel:artist-member_by", "artista"),
            ("imagenes", _("Imágenes"), "panel:artist-image_by", "artista")]


class ArtistImageDetailView(BaseArtistImage, BaseAdminDetailView):
    template_name = "music/detail/artist_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:artist-image_update"
    delete_url = "panel:artist-image_delete"
    list_url = "panel:artist-image_list"
    toggle_url = "panel:artist-image_toggle"


class ArtistMemberDetailView(BaseArtistMember, BaseAdminDetailView):
    template_name = "music/detail/artist_member.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:artist-member_update"
    delete_url = "panel:artist-member_delete"
    list_url = "panel:artist-member_list"
    toggle_url = "panel:artist-member_toggle"


class ArtistTypeDetailView(BaseArtistType, BaseAdminDetailView):
    template_name = "music/detail/artist_type.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:music-artist-type_update"
    delete_url = "panel:music-artist-type_delete"
    list_url = "panel:music-artist-type_list"
    toggle_url = "panel:music-artist-type_toggle"


class DataDeezerAlbumDetailView(BaseDataDeezerAlbum, BaseAdminDetailView):
    template_name = "music/detail/data_deezer_album.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-deezer-album_update"
    delete_url = "panel:data-deezer-album_delete"
    list_url = "panel:data-deezer-album_list"
    reprocesar = staticmethod(lambda obj: deezer.process_album(obj.deezer_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


# ------------------------ datos crudos de importación (Deezer; antes en apps/imports) ------------------------
class DataDeezerArtistDetailView(BaseDataDeezerArtist, BaseAdminDetailView):
    template_name = "music/detail/data_deezer_artist.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-deezer-artist_update"
    delete_url = "panel:data-deezer-artist_delete"
    list_url = "panel:data-deezer-artist_list"
    reprocesar = staticmethod(lambda obj: deezer.process_artist(obj.deezer_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataDeezerGenreDetailView(BaseDataDeezerGenre, BaseAdminDetailView):
    template_name = "music/detail/data_deezer_genre.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-deezer-genre_update"
    delete_url = "panel:data-deezer-genre_delete"
    list_url = "panel:data-deezer-genre_list"
    reprocesar = staticmethod(lambda obj: deezer.process_genre(obj.deezer_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataDeezerTrackDetailView(BaseDataDeezerTrack, BaseAdminDetailView):
    template_name = "music/detail/data_deezer_track.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-deezer-track_update"
    delete_url = "panel:data-deezer-track_delete"
    list_url = "panel:data-deezer-track_list"


class GenreDetailView(BaseGenre, BaseAdminDetailView):
    template_name = "music/detail/genre.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:music-genre_update"
    delete_url = "panel:music-genre_delete"
    list_url = "panel:music-genre_list"
    toggle_url = "panel:music-genre_toggle"


class RoleDetailView(BaseRole, BaseAdminDetailView):
    template_name = "music/detail/role.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:music-role_update"
    delete_url = "panel:music-role_delete"
    list_url = "panel:music-role_list"
    toggle_url = "panel:music-role_toggle"


class SongDetailView(BaseSong, BaseAdminDetailView):
    template_name = "music/detail/song.html"
    update_url = "panel:song_update"
    delete_url = "panel:song_delete"
    list_url = "panel:song_list"
    toggle_url = "panel:song_toggle"
    by_url = "panel:song_by"
    tabs = []


class SongComposerDetailView(BaseSongComposer, BaseAdminDetailView):
    template_name = "music/detail/song_composer.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:song-composer_update"
    delete_url = "panel:song-composer_delete"
    list_url = "panel:song-composer_list"
    toggle_url = "panel:song-composer_toggle"


class SongTranslationDetailView(BaseSongTranslation, BaseAdminDetailView):
    template_name = "music/detail/song_translation.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:song-translation_update"
    delete_url = "panel:song-translation_delete"
    list_url = "panel:song-translation_list"
    toggle_url = "panel:song-translation_toggle"


class MusicLogDetailView(BaseMusicLog, BaseAdminDetailView):
    template_name = "music/detail/music_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:music-log_update"
    delete_url = "panel:music-log_delete"
    list_url = "panel:music-log_list"


# ==============================================================================
# Público
# ==============================================================================


class AlbumPublicDetailView(BaseAlbum, BasePublicDetailView):
    """Ficha pública de un álbum: reseña, pistas numeradas e imágenes."""
    template_name = "music/detail/album.html"
    list_url = "music:albums-catalog"
    by_url = "music:albums-by"
    section = "musica"
    collect_kind = "album"
    background_image = "bg-music-album"
    background_fallback = "bg-music-home"
    tabs = [("canciones", _("Canciones"), "music:songs-by", "album"),
            ("imagenes", _("Imágenes"), "music:album-images-by", "album")]


class ArtistPublicDetailView(BaseArtist, BasePublicDetailView):
    """Ficha pública de un artista: el mismo HTML que en gestión, sin botones y con la colección."""
    template_name = "music/detail/artist.html"
    list_url = "music:artists-catalog"
    by_url = "music:artists-by"
    section = "musica"
    collect_kind = "artist"
    background_image = "bg-music-artist"
    background_fallback = "bg-music-home"
    tabs = [("albumes", _("Álbumes"), "music:albums-by", "artista"),
            ("integrantes", _("Integrantes"), "personas:people-by", "integrantes-artista"),
            ("imagenes", _("Imágenes"), "music:artist-images-by", "artista")]


class GenreAliasDetailView(BaseGenreAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:music-genre-alias_list"
    update_url = "panel:music-genre-alias_update"
    delete_url = "panel:music-genre-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Género', 'genre')]


class SongPublicDetailView(BaseSong, BasePublicDetailView):
    """Ficha pública de una canción: significado, letra con traducciones y el resto del álbum."""
    template_name = "music/detail/song.html"
    list_url = "music:songs-catalog"
    by_url = "music:songs-by"
    section = "musica"
    collect_kind = "song"
    background_image = "bg-music-song"
    background_fallback = "bg-music-home"

    def get_queryset(self):
        return super().get_queryset().filter(album__is_active=True).select_related("album", "album__artist")
