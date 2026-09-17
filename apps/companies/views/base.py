"""BASE de la sección Compañías: config por entidad (clases privadas).

La clase privada `_Entidad` es la única fuente de config compartida; las vistas de los módulos vN_*.py la heredan
como PRIMER mixin — estilo Poseidon."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company, CompanyImage, CompanyLog





# NAV PÚBLICO de la sección: (etiqueta, ruta, icono, {nombres de ruta donde queda ACTIVA}).
NAV_PUBLICO = (
    (_("Compañías"), "companias:home", "bi-building", {"home"}),
    (_("Todas"), "companias:companies-catalog", "bi-list-ul", {"companies-catalog", "company-detail"}),
)


class _Companies:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = 'bg-companies-home'   # respaldo si falta la imagen
    section_url = "panel:companies-home"
    section_label = _("Compañías")
    nav = NAV_PUBLICO


class BaseCompany(_Companies):
    model = Company
    entity = "company"
    label = _("compañía")
    label_plural = _("compañías")
    background_image = "bg-companies-company"


class BaseCompanyImage(_Companies):
    model = CompanyImage
    entity = "company-image"
    label = _("imagen")
    label_plural = _("imágenes de compañía")
    background_image = "bg-companies-company-image"


class BaseCompanyImageContext(BaseCompanyImage):
    """Mapa «por» de imágenes de compañía: tipo → (campo que acota, título, fondo)."""
    filter_config = {
        "compania": ("company", _("Imágenes de {padre}"), "bg-companies-company"),
    }


class BaseCompanyLog(_Companies):
    model = CompanyLog
    entity = "company-log"
    label = "log de compañías"
    label_plural = "log de compañías"
    background_image = "bg-companies-log"
