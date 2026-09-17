"""SIDEBAR del panel de gestión (/panel/): namespace, título, pie y el árbol
de navegación (`nav`, datos, no HTML). Se registra desde SystemConfig.ready().
«Navegación» solo navega (portada, sitio, admin); cada app —Sistema incluida— es
un árbol propio con su home. Las URLS en core/panel_urls.py."""
from django.utils.translation import gettext_lazy as _

from core.shared.views.sidebar import link, register_sidebar, Sidebar, tree


GESTION = Sidebar(
    namespace="panel",
    title=_("Panel de gestión"),
    footer=_("Panel de gestión"),
    # Las URLs (dashboard + secciones) están en core/panel_urls.py, explícitas.
    nav=[
        tree(_("Navegación"), icon="bi-compass", url="panel:home", entity="home", children=[
            link(_("Panel de gestión"), "panel:home", entity="home"),
            link(_("Ver sitio"), "pages:index"),
            link(_("Admin Django"), href="/admin/", super_only=True),
        ]),
        tree(_("Sistema"), icon="bi-cpu", url="panel:tasks-home", entity="tareas-home", children=[
            tree(_("Tareas"), children=[
                link(_("Tareas programadas (beat)"), "panel:scheduled-task_list", entity="scheduled-task"),
                link(_("Cursores de lote"), "panel:import-cursor_list", entity="import-cursor"),
                link(_("Cursores de Deezer"), "panel:import-cursor-deezer_list", entity="import-cursor-deezer"),
                link(_("Cursores de MAL"), "panel:import-cursor-mal_list", entity="import-cursor-mal"),
                link(_("Cursores de VNDB"), "panel:import-cursor-vndb_list", entity="import-cursor-vndb"),
            ]),
            tree(_("Nube (R2)"), children=[
                link(_("Archivos en la nube"), "panel:cloud-file_list", entity="cloud-file"),
            ]),
            tree(_("Registro"), children=[
                link(_("Ejecuciones (cancelador)"), "panel:task-run_list", entity="task-run"),
            ]),
        ]),
        tree(_("Usuarios"), icon="bi-people", url="panel:users-home", entity="usuario-home", children=[
            tree(_("Usuarios"), children=[
                link(_("Usuarios"), "panel:user_list", entity="user"),
            ]),
            tree(_("Registro"), children=[
                link(_("Actividad de usuarios"), "panel:user-activity_list", entity="user-activity"),
                link(_("Log de usuarios"), "panel:user-log_list", entity="user-log"),
            ]),
        ]),
        tree(_("Correos"), icon="bi-envelope-at", url="panel:mailing-home", entity="mailing-home", children=[
            tree(_("Configuración"), children=[
                link(_("Plantillas de correo"), "panel:email-template_list", entity="email-template"),
                link(_("Configuración"), "panel:mail-config", entity="mailing-config"),
            ]),
            tree(_("Envíos"), children=[
                link(_("Correos"), "panel:email-message_list", entity="email-message"),
            ]),
            tree(_("Contacto"), children=[
                link(_("Mensajes de contacto"), "panel:contact-message_list", entity="contact-message"),
                link(_("Respuestas de contacto"), "panel:contact-reply_list", entity="contact-reply"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de correo"), "panel:email-log_list", entity="email-log"),
            ]),
        ]),
        tree(_("Colecciones"), icon="bi-collection", url="panel:collections-home", entity="collections-home", children=[
            tree(_("Colecciones"), children=[
                link(_("Colecciones de series"), "panel:serie-collection_list", entity="serie-collection"),
                link(_("Colecciones de películas"), "panel:movie-collection_list", entity="movie-collection"),
                link(_("Colecciones de anime"), "panel:anime-collection_list", entity="anime-collection"),
                link(_("Colecciones de manga"), "panel:manga-collection_list", entity="manga-collection"),
                link(_("Colecciones de juegos"), "panel:game-collection_list", entity="game-collection"),
                link(_("Colecciones de álbumes"), "panel:album-collection_list", entity="album-collection"),
                link(_("Colecciones de artistas"), "panel:artist-collection_list", entity="artist-collection"),
                link(_("Colecciones de canciones"), "panel:song-collection_list", entity="song-collection"),
                link(_("Colecciones de personajes"), "panel:character-collection_list", entity="character-collection"),
                link(_("Colecciones de personas"), "panel:person-collection_list", entity="person-collection"),
                link(_("Colecciones de compañías"), "panel:company-collection_list", entity="company-collection"),
                link(_("Colecciones de personajes de juego"), "panel:game-character-collection_list", entity="game-character-collection"),
            ]),
            tree(_("Estados"), children=[
            ]),
            tree(_("Registro"), children=[
                link(_("Log de colecciones"), "panel:collection-log_list", entity="collection-log"),
            ]),
        ]),
        tree(_("Personas"), icon="bi-person", url="panel:people-home", entity="people-home", children=[
            tree(_("Personas"), children=[
                link(_("Personas"), "panel:person_list", entity="person"),
                link(_("Apodos"), "panel:person-nickname_list", entity="person-nickname"),
                link(_("Enlaces"), "panel:person-link_list", entity="person-link"),
                link(_("Imágenes"), "panel:person-image_list", entity="person-image"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de personas"), "panel:people-log_list", entity="people-log"),
            ]),
        ]),
        tree(_("Compañías"), icon="bi-building", url="panel:companies-home", entity="companies-home", children=[
            tree(_("Compañías"), children=[
                link(_("Compañías"), "panel:company_list", entity="company"),
                link(_("Imágenes"), "panel:company-image_list", entity="company-image"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de compañías"), "panel:company-log_list", entity="company-log"),
            ]),
        ]),
        tree(_("Páginas"), icon="bi-file-text", url="panel:pages-home", entity="pages-home", children=[
            tree(_("Páginas"), children=[
                link(_("Secciones de nosotros"), "panel:about-section_list", entity="about-section"),
                link(_("Secciones de términos"), "panel:terms-section_list", entity="terms-section"),
                link(_("Secciones de privacidad"), "panel:privacy-section_list", entity="privacy-section"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de páginas"), "panel:pages-log_list", entity="pages-log"),
            ]),
        ]),
        tree(_("Catálogos"), icon="bi-database", url="panel:catalogs-home", entity="catalogs-home", children=[
            tree(_("Localización"), children=[
                link(_("Países"), "panel:country_list", entity="country"),
                link(_("Idiomas"), "panel:language_list", entity="language"),
            ]),
            tree(_("Referencias"), children=[
                link(_("Formatos"), "panel:format_list", entity="format"),
                link(_("Calidades"), "panel:quality_list", entity="quality"),
                link(_("Sitios web"), "panel:website_list", entity="website"),
                link(_("Fuentes externas"), "panel:external-source_list", entity="external-source"),
            ]),
            tree(_("Tipos"), children=[
                link(_("Tipos de relación"), "panel:relation-type_list", entity="relation-type"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de catálogos"), "panel:catalogs-log_list", entity="catalogs-log"),
            ]),
        ]),
        tree(_("Música"), icon="bi-music-note-beamed", url="panel:music-home", entity="music-home", children=[
            tree(_("Artistas"), children=[
                link(_("Artistas"), "panel:artist_list", entity="artist"),
                link(_("Imágenes"), "panel:artist-image_list", entity="artist-image"),
            ]),
            tree(_("Álbumes"), children=[
                link(_("Álbumes"), "panel:album_list", entity="album"),
                link(_("Canciones"), "panel:song_list", entity="song"),
                link(_("Traducciones de canción"), "panel:song-translation_list", entity="song-translation"),
                link(_("Compositores de canción"), "panel:song-composer_list", entity="song-composer"),
                link(_("Imágenes"), "panel:album-image_list", entity="album-image"),
            ]),
            tree(_("Tipos y géneros"), children=[
                link(_("Géneros"), "panel:music-genre_list", entity="music-genre"),
                link(_("Alias de géneros"), "panel:music-genre-alias_list", entity="music-genre-alias"),
                link(_("Tipos de álbum"), "panel:music-album-type_list", entity="music-album-type"),
                link(_("Tipos de artista"), "panel:music-artist-type_list", entity="music-artist-type"),
            ]),
            tree(_("Roles y miembros"), children=[
                link(_("Roles"), "panel:music-role_list", entity="music-role"),
                link(_("Miembros"), "panel:artist-member_list", entity="artist-member"),
            ]),
            tree(_("Importación · Deezer"), children=[
                link(_("Importar géneros"), "panel:deezer-genres", entity="deezer-genres"),
                link(_("Importar artista"), "panel:deezer-artist", entity="deezer-artist"),
                link(_("Importar álbum"), "panel:deezer-album", entity="deezer-album"),
                link(_("Importar canción"), "panel:deezer-song", entity="deezer-song"),
            ]),
            tree(_("Datos crudos · Deezer"), children=[
                link(_("Datos · Artista (Deezer)"), "panel:data-deezer-artist_list", entity="data-deezer-artist"),
                link(_("Datos · Álbum (Deezer)"), "panel:data-deezer-album_list", entity="data-deezer-album"),
                link(_("Datos · Pistas del álbum (Deezer)"), "panel:data-deezer-track_list", entity="data-deezer-track"),
                link(_("Datos · Género (Deezer)"), "panel:data-deezer-genre_list", entity="data-deezer-genre"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de música"), "panel:music-log_list", entity="music-log"),
            ]),
        ]),
        tree(_("Juegos"), icon="bi-controller", url="panel:games-home", entity="games-home", children=[
            tree(_("Catálogo"), children=[
                link(_("Juegos"), "panel:game_list", entity="game"),
                link(_("Títulos"), "panel:game-title_list", entity="game-title"),
                link(_("Lanzamientos de juego"), "panel:game-release_list", entity="game-release"),
                link(_("Imágenes de lanzamiento"), "panel:game-release-image_list", entity="game-release-image"),
                link(_("Imágenes"), "panel:game-image_list", entity="game-image"),
                link(_("Enlaces"), "panel:game-link_list", entity="game-link"),
            ]),
            tree(_("Personajes"), children=[
                link(_("Personajes de juego"), "panel:game-character_list", entity="game-character"),
                link(_("Roles de personaje"), "panel:game-character-role_list", entity="game-character-role"),
                link(_("Imágenes de personaje de juego"), "panel:game-character-image_list", entity="game-character-image"),
            ]),
            tree(_("Creadores"), children=[
                link(_("Creadores"), "panel:creator_list", entity="creator"),
                link(_("Apodos"), "panel:creator-nickname_list", entity="creator-nickname"),
                link(_("Enlaces"), "panel:creator-link_list", entity="creator-link"),
            ]),
            tree(_("Taxonomías"), children=[
                link(_("Géneros"), "panel:game-genre_list", entity="game-genre"),
                link(_("Alias de géneros"), "panel:game-genre-alias_list", entity="game-genre-alias"),
                link(_("Etiquetas"), "panel:tag_list", entity="tag"),
                link(_("Alias de etiquetas"), "panel:tag-alias_list", entity="tag-alias"),
                link(_("Motores"), "panel:game-engine_list", entity="game-engine"),
                link(_("Plataformas"), "panel:game-platform_list", entity="game-platform"),
                link(_("Medios"), "panel:game-medium_list", entity="game-medium"),
            ]),
            tree(_("Importación · VNDB"), children=[
                link(_("Importar juego"), "panel:vndb-game", entity="vndb-game"),
                link(_("Importar creador"), "panel:vndb-creator", entity="vndb-creator"),
                link(_("Importar lanzamiento"), "panel:vndb-release", entity="vndb-release"),
                link(_("Importar personaje"), "panel:vndb-character", entity="vndb-character"),
                link(_("Cargar tags (dump)"), "panel:load-tags-vndb", entity="load-tags-vndb"),
            ]),
            tree(_("Datos crudos · VNDB"), children=[
                link(_("Datos · Juego (VNDB)"), "panel:data-vndb-game_list", entity="data-vndb-game"),
                link(_("Datos · Creador (VNDB)"), "panel:data-vndb-creator_list", entity="data-vndb-creator"),
                link(_("Datos · Lanzamiento (VNDB)"), "panel:data-vndb-release_list", entity="data-vndb-release"),
                link(_("Datos · Personaje (VNDB)"), "panel:data-vndb-character_list", entity="data-vndb-character"),
                link(_("Datos · Juego (F95)"), "panel:data-f95-game_list", entity="data-f95-game"),
                link(_("Datos · Creador (F95)"), "panel:data-f95-creator_list", entity="data-f95-creator"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de juegos"), "panel:game-log_list", entity="game-log"),
            ]),
        ]),
        tree(_("Películas"), icon="bi-film", url="panel:movies-home", entity="movies-home", children=[
            tree(_("Contenido"), children=[
                link(_("Películas"), "panel:movie_list", entity="movie"),
                link(_("Títulos alternativos"), "panel:movie-title_list", entity="movie-title"),
                link(_("Imágenes"), "panel:movie-image_list", entity="movie-image"),
            ]),
            tree(_("Reparto y equipo"), children=[
                link(_("Reparto"), "panel:movie-cast_list", entity="movie-cast"),
                link(_("Equipo"), "panel:movie-staff_list", entity="movie-staff"),
                link(_("Roles"), "panel:movie-role_list", entity="movie-role"),
            ]),
            tree(_("Taxonomías"), children=[
                link(_("Géneros"), "panel:movie-genre_list", entity="movie-genre"),
                link(_("Alias de géneros"), "panel:movie-genre-alias_list", entity="movie-genre-alias"),
                link(_("Tipos"), "panel:movie-type_list", entity="movie-type"),
                link(_("Clasificaciones"), "panel:movie-rating_list", entity="movie-rating"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de películas"), "panel:movie-log_list", entity="movie-log"),
            ]),
        ]),
        tree(_("Series"), icon="bi-collection-play", url="panel:series-home", entity="series-home", children=[
            tree(_("Contenido"), children=[
                link(_("Series"), "panel:serie_list", entity="serie"),
                link(_("Títulos alternativos"), "panel:serie-title_list", entity="serie-title"),
                link(_("Imágenes"), "panel:serie-image_list", entity="serie-image"),
            ]),
            tree(_("Reparto y equipo"), children=[
                link(_("Reparto"), "panel:serie-cast_list", entity="serie-cast"),
                link(_("Equipo"), "panel:serie-staff_list", entity="serie-staff"),
                link(_("Roles"), "panel:serie-role_list", entity="serie-role"),
            ]),
            tree(_("Taxonomías"), children=[
                link(_("Géneros"), "panel:serie-genre_list", entity="serie-genre"),
                link(_("Alias de géneros"), "panel:serie-genre-alias_list", entity="serie-genre-alias"),
                link(_("Tipos"), "panel:serie-type_list", entity="serie-type"),
                link(_("Clasificaciones"), "panel:serie-rating_list", entity="serie-rating"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de series"), "panel:serie-log_list", entity="serie-log"),
            ]),
        ]),
        tree(_("Otaku"), icon="bi-stars", url="panel:otaku-home", entity="otaku-home", children=[
            tree(_("Anime"), children=[
                link(_("Animes"), "panel:anime_list", entity="anime"),
                link(_("Canciones de anime"), "panel:anime-song_list", entity="anime-song"),
                link(_("Personajes de anime"), "panel:anime-character_list", entity="anime-character"),
                link(_("Staff de anime"), "panel:anime-staff_list", entity="anime-staff"),
                link(_("Títulos"), "panel:anime-title_list", entity="anime-title"),
                link(_("Imágenes"), "panel:anime-image_list", entity="anime-image"),
            ]),
            tree(_("Manga"), children=[
                link(_("Mangas"), "panel:manga_list", entity="manga"),
                link(_("Autores de manga"), "panel:manga-author_list", entity="manga-author"),
                link(_("Personajes de manga"), "panel:manga-character_list", entity="manga-character"),
                link(_("Títulos"), "panel:manga-title_list", entity="manga-title"),
                link(_("Imágenes"), "panel:manga-image_list", entity="manga-image"),
            ]),
            tree(_("Personajes"), children=[
                link(_("Personajes"), "panel:character_list", entity="character"),
                link(_("Roles"), "panel:otaku-role_list", entity="otaku-role"),
                link(_("Voces de personaje"), "panel:character-voice_list", entity="character-voice"),
                link(_("Apodos"), "panel:character-nickname_list", entity="character-nickname"),
                link(_("Imágenes"), "panel:character-image_list", entity="character-image"),
            ]),
            tree(_("Personas (MAL)"), children=[
                link(_("Personas (MAL)"), "panel:person-mal_list", entity="person-mal"),
                link(_("Imágenes"), "panel:person-image-mal_list", entity="person-image-mal"),
            ]),
            tree(_("Compañías (MAL)"), children=[
                link(_("Compañías (MAL)"), "panel:company-mal_list", entity="company-mal"),
                link(_("Imágenes"), "panel:company-image-mal_list", entity="company-image-mal"),
            ]),
            tree(_("Taxonomías"), children=[
                link(_("Géneros"), "panel:genre_list", entity="genre"),
                link(_("Alias de géneros"), "panel:genre-alias_list", entity="genre-alias"),
                link(_("Tipos"), "panel:type_list", entity="type"),
                link(_("Estados"), "panel:status_list", entity="status"),
                link(_("Fuentes"), "panel:source_list", entity="source"),
                link(_("Temas"), "panel:theme_list", entity="theme"),
                link(_("Alias de temas"), "panel:theme-alias_list", entity="theme-alias"),
                link(_("Demografías"), "panel:demographic_list", entity="demographic"),
                link(_("Alias de demografías"), "panel:demographic-alias_list", entity="demographic-alias"),
                link(_("Años"), "panel:year_list", entity="year"),
            ]),
            tree(_("Relaciones"), children=[
                link(_("Relaciones"), "panel:relation_list", entity="relation"),
                link(_("Relaciones anime → anime"), "panel:relation-anime-anime_list", entity="relation-anime-anime"),
                link(_("Relaciones manga → anime"), "panel:relation-manga-anime_list", entity="relation-manga-anime"),
                link(_("Relaciones manga → manga"), "panel:relation-manga-manga_list", entity="relation-manga-manga"),
            ]),
            tree(_("Importación · AniList"), children=[
                link(_("Importar anime"), "panel:anilist-anime", entity="anilist-anime"),
                link(_("Importar manga"), "panel:anilist-manga", entity="anilist-manga"),
                link(_("Importar personaje"), "panel:anilist-character", entity="anilist-character"),
                link(_("Importar persona"), "panel:anilist-person", entity="anilist-person"),
            ]),
            tree(_("Datos crudos · AniList"), children=[
                link(_("Datos · Anime (AniList)"), "panel:data-anilist-anime_list", entity="data-anilist-anime"),
                link(_("Datos · Personaje (AniList)"), "panel:data-anilist-character_list", entity="data-anilist-character"),
                link(_("Datos · Manga (AniList)"), "panel:data-anilist-manga_list", entity="data-anilist-manga"),
                link(_("Datos · Persona (AniList)"), "panel:data-anilist-person_list", entity="data-anilist-person"),
            ]),
            tree(_("Datos crudos · MAL"), children=[
                link(_("Datos · Anime (MAL)"), "panel:data-mal-anime_list", entity="data-mal-anime"),
                link(_("Datos · Anime · personajes (MAL)"), "panel:data-mal-anime-character_list", entity="data-mal-anime-character"),
                link(_("Datos · Anime · staff (MAL)"), "panel:data-mal-anime-staff_list", entity="data-mal-anime-staff"),
                link(_("Datos · Anime · imágenes (MAL)"), "panel:data-mal-anime-picture_list", entity="data-mal-anime-picture"),
                link(_("Datos · Manga (MAL)"), "panel:data-mal-manga_list", entity="data-mal-manga"),
                link(_("Datos · Manga · personajes (MAL)"), "panel:data-mal-manga-character_list", entity="data-mal-manga-character"),
                link(_("Datos · Manga · imágenes (MAL)"), "panel:data-mal-manga-picture_list", entity="data-mal-manga-picture"),
                link(_("Datos · Personaje (MAL)"), "panel:data-mal-character_list", entity="data-mal-character"),
                link(_("Datos · Personaje · imágenes (MAL)"), "panel:data-mal-character-picture_list", entity="data-mal-character-picture"),
                link(_("Datos · Persona (MAL)"), "panel:data-mal-person_list", entity="data-mal-person"),
                link(_("Datos · Persona · imágenes (MAL)"), "panel:data-mal-person-picture_list", entity="data-mal-person-picture"),
            ]),
            tree(_("Registro"), children=[
                link(_("Log de otaku"), "panel:otaku-log_list", entity="otaku-log"),
            ]),
        ]),
    ],
)
register_sidebar(GESTION)
