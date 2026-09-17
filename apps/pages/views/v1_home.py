"""pages · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.pages.views.base import _SECCIONES_PORTADA, FONDO
from core.shared.views.base import BaseHomeView
from core.utils.views import resolve_background


# ==============================================================================
# Gestión
# ==============================================================================


class PagesHomeView(BaseHomeView):
    title = 'Páginas'
    active_entity = 'pages-home'
    background_image = FONDO
    background_fallback = FONDO   # respaldo si falta la imagen
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Páginas"), [
            ('about-section', _('Secciones de nosotros'), '<i class="bi bi-info-circle"></i>', 'bg-pages-about'),
            ('terms-section', _('Secciones de términos'), '<i class="bi bi-file-earmark-text"></i>', 'bg-pages-terms'),
            ('privacy-section', _('Secciones de privacidad'), '<i class="bi bi-shield-check"></i>', 'bg-pages-privacy'),
        ]),
        (_("Registro"), [
            ('pages-log', _('Log de páginas'), '<i class="bi bi-journal-text"></i>', "bg-pages-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class IndexView(TemplateView):
    """Landing general (identidad + secciones + arte)."""
    template_name = "pages/index.html"
    title = _("Inicio")
    background_image = "bg-pages-index"
    background_fallback = "bg-pages-index"   # respaldo si falta la imagen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "inicio"
        context["page_title"] = self.title
        context["background_image"] = resolve_background(self)
        context["secciones"] = [
            {"url": reverse(url_name), "image": f"image/screen/wide/{bg}.webp",
             "title": title, "text": text}
            for url_name, bg, title, text in _SECCIONES_PORTADA
        ]
        return context
