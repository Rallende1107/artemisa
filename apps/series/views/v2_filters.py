"""series · panel de filtros por modelo, de gestión (con «Activo») y público."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.series.models import Role, Serie, SerieCast, SerieStaff
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter, RelationFilter, YearFilter


# ==============================================================================
# Público
# ==============================================================================


class CompanyFilters(BaseFilters):
    model = Company
    include_filters = []


class RoleFilters(BaseFilters):
    model = Role
    generic_filters = [ChoiceFilter("type", _("Tipo de rol")), BooleanFilter("is_active", _("Activo"))]


class SerieFilters(BaseFilters):
    model = Serie
    include_filters = [RelationFilter("genres", _("Género")), RelationFilter("serie_type", _("Tipo")), RelationFilter("producers", _("Productora")), RelationFilter("serie_rating", _("Clasificación")), RelationFilter("distributors", _("Distribuidora")), YearFilter("release_year", _("Año"))]


class SerieCastFilters(BaseFilters):
    model = SerieCast
    include_filters = [RelationFilter("role", _("Rol"))]


class SerieStaffFilters(BaseFilters):
    model = SerieStaff
    include_filters = [RelationFilter("role", _("Rol"))]
