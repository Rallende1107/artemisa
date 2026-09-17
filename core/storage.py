"""Almacenamiento de MEDIA «local primero, nube después».

Todo archivo (portadas, fotos, imágenes de categorías) se guarda SIEMPRE en disco local (MEDIA_ROOT).
Con USE_R2=1, la tarea `apps.system.tasks.upload_pending_to_cloud_task` sube N archivos al día a R2 y
los anota en `system.CloudFile`; desde ese momento `url()` de ESE archivo apunta al dominio público de
R2 y el resto sigue sirviéndose desde /media/. Así el tope diario de subidas de R2 no frena las
descargas, y habilitar R2 más tarde no obliga a migrar nada de golpe."""
import time

from django.conf import settings
from django.core.files.storage import FileSystemStorage

_TTL = 60          # segundos que vive la lista de nombres subidos en memoria (por proceso)
_cache = {"hasta": 0.0, "nombres": frozenset()}


def nombres_en_nube():
    """Conjunto de nombres de archivo ya subidos a R2 (cacheado por proceso; se refresca cada minuto)."""
    ahora = time.monotonic()
    if ahora > _cache["hasta"]:
        try:
            from apps.system.models import CloudFile
            _cache["nombres"] = frozenset(CloudFile.objects.values_list("name", flat=True))
        except Exception:            # tabla aún no migrada, sin DB…: todo local
            _cache["nombres"] = frozenset()
        _cache["hasta"] = ahora + _TTL
    return _cache["nombres"]


def anotar_en_nube(nombre):
    """Suma un nombre al conjunto en memoria (tras subirlo) sin esperar al refresco."""
    _cache["nombres"] = _cache["nombres"] | {nombre}


def olvidar_nube():
    _cache["hasta"] = 0.0


class MediaLocalYNube(FileSystemStorage):
    """FileSystemStorage cuya `url()` apunta a R2 para los archivos que ya están allí."""

    def url(self, name):
        if name and getattr(settings, "USE_R2", False) and settings.R2_PUBLIC_DOMAIN and name in nombres_en_nube():
            return f"{settings.R2_PUBLIC_DOMAIN.rstrip('/')}/{name.lstrip('/')}"
        return super().url(name)
