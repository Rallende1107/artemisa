"""Vistas de pages como PAQUETE plano (estilo Poseidón): base.py (mixins _Base<Modelo>, mapas _BaseXBy y helpers) y un
archivo por rol con las DOS caras, gestión y público. Este __init__ SOLO re-exporta: `from apps.pages import views`
(urls/public.py) y `views as v` (urls/panel.py, urls/data.py) siguen funcionando y cada clase tiene UN archivo dueño."""
from apps.pages.views.v1_home import PagesHomeView, IndexView  # noqa: F401,E402
from apps.pages.views.v3_data import AboutSectionDataView, AboutSectionSelectView, TermsSectionDataView, TermsSectionSelectView, PrivacySectionDataView, PrivacySectionSelectView, PagesLogDataView, LEGAL_COLUMNS  # noqa: F401,E402
from apps.pages.views.v4_write import AboutSectionCreateView, AboutSectionUpdateView, AboutSectionDeleteView, TermsSectionCreateView, TermsSectionUpdateView, TermsSectionDeleteView, PrivacySectionCreateView, PrivacySectionUpdateView, PrivacySectionDeleteView, PagesLogCreateView, PagesLogUpdateView, PagesLogDeleteView  # noqa: F401,E402
from apps.pages.views.v5_list import AboutSectionListView, TermsSectionListView, PrivacySectionListView, PagesLogListView  # noqa: F401,E402
from apps.pages.views.v6_detail import AboutSectionDetailView, TermsSectionDetailView, PrivacySectionDetailView, PagesLogDetailView  # noqa: F401,E402
from apps.pages.views.v8_actions import BasePaginaInformativa, AboutView, ContactView, GlobalSearchView, MyMessagesView, TermsView, PrivacyView, BaseErrorView, BaseErrorStandaloneView, Error404View, Error403View, Error403CsrfView, Error500View, Error400View, error_404, error_500, error_403, error_400, csrf_failure_view  # noqa: F401,E402
