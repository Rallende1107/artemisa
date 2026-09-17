"""movies · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.movies.views.base import BaseGenre, BaseGenreAlias, BaseMovie, BaseMovieCast, BaseMovieImage, BaseMovieLog, BaseMovieRelation, BaseMovieStaff, BaseMovieTitle, BaseRating, BaseRole, BaseType
from core.shared.views.base import BaseAdminDetailView, BasePublicDetailView


# ==============================================================================
# Gestión
# ==============================================================================


class GenreDetailView(BaseGenre, BaseAdminDetailView):
    template_name = "movies/detail/genre.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-genre_update"
    delete_url = "panel:movie-genre_delete"
    list_url = "panel:movie-genre_list"
    toggle_url = "panel:movie-genre_toggle"


class MovieDetailView(BaseMovie, BaseAdminDetailView):
    template_name = "movies/detail/movie.html"   # la misma ficha que el público, con los botones de gestión
    update_url = "panel:movie_update"
    delete_url = "panel:movie_delete"
    list_url = "panel:movie_list"
    toggle_url = "panel:movie_toggle"
    by_url = "panel:movie_by"
    tabs = [("reparto", _("Reparto"), "panel:movie-cast_by", "pelicula"),
            ("equipo", _("Equipo"), "panel:movie-staff_by", "pelicula"),
            ("imagenes", _("Imágenes"), "panel:movie-image_by", "pelicula"),
            ("relaciones", _("Relaciones"), "panel:movie-relation_by", "pelicula"),
            ("titulos", _("Títulos"), "panel:movie-title_by", "pelicula")]


class MovieCastDetailView(BaseMovieCast, BaseAdminDetailView):
    template_name = "movies/detail/movie_cast.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-cast_update"
    delete_url = "panel:movie-cast_delete"
    list_url = "panel:movie-cast_list"
    toggle_url = "panel:movie-cast_toggle"


class MovieImageDetailView(BaseMovieImage, BaseAdminDetailView):
    template_name = "movies/detail/movie_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-image_update"
    delete_url = "panel:movie-image_delete"
    list_url = "panel:movie-image_list"
    toggle_url = "panel:movie-image_toggle"


class MovieRelationDetailView(BaseMovieRelation, BaseAdminDetailView):
    template_name = "movies/detail/movie_relation.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-relation_update"
    delete_url = "panel:movie-relation_delete"
    list_url = "panel:movie-relation_list"
    toggle_url = "panel:movie-relation_toggle"


class MovieStaffDetailView(BaseMovieStaff, BaseAdminDetailView):
    template_name = "movies/detail/movie_staff.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-staff_update"
    delete_url = "panel:movie-staff_delete"
    list_url = "panel:movie-staff_list"
    toggle_url = "panel:movie-staff_toggle"


class MovieTitleDetailView(BaseMovieTitle, BaseAdminDetailView):
    template_name = "movies/detail/movie_title.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-title_update"
    delete_url = "panel:movie-title_delete"
    list_url = "panel:movie-title_list"
    toggle_url = "panel:movie-title_toggle"


class RatingDetailView(BaseRating, BaseAdminDetailView):
    template_name = "movies/detail/rating.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-rating_update"
    delete_url = "panel:movie-rating_delete"
    list_url = "panel:movie-rating_list"
    toggle_url = "panel:movie-rating_toggle"


class RoleDetailView(BaseRole, BaseAdminDetailView):
    template_name = "movies/detail/role.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-role_update"
    delete_url = "panel:movie-role_delete"
    list_url = "panel:movie-role_list"
    toggle_url = "panel:movie-role_toggle"


class TypeDetailView(BaseType, BaseAdminDetailView):
    template_name = "movies/detail/type.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-type_update"
    delete_url = "panel:movie-type_delete"
    list_url = "panel:movie-type_list"
    toggle_url = "panel:movie-type_toggle"


class MovieLogDetailView(BaseMovieLog, BaseAdminDetailView):
    template_name = "movies/detail/movie_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:movie-log_update"
    delete_url = "panel:movie-log_delete"
    list_url = "panel:movie-log_list"


# ==============================================================================
# Público
# ==============================================================================


class GenreAliasDetailView(BaseGenreAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:movie-genre-alias_list"
    update_url = "panel:movie-genre-alias_update"
    delete_url = "panel:movie-genre-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Género', 'genre')]


class MoviePublicDetailView(BaseMovie, BasePublicDetailView):
    """Ficha pública de una película: el mismo HTML que en gestión, sin botones y con la colección."""
    template_name = "movies/detail/movie.html"
    list_url = "movies:movies-catalog"
    by_url = "movies:movies-by"
    section = "peliculas"
    collect_kind = "movie"
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    tabs = [("reparto", _("Reparto"), "movies:cast-by", "pelicula"),
            ("equipo", _("Equipo"), "movies:crew-by", "pelicula"),
            ("imagenes", _("Imágenes"), "movies:movie-images-by", "pelicula")]
