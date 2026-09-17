"""URLs del panel para serie (sección «Series»): home + CRUD por entidad.

Rutas EXPLÍCITAS (estilo Hades): una `path()` por vista, con su `name=` editable.
Sin funciones que las generen. Se montan en el namespace `panel` desde core/panel_urls.py.

Rutas por entidad: list · [nuevo] · data (DataTables) · select (AJAX FK/M2M) ·
detail · editar · eliminar · accion (toggle is_active/is_staff/...).

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.series import views as v
from core.views import AdminImageActionView, AdminToggleView


urlpatterns = [
    path('', include('apps.series.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('series/', v.SeriesHomeView.as_view(), name='series-home'),

    # ---------- serie-genre · Genre ----------
    path('serie-genre/', v.GenreListView.as_view(), name='serie-genre_list'),
    path('serie-genre/create/', v.GenreCreateView.as_view(), name='serie-genre_create'),
    path('serie-genre/<int:pk>/', v.GenreDetailView.as_view(), name='serie-genre_detail'),
    path('serie-genre/<int:pk>/update/', v.GenreUpdateView.as_view(), name='serie-genre_update'),
    path('serie-genre/<int:pk>/delete/', v.GenreDeleteView.as_view(), name='serie-genre_delete'),
    path('serie-genre/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GenreListView.model, entity='serie-genre', label='género', namespace='panel'), name='serie-genre_toggle'),

    # ---------- serie-genre-alias · GenreAlias ----------
    path('serie-genre-alias/', v.GenreAliasListView.as_view(), name='serie-genre-alias_list'),
    path('serie-genre-alias/create/', v.GenreAliasCreateView.as_view(), name='serie-genre-alias_create'),
    path('serie-genre-alias/<int:pk>/', v.GenreAliasDetailView.as_view(), name='serie-genre-alias_detail'),
    path('serie-genre-alias/<int:pk>/update/', v.GenreAliasUpdateView.as_view(), name='serie-genre-alias_update'),
    path('serie-genre-alias/<int:pk>/delete/', v.GenreAliasDeleteView.as_view(), name='serie-genre-alias_delete'),
    path('serie-genre-alias/<str:tipo>/<str:pk>/', v.GenreAliasListByView.as_view(), name='serie-genre-alias_by'),

    # ---------- serie-rating · Rating ----------
    path('serie-rating/', v.RatingListView.as_view(), name='serie-rating_list'),
    path('serie-rating/create/', v.RatingCreateView.as_view(), name='serie-rating_create'),
    path('serie-rating/<int:pk>/', v.RatingDetailView.as_view(), name='serie-rating_detail'),
    path('serie-rating/<int:pk>/update/', v.RatingUpdateView.as_view(), name='serie-rating_update'),
    path('serie-rating/<int:pk>/delete/', v.RatingDeleteView.as_view(), name='serie-rating_delete'),
    path('serie-rating/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RatingListView.model, entity='serie-rating', label='clasificación', namespace='panel'), name='serie-rating_toggle'),

    # ---------- serie-role · Role ----------
    path('serie-role/', v.RoleListView.as_view(), name='serie-role_list'),
    path('serie-role/create/', v.RoleCreateView.as_view(), name='serie-role_create'),
    path('serie-role/<int:pk>/', v.RoleDetailView.as_view(), name='serie-role_detail'),
    path('serie-role/<int:pk>/update/', v.RoleUpdateView.as_view(), name='serie-role_update'),
    path('serie-role/<int:pk>/delete/', v.RoleDeleteView.as_view(), name='serie-role_delete'),
    path('serie-role/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RoleListView.model, entity='serie-role', label='rol', namespace='panel'), name='serie-role_toggle'),
    path('serie-role/<str:tipo>/<str:pk>/', v.RoleListByView.as_view(), name='serie-role_by'),

    # ---------- serie · Serie ----------
    path('serie/', v.SerieListView.as_view(), name='serie_list'),
    path('serie/create/', v.SerieCreateView.as_view(), name='serie_create'),
    path('serie/<int:pk>/', v.SerieDetailView.as_view(), name='serie_detail'),
    path('serie/<int:pk>/update/', v.SerieUpdateView.as_view(), name='serie_update'),
    path('serie/<int:pk>/delete/', v.SerieDeleteView.as_view(), name='serie_delete'),
    path('serie/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SerieListView.model, entity='serie', label='serie', namespace='panel'), name='serie_toggle'),
    path('serie/<str:tipo>/<str:pk>/', v.SerieListByView.as_view(), name='serie_by'),

    # ---------- serie-cast · SerieCast ----------
    path('serie-cast/', v.SerieCastListView.as_view(), name='serie-cast_list'),
    path('serie-cast/create/', v.SerieCastCreateView.as_view(), name='serie-cast_create'),
    path('serie-cast/<int:pk>/', v.SerieCastDetailView.as_view(), name='serie-cast_detail'),
    path('serie-cast/<int:pk>/update/', v.SerieCastUpdateView.as_view(), name='serie-cast_update'),
    path('serie-cast/<int:pk>/delete/', v.SerieCastDeleteView.as_view(), name='serie-cast_delete'),
    path('serie-cast/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SerieCastListView.model, entity='serie-cast', label='reparto', namespace='panel'), name='serie-cast_toggle'),
    path('serie-cast/<str:tipo>/<str:pk>/', v.SerieCastListByView.as_view(), name='serie-cast_by'),

    # ---------- serie-image · SerieImage ----------
    path('serie-image/', v.SerieImageListView.as_view(), name='serie-image_list'),
    path('serie-image/download/', v.SerieImageDownloadView.as_view(), name='serie-image_download'),   # descargar pendientes (N o todas)
    path('serie-image/create/', v.SerieImageCreateView.as_view(), name='serie-image_create'),
    path('serie-image/<int:pk>/', v.SerieImageDetailView.as_view(), name='serie-image_detail'),
    path('serie-image/<int:pk>/update/', v.SerieImageUpdateView.as_view(), name='serie-image_update'),
    path('serie-image/<int:pk>/delete/', v.SerieImageDeleteView.as_view(), name='serie-image_delete'),
    path('serie-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SerieImageListView.model, entity='serie-image', label='imagen', namespace='panel'), name='serie-image_toggle'),
    path('serie-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.SerieImageListView.model), name='serie-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('serie-image/<str:tipo>/<str:pk>/', v.SerieImageListByView.as_view(), name='serie-image_by'),

    # ---------- serie-relation · SerieRelation ----------
    path('serie-relation/', v.SerieRelationListView.as_view(), name='serie-relation_list'),
    path('serie-relation/create/', v.SerieRelationCreateView.as_view(), name='serie-relation_create'),
    path('serie-relation/<int:pk>/', v.SerieRelationDetailView.as_view(), name='serie-relation_detail'),
    path('serie-relation/<int:pk>/update/', v.SerieRelationUpdateView.as_view(), name='serie-relation_update'),
    path('serie-relation/<int:pk>/delete/', v.SerieRelationDeleteView.as_view(), name='serie-relation_delete'),
    path('serie-relation/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SerieRelationListView.model, entity='serie-relation', label='relación', namespace='panel'), name='serie-relation_toggle'),
    path('serie-relation/<str:tipo>/<str:pk>/', v.SerieRelationListByView.as_view(), name='serie-relation_by'),

    # ---------- serie-staff · SerieStaff ----------
    path('serie-staff/', v.SerieStaffListView.as_view(), name='serie-staff_list'),
    path('serie-staff/create/', v.SerieStaffCreateView.as_view(), name='serie-staff_create'),
    path('serie-staff/<int:pk>/', v.SerieStaffDetailView.as_view(), name='serie-staff_detail'),
    path('serie-staff/<int:pk>/update/', v.SerieStaffUpdateView.as_view(), name='serie-staff_update'),
    path('serie-staff/<int:pk>/delete/', v.SerieStaffDeleteView.as_view(), name='serie-staff_delete'),
    path('serie-staff/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SerieStaffListView.model, entity='serie-staff', label='equipo', namespace='panel'), name='serie-staff_toggle'),
    path('serie-staff/<str:tipo>/<str:pk>/', v.SerieStaffListByView.as_view(), name='serie-staff_by'),

    # ---------- serie-title · SerieTitle ----------
    path('serie-title/', v.SerieTitleListView.as_view(), name='serie-title_list'),
    path('serie-title/create/', v.SerieTitleCreateView.as_view(), name='serie-title_create'),
    path('serie-title/<int:pk>/', v.SerieTitleDetailView.as_view(), name='serie-title_detail'),
    path('serie-title/<int:pk>/update/', v.SerieTitleUpdateView.as_view(), name='serie-title_update'),
    path('serie-title/<int:pk>/delete/', v.SerieTitleDeleteView.as_view(), name='serie-title_delete'),
    path('serie-title/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SerieTitleListView.model, entity='serie-title', label='título', namespace='panel'), name='serie-title_toggle'),
    path('serie-title/<str:tipo>/<str:pk>/', v.SerieTitleListByView.as_view(), name='serie-title_by'),

    # ---------- serie-type · Type ----------
    path('serie-type/', v.TypeListView.as_view(), name='serie-type_list'),
    path('serie-type/create/', v.TypeCreateView.as_view(), name='serie-type_create'),
    path('serie-type/<int:pk>/', v.TypeDetailView.as_view(), name='serie-type_detail'),
    path('serie-type/<int:pk>/update/', v.TypeUpdateView.as_view(), name='serie-type_update'),
    path('serie-type/<int:pk>/delete/', v.TypeDeleteView.as_view(), name='serie-type_delete'),
    path('serie-type/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.TypeListView.model, entity='serie-type', label='tipo', namespace='panel'), name='serie-type_toggle'),

    # ---------- serie-log · SerieLog ----------
    path('serie-log/', v.SerieLogListView.as_view(), name='serie-log_list'),
    path('serie-log/create/', v.SerieLogCreateView.as_view(), name='serie-log_create'),
    path('serie-log/<int:pk>/', v.SerieLogDetailView.as_view(), name='serie-log_detail'),
    path('serie-log/<int:pk>/update/', v.SerieLogUpdateView.as_view(), name='serie-log_update'),
    path('serie-log/<int:pk>/delete/', v.SerieLogDeleteView.as_view(), name='serie-log_delete'),
]
