"""BASE de la sección Correo del panel: config por entidad + columnas.

La clase privada `_Entidad` es la ÚNICA fuente de config compartida de cada
entidad (modelo, slug, etiquetas, fondo). Las vistas de los módulos vN_*.py
la heredan como PRIMER mixin — estilo Poseidon.
"""
from django.utils.translation import gettext_lazy as _

from apps.mailing.models import ContactMessage, ContactReply, EmailLog, EmailMessage, EmailTemplate, MailConfig


# "Activo" (is_active) se declara aquí como cualquier columna: nadie la añade por detrás.


class _Mailing:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-mailing-home"   # respaldo si falta la imagen
    section_url = "panel:mailing-home"
    section_label = _("Mailing")


class BaseContactMessage(_Mailing):
    # El contacto es correo → gestión Y modelo viven aquí (movidos desde system).
    model = ContactMessage
    entity = "contact-message"
    label = _("mensaje")
    label_plural = _("mensajes de contacto")
    background_image = "bg-mailing-contact-message"


class BaseContactMessageContext(BaseContactMessage):
    """Mapa «por» de mensajes de contacto: tipo → (campo, título, fondo). `status` acota por el CHOICE del campo `status`
    (valor en la URL, validado contra sus choices); lo comparten la Data (filtra) y la ListBy (título, fondo)."""
    filter_config = {
        "status": ("status", _("Mensajes de contacto · {valor}"), "bg-mailing-contact-message"),
    }


class BaseContactReply(_Mailing):
    model = ContactReply
    entity = "contact-reply"
    label = _("respuesta")
    label_plural = _("respuestas de contacto")
    background_image = "bg-mailing-contact-reply"


class BaseEmailMessage(_Mailing):
    model = EmailMessage
    entity = "email-message"
    label = _("correo")
    label_plural = _("correos")
    background_image = "bg-mailing-email-message"


class BaseEmailMessageContext(BaseEmailMessage):
    """Mapa «por» de correos: tipo → (campo, título, fondo). `status` acota por el CHOICE del campo `status`
    (valor en la URL, validado contra sus choices); lo comparten la Data (filtra) y la ListBy (título, fondo)."""
    filter_config = {
        "status": ("status", _("Correos · {valor}"), "bg-mailing-email-message"),
    }


class BaseEmailTemplate(_Mailing):
    model = EmailTemplate
    entity = "email-template"
    label = _("plantilla de correo")
    label_plural = _("plantillas de correo")
    background_image = "bg-mailing-email-template"


class BaseMailConfig(_Mailing):
    model = MailConfig
    entity = "mail-config"
    label = _("configuración de correo")
    label_plural = _("configuración de correo")
    background_image = "bg-mailing-mail-config"


class BaseEmailLog(_Mailing):
    model = EmailLog
    entity = "email-log"
    label = _("log de correo")
    label_plural = _("log de correo")
    background_image = "bg-mailing-log"
