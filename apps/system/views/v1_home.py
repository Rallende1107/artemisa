"""system · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from apps.mailing.models import ContactMessage
from core.shared.views.base import BaseHomeView


# ==============================================================================
# Gestión
# ==============================================================================


class SystemHomeView(BaseHomeView):
    template_name = "panel/home.html"
    """Portada de /panel/: una card por app con home de gestión, y nada más —
    la portada solo NAVEGA. Los logs viven en el home de cada app y lo de
    system (tareas, cursores, nube) en su propio home, TasksHomeView."""
    title = _("Panel de gestión")
    page_sub = _("Elige una aplicación para gestionar.")
    background_image = "bg-system-home"
    background_fallback = "bg-system-home"   # respaldo si falta la imagen
    # Una card por app con home de gestión, en orden ALFABÉTICO por etiqueta.
    # Tupla: (ruta panel:<app>-home, etiqueta, icono, modelos que suman el
    # conteo, clase de fondo bg-<app>-home). La ruta debe existir en el
    # urls/panel.py de la app: si no, reverse() rompe el dashboard entero.
    cards = [
        ("panel:catalogs-home", _("Catálogos"), '<i class="bi bi-database"></i>', "bg-catalogs-home"),
        ("panel:collections-home", _("Colecciones"), '<i class="bi bi-collection"></i>', "bg-collections-home"),
        ("panel:companies-home", _("Compañías"), '<i class="bi bi-building"></i>', "bg-companies-home"),
        ("panel:mailing-home", _("Correos"), '<i class="bi bi-envelope-at"></i>', "bg-mailing-home"),
        ("panel:games-home", _("Juegos"), '<i class="bi bi-controller"></i>', "bg-games-home"),
        ("panel:music-home", _("Música"), '<i class="bi bi-music-note-beamed"></i>', "bg-music-home"),
        ("panel:otaku-home", _("Otaku"), '<i class="bi bi-stars"></i>', "bg-otaku-home"),
        ("panel:pages-home", _("Páginas"), '<i class="bi bi-file-text"></i>', "bg-pages-home"),
        ("panel:movies-home", _("Películas"), '<i class="bi bi-film"></i>', "bg-movies-home"),
        ("panel:people-home", _("Personas"), '<i class="bi bi-person"></i>', "bg-people-home"),
        ("panel:series-home", _("Series"), '<i class="bi bi-collection-play"></i>', "bg-series-home"),
        ("panel:tasks-home", _("Sistema"), '<i class="bi bi-cpu"></i>', "bg-system-task"),
        ("panel:users-home", _("Usuarios"), '<i class="bi bi-people"></i>', "bg-users-home"),
    ]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"cards": ctx["items"], "page_sub": self.page_sub, "contact_count": ContactMessage.objects.count()})
        return ctx


class TasksHomeView(BaseHomeView):
    """Home de la sección SISTEMA (/panel/tareas/): las tareas programadas (beat) con su
    alta, los cursores de lote, los archivos subidos a la nube y, como registro, las
    ejecuciones con el cancelador."""
    title = _("Sistema")
    active_entity = "tareas-home"
    background_image = "bg-system-task"
    background_fallback = "bg-system-home"   # respaldo si falta la imagen
    groups = [
        (_("Tareas"), [
            ("scheduled-task", _("Tareas programadas (beat)"), '<i class="bi bi-alarm"></i>', "bg-system-scheduled-task"),
            ("import-cursor", _("Cursores de lote"), '<i class="bi bi-skip-forward"></i>', "bg-system-import-cursor"),
            ("import-cursor-deezer", _("Cursores de Deezer"), '<i class="bi bi-skip-forward"></i>', "bg-system-import-cursor-deezer"),
            ("import-cursor-mal", _("Cursores de MAL"), '<i class="bi bi-skip-forward"></i>', "bg-system-import-cursor-mal"),
            ("import-cursor-vndb", _("Cursores de VNDB"), '<i class="bi bi-skip-forward"></i>', "bg-system-import-cursor-vndb"),
        ]),
        (_("Nube (R2)"), [
            ("cloud-file", _("Archivos en la nube"), '<i class="bi bi-cloud-upload"></i>', "bg-system-cloud-file"),
        ]),
        (_("Registro"), [
            ("task-run", _("Ejecuciones (cancelador)"), '<i class="bi bi-cpu"></i>', "bg-system-task"),
        ]),
    ]
