"""Señales de users: registran actividad de cuenta en UserLog (correo,
contraseña, usuario, teléfono, nacimiento, avatar, activar/desactivar, staff,
superusuario) y avisan por correo
cuando se BLOQUEA/ACTIVA una cuenta.

Detecta el cambio venga de donde venga (panel, /admin/, shell): compara el
estado de ANTES (pre_save) contra el de DESPUÉS (post_save), igual para los
5 campos vigilados. El actor (quién lo hizo) viaja en `instance._actor`
—atributo transitorio, nunca se persiste— que las vistas ponen justo antes
de guardar (apps/users/views/public.py, apps/users/views/v4_create.py,
v5_update.py, core/views/v8_actions.py:AdminToggleView). Sin `_actor` (shell,
`/admin/` directo) el log queda con actor=None ("el sistema").
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.users.activity import registrar
from apps.users.models import CustomUser, UserLog
from core.shared.models.choices import LogLevel, UserActivityAction
from core.utils.importlog import log_to


_WATCHED = ("email", "password", "username", "first_name", "last_name", "phone", "birth_date", "avatar",
            "is_active", "is_staff", "is_superuser")

# (self, otro) por campo — "otro" lleva `{user}` para el afectado.
_ACCIONES = {
    "email": ("cambió su correo", "cambió el correo de {user}"),
    "password": ("cambió su contraseña", "cambió la contraseña de {user}"),
    "username": ("cambió su nombre de usuario", "cambió el nombre de usuario de {user}"),
    "first_name": ("cambió su nombre", "cambió el nombre de {user}"),
    "last_name": ("cambió su apellido", "cambió el apellido de {user}"),
    "phone": ("cambió su teléfono", "cambió el teléfono de {user}"),
    "birth_date": ("cambió su fecha de nacimiento", "cambió la fecha de nacimiento de {user}"),
    "avatar": ("cambió su avatar", "cambió el avatar de {user}"),
    ("is_active", True): ("activó su cuenta", "activó la cuenta de {user}"),
    ("is_active", False): ("desactivó su cuenta", "desactivó la cuenta de {user}"),
    ("is_staff", True): ("obtuvo permisos de staff", "otorgó permisos de staff a {user}"),
    ("is_staff", False): ("perdió permisos de staff", "quitó permisos de staff a {user}"),
    ("is_superuser", True): ("obtuvo superusuario", "otorgó superusuario a {user}"),
    ("is_superuser", False): ("quitó su superusuario", "quitó superusuario a {user}"),
}


@receiver(pre_save, sender=CustomUser)
def _capturar_estado_previo(sender, instance, **kwargs):
    if instance.pk:
        prev = sender.objects.filter(pk=instance.pk).only(*_WATCHED).first()
        instance._old = {f: getattr(prev, f) for f in _WATCHED} if prev else None
    else:
        instance._old = None


def _sujeto(actor):
    if actor is None:
        return "El sistema"
    return f"{actor} (staff)" if actor.is_staff else str(actor)


# Campos cuyo log lleva el DETALLE «de X a Y» (nunca password; avatar sin rutas).
_CON_DETALLE = ("email", "username", "first_name", "last_name", "phone", "birth_date")


def _fmt(valor):
    if valor in (None, ""):
        return "—"
    if hasattr(valor, "strftime"):
        return valor.strftime("%d-%m-%Y")
    return str(valor)


def _frase(field, old_value, new_value, user, actor):
    key = (field, bool(new_value)) if field in ("is_active", "is_staff", "is_superuser") else field
    self_tpl, otro_tpl = _ACCIONES[key]
    if actor is not None and actor.pk == user.pk:
        frase = f"{user} {self_tpl}"
    else:
        frase = f"{_sujeto(actor)} {otro_tpl.format(user=user)}"
    if field in _CON_DETALLE:
        frase += f": de «{_fmt(old_value)}» a «{_fmt(new_value)}»"
    return frase


@receiver(post_save, sender=CustomUser)
def _registrar_actividad(sender, instance, created, **kwargs):
    actor = getattr(instance, "_actor", None)

    if created:
        propio = actor is None or actor.pk == instance.pk
        frase = f"{instance} creó su cuenta" if propio else f"{_sujeto(actor)} creó la cuenta de {instance}"
        log_to(UserLog, LogLevel.INFO, frase, user=instance, actor=actor)
        registrar(instance, UserActivityAction.REGISTER)
        return

    old = getattr(instance, "_old", None)
    if old is None:
        return

    for field in _WATCHED:
        old_val, new_val = old[field], getattr(instance, field)
        if old_val == new_val:
            continue
        log_to(UserLog, LogLevel.INFO, _frase(field, old_val, new_val, instance, actor), user=instance, actor=actor)
        if actor is not None and actor.pk == instance.pk:
            frase = _frase(field, old_val, new_val, instance, actor)
            frase = frase[len(f"{instance} "):] if frase.startswith(f"{instance} ") else frase   # sin el sujeto: es SU actividad
            registrar(instance, UserActivityAction.PASSWORD if field == "password" else UserActivityAction.PROFILE, label=frase)
        if field == "is_active":
            from apps.users.notifications import notify_user_action
            notify_user_action(instance, "activated" if new_val else "deactivated", actor=actor)


@receiver(user_logged_in)
def _actividad_login(sender, request, user, **kwargs):
    registrar(user, UserActivityAction.LOGIN)


@receiver(user_logged_out)
def _actividad_logout(sender, request, user, **kwargs):
    registrar(user, UserActivityAction.LOGOUT)
