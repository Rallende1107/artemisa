from django.urls import path
from django.views.generic import RedirectView

from apps.movies import views


app_name = "movies"

urlpatterns = [
    # Homes intermedios retirados: sus URL redirigen a la lista (home de sección → lista, sin nivel de por medio)
    path("producers/", RedirectView.as_view(pattern_name="movies:producers-catalog", permanent=True), name="producers"),
    path("distributors/", RedirectView.as_view(pattern_name="movies:distributors-catalog", permanent=True), name="distributors"),
    path("", views.MoviesPublicHomeView.as_view(), name="home"),
    path("list/", views.MoviePublicListView.as_view(), name="movies-catalog"),
    path("list/data/", views.MoviePublicDataView.as_view(), name="movies-catalog-data"),
    # Ficha canónica /pelicula/<id>/<slug>/ (el pk resuelve, el slug decora).
    # Las subpáginas van ANTES del patrón slug para que no las capture.
    path("movie/<int:pk>/<slug:slug>/", views.MoviePublicDetailView.as_view(), name="movie-detail"),
    path("movie/<int:pk>/", views.MoviePublicDetailView.as_view(), name="movie-detail"),
    # Bodies de compañías (landing por entidad) + su catálogo un nivel adentro.
    path("producers/list/", views.ProducerPublicListView.as_view(), name="producers-catalog"),
    path("producers/list/data/", views.ProducerPublicDataView.as_view(), name="producers-catalog-data"),
    path("distributors/list/", views.DistributorPublicListView.as_view(), name="distributors-catalog"),
    path("distributors/list/data/", views.DistributorPublicDataView.as_view(), name="distributors-catalog-data"),
    # Listas «por» (acotadas a un padre): <tipo>/<pk>/<slug del padre>/ — al final, tras las fichas
    path("staff/<str:tipo>/<int:pk>/", views.MovieStaffPublicListByView.as_view(), name="crew-by"),
    path("staff/<str:tipo>/<int:pk>/data/", views.MovieStaffPublicDataView.as_view(), name="crew-by-data"),
    path("staff/<str:tipo>/<int:pk>/<slug:slug>/", views.MovieStaffPublicListByView.as_view(), name="crew-by"),
    path("images/<str:tipo>/<int:pk>/", views.MovieImagePublicListByView.as_view(), name="movie-images-by"),
    path("images/<str:tipo>/<int:pk>/data/", views.MovieImagesPublicDataView.as_view(), name="movie-images-by-data"),
    path("images/<str:tipo>/<int:pk>/<slug:slug>/", views.MovieImagePublicListByView.as_view(), name="movie-images-by"),
    path("<str:tipo>/<int:pk>/", views.MoviePublicListByView.as_view(), name="movies-by"),
    path("<str:tipo>/<int:pk>/data/", views.MoviePublicDataView.as_view(), name="movies-by-data"),
    path("<str:tipo>/<int:pk>/<slug:slug>/", views.MoviePublicListByView.as_view(), name="movies-by"),
    path("cast/<str:tipo>/<int:pk>/", views.MovieCastPublicListByView.as_view(), name="cast-by"),
    path("cast/<str:tipo>/<int:pk>/data/", views.MovieCastPublicDataView.as_view(), name="cast-by-data"),
    path("cast/<str:tipo>/<int:pk>/<slug:slug>/", views.MovieCastPublicListByView.as_view(), name="cast-by"),
]
