"""games · panel de filtros por modelo, de gestión (con «Activo») y público."""
from django.utils.translation import gettext_lazy as _

from apps.games.models import Character, Creator, Game, Release
from core.shared.views.filters import BaseFilters, ChoiceFilter, RelationFilter, YearFilter


# ==============================================================================
# Público
# ==============================================================================


class CharacterFilters(BaseFilters):
    """Personajes de UN juego: el rol y el sexo se miran EN ESTE juego (ancla)."""
    model = Character
    ROLES = {"main": _("Protagonista"), "primary": _("Principal"), "side": _("Secundario"), "appears": _("Aparece")}
    SEXOS = {"m": _("Masculino"), "f": _("Femenino"), "b": _("Ambos"), "n": _("Sin sexo")}
    include_filters = [ChoiceFilter("roles__role", _("Rol"), ancla="roles__game", etiquetas=ROLES), ChoiceFilter("sex", _("Sexo"), etiquetas=SEXOS)]


class CreatorFilters(BaseFilters):
    model = Creator
    include_filters = [ChoiceFilter("type", _("Tipo")), RelationFilter("languages", _("Idioma"))]


class GameFilters(BaseFilters):
    model = Game
    include_filters = [
        RelationFilter("genres", _("Género")),
        ChoiceFilter("type", _("Tipo")),
        RelationFilter("developers", _("Creador")),
        RelationFilter("publishers", _("Editora")),
        ChoiceFilter("status", _("Estado")),
        RelationFilter("engine", _("Motor")),
        RelationFilter("platforms", _("Plataforma")),
        YearFilter("release_date", _("Año"))
        ]


class ReleaseFilters(BaseFilters):
    model = Release
    include_filters = [YearFilter("released", _("Año"))]
