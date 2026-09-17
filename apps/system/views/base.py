"""BASE de la sección Sistema (tareas): config por entidad (clases privadas).

La clase privada `_Entidad` es la única fuente de config compartida; las vistas de los
módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.utils.translation import gettext_lazy as _

from apps.system.models import CloudFile, ImportCursor, ScheduledTask, TaskRun


FONDO = "bg-system-home"


class _System:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = FONDO   # respaldo si falta la imagen
    section_url = "panel:tasks-home"
    section_label = _("Sistema")


class BaseCloudFile(_System):
    model = CloudFile
    read_only = True   # lo escribe la tarea de subida a R2; aquí se consulta y, si hace falta, se limpia
    entity = "cloud-file"
    label = _("archivo en la nube")
    label_plural = _("archivos en la nube")
    background_image = "bg-system-cloud-file"
    namespace = "panel"
    page_template = "panel/base.html"


class BaseImportCursor(_System):
    model = ImportCursor
    entity = "import-cursor"
    label = _("cursor de lote")
    label_plural = _("cursores de lote")
    background_image = "bg-system-import-cursor"
    namespace = "panel"
    page_template = "panel/base.html"


class BaseScheduledTask(_System):
    model = ScheduledTask
    entity = "scheduled-task"
    label = _("tarea programada")
    label_plural = _("tareas programadas (beat)")
    background_image = "bg-system-scheduled-task"
    namespace = "panel"
    page_template = "panel/base.html"


class BaseTaskRun(_System):
    model = TaskRun
    read_only = True   # registro: se consulta, se cancela y se limpia; no se edita
    entity = "task-run"
    label = _("tarea")
    label_plural = _("ejecuciones (cancelador)")
    background_image = "bg-system-task"
    namespace = "panel"
    page_template = "panel/base.html"


class BaseTaskRunContext(BaseTaskRun):
    """Mapa «por» de ejecuciones: tipo → (campo, título, fondo). `status` acota por el CHOICE del campo `status`
    (valor en la URL, validado contra sus choices); lo comparten la Data (filtra) y la ListBy (título, fondo)."""
    filter_config = {
        "status": ("status", _("Ejecuciones · {valor}"), "bg-system-task"),
    }
