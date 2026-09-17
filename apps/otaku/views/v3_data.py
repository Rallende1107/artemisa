"""otaku · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company, CompanyImage
from apps.otaku.models import Anime, AnimeCharacter, AnimeImage, AnimeSong, AnimeStaff, AnimeTitle, Character, CharacterImage, CharacterNickname, CharacterVoice, CompanyMAL, DataAnilistAnime, DataAnilistCharacter, DataAnilistManga, DataAnilistPerson, DataMalAnime, DataMalAnimeCharacter, DataMalAnimePicture, DataMalAnimeStaff, DataMalCharacter, DataMalCharacterPicture, DataMalManga, DataMalMangaCharacter, DataMalMangaPicture, DataMalPerson, DataMalPersonPicture, Demographic, DemographicAlias, Genre, GenreAlias, Manga, MangaAuthor, MangaCharacter, MangaImage, MangaTitle, OtakuLog, PersonMAL, Relation, Role, Source, Status, Theme, ThemeAlias, Type, Year
from apps.otaku.views.base import BaseAnime, BaseAnimeCharacter, BaseAnimeCharacterContext, BaseAnimeContext, BaseAnimeImage, BaseAnimeImageContext, BaseAnimeSong, BaseAnimeSongContext, BaseAnimeStaff, BaseAnimeStaffContext, BaseAnimeTitle, BaseAnimeTitleContext, BaseCharacter, BaseCharacterContext, BaseCharacterImage, BaseCharacterImageContext, BaseCharacterNickname, BaseCharacterNicknameContext, BaseCharacterVoice, BaseCharacterVoiceContext, BaseCompanyImageMal, BaseCompanyMAL, BaseDataAnilistAnime, BaseDataAnilistCharacter, BaseDataAnilistManga, BaseDataAnilistPerson, BaseDataMalAnime, BaseDataMalAnimeCharacter, BaseDataMalAnimePicture, BaseDataMalAnimeStaff, BaseDataMalCharacter, BaseDataMalCharacterPicture, BaseDataMalManga, BaseDataMalMangaCharacter, BaseDataMalMangaPicture, BaseDataMalPerson, BaseDataMalPersonPicture, BaseDemographic, BaseDemographicAliasContext, BaseGenre, BaseGenreAliasContext, BaseLicensor, BaseManga, BaseMangaAuthor, BaseMangaAuthorContext, BaseMangaCharacter, BaseMangaCharacterContext, BaseMangaContext, BaseMangaImage, BaseMangaImageContext, BaseMangaTitle, BaseMangaTitleContext, BaseOtakuLog, BasePersonImageMal, BasePersonMAL, BasePersonMALContext, BaseProducer, BaseRelation, BaseRole, BaseRoleContext, BaseSerialization, BaseSource, BaseStatus, BaseStudio, BaseTheme, BaseThemeAliasContext, BaseType, BaseYear
from apps.otaku.views.v2_filters import AnimeCharacterFilters, AnimeFilters, AnimeSongFilters, CharacterFilters, LicensorFilters, MangaCharacterFilters, MangaFilters, ProducerFilters, RoleFilters, SerializationFilters, StudioFilters
from apps.people.models import PersonImage
from core.shared.models.choices import RelationMedia
from core.shared.views.base import AdminDataView, BaseSelectView, PublicDataView
from core.shared.views.filters import DatosFilters, ImagenesFilters, LogFilters
from core.utils.queries import con_nube, con_relacion
from core.utils.views_base import cell, cell_cover, cell_miniatura, meta_line


# ==============================================================================
# Gestión
# ==============================================================================


class AnimeDataView(BaseAnimeContext, AdminDataView):
    columns = [(_('Título'), "ficha"), (_('Tipo'), 'anime_type'), (_('Estado'), 'status'), (_('Año'), 'year'), (_('Ep.'), 'episodes'), (_('Activo'), 'is_active')]
    filters = AnimeFilters

    def get(self, request, tipo=None, pk=None):
        qs = Anime.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'title_eng', 'title_jap', 'titles__title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": self.link_by(obj, "anime_type"),
                "c2": self.link_by(obj, "status"),
                "c3": cell(obj, "year"),
                "c4": cell(obj, "episodes"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeSelectView(BaseAnime, BaseSelectView):
    search_fields = ['title', 'title_eng', 'title_jap', 'titles__title']


class AnimePublicDataView(BaseAnimeContext, PublicDataView):
    columns = [(_("Título"), "ficha"), (_("Año"), "year")]
    filters = AnimeFilters
    priority = {"ficha": 1}
    detail_url_name = "otaku:anime-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Anime.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'titles__title', 'title_eng', 'title_jap'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": cell(obj, "year"),
                "acciones": self.row_actions(obj, request, str(obj.title or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeCharacterDataView(BaseAnimeCharacterContext, AdminDataView):
    columns = [(_('Personaje'), 'character'), (_('Rol'), 'role'), (_('Anime'), 'anime'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = AnimeCharacter.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "character"),
                "c1": cell(obj, "role"),
                "c2": self.link_by(obj, "anime"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeCharacterSelectView(BaseAnimeCharacter, BaseSelectView):
    search_fields = []


class AnimeImageDataView(BaseAnimeImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Anime'), 'anime'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(AnimeImage.objects.select_related("anime"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "anime"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "anime", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeImageSelectView(BaseAnimeImage, BaseSelectView):
    search_fields = ['image_url']


class AnimeImagesPublicDataView(BaseAnimeImageContext, PublicDataView):
    """Galería de un anime: sus imágenes extra en tarjetas."""
    columns = [(_("Imagen"), "image")]
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = AnimeImage.objects.all()
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


class AnimeSongDataView(BaseAnimeSongContext, AdminDataView):
    columns = [(_('Título'), 'title'), (_('Tipo'), 'type'), (_('Nº'), 'song_id'), (_('Anime'), 'anime'), (_('Activo'), 'is_active')]
    filters = AnimeSongFilters

    def get(self, request, tipo=None, pk=None):
        qs = AnimeSong.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'title_eng'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "title"),
                "c1": self.link_by(obj, "type"),
                "c2": cell(obj, "song_id"),
                "c3": self.link_by(obj, "anime"),
                "c4": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeSongSelectView(BaseAnimeSong, BaseSelectView):
    search_fields = ['title', 'title_eng']


class AnimeStaffDataView(BaseAnimeStaffContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('Rol'), 'role'), (_('Anime'), 'anime'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = AnimeStaff.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": cell(obj, "role"),
                "c2": self.link_by(obj, "anime"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeStaffSelectView(BaseAnimeStaff, BaseSelectView):
    search_fields = []


class AnimeTitleDataView(BaseAnimeTitleContext, AdminDataView):
    columns = [(_('Título'), 'title'), (_('Anime'), 'anime'), (_('Idioma'), 'title_lang'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = AnimeTitle.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "title"),
                "c1": self.link_by(obj, "anime"),
                "c2": cell(obj, "title_lang"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeTitleSelectView(BaseAnimeTitle, BaseSelectView):
    search_fields = ['title']


class CharacterDataView(BaseCharacterContext, AdminDataView):
    columns = [(_('Nombre'), 'full_name'), (_('Kanji'), 'name_kanji'), (_('Activo'), 'is_active')]
    filters = AnimeCharacterFilters

    def get(self, request, tipo=None, pk=None):
        qs = Character.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['full_name', 'name_kanji', 'nicknames__nickname'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "full_name"),
                "c1": cell(obj, "name_kanji"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": self.sub(obj) or "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CharacterSelectView(BaseCharacter, BaseSelectView):
    search_fields = ['full_name', 'name_kanji', 'nicknames__nickname']


class CharacterPublicDataView(BaseCharacterContext, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = CharacterFilters
    priority = {"ficha": 1}
    filters_by = {"anime": AnimeCharacterFilters, "manga": MangaCharacterFilters}
    detail_url_name = "otaku:character-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Character.objects.all()
        qs = qs.prefetch_related("images")
        p, total, filtrado, objetos = self.query(request, qs, ['full_name', 'nicknames__nickname'], {'ficha': 'full_name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.full_name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.full_name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.full_name or '')), "card_image": obj.cover_url, "card_sub": self.sub(obj) or "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CharacterImageDataView(BaseCharacterImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Personaje'), 'character'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(CharacterImage.objects.select_related("character"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
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


class CharacterImageSelectView(BaseCharacterImage, BaseSelectView):
    search_fields = ['image_url']


class CharacterImagesPublicDataView(BaseCharacterImageContext, PublicDataView):
    """Galería de un personaje: sus imágenes extra en tarjetas."""
    columns = [(_("Imagen"), "image")]
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = CharacterImage.objects.all()
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


class CharacterNicknameDataView(BaseCharacterNicknameContext, AdminDataView):
    columns = [(_('Apodo'), 'nickname'), (_('Personaje'), 'character'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = CharacterNickname.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['nickname'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "nickname"),
                "c1": self.link_by(obj, "character"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CharacterNicknameSelectView(BaseCharacterNickname, BaseSelectView):
    search_fields = ['nickname']


class CharacterVoiceDataView(BaseCharacterVoiceContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('Personaje'), 'character'), (_('Idioma'), 'language'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = CharacterVoice.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": self.link_by(obj, "character"),
                "c2": cell(obj, "language"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CharacterVoiceSelectView(BaseCharacterVoice, BaseSelectView):
    search_fields = []


class CompanyMALDataView(BaseCompanyMAL, AdminDataView):
    columns = [(_('Compañía'), 'company'), (_('Tipo'), 'get_kind_display'), (_('MAL id'), 'mal_id'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = CompanyMAL.objects.select_related("company")
        p, total, filtrado, objetos = self.query(request, qs, ['company__name', 'mal_id'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "company"),
                "c1": cell(obj, "get_kind_display"),
                "c2": cell(obj, "mal_id"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": "", "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CompanyMALSelectView(BaseCompanyMAL, BaseSelectView):
    search_fields = ['company__name']
    select_related = ('company',)


class CompanyImageMalDataView(BaseCompanyImageMal, AdminDataView):
    """Solo las imágenes de compañías con ficha MAL (JOIN uno a uno por índice)."""
    columns = [(_('Imagen'), 'miniatura'), (_('Compañías'), 'company'), (_('Orden'), 'order'), (_('URL'), 'image_url'),
               (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'),
               (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(CompanyImage.objects.select_related("company").filter(company__company_mal__isnull=False))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url', 'company__name'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": cell(obj, "company"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PersonImageMalDataView(BasePersonImageMal, AdminDataView):
    """Solo las imágenes de personas con ficha MAL (JOIN uno a uno por índice)."""
    columns = [(_('Imagen'), 'miniatura'), (_('Personas'), 'person'), (_('Orden'), 'order'), (_('URL'), 'image_url'),
               (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'),
               (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(PersonImage.objects.select_related("person").filter(person__person_mal__isnull=False))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url', 'person__name'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": cell(obj, "person"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

class DataAnilistAnimeDataView(BaseDataAnilistAnime, AdminDataView):
    columns = [(_('AniList id'), 'anilist_id'), (_('MAL id'), 'id_mal'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'),
               (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Actualizado'), 'updated_at'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataAnilistAnime.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['anilist_id', 'id_mal'], {}, ('-updated_at',))
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "anilist_id"),
                "c1": cell(obj, "id_mal"),
                "c2": cell(obj, "titulo"),
                "c3": cell(obj, "data_status"),
                "c4": cell(obj, "data_processed"),
                "c5": cell(obj, "status_code"),
                "c6": cell(obj, "updated_at"),
                "c7": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataAnilistCharacterDataView(BaseDataAnilistCharacter, AdminDataView):
    columns = [(_('AniList id'), 'anilist_id'), (_('MAL id'), 'id_mal'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'),
               (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Actualizado'), 'updated_at'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataAnilistCharacter.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['anilist_id', 'id_mal'], {}, ('-updated_at',))
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "anilist_id"),
                "c1": cell(obj, "id_mal"),
                "c2": cell(obj, "titulo"),
                "c3": cell(obj, "data_status"),
                "c4": cell(obj, "data_processed"),
                "c5": cell(obj, "status_code"),
                "c6": cell(obj, "updated_at"),
                "c7": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataAnilistMangaDataView(BaseDataAnilistManga, AdminDataView):
    columns = [(_('AniList id'), 'anilist_id'), (_('MAL id'), 'id_mal'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'),
               (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Actualizado'), 'updated_at'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataAnilistManga.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['anilist_id', 'id_mal'], {}, ('-updated_at',))
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "anilist_id"),
                "c1": cell(obj, "id_mal"),
                "c2": cell(obj, "titulo"),
                "c3": cell(obj, "data_status"),
                "c4": cell(obj, "data_processed"),
                "c5": cell(obj, "status_code"),
                "c6": cell(obj, "updated_at"),
                "c7": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DataAnilistPersonDataView(BaseDataAnilistPerson, AdminDataView):
    columns = [(_('AniList id'), 'anilist_id'), (_('MAL id'), 'id_mal'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'),
               (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Actualizado'), 'updated_at'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataAnilistPerson.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['anilist_id', 'id_mal'], {}, ('-updated_at',))
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "anilist_id"),
                "c1": cell(obj, "id_mal"),
                "c2": cell(obj, "titulo"),
                "c3": cell(obj, "data_status"),
                "c4": cell(obj, "data_processed"),
                "c5": cell(obj, "status_code"),
                "c6": cell(obj, "updated_at"),
                "c7": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


# ------------------------ datos crudos de importación (MAL: cargados desde los dumps) ------------------------
class DataMalAnimeDataView(BaseDataMalAnime, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalAnime.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalAnimeCharacterDataView(BaseDataMalAnimeCharacter, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalAnimeCharacter.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalAnimePictureDataView(BaseDataMalAnimePicture, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalAnimePicture.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalAnimeStaffDataView(BaseDataMalAnimeStaff, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalAnimeStaff.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalCharacterDataView(BaseDataMalCharacter, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalCharacter.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalCharacterPictureDataView(BaseDataMalCharacterPicture, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalCharacterPicture.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalMangaDataView(BaseDataMalManga, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalManga.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalMangaCharacterDataView(BaseDataMalMangaCharacter, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalMangaCharacter.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalMangaPictureDataView(BaseDataMalMangaPicture, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalMangaPicture.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalPersonDataView(BaseDataMalPerson, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalPerson.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DataMalPersonPictureDataView(BaseDataMalPersonPicture, AdminDataView):
    columns = [(_('mal_id'), 'mal_id'), (_('Título'), 'titulo'), (_('Fetch OK'), 'data_status'), (_('Procesado'), 'data_processed'), (_('HTTP'), 'status_code'), (_('Creado'), 'created_at'), (_('Datos'), 'data'), (_('Activo'), 'is_active')]
    filters = DatosFilters

    def get(self, request, tipo=None, pk=None):
        qs = DataMalPersonPicture.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['mal_id', 'data__title', 'data__name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "mal_id"),
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


class DemographicDataView(BaseDemographic, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Demographic.objects.all()
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


class DemographicSelectView(BaseDemographic, BaseSelectView):
    search_fields = ['name', 'name_esp', 'aliases__name', 'aliases__name_esp']


class DemographicAliasDataView(BaseDemographicAliasContext, AdminDataView):
    columns = [(_('Alias'), 'name'), (_('Alias (ES)'), 'name_esp'), (_('Demografía'), 'demographic'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = DemographicAlias.objects.all().select_related(*('demographic',))
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'demographic__name', 'demographic__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "name_esp"),
                "c2": self.link_by(obj, "demographic"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


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


class LicensorPublicDataView(BaseLicensor, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = LicensorFilters
    priority = {"ficha": 1}
    detail_url_name = "companias:company-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.filter(con_relacion(Company, "animes_licensed"))
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaDataView(BaseMangaContext, AdminDataView):
    columns = [(_('Título'), "ficha"), (_('Tipo'), 'manga_type'), (_('Estado'), 'status'), (_('Año'), 'year'), (_('Caps.'), 'chapters'), (_('Activo'), 'is_active')]
    filters = MangaFilters

    def get(self, request, tipo=None, pk=None):
        qs = Manga.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'title_eng', 'title_jap', 'titles__title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": self.link_by(obj, "manga_type"),
                "c2": self.link_by(obj, "status"),
                "c3": cell(obj, "year"),
                "c4": cell(obj, "chapters"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaSelectView(BaseManga, BaseSelectView):
    search_fields = ['title', 'title_eng', 'title_jap', 'titles__title']


class MangaPublicDataView(BaseMangaContext, PublicDataView):
    columns = [(_("Título"), "ficha"), (_("Año"), "year")]
    filters = MangaFilters
    priority = {"ficha": 1}
    detail_url_name = "otaku:manga-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Manga.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'titles__title', 'title_eng', 'title_jap'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": cell(obj, "year"),
                "acciones": self.row_actions(obj, request, str(obj.title or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaAuthorDataView(BaseMangaAuthorContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('Rol'), 'role'), (_('Manga'), 'manga'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = MangaAuthor.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": cell(obj, "role"),
                "c2": self.link_by(obj, "manga"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaAuthorSelectView(BaseMangaAuthor, BaseSelectView):
    search_fields = []


class MangaCharacterDataView(BaseMangaCharacterContext, AdminDataView):
    columns = [(_('Personaje'), 'character'), (_('Rol'), 'role'), (_('Manga'), 'manga'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = MangaCharacter.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "character"),
                "c1": cell(obj, "role"),
                "c2": self.link_by(obj, "manga"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaCharacterSelectView(BaseMangaCharacter, BaseSelectView):
    search_fields = []


class MangaImageDataView(BaseMangaImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Manga'), 'manga'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(MangaImage.objects.select_related("manga"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "manga"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "manga", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaImageSelectView(BaseMangaImage, BaseSelectView):
    search_fields = ['image_url']


class MangaImagesPublicDataView(BaseMangaImageContext, PublicDataView):
    """Galería de un manga: sus imágenes extra en tarjetas."""
    columns = [(_("Imagen"), "image")]
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = MangaImage.objects.all()
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


class MangaTitleDataView(BaseMangaTitleContext, AdminDataView):
    columns = [(_('Título'), 'title'), (_('Manga'), 'manga'), (_('Idioma'), 'title_lang'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = MangaTitle.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "title"),
                "c1": self.link_by(obj, "manga"),
                "c2": cell(obj, "title_lang"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaTitleSelectView(BaseMangaTitle, BaseSelectView):
    search_fields = ['title']


class PersonMALDataView(BasePersonMALContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('MAL id'), 'mal_id'), (_('Nombre japonés'), 'nombre_japones'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = PersonMAL.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['person__full_name', 'given_name', 'family_name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": cell(obj, "mal_id"),
                "c2": cell(obj, "nombre_japones"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PersonMALSelectView(BasePersonMAL, BaseSelectView):
    search_fields = ['person__full_name', 'given_name', 'family_name']
    select_related = ('person',)


class ProducerPublicDataView(BaseProducer, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = ProducerFilters
    priority = {"ficha": 1}
    detail_url_name = "companias:company-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.filter(con_relacion(Company, "animes_produced"))
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RelationDataView(BaseRelation, AdminDataView):
    columns = [(_('Tipo'), 'relation_type'), (_('Origen'), 'from_type'), (_('Origen MAL'), 'from_mal_id'), (_('Destino'), 'to_type'), (_('Destino MAL'), 'to_mal_id'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Relation.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "relation_type"),
                "c1": cell(obj, "from_type"),
                "c2": cell(obj, "from_mal_id"),
                "c3": cell(obj, "to_type"),
                "c4": cell(obj, "to_mal_id"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RelationSelectView(BaseRelation, BaseSelectView):
    search_fields = []


class RelationAnimeAnimeDataView(RelationDataView):
    """Solo las relaciones anime → anime."""

    def get(self, request, tipo=None, pk=None):
        qs = Relation.objects.filter(from_type=RelationMedia.ANIME, to_type=RelationMedia.ANIME)
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "relation_type"),
                "c1": cell(obj, "from_type"),
                "c2": cell(obj, "from_mal_id"),
                "c3": cell(obj, "to_type"),
                "c4": cell(obj, "to_mal_id"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RelationAnimeMangaDataView(RelationDataView):
    """Solo las relaciones anime → manga."""

    def get(self, request, tipo=None, pk=None):
        qs = Relation.objects.filter(from_type=RelationMedia.ANIME, to_type=RelationMedia.MANGA)
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "relation_type"),
                "c1": cell(obj, "from_type"),
                "c2": cell(obj, "from_mal_id"),
                "c3": cell(obj, "to_type"),
                "c4": cell(obj, "to_mal_id"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RelationMangaAnimeDataView(RelationDataView):
    """Solo las relaciones manga → anime."""

    def get(self, request, tipo=None, pk=None):
        qs = Relation.objects.filter(from_type=RelationMedia.MANGA, to_type=RelationMedia.ANIME)
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "relation_type"),
                "c1": cell(obj, "from_type"),
                "c2": cell(obj, "from_mal_id"),
                "c3": cell(obj, "to_type"),
                "c4": cell(obj, "to_mal_id"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RelationMangaMangaDataView(RelationDataView):
    """Solo las relaciones manga → manga."""

    def get(self, request, tipo=None, pk=None):
        qs = Relation.objects.filter(from_type=RelationMedia.MANGA, to_type=RelationMedia.MANGA)
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "relation_type"),
                "c1": cell(obj, "from_type"),
                "c2": cell(obj, "from_mal_id"),
                "c3": cell(obj, "to_type"),
                "c4": cell(obj, "to_mal_id"),
                "c5": cell(obj, "is_active"),
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


class SerializationPublicDataView(BaseSerialization, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = SerializationFilters
    priority = {"ficha": 1}
    detail_url_name = "companias:company-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.filter(con_relacion(Company, "mangas_serialized"))
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SourceDataView(BaseSource, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Source.objects.all()
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


class SourceSelectView(BaseSource, BaseSelectView):
    search_fields = ['name', 'name_esp']


class StatusDataView(BaseStatus, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Status.objects.all()
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


class StatusSelectView(BaseStatus, BaseSelectView):
    search_fields = ['name', 'name_esp']


class StudioPublicDataView(BaseStudio, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = StudioFilters
    priority = {"ficha": 1}
    detail_url_name = "companias:company-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.filter(con_relacion(Company, "animes_studio"))
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ThemeDataView(BaseTheme, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Theme.objects.all()
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


class ThemeSelectView(BaseTheme, BaseSelectView):
    search_fields = ['name', 'name_esp', 'aliases__name', 'aliases__name_esp']


class ThemeAliasDataView(BaseThemeAliasContext, AdminDataView):
    columns = [(_('Alias'), 'name'), (_('Alias (ES)'), 'name_esp'), (_('Tema'), 'theme'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = ThemeAlias.objects.all().select_related(*('theme',))
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'theme__name', 'theme__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "name_esp"),
                "c2": self.link_by(obj, "theme"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class TypeDataView(BaseType, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Type.objects.all()
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


class TypeSelectView(BaseType, BaseSelectView):
    search_fields = ['name', 'name_esp']


class YearDataView(BaseYear, AdminDataView):
    columns = [(_('Año'), 'year'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Year.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['year'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "year"),
                "c1": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class YearSelectView(BaseYear, BaseSelectView):
    search_fields = ['year']


class OtakuLogDataView(BaseOtakuLog, AdminDataView):
    columns = [(_('#'), 'id'), (_('Nivel'), 'get_level_display'), (_('Proceso'), 'process'), (_('Mensaje'), 'message'), (_('Momento'), 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = OtakuLog.objects.all()
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
