"""companies · panel de filtros por modelo."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from core.shared.views.filters import BaseFilters, RelationFilter


class CompanyFilters(BaseFilters):
    model = Company
    include_filters = [RelationFilter("country", _("País"))]
