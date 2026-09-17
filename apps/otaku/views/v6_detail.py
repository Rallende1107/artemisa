"""otaku · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.otaku.services import mal_dump_process
from apps.otaku.views.base import BaseAnime, BaseAnimeCharacter, BaseAnimeImage, BaseAnimeSong, BaseAnimeStaff, BaseAnimeTitle, BaseCharacter, BaseCharacterImage, BaseCharacterNickname, BaseCharacterVoice, BaseCompanyMAL, BaseDataAnilistAnime, BaseDataAnilistCharacter, BaseDataAnilistManga, BaseDataAnilistPerson, BaseDataMalAnime, BaseDataMalAnimeCharacter, BaseDataMalAnimePicture, BaseDataMalAnimeStaff, BaseDataMalCharacter, BaseDataMalCharacterPicture, BaseDataMalManga, BaseDataMalMangaCharacter, BaseDataMalMangaPicture, BaseDataMalPerson, BaseDataMalPersonPicture, BaseDemographic, BaseDemographicAlias, BaseGenre, BaseGenreAlias, BaseManga, BaseMangaAuthor, BaseMangaCharacter, BaseMangaImage, BaseMangaTitle, BaseOtakuLog, BasePersonMAL, BaseRelation, BaseRole, BaseSource, BaseStatus, BaseTheme, BaseThemeAlias, BaseType, BaseYear
from core.shared.views.base import BaseAdminDetailView, BasePublicDetailView


# ==============================================================================
# Gestión
# ==============================================================================


class AnimeDetailView(BaseAnime, BaseAdminDetailView):
    template_name = "otaku/detail/anime.html"   # la misma ficha que el público, con los botones de gestión
    update_url = "panel:anime_update"
    delete_url = "panel:anime_delete"
    list_url = "panel:anime_list"
    toggle_url = "panel:anime_toggle"
    by_url = "panel:anime_by"
    tabs = [("personajes", _("Personajes"), "panel:anime-character_by", "anime"),
            ("equipo", _("Equipo"), "panel:anime-staff_by", "anime"),
            ("canciones", _("Banda sonora"), "panel:anime-song_by", "anime"),
            ("imagenes", _("Imágenes"), "panel:anime-image_by", "anime"),
            ("titulos", _("Títulos"), "panel:anime-title_by", "anime")]


class AnimePublicDetailView(BaseAnime, BasePublicDetailView):
    """Ficha pública de un anime: el mismo HTML que en gestión, sin botones y con la colección."""
    template_name = "otaku/detail/anime.html"
    list_url = "otaku:anime-catalog"
    by_url = "otaku:anime-by"
    section = "otaku"
    collect_kind = "anime"
    tabs = [("personajes", _("Personajes"), "otaku:characters-by", "anime"),
            ("voces", _("Actores de voz"), "personas:people-by", "voces-anime"),
            ("equipo", _("Equipo"), "personas:people-by", "equipo-anime"),
            ("imagenes", _("Imágenes"), "otaku:anime-images-by", "anime")]


class AnimeCharacterDetailView(BaseAnimeCharacter, BaseAdminDetailView):
    template_name = "otaku/detail/anime_character.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:anime-character_update"
    delete_url = "panel:anime-character_delete"
    list_url = "panel:anime-character_list"
    toggle_url = "panel:anime-character_toggle"


class AnimeImageDetailView(BaseAnimeImage, BaseAdminDetailView):
    template_name = "otaku/detail/anime_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:anime-image_update"
    delete_url = "panel:anime-image_delete"
    list_url = "panel:anime-image_list"
    toggle_url = "panel:anime-image_toggle"


class AnimeSongDetailView(BaseAnimeSong, BaseAdminDetailView):
    template_name = "otaku/detail/anime_song.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:anime-song_update"
    delete_url = "panel:anime-song_delete"
    list_url = "panel:anime-song_list"
    toggle_url = "panel:anime-song_toggle"


class AnimeStaffDetailView(BaseAnimeStaff, BaseAdminDetailView):
    template_name = "otaku/detail/anime_staff.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:anime-staff_update"
    delete_url = "panel:anime-staff_delete"
    list_url = "panel:anime-staff_list"
    toggle_url = "panel:anime-staff_toggle"


class AnimeTitleDetailView(BaseAnimeTitle, BaseAdminDetailView):
    template_name = "otaku/detail/anime_title.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:anime-title_update"
    delete_url = "panel:anime-title_delete"
    list_url = "panel:anime-title_list"
    toggle_url = "panel:anime-title_toggle"


class CharacterDetailView(BaseCharacter, BaseAdminDetailView):
    template_name = "otaku/detail/character.html"
    update_url = "panel:character_update"
    delete_url = "panel:character_delete"
    list_url = "panel:character_list"
    toggle_url = "panel:character_toggle"
    tabs = [("voces", _("Voces"), "panel:character-voice_by", "personaje"),
            ("animes", _("Anime"), "panel:anime-character_by", "personaje"),
            ("mangas", _("Manga"), "panel:manga-character_by", "personaje"),
            ("imagenes", _("Imágenes"), "panel:character-image_by", "personaje"),
            ("apodos", _("Apodos"), "panel:character-nickname_by", "personaje")]


class CharacterPublicDetailView(BaseCharacter, BasePublicDetailView):
    template_name = "otaku/detail/character.html"
    list_url = "otaku:characters-catalog"
    section = "otaku"
    collect_kind = "character"
    tabs = [("voces", _("Voces"), "personas:people-by", "voces-personaje"),
            ("animes", _("Anime"), "otaku:anime-by", "personaje"),
            ("mangas", _("Manga"), "otaku:manga-by", "personaje"),
            ("imagenes", _("Imágenes"), "otaku:character-images-by", "personaje")]


class CharacterImageDetailView(BaseCharacterImage, BaseAdminDetailView):
    template_name = "otaku/detail/character_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:character-image_update"
    delete_url = "panel:character-image_delete"
    list_url = "panel:character-image_list"
    toggle_url = "panel:character-image_toggle"


class CharacterNicknameDetailView(BaseCharacterNickname, BaseAdminDetailView):
    template_name = "otaku/detail/character_nickname.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:character-nickname_update"
    delete_url = "panel:character-nickname_delete"
    list_url = "panel:character-nickname_list"
    toggle_url = "panel:character-nickname_toggle"


class CharacterVoiceDetailView(BaseCharacterVoice, BaseAdminDetailView):
    template_name = "otaku/detail/character_voice.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:character-voice_update"
    delete_url = "panel:character-voice_delete"
    list_url = "panel:character-voice_list"
    toggle_url = "panel:character-voice_toggle"


class CompanyMALDetailView(BaseCompanyMAL, BaseAdminDetailView):
    template_name = "otaku/detail/company_mal.html"
    update_url = "panel:company-mal_update"
    delete_url = "panel:company-mal_delete"
    list_url = "panel:company-mal_list"
    toggle_url = "panel:company-mal_toggle"


class DataAnilistAnimeDetailView(BaseDataAnilistAnime, BaseAdminDetailView):
    template_name = "otaku/detail/data_anilist_anime.html"
    update_url = "panel:data-anilist-anime_update"
    delete_url = "panel:data-anilist-anime_delete"
    list_url = "panel:data-anilist-anime_list"


class DataAnilistCharacterDetailView(BaseDataAnilistCharacter, BaseAdminDetailView):
    template_name = "otaku/detail/data_anilist_character.html"
    update_url = "panel:data-anilist-character_update"
    delete_url = "panel:data-anilist-character_delete"
    list_url = "panel:data-anilist-character_list"


class DataAnilistMangaDetailView(BaseDataAnilistManga, BaseAdminDetailView):
    template_name = "otaku/detail/data_anilist_manga.html"
    update_url = "panel:data-anilist-manga_update"
    delete_url = "panel:data-anilist-manga_delete"
    list_url = "panel:data-anilist-manga_list"


class DataAnilistPersonDetailView(BaseDataAnilistPerson, BaseAdminDetailView):
    template_name = "otaku/detail/data_anilist_person.html"
    update_url = "panel:data-anilist-person_update"
    delete_url = "panel:data-anilist-person_delete"
    list_url = "panel:data-anilist-person_list"


# ------------------------ datos crudos de importación (MAL: cargados desde los dumps) ------------------------
class DataMalAnimeDetailView(BaseDataMalAnime, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_anime.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-anime_update"
    delete_url = "panel:data-mal-anime_delete"
    list_url = "panel:data-mal-anime_list"
    reprocesar = staticmethod(lambda obj: mal_dump_process.process_anime(obj.mal_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataMalAnimeCharacterDetailView(BaseDataMalAnimeCharacter, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_anime_character.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-anime-character_update"
    delete_url = "panel:data-mal-anime-character_delete"
    list_url = "panel:data-mal-anime-character_list"


class DataMalAnimePictureDetailView(BaseDataMalAnimePicture, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_anime_picture.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-anime-picture_update"
    delete_url = "panel:data-mal-anime-picture_delete"
    list_url = "panel:data-mal-anime-picture_list"


class DataMalAnimeStaffDetailView(BaseDataMalAnimeStaff, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_anime_staff.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-anime-staff_update"
    delete_url = "panel:data-mal-anime-staff_delete"
    list_url = "panel:data-mal-anime-staff_list"


class DataMalCharacterDetailView(BaseDataMalCharacter, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_character.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-character_update"
    delete_url = "panel:data-mal-character_delete"
    list_url = "panel:data-mal-character_list"
    reprocesar = staticmethod(lambda obj: mal_dump_process.process_character(obj.mal_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataMalCharacterPictureDetailView(BaseDataMalCharacterPicture, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_character_picture.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-character-picture_update"
    delete_url = "panel:data-mal-character-picture_delete"
    list_url = "panel:data-mal-character-picture_list"


class DataMalMangaDetailView(BaseDataMalManga, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_manga.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-manga_update"
    delete_url = "panel:data-mal-manga_delete"
    list_url = "panel:data-mal-manga_list"
    reprocesar = staticmethod(lambda obj: mal_dump_process.process_manga(obj.mal_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataMalMangaCharacterDetailView(BaseDataMalMangaCharacter, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_manga_character.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-manga-character_update"
    delete_url = "panel:data-mal-manga-character_delete"
    list_url = "panel:data-mal-manga-character_list"


class DataMalMangaPictureDetailView(BaseDataMalMangaPicture, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_manga_picture.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-manga-picture_update"
    delete_url = "panel:data-mal-manga-picture_delete"
    list_url = "panel:data-mal-manga-picture_list"


class DataMalPersonDetailView(BaseDataMalPerson, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_person.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-person_update"
    delete_url = "panel:data-mal-person_delete"
    list_url = "panel:data-mal-person_list"
    reprocesar = staticmethod(lambda obj: mal_dump_process.process_person(obj.mal_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataMalPersonPictureDetailView(BaseDataMalPersonPicture, BaseAdminDetailView):
    template_name = "otaku/detail/data_mal_person_picture.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-mal-person-picture_update"
    delete_url = "panel:data-mal-person-picture_delete"
    list_url = "panel:data-mal-person-picture_list"


class DemographicDetailView(BaseDemographic, BaseAdminDetailView):
    template_name = "otaku/detail/demographic.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:demographic_update"
    delete_url = "panel:demographic_delete"
    list_url = "panel:demographic_list"
    toggle_url = "panel:demographic_toggle"


class DemographicAliasDetailView(BaseDemographicAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:demographic-alias_list"
    update_url = "panel:demographic-alias_update"
    delete_url = "panel:demographic-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Demografía', 'demographic')]


class GenreDetailView(BaseGenre, BaseAdminDetailView):
    template_name = "otaku/detail/genre.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:genre_update"
    delete_url = "panel:genre_delete"
    list_url = "panel:genre_list"
    toggle_url = "panel:genre_toggle"


class GenreAliasDetailView(BaseGenreAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:genre-alias_list"
    update_url = "panel:genre-alias_update"
    delete_url = "panel:genre-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Género', 'genre')]


class MangaDetailView(BaseManga, BaseAdminDetailView):
    template_name = "otaku/detail/manga.html"
    update_url = "panel:manga_update"
    delete_url = "panel:manga_delete"
    list_url = "panel:manga_list"
    toggle_url = "panel:manga_toggle"
    by_url = "panel:manga_by"
    tabs = [("personajes", _("Personajes"), "panel:manga-character_by", "manga"),
            ("autores", _("Autores"), "panel:manga-author_by", "manga"),
            ("imagenes", _("Imágenes"), "panel:manga-image_by", "manga"),
            ("titulos", _("Títulos"), "panel:manga-title_by", "manga")]


class MangaPublicDetailView(BaseManga, BasePublicDetailView):
    template_name = "otaku/detail/manga.html"
    list_url = "otaku:manga-catalog"
    by_url = "otaku:manga-by"
    section = "otaku"
    collect_kind = "manga"
    tabs = [("personajes", _("Personajes"), "otaku:characters-by", "manga"),
            ("autores", _("Autores"), "personas:people-by", "autores-manga"),
            ("imagenes", _("Imágenes"), "otaku:manga-images-by", "manga")]


class MangaAuthorDetailView(BaseMangaAuthor, BaseAdminDetailView):
    template_name = "otaku/detail/manga_author.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:manga-author_update"
    delete_url = "panel:manga-author_delete"
    list_url = "panel:manga-author_list"
    toggle_url = "panel:manga-author_toggle"


class MangaCharacterDetailView(BaseMangaCharacter, BaseAdminDetailView):
    template_name = "otaku/detail/manga_character.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:manga-character_update"
    delete_url = "panel:manga-character_delete"
    list_url = "panel:manga-character_list"
    toggle_url = "panel:manga-character_toggle"


class MangaImageDetailView(BaseMangaImage, BaseAdminDetailView):
    template_name = "otaku/detail/manga_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:manga-image_update"
    delete_url = "panel:manga-image_delete"
    list_url = "panel:manga-image_list"
    toggle_url = "panel:manga-image_toggle"


class MangaTitleDetailView(BaseMangaTitle, BaseAdminDetailView):
    template_name = "otaku/detail/manga_title.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:manga-title_update"
    delete_url = "panel:manga-title_delete"
    list_url = "panel:manga-title_list"
    toggle_url = "panel:manga-title_toggle"


class PersonMALDetailView(BasePersonMAL, BaseAdminDetailView):
    template_name = "otaku/detail/person_mal.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:person-mal_update"
    delete_url = "panel:person-mal_delete"
    list_url = "panel:person-mal_list"
    toggle_url = "panel:person-mal_toggle"


class RelationDetailView(BaseRelation, BaseAdminDetailView):
    template_name = "otaku/detail/relation.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:relation_update"
    delete_url = "panel:relation_delete"
    list_url = "panel:relation_list"
    toggle_url = "panel:relation_toggle"


class RoleDetailView(BaseRole, BaseAdminDetailView):
    template_name = "otaku/detail/role.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:otaku-role_update"
    delete_url = "panel:otaku-role_delete"
    list_url = "panel:otaku-role_list"
    toggle_url = "panel:otaku-role_toggle"


class SourceDetailView(BaseSource, BaseAdminDetailView):
    template_name = "otaku/detail/source.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:source_update"
    delete_url = "panel:source_delete"
    list_url = "panel:source_list"
    toggle_url = "panel:source_toggle"


class StatusDetailView(BaseStatus, BaseAdminDetailView):
    template_name = "otaku/detail/status.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:status_update"
    delete_url = "panel:status_delete"
    list_url = "panel:status_list"
    toggle_url = "panel:status_toggle"


class ThemeDetailView(BaseTheme, BaseAdminDetailView):
    template_name = "otaku/detail/theme.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:theme_update"
    delete_url = "panel:theme_delete"
    list_url = "panel:theme_list"
    toggle_url = "panel:theme_toggle"


class ThemeAliasDetailView(BaseThemeAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:theme-alias_list"
    update_url = "panel:theme-alias_update"
    delete_url = "panel:theme-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Tema', 'theme')]


class TypeDetailView(BaseType, BaseAdminDetailView):
    template_name = "otaku/detail/type.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:type_update"
    delete_url = "panel:type_delete"
    list_url = "panel:type_list"
    toggle_url = "panel:type_toggle"


class YearDetailView(BaseYear, BaseAdminDetailView):
    template_name = "otaku/detail/year.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:year_update"
    delete_url = "panel:year_delete"
    list_url = "panel:year_list"
    toggle_url = "panel:year_toggle"


class OtakuLogDetailView(BaseOtakuLog, BaseAdminDetailView):
    template_name = "otaku/detail/otaku_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:otaku-log_update"
    delete_url = "panel:otaku-log_delete"
    list_url = "panel:otaku-log_list"
