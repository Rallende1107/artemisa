"""collections · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.collections.models import AlbumCollection, AnimeCollection, ArtistCollection, CharacterCollection, CompanyCollection, GameCharacterCollection, GameCollection, MangaCollection, MovieCollection, PersonCollection, SerieCollection, SongCollection
from apps.companies.views.v3_data import CompanyPublicDataView
from apps.games.views.v3_data import CharacterPublicDataView as GameCharacterPublicDataView, GamePublicDataView
from apps.movies.views.v3_data import MoviePublicDataView
from apps.music.views.v3_data import AlbumPublicDataView, ArtistPublicDataView, SongPublicDataView
from apps.otaku.views.v3_data import AnimePublicDataView, CharacterPublicDataView, MangaPublicDataView
from apps.people.views.v3_data import PersonPublicDataView
from apps.series.views.v3_data import SeriePublicDataView
from core.shared.views.base import BaseHomeView, BasePage


# ==============================================================================
# Gestión
# ==============================================================================


class CollectionsHomeView(BaseHomeView):
    title = "Colecciones"
    active_entity = "collections-home"
    background_image = "bg-collections-home"
    background_fallback = "bg-collections-home"   # respaldo si falta la imagen

    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Colecciones"), [
            ("serie-collection", _("Colecciones de series"), '<i class="bi bi-collection-play"></i>', "bg-coleccions-series"),
            ("movie-collection", _("Colecciones de películas"), '<i class="bi bi-film"></i>', "bg-coleccions-movies"),
            ("anime-collection", _("Colecciones de anime"), '<i class="bi bi-stars"></i>', "bg-coleccions-animes"),
            ("manga-collection", _("Colecciones de manga"), '<i class="bi bi-book"></i>', "bg-coleccions-mangas"),
            ("game-collection", _("Colecciones de juegos"), '<i class="bi bi-controller"></i>', "bg-coleccions-games"),
            ("album-collection", _("Colecciones de álbumes"), '<i class="bi bi-vinyl"></i>', "bg-coleccions-albums"),
            ("artist-collection", _("Colecciones de artistas"), '<i class="bi bi-music-note-beamed"></i>', "bg-coleccions-artists"),
            ("song-collection", _("Colecciones de canciones"), '<i class="bi bi-music-note"></i>', "bg-coleccions-songs"),
            ("character-collection", _("Colecciones de personajes"), '<i class="bi bi-person-badge"></i>', "bg-coleccions-characters"),
            ("person-collection", _("Colecciones de personas"), '<i class="bi bi-person-video3"></i>', "bg-coleccions-people"),
            ("company-collection", _("Colecciones de compañías"), '<i class="bi bi-building"></i>', "bg-coleccions-companies"),
            ("game-character-collection", _("Colecciones de personajes de juego"), '<i class="bi bi-joystick"></i>', "bg-coleccions-game-characters"),
        ]),
        (_("Estados"), [
        ]),
        (_("Registro"), [
            ("collection-log", _("Log de colecciones"), '<i class="bi bi-journal-text"></i>', "bg-collections-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class CollectionsPublicHomeView(BasePage, TemplateView):
    """DASHBOARD de Mi colección (estilo panel de gestión): una tarjeta por
    colección del usuario, con el fondo HOME de su app, hacia su lista."""
    staff_only = False
    login_only = True   # el área del usuario: logueado, sin exigir staff
    template_name = "collections/home.html"
    login_url = "users:login"
    background_image = "bg-collections-home"
    background_fallback = "bg-users-user"   # respaldo mientras no exista el .webp propio
    title = _("Mi colección")

    # Cada card = (tabla, etiqueta, icono, FONDO, catálogo). El fondo es la clase
    # bg-<app>-home de su app (static/image/screen/wide/<clase>.webp); cambia el string
    # para usar otra imagen. `catálogo` es la lista pública del medio: de ahí salen el
    # panel de filtros (géneros, año, tipo…) y su lógica, aplicados sobre TUS filas.
    # La lista de cada colección hereda etiqueta, fondo y filtros de aquí. `catálogo` es la
    # PublicDataView del medio: sus `filters` (v5_filters.py público) son el panel de la colección.
    cards = [
        (SerieCollection, _("Series"), '<i class="bi bi-collection-play"></i>', "bg-series-home", SeriePublicDataView),
        (MovieCollection, _("Películas"), '<i class="bi bi-film"></i>', "bg-movies-home", MoviePublicDataView),
        (AnimeCollection, _("Anime"), '<i class="bi bi-stars"></i>', "bg-otaku-home", AnimePublicDataView),
        (MangaCollection, _("Manga"), '<i class="bi bi-book"></i>', "bg-otaku-home", MangaPublicDataView),
        (GameCollection, _("Juegos"), '<i class="bi bi-controller"></i>', "bg-games-home", GamePublicDataView),
        (AlbumCollection, _("Álbumes"), '<i class="bi bi-vinyl"></i>', "bg-music-home", AlbumPublicDataView),
        (ArtistCollection, _("Artistas"), '<i class="bi bi-music-note-beamed"></i>', "bg-music-home", ArtistPublicDataView),
        (SongCollection, _("Canciones"), '<i class="bi bi-music-note"></i>', "bg-music-home", SongPublicDataView),
        (CharacterCollection, _("Personajes"), '<i class="bi bi-person-badge"></i>', "bg-otaku-home", CharacterPublicDataView),
        (PersonCollection, _("Personas"), '<i class="bi bi-person-video3"></i>', "bg-people-home", PersonPublicDataView),
        (CompanyCollection, _("Compañías"), '<i class="bi bi-building"></i>', "bg-companies-home", CompanyPublicDataView),
        (GameCharacterCollection, _("Personajes de juego"), '<i class="bi bi-joystick"></i>', "bg-games-home", GameCharacterPublicDataView),
    ]

    @classmethod
    def card_de(cls, tabla):
        """(etiqueta, icono, fondo) de una tabla, para la lista y los enlaces."""
        for t, etiqueta, icono, bg, _cat in cls.cards:
            if t is tabla:
                return etiqueta, icono, bg
        return tabla._meta.verbose_name_plural, "", cls.background_image

    @classmethod
    def catalogo_de(cls, tabla, request=None):
        """La PublicDataView del medio (clase): de ahí salen `model` y `filters` para el panel
        y el filtrado de la colección (None si el medio no declara catálogo)."""
        for t, _e, _i, _b, Catalogo in cls.cards:
            if t is tabla:
                return Catalogo
        return None

    def get_context_data(self, **kwargs):
        from core.utils.views import _bg_from_class
        ctx = super().get_context_data(**kwargs)
        cards, total = [], 0
        for tabla, etiqueta, icono, bg, _cat in self.cards:
            n = tabla.objects.filter(user=self.request.user, is_active=True).count()
            total += n
            cards.append({"url": reverse("collections:list", args=[tabla.medio()]),
                          "label": etiqueta, "icon": icono, "count": n, "bg": _bg_from_class(bg)})
        ctx["total"] = total
        ctx["cards"] = cards
        return ctx
