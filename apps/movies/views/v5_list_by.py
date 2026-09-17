"""movies · listas «por» (ListBy) de los DOS lados, público y gestión: «Películas del género X», «Reparto de X»,
«Personas de Chile». El mapa `filter_config` (tipo → campo, título, fondo) vive en el mixin `_BaseXBy` de base.py y lo comparten
con las Data; aquí cada lista declara sus rutas, su miga y su fondo por defecto. Ruta: `…/por/<tipo>/<pk>/`."""
from apps.movies.views.base import BaseMovieCastContext, BaseMovieContext, BaseMovieImageContext, BaseMovieRelationContext, BaseMovieStaffContext, BaseMovieTitleContext
from core.shared.views.base import AdminListByView, PublicListByView


# ==============================================================================
# Público
# ==============================================================================


class MoviePublicListByView(BaseMovieContext, PublicListByView):
    """genero, productora, distribuidora, tipo, clasificacion, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "movies:movies-by-data"
    by_url = "movies:movies-by"
    full_list_url = "movies:movies-catalog"
    parent_urls = {"persona": "personas:person-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    section = "peliculas"
    icon = "bi-film"


class MovieCastPublicListByView(BaseMovieCastContext, PublicListByView):
    """pelicula, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "movies:cast-by-data"
    by_url = "movies:cast-by"
    parent_urls = {"pelicula": "movies:movie-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    section = "peliculas"
    icon = "bi-people"
    cards_default = False   # en tabla se lee mejor (persona · personaje · rol)


class MovieImagePublicListByView(BaseMovieImageContext, PublicListByView):
    """pelicula."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "movies:movie-images-by-data"
    by_url = "movies:movie-images-by"
    parent_urls = {"pelicula": "movies:movie-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    section = "peliculas"
    icon = "bi-images"


class MovieStaffPublicListByView(BaseMovieStaffContext, PublicListByView):
    """pelicula, persona."""
    keep_nav = True      # se llega desde el catálogo: la barra se queda, con su pastilla marcada
    data_url = "movies:crew-by-data"
    by_url = "movies:crew-by"
    parent_urls = {"pelicula": "movies:movie-detail"}   # ficha del padre (solo donde la hay)
    background_image = "bg-movies-movie"
    background_fallback = "bg-movies-home"
    section = "peliculas"
    icon = "bi-person-gear"
    cards_default = False   # en tabla se lee mejor (persona · personaje · rol)


# ==============================================================================
# Gestión
# ==============================================================================


class MovieListByView(BaseMovieContext, AdminListByView):
    """genero, productora, distribuidora, tipo, clasificacion, persona."""
    home_url = "panel:movies-home"
    data_url = "panel:movie_data-by"
    full_list_url = "panel:movie_list"
    create_url = "panel:movie_create"


class MovieCastListByView(BaseMovieCastContext, AdminListByView):
    """pelicula, persona."""
    home_url = "panel:movies-home"
    data_url = "panel:movie-cast_data-by"
    full_list_url = "panel:movie-cast_list"
    create_url = "panel:movie-cast_create"


class MovieImageListByView(BaseMovieImageContext, AdminListByView):
    """pelicula."""
    home_url = "panel:movies-home"
    data_url = "panel:movie-image_data-by"
    full_list_url = "panel:movie-image_list"
    create_url = "panel:movie-image_create"


class MovieRelationListByView(BaseMovieRelationContext, AdminListByView):
    """pelicula, tipo."""
    home_url = "panel:movies-home"
    data_url = "panel:movie-relation_data-by"
    full_list_url = "panel:movie-relation_list"
    create_url = "panel:movie-relation_create"


class MovieStaffListByView(BaseMovieStaffContext, AdminListByView):
    """pelicula, persona."""
    home_url = "panel:movies-home"
    data_url = "panel:movie-staff_data-by"
    full_list_url = "panel:movie-staff_list"
    create_url = "panel:movie-staff_create"


class MovieTitleListByView(BaseMovieTitleContext, AdminListByView):
    """pelicula."""
    home_url = "panel:movies-home"
    data_url = "panel:movie-title_data-by"
    full_list_url = "panel:movie-title_list"
    create_url = "panel:movie-title_create"
