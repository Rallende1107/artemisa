"""mailing · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from apps.mailing.models import EmailMessage, MailConfig
from core.shared.models.choices import EmailMessageStatus
from core.shared.views.base import BaseHomeView


# ==============================================================================
# Gestión
# ==============================================================================


class MailingHomeView(BaseHomeView):
    title = "Correo"
    active_entity = "mailing-home"
    background_image = "bg-mailing-home"
    background_fallback = "bg-mailing-home"   # respaldo si falta la imagen
    template_name = "mailing/home.html"
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Configuración"), [
            ("email-template", _("Plantillas de correo"), '<i class="bi bi-file-earmark-text"></i>', "bg-mailing-email-template"),
            ("panel:mail-config", _("Configuración"), '<i class="bi bi-gear"></i>', "bg-mailing-mail-config"),
        ]),
        (_("Envíos"), [
            ("email-message", _("Correos"), '<i class="bi bi-envelope-check"></i>', "bg-mailing-email-message"),
        ]),
        (_("Contacto"), [
            ("contact-message", _("Mensajes de contacto"), '<i class="bi bi-inbox"></i>', "bg-mailing-contact-message"),
            ("contact-reply", _("Respuestas de contacto"), '<i class="bi bi-reply"></i>', "bg-mailing-contact-reply"),
        ]),
        (_("Registro"), [
            ("email-log", _("Log de correo"), '<i class="bi bi-journal-text"></i>', "bg-mailing-log"),
        ]),
    ]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        counts = dict(EmailMessage.objects.values_list("status").annotate(n=Count("id")))
        ctx["counts"] = {
            "sent": counts.get(EmailMessageStatus.SENT, 0), "queued": counts.get(EmailMessageStatus.QUEUED, 0),
            "error": counts.get(EmailMessageStatus.ERROR, 0), "skipped": counts.get(EmailMessageStatus.SKIPPED, 0),
        }
        ctx["pending"] = counts.get(EmailMessageStatus.QUEUED, 0) + counts.get(EmailMessageStatus.ERROR, 0)
        ctx["cfg"] = MailConfig.load()
        return ctx
