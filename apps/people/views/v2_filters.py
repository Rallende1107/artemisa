"""people · panel de filtros por modelo, de gestión (con «Activo») y público."""
from django.utils.translation import gettext_lazy as _

from apps.people.models import Person
from core.shared.views.filters import BaseFilters, BooleanFilter, RelationFilter, YearFilter


# ==============================================================================
# Gestión
# ==============================================================================


class PersonAdminFilters(BaseFilters):
    model = Person
    generic_filters = [BooleanFilter("is_active", _("Activo"))]
    include_filters = [RelationFilter("country", _("País")), YearFilter("birth_date", _("Año de nacimiento"))]


# ==============================================================================
# Público
# ==============================================================================


class PersonFilters(BaseFilters):
    model = Person
    include_filters = [RelationFilter("country", _("País")), YearFilter("birth_date", _("Año de nacimiento"))]
