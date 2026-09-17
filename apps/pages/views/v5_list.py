"""pages · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.pages.views.base import BaseAboutSection, BasePagesLog, BasePrivacySection, BaseTermsSection
from core.shared.views.base import AdminListView


# ==============================================================================
# Gestión
# ==============================================================================


class AboutSectionListView(BaseAboutSection, AdminListView):
    home_url = "panel:pages-home"
    data_url = "panel:about-section_data"
    create_url = "panel:about-section_create"
    title = _("Lista de secciones de nosotros")


class PrivacySectionListView(BasePrivacySection, AdminListView):
    home_url = "panel:pages-home"
    data_url = "panel:privacy-section_data"
    create_url = "panel:privacy-section_create"
    title = _("Lista de secciones de privacidad")


class TermsSectionListView(BaseTermsSection, AdminListView):
    home_url = "panel:pages-home"
    data_url = "panel:terms-section_data"
    create_url = "panel:terms-section_create"
    title = _("Lista de secciones de términos")


class PagesLogListView(BasePagesLog, AdminListView):
    home_url = "panel:pages-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:pages-log_data"
    create_url = "panel:pages-log_create"
    title = _("Lista de log de páginas")
