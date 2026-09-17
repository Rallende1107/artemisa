"""system · panel de filtros por modelo (gestión)."""
from django.utils.translation import gettext_lazy as _

from apps.system.models import TaskRun
from core.shared.views.filters import BaseFilters, ChoiceFilter


class TaskRunFilters(BaseFilters):
    model = TaskRun
    generic_filters = [ChoiceFilter("status", _("Estado"))]
