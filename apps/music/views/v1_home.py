"""music · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from apps.music.models import Album, Artist, Song
from apps.music.views.base import _cards_canciones, _sub_album
from core.shared.views.base import BaseHomeView, BasePublicHomeView
from core.utils.public import populares_de


# ==============================================================================
# Gestión
# ==============================================================================


class MusicHomeView(BaseHomeView):
    title = 'Música'
    active_entity = 'music-home'
    background_image = "bg-music-home"
    background_fallback = "bg-music-home"   # respaldo si falta la imagen
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Artistas"), [
            ('artist', _('Artistas'), '<i class="bi bi-mic"></i>', "bg-music-artist"),
            ('artist-image', _('Imágenes'), '<i class="bi bi-images"></i>', "bg-music-artist-image"),
        ]),
        (_("Álbumes"), [
            ('album', _('Álbumes'), '<i class="bi bi-disc"></i>', "bg-music-album"),
            ('song', _('Canciones'), '<i class="bi bi-music-note-beamed"></i>', "bg-music-song"),
            ('song-translation', _('Traducciones de canción'), '<i class="bi bi-translate"></i>', "bg-music-song-translation"),
            ('song-composer', _('Compositores de canción'), '<i class="bi bi-vector-pen"></i>', "bg-music-song-composer"),
            ('album-image', _('Imágenes'), '<i class="bi bi-images"></i>', "bg-music-album-image"),
        ]),
        (_("Tipos y géneros"), [
            ('music-genre', _('Géneros'), '<i class="bi bi-tags"></i>', "bg-music-genre"),
            ('music-genre-alias', _('Alias de géneros'), '<i class="bi bi-tags"></i>', "bg-music-genre-alias"),
            ('music-album-type', _('Tipos de álbum'), '<i class="bi bi-collection"></i>', "bg-music-album-type"),
            ('music-artist-type', _('Tipos de artista'), '<i class="bi bi-diagram-3"></i>', "bg-music-artist-type"),
        ]),
        (_("Roles y miembros"), [
            ('music-role', _('Roles'), '<i class="bi bi-person-badge"></i>', "bg-music-role"),
            ('artist-member', _('Miembros'), '<i class="bi bi-people"></i>', "bg-music-artist-member"),
        ]),
        # A importar se entra por la lista de DATOS de cada tipo (su botón «Importar»), como a un alta se
        # entra por su lista: la tarjeta lleva a la lista y la lista al importador (igual que VNDB).
        (_("Importación datos · Deezer"), [
            ("data-deezer-genre", _("Datos · Género (Deezer)"), '<i class="bi bi-tags"></i>', "bg-music-data-deezer-genre"),
            ("data-deezer-artist", _("Datos · Artista (Deezer)"), '<i class="bi bi-person-lines-fill"></i>', "bg-music-data-deezer-artist"),
            ("data-deezer-album", _("Datos · Álbum (Deezer)"), '<i class="bi bi-disc"></i>', "bg-music-data-deezer-album"),
            ("data-deezer-track", _("Datos · Pistas del álbum (Deezer)"), '<i class="bi bi-music-note-list"></i>', "bg-music-data-deezer-track"),
        ]),
        (_("Registro"), [
            ('music-log', _('Log de música'), '<i class="bi bi-journal-text"></i>', "bg-music-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class MusicPublicHomeView(BasePublicHomeView):
    section = "musica"
    title = _("Álbumes y artistas")
    title_tab = _("Música")
    background_image = "bg-music-home"
    background_fallback = "bg-music-home"   # respaldo si falta la imagen


    def get_rows(self):
        """Las filas del home. El `group` de cada una es su PESTAÑA."""
        artistas = Artist.objects.filter(is_active=True)
        albumes = Album.objects.filter(is_active=True)
        canciones = Song.objects.filter(is_active=True, album__is_active=True).select_related("album", "album__artist")
        ALBUMES, ARTISTAS, CANCIONES = _("Álbumes"), _("Artistas"), _("Canciones")
        return [
            self.row(_("Álbumes recientes"), albumes.order_by("-created_at")[:12], _("Álbum"), "music:album-detail", url="music:albums-catalog", sub=_sub_album, group=ALBUMES),
            self.row(_("Álbumes populares"), populares_de(Album), _("Álbum"), "music:album-detail", url="music:albums-catalog", sub=_sub_album, group=ALBUMES),
            self.row(_("Artistas recientes"), artistas.order_by("-created_at", "name")[:12], _("Artista"), "music:artist-detail", url="music:artists-catalog", group=ARTISTAS),
            self.row(_("Artistas populares"), populares_de(Artist), _("Artista"), "music:artist-detail", url="music:artists-catalog", group=ARTISTAS),
            self.row(_("Canciones recientes"), url="music:songs-catalog", items=_cards_canciones(canciones.order_by("-created_at")[:12]), group=CANCIONES),
            self.row(_("Canciones populares"), url="music:songs-catalog", items=_cards_canciones(populares_de(Song)), group=CANCIONES),
        ]
