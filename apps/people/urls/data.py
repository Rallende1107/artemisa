"""URLs de DATOS del panel de people: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.people import views as v


urlpatterns = [
    # ---------- person · Person ----------
    path('person/data/', v.PersonDataView.as_view(), name='person_data'),
    path('person/data/<str:tipo>/<str:pk>/', v.PersonDataView.as_view(), name='person_data-by'),
    path('person/select/', v.PersonSelectView.as_view(), name='person_select'),

    # ---------- person-image · PersonImage ----------
    path('person-image/data/', v.PersonImageDataView.as_view(), name='person-image_data'),
    path('person-image/data/<str:tipo>/<str:pk>/', v.PersonImageDataView.as_view(), name='person-image_data-by'),
    path('person-image/select/', v.PersonImageSelectView.as_view(), name='person-image_select'),

    # ---------- person-link · PersonLink ----------
    path('person-link/data/', v.PersonLinkDataView.as_view(), name='person-link_data'),
    path('person-link/data/<str:tipo>/<str:pk>/', v.PersonLinkDataView.as_view(), name='person-link_data-by'),
    path('person-link/select/', v.PersonLinkSelectView.as_view(), name='person-link_select'),

    # ---------- person-nickname · PersonNickname ----------
    path('person-nickname/data/', v.PersonNicknameDataView.as_view(), name='person-nickname_data'),
    path('person-nickname/data/<str:tipo>/<str:pk>/', v.PersonNicknameDataView.as_view(), name='person-nickname_data-by'),
    path('person-nickname/select/', v.PersonNicknameSelectView.as_view(), name='person-nickname_select'),

    # ---------- people-log · PeopleLog ----------
    path('people-log/data/', v.PeopleLogDataView.as_view(), name='people-log_data'),
]
