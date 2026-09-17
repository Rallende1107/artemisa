"""series · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.series.views.base import BaseCompany, BaseGenre, BaseGenreAlias, BaseGenreAliasContext, BaseRating, BaseRole, BaseRoleContext, BaseSerie, BaseSerieCast, BaseSerieImage, BaseSerieLog, BaseSerieRelation, BaseSerieStaff, BaseSerieTitle, BaseType
from core.shared.views.base import AdminListByView, AdminListView, PublicListView


# ==============================================================================
# Gestión
# ==============================================================================


class GenreListView(BaseGenre, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-genre_data"
    create_url = "panel:serie-genre_create"
    title = _("Lista de géneros")


class RatingListView(BaseRating, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-rating_data"
    create_url = "panel:serie-rating_create"
    title = _("Lista de clasificaciones")


class RoleListView(BaseRole, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-role_data"
    create_url = "panel:serie-role_create"
    title = _("Lista de roles")


class SerieListView(BaseSerie, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie_data"
    create_url = "panel:serie_create"
    title = _("Lista de series")


class SerieCastListView(BaseSerieCast, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-cast_data"
    create_url = "panel:serie-cast_create"
    title = _("Lista de reparto")


class SerieImageListView(BaseSerieImage, AdminListView):
    home_url = "panel:series-home"
    buttons = (("panel:serie-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:serie-image_data"
    create_url = "panel:serie-image_create"
    title = _("Lista de imágenes extra")


class SerieRelationListView(BaseSerieRelation, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-relation_data"
    create_url = "panel:serie-relation_create"
    title = _("Lista de relaciones")


class SerieStaffListView(BaseSerieStaff, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-staff_data"
    create_url = "panel:serie-staff_create"
    title = _("Lista de equipo")


class SerieTitleListView(BaseSerieTitle, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-title_data"
    create_url = "panel:serie-title_create"
    title = _("Lista de títulos alternativos")


class TypeListView(BaseType, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-type_data"
    create_url = "panel:serie-type_create"
    title = _("Lista de tipos")


class SerieLogListView(BaseSerieLog, AdminListView):
    home_url = "panel:series-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:serie-log_data"
    create_url = "panel:serie-log_create"
    title = _("Lista de log de series")


# ==============================================================================
# Público
# ==============================================================================

# ==============================================================================
# Catálogos sobre la base NUEVA (PublicListView + PublicDataView por data_url)
# ==============================================================================


class ProducerPublicListView(BaseCompany, PublicListView):
    """Catálogo de PRODUCTORAS de series (con buscador y filtros)."""
    data_url = "series:producers-catalog-data"
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    section = "series"
    title = _("Productoras")
    icon = "bi-building"
    subtitle = _("Compañías productoras y distribuidoras de televisión.")
    home_url = "series:home"
    home_label = _("series")


class DistributorPublicListView(BaseCompany, PublicListView):
    """Catálogo de DISTRIBUIDORAS de series (con buscador y filtros)."""
    data_url = "series:distributors-catalog-data"
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    section = "series"
    title = _("Distribuidoras")
    icon = "bi-building"
    subtitle = _("Compañías que distribuyen series.")
    home_url = "series:home"
    home_label = _("series")


class GenreAliasListView(BaseGenreAlias, AdminListView):
    home_url = "panel:series-home"
    data_url = "panel:serie-genre-alias_data"
    create_url = "panel:serie-genre-alias_create"
    title = _("Lista de alias de géneros")


class GenreAliasListByView(BaseGenreAliasContext, AdminListByView):
    """Alias acotados por su padre (`/serie-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`."""
    home_url = "panel:series-home"
    create_url = "panel:serie-genre-alias_create"
    data_url = "panel:serie-genre-alias_data-by"
    full_list_url = "panel:serie-genre-alias_list"
    by_url = "panel:serie-genre-alias_by"


class RoleListByView(BaseRoleContext, AdminListByView):
    """Lista de roles acotada por familia (`/serie-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`."""
    home_url = "panel:series-home"
    create_url = "panel:serie-role_create"
    data_url = "panel:serie-role_data-by"
    full_list_url = "panel:serie-role_list"
    by_url = "panel:serie-role_by"


class SeriePublicListView(BaseSerie, PublicListView):
    data_url = "series:series-catalog-data"
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    section = "series"
    title = _("Series")
    icon = "bi-collection-play"
    home_url = "series:home"
    home_label = _("series")
