"""games · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.games.services import vndb
from apps.games.views.base import BaseCharacter, BaseCharacterImage, BaseCharacterRole, BaseCreator, BaseCreatorLink, BaseCreatorNickname, BaseDataF95Creator, BaseDataF95Game, BaseDataVndbCharacter, BaseDataVndbCreator, BaseDataVndbGame, BaseDataVndbRelease, BaseDevelopmentEngine, BaseGame, BaseGameImage, BaseGameLink, BaseGameLog, BaseGameTitle, BaseGenre, BaseGenreAlias, BaseMedium, BasePlatform, BaseRelease, BaseReleaseImage, BaseTag, BaseTagAlias
from core.shared.views.base import BaseAdminDetailView, BasePublicDetailView


# ==============================================================================
# Gestión
# ==============================================================================


# ------------------------ personajes de juego (VNDB) ------------------------

class CharacterDetailView(BaseCharacter, BaseAdminDetailView):
    template_name = "games/detail/character.html"
    update_url = "panel:game-character_update"
    delete_url = "panel:game-character_delete"
    list_url = "panel:game-character_list"
    toggle_url = "panel:game-character_toggle"
    tabs = [("juegos", _("Juegos"), "panel:game-character-role_by", "juego-personaje"),
            ("imagenes", _("Imágenes"), "panel:game-character-image_by", "juego-personaje")]


class CharacterImageDetailView(BaseCharacterImage, BaseAdminDetailView):
    template_name = "games/detail/character_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-character-image_update"
    delete_url = "panel:game-character-image_delete"
    list_url = "panel:game-character-image_list"
    toggle_url = "panel:game-character-image_toggle"


class CharacterRoleDetailView(BaseCharacterRole, BaseAdminDetailView):
    template_name = "games/detail/character_role.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-character-role_update"
    delete_url = "panel:game-character-role_delete"
    list_url = "panel:game-character-role_list"
    toggle_url = "panel:game-character-role_toggle"


class CreatorDetailView(BaseCreator, BaseAdminDetailView):
    template_name = "games/detail/creator.html"
    update_url = "panel:creator_update"
    delete_url = "panel:creator_delete"
    list_url = "panel:creator_list"
    toggle_url = "panel:creator_toggle"
    by_url = "panel:creator_by"
    tabs = [("juegos", _("Desarrolla"), "panel:game_by", "creador"),
            ("editados", _("Edita"), "panel:game_by", "editora"),
            ("enlaces", _("Enlaces"), "panel:creator-link_by", "creador"),
            ("apodos", _("Apodos"), "panel:creator-nickname_by", "creador")]


class CreatorLinkDetailView(BaseCreatorLink, BaseAdminDetailView):
    template_name = "games/detail/creator_link.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:creator-link_update"
    delete_url = "panel:creator-link_delete"
    list_url = "panel:creator-link_list"
    toggle_url = "panel:creator-link_toggle"


class CreatorNicknameDetailView(BaseCreatorNickname, BaseAdminDetailView):
    template_name = "games/detail/creator_nickname.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:creator-nickname_update"
    delete_url = "panel:creator-nickname_delete"
    list_url = "panel:creator-nickname_list"
    toggle_url = "panel:creator-nickname_toggle"


class DataF95CreatorDetailView(BaseDataF95Creator, BaseAdminDetailView):
    template_name = "games/detail/data_f95_creator.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-f95-creator_update"
    delete_url = "panel:data-f95-creator_delete"
    list_url = "panel:data-f95-creator_list"


class DataF95GameDetailView(BaseDataF95Game, BaseAdminDetailView):
    template_name = "games/detail/data_f95_game.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-f95-game_update"
    delete_url = "panel:data-f95-game_delete"
    list_url = "panel:data-f95-game_list"


class DataVndbCharacterDetailView(BaseDataVndbCharacter, BaseAdminDetailView):
    template_name = "games/detail/data_vndb_character.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-vndb-character_update"
    delete_url = "panel:data-vndb-character_delete"
    list_url = "panel:data-vndb-character_list"
    reprocesar = staticmethod(lambda obj: vndb.process_character(obj.vndb_id, traer_juegos=False))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataVndbCreatorDetailView(BaseDataVndbCreator, BaseAdminDetailView):
    template_name = "games/detail/data_vndb_creator.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-vndb-creator_update"
    delete_url = "panel:data-vndb-creator_delete"
    list_url = "panel:data-vndb-creator_list"
    reprocesar = staticmethod(lambda obj: vndb.process_creator(obj.vndb_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


# ------------------------ datos crudos de importación (VNDB; antes en apps/imports) ------------------------
class DataVndbGameDetailView(BaseDataVndbGame, BaseAdminDetailView):
    template_name = "games/detail/data_vndb_game.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-vndb-game_update"
    delete_url = "panel:data-vndb-game_delete"
    list_url = "panel:data-vndb-game_list"
    reprocesar = staticmethod(lambda obj: vndb.process_game(obj.vndb_id))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DataVndbReleaseDetailView(BaseDataVndbRelease, BaseAdminDetailView):
    template_name = "games/detail/data_vndb_release.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:data-vndb-release_update"
    delete_url = "panel:data-vndb-release_delete"
    list_url = "panel:data-vndb-release_list"
    reprocesar = staticmethod(lambda obj: vndb.process_release(obj.vndb_id, traer_juego=False))   # botón «Reprocesar» de la ficha (sin peticiones nuevas si el crudo está)


class DevelopmentEngineDetailView(BaseDevelopmentEngine, BaseAdminDetailView):
    template_name = "games/detail/development_engine.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-engine_update"
    delete_url = "panel:game-engine_delete"
    list_url = "panel:game-engine_list"
    toggle_url = "panel:game-engine_toggle"


class GameDetailView(BaseGame, BaseAdminDetailView):
    template_name = "games/detail/game.html"
    update_url = "panel:game_update"
    delete_url = "panel:game_delete"
    list_url = "panel:game_list"
    toggle_url = "panel:game_toggle"
    by_url = "panel:game_by"
    tabs = [("personajes", _("Personajes"), "panel:game-character_by", "juego"),
            ("lanzamientos", _("Lanzamientos"), "panel:game-release_by", "juego"),
            ("imagenes", _("Imágenes"), "panel:game-image_by", "juego"),
            ("titulos", _("Títulos"), "panel:game-title_by", "juego"),
            ("enlaces", _("Enlaces"), "panel:game-link_by", "juego")]


class GameImageDetailView(BaseGameImage, BaseAdminDetailView):
    template_name = "games/detail/game_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-image_update"
    delete_url = "panel:game-image_delete"
    list_url = "panel:game-image_list"
    toggle_url = "panel:game-image_toggle"


class GameLinkDetailView(BaseGameLink, BaseAdminDetailView):
    template_name = "games/detail/game_link.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-link_update"
    delete_url = "panel:game-link_delete"
    list_url = "panel:game-link_list"
    toggle_url = "panel:game-link_toggle"


class GameTitleDetailView(BaseGameTitle, BaseAdminDetailView):
    template_name = "games/detail/game_title.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-title_update"
    delete_url = "panel:game-title_delete"
    list_url = "panel:game-title_list"
    toggle_url = "panel:game-title_toggle"


class GenreDetailView(BaseGenre, BaseAdminDetailView):
    template_name = "games/detail/genre.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-genre_update"
    delete_url = "panel:game-genre_delete"
    list_url = "panel:game-genre_list"
    toggle_url = "panel:game-genre_toggle"


class MediumDetailView(BaseMedium, BaseAdminDetailView):
    template_name = "games/detail/medium.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-medium_update"
    delete_url = "panel:game-medium_delete"
    list_url = "panel:game-medium_list"
    toggle_url = "panel:game-medium_toggle"


class PlatformDetailView(BasePlatform, BaseAdminDetailView):
    template_name = "games/detail/platform.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-platform_update"
    delete_url = "panel:game-platform_delete"
    list_url = "panel:game-platform_list"
    toggle_url = "panel:game-platform_toggle"


class ReleaseDetailView(BaseRelease, BaseAdminDetailView):
    template_name = "games/detail/release.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-release_update"
    delete_url = "panel:game-release_delete"
    list_url = "panel:game-release_list"
    toggle_url = "panel:game-release_toggle"


class GameLogDetailView(BaseGameLog, BaseAdminDetailView):
    template_name = "games/detail/game_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:game-log_update"
    delete_url = "panel:game-log_delete"
    list_url = "panel:game-log_list"


# ==============================================================================
# Público
# ==============================================================================


class CharacterPublicDetailView(BaseCharacter, BasePublicDetailView):
    collect_kind = "game-character"
    template_name = "games/detail/character.html"
    list_url = "games:games-catalog"
    section = "juegos"


class CreatorPublicDetailView(BaseCreator, BasePublicDetailView):
    template_name = "games/detail/creator.html"
    list_url = "games:creators-catalog"
    by_url = "games:creators-by"
    section = "juegos"
    tabs = [("juegos", _("Desarrolla"), "games:games-by", "creador"),
            ("editados", _("Edita"), "games:games-by", "editora")]


class GamePublicDetailView(BaseGame, BasePublicDetailView):
    """Ficha pública de un juego: el mismo HTML que en gestión, sin botones y con la colección."""
    template_name = "games/detail/game.html"
    list_url = "games:games-catalog"
    by_url = "games:games-by"
    section = "juegos"
    collect_kind = "game"
    tabs = [("personajes", _("Personajes"), "games:characters-by", "juego"),
            ("lanzamientos", _("Lanzamientos"), "games:releases-by", "juego"),
            ("imagenes", _("Imágenes"), "games:game-images-by", "juego")]


class GenreAliasDetailView(BaseGenreAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:game-genre-alias_list"
    update_url = "panel:game-genre-alias_update"
    delete_url = "panel:game-genre-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Género', 'genre')]


class ReleaseImageDetailView(BaseReleaseImage, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:game-release-image_list"
    update_url = "panel:game-release-image_update"
    delete_url = "panel:game-release-image_delete"
    detail_fields = [('Url de la imagen', 'image_url'), ('Descargada', 'image_downloaded'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Lanzamiento', 'release'), ('Imagen', 'image'), ('Tipo de arte', 'label')]


class TagDetailView(BaseTag, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:tag_list"
    update_url = "panel:tag_update"
    delete_url = "panel:tag_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Descripción', 'description'), ('Imagen', 'image'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at')]


class TagAliasDetailView(BaseTagAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:tag-alias_list"
    update_url = "panel:tag-alias_update"
    delete_url = "panel:tag-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Etiqueta', 'tag')]
