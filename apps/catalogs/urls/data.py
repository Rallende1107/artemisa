"""URLs de DATOS del panel de catalogs: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.catalogs import views as v


urlpatterns = [
    # ---------- country · Country ----------
    path('country/data/', v.CountryDataView.as_view(), name='country_data'),
    path('country/select/', v.CountrySelectView.as_view(), name='country_select'),

    # ---------- external-source · ExternalSource ----------
    path('external-source/data/', v.ExternalSourceDataView.as_view(), name='external-source_data'),
    path('external-source/data/<str:tipo>/<str:pk>/', v.ExternalSourceDataView.as_view(), name='external-source_data-by'),
    path('external-source/select/', v.ExternalSourceSelectView.as_view(), name='external-source_select'),

    # ---------- format · Format ----------
    path('format/data/', v.FormatDataView.as_view(), name='format_data'),
    path('format/select/', v.FormatSelectView.as_view(), name='format_select'),

    # ---------- language · Language ----------
    path('language/data/', v.LanguageDataView.as_view(), name='language_data'),
    path('language/select/', v.LanguageSelectView.as_view(), name='language_select'),

    # ---------- quality · Quality ----------
    path('quality/data/', v.QualityDataView.as_view(), name='quality_data'),
    path('quality/select/', v.QualitySelectView.as_view(), name='quality_select'),

    # ---------- relation-type · RelationType ----------
    path('relation-type/data/', v.RelationTypeDataView.as_view(), name='relation-type_data'),
    path('relation-type/select/', v.RelationTypeSelectView.as_view(), name='relation-type_select'),

    # ---------- website · Website ----------
    path('website/data/', v.WebsiteDataView.as_view(), name='website_data'),
    path('website/data/<str:tipo>/<str:pk>/', v.WebsiteDataView.as_view(), name='website_data-by'),
    path('website/select/', v.WebsiteSelectView.as_view(), name='website_select'),

    # ---------- catalogs-log · CatalogsLog ----------
    path('catalogs-log/data/', v.CatalogsLogDataView.as_view(), name='catalogs-log_data'),
]
