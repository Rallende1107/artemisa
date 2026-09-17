"""Rutas del PANEL de la sección Páginas (namespace `panel`, las incluye
core/panel_urls.py): home + CRUD de las secciones de Nosotros, Términos y Privacidad.
Las rutas PÚBLICAS de la app están en urls/public.py.

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.pages import views as v
from core.views import AdminToggleView


urlpatterns = [
    path('', include('apps.pages.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('pages/', v.PagesHomeView.as_view(), name='pages-home'),

    # ---------- about-section · AboutSection ----------
    path('about-section/', v.AboutSectionListView.as_view(), name='about-section_list'),
    path('about-section/create/', v.AboutSectionCreateView.as_view(), name='about-section_create'),
    path('about-section/<int:pk>/', v.AboutSectionDetailView.as_view(), name='about-section_detail'),
    path('about-section/<int:pk>/update/', v.AboutSectionUpdateView.as_view(), name='about-section_update'),
    path('about-section/<int:pk>/delete/', v.AboutSectionDeleteView.as_view(), name='about-section_delete'),
    path('about-section/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AboutSectionListView.model, entity='about-section', label='sección de nosotros', namespace='panel'), name='about-section_toggle'),

    # ---------- privacy-section · PrivacySection ----------
    path('privacy-section/', v.PrivacySectionListView.as_view(), name='privacy-section_list'),
    path('privacy-section/create/', v.PrivacySectionCreateView.as_view(), name='privacy-section_create'),
    path('privacy-section/<int:pk>/', v.PrivacySectionDetailView.as_view(), name='privacy-section_detail'),
    path('privacy-section/<int:pk>/update/', v.PrivacySectionUpdateView.as_view(), name='privacy-section_update'),
    path('privacy-section/<int:pk>/delete/', v.PrivacySectionDeleteView.as_view(), name='privacy-section_delete'),
    path('privacy-section/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.PrivacySectionListView.model, entity='privacy-section', label='sección de privacidad', namespace='panel'), name='privacy-section_toggle'),

    # ---------- terms-section · TermsSection ----------
    path('terms-section/', v.TermsSectionListView.as_view(), name='terms-section_list'),
    path('terms-section/create/', v.TermsSectionCreateView.as_view(), name='terms-section_create'),
    path('terms-section/<int:pk>/', v.TermsSectionDetailView.as_view(), name='terms-section_detail'),
    path('terms-section/<int:pk>/update/', v.TermsSectionUpdateView.as_view(), name='terms-section_update'),
    path('terms-section/<int:pk>/delete/', v.TermsSectionDeleteView.as_view(), name='terms-section_delete'),
    path('terms-section/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.TermsSectionListView.model, entity='terms-section', label='sección de términos', namespace='panel'), name='terms-section_toggle'),

    # ---------- pages-log · PagesLog ----------
    path('pages-log/', v.PagesLogListView.as_view(), name='pages-log_list'),
    path('pages-log/create/', v.PagesLogCreateView.as_view(), name='pages-log_create'),
    path('pages-log/<int:pk>/', v.PagesLogDetailView.as_view(), name='pages-log_detail'),
    path('pages-log/<int:pk>/update/', v.PagesLogUpdateView.as_view(), name='pages-log_update'),
    path('pages-log/<int:pk>/delete/', v.PagesLogDeleteView.as_view(), name='pages-log_delete'),
]
