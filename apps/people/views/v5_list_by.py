"""people · listas «por» (ListBy) de los DOS lados, público y gestión: «Películas del género X», «Reparto de X»,
«Personas de Chile». El mapa `filter_config` (tipo → campo, título, fondo) vive en el mixin `_BaseXBy` de base.py y lo comparten
con las Data; aquí cada lista declara sus rutas, su miga y su fondo por defecto. Ruta: `…/por/<tipo>/<pk>/`."""
from apps.people.views.base import BasePersonContext, BasePersonImageContext, BasePersonLinkContext, BasePersonNicknameContext
from core.shared.views.base import AdminListByView, PublicListByView


# ==============================================================================
# Público
# ==============================================================================


class PersonPublicListByView(BasePersonContext, PublicListByView):
    """voces-anime, equipo-anime, autores-manga, voces-personaje, pais, integrantes-artista."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "personas:people-by-data"
    by_url = "personas:people-by"
    full_list_url = "personas:people-catalog"
    parent_urls = {"voces-anime": "otaku:anime-detail", "equipo-anime": "otaku:anime-detail", "autores-manga": "otaku:manga-detail", "voces-personaje": "otaku:character-detail", "integrantes-artista": "music:artist-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-people-person"
    background_fallback = "bg-catalogs-home"
    section = "personas"
    icon = "bi-people"


class PersonImagePublicListByView(BasePersonImageContext, PublicListByView):
    """persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "personas:person-images-by-data"
    by_url = "personas:person-images-by"
    parent_urls = {"persona": "personas:person-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-people-person"
    background_fallback = "bg-catalogs-home"
    section = "personas"
    icon = "bi-images"


# ==============================================================================
# Gestión
# ==============================================================================


class PersonListByView(BasePersonContext, AdminListByView):
    """voces-anime, equipo-anime, autores-manga, voces-personaje, pais, integrantes-artista."""
    home_url = "panel:people-home"
    data_url = "panel:person_data-by"
    full_list_url = "panel:person_list"
    create_url = "panel:person_create"


class PersonImageListByView(BasePersonImageContext, AdminListByView):
    """persona."""
    home_url = "panel:people-home"
    data_url = "panel:person-image_data-by"
    full_list_url = "panel:person-image_list"
    create_url = "panel:person-image_create"


class PersonLinkListByView(BasePersonLinkContext, AdminListByView):
    """persona."""
    home_url = "panel:people-home"
    data_url = "panel:person-link_data-by"
    full_list_url = "panel:person-link_list"
    create_url = "panel:person-link_create"


class PersonNicknameListByView(BasePersonNicknameContext, AdminListByView):
    """persona."""
    home_url = "panel:people-home"
    data_url = "panel:person-nickname_data-by"
    full_list_url = "panel:person-nickname_list"
    create_url = "panel:person-nickname_create"
