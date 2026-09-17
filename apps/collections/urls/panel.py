"""URLs del panel para collections (sección «Colecciones»): home + moderación de
las colecciones por medio, personajes y personas incluidos (ver y borrar) + CRUD de los estados + log.

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.collections import views as v


urlpatterns = [
    path('', include('apps.collections.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('collections/', v.CollectionsHomeView.as_view(), name='collections-home'),

    # ---------- album-collection · AlbumCollection ----------
    path('album-collection/', v.AlbumCollectionListView.as_view(), name='album-collection_list'),
    path('album-collection/create/', v.AlbumCollectionCreateView.as_view(), name='album-collection_create'),
    path('album-collection/<int:pk>/', v.AlbumCollectionDetailView.as_view(), name='album-collection_detail'),
    path('album-collection/<int:pk>/update/', v.AlbumCollectionUpdateView.as_view(), name='album-collection_update'),
    path('album-collection/<int:pk>/delete/', v.AlbumCollectionDeleteView.as_view(), name='album-collection_delete'),

    # ---------- anime-collection · AnimeCollection ----------
    path('anime-collection/', v.AnimeCollectionListView.as_view(), name='anime-collection_list'),
    path('anime-collection/create/', v.AnimeCollectionCreateView.as_view(), name='anime-collection_create'),
    path('anime-collection/<int:pk>/', v.AnimeCollectionDetailView.as_view(), name='anime-collection_detail'),
    path('anime-collection/<int:pk>/update/', v.AnimeCollectionUpdateView.as_view(), name='anime-collection_update'),
    path('anime-collection/<int:pk>/delete/', v.AnimeCollectionDeleteView.as_view(), name='anime-collection_delete'),

    # ---------- artist-collection · ArtistCollection ----------
    path('artist-collection/', v.ArtistCollectionListView.as_view(), name='artist-collection_list'),
    path('artist-collection/create/', v.ArtistCollectionCreateView.as_view(), name='artist-collection_create'),
    path('artist-collection/<int:pk>/', v.ArtistCollectionDetailView.as_view(), name='artist-collection_detail'),
    path('artist-collection/<int:pk>/update/', v.ArtistCollectionUpdateView.as_view(), name='artist-collection_update'),
    path('artist-collection/<int:pk>/delete/', v.ArtistCollectionDeleteView.as_view(), name='artist-collection_delete'),

    # ---------- character-collection · CharacterCollection ----------
    path('character-collection/', v.CharacterCollectionListView.as_view(), name='character-collection_list'),
    path('character-collection/create/', v.CharacterCollectionCreateView.as_view(), name='character-collection_create'),
    path('character-collection/<int:pk>/', v.CharacterCollectionDetailView.as_view(), name='character-collection_detail'),
    path('character-collection/<int:pk>/update/', v.CharacterCollectionUpdateView.as_view(), name='character-collection_update'),
    path('character-collection/<int:pk>/delete/', v.CharacterCollectionDeleteView.as_view(), name='character-collection_delete'),

    # ---------- company-collection · CompanyCollection ----------
    path('company-collection/', v.CompanyCollectionListView.as_view(), name='company-collection_list'),
    path('company-collection/create/', v.CompanyCollectionCreateView.as_view(), name='company-collection_create'),
    path('company-collection/<int:pk>/', v.CompanyCollectionDetailView.as_view(), name='company-collection_detail'),
    path('company-collection/<int:pk>/update/', v.CompanyCollectionUpdateView.as_view(), name='company-collection_update'),
    path('company-collection/<int:pk>/delete/', v.CompanyCollectionDeleteView.as_view(), name='company-collection_delete'),

    # ---------- game-character-collection · GameCharacterCollection ----------
    path('game-character-collection/', v.GameCharacterCollectionListView.as_view(), name='game-character-collection_list'),
    path('game-character-collection/create/', v.GameCharacterCollectionCreateView.as_view(), name='game-character-collection_create'),
    path('game-character-collection/<int:pk>/', v.GameCharacterCollectionDetailView.as_view(), name='game-character-collection_detail'),
    path('game-character-collection/<int:pk>/update/', v.GameCharacterCollectionUpdateView.as_view(), name='game-character-collection_update'),
    path('game-character-collection/<int:pk>/delete/', v.GameCharacterCollectionDeleteView.as_view(), name='game-character-collection_delete'),

    # ---------- game-collection · GameCollection ----------
    path('game-collection/', v.GameCollectionListView.as_view(), name='game-collection_list'),
    path('game-collection/create/', v.GameCollectionCreateView.as_view(), name='game-collection_create'),
    path('game-collection/<int:pk>/', v.GameCollectionDetailView.as_view(), name='game-collection_detail'),
    path('game-collection/<int:pk>/update/', v.GameCollectionUpdateView.as_view(), name='game-collection_update'),
    path('game-collection/<int:pk>/delete/', v.GameCollectionDeleteView.as_view(), name='game-collection_delete'),

    # ---------- manga-collection · MangaCollection ----------
    path('manga-collection/', v.MangaCollectionListView.as_view(), name='manga-collection_list'),
    path('manga-collection/create/', v.MangaCollectionCreateView.as_view(), name='manga-collection_create'),
    path('manga-collection/<int:pk>/', v.MangaCollectionDetailView.as_view(), name='manga-collection_detail'),
    path('manga-collection/<int:pk>/update/', v.MangaCollectionUpdateView.as_view(), name='manga-collection_update'),
    path('manga-collection/<int:pk>/delete/', v.MangaCollectionDeleteView.as_view(), name='manga-collection_delete'),

    # ---------- movie-collection · MovieCollection ----------
    path('movie-collection/', v.MovieCollectionListView.as_view(), name='movie-collection_list'),
    path('movie-collection/create/', v.MovieCollectionCreateView.as_view(), name='movie-collection_create'),
    path('movie-collection/<int:pk>/', v.MovieCollectionDetailView.as_view(), name='movie-collection_detail'),
    path('movie-collection/<int:pk>/update/', v.MovieCollectionUpdateView.as_view(), name='movie-collection_update'),
    path('movie-collection/<int:pk>/delete/', v.MovieCollectionDeleteView.as_view(), name='movie-collection_delete'),

    # ---------- person-collection · PersonCollection ----------
    path('person-collection/', v.PersonCollectionListView.as_view(), name='person-collection_list'),
    path('person-collection/create/', v.PersonCollectionCreateView.as_view(), name='person-collection_create'),
    path('person-collection/<int:pk>/', v.PersonCollectionDetailView.as_view(), name='person-collection_detail'),
    path('person-collection/<int:pk>/update/', v.PersonCollectionUpdateView.as_view(), name='person-collection_update'),
    path('person-collection/<int:pk>/delete/', v.PersonCollectionDeleteView.as_view(), name='person-collection_delete'),

    # ---------- serie-collection · SerieCollection ----------
    path('serie-collection/', v.SerieCollectionListView.as_view(), name='serie-collection_list'),
    path('serie-collection/create/', v.SerieCollectionCreateView.as_view(), name='serie-collection_create'),
    path('serie-collection/<int:pk>/', v.SerieCollectionDetailView.as_view(), name='serie-collection_detail'),
    path('serie-collection/<int:pk>/update/', v.SerieCollectionUpdateView.as_view(), name='serie-collection_update'),
    path('serie-collection/<int:pk>/delete/', v.SerieCollectionDeleteView.as_view(), name='serie-collection_delete'),

    # ---------- song-collection · SongCollection ----------
    path('song-collection/', v.SongCollectionListView.as_view(), name='song-collection_list'),
    path('song-collection/create/', v.SongCollectionCreateView.as_view(), name='song-collection_create'),
    path('song-collection/<int:pk>/', v.SongCollectionDetailView.as_view(), name='song-collection_detail'),
    path('song-collection/<int:pk>/update/', v.SongCollectionUpdateView.as_view(), name='song-collection_update'),
    path('song-collection/<int:pk>/delete/', v.SongCollectionDeleteView.as_view(), name='song-collection_delete'),

    # ---------- collection-log · CollectionLog ----------
    path('collection-log/', v.CollectionLogListView.as_view(), name='collection-log_list'),
    path('collection-log/create/', v.CollectionLogCreateView.as_view(), name='collection-log_create'),
    path('collection-log/<int:pk>/', v.CollectionLogDetailView.as_view(), name='collection-log_detail'),
    path('collection-log/<int:pk>/update/', v.CollectionLogUpdateView.as_view(), name='collection-log_update'),
    path('collection-log/<int:pk>/delete/', v.CollectionLogDeleteView.as_view(), name='collection-log_delete'),
]
