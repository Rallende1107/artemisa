"""URLs del panel para music (sección «Música»): home + CRUD por entidad.

Rutas EXPLÍCITAS (estilo Hades): una `path()` por vista, con su `name=` editable.
Sin funciones que las generen. Se montan en el namespace `panel` desde core/panel_urls.py.

Rutas por entidad: list · [nuevo] · data (DataTables) · select (AJAX FK/M2M) ·
detail · editar · eliminar · accion (toggle is_active/is_staff/...).

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.music import views as v
from apps.music.views import v8_import as imp
from core.views import AdminImageActionView, AdminToggleView


urlpatterns = [
    path('', include('apps.music.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('music/', v.MusicHomeView.as_view(), name='music-home'),

    # ---------- album · Album ----------
    path('album/', v.AlbumListView.as_view(), name='album_list'),
    path('album/create/', v.AlbumCreateView.as_view(), name='album_create'),
    path('album/<int:pk>/', v.AlbumDetailView.as_view(), name='album_detail'),
    path('album/<int:pk>/update/', v.AlbumUpdateView.as_view(), name='album_update'),
    path('album/<int:pk>/delete/', v.AlbumDeleteView.as_view(), name='album_delete'),
    path('album/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AlbumListView.model, entity='album', label='álbum', namespace='panel'), name='album_toggle'),
    path('album/<str:tipo>/<str:pk>/', v.AlbumListByView.as_view(), name='album_by'),

    # ---------- album-image · AlbumImage ----------
    path('album-image/', v.AlbumImageListView.as_view(), name='album-image_list'),
    path('album-image/download/', v.AlbumImageDownloadView.as_view(), name='album-image_download'),   # descargar pendientes (N o todas)
    path('album-image/create/', v.AlbumImageCreateView.as_view(), name='album-image_create'),
    path('album-image/<int:pk>/', v.AlbumImageDetailView.as_view(), name='album-image_detail'),
    path('album-image/<int:pk>/update/', v.AlbumImageUpdateView.as_view(), name='album-image_update'),
    path('album-image/<int:pk>/delete/', v.AlbumImageDeleteView.as_view(), name='album-image_delete'),
    path('album-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AlbumImageListView.model, entity='album-image', label='imagen', namespace='panel'), name='album-image_toggle'),
    path('album-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.AlbumImageListView.model), name='album-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('album-image/<str:tipo>/<str:pk>/', v.AlbumImageListByView.as_view(), name='album-image_by'),

    # ---------- music-album-type · AlbumType ----------
    path('music-album-type/', v.AlbumTypeListView.as_view(), name='music-album-type_list'),
    path('music-album-type/create/', v.AlbumTypeCreateView.as_view(), name='music-album-type_create'),
    path('music-album-type/<int:pk>/', v.AlbumTypeDetailView.as_view(), name='music-album-type_detail'),
    path('music-album-type/<int:pk>/update/', v.AlbumTypeUpdateView.as_view(), name='music-album-type_update'),
    path('music-album-type/<int:pk>/delete/', v.AlbumTypeDeleteView.as_view(), name='music-album-type_delete'),
    path('music-album-type/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AlbumTypeListView.model, entity='music-album-type', label='tipo de álbum', namespace='panel'), name='music-album-type_toggle'),

    # ---------- artist · Artist ----------
    path('artist/', v.ArtistListView.as_view(), name='artist_list'),
    path('artist/create/', v.ArtistCreateView.as_view(), name='artist_create'),
    path('artist/<int:pk>/', v.ArtistDetailView.as_view(), name='artist_detail'),
    path('artist/<int:pk>/update/', v.ArtistUpdateView.as_view(), name='artist_update'),
    path('artist/<int:pk>/delete/', v.ArtistDeleteView.as_view(), name='artist_delete'),
    path('artist/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ArtistListView.model, entity='artist', label='artista', namespace='panel'), name='artist_toggle'),
    path('artist/<str:tipo>/<str:pk>/', v.ArtistListByView.as_view(), name='artist_by'),

    # ---------- artist-image · ArtistImage ----------
    path('artist-image/', v.ArtistImageListView.as_view(), name='artist-image_list'),
    path('artist-image/download/', v.ArtistImageDownloadView.as_view(), name='artist-image_download'),   # descargar pendientes (N o todas)
    path('artist-image/create/', v.ArtistImageCreateView.as_view(), name='artist-image_create'),
    path('artist-image/<int:pk>/', v.ArtistImageDetailView.as_view(), name='artist-image_detail'),
    path('artist-image/<int:pk>/update/', v.ArtistImageUpdateView.as_view(), name='artist-image_update'),
    path('artist-image/<int:pk>/delete/', v.ArtistImageDeleteView.as_view(), name='artist-image_delete'),
    path('artist-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ArtistImageListView.model, entity='artist-image', label='imagen', namespace='panel'), name='artist-image_toggle'),
    path('artist-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.ArtistImageListView.model), name='artist-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('artist-image/<str:tipo>/<str:pk>/', v.ArtistImageListByView.as_view(), name='artist-image_by'),

    # ---------- artist-member · ArtistMember ----------
    path('artist-member/', v.ArtistMemberListView.as_view(), name='artist-member_list'),
    path('artist-member/create/', v.ArtistMemberCreateView.as_view(), name='artist-member_create'),
    path('artist-member/<int:pk>/', v.ArtistMemberDetailView.as_view(), name='artist-member_detail'),
    path('artist-member/<int:pk>/update/', v.ArtistMemberUpdateView.as_view(), name='artist-member_update'),
    path('artist-member/<int:pk>/delete/', v.ArtistMemberDeleteView.as_view(), name='artist-member_delete'),
    path('artist-member/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ArtistMemberListView.model, entity='artist-member', label='miembro', namespace='panel'), name='artist-member_toggle'),
    path('artist-member/<str:tipo>/<str:pk>/', v.ArtistMemberListByView.as_view(), name='artist-member_by'),

    # ---------- music-artist-type · ArtistType ----------
    path('music-artist-type/', v.ArtistTypeListView.as_view(), name='music-artist-type_list'),
    path('music-artist-type/create/', v.ArtistTypeCreateView.as_view(), name='music-artist-type_create'),
    path('music-artist-type/<int:pk>/', v.ArtistTypeDetailView.as_view(), name='music-artist-type_detail'),
    path('music-artist-type/<int:pk>/update/', v.ArtistTypeUpdateView.as_view(), name='music-artist-type_update'),
    path('music-artist-type/<int:pk>/delete/', v.ArtistTypeDeleteView.as_view(), name='music-artist-type_delete'),
    path('music-artist-type/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ArtistTypeListView.model, entity='music-artist-type', label='tipo de artista', namespace='panel'), name='music-artist-type_toggle'),

    # ---------- data-deezer-album · DataDeezerAlbum ----------
    path('data-deezer-album/', v.DataDeezerAlbumListView.as_view(), name='data-deezer-album_list'),
    path('data-deezer-album/create/', v.DataDeezerAlbumCreateView.as_view(), name='data-deezer-album_create'),
    path('data-deezer-album/<int:pk>/', v.DataDeezerAlbumDetailView.as_view(), name='data-deezer-album_detail'),
    path('data-deezer-album/<int:pk>/update/', v.DataDeezerAlbumUpdateView.as_view(), name='data-deezer-album_update'),
    path('data-deezer-album/<int:pk>/delete/', v.DataDeezerAlbumDeleteView.as_view(), name='data-deezer-album_delete'),

    # ---------- data-deezer-artist · DataDeezerArtist ----------
    path('data-deezer-artist/', v.DataDeezerArtistListView.as_view(), name='data-deezer-artist_list'),
    path('data-deezer-artist/create/', v.DataDeezerArtistCreateView.as_view(), name='data-deezer-artist_create'),
    path('data-deezer-artist/<int:pk>/', v.DataDeezerArtistDetailView.as_view(), name='data-deezer-artist_detail'),
    path('data-deezer-artist/<int:pk>/update/', v.DataDeezerArtistUpdateView.as_view(), name='data-deezer-artist_update'),
    path('data-deezer-artist/<int:pk>/delete/', v.DataDeezerArtistDeleteView.as_view(), name='data-deezer-artist_delete'),

    # ---------- data-deezer-genre · DataDeezerGenre ----------
    path('data-deezer-genre/', v.DataDeezerGenreListView.as_view(), name='data-deezer-genre_list'),
    path('data-deezer-genre/create/', v.DataDeezerGenreCreateView.as_view(), name='data-deezer-genre_create'),
    path('data-deezer-genre/<int:pk>/', v.DataDeezerGenreDetailView.as_view(), name='data-deezer-genre_detail'),
    path('data-deezer-genre/<int:pk>/update/', v.DataDeezerGenreUpdateView.as_view(), name='data-deezer-genre_update'),
    path('data-deezer-genre/<int:pk>/delete/', v.DataDeezerGenreDeleteView.as_view(), name='data-deezer-genre_delete'),

    # ---------- data-deezer-track · DataDeezerTrack ----------
    path('data-deezer-track/', v.DataDeezerTrackListView.as_view(), name='data-deezer-track_list'),
    path('data-deezer-track/create/', v.DataDeezerTrackCreateView.as_view(), name='data-deezer-track_create'),
    path('data-deezer-track/<int:pk>/', v.DataDeezerTrackDetailView.as_view(), name='data-deezer-track_detail'),
    path('data-deezer-track/<int:pk>/update/', v.DataDeezerTrackUpdateView.as_view(), name='data-deezer-track_update'),
    path('data-deezer-track/<int:pk>/delete/', v.DataDeezerTrackDeleteView.as_view(), name='data-deezer-track_delete'),

    # ---------- music-genre · Genre ----------
    path('music-genre/', v.GenreListView.as_view(), name='music-genre_list'),
    path('music-genre/create/', v.GenreCreateView.as_view(), name='music-genre_create'),
    path('music-genre/<int:pk>/', v.GenreDetailView.as_view(), name='music-genre_detail'),
    path('music-genre/<int:pk>/update/', v.GenreUpdateView.as_view(), name='music-genre_update'),
    path('music-genre/<int:pk>/delete/', v.GenreDeleteView.as_view(), name='music-genre_delete'),
    path('music-genre/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GenreListView.model, entity='music-genre', label='género', namespace='panel'), name='music-genre_toggle'),

    # ---------- music-genre-alias · GenreAlias ----------
    path('music-genre-alias/', v.GenreAliasListView.as_view(), name='music-genre-alias_list'),
    path('music-genre-alias/create/', v.GenreAliasCreateView.as_view(), name='music-genre-alias_create'),
    path('music-genre-alias/<int:pk>/', v.GenreAliasDetailView.as_view(), name='music-genre-alias_detail'),
    path('music-genre-alias/<int:pk>/update/', v.GenreAliasUpdateView.as_view(), name='music-genre-alias_update'),
    path('music-genre-alias/<int:pk>/delete/', v.GenreAliasDeleteView.as_view(), name='music-genre-alias_delete'),
    path('music-genre-alias/<str:tipo>/<str:pk>/', v.GenreAliasListByView.as_view(), name='music-genre-alias_by'),

    # ---------- music-role · Role ----------
    path('music-role/', v.RoleListView.as_view(), name='music-role_list'),
    path('music-role/create/', v.RoleCreateView.as_view(), name='music-role_create'),
    path('music-role/<int:pk>/', v.RoleDetailView.as_view(), name='music-role_detail'),
    path('music-role/<int:pk>/update/', v.RoleUpdateView.as_view(), name='music-role_update'),
    path('music-role/<int:pk>/delete/', v.RoleDeleteView.as_view(), name='music-role_delete'),
    path('music-role/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RoleListView.model, entity='music-role', label='rol', namespace='panel'), name='music-role_toggle'),
    path('music-role/<str:tipo>/<str:pk>/', v.RoleListByView.as_view(), name='music-role_by'),

    # ---------- song · Song ----------
    path('song/', v.SongListView.as_view(), name='song_list'),
    path('song/create/', v.SongCreateView.as_view(), name='song_create'),
    path('song/<int:pk>/', v.SongDetailView.as_view(), name='song_detail'),
    path('song/<int:pk>/update/', v.SongUpdateView.as_view(), name='song_update'),
    path('song/<int:pk>/delete/', v.SongDeleteView.as_view(), name='song_delete'),
    path('song/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SongListView.model, entity='song', label='canción', namespace='panel'), name='song_toggle'),
    path('song/<str:tipo>/<str:pk>/', v.SongListByView.as_view(), name='song_by'),

    # ---------- song-composer · SongComposer ----------
    path('song-composer/', v.SongComposerListView.as_view(), name='song-composer_list'),
    path('song-composer/create/', v.SongComposerCreateView.as_view(), name='song-composer_create'),
    path('song-composer/<int:pk>/', v.SongComposerDetailView.as_view(), name='song-composer_detail'),
    path('song-composer/<int:pk>/update/', v.SongComposerUpdateView.as_view(), name='song-composer_update'),
    path('song-composer/<int:pk>/delete/', v.SongComposerDeleteView.as_view(), name='song-composer_delete'),
    path('song-composer/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SongComposerListView.model, entity='song-composer', label='compositor de canción', namespace='panel'), name='song-composer_toggle'),
    path('song-composer/<str:tipo>/<str:pk>/', v.SongComposerListByView.as_view(), name='song-composer_by'),

    # ---------- song-translation · SongTranslation ----------
    path('song-translation/', v.SongTranslationListView.as_view(), name='song-translation_list'),
    path('song-translation/create/', v.SongTranslationCreateView.as_view(), name='song-translation_create'),
    path('song-translation/<int:pk>/', v.SongTranslationDetailView.as_view(), name='song-translation_detail'),
    path('song-translation/<int:pk>/update/', v.SongTranslationUpdateView.as_view(), name='song-translation_update'),
    path('song-translation/<int:pk>/delete/', v.SongTranslationDeleteView.as_view(), name='song-translation_delete'),
    path('song-translation/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SongTranslationListView.model, entity='song-translation', label='traducción de canción', namespace='panel'), name='song-translation_toggle'),
    path('song-translation/<str:tipo>/<str:pk>/', v.SongTranslationListByView.as_view(), name='song-translation_by'),

    # ---------- importación Deezer (antes en apps/imports): lanzador + datos crudos ----------
    # Lanzadores Deezer: UNA vista por tabla Data; sus formas de importar van en la misma página.
    path("deezer/artist/", imp.LoadDeezerDataArtistView.as_view(), name="deezer-artist"),
    path("deezer/artist/search/", imp.LoadDeezerDataArtistSearchView.as_view(), name="deezer-artist-search"),
    path("deezer/album/", imp.LoadDeezerDataAlbumView.as_view(), name="deezer-album"),
    path("deezer/album/search/", imp.LoadDeezerDataAlbumSearchView.as_view(), name="deezer-album-search"),
    path("deezer/song/", imp.LoadDeezerDataTrackView.as_view(), name="deezer-song"),
    path("deezer/song/search/", imp.LoadDeezerDataTrackSearchView.as_view(), name="deezer-song-search"),
    path("deezer/genres/", imp.LoadDeezerGenreView.as_view(), name="deezer-genres"),
    path("deezer/procesar/", imp.DeezerProcessPendingView.as_view(), name="deezer-procesar"),   # POST «Procesar pendientes»

    # ---------- music-log · MusicLog ----------
    path('music-log/', v.MusicLogListView.as_view(), name='music-log_list'),
    path('music-log/create/', v.MusicLogCreateView.as_view(), name='music-log_create'),
    path('music-log/<int:pk>/', v.MusicLogDetailView.as_view(), name='music-log_detail'),
    path('music-log/<int:pk>/update/', v.MusicLogUpdateView.as_view(), name='music-log_update'),
    path('music-log/<int:pk>/delete/', v.MusicLogDeleteView.as_view(), name='music-log_delete'),
]
