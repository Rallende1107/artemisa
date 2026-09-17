"""music · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.music.models import Album, AlbumImage, AlbumType, Artist, ArtistImage, ArtistMember, ArtistType, DataDeezerAlbum, DataDeezerArtist, DataDeezerGenre, DataDeezerTrack, Genre, GenreAlias, MusicLog, Role, Song, SongComposer, SongTranslation
from apps.music.views.base import BaseAlbum, BaseAlbumContext, BaseAlbumImage, BaseAlbumImageContext, BaseAlbumType, BaseArtist, BaseArtistContext, BaseArtistImage, BaseArtistImageContext, BaseArtistMember, BaseArtistMemberContext, BaseArtistType, BaseDataDeezerAlbum, BaseDataDeezerArtist, BaseDataDeezerGenre, BaseDataDeezerTrack, BaseGenre, BaseGenreAliasContext, BaseMusicLog, BaseRole, BaseRoleContext, BaseSong, BaseSongComposer, BaseSongComposerContext, BaseSongContext, BaseSongTranslation, BaseSongTranslationContext
from apps.music.views.v2_filters import AlbumFilters, ArtistAdminFilters, ArtistFilters, ArtistSongFilters, RoleFilters, SongFilters
from core.shared.views.base import AdminDataView, BaseSelectView, PublicDataView
from core.shared.views.filters import DatosFilters, ImagenesFilters, LogFilters
from core.utils.queries import con_nube
from core.utils.views_base import cell, cell_cover, cell_miniatura, meta_line


# ==============================================================================
# Gestión
# ==============================================================================


class AlbumDataView(BaseAlbumContext, AdminDataView):
    columns = [(_('Título'), "ficha"), (_('Artista'), 'artist'), (_('Tipo'), 'album_type'), (_('Lanzamiento'), 'release_date'), (_('Activo'), 'is_active')]
    filters = AlbumFilters

    def get(self, request, tipo=None, pk=None):
        qs = Album.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj), meta_line(obj)),
                "c1": self.link_by(obj, "artist"),
                "c2": self.link_by(obj, "album_type"),
                "c3": cell(obj, "release_date"),
                "c4": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AlbumSelectView(BaseAlbum, BaseSelectView):
    search_fields = ['title']


class AlbumPublicDataView(BaseAlbumContext, PublicDataView):
    columns = [(_("Título"), "ficha")]
    filters = AlbumFilters
    priority = {"ficha": 1}
    detail_url_name = "music:album-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Album.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.title or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AlbumImageDataView(BaseAlbumImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Álbum'), 'album'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(AlbumImage.objects.select_related("album"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "album"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "album", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AlbumImageSelectView(BaseAlbumImage, BaseSelectView):
    search_fields = ['image_url']


class AlbumImagesPublicDataView(BaseAlbumImageContext, PublicDataView):
    """Galería de un álbum: sus imágenes extra en tarjetas (la portada va en la ficha)."""
    columns = [(_("Imagen"), "image")]
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = AlbumImage.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "image"),
                "acciones": self.row_actions(obj, request, ""),
                "detail_url": self.detail_url(obj), "card_title": escape(""), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AlbumTypeDataView(BaseAlbumType, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = AlbumType.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AlbumTypeSelectView(BaseAlbumType, BaseSelectView):
    search_fields = ['name', 'name_esp']


class ArtistDataView(BaseArtistContext, AdminDataView):
    columns = [(_('Nombre'), 'name'), (_('Tipo'), 'artist_type'), (_('Inicio'), 'start_year'), (_('Activo'), 'is_active')]
    filters = ArtistAdminFilters
    priority = {"name": 1, "is_active": 2}

    def get(self, request, tipo=None, pk=None):
        qs = Artist.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": self.link_by(obj, "artist_type"),
                "c2": cell(obj, "start_year"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ArtistSelectView(BaseArtist, BaseSelectView):
    search_fields = ['name']


class ArtistPublicDataView(BaseArtistContext, PublicDataView):
    columns = [(_("Nombre"), "ficha"), (_("Inicio"), "start_year")]
    filters = ArtistFilters
    priority = {"ficha": 1}
    detail_url_name = "music:artist-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Artist.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "c1": cell(obj, "start_year"),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ArtistImageDataView(BaseArtistImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Artista'), 'artist'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(ArtistImage.objects.select_related("artist"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "artist"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "artist", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ArtistImageSelectView(BaseArtistImage, BaseSelectView):
    search_fields = ['image_url']


class ArtistImagesPublicDataView(BaseArtistImageContext, PublicDataView):
    """Galería de un artista: sus imágenes extra en tarjetas."""
    columns = [(_("Imagen"), "image")]
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = ArtistImage.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "image"),
                "acciones": self.row_actions(obj, request, ""),
                "detail_url": self.detail_url(obj), "card_title": escape(""), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ArtistMemberDataView(BaseArtistMemberContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('Rol'), 'role'), (_('Artista'), 'artist'), (_('Desde'), 'join_date'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = ArtistMember.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": cell(obj, "role"),
                "c2": self.link_by(obj, "artist"),
                "c3": cell(obj, "join_date"),
                "c4": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ArtistMemberSelectView(BaseArtistMember, BaseSelectView):
    search_fields = []


class ArtistTypeDataView(BaseArtistType, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = ArtistType.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ArtistTypeSelectView(BaseArtistType, BaseSelectView):
    search_fields = ['name', 'name_esp']


class DataDeezerAlbumDataView(BaseDataDeezerAlbum, AdminDataView):
    columns = [(_('deezer_id'), 'deezer_id'), (_('Título'), 'titulo'), (_('Artista'), 'artista'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataDeezerAlbum.objects.all()
        # `data__artist__name`: el buscador entra al JSON, así se encuentra un álbum por su artista
        p, total, filtrado, objetos = self.query(request, qs, ['deezer_id', 'data__title', 'data__name', 'data__artist__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "deezer_id"),
                "c1": cell(obj, "titulo"),
                "c2": cell(obj, "artista"),
                "c3": cell(obj, "data_status"),
                "c4": cell(obj, "data_processed"),
                "c5": cell(obj, "status_code"),
                "c6": cell(obj, "created_at"),
                "c7": cell(obj, "data"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


# ------------------------ datos crudos de importación (Deezer; antes en apps/imports) ------------------------
class DataDeezerArtistDataView(BaseDataDeezerArtist, AdminDataView):
    columns = [(_('deezer_id'), 'deezer_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataDeezerArtist.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['deezer_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "deezer_id"),
                "c1": cell(obj, "titulo"),
                "c2": cell(obj, "data_status"),
                "c3": cell(obj, "data_processed"),
                "c4": cell(obj, "status_code"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "data"),
                "c7": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataDeezerGenreDataView(BaseDataDeezerGenre, AdminDataView):
    columns = [(_('deezer_id'), 'deezer_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataDeezerGenre.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['deezer_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "deezer_id"),
                "c1": cell(obj, "titulo"),
                "c2": cell(obj, "data_status"),
                "c3": cell(obj, "data_processed"),
                "c4": cell(obj, "status_code"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "data"),
                "c7": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataDeezerTrackDataView(BaseDataDeezerTrack, AdminDataView):
    columns = [(_('deezer_id'), 'deezer_id'), (_('Título'), 'titulo'), (_('Álbum'), 'deezer_id_album'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataDeezerTrack.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['deezer_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "deezer_id"),
                "c1": cell(obj, "titulo"),
                "c2": cell(obj, "deezer_id_album"),
                "c3": cell(obj, "data_status"),
                "c4": cell(obj, "data_processed"),
                "c5": cell(obj, "status_code"),
                "c6": cell(obj, "created_at"),
                "c7": cell(obj, "data"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GenreDataView(BaseGenre, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Genre.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'aliases__name', 'aliases__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GenreSelectView(BaseGenre, BaseSelectView):
    search_fields = ['name', 'name_esp', 'aliases__name', 'aliases__name_esp']


class GenreAliasDataView(BaseGenreAliasContext, AdminDataView):
    columns = [(_('Alias'), 'name'), (_('Alias (ES)'), 'name_esp'), (_('Género'), 'genre'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = GenreAlias.objects.all().select_related(*('genre',))
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'genre__name', 'genre__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "name_esp"),
                "c2": self.link_by(obj, "genre"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RoleDataView(BaseRoleContext, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Tipo de rol'), 'get_type_display'), (_('Activo'), 'is_active')]
    filters = RoleFilters

    def get(self, request, tipo=None, pk=None):
        qs = Role.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "get_type_display"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RoleSelectView(BaseRole, BaseSelectView):
    search_fields = ['name', 'name_esp']


class SongDataView(BaseSongContext, AdminDataView):
    columns = [(_('Título'), 'title'), (_('Álbum'), 'album'), (_('Pista'), 'album_song_id'), (_('Activo'), 'is_active')]
    filters = ArtistSongFilters

    def get(self, request, tipo=None, pk=None):
        qs = Song.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'title_short'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "title"),
                "c1": self.link_by(obj, "album"),
                "c2": cell(obj, "album_song_id"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SongSelectView(BaseSong, BaseSelectView):
    search_fields = ['title', 'title_short']


class SongPublicDataView(BaseSongContext, PublicDataView):
    columns = [(_("Título"), "ficha")]
    filters = SongFilters
    priority = {"ficha": 1}
    filters_by = {"artista": ArtistSongFilters}
    detail_url_name = "music:song-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Song.objects.all()
        qs = qs.filter(album__is_active=True).select_related("album")
        p, total, filtrado, objetos = self.query(request, qs, ['title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), (obj.album.cover_url if obj.album_id else ""), str(obj.title or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.title or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": (obj.album.cover_url if obj.album_id else ""), "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SongComposerDataView(BaseSongComposerContext, AdminDataView):
    columns = [(_("Canción"), "song"), (_("Persona"), "person"), (_("Activo"), "is_active")]

    def get(self, request, tipo=None, pk=None):
        qs = SongComposer.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["song__title", "person__full_name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "song"),
                "c1": self.link_by(obj, "person"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SongComposerSelectView(BaseSongComposer, BaseSelectView):
    search_fields = ['song__title', 'person__full_name']


class SongTranslationDataView(BaseSongTranslationContext, AdminDataView):
    columns = [(_("Canción"), "song"), (_("Idioma"), "language"), (_("Activo"), "is_active")]

    def get(self, request, tipo=None, pk=None):
        qs = SongTranslation.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["song__title", "language__name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "song"),
                "c1": cell(obj, "language"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SongTranslationSelectView(BaseSongTranslation, BaseSelectView):
    search_fields = ['song__title']


class MusicLogDataView(BaseMusicLog, AdminDataView):
    columns = [(_('#'), 'id'), (_('Nivel'), 'get_level_display'), (_('Proceso'), 'process'), (_('Mensaje'), 'message'), (_('Momento'), 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = MusicLog.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['process', 'message'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "id"),
                "c1": cell(obj, "get_level_display"),
                "c2": cell(obj, "process"),
                "c3": cell(obj, "message", truncar=120),
                "c4": cell(obj, "timestamp"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)
