from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import CatalogsLog, Country, ExternalSource, Format, Language, Quality, RelationType, Website
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter


# ==============================================================================
# Gestión
# ==============================================================================


class CountryFilters(BaseFilters):
    model = Country
    generic_filters = [BooleanFilter("is_active", _("Activo"))]


class ExternalSourceFilters(BaseFilters):
    model = ExternalSource
    generic_filters = [
        ChoiceFilter("type", _("Tipo")),
        BooleanFilter("is_active", _("Activo")),
    ]


class FormatFilters(BaseFilters):
    model = Format
    generic_filters = [BooleanFilter("is_active", _("Activo"))]


class LanguageFilters(BaseFilters):
    model = Language
    generic_filters = [BooleanFilter("is_active", _("Activo"))]


class QualityFilters(BaseFilters):
    model = Quality
    generic_filters = [BooleanFilter("is_active", _("Activo"))]


class RelationTypeFilters(BaseFilters):
    model = RelationType
    generic_filters = [BooleanFilter("is_active", _("Activo"))]


class WebsiteFilters(BaseFilters):
    model = Website
    generic_filters = [
        ChoiceFilter("type", _("Tipo")),
        BooleanFilter("is_active", _("Activo")),
    ]
