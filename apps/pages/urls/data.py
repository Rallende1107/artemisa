"""URLs de DATOS del panel de pages: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.pages import views as v


urlpatterns = [
    # ---------- about-section · AboutSection ----------
    path('about-section/data/', v.AboutSectionDataView.as_view(), name='about-section_data'),
    path('about-section/select/', v.AboutSectionSelectView.as_view(), name='about-section_select'),

    # ---------- privacy-section · PrivacySection ----------
    path('privacy-section/data/', v.PrivacySectionDataView.as_view(), name='privacy-section_data'),
    path('privacy-section/select/', v.PrivacySectionSelectView.as_view(), name='privacy-section_select'),

    # ---------- terms-section · TermsSection ----------
    path('terms-section/data/', v.TermsSectionDataView.as_view(), name='terms-section_data'),
    path('terms-section/select/', v.TermsSectionSelectView.as_view(), name='terms-section_select'),

    # ---------- pages-log · PagesLog ----------
    path('pages-log/data/', v.PagesLogDataView.as_view(), name='pages-log_data'),
]
