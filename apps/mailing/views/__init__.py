"""Vistas de mailing como PAQUETE plano (estilo Poseidón): base.py (mixins _Base<Modelo>, mapas _BaseXBy y helpers) y un
archivo por rol con las DOS caras, gestión y público. Este __init__ SOLO re-exporta: `from apps.mailing import views`
(urls/public.py) y `views as v` (urls/panel.py, urls/data.py) siguen funcionando y cada clase tiene UN archivo dueño."""
from apps.mailing.views.v1_home import MailingHomeView  # noqa: F401,E402
from apps.mailing.views.v2_filters import EmailMessageFilters, ContactMessageFilters  # noqa: F401,E402
from apps.mailing.views.v3_data import EmailTemplateDataView, EmailMessageDataView, ContactMessageDataView, ContactMessageSelectView, ContactReplyDataView, EmailLogDataView, MailConfigDataView, TPL_COLUMNS, LOG_COLUMNS, CONTACT_COLUMNS, REPLY_COLUMNS  # noqa: F401,E402
from apps.mailing.views.v4_write import EmailTemplateCreateView, EmailTemplateUpdateView, EmailTemplateDeleteView, ContactReplyCreateView, ContactReplyUpdateView, ContactReplyDeleteView, ContactMessageUpdateView, ContactMessageDeleteView, MailConfigUpdateView, EmailMessageDeleteView, EmailLogCreateView, EmailLogUpdateView, EmailLogDeleteView, ContactMessageCreateView, EmailMessageCreateView, EmailMessageUpdateView, MailConfigCreateView, MailConfigDeleteView  # noqa: F401,E402
from apps.mailing.views.v5_list import EmailTemplateListView, EmailMessageListView, ContactMessageListView, ContactReplyListView, EmailLogListView, MailConfigListView, EmailMessageListByView, ContactMessageListByView  # noqa: F401,E402
from apps.mailing.views.v6_detail import EmailTemplateDetailView, EmailMessageDetailView, ContactMessageDetailView, ContactReplyDetailView, EmailLogDetailView, MailConfigDetailView  # noqa: F401,E402
from apps.mailing.views.v8_actions import EmailResendView, EmailResendPendingView, MailToggleView  # noqa: F401,E402
