"""BASE de la sección: config por entidad (clases privadas) + constantes de columnas.

La clase privada `_Entidad` es la única fuente de config compartida; las vistas
de los módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.utils.translation import gettext_lazy as _

from apps.games.models import Character, CharacterImage, CharacterRole, Creator, CreatorLink, CreatorNickname, DataF95Creator, DataF95Game, DataVndbCharacter, DataVndbCreator, DataVndbGame, DataVndbRelease, DevelopmentEngine, Game, GameImage, GameLink, GameLog, GameTitle, Genre, GenreAlias, Medium, Platform, Release, ReleaseImage, Tag, TagAlias


# NAV PÚBLICO de la sección: las pastillas que se ven en las páginas públicas de esta app. Cada entrada es
#   (etiqueta, ruta, icono, {nombres de ruta donde queda ACTIVA})
# y la resuelve `core.context_processors.seccion_nav` (calcula el href y cuál se enciende). Se declara en
# `nav`; una vista puede pisarlo con el suyo, o con () para no pintar barra.
NAV_PUBLICO = (
    (_("Inicio"), "games:home", "bi-house", {"home"}),
    (_("Juegos"), "games:games-catalog", "bi-list-ul", {"games-catalog", "game-detail", "games-by", "character-detail", "characters-by", "releases-by", "game-images-by"}),
    (_("Creadores"), "games:creators-catalog", "bi-person-badge", {"creators", "creators-catalog", "creators-by", "creator-detail"}),
)


class _Games:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-games-home"   # respaldo si falta la imagen
    section_url = "panel:games-home"
    section_label = _("Juegos")
    nav = NAV_PUBLICO          # las pastillas públicas de la sección


class BaseCharacter(_Games):
    model = Character
    entity = 'game-character'
    label = _('personaje de juego')
    label_plural = _('personajes de juego')
    background_image = "bg-games-game-character"


class BaseCharacterContext(BaseCharacter):
    """Mapa «por» de personajes de juego: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "juego": ("games.Game", _("Personajes de {padre}"), "bg-games-game-character"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "juego":
            return qs.filter(roles__game=padre, roles__is_active=True)
        return super().filter_by(qs, padre, tipo)


class BaseCharacterImage(_Games):
    model = CharacterImage
    entity = 'game-character-image'
    label = _('imagen de personaje')
    label_plural = _('imágenes de personaje de juego')
    background_image = "bg-games-game-character-image"


class BaseCharacterImageContext(BaseCharacterImage):
    """Mapa «por» de imágenes de personaje de juego: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "juego-personaje": ("character", _("Imágenes de personaje de juego de {padre}"), ""),
    }


class BaseCharacterRole(_Games):
    model = CharacterRole
    entity = 'game-character-role'
    label = _('rol de personaje')
    label_plural = _('roles de personaje')
    background_image = "bg-games-game-character-role"


class BaseCharacterRoleContext(BaseCharacterRole):
    """Mapa «por» de roles de personaje: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "juego-personaje": ("character", _("Roles de personaje de {padre}"), ""),
        "juego": ("game", _("Roles de personaje de {padre}"), ""),
    }


class BaseCreator(_Games):
    model = Creator
    entity = 'creator'
    label = _('creador')
    label_plural = _('creadores')
    background_image = "bg-games-creator"


class BaseCreatorContext(BaseCreator):
    """Mapa «por» de creadores: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "idioma": ("languages", _("Creadores en {padre}"), "bg-catalogs-language"),
        "type": ("type", _("Creadores · {valor}"), "bg-games-creator"),
    }


class BaseCreatorLink(_Games):
    model = CreatorLink
    entity = 'creator-link'
    label = _('enlace')
    label_plural = _('enlaces')
    background_image = "bg-games-creator-link"


class BaseCreatorLinkContext(BaseCreatorLink):
    """Mapa «por» de enlaces de creador: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "creador": ("creator", _("Enlaces de {padre}"), ""),
    }


class BaseCreatorNickname(_Games):
    model = CreatorNickname
    entity = 'creator-nickname'
    label = _('apodo')
    label_plural = _('apodos')
    background_image = "bg-games-creator-nickname"


class BaseCreatorNicknameContext(BaseCreatorNickname):
    """Mapa «por» de apodos de creador: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "creador": ("creator", _("Apodos de {padre}"), ""),
    }


class BaseDataF95Creator(_Games):
    model = DataF95Creator
    entity = 'data-f95-creator'
    label = _('datos de creador (F95)')
    label_plural = _('datos · Creador (F95)')
    title_create = _("Crear datos de creador (F95)")
    title_delete = _("Eliminar datos de creador (F95)")
    title_update = _("Editar datos de creador (F95)")
    title_list = _("Lista de datos · Creador (F95)")   # el título de la PÁGINA (la lista lo toma de aquí)
    background_image = "bg-games-data-f95-creator"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataF95Game(_Games):
    model = DataF95Game
    entity = 'data-f95-game'
    label = _('datos de juego (F95)')
    label_plural = _('datos · Juego (F95)')
    title_create = _("Crear datos de juego (F95)")
    title_delete = _("Eliminar datos de juego (F95)")
    title_update = _("Editar datos de juego (F95)")
    title_list = _("Lista de datos · Juego (F95)")   # el título de la PÁGINA (la lista lo toma de aquí)
    background_image = "bg-games-data-f95-game"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataVndbCharacter(_Games):
    model = DataVndbCharacter
    entity = 'data-vndb-character'
    label = _('datos de personaje')
    label_plural = _('datos · Personaje (VNDB)')
    title_create = _("Crear datos de personaje (VNDB)")
    title_delete = _("Eliminar datos de personaje")
    title_update = _("Editar datos de personaje")
    title_list = _("Lista de datos · Personaje (VNDB)")   # el título de la PÁGINA (la lista lo toma de aquí)
    background_image = "bg-games-data-vndb-character"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataVndbCreator(_Games):
    model = DataVndbCreator
    entity = 'data-vndb-creator'
    label = _('datos de creador')
    label_plural = _('datos · Creador (VNDB)')
    title_create = _("Crear datos de creador (VNDB)")
    title_delete = _("Eliminar datos de creador")
    title_update = _("Editar datos de creador")
    title_list = _("Lista de datos · Creador (VNDB)")   # el título de la PÁGINA (la lista lo toma de aquí)
    background_image = "bg-games-data-vndb-creator"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataVndbGame(_Games):
    model = DataVndbGame
    entity = 'data-vndb-game'
    label = _('datos de juego')
    label_plural = _('datos · Juego (VNDB)')
    title_create = _("Crear datos de juego (VNDB)")
    title_delete = _("Eliminar datos de juego")
    title_update = _("Editar datos de juego")
    title_list = _("Lista de datos · Juego (VNDB)")   # el título de la PÁGINA (la lista lo toma de aquí)
    background_image = "bg-games-data-vndb-game"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataVndbRelease(_Games):
    model = DataVndbRelease
    entity = 'data-vndb-release'
    label = _('datos de lanzamiento')
    label_plural = _('datos · Lanzamiento (VNDB)')
    title_create = _("Crear datos de lanzamiento (VNDB)")
    title_delete = _("Eliminar datos de lanzamiento")
    title_update = _("Editar datos de lanzamiento")
    title_list = _("Lista de datos · Lanzamiento (VNDB)")   # el título de la PÁGINA (la lista lo toma de aquí)
    background_image = "bg-games-data-vndb-release"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDevelopmentEngine(_Games):
    model = DevelopmentEngine
    entity = 'game-engine'
    label = _('motor')
    label_plural = _('motores')
    background_image = "bg-games-development-engine"


class BaseGame(_Games):
    model = Game
    entity = 'game'
    label = _('juego')
    label_plural = _('juegos')
    background_image = "bg-games-game"


class BaseGameContext(BaseGame):
    """Mapa «por» de juegos: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("genres", _("Juegos del género {padre}"), "bg-games-genre"),
        "plataforma": ("platforms", _("Juegos en {padre}"), "bg-games-platform"),
        "idioma": ("languages", _("Juegos en {padre}"), "bg-catalogs-language"),
        "motor": ("engine", _("Juegos hechos con {padre}"), "bg-games-development-engine"),
        "medio": ("mediums", _("Juegos en {padre}"), "bg-games-medium"),
        "creador": ("developers", _("Juegos desarrollados por {padre}"), "bg-games-creator"),
        "editora": ("publishers", _("Juegos editados por {padre}"), "bg-games-creator"),
        "type": ("type", _("Juegos · {valor}"), "bg-games-game"),
        "status": ("status", _("Juegos · {valor}"), "bg-games-game"),
    }


class BaseGameImage(_Games):
    model = GameImage
    entity = 'game-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-games-game-image"


class BaseGameImageContext(BaseGameImage):
    """Mapa «por» de imágenes extra de juego: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "juego": ("game", _("Imágenes de {padre}"), "bg-games-game"),
    }


class BaseGameLink(_Games):
    model = GameLink
    entity = 'game-link'
    label = _('enlace')
    label_plural = _('enlaces')
    background_image = "bg-games-game-link"


class BaseGameLinkContext(BaseGameLink):
    """Mapa «por» de enlaces de juego: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "juego": ("game", _("Enlaces de {padre}"), ""),
    }


class BaseGameTitle(_Games):
    model = GameTitle
    entity = 'game-title'
    label = _('título')
    label_plural = _('títulos')
    background_image = "bg-games-title-game"


class BaseGameTitleContext(BaseGameTitle):
    """Mapa «por» de títulos de juego: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "juego": ("game", _("Títulos de {padre}"), ""),
    }


class BaseGenre(_Games):
    model = Genre
    entity = 'game-genre'
    label = _('género')
    label_plural = _('géneros')
    background_image = "bg-games-genre"


class BaseGenreAlias(_Games):
    model = GenreAlias
    entity = 'game-genre-alias'
    label = _('alias de género')
    label_plural = _('alias de géneros')
    background_image = "bg-games-genre-alias"          # mismo fondo que su padre


class BaseGenreAliasContext(BaseGenreAlias):
    """Mapa «por» de alias: por su género (/panel/game-genre-alias/genre/<id>/)."""
    filter_config = {
        "genre": ("genre", _("Alias de géneros de {padre}"), "bg-games-genre"),
    }


class BaseMedium(_Games):
    model = Medium
    entity = 'game-medium'
    label = _('medio')
    label_plural = _('medios')
    background_image = "bg-games-medium"


class BasePlatform(_Games):
    model = Platform
    entity = 'game-platform'
    label = _('plataforma')
    label_plural = _('plataformas')
    background_image = "bg-games-platform"


class BaseRelease(_Games):
    model = Release
    entity = 'game-release'
    label = _('lanzamiento de juego')
    label_plural = _('lanzamientos de juego')
    background_image = "bg-games-game-release"


# Vistas públicas de la sección Juegos: home (portada) + catálogo + ficha.
#
# Vistas EXPLÍCITAS (estilo Hades): CBVs de Django directas con su contexto.
# Las filas del home y las tarjetas salen de la BD real (nada hardcodeado).


class BaseReleaseContext(BaseRelease):
    """Mapa «por» de lanzamientos de juego: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "juego": ("games.Game", _("Lanzamientos de {padre}"), "bg-games-game-release"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "juego":
            return qs.filter(game=padre)
        return super().filter_by(qs, padre, tipo)


class BaseReleaseImage(_Games):
    model = ReleaseImage
    entity = 'game-release-image'
    label = _('imagen de lanzamiento')
    label_plural = _('imágenes de lanzamiento')
    background_image = "bg-games-game-release-image"          # mismo fondo que su padre


class BaseReleaseImageContext(BaseReleaseImage):
    """Mapa «por» de imágenes de lanzamiento: por su lanzamiento (/panel/game-release-image/release/<id>/)."""
    filter_config = {
        "release": ("release", _("Imágenes de {padre}"), "bg-games-game-release-image"),
    }


def _sub_juego(g):
    return str(g.release_date.year) if g.release_date else (g.version or "")


class BaseTag(_Games):
    model = Tag
    entity = "tag"
    label = _("etiqueta")
    label_plural = _("etiquetas")
    background_image = "bg-games-tag"


class BaseTagAlias(_Games):
    model = TagAlias
    entity = 'tag-alias'
    label = _('alias de etiqueta')
    label_plural = _('alias de etiquetas')
    background_image = "bg-games-tag-alias"          # mismo fondo que su padre


class BaseTagAliasContext(BaseTagAlias):
    """Mapa «por» de alias: por su etiqueta (/panel/tag-alias/tag/<id>/)."""
    filter_config = {
        "tag": ("tag", _("Alias de etiquetas de {padre}"), "bg-games-tag"),
    }


class BaseGameLog(_Games):
    model = GameLog
    entity = 'game-log'
    label = _('log')
    label_plural = _('log de juegos')
    background_image = "bg-games-log"
