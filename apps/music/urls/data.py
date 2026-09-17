"""URLs de DATOS del panel de music: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.music import views as v


urlpatterns = [
    # ---------- album · Album ----------
    path('album/data/', v.AlbumDataView.as_view(), name='album_data'),
    path('album/data/<str:tipo>/<str:pk>/', v.AlbumDataView.as_view(), name='album_data-by'),
    path('album/select/', v.AlbumSelectView.as_view(), name='album_select'),

    # ---------- album-image · AlbumImage ----------
    path('album-image/data/', v.AlbumImageDataView.as_view(), name='album-image_data'),
    path('album-image/data/<str:tipo>/<str:pk>/', v.AlbumImageDataView.as_view(), name='album-image_data-by'),
    path('album-image/select/', v.AlbumImageSelectView.as_view(), name='album-image_select'),

    # ---------- music-album-type · AlbumType ----------
    path('music-album-type/data/', v.AlbumTypeDataView.as_view(), name='music-album-type_data'),
    path('music-album-type/select/', v.AlbumTypeSelectView.as_view(), name='music-album-type_select'),

    # ---------- artist · Artist ----------
    path('artist/data/', v.ArtistDataView.as_view(), name='artist_data'),
    path('artist/data/<str:tipo>/<str:pk>/', v.ArtistDataView.as_view(), name='artist_data-by'),
    path('artist/select/', v.ArtistSelectView.as_view(), name='artist_select'),

    # ---------- artist-image · ArtistImage ----------
    path('artist-image/data/', v.ArtistImageDataView.as_view(), name='artist-image_data'),
    path('artist-image/data/<str:tipo>/<str:pk>/', v.ArtistImageDataView.as_view(), name='artist-image_data-by'),
    path('artist-image/select/', v.ArtistImageSelectView.as_view(), name='artist-image_select'),

    # ---------- artist-member · ArtistMember ----------
    path('artist-member/data/', v.ArtistMemberDataView.as_view(), name='artist-member_data'),
    path('artist-member/data/<str:tipo>/<str:pk>/', v.ArtistMemberDataView.as_view(), name='artist-member_data-by'),
    path('artist-member/select/', v.ArtistMemberSelectView.as_view(), name='artist-member_select'),

    # ---------- music-artist-type · ArtistType ----------
    path('music-artist-type/data/', v.ArtistTypeDataView.as_view(), name='music-artist-type_data'),
    path('music-artist-type/select/', v.ArtistTypeSelectView.as_view(), name='music-artist-type_select'),

    # ---------- data-deezer-album · DataDeezerAlbum ----------
    path('data-deezer-album/data/', v.DataDeezerAlbumDataView.as_view(), name='data-deezer-album_data'),

    # ---------- data-deezer-artist · DataDeezerArtist ----------
    path('data-deezer-artist/data/', v.DataDeezerArtistDataView.as_view(), name='data-deezer-artist_data'),

    # ---------- data-deezer-genre · DataDeezerGenre ----------
    path('data-deezer-genre/data/', v.DataDeezerGenreDataView.as_view(), name='data-deezer-genre_data'),

    # ---------- data-deezer-track · DataDeezerTrack ----------
    path('data-deezer-track/data/', v.DataDeezerTrackDataView.as_view(), name='data-deezer-track_data'),

    # ---------- music-genre · Genre ----------
    path('music-genre/data/', v.GenreDataView.as_view(), name='music-genre_data'),
    path('music-genre/select/', v.GenreSelectView.as_view(), name='music-genre_select'),

    # ---------- music-genre-alias · GenreAlias ----------
    path('music-genre-alias/data/', v.GenreAliasDataView.as_view(), name='music-genre-alias_data'),
    path('music-genre-alias/data/<str:tipo>/<str:pk>/', v.GenreAliasDataView.as_view(), name='music-genre-alias_data-by'),

    # ---------- music-role · Role ----------
    path('music-role/data/', v.RoleDataView.as_view(), name='music-role_data'),
    path('music-role/data/<str:tipo>/<str:pk>/', v.RoleDataView.as_view(), name='music-role_data-by'),
    path('music-role/select/', v.RoleSelectView.as_view(), name='music-role_select'),

    # ---------- song · Song ----------
    path('song/data/', v.SongDataView.as_view(), name='song_data'),
    path('song/data/<str:tipo>/<str:pk>/', v.SongDataView.as_view(), name='song_data-by'),
    path('song/select/', v.SongSelectView.as_view(), name='song_select'),

    # ---------- song-composer · SongComposer ----------
    path('song-composer/data/', v.SongComposerDataView.as_view(), name='song-composer_data'),
    path('song-composer/data/<str:tipo>/<str:pk>/', v.SongComposerDataView.as_view(), name='song-composer_data-by'),
    path('song-composer/select/', v.SongComposerSelectView.as_view(), name='song-composer_select'),

    # ---------- song-translation · SongTranslation ----------
    path('song-translation/data/', v.SongTranslationDataView.as_view(), name='song-translation_data'),
    path('song-translation/data/<str:tipo>/<str:pk>/', v.SongTranslationDataView.as_view(), name='song-translation_data-by'),
    path('song-translation/select/', v.SongTranslationSelectView.as_view(), name='song-translation_select'),

    # ---------- music-log · MusicLog ----------
    path('music-log/data/', v.MusicLogDataView.as_view(), name='music-log_data'),
]
