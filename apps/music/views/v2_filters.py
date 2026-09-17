"""music · panel de filtros por modelo, de gestión (con «Activo») y público."""
from django.utils.translation import gettext_lazy as _

from apps.music.models import Album, Artist, Role, Song
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter, RelationFilter, YearFilter


# ==============================================================================
# Gestión
# ==============================================================================


class ArtistAdminFilters(BaseFilters):
    model = Artist
    generic_filters = [BooleanFilter("is_active", _("Activo"))]
    include_filters = [RelationFilter("artist_type", _("Tipo de artista")), RelationFilter("genres", _("Género")), YearFilter("start_year", _("Año de inicio"))]


# ==============================================================================
# Público
# ==============================================================================


class AlbumFilters(BaseFilters):
    model = Album
    include_filters = [RelationFilter("genres", _("Género")), YearFilter("release_date", _("Año"))]


class ArtistFilters(BaseFilters):
    model = Artist
    include_filters = [RelationFilter("genres", _("Género"))]


class ArtistSongFilters(BaseFilters):
    """Canciones de UN artista: la faceta Álbum acotada a SUS álbumes (padre_en)."""
    model = Song
    include_filters = [RelationFilter("album", _("Álbum"), padre_en="artist")]


class RoleFilters(BaseFilters):
    model = Role
    generic_filters = [ChoiceFilter("type", _("Tipo de rol")), BooleanFilter("is_active", _("Activo"))]


class SongFilters(BaseFilters):
    model = Song
    include_filters = [YearFilter("release_year", _("Año"))]
