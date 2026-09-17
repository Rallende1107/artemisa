"""BASE de la sección: config por entidad (clases privadas) + constantes de columnas.

La clase privada `_Entidad` es la única fuente de config compartida; las vistas
de los módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.series.models import Genre, GenreAlias, Rating, Role, Serie, SerieCast, SerieImage, SerieLog, SerieRelation, SerieStaff, SerieTitle, Type


# NAV PÚBLICO de la sección: las pastillas que se ven en las páginas públicas de esta app. Cada entrada es
#   (etiqueta, ruta, icono, {nombres de ruta donde queda ACTIVA})
# y la resuelve `core.context_processors.seccion_nav` (calcula el href y cuál se enciende). Se declara en
# `nav`; una vista puede pisarlo con el suyo, o con () para no pintar barra.
NAV_PUBLICO = (
    (_("Series"), "series:home", "bi-collection-play", {"home"}),
    (_("Lista"), "series:series-catalog", "bi-list-ul", {"series-catalog", "serie-detail", "series-by", "cast-by", "crew-by", "serie-images-by"}),
    (_("Productoras"), "series:producers-catalog", "bi-building", {"producers", "producers-catalog", "company-detail"}),
    (_("Distribuidoras"), "series:distributors-catalog", "bi-truck", {"distributors", "distributors-catalog"}),
)


class _Series:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-series-home"   # respaldo si falta la imagen
    section_url = "panel:series-home"
    section_label = _("Series")
    nav = NAV_PUBLICO          # las pastillas públicas de la sección


class BaseCompany(_Series):
    """La compañía GLOBAL (apps/companies) vista desde TV: la usan los catálogos públicos de productoras y
    distribuidoras. Su CRUD vive en su app; la entidad apunta allí."""
    model = Company
    entity = 'company'
    label = _('compañía')
    label_plural = _('compañías')
    background_image = "bg-series-company"


class BaseGenre(_Series):
    model = Genre
    entity = 'serie-genre'
    label = _('género')
    label_plural = _('géneros')
    background_image = "bg-series-genre"


class BaseGenreAlias(_Series):
    model = GenreAlias
    entity = 'serie-genre-alias'
    label = _('alias de género')
    label_plural = _('alias de géneros')
    background_image = "bg-series-genre"          # mismo fondo que su padre


class BaseGenreAliasContext(BaseGenreAlias):
    """Mapa «por» de alias: por su género (/panel/serie-genre-alias/genre/<id>/)."""
    filter_config = {
        "genre": ("genre", _("Alias de géneros de {padre}"), "bg-series-genre"),
    }


class BaseRating(_Series):
    model = Rating
    entity = 'serie-rating'
    label = _('clasificación')
    label_plural = _('clasificaciones')
    background_image = "bg-series-rating"


class BaseRole(_Series):
    model = Role
    entity = 'serie-role'
    label = _('rol')
    label_plural = _('roles')
    background_image = "bg-series-role"


class BaseRoleContext(BaseRole):
    """Mapa «por» de roles: `type` acota por la familia fija (`RoleType`): /serie-role/type/<valor>/."""
    filter_config = {
        "type": ("type", _("Roles de series · {valor}"), "bg-series-role"),
    }


class BaseSerie(_Series):
    model = Serie
    entity = 'serie'
    label = _('series')
    label_plural = _('series')
    background_image = "bg-series-serie"


class BaseSerieCast(_Series):
    model = SerieCast
    entity = 'serie-cast'
    label = _('reparto')
    label_plural = _('reparto')
    background_image = "bg-series-serie-cast"


class BaseSerieCastContext(BaseSerieCast):
    """Mapa «por» de reparto: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "serie": ("serie", _("Reparto de {padre}"), "bg-series-serie"),
        "persona": ("person", _("Reparto de {padre}"), ""),
    }


class BaseSerieContext(BaseSerie):
    """Mapa «por» de series: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("genres", _("Series del género {padre}"), "bg-series-genre"),
        "productora": ("producers", _("Series producidas por {padre}"), "bg-series-company"),
        "distribuidora": ("distributors", _("Series distribuidas por {padre}"), "bg-series-company"),
        "tipo": ("serie_type", _("Series de tipo {padre}"), "bg-series-type"),
        "clasificacion": ("serie_rating", _("Series con clasificación {padre}"), "bg-series-rating"),
        "persona": ("people.Person", _("Series de {padre}"), "bg-series-serie"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "persona":
            return qs.filter(Q(cast__person=padre) | Q(staff__person=padre))
        return super().filter_by(qs, padre, tipo)


class BaseSerieImage(_Series):
    model = SerieImage
    entity = 'serie-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-series-serie-image"


class BaseSerieImageContext(BaseSerieImage):
    """Mapa «por» de imágenes extra de serie: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "serie": ("serie", _("Imágenes de {padre}"), "bg-series-serie"),
    }


class BaseSerieRelation(_Series):
    model = SerieRelation
    entity = 'serie-relation'
    label = _('relación')
    label_plural = _('relaciones')
    background_image = "bg-series-serie-relation"
    background_fallback = "bg-series-serie"


class BaseSerieRelationContext(BaseSerieRelation):
    """Mapa «por» de relaciones: por película y por tipo de relación."""
    filter_config = {
        "serie": ("serie", _("Relaciones de {padre}"), "bg-series-serie"),
        "tipo": ("relation_type", _("Relaciones de tipo {padre}"), ""),
    }


class BaseSerieStaff(_Series):
    model = SerieStaff
    entity = 'serie-staff'
    label = _('equipo')
    label_plural = _('equipo')
    background_image = "bg-series-serie-staff"


class BaseSerieStaffContext(BaseSerieStaff):
    """Mapa «por» de equipo: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "serie": ("serie", _("Equipo de {padre}"), "bg-series-serie"),
        "persona": ("person", _("Equipo de {padre}"), ""),
    }


class BaseSerieTitle(_Series):
    model = SerieTitle
    entity = 'serie-title'
    label = _('título')
    label_plural = _('títulos alternativos')
    background_image = "bg-series-title-serie"


class BaseSerieTitleContext(BaseSerieTitle):
    """Mapa «por» de títulos de serie: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "serie": ("serie", _("Títulos alternativos de {padre}"), ""),
    }


class BaseType(_Series):
    model = Type
    entity = 'serie-type'
    label = _('tipo')
    label_plural = _('tipos')
    background_image = "bg-series-type"


class BaseSerieLog(_Series):
    model = SerieLog
    entity = 'serie-log'
    label = _('log')
    label_plural = _('log de series')
    background_image = "bg-series-log"
