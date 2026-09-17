"""games · listas «por» (ListBy) de los DOS lados, público y gestión: «Películas del género X», «Reparto de X»,
«Personas de Chile». El mapa `filter_config` (tipo → campo, título, fondo) vive en el mixin `_BaseXBy` de base.py y lo comparten
con las Data; aquí cada lista declara sus rutas, su miga y su fondo por defecto. Ruta: `…/por/<tipo>/<pk>/`."""
from apps.games.views.base import BaseCharacterContext, BaseCharacterImageContext, BaseCharacterRoleContext, BaseCreatorContext, BaseCreatorLinkContext, BaseCreatorNicknameContext, BaseGameContext, BaseGameImageContext, BaseGameLinkContext, BaseGameTitleContext, BaseReleaseContext
from core.shared.views.base import AdminListByView, PublicListByView


# ==============================================================================
# Público
# ==============================================================================


class CharacterPublicListByView(BaseCharacterContext, PublicListByView):
    """juego."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "games:characters-by-data"
    by_url = "games:characters-by"
    parent_urls = {"juego": "games:game-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-games-game-character"
    background_fallback = "bg-games-home"
    section = "juegos"
    icon = "bi-person"


class CreatorPublicListByView(BaseCreatorContext, PublicListByView):
    """idioma, tipo."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "games:creators-by-data"
    by_url = "games:creators-by"
    full_list_url = "games:creators-catalog"
    background_image = "bg-games-creator"
    background_fallback = "bg-games-home"
    section = "juegos"
    icon = "bi-person-badge"


class GamePublicListByView(BaseGameContext, PublicListByView):
    """genero, plataforma, idioma, motor, medio, creador, editora, tipo, estado."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "games:games-by-data"
    by_url = "games:games-by"
    full_list_url = "games:games-catalog"
    background_image = "bg-games-game"
    background_fallback = "bg-games-home"
    section = "juegos"
    icon = "bi-controller"


class GameImagePublicListByView(BaseGameImageContext, PublicListByView):
    """juego."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "games:game-images-by-data"
    by_url = "games:game-images-by"
    parent_urls = {"juego": "games:game-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-games-game"
    background_fallback = "bg-games-home"
    section = "juegos"
    icon = "bi-images"


class ReleasePublicListByView(BaseReleaseContext, PublicListByView):
    """juego."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "games:releases-by-data"
    by_url = "games:releases-by"
    parent_urls = {"juego": "games:game-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-games-game-release"
    background_fallback = "bg-games-home"
    section = "juegos"
    icon = "bi-calendar3"


# ==============================================================================
# Gestión
# ==============================================================================


class CharacterListByView(BaseCharacterContext, AdminListByView):
    """juego."""
    home_url = "panel:games-home"
    data_url = "panel:game-character_data-by"
    full_list_url = "panel:game-character_list"
    create_url = "panel:game-character_create"


class CharacterImageListByView(BaseCharacterImageContext, AdminListByView):
    """juego-personaje."""
    home_url = "panel:games-home"
    data_url = "panel:game-character-image_data-by"
    full_list_url = "panel:game-character-image_list"
    create_url = "panel:game-character-image_create"


class CharacterRoleListByView(BaseCharacterRoleContext, AdminListByView):
    """juego-personaje, juego."""
    home_url = "panel:games-home"
    data_url = "panel:game-character-role_data-by"
    full_list_url = "panel:game-character-role_list"
    create_url = "panel:game-character-role_create"


class CreatorListByView(BaseCreatorContext, AdminListByView):
    """idioma, tipo."""
    home_url = "panel:games-home"
    data_url = "panel:creator_data-by"
    full_list_url = "panel:creator_list"
    create_url = "panel:creator_create"


class CreatorLinkListByView(BaseCreatorLinkContext, AdminListByView):
    """creador."""
    home_url = "panel:games-home"
    data_url = "panel:creator-link_data-by"
    full_list_url = "panel:creator-link_list"
    create_url = "panel:creator-link_create"


class CreatorNicknameListByView(BaseCreatorNicknameContext, AdminListByView):
    """creador."""
    home_url = "panel:games-home"
    data_url = "panel:creator-nickname_data-by"
    full_list_url = "panel:creator-nickname_list"
    create_url = "panel:creator-nickname_create"


class GameListByView(BaseGameContext, AdminListByView):
    """genero, plataforma, idioma, motor, medio, creador, editora, tipo, estado."""
    home_url = "panel:games-home"
    data_url = "panel:game_data-by"
    full_list_url = "panel:game_list"
    create_url = "panel:game_create"


class GameImageListByView(BaseGameImageContext, AdminListByView):
    """juego."""
    home_url = "panel:games-home"
    data_url = "panel:game-image_data-by"
    full_list_url = "panel:game-image_list"
    create_url = "panel:game-image_create"


class GameLinkListByView(BaseGameLinkContext, AdminListByView):
    """juego."""
    home_url = "panel:games-home"
    data_url = "panel:game-link_data-by"
    full_list_url = "panel:game-link_list"
    create_url = "panel:game-link_create"


class GameTitleListByView(BaseGameTitleContext, AdminListByView):
    """juego."""
    home_url = "panel:games-home"
    data_url = "panel:game-title_data-by"
    full_list_url = "panel:game-title_list"
    create_url = "panel:game-title_create"


class ReleaseListByView(BaseReleaseContext, AdminListByView):
    """juego."""
    home_url = "panel:games-home"
    data_url = "panel:game-release_data-by"
    full_list_url = "panel:game-release_list"
    create_url = "panel:game-release_create"
