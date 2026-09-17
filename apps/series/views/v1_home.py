"""series · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.series.models import Serie
from core.shared.views.base import BaseHomeView, BasePublicHomeView
from core.utils.public import populares_de
from core.utils.queries import con_relacion


# ==============================================================================
# Gestión
# ==============================================================================


class SeriesHomeView(BaseHomeView):
    title = 'Series'
    active_entity = 'series-home'
    background_image = "bg-series-home"
    background_fallback = "bg-series-home"   # respaldo si falta la imagen
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Contenido"), [
            ('serie', _('Series'), '<i class="bi bi-collection-play"></i>', "bg-series-serie"),
            ('serie-title', _('Títulos alternativos'), '<i class="bi bi-type"></i>', "bg-series-title-serie"),
            ('serie-image', _('Imágenes'), '<i class="bi bi-images"></i>', "bg-series-serie-image"),
        ]),
        (_("Reparto y equipo"), [
            ('serie-cast', _('Reparto'), '<i class="bi bi-people"></i>', "bg-series-serie-cast"),
            ('serie-staff', _('Equipo'), '<i class="bi bi-person-workspace"></i>', "bg-series-serie-staff"),
            ('serie-relation', _('Relaciones'), '<i class="bi bi-diagram-3"></i>', "bg-series-serie-relation"),
            ('serie-role', _('Roles'), '<i class="bi bi-person-badge"></i>', "bg-series-role"),
        ]),
        (_("Taxonomías"), [
            ('serie-genre', _('Géneros'), '<i class="bi bi-tags"></i>', "bg-series-genre"),
            ('serie-genre-alias', _('Alias de géneros'), '<i class="bi bi-tags"></i>', "bg-series-genre-alias"),
            ('serie-type', _('Tipos'), '<i class="bi bi-collection"></i>', "bg-series-type"),
            ('serie-rating', _('Clasificaciones'), '<i class="bi bi-shield-check"></i>', "bg-series-rating"),
        ]),
        (_("Compañías"), [
            ('company-serie', _('Compañías de TV'), '<i class="bi bi-building"></i>', "bg-series-company"),
        ]),
        (_("Registro"), [
            ('serie-log', _('Log de series'), '<i class="bi bi-journal-text"></i>', "bg-series-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class SeriesPublicHomeView(BasePublicHomeView):
    section = "series"
    title = _("Televisión")
    title_tab = _("Series")
    background_image = "bg-series-home"
    background_fallback = "bg-series-home"   # respaldo si falta la imagen
    queryset = Serie.objects.filter(is_active=True)
    card_tag = _("Serie")
    detail_url = "series:serie-detail"

    def get_rows(self):
        """Las filas del home. El `group` de cada una es su PESTAÑA."""
        activas = self.queryset
        companias = Company.objects.filter(is_active=True)
        SERIES, PRODUCTORAS, DISTRIBUIDORAS = _("Series"), _("Productoras"), _("Distribuidoras")
        return [
            self.row(_("Series recientes"), activas.order_by("-created_at", "title")[:12], url="series:series-catalog", group=SERIES),
            self.row(_("Series populares"), populares_de(Serie), url="series:series-catalog", group=SERIES),
            self.row(_("Productoras recientes"), companias.filter(con_relacion(Company, "series_produced")).order_by("-created_at", "name")[:12],
                     _("Compañía"), "companias:company-detail", url="series:producers-catalog", group=PRODUCTORAS),
            self.row(_("Distribuidoras recientes"), companias.filter(con_relacion(Company, "series_distributed")).order_by("-created_at", "name")[:12],
                     _("Compañía"), "companias:company-detail", url="series:distributors-catalog", group=DISTRIBUIDORAS),
        ]
