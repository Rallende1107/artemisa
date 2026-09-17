"""system · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.system.models import CloudFile, ImportCursor, ScheduledTask, TaskRun
from apps.system.views.base import BaseCloudFile, BaseImportCursor, BaseScheduledTask, BaseTaskRunContext
from apps.system.views.v2_filters import TaskRunFilters
from core.shared.models.choices import TaskRunStatus
from core.shared.views.base import AdminDataView
from core.utils.views_base import cell


# ==============================================================================
# Gestión
# ==============================================================================

PILDORA = {"QUEUED": "warn", "RUNNING": "on", "DONE": "on", "FAILED": "off", "CANCELLED": "off"}


class CloudFileDataView(BaseCloudFile, AdminDataView):
    columns = [(_("Archivo"), "name"), (_("KB"), "size"), (_("Subido"), "uploaded_at")]

    def get(self, request, tipo=None, pk=None):
        qs = CloudFile.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["name"], {}, ('-uploaded_at',))
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": str(self.col_size(obj)),
                "c2": cell(obj, "uploaded_at"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

    def col_size(self, obj):
        return f"{obj.size / 1024:,.0f}".replace(",", ".") if obj.size else ""


class ImportCursorDataView(BaseImportCursor, AdminDataView):
    columns = [(_("Fuente"), "source"), (_("Tipo"), "type"), (_("Próximo id"), "next_id"), (_("Cantidad"), "batch_size"),
               (_("Actualizado"), "updated_at")]

    def get(self, request, tipo=None, pk=None):
        qs = ImportCursor.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["source", "type"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": str(self.col_source(obj)),
                "c1": cell(obj, "type"),
                "c2": cell(obj, "next_id"),
                "c3": cell(obj, "batch_size"),
                "c4": cell(obj, "updated_at"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

    def col_source(self, obj):
        return obj.get_source_display()

    def extra_row_actions(self, obj, request):
        return [f'<a role="menuitem" href="{reverse("panel:import-cursor_launch", args=[obj.pk])}">'
                f'<i class="bi bi-play-circle ic"></i> Lanzar lote ahora</a>']


class ImportCursorDeezerDataView(ImportCursorDataView):
    """Solo los cursores de Deezer."""

    def get(self, request, tipo=None, pk=None):
        qs = ImportCursor.objects.filter(source="deezer")
        p, total, filtrado, objetos = self.query(request, qs, ["source", "type"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": str(self.col_source(obj)),
                "c1": cell(obj, "type"),
                "c2": cell(obj, "next_id"),
                "c3": cell(obj, "batch_size"),
                "c4": cell(obj, "updated_at"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ImportCursorMalDataView(ImportCursorDataView):
    """Solo los cursores de MAL."""

    def get(self, request, tipo=None, pk=None):
        qs = ImportCursor.objects.filter(source="mal")
        p, total, filtrado, objetos = self.query(request, qs, ["source", "type"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": str(self.col_source(obj)),
                "c1": cell(obj, "type"),
                "c2": cell(obj, "next_id"),
                "c3": cell(obj, "batch_size"),
                "c4": cell(obj, "updated_at"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ImportCursorVndbDataView(ImportCursorDataView):
    """Solo los cursores de VNDB."""

    def get(self, request, tipo=None, pk=None):
        qs = ImportCursor.objects.filter(source="vndb")
        p, total, filtrado, objetos = self.query(request, qs, ["source", "type"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": str(self.col_source(obj)),
                "c1": cell(obj, "type"),
                "c2": cell(obj, "next_id"),
                "c3": cell(obj, "batch_size"),
                "c4": cell(obj, "updated_at"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ScheduledTaskDataView(BaseScheduledTask, AdminDataView):
    columns = [(_("Nombre"), "name"), (_("Tarea"), "task"), (_("Cada N min"), "every_minutes"),
               (_("A esta hora"), "at_time"), (_("Última"), "last_run_at"), (_("Próxima"), "next_run_at"), (_("Activa"), "is_active")]

    def get(self, request, tipo=None, pk=None):
        qs = ScheduledTask.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["name", "task"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": str(self.col_task(obj)),
                "c2": cell(obj, "every_minutes"),
                "c3": cell(obj, "at_time"),
                "c4": cell(obj, "last_run_at"),
                "c5": cell(obj, "next_run_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

    def col_task(self, obj):
        from apps.system.registro import nombre_tarea
        return nombre_tarea(obj.task)

    def extra_row_actions(self, obj, request):
        return [f'<a role="menuitem" href="{reverse("panel:scheduled-task_run", args=[obj.pk])}">'
                f'<i class="bi bi-play-circle ic"></i> Ejecutar ahora</a>']


class TaskRunDataView(BaseTaskRunContext, AdminDataView):
    columns = [(_("Tarea"), "corto"), (_("Fuente"), "fuente"), (_("Argumentos"), "args"), (_("Estado"), "status"),
               (_("Avance"), "avance"), (_("Encolada"), "queued_at"), (_("Duración (s)"), "duracion"), (_("Lanzada por"), "user")]
    filters = TaskRunFilters

    def get(self, request, tipo=None, pk=None):
        qs = TaskRun.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["name", "args", "task_id", "result"], {}, ('-queued_at',))
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "corto"),
                "c1": cell(obj, "fuente"),
                "c2": str(self.col_args(obj)),
                "c3": str(self.col_status(obj)),
                "c4": str(self.col_avance(obj)),
                "c5": cell(obj, "queued_at"),
                "c6": cell(obj, "duracion"),
                "c7": cell(obj, "user"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        respuesta = self.response(p, total, filtrado, filas)
        # «activas»: la lista se auto-recarga mientras sea > 0 (datatable.js); al terminar todas, se detiene sola
        import json
        datos = json.loads(respuesta.content)
        datos["activas"] = TaskRun.objects.filter(status__in=(TaskRunStatus.QUEUED, TaskRunStatus.RUNNING)).count()
        return JsonResponse(datos)

    def col_avance(self, obj):
        """«X de N (P %)» con una barrita; vacío si la tarea no informa avance."""
        if not obj.progress_total:
            return ""
        pct = min(100, round(obj.progress_done * 100 / obj.progress_total))
        return mark_safe(f'<div style="min-width:140px"><div style="font-size:12px">{escape(obj.avance)}</div>'
                         f'<div style="height:4px;border-radius:2px;background:rgba(255,255,255,.12);margin-top:3px">'
                         f'<div style="height:4px;border-radius:2px;background:var(--accent);width:{pct}%"></div></div></div>')

    def col_status(self, obj):
        clase = PILDORA.get(obj.status, "")
        texto = escape(str(obj.get_status_display()))
        if obj.cancel_requested and obj.activa:
            texto += " · cancelando…"
        return mark_safe(f'<span class="stat {clase}">{texto}</span>')

    def col_args(self, obj):
        return (obj.args or "")[:80]      # la celda ya escapa

    def extra_row_actions(self, obj, request):
        if not obj.activa:
            return []
        acciones = [f'<a role="menuitem" href="{reverse("panel:task-run_cancel", args=[obj.pk])}">'
                    f'<i class="bi bi-hand-index ic"></i> Cancelar (cooperativa)</a>']
        if obj.status == TaskRunStatus.RUNNING:
            acciones.append(f'<a role="menuitem" href="{reverse("panel:task-run_finish", args=[obj.pk])}">'
                            f'<i class="bi bi-x-octagon ic"></i> Terminar (forzada)</a>')
        return acciones
