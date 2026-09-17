"""Context processors globales de Artemisa."""
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def sitio(request):
    """Identidad del sitio (marca) disponible en todas las plantillas.
    Centraliza SITE_NAME: cambiarlo en settings lo cambia en título y header."""
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Frikiverso"),
        "SITE_TAGLINE": getattr(settings, "SITE_TAGLINE", ""),
        "ASSET_VERSION": getattr(settings, "ASSET_VERSION", "1"),
    }


def sidebar(request):
    """Si la request cae dentro de un panel con SIDEBAR registrado (por su
    namespace de URL), expone nav/título/pie para `templates/panel/_sidebar.html`
    (genérico, data-driven). Fuera de un panel registrado no aporta nada."""
    from core.shared.views.sidebar import get_sidebar

    match = getattr(request, "resolver_match", None)
    ns = match.namespace if match else ""
    sb = get_sidebar(ns)
    if not sb:
        return {}
    return {
        "sidebar": {
            "namespace": sb.namespace,
            "title": sb.title,
            "footer": sb.footer,
            "nav": sb.nav_for_context(),
        }
    }


def seccion_nav(request):
    """Nav SECUNDARIO (de sección): navega el CONTENIDO de la app y persiste en todas sus páginas (el sidebar es
    el nav global entre apps). Lo DECLARA CADA APP en su `views/base.py` (`nav`, normalmente en el mixin `_<App>`
    que heredan todas sus entidades); aquí solo se resuelve: se calcula el href de cada entrada y cuál se
    enciende, comparando el nombre de la ruta actual con los que la entrada declare.

    Una vista sin `nav` —o con `nav = ()`— no pinta barra. Las fichas y las páginas hijas la apagan poniendo
    `SECCION_NAV: []` en su contexto, que gana sobre esto.
    """
    from django.urls import reverse

    match = getattr(request, "resolver_match", None)
    if match is None:
        return {}
    vista = getattr(match.func, "view_class", None)
    nav = getattr(vista, "nav", ()) if vista is not None else ()
    if not nav:
        return {}
    name = match.url_name
    return {"SECCION_NAV": [{"label": etiqueta, "url": reverse(ruta), "icon": icono, "on": name in activos}
                            for etiqueta, ruta, icono, activos in nav]}


def secciones(request):
    """Secciones del catálogo para el navbar público: cada sección lleva a su
    HOME (landing con portada y CTA al catálogo). Anime y Manga son secciones
    distintas, cada una con su home propio.
    (La sección 'Imágenes'/civitai se descartó por lo legal.)"""
    from django.urls import reverse

    # `icon` = clase de Bootstrap Icons (se pinta como <i class="bi {{ icon }}">).
    defs = [
        ("otaku", _("Anime y Manga"), "otaku:home", "bi-stars"),
        ("musica", _("Música"), "music:home", "bi-music-note-beamed"),
        ("peliculas", _("Películas"), "movies:home", "bi-film"),
        ("series", _("Series"), "series:home", "bi-collection-play"),
        ("juegos", _("Juegos"), "games:home", "bi-controller"),
        ("personas", _("Personas"), "personas:home", "bi-people"),
        ("companias", _("Compañías"), "companias:home", "bi-building"),
    ]
    return {
        "SECCIONES": [
            {"slug": slug, "label": label, "url": reverse(name), "icon": icon}
            for slug, label, name, icon in defs
        ],
    }
