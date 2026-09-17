"""SUBIDA a la nube (Cloudflare R2) de los archivos de media que ya están en disco local.

Recorre todos los ImageField del proyecto (portadas de obras, fotos de personas, imágenes de categorías,
tablas de imágenes), toma los archivos que existen en disco y NO están en `system.CloudFile`, y los sube
hasta un tope por tanda (la tarea diaria usa 100: el límite de subidas de R2). Cada subida se anota en
CloudFile y, desde entonces, su URL pública apunta a R2 (core/storage.py). Sin USE_R2 no hace nada."""
import os

from django.apps import apps
from django.conf import settings
from django.db.models import ImageField

from core.shared.tasks.cancel import cancelado


def r2_activo():
    return bool(getattr(settings, "USE_R2", False))


def campos_imagen():
    """[(modelo, nombre del ImageField), …] de todo el proyecto."""
    out = []
    for m in apps.get_models():
        for f in m._meta.get_fields():
            if isinstance(f, ImageField):
                out.append((m, f.name))
    return out


def _cliente_r2():
    """Storage S3 de django-storages apuntando a R2 (se importa aquí: sin USE_R2 no hace falta la librería)."""
    from storages.backends.s3 import S3Storage
    return S3Storage()


def _subir_archivo(r2, nombre, ruta):
    """Sube `ruta` con la clave `nombre` (misma ruta relativa que en /media/). Devuelve (ok, detalle)."""
    try:
        with open(ruta, "rb") as f:
            if r2.exists(nombre):
                return True, "ya estaba en la nube"
            r2.bucket.upload_fileobj(f, nombre)
        return True, "subida"
    except Exception as exc:       # credenciales, red, permisos…
        return False, f"{type(exc).__name__}: {exc}"


def archivos_pendientes(modelo=None, ids=None):
    """Nombres de archivo en disco que aún no están en la nube: [(modelo, pk, nombre, ruta)…]."""
    from apps.system.models import CloudFile
    subidos = set(CloudFile.objects.values_list("name", flat=True))
    campos = [(m, c) for m, c in campos_imagen() if modelo is None or m is modelo]
    out = []
    for m, campo in campos:
        qs = m.objects.exclude(**{campo: ""}).order_by("pk")
        if ids:
            qs = qs.filter(pk__in=ids)
        for pk, nombre in qs.values_list("pk", campo):
            if not nombre or nombre in subidos:
                continue
            ruta = os.path.join(settings.MEDIA_ROOT, nombre)
            if os.path.isfile(ruta):
                out.append((m, pk, nombre, ruta))
                subidos.add(nombre)      # el mismo archivo referido dos veces se sube una
    return out


def subir_pendientes(modelo=None, ids=None, tope=100):
    """Sube hasta `tope` archivos pendientes. Devuelve {"ok": n, "fallos": n, "detalle": [(modelo, pk, detalle)…]}."""
    from apps.system.models import CloudFile
    from core.storage import anotar_en_nube
    resultado = {"ok": 0, "fallos": 0, "detalle": []}
    if not r2_activo():
        resultado["detalle"].append(("system", None, "USE_R2 apagado: nada que subir"))
        return resultado
    pendientes = archivos_pendientes(modelo, ids)[:max(int(tope), 0)]
    if not pendientes:
        return resultado
    try:
        r2 = _cliente_r2()
    except Exception as exc:
        resultado["fallos"] = len(pendientes)
        resultado["detalle"].append(("system", None, f"sin cliente R2: {type(exc).__name__}: {exc}"))
        return resultado
    for m, pk, nombre, ruta in pendientes:
        if cancelado():
            resultado["detalle"].append((m._meta.label, None, "cancelada por el usuario"))
            break
        ok, detalle = _subir_archivo(r2, nombre, ruta)
        if ok:
            CloudFile.objects.get_or_create(name=nombre, defaults={"size": os.path.getsize(ruta)})
            anotar_en_nube(nombre)
            resultado["ok"] += 1
        else:
            resultado["fallos"] += 1
            resultado["detalle"].append((m._meta.label, pk, detalle))
    return resultado
