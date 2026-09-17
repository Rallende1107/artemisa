"""collections · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.collections import forms as f
from apps.collections.views.base import BaseAlbumCollection, BaseAnimeCollection, BaseArtistCollection, BaseCharacterCollection, BaseCollectionLog, BaseCompanyCollection, BaseGameCharacterCollection, BaseGameCollection, BaseMangaCollection, BaseMovieCollection, BasePersonCollection, BaseSerieCollection, BaseSongCollection
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class AlbumCollectionDeleteView(BaseAlbumCollection, BaseDelete):
    list_url = "panel:album-collection_list"
    success_url = "panel:album-collection_list"
    cancel_url = "panel:album-collection_list"
    success_message = _("Colección de álbumes «%(obj)s» eliminada.")
    title = _("Eliminar colección de álbumes")


class AlbumCollectionCreateView(BaseAlbumCollection, BaseCreate):
    form_class = f.AlbumCollectionForm
    list_url = "panel:album-collection_list"
    success_url = "panel:album-collection_list"
    cancel_url = "panel:album-collection_list"
    success_message = _("Colección de álbumes «%(obj)s» creado.")
    title = _("Crear colección de álbumes")


class AlbumCollectionUpdateView(BaseAlbumCollection, BaseUpdate):
    form_class = f.AlbumCollectionForm
    list_url = "panel:album-collection_list"
    success_url = "panel:album-collection_list"
    cancel_url = "panel:album-collection_list"
    success_message = _("Colección de álbumes «%(obj)s» actualizado.")
    title = _("Editar colección de álbumes")


class AnimeCollectionDeleteView(BaseAnimeCollection, BaseDelete):
    list_url = "panel:anime-collection_list"
    success_url = "panel:anime-collection_list"
    cancel_url = "panel:anime-collection_list"
    success_message = _("Colección de anime «%(obj)s» eliminada.")
    title = _("Eliminar colección de anime")


class AnimeCollectionCreateView(BaseAnimeCollection, BaseCreate):
    form_class = f.AnimeCollectionForm
    list_url = "panel:anime-collection_list"
    success_url = "panel:anime-collection_list"
    cancel_url = "panel:anime-collection_list"
    success_message = _("Colección de anime «%(obj)s» creado.")
    title = _("Crear colección de anime")


class AnimeCollectionUpdateView(BaseAnimeCollection, BaseUpdate):
    form_class = f.AnimeCollectionForm
    list_url = "panel:anime-collection_list"
    success_url = "panel:anime-collection_list"
    cancel_url = "panel:anime-collection_list"
    success_message = _("Colección de anime «%(obj)s» actualizado.")
    title = _("Editar colección de anime")


class ArtistCollectionDeleteView(BaseArtistCollection, BaseDelete):
    list_url = "panel:artist-collection_list"
    success_url = "panel:artist-collection_list"
    cancel_url = "panel:artist-collection_list"
    success_message = _("Colección de artistas «%(obj)s» eliminada.")
    title = _("Eliminar colección de artistas")


class ArtistCollectionCreateView(BaseArtistCollection, BaseCreate):
    form_class = f.ArtistCollectionForm
    list_url = "panel:artist-collection_list"
    success_url = "panel:artist-collection_list"
    cancel_url = "panel:artist-collection_list"
    success_message = _("Colección de artistas «%(obj)s» creado.")
    title = _("Crear colección de artistas")


class ArtistCollectionUpdateView(BaseArtistCollection, BaseUpdate):
    form_class = f.ArtistCollectionForm
    list_url = "panel:artist-collection_list"
    success_url = "panel:artist-collection_list"
    cancel_url = "panel:artist-collection_list"
    success_message = _("Colección de artistas «%(obj)s» actualizado.")
    title = _("Editar colección de artistas")


class CharacterCollectionDeleteView(BaseCharacterCollection, BaseDelete):
    list_url = "panel:character-collection_list"
    success_url = "panel:character-collection_list"
    cancel_url = "panel:character-collection_list"
    success_message = _("Colección de personajes «%(obj)s» eliminada.")
    title = _("Eliminar colección de personajes")


class CharacterCollectionCreateView(BaseCharacterCollection, BaseCreate):
    form_class = f.CharacterCollectionForm
    list_url = "panel:character-collection_list"
    success_url = "panel:character-collection_list"
    cancel_url = "panel:character-collection_list"
    success_message = _("Colección de personajes «%(obj)s» creado.")
    title = _("Crear colección de personajes")


class CharacterCollectionUpdateView(BaseCharacterCollection, BaseUpdate):
    form_class = f.CharacterCollectionForm
    list_url = "panel:character-collection_list"
    success_url = "panel:character-collection_list"
    cancel_url = "panel:character-collection_list"
    success_message = _("Colección de personajes «%(obj)s» actualizado.")
    title = _("Editar colección de personajes")


class CompanyCollectionDeleteView(BaseCompanyCollection, BaseDelete):
    list_url = "panel:company-collection_list"
    success_url = "panel:company-collection_list"
    cancel_url = "panel:company-collection_list"
    success_message = _("Colección de compañías «%(obj)s» eliminada.")
    title = _("Eliminar colección de compañías")


class CompanyCollectionCreateView(BaseCompanyCollection, BaseCreate):
    form_class = f.CompanyCollectionForm
    list_url = "panel:company-collection_list"
    success_url = "panel:company-collection_list"
    cancel_url = "panel:company-collection_list"
    success_message = _("Colección de compañías «%(obj)s» creado.")
    title = _("Crear colección de compañías")


class CompanyCollectionUpdateView(BaseCompanyCollection, BaseUpdate):
    form_class = f.CompanyCollectionForm
    list_url = "panel:company-collection_list"
    success_url = "panel:company-collection_list"
    cancel_url = "panel:company-collection_list"
    success_message = _("Colección de compañías «%(obj)s» actualizado.")
    title = _("Editar colección de compañías")


class GameCharacterCollectionDeleteView(BaseGameCharacterCollection, BaseDelete):
    list_url = "panel:game-character-collection_list"
    success_url = "panel:game-character-collection_list"
    cancel_url = "panel:game-character-collection_list"
    success_message = _("Colección de personajes de juego «%(obj)s» eliminada.")
    title = _("Eliminar colección de personajes de juego")


class GameCharacterCollectionCreateView(BaseGameCharacterCollection, BaseCreate):
    form_class = f.GameCharacterCollectionForm
    list_url = "panel:game-character-collection_list"
    success_url = "panel:game-character-collection_list"
    cancel_url = "panel:game-character-collection_list"
    success_message = _("Colección de personajes de juego «%(obj)s» creado.")
    title = _("Crear colección de personajes de juego")


class GameCharacterCollectionUpdateView(BaseGameCharacterCollection, BaseUpdate):
    form_class = f.GameCharacterCollectionForm
    list_url = "panel:game-character-collection_list"
    success_url = "panel:game-character-collection_list"
    cancel_url = "panel:game-character-collection_list"
    success_message = _("Colección de personajes de juego «%(obj)s» actualizado.")
    title = _("Editar colección de personajes de juego")


class GameCollectionDeleteView(BaseGameCollection, BaseDelete):
    list_url = "panel:game-collection_list"
    success_url = "panel:game-collection_list"
    cancel_url = "panel:game-collection_list"
    success_message = _("Colección de juegos «%(obj)s» eliminada.")
    title = _("Eliminar colección de juegos")


class GameCollectionCreateView(BaseGameCollection, BaseCreate):
    form_class = f.GameCollectionForm
    list_url = "panel:game-collection_list"
    success_url = "panel:game-collection_list"
    cancel_url = "panel:game-collection_list"
    success_message = _("Colección de juegos «%(obj)s» creado.")
    title = _("Crear colección de juegos")


class GameCollectionUpdateView(BaseGameCollection, BaseUpdate):
    form_class = f.GameCollectionForm
    list_url = "panel:game-collection_list"
    success_url = "panel:game-collection_list"
    cancel_url = "panel:game-collection_list"
    success_message = _("Colección de juegos «%(obj)s» actualizado.")
    title = _("Editar colección de juegos")


class MangaCollectionDeleteView(BaseMangaCollection, BaseDelete):
    list_url = "panel:manga-collection_list"
    success_url = "panel:manga-collection_list"
    cancel_url = "panel:manga-collection_list"
    success_message = _("Colección de manga «%(obj)s» eliminada.")
    title = _("Eliminar colección de manga")


class MangaCollectionCreateView(BaseMangaCollection, BaseCreate):
    form_class = f.MangaCollectionForm
    list_url = "panel:manga-collection_list"
    success_url = "panel:manga-collection_list"
    cancel_url = "panel:manga-collection_list"
    success_message = _("Colección de manga «%(obj)s» creado.")
    title = _("Crear colección de manga")


class MangaCollectionUpdateView(BaseMangaCollection, BaseUpdate):
    form_class = f.MangaCollectionForm
    list_url = "panel:manga-collection_list"
    success_url = "panel:manga-collection_list"
    cancel_url = "panel:manga-collection_list"
    success_message = _("Colección de manga «%(obj)s» actualizado.")
    title = _("Editar colección de manga")


class MovieCollectionDeleteView(BaseMovieCollection, BaseDelete):
    list_url = "panel:movie-collection_list"
    success_url = "panel:movie-collection_list"
    cancel_url = "panel:movie-collection_list"
    success_message = _("Colección de películas «%(obj)s» eliminada.")
    title = _("Eliminar colección de películas")


class MovieCollectionCreateView(BaseMovieCollection, BaseCreate):
    form_class = f.MovieCollectionForm
    list_url = "panel:movie-collection_list"
    success_url = "panel:movie-collection_list"
    cancel_url = "panel:movie-collection_list"
    success_message = _("Colección de películas «%(obj)s» creado.")
    title = _("Crear colección de películas")


class MovieCollectionUpdateView(BaseMovieCollection, BaseUpdate):
    form_class = f.MovieCollectionForm
    list_url = "panel:movie-collection_list"
    success_url = "panel:movie-collection_list"
    cancel_url = "panel:movie-collection_list"
    success_message = _("Colección de películas «%(obj)s» actualizado.")
    title = _("Editar colección de películas")


class PersonCollectionDeleteView(BasePersonCollection, BaseDelete):
    list_url = "panel:person-collection_list"
    success_url = "panel:person-collection_list"
    cancel_url = "panel:person-collection_list"
    success_message = _("Colección de personas «%(obj)s» eliminada.")
    title = _("Eliminar colección de personas")


class PersonCollectionCreateView(BasePersonCollection, BaseCreate):
    form_class = f.PersonCollectionForm
    list_url = "panel:person-collection_list"
    success_url = "panel:person-collection_list"
    cancel_url = "panel:person-collection_list"
    success_message = _("Colección de personas «%(obj)s» creado.")
    title = _("Crear colección de personas")


class PersonCollectionUpdateView(BasePersonCollection, BaseUpdate):
    form_class = f.PersonCollectionForm
    list_url = "panel:person-collection_list"
    success_url = "panel:person-collection_list"
    cancel_url = "panel:person-collection_list"
    success_message = _("Colección de personas «%(obj)s» actualizado.")
    title = _("Editar colección de personas")


class SerieCollectionDeleteView(BaseSerieCollection, BaseDelete):
    list_url = "panel:serie-collection_list"
    success_url = "panel:serie-collection_list"
    cancel_url = "panel:serie-collection_list"
    success_message = _("Colección de series «%(obj)s» eliminada.")
    title = _("Eliminar colección de series")


class SerieCollectionCreateView(BaseSerieCollection, BaseCreate):
    form_class = f.SerieCollectionForm
    list_url = "panel:serie-collection_list"
    success_url = "panel:serie-collection_list"
    cancel_url = "panel:serie-collection_list"
    success_message = _("Colección de series «%(obj)s» creado.")
    title = _("Crear colección de series")


class SerieCollectionUpdateView(BaseSerieCollection, BaseUpdate):
    form_class = f.SerieCollectionForm
    list_url = "panel:serie-collection_list"
    success_url = "panel:serie-collection_list"
    cancel_url = "panel:serie-collection_list"
    success_message = _("Colección de series «%(obj)s» actualizado.")
    title = _("Editar colección de series")


class SongCollectionDeleteView(BaseSongCollection, BaseDelete):
    list_url = "panel:song-collection_list"
    success_url = "panel:song-collection_list"
    cancel_url = "panel:song-collection_list"
    success_message = _("Colección de canciones «%(obj)s» eliminada.")
    title = _("Eliminar colección de canciones")


class SongCollectionCreateView(BaseSongCollection, BaseCreate):
    form_class = f.SongCollectionForm
    list_url = "panel:song-collection_list"
    success_url = "panel:song-collection_list"
    cancel_url = "panel:song-collection_list"
    success_message = _("Colección de canciones «%(obj)s» creado.")
    title = _("Crear colección de canciones")


class SongCollectionUpdateView(BaseSongCollection, BaseUpdate):
    form_class = f.SongCollectionForm
    list_url = "panel:song-collection_list"
    success_url = "panel:song-collection_list"
    cancel_url = "panel:song-collection_list"
    success_message = _("Colección de canciones «%(obj)s» actualizado.")
    title = _("Editar colección de canciones")


class CollectionLogCreateView(BaseCollectionLog, BaseCreate):
    form_class = f.CollectionLogForm
    form_template = "collections/form/collection_log.html"
    list_url = "panel:collection-log_list"
    success_url = "panel:collection-log_list"
    cancel_url = "panel:collection-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class CollectionLogUpdateView(BaseCollectionLog, BaseUpdate):
    form_class = f.CollectionLogForm
    form_template = "collections/form/collection_log.html"
    list_url = "panel:collection-log_list"
    success_url = "panel:collection-log_list"
    cancel_url = "panel:collection-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class CollectionLogDeleteView(BaseCollectionLog, BaseDelete):
    list_url = "panel:collection-log_list"
    success_url = "panel:collection-log_list"
    cancel_url = "panel:collection-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
