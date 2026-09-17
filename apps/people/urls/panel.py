"""rutas de ADMINISTRACIÓN de la sección Personas (namespace `panel`, las suma
core/panel_urls.py; sidebar en apps/system/sidebar.py). Explícitas (estilo Hades): home +
CRUD/data/select/toggle de persona, apodo e imágenes.

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.people import views as v
from core.views import AdminImageActionView, AdminToggleView


urlpatterns = [
    path('', include('apps.people.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('people/', v.PeopleHomeView.as_view(), name='people-home'),

    # ---------- person · Person ----------
    path('person/', v.PersonListView.as_view(), name='person_list'),
    path('person/create/', v.PersonCreateView.as_view(), name='person_create'),
    path('person/<int:pk>/', v.PersonDetailView.as_view(), name='person_detail'),
    path('person/<int:pk>/update/', v.PersonUpdateView.as_view(), name='person_update'),
    path('person/<int:pk>/delete/', v.PersonDeleteView.as_view(), name='person_delete'),
    path('person/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.PersonListView.model, entity='person', label='persona', namespace='panel'), name='person_toggle'),
    path('person/<str:tipo>/<str:pk>/', v.PersonListByView.as_view(), name='person_by'),

    # ---------- person-image · PersonImage ----------
    path('person-image/', v.PersonImageListView.as_view(), name='person-image_list'),
    path('person-image/download/', v.PersonImageDownloadView.as_view(), name='person-image_download'),   # descargar pendientes (N o todas)
    path('person-image/create/', v.PersonImageCreateView.as_view(), name='person-image_create'),
    path('person-image/<int:pk>/', v.PersonImageDetailView.as_view(), name='person-image_detail'),
    path('person-image/<int:pk>/update/', v.PersonImageUpdateView.as_view(), name='person-image_update'),
    path('person-image/<int:pk>/delete/', v.PersonImageDeleteView.as_view(), name='person-image_delete'),
    path('person-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.PersonImageListView.model, entity='person-image', label='imagen', namespace='panel'), name='person-image_toggle'),
    path('person-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.PersonImageListView.model), name='person-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('person-image/<str:tipo>/<str:pk>/', v.PersonImageListByView.as_view(), name='person-image_by'),

    # ---------- person-link · PersonLink ----------
    path('person-link/', v.PersonLinkListView.as_view(), name='person-link_list'),
    path('person-link/create/', v.PersonLinkCreateView.as_view(), name='person-link_create'),
    path('person-link/<int:pk>/', v.PersonLinkDetailView.as_view(), name='person-link_detail'),
    path('person-link/<int:pk>/update/', v.PersonLinkUpdateView.as_view(), name='person-link_update'),
    path('person-link/<int:pk>/delete/', v.PersonLinkDeleteView.as_view(), name='person-link_delete'),
    path('person-link/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.PersonLinkListView.model, entity='person-link', label='enlace de persona', namespace='panel'), name='person-link_toggle'),
    path('person-link/<str:tipo>/<str:pk>/', v.PersonLinkListByView.as_view(), name='person-link_by'),

    # ---------- person-nickname · PersonNickname ----------
    path('person-nickname/', v.PersonNicknameListView.as_view(), name='person-nickname_list'),
    path('person-nickname/create/', v.PersonNicknameCreateView.as_view(), name='person-nickname_create'),
    path('person-nickname/<int:pk>/', v.PersonNicknameDetailView.as_view(), name='person-nickname_detail'),
    path('person-nickname/<int:pk>/update/', v.PersonNicknameUpdateView.as_view(), name='person-nickname_update'),
    path('person-nickname/<int:pk>/delete/', v.PersonNicknameDeleteView.as_view(), name='person-nickname_delete'),
    path('person-nickname/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.PersonNicknameListView.model, entity='person-nickname', label='apodo', namespace='panel'), name='person-nickname_toggle'),
    path('person-nickname/<str:tipo>/<str:pk>/', v.PersonNicknameListByView.as_view(), name='person-nickname_by'),

    # ---------- people-log · PeopleLog ----------
    path('people-log/', v.PeopleLogListView.as_view(), name='people-log_list'),
    path('people-log/create/', v.PeopleLogCreateView.as_view(), name='people-log_create'),
    path('people-log/<int:pk>/', v.PeopleLogDetailView.as_view(), name='people-log_detail'),
    path('people-log/<int:pk>/update/', v.PeopleLogUpdateView.as_view(), name='people-log_update'),
    path('people-log/<int:pk>/delete/', v.PeopleLogDeleteView.as_view(), name='people-log_delete'),
]
