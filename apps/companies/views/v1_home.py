"""companies · los dos HOMES (gestión: tarjetas de entidades; público: el hub de la industria de todos los medios)."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company, PAPELES
from apps.companies.views.base import NAV_PUBLICO
from core.shared.views.base import BaseHomeView, BasePublicHomeView
from core.utils.public import populares_de
from core.utils.queries import con_relacion


# ==============================================================================
# Gestión
# ==============================================================================


class CompaniesHomeView(BaseHomeView):
    title = "Compañías"
    active_entity = "companies-home"
    background_image = "bg-companies-home"
    # Cada card = (entidad, etiqueta, icono, FONDO). Sin modelo ni conteo: el home solo navega.
    groups = [
        (_("Compañías"), [
            ("company", _("Compañías"), '<i class="bi bi-building"></i>', "bg-companies-company"),
            ("company-image", _("Imágenes"), '<i class="bi bi-images"></i>', "bg-companies-company-image"),
        ]),
        (_("Registro"), [
            ("company-log", _("Log de compañías"), '<i class="bi bi-journal-text"></i>', "bg-companies-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


# Las filas del hub, por MEDIO (el `group` es su pestaña): (clave de PAPELES, título, lista «ver todo» de ese medio).
FILAS_HUB = (
    ("peliculas-producidas", _("Cine · productoras"), "movies:producers-catalog", _("Cine")),
    ("peliculas-distribuidas", _("Cine · distribuidoras"), "movies:distributors-catalog", _("Cine")),
    ("series-producidas", _("TV · productoras"), "series:producers-catalog", _("TV")),
    ("series-distribuidas", _("TV · distribuidoras"), "series:distributors-catalog", _("TV")),
    ("anime-estudio", _("Anime · estudios"), "otaku:studios-catalog", _("Anime")),
    ("anime-produccion", _("Anime · productoras"), "otaku:producers-catalog", _("Anime")),
    ("anime-licencia", _("Anime · licenciatarias"), "otaku:licensors-catalog", _("Anime")),
    ("manga-serializacion", _("Manga · revistas"), "otaku:magazines-catalog", _("Manga")),
)


class CompaniesPublicHomeView(BasePublicHomeView):
    """Hub GLOBAL de COMPAÑÍAS: la industria de TODOS los medios en un lugar, sobre una sola tabla.
    Cada fila lleva con «Ver todo» a la lista de esa industria en su medio."""
    section = "companias"
    title = _("Compañías")
    background_image = "bg-companies-home"
    nav = NAV_PUBLICO

    def get_rows(self):
        """Una fila por papel que ya exista (un medio que aún no apunte a Company, se salta). Los creadores de
        juegos siguen en su app: son personas y estudios a la vez, no entran en esta tabla."""
        from apps.games.models import Creator
        activas = Company.objects.filter(is_active=True)
        relaciones = {f.name for f in Company._meta.get_fields()}
        related = {clave: rel for clave, _etiqueta, rel, _orden in PAPELES}
        # Primero TODAS, sin pestaña propia: una compañía existe aunque todavía no tenga obras que la clasifiquen.
        filas = [self.row(_("Compañías"), activas.order_by("-created_at", "name")[:12], _("Compañía"),
                          "companias:company-detail", url="companias:companies-catalog"),
                 self.row(_("Compañías populares"), populares_de(Company), _("Compañía"),
                          "companias:company-detail", url="companias:companies-catalog",
                          empty=_("Aún ninguna en colecciones."))]
        for clave, titulo, ver_todo, grupo in FILAS_HUB:
            rel = related[clave]
            if rel not in relaciones:
                continue
            qs = list(activas.filter(con_relacion(Company, rel)).order_by("name")[:12])
            if not qs:          # sin obras en ese papel todavía: la fila no se pinta
                continue
            filas.append(self.row(titulo, qs, grupo, "companias:company-detail", url=ver_todo, group=grupo))
        creadores = Creator.objects.filter(is_active=True)
        JUEGOS = _("Juegos")
        filas += [
            self.row(_("Juegos · creadores"), creadores.order_by("name")[:12], JUEGOS, "games:creator-detail", url="games:creators-catalog", group=JUEGOS),
            self.row(_("Juegos · editoras"), creadores.filter(con_relacion(Creator, "published_games")).order_by("name")[:12], JUEGOS, "games:creator-detail", url="games:publishers-catalog", group=JUEGOS),
        ]
        return filas
