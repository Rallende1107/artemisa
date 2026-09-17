"""URLs de DATOS del panel de collections: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.collections import views as v


urlpatterns = [
    # ---------- album-collection · AlbumCollection ----------
    path('album-collection/data/', v.AlbumCollectionDataView.as_view(), name='album-collection_data'),

    # ---------- anime-collection · AnimeCollection ----------
    path('anime-collection/data/', v.AnimeCollectionDataView.as_view(), name='anime-collection_data'),

    # ---------- artist-collection · ArtistCollection ----------
    path('artist-collection/data/', v.ArtistCollectionDataView.as_view(), name='artist-collection_data'),

    # ---------- character-collection · CharacterCollection ----------
    path('character-collection/data/', v.CharacterCollectionDataView.as_view(), name='character-collection_data'),

    # ---------- company-collection · CompanyCollection ----------
    path('company-collection/data/', v.CompanyCollectionDataView.as_view(), name='company-collection_data'),

    # ---------- game-character-collection · GameCharacterCollection ----------
    path('game-character-collection/data/', v.GameCharacterCollectionDataView.as_view(), name='game-character-collection_data'),

    # ---------- game-collection · GameCollection ----------
    path('game-collection/data/', v.GameCollectionDataView.as_view(), name='game-collection_data'),

    # ---------- manga-collection · MangaCollection ----------
    path('manga-collection/data/', v.MangaCollectionDataView.as_view(), name='manga-collection_data'),

    # ---------- movie-collection · MovieCollection ----------
    path('movie-collection/data/', v.MovieCollectionDataView.as_view(), name='movie-collection_data'),

    # ---------- person-collection · PersonCollection ----------
    path('person-collection/data/', v.PersonCollectionDataView.as_view(), name='person-collection_data'),

    # ---------- serie-collection · SerieCollection ----------
    path('serie-collection/data/', v.SerieCollectionDataView.as_view(), name='serie-collection_data'),

    # ---------- song-collection · SongCollection ----------
    path('song-collection/data/', v.SongCollectionDataView.as_view(), name='song-collection_data'),

    # ---------- collection-log · CollectionLog ----------
    path('collection-log/data/', v.CollectionLogDataView.as_view(), name='collection-log_data'),
]
