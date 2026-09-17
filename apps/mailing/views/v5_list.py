"""mailing · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.mailing.views.base import BaseContactMessage, BaseContactMessageContext, BaseContactReply, BaseEmailLog, BaseEmailMessage, BaseEmailMessageContext, BaseEmailTemplate, BaseMailConfig
from core.shared.views.base import AdminListByView, AdminListView


# Gestión
# ==============================================================================


# Cada una declara su filtro, su slug para el sidebar y su fondo (con respaldo en el de correo).


class ContactMessageListView(BaseContactMessage, AdminListView):
    home_url = "panel:mailing-home"
    data_url = "panel:contact-message_data"
    title = _("Lista de mensajes de contacto")


class ContactMessageListByView(BaseContactMessageContext, AdminListByView):
    """Lista acotada por el mapa (`/contact-message/<tipo>/<valor>/`): la alimenta ContactMessageDataView con `/data/<tipo>/<valor>/`."""
    home_url = "panel:mailing-home"
    data_url = "panel:contact-message_data-by"
    full_list_url = "panel:contact-message_list"
    by_url = "panel:contact-message_by"


class ContactReplyListView(BaseContactReply, AdminListView):
    home_url = "panel:mailing-home"
    data_url = "panel:contact-reply_data"
    create_url = "panel:contact-reply_create"
    title = _("Lista de respuestas de contacto")


class EmailMessageListView(BaseEmailMessage, AdminListView):
    home_url = "panel:mailing-home"
    data_url = "panel:email-message_data"
    title = _("Lista de correos")


class EmailMessageListByView(BaseEmailMessageContext, AdminListByView):
    """Lista acotada por el mapa (`/email-message/<tipo>/<valor>/`): la alimenta EmailMessageDataView con `/data/<tipo>/<valor>/`."""
    home_url = "panel:mailing-home"
    data_url = "panel:email-message_data-by"
    full_list_url = "panel:email-message_list"
    by_url = "panel:email-message_by"


class EmailTemplateListView(BaseEmailTemplate, AdminListView):
    home_url = "panel:mailing-home"
    data_url = "panel:email-template_data"
    create_url = "panel:email-template_create"
    title = _("Lista de plantillas de correo")


class MailConfigListView(BaseMailConfig, AdminListView):
    home_url = "panel:mailing-home"
    data_url = "panel:mail-config_data"
    create_url = "panel:mail-config_create"
    title = _("Lista de configuración de correo")


class EmailLogListView(BaseEmailLog, AdminListView):
    home_url = "panel:mailing-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:email-log_data"
    create_url = "panel:email-log_create"
    title = _("Lista de log de correo")
