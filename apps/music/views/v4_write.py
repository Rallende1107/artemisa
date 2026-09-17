"""music · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.music import forms as f
from apps.music.views.base import BaseAlbum, BaseAlbumImage, BaseAlbumType, BaseArtist, BaseArtistImage, BaseArtistMember, BaseArtistType, BaseDataDeezerAlbum, BaseDataDeezerArtist, BaseDataDeezerGenre, BaseDataDeezerTrack, BaseGenre, BaseGenreAlias, BaseMusicLog, BaseRole, BaseSong, BaseSongComposer, BaseSongTranslation
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class AlbumCreateView(BaseAlbum, BaseCreate):
    # Django core
    form_class = f.AlbumForm
    form_template = "music/form/album.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:album_list"
    success_url = "panel:album_list"
    cancel_url = "panel:album_list"
    # UX
    success_message = _("Álbum «%(obj)s» creado.")
    title = _("Crear álbum")


class AlbumUpdateView(BaseAlbum, BaseUpdate):
    # Django core
    form_class = f.AlbumForm
    form_template = "music/form/album.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:album_list"
    success_url = "panel:album_list"
    cancel_url = "panel:album_list"
    # UX
    success_message = _("Álbum «%(obj)s» actualizado.")
    title = _("Editar álbum")


class AlbumDeleteView(BaseAlbum, BaseDelete):
    list_url = "panel:album_list"
    success_url = "panel:album_list"
    cancel_url = "panel:album_list"
    success_message = _("Álbum «%(obj)s» eliminado.")
    title = _("Eliminar álbum")


class AlbumImageCreateView(BaseAlbumImage, BaseCreate):
    # Django core
    form_class = f.AlbumImageForm
    form_template = "music/form/album_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:album-image_list"
    success_url = "panel:album-image_list"
    cancel_url = "panel:album-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class AlbumImageUpdateView(BaseAlbumImage, BaseUpdate):
    # Django core
    form_class = f.AlbumImageForm
    form_template = "music/form/album_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:album-image_list"
    success_url = "panel:album-image_list"
    cancel_url = "panel:album-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class AlbumImageDeleteView(BaseAlbumImage, BaseDelete):
    list_url = "panel:album-image_list"
    success_url = "panel:album-image_list"
    cancel_url = "panel:album-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class AlbumTypeCreateView(BaseAlbumType, BaseCreate):
    # Django core
    form_class = f.AlbumTypeForm
    form_template = "music/form/album_type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-album-type_list"
    success_url = "panel:music-album-type_list"
    cancel_url = "panel:music-album-type_list"
    # UX
    success_message = _("Tipo de álbum «%(obj)s» creado.")
    title = _("Crear tipo de álbum")


class AlbumTypeUpdateView(BaseAlbumType, BaseUpdate):
    # Django core
    form_class = f.AlbumTypeForm
    form_template = "music/form/album_type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-album-type_list"
    success_url = "panel:music-album-type_list"
    cancel_url = "panel:music-album-type_list"
    # UX
    success_message = _("Tipo de álbum «%(obj)s» actualizado.")
    title = _("Editar tipo de álbum")


class AlbumTypeDeleteView(BaseAlbumType, BaseDelete):
    list_url = "panel:music-album-type_list"
    success_url = "panel:music-album-type_list"
    cancel_url = "panel:music-album-type_list"
    success_message = _("Tipo de álbum «%(obj)s» eliminado.")
    title = _("Eliminar tipo de álbum")


class ArtistCreateView(BaseArtist, BaseCreate):
    # Django core
    form_class = f.ArtistForm
    form_template = "music/form/artist.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:artist_list"
    success_url = "panel:artist_list"
    cancel_url = "panel:artist_list"
    # UX
    success_message = _("Artista «%(obj)s» creado.")
    title = _("Crear artista")


class ArtistUpdateView(BaseArtist, BaseUpdate):
    # Django core
    form_class = f.ArtistForm
    form_template = "music/form/artist.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:artist_list"
    success_url = "panel:artist_list"
    cancel_url = "panel:artist_list"
    # UX
    success_message = _("Artista «%(obj)s» actualizado.")
    title = _("Editar artista")


class ArtistDeleteView(BaseArtist, BaseDelete):
    list_url = "panel:artist_list"
    success_url = "panel:artist_list"
    cancel_url = "panel:artist_list"
    success_message = _("Artista «%(obj)s» eliminado.")
    title = _("Eliminar artista")


class ArtistImageCreateView(BaseArtistImage, BaseCreate):
    # Django core
    form_class = f.ArtistImageForm
    form_template = "music/form/artist_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:artist-image_list"
    success_url = "panel:artist-image_list"
    cancel_url = "panel:artist-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class ArtistImageUpdateView(BaseArtistImage, BaseUpdate):
    # Django core
    form_class = f.ArtistImageForm
    form_template = "music/form/artist_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:artist-image_list"
    success_url = "panel:artist-image_list"
    cancel_url = "panel:artist-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class ArtistImageDeleteView(BaseArtistImage, BaseDelete):
    list_url = "panel:artist-image_list"
    success_url = "panel:artist-image_list"
    cancel_url = "panel:artist-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class ArtistMemberCreateView(BaseArtistMember, BaseCreate):
    # Django core
    form_class = f.ArtistMemberForm
    form_template = "music/form/artist_member.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:artist-member_list"
    success_url = "panel:artist-member_list"
    cancel_url = "panel:artist-member_list"
    # UX
    success_message = _("Miembro «%(obj)s» creado.")
    title = _("Crear miembro")


class ArtistMemberUpdateView(BaseArtistMember, BaseUpdate):
    # Django core
    form_class = f.ArtistMemberForm
    form_template = "music/form/artist_member.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:artist-member_list"
    success_url = "panel:artist-member_list"
    cancel_url = "panel:artist-member_list"
    # UX
    success_message = _("Miembro «%(obj)s» actualizado.")
    title = _("Editar miembro")


class ArtistMemberDeleteView(BaseArtistMember, BaseDelete):
    list_url = "panel:artist-member_list"
    success_url = "panel:artist-member_list"
    cancel_url = "panel:artist-member_list"
    success_message = _("Miembro «%(obj)s» eliminado.")
    title = _("Eliminar miembro")


class ArtistTypeCreateView(BaseArtistType, BaseCreate):
    # Django core
    form_class = f.ArtistTypeForm
    form_template = "music/form/artist_type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-artist-type_list"
    success_url = "panel:music-artist-type_list"
    cancel_url = "panel:music-artist-type_list"
    # UX
    success_message = _("Tipo de artista «%(obj)s» creado.")
    title = _("Crear tipo de artista")


class ArtistTypeUpdateView(BaseArtistType, BaseUpdate):
    # Django core
    form_class = f.ArtistTypeForm
    form_template = "music/form/artist_type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-artist-type_list"
    success_url = "panel:music-artist-type_list"
    cancel_url = "panel:music-artist-type_list"
    # UX
    success_message = _("Tipo de artista «%(obj)s» actualizado.")
    title = _("Editar tipo de artista")


class ArtistTypeDeleteView(BaseArtistType, BaseDelete):
    list_url = "panel:music-artist-type_list"
    success_url = "panel:music-artist-type_list"
    cancel_url = "panel:music-artist-type_list"
    success_message = _("Tipo de artista «%(obj)s» eliminado.")
    title = _("Eliminar tipo de artista")


class DataDeezerAlbumUpdateView(BaseDataDeezerAlbum, BaseUpdate):
    # Django core
    form_class = f.DataDeezerAlbumForm
    list_url = "panel:data-deezer-album_list"
    success_url = "panel:data-deezer-album_list"
    cancel_url = "panel:data-deezer-album_list"
    # UX
    success_message = _("Datos de álbum «%(obj)s» actualizados.")


class DataDeezerAlbumDeleteView(BaseDataDeezerAlbum, BaseDelete):
    list_url = "panel:data-deezer-album_list"
    success_url = "panel:data-deezer-album_list"
    cancel_url = "panel:data-deezer-album_list"
    success_message = _("Datos de álbum «%(obj)s» eliminados.")


class DataDeezerAlbumCreateView(BaseDataDeezerAlbum, BaseCreate):
    form_class = f.DataDeezerAlbumForm
    list_url = "panel:data-deezer-album_list"
    success_url = "panel:data-deezer-album_list"
    cancel_url = "panel:data-deezer-album_list"
    success_message = _("Datos de álbum (deezer) «%(obj)s» creado.")


class DataDeezerArtistUpdateView(BaseDataDeezerArtist, BaseUpdate):
    # Django core
    form_class = f.DataDeezerArtistForm
    list_url = "panel:data-deezer-artist_list"
    success_url = "panel:data-deezer-artist_list"
    cancel_url = "panel:data-deezer-artist_list"
    # UX
    success_message = _("Datos de artista «%(obj)s» actualizados.")


class DataDeezerArtistDeleteView(BaseDataDeezerArtist, BaseDelete):
    list_url = "panel:data-deezer-artist_list"
    success_url = "panel:data-deezer-artist_list"
    cancel_url = "panel:data-deezer-artist_list"
    success_message = _("Datos de artista «%(obj)s» eliminados.")


class DataDeezerArtistCreateView(BaseDataDeezerArtist, BaseCreate):
    form_class = f.DataDeezerArtistForm
    list_url = "panel:data-deezer-artist_list"
    success_url = "panel:data-deezer-artist_list"
    cancel_url = "panel:data-deezer-artist_list"
    success_message = _("Datos de artista (deezer) «%(obj)s» creado.")


class DataDeezerGenreUpdateView(BaseDataDeezerGenre, BaseUpdate):
    # Django core
    form_class = f.DataDeezerGenreForm
    list_url = "panel:data-deezer-genre_list"
    success_url = "panel:data-deezer-genre_list"
    cancel_url = "panel:data-deezer-genre_list"
    # UX
    success_message = _("Datos de género «%(obj)s» actualizados.")


class DataDeezerGenreDeleteView(BaseDataDeezerGenre, BaseDelete):
    list_url = "panel:data-deezer-genre_list"
    success_url = "panel:data-deezer-genre_list"
    cancel_url = "panel:data-deezer-genre_list"
    success_message = _("Datos de género «%(obj)s» eliminados.")


class DataDeezerGenreCreateView(BaseDataDeezerGenre, BaseCreate):
    form_class = f.DataDeezerGenreForm
    list_url = "panel:data-deezer-genre_list"
    success_url = "panel:data-deezer-genre_list"
    cancel_url = "panel:data-deezer-genre_list"
    success_message = _("Datos de género (deezer) «%(obj)s» creado.")


class DataDeezerTrackUpdateView(BaseDataDeezerTrack, BaseUpdate):
    # Django core
    form_class = f.DataDeezerTrackForm
    list_url = "panel:data-deezer-track_list"
    success_url = "panel:data-deezer-track_list"
    cancel_url = "panel:data-deezer-track_list"
    # UX
    success_message = _("Datos de pista del álbum «%(obj)s» actualizados.")


class DataDeezerTrackDeleteView(BaseDataDeezerTrack, BaseDelete):
    list_url = "panel:data-deezer-track_list"
    success_url = "panel:data-deezer-track_list"
    cancel_url = "panel:data-deezer-track_list"
    success_message = _("Datos de pista del álbum «%(obj)s» eliminados.")


class DataDeezerTrackCreateView(BaseDataDeezerTrack, BaseCreate):
    form_class = f.DataDeezerTrackForm
    list_url = "panel:data-deezer-track_list"
    success_url = "panel:data-deezer-track_list"
    cancel_url = "panel:data-deezer-track_list"
    success_message = _("Datos de pista del álbum (deezer) «%(obj)s» creado.")


class GenreCreateView(BaseGenre, BaseCreate):
    # Django core
    form_class = f.GenreForm
    form_template = "music/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-genre_list"
    success_url = "panel:music-genre_list"
    cancel_url = "panel:music-genre_list"
    # UX
    success_message = _("Género «%(obj)s» creado.")
    title = _("Crear género")


class GenreUpdateView(BaseGenre, BaseUpdate):
    # Django core
    form_class = f.GenreForm
    form_template = "music/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-genre_list"
    success_url = "panel:music-genre_list"
    cancel_url = "panel:music-genre_list"
    # UX
    success_message = _("Género «%(obj)s» actualizado.")
    title = _("Editar género")


class GenreDeleteView(BaseGenre, BaseDelete):
    list_url = "panel:music-genre_list"
    success_url = "panel:music-genre_list"
    cancel_url = "panel:music-genre_list"
    success_message = _("Género «%(obj)s» eliminado.")
    title = _("Eliminar género")


class GenreAliasCreateView(BaseGenreAlias, BaseCreate):
    form_class = f.GenreAliasForm
    list_url = "panel:music-genre-alias_list"
    success_url = "panel:music-genre-alias_list"
    cancel_url = "panel:music-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» creado.")
    title = _("Crear alias de género")


class GenreAliasUpdateView(BaseGenreAlias, BaseUpdate):
    form_class = f.GenreAliasForm
    list_url = "panel:music-genre-alias_list"
    success_url = "panel:music-genre-alias_list"
    cancel_url = "panel:music-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» actualizado.")
    title = _("Editar alias de género")


class GenreAliasDeleteView(BaseGenreAlias, BaseDelete):
    list_url = "panel:music-genre-alias_list"
    success_url = "panel:music-genre-alias_list"
    cancel_url = "panel:music-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» eliminado.")
    title = _("Eliminar alias de género")


class RoleCreateView(BaseRole, BaseCreate):
    # Django core
    form_class = f.RoleForm
    form_template = "music/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-role_list"
    success_url = "panel:music-role_list"
    cancel_url = "panel:music-role_list"
    # UX
    success_message = _("Rol «%(obj)s» creado.")
    title = _("Crear rol")


class RoleUpdateView(BaseRole, BaseUpdate):
    # Django core
    form_class = f.RoleForm
    form_template = "music/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:music-role_list"
    success_url = "panel:music-role_list"
    cancel_url = "panel:music-role_list"
    # UX
    success_message = _("Rol «%(obj)s» actualizado.")
    title = _("Editar rol")


class RoleDeleteView(BaseRole, BaseDelete):
    list_url = "panel:music-role_list"
    success_url = "panel:music-role_list"
    cancel_url = "panel:music-role_list"
    success_message = _("Rol «%(obj)s» eliminado.")
    title = _("Eliminar rol")


class SongCreateView(BaseSong, BaseCreate):
    # Django core
    form_class = f.SongForm
    form_template = "music/form/song.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:song_list"
    success_url = "panel:song_list"
    cancel_url = "panel:song_list"
    # UX
    success_message = _("Canción «%(obj)s» creada.")
    title = _("Crear canción")


class SongUpdateView(BaseSong, BaseUpdate):
    # Django core
    form_class = f.SongForm
    form_template = "music/form/song.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:song_list"
    success_url = "panel:song_list"
    cancel_url = "panel:song_list"
    # UX
    success_message = _("Canción «%(obj)s» actualizada.")
    title = _("Editar canción")


class SongDeleteView(BaseSong, BaseDelete):
    list_url = "panel:song_list"
    success_url = "panel:song_list"
    cancel_url = "panel:song_list"
    success_message = _("Canción «%(obj)s» eliminada.")
    title = _("Eliminar canción")


class SongComposerCreateView(BaseSongComposer, BaseCreate):
    # Django core
    form_class = f.SongComposerForm
    list_url = "panel:song-composer_list"
    success_url = "panel:song-composer_list"
    cancel_url = "panel:song-composer_list"
    # UX
    success_message = _("Compositor de canción «%(obj)s» creado.")
    title = _("Crear compositor de canción")


class SongComposerUpdateView(BaseSongComposer, BaseUpdate):
    # Django core
    form_class = f.SongComposerForm
    list_url = "panel:song-composer_list"
    success_url = "panel:song-composer_list"
    cancel_url = "panel:song-composer_list"
    # UX
    success_message = _("Compositor de canción «%(obj)s» actualizado.")
    title = _("Editar compositor de canción")


class SongComposerDeleteView(BaseSongComposer, BaseDelete):
    list_url = "panel:song-composer_list"
    success_url = "panel:song-composer_list"
    cancel_url = "panel:song-composer_list"
    success_message = _("Compositor de canción «%(obj)s» eliminado.")
    title = _("Eliminar compositor de canción")


class SongTranslationCreateView(BaseSongTranslation, BaseCreate):
    # Django core
    form_class = f.SongTranslationForm
    list_url = "panel:song-translation_list"
    success_url = "panel:song-translation_list"
    cancel_url = "panel:song-translation_list"
    # UX
    success_message = _("Traducción de canción «%(obj)s» creada.")
    title = _("Crear traducción de canción")


class SongTranslationUpdateView(BaseSongTranslation, BaseUpdate):
    # Django core
    form_class = f.SongTranslationForm
    list_url = "panel:song-translation_list"
    success_url = "panel:song-translation_list"
    cancel_url = "panel:song-translation_list"
    # UX
    success_message = _("Traducción de canción «%(obj)s» actualizada.")
    title = _("Editar traducción de canción")


class SongTranslationDeleteView(BaseSongTranslation, BaseDelete):
    list_url = "panel:song-translation_list"
    success_url = "panel:song-translation_list"
    cancel_url = "panel:song-translation_list"
    success_message = _("Traducción de canción «%(obj)s» eliminada.")
    title = _("Eliminar traducción de canción")


class MusicLogCreateView(BaseMusicLog, BaseCreate):
    form_class = f.MusicLogForm
    form_template = "music/form/music_log.html"
    list_url = "panel:music-log_list"
    success_url = "panel:music-log_list"
    cancel_url = "panel:music-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class MusicLogUpdateView(BaseMusicLog, BaseUpdate):
    form_class = f.MusicLogForm
    form_template = "music/form/music_log.html"
    list_url = "panel:music-log_list"
    success_url = "panel:music-log_list"
    cancel_url = "panel:music-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class MusicLogDeleteView(BaseMusicLog, BaseDelete):
    list_url = "panel:music-log_list"
    success_url = "panel:music-log_list"
    cancel_url = "panel:music-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
