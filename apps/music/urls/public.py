from django.urls import path
from django.views.generic import RedirectView

from apps.music import views


app_name = "music"

urlpatterns = [
    # Homes intermedios retirados: sus URL redirigen a la lista (home de sección → lista, sin nivel de por medio)
    path("artists/", RedirectView.as_view(pattern_name="music:artists-catalog", permanent=True), name="artists"),
    path("albums/", RedirectView.as_view(pattern_name="music:albums-catalog", permanent=True), name="albums"),
    path("songs/", RedirectView.as_view(pattern_name="music:songs-catalog", permanent=True), name="songs"),
    path("", views.MusicPublicHomeView.as_view(), name="home"),
    # Landings por entidad (el body de cada entrada del nav de sección)…
    # …y su catálogo con filtros un nivel más adentro (Ver todo →).
    path("artists/list/", views.ArtistPublicListView.as_view(), name="artists-catalog"),
    path("artists/list/data/", views.ArtistPublicDataView.as_view(), name="artists-catalog-data"),
    path("albums/list/", views.AlbumPublicListView.as_view(), name="albums-catalog"),
    path("albums/list/data/", views.AlbumPublicDataView.as_view(), name="albums-catalog-data"),
    path("songs/list/", views.SongPublicListView.as_view(), name="songs-catalog"),
    path("songs/list/data/", views.SongPublicDataView.as_view(), name="songs-catalog-data"),
    # Fichas canónicas /<entidad>/<id>/<slug>/ (el pk resuelve, el slug decora).
    path("album/<int:pk>/<slug:slug>/", views.AlbumPublicDetailView.as_view(), name="album-detail"),
    path("album/<int:pk>/", views.AlbumPublicDetailView.as_view(), name="album-detail"),
    path("artist/<int:pk>/<slug:slug>/", views.ArtistPublicDetailView.as_view(), name="artist-detail"),
    path("artist/<int:pk>/", views.ArtistPublicDetailView.as_view(), name="artist-detail"),
    path("song/<int:pk>/<slug:slug>/", views.SongPublicDetailView.as_view(), name="song-detail"),
    path("song/<int:pk>/", views.SongPublicDetailView.as_view(), name="song-detail"),
    # Listas «por» (acotadas a un padre): <tipo>/<pk>/<slug del padre>/ — al final, tras las fichas
    path("album/images/<str:tipo>/<int:pk>/", views.AlbumImagePublicListByView.as_view(), name="album-images-by"),
    path("album/images/<str:tipo>/<int:pk>/data/", views.AlbumImagesPublicDataView.as_view(), name="album-images-by-data"),
    path("album/images/<str:tipo>/<int:pk>/<slug:slug>/", views.AlbumImagePublicListByView.as_view(), name="album-images-by"),
    path("albums/<str:tipo>/<int:pk>/", views.AlbumPublicListByView.as_view(), name="albums-by"),
    path("albums/<str:tipo>/<int:pk>/data/", views.AlbumPublicDataView.as_view(), name="albums-by-data"),
    path("albums/<str:tipo>/<int:pk>/<slug:slug>/", views.AlbumPublicListByView.as_view(), name="albums-by"),
    path("artist/images/<str:tipo>/<int:pk>/", views.ArtistImagePublicListByView.as_view(), name="artist-images-by"),
    path("artist/images/<str:tipo>/<int:pk>/data/", views.ArtistImagesPublicDataView.as_view(), name="artist-images-by-data"),
    path("artist/images/<str:tipo>/<int:pk>/<slug:slug>/", views.ArtistImagePublicListByView.as_view(), name="artist-images-by"),
    path("artists/<str:tipo>/<int:pk>/", views.ArtistPublicListByView.as_view(), name="artists-by"),
    path("artists/<str:tipo>/<int:pk>/data/", views.ArtistPublicDataView.as_view(), name="artists-by-data"),
    path("artists/<str:tipo>/<int:pk>/<slug:slug>/", views.ArtistPublicListByView.as_view(), name="artists-by"),
    path("songs/<str:tipo>/<int:pk>/", views.SongPublicListByView.as_view(), name="songs-by"),
    path("songs/<str:tipo>/<int:pk>/data/", views.SongPublicDataView.as_view(), name="songs-by-data"),
    path("songs/<str:tipo>/<int:pk>/<slug:slug>/", views.SongPublicListByView.as_view(), name="songs-by"),
]
