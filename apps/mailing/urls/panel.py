"""URLs del panel para mailing (se montan en el namespace `panel`).

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.mailing import views as v
from core.views import AdminToggleView


urlpatterns = [
    path('', include('apps.mailing.urls.data')),        # data · data-by · select (DataTables y AJAX)

    # ---------- home de sección ----------
    path('mailing/', v.MailingHomeView.as_view(), name='mailing-home'),

    # ---------- contact-message · ContactMessage ----------
    path('contact-message/', v.ContactMessageListView.as_view(), name='contact-message_list'),
    path('contact-message/create/', v.ContactMessageCreateView.as_view(), name='contact-message_create'),
    path('contact-message/<int:pk>/', v.ContactMessageDetailView.as_view(), name='contact-message_detail'),
    path('contact-message/<int:pk>/update/', v.ContactMessageUpdateView.as_view(), name='contact-message_update'),
    path('contact-message/<int:pk>/delete/', v.ContactMessageDeleteView.as_view(), name='contact-message_delete'),
    path('contact-message/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ContactMessageListView.model, entity='contact-message', label='mensaje', namespace='panel'), name='contact-message_toggle'),
    path('contact-message/<str:tipo>/<str:pk>/', v.ContactMessageListByView.as_view(), name='contact-message_by'),

    # ---------- contact-reply · ContactReply ----------
    path('contact-reply/', v.ContactReplyListView.as_view(), name='contact-reply_list'),
    path('contact-reply/create/', v.ContactReplyCreateView.as_view(), name='contact-reply_create'),
    path('contact-reply/<int:pk>/', v.ContactReplyDetailView.as_view(), name='contact-reply_detail'),
    path('contact-reply/<int:pk>/update/', v.ContactReplyUpdateView.as_view(), name='contact-reply_update'),
    path('contact-reply/<int:pk>/delete/', v.ContactReplyDeleteView.as_view(), name='contact-reply_delete'),
    path('contact-reply/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ContactReplyListView.model, entity='contact-reply', label='respuesta', namespace='panel'), name='contact-reply_toggle'),

    # ---------- email-message · EmailMessage ----------
    path('email-message/', v.EmailMessageListView.as_view(), name='email-message_list'),
    path('email-message/create/', v.EmailMessageCreateView.as_view(), name='email-message_create'),
    path('email-message/<int:pk>/', v.EmailMessageDetailView.as_view(), name='email-message_detail'),
    path('email-message/<int:pk>/update/', v.EmailMessageUpdateView.as_view(), name='email-message_update'),
    path('email-message/<int:pk>/delete/', v.EmailMessageDeleteView.as_view(), name='email-message_delete'),
    path('email-message/<int:pk>/reenviar/', v.EmailResendView.as_view(), name='email-message_resend'),
    path('email-message/<str:tipo>/<str:pk>/', v.EmailMessageListByView.as_view(), name='email-message_by'),

    # ---------- email-template · EmailTemplate ----------
    path('email-template/', v.EmailTemplateListView.as_view(), name='email-template_list'),
    path('email-template/create/', v.EmailTemplateCreateView.as_view(), name='email-template_create'),
    path('email-template/reenviar-pendientes/', v.EmailResendPendingView.as_view(), name='email-message_resend_pending'),
    path('email-template/<int:pk>/', v.EmailTemplateDetailView.as_view(), name='email-template_detail'),
    path('email-template/<int:pk>/update/', v.EmailTemplateUpdateView.as_view(), name='email-template_update'),
    path('email-template/<int:pk>/delete/', v.EmailTemplateDeleteView.as_view(), name='email-template_delete'),
    path('email-template/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.EmailTemplateListView.model, entity='email-template', label='plantilla', namespace='panel'), name='email-template_toggle'),

    # ---------- mail-config · MailConfig ----------
    path('mail-config/', v.MailConfigListView.as_view(), name='mail-config_list'),
    path('mail-config/create/', v.MailConfigCreateView.as_view(), name='mail-config_create'),
    path('mail-config/<int:pk>/', v.MailConfigDetailView.as_view(), name='mail-config_detail'),
    path('mail-config/<int:pk>/delete/', v.MailConfigDeleteView.as_view(), name='mail-config_delete'),
    path('mail-config/config/toggle/', v.MailToggleView.as_view(), name='mail-config_toggle'),

    # ---------- configuración de correo (SMTP + flag) ----------
    path('mailing/config/', v.MailConfigUpdateView.as_view(), name='mail-config'),

    # ---------- email-log · EmailLog ----------
    path('email-log/', v.EmailLogListView.as_view(), name='email-log_list'),
    path('email-log/create/', v.EmailLogCreateView.as_view(), name='email-log_create'),
    path('email-log/<int:pk>/', v.EmailLogDetailView.as_view(), name='email-log_detail'),
    path('email-log/<int:pk>/update/', v.EmailLogUpdateView.as_view(), name='email-log_update'),
    path('email-log/<int:pk>/delete/', v.EmailLogDeleteView.as_view(), name='email-log_delete'),
]
