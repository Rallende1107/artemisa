"""companies · LISTAS (el shell; las filas llegan por su Data)."""
from django.utils.translation import gettext_lazy as _

from apps.companies.views.base import BaseCompany, BaseCompanyImage, BaseCompanyLog
from core.shared.views.base import AdminListView, PublicListView


# ==============================================================================
# Gestión
# ==============================================================================


class CompanyListView(BaseCompany, AdminListView):
    home_url = "panel:companies-home"
    data_url = "panel:company_data"
    create_url = "panel:company_create"
    title = _("Lista de compañías")


class CompanyMovieListView(BaseCompany, AdminListView):
    """Lista FIJA: solo las compañías con obras de ese medio. «Nuevo» crea la compañía global."""
    home_url = "panel:companies-home"
    data_url = "panel:company-movie_data"
    create_url = "panel:company_create"
    title = _("Compañías de cine")
    active_entity = "company-movie"
    label_plural = _("compañías de cine")
    background_image = "bg-movies-company"            # el fondo de CINE, no el de la compañía general
    background_fallback = ("bg-companies-company", "bg-movies-home")


class CompanySerieListView(BaseCompany, AdminListView):
    """Lista FIJA: solo las compañías con obras de ese medio. «Nuevo» crea la compañía global."""
    home_url = "panel:companies-home"
    data_url = "panel:company-serie_data"
    create_url = "panel:company_create"
    title = _("Compañías de TV")
    active_entity = "company-serie"
    label_plural = _("compañías de tv")
    background_image = "bg-series-company"            # el fondo de TV, no el de la compañía general
    background_fallback = ("bg-companies-company", "bg-series-home")


class CompanyImageListView(BaseCompanyImage, AdminListView):
    home_url = "panel:companies-home"
    buttons = (("panel:company-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:company-image_data"
    create_url = "panel:company-image_create"
    title = _("Lista de imágenes de compañía")


class CompanyLogListView(BaseCompanyLog, AdminListView):
    data_url = "panel:company-log_data"
    home_url = "panel:companies-home"
    create_url = "panel:company-log_create"
    title = _("Lista de log de compañías")
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)


# ==============================================================================
# Público
# ==============================================================================


class CompanyPublicListView(BaseCompany, PublicListView):
    """Catálogo de TODAS las compañías (con buscador y filtros)."""
    data_url = "companias:companies-catalog-data"
    section = "companias"
    title = _("Compañías")
    icon = "bi-building"
    subtitle = _("Estudios, productoras, distribuidoras, licenciatarias y revistas de todos los medios.")
    home_url = "companias:home"
    home_label = _("compañías")
