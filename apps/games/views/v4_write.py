"""games · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.games import forms as f
from apps.games.views.base import BaseCharacter, BaseCharacterImage, BaseCharacterRole, BaseCreator, BaseCreatorLink, BaseCreatorNickname, BaseDataF95Creator, BaseDataF95Game, BaseDataVndbCharacter, BaseDataVndbCreator, BaseDataVndbGame, BaseDataVndbRelease, BaseDevelopmentEngine, BaseGame, BaseGameImage, BaseGameLink, BaseGameLog, BaseGameTitle, BaseGenre, BaseGenreAlias, BaseMedium, BasePlatform, BaseRelease, BaseReleaseImage, BaseTag, BaseTagAlias
from core.shared.views.base import BaseCreate, BaseDelete, BaseSoftDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class CharacterCreateView(BaseCharacter, BaseCreate):
    # Django core
    form_class = f.CharacterForm
    list_url = "panel:game-character_list"
    success_url = "panel:game-character_list"
    cancel_url = "panel:game-character_list"
    # UX
    success_message = _("Personaje de juego «%(obj)s» creado.")
    title = _("Crear personaje de juego")


class CharacterUpdateView(BaseCharacter, BaseUpdate):
    # Django core
    form_class = f.CharacterForm
    list_url = "panel:game-character_list"
    success_url = "panel:game-character_list"
    cancel_url = "panel:game-character_list"
    # UX
    success_message = _("Personaje de juego «%(obj)s» actualizado.")
    title = _("Editar personaje de juego")


class CharacterDeleteView(BaseCharacter, BaseDelete):
    list_url = "panel:game-character_list"
    success_url = "panel:game-character_list"
    cancel_url = "panel:game-character_list"
    success_message = _("Personaje de juego «%(obj)s» eliminado.")
    title = _("Eliminar personaje de juego")


class CharacterImageCreateView(BaseCharacterImage, BaseCreate):
    # Django core
    form_class = f.CharacterImageForm
    list_url = "panel:game-character-image_list"
    success_url = "panel:game-character-image_list"
    cancel_url = "panel:game-character-image_list"
    # UX
    success_message = _("Imagen de personaje «%(obj)s» creado.")
    title = _("Crear imagen de personaje")


class CharacterImageUpdateView(BaseCharacterImage, BaseUpdate):
    # Django core
    form_class = f.CharacterImageForm
    list_url = "panel:game-character-image_list"
    success_url = "panel:game-character-image_list"
    cancel_url = "panel:game-character-image_list"
    # UX
    success_message = _("Imagen de personaje «%(obj)s» actualizado.")
    title = _("Editar imagen de personaje")


class CharacterImageDeleteView(BaseCharacterImage, BaseDelete):
    list_url = "panel:game-character-image_list"
    success_url = "panel:game-character-image_list"
    cancel_url = "panel:game-character-image_list"
    success_message = _("Imagen de personaje «%(obj)s» eliminado.")
    title = _("Eliminar imagen de personaje")


class CharacterRoleCreateView(BaseCharacterRole, BaseCreate):
    # Django core
    form_class = f.CharacterRoleForm
    list_url = "panel:game-character-role_list"
    success_url = "panel:game-character-role_list"
    cancel_url = "panel:game-character-role_list"
    # UX
    success_message = _("Rol de personaje «%(obj)s» creado.")
    title = _("Crear rol de personaje")


class CharacterRoleUpdateView(BaseCharacterRole, BaseUpdate):
    # Django core
    form_class = f.CharacterRoleForm
    list_url = "panel:game-character-role_list"
    success_url = "panel:game-character-role_list"
    cancel_url = "panel:game-character-role_list"
    # UX
    success_message = _("Rol de personaje «%(obj)s» actualizado.")
    title = _("Editar rol de personaje")


class CharacterRoleDeleteView(BaseCharacterRole, BaseDelete):
    list_url = "panel:game-character-role_list"
    success_url = "panel:game-character-role_list"
    cancel_url = "panel:game-character-role_list"
    success_message = _("Rol de personaje «%(obj)s» eliminado.")
    title = _("Eliminar rol de personaje")


class CreatorCreateView(BaseCreator, BaseCreate):
    # Django core
    form_class = f.CreatorForm
    form_template = "games/form/creator.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:creator_list"
    success_url = "panel:creator_list"
    cancel_url = "panel:creator_list"
    # UX
    success_message = _("Creador «%(obj)s» creado.")
    title = _("Crear creador")


class CreatorUpdateView(BaseCreator, BaseUpdate):
    # Django core
    form_class = f.CreatorForm
    form_template = "games/form/creator.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:creator_list"
    success_url = "panel:creator_list"
    cancel_url = "panel:creator_list"
    # UX
    success_message = _("Creador «%(obj)s» actualizado.")
    title = _("Editar creador")


class CreatorDeleteView(BaseCreator, BaseDelete):
    list_url = "panel:creator_list"
    success_url = "panel:creator_list"
    cancel_url = "panel:creator_list"
    success_message = _("Creador «%(obj)s» eliminado.")
    title = _("Eliminar creador")


class CreatorLinkCreateView(BaseCreatorLink, BaseCreate):
    # Django core
    form_class = f.CreatorLinkForm
    form_template = "games/form/creator_link.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:creator-link_list"
    success_url = "panel:creator-link_list"
    cancel_url = "panel:creator-link_list"
    # UX
    success_message = _("Enlace «%(obj)s» creado.")
    title = _("Crear enlace")


class CreatorLinkUpdateView(BaseCreatorLink, BaseUpdate):
    # Django core
    form_class = f.CreatorLinkForm
    form_template = "games/form/creator_link.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:creator-link_list"
    success_url = "panel:creator-link_list"
    cancel_url = "panel:creator-link_list"
    # UX
    success_message = _("Enlace «%(obj)s» actualizado.")
    title = _("Editar enlace")


class CreatorLinkDeleteView(BaseCreatorLink, BaseDelete):
    list_url = "panel:creator-link_list"
    success_url = "panel:creator-link_list"
    cancel_url = "panel:creator-link_list"
    success_message = _("Enlace «%(obj)s» eliminado.")
    title = _("Eliminar enlace")


class CreatorNicknameCreateView(BaseCreatorNickname, BaseCreate):
    # Django core
    form_class = f.CreatorNicknameForm
    form_template = "games/form/creator_nickname.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:creator-nickname_list"
    success_url = "panel:creator-nickname_list"
    cancel_url = "panel:creator-nickname_list"
    # UX
    success_message = _("Apodo «%(obj)s» creado.")
    title = _("Crear apodo")


class CreatorNicknameUpdateView(BaseCreatorNickname, BaseUpdate):
    # Django core
    form_class = f.CreatorNicknameForm
    form_template = "games/form/creator_nickname.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:creator-nickname_list"
    success_url = "panel:creator-nickname_list"
    cancel_url = "panel:creator-nickname_list"
    # UX
    success_message = _("Apodo «%(obj)s» actualizado.")
    title = _("Editar apodo")


class CreatorNicknameDeleteView(BaseCreatorNickname, BaseDelete):
    list_url = "panel:creator-nickname_list"
    success_url = "panel:creator-nickname_list"
    cancel_url = "panel:creator-nickname_list"
    success_message = _("Apodo «%(obj)s» eliminado.")
    title = _("Eliminar apodo")


class DataF95CreatorUpdateView(BaseDataF95Creator, BaseUpdate):
    # Django core
    form_class = f.DataF95CreatorForm
    list_url = "panel:data-f95-creator_list"
    success_url = "panel:data-f95-creator_list"
    cancel_url = "panel:data-f95-creator_list"
    # UX
    success_message = _("Datos de creador (F95) «%(obj)s» actualizado.")


class DataF95CreatorDeleteView(BaseDataF95Creator, BaseDelete):
    list_url = "panel:data-f95-creator_list"
    success_url = "panel:data-f95-creator_list"
    cancel_url = "panel:data-f95-creator_list"
    success_message = _("Datos de creador (F95) «%(obj)s» eliminado.")


class DataF95CreatorCreateView(BaseDataF95Creator, BaseCreate):
    form_class = f.DataF95CreatorForm
    list_url = "panel:data-f95-creator_list"
    success_url = "panel:data-f95-creator_list"
    cancel_url = "panel:data-f95-creator_list"
    success_message = _("Datos crudos de juego «%(obj)s» creado.")


class DataF95GameUpdateView(BaseDataF95Game, BaseUpdate):
    # Django core
    form_class = f.DataF95GameForm
    list_url = "panel:data-f95-game_list"
    success_url = "panel:data-f95-game_list"
    cancel_url = "panel:data-f95-game_list"
    # UX
    success_message = _("Datos de juego (F95) «%(obj)s» actualizados.")


class DataF95GameDeleteView(BaseDataF95Game, BaseDelete):
    list_url = "panel:data-f95-game_list"
    success_url = "panel:data-f95-game_list"
    cancel_url = "panel:data-f95-game_list"
    success_message = _("Datos de juego (F95) «%(obj)s» eliminados.")


class DataF95GameCreateView(BaseDataF95Game, BaseCreate):
    form_class = f.DataF95GameForm
    list_url = "panel:data-f95-game_list"
    success_url = "panel:data-f95-game_list"
    cancel_url = "panel:data-f95-game_list"
    success_message = _("Datos de juego (f95) «%(obj)s» creado.")


class DataVndbCharacterUpdateView(BaseDataVndbCharacter, BaseUpdate):
    # Django core
    form_class = f.DataVndbCharacterForm
    list_url = "panel:data-vndb-character_list"
    success_url = "panel:data-vndb-character_list"
    cancel_url = "panel:data-vndb-character_list"
    # UX
    success_message = _("Datos de personaje «%(obj)s» actualizados.")


class DataVndbCharacterDeleteView(BaseDataVndbCharacter, BaseDelete):
    list_url = "panel:data-vndb-character_list"
    success_url = "panel:data-vndb-character_list"
    cancel_url = "panel:data-vndb-character_list"
    success_message = _("Datos de personaje «%(obj)s» eliminados.")


class DataVndbCharacterCreateView(BaseDataVndbCharacter, BaseCreate):
    form_class = f.DataVndbCharacterForm
    list_url = "panel:data-vndb-character_list"
    success_url = "panel:data-vndb-character_list"
    cancel_url = "panel:data-vndb-character_list"
    success_message = _("Datos de personaje (vndb) «%(obj)s» creado.")


class DataVndbCreatorUpdateView(BaseDataVndbCreator, BaseUpdate):
    # Django core
    form_class = f.DataVndbCreatorForm
    list_url = "panel:data-vndb-creator_list"
    success_url = "panel:data-vndb-creator_list"
    cancel_url = "panel:data-vndb-creator_list"
    # UX
    success_message = _("Datos de creador «%(obj)s» actualizados.")


class DataVndbCreatorDeleteView(BaseDataVndbCreator, BaseDelete):
    list_url = "panel:data-vndb-creator_list"
    success_url = "panel:data-vndb-creator_list"
    cancel_url = "panel:data-vndb-creator_list"
    success_message = _("Datos de creador «%(obj)s» eliminados.")


class DataVndbCreatorCreateView(BaseDataVndbCreator, BaseCreate):
    form_class = f.DataVndbCreatorForm
    list_url = "panel:data-vndb-creator_list"
    success_url = "panel:data-vndb-creator_list"
    cancel_url = "panel:data-vndb-creator_list"
    success_message = _("Datos de creador (vndb) «%(obj)s» creado.")


class DataVndbGameUpdateView(BaseDataVndbGame, BaseUpdate):
    # Django core
    form_class = f.DataVndbGameForm
    list_url = "panel:data-vndb-game_list"
    success_url = "panel:data-vndb-game_list"
    cancel_url = "panel:data-vndb-game_list"
    # UX
    success_message = _("Datos de juego «%(obj)s» actualizados.")


class DataVndbGameDeleteView(BaseDataVndbGame, BaseDelete):
    list_url = "panel:data-vndb-game_list"
    success_url = "panel:data-vndb-game_list"
    cancel_url = "panel:data-vndb-game_list"
    success_message = _("Datos de juego «%(obj)s» eliminados.")


class DataVndbGameCreateView(BaseDataVndbGame, BaseCreate):
    form_class = f.DataVndbGameForm
    list_url = "panel:data-vndb-game_list"
    success_url = "panel:data-vndb-game_list"
    cancel_url = "panel:data-vndb-game_list"
    success_message = _("Datos de juego (vndb) «%(obj)s» creado.")


class DataVndbReleaseUpdateView(BaseDataVndbRelease, BaseUpdate):
    # Django core
    form_class = f.DataVndbReleaseForm
    list_url = "panel:data-vndb-release_list"
    success_url = "panel:data-vndb-release_list"
    cancel_url = "panel:data-vndb-release_list"
    # UX
    success_message = _("Datos de lanzamiento «%(obj)s» actualizados.")


class DataVndbReleaseDeleteView(BaseDataVndbRelease, BaseDelete):
    list_url = "panel:data-vndb-release_list"
    success_url = "panel:data-vndb-release_list"
    cancel_url = "panel:data-vndb-release_list"
    success_message = _("Datos de lanzamiento «%(obj)s» eliminados.")


class DataVndbReleaseCreateView(BaseDataVndbRelease, BaseCreate):
    form_class = f.DataVndbReleaseForm
    list_url = "panel:data-vndb-release_list"
    success_url = "panel:data-vndb-release_list"
    cancel_url = "panel:data-vndb-release_list"
    success_message = _("Datos de lanzamiento (vndb) «%(obj)s» creado.")


class DevelopmentEngineCreateView(BaseDevelopmentEngine, BaseCreate):
    # Django core
    form_class = f.DevelopmentEngineForm
    form_template = "games/form/development_engine.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-engine_list"
    success_url = "panel:game-engine_list"
    cancel_url = "panel:game-engine_list"
    # UX
    success_message = _("Motor «%(obj)s» creado.")
    title = _("Crear motor")


class DevelopmentEngineUpdateView(BaseDevelopmentEngine, BaseUpdate):
    # Django core
    form_class = f.DevelopmentEngineForm
    form_template = "games/form/development_engine.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-engine_list"
    success_url = "panel:game-engine_list"
    cancel_url = "panel:game-engine_list"
    # UX
    success_message = _("Motor «%(obj)s» actualizado.")
    title = _("Editar motor")


class DevelopmentEngineDeleteView(BaseDevelopmentEngine, BaseDelete):
    list_url = "panel:game-engine_list"
    success_url = "panel:game-engine_list"
    cancel_url = "panel:game-engine_list"
    success_message = _("Motor «%(obj)s» eliminado.")
    title = _("Eliminar motor")


class GameCreateView(BaseGame, BaseCreate):
    # Django core
    form_class = f.GameForm
    form_template = "games/form/game.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game_list"
    success_url = "panel:game_list"
    cancel_url = "panel:game_list"
    # UX
    success_message = _("Juego «%(obj)s» creado.")
    title = _("Crear juego")


class GameUpdateView(BaseGame, BaseUpdate):
    # Django core
    form_class = f.GameForm
    form_template = "games/form/game.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game_list"
    success_url = "panel:game_list"
    cancel_url = "panel:game_list"
    # UX
    success_message = _("Juego «%(obj)s» actualizado.")
    title = _("Editar juego")


class GameDeleteView(BaseGame, BaseDelete):
    list_url = "panel:game_list"
    success_url = "panel:game_list"
    cancel_url = "panel:game_list"
    success_message = _("Juego «%(obj)s» eliminado.")
    title = _("Eliminar juego")


class GameImageCreateView(BaseGameImage, BaseCreate):
    # Django core
    form_class = f.GameImageForm
    form_template = "games/form/game_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-image_list"
    success_url = "panel:game-image_list"
    cancel_url = "panel:game-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class GameImageUpdateView(BaseGameImage, BaseUpdate):
    # Django core
    form_class = f.GameImageForm
    form_template = "games/form/game_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-image_list"
    success_url = "panel:game-image_list"
    cancel_url = "panel:game-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class GameImageDeleteView(BaseGameImage, BaseDelete):
    list_url = "panel:game-image_list"
    success_url = "panel:game-image_list"
    cancel_url = "panel:game-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class GameLinkCreateView(BaseGameLink, BaseCreate):
    # Django core
    form_class = f.GameLinkForm
    form_template = "games/form/game_link.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-link_list"
    success_url = "panel:game-link_list"
    cancel_url = "panel:game-link_list"
    # UX
    success_message = _("Enlace «%(obj)s» creado.")
    title = _("Crear enlace")


class GameLinkUpdateView(BaseGameLink, BaseUpdate):
    # Django core
    form_class = f.GameLinkForm
    form_template = "games/form/game_link.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-link_list"
    success_url = "panel:game-link_list"
    cancel_url = "panel:game-link_list"
    # UX
    success_message = _("Enlace «%(obj)s» actualizado.")
    title = _("Editar enlace")


class GameLinkDeleteView(BaseGameLink, BaseDelete):
    list_url = "panel:game-link_list"
    success_url = "panel:game-link_list"
    cancel_url = "panel:game-link_list"
    success_message = _("Enlace «%(obj)s» eliminado.")
    title = _("Eliminar enlace")


class GameTitleCreateView(BaseGameTitle, BaseCreate):
    # Django core
    form_class = f.GameTitleForm
    form_template = "games/form/game_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-title_list"
    success_url = "panel:game-title_list"
    cancel_url = "panel:game-title_list"
    # UX
    success_message = _("Título «%(obj)s» creado.")
    title = _("Crear título")


class GameTitleUpdateView(BaseGameTitle, BaseUpdate):
    # Django core
    form_class = f.GameTitleForm
    form_template = "games/form/game_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-title_list"
    success_url = "panel:game-title_list"
    cancel_url = "panel:game-title_list"
    # UX
    success_message = _("Título «%(obj)s» actualizado.")
    title = _("Editar título")


class GameTitleDeleteView(BaseGameTitle, BaseDelete):
    list_url = "panel:game-title_list"
    success_url = "panel:game-title_list"
    cancel_url = "panel:game-title_list"
    success_message = _("Título «%(obj)s» eliminado.")
    title = _("Eliminar título")


class GenreCreateView(BaseGenre, BaseCreate):
    # Django core
    form_class = f.GenreForm
    form_template = "games/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-genre_list"
    success_url = "panel:game-genre_list"
    cancel_url = "panel:game-genre_list"
    # UX
    success_message = _("Género «%(obj)s» creado.")
    title = _("Crear género")


class GenreUpdateView(BaseGenre, BaseUpdate):
    # Django core
    form_class = f.GenreForm
    form_template = "games/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-genre_list"
    success_url = "panel:game-genre_list"
    cancel_url = "panel:game-genre_list"
    # UX
    success_message = _("Género «%(obj)s» actualizado.")
    title = _("Editar género")


class GenreDeleteView(BaseGenre, BaseDelete):
    list_url = "panel:game-genre_list"
    success_url = "panel:game-genre_list"
    cancel_url = "panel:game-genre_list"
    success_message = _("Género «%(obj)s» eliminado.")
    title = _("Eliminar género")


class GenreAliasCreateView(BaseGenreAlias, BaseCreate):
    form_class = f.GenreAliasForm
    list_url = "panel:game-genre-alias_list"
    success_url = "panel:game-genre-alias_list"
    cancel_url = "panel:game-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» creado.")
    title = _("Crear alias de género")


class GenreAliasUpdateView(BaseGenreAlias, BaseUpdate):
    form_class = f.GenreAliasForm
    list_url = "panel:game-genre-alias_list"
    success_url = "panel:game-genre-alias_list"
    cancel_url = "panel:game-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» actualizado.")
    title = _("Editar alias de género")


class GenreAliasDeleteView(BaseGenreAlias, BaseDelete):
    list_url = "panel:game-genre-alias_list"
    success_url = "panel:game-genre-alias_list"
    cancel_url = "panel:game-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» eliminado.")
    title = _("Eliminar alias de género")


class MediumCreateView(BaseMedium, BaseCreate):
    # Django core
    form_class = f.MediumForm
    form_template = "games/form/medium.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-medium_list"
    success_url = "panel:game-medium_list"
    cancel_url = "panel:game-medium_list"
    # UX
    success_message = _("Medio «%(obj)s» creado.")
    title = _("Crear medio")


class MediumUpdateView(BaseMedium, BaseUpdate):
    # Django core
    form_class = f.MediumForm
    form_template = "games/form/medium.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-medium_list"
    success_url = "panel:game-medium_list"
    cancel_url = "panel:game-medium_list"
    # UX
    success_message = _("Medio «%(obj)s» actualizado.")
    title = _("Editar medio")


class MediumDeleteView(BaseMedium, BaseDelete):
    list_url = "panel:game-medium_list"
    success_url = "panel:game-medium_list"
    cancel_url = "panel:game-medium_list"
    success_message = _("Medio «%(obj)s» eliminado.")
    title = _("Eliminar medio")


class PlatformCreateView(BasePlatform, BaseCreate):
    # Django core
    form_class = f.PlatformForm
    form_template = "games/form/platform.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-platform_list"
    success_url = "panel:game-platform_list"
    cancel_url = "panel:game-platform_list"
    # UX
    success_message = _("Plataforma «%(obj)s» creada.")
    title = _("Crear plataforma")


class PlatformUpdateView(BasePlatform, BaseUpdate):
    # Django core
    form_class = f.PlatformForm
    form_template = "games/form/platform.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:game-platform_list"
    success_url = "panel:game-platform_list"
    cancel_url = "panel:game-platform_list"
    # UX
    success_message = _("Plataforma «%(obj)s» actualizada.")
    title = _("Editar plataforma")


class PlatformDeleteView(BasePlatform, BaseDelete):
    list_url = "panel:game-platform_list"
    success_url = "panel:game-platform_list"
    cancel_url = "panel:game-platform_list"
    success_message = _("Plataforma «%(obj)s» eliminada.")
    title = _("Eliminar plataforma")


class ReleaseCreateView(BaseRelease, BaseCreate):
    # Django core
    form_class = f.ReleaseForm
    list_url = "panel:game-release_list"
    success_url = "panel:game-release_list"
    cancel_url = "panel:game-release_list"
    # UX
    success_message = _("Lanzamiento «%(obj)s» creado.")
    title = _("Crear lanzamiento de juego")


class ReleaseUpdateView(BaseRelease, BaseUpdate):
    # Django core
    form_class = f.ReleaseForm
    list_url = "panel:game-release_list"
    success_url = "panel:game-release_list"
    cancel_url = "panel:game-release_list"
    # UX
    success_message = _("Lanzamiento «%(obj)s» actualizado.")
    title = _("Editar lanzamiento de juego")


class ReleaseDeleteView(BaseRelease, BaseDelete):
    list_url = "panel:game-release_list"
    success_url = "panel:game-release_list"
    cancel_url = "panel:game-release_list"
    success_message = _("Lanzamiento «%(obj)s» eliminado.")
    title = _("Eliminar lanzamiento de juego")


class ReleaseImageCreateView(BaseReleaseImage, BaseCreate):
    form_class = f.ReleaseImageForm
    list_url = "panel:game-release-image_list"
    success_url = "panel:game-release-image_list"
    cancel_url = "panel:game-release-image_list"
    success_message = _("Imagen de lanzamiento «%(obj)s» creado.")
    title = _("Crear imagen de lanzamiento")


class ReleaseImageUpdateView(BaseReleaseImage, BaseUpdate):
    form_class = f.ReleaseImageForm
    list_url = "panel:game-release-image_list"
    success_url = "panel:game-release-image_list"
    cancel_url = "panel:game-release-image_list"
    success_message = _("Imagen de lanzamiento «%(obj)s» actualizado.")
    title = _("Editar imagen de lanzamiento")


class ReleaseImageDeleteView(BaseReleaseImage, BaseDelete):
    list_url = "panel:game-release-image_list"
    success_url = "panel:game-release-image_list"
    cancel_url = "panel:game-release-image_list"
    success_message = _("Imagen de lanzamiento «%(obj)s» eliminado.")
    title = _("Eliminar imagen de lanzamiento")


class TagCreateView(BaseTag, BaseCreate):
    form_class = f.TagForm
    list_url = "panel:tag_list"
    success_url = "panel:tag_list"
    cancel_url = "panel:tag_list"
    success_message = _("Etiqueta «%(obj)s» creado.")
    title = _("Crear etiqueta")


class TagUpdateView(BaseTag, BaseUpdate):
    form_class = f.TagForm
    list_url = "panel:tag_list"
    success_url = "panel:tag_list"
    cancel_url = "panel:tag_list"
    success_message = _("Etiqueta «%(obj)s» actualizado.")
    title = _("Editar etiqueta")


class TagDeleteView(BaseTag, BaseDelete):
    list_url = "panel:tag_list"
    success_url = "panel:tag_list"
    cancel_url = "panel:tag_list"
    success_message = _("Etiqueta «%(obj)s» eliminado.")
    title = _("Eliminar etiqueta")


class TagAliasCreateView(BaseTagAlias, BaseCreate):
    form_class = f.TagAliasForm
    list_url = "panel:tag-alias_list"
    success_url = "panel:tag-alias_list"
    cancel_url = "panel:tag-alias_list"
    success_message = _("Alias de etiqueta «%(obj)s» creado.")
    title = _("Crear alias de etiqueta")


class TagAliasUpdateView(BaseTagAlias, BaseUpdate):
    form_class = f.TagAliasForm
    list_url = "panel:tag-alias_list"
    success_url = "panel:tag-alias_list"
    cancel_url = "panel:tag-alias_list"
    success_message = _("Alias de etiqueta «%(obj)s» actualizado.")
    title = _("Editar alias de etiqueta")


class TagAliasDeleteView(BaseTagAlias, BaseDelete):
    list_url = "panel:tag-alias_list"
    success_url = "panel:tag-alias_list"
    cancel_url = "panel:tag-alias_list"
    success_message = _("Alias de etiqueta «%(obj)s» eliminado.")
    title = _("Eliminar alias de etiqueta")


class GameLogCreateView(BaseGameLog, BaseCreate):
    form_class = f.GameLogForm
    form_template = "games/form/game_log.html"
    list_url = "panel:game-log_list"
    success_url = "panel:game-log_list"
    cancel_url = "panel:game-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class GameLogUpdateView(BaseGameLog, BaseUpdate):
    form_class = f.GameLogForm
    form_template = "games/form/game_log.html"
    list_url = "panel:game-log_list"
    success_url = "panel:game-log_list"
    cancel_url = "panel:game-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class GameLogDeleteView(BaseGameLog, BaseDelete):
    list_url = "panel:game-log_list"
    success_url = "panel:game-log_list"
    cancel_url = "panel:game-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
