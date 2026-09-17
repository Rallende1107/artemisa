"""music · lanzadores de importación desde Deezer (gestión).

UNA vista por tabla Data (`LoadDeezerDataArtistView` llena `DataDeezerArtist`), con un ARREGLO de formularios
que la página recorre. Cada vista se declara como un alta — dos bases y todo directo:

    class LoadDeezerDataArtistView(BaseDataDeezerArtist, _BaseImportDeezer, BaseImport):
        forms = (forms.DataDeezerArtistSearchForm, forms.DataDeezerArtistImportForm)
        title = _("Importar artistas")

Quitar una forma de importar es quitar su formulario del arreglo. Cada FORMULARIO lleva lo suyo (su tipo, su
título, su botón, a dónde lleva y qué tarea lanza). Las de búsqueda («…SearchView») son la página de resultados.
"""
from django.utils.translation import gettext_lazy as _

from apps.music import forms, tasks
from apps.music.services import deezer
from apps.music.views.base import BaseDataDeezerAlbum, BaseDataDeezerArtist, BaseDataDeezerTrack, BaseGenre
from core.shared.views.base import BaseImport, BaseImportSearch
from core.shared.views.imports import ProcesarPendientesView


# Ayuda de las páginas de RESULTADOS: la misma en todas, pero cada vista la declara (`ayuda = TEXTO_AYUDA`),
# así una puede poner la suya o quedarse sin ayuda sin tocar a las demás.
TEXTO_AYUDA = _("Marca los que quieras traer: se descargan al crudo y se procesan luego desde la lista de datos.")


class _BaseImportDeezer:
    source_key, source_label = "deezer", "Deezer"
    task_rango = tasks.import_deezer_range_task
    task_ids = tasks.import_deezer_ids_task


class LoadDeezerDataArtistView(BaseDataDeezerArtist, _BaseImportDeezer, BaseImport):
    forms = (forms.DataDeezerArtistSearchForm, forms.DataDeezerArtistImportForm)
    title = _("Importar artistas")
    label = _("Artista")
    ayuda = _("Trae el artista, TODOS sus álbumes (listado paginado completo) y las pistas de cada álbum.")
    active_entity = "deezer-artist"


class LoadDeezerDataArtistSearchView(BaseDataDeezerArtist, _BaseImportDeezer, BaseImportSearch):
    """Resultados de buscar artistas por nombre; los marcados se importan al crudo."""
    search_form = forms.DataDeezerArtistSearchForm
    buscador = staticmethod(deezer.buscar_artistas)
    back_url = "panel:deezer-artist"
    title = _("Buscar artistas en Deezer")
    label = _("Artista")
    ayuda = TEXTO_AYUDA
    active_entity = "deezer-artist"


class LoadDeezerDataAlbumView(BaseDataDeezerAlbum, _BaseImportDeezer, BaseImport):
    forms = (forms.DataDeezerAlbumSearchForm, forms.DataDeezerAlbumImportForm)
    title = _("Importar álbumes")
    label = _("Álbum")
    ayuda = _("Trae la ficha del álbum y todas sus pistas. Si su artista no estaba, se crea con su nombre; "
              "importándolo después como artista se completa (foto, biografía, géneros).")
    active_entity = "deezer-album"


class LoadDeezerDataAlbumSearchView(BaseDataDeezerAlbum, _BaseImportDeezer, BaseImportSearch):
    """Resultados de buscar álbumes por nombre; los marcados se importan."""
    search_form = forms.DataDeezerAlbumSearchForm
    buscador = staticmethod(deezer.buscar_albumes)
    back_url = "panel:deezer-album"
    title = _("Buscar álbumes en Deezer")
    label = _("Álbum")
    ayuda = TEXTO_AYUDA
    active_entity = "deezer-album"


class LoadDeezerDataTrackView(BaseDataDeezerTrack, _BaseImportDeezer, BaseImport):
    forms = (forms.DataDeezerTrackSearchForm, forms.DataDeezerTrackImportForm)
    title = _("Importar canciones")
    label = _("Canción")
    ayuda = _("Una canción vive dentro de su álbum: al importarla se trae el ÁLBUM entero, con su artista y "
              "todas sus pistas.")
    active_entity = "deezer-song"


class LoadDeezerDataTrackSearchView(BaseDataDeezerTrack, _BaseImportDeezer, BaseImportSearch):
    """Resultados de buscar canciones por nombre; cada marcada trae su álbum."""
    search_form = forms.DataDeezerTrackSearchForm
    buscador = staticmethod(deezer.buscar_canciones)
    back_url = "panel:deezer-song"
    title = _("Buscar canciones en Deezer")
    label = _("Canción")
    ayuda = _("Marca las canciones: se importa el álbum de cada una (dos del mismo álbum, una sola vez).")
    active_entity = "deezer-song"


class LoadDeezerGenreView(BaseGenre, _BaseImportDeezer, BaseImport):
    """Géneros: todos en una llamada (GET /genre) o por rango de ids. Deezer no tiene búsqueda de géneros."""
    forms = (forms.GenreDeezerImportAllForm, forms.GenreDeezerImportForm)
    title = _("Importar géneros")
    label = _("Géneros")
    ayuda = _("«Todos de una vez» trae los géneros que Deezer publica en GET /genre, con su imagen. «Por id» "
              "trae un rango; los ids que no son música (podcasts, moods…) no crean Género.")
    task_uno = tasks.import_all_genres_task
    active_entity = "deezer-genres"


class DeezerProcessPendingView(ProcesarPendientesView):
    """POST «Procesar pendientes» de Deezer (desde las listas de datos crudos)."""
    process_task = tasks.process_music_pending_task
    home_url = "panel:music-home"
