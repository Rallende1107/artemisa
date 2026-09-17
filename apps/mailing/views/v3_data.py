"""mailing · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.mailing.models import ContactMessage, ContactReply, EmailLog, EmailMessage, EmailTemplate, MailConfig
from apps.mailing.views.base import BaseContactMessage, BaseContactMessageContext, BaseContactReply, BaseEmailLog, BaseEmailMessageContext, BaseEmailTemplate, BaseMailConfig
from apps.mailing.views.v2_filters import ContactMessageFilters, EmailMessageFilters
from core.shared.models.choices import EmailMessageStatus
from core.shared.views.base import AdminDataView, BaseSelectView
from core.shared.views.filters import LogFilters
from core.utils.views_base import cell


# ==============================================================================
# Gestión
# ==============================================================================

TPL_COLUMNS = [("Nombre", "name"), ("Clave", "key"), ("Asunto", "subject"), ("Activo", "is_active")]
LOG_COLUMNS = [("Destinatario", "to_email"), ("Asunto", "subject"), ("Estado", "get_status_display"), ("Fecha", "created_at")]
CONTACT_COLUMNS = [("Nombre", "name"), ("Correo", "email"), ("Asunto", "subject"),
                   ("Estado", "get_status_display"), ("Recibido", "created_at"), ("Activo", "is_active")]
REPLY_COLUMNS = [("Mensaje", "message"), ("Autor", "author"), ("Fecha", "created_at"), ("Activo", "is_active")]


# Endpoints de las bandejas FIJAS: mismo filtro que su lista.


class ContactMessageDataView(BaseContactMessageContext, AdminDataView):
    columns = CONTACT_COLUMNS
    filters = ContactMessageFilters

    def get(self, request, tipo=None, pk=None):
        qs = ContactMessage.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["name", "email", "subject", "message"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "email"),
                "c2": cell(obj, "subject"),
                "c3": cell(obj, "get_status_display"),
                "c4": cell(obj, "created_at"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ContactMessageSelectView(BaseContactMessage, BaseSelectView):
    search_fields = ['name', 'email', 'subject', 'message']


class ContactReplyDataView(BaseContactReply, AdminDataView):
    columns = REPLY_COLUMNS

    def get(self, request, tipo=None, pk=None):
        qs = ContactReply.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["body", "message__name", "message__email", "message__subject"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "message", truncar=120),
                "c1": cell(obj, "author"),
                "c2": cell(obj, "created_at"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class EmailMessageDataView(BaseEmailMessageContext, AdminDataView):
    columns = LOG_COLUMNS
    filters = EmailMessageFilters

    def get(self, request, tipo=None, pk=None):
        qs = EmailMessage.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["to_email", "subject", "template__key", "template__name", "error"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "to_email"),
                "c1": cell(obj, "subject"),
                "c2": cell(obj, "get_status_display"),
                "c3": cell(obj, "created_at"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

    def extra_row_actions(self, obj, request):
        """«Reenviar» en la fila de todo correo que NO salió (en cola, error, omitido).
        Al reenviarse pasa a «enviado» y desaparece de las listas de pendientes."""
        if obj.status not in (EmailMessageStatus.QUEUED, EmailMessageStatus.ERROR, EmailMessageStatus.SKIPPED):
            return []
        url = reverse("panel:email-message_resend", args=[obj.pk])
        return [f'<a role="menuitem" class="js-post" href="{url}" '
                f'data-confirm="¿Reenviar el correo a «{escape(obj.to_email)}»?">'
                f'<i class="bi bi-send-check ic"></i> Reenviar</a>']


class EmailTemplateDataView(BaseEmailTemplate, AdminDataView):
    columns = TPL_COLUMNS

    def get(self, request, tipo=None, pk=None):
        qs = EmailTemplate.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["name", "key", "subject"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "key"),
                "c2": cell(obj, "subject"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MailConfigDataView(BaseMailConfig, AdminDataView):
    columns = [('Enviar correos', 'send_email'), ('Firma', 'signature'), ('Remitente (from)', 'from_email'), ('Smtp host', 'smtp_host'), ('Smtp puerto', 'smtp_port')]

    def get(self, request, tipo=None, pk=None):
        qs = MailConfig.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['signature', 'from_email', 'smtp_host'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "send_email"),
                "c1": cell(obj, "signature"),
                "c2": cell(obj, "from_email"),
                "c3": cell(obj, "smtp_host"),
                "c4": cell(obj, "smtp_port"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class EmailLogDataView(BaseEmailLog, AdminDataView):
    columns = [(_("Nivel"), "level"), (_("Proceso"), "process"), (_("Mensaje"), "message"), (_("Momento"), "timestamp")]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = EmailLog.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["process", "message", "email__to_email"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "level"),
                "c1": cell(obj, "process"),
                "c2": cell(obj, "message", truncar=120),
                "c3": cell(obj, "timestamp"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)
