"""system · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.system import forms as f
from apps.system.views.base import BaseCloudFile, BaseImportCursor, BaseScheduledTask, BaseTaskRun
from core.shared.views.base import BaseCreate, BaseDelete, BaseSoftDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class CloudFileDeleteView(BaseCloudFile, BaseDelete):
    list_url = "panel:cloud-file_list"
    success_url = "panel:cloud-file_list"
    cancel_url = "panel:cloud-file_list"
    read_only = False   # quitar del registro: la URL de ese archivo vuelve al disco local
    success_message = _("Archivo «%(obj)s» quitado del registro de la nube.")
    title = _("Eliminar archivo en la nube")


class CloudFileCreateView(BaseCloudFile, BaseCreate):
    form_class = f.CloudFileForm
    list_url = "panel:cloud-file_list"
    success_url = "panel:cloud-file_list"
    cancel_url = "panel:cloud-file_list"
    success_message = _("Archivo en la nube «%(obj)s» creado.")
    title = _("Crear archivo en la nube")


class CloudFileUpdateView(BaseCloudFile, BaseUpdate):
    form_class = f.CloudFileForm
    list_url = "panel:cloud-file_list"
    success_url = "panel:cloud-file_list"
    cancel_url = "panel:cloud-file_list"
    success_message = _("Archivo en la nube «%(obj)s» actualizado.")
    title = _("Editar archivo en la nube")


class ImportCursorCreateView(BaseImportCursor, BaseCreate):
    # Django core
    form_class = f.ImportCursorForm
    list_url = "panel:import-cursor_list"
    success_url = "panel:import-cursor_list"
    cancel_url = "panel:import-cursor_list"
    # UX
    success_message = _("Cursor de lote «%(obj)s» creado.")
    title = _("Crear cursor de lote")


class ImportCursorUpdateView(BaseImportCursor, BaseUpdate):
    # Django core
    form_class = f.ImportCursorForm
    list_url = "panel:import-cursor_list"
    success_url = "panel:import-cursor_list"
    cancel_url = "panel:import-cursor_list"
    # UX
    success_message = _("Cursor de lote «%(obj)s» actualizado.")
    title = _("Editar cursor de lote")


class ImportCursorDeleteView(BaseImportCursor, BaseSoftDelete):
    list_url = "panel:import-cursor_list"
    success_url = "panel:import-cursor_list"
    cancel_url = "panel:import-cursor_list"
    success_message = _("Cursor de lote «%(obj)s» eliminado (el próximo lote partirá de 1).")
    title = _("Eliminar cursor de lote")


class ScheduledTaskCreateView(BaseScheduledTask, BaseCreate):
    # Django core
    form_class = f.ScheduledTaskForm
    list_url = "panel:scheduled-task_list"
    success_url = "panel:scheduled-task_list"
    cancel_url = "panel:scheduled-task_list"
    # UX
    success_message = _("Tarea programada «%(obj)s» creada.")
    title = _("Crear tarea programada")


class ScheduledTaskUpdateView(BaseScheduledTask, BaseUpdate):
    # Django core
    form_class = f.ScheduledTaskForm
    list_url = "panel:scheduled-task_list"
    success_url = "panel:scheduled-task_list"
    cancel_url = "panel:scheduled-task_list"
    # UX
    success_message = _("Tarea programada «%(obj)s» actualizada.")
    title = _("Editar tarea programada")


class ScheduledTaskDeleteView(BaseScheduledTask, BaseDelete):
    list_url = "panel:scheduled-task_list"
    success_url = "panel:scheduled-task_list"
    cancel_url = "panel:scheduled-task_list"
    success_message = _("Tarea programada «%(obj)s» eliminada.")
    title = _("Eliminar tarea programada")


class TaskRunDeleteView(BaseTaskRun, BaseDelete):
    list_url = "panel:task-run_list"
    success_url = "panel:task-run_list"
    cancel_url = "panel:task-run_list"
    read_only = False   # sí se puede borrar del registro (limpieza), aunque no se edite
    success_message = _("Tarea «%(obj)s» eliminada del registro.")
    title = _("Eliminar tarea")


class TaskRunCreateView(BaseTaskRun, BaseCreate):
    form_class = f.TaskRunForm
    list_url = "panel:task-run_list"
    success_url = "panel:task-run_list"
    cancel_url = "panel:task-run_list"
    success_message = _("Tarea «%(obj)s» creado.")
    title = _("Crear tarea")


class TaskRunUpdateView(BaseTaskRun, BaseUpdate):
    form_class = f.TaskRunForm
    list_url = "panel:task-run_list"
    success_url = "panel:task-run_list"
    cancel_url = "panel:task-run_list"
    success_message = _("Tarea «%(obj)s» actualizado.")
    title = _("Editar tarea")
