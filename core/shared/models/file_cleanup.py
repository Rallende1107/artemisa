"""Borrado automático de archivos huérfanos (imágenes/ficheros) al REEMPLAZAR o
ELIMINAR registros — global para TODOS los modelos (y los futuros).

- pre_save:  si un FileField/ImageField cambió, borra el archivo ANTERIOR.
- post_delete: al borrar un registro, borra sus archivos.

`storage.delete()` funciona con cualquier backend de Django: hoy disco local,
mañana R2/S3 (Cloudflare) sin tocar este código. Va todo en try/except para no
romper el guardado/borrado si el archivo ya no existe.

Nota: las operaciones en lote (`QuerySet.update()`, `bulk_create`) NO disparan
señales; el panel usa `instance.save()`/`instance.delete()`, que sí las disparan.
"""
from functools import lru_cache

from django.db import models
from django.db.models.signals import post_delete, pre_save


@lru_cache(maxsize=None)
def _file_fields(model):
    """Nombres de los campos FileField/ImageField del modelo (cacheado)."""
    return tuple(
        f.name for f in model._meta.get_fields()
        if isinstance(f, models.FileField)
    )


def _delete_file(fieldfile):
    if fieldfile and getattr(fieldfile, "name", ""):
        try:
            fieldfile.storage.delete(fieldfile.name)
        except Exception:
            pass


def cleanup_on_change(sender, instance, **kwargs):
    """pre_save: borra el archivo anterior de cada campo de archivo que cambió."""
    fields = _file_fields(sender)
    if not fields or not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    for name in fields:
        old_f = getattr(old, name, None)
        new_f = getattr(instance, name, None)
        new_name = new_f.name if new_f else ""
        if old_f and old_f.name and old_f.name != new_name:
            _delete_file(old_f)


def cleanup_on_delete(sender, instance, **kwargs):
    """post_delete: borra todos los archivos del registro eliminado."""
    for name in _file_fields(sender):
        _delete_file(getattr(instance, name, None))


def register():
    """Conecta las señales globalmente (sin sender). El handler descarta rápido
    los modelos sin campos de archivo."""
    pre_save.connect(cleanup_on_change, dispatch_uid="artemisa_file_cleanup_save")
    post_delete.connect(cleanup_on_delete, dispatch_uid="artemisa_file_cleanup_delete")
