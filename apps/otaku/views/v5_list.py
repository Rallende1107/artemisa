"""otaku · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.otaku import tasks
from apps.otaku.views.base import BaseCompanyImageMal, BasePersonImageMal, BaseAnime, BaseAnimeCharacter, BaseAnimeImage, BaseAnimeSong, BaseAnimeStaff, BaseAnimeTitle, BaseCharacter, BaseCharacterImage, BaseCharacterNickname, BaseCharacterVoice, BaseCompanyMAL, BaseDataAnilistAnime, BaseDataAnilistCharacter, BaseDataAnilistManga, BaseDataAnilistPerson, BaseDataMalAnime, BaseDataMalAnimeCharacter, BaseDataMalAnimePicture, BaseDataMalAnimeStaff, BaseDataMalCharacter, BaseDataMalCharacterPicture, BaseDataMalManga, BaseDataMalMangaCharacter, BaseDataMalMangaPicture, BaseDataMalPerson, BaseDataMalPersonPicture, BaseDemographic, BaseDemographicAlias, BaseDemographicAliasContext, BaseGenre, BaseGenreAlias, BaseGenreAliasContext, BaseLicensor, BaseManga, BaseMangaAuthor, BaseMangaCharacter, BaseMangaImage, BaseMangaTitle, BaseOtakuLog, BasePersonMAL, BaseProducer, BaseRelation, BaseRole, BaseRoleContext, BaseSerialization, BaseSource, BaseStatus, BaseStudio, BaseTheme, BaseThemeAlias, BaseThemeAliasContext, BaseType, BaseYear
from core.shared.views.base import AdminListByView, AdminListView, PublicListView
from core.shared.views.imports import DataBulkMixin


# ==============================================================================
# Gestión
# ==============================================================================


class AnimeListView(BaseAnime, AdminListView):
    data_url = "panel:anime_data"
    create_url = "panel:anime_create"
    home_url = "panel:otaku-home"
    title = _("Lista de animes")
    buttons = [("panel:anime-image_list", _("Imágenes"), "images")]


class AnimePublicListView(BaseAnime, PublicListView):
    data_url = "otaku:anime-catalog-data"
    background_image = "bg-otaku-anime"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    title = _("Anime")
    icon = "bi-collection-play"
    subtitle = _("Series y películas de animación.")
    home_url = "otaku:home"
    home_label = _("otaku")


class AnimeCharacterListView(BaseAnimeCharacter, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:anime-character_data"
    create_url = "panel:anime-character_create"
    title = _("Lista de personajes de anime")


class AnimeImageListView(BaseAnimeImage, AdminListView):
    home_url = "panel:otaku-home"
    buttons = (("panel:anime-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:anime-image_data"
    create_url = "panel:anime-image_create"
    title = _("Lista de imágenes extra")


class AnimeSongListView(BaseAnimeSong, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:anime-song_data"
    create_url = "panel:anime-song_create"
    title = _("Lista de canciones de anime")


class AnimeStaffListView(BaseAnimeStaff, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:anime-staff_data"
    create_url = "panel:anime-staff_create"
    title = _("Lista de staff de anime")


class AnimeTitleListView(BaseAnimeTitle, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:anime-title_data"
    create_url = "panel:anime-title_create"
    title = _("Lista de títulos")


class CharacterListView(BaseCharacter, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:character_data"
    create_url = "panel:character_create"
    title = _("Lista de personajes")


class CharacterPublicListView(BaseCharacter, PublicListView):
    """Catálogo público de PERSONAJES de anime y manga (estilo MAL)."""
    data_url = "otaku:characters-catalog-data"
    background_image = "bg-otaku-character"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    title = _("Personajes")
    icon = "bi-emoji-smile"
    subtitle = _("Personajes de anime y manga.")
    home_url = "otaku:home"
    home_label = _("otaku")


class CharacterImageListView(BaseCharacterImage, AdminListView):
    home_url = "panel:otaku-home"
    buttons = (("panel:character-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:character-image_data"
    create_url = "panel:character-image_create"
    title = _("Lista de imágenes extra")


class CharacterNicknameListView(BaseCharacterNickname, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:character-nickname_data"
    create_url = "panel:character-nickname_create"
    title = _("Lista de apodos")


class CharacterVoiceListView(BaseCharacterVoice, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:character-voice_data"
    create_url = "panel:character-voice_create"
    title = _("Lista de voces de personaje")


class CompanyMALListView(BaseCompanyMAL, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:company-mal_data"
    create_url = "panel:company-mal_create"
    buttons = (("panel:company-mal_link", _("Enlazar a compañía existente"), "link-45deg"),
                  ("panel:company-image-mal_list", _("Imágenes"), "images"))
    title = _("Lista de compañías (MAL)")


class DataAnilistAnimeListView(BaseDataAnilistAnime, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-anilist-anime_data"
    create_url = "panel:data-anilist-anime_create"
    export_url = "panel:data-anilist-anime_export"      # «Generar dump»
    import_url = "panel:anilist-anime"    # «Importar» → el lanzador de AniList


class DataAnilistCharacterListView(BaseDataAnilistCharacter, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-anilist-character_data"
    create_url = "panel:data-anilist-character_create"
    export_url = "panel:data-anilist-character_export"      # «Generar dump»
    import_url = "panel:anilist-character"    # «Importar» → el lanzador de AniList


class DataAnilistMangaListView(BaseDataAnilistManga, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-anilist-manga_data"
    create_url = "panel:data-anilist-manga_create"
    export_url = "panel:data-anilist-manga_export"      # «Generar dump»
    import_url = "panel:anilist-manga"    # «Importar» → el lanzador de AniList


class DataAnilistPersonListView(BaseDataAnilistPerson, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-anilist-person_data"
    create_url = "panel:data-anilist-person_create"
    export_url = "panel:data-anilist-person_export"      # «Generar dump»
    import_url = "panel:anilist-person"    # «Importar» → el lanzador de AniList


# ------------------------ datos crudos de importación (MAL: cargados desde los dumps) ------------------------


class DataMalAnimeListView(BaseDataMalAnime, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    export_url = "panel:data-mal-anime_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-mal-anime_data"
    buttons = (("panel:dump-mal-anime", _("Cargar dump"), "filetype-json"), ("panel:process-mal-anime", _("Procesar"), "arrow-repeat"))
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalAnimeCharacterListView(BaseDataMalAnimeCharacter, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-mal-anime-character_data"
    process_url = "panel:mal-procesar"   # botón «Procesar pendientes» de la fuente
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalAnimePictureListView(BaseDataMalAnimePicture, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-mal-anime-picture_data"
    process_url = "panel:mal-procesar"   # botón «Procesar pendientes» de la fuente
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalAnimeStaffListView(BaseDataMalAnimeStaff, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-mal-anime-staff_data"
    process_url = "panel:mal-procesar"   # botón «Procesar pendientes» de la fuente
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalCharacterListView(BaseDataMalCharacter, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    export_url = "panel:data-mal-character_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-mal-character_data"
    buttons = (("panel:dump-mal-character", _("Cargar dump"), "filetype-json"), ("panel:process-mal-character", _("Procesar"), "arrow-repeat"))
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalCharacterPictureListView(BaseDataMalCharacterPicture, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-mal-character-picture_data"
    process_url = "panel:mal-procesar"   # botón «Procesar pendientes» de la fuente
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalMangaListView(BaseDataMalManga, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    export_url = "panel:data-mal-manga_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-mal-manga_data"
    buttons = (("panel:dump-mal-manga", _("Cargar dump"), "filetype-json"), ("panel:process-mal-manga", _("Procesar"), "arrow-repeat"))
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalMangaCharacterListView(BaseDataMalMangaCharacter, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-mal-manga-character_data"
    process_url = "panel:mal-procesar"   # botón «Procesar pendientes» de la fuente
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalMangaPictureListView(BaseDataMalMangaPicture, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-mal-manga-picture_data"
    process_url = "panel:mal-procesar"   # botón «Procesar pendientes» de la fuente
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalPersonListView(BaseDataMalPerson, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    export_url = "panel:data-mal-person_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-mal-person_data"
    buttons = (("panel:dump-mal-person", _("Cargar dump"), "filetype-json"), ("panel:process-mal-person", _("Procesar"), "arrow-repeat"))
    bulk_process_task = tasks.process_otaku_pending_task


class DataMalPersonPictureListView(BaseDataMalPersonPicture, DataBulkMixin, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:data-mal-person-picture_data"
    process_url = "panel:mal-procesar"   # botón «Procesar pendientes» de la fuente
    bulk_process_task = tasks.process_otaku_pending_task


class DemographicListView(BaseDemographic, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:demographic_data"
    create_url = "panel:demographic_create"
    title = _("Lista de demografías")


class DemographicAliasListView(BaseDemographicAlias, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:demographic-alias_data"
    create_url = "panel:demographic-alias_create"
    title = _("Lista de alias de demografías")


class DemographicAliasListByView(BaseDemographicAliasContext, AdminListByView):
    """Alias acotados por su padre (`/demographic-alias/demographic/<id>/`): los alimenta DemographicAliasDataView con `/data/demographic/<id>/`."""
    home_url = "panel:otaku-home"
    create_url = "panel:demographic-alias_create"
    data_url = "panel:demographic-alias_data-by"
    full_list_url = "panel:demographic-alias_list"
    by_url = "panel:demographic-alias_by"


class GenreListView(BaseGenre, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:genre_data"
    create_url = "panel:genre_create"
    title = _("Lista de géneros")


class GenreAliasListView(BaseGenreAlias, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:genre-alias_data"
    create_url = "panel:genre-alias_create"
    title = _("Lista de alias de géneros")


class GenreAliasListByView(BaseGenreAliasContext, AdminListByView):
    """Alias acotados por su padre (`/genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`."""
    home_url = "panel:otaku-home"
    create_url = "panel:genre-alias_create"
    data_url = "panel:genre-alias_data-by"
    full_list_url = "panel:genre-alias_list"
    by_url = "panel:genre-alias_by"


class LicensorPublicListView(BaseLicensor, PublicListView):
    """Catálogo de LICENCIATARIAS de anime."""
    data_url = "otaku:licensors-catalog-data"
    background_image = "bg-otaku-licensor"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    title = _("Licenciatarias")
    icon = "bi-building"
    subtitle = _("Licenciatarias de anime.")
    home_url = "otaku:home"
    home_label = _("otaku")


class MangaListView(BaseManga, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:manga_data"
    create_url = "panel:manga_create"
    title = _("Lista de mangas")


class MangaPublicListView(BaseManga, PublicListView):
    data_url = "otaku:manga-catalog-data"
    background_image = "bg-otaku-manga"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    title = _("Manga")
    icon = "bi-book"
    subtitle = _("Manga y novelas ligeras.")
    home_url = "otaku:home"
    home_label = _("otaku")


class MangaAuthorListView(BaseMangaAuthor, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:manga-author_data"
    create_url = "panel:manga-author_create"
    title = _("Lista de autores de manga")


class MangaCharacterListView(BaseMangaCharacter, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:manga-character_data"
    create_url = "panel:manga-character_create"
    title = _("Lista de personajes de manga")


class MangaImageListView(BaseMangaImage, AdminListView):
    home_url = "panel:otaku-home"
    buttons = (("panel:manga-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:manga-image_data"
    create_url = "panel:manga-image_create"
    title = _("Lista de imágenes extra")


class MangaTitleListView(BaseMangaTitle, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:manga-title_data"
    create_url = "panel:manga-title_create"
    title = _("Lista de títulos")


class PersonMALListView(BasePersonMAL, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:person-mal_data"
    create_url = "panel:person-mal_create"
    buttons = (("panel:person-mal_link", _("Enlazar a persona existente"), "link-45deg"),
                  ("panel:person-image-mal_list", _("Imágenes"), "images"))
    title = _("Lista de personas (MAL)")


class ProducerPublicListView(BaseProducer, PublicListView):
    """Catálogo de PRODUCTORAS de anime."""
    data_url = "otaku:producers-catalog-data"
    background_image = "bg-otaku-producer"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    title = _("Productoras")
    icon = "bi-building"
    subtitle = _("Productoras de anime.")
    home_url = "otaku:home"
    home_label = _("otaku")


class RelationListView(BaseRelation, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:relation_data"
    create_url = "panel:relation_create"
    title = _("Lista de relaciones")


# Vistas FIJAS de «relacion» (una URL, una card y un fondo por cada una; sin filtros en página).


class RelationAnimeAnimeListView(BaseRelation, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:relation-anime-anime_data"
    create_url = "panel:relation_create"
    title = _("Lista de relaciones anime → anime")
    active_entity = "relation-anime-anime"
    label_plural = _("relaciones anime → anime")
    background_image = "bg-otaku-relation-anime-anime"
    background_fallback = ("bg-otaku-relation", "bg-otaku-home")


class RelationAnimeMangaListView(BaseRelation, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:relation-anime-manga_data"
    create_url = "panel:relation_create"
    title = _("Lista de relaciones anime → manga")
    active_entity = "relation-anime-manga"
    label_plural = _("relaciones anime → manga")
    background_image = "bg-otaku-relation-manga-anime"   # misma imagen que manga → anime
    background_fallback = ("bg-otaku-relation", "bg-otaku-home")


class RelationMangaAnimeListView(BaseRelation, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:relation-manga-anime_data"
    create_url = "panel:relation_create"
    title = _("Lista de relaciones manga → anime")
    active_entity = "relation-manga-anime"
    label_plural = _("relaciones manga → anime")
    background_image = "bg-otaku-relation-manga-anime"
    background_fallback = ("bg-otaku-relation", "bg-otaku-home")


class RelationMangaMangaListView(BaseRelation, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:relation-manga-manga_data"
    create_url = "panel:relation_create"
    title = _("Lista de relaciones manga → manga")
    active_entity = "relation-manga-manga"
    label_plural = _("relaciones manga → manga")
    background_image = "bg-otaku-relation-manga-manga"
    background_fallback = ("bg-otaku-relation", "bg-otaku-home")


class RoleListView(BaseRole, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:otaku-role_data"
    create_url = "panel:otaku-role_create"
    title = _("Lista de roles")


SONG_KINDS = [("OPENING", "Openings"), ("ENDING", "Endings"), ("INSERT", "Insert songs")]


class RoleListByView(BaseRoleContext, AdminListByView):
    """Lista de roles acotada por familia (`/otaku-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`."""
    home_url = "panel:otaku-home"
    create_url = "panel:otaku-role_create"
    data_url = "panel:otaku-role_data-by"
    full_list_url = "panel:otaku-role_list"
    by_url = "panel:otaku-role_by"


class SerializationPublicListView(BaseSerialization, PublicListView):
    """Catálogo de REVISTAS de serialización de manga."""
    data_url = "otaku:magazines-catalog-data"
    background_image = "bg-otaku-serialization"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    title = _("Revistas")
    icon = "bi-building"
    subtitle = _("Revistas de serialización.")
    home_url = "otaku:home"
    home_label = _("otaku")


class SourceListView(BaseSource, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:source_data"
    create_url = "panel:source_create"
    title = _("Lista de fuentes")


class StatusListView(BaseStatus, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:status_data"
    create_url = "panel:status_create"
    title = _("Lista de estados")


class StudioPublicListView(BaseStudio, PublicListView):
    """Catálogo público de ESTUDIOS de animación."""
    data_url = "otaku:studios-catalog-data"
    background_image = "bg-otaku-studio"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    title = _("Estudios")
    icon = "bi-building"
    subtitle = _("Estudios de animación.")
    home_url = "otaku:home"
    home_label = _("otaku")


class ThemeListView(BaseTheme, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:theme_data"
    create_url = "panel:theme_create"
    title = _("Lista de temas")


class ThemeAliasListView(BaseThemeAlias, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:theme-alias_data"
    create_url = "panel:theme-alias_create"
    title = _("Lista de alias de temas")


class ThemeAliasListByView(BaseThemeAliasContext, AdminListByView):
    """Alias acotados por su padre (`/theme-alias/theme/<id>/`): los alimenta ThemeAliasDataView con `/data/theme/<id>/`."""
    home_url = "panel:otaku-home"
    create_url = "panel:theme-alias_create"
    data_url = "panel:theme-alias_data-by"
    full_list_url = "panel:theme-alias_list"
    by_url = "panel:theme-alias_by"


class TypeListView(BaseType, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:type_data"
    create_url = "panel:type_create"
    title = _("Lista de tipos")


class YearListView(BaseYear, AdminListView):
    home_url = "panel:otaku-home"
    data_url = "panel:year_data"
    create_url = "panel:year_create"
    title = _("Lista de años")


class OtakuLogListView(BaseOtakuLog, AdminListView):
    home_url = "panel:otaku-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:otaku-log_data"
    create_url = "panel:otaku-log_create"
    title = _("Lista de log de otaku")


class CompanyImageMalListView(BaseCompanyImageMal, AdminListView):
    """Lista FIJA: las imágenes de compañías que tienen ficha MAL."""
    home_url = "panel:otaku-home"
    data_url = "panel:company-image-mal_data"
    create_url = "panel:company-image_create"
    buttons = [("panel:company-image-mal_download", _("Descargar imágenes"), "cloud-download")]
    title = _("Imágenes de compañías (MAL)")


class PersonImageMalListView(BasePersonImageMal, AdminListView):
    """Lista FIJA: las imágenes de personas que tienen ficha MAL."""
    home_url = "panel:otaku-home"
    data_url = "panel:person-image-mal_data"
    create_url = "panel:person-image_create"
    buttons = [("panel:person-image-mal_download", _("Descargar imágenes"), "cloud-download")]
    title = _("Imágenes de personas (MAL)")

