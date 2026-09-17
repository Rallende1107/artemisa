"""URLs de DATOS del panel de movies: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.movies import views as v


urlpatterns = [
    # ---------- movie-genre · Genre ----------
    path('movie-genre/data/', v.GenreDataView.as_view(), name='movie-genre_data'),
    path('movie-genre/select/', v.GenreSelectView.as_view(), name='movie-genre_select'),

    # ---------- movie-genre-alias · GenreAlias ----------
    path('movie-genre-alias/data/', v.GenreAliasDataView.as_view(), name='movie-genre-alias_data'),
    path('movie-genre-alias/data/<str:tipo>/<str:pk>/', v.GenreAliasDataView.as_view(), name='movie-genre-alias_data-by'),

    # ---------- movie · Movie ----------
    path('movie/data/', v.MovieDataView.as_view(), name='movie_data'),
    path('movie/data/<str:tipo>/<str:pk>/', v.MovieDataView.as_view(), name='movie_data-by'),
    path('movie/select/', v.MovieSelectView.as_view(), name='movie_select'),

    # ---------- movie-cast · MovieCast ----------
    path('movie-cast/data/', v.MovieCastDataView.as_view(), name='movie-cast_data'),
    path('movie-cast/data/<str:tipo>/<str:pk>/', v.MovieCastDataView.as_view(), name='movie-cast_data-by'),
    path('movie-cast/select/', v.MovieCastSelectView.as_view(), name='movie-cast_select'),

    # ---------- movie-image · MovieImage ----------
    path('movie-image/data/', v.MovieImageDataView.as_view(), name='movie-image_data'),
    path('movie-image/data/<str:tipo>/<str:pk>/', v.MovieImageDataView.as_view(), name='movie-image_data-by'),
    path('movie-image/select/', v.MovieImageSelectView.as_view(), name='movie-image_select'),

    # ---------- movie-relation · MovieRelation ----------
    path('movie-relation/data/', v.MovieRelationDataView.as_view(), name='movie-relation_data'),
    path('movie-relation/data/<str:tipo>/<str:pk>/', v.MovieRelationDataView.as_view(), name='movie-relation_data-by'),
    path('movie-relation/select/', v.MovieRelationSelectView.as_view(), name='movie-relation_select'),

    # ---------- movie-staff · MovieStaff ----------
    path('movie-staff/data/', v.MovieStaffDataView.as_view(), name='movie-staff_data'),
    path('movie-staff/data/<str:tipo>/<str:pk>/', v.MovieStaffDataView.as_view(), name='movie-staff_data-by'),
    path('movie-staff/select/', v.MovieStaffSelectView.as_view(), name='movie-staff_select'),

    # ---------- movie-title · MovieTitle ----------
    path('movie-title/data/', v.MovieTitleDataView.as_view(), name='movie-title_data'),
    path('movie-title/data/<str:tipo>/<str:pk>/', v.MovieTitleDataView.as_view(), name='movie-title_data-by'),
    path('movie-title/select/', v.MovieTitleSelectView.as_view(), name='movie-title_select'),

    # ---------- movie-rating · Rating ----------
    path('movie-rating/data/', v.RatingDataView.as_view(), name='movie-rating_data'),
    path('movie-rating/select/', v.RatingSelectView.as_view(), name='movie-rating_select'),

    # ---------- movie-role · Role ----------
    path('movie-role/data/', v.RoleDataView.as_view(), name='movie-role_data'),
    path('movie-role/data/<str:tipo>/<str:pk>/', v.RoleDataView.as_view(), name='movie-role_data-by'),
    path('movie-role/select/', v.RoleSelectView.as_view(), name='movie-role_select'),

    # ---------- movie-type · Type ----------
    path('movie-type/data/', v.TypeDataView.as_view(), name='movie-type_data'),
    path('movie-type/select/', v.TypeSelectView.as_view(), name='movie-type_select'),

    # ---------- movie-log · MovieLog ----------
    path('movie-log/data/', v.MovieLogDataView.as_view(), name='movie-log_data'),
]
