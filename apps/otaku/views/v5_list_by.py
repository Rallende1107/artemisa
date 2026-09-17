"""otaku · listas «por» (ListBy) de los DOS lados, público y gestión: «Películas del género X», «Reparto de X»,
«Personas de Chile». El mapa `filter_config` (tipo → campo, título, fondo) vive en el mixin `_BaseXBy` de base.py y lo comparten
con las Data; aquí cada lista declara sus rutas, su miga y su fondo por defecto. Ruta: `…/por/<tipo>/<pk>/`."""
from apps.otaku.views.base import BaseAnimeCharacterContext, BaseAnimeContext, BaseAnimeImageContext, BaseAnimeSongContext, BaseAnimeStaffContext, BaseAnimeTitleContext, BaseCharacterContext, BaseCharacterImageContext, BaseCharacterNicknameContext, BaseCharacterVoiceContext, BaseMangaAuthorContext, BaseMangaCharacterContext, BaseMangaContext, BaseMangaImageContext, BaseMangaTitleContext, BasePersonMALContext
from core.shared.views.base import AdminListByView, PublicListByView


# ==============================================================================
# Público
# ==============================================================================


class AnimePublicListByView(BaseAnimeContext, PublicListByView):
    """genero, tema, demografia, estudio, productora, licenciataria, tipo, estado, temporada, fuente, clasificacion, personaje, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "otaku:anime-by-data"
    by_url = "otaku:anime-by"
    full_list_url = "otaku:anime-catalog"
    parent_urls = {"personaje": "otaku:character-detail", "persona": "personas:person-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-otaku-anime"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    icon = "bi-collection-play"


class AnimeImagePublicListByView(BaseAnimeImageContext, PublicListByView):
    """anime."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "otaku:anime-images-by-data"
    by_url = "otaku:anime-images-by"
    parent_urls = {"anime": "otaku:anime-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-otaku-anime-image"
    background_fallback = "bg-otaku-anime"
    section = "otaku"
    icon = "bi-images"


class CharacterPublicListByView(BaseCharacterContext, PublicListByView):
    """anime, manga, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "otaku:characters-by-data"
    by_url = "otaku:characters-by"
    full_list_url = "otaku:characters-catalog"
    parent_urls = {"anime": "otaku:anime-detail", "manga": "otaku:manga-detail", "persona": "personas:person-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-otaku-character"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    icon = "bi-emoji-smile"


class CharacterImagePublicListByView(BaseCharacterImageContext, PublicListByView):
    """personaje."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "otaku:character-images-by-data"
    by_url = "otaku:character-images-by"
    parent_urls = {"personaje": "otaku:character-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-otaku-character"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    icon = "bi-images"


class MangaPublicListByView(BaseMangaContext, PublicListByView):
    """genero, tema, demografia, revista, tipo, estado, fuente, clasificacion, personaje, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "otaku:manga-by-data"
    by_url = "otaku:manga-by"
    full_list_url = "otaku:manga-catalog"
    parent_urls = {"personaje": "otaku:character-detail", "persona": "personas:person-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-otaku-manga"
    background_fallback = "bg-otaku-home"
    section = "otaku"
    icon = "bi-book"


class MangaImagePublicListByView(BaseMangaImageContext, PublicListByView):
    """manga."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "otaku:manga-images-by-data"
    by_url = "otaku:manga-images-by"
    parent_urls = {"manga": "otaku:manga-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-otaku-manga-image"
    background_fallback = "bg-otaku-manga"
    section = "otaku"
    icon = "bi-images"


# ==============================================================================
# Gestión
# ==============================================================================


class AnimeListByView(BaseAnimeContext, AdminListByView):
    """genero, tema, demografia, estudio, productora, licenciataria, tipo, estado, temporada, fuente, clasificacion, personaje, persona."""
    home_url = "panel:otaku-home"
    data_url = "panel:anime_data-by"
    full_list_url = "panel:anime_list"
    create_url = "panel:anime_create"


class AnimeCharacterListByView(BaseAnimeCharacterContext, AdminListByView):
    """anime, personaje."""
    home_url = "panel:otaku-home"
    data_url = "panel:anime-character_data-by"
    full_list_url = "panel:anime-character_list"
    create_url = "panel:anime-character_create"


class AnimeImageListByView(BaseAnimeImageContext, AdminListByView):
    """anime."""
    home_url = "panel:otaku-home"
    data_url = "panel:anime-image_data-by"
    full_list_url = "panel:anime-image_list"
    create_url = "panel:anime-image_create"


class AnimeSongListByView(BaseAnimeSongContext, AdminListByView):
    """anime."""
    home_url = "panel:otaku-home"
    data_url = "panel:anime-song_data-by"
    full_list_url = "panel:anime-song_list"
    create_url = "panel:anime-song_create"


class AnimeStaffListByView(BaseAnimeStaffContext, AdminListByView):
    """anime, persona."""
    home_url = "panel:otaku-home"
    data_url = "panel:anime-staff_data-by"
    full_list_url = "panel:anime-staff_list"
    create_url = "panel:anime-staff_create"


class AnimeTitleListByView(BaseAnimeTitleContext, AdminListByView):
    """anime."""
    home_url = "panel:otaku-home"
    data_url = "panel:anime-title_data-by"
    full_list_url = "panel:anime-title_list"
    create_url = "panel:anime-title_create"


class CharacterListByView(BaseCharacterContext, AdminListByView):
    """anime, manga, persona."""
    home_url = "panel:otaku-home"
    data_url = "panel:character_data-by"
    full_list_url = "panel:character_list"
    create_url = "panel:character_create"


class CharacterImageListByView(BaseCharacterImageContext, AdminListByView):
    """personaje."""
    home_url = "panel:otaku-home"
    data_url = "panel:character-image_data-by"
    full_list_url = "panel:character-image_list"
    create_url = "panel:character-image_create"


class CharacterNicknameListByView(BaseCharacterNicknameContext, AdminListByView):
    """personaje."""
    home_url = "panel:otaku-home"
    data_url = "panel:character-nickname_data-by"
    full_list_url = "panel:character-nickname_list"
    create_url = "panel:character-nickname_create"


class CharacterVoiceListByView(BaseCharacterVoiceContext, AdminListByView):
    """persona, personaje."""
    home_url = "panel:otaku-home"
    data_url = "panel:character-voice_data-by"
    full_list_url = "panel:character-voice_list"
    create_url = "panel:character-voice_create"


class MangaListByView(BaseMangaContext, AdminListByView):
    """genero, tema, demografia, revista, tipo, estado, fuente, clasificacion, personaje, persona."""
    home_url = "panel:otaku-home"
    data_url = "panel:manga_data-by"
    full_list_url = "panel:manga_list"
    create_url = "panel:manga_create"


class MangaAuthorListByView(BaseMangaAuthorContext, AdminListByView):
    """manga, persona."""
    home_url = "panel:otaku-home"
    data_url = "panel:manga-author_data-by"
    full_list_url = "panel:manga-author_list"
    create_url = "panel:manga-author_create"


class MangaCharacterListByView(BaseMangaCharacterContext, AdminListByView):
    """manga, personaje."""
    home_url = "panel:otaku-home"
    data_url = "panel:manga-character_data-by"
    full_list_url = "panel:manga-character_list"
    create_url = "panel:manga-character_create"


class MangaImageListByView(BaseMangaImageContext, AdminListByView):
    """manga."""
    home_url = "panel:otaku-home"
    data_url = "panel:manga-image_data-by"
    full_list_url = "panel:manga-image_list"
    create_url = "panel:manga-image_create"


class MangaTitleListByView(BaseMangaTitleContext, AdminListByView):
    """manga."""
    home_url = "panel:otaku-home"
    data_url = "panel:manga-title_data-by"
    full_list_url = "panel:manga-title_list"
    create_url = "panel:manga-title_create"


class PersonMALListByView(BasePersonMALContext, AdminListByView):
    """persona."""
    home_url = "panel:otaku-home"
    data_url = "panel:person-mal_data-by"
    full_list_url = "panel:person-mal_list"
    create_url = "panel:person-mal_create"
