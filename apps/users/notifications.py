"""Notificaciones por correo de acciones sobre usuarios.

Un único punto: cuando se crea/bloquea/activa/resetea/elimina a un usuario, se le
avisa por correo con la plantilla editable correspondiente (app mailing). Respeta
el master switch SEND_EMAIL y el estado del correo (consola en dev / SMTP en prod).
Si no hay plantilla activa para la acción, no pasa nada (queda traza en Email/EmailLog).
"""
import logging

from django.conf import settings

from core.shared.models.choices import EmailMessageStatus


log = logging.getLogger("artemisa.users")

# acción → key de la plantilla de correo (EmailTemplate)
TEMPLATE_FOR = {
    "created": "usuario_created",
    "activated": "usuario_activated",
    "deactivated": "usuario_bloqueado",
    "password_reset": "usuario_password_reset",
    "deleted": "usuario_deleted",
}


def notify_user_action(user, action, actor=None, extra=None):
    """Avisa al `user` de una `action` sobre su cuenta, por correo.

    action: 'created' | 'activated' | 'deactivated' | 'password_reset' | 'deleted'
    Devuelve True si se envió el correo, False si no (switch off / sin plantilla /
    sin email). Nunca lanza.
    """
    who = getattr(actor, "username", "sistema")
    log.info("acción usuario: %s → %s (por %s) %s", action, getattr(user, "username", user), who, extra or "")

    email = (getattr(user, "email", "") or "").strip()
    key = TEMPLATE_FOR.get(action)
    if not key or not email:
        return False

    from apps.mailing.services import send_templated  # import perezoso (evita ciclos)
    context = {
        "usuario": getattr(user, "username", str(user)),
        "sitio": settings.SITE_NAME,
        "actor": who,
        "extra": extra or "",
    }
    res = send_templated(key, email, context)
    return bool(res and res.status == EmailMessageStatus.SENT)
