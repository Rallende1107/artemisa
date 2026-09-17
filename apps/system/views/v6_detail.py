"""system · fichas, de gestión y públicas."""
from apps.system.views.base import BaseCloudFile, BaseImportCursor, BaseScheduledTask, BaseTaskRun
from core.shared.views.base import BaseAdminDetailView


# ==============================================================================
# Gestión
# ==============================================================================


class CloudFileDetailView(BaseCloudFile, BaseAdminDetailView):
    template_name = "system/detail/cloud_file.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:cloud-file_delete"
    list_url = "panel:cloud-file_list"


class ImportCursorDetailView(BaseImportCursor, BaseAdminDetailView):
    template_name = "system/detail/import_cursor.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:import-cursor_update"
    delete_url = "panel:import-cursor_delete"
    list_url = "panel:import-cursor_list"


class ScheduledTaskDetailView(BaseScheduledTask, BaseAdminDetailView):
    template_name = "system/detail/scheduled_task.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:scheduled-task_update"
    delete_url = "panel:scheduled-task_delete"
    list_url = "panel:scheduled-task_list"
    toggle_url = "panel:scheduled-task_toggle"


class TaskRunDetailView(BaseTaskRun, BaseAdminDetailView):
    template_name = "system/detail/task_run.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:task-run_delete"
    list_url = "panel:task-run_list"
