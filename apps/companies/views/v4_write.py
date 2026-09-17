"""companies · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.companies import forms as f
from apps.companies.views.base import BaseCompany, BaseCompanyImage, BaseCompanyLog
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class CompanyCreateView(BaseCompany, BaseCreate):
    # Django core
    form_class = f.CompanyForm
    form_template = "companies/form/company.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:company_list"
    success_url = "panel:company_list"
    cancel_url = "panel:company_list"
    # UX
    success_message = _("Compañía «%(obj)s» creada.")
    title = _("Crear compañía")


class CompanyUpdateView(BaseCompany, BaseUpdate):
    # Django core
    form_class = f.CompanyForm
    form_template = "companies/form/company.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:company_list"
    success_url = "panel:company_list"
    cancel_url = "panel:company_list"
    # UX
    success_message = _("Compañía «%(obj)s» actualizada.")
    title = _("Editar compañía")


class CompanyDeleteView(BaseCompany, BaseDelete):
    list_url = "panel:company_list"
    success_url = "panel:company_list"
    cancel_url = "panel:company_list"
    success_message = _("Compañía «%(obj)s» eliminada.")
    title = _("Eliminar compañía")


class CompanyImageCreateView(BaseCompanyImage, BaseCreate):
    form_class = f.CompanyImageForm
    form_template = "companies/form/company_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:company-image_list"
    success_url = "panel:company-image_list"
    cancel_url = "panel:company-image_list"
    success_message = _("Imagen de compañía «%(obj)s» creada.")
    title = _("Crear imagen de compañía")


class CompanyImageUpdateView(BaseCompanyImage, BaseUpdate):
    form_class = f.CompanyImageForm
    form_template = "companies/form/company_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:company-image_list"
    success_url = "panel:company-image_list"
    cancel_url = "panel:company-image_list"
    success_message = _("Imagen de compañía «%(obj)s» actualizada.")
    title = _("Editar imagen de compañía")


class CompanyImageDeleteView(BaseCompanyImage, BaseDelete):
    list_url = "panel:company-image_list"
    success_url = "panel:company-image_list"
    cancel_url = "panel:company-image_list"
    success_message = _("Imagen de compañía «%(obj)s» eliminada.")
    title = _("Eliminar imagen de compañía")


class CompanyLogCreateView(BaseCompanyLog, BaseCreate):
    form_class = f.CompanyLogForm
    form_template = "companies/form/company_log.html"
    list_url = "panel:company-log_list"
    success_url = "panel:company-log_list"
    cancel_url = "panel:company-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class CompanyLogUpdateView(BaseCompanyLog, BaseUpdate):
    form_class = f.CompanyLogForm
    form_template = "companies/form/company_log.html"
    list_url = "panel:company-log_list"
    success_url = "panel:company-log_list"
    cancel_url = "panel:company-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class CompanyLogDeleteView(BaseCompanyLog, BaseDelete):
    list_url = "panel:company-log_list"
    success_url = "panel:company-log_list"
    cancel_url = "panel:company-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
