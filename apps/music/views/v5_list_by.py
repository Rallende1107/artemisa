"""music · listas «por» (ListBy) de los DOS lados, público y gestión: «Películas del género X», «Reparto de X»,
«Personas de Chile». El mapa `filter_config` (tipo → campo, título, fondo) vive en el mixin `_BaseXBy` de base.py y lo comparten
con las Data; aquí cada lista declara sus rutas, su miga y su fondo por defecto. Ruta: `…/por/<tipo>/<pk>/`."""
from apps.music.views.base import BaseAlbumContext, BaseAlbumImageContext, BaseArtistContext, BaseArtistImageContext, BaseArtistMemberContext, BaseSongComposerContext, BaseSongContext, BaseSongTranslationContext
from core.shared.views.base import AdminListByView, PublicListByView


# ==============================================================================
# Público
# ==============================================================================


class AlbumPublicListByView(BaseAlbumContext, PublicListByView):
    """genero, tipo, artista."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "music:albums-by-data"
    by_url = "music:albums-by"
    full_list_url = "music:albums-catalog"
    parent_urls = {"artista": "music:artist-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-music-album"
    background_fallback = "bg-music-home"
    section = "musica"
    icon = "bi-disc"


class AlbumImagePublicListByView(BaseAlbumImageContext, PublicListByView):
    """album."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "music:album-images-by-data"
    by_url = "music:album-images-by"
    parent_urls = {"album": "music:album-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-music-album"
    background_fallback = "bg-music-home"
    section = "musica"
    icon = "bi-images"


class ArtistPublicListByView(BaseArtistContext, PublicListByView):
    """genero, tipo."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "music:artists-by-data"
    by_url = "music:artists-by"
    full_list_url = "music:artists-catalog"
    background_image = "bg-music-artist"
    background_fallback = "bg-music-home"
    section = "musica"
    icon = "bi-person-video2"


class ArtistImagePublicListByView(BaseArtistImageContext, PublicListByView):
    """artista."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "music:artist-images-by-data"
    by_url = "music:artist-images-by"
    parent_urls = {"artista": "music:artist-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-music-artist"
    background_fallback = "bg-music-home"
    section = "musica"
    icon = "bi-images"


class SongPublicListByView(BaseSongContext, PublicListByView):
    """genero, artista, album."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "music:songs-by-data"
    by_url = "music:songs-by"
    full_list_url = "music:songs-catalog"
    parent_urls = {"artista": "music:artist-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-music-song"
    background_fallback = "bg-music-home"
    section = "musica"
    icon = "bi-music-note-beamed"


# ==============================================================================
# Gestión
# ==============================================================================


class AlbumListByView(BaseAlbumContext, AdminListByView):
    """genero, tipo, artista."""
    home_url = "panel:music-home"
    data_url = "panel:album_data-by"
    full_list_url = "panel:album_list"
    create_url = "panel:album_create"


class AlbumImageListByView(BaseAlbumImageContext, AdminListByView):
    """album."""
    home_url = "panel:music-home"
    data_url = "panel:album-image_data-by"
    full_list_url = "panel:album-image_list"
    create_url = "panel:album-image_create"


class ArtistListByView(BaseArtistContext, AdminListByView):
    """genero, tipo."""
    home_url = "panel:music-home"
    data_url = "panel:artist_data-by"
    full_list_url = "panel:artist_list"
    create_url = "panel:artist_create"


class ArtistImageListByView(BaseArtistImageContext, AdminListByView):
    """artista."""
    home_url = "panel:music-home"
    data_url = "panel:artist-image_data-by"
    full_list_url = "panel:artist-image_list"
    create_url = "panel:artist-image_create"


class ArtistMemberListByView(BaseArtistMemberContext, AdminListByView):
    """artista, persona."""
    home_url = "panel:music-home"
    data_url = "panel:artist-member_data-by"
    full_list_url = "panel:artist-member_list"
    create_url = "panel:artist-member_create"


class SongListByView(BaseSongContext, AdminListByView):
    """genero, artista, album."""
    home_url = "panel:music-home"
    data_url = "panel:song_data-by"
    full_list_url = "panel:song_list"
    create_url = "panel:song_create"


class SongComposerListByView(BaseSongComposerContext, AdminListByView):
    """cancion, persona."""
    home_url = "panel:music-home"
    data_url = "panel:song-composer_data-by"
    full_list_url = "panel:song-composer_list"
    create_url = "panel:song-composer_create"


class SongTranslationListByView(BaseSongTranslationContext, AdminListByView):
    """cancion."""
    home_url = "panel:music-home"
    data_url = "panel:song-translation_data-by"
    full_list_url = "panel:song-translation_list"
    create_url = "panel:song-translation_create"
