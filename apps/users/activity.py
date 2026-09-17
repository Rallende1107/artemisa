"""Registro de ACTIVIDAD del usuario (R9): una línea por acción, persistente (no se purga).

    from apps.users.activity import registrar
    registrar(request.user, UserActivityAction.COLLECTION_ADD, obj=anime)
"""
from django.contrib.contenttypes.models import ContentType

from apps.users.models import UserActivity


def registrar(user, action, obj=None, label=""):
    """Crea la fila; nunca rompe la vista que la llama (usuario anónimo o error → no se registra)."""
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    try:
        ct = ContentType.objects.get_for_model(type(obj)) if obj is not None else None
        return UserActivity.objects.create(
            user=user, action=action, content_type=ct, object_id=getattr(obj, "pk", None) if obj is not None else None,
            label=(label or (str(obj) if obj is not None else ""))[:255])
    except Exception:  # noqa: BLE001
        return None
