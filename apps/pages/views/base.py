"""BASE de la sección Páginas: config por entidad (clases privadas).

La clase privada `_Entidad` es la única fuente de config compartida; las vistas
de los módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.pages.models import AboutSection, PagesLog, PrivacySection, TermsSection


FONDO = "bg-pages-home"


class _Pages:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = FONDO   # respaldo si falta la imagen
    section_url = "panel:pages-home"
    section_label = _("Páginas")


class BaseAboutSection(_Pages):
    model = AboutSection
    entity = "about-section"
    label = _("sección de nosotros")
    label_plural = _("secciones de nosotros")
    background_image = "bg-pages-about"      # la sección ES la página pública: misma imagen


class BasePrivacySection(_Pages):
    model = PrivacySection
    entity = "privacy-section"
    label = _("sección de privacidad")
    label_plural = _("secciones de privacidad")
    background_image = "bg-pages-privacy"


class BaseTermsSection(_Pages):
    model = TermsSection
    entity = "terms-section"
    label = _("sección de términos")
    label_plural = _("secciones de términos")
    background_image = "bg-pages-terms"


class BasePagesLog(_Pages):
    model = PagesLog
    entity = "pages-log"
    label = "log de páginas"
    label_plural = "log de páginas"
    background_image = "bg-pages-log"
    background_fallback = "bg-pages-home"   # respaldo si falta la imagen


# Vistas de la cara pública informativa (app pages).
# Basadas en clases (CBV), como el patrón de Hades.
# Tarjetas de «Explora las secciones» de la portada: (nombre de url, clase de
# fondo cuya imagen `wide` sirve de arte, título, bajada). Datos, no HTML: el
# template solo itera; los textos pasan por gettext_lazy para traducirse.

_SECCIONES_PORTADA = [
    ("otaku:home",    "bg-otaku-home",  _("Anime & Manga"), _("Series y películas de animación, manga y novelas ligeras.")),
    ("movies:home",   "bg-movies-home", _("Películas"),     _("Cine y animación.")),
    ("series:home",   "bg-series-home", _("Series"),        _("Televisión, temporadas y reparto.")),
    ("music:home",    "bg-music-home",  _("Música"),        _("Artistas, álbumes y canciones.")),
    ("games:home",    "bg-games-home",  _("Juegos"),        _("Visual novels y juegos Ren'Py.")),
    ("personas:home", "bg-people-home", _("Personas"),     _("Actores, directores, voces y staff detrás de cada obra.")),
    ("companias:home", "bg-companies-home", _("Compañías"), _("Estudios, productoras y distribuidoras de todos los medios.")),
]


def _parsear_cuerpo(texto):
    """Contenido de una sección → (párrafos, lista): bloques separados por
    línea en blanco; las líneas que comienzan con «- » forman la lista."""
    parrafos, lista = [], []
    for bloque in (texto or "").split("\n\n"):
        lineas = [l.strip() for l in bloque.strip().splitlines()]
        lista += [l[2:].strip() for l in lineas if l.startswith("- ")]
        limpio = " ".join(l for l in lineas if l and not l.startswith("- "))
        if limpio:
            parrafos.append(limpio)
    return parrafos, lista


# Fondo genérico de las 4 páginas de error (imagen única, sin fallback por
# entidad: no hay resolve_background porque no depende de ningún modelo).
_ERROR_BG = "bg-pages-error"


def _error_context(heading, message):
    """Contexto mínimo que consumen los templates de error: nada de texto,
    URL ni clase de fondo quedan hardcodeados en el HTML — todo pasa desde
    acá para poder traducirse (gettext_lazy)."""
    return {
        "heading": heading,
        "message": message,
        "background_image": _ERROR_BG,
        "home_url": reverse("pages:index"),
        "cta_label": _("Volver al inicio"),
    }
