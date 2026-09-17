"""collections · fichas, de gestión y públicas."""
from apps.collections.views.base import BaseAlbumCollection, BaseAnimeCollection, BaseArtistCollection, BaseCharacterCollection, BaseCollectionLog, BaseCompanyCollection, BaseGameCharacterCollection, BaseGameCollection, BaseMangaCollection, BaseMovieCollection, BasePersonCollection, BaseSerieCollection, BaseSongCollection
from core.shared.views.base import BaseAdminDetailView


# Gestión
# ==============================================================================


class AlbumCollectionDetailView(BaseAlbumCollection, BaseAdminDetailView):
    template_name = "collections/detail/album_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:album-collection_delete"
    list_url = "panel:album-collection_list"


# ---------------------------------------------------------------- colecciones
class AnimeCollectionDetailView(BaseAnimeCollection, BaseAdminDetailView):
    template_name = "collections/detail/anime_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:anime-collection_delete"
    list_url = "panel:anime-collection_list"


class ArtistCollectionDetailView(BaseArtistCollection, BaseAdminDetailView):
    template_name = "collections/detail/artist_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:artist-collection_delete"
    list_url = "panel:artist-collection_list"


class CharacterCollectionDetailView(BaseCharacterCollection, BaseAdminDetailView):
    template_name = "collections/detail/character_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:character-collection_delete"
    list_url = "panel:character-collection_list"


class CompanyCollectionDetailView(BaseCompanyCollection, BaseAdminDetailView):
    template_name = "collections/detail/company_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:company-collection_delete"
    list_url = "panel:company-collection_list"


class GameCharacterCollectionDetailView(BaseGameCharacterCollection, BaseAdminDetailView):
    template_name = "collections/detail/game_character_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:game-character-collection_delete"
    list_url = "panel:game-character-collection_list"


class GameCollectionDetailView(BaseGameCollection, BaseAdminDetailView):
    template_name = "collections/detail/game_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:game-collection_delete"
    list_url = "panel:game-collection_list"


class MangaCollectionDetailView(BaseMangaCollection, BaseAdminDetailView):
    template_name = "collections/detail/manga_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:manga-collection_delete"
    list_url = "panel:manga-collection_list"


class MovieCollectionDetailView(BaseMovieCollection, BaseAdminDetailView):
    template_name = "collections/detail/movie_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:movie-collection_delete"
    list_url = "panel:movie-collection_list"


class PersonCollectionDetailView(BasePersonCollection, BaseAdminDetailView):
    template_name = "collections/detail/person_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:person-collection_delete"
    list_url = "panel:person-collection_list"


class SerieCollectionDetailView(BaseSerieCollection, BaseAdminDetailView):
    template_name = "collections/detail/serie_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:serie-collection_delete"
    list_url = "panel:serie-collection_list"


class SongCollectionDetailView(BaseSongCollection, BaseAdminDetailView):
    template_name = "collections/detail/song_collection.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    delete_url = "panel:song-collection_delete"
    list_url = "panel:song-collection_list"


# ---------------------------------------------------------------- registro
class CollectionLogDetailView(BaseCollectionLog, BaseAdminDetailView):
    template_name = "collections/detail/collection_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    list_url = "panel:collection-log_list"
