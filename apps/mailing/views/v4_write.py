"""mailing · ESCRITURA de gestión: crear, editar y eliminar."""
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from apps.mailing import forms as f
from apps.mailing.models import MailConfig
from apps.mailing.views.base import BaseContactMessage, BaseContactReply, BaseEmailLog, BaseEmailMessage, BaseEmailTemplate, BaseMailConfig
from core.shared.views.base import BaseCreate, BaseDelete, BasePage, BaseSoftDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class ContactMessageUpdateView(BaseContactMessage, BaseUpdate):
    # Django core
    form_class = f.ContactMessageForm
    list_url = "panel:contact-message_list"
    success_url = "panel:contact-message_list"
    cancel_url = "panel:contact-message_list"
    # Navegación
    section_label = _("mailing")
    # UX
    success_message = _("Mensaje «%(obj)s» actualizado.")
    title = _("Editar mensaje")


class ContactMessageDeleteView(BaseContactMessage, BaseSoftDelete):
    list_url = "panel:contact-message_list"
    success_url = "panel:contact-message_list"
    cancel_url = "panel:contact-message_list"
    success_message = _("Mensaje «%(obj)s» eliminado.")
    title = _("Eliminar mensaje")


class ContactMessageCreateView(BaseContactMessage, BaseCreate):
    form_class = f.ContactMessageForm
    list_url = "panel:contact-message_list"
    success_url = "panel:contact-message_list"
    cancel_url = "panel:contact-message_list"
    success_message = _("Mensaje de contacto «%(obj)s» creado.")
    title = _("Crear mensaje de contacto")


class ContactReplyCreateView(BaseContactReply, BaseCreate):
    # Django core
    form_class = f.ContactReplyForm
    list_url = "panel:contact-reply_list"
    success_url = "panel:contact-reply_list"
    cancel_url = "panel:contact-reply_list"
    # Navegación
    section_label = _("mailing")
    # UX
    success_message = _("Respuesta a «%(obj)s» creada.")
    title = _("Crear respuesta")

    def form_valid(self, form):
        # El autor es quien responde desde el panel.
        form.instance.author = self.request.user
        respuesta = super().form_valid(form)
        # AVISO al usuario: «te respondimos», con enlace a Mis mensajes.
        from django.urls import reverse
        from apps.mailing.services import avisar_respuesta
        avisar_respuesta(form.instance,
                         self.request.build_absolute_uri(reverse("pages:my-messages")))
        return respuesta


class ContactReplyUpdateView(BaseContactReply, BaseUpdate):
    # Django core
    form_class = f.ContactReplyForm
    list_url = "panel:contact-reply_list"
    success_url = "panel:contact-reply_list"
    cancel_url = "panel:contact-reply_list"
    # Navegación
    section_label = _("mailing")
    # UX
    success_message = _("Respuesta «%(obj)s» actualizada.")
    title = _("Editar respuesta")


class ContactReplyDeleteView(BaseContactReply, BaseDelete):
    list_url = "panel:contact-reply_list"
    success_url = "panel:contact-reply_list"
    cancel_url = "panel:contact-reply_list"
    success_message = _("Respuesta «%(obj)s» eliminada.")
    title = _("Eliminar respuesta")


class MailConfigUpdateView(BasePage, UpdateView):
    """Config MÍNIMA: el interruptor de envío + la firma al pie. (SMTP → .env)."""
    model = MailConfig
    form_class = f.MailConfigForm
    template_name = "mailing/config.html"
    title = _("Configuración")
    active_entity = "mailing-config"
    background_image = "bg-mailing-mail-config"   # registro unico: pagina propia, como un home
    background_fallback = "bg-mailing-home"   # respaldo si falta la imagen

    def get_object(self, queryset=None):
        return MailConfig.load()

    def get_success_url(self):
        messages.success(self.request, "Configuración guardada.")
        return reverse("panel:mail-config")


class EmailMessageDeleteView(BaseEmailMessage, BaseDelete):
    list_url = "panel:email-message_list"
    success_url = "panel:email-message_list"
    cancel_url = "panel:email-message_list"
    success_message = _("Correo «%(obj)s» eliminado.")
    title = _("Eliminar correo")
    pass   # permitir limpiar el historial


class EmailMessageCreateView(BaseEmailMessage, BaseCreate):
    form_class = f.EmailMessageForm
    list_url = "panel:email-message_list"
    success_url = "panel:email-message_list"
    cancel_url = "panel:email-message_list"
    success_message = _("Correo «%(obj)s» creado.")
    title = _("Crear correo")


class EmailMessageUpdateView(BaseEmailMessage, BaseUpdate):
    form_class = f.EmailMessageForm
    list_url = "panel:email-message_list"
    success_url = "panel:email-message_list"
    cancel_url = "panel:email-message_list"
    success_message = _("Correo «%(obj)s» actualizado.")
    title = _("Editar correo")


class EmailTemplateCreateView(BaseEmailTemplate, BaseCreate):
    # Django core
    form_class = f.EmailTemplateForm
    form_template = "mailing/form/email_template.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:email-template_list"
    success_url = "panel:email-template_list"
    cancel_url = "panel:email-template_list"
    # Navegación
    section_label = _("mailing")
    # UX
    success_message = _("Plantilla de correo «%(obj)s» creada.")
    title = _("Crear plantilla de correo")


class EmailTemplateUpdateView(BaseEmailTemplate, BaseUpdate):
    # Django core
    form_class = f.EmailTemplateForm
    form_template = "mailing/form/email_template.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:email-template_list"
    success_url = "panel:email-template_list"
    cancel_url = "panel:email-template_list"
    # Navegación
    section_label = _("mailing")
    # UX
    success_message = _("Plantilla de correo «%(obj)s» actualizada.")
    title = _("Editar plantilla de correo")


class EmailTemplateDeleteView(BaseEmailTemplate, BaseDelete):
    list_url = "panel:email-template_list"
    success_url = "panel:email-template_list"
    cancel_url = "panel:email-template_list"
    success_message = _("Plantilla de correo «%(obj)s» eliminada.")
    title = _("Eliminar plantilla de correo")


class MailConfigCreateView(BaseMailConfig, BaseCreate):
    form_class = f.MailConfigForm
    list_url = "panel:mail-config_list"
    success_url = "panel:mail-config_list"
    cancel_url = "panel:mail-config_list"
    success_message = _("Configuración de correo «%(obj)s» creado.")
    title = _("Crear configuración de correo")


class MailConfigDeleteView(BaseMailConfig, BaseDelete):
    list_url = "panel:mail-config_list"
    success_url = "panel:mail-config_list"
    cancel_url = "panel:mail-config_list"
    success_message = _("Configuración de correo «%(obj)s» eliminado.")
    title = _("Eliminar configuración de correo")


class EmailLogCreateView(BaseEmailLog, BaseCreate):
    form_class = f.EmailLogForm
    form_template = "mailing/form/email_log.html"
    list_url = "panel:email-log_list"
    success_url = "panel:email-log_list"
    cancel_url = "panel:email-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class EmailLogUpdateView(BaseEmailLog, BaseUpdate):
    form_class = f.EmailLogForm
    form_template = "mailing/form/email_log.html"
    list_url = "panel:email-log_list"
    success_url = "panel:email-log_list"
    cancel_url = "panel:email-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class EmailLogDeleteView(BaseEmailLog, BaseDelete):
    list_url = "panel:email-log_list"
    success_url = "panel:email-log_list"
    cancel_url = "panel:email-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
