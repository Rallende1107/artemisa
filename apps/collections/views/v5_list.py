"""collections · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.collections.models import ModelBaseCollection
from apps.collections.views import v3_data
from apps.collections.views.base import BaseAlbumCollection, BaseAnimeCollection, BaseArtistCollection, BaseCharacterCollection, BaseCollectionLog, BaseCompanyCollection, BaseGameCharacterCollection, BaseGameCollection, BaseMangaCollection, BaseMovieCollection, BasePersonCollection, BaseSerieCollection, BaseSongCollection
from apps.collections.views.v1_home import CollectionsPublicHomeView
from core.shared.views.base import AdminListView, PublicListView


# ==============================================================================
# Gestión
# ==============================================================================


class AlbumCollectionListView(BaseAlbumCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:album-collection_data"
    title = _("Lista de colecciones de álbumes")


# ---------------------------------------------------------------- colecciones (moderación)


class AnimeCollectionListView(BaseAnimeCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:anime-collection_data"
    title = _("Lista de colecciones de anime")


class ArtistCollectionListView(BaseArtistCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:artist-collection_data"
    title = _("Lista de colecciones de artistas")


class CharacterCollectionListView(BaseCharacterCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:character-collection_data"
    title = _("Lista de colecciones de personajes")


class CompanyCollectionListView(BaseCompanyCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:company-collection_data"
    title = _("Lista de colecciones de compañías")


class GameCharacterCollectionListView(BaseGameCharacterCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:game-character-collection_data"
    title = _("Lista de colecciones de personajes de juego")


class GameCollectionListView(BaseGameCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:game-collection_data"
    title = _("Lista de colecciones de juegos")


class MangaCollectionListView(BaseMangaCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:manga-collection_data"
    title = _("Lista de colecciones de manga")


class MovieCollectionListView(BaseMovieCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:movie-collection_data"
    title = _("Lista de colecciones de películas")


class PersonCollectionListView(BasePersonCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:person-collection_data"
    title = _("Lista de colecciones de personas")


class SerieCollectionListView(BaseSerieCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:serie-collection_data"
    title = _("Lista de colecciones de series")


class SongCollectionListView(BaseSongCollection, AdminListView):
    home_url = "panel:collections-home"
    data_url = "panel:song-collection_data"
    title = _("Lista de colecciones de canciones")


# ---------------------------------------------------------------- registro


class CollectionLogListView(BaseCollectionLog, AdminListView):
    home_url = "panel:collections-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:collection-log_data"
    create_url = "panel:collection-log_create"
    title = _("Lista de log de colecciones")


# ==============================================================================
# Público
# ==============================================================================


class BaseCollectionList(PublicListView):
    """Lo común de las 10 listas: candado de login, plantilla con la edición en línea, y la Data
    del medio (la ruta /collection/<medio>/data/ despacha, así que la clase se toma del mapa)."""
    login_only = True
    template_name = "collections/list.html"
    data_url = "collections:list-data"
    home_url = "collections:mine"
    home_label = _("mi colección")
    icon = "bi-collection"

    def data_url_args(self):
        return [self.model.medio()]

    @property
    def data(self):
        return v3_data.DATAS[self.model.medio()]

    def get_context_data(self, **kwargs):
        etiqueta, _icono, bg = CollectionsPublicHomeView.card_de(self.model)
        self.background_image = bg          # la lista lleva el fondo HOME de su app
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Colección de %s") % etiqueta
        ctx["tipo"] = self.model.medio()
        ctx["active_section"] = f"coleccion-{self.model.medio()}"
        return ctx


class AlbumCollectionPublicListView(BaseAlbumCollection, BaseCollectionList):
    section = "coleccion-album"
    title = _("Colección")


class AnimeCollectionPublicListView(BaseAnimeCollection, BaseCollectionList):
    section = "coleccion-anime"
    title = _("Colección")


class ArtistCollectionPublicListView(BaseArtistCollection, BaseCollectionList):
    section = "coleccion-artist"
    title = _("Colección")


class CharacterCollectionPublicListView(BaseCharacterCollection, BaseCollectionList):
    section = "coleccion-character"
    title = _("Colección")


class CompanyCollectionPublicListView(BaseCompanyCollection, BaseCollectionList):
    section = "coleccion-company"
    title = _("Colección")


class GameCharacterCollectionPublicListView(BaseGameCharacterCollection, BaseCollectionList):
    section = "coleccion-game-character"
    title = _("Colección")


class GameCollectionPublicListView(BaseGameCollection, BaseCollectionList):
    section = "coleccion-game"
    title = _("Colección")


class MangaCollectionPublicListView(BaseMangaCollection, BaseCollectionList):
    section = "coleccion-manga"
    title = _("Colección")


class MovieCollectionPublicListView(BaseMovieCollection, BaseCollectionList):
    section = "coleccion-movie"
    title = _("Colección")


class PersonCollectionPublicListView(BasePersonCollection, BaseCollectionList):
    section = "coleccion-person"
    title = _("Colección")


class SerieCollectionPublicListView(BaseSerieCollection, BaseCollectionList):
    section = "coleccion-serie"
    title = _("Colección")


class SongCollectionPublicListView(BaseSongCollection, BaseCollectionList):
    section = "coleccion-song"
    title = _("Colección")


LISTAS = {t.medio(): globals()[f"{t.__name__}PublicListView"] for t in ModelBaseCollection.tablas()}   # la lista del USUARIO, no la de gestión


def collection_list(request, tipo):
    from apps.collections.views.base import _tabla_o_404
    tabla = _tabla_o_404(tipo)
    return LISTAS[tabla.medio()].as_view()(request, tipo=tipo)
