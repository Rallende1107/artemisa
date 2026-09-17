"""URLs de DATOS del panel de series: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.series import views as v


urlpatterns = [
    # ---------- serie-genre · Genre ----------
    path('serie-genre/data/', v.GenreDataView.as_view(), name='serie-genre_data'),
    path('serie-genre/select/', v.GenreSelectView.as_view(), name='serie-genre_select'),

    # ---------- serie-genre-alias · GenreAlias ----------
    path('serie-genre-alias/data/', v.GenreAliasDataView.as_view(), name='serie-genre-alias_data'),
    path('serie-genre-alias/data/<str:tipo>/<str:pk>/', v.GenreAliasDataView.as_view(), name='serie-genre-alias_data-by'),

    # ---------- serie-rating · Rating ----------
    path('serie-rating/data/', v.RatingDataView.as_view(), name='serie-rating_data'),
    path('serie-rating/select/', v.RatingSelectView.as_view(), name='serie-rating_select'),

    # ---------- serie-role · Role ----------
    path('serie-role/data/', v.RoleDataView.as_view(), name='serie-role_data'),
    path('serie-role/data/<str:tipo>/<str:pk>/', v.RoleDataView.as_view(), name='serie-role_data-by'),
    path('serie-role/select/', v.RoleSelectView.as_view(), name='serie-role_select'),

    # ---------- serie · Serie ----------
    path('serie/data/', v.SerieDataView.as_view(), name='serie_data'),
    path('serie/data/<str:tipo>/<str:pk>/', v.SerieDataView.as_view(), name='serie_data-by'),
    path('serie/select/', v.SerieSelectView.as_view(), name='serie_select'),

    # ---------- serie-cast · SerieCast ----------
    path('serie-cast/data/', v.SerieCastDataView.as_view(), name='serie-cast_data'),
    path('serie-cast/data/<str:tipo>/<str:pk>/', v.SerieCastDataView.as_view(), name='serie-cast_data-by'),
    path('serie-cast/select/', v.SerieCastSelectView.as_view(), name='serie-cast_select'),

    # ---------- serie-image · SerieImage ----------
    path('serie-image/data/', v.SerieImageDataView.as_view(), name='serie-image_data'),
    path('serie-image/data/<str:tipo>/<str:pk>/', v.SerieImageDataView.as_view(), name='serie-image_data-by'),
    path('serie-image/select/', v.SerieImageSelectView.as_view(), name='serie-image_select'),

    # ---------- serie-relation · SerieRelation ----------
    path('serie-relation/data/', v.SerieRelationDataView.as_view(), name='serie-relation_data'),
    path('serie-relation/data/<str:tipo>/<str:pk>/', v.SerieRelationDataView.as_view(), name='serie-relation_data-by'),
    path('serie-relation/select/', v.SerieRelationSelectView.as_view(), name='serie-relation_select'),

    # ---------- serie-staff · SerieStaff ----------
    path('serie-staff/data/', v.SerieStaffDataView.as_view(), name='serie-staff_data'),
    path('serie-staff/data/<str:tipo>/<str:pk>/', v.SerieStaffDataView.as_view(), name='serie-staff_data-by'),
    path('serie-staff/select/', v.SerieStaffSelectView.as_view(), name='serie-staff_select'),

    # ---------- serie-title · SerieTitle ----------
    path('serie-title/data/', v.SerieTitleDataView.as_view(), name='serie-title_data'),
    path('serie-title/data/<str:tipo>/<str:pk>/', v.SerieTitleDataView.as_view(), name='serie-title_data-by'),
    path('serie-title/select/', v.SerieTitleSelectView.as_view(), name='serie-title_select'),

    # ---------- serie-type · Type ----------
    path('serie-type/data/', v.TypeDataView.as_view(), name='serie-type_data'),
    path('serie-type/select/', v.TypeSelectView.as_view(), name='serie-type_select'),

    # ---------- serie-log · SerieLog ----------
    path('serie-log/data/', v.SerieLogDataView.as_view(), name='serie-log_data'),
]
