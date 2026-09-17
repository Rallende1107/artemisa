"""pages · fichas, de gestión y públicas."""
from apps.pages.views.base import BaseAboutSection, BasePagesLog, BasePrivacySection, BaseTermsSection
from core.shared.views.base import BaseAdminDetailView


# Gestión
# ==============================================================================


class AboutSectionDetailView(BaseAboutSection, BaseAdminDetailView):
    template_name = "pages/detail/about_section.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:about-section_update"
    delete_url = "panel:about-section_delete"
    list_url = "panel:about-section_list"
    toggle_url = "panel:about-section_toggle"


class PrivacySectionDetailView(BasePrivacySection, BaseAdminDetailView):
    template_name = "pages/detail/privacy_section.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:privacy-section_update"
    delete_url = "panel:privacy-section_delete"
    list_url = "panel:privacy-section_list"
    toggle_url = "panel:privacy-section_toggle"


class TermsSectionDetailView(BaseTermsSection, BaseAdminDetailView):
    template_name = "pages/detail/terms_section.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:terms-section_update"
    delete_url = "panel:terms-section_delete"
    list_url = "panel:terms-section_list"
    toggle_url = "panel:terms-section_toggle"


class PagesLogDetailView(BasePagesLog, BaseAdminDetailView):
    template_name = "pages/detail/pages_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    list_url = "panel:pages-log_list"
    section_label = "Páginas"
