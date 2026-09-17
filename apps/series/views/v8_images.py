"""series · DESCARGAR IMÁGENES: una vista por tabla de imágenes, como «Procesar»: cuántas faltan, N o todas, en el worker
(se ve en Tareas y en Dozzle), por lotes y cancelable. Los fallos quedan en el log de la app."""
from django.utils.translation import gettext_lazy as _

from apps.series import forms
from apps.series.views.base import BaseSerieImage
from apps.system import tasks as system_tasks
from core.shared.views.base import BaseImport


class SerieImageDownloadView(BaseSerieImage, BaseImport):
    """Descargar a disco las imágenes pendientes de series."""
    forms = (forms.SerieImageDownloadForm, forms.SerieImageRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de series")
    ayuda = _("Baja a disco las imágenes que tienen URL y aún no están descargadas. Un 404 da la URL por muerta al primer intento; "
              "un timeout o un error del servidor, al tercero. Los fallos quedan en el log de la app con la URL y el motivo.")
    active_entity = "serie-image"
