"""URLs del panel para common (sección «General»): home + CRUD por entidad.

Rutas EXPLÍCITAS (estilo Hades): una `path()` por vista, con su `name=` editable.
Sin funciones que las generen. Se montan en el namespace `panel` desde core/panel_urls.py.

Rutas por entidad: list · [nuevo] · data (DataTables) · select (AJAX FK/M2M) ·
detail · editar · eliminar · accion (toggle is_active/is_staff/...).

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.catalogs import views as v
from core.views import AdminToggleView


urlpatterns = [
    path('', include('apps.catalogs.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('catalogs/', v.CatalogsHomeView.as_view(), name='catalogs-home'),

    # ---------- country · Country ----------
    path('country/', v.CountryListView.as_view(), name='country_list'),
    path('country/create/', v.CountryCreateView.as_view(), name='country_create'),
    path('country/<int:pk>/', v.CountryDetailView.as_view(), name='country_detail'),
    path('country/<int:pk>/update/', v.CountryUpdateView.as_view(), name='country_update'),
    path('country/<int:pk>/delete/', v.CountryDeleteView.as_view(), name='country_delete'),
    path('country/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CountryListView.model, entity='country', label='país', namespace='panel'), name='country_toggle'),

    # ---------- external-source · ExternalSource ----------
    path('external-source/', v.ExternalSourceListView.as_view(), name='external-source_list'),
    path('external-source/create/', v.ExternalSourceCreateView.as_view(), name='external-source_create'),
    path('external-source/<int:pk>/', v.ExternalSourceDetailView.as_view(), name='external-source_detail'),
    path('external-source/<int:pk>/update/', v.ExternalSourceUpdateView.as_view(), name='external-source_update'),
    path('external-source/<int:pk>/delete/', v.ExternalSourceDeleteView.as_view(), name='external-source_delete'),
    path('external-source/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ExternalSourceListView.model, entity='external-source', label='fuente externa', namespace='panel'), name='external-source_toggle'),
    path('external-source/<str:tipo>/<str:pk>/', v.ExternalSourceListByView.as_view(), name='external-source_by'),

    # ---------- format · Format ----------
    path('format/', v.FormatListView.as_view(), name='format_list'),
    path('format/create/', v.FormatCreateView.as_view(), name='format_create'),
    path('format/<int:pk>/', v.FormatDetailView.as_view(), name='format_detail'),
    path('format/<int:pk>/update/', v.FormatUpdateView.as_view(), name='format_update'),
    path('format/<int:pk>/delete/', v.FormatDeleteView.as_view(), name='format_delete'),
    path('format/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.FormatListView.model, entity='format', label='formato', namespace='panel'), name='format_toggle'),

    # ---------- language · Language ----------
    path('language/', v.LanguageListView.as_view(), name='language_list'),
    path('language/create/', v.LanguageCreateView.as_view(), name='language_create'),
    path('language/<int:pk>/', v.LanguageDetailView.as_view(), name='language_detail'),
    path('language/<int:pk>/update/', v.LanguageUpdateView.as_view(), name='language_update'),
    path('language/<int:pk>/delete/', v.LanguageDeleteView.as_view(), name='language_delete'),
    path('language/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.LanguageListView.model, entity='language', label='idioma', namespace='panel'), name='language_toggle'),

    # ---------- quality · Quality ----------
    path('quality/', v.QualityListView.as_view(), name='quality_list'),
    path('quality/create/', v.QualityCreateView.as_view(), name='quality_create'),
    path('quality/<int:pk>/', v.QualityDetailView.as_view(), name='quality_detail'),
    path('quality/<int:pk>/update/', v.QualityUpdateView.as_view(), name='quality_update'),
    path('quality/<int:pk>/delete/', v.QualityDeleteView.as_view(), name='quality_delete'),
    path('quality/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.QualityListView.model, entity='quality', label='calidad', namespace='panel'), name='quality_toggle'),

    # ---------- relation-type · RelationType ----------
    path('relation-type/', v.RelationTypeListView.as_view(), name='relation-type_list'),
    path('relation-type/create/', v.RelationTypeCreateView.as_view(), name='relation-type_create'),
    path('relation-type/<int:pk>/', v.RelationTypeDetailView.as_view(), name='relation-type_detail'),
    path('relation-type/<int:pk>/update/', v.RelationTypeUpdateView.as_view(), name='relation-type_update'),
    path('relation-type/<int:pk>/delete/', v.RelationTypeDeleteView.as_view(), name='relation-type_delete'),
    path('relation-type/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RelationTypeListView.model, entity='relation-type', label='tipo de relación', namespace='panel'), name='relation-type_toggle'),

    # ---------- website · Website ----------
    path('website/', v.WebsiteListView.as_view(), name='website_list'),
    path('website/create/', v.WebsiteCreateView.as_view(), name='website_create'),
    path('website/<int:pk>/', v.WebsiteDetailView.as_view(), name='website_detail'),
    path('website/<int:pk>/update/', v.WebsiteUpdateView.as_view(), name='website_update'),
    path('website/<int:pk>/delete/', v.WebsiteDeleteView.as_view(), name='website_delete'),
    path('website/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.WebsiteListView.model, entity='website', label='sitio web', namespace='panel'), name='website_toggle'),
    path('website/<str:tipo>/<str:pk>/', v.WebsiteListByView.as_view(), name='website_by'),

    # ---------- catalogs-log · CatalogsLog ----------
    path('catalogs-log/', v.CatalogsLogListView.as_view(), name='catalogs-log_list'),
    path('catalogs-log/create/', v.CatalogsLogCreateView.as_view(), name='catalogs-log_create'),
    path('catalogs-log/<int:pk>/', v.CatalogsLogDetailView.as_view(), name='catalogs-log_detail'),
    path('catalogs-log/<int:pk>/update/', v.CatalogsLogUpdateView.as_view(), name='catalogs-log_update'),
    path('catalogs-log/<int:pk>/delete/', v.CatalogsLogDeleteView.as_view(), name='catalogs-log_delete'),
]
