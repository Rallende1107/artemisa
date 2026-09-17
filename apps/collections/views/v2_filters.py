"""collections · panel de filtros por modelo, de gestión (con «Activo») y público."""
import copy

from django.utils.translation import gettext_lazy as _

from apps.collections.models import AlbumCollection, AnimeCollection, ArtistCollection, CharacterCollection, CompanyCollection, GameCharacterCollection, GameCollection, MangaCollection, MovieCollection, PersonCollection, SerieCollection, SongCollection
from apps.companies.views.v3_data import CompanyPublicDataView
from apps.games.views.v3_data import CharacterPublicDataView as GameCharacterPublicDataView, GamePublicDataView
from apps.movies.views.v3_data import MoviePublicDataView
from apps.music.views.v3_data import AlbumPublicDataView, ArtistPublicDataView, SongPublicDataView
from apps.otaku.views.v3_data import AnimePublicDataView, CharacterPublicDataView, MangaPublicDataView
from apps.people.views.v3_data import PersonPublicDataView
from apps.series.views.v3_data import SeriePublicDataView
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter, RelationFilter


def con_content(filtros):
    """Los filtros del catálogo del medio, sobre el contenido de la fila de colección (`content__…`)."""
    out = []
    for f in filtros:
        g = copy.copy(f)
        g.campo = "content__" + f.campo
        if getattr(g, "ancla", ""):
            g.ancla = "content__" + g.ancla
        out.append(g)
    return out


# ==============================================================================
# Gestión
# ==============================================================================


class AlbumCollectionAdminFilters(BaseFilters):
    model = AlbumCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


class AnimeCollectionAdminFilters(BaseFilters):
    model = AnimeCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


class ArtistCollectionAdminFilters(BaseFilters):
    model = ArtistCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


class CharacterCollectionAdminFilters(BaseFilters):
    model = CharacterCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario"))]


class CompanyCollectionAdminFilters(BaseFilters):
    model = CompanyCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario"))]


class GameCharacterCollectionAdminFilters(BaseFilters):
    model = GameCharacterCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario"))]


class GameCollectionAdminFilters(BaseFilters):
    model = GameCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


class MangaCollectionAdminFilters(BaseFilters):
    model = MangaCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


class MovieCollectionAdminFilters(BaseFilters):
    model = MovieCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


class PersonCollectionAdminFilters(BaseFilters):
    model = PersonCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario"))]


class SerieCollectionAdminFilters(BaseFilters):
    model = SerieCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


class SongCollectionAdminFilters(BaseFilters):
    model = SongCollection
    generic_filters = [BooleanFilter("is_active", _("Activo")), BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [RelationFilter("user", _("Usuario")), ChoiceFilter("status", _("Estado"))]


# ==============================================================================
# Público
# ==============================================================================


class AlbumCollectionFilters(BaseFilters):
    model = AlbumCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(AlbumPublicDataView.filters.include_filters)]


class AnimeCollectionFilters(BaseFilters):
    model = AnimeCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(AnimePublicDataView.filters.include_filters)]


class ArtistCollectionFilters(BaseFilters):
    model = ArtistCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(ArtistPublicDataView.filters.include_filters)]


class CharacterCollectionFilters(BaseFilters):
    model = CharacterCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [*con_content(CharacterPublicDataView.filters.include_filters)]


class CompanyCollectionFilters(BaseFilters):
    model = CompanyCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [*con_content(CompanyPublicDataView.filters.include_filters)]


class GameCharacterCollectionFilters(BaseFilters):
    model = GameCharacterCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [*con_content(GameCharacterPublicDataView.filters.include_filters)]


class GameCollectionFilters(BaseFilters):
    model = GameCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(GamePublicDataView.filters.include_filters)]


class MangaCollectionFilters(BaseFilters):
    model = MangaCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(MangaPublicDataView.filters.include_filters)]


class MovieCollectionFilters(BaseFilters):
    model = MovieCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(MoviePublicDataView.filters.include_filters)]


class PersonCollectionFilters(BaseFilters):
    model = PersonCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [*con_content(PersonPublicDataView.filters.include_filters)]


class SerieCollectionFilters(BaseFilters):
    model = SerieCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(SeriePublicDataView.filters.include_filters)]


class SongCollectionFilters(BaseFilters):
    model = SongCollection
    generic_filters = [BooleanFilter("is_favorite", _("Favorito"))]
    include_filters = [ChoiceFilter("status", _("Mi estado")), *con_content(SongPublicDataView.filters.include_filters)]
