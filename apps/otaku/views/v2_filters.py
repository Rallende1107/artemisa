"""otaku · panel de filtros por modelo, de gestión (con «Activo») y público."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.otaku.models import Anime, AnimeSong, Character, Manga, Role
from apps.people.models import Person
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter, InicialFilter, RelationFilter, YearFilter


# ==============================================================================
# Público
# ==============================================================================


class AnimeFilters(BaseFilters):
    model = Anime
    include_filters = [InicialFilter("initial", _("Inicial")), RelationFilter("genres", _("Género")), RelationFilter("anime_type", _("Tipo")), RelationFilter("themes", _("Temas")), RelationFilter("demographics", _("Demografías")), RelationFilter("studios", _("Estudios")), RelationFilter("producers", _("Productoras")), RelationFilter("licensors", _("Licenciatarias")), RelationFilter("status", _("Estado")), RelationFilter("source", _("Fuente")), ChoiceFilter("rating", _("Clasificación")), ChoiceFilter("season", _("Temporada")), YearFilter("year", _("Año"))]


class AnimeCharacterFilters(BaseFilters):
    model = Character
    include_filters = [RelationFilter("anime_appearances__role", _("Rol"), ancla="anime_appearances__anime")]


class AnimeSongFilters(BaseFilters):
    model = AnimeSong
    generic_filters = [ChoiceFilter("type", _("Tipo")), BooleanFilter("is_active", _("Activo"))]
    include_filters = [RelationFilter("anime", _("Anime"))]


class VoiceFilters(BaseFilters):
    model = Person
    include_filters = [RelationFilter("voice_roles__language", _("Idioma"))]


class AnimeStaffFilters(BaseFilters):
    model = Person
    include_filters = [RelationFilter("anime_staff__role", _("Cargo"), ancla="anime_staff__anime")]


class CharacterFilters(BaseFilters):
    model = Character
    include_filters = []


class LicensorFilters(BaseFilters):
    model = Company
    include_filters = []


class MangaFilters(BaseFilters):
    model = Manga
    include_filters = [InicialFilter("initial", _("Inicial")), RelationFilter("genres", _("Género")), RelationFilter("manga_type", _("Tipo")), RelationFilter("status", _("Estado")), RelationFilter("demographics", _("Demografía")), RelationFilter("serializations", _("Revista")), ChoiceFilter("rating", _("Clasificación")), ChoiceFilter("season", _("Temporada")), YearFilter("year", _("Año"))]


class MangaAuthorFilters(BaseFilters):
    model = Person
    include_filters = [RelationFilter("manga_authored__role", _("Rol"), ancla="manga_authored__manga")]


class MangaCharacterFilters(BaseFilters):
    model = Character
    include_filters = [RelationFilter("manga_appearances__role", _("Rol"), ancla="manga_appearances__manga")]


class ProducerFilters(BaseFilters):
    model = Company
    include_filters = []


class RoleFilters(BaseFilters):
    model = Role
    generic_filters = [ChoiceFilter("type", _("Tipo de rol")), BooleanFilter("is_active", _("Activo"))]


class SerializationFilters(BaseFilters):
    model = Company
    include_filters = []


class StudioFilters(BaseFilters):
    model = Company
    include_filters = []
