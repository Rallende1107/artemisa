"""games · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.games.models import Character, CharacterImage, CharacterRole, Creator, CreatorLink, CreatorNickname, DataF95Creator, DataF95Game, DataVndbCharacter, DataVndbCreator, DataVndbGame, DataVndbRelease, DevelopmentEngine, Game, GameImage, GameLink, GameLog, GameTitle, Genre, GenreAlias, Medium, Platform, Release, ReleaseImage, Tag, TagAlias
from apps.games.views.base import BaseCharacter, BaseCharacterContext, BaseCharacterImageContext, BaseCharacterRoleContext, BaseCreator, BaseCreatorContext, BaseCreatorLink, BaseCreatorLinkContext, BaseCreatorNickname, BaseCreatorNicknameContext, BaseDataF95Creator, BaseDataF95Game, BaseDataVndbCharacter, BaseDataVndbCreator, BaseDataVndbGame, BaseDataVndbRelease, BaseDevelopmentEngine, BaseGame, BaseGameContext, BaseGameImage, BaseGameImageContext, BaseGameLink, BaseGameLinkContext, BaseGameLog, BaseGameTitle, BaseGameTitleContext, BaseGenre, BaseGenreAliasContext, BaseMedium, BasePlatform, BaseReleaseContext, BaseReleaseImage, BaseReleaseImageContext, BaseTag, BaseTagAliasContext
from apps.games.views.v2_filters import CharacterFilters, CreatorFilters, GameFilters, ReleaseFilters
from core.shared.views.base import AdminDataView, BaseSelectView, PublicDataView
from core.shared.views.filters import DatosFilters, ImagenesFilters, LogFilters
from core.utils.queries import con_nube, con_relacion
from core.utils.views_base import cell, cell_cover, cell_miniatura, meta_line


# ==============================================================================
# Gestión
# ==============================================================================


# ------------------------ personajes de juego (VNDB) ------------------------

class CharacterDataView(BaseCharacterContext, AdminDataView):
    columns = [(_('Nombre'), 'name'), (_('Original'), 'original'), (_('Sexo'), 'sex'), (_('Edad'), 'age'), (_('VNDB'), 'vndb_id'), (_('Activo'), 'is_active')]
    filters = CharacterFilters

    def get(self, request, tipo=None, pk=None):
        qs = Character.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'original'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "original"),
                "c2": cell(obj, "sex"),
                "c3": cell(obj, "age"),
                "c4": cell(obj, "vndb_id"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CharacterSelectView(BaseCharacter, BaseSelectView):
    search_fields = ['name', 'original']


class CharacterImageDataView(BaseCharacterImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Personaje'), 'character'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(CharacterImage.objects.select_related("character"))
        p, total, filtrado, objetos = self.query(request, qs, ['character__name', 'image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "character"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "character", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CharacterRoleDataView(BaseCharacterRoleContext, AdminDataView):
    columns = [(_('Personaje'), 'character'), (_('Juego'), 'game'), (_('Rol'), 'role'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = CharacterRole.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['character__name', 'game__title', 'role'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "character"),
                "c1": self.link_by(obj, "game"),
                "c2": cell(obj, "role"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CreatorDataView(BaseCreatorContext, AdminDataView):
    columns = [(_('Nombre'), 'name'), (_('Tipo'), 'type'), (_('Activo'), 'is_active')]
    filters = CreatorFilters

    def get(self, request, tipo=None, pk=None):
        qs = Creator.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'nicknames__nickname'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": self.link_by(obj, "type"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CreatorSelectView(BaseCreator, BaseSelectView):
    search_fields = ['name', 'nicknames__nickname']


class CreatorLinkDataView(BaseCreatorLinkContext, AdminDataView):
    columns = [(_('Creador'), 'creator'), (_('Fuente'), 'source'), (_('URL'), 'url'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = CreatorLink.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['url', 'external_id'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "creator"),
                "c1": cell(obj, "source"),
                "c2": cell(obj, "url"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CreatorLinkSelectView(BaseCreatorLink, BaseSelectView):
    search_fields = ['url', 'external_id']


class CreatorNicknameDataView(BaseCreatorNicknameContext, AdminDataView):
    columns = [(_('Apodo'), 'nickname'), (_('Creador'), 'creator'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = CreatorNickname.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['nickname'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "nickname"),
                "c1": self.link_by(obj, "creator"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CreatorNicknameSelectView(BaseCreatorNickname, BaseSelectView):
    search_fields = ['nickname']


class DataF95CreatorDataView(BaseDataF95Creator, AdminDataView):
    columns = [(_('f95_id'), 'f95_id'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataF95Creator.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['data__name', 'data__title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "f95_id"), "c1": cell(obj, "data_status"), "c2": cell(obj, "data_processed"), "c3": cell(obj, "status_code"), "c4": cell(obj, "created_at"), "c5": cell(obj, "data"), "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataF95GameDataView(BaseDataF95Game, AdminDataView):
    columns = [(_('f95_id'), 'f95_id'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataF95Game.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "f95_id"), "c1": cell(obj, "data_status"), "c2": cell(obj, "data_processed"), "c3": cell(obj, "status_code"), "c4": cell(obj, "created_at"), "c5": cell(obj, "data"), "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataVndbCharacterDataView(BaseDataVndbCharacter, AdminDataView):
    columns = [(_('vndb_id'), 'vndb_id'), (_('Título'), 'titulo'), (_('Juego'), 'juego'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataVndbCharacter.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['vndb_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "vndb_id"), "c1": cell(obj, "titulo"), "c2": str(self.col_juego(obj)), "c3": cell(obj, "data_status"), "c4": cell(obj, "data_processed"), "c5": cell(obj, "status_code"), "c6": cell(obj, "created_at"), "c7": cell(obj, "data"), "c8": cell(obj, "is_active"),
  "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataVndbCreatorDataView(BaseDataVndbCreator, AdminDataView):
    columns = [(_('vndb_id'), 'vndb_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataVndbCreator.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['vndb_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "vndb_id"),
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


# ------------------------ datos crudos de importación (VNDB; antes en apps/imports) ------------------------
class DataVndbGameDataView(BaseDataVndbGame, AdminDataView):
    columns = [(_('vndb_id'), 'vndb_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataVndbGame.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['vndb_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "vndb_id"), "c1": cell(obj, "titulo"), "c2": cell(obj, "data_status"), "c3": cell(obj, "data_processed"), "c4": cell(obj, "status_code"), "c5": cell(obj, "created_at"), "c6": cell(obj, "data"), "c7": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataVndbReleaseDataView(BaseDataVndbRelease, AdminDataView):
    columns = [(_('vndb_id'), 'vndb_id'), (_('Título'), 'titulo'), (_('Juego'), 'juego'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataVndbRelease.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['vndb_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "vndb_id"),
                "c1": cell(obj, "titulo"),
                "c2": str(self.col_juego(obj)),
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


class DevelopmentEngineDataView(BaseDevelopmentEngine, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = DevelopmentEngine.objects.all()
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


class DevelopmentEngineSelectView(BaseDevelopmentEngine, BaseSelectView):
    search_fields = ['name', 'name_esp']


class GameDataView(BaseGameContext, AdminDataView):
    columns = [(_('Título'), "ficha"), (_('Estado'), 'get_status_display'), (_('Tipo'), 'get_type_display'), (_('Versión'), 'version'), (_('Activo'), 'is_active')]
    filters = GameFilters

    def get(self, request, tipo=None, pk=None):
        qs = Game.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'titles__title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": cell(obj, "get_status_display"),
                "c2": cell(obj, "get_type_display"),
                "c3": cell(obj, "version"),
                "c4": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameSelectView(BaseGame, BaseSelectView):
    search_fields = ['title', 'titles__title']


class GameImageDataView(BaseGameImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Juego'), 'game'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(GameImage.objects.select_related("game"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "game"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "game", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameImageSelectView(BaseGameImage, BaseSelectView):
    search_fields = ['image_url']


class GameLinkDataView(BaseGameLinkContext, AdminDataView):
    columns = [(_('Juego'), 'game'), (_('Fuente'), 'source'), (_('URL'), 'url'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = GameLink.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['url', 'external_id'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "game"),
                "c1": cell(obj, "source"),
                "c2": cell(obj, "url"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameLinkSelectView(BaseGameLink, BaseSelectView):
    search_fields = ['url', 'external_id']


class GameTitleDataView(BaseGameTitleContext, AdminDataView):
    columns = [(_('Título'), 'title'), (_('Juego'), 'game'), (_('Idioma'), 'title_lang'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = GameTitle.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "title"),
                "c1": self.link_by(obj, "game"),
                "c2": cell(obj, "title_lang"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameTitleSelectView(BaseGameTitle, BaseSelectView):
    search_fields = ['title']


class GenreDataView(BaseGenre, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('+18'), 'explicit'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Genre.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'aliases__name', 'aliases__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "explicit"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GenreSelectView(BaseGenre, BaseSelectView):
    search_fields = ['name', 'name_esp', 'aliases__name', 'aliases__name_esp']


class MediumDataView(BaseMedium, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Medium.objects.all()
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


class MediumSelectView(BaseMedium, BaseSelectView):
    search_fields = ['name', 'name_esp']


class PlatformDataView(BasePlatform, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Platform.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"), "c1": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PlatformSelectView(BasePlatform, BaseSelectView):
    search_fields = ['name', 'name_esp']


class ReleaseDataView(BaseReleaseContext, AdminDataView):
    columns = [(_('Juego'), 'game'), (_('Título'), 'title'), (_('Fecha'), 'released'), (_('Oficial'), 'official'), (_('Parche'), 'patch'), (_('VNDB'), 'vndb_id'), (_('Activo'), 'is_active')]
    filters = ReleaseFilters

    def get(self, request, tipo=None, pk=None):
        qs = Release.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'alttitle', 'game__title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "game"),
                "c1": cell(obj, "title"),
                "c2": cell(obj, "released"),
                "c3": cell(obj, "official"),
                "c4": cell(obj, "patch"),
                "c5": cell(obj, "vndb_id"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameLogDataView(BaseGameLog, AdminDataView):
    columns = [(_('#'), 'id'), (_('Nivel'), 'get_level_display'), (_('Proceso'), 'process'), (_('Mensaje'), 'message'), (_('Momento'), 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = GameLog.objects.all()
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


def _juego_de(obj):
    """Nombre del juego al que pertenece una fila Data de VNDB (personaje / lanzamiento), por su VN."""
    from django.utils.html import escape
    from apps.games.models import DataVndbGame, Game
    vid = getattr(obj, "vndb_id_vn", None)
    if not vid:
        return ""
    juego = Game.objects.filter(vndb_id=vid).only("title").first()
    if juego:
        return escape(juego.title)
    fila = DataVndbGame.objects.filter(vndb_id=vid).only("data").first()
    titulo = (fila.data or {}).get("title") if fila and isinstance(fila.data, dict) else ""
    return escape(titulo) if titulo else f"v{vid}"


DataVndbCharacterDataView.col_juego = staticmethod(_juego_de)


DataVndbReleaseDataView.col_juego = staticmethod(_juego_de)


# ==============================================================================
# Público
# ==============================================================================


class CharacterPublicDataView(BaseCharacterContext, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = CharacterFilters
    priority = {"ficha": 1}
    detail_url_name = "games:character-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Character.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["name"], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CreatorPublicDataView(BaseCreatorContext, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = CreatorFilters
    priority = {"ficha": 1}
    detail_url_name = "games:creator-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Creator.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'nicknames__nickname'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PublisherPublicDataView(BaseCreator, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = CreatorFilters
    priority = {"ficha": 1}
    detail_url_name = "games:creator-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Creator.objects.all()
        qs = qs.filter(con_relacion(Creator, "published_games"))
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'nicknames__nickname'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GamePublicDataView(BaseGameContext, PublicDataView):
    columns = [(_("Título"), "ficha"), (_("Versión"), "version")]
    filters = GameFilters
    priority = {"ficha": 1}
    detail_url_name = "games:game-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Game.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'titles__title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": cell(obj, "version"),
                "acciones": self.row_actions(obj, request, str(obj.title or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameImagesPublicDataView(BaseGameImageContext, PublicDataView):
    columns = [(_("Imagen"), "image")]
    """Galería de un juego: sus imágenes extra en tarjetas."""
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = GameImage.objects.all()
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


class ReleasePublicDataView(BaseReleaseContext, PublicDataView):
    columns = [(_("Título"), "ficha"), (_("Fecha"), "released")]
    filters = ReleaseFilters
    priority = {"ficha": 1}
    detail_url_name = ""

    def get(self, request, tipo=None, pk=None):
        qs = Release.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["title", "alttitle"], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), "", str(obj.title or ''), meta_line(obj)),
                "c1": cell(obj, "released"),
                "acciones": self.row_actions(obj, request, str(obj.title or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": "", "card_sub": str(obj.released or ''), "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ReleaseImageDataView(BaseReleaseImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Lanzamiento'), 'release'), (_('Orden'), 'order'), (_('Tipo de arte'), 'label'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(ReleaseImage.objects.select_related("release"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url', 'release__title'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "release"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "label"),
                "c4": cell(obj, "image_url", truncar=60),
                "c5": cell(obj, "estado_descarga"),
                "c6": cell(obj, "download_attempts"),
                "c7": cell(obj, "download_error", truncar=40),
                "c8": cell(obj, "en_nube"),
                "c9": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "release", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class TagDataView(BaseTag, AdminDataView):
    columns = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Descripción', 'description'), ('Imagen', 'image')]

    def get(self, request, tipo=None, pk=None):
        qs = Tag.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'slug', 'aliases__name', 'aliases__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "name_esp"),
                "c2": cell(obj, "slug"),
                "c3": cell(obj, "description"),
                "c4": cell(obj, "image"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class TagAliasDataView(BaseTagAliasContext, AdminDataView):
    columns = [(_('Alias'), 'name'), (_('Alias (ES)'), 'name_esp'), (_('Etiqueta'), 'tag'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = TagAlias.objects.all().select_related(*('tag',))
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'tag__name', 'tag__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "name_esp"),
                "c2": self.link_by(obj, "tag"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)
