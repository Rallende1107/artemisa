"""Rutas PÚBLICAS de compañías (namespace `companias`): el hub de la industria de todos los medios, el catálogo
completo y la ficha. Cuelga de /catalog/companies/."""
from django.urls import path
from django.views.generic import RedirectView

from apps.companies.views import CompaniesPublicHomeView, CompanyPublicDataView, CompanyPublicDetailView, CompanyPublicListView


app_name = "companias"

urlpatterns = [
    # Homes intermedios retirados: sus URL redirigen al hub (home de sección → lista, sin nivel de por medio)
    path("cinema/", RedirectView.as_view(pattern_name="companias:home", permanent=True), name="film"),
    path("tv/", RedirectView.as_view(pattern_name="companias:home", permanent=True), name="tv"),
    path("otaku/", RedirectView.as_view(pattern_name="companias:home", permanent=True), name="otaku"),
    path("games/", RedirectView.as_view(pattern_name="companias:home", permanent=True), name="games"),
    path("", CompaniesPublicHomeView.as_view(), name="home"),
    path("list/", CompanyPublicListView.as_view(), name="companies-catalog"),
    path("list/data/", CompanyPublicDataView.as_view(), name="companies-catalog-data"),
    # Ficha canónica /catalog/companies/<id>/<slug>/ (el pk resuelve, el slug decora).
    path("<int:pk>/<slug:slug>/", CompanyPublicDetailView.as_view(), name="company-detail"),
    path("<int:pk>/", CompanyPublicDetailView.as_view(), name="company-detail"),
]
