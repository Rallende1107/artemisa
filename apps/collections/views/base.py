from django.http import Http404
from django.utils.translation import gettext_lazy as _

from apps.collections.models import AlbumCollection, AnimeCollection, ArtistCollection, CharacterCollection, CollectionLog, CompanyCollection, GameCharacterCollection, GameCollection, MangaCollection, ModelBaseCollection, MovieCollection, PersonCollection, SerieCollection, SongCollection


class _Collections:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-collections-home"
    section_url = "panel:collections-home"
    section_label = _("Colecciones")


class BaseAlbumCollection(_Collections):
    model = AlbumCollection
    entity = "album-collection"
    label = _("colección de álbumes")
    label_plural = _("colecciones de álbumes")
    background_image = "bg-coleccions-albums"


class BaseAnimeCollection(_Collections):
    model = AnimeCollection
    entity = "anime-collection"
    label = _("colección de anime")
    label_plural = _("colecciones de anime")
    background_image = "bg-coleccions-animes"


class BaseArtistCollection(_Collections):
    model = ArtistCollection
    entity = "artist-collection"
    label = _("colección de artistas")
    label_plural = _("colecciones de artistas")
    background_image = "bg-coleccions-artists"


class BaseCharacterCollection(_Collections):
    model = CharacterCollection
    entity = "character-collection"
    label = _("colección de personajes")
    label_plural = _("colecciones de personajes")
    background_image = "bg-coleccions-characters"


class BaseCompanyCollection(_Collections):
    model = CompanyCollection
    entity = "company-collection"
    label = _("colección de compañías")
    label_plural = _("colecciones de compañías")
    background_image = "bg-coleccions-companies"


class BaseGameCharacterCollection(_Collections):
    model = GameCharacterCollection
    entity = "game-character-collection"
    label = _("colección de personajes de juego")
    label_plural = _("colecciones de personajes de juego")
    background_image = "bg-coleccions-game-characters"


class BaseGameCollection(_Collections):
    model = GameCollection
    entity = "game-collection"
    label = _("colección de juegos")
    label_plural = _("colecciones de juegos")
    background_image = "bg-coleccions-games"


class BaseMangaCollection(_Collections):
    model = MangaCollection
    entity = "manga-collection"
    label = _("colección de manga")
    label_plural = _("colecciones de manga")
    background_image = "bg-coleccions-mangas"


class BaseMovieCollection(_Collections):
    model = MovieCollection
    entity = "movie-collection"
    label = _("colección de películas")
    label_plural = _("colecciones de películas")
    background_image = "bg-coleccions-movies"


class BasePersonCollection(_Collections):
    model = PersonCollection
    entity = "person-collection"
    label = _("colección de personas")
    label_plural = _("colecciones de personas")
    background_image = "bg-coleccions-people"


class BaseSerieCollection(_Collections):
    model = SerieCollection
    entity = "serie-collection"
    label = _("colección de series")
    label_plural = _("colecciones de series")
    background_image = "bg-coleccions-series"


class BaseSongCollection(_Collections):
    model = SongCollection
    entity = "song-collection"
    label = _("colección de canciones")
    label_plural = _("colecciones de canciones")
    background_image = "bg-coleccions-songs"


class BaseCollectionLog(_Collections):
    model = CollectionLog
    entity = "collection-log"
    label = _("log de colecciones")
    label_plural = _("log de colecciones")
    background_image = "bg-collections-log"


# Vistas de la colección del usuario ("Mi colección"): dashboard, lista por medio,
# añadir, quitar, actualizar (estado / puntuación / favorito) y la
# página de EDICIÓN del ítem (seguimiento + dónde lo veo / lo descargué).
#
# Cada medio tiene SU tabla (AnimeCollection, MovieCollection… personajes y personas incluidos);
# `ModelBaseCollection` (core) la encuentra por su clave (`medio()`, el nombre del modelo de
# contenido) o por el modelo. Las URLs llevan esa clave (/collection/anime/…) porque el pk
# de una fila solo es único dentro de su tabla.

def _next(request, default="collections:mine"):
    return request.POST.get("next") or default


def _tabla_o_404(tipo):
    tabla = ModelBaseCollection.por_medio(tipo)
    if tabla is None:
        raise Http404("Colección desconocida")
    return tabla


def _titulo_fila(fila):
    """Texto de la fila: el título del contenido con su año si lo tiene (películas y
    series iguales se distinguen por el año, como en el panel)."""
    from core.shared.forms.widgets import etiqueta_select
    return etiqueta_select(fila.content)
