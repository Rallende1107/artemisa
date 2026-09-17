"""people · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from apps.people.models import Person
from apps.people.views.base import _personas_de, FONDO_RESPALDO
from core.shared.views.base import BaseHomeView, BasePublicHomeView
from core.utils.public import populares_de


# ==============================================================================
# Gestión
# ==============================================================================


FONDO = "bg-people-home"            # fondo de la sección; cae al respaldo si no existe el .webp


class PeopleHomeView(BaseHomeView):
    title = 'Personas'
    active_entity = 'people-home'
    background_image = FONDO
    background_fallback = FONDO_RESPALDO   # respaldo si falta la imagen
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Personas"), [
            ('person', _('Personas'), '<i class="bi bi-person"></i>', "bg-people-person"),
            ('person-nickname', _('Apodos'), '<i class="bi bi-chat-quote"></i>', "bg-people-person-nickname"),
            ('person-link', _('Enlaces'), '<i class="bi bi-link-45deg"></i>', "bg-people-person-link"),
            ('person-image', _('Imágenes'), '<i class="bi bi-images"></i>', "bg-people-person-image"),
        ]),
        (_("Registro"), [
            ('people-log', _('Log de personas'), '<i class="bi bi-journal-text"></i>', "bg-people-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class PeoplePublicHomeView(BasePublicHomeView):
    """Landing de PERSONAS (`personas:home`, como games/movies): resumen global
    + adelanto por dominio."""
    section = "personas"
    title = _("Personas")
    background_image = "bg-people-home"
    background_fallback = "bg-people-home"   # respaldo si falta la imagen
    queryset = Person.objects.filter(is_active=True)
    card_tag = _("Persona")
    detail_url = "personas:person-detail"

    def get_rows(self):
        """Las filas del home. El `group` de cada una es su PESTAÑA."""
        personas = self.queryset
        PERSONAS, CINE, TV, VOCES = _("Personas"), _("Cine"), _("TV"), _("Voces")
        return [
            self.row(_("Personas recientes"), personas.order_by("-created_at", "full_name")[:12], url="personas:people-catalog", group=PERSONAS),
            self.row(_("Personas populares"), populares_de(Person), url="personas:people-catalog", group=PERSONAS),
            self.row(_("Cine"), _personas_de("cine").order_by("-created_at", "full_name")[:12], _("Cine"), url="personas:film-catalog", group=CINE),
            self.row(_("TV"), _personas_de("tv").order_by("-created_at", "full_name")[:12], _("TV"), url="personas:tv-catalog", group=TV),
            self.row(_("Actores de voz"), _personas_de("voces").order_by("-created_at", "full_name")[:12], _("Voz"), url="personas:voices-catalog", group=VOCES),
        ]
