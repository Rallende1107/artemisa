"""system · acciones POST y páginas «a mano», de gestión y públicas."""
from celery import current_app
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.system.models import ImportCursor, ScheduledTask, TaskRun
from apps.system.views.base import BaseImportCursor, BaseScheduledTask, BaseTaskRun
from core.shared.models.choices import TaskRunStatus
from core.shared.views.base import BasePage
from core.utils.views import resolve_background


# ==============================================================================
# Gestión
# ==============================================================================

class BaseAccionTarea(BasePage, BaseTaskRun, TemplateView):
    """Página de confirmación (GET) + acción (POST) sobre una TaskRun activa."""
    template_name = "admin_panel/tarea_accion.html"
    modo = ""            # "cancelar" | "terminar"
    titulo = ""
    explicacion = ""

    def dispatch(self, request, *args, **kwargs):
        self.tarea = get_object_or_404(TaskRun, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"tarea": self.tarea, "modo": self.modo, "titulo": self.titulo, "explicacion": self.explicacion,
                    "background_image": resolve_background(self), "page_title": self.titulo,
                    "list_url": "panel:task-run_list", "label_plural": self.label_plural})
        return ctx

    def _volver(self):
        return redirect(reverse("panel:task-run_list"))


class TaskRunCancelView(BaseAccionTarea):
    modo = "cancelar"
    titulo = _("Cancelar tarea")
    explicacion = _("Se pide la cancelación: si la tarea aún no empezó, el worker la descarta; si ya está "
                    "corriendo, se detiene sola en el siguiente paso (entre ids, entre álbumes…). Lo ya guardado se queda.")

    def post(self, request, *args, **kwargs):
        t = self.tarea
        if not t.activa:
            messages.warning(request, f"«{t}» ya terminó ({t.get_status_display()}).")
            return self._volver()
        t.cancel_requested = True
        t.save(update_fields=["cancel_requested"])
        try:
            current_app.control.revoke(t.task_id, terminate=False)
        except Exception as exc:  # noqa: BLE001 — sin broker (modo síncrono) no hay a quién avisar
            messages.info(request, f"Sin broker para el revoke ({type(exc).__name__}); queda la bandera de cancelación.")
        if t.status == TaskRunStatus.QUEUED:
            t.status = TaskRunStatus.CANCELLED
            t.finished_at = timezone.now()
            t.result = "cancelada antes de empezar"
            t.save(update_fields=["status", "finished_at", "result"])
        messages.success(request, f"Cancelación pedida para «{t}».")
        return self._volver()


class TaskRunFinishView(BaseAccionTarea):
    modo = "terminar"
    titulo = _("Terminar tarea (forzada)")
    explicacion = _("Mata el proceso del worker que la ejecuta (SIGTERM). Úsalo solo si la cancelación cooperativa "
                    "no responde: lo que estuviera a medio guardar queda a medias.")

    def post(self, request, *args, **kwargs):
        t = self.tarea
        if t.status != TaskRunStatus.RUNNING:
            messages.warning(request, f"«{t}» no está corriendo ({t.get_status_display()}).")
            return self._volver()
        t.cancel_requested = True
        t.save(update_fields=["cancel_requested"])
        try:
            current_app.control.revoke(t.task_id, terminate=True, signal="SIGTERM")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"No pude mandar el terminate ({type(exc).__name__}): ¿está el broker arriba?")
            return self._volver()
        t.status = TaskRunStatus.CANCELLED
        t.finished_at = timezone.now()
        t.result = "terminada por el usuario"
        t.save(update_fields=["status", "finished_at", "result"])
        messages.success(request, f"«{t}» terminada.")
        return self._volver()


class ScheduledTaskRunView(BasePage, BaseScheduledTask, TemplateView):
    """«Ejecutar ahora»: encola la tarea programada en este momento con sus argumentos y su cantidad,
    esté activa o no. Es el modo MANUAL: la fila guarda la configuración (qué tarea, cuántos) y René
    la lanza cuando quiere, sin que beat la toque mientras siga apagada."""
    template_name = "admin_panel/programada_ejecutar.html"

    def dispatch(self, request, *args, **kwargs):
        self.programada = get_object_or_404(ScheduledTask, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"programada": self.programada, "kwargs_efectivos": self.programada.kwargs_efectivos(),
                    "background_image": resolve_background(self), "page_title": _("Ejecutar ahora"),
                    "label_plural": self.label_plural})
        return ctx

    def post(self, request, *args, **kwargs):
        from core.shared.views.imports import anotar_usuario
        p = self.programada
        try:
            resultado = p.encolar()
        except Exception as exc:  # noqa: BLE001 — sin broker no hay a quién encolar
            messages.error(request, f"No pude encolar «{p}» ({type(exc).__name__}: {exc}). ¿Está el worker arriba?")
            return redirect(reverse("panel:scheduled-task_list"))
        anotar_usuario(resultado, request.user)
        messages.success(request, f"«{p}» encolada ahora. Síguela en Ejecuciones.")
        return redirect(reverse("panel:task-run_list"))


class ImportCursorLaunchView(BasePage, BaseImportCursor, TemplateView):
    """«Lanzar lote ahora» desde el cursor: encola el siguiente lote de esa fuente y tipo con la cantidad de
    la fila. El cursor avanza cuando la tarea reparte el lote."""
    template_name = "admin_panel/cursor_lanzar.html"

    def dispatch(self, request, *args, **kwargs):
        self.cursor = get_object_or_404(ImportCursor, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"cursor": self.cursor, "background_image": resolve_background(self), "page_title": _("Lanzar lote ahora"),
                    "label_plural": self.label_plural, "hasta": self.cursor.next_id + self.cursor.batch_size - 1})
        return ctx

    def post(self, request, *args, **kwargs):
        from core.shared.views.imports import anotar_usuario
        c = self.cursor
        try:
            resultado = c.lanzar()
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"No pude encolar el lote ({type(exc).__name__}: {exc}). ¿Está el worker arriba?")
            return redirect(reverse("panel:import-cursor_list"))
        anotar_usuario(resultado, request.user)
        messages.success(request, f"Lote de {c.batch_size} {c.type}(s) de {c.get_source_display()} encolado desde #{c.next_id}. Síguelo en Ejecuciones.")
        return redirect(reverse("panel:task-run_list"))
