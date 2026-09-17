"""music · DESCARGAR IMÁGENES: una vista por tabla de imágenes, como «Procesar»: cuántas faltan, N o todas, en el worker
(se ve en Tareas y en Dozzle), por lotes y cancelable. Los fallos quedan en el log de la app."""
from django.utils.translation import gettext_lazy as _

from apps.music import forms
from apps.music.views.base import BaseAlbumImage, BaseArtistImage
from apps.system import tasks as system_tasks
from core.shared.views.base import BaseImport


class AlbumImageDownloadView(BaseAlbumImage, BaseImport):
    """Descargar a disco las imágenes pendientes de álbumes."""
    forms = (forms.AlbumImageDownloadForm, forms.AlbumImageRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de álbumes")
    ayuda = _("Baja a disco las imágenes que tienen URL y aún no están descargadas. Un 404 da la URL por muerta al primer intento; "
              "un timeout o un error del servidor, al tercero. Los fallos quedan en el log de la app con la URL y el motivo.")
    active_entity = "album-image"


class ArtistImageDownloadView(BaseArtistImage, BaseImport):
    """Descargar a disco las imágenes pendientes de artistas."""
    forms = (forms.ArtistImageDownloadForm, forms.ArtistImageRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de artistas")
    ayuda = _("Baja a disco las imágenes que tienen URL y aún no están descargadas. Un 404 da la URL por muerta al primer intento; "
              "un timeout o un error del servidor, al tercero. Los fallos quedan en el log de la app con la URL y el motivo.")
    active_entity = "artist-image"
