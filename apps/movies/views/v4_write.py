"""movies · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.movies import forms as f
from apps.movies.views.base import BaseGenre, BaseGenreAlias, BaseMovie, BaseMovieCast, BaseMovieImage, BaseMovieLog, BaseMovieRelation, BaseMovieStaff, BaseMovieTitle, BaseRating, BaseRole, BaseType
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class GenreCreateView(BaseGenre, BaseCreate):
    # Django core
    form_class = f.GenreForm
    form_template = "movies/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-genre_list"
    success_url = "panel:movie-genre_list"
    cancel_url = "panel:movie-genre_list"
    # UX
    success_message = _("Género «%(obj)s» creado.")
    title = _("Crear género")


class GenreUpdateView(BaseGenre, BaseUpdate):
    # Django core
    form_class = f.GenreForm
    form_template = "movies/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-genre_list"
    success_url = "panel:movie-genre_list"
    cancel_url = "panel:movie-genre_list"
    # UX
    success_message = _("Género «%(obj)s» actualizado.")
    title = _("Editar género")


class GenreDeleteView(BaseGenre, BaseDelete):
    list_url = "panel:movie-genre_list"
    success_url = "panel:movie-genre_list"
    cancel_url = "panel:movie-genre_list"
    success_message = _("Género «%(obj)s» eliminado.")
    title = _("Eliminar género")


class GenreAliasCreateView(BaseGenreAlias, BaseCreate):
    form_class = f.GenreAliasForm
    list_url = "panel:movie-genre-alias_list"
    success_url = "panel:movie-genre-alias_list"
    cancel_url = "panel:movie-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» creado.")
    title = _("Crear alias de género")


class GenreAliasUpdateView(BaseGenreAlias, BaseUpdate):
    form_class = f.GenreAliasForm
    list_url = "panel:movie-genre-alias_list"
    success_url = "panel:movie-genre-alias_list"
    cancel_url = "panel:movie-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» actualizado.")
    title = _("Editar alias de género")


class GenreAliasDeleteView(BaseGenreAlias, BaseDelete):
    list_url = "panel:movie-genre-alias_list"
    success_url = "panel:movie-genre-alias_list"
    cancel_url = "panel:movie-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» eliminado.")
    title = _("Eliminar alias de género")


class MovieCreateView(BaseMovie, BaseCreate):
    # Django core
    form_class = f.MovieForm
    form_template = "movies/form/movie.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie_list"
    success_url = "panel:movie_list"
    cancel_url = "panel:movie_list"
    # UX
    success_message = _("Película «%(obj)s» creada.")
    title = _("Crear película")


class MovieUpdateView(BaseMovie, BaseUpdate):
    # Django core
    form_class = f.MovieForm
    form_template = "movies/form/movie.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie_list"
    success_url = "panel:movie_list"
    cancel_url = "panel:movie_list"
    # UX
    success_message = _("Película «%(obj)s» actualizada.")
    title = _("Editar película")


class MovieDeleteView(BaseMovie, BaseDelete):
    list_url = "panel:movie_list"
    success_url = "panel:movie_list"
    cancel_url = "panel:movie_list"
    success_message = _("Película «%(obj)s» eliminada.")
    title = _("Eliminar película")


class MovieCastCreateView(BaseMovieCast, BaseCreate):
    # Django core
    form_class = f.MovieCastForm
    form_template = "movies/form/movie_cast.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-cast_list"
    success_url = "panel:movie-cast_list"
    cancel_url = "panel:movie-cast_list"
    # UX
    success_message = _("Reparto «%(obj)s» creado.")
    title = _("Crear reparto")


class MovieCastUpdateView(BaseMovieCast, BaseUpdate):
    # Django core
    form_class = f.MovieCastForm
    form_template = "movies/form/movie_cast.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-cast_list"
    success_url = "panel:movie-cast_list"
    cancel_url = "panel:movie-cast_list"
    # UX
    success_message = _("Reparto «%(obj)s» actualizado.")
    title = _("Editar reparto")


class MovieCastDeleteView(BaseMovieCast, BaseDelete):
    list_url = "panel:movie-cast_list"
    success_url = "panel:movie-cast_list"
    cancel_url = "panel:movie-cast_list"
    success_message = _("Reparto «%(obj)s» eliminado.")
    title = _("Eliminar reparto")


class MovieImageCreateView(BaseMovieImage, BaseCreate):
    # Django core
    form_class = f.MovieImageForm
    form_template = "movies/form/movie_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-image_list"
    success_url = "panel:movie-image_list"
    cancel_url = "panel:movie-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class MovieImageUpdateView(BaseMovieImage, BaseUpdate):
    # Django core
    form_class = f.MovieImageForm
    form_template = "movies/form/movie_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-image_list"
    success_url = "panel:movie-image_list"
    cancel_url = "panel:movie-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class MovieImageDeleteView(BaseMovieImage, BaseDelete):
    list_url = "panel:movie-image_list"
    success_url = "panel:movie-image_list"
    cancel_url = "panel:movie-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class MovieRelationCreateView(BaseMovieRelation, BaseCreate):
    form_class = f.MovieRelationForm
    form_template = "movies/form/movie_relation.html"
    list_url = "panel:movie-relation_list"
    success_url = "panel:movie-relation_list"
    cancel_url = "panel:movie-relation_list"
    success_message = _("Relación «%(obj)s» creada.")
    title = _("Crear relación")


class MovieRelationUpdateView(BaseMovieRelation, BaseUpdate):
    form_class = f.MovieRelationForm
    form_template = "movies/form/movie_relation.html"
    list_url = "panel:movie-relation_list"
    success_url = "panel:movie-relation_list"
    cancel_url = "panel:movie-relation_list"
    success_message = _("Relación «%(obj)s» actualizada.")
    title = _("Editar relación")


class MovieRelationDeleteView(BaseMovieRelation, BaseDelete):
    list_url = "panel:movie-relation_list"
    success_url = "panel:movie-relation_list"
    cancel_url = "panel:movie-relation_list"
    success_message = _("Relación «%(obj)s» eliminada.")
    title = _("Eliminar relación")


class MovieStaffCreateView(BaseMovieStaff, BaseCreate):
    # Django core
    form_class = f.MovieStaffForm
    form_template = "movies/form/movie_staff.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-staff_list"
    success_url = "panel:movie-staff_list"
    cancel_url = "panel:movie-staff_list"
    # UX
    success_message = _("Equipo «%(obj)s» creado.")
    title = _("Crear equipo")


class MovieStaffUpdateView(BaseMovieStaff, BaseUpdate):
    # Django core
    form_class = f.MovieStaffForm
    form_template = "movies/form/movie_staff.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-staff_list"
    success_url = "panel:movie-staff_list"
    cancel_url = "panel:movie-staff_list"
    # UX
    success_message = _("Equipo «%(obj)s» actualizado.")
    title = _("Editar equipo")


class MovieStaffDeleteView(BaseMovieStaff, BaseDelete):
    list_url = "panel:movie-staff_list"
    success_url = "panel:movie-staff_list"
    cancel_url = "panel:movie-staff_list"
    success_message = _("Equipo «%(obj)s» eliminado.")
    title = _("Eliminar equipo")


class MovieTitleCreateView(BaseMovieTitle, BaseCreate):
    # Django core
    form_class = f.MovieTitleForm
    form_template = "movies/form/movie_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-title_list"
    success_url = "panel:movie-title_list"
    cancel_url = "panel:movie-title_list"
    # UX
    success_message = _("Título «%(obj)s» creado.")
    title = _("Crear título")


class MovieTitleUpdateView(BaseMovieTitle, BaseUpdate):
    # Django core
    form_class = f.MovieTitleForm
    form_template = "movies/form/movie_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-title_list"
    success_url = "panel:movie-title_list"
    cancel_url = "panel:movie-title_list"
    # UX
    success_message = _("Título «%(obj)s» actualizado.")
    title = _("Editar título")


class MovieTitleDeleteView(BaseMovieTitle, BaseDelete):
    list_url = "panel:movie-title_list"
    success_url = "panel:movie-title_list"
    cancel_url = "panel:movie-title_list"
    success_message = _("Título «%(obj)s» eliminado.")
    title = _("Eliminar título")


class RatingCreateView(BaseRating, BaseCreate):
    # Django core
    form_class = f.RatingForm
    form_template = "movies/form/rating.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-rating_list"
    success_url = "panel:movie-rating_list"
    cancel_url = "panel:movie-rating_list"
    # UX
    success_message = _("Clasificación «%(obj)s» creada.")
    title = _("Crear clasificación")


class RatingUpdateView(BaseRating, BaseUpdate):
    # Django core
    form_class = f.RatingForm
    form_template = "movies/form/rating.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-rating_list"
    success_url = "panel:movie-rating_list"
    cancel_url = "panel:movie-rating_list"
    # UX
    success_message = _("Clasificación «%(obj)s» actualizada.")
    title = _("Editar clasificación")


class RatingDeleteView(BaseRating, BaseDelete):
    list_url = "panel:movie-rating_list"
    success_url = "panel:movie-rating_list"
    cancel_url = "panel:movie-rating_list"
    success_message = _("Clasificación «%(obj)s» eliminada.")
    title = _("Eliminar clasificación")


class RoleCreateView(BaseRole, BaseCreate):
    # Django core
    form_class = f.RoleForm
    form_template = "movies/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-role_list"
    success_url = "panel:movie-role_list"
    cancel_url = "panel:movie-role_list"
    # UX
    success_message = _("Rol «%(obj)s» creado.")
    title = _("Crear rol")


class RoleUpdateView(BaseRole, BaseUpdate):
    # Django core
    form_class = f.RoleForm
    form_template = "movies/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-role_list"
    success_url = "panel:movie-role_list"
    cancel_url = "panel:movie-role_list"
    # UX
    success_message = _("Rol «%(obj)s» actualizado.")
    title = _("Editar rol")


class RoleDeleteView(BaseRole, BaseDelete):
    list_url = "panel:movie-role_list"
    success_url = "panel:movie-role_list"
    cancel_url = "panel:movie-role_list"
    success_message = _("Rol «%(obj)s» eliminado.")
    title = _("Eliminar rol")


class TypeCreateView(BaseType, BaseCreate):
    # Django core
    form_class = f.TypeForm
    form_template = "movies/form/type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-type_list"
    success_url = "panel:movie-type_list"
    cancel_url = "panel:movie-type_list"
    # UX
    success_message = _("Tipo «%(obj)s» creado.")
    title = _("Crear tipo")


class TypeUpdateView(BaseType, BaseUpdate):
    # Django core
    form_class = f.TypeForm
    form_template = "movies/form/type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:movie-type_list"
    success_url = "panel:movie-type_list"
    cancel_url = "panel:movie-type_list"
    # UX
    success_message = _("Tipo «%(obj)s» actualizado.")
    title = _("Editar tipo")


class TypeDeleteView(BaseType, BaseDelete):
    list_url = "panel:movie-type_list"
    success_url = "panel:movie-type_list"
    cancel_url = "panel:movie-type_list"
    success_message = _("Tipo «%(obj)s» eliminado.")
    title = _("Eliminar tipo")


class MovieLogCreateView(BaseMovieLog, BaseCreate):
    form_class = f.MovieLogForm
    form_template = "movies/form/movie_log.html"
    list_url = "panel:movie-log_list"
    success_url = "panel:movie-log_list"
    cancel_url = "panel:movie-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class MovieLogUpdateView(BaseMovieLog, BaseUpdate):
    form_class = f.MovieLogForm
    form_template = "movies/form/movie_log.html"
    list_url = "panel:movie-log_list"
    success_url = "panel:movie-log_list"
    cancel_url = "panel:movie-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class MovieLogDeleteView(BaseMovieLog, BaseDelete):
    list_url = "panel:movie-log_list"
    success_url = "panel:movie-log_list"
    cancel_url = "panel:movie-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
