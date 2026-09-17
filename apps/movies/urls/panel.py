"""URLs del panel para movie (sección «Películas»): home + CRUD por entidad.

Rutas EXPLÍCITAS (estilo Hades): una `path()` por vista, con su `name=` editable.
Sin funciones que las generen. Se montan en el namespace `panel` desde core/panel_urls.py.

Rutas por entidad: list · [nuevo] · data (DataTables) · select (AJAX FK/M2M) ·
detail · editar · eliminar · accion (toggle is_active/is_staff/...).

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.movies import views as v
from core.views import AdminImageActionView, AdminToggleView


urlpatterns = [
    path('', include('apps.movies.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('movies/', v.MoviesHomeView.as_view(), name='movies-home'),

    # ---------- movie-genre · Genre ----------
    path('movie-genre/', v.GenreListView.as_view(), name='movie-genre_list'),
    path('movie-genre/create/', v.GenreCreateView.as_view(), name='movie-genre_create'),
    path('movie-genre/<int:pk>/', v.GenreDetailView.as_view(), name='movie-genre_detail'),
    path('movie-genre/<int:pk>/update/', v.GenreUpdateView.as_view(), name='movie-genre_update'),
    path('movie-genre/<int:pk>/delete/', v.GenreDeleteView.as_view(), name='movie-genre_delete'),
    path('movie-genre/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GenreListView.model, entity='movie-genre', label='género', namespace='panel'), name='movie-genre_toggle'),

    # ---------- movie-genre-alias · GenreAlias ----------
    path('movie-genre-alias/', v.GenreAliasListView.as_view(), name='movie-genre-alias_list'),
    path('movie-genre-alias/create/', v.GenreAliasCreateView.as_view(), name='movie-genre-alias_create'),
    path('movie-genre-alias/<int:pk>/', v.GenreAliasDetailView.as_view(), name='movie-genre-alias_detail'),
    path('movie-genre-alias/<int:pk>/update/', v.GenreAliasUpdateView.as_view(), name='movie-genre-alias_update'),
    path('movie-genre-alias/<int:pk>/delete/', v.GenreAliasDeleteView.as_view(), name='movie-genre-alias_delete'),
    path('movie-genre-alias/<str:tipo>/<str:pk>/', v.GenreAliasListByView.as_view(), name='movie-genre-alias_by'),

    # ---------- movie · Movie ----------
    path('movie/', v.MovieListView.as_view(), name='movie_list'),
    path('movie/create/', v.MovieCreateView.as_view(), name='movie_create'),
    path('movie/<int:pk>/', v.MovieDetailView.as_view(), name='movie_detail'),
    path('movie/<int:pk>/update/', v.MovieUpdateView.as_view(), name='movie_update'),
    path('movie/<int:pk>/delete/', v.MovieDeleteView.as_view(), name='movie_delete'),
    path('movie/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MovieListView.model, entity='movie', label='película', namespace='panel'), name='movie_toggle'),
    path('movie/<str:tipo>/<str:pk>/', v.MovieListByView.as_view(), name='movie_by'),

    # ---------- movie-cast · MovieCast ----------
    path('movie-cast/', v.MovieCastListView.as_view(), name='movie-cast_list'),
    path('movie-cast/create/', v.MovieCastCreateView.as_view(), name='movie-cast_create'),
    path('movie-cast/<int:pk>/', v.MovieCastDetailView.as_view(), name='movie-cast_detail'),
    path('movie-cast/<int:pk>/update/', v.MovieCastUpdateView.as_view(), name='movie-cast_update'),
    path('movie-cast/<int:pk>/delete/', v.MovieCastDeleteView.as_view(), name='movie-cast_delete'),
    path('movie-cast/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MovieCastListView.model, entity='movie-cast', label='reparto', namespace='panel'), name='movie-cast_toggle'),
    path('movie-cast/<str:tipo>/<str:pk>/', v.MovieCastListByView.as_view(), name='movie-cast_by'),

    # ---------- movie-image · MovieImage ----------
    path('movie-image/', v.MovieImageListView.as_view(), name='movie-image_list'),
    path('movie-image/download/', v.MovieImageDownloadView.as_view(), name='movie-image_download'),   # descargar pendientes (N o todas)
    path('movie-image/create/', v.MovieImageCreateView.as_view(), name='movie-image_create'),
    path('movie-image/<int:pk>/', v.MovieImageDetailView.as_view(), name='movie-image_detail'),
    path('movie-image/<int:pk>/update/', v.MovieImageUpdateView.as_view(), name='movie-image_update'),
    path('movie-image/<int:pk>/delete/', v.MovieImageDeleteView.as_view(), name='movie-image_delete'),
    path('movie-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MovieImageListView.model, entity='movie-image', label='imagen', namespace='panel'), name='movie-image_toggle'),
    path('movie-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.MovieImageListView.model), name='movie-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('movie-image/<str:tipo>/<str:pk>/', v.MovieImageListByView.as_view(), name='movie-image_by'),

    # ---------- movie-relation · MovieRelation ----------
    path('movie-relation/', v.MovieRelationListView.as_view(), name='movie-relation_list'),
    path('movie-relation/create/', v.MovieRelationCreateView.as_view(), name='movie-relation_create'),
    path('movie-relation/<int:pk>/', v.MovieRelationDetailView.as_view(), name='movie-relation_detail'),
    path('movie-relation/<int:pk>/update/', v.MovieRelationUpdateView.as_view(), name='movie-relation_update'),
    path('movie-relation/<int:pk>/delete/', v.MovieRelationDeleteView.as_view(), name='movie-relation_delete'),
    path('movie-relation/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MovieRelationListView.model, entity='movie-relation', label='relación', namespace='panel'), name='movie-relation_toggle'),
    path('movie-relation/<str:tipo>/<str:pk>/', v.MovieRelationListByView.as_view(), name='movie-relation_by'),

    # ---------- movie-staff · MovieStaff ----------
    path('movie-staff/', v.MovieStaffListView.as_view(), name='movie-staff_list'),
    path('movie-staff/create/', v.MovieStaffCreateView.as_view(), name='movie-staff_create'),
    path('movie-staff/<int:pk>/', v.MovieStaffDetailView.as_view(), name='movie-staff_detail'),
    path('movie-staff/<int:pk>/update/', v.MovieStaffUpdateView.as_view(), name='movie-staff_update'),
    path('movie-staff/<int:pk>/delete/', v.MovieStaffDeleteView.as_view(), name='movie-staff_delete'),
    path('movie-staff/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MovieStaffListView.model, entity='movie-staff', label='equipo', namespace='panel'), name='movie-staff_toggle'),
    path('movie-staff/<str:tipo>/<str:pk>/', v.MovieStaffListByView.as_view(), name='movie-staff_by'),

    # ---------- movie-title · MovieTitle ----------
    path('movie-title/', v.MovieTitleListView.as_view(), name='movie-title_list'),
    path('movie-title/create/', v.MovieTitleCreateView.as_view(), name='movie-title_create'),
    path('movie-title/<int:pk>/', v.MovieTitleDetailView.as_view(), name='movie-title_detail'),
    path('movie-title/<int:pk>/update/', v.MovieTitleUpdateView.as_view(), name='movie-title_update'),
    path('movie-title/<int:pk>/delete/', v.MovieTitleDeleteView.as_view(), name='movie-title_delete'),
    path('movie-title/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MovieTitleListView.model, entity='movie-title', label='título', namespace='panel'), name='movie-title_toggle'),
    path('movie-title/<str:tipo>/<str:pk>/', v.MovieTitleListByView.as_view(), name='movie-title_by'),

    # ---------- movie-rating · Rating ----------
    path('movie-rating/', v.RatingListView.as_view(), name='movie-rating_list'),
    path('movie-rating/create/', v.RatingCreateView.as_view(), name='movie-rating_create'),
    path('movie-rating/<int:pk>/', v.RatingDetailView.as_view(), name='movie-rating_detail'),
    path('movie-rating/<int:pk>/update/', v.RatingUpdateView.as_view(), name='movie-rating_update'),
    path('movie-rating/<int:pk>/delete/', v.RatingDeleteView.as_view(), name='movie-rating_delete'),
    path('movie-rating/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RatingListView.model, entity='movie-rating', label='clasificación', namespace='panel'), name='movie-rating_toggle'),

    # ---------- movie-role · Role ----------
    path('movie-role/', v.RoleListView.as_view(), name='movie-role_list'),
    path('movie-role/create/', v.RoleCreateView.as_view(), name='movie-role_create'),
    path('movie-role/<int:pk>/', v.RoleDetailView.as_view(), name='movie-role_detail'),
    path('movie-role/<int:pk>/update/', v.RoleUpdateView.as_view(), name='movie-role_update'),
    path('movie-role/<int:pk>/delete/', v.RoleDeleteView.as_view(), name='movie-role_delete'),
    path('movie-role/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RoleListView.model, entity='movie-role', label='rol', namespace='panel'), name='movie-role_toggle'),
    path('movie-role/<str:tipo>/<str:pk>/', v.RoleListByView.as_view(), name='movie-role_by'),

    # ---------- movie-type · Type ----------
    path('movie-type/', v.TypeListView.as_view(), name='movie-type_list'),
    path('movie-type/create/', v.TypeCreateView.as_view(), name='movie-type_create'),
    path('movie-type/<int:pk>/', v.TypeDetailView.as_view(), name='movie-type_detail'),
    path('movie-type/<int:pk>/update/', v.TypeUpdateView.as_view(), name='movie-type_update'),
    path('movie-type/<int:pk>/delete/', v.TypeDeleteView.as_view(), name='movie-type_delete'),
    path('movie-type/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.TypeListView.model, entity='movie-type', label='tipo', namespace='panel'), name='movie-type_toggle'),

    # ---------- movie-log · MovieLog ----------
    path('movie-log/', v.MovieLogListView.as_view(), name='movie-log_list'),
    path('movie-log/create/', v.MovieLogCreateView.as_view(), name='movie-log_create'),
    path('movie-log/<int:pk>/', v.MovieLogDetailView.as_view(), name='movie-log_detail'),
    path('movie-log/<int:pk>/update/', v.MovieLogUpdateView.as_view(), name='movie-log_update'),
    path('movie-log/<int:pk>/delete/', v.MovieLogDeleteView.as_view(), name='movie-log_delete'),
]
