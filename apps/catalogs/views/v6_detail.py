from apps.catalogs.views.base import BaseCatalogsLog, BaseCountry, BaseExternalSource, BaseFormat, BaseLanguage, BaseQuality, BaseRelationType, BaseWebsite
from core.shared.views.base import BaseAdminDetailView


# Gestión
# ==============================================================================


class CountryDetailView(BaseCountry, BaseAdminDetailView):
    template_name = "catalogs/detail/country.html"
    update_url = "panel:country_update"
    delete_url = "panel:country_delete"
    list_url = "panel:country_list"
    toggle_url = "panel:country_toggle"


class ExternalSourceDetailView(BaseExternalSource, BaseAdminDetailView):
    template_name = "catalogs/detail/external_source.html"
    update_url = "panel:external-source_update"
    delete_url = "panel:external-source_delete"
    list_url = "panel:external-source_list"
    toggle_url = "panel:external-source_toggle"


class FormatDetailView(BaseFormat, BaseAdminDetailView):
    template_name = "catalogs/detail/format.html"
    update_url = "panel:format_update"
    delete_url = "panel:format_delete"
    list_url = "panel:format_list"
    toggle_url = "panel:format_toggle"


class LanguageDetailView(BaseLanguage, BaseAdminDetailView):
    template_name = "catalogs/detail/language.html"
    update_url = "panel:language_update"
    delete_url = "panel:language_delete"
    list_url = "panel:language_list"
    toggle_url = "panel:language_toggle"


class QualityDetailView(BaseQuality, BaseAdminDetailView):
    template_name = "catalogs/detail/quality.html"
    update_url = "panel:quality_update"
    delete_url = "panel:quality_delete"
    list_url = "panel:quality_list"
    toggle_url = "panel:quality_toggle"


class RelationTypeDetailView(BaseRelationType, BaseAdminDetailView):
    template_name = "catalogs/detail/relation_type.html"
    update_url = "panel:relation-type_update"
    delete_url = "panel:relation-type_delete"
    list_url = "panel:relation-type_list"
    toggle_url = "panel:relation-type_toggle"


class WebsiteDetailView(BaseWebsite, BaseAdminDetailView):
    template_name = "catalogs/detail/website.html"
    update_url = "panel:website_update"
    delete_url = "panel:website_delete"
    list_url = "panel:website_list"
    toggle_url = "panel:website_toggle"


class CatalogsLogDetailView(BaseCatalogsLog, BaseAdminDetailView):
    template_name = "catalogs/detail/catalogs_log.html"
    update_url = "panel:catalogs-log_update"
    delete_url = "panel:catalogs-log_delete"
    list_url = "panel:catalogs-log_list"
