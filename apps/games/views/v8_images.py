"""games · DESCARGAR IMÁGENES: una vista por tabla de imágenes, como «Procesar»: cuántas faltan, N o todas, en el worker
(se ve en Tareas y en Dozzle), por lotes y cancelable. Los fallos quedan en el log de la app."""
from django.utils.translation import gettext_lazy as _

from apps.games import forms
from apps.games.views.base import BaseCharacterImage, BaseGameImage, BaseReleaseImage
from apps.system import tasks as system_tasks
from core.shared.views.base import BaseImport


class CharacterImageDownloadView(BaseCharacterImage, BaseImport):
    """Descargar a disco las imágenes pendientes de personajes de juego."""
    forms = (forms.CharacterImageDownloadForm, forms.CharacterImageRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de personajes de juego")
    ayuda = _("Baja a disco las imágenes que tienen URL y aún no están descargadas. Un 404 da la URL por muerta al primer intento; "
              "un timeout o un error del servidor, al tercero. Los fallos quedan en el log de la app con la URL y el motivo.")
    active_entity = "game-character-image"


class GameImageDownloadView(BaseGameImage, BaseImport):
    """Descargar a disco las imágenes pendientes de juegos."""
    forms = (forms.GameImageDownloadForm, forms.GameImageRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de juegos")
    ayuda = _("Baja a disco las imágenes que tienen URL y aún no están descargadas. Un 404 da la URL por muerta al primer intento; "
              "un timeout o un error del servidor, al tercero. Los fallos quedan en el log de la app con la URL y el motivo.")
    active_entity = "game-image"


class ReleaseImageDownloadView(BaseReleaseImage, BaseImport):
    """Descargar a disco las imágenes pendientes de lanzamientos."""
    forms = (forms.ReleaseImageDownloadForm, forms.ReleaseImageRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de lanzamientos")
    ayuda = _("Baja a disco las imágenes que tienen URL y aún no están descargadas. Un 404 da la URL por muerta al primer intento; "
              "un timeout o un error del servidor, al tercero. Los fallos quedan en el log de la app con la URL y el motivo.")
    active_entity = "game-release-image"
