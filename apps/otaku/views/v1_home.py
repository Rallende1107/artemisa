"""otaku · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.otaku.models import Anime, Character, Manga
from apps.otaku.views.base import _sub_anime, _sub_manga
from core.shared.views.base import BaseHomeView, BasePublicHomeView
from core.utils.public import populares_de
from core.utils.queries import con_relacion


# ==============================================================================
# Gestión
# ==============================================================================


class OtakuHomeView(BaseHomeView):
    """Home de Otaku en UNA página con secciones colapsables (Anime, Manga,
    Personajes, Taxonomías, Relaciones). Evita la grilla gigante de ~33 entidades."""
    title = 'Otaku'
    active_entity = 'otaku-home'
    background_image = "bg-otaku-home"
    background_fallback = "bg-otaku-home"   # respaldo si falta la imagen
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    # Cada grupo es una ENTIDAD completa: primero sus listas reales, después de dónde salen (importar de AniList,
    # cargar el dump de MAL, procesar) y al final sus tablas de datos crudos. Así todo lo de «anime» está junto.
    groups = [
        (_("Anime"), [
            ('anime', _('Animes'), '<i class="bi bi-collection-play"></i>', "bg-otaku-anime"),
            ('anime-song', _('Canciones de anime'), '<i class="bi bi-music-note-beamed"></i>', "bg-otaku-anime-song"),
            ('anime-character', _('Personajes de anime'), '<i class="bi bi-person-video2"></i>', "bg-otaku-anime-character"),
            ('anime-staff', _('Staff de anime'), '<i class="bi bi-person-workspace"></i>', "bg-otaku-anime-staff"),
            ('anime-title', _('Títulos'), '<i class="bi bi-type"></i>', "bg-otaku-title-anime"),
            ('anime-image', _('Imágenes de animes'), '<i class="bi bi-images"></i>', "bg-otaku-anime-image"),
        ]),
        (_("Anime · datos"), [
            ("data-anilist-anime", _("Datos de animes (AniList)"), '<i class="bi bi-database"></i>', "bg-otaku-data-anilist-anime"),
            ("data-mal-anime", _("Datos de animes (MAL)"), '<i class="bi bi-database"></i>', "bg-otaku-data-mal-anime"),
            ("data-mal-anime-character", _("Datos · personajes de animes (MAL)"), '<i class="bi bi-person-video2"></i>', "bg-otaku-data-mal-anime-character"),
            ("data-mal-anime-staff", _("Datos · staff de animes (MAL)"), '<i class="bi bi-person-workspace"></i>', "bg-otaku-data-mal-anime-staff"),
        ]),
        (_("Manga"), [
            ('manga', _('Mangas'), '<i class="bi bi-book"></i>', "bg-otaku-manga"),
            ('manga-author', _('Autores de manga'), '<i class="bi bi-pencil"></i>', "bg-otaku-author-manga"),
            ('manga-character', _('Personajes de manga'), '<i class="bi bi-person-video2"></i>', "bg-otaku-manga-character"),
            ('manga-title', _('Títulos'), '<i class="bi bi-type"></i>', "bg-otaku-title-manga"),
            ('manga-image', _('Imágenes de mangas'), '<i class="bi bi-images"></i>', "bg-otaku-manga-image"),
        ]),
        (_("Manga · datos"), [
            ("data-anilist-manga", _("Datos de mangas (AniList)"), '<i class="bi bi-database"></i>', "bg-otaku-data-anilist-manga"),
            ("data-mal-manga", _("Datos de mangas (MAL)"), '<i class="bi bi-database"></i>', "bg-otaku-data-mal-manga"),
            ("data-mal-manga-character", _("Datos · personajes de mangas (MAL)"), '<i class="bi bi-person-video2"></i>', "bg-otaku-data-mal-manga-character"),
        ]),
        (_("Personajes"), [
            ('character', _('Personajes'), '<i class="bi bi-person-bounding-box"></i>', "bg-otaku-character"),
            ('otaku-role', _('Roles'), '<i class="bi bi-person-badge"></i>', "bg-otaku-role"),
            ('character-voice', _('Voces de personaje'), '<i class="bi bi-mic"></i>', "bg-otaku-voice-character"),
            ('character-nickname', _('Apodos'), '<i class="bi bi-chat-quote"></i>', "bg-otaku-character-nickname"),
            ('character-image', _('Imágenes de personajes'), '<i class="bi bi-images"></i>', "bg-otaku-character-image"),
        ]),
        (_("Personajes · datos"), [
            ("data-anilist-character", _("Datos de personajes (AniList)"), '<i class="bi bi-database"></i>', "bg-otaku-data-anilist-character"),
            ("data-mal-character", _("Datos de personajes (MAL)"), '<i class="bi bi-database"></i>', "bg-otaku-data-mal-character"),
        ]),
        (_("Personas (MAL)"), [
            ('person-mal', _('Personas (MAL)'), '<i class="bi bi-person-badge"></i>', "bg-otaku-person"),
            ('person-image-mal', _('Imágenes de personas (MAL)'), '<i class="bi bi-images"></i>', "bg-people-person-image"),
        ]),
        (_("Personas · datos"), [
            ("data-anilist-person", _("Datos de personas (AniList)"), '<i class="bi bi-database"></i>', "bg-otaku-data-anilist-person"),
            ("data-mal-person", _("Datos de personas (MAL)"), '<i class="bi bi-database"></i>', "bg-otaku-data-mal-person"),
        ]),
        (_("Compañías (MAL)"), [
            ('company-mal', _('Compañías (MAL)'), '<i class="bi bi-building"></i>', "bg-otaku-company-mal"),
            ('company-image-mal', _('Imágenes de compañías (MAL)'), '<i class="bi bi-images"></i>', "bg-companies-company-image"),
        ]),
        (_("Compañías · datos"), [
            ("panel:dump-mal-company", _("Cargar dump de compañías (MAL)"), '<i class="bi bi-filetype-json"></i>', "bg-otaku-load-dump-company"),
        ]),
        (_("Taxonomías"), [
            ('genre', _('Géneros'), '<i class="bi bi-tags"></i>', "bg-otaku-genre"),
            ('genre-alias', _('Alias de géneros'), '<i class="bi bi-tags"></i>', "bg-otaku-genre-alias"),
            ('type', _('Tipos'), '<i class="bi bi-collection"></i>', "bg-otaku-type"),
            ('status', _('Estados'), '<i class="bi bi-flag"></i>', "bg-otaku-status"),
            ('source', _('Fuentes'), '<i class="bi bi-diagram-2"></i>', "bg-otaku-source"),
            ('theme', _('Temas'), '<i class="bi bi-palette"></i>', "bg-otaku-theme"),
            ('theme-alias', _('Alias de temas'), '<i class="bi bi-tags"></i>', "bg-otaku-theme-alias"),
            ('demographic', _('Demografías'), '<i class="bi bi-people"></i>', "bg-otaku-demographic"),
            ('demographic-alias', _('Alias de demografías'), '<i class="bi bi-tags"></i>', "bg-otaku-demographic-alias"),
            ('year', _('Años'), '<i class="bi bi-calendar-event"></i>', "bg-otaku-year"),
        ]),
        (_("Relaciones"), [
            ('relation', _('Relaciones'), '<i class="bi bi-share"></i>', "bg-otaku-relation"),
            ('relation-anime-anime', _('Relaciones anime → anime'), '<i class="bi bi-share"></i>', 'bg-otaku-relation-anime-anime'),
            ('relation-manga-anime', _('Relaciones manga → anime'), '<i class="bi bi-share"></i>', 'bg-otaku-relation-manga-anime'),
            ('relation-manga-manga', _('Relaciones manga → manga'), '<i class="bi bi-share"></i>', 'bg-otaku-relation-manga-manga'),
        ]),
        (_("Registro"), [
            ('otaku-log', _('Log de otaku'), '<i class="bi bi-journal-text"></i>', "bg-otaku-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class OtakuPublicHomeView(BasePublicHomeView):
    """Home ÚNICO de la sección Otaku: anime y manga juntos, con su industria
    (personajes, estudios, productoras, licenciatarias y revistas) como filas."""
    section = "otaku"
    title = _("Anime y manga")
    title_tab = _("Otaku")
    background_image = "bg-otaku-home"
    background_fallback = "bg-otaku-home"   # respaldo si falta la imagen


    def get_rows(self):
        """Las filas del home. El `group` de cada una es su PESTAÑA: «Compañías» junta estudios, productoras,
        licenciatarias y revistas, que por separado darían cuatro pestañas casi vacías."""
        animes = Anime.objects.filter(is_active=True)
        mangas = Manga.objects.filter(is_active=True)
        personajes = Character.objects.filter(is_active=True)
        ANIME, MANGA, PERSONAJES, COMPANIAS = _("Anime"), _("Manga"), _("Personajes"), _("Compañías")
        return [
            self.row(_("Anime reciente"), animes.order_by("-created_at", "title")[:12], _("Anime"), "otaku:anime-detail", url="otaku:anime-catalog", sub=_sub_anime, group=ANIME),
            self.row(_("Anime popular"), populares_de(Anime), _("Anime"), "otaku:anime-detail", url="otaku:anime-catalog", sub=_sub_anime, group=ANIME),
            self.row(_("Manga reciente"), mangas.order_by("-created_at", "title")[:12], _("Manga"), "otaku:manga-detail", url="otaku:manga-catalog", sub=_sub_manga, group=MANGA),
            self.row(_("Manga popular"), populares_de(Manga), _("Manga"), "otaku:manga-detail", url="otaku:manga-catalog", sub=_sub_manga, group=MANGA),
            self.row(_("Personajes recientes"), personajes.order_by("-created_at", "full_name")[:12], _("Personaje"), "otaku:character-detail", url="otaku:characters-catalog", group=PERSONAJES),
            self.row(_("Personajes populares"), populares_de(Character), _("Personaje"), "otaku:character-detail", url="otaku:characters-catalog", group=PERSONAJES),
            self.row(_("Estudios"), Company.objects.filter(con_relacion(Company, "animes_studio"), is_active=True).order_by("-created_at", "name")[:12], _("Estudio"), "companias:company-detail", url="otaku:studios-catalog", group=COMPANIAS),
            self.row(_("Productoras"), Company.objects.filter(con_relacion(Company, "animes_produced"), is_active=True).order_by("-created_at", "name")[:12], _("Productora"), "companias:company-detail", url="otaku:producers-catalog", group=COMPANIAS),
            self.row(_("Licenciatarias"), Company.objects.filter(con_relacion(Company, "animes_licensed"), is_active=True).order_by("-created_at", "name")[:12], _("Licenciataria"), "companias:company-detail", url="otaku:licensors-catalog", group=COMPANIAS),
            self.row(_("Revistas de manga"), Company.objects.filter(con_relacion(Company, "mangas_serialized"), is_active=True).order_by("-created_at", "name")[:12], _("Revista"), "companias:company-detail", url="otaku:magazines-catalog", group=COMPANIAS),
        ]
