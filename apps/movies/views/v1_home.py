"""movies · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.movies.models import Movie
from core.shared.views.base import BaseHomeView, BasePublicHomeView
from core.utils.public import populares_de
from core.utils.queries import con_relacion


# ==============================================================================
# Gestión
# ==============================================================================


class MoviesHomeView(BaseHomeView):
    title = 'Películas'
    active_entity = 'movies-home'
    background_image = "bg-movies-home"
    background_fallback = "bg-movies-home"   # respaldo si falta la imagen
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Contenido"), [
            ('movie', _('Películas'), '<i class="bi bi-film"></i>', "bg-movies-movie"),
            ('movie-title', _('Títulos alternativos'), '<i class="bi bi-type"></i>', "bg-movies-title-movie"),
            ('movie-image', _('Imágenes'), '<i class="bi bi-images"></i>', "bg-movies-movie-image"),
        ]),
        (_("Reparto y equipo"), [
            ('movie-cast', _('Reparto'), '<i class="bi bi-people"></i>', "bg-movies-movie-cast"),
            ('movie-staff', _('Equipo'), '<i class="bi bi-person-workspace"></i>', "bg-movies-movie-staff"),
            ('movie-relation', _('Relaciones'), '<i class="bi bi-diagram-3"></i>', "bg-movies-movie-relation"),
            ('movie-role', _('Roles'), '<i class="bi bi-person-badge"></i>', "bg-movies-role"),
        ]),
        (_("Taxonomías"), [
            ('movie-genre', _('Géneros'), '<i class="bi bi-tags"></i>', "bg-movies-genre"),
            ('movie-genre-alias', _('Alias de géneros'), '<i class="bi bi-tags"></i>', "bg-movies-movie-genre-alias"),
            ('movie-type', _('Tipos'), '<i class="bi bi-collection"></i>', "bg-movies-type"),
            ('movie-rating', _('Clasificaciones'), '<i class="bi bi-shield-check"></i>', "bg-movies-rating"),
        ]),
        (_("Compañías"), [
            ('company-movie', _('Compañías de cine'), '<i class="bi bi-building"></i>', "bg-movies-company"),
        ]),
        (_("Registro"), [
            ('movie-log', _('Log de películas'), '<i class="bi bi-journal-text"></i>', "bg-movies-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class MoviesPublicHomeView(BasePublicHomeView):
    section = "peliculas"
    title = _("Cine y animación")
    title_tab = _("Películas")
    background_image = "bg-movies-home"
    background_fallback = "bg-movies-home"   # respaldo si falta la imagen
    queryset = Movie.objects.filter(is_active=True)
    card_tag = _("Película")
    detail_url = "movies:movie-detail"

    def get_rows(self):
        """Las filas del home. El `group` de cada una es su PESTAÑA."""
        activas = self.queryset
        companias = Company.objects.filter(is_active=True)
        PELICULAS, PRODUCTORAS, DISTRIBUIDORAS = _("Películas"), _("Productoras"), _("Distribuidoras")
        return [
            self.row(_("Películas recientes"), activas.order_by("-created_at", "title")[:12], url="movies:movies-catalog", group=PELICULAS),
            self.row(_("Películas populares"), populares_de(Movie), url="movies:movies-catalog", group=PELICULAS),
            self.row(_("Productoras recientes"), companias.filter(con_relacion(Company, "movies_produced")).order_by("-created_at", "name")[:12],
                     _("Compañía"), "companias:company-detail", url="movies:producers-catalog", group=PRODUCTORAS),
            self.row(_("Distribuidoras recientes"), companias.filter(con_relacion(Company, "movies_distributed")).order_by("-created_at", "name")[:12],
                     _("Compañía"), "companias:company-detail", url="movies:distributors-catalog", group=DISTRIBUIDORAS),
        ]
