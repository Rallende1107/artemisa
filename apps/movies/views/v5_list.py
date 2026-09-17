"""movies · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.movies.views.base import BaseCompany, BaseGenre, BaseGenreAlias, BaseGenreAliasContext, BaseMovie, BaseMovieCast, BaseMovieImage, BaseMovieLog, BaseMovieRelation, BaseMovieStaff, BaseMovieTitle, BaseRating, BaseRole, BaseRoleContext, BaseType
from core.shared.views.base import AdminListByView, AdminListView, PublicListView


# ==============================================================================
# Gestión
# ==============================================================================


class GenreListView(BaseGenre, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-genre_data"
    create_url = "panel:movie-genre_create"
    title = _("Lista de géneros")


class MovieListView(BaseMovie, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie_data"
    create_url = "panel:movie_create"
    title = _("Lista de películas")


class MovieCastListView(BaseMovieCast, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-cast_data"
    create_url = "panel:movie-cast_create"
    title = _("Lista de reparto")


class MovieImageListView(BaseMovieImage, AdminListView):
    home_url = "panel:movies-home"
    buttons = (("panel:movie-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:movie-image_data"
    create_url = "panel:movie-image_create"
    title = _("Lista de imágenes extra")


class MovieRelationListView(BaseMovieRelation, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-relation_data"
    create_url = "panel:movie-relation_create"
    title = _("Lista de relaciones")


class MovieStaffListView(BaseMovieStaff, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-staff_data"
    create_url = "panel:movie-staff_create"
    title = _("Lista de equipo")


class MovieTitleListView(BaseMovieTitle, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-title_data"
    create_url = "panel:movie-title_create"
    title = _("Lista de títulos alternativos")


class RatingListView(BaseRating, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-rating_data"
    create_url = "panel:movie-rating_create"
    title = _("Lista de clasificaciones")


class RoleListView(BaseRole, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-role_data"
    create_url = "panel:movie-role_create"
    title = _("Lista de roles")


class TypeListView(BaseType, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-type_data"
    create_url = "panel:movie-type_create"
    title = _("Lista de tipos")


class MovieLogListView(BaseMovieLog, AdminListView):
    home_url = "panel:movies-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:movie-log_data"
    create_url = "panel:movie-log_create"
    title = _("Lista de log de películas")


# ==============================================================================
# Público
# ==============================================================================

# ==============================================================================
# Catálogos sobre la base NUEVA (PublicListView + PublicDataView por data_url)
# ==============================================================================


class ProducerPublicListView(BaseCompany, PublicListView):
    """Catálogo de PRODUCTORAS de cine (con buscador y filtros)."""
    data_url = "movies:producers-catalog-data"
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    section = "peliculas"
    title = _("Productoras")
    icon = "bi-building"
    subtitle = _("Compañías productoras y distribuidoras de cine.")
    home_url = "movies:home"
    home_label = _("películas")


class DistributorPublicListView(BaseCompany, PublicListView):
    """Catálogo de DISTRIBUIDORAS de cine (con buscador y filtros)."""
    data_url = "movies:distributors-catalog-data"
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    section = "peliculas"
    title = _("Distribuidoras")
    icon = "bi-building"
    subtitle = _("Compañías que distribuyen películas.")
    home_url = "movies:home"
    home_label = _("películas")


class GenreAliasListView(BaseGenreAlias, AdminListView):
    home_url = "panel:movies-home"
    data_url = "panel:movie-genre-alias_data"
    create_url = "panel:movie-genre-alias_create"
    title = _("Lista de alias de géneros")


class GenreAliasListByView(BaseGenreAliasContext, AdminListByView):
    """Alias acotados por su padre (`/movie-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`."""
    home_url = "panel:movies-home"
    create_url = "panel:movie-genre-alias_create"
    data_url = "panel:movie-genre-alias_data-by"
    full_list_url = "panel:movie-genre-alias_list"
    by_url = "panel:movie-genre-alias_by"


class MoviePublicListView(BaseMovie, PublicListView):
    data_url = "movies:movies-catalog-data"
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    section = "peliculas"
    title = _("Películas")
    icon = "bi-film"
    home_url = "movies:home"
    home_label = _("películas")


class RoleListByView(BaseRoleContext, AdminListByView):
    """Lista de roles acotada por familia (`/movie-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`."""
    home_url = "panel:movies-home"
    create_url = "panel:movie-role_create"
    data_url = "panel:movie-role_data-by"
    full_list_url = "panel:movie-role_list"
    by_url = "panel:movie-role_by"
