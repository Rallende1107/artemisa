"""AUDITORÍA del panel: lo que hace un administrador queda en el LOG DE SU APP.

Cada app tiene su propio modelo de log (subclase de ModelBaseLog: MovieLog, OtakuLog,
EmailLog, PeopleLog…) para no amontonar todo en una tabla. `audit()` localiza el log
de la app del objeto y anota: «admin creó género «Acción» (#12)». Lo llaman las
bases del panel (BaseCreate/BaseUpdate/BaseDelete) y AdminToggleView, así que NO hay
que hacer nada por entidad.

Excepciones: el modelo de usuario (su actividad la registra la señal de UserLog con
afectado + actor) y los propios modelos de log (no se auditan a sí mismos)."""
from django.apps import apps as registry
from django.contrib.auth import get_user_model

from core.utils.importlog import log_to
from core.shared.models.abstract import ModelBaseLog
from core.shared.models.choices import LogLevel


def log_model_for(model):
    """El modelo de log de la app de `model` (None si la app no tiene)."""
    if issubclass(model, ModelBaseLog):
        return None
    for m in registry.get_app_config(model._meta.app_label).get_models():
        if issubclass(m, ModelBaseLog):
            return m
    return None


def audit(user, verbo, obj, detalle=""):
    """Anota en el log de la app: «<usuario> <verbo> <entidad> «<obj>» (#pk)[: detalle]».
    Nunca lanza: una auditoría que falla no debe romper la acción."""
    model = getattr(obj, "_model", None) or type(obj)   # objeto real o cáscara de un borrado
    if model is get_user_model():
        return None                       # lo cubre la señal de UserLog
    log_model = log_model_for(model)
    if log_model is None:
        return None
    quien = getattr(user, "username", None) or "sistema"
    msg = f"{quien} {verbo} {model._meta.verbose_name} «{obj}» (#{obj.pk})"
    if detalle:
        msg += f": {detalle}"
    try:
        return log_to(log_model, LogLevel.INFO, "panel", msg)
    except Exception:  # noqa: BLE001
        return None
