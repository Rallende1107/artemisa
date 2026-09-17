"""system · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.system.views.base import BaseCloudFile, BaseImportCursor, BaseScheduledTask, BaseTaskRun, BaseTaskRunContext
from core.shared.views.base import AdminListByView, AdminListView


# ==============================================================================
# Gestión
# ==============================================================================


class CloudFileListView(BaseCloudFile, AdminListView):
    """Archivos de media que YA están en R2 (los anota la tarea de subida). Borrar una fila hace que
    la URL de ese archivo vuelva a apuntar al disco local."""
    home_url = "panel:tasks-home"
    data_url = "panel:cloud-file_data"
    title = _("Lista de archivos en la nube")
    bulk_delete = True


class ImportCursorListView(BaseImportCursor, AdminListView):
    """Por dónde va el lote de cada fuente y tipo. Se crean solos al primer lote; aquí se corrigen."""
    home_url = "panel:tasks-home"
    data_url = "panel:import-cursor_data"
    create_url = "panel:import-cursor_create"
    title = _("Lista de cursores de lote")


class ImportCursorDeezerListView(BaseImportCursor, AdminListView):
    home_url = "panel:tasks-home"
    data_url = "panel:import-cursor-deezer_data"
    create_url = "panel:import-cursor_create"
    title = _("Lista de cursores de Deezer")
    active_entity = "import-cursor-deezer"
    label_plural = _("cursores de Deezer")
    background_image = "bg-system-import-cursor-deezer"
    background_fallback = ("bg-system-import-cursor", "bg-system-home")


class ImportCursorMalListView(BaseImportCursor, AdminListView):
    home_url = "panel:tasks-home"
    data_url = "panel:import-cursor-mal_data"
    create_url = "panel:import-cursor_create"
    title = _("Lista de cursores de MAL")
    active_entity = "import-cursor-mal"
    label_plural = _("cursores de MAL")
    background_image = "bg-system-import-cursor-mal"
    background_fallback = ("bg-system-import-cursor", "bg-system-home")


class ImportCursorVndbListView(BaseImportCursor, AdminListView):
    home_url = "panel:tasks-home"
    data_url = "panel:import-cursor-vndb_data"
    create_url = "panel:import-cursor_create"
    title = _("Lista de cursores de VNDB")
    active_entity = "import-cursor-vndb"
    label_plural = _("cursores de VNDB")
    background_image = "bg-system-import-cursor-vndb"
    background_fallback = ("bg-system-import-cursor", "bg-system-home")


class ScheduledTaskListView(BaseScheduledTask, AdminListView):
    home_url = "panel:tasks-home"
    data_url = "panel:scheduled-task_data"
    create_url = "panel:scheduled-task_create"
    title = _("Lista de tareas programadas (beat)")


class TaskRunListView(BaseTaskRun, AdminListView):
    home_url = "panel:tasks-home"
    data_url = "panel:task-run_data"
    title = _("Lista de ejecuciones (cancelador)")
    bulk_delete = True    # limpiar el registro a mano: marcar y eliminar
    auto_recarga = 5      # segundos: se refresca sola mientras haya ejecuciones en cola o corriendo (ver TaskRunDataView)


class TaskRunListByView(BaseTaskRunContext, AdminListByView):
    """Lista acotada por el mapa (`/task-run/<tipo>/<valor>/`): la alimenta TaskRunDataView con `/data/<tipo>/<valor>/`."""
    home_url = "panel:tasks-home"
    data_url = "panel:task-run_data-by"
    full_list_url = "panel:task-run_list"
    by_url = "panel:task-run_by"
    bulk_delete = True    # limpiar el registro a mano: marcar y eliminar
