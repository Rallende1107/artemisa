"""pages · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.pages import forms as f
from apps.pages.views.base import BaseAboutSection, BasePagesLog, BasePrivacySection, BaseTermsSection
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class AboutSectionCreateView(BaseAboutSection, BaseCreate):
    # Django core
    form_class = f.AboutSectionForm
    list_url = "panel:about-section_list"
    success_url = "panel:about-section_list"
    cancel_url = "panel:about-section_list"
    # UX
    success_message = _("Sección de nosotros «%(obj)s» creada.")
    title = _("Crear sección de nosotros")


class AboutSectionUpdateView(BaseAboutSection, BaseUpdate):
    # Django core
    form_class = f.AboutSectionForm
    list_url = "panel:about-section_list"
    success_url = "panel:about-section_list"
    cancel_url = "panel:about-section_list"
    # UX
    success_message = _("Sección de nosotros «%(obj)s» actualizada.")
    title = _("Editar sección de nosotros")


class AboutSectionDeleteView(BaseAboutSection, BaseDelete):
    list_url = "panel:about-section_list"
    success_url = "panel:about-section_list"
    cancel_url = "panel:about-section_list"
    success_message = _("Sección de nosotros «%(obj)s» eliminada.")
    title = _("Eliminar sección de nosotros")


class PrivacySectionCreateView(BasePrivacySection, BaseCreate):
    # Django core
    form_class = f.PrivacySectionForm
    list_url = "panel:privacy-section_list"
    success_url = "panel:privacy-section_list"
    cancel_url = "panel:privacy-section_list"
    # UX
    success_message = _("Sección de privacidad «%(obj)s» creada.")
    title = _("Crear sección de privacidad")


class PrivacySectionUpdateView(BasePrivacySection, BaseUpdate):
    # Django core
    form_class = f.PrivacySectionForm
    list_url = "panel:privacy-section_list"
    success_url = "panel:privacy-section_list"
    cancel_url = "panel:privacy-section_list"
    # UX
    success_message = _("Sección de privacidad «%(obj)s» actualizada.")
    title = _("Editar sección de privacidad")


class PrivacySectionDeleteView(BasePrivacySection, BaseDelete):
    list_url = "panel:privacy-section_list"
    success_url = "panel:privacy-section_list"
    cancel_url = "panel:privacy-section_list"
    success_message = _("Sección de privacidad «%(obj)s» eliminada.")
    title = _("Eliminar sección de privacidad")


class TermsSectionCreateView(BaseTermsSection, BaseCreate):
    # Django core
    form_class = f.TermsSectionForm
    list_url = "panel:terms-section_list"
    success_url = "panel:terms-section_list"
    cancel_url = "panel:terms-section_list"
    # UX
    success_message = _("Sección de términos «%(obj)s» creada.")
    title = _("Crear sección de términos")


class TermsSectionUpdateView(BaseTermsSection, BaseUpdate):
    # Django core
    form_class = f.TermsSectionForm
    list_url = "panel:terms-section_list"
    success_url = "panel:terms-section_list"
    cancel_url = "panel:terms-section_list"
    # UX
    success_message = _("Sección de términos «%(obj)s» actualizada.")
    title = _("Editar sección de términos")


class TermsSectionDeleteView(BaseTermsSection, BaseDelete):
    list_url = "panel:terms-section_list"
    success_url = "panel:terms-section_list"
    cancel_url = "panel:terms-section_list"
    success_message = _("Sección de términos «%(obj)s» eliminada.")
    title = _("Eliminar sección de términos")


class PagesLogCreateView(BasePagesLog, BaseCreate):
    form_class = f.PagesLogForm
    form_template = "pages/form/pages_log.html"
    list_url = "panel:pages-log_list"
    success_url = "panel:pages-log_list"
    cancel_url = "panel:pages-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class PagesLogUpdateView(BasePagesLog, BaseUpdate):
    form_class = f.PagesLogForm
    form_template = "pages/form/pages_log.html"
    list_url = "panel:pages-log_list"
    success_url = "panel:pages-log_list"
    cancel_url = "panel:pages-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class PagesLogDeleteView(BasePagesLog, BaseDelete):
    list_url = "panel:pages-log_list"
    success_url = "panel:pages-log_list"
    cancel_url = "panel:pages-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
