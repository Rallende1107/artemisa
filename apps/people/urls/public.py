"""Rutas PÚBLICAS de personas (namespace `personas`): landing, bodies por dominio (cine,
TV, anime y manga, voces), catálogos y la ficha cruzada."""
from django.urls import path
from django.views.generic import RedirectView

from apps.people.views import CinePersonPublicDataView, CinePersonPublicListView, OtakuPersonPublicDataView, OtakuPersonPublicListView, PeoplePublicHomeView, PersonImagePublicListByView, PersonImagesPublicDataView, PersonPublicDataView, PersonPublicDetailView, PersonPublicListByView, PersonPublicListView, TvPersonPublicDataView, TvPersonPublicListView, VoicePersonPublicDataView, VoicePersonPublicListView


app_name = "personas"

urlpatterns = [
    # Homes intermedios retirados: sus URL redirigen a la lista (home de sección → lista, sin nivel de por medio)
    path("cinema/", RedirectView.as_view(pattern_name="personas:film-catalog", permanent=True), name="film"),
    path("tv/", RedirectView.as_view(pattern_name="personas:tv-catalog", permanent=True), name="tv"),
    path("otaku/", RedirectView.as_view(pattern_name="personas:otaku-catalog", permanent=True), name="otaku"),
    path("voices/", RedirectView.as_view(pattern_name="personas:voices-catalog", permanent=True), name="voices"),
    path("", PeoplePublicHomeView.as_view(), name="home"),
    path("list/", PersonPublicListView.as_view(), name="people-catalog"),
    path("list/data/", PersonPublicDataView.as_view(), name="people-catalog-data"),
    path("cinema/list/", CinePersonPublicListView.as_view(), name="film-catalog"),
    path("cinema/list/data/", CinePersonPublicDataView.as_view(), name="film-catalog-data"),
    path("tv/list/", TvPersonPublicListView.as_view(), name="tv-catalog"),
    path("tv/list/data/", TvPersonPublicDataView.as_view(), name="tv-catalog-data"),
    path("otaku/list/", OtakuPersonPublicListView.as_view(), name="otaku-catalog"),
    path("otaku/list/data/", OtakuPersonPublicDataView.as_view(), name="otaku-catalog-data"),
    path("voices/list/", VoicePersonPublicListView.as_view(), name="voices-catalog"),
    path("voices/list/data/", VoicePersonPublicDataView.as_view(), name="voices-catalog-data"),
    # Páginas hijas de la ficha: sus obras completas.
    # Ficha canónica /personas/<id>/<slug>/ (el pk resuelve, el slug decora).
    path("<int:pk>/<slug:slug>/", PersonPublicDetailView.as_view(), name="person-detail"),
    path("<int:pk>/", PersonPublicDetailView.as_view(), name="person-detail"),
    # Listas «por» (acotadas a un padre): <tipo>/<pk>/<slug del padre>/ — al final, tras las fichas
    path("images/<str:tipo>/<int:pk>/", PersonImagePublicListByView.as_view(), name="person-images-by"),
    path("images/<str:tipo>/<int:pk>/data/", PersonImagesPublicDataView.as_view(), name="person-images-by-data"),
    path("images/<str:tipo>/<int:pk>/<slug:slug>/", PersonImagePublicListByView.as_view(), name="person-images-by"),
    path("<str:tipo>/<int:pk>/", PersonPublicListByView.as_view(), name="people-by"),
    path("<str:tipo>/<int:pk>/data/", PersonPublicDataView.as_view(), name="people-by-data"),
    path("<str:tipo>/<int:pk>/<slug:slug>/", PersonPublicListByView.as_view(), name="people-by"),
]
