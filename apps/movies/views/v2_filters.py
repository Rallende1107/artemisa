"""movies · panel de filtros por modelo, de gestión (con «Activo») y público."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.movies.models import Movie, MovieCast, MovieStaff, Role
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter, RelationFilter, YearFilter


# ==============================================================================
# Público
# ==============================================================================


class CompanyFilters(BaseFilters):
    model = Company
    include_filters = []


class MovieFilters(BaseFilters):
    model = Movie
    include_filters = [RelationFilter("genres", _("Género")), RelationFilter("movie_type", _("Tipo")), RelationFilter("producers", _("Productora")), RelationFilter("movie_rating", _("Clasificación")), RelationFilter("distributors", _("Distribuidora")), YearFilter("release_year", _("Año"))]


class MovieCastFilters(BaseFilters):
    model = MovieCast
    include_filters = [RelationFilter("role", _("Rol"))]


class MovieStaffFilters(BaseFilters):
    model = MovieStaff
    include_filters = [RelationFilter("role", _("Rol"))]


class RoleFilters(BaseFilters):
    model = Role
    generic_filters = [ChoiceFilter("type", _("Tipo de rol")), BooleanFilter("is_active", _("Activo"))]
