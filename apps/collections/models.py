"""
Capa colección (funcionalidad NUEVA, no existe en Hades).
Tracker personal estilo MyAnimeList / Letterboxd: cada usuario construye su
biblioteca sobre el catálogo. Aquí vive TODO lo de colección:

  · los ESTADOS por medio son CHOICES fijos (<Medio>CollectionStatus en core/shared/models/choices.py), únicos por tipo de
    colección: anime, manga, serie, movie, game y music;
  · una TABLA de colección por medio (AnimeCollection, MovieCollection…): usuario
    × título con estado, puntuación y favorito — FK directas, sin genéricos
    (lo común viene de core.shared.models.abstract.ModelBaseCollectionItem);
  · personajes y personas también son colecciones (CharacterCollection,
    PersonCollection), sin estados; «favorito» es el booleano de cada fila;
  · cada tabla solo declara `content`, `status` (si hay) y FORMATO; su clave y su ficha
    se deducen del contenido (ver core ModelBaseCollection);
  · «lo veo en» y «lo descargué de» (sitio, formato, calidad) son columnas de la
    propia fila de colección (ModelBaseCollectionItem): nada aparte.
"""
from django.db import models

from core.shared.models.abstract import ModelBaseCollection, ModelBaseCollectionItem, ModelBaseLog  # ModelBaseCollection se re-exporta (templatetags, views.public)
from core.shared.models.choices import AnimeCollectionStatus, GameCollectionStatus, MangaCollectionStatus, MovieCollectionStatus, MusicCollectionStatus, SerieCollectionStatus


class AlbumCollection(ModelBaseCollectionItem):
    FORMATO = "for_music"
    content = models.ForeignKey("music.Album", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="álbum")
    STATUS_CHOICES = MusicCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=MusicCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de álbumes"
        verbose_name_plural = "colecciones de álbumes"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_album_collection")]


class AnimeCollection(ModelBaseCollectionItem):
    FORMATO = "for_video"
    content = models.ForeignKey("otaku.Anime", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="anime")
    STATUS_CHOICES = AnimeCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=AnimeCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de anime"
        verbose_name_plural = "colecciones de anime"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_anime_collection")]


class ArtistCollection(ModelBaseCollectionItem):
    FORMATO = "for_music"
    content = models.ForeignKey("music.Artist", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="artista")
    STATUS_CHOICES = MusicCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=MusicCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de artistas"
        verbose_name_plural = "colecciones de artistas"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_artist_collection")]


class CharacterCollection(ModelBaseCollectionItem):
    """Personajes: colección sin estados (se marcan como favoritos, se puntúan…)."""
    content = models.ForeignKey("otaku.Character", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="personaje")

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de personajes"
        verbose_name_plural = "colecciones de personajes"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_character_collection")]


class CompanyCollection(ModelBaseCollectionItem):
    """Compañías: colección sin estados (se marcan como favoritos, se puntúan…)."""
    content = models.ForeignKey("companies.Company", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="compañía")

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de compañías"
        verbose_name_plural = "colecciones de compañías"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_company_collection")]


class GameCharacterCollection(ModelBaseCollectionItem):
    """Personajes de juego: colección sin estados (se marcan como favoritos, se puntúan…)."""
    MEDIO = "game-character"      # otaku.Character ya usa «character»
    content = models.ForeignKey("games.Character", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="personaje de juego")

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de personajes de juego"
        verbose_name_plural = "colecciones de personajes de juego"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_game_character_collection")]


class GameCollection(ModelBaseCollectionItem):
    FORMATO = "for_other"
    content = models.ForeignKey("games.Game", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="juego")
    STATUS_CHOICES = GameCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=GameCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de juegos"
        verbose_name_plural = "colecciones de juegos"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_game_collection")]


class MangaCollection(ModelBaseCollectionItem):
    FORMATO = "for_document"
    content = models.ForeignKey("otaku.Manga", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="manga")
    STATUS_CHOICES = MangaCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=MangaCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de manga"
        verbose_name_plural = "colecciones de manga"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_manga_collection")]


class MovieCollection(ModelBaseCollectionItem):
    FORMATO = "for_video"
    content = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="película")
    STATUS_CHOICES = MovieCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=MovieCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de películas"
        verbose_name_plural = "colecciones de películas"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_movie_collection")]


class PersonCollection(ModelBaseCollectionItem):
    """Personas: colección sin estados (se marcan como favoritos, se puntúan…)."""
    content = models.ForeignKey("people.Person", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="persona")

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de personas"
        verbose_name_plural = "colecciones de personas"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_person_collection")]


class SerieCollection(ModelBaseCollectionItem):
    FORMATO = "for_video"
    content = models.ForeignKey("series.Serie", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="serie")
    STATUS_CHOICES = SerieCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=SerieCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de series"
        verbose_name_plural = "colecciones de series"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_serie_collection")]


class SongCollection(ModelBaseCollectionItem):
    FORMATO = "for_music"
    content = models.ForeignKey("music.Song", on_delete=models.CASCADE,
                                related_name="collection_items", verbose_name="canción")
    STATUS_CHOICES = MusicCollectionStatus
    status = models.CharField(verbose_name="estado", max_length=20, choices=MusicCollectionStatus.choices, blank=True)

    class Meta(ModelBaseCollectionItem.Meta):
        verbose_name = "colección de canciones"
        verbose_name_plural = "colecciones de canciones"
        constraints = [models.UniqueConstraint(fields=["user", "content"], name="uniq_song_collection")]


class CollectionLog(ModelBaseLog):
    """Log de la app: auditoría del panel (altas, ediciones, borrados, toggles) y
    cualquier proceso propio. Una tabla por app, para no amontonar."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de colecciones"
        verbose_name_plural = "logs de colecciones"
