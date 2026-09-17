from django.utils.translation import gettext_lazy as _

from apps.catalogs.views.base import BaseCatalogsLog, BaseCountry, BaseExternalSource, BaseExternalSourceContext, BaseFormat, BaseLanguage, BaseQuality, BaseRelationType, BaseWebsite, BaseWebsiteContext
from core.shared.views.base import AdminListByView, AdminListView


# Gestión
# ==============================================================================


class CountryListView(BaseCountry, AdminListView):
    home_url = "panel:catalogs-home"
    data_url = "panel:country_data"
    create_url = "panel:country_create"
    title = _("Lista de países")


class ExternalSourceListView(BaseExternalSource, AdminListView):
    home_url = "panel:catalogs-home"
    data_url = "panel:external-source_data"
    create_url = "panel:external-source_create"
    title = _("Lista de fuentes externas")


class FormatListView(BaseFormat, AdminListView):
    home_url = "panel:catalogs-home"
    data_url = "panel:format_data"
    create_url = "panel:format_create"
    title = _("Lista de formatos")


class LanguageListView(BaseLanguage, AdminListView):
    home_url = "panel:catalogs-home"
    data_url = "panel:language_data"
    create_url = "panel:language_create"
    title = _("Lista de idiomas")


class QualityListView(BaseQuality, AdminListView):
    home_url = "panel:catalogs-home"
    data_url = "panel:quality_data"
    create_url = "panel:quality_create"
    title = _("Lista de calidades")


class RelationTypeListView(BaseRelationType, AdminListView):
    home_url = "panel:catalogs-home"
    data_url = "panel:relation-type_data"
    create_url = "panel:relation-type_create"
    title = _("Lista de tipos de relación")


class WebsiteListView(BaseWebsite, AdminListView):
    home_url = "panel:catalogs-home"
    data_url = "panel:website_data"
    create_url = "panel:website_create"
    title = _("Lista de sitios web")


class CatalogsLogListView(BaseCatalogsLog, AdminListView):
    home_url = "panel:catalogs-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:catalogs-log_data"
    create_url = "panel:catalogs-log_create"
    title = _("Lista de log de catálogos")


# List By
# ==============================================================================


class ExternalSourceListByView(BaseExternalSourceContext, AdminListByView):
    """Lista acotada por el mapa (`/external-source/<tipo>/<valor>/`): la alimenta ExternalSourceDataView con `/data/<tipo>/<valor>/`."""
    home_url = "panel:catalogs-home"
    create_url = "panel:external-source_create"

    data_url = "panel:external-source_data-by"
    full_list_url = "panel:external-source_list"
    by_url = "panel:external-source_by"


class WebsiteListByView(BaseWebsiteContext, AdminListByView):
    """Lista acotada por el mapa (`/website/<tipo>/<valor>/`): la alimenta WebsiteDataView con `/data/<tipo>/<valor>/`."""
    home_url = "panel:catalogs-home"
    create_url = "panel:website_create"

    data_url = "panel:website_data-by"
    full_list_url = "panel:website_list"
    by_url = "panel:website_by"
