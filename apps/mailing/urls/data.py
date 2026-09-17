"""URLs de DATOS del panel de mailing: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.mailing import views as v


urlpatterns = [
    # ---------- contact-message · ContactMessage ----------
    path('contact-message/data/', v.ContactMessageDataView.as_view(), name='contact-message_data'),
    path('contact-message/data/<str:tipo>/<str:pk>/', v.ContactMessageDataView.as_view(), name='contact-message_data-by'),
    path('contact-message/select/', v.ContactMessageSelectView.as_view(), name='contact-message_select'),

    # ---------- contact-reply · ContactReply ----------
    path('contact-reply/data/', v.ContactReplyDataView.as_view(), name='contact-reply_data'),

    # ---------- email-message · EmailMessage ----------
    path('email-message/data/', v.EmailMessageDataView.as_view(), name='email-message_data'),
    path('email-message/data/<str:tipo>/<str:pk>/', v.EmailMessageDataView.as_view(), name='email-message_data-by'),

    # ---------- email-template · EmailTemplate ----------
    path('email-template/data/', v.EmailTemplateDataView.as_view(), name='email-template_data'),

    # ---------- mail-config · MailConfig ----------
    path('mail-config/data/', v.MailConfigDataView.as_view(), name='mail-config_data'),

    # ---------- email-log · EmailLog ----------
    path('email-log/data/', v.EmailLogDataView.as_view(), name='email-log_data'),
]
