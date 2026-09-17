from django.urls import path
from django.views.generic import RedirectView

from apps.otaku import views


app_name = "otaku"

urlpatterns = [
    # Homes intermedios retirados: sus URL redirigen a la lista (home de sección → lista, sin nivel de por medio)
    path("anime/", RedirectView.as_view(pattern_name="otaku:anime-catalog", permanent=True), name="anime"),
    path("manga/", RedirectView.as_view(pattern_name="otaku:manga-catalog", permanent=True), name="manga"),
    path("characters/", RedirectView.as_view(pattern_name="otaku:characters-catalog", permanent=True), name="characters"),
    path("studios/", RedirectView.as_view(pattern_name="otaku:studios-catalog", permanent=True), name="studios"),
    path("producers/", RedirectView.as_view(pattern_name="otaku:producers-catalog", permanent=True), name="producers"),
    path("licensors/", RedirectView.as_view(pattern_name="otaku:licensors-catalog", permanent=True), name="licensors"),
    path("magazines/", RedirectView.as_view(pattern_name="otaku:magazines-catalog", permanent=True), name="magazines"),
    path("", views.OtakuPublicHomeView.as_view(), name="home"),   # hub de la sección

    # — Anime: body + catálogo + fichas canónicas /<pk>/<slug>/ —
    path("anime/list/", views.AnimePublicListView.as_view(), name="anime-catalog"),
    path("anime/list/data/", views.AnimePublicDataView.as_view(), name="anime-catalog-data"),
    path("anime/<int:pk>/<slug:slug>/", views.AnimePublicDetailView.as_view(), name="anime-detail"),
    path("anime/<int:pk>/", views.AnimePublicDetailView.as_view(), name="anime-detail"),

    # — Manga —
    path("manga/list/", views.MangaPublicListView.as_view(), name="manga-catalog"),
    path("manga/list/data/", views.MangaPublicDataView.as_view(), name="manga-catalog-data"),
    path("manga/<int:pk>/<slug:slug>/", views.MangaPublicDetailView.as_view(), name="manga-detail"),
    path("manga/<int:pk>/", views.MangaPublicDetailView.as_view(), name="manga-detail"),

    # — Personajes —
    path("characters/list/", views.CharacterPublicListView.as_view(), name="characters-catalog"),
    path("characters/list/data/", views.CharacterPublicDataView.as_view(), name="characters-catalog-data"),
    path("character/<int:pk>/<slug:slug>/", views.CharacterPublicDetailView.as_view(), name="character-detail"),
    path("character/<int:pk>/", views.CharacterPublicDetailView.as_view(), name="character-detail"),

    # — Industria (estilo MAL): bodies + catálogos + fichas —
    path("studios/list/", views.StudioPublicListView.as_view(), name="studios-catalog"),
    path("studios/list/data/", views.StudioPublicDataView.as_view(), name="studios-catalog-data"),
    path("producers/list/", views.ProducerPublicListView.as_view(), name="producers-catalog"),
    path("producers/list/data/", views.ProducerPublicDataView.as_view(), name="producers-catalog-data"),
    path("licensors/list/", views.LicensorPublicListView.as_view(), name="licensors-catalog"),
    path("licensors/list/data/", views.LicensorPublicDataView.as_view(), name="licensors-catalog-data"),
    path("magazines/list/", views.SerializationPublicListView.as_view(), name="magazines-catalog"),
    path("magazines/list/data/", views.SerializationPublicDataView.as_view(), name="magazines-catalog-data"),
    # Listas «por» (acotadas a un padre): <tipo>/<pk>/<slug del padre>/ — al final, tras las fichas
    path("anime/images/<str:tipo>/<int:pk>/", views.AnimeImagePublicListByView.as_view(), name="anime-images-by"),
    path("anime/images/<str:tipo>/<int:pk>/data/", views.AnimeImagesPublicDataView.as_view(), name="anime-images-by-data"),
    path("anime/images/<str:tipo>/<int:pk>/<slug:slug>/", views.AnimeImagePublicListByView.as_view(), name="anime-images-by"),
    path("anime/<str:tipo>/<int:pk>/", views.AnimePublicListByView.as_view(), name="anime-by"),
    path("anime/<str:tipo>/<int:pk>/data/", views.AnimePublicDataView.as_view(), name="anime-by-data"),
    path("anime/<str:tipo>/<int:pk>/<slug:slug>/", views.AnimePublicListByView.as_view(), name="anime-by"),
    path("manga/images/<str:tipo>/<int:pk>/", views.MangaImagePublicListByView.as_view(), name="manga-images-by"),
    path("manga/images/<str:tipo>/<int:pk>/data/", views.MangaImagesPublicDataView.as_view(), name="manga-images-by-data"),
    path("manga/images/<str:tipo>/<int:pk>/<slug:slug>/", views.MangaImagePublicListByView.as_view(), name="manga-images-by"),
    path("manga/<str:tipo>/<int:pk>/", views.MangaPublicListByView.as_view(), name="manga-by"),
    path("manga/<str:tipo>/<int:pk>/data/", views.MangaPublicDataView.as_view(), name="manga-by-data"),
    path("manga/<str:tipo>/<int:pk>/<slug:slug>/", views.MangaPublicListByView.as_view(), name="manga-by"),
    path("character/images/<str:tipo>/<int:pk>/", views.CharacterImagePublicListByView.as_view(), name="character-images-by"),
    path("character/images/<str:tipo>/<int:pk>/data/", views.CharacterImagesPublicDataView.as_view(), name="character-images-by-data"),
    path("character/images/<str:tipo>/<int:pk>/<slug:slug>/", views.CharacterImagePublicListByView.as_view(), name="character-images-by"),
    path("characters/<str:tipo>/<int:pk>/", views.CharacterPublicListByView.as_view(), name="characters-by"),
    path("characters/<str:tipo>/<int:pk>/data/", views.CharacterPublicDataView.as_view(), name="characters-by-data"),
    path("characters/<str:tipo>/<int:pk>/<slug:slug>/", views.CharacterPublicListByView.as_view(), name="characters-by"),
]
