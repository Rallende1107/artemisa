"""pages · acciones POST y páginas «a mano», de gestión y públicas."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.mailing.models import ContactMessage, ContactReply
from apps.pages.models import AboutSection, PrivacySection, TermsSection
from apps.pages.views.base import _error_context, _parsear_cuerpo
from core.shared.models.choices import ContactMessageStatus
from core.utils.views import resolve_background


# ==============================================================================
# Público
# ==============================================================================

class BasePaginaInformativa(TemplateView):
    """Página informativa (Nosotros / Términos / Privacidad): el contenido
    vive en la BD (system.LegalSection, editable desde el panel con
    auditoría) — aquí solo se declara qué página es. La plantilla compartida
    pinta el TOC (una sección a la vez) y el cuerpo."""
    template_name = "pages/legal.html"
    title = ""
    subtitulo = ""
    con_fecha = True    # muestra la última actualización real (auditoría)
    seccion = ""        # active_section (nav)
    modelo = None       # SU modelo de contenido (responsabilidades separadas)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        secciones, ultima = [], None
        filas = self.modelo.objects.filter(is_active=True).order_by("order", "pk")
        for f in filas:
            parrafos, lista = _parsear_cuerpo(f.body)
            secciones.append({"clave": f"s{f.pk}", "titulo": f.title,
                              "parrafos": parrafos, "lista": lista})
            if ultima is None or f.updated_at > ultima:
                ultima = f.updated_at
        subtitulo = self.subtitulo
        if self.con_fecha:
            fecha = ultima.strftime("%d-%m-%Y") if ultima else "—"
            subtitulo = f"{_('Última actualización')}: {fecha}"
        ctx.update({
            "active_section": self.seccion,
            "page_title": self.title,
            "background_image": resolve_background(self),
            "subtitulo": subtitulo,
            "secciones": secciones,
        })
        return ctx


class AboutView(BasePaginaInformativa):
    title = _("Nosotros")
    seccion = "nosotros"
    modelo = AboutSection
    subtitulo = _("Frikiverso · un proyecto personal, hecho por y para frikis")
    con_fecha = False
    background_image = "bg-pages-about"
    background_fallback = "bg-pages-about"   # respaldo si falta la imagen


class ContactView(TemplateView):
    template_name = "pages/contacto.html"
    title = _("Contacto")
    background_image = "bg-pages-contact"
    background_fallback = "bg-pages-contact"   # respaldo si falta la imagen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = "contacto"
        context["page_title"] = self.title
        context["background_image"] = resolve_background(self)
        return context

    def post(self, request, *args, **kwargs):
        nombre = (request.POST.get("nombre") or "").strip()
        email = (request.POST.get("email") or "").strip()
        asunto = (request.POST.get("asunto") or "").strip()
        mensaje = (request.POST.get("mensaje") or "").strip()

        if not (nombre and email and mensaje):
            messages.error(request, _("Completa al menos nombre, correo y mensaje."))
            return redirect("pages:contact")

        # Persistir en BD (gestionable desde el panel). Si escribe un usuario
        # registrado, el mensaje queda LIGADO a su cuenta (hilo «Mis mensajes»).
        ContactMessage.objects.create(
            name=nombre, email=email, subject=asunto, message=mensaje,
            user=request.user if request.user.is_authenticated else None)

        # Avisar por correo al dueño del sitio (CONTACT_EMAIL): "fulano te escribió".
        # Usa la plantilla editable 'contacto_aviso' y queda guardado en EmailMessage (bandeja) y anotado en EmailLog (log).
        from django.conf import settings
        from apps.mailing.services import send_templated
        send_templated("contacto_aviso", settings.CONTACT_EMAIL, {
            "nombre": nombre,
            "email": email,
            "asunto": asunto or "(sin asunto)",
            "mensaje": mensaje,
            "sitio": settings.SITE_NAME,
        })

        messages.success(request, _("¡Mensaje recibido! Lo revisaremos y te responderemos."))
        return redirect("pages:contact")


class GlobalSearchView(TemplateView):
    """BUSCADOR GLOBAL del sitio: cruza todos los medios. Pensado para
    ESCALA: sin conteos (nada de COUNT sobre LIKE en tablas enormes) — trae
    6 por categoría; si llegan 6, el «Ver más» manda al catálogo del medio
    con la búsqueda ya puesta (?q=), que pagina y filtra de verdad."""
    template_name = "search/global.html"
    background_image = "bg-pages-index"
    background_fallback = "bg-pages-index"
    TOPE = 6

    def get_context_data(self, **kwargs):
        from apps.people.models import Person
        from apps.movies.models import Movie
        from apps.music.models import Album, Artist, Song
        from apps.otaku.models import Anime, Character, Manga
        from apps.games.models import Creator, Game
        from apps.series.models import Serie
        from core.utils.public import resolve_cover, url_detail

        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()
        grupos = []
        if q:
            FUENTES = [
                (_("Anime"), Anime, "title", "otaku:anime-detail", "otaku:anime-catalog"),
                (_("Manga"), Manga, "title", "otaku:manga-detail", "otaku:manga-catalog"),
                (_("Películas"), Movie, "title", "movies:movie-detail", "movies:movies-catalog"),
                (_("Series"), Serie, "title", "series:serie-detail", "series:series-catalog"),
                (_("Juegos"), Game, "title", "games:game-detail", "games:games-catalog"),
                (_("Álbumes"), Album, "title", "music:album-detail", "music:albums-catalog"),
                (_("Artistas"), Artist, "name", "music:artist-detail", "music:artists-catalog"),
                (_("Canciones"), Song, "title", "music:song-detail", "music:songs-catalog"),
                (_("Personas"), Person, "full_name", "personas:person-detail", "personas:people-catalog"),
                (_("Personajes"), Character, "full_name", "otaku:character-detail", "otaku:characters-catalog"),
                (_("Creadores"), Creator, "name", "games:creator-detail", "games:creators-catalog"),
            ]
            for titulo, modelo, campo, ruta, catalogo in FUENTES:
                filas = list(modelo.objects.filter(
                    is_active=True, **{f"{campo}__icontains": q})[:self.TOPE])
                if not filas:
                    continue
                items = []
                for o in filas:
                    anio = getattr(o, "year", None) or getattr(o, "release_year", None)
                    items.append({"name": str(o), "sub": str(anio or ""),
                                  "image": resolve_cover(o), "url": url_detail(ruta, o)})
                grupos.append({"titulo": titulo, "items": items,
                               "hay_mas": len(filas) >= self.TOPE,
                               "url_mas": f"{reverse(catalogo)}?q={q}"})
        ctx.update({
            "active_section": "",
            "page_title": _("Resultados para «%s»") % q if q else _("Buscar"),
            "background_image": resolve_background(self),
            "q": q,
            "grupos": grupos,
        })
        return ctx


class MyMessagesView(LoginRequiredMixin, TemplateView):
    """MIS MENSAJES: el hilo del usuario registrado con el sitio — cada vez
    que nos contactó y lo que se le respondió. Se enlazan por su cuenta y,
    para mensajes viejos, por su correo."""
    template_name = "pages/mis_mensajes.html"
    background_image = "bg-pages-contact"
    background_fallback = "bg-pages-contact"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        enlazado = Q(user=u)
        if u.email:
            enlazado |= Q(email__iexact=u.email)
        hilos = (ContactMessage.objects.filter(enlazado, is_active=True)
                 .exclude(status=ContactMessageStatus.SPAM)
                 .prefetch_related(Prefetch(
                     "replies",
                     queryset=ContactReply.objects.filter(is_active=True)
                     .select_related("author")))
                 .order_by("-created_at"))
        ctx.update({
            "active_section": "contacto",
            "page_title": _("Mis mensajes"),
            "background_image": resolve_background(self),
            "hilos": hilos,
        })
        return ctx


class TermsView(BasePaginaInformativa):
    title = _("Términos de uso")
    seccion = "terminos"
    modelo = TermsSection
    background_image = "bg-pages-terms"
    background_fallback = "bg-pages-terms"   # respaldo si falta la imagen


class PrivacyView(BasePaginaInformativa):
    title = _("Privacidad")
    seccion = "privacidad"
    modelo = PrivacySection
    background_image = "bg-pages-privacy"
    background_fallback = "bg-pages-privacy"   # respaldo si falta la imagen


class BaseErrorView(TemplateView):
    """Base de las 4 páginas de error. Django exige que handler400/403/404
    acepten cualquier método HTTP (llegan también por POST: un formulario
    con CSRF vencido, un host no permitido, etc.) — el dispatch normal de
    una CBV los rechazaría con 405, así que acá se ignora el método y
    siempre se sirve el mismo GET."""
    status_code = 200
    heading = ""
    message_text = ""

    def dispatch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_error_context(self.heading, self.message_text))
        ctx["status_code"] = self.status_code
        return ctx

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault("status", self.status_code)
        return super().render_to_response(context, **response_kwargs)


class BaseErrorStandaloneView(BaseErrorView):
    """Plantilla autónoma (sin extends de base.html) para las 4 páginas de
    error: cualquiera de ellas puede llegar a ocurrir con el request en un
    estado que no garantiza que el cromo del sitio (header/sidebar, con sus
    context processors) sea seguro de renderizar."""
    template_name = "errors/standalone.html"


class Error404View(BaseErrorStandaloneView):
    status_code = 404
    heading = _("Página no encontrada")
    message_text = _("Quizás el título que buscas ya no existe o el enlace está roto.")


class Error403View(BaseErrorStandaloneView):
    status_code = 403
    heading = _("Acceso no permitido")
    message_text = _("No tienes permiso para ver esta página o realizar esta acción.")
    csrf = False

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["csrf"] = self.csrf
        return ctx


class Error403CsrfView(Error403View):
    """CSRF_FAILURE_VIEW: el 403 bonito también para fallos CSRF (sesión
    caducada, formulario viejo) — reemplaza la página técnica de Django."""
    message_text = _("Tu sesión caducó o el formulario quedó viejo. Vuelve atrás, recarga la página e inténtalo de nuevo.")
    csrf = True


class Error500View(BaseErrorStandaloneView):
    status_code = 500
    heading = _("Error del servidor")
    message_text = _("Algo salió mal de nuestro lado. Ya estamos en ello — inténtalo de nuevo en un momento.")


class Error400View(BaseErrorStandaloneView):
    """DisallowedHost y peticiones malformadas."""
    status_code = 400
    heading = _("Petición no válida")
    message_text = _("El servidor no reconoce este dominio o la petición llegó malformada.")


# Los handlers de core/urls.py y CSRF_FAILURE_VIEW (settings) apuntan a apps.pages.views.<nombre>.
# handler404/500/403/400 y CSRF_FAILURE_VIEW se referencian por string desde
# core/urls.py y core/settings.py (import perezoso: settings.py se carga
# antes de que el registro de apps esté listo). Estos nombres son las
# instancias .as_view() ya construidas de las CBV de arriba.
error_404 = Error404View.as_view()


error_500 = Error500View.as_view()


error_403 = Error403View.as_view()


error_400 = Error400View.as_view()


csrf_failure_view = Error403CsrfView.as_view()
