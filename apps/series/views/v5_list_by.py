"""series · listas «por» (ListBy) de los DOS lados, público y gestión: «Películas del género X», «Reparto de X»,
«Personas de Chile». El mapa `filter_config` (tipo → campo, título, fondo) vive en el mixin `_BaseXBy` de base.py y lo comparten
con las Data; aquí cada lista declara sus rutas, su miga y su fondo por defecto. Ruta: `…/por/<tipo>/<pk>/`."""
from apps.series.views.base import BaseSerieCastContext, BaseSerieContext, BaseSerieImageContext, BaseSerieRelationContext, BaseSerieStaffContext, BaseSerieTitleContext
from core.shared.views.base import AdminListByView, PublicListByView


# ==============================================================================
# Público
# ==============================================================================


class SeriePublicListByView(BaseSerieContext, PublicListByView):
    """genero, productora, distribuidora, tipo, clasificacion, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "series:series-by-data"
    by_url = "series:series-by"
    full_list_url = "series:series-catalog"
    parent_urls = {"persona": "personas:person-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    section = "series"
    icon = "bi-collection-play"


class SerieCastPublicListByView(BaseSerieCastContext, PublicListByView):
    """serie, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "series:cast-by-data"
    by_url = "series:cast-by"
    parent_urls = {"serie": "series:serie-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    section = "series"
    icon = "bi-people"
    cards_default = False   # en tabla se lee mejor (persona · personaje · rol)


class SerieImagePublicListByView(BaseSerieImageContext, PublicListByView):
    """serie."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "series:serie-images-by-data"
    by_url = "series:serie-images-by"
    parent_urls = {"serie": "series:serie-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    section = "series"
    icon = "bi-images"


class SerieStaffPublicListByView(BaseSerieStaffContext, PublicListByView):
    """serie, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "series:crew-by-data"
    by_url = "series:crew-by"
    parent_urls = {"serie": "series:serie-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    section = "series"
    icon = "bi-person-gear"
    cards_default = False   # en tabla se lee mejor (persona · personaje · rol)


# ==============================================================================
# Gestión
# ==============================================================================


class SerieListByView(BaseSerieContext, AdminListByView):
    """genero, productora, distribuidora, tipo, clasificacion, persona."""
    home_url = "panel:series-home"
    data_url = "panel:serie_data-by"
    full_list_url = "panel:serie_list"
    create_url = "panel:serie_create"


class SerieCastListByView(BaseSerieCastContext, AdminListByView):
    """serie, persona."""
    home_url = "panel:series-home"
    data_url = "panel:serie-cast_data-by"
    full_list_url = "panel:serie-cast_list"
    create_url = "panel:serie-cast_create"


class SerieImageListByView(BaseSerieImageContext, AdminListByView):
    """serie."""
    home_url = "panel:series-home"
    data_url = "panel:serie-image_data-by"
    full_list_url = "panel:serie-image_list"
    create_url = "panel:serie-image_create"


class SerieRelationListByView(BaseSerieRelationContext, AdminListByView):
    """serie, tipo."""
    home_url = "panel:series-home"
    data_url = "panel:serie-relation_data-by"
    full_list_url = "panel:serie-relation_list"
    create_url = "panel:serie-relation_create"


class SerieStaffListByView(BaseSerieStaffContext, AdminListByView):
    """serie, persona."""
    home_url = "panel:series-home"
    data_url = "panel:serie-staff_data-by"
    full_list_url = "panel:serie-staff_list"
    create_url = "panel:serie-staff_create"


class SerieTitleListByView(BaseSerieTitleContext, AdminListByView):
    """serie."""
    home_url = "panel:series-home"
    data_url = "panel:serie-title_data-by"
    full_list_url = "panel:serie-title_list"
    create_url = "panel:serie-title_create"
