from django.urls import path
from django.views.generic import RedirectView

from apps.series import views


app_name = "series"

urlpatterns = [
    # Homes intermedios retirados: sus URL redirigen a la lista (home de sección → lista, sin nivel de por medio)
    path("producers/", RedirectView.as_view(pattern_name="series:producers-catalog", permanent=True), name="producers"),
    path("distributors/", RedirectView.as_view(pattern_name="series:distributors-catalog", permanent=True), name="distributors"),
    path("", views.SeriesPublicHomeView.as_view(), name="home"),
    path("list/", views.SeriePublicListView.as_view(), name="series-catalog"),
    path("list/data/", views.SeriePublicDataView.as_view(), name="series-catalog-data"),
    # Ficha canónica /serie/<id>/<slug>/ (el pk resuelve, el slug decora).
    # Las subpáginas van ANTES del patrón slug para que no las capture.
    path("series/<int:pk>/<slug:slug>/", views.SeriePublicDetailView.as_view(), name="serie-detail"),
    path("series/<int:pk>/", views.SeriePublicDetailView.as_view(), name="serie-detail"),
    # Bodies de compañías (landing por entidad) + su catálogo un nivel adentro.
    path("producers/list/", views.ProducerPublicListView.as_view(), name="producers-catalog"),
    path("producers/list/data/", views.ProducerPublicDataView.as_view(), name="producers-catalog-data"),
    path("distributors/list/", views.DistributorPublicListView.as_view(), name="distributors-catalog"),
    path("distributors/list/data/", views.DistributorPublicDataView.as_view(), name="distributors-catalog-data"),
    # Listas «por» (acotadas a un padre): <tipo>/<pk>/<slug del padre>/ — al final, tras las fichas
    path("staff/<str:tipo>/<int:pk>/", views.SerieStaffPublicListByView.as_view(), name="crew-by"),
    path("staff/<str:tipo>/<int:pk>/data/", views.SerieStaffPublicDataView.as_view(), name="crew-by-data"),
    path("staff/<str:tipo>/<int:pk>/<slug:slug>/", views.SerieStaffPublicListByView.as_view(), name="crew-by"),
    path("images/<str:tipo>/<int:pk>/", views.SerieImagePublicListByView.as_view(), name="serie-images-by"),
    path("images/<str:tipo>/<int:pk>/data/", views.SerieImagesPublicDataView.as_view(), name="serie-images-by-data"),
    path("images/<str:tipo>/<int:pk>/<slug:slug>/", views.SerieImagePublicListByView.as_view(), name="serie-images-by"),
    path("<str:tipo>/<int:pk>/", views.SeriePublicListByView.as_view(), name="series-by"),
    path("<str:tipo>/<int:pk>/data/", views.SeriePublicDataView.as_view(), name="series-by-data"),
    path("<str:tipo>/<int:pk>/<slug:slug>/", views.SeriePublicListByView.as_view(), name="series-by"),
    path("cast/<str:tipo>/<int:pk>/", views.SerieCastPublicListByView.as_view(), name="cast-by"),
    path("cast/<str:tipo>/<int:pk>/data/", views.SerieCastPublicDataView.as_view(), name="cast-by-data"),
    path("cast/<str:tipo>/<int:pk>/<slug:slug>/", views.SerieCastPublicListByView.as_view(), name="cast-by"),
]
