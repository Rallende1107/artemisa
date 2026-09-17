"""mailing · panel de filtros por modelo (gestión)."""
from django.utils.translation import gettext_lazy as _

from apps.mailing.models import ContactMessage, EmailMessage
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter


class ContactMessageFilters(BaseFilters):
    model = ContactMessage
    generic_filters = [ChoiceFilter("status", _("Estado")), BooleanFilter("is_active", _("Activo"))]


class EmailMessageFilters(BaseFilters):
    model = EmailMessage
    generic_filters = [ChoiceFilter("status", _("Estado"))]
