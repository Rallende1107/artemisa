"""games · lanzadores de importación desde VNDB (gestión).

UNA vista por tabla Data (`LoadVNDBDataF95GameView` llena `DataVndbGame`), con un ARREGLO de formularios que la
página recorre: por nombre, por id y por páginas. Cada vista se declara como un alta — dos bases y todo directo:

    class LoadVNDBDataF95GameView(BaseDataVndbGame, _BaseImportVndb, BaseImport):
        forms = (forms.DataVndbGameSearchForm, forms.DataVndbGameImportForm, forms.DataVndbGamePagesForm)
        title = _("Importar juegos")

  · `BaseDataVndbGame` — la _Entidad de la tabla que se llena: modelo, entidad, sección del panel y page_template.
  · `_BaseImportVndb`  — lo común de la fuente VNDB: de dónde viene, «Cancelar» y las tareas de lote (aquí abajo).
  · `BaseImport`       — la vista genérica (core/shared/views/base.py): valida el formulario que llegó, decide si
                         va a Celery o corre en la petición, avisa y redirige.

Quitar una forma de importar es quitar su formulario del arreglo. Cada FORMULARIO lleva lo suyo (su tipo, su
título, su botón, a dónde lleva y qué tarea lanza), así que un cambio en «por páginas» de personajes no toca a
juegos. Las de búsqueda («…SearchView») son la página de resultados: `BaseImportSearch`.
"""
from pathlib import Path

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.games import forms, tasks
from apps.games.models import GameLog
from apps.games.services import vndb, vndb_dump, vndb_tags
from apps.games.views.base import BaseDataVndbCharacter, BaseDataVndbCreator, BaseDataVndbGame, BaseDataVndbRelease
from core.shared.models.choices import LogLevel
from core.shared.views.base import BaseImport, BaseImportSearch, BaseLoadFileView, BaseLoadSummaryView
from core.shared.views.export import BaseExportDumpView
from core.shared.views.imports import ProcesarPendientesView
from core.utils.importlog import log_to


# Ayuda de las páginas de RESULTADOS: la misma en las cuatro, pero cada vista la declara (`ayuda = TEXTO_AYUDA`),
# así una puede poner la suya o quedarse sin ayuda sin tocar a las demás.
TEXTO_AYUDA = _("Marca los que quieras traer: se descargan al crudo y se procesan luego desde la lista de datos.")


class _BaseImportVndb:
    source_key, source_label = "vndb", "VNDB"
    task_rango = tasks.import_vndb_range_task
    task_barrido = tasks.barrer_vndb_task
    task_ids = tasks.import_vndb_ids_task


class LoadVNDBDataF95GameView(BaseDataVndbGame, _BaseImportVndb, BaseImport):
    forms = (forms.DataVndbGameSearchForm, forms.DataVndbGameImportForm, forms.DataVndbGamePagesForm)
    title = _("Importar juegos")
    label = _("Juego")
    active_entity = "vndb-game"


class LoadVNDBDataCreatorView(BaseDataVndbCreator, _BaseImportVndb, BaseImport):
    forms = (forms.DataVndbCreatorSearchForm, forms.DataVndbCreatorImportForm, forms.DataVndbCreatorPagesForm)
    title = _("Importar creadores")
    label = _("Creador")
    ayuda = _("Un productor de VNDB (p<id>): nombre, descripción, idioma y tipo. Sus juegos se traen aparte, por id o por páginas.")
    active_entity = "vndb-creator"


class LoadVNDBDataReleaseView(BaseDataVndbRelease, _BaseImportVndb, BaseImport):
    forms = (forms.DataVndbReleaseSearchForm, forms.DataVndbReleaseImportForm, forms.DataVndbReleasePagesForm)
    title = _("Importar lanzamientos")
    label = _("Lanzamiento")
    ayuda = _("Un lanzamiento de VNDB (r<id>): edición, idiomas, plataformas y editoras. No vive sin su juego: si el juego falta, se trae entero.")
    active_entity = "vndb-release"


class LoadVNDBDataCharacterView(BaseDataVndbCharacter, _BaseImportVndb, BaseImport):
    forms = (forms.DataVndbCharacterSearchForm, forms.DataVndbCharacterImportForm, forms.DataVndbCharacterPagesForm)
    title = _("Importar personajes")
    label = _("Personaje")
    ayuda = _("Un personaje de VNDB (c<id>) con su imagen y su rol en cada juego. No vive sin su juego: los que falten se traen enteros.")
    active_entity = "vndb-character"


class LoadVNDBDataF95GameSearchView(BaseDataVndbGame, _BaseImportVndb, BaseImportSearch):
    """Resultados de buscar juegos por título; los marcados se importan al crudo."""
    search_form = forms.DataVndbGameSearchForm
    buscador = staticmethod(vndb.buscar_juegos)
    back_url = "panel:vndb-game"
    ayuda = TEXTO_AYUDA
    title = _("Buscar juegos en VNDB")
    label = _("Juego")
    active_entity = "vndb-game"


class LoadVNDBDataCreatorSearchView(BaseDataVndbCreator, _BaseImportVndb, BaseImportSearch):
    """Resultados de buscar creadores por nombre; los marcados se importan al crudo."""
    search_form = forms.DataVndbCreatorSearchForm
    buscador = staticmethod(vndb.buscar_creadores)
    back_url = "panel:vndb-creator"
    ayuda = TEXTO_AYUDA
    title = _("Buscar creadores en VNDB")
    label = _("Creador")
    active_entity = "vndb-creator"


class LoadVNDBDataReleaseSearchView(BaseDataVndbRelease, _BaseImportVndb, BaseImportSearch):
    """Resultados de buscar lanzamientos por título; los marcados se importan al crudo."""
    search_form = forms.DataVndbReleaseSearchForm
    buscador = staticmethod(vndb.buscar_lanzamientos)
    back_url = "panel:vndb-release"
    ayuda = TEXTO_AYUDA
    title = _("Buscar lanzamientos en VNDB")
    label = _("Lanzamiento")
    active_entity = "vndb-release"


class LoadVNDBDataCharacterSearchView(BaseDataVndbCharacter, _BaseImportVndb, BaseImportSearch):
    """Resultados de buscar personajes por nombre; los marcados se importan al crudo."""
    search_form = forms.DataVndbCharacterSearchForm
    buscador = staticmethod(vndb.buscar_personajes)
    back_url = "panel:vndb-character"
    ayuda = TEXTO_AYUDA
    title = _("Buscar personajes en VNDB")
    label = _("Personaje")
    active_entity = "vndb-character"


class VNDBProcessPendingView(ProcesarPendientesView):
    """POST «Procesar pendientes» de VNDB (desde las listas de datos crudos)."""
    process_task = tasks.process_games_pending_task
    home_url = "panel:games-home"


class VNDBTagsLoadView(BaseLoadFileView):
    """Paso 1 de «Cargar tags de VNDB»: el formulario (subir el .json(.gz), descargarlo o releer el último) →
    deja la ruta en sesión y manda al resumen. El dump queda en dump/."""
    form_class = forms.VNDBTagsDumpForm
    template_name = "games/vndb_tags.html"
    title = _("Cargar tags de VNDB")
    active_entity = "load-tags-vndb"
    background_image = "bg-games-load-tags-vndb"   # página FIJA: bg-<app>-<slug>, como bg-pages-about
    section_url = "panel:games-home"
    section_label = _("Juegos")
    cancel_url = "panel:games-home"                # esta pantalla llena géneros Y etiquetas: vuelve a la home
    success_url = "panel:load-tags-vndb-summary"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"ultimo": vndb_tags.ultimo_dump(), "url_dump": vndb_tags.URL_DUMP})
        return ctx

    def procesar(self, form):
        return form.ruta_dump()


class VNDBTagsSummaryView(BaseLoadSummaryView):
    """Paso 2: el resumen (N en el dump, X se crean, Y cambian, Z iguales, W desaparecen) y «Sí, continuar», que
    aplica por vndb_id: cont y ero a géneros (ero explícito), tech a etiquetas; lo que ya no viene queda inactivo."""
    template_name = "games/vndb_tags_summary.html"
    title = _("Cargar tags de VNDB · resumen")
    active_entity = "load-tags-vndb"               # la misma que el formulario: es la clave de sesión
    background_image = "bg-games-load-tags-vndb"
    section_url = "panel:games-home"
    section_label = _("Juegos")
    load_url = "panel:load-tags-vndb"              # la miga, y a dónde volver si el dump ya no está
    cancel_url = "panel:load-tags-vndb"            # «No, cancelar»: se sale sin aplicar, de vuelta al formulario
    success_url = "panel:game-genre_list"          # tras aplicar

    def resumen(self, ruta):
        return vndb_tags.resumen(vndb_tags.leer(ruta))

    def aplicar(self, ruta):
        hecho = vndb_tags.aplicar(vndb_tags.leer(ruta))
        log_to(GameLog, LogLevel.INFO, "vndb tags", f"{ruta.name}: {hecho['creados']} creados, {hecho['actualizados']} actualizados, {hecho['desactivados']} desactivados")
        messages.success(self.request, _("Tags de VNDB aplicados: %(c)s creados, %(a)s actualizados, %(d)s desactivados (de %(t)s en el dump).")
                         % {"c": hecho["creados"], "a": hecho["actualizados"], "d": hecho["desactivados"], "t": hecho["total"]})


# ==============================================================================
# Gestión · Dumps de VNDB (archivo → tabla Data, sin procesar)
# ==============================================================================
# Dos vistas por tipo, como los tags: el FORMULARIO deja la ruta en sesión y el RESUMEN aplica. El dump lo
# genera nuestro propio exportador desde la tabla, así que cargar y exportar hablan el mismo formato.

class VndbDumpLoadView(BaseLoadFileView):
    """Paso 1 de «cargar un dump de VNDB»: el formulario → deja la ruta en sesión y manda al resumen."""
    template_name = "games/vndb_dump.html"
    page_template = "panel/base.html"
    section_url = "panel:games-home"
    section_label = _("Juegos")
    cancel_url = "panel:games-home"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ultimo"] = vndb_dump.ultimo_dump(self.form_class.TIPO)   # «Releer el último», si hay alguno en dump/
        return ctx

    def procesar(self, form):
        return form.ruta_dump()


class VndbDumpSummaryView(BaseLoadSummaryView):
    """Paso 2: el resumen de lo que va a entrar y «Sí, continuar», que guarda el crudo en su tabla."""
    template_name = "games/vndb_dump_summary.html"
    page_template = "panel/base.html"
    section_url = "panel:games-home"
    section_label = _("Juegos")
    TIPO = ""

    def resumen(self, ruta):
        return vndb_dump.resumen(self.TIPO, vndb_dump.leer(ruta))

    def aplicar(self, ruta):
        hecho = vndb_dump.aplicar(self.TIPO, vndb_dump.leer(ruta), ruta=ruta)
        log_to(GameLog, LogLevel.INFO, f"dump vndb {self.TIPO}",
               f"{Path(ruta).name}: {hecho['fichas']} fichas, {hecho['descartados']} sin id")
        messages.success(self.request, _("Dump cargado: %(f)s fichas (de %(t)s en el archivo; %(d)s sin id). "
                                         "Nada se ha procesado todavía.")
                         % {"f": hecho["fichas"], "t": hecho["total"], "d": hecho["descartados"]})


class VndbGameLoadView(BaseDataVndbGame, VndbDumpLoadView):
    background_image = "bg-games-load-dump-game"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.VndbGameDumpForm
    title = _("Cargar dump de juegos (VNDB)")
    active_entity = "dump-vndb-game"          # la misma en las dos vistas: es la clave de sesión
    success_url = "panel:dump-vndb-game-summary"
    ayuda = _("Guarda el crudo en datos · Juego (VNDB). No procesa nada.")


class VndbGameSummaryView(BaseDataVndbGame, VndbDumpSummaryView):
    background_image = "bg-games-load-dump-game"      # fondo PROPIO de la carga (no el de la lista de datos)
    TIPO = "game"
    title = _("Cargar dump de juegos (VNDB) · resumen")
    active_entity = "dump-vndb-game"
    load_url = "panel:dump-vndb-game"
    cancel_url = "panel:dump-vndb-game"
    success_url = "panel:data-vndb-game_list"


class VndbCreatorLoadView(BaseDataVndbCreator, VndbDumpLoadView):
    background_image = "bg-games-load-dump-creator"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.VndbCreatorDumpForm
    title = _("Cargar dump de creadores (VNDB)")
    active_entity = "dump-vndb-creator"
    success_url = "panel:dump-vndb-creator-summary"
    ayuda = _("Guarda el crudo en datos · Creador (VNDB). No procesa nada.")


class VndbCreatorSummaryView(BaseDataVndbCreator, VndbDumpSummaryView):
    background_image = "bg-games-load-dump-creator"      # fondo PROPIO de la carga (no el de la lista de datos)
    TIPO = "creator"
    title = _("Cargar dump de creadores (VNDB) · resumen")
    active_entity = "dump-vndb-creator"
    load_url = "panel:dump-vndb-creator"
    cancel_url = "panel:dump-vndb-creator"
    success_url = "panel:data-vndb-creator_list"


class VndbReleaseLoadView(BaseDataVndbRelease, VndbDumpLoadView):
    background_image = "bg-games-load-dump-release"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.VndbReleaseDumpForm
    title = _("Cargar dump de lanzamientos (VNDB)")
    active_entity = "dump-vndb-release"
    success_url = "panel:dump-vndb-release-summary"
    ayuda = _("Guarda el crudo en datos · Lanzamiento (VNDB). No procesa nada.")


class VndbReleaseSummaryView(BaseDataVndbRelease, VndbDumpSummaryView):
    background_image = "bg-games-load-dump-release"      # fondo PROPIO de la carga (no el de la lista de datos)
    TIPO = "release"
    title = _("Cargar dump de lanzamientos (VNDB) · resumen")
    active_entity = "dump-vndb-release"
    load_url = "panel:dump-vndb-release"
    cancel_url = "panel:dump-vndb-release"
    success_url = "panel:data-vndb-release_list"


class VndbCharacterLoadView(BaseDataVndbCharacter, VndbDumpLoadView):
    background_image = "bg-games-load-dump-character"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.VndbCharacterDumpForm
    title = _("Cargar dump de personajes (VNDB)")
    active_entity = "dump-vndb-character"
    success_url = "panel:dump-vndb-character-summary"
    ayuda = _("Guarda el crudo en datos · Personaje (VNDB). No procesa nada.")


class VndbCharacterSummaryView(BaseDataVndbCharacter, VndbDumpSummaryView):
    background_image = "bg-games-load-dump-character"      # fondo PROPIO de la carga (no el de la lista de datos)
    TIPO = "character"
    title = _("Cargar dump de personajes (VNDB) · resumen")
    active_entity = "dump-vndb-character"
    load_url = "panel:dump-vndb-character"
    cancel_url = "panel:dump-vndb-character"
    success_url = "panel:data-vndb-character_list"


# ==============================================================================
# Gestión · Generar dump (tabla Data → .json.gz). Vuelve a entrar por su LoadView.
# ==============================================================================
# El prefijo es el MISMO que busca su cargador, así «Releer el último» también lo encuentra en dump/.


class ProcessVndbGameView(BaseDataVndbGame, BaseImport):
    """Procesar datos de juego de VNDB: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataVndbGameProcessForm,)
    source_key = "vndb"
    source_label = "VNDB"
    task_procesar = tasks.process_vndb_task
    title = _("Procesar juegos (VNDB)")
    ayuda = _("Convierte los datos crudos en fichas reales, en local y sin peticiones. Las imágenes quedan pendientes "
              "para su propia tarea.")
    active_entity = "process-vndb-game"

class DataVndbGameExportView(BaseDataVndbGame, BaseExportDumpView):
    prefijo = "vndb-game"


class ProcessVndbCreatorView(BaseDataVndbCreator, BaseImport):
    """Procesar datos de creador de VNDB: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataVndbCreatorProcessForm,)
    source_key = "vndb"
    source_label = "VNDB"
    task_procesar = tasks.process_vndb_task
    title = _("Procesar creadores (VNDB)")
    ayuda = _("Convierte los datos crudos en fichas reales, en local y sin peticiones. Las imágenes quedan pendientes "
              "para su propia tarea.")
    active_entity = "process-vndb-creator"

class DataVndbCreatorExportView(BaseDataVndbCreator, BaseExportDumpView):
    prefijo = "vndb-creator"


class ProcessVndbReleaseView(BaseDataVndbRelease, BaseImport):
    """Procesar datos de lanzamiento de VNDB: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataVndbReleaseProcessForm,)
    source_key = "vndb"
    source_label = "VNDB"
    task_procesar = tasks.process_vndb_task
    title = _("Procesar lanzamientos (VNDB)")
    ayuda = _("Convierte los datos crudos en fichas reales, en local y sin peticiones. Lanzamientos y personajes: solo los de juegos que ya existen. Las imágenes quedan pendientes "
              "para su propia tarea.")
    active_entity = "process-vndb-release"

class DataVndbReleaseExportView(BaseDataVndbRelease, BaseExportDumpView):
    prefijo = "vndb-release"


class ProcessVndbCharacterView(BaseDataVndbCharacter, BaseImport):
    """Procesar datos de personaje de VNDB: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataVndbCharacterProcessForm,)
    source_key = "vndb"
    source_label = "VNDB"
    task_procesar = tasks.process_vndb_task
    title = _("Procesar personajes (VNDB)")
    ayuda = _("Convierte los datos crudos en fichas reales, en local y sin peticiones. Lanzamientos y personajes: solo los de juegos que ya existen. Las imágenes quedan pendientes "
              "para su propia tarea.")
    active_entity = "process-vndb-character"

class DataVndbCharacterExportView(BaseDataVndbCharacter, BaseExportDumpView):
    prefijo = "vndb-character"
