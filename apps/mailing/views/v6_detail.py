"""mailing · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.mailing.views.base import BaseContactMessage, BaseContactReply, BaseEmailLog, BaseEmailMessage, BaseEmailTemplate, BaseMailConfig
from core.shared.views.base import BaseAdminDetailView


# Gestión
# ==============================================================================


class ContactMessageDetailView(BaseContactMessage, BaseAdminDetailView):
    template_name = "mailing/detail/contact_message.html"   # datos + el HILO con responder inline
    """Detalle del mensaje de contacto = el HILO completo (mensaje + respuestas)
    con RESPONDER INLINE: se contesta aquí mismo, sin ir a la entidad Respuestas.
    Plantilla propia: mailing/detail/contact_message.html."""
    section_label = _("mailing")
    update_url = "panel:contact-message_update"
    delete_url = "panel:contact-message_delete"
    list_url = "panel:contact-message_list"
    toggle_url = "panel:contact-message_toggle"
    detail_fields = [(_("Nombre"), "name"), (_("Correo"), "email"), (_("Asunto"), "subject"),
                     (_("Estado"), "get_status_display"), (_("Recibido"), "created_at")]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["respuestas"] = self.object.replies.select_related("author").order_by("created_at")
        return ctx

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse
        from apps.mailing.models import ContactReply
        from apps.mailing.services import avisar_respuesta

        self.object = self.get_object()
        cuerpo = (request.POST.get("body") or "").strip()
        if not cuerpo:
            messages.error(request, "Escribe la respuesta antes de enviar.")
        else:
            r = ContactReply.objects.create(message=self.object, body=cuerpo,
                                            author=request.user, is_active=True)
            avisar_respuesta(r, request.build_absolute_uri(reverse("pages:my-messages")))
            messages.success(request, "Respuesta guardada y correo de aviso enviado.")
        return redirect(reverse("panel:contact-message_detail", args=[self.object.pk]))


class ContactReplyDetailView(BaseContactReply, BaseAdminDetailView):
    template_name = "mailing/detail/contact_reply.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    section_label = _("mailing")
    update_url = "panel:contact-reply_update"
    delete_url = "panel:contact-reply_delete"
    list_url = "panel:contact-reply_list"
    toggle_url = "panel:contact-reply_toggle"


class EmailMessageDetailView(BaseEmailMessage, BaseAdminDetailView):
    section_label = _("mailing")
    delete_url = "panel:email-message_delete"
    list_url = "panel:email-message_list"
    template_name = "admin_panel/correo_detail.html"   # añade el botón "Reenviar"
    detail_fields = [
        (_("Destinatario"), "to_email"), (_("Asunto"), "subject"), (_("Estado"), "get_status_display"),
        (_("Plantilla"), "template"), (_("Error"), "error"), (_("Cuerpo"), "body"), (_("Fecha"), "created_at"),
    ]


class EmailTemplateDetailView(BaseEmailTemplate, BaseAdminDetailView):
    template_name = "mailing/detail/email_template.html"   # datos + VISTA PREVIA (el cuerpo no va en facts)
    section_label = _("mailing")
    update_url = "panel:email-template_update"
    delete_url = "panel:email-template_delete"
    list_url = "panel:email-template_list"
    toggle_url = "panel:email-template_toggle"
    detail_fields = [
        (_("Nombre"), "name"), (_("Clave"), "key"), (_("Asunto"), "subject"),
        (_("Notas"), "description"), (_("Activa"), "is_active"),
    ]

    # Datos de ejemplo para renderizar el preview (cubren todas las variables).
    SAMPLE = {
        "usuario": "René", "nombre": "Juan Pérez", "email": "juan.perez@ejemplo.com",
        "asunto": "Consulta", "mensaje": "Hola, me interesa el sitio. ¿Cómo colaboro?",
        "actor": "admin", "enlace": "https://frikiverso.local/account/reset/…",
    }

    def get_context_data(self, **kwargs):
        from django.conf import settings
        from django.template import Context, Template
        ctx = super().get_context_data(**kwargs)
        sample = {**self.SAMPLE, "sitio": settings.SITE_NAME}
        tpl = self.object
        ctx["preview_subject"] = Template(tpl.subject).render(Context(sample))
        rendered = Template(tpl.body_html).render(Context(sample))
        # La MISMA maqueta que el envío (apps/mailing/layout.py), con la firma de la config: lo que se ve es lo que llega.
        from apps.mailing.layout import envolver, es_documento
        from apps.mailing.models import MailConfig
        firma = (MailConfig.load().signature or "").strip()
        ctx["preview_doc"] = rendered if es_documento(rendered) else envolver(rendered, settings.SITE_NAME, firma=firma)
        ctx["sample_vars"] = sample
        return ctx


class MailConfigDetailView(BaseMailConfig, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:mail-config_list"
    update_url = "panel:mail-config_update"
    delete_url = "panel:mail-config_delete"
    detail_fields = [('Enviar correos', 'send_email'), ('Firma', 'signature'), ('Remitente (from)', 'from_email'), ('Smtp host', 'smtp_host'), ('Smtp puerto', 'smtp_port'), ('Smtp usuario', 'smtp_user'), ('Smtp contraseña', 'smtp_password'), ('Usar tls', 'use_tls')]


class EmailLogDetailView(BaseEmailLog, BaseAdminDetailView):
    template_name = "mailing/detail/email_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    list_url = "panel:email-log_list"
    section_label = _("mailing")
