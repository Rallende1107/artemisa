"""BASE de la sección: config por entidad (clases privadas) + constantes de columnas.

La clase privada `_Entidad` es la única fuente de config compartida; las vistas
de los módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company, CompanyImage
from apps.otaku.models import Anime, AnimeCharacter, AnimeImage, AnimeSong, AnimeStaff, AnimeTitle, Character, CharacterImage, CharacterNickname, CharacterVoice, CompanyMAL, DataAnilistAnime, DataAnilistCharacter, DataAnilistManga, DataAnilistPerson, DataMalAnime, DataMalAnimeCharacter, DataMalAnimePicture, DataMalAnimeStaff, DataMalCharacter, DataMalCharacterPicture, DataMalManga, DataMalMangaCharacter, DataMalMangaPicture, DataMalPerson, DataMalPersonPicture, Demographic, DemographicAlias, Genre, GenreAlias, Manga, MangaAuthor, MangaCharacter, MangaImage, MangaTitle, OtakuLog, PersonMAL, Relation, Role, Source, Status, Theme, ThemeAlias, Type, Year
from apps.people.models import PersonImage


# NAV PÚBLICO de la sección: las pastillas que se ven en las páginas públicas de esta app. Cada entrada es
#   (etiqueta, ruta, icono, {nombres de ruta donde queda ACTIVA})
# y la resuelve `core.context_processors.seccion_nav` (calcula el href y cuál se enciende). Se declara en
# `nav`; una vista puede pisarlo con el suyo, o con () para no pintar barra.
# Otaku tiene TRES: las páginas de anime enseñan el nav de anime, las de manga el suyo, y lo compartido
# (home, personajes) una mezcla. Antes se adivinaba por el nombre de la ruta; ahora lo dice cada entidad.
_HOME = (
    _("Otaku"), "otaku:home", "bi-stars", {"home"}
    )


_ANIME = (
    _("Anime"), "otaku:anime-catalog", "bi-collection-play", {
        "anime", "anime-catalog", "anime-detail", "anime-by", "anime-images-by"}
    )


_MANGA = (
    _("Manga"), "otaku:manga-catalog", "bi-book", {
        "manga",
        "manga-catalog",
        "manga-detail",
        "manga-by",
        "manga-images-by"}
    )


_PERSONAJES = (
    _("Personajes"), "otaku:characters-catalog", "bi-emoji-smile",
    {"characters", "characters-catalog", "character-detail", "characters-by", "character-images-by"})


_ESTUDIOS = (_("Estudios"), "otaku:studios-catalog", "bi-building", {"studios", "studios-catalog", "studio-detail"})


_PRODUCTORAS = (_("Productoras"), "otaku:producers-catalog", "bi-briefcase", {"producers", "producers-catalog", "producer-detail"})


_LICENCIATARIAS = (_("Licenciatarias"), "otaku:licensors-catalog", "bi-globe2", {"licensors", "licensors-catalog", "licensor-detail"})


_REVISTAS = (_("Revistas"), "otaku:magazines-catalog", "bi-journal-bookmark", {"magazines", "magazines-catalog", "magazine-detail"})


NAV_PUBLICO_INTERNO = (_HOME, _ANIME, _MANGA, _PERSONAJES, _ESTUDIOS, _PRODUCTORAS, _LICENCIATARIAS, _REVISTAS)


NAV_PUBLICO = (_HOME, _ANIME, _MANGA, _PERSONAJES, _ESTUDIOS)   # lo compartido por los dos medios


class _Otaku:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-otaku-home"   # respaldo si falta la imagen
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    nav = NAV_PUBLICO          # las pastillas públicas; anime y manga declaran las suyas


class BaseAnime(_Otaku):
    model = Anime
    entity = 'anime'
    label = _('anime')
    label_plural = _('animes')
    background_image = "bg-otaku-anime"
    nav = NAV_PUBLICO_INTERNO


class BaseAnimeCharacter(_Otaku):
    model = AnimeCharacter
    entity = 'anime-character'
    label = _('personaje')
    label_plural = _('personajes de anime')
    background_image = "bg-otaku-anime-character"


class BaseAnimeCharacterContext(BaseAnimeCharacter):
    """Mapa «por» de personajes de anime: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "anime": ("anime", _("Personajes de anime de {padre}"), ""),
        "personaje": ("character", _("Personajes de anime de {padre}"), ""),
    }


class BaseAnimeContext(BaseAnime):
    """Mapa «por» de animes: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("genres", _("Animes del género {padre}"), "bg-otaku-genre"),
        "tema": ("themes", _("Animes del tema {padre}"), "bg-otaku-theme"),
        "demografia": ("demographics", _("Animes de la demografía {padre}"), "bg-otaku-demographic"),
        "estudio": ("studios", _("Animes del estudio {padre}"), "bg-otaku-studio"),
        "productora": ("producers", _("Animes producidos por {padre}"), "bg-otaku-producer"),
        "licenciataria": ("licensors", _("Animes licenciados por {padre}"), "bg-otaku-licensor"),
        "tipo": ("anime_type", _("Animes de tipo {padre}"), "bg-otaku-type"),
        "estado": ("status", _("Animes con estado {padre}"), "bg-otaku-status"),
        "season": ("season", _("Animes · {valor}"), "bg-otaku-anime"),
        "fuente": ("source", _("Animes basados en {padre}"), "bg-otaku-source"),
        "rating": ("rating", _("Animes · {valor}"), "bg-otaku-anime"),
        "personaje": ("otaku.Character", _("Anime con {padre}"), "bg-otaku-anime"),
        "persona": ("people.Person", _("Anime de {padre}"), "bg-otaku-anime-staff"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "personaje":
            return qs.filter(characters__character=padre)
        if tipo == "persona":
            return qs.filter(staff__person=padre, staff__is_active=True)
        return super().filter_by(qs, padre, tipo)


class BaseAnimeImage(_Otaku):
    model = AnimeImage
    entity = 'anime-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-otaku-anime-image"


class BaseAnimeImageContext(BaseAnimeImage):
    """Mapa «por» de imágenes extra de anime: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "anime": ("anime", _("Imágenes de {padre}"), "bg-otaku-anime-image"),
    }


class BaseAnimeSong(_Otaku):
    model = AnimeSong
    entity = 'anime-song'
    label = _('canción')
    label_plural = _('canciones de anime')
    background_image = "bg-otaku-anime-song"


class BaseAnimeSongContext(BaseAnimeSong):
    """Mapa «por» de canciones de anime: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "anime": ("anime", _("Canciones de anime de {padre}"), ""),
        "type": ("type", _("Canciones de anime · {valor}"), "bg-otaku-anime-song"),
    }


class BaseAnimeStaff(_Otaku):
    model = AnimeStaff
    entity = 'anime-staff'
    label = _('staff')
    label_plural = _('staff de anime')
    background_image = "bg-otaku-anime-staff"


class BaseAnimeStaffContext(BaseAnimeStaff):
    """Mapa «por» de staff de anime: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "anime": ("anime", _("Staff de anime de {padre}"), ""),
        "persona": ("person", _("Staff de anime de {padre}"), ""),
    }


class BaseAnimeTitle(_Otaku):
    model = AnimeTitle
    entity = 'anime-title'
    label = _('título')
    label_plural = _('títulos')
    background_image = "bg-otaku-title-anime"


class BaseAnimeTitleContext(BaseAnimeTitle):
    """Mapa «por» de títulos de anime: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "anime": ("anime", _("Títulos de {padre}"), ""),
    }


class BaseCharacter(_Otaku):
    model = Character
    entity = 'character'
    label = _('personaje')
    label_plural = _('personajes')
    background_image = "bg-otaku-character"


class BaseCharacterContext(BaseCharacter):
    """Mapa «por» de personajes: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "anime": ("otaku.Anime", _("Personajes de {padre}"), "bg-otaku-anime-character"),
        "manga": ("otaku.Manga", _("Personajes de {padre}"), "bg-otaku-manga-character"),
        "persona": ("people.Person", _("Personajes de {padre}"), "bg-otaku-character"),
    }
    sub_via = {"anime": ('characters', 'character_id', 'role__name'), "manga": ('characters', 'character_id', 'role__name')}

    def filter_by(self, qs, padre, tipo):
        if tipo == "anime":
            return qs.filter(anime_appearances__anime=padre, anime_appearances__is_active=True)
        if tipo == "manga":
            return qs.filter(manga_appearances__manga=padre, manga_appearances__is_active=True)
        if tipo == "persona":
            return qs.filter(voices__person=padre)
        return super().filter_by(qs, padre, tipo)


class BaseCharacterImage(_Otaku):
    model = CharacterImage
    entity = 'character-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-otaku-character-image"


class BaseCharacterImageContext(BaseCharacterImage):
    """Mapa «por» de imágenes extra de personaje: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "personaje": ("character", _("Imágenes de {padre}"), "bg-otaku-character"),
    }


class BaseCharacterNickname(_Otaku):
    model = CharacterNickname
    entity = 'character-nickname'
    label = _('apodo')
    label_plural = _('apodos')
    background_image = "bg-otaku-character-nickname"


class BaseCharacterNicknameContext(BaseCharacterNickname):
    """Mapa «por» de apodos de personaje: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "personaje": ("character", _("Apodos de {padre}"), ""),
    }


class BaseCharacterVoice(_Otaku):
    model = CharacterVoice
    entity = 'character-voice'
    label = _('voz')
    label_plural = _('voces de personaje')
    background_image = "bg-otaku-voice-character"


class BaseCharacterVoiceContext(BaseCharacterVoice):
    """Mapa «por» de voces de personaje: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "persona": ("person", _("Voces de personaje de {padre}"), ""),
        "personaje": ("character", _("Voces de personaje de {padre}"), ""),
    }


class BaseCompanyImageMal(_Otaku):
    """Lista FIJA de Otaku sobre companies.CompanyImage: solo las imágenes de compañías con ficha MAL. El modelo vive en su app;
    la vista es de Otaku (su sección, su miga y su fondo)."""
    model = CompanyImage
    entity = "company-image-mal"
    label = _("imagen")
    label_plural = _("imágenes de compañías (MAL)")
    background_image = "bg-otaku-company-mal"


class BasePersonImageMal(_Otaku):
    """Lista FIJA de Otaku sobre people.PersonImage: solo las imágenes de personas con ficha MAL. El modelo vive en su app;
    la vista es de Otaku (su sección, su miga y su fondo)."""
    model = PersonImage
    entity = "person-image-mal"
    label = _("imagen")
    label_plural = _("imágenes de personas (MAL)")
    background_image = "bg-otaku-person"

class BaseCompanyMAL(_Otaku):
    model = CompanyMAL
    entity = 'company-mal'
    label = _('compañía (MAL)')
    label_plural = _('compañías (MAL)')
    background_image = "bg-otaku-company-mal"


class BaseDataAnilistAnime(_Otaku):
    model = DataAnilistAnime
    entity = 'data-anilist-anime'
    label = _('datos de anime (AniList)')
    label_plural = _('datos · Anime (AniList)')
    title_create = _("Crear datos de anime (AniList)")
    title_delete = _("Eliminar datos de anime (AniList)")
    title_list = _("Lista de datos · Anime (AniList)")
    title_update = _("Editar datos de anime (AniList)")
    background_image = "bg-otaku-data-anilist-anime"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataAnilistCharacter(_Otaku):
    model = DataAnilistCharacter
    entity = 'data-anilist-character'
    label = _('datos de personaje (AniList)')
    label_plural = _('datos · Personaje (AniList)')
    title_create = _("Crear datos de personaje (AniList)")
    title_delete = _("Eliminar datos de personaje (AniList)")
    title_list = _("Lista de datos · Personaje (AniList)")
    title_update = _("Editar datos de personaje (AniList)")
    background_image = "bg-otaku-data-anilist-character"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataAnilistManga(_Otaku):
    model = DataAnilistManga
    entity = 'data-anilist-manga'
    label = _('datos de manga (AniList)')
    label_plural = _('datos · Manga (AniList)')
    title_create = _("Crear datos de manga (AniList)")
    title_delete = _("Eliminar datos de manga (AniList)")
    title_list = _("Lista de datos · Manga (AniList)")
    title_update = _("Editar datos de manga (AniList)")
    background_image = "bg-otaku-data-anilist-manga"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataAnilistPerson(_Otaku):
    model = DataAnilistPerson
    entity = 'data-anilist-person'
    label = _('datos de persona (AniList)')
    label_plural = _('datos · Persona (AniList)')
    title_create = _("Crear datos de persona (AniList)")
    title_delete = _("Eliminar datos de persona (AniList)")
    title_list = _("Lista de datos · Persona (AniList)")
    title_update = _("Editar datos de persona (AniList)")
    background_image = "bg-otaku-data-anilist-person"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalAnime(_Otaku):
    model = DataMalAnime
    entity = 'data-mal-anime'
    label = _('datos de anime (MAL)')
    label_plural = _('Lista Datos Anime (MAL)')
    title_create = _("Crear datos de anime")
    title_delete = _("Eliminar datos de anime")
    title_list = _("Lista datos My Anime List Anime")
    title_update = _("Editar datos de anime")
    background_image = "bg-otaku-data-mal-anime"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalAnimeCharacter(_Otaku):
    model = DataMalAnimeCharacter
    entity = 'data-mal-anime-character'
    label = _('datos personajes de anime')
    label_plural = _('datos · Anime · personajes (MAL)')
    title_create = _("Crear datos personajes de anime")
    title_delete = _("Eliminar datos personajes de anime")
    title_list = _("Lista de datos · Anime · personajes (MAL)")
    title_update = _("Editar datos personajes de anime")
    background_image = "bg-otaku-data-mal-anime-character"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalAnimePicture(_Otaku):
    model = DataMalAnimePicture
    entity = 'data-mal-anime-picture'
    label = _('datos imágenes de anime')
    label_plural = _('datos · Anime · imágenes (MAL)')
    title_create = _("Crear datos imágenes de anime")
    title_delete = _("Eliminar datos imágenes de anime")
    title_list = _("Lista de datos · Anime · imágenes (MAL)")
    title_update = _("Editar datos imágenes de anime")
    background_image = "bg-otaku-data-mal-anime-picture"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalAnimeStaff(_Otaku):
    model = DataMalAnimeStaff
    entity = 'data-mal-anime-staff'
    label = _('datos staff de anime')
    label_plural = _('datos · Anime · staff (MAL)')
    title_create = _("Crear datos staff de anime")
    title_delete = _("Eliminar datos staff de anime")
    title_list = _("Lista de datos · Anime · staff (MAL)")
    title_update = _("Editar datos staff de anime")
    background_image = "bg-otaku-data-mal-anime-staff"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalCharacter(_Otaku):
    model = DataMalCharacter
    entity = 'data-mal-character'
    label = _('datos de personaje')
    label_plural = _('datos · Personaje (MAL)')
    title_create = _("Crear datos de personaje")
    title_delete = _("Eliminar datos de personaje")
    title_list = _("Lista de datos · Personaje (MAL)")
    title_update = _("Editar datos de personaje")
    background_image = "bg-otaku-data-mal-character"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalCharacterPicture(_Otaku):
    model = DataMalCharacterPicture
    entity = 'data-mal-character-picture'
    label = _('datos imágenes de personaje')
    label_plural = _('datos · Personaje · imágenes (MAL)')
    title_create = _("Crear datos imágenes de personaje")
    title_delete = _("Eliminar datos imágenes de personaje")
    title_list = _("Lista de datos · Personaje · imágenes (MAL)")
    title_update = _("Editar datos imágenes de personaje")
    background_image = "bg-otaku-data-mal-character-picture"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalManga(_Otaku):
    model = DataMalManga
    entity = 'data-mal-manga'
    label = _('datos de manga')
    label_plural = _('datos · Manga (MAL)')
    title_create = _("Crear datos de manga")
    title_delete = _("Eliminar datos de manga")
    title_list = _("Lista de datos · Manga (MAL)")
    title_update = _("Editar datos de manga")
    background_image = "bg-otaku-data-mal-manga"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalMangaCharacter(_Otaku):
    model = DataMalMangaCharacter
    entity = 'data-mal-manga-character'
    label = _('datos personajes de manga')
    label_plural = _('datos · Manga · personajes (MAL)')
    title_create = _("Crear datos personajes de manga")
    title_delete = _("Eliminar datos personajes de manga")
    title_list = _("Lista de datos · Manga · personajes (MAL)")
    title_update = _("Editar datos personajes de manga")
    background_image = "bg-otaku-data-mal-manga-character"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalMangaPicture(_Otaku):
    model = DataMalMangaPicture
    entity = 'data-mal-manga-picture'
    label = _('datos imágenes de manga')
    label_plural = _('datos · Manga · imágenes (MAL)')
    title_create = _("Crear datos imágenes de manga")
    title_delete = _("Eliminar datos imágenes de manga")
    title_list = _("Lista de datos · Manga · imágenes (MAL)")
    title_update = _("Editar datos imágenes de manga")
    background_image = "bg-otaku-data-mal-manga-picture"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalPerson(_Otaku):
    model = DataMalPerson
    entity = 'data-mal-person'
    label = _('datos de persona')
    label_plural = _('datos · Persona (MAL)')
    title_create = _("Crear datos de persona")
    title_delete = _("Eliminar datos de persona")
    title_list = _("Lista de datos · Persona (MAL)")
    title_update = _("Editar datos de persona")
    background_image = "bg-otaku-data-mal-person"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDataMalPersonPicture(_Otaku):
    model = DataMalPersonPicture
    entity = 'data-mal-person-picture'
    label = _('datos imágenes de persona')
    label_plural = _('datos · Persona · imágenes (MAL)')
    title_create = _("Crear datos imágenes de persona")
    title_delete = _("Eliminar datos imágenes de persona")
    title_list = _("Lista de datos · Persona · imágenes (MAL)")
    title_update = _("Editar datos imágenes de persona")
    background_image = "bg-otaku-data-mal-person-picture"
    namespace = 'panel'
    page_template = 'panel/base.html'


class BaseDemographic(_Otaku):
    model = Demographic
    entity = 'demographic'
    label = _('demografía')
    label_plural = _('demografías')
    background_image = "bg-otaku-demographic"


class BaseDemographicAlias(_Otaku):
    model = DemographicAlias
    entity = 'demographic-alias'
    label = _('alias de demografía')
    label_plural = _('alias de demografías')
    background_image = "bg-otaku-demographic-alias"


class BaseDemographicAliasContext(BaseDemographicAlias):
    """Mapa «por» de alias: por su demografía (/panel/demographic-alias/demographic/<id>/)."""
    filter_config = {
        "demographic": ("demographic", _("Alias de demografías de {padre}"), "bg-otaku-demographic"),
    }


class BaseGenre(_Otaku):
    model = Genre
    entity = 'genre'
    label = _('género')
    label_plural = _('géneros')
    background_image = "bg-otaku-genre"


def _sub_anime(a):
    partes = [str(a.year)] if a.year else []
    if a.episodes:
        partes.append(f"{a.episodes} {_('ep')}")
    return " · ".join(partes)


def _sub_manga(m):
    partes = [str(m.year)] if m.year else []
    if m.chapters:
        partes.append(f"{m.chapters} {_('cap')}")
    return " · ".join(partes)


def _img(x):
    f = getattr(x, "image", None)
    try:
        return f.url if f else None
    except (ValueError, AttributeError):
        return None


class BaseGenreAlias(_Otaku):
    model = GenreAlias
    entity = 'genre-alias'
    label = _('alias de género')
    label_plural = _('alias de géneros')
    background_image = "bg-otaku-genre-alias"


class BaseGenreAliasContext(BaseGenreAlias):
    """Mapa «por» de alias: por su género (/panel/genre-alias/genre/<id>/)."""
    filter_config = {
        "genre": ("genre", _("Alias de géneros de {padre}"), "bg-otaku-genre"),
    }


class BaseLicensor(_Otaku):
    """La compañía GLOBAL (apps/companies) en su papel de licensor de otaku: la usan los catálogos públicos."""
    model = Company
    entity = 'company'
    label = _('licenciataria')
    label_plural = _('licenciatarias')
    background_image = "bg-otaku-licensor"
    nav = NAV_PUBLICO_INTERNO


class BaseManga(_Otaku):
    model = Manga
    entity = 'manga'
    label = _('manga')
    label_plural = _('mangas')
    background_image = "bg-otaku-manga"
    nav = NAV_PUBLICO_INTERNO


class BaseMangaAuthor(_Otaku):
    model = MangaAuthor
    entity = 'manga-author'
    label = _('autor')
    label_plural = _('autores de manga')
    background_image = "bg-otaku-author-manga"


class BaseMangaAuthorContext(BaseMangaAuthor):
    """Mapa «por» de autores de manga: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "manga": ("manga", _("Autores de manga de {padre}"), ""),
        "persona": ("person", _("Autores de manga de {padre}"), ""),
    }


class BaseMangaCharacter(_Otaku):
    model = MangaCharacter
    entity = 'manga-character'
    label = _('personaje')
    label_plural = _('personajes de manga')
    background_image = "bg-otaku-manga-character"


class BaseMangaCharacterContext(BaseMangaCharacter):
    """Mapa «por» de personajes de manga: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "manga": ("manga", _("Personajes de manga de {padre}"), ""),
        "personaje": ("character", _("Personajes de manga de {padre}"), ""),
    }


class BaseMangaContext(BaseManga):
    """Mapa «por» de mangas: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "genero": ("genres", _("Mangas del género {padre}"), "bg-otaku-genre"),
        "tema": ("themes", _("Mangas del tema {padre}"), "bg-otaku-theme"),
        "demografia": ("demographics", _("Mangas de la demografía {padre}"), "bg-otaku-demographic"),
        "revista": ("serializations", _("Mangas serializados en {padre}"), "bg-otaku-serialization"),
        "tipo": ("manga_type", _("Mangas de tipo {padre}"), "bg-otaku-type"),
        "estado": ("status", _("Mangas con estado {padre}"), "bg-otaku-status"),
        "fuente": ("source", _("Mangas basados en {padre}"), "bg-otaku-source"),
        "rating": ("rating", _("Mangas · {valor}"), "bg-otaku-manga"),
        "season": ("season", _("Mangas · {valor}"), "bg-otaku-manga"),
        "personaje": ("otaku.Character", _("Manga con {padre}"), "bg-otaku-manga"),
        "persona": ("people.Person", _("Manga de {padre}"), "bg-otaku-author-manga"),
    }

    def filter_by(self, qs, padre, tipo):
        if tipo == "personaje":
            return qs.filter(characters__character=padre)
        if tipo == "persona":
            return qs.filter(authors__person=padre, authors__is_active=True)
        return super().filter_by(qs, padre, tipo)


class BaseMangaImage(_Otaku):
    model = MangaImage
    entity = 'manga-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-otaku-manga-image"


class BaseMangaImageContext(BaseMangaImage):
    """Mapa «por» de imágenes extra de manga: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "manga": ("manga", _("Imágenes de {padre}"), "bg-otaku-manga-image"),
    }


class BaseMangaTitle(_Otaku):
    model = MangaTitle
    entity = 'manga-title'
    label = _('título')
    label_plural = _('títulos')
    background_image = "bg-otaku-title-manga"


class BaseMangaTitleContext(BaseMangaTitle):
    """Mapa «por» de títulos de manga: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "manga": ("manga", _("Títulos de {padre}"), ""),
    }


class BasePersonMAL(_Otaku):
    model = PersonMAL
    entity = 'person-mal'
    label = _('persona (MAL)')
    label_plural = _('personas (MAL)')
    background_image = "bg-otaku-person"    # EXCEPCIÓN a bg-app-modelo: PersonMAL ES la persona del mundo otaku


class BasePersonMALContext(BasePersonMAL):
    """Mapa «por» de personas (MAL): tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "persona": ("person", _("Personas (MAL) de {padre}"), ""),
    }


class BaseProducer(_Otaku):
    """La compañía GLOBAL (apps/companies) en su papel de producer de otaku: la usan los catálogos públicos."""
    model = Company
    entity = 'company'
    label = _('productora')
    label_plural = _('productoras')
    background_image = "bg-otaku-producer"
    nav = NAV_PUBLICO_INTERNO


class BaseRelation(_Otaku):
    model = Relation
    entity = 'relation'
    label = _('relación')
    label_plural = _('relaciones')
    background_image = "bg-otaku-relation"


class BaseRole(_Otaku):
    model = Role
    entity = 'otaku-role'
    label = _('rol')
    label_plural = _('roles')
    background_image = "bg-otaku-role"


class BaseRoleContext(BaseRole):
    """Mapa «por» de roles: `type` acota por la familia fija (`RoleType`): /otaku-role/type/<valor>/."""
    filter_config = {
        "type": ("type", _("Roles de otaku · {valor}"), "bg-otaku-role"),
    }


class BaseSerialization(_Otaku):
    """La compañía GLOBAL (apps/companies) en su papel de serialization de otaku: la usan los catálogos públicos."""
    model = Company
    entity = 'company'
    label = _('serialización')
    label_plural = _('serializaciones')
    background_image = "bg-otaku-serialization"
    nav = NAV_PUBLICO_INTERNO


class BaseSource(_Otaku):
    model = Source
    entity = 'source'
    label = _('fuente')
    label_plural = _('fuentes')
    background_image = "bg-otaku-source"


class BaseStatus(_Otaku):
    model = Status
    entity = 'status'
    label = _('estado')
    label_plural = _('estados')
    background_image = "bg-otaku-status"


class BaseStudio(_Otaku):
    """La compañía GLOBAL (apps/companies) en su papel de studio de otaku: la usan los catálogos públicos."""
    model = Company
    entity = 'company'
    label = _('estudio')
    label_plural = _('estudios')
    background_image = "bg-otaku-studio"
    nav = NAV_PUBLICO_INTERNO


class BaseTheme(_Otaku):
    model = Theme
    entity = 'theme'
    label = _('tema')
    label_plural = _('temas')
    background_image = "bg-otaku-theme"


class BaseThemeAlias(_Otaku):
    model = ThemeAlias
    entity = 'theme-alias'
    label = _('alias de tema')
    label_plural = _('alias de temas')
    background_image = "bg-otaku-theme-alias"


class BaseThemeAliasContext(BaseThemeAlias):
    """Mapa «por» de alias: por su tema (/panel/theme-alias/theme/<id>/)."""
    filter_config = {
        "theme": ("theme", _("Alias de temas de {padre}"), "bg-otaku-theme"),
    }


class BaseType(_Otaku):
    model = Type
    entity = 'type'
    label = _('tipo')
    label_plural = _('tipos')
    background_image = "bg-otaku-type"


class BaseYear(_Otaku):
    model = Year
    entity = 'year'
    label = _('año')
    label_plural = _('años')
    background_image = "bg-otaku-year"


class BaseOtakuLog(_Otaku):
    model = OtakuLog
    entity = 'otaku-log'
    label = _('log')
    label_plural = _('log de otaku')
    background_image = "bg-otaku-log"
