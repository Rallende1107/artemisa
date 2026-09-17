"""catalogs · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.catalogs import forms as f
from apps.catalogs.views.base import BaseCatalogsLog, BaseCountry, BaseExternalSource, BaseFormat, BaseLanguage, BaseQuality, BaseRelationType, BaseWebsite
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# Gestión
# ==============================================================================


class CountryCreateView(BaseCountry, BaseCreate):
    form_class = f.CountryForm
    form_template = "catalogs/form/country.html"
    list_url = "panel:country_list"
    success_url = "panel:country_list"
    cancel_url = "panel:country_list"
    success_message = _("País «%(obj)s» creado.")
    title = _("Crear país")


class CountryUpdateView(BaseCountry, BaseUpdate):
    form_class = f.CountryForm
    form_template = "catalogs/form/country.html"
    list_url = "panel:country_list"
    success_url = "panel:country_list"
    cancel_url = "panel:country_list"
    success_message = _("País «%(obj)s» actualizado.")
    title = _("Editar país")


class CountryDeleteView(BaseCountry, BaseDelete):
    list_url = "panel:country_list"
    success_url = "panel:country_list"
    cancel_url = "panel:country_list"
    success_message = _("País «%(obj)s» eliminado.")
    title = _("Eliminar país")


class ExternalSourceCreateView(BaseExternalSource, BaseCreate):
    form_class = f.ExternalSourceForm
    form_template = "catalogs/form/external_source.html"
    list_url = "panel:external-source_list"
    success_url = "panel:external-source_list"
    cancel_url = "panel:external-source_list"
    success_message = _("Fuente externa «%(obj)s» creada.")
    title = _("Crear fuente externa")


class ExternalSourceUpdateView(BaseExternalSource, BaseUpdate):
    form_class = f.ExternalSourceForm
    form_template = "catalogs/form/external_source.html"
    list_url = "panel:external-source_list"
    success_url = "panel:external-source_list"
    cancel_url = "panel:external-source_list"
    success_message = _("Fuente externa «%(obj)s» actualizada.")
    title = _("Editar fuente externa")


class ExternalSourceDeleteView(BaseExternalSource, BaseDelete):
    list_url = "panel:external-source_list"
    success_url = "panel:external-source_list"
    cancel_url = "panel:external-source_list"
    success_message = _("Fuente externa «%(obj)s» eliminada.")
    title = _("Eliminar fuente externa")


class FormatCreateView(BaseFormat, BaseCreate):
    form_class = f.FormatForm
    form_template = "catalogs/form/format.html"
    list_url = "panel:format_list"
    success_url = "panel:format_list"
    cancel_url = "panel:format_list"
    success_message = _("Formato «%(obj)s» creado.")
    title = _("Crear formato")


class FormatUpdateView(BaseFormat, BaseUpdate):
    form_class = f.FormatForm
    form_template = "catalogs/form/format.html"
    list_url = "panel:format_list"
    success_url = "panel:format_list"
    cancel_url = "panel:format_list"
    success_message = _("Formato «%(obj)s» actualizado.")
    title = _("Editar formato")


class FormatDeleteView(BaseFormat, BaseDelete):
    list_url = "panel:format_list"
    success_url = "panel:format_list"
    cancel_url = "panel:format_list"
    success_message = _("Formato «%(obj)s» eliminado.")
    title = _("Eliminar formato")


class LanguageCreateView(BaseLanguage, BaseCreate):
    form_class = f.LanguageForm
    form_template = "catalogs/form/language.html"
    list_url = "panel:language_list"
    success_url = "panel:language_list"
    cancel_url = "panel:language_list"
    success_message = _("Idioma «%(obj)s» creado.")
    title = _("Crear idioma")


class LanguageUpdateView(BaseLanguage, BaseUpdate):
    form_class = f.LanguageForm
    form_template = "catalogs/form/language.html"
    list_url = "panel:language_list"
    success_url = "panel:language_list"
    cancel_url = "panel:language_list"
    success_message = _("Idioma «%(obj)s» actualizado.")
    title = _("Editar idioma")


class LanguageDeleteView(BaseLanguage, BaseDelete):
    list_url = "panel:language_list"
    success_url = "panel:language_list"
    cancel_url = "panel:language_list"
    success_message = _("Idioma «%(obj)s» eliminado.")
    title = _("Eliminar idioma")


class QualityCreateView(BaseQuality, BaseCreate):
    form_class = f.QualityForm
    form_template = "catalogs/form/quality.html"
    list_url = "panel:quality_list"
    success_url = "panel:quality_list"
    cancel_url = "panel:quality_list"
    success_message = _("Calidad «%(obj)s» creada.")
    title = _("Crear calidad")


class QualityUpdateView(BaseQuality, BaseUpdate):
    form_class = f.QualityForm
    form_template = "catalogs/form/quality.html"
    list_url = "panel:quality_list"
    success_url = "panel:quality_list"
    cancel_url = "panel:quality_list"
    success_message = _("Calidad «%(obj)s» actualizada.")
    title = _("Editar calidad")


class QualityDeleteView(BaseQuality, BaseDelete):
    list_url = "panel:quality_list"
    success_url = "panel:quality_list"
    cancel_url = "panel:quality_list"
    success_message = _("Calidad «%(obj)s» eliminada.")
    title = _("Eliminar calidad")


class RelationTypeCreateView(BaseRelationType, BaseCreate):
    form_class = f.RelationTypeForm
    form_template = "catalogs/form/relation_type.html"
    list_url = "panel:relation-type_list"
    success_url = "panel:relation-type_list"
    cancel_url = "panel:relation-type_list"
    success_message = _("Tipo de relación «%(obj)s» creado.")
    title = _("Crear tipo de relación")


class RelationTypeUpdateView(BaseRelationType, BaseUpdate):
    form_class = f.RelationTypeForm
    form_template = "catalogs/form/relation_type.html"
    list_url = "panel:relation-type_list"
    success_url = "panel:relation-type_list"
    cancel_url = "panel:relation-type_list"
    success_message = _("Tipo de relación «%(obj)s» actualizado.")
    title = _("Editar tipo de relación")


class RelationTypeDeleteView(BaseRelationType, BaseDelete):
    list_url = "panel:relation-type_list"
    success_url = "panel:relation-type_list"
    cancel_url = "panel:relation-type_list"
    success_message = _("Tipo de relación «%(obj)s» eliminado.")
    title = _("Eliminar tipo de relación")


class WebsiteCreateView(BaseWebsite, BaseCreate):
    form_class = f.WebsiteForm
    form_template = "catalogs/form/website.html"
    list_url = "panel:website_list"
    success_url = "panel:website_list"
    cancel_url = "panel:website_list"
    success_message = _("Sitio web «%(obj)s» creado.")
    title = _("Crear sitio web")


class WebsiteUpdateView(BaseWebsite, BaseUpdate):
    form_class = f.WebsiteForm
    form_template = "catalogs/form/website.html"
    list_url = "panel:website_list"
    success_url = "panel:website_list"
    cancel_url = "panel:website_list"
    success_message = _("Sitio web «%(obj)s» actualizado.")
    title = _("Editar sitio web")


class WebsiteDeleteView(BaseWebsite, BaseDelete):
    list_url = "panel:website_list"
    success_url = "panel:website_list"
    cancel_url = "panel:website_list"
    success_message = _("Sitio web «%(obj)s» eliminado.")
    title = _("Eliminar sitio web")


class CatalogsLogCreateView(BaseCatalogsLog, BaseCreate):
    form_class = f.CatalogsLogForm
    form_template = "catalogs/form/catalogs_log.html"
    list_url = "panel:catalogs-log_list"
    success_url = "panel:catalogs-log_list"
    cancel_url = "panel:catalogs-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class CatalogsLogUpdateView(BaseCatalogsLog, BaseUpdate):
    form_class = f.CatalogsLogForm
    form_template = "catalogs/form/catalogs_log.html"
    list_url = "panel:catalogs-log_list"
    success_url = "panel:catalogs-log_list"
    cancel_url = "panel:catalogs-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class CatalogsLogDeleteView(BaseCatalogsLog, BaseDelete):
    list_url = "panel:catalogs-log_list"
    success_url = "panel:catalogs-log_list"
    cancel_url = "panel:catalogs-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
