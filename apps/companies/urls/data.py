"""URLs de DATOS del panel de companies: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.companies import views as v


urlpatterns = [
    # ---------- company · Company ----------
    path('company/data/', v.CompanyDataView.as_view(), name='company_data'),
    path('company/select/', v.CompanySelectView.as_view(), name='company_select'),

    # ---------- vistas FIJAS de compañía ----------
    path('company-movie/data/', v.CompanyMovieDataView.as_view(), name='company-movie_data'),
    path('company-serie/data/', v.CompanySerieDataView.as_view(), name='company-serie_data'),

    # ---------- company-image · CompanyImage ----------
    path('company-image/data/', v.CompanyImageDataView.as_view(), name='company-image_data'),
    path('company-image/data/<str:tipo>/<str:pk>/', v.CompanyImageDataView.as_view(), name='company-image_data-by'),
    path('company-image/select/', v.CompanyImageSelectView.as_view(), name='company-image_select'),

    # ---------- company-log · CompanyLog ----------
    path('company-log/data/', v.CompanyLogDataView.as_view(), name='company-log_data'),
]
