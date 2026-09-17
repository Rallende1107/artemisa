"""BASE de la sección: config por entidad (clases privadas) + constantes de columnas.

La clase privada `_Entidad` es la única fuente de config compartida; las vistas
de los módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.utils.translation import gettext_lazy as _

from apps.music.models import Album, AlbumImage, AlbumType, Artist, ArtistImage, ArtistMember, ArtistType, DataDeezerAlbum, DataDeezerArtist, DataDeezerGenre, DataDeezerTrack, Genre, GenreAlias, MusicLog, Role, Song, SongComposer, SongTranslation
from core.utils.public import cover_cards, resolve_cover


# NAV PÚBLICO de la sección: las pastillas que se ven en las páginas públicas de esta app. Cada entrada es
#   (etiqueta, ruta, icono, {nombres de ruta donde queda ACTIVA})
# y la resuelve `core.context_processors.seccion_nav` (calcula el href y cuál se enciende). Se declara en
# `nav`; una vista puede pisarlo con el suyo, o con () para no pintar barra.
NAV_PUBLICO = (
    (_("Música"), "music:home", "bi-music-note-beamed", {"home"}),
    (_("Álbumes"), "music:albums-catalog", "bi-disc", {"albums", "albums-catalog", "albums-by", "album-detail"}),
    (_("Artistas"), "music:artists-catalog", "bi-person-video2", {"artists", "artists-catalog", "artists-by", "artist-detail"}),
    (_("Canciones"), "music:songs-catalog", "bi-file-music", {"songs", "songs-catalog", "songs-by", "song-detail"}),
)


class _Music:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-music-home"   # respaldo si falta la imagen
    section_url = "panel:music-home"
    section_label = _("Música")
    nav = NAV_PUBLICO          # las pastillas públicas de la sección


class BaseAlbum(_Music):
    model = Album
    entity = 'album'
    label = _('álbum')
    label_plural = _('álbumes')
    background_image = "bg-music-album"


class BaseAlbumContext(BaseAlbum):
    """Mapa «por» de álbumes: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("genres", _("Álbumes del género {padre}"), "bg-music-genre"),
        "tipo": ("album_type", _("Álbumes de tipo {padre}"), "bg-music-album-type"),
        "artista": ("artist", _("Álbumes de {padre}"), "bg-music-artist"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "artista":
            return qs.filter(artist=padre)
        return super().filter_by(qs, padre, tipo)


class BaseAlbumImage(_Music):
    model = AlbumImage
    entity = 'album-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-music-album-image"


class BaseAlbumImageContext(BaseAlbumImage):
    """Mapa «por» de imágenes extra de álbum: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "album": ("album", _("Imágenes de {padre}"), "bg-music-album"),
    }


class BaseAlbumType(_Music):
    model = AlbumType
    entity = 'music-album-type'
    label = _('tipo de álbum')
    label_plural = _('tipos de álbum')
    background_image = "bg-music-album-type"


class BaseArtist(_Music):
    model = Artist
    entity = 'artist'
    label = _('artista')
    label_plural = _('artistas')
    background_image = "bg-music-artist"


class BaseArtistContext(BaseArtist):
    """Mapa «por» de artistas: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("genres", _("Artistas del género {padre}"), "bg-music-genre"),
        "tipo": ("artist_type", _("Artistas de tipo {padre}"), "bg-music-artist-type"),
    }


class BaseArtistImage(_Music):
    model = ArtistImage
    entity = 'artist-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-music-artist-image"


class BaseArtistImageContext(BaseArtistImage):
    """Mapa «por» de imágenes extra de artista: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "artista": ("artist", _("Imágenes de {padre}"), "bg-music-artist"),
    }


class BaseArtistMember(_Music):
    model = ArtistMember
    entity = 'artist-member'
    label = _('miembro')
    label_plural = _('miembros')
    background_image = "bg-music-artist-member"


class BaseArtistMemberContext(BaseArtistMember):
    """Mapa «por» de miembros: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "artista": ("artist", _("Miembros de {padre}"), ""),
        "persona": ("person", _("Miembros de {padre}"), ""),
    }


class BaseArtistType(_Music):
    model = ArtistType
    entity = 'music-artist-type'
    label = _('tipo de artista')
    label_plural = _('tipos de artista')
    background_image = "bg-music-artist-type"


class BaseDataDeezerAlbum(_Music):
    model = DataDeezerAlbum
    entity = 'data-deezer-album'
    label = _('datos de álbum')
    label_plural = _('datos · Álbum (Deezer)')
    title_create = _("Crear datos de álbum (Deezer)")
    title_delete = _("Eliminar datos de álbum")
    title_list = _("Lista de datos · Álbum (Deezer)")
    title_update = _("Editar datos de álbum")
    background_image = "bg-music-data-deezer-album"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataDeezerArtist(_Music):
    model = DataDeezerArtist
    entity = 'data-deezer-artist'
    label = _('datos de artista')
    label_plural = _('datos · Artista (Deezer)')
    title_create = _("Crear datos de artista (Deezer)")
    title_delete = _("Eliminar datos de artista")
    title_list = _("Lista de datos · Artista (Deezer)")
    title_update = _("Editar datos de artista")
    background_image = "bg-music-data-deezer-artist"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataDeezerGenre(_Music):
    model = DataDeezerGenre
    entity = 'data-deezer-genre'
    label = _('datos de género')
    label_plural = _('datos · Género (Deezer)')
    title_create = _("Crear datos de género (Deezer)")
    title_delete = _("Eliminar datos de género")
    title_list = _("Lista de datos · Género (Deezer)")
    title_update = _("Editar datos de género")
    background_image = "bg-music-data-deezer-genre"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataDeezerTrack(_Music):
    model = DataDeezerTrack
    entity = 'data-deezer-track'
    label = _('datos de pista del álbum')
    label_plural = _('datos · Pistas del álbum (Deezer)')
    title_create = _("Crear datos de pista del álbum (Deezer)")
    title_delete = _("Eliminar datos de pista del álbum")
    title_list = _("Lista de datos · Pistas del álbum (Deezer)")
    title_update = _("Editar datos de pista del álbum")
    background_image = "bg-music-data-deezer-track"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseGenre(_Music):
    model = Genre
    entity = 'music-genre'
    label = _('género')
    label_plural = _('géneros')
    background_image = "bg-music-genre"


# Vistas públicas de la sección Música: home (portada) + listados de catálogo.
#
# Vistas EXPLÍCITAS (estilo Hades): CBVs de Django directas con su contexto.
# Las filas del home y los conteos salen de la BD real (nada hardcodeado).

def _img_album(album):
    try:
        return resolve_cover(album) if album else None
    except ValueError:
        return None


def _sub_album(a):
    artista = getattr(a, "artist", None)
    return str(artista) if artista else ""


def _cards_canciones(canciones):
    """Tarjetas de canciones: la canción no tiene portada propia → la del álbum."""
    canciones = list(canciones)
    cards = cover_cards(canciones, _("Canción"), "music:song-detail",
                        sub=lambda s: str(s.album.artist) if s.album_id else "")
    for card, s in zip(cards, canciones):
        try:
            card["image"] = resolve_cover(s.album) if s.album_id else None
        except ValueError:
            card["image"] = None
    return cards


class BaseGenreAlias(_Music):
    model = GenreAlias
    entity = 'music-genre-alias'
    label = _('alias de género')
    label_plural = _('alias de géneros')
    background_image = "bg-music-genre-alias"          # mismo fondo que su padre


class BaseGenreAliasContext(BaseGenreAlias):
    """Mapa «por» de alias: por su género (/panel/music-genre-alias/genre/<id>/)."""
    filter_config = {
        "genre": ("genre", _("Alias de géneros de {padre}"), "bg-music-genre"),
    }


class BaseRole(_Music):
    model = Role
    entity = 'music-role'
    label = _('rol')
    label_plural = _('roles')
    background_image = "bg-music-role"


class BaseRoleContext(BaseRole):
    """Mapa «por» de roles: `type` acota por la familia fija (`RoleType`): /music-role/type/<valor>/."""
    filter_config = {
        "type": ("type", _("Roles de música · {valor}"), "bg-music-role"),
    }


class BaseSong(_Music):
    model = Song
    entity = 'song'
    label = _('canción')
    label_plural = _('canciones')
    background_image = "bg-music-song"


class BaseSongComposer(_Music):
    model = SongComposer
    entity = 'song-composer'
    label = _('compositor de canción')
    label_plural = _('compositores de canción')
    background_image = "bg-music-song-composer"


class BaseSongComposerContext(BaseSongComposer):
    """Mapa «por» de compositores de canción: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "cancion": ("song", _("Compositores de canción de {padre}"), ""),
        "persona": ("person", _("Compositores de canción de {padre}"), ""),
    }


class BaseSongContext(BaseSong):
    """Mapa «por» de canciones: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("album__genres", _("Canciones del género {padre}"), "bg-music-genre"),
        "artista": ("album__artist", _("Canciones de {padre}"), "bg-music-artist"),
        "album": ("album", _("Canciones de {padre}"), "bg-music-album"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "artista":
            return qs.filter(album__is_active=True, album__artist=padre).select_related("album")
        return super().filter_by(qs, padre, tipo)


class BaseSongTranslation(_Music):
    model = SongTranslation
    entity = 'song-translation'
    label = _('traducción de canción')
    label_plural = _('traducciones de canción')
    background_image = "bg-music-song-translation"


class BaseSongTranslationContext(BaseSongTranslation):
    """Mapa «por» de traducciones de canción: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "cancion": ("song", _("Traducciones de canción de {padre}"), ""),
    }


class BaseMusicLog(_Music):
    model = MusicLog
    entity = 'music-log'
    label = _('log')
    label_plural = _('log de música')
    background_image = "bg-music-log"
