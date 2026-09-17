from django.urls import path
from django.views.generic import RedirectView

from apps.games import views


app_name = "games"

urlpatterns = [
    # Homes intermedios retirados: sus URL redirigen a la lista (home de sección → lista, sin nivel de por medio)
    path("creators/", RedirectView.as_view(pattern_name="games:creators-catalog", permanent=True), name="creators"),
    path("publishers/", RedirectView.as_view(pattern_name="games:publishers-catalog", permanent=True), name="publishers"),
    path("", views.GamesPublicHomeView.as_view(), name="home"),
    path("list/", views.GamePublicListView.as_view(), name="games-catalog"),
    path("list/data/", views.GamePublicDataView.as_view(), name="games-catalog-data"),
    # Ficha canónica /juego/<id>/<slug>/ (el pk resuelve, el slug decora).
    path("character/<int:pk>/<slug:slug>/", views.CharacterPublicDetailView.as_view(), name="character-detail"),
    path("character/<int:pk>/", views.CharacterPublicDetailView.as_view(), name="character-detail"),
    path("game/<int:pk>/<slug:slug>/", views.GamePublicDetailView.as_view(), name="game-detail"),
    path("game/<int:pk>/", views.GamePublicDetailView.as_view(), name="game-detail"),
    # Bodies por entidad (landing) + su catálogo un nivel adentro.
    path("creators/list/", views.CreatorPublicListView.as_view(), name="creators-catalog"),
    path("creators/list/data/", views.CreatorPublicDataView.as_view(), name="creators-catalog-data"),
    path("publishers/list/", views.PublisherPublicListView.as_view(), name="publishers-catalog"),
    path("publishers/list/data/", views.PublisherPublicDataView.as_view(), name="publishers-catalog-data"),
    path("creator/<int:pk>/<slug:slug>/", views.CreatorPublicDetailView.as_view(), name="creator-detail"),
    path("creator/<int:pk>/", views.CreatorPublicDetailView.as_view(), name="creator-detail"),
    # Listas «por» (acotadas a un padre): <tipo>/<pk>/<slug del padre>/ — al final, tras las fichas
    path("creators/<str:tipo>/<int:pk>/", views.CreatorPublicListByView.as_view(), name="creators-by"),
    path("creators/<str:tipo>/<int:pk>/data/", views.CreatorPublicDataView.as_view(), name="creators-by-data"),
    path("creators/<str:tipo>/<int:pk>/<slug:slug>/", views.CreatorPublicListByView.as_view(), name="creators-by"),
    path("images/<str:tipo>/<int:pk>/", views.GameImagePublicListByView.as_view(), name="game-images-by"),
    path("images/<str:tipo>/<int:pk>/data/", views.GameImagesPublicDataView.as_view(), name="game-images-by-data"),
    path("images/<str:tipo>/<int:pk>/<slug:slug>/", views.GameImagePublicListByView.as_view(), name="game-images-by"),
    path("releases/<str:tipo>/<int:pk>/", views.ReleasePublicListByView.as_view(), name="releases-by"),
    path("releases/<str:tipo>/<int:pk>/data/", views.ReleasePublicDataView.as_view(), name="releases-by-data"),
    path("releases/<str:tipo>/<int:pk>/<slug:slug>/", views.ReleasePublicListByView.as_view(), name="releases-by"),
    path("characters/<str:tipo>/<int:pk>/", views.CharacterPublicListByView.as_view(), name="characters-by"),
    path("characters/<str:tipo>/<int:pk>/data/", views.CharacterPublicDataView.as_view(), name="characters-by-data"),
    path("characters/<str:tipo>/<int:pk>/<slug:slug>/", views.CharacterPublicListByView.as_view(), name="characters-by"),
    path("<str:tipo>/<int:pk>/", views.GamePublicListByView.as_view(), name="games-by"),
    path("<str:tipo>/<int:pk>/data/", views.GamePublicDataView.as_view(), name="games-by-data"),
    path("<str:tipo>/<int:pk>/<slug:slug>/", views.GamePublicListByView.as_view(), name="games-by"),
]
