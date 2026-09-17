"""URLs del panel para companies (sección «Compañías»): home + CRUD por entidad.

Rutas EXPLÍCITAS (estilo Hades): una `path()` por vista, con su `name=` editable. Se montan en el namespace `panel`
desde core/panel_urls.py.

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.companies import views as v
from core.views import AdminImageActionView, AdminToggleView


urlpatterns = [
    path('', include('apps.companies.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('companies/', v.CompaniesHomeView.as_view(), name='companies-home'),

    # ---------- company · Company ----------
    path('company/', v.CompanyListView.as_view(), name='company_list'),
    path('company/create/', v.CompanyCreateView.as_view(), name='company_create'),
    path('company/<int:pk>/', v.CompanyDetailView.as_view(), name='company_detail'),
    path('company/<int:pk>/update/', v.CompanyUpdateView.as_view(), name='company_update'),
    path('company/<int:pk>/delete/', v.CompanyDeleteView.as_view(), name='company_delete'),
    path('company/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CompanyListView.model, entity='company', label='compañía', namespace='panel'), name='company_toggle'),

    # ---------- vistas FIJAS de compañía (una URL por medio) ----------
    path('company-movie/', v.CompanyMovieListView.as_view(), name='company-movie_list'),
    path('company-serie/', v.CompanySerieListView.as_view(), name='company-serie_list'),

    # ---------- company-image · CompanyImage ----------
    path('company-image/', v.CompanyImageListView.as_view(), name='company-image_list'),
    path('company-image/download/', v.CompanyImageDownloadView.as_view(), name='company-image_download'),   # descargar pendientes (N o todas)
    path('company-image/create/', v.CompanyImageCreateView.as_view(), name='company-image_create'),
    path('company-image/<int:pk>/', v.CompanyImageDetailView.as_view(), name='company-image_detail'),
    path('company-image/<int:pk>/update/', v.CompanyImageUpdateView.as_view(), name='company-image_update'),
    path('company-image/<int:pk>/delete/', v.CompanyImageDeleteView.as_view(), name='company-image_delete'),
    path('company-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CompanyImageListView.model, entity='company-image', label='imagen de compañía', namespace='panel'), name='company-image_toggle'),
    path('company-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.CompanyImageListView.model), name='company-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('company-image/<str:tipo>/<str:pk>/', v.CompanyImageListByView.as_view(), name='company-image_by'),

    # ---------- company-log · CompanyLog ----------
    path('company-log/', v.CompanyLogListView.as_view(), name='company-log_list'),
    path('company-log/create/', v.CompanyLogCreateView.as_view(), name='company-log_create'),
    path('company-log/<int:pk>/', v.CompanyLogDetailView.as_view(), name='company-log_detail'),
    path('company-log/<int:pk>/update/', v.CompanyLogUpdateView.as_view(), name='company-log_update'),
    path('company-log/<int:pk>/delete/', v.CompanyLogDeleteView.as_view(), name='company-log_delete'),
]
