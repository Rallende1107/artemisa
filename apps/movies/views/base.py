"""BASE de la sección: config por entidad (clases privadas) + constantes de columnas.

La clase privada `_Entidad` es la única fuente de config compartida; las vistas
de los módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.movies.models import Genre, GenreAlias, Movie, MovieCast, MovieImage, MovieLog, MovieRelation, MovieStaff, MovieTitle, Rating, Role, Type


# NAV PÚBLICO de la sección: las pastillas que se ven en las páginas públicas de esta app. Cada entrada es
#   (etiqueta, ruta, icono, {nombres de ruta donde queda ACTIVA})
# y la resuelve `core.context_processors.seccion_nav` (calcula el href y cuál se enciende). Se declara en
# `nav`; una vista puede pisarlo con el suyo, o con () para no pintar barra.
NAV_PUBLICO = (
    (_("Películas"), "movies:home", "bi-film", {"home"}),
    (_("Lista"), "movies:movies-catalog", "bi-list-ul", {"movies-catalog", "movie-detail", "movies-by", "cast-by", "crew-by", "movie-images-by"}),
    (_("Productoras"), "movies:producers-catalog", "bi-building", {"producers", "producers-catalog", "company-detail"}),
    (_("Distribuidoras"), "movies:distributors-catalog", "bi-truck", {"distributors", "distributors-catalog"}),
)


class _Movies:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-movies-home"   # respaldo si falta la imagen
    section_url = "panel:movies-home"
    section_label = _("Películas")
    nav = NAV_PUBLICO          # las pastillas públicas de la sección


class BaseCompany(_Movies):
    """La compañía GLOBAL (apps/companies) vista desde cine: la usan los catálogos públicos de productoras y
    distribuidoras. Su CRUD vive en su app; la entidad apunta allí."""
    model = Company
    entity = 'company'
    label = _('compañía')
    label_plural = _('compañías')
    background_image = "bg-movies-company"


class BaseGenre(_Movies):
    model = Genre
    entity = 'movie-genre'
    label = _('género')
    label_plural = _('géneros')
    background_image = "bg-movies-genre"


class BaseGenreAlias(_Movies):
    model = GenreAlias
    entity = 'movie-genre-alias'
    label = _('alias de género')
    label_plural = _('alias de géneros')
    background_image = "bg-movies-genre"          # mismo fondo que su padre


class BaseGenreAliasContext(BaseGenreAlias):
    """Mapa «por» de alias: por su género (/panel/movie-genre-alias/genre/<id>/)."""
    filter_config = {
        "genre": ("genre", _("Alias de géneros de {padre}"), "bg-movies-genre"),
    }


class BaseMovie(_Movies):
    model = Movie
    entity = 'movie'
    label = _('película')
    label_plural = _('películas')
    background_image = "bg-movies-movie"


class BaseMovieCast(_Movies):
    model = MovieCast
    entity = 'movie-cast'
    label = _('reparto')
    label_plural = _('reparto')
    background_image = "bg-movies-movie-cast"


class BaseMovieCastContext(BaseMovieCast):
    """Mapa «por» de reparto: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "pelicula": ("movie", _("Reparto de {padre}"), "bg-movies-movie"),
        "persona": ("person", _("Reparto de {padre}"), ""),
    }


class BaseMovieContext(BaseMovie):
    """Mapa «por» de películas: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("genres", _("Películas del género {padre}"), "bg-movies-genre"),
        "productora": ("producers", _("Películas producidas por {padre}"), "bg-movies-company"),
        "distribuidora": ("distributors", _("Películas distribuidas por {padre}"), "bg-movies-company"),
        "tipo": ("movie_type", _("Películas de tipo {padre}"), "bg-movies-type"),
        "clasificacion": ("movie_rating", _("Películas con clasificación {padre}"), "bg-movies-rating"),
        "persona": ("people.Person", _("Películas de {padre}"), "bg-movies-movie"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "persona":
            return qs.filter(Q(cast__person=padre) | Q(staff__person=padre))
        return super().filter_by(qs, padre, tipo)


class BaseMovieImage(_Movies):
    model = MovieImage
    entity = 'movie-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-movies-movie-image"


class BaseMovieImageContext(BaseMovieImage):
    """Mapa «por» de imágenes extra de película: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "pelicula": ("movie", _("Imágenes de {padre}"), "bg-movies-movie"),
    }


class BaseMovieRelation(_Movies):
    model = MovieRelation
    entity = 'movie-relation'
    label = _('relación')
    label_plural = _('relaciones')
    background_image = "bg-movies-movie-relation"
    background_fallback = "bg-movies-movie"


class BaseMovieRelationContext(BaseMovieRelation):
    """Mapa «por» de relaciones: por película y por tipo de relación."""
    filter_config = {
        "pelicula": ("movie", _("Relaciones de {padre}"), "bg-movies-movie"),
        "tipo": ("relation_type", _("Relaciones de tipo {padre}"), ""),
    }


class BaseMovieStaff(_Movies):
    model = MovieStaff
    entity = 'movie-staff'
    label = _('equipo')
    label_plural = _('equipo')
    background_image = "bg-movies-movie-staff"


class BaseMovieStaffContext(BaseMovieStaff):
    """Mapa «por» de equipo: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "pelicula": ("movie", _("Equipo de {padre}"), "bg-movies-movie"),
        "persona": ("person", _("Equipo de {padre}"), ""),
    }


class BaseMovieTitle(_Movies):
    model = MovieTitle
    entity = 'movie-title'
    label = _('título')
    label_plural = _('títulos alternativos')
    background_image = "bg-movies-title-movie"


class BaseMovieTitleContext(BaseMovieTitle):
    """Mapa «por» de títulos de película: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "pelicula": ("movie", _("Títulos alternativos de {padre}"), ""),
    }


class BaseRating(_Movies):
    model = Rating
    entity = 'movie-rating'
    label = _('clasificación')
    label_plural = _('clasificaciones')
    background_image = "bg-movies-rating"


class BaseRole(_Movies):
    model = Role
    entity = 'movie-role'
    label = _('rol')
    label_plural = _('roles')
    background_image = "bg-movies-role"


class BaseRoleContext(BaseRole):
    """Mapa «por» de roles: `type` acota por la familia fija (`RoleType`): /movie-role/type/<valor>/."""
    filter_config = {
        "type": ("type", _("Roles de películas · {valor}"), "bg-movies-role"),
    }


class BaseType(_Movies):
    model = Type
    entity = 'movie-type'
    label = _('tipo')
    label_plural = _('tipos')
    background_image = "bg-movies-type"


class BaseMovieLog(_Movies):
    model = MovieLog
    entity = 'movie-log'
    label = _('log')
    label_plural = _('log de películas')
    background_image = "bg-movies-log"
