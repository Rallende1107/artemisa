"""otaku · importar (AniList), cargar dumps (MAL), generar dumps y procesar pendientes (gestión).

Una sección por entidad, en orden alfabético. Cada vista declara TODO lo suyo: la `Base<Entidad>` de su tabla y la
vista del framework (`BaseImport`, `BaseLoadFileView`, `BaseLoadSummaryView`, `BaseExportDumpView`), sin bases
intermedias. Cargar un dump son dos vistas, como los tags de VNDB: el FORMULARIO deja la ruta en sesión y el
RESUMEN aplica.
"""
from pathlib import Path

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.otaku import forms, tasks
from apps.otaku.models import OtakuLog
from apps.otaku.services import mal_companies, mal_dump_load
from apps.otaku.views.base import BaseCompanyImageMal, BaseCompanyMAL, BaseDataAnilistAnime, BaseDataAnilistCharacter, BaseDataAnilistManga, BaseDataAnilistPerson, BaseDataMalAnime, BaseDataMalCharacter, BaseDataMalManga, BaseDataMalPerson, BasePersonImageMal
from apps.system import tasks as system_tasks
from core.shared.models.choices import LogLevel
from core.shared.views.base import BaseImport, BaseLoadFileView, BaseLoadSummaryView
from core.shared.views.export import BaseExportDumpView
from core.shared.views.imports import ProcesarPendientesView
from core.utils.importlog import log_to


# ==============================================================================
# Gestión · Anime
# ==============================================================================

class LoadAnilistDataAnimeView(BaseDataAnilistAnime, BaseImport):
    """Importar anime desde AniList al crudo: por id, por rango de ids o por páginas."""
    forms = (forms.DataAnilistAnimeIdForm, forms.DataAnilistAnimeRangeForm, forms.DataAnilistAnimePagesForm)
    source_key = "anilist"
    source_label = "AniList"
    task_uno = tasks.import_anilist_id_task
    task_rango = tasks.import_anilist_range_task
    task_barrido = tasks.barrer_anilist_task
    task_ids = tasks.import_anilist_ids_task
    title = _("Importar anime (AniList)")
    label = _("Anime")
    ayuda = _("Descarga al crudo desde la API de AniList: por id, por rango de ids o por páginas. Procesar es otro paso.")
    active_entity = "anilist-anime"


class DataAnilistAnimeExportView(BaseDataAnilistAnime, BaseExportDumpView):
    prefijo = "anilist-anime"

class AnimeMALLoadView(BaseDataMalAnime, BaseLoadFileView):
    """Paso 1 de «cargar el dump de animes de MAL»: el formulario deja la ruta en sesión y manda al resumen."""
    template_name = "otaku/mal_dump.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-anime"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.AnimeMALDumpForm
    title = _("Cargar dump de animes (MAL)")
    active_entity = "dump-mal-anime"          # la misma en las dos vistas: es la clave de sesión
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    cancel_url = "panel:otaku-home"
    success_url = "panel:dump-mal-anime-summary"
    ayuda = _("Guarda el crudo en datos · Anime (con sus imágenes dentro del registro). No procesa nada.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ultimo"] = mal_dump_load.ultimo_dump("anime")   # «Releer el último», si hay alguno en dump/
        return ctx

    def procesar(self, form):
        return form.ruta_dump()


class AnimeMALSummaryView(BaseDataMalAnime, BaseLoadSummaryView):
    """Paso 2: el resumen de lo que va a entrar y «Sí, continuar», que guarda el crudo en sus dos tablas."""
    template_name = "otaku/mal_dump_summary.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-anime"
    TIPO = "anime"
    title = _("Cargar dump de animes (MAL) · resumen")
    active_entity = "dump-mal-anime"
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    load_url = "panel:dump-mal-anime"
    cancel_url = "panel:dump-mal-anime"
    success_url = "panel:data-mal-anime_list"

    def resumen(self, ruta):
        return mal_dump_load.resumen("anime", mal_dump_load.leer(ruta))

    def aplicar(self, ruta):
        hecho = mal_dump_load.aplicar("anime", mal_dump_load.leer(ruta), ruta=ruta)
        log_to(OtakuLog, LogLevel.INFO, "dump mal anime", f"{Path(ruta).name}: {hecho['fichas']} fichas, "
                                                      f"{hecho['imagenes']} con imágenes, {hecho['descartados']} sin id")
        messages.success(self.request, _("Dump cargado: %(f)s fichas, %(i)s con imágenes (de %(t)s registros; "
                                         "%(d)s sin id). Nada se ha procesado todavía.")
                         % {"f": hecho["fichas"], "i": hecho["imagenes"], "t": hecho["total"], "d": hecho["descartados"]})


class ProcessMalAnimeView(BaseDataMalAnime, BaseImport):
    """Procesar datos de anime de MAL: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataMalAnimeProcessForm,)
    source_key = "mal"
    source_label = "MAL"
    task_procesar = tasks.process_mal_task
    title = _("Procesar animes (MAL)")
    ayuda = _("Convierte los datos cargados del dump en fichas reales. Solo enlaza lo que ya existe; no descarga imágenes: "
              "quedan pendientes para su propia tarea.")
    active_entity = "process-mal-anime"

class DataMalAnimeExportView(BaseDataMalAnime, BaseExportDumpView):
    prefijo = "mal-anime"      # el MISMO que busca su cargador: «Releer el último» también lo encuentra en dump/


# ==============================================================================
# Gestión · Compañía (MAL)
# ==============================================================================

class CompanyMALLoadView(BaseCompanyMAL, BaseLoadFileView):
    """Paso 1 de «cargar el dump de compañías de MAL»: el formulario deja la ruta en sesión y manda al resumen."""
    template_name = "otaku/mal_dump.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-company"      # fondo PROPIO de la carga (no el de la lista)
    form_class = forms.CompanyMALDumpForm
    title = _("Cargar dump de compañías (MAL)")
    active_entity = "dump-mal-company"          # la misma en las dos vistas: es la clave de sesión
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    cancel_url = "panel:otaku-home"
    success_url = "panel:dump-mal-company-summary"
    ayuda = _("Crea las compañías con su MAL id, o le pone el MAL id a una que ya existía con ese nombre. "
              "No pasa por datos crudos: no hay nada que procesar después.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ultimo"] = mal_dump_load.ultimo_dump("company")   # «Releer el último», si hay alguno en dump/
        return ctx

    def procesar(self, form):
        return form.ruta_dump()


class CompanyMALSummaryView(BaseCompanyMAL, BaseLoadSummaryView):
    """Paso 2: no hay fichas ni imágenes, hay compañías que se crean o se enlazan."""
    template_name = "otaku/mal_companies_summary.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-company"
    TIPO = "company"
    title = _("Cargar dump de compañías (MAL) · resumen")
    active_entity = "dump-mal-company"
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    load_url = "panel:dump-mal-company"
    cancel_url = "panel:dump-mal-company"
    success_url = "panel:company-mal_list"

    def resumen(self, ruta):
        return mal_companies.resumen(mal_dump_load.leer(ruta))

    def aplicar(self, ruta):
        hecho = mal_companies.aplicar(mal_dump_load.leer(ruta))
        log_to(OtakuLog, LogLevel.INFO, "dump mal company",
               f"{Path(ruta).name}: {hecho['creadas']} creadas, {hecho['enlazadas']} enlazadas, "
               f"{hecho['ya_estaban']} actualizadas ({hecho['con_url_nueva']} con URL nueva), {hecho['logos']} logos pendientes, {hecho['sin_datos']} sin id o nombre")
        messages.success(self.request, _("Compañías cargadas: %(c)s nuevas, %(e)s enlazadas a una que ya existía y "
                                         "%(y)s actualizadas (de %(t)s en el archivo). %(l)s logos quedan pendientes de descarga.")
                         % {"c": hecho["creadas"], "e": hecho["enlazadas"], "y": hecho["ya_estaban"], "t": hecho["total"], "l": hecho["logos"]})


# ==============================================================================
# Gestión · Manga
# ==============================================================================

class LoadAnilistDataMangaView(BaseDataAnilistManga, BaseImport):
    """Importar manga desde AniList al crudo: por id, por rango de ids o por páginas."""
    forms = (forms.DataAnilistMangaIdForm, forms.DataAnilistMangaRangeForm, forms.DataAnilistMangaPagesForm)
    source_key = "anilist"
    source_label = "AniList"
    task_uno = tasks.import_anilist_id_task
    task_rango = tasks.import_anilist_range_task
    task_barrido = tasks.barrer_anilist_task
    task_ids = tasks.import_anilist_ids_task
    title = _("Importar manga (AniList)")
    label = _("Manga")
    ayuda = _("Descarga al crudo desde la API de AniList: por id, por rango de ids o por páginas. Procesar es otro paso.")
    active_entity = "anilist-manga"


class DataAnilistMangaExportView(BaseDataAnilistManga, BaseExportDumpView):
    prefijo = "anilist-manga"

class MangaMALLoadView(BaseDataMalManga, BaseLoadFileView):
    """Paso 1 de «cargar el dump de mangas de MAL»: el formulario deja la ruta en sesión y manda al resumen."""
    template_name = "otaku/mal_dump.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-manga"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.MangaMALDumpForm
    title = _("Cargar dump de mangas (MAL)")
    active_entity = "dump-mal-manga"          # la misma en las dos vistas: es la clave de sesión
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    cancel_url = "panel:otaku-home"
    success_url = "panel:dump-mal-manga-summary"
    ayuda = _("Guarda el crudo en datos · Manga (con sus imágenes dentro del registro). No procesa nada.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ultimo"] = mal_dump_load.ultimo_dump("manga")   # «Releer el último», si hay alguno en dump/
        return ctx

    def procesar(self, form):
        return form.ruta_dump()


class MangaMALSummaryView(BaseDataMalManga, BaseLoadSummaryView):
    """Paso 2: el resumen de lo que va a entrar y «Sí, continuar», que guarda el crudo en sus dos tablas."""
    template_name = "otaku/mal_dump_summary.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-manga"
    TIPO = "manga"
    title = _("Cargar dump de mangas (MAL) · resumen")
    active_entity = "dump-mal-manga"
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    load_url = "panel:dump-mal-manga"
    cancel_url = "panel:dump-mal-manga"
    success_url = "panel:data-mal-manga_list"

    def resumen(self, ruta):
        return mal_dump_load.resumen("manga", mal_dump_load.leer(ruta))

    def aplicar(self, ruta):
        hecho = mal_dump_load.aplicar("manga", mal_dump_load.leer(ruta), ruta=ruta)
        log_to(OtakuLog, LogLevel.INFO, "dump mal manga", f"{Path(ruta).name}: {hecho['fichas']} fichas, "
                                                      f"{hecho['imagenes']} con imágenes, {hecho['descartados']} sin id")
        messages.success(self.request, _("Dump cargado: %(f)s fichas, %(i)s con imágenes (de %(t)s registros; "
                                         "%(d)s sin id). Nada se ha procesado todavía.")
                         % {"f": hecho["fichas"], "i": hecho["imagenes"], "t": hecho["total"], "d": hecho["descartados"]})


class ProcessMalMangaView(BaseDataMalManga, BaseImport):
    """Procesar datos de manga de MAL: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataMalMangaProcessForm,)
    source_key = "mal"
    source_label = "MAL"
    task_procesar = tasks.process_mal_task
    title = _("Procesar mangas (MAL)")
    ayuda = _("Convierte los datos cargados del dump en fichas reales. Solo enlaza lo que ya existe; no descarga imágenes: "
              "quedan pendientes para su propia tarea.")
    active_entity = "process-mal-manga"

class DataMalMangaExportView(BaseDataMalManga, BaseExportDumpView):
    prefijo = "mal-manga"      # el MISMO que busca su cargador: «Releer el último» también lo encuentra en dump/


# ==============================================================================
# Gestión · Persona
# ==============================================================================

class LoadAnilistDataPersonView(BaseDataAnilistPerson, BaseImport):
    """Importar persona desde AniList al crudo: por id, por rango de ids o por páginas."""
    forms = (forms.DataAnilistPersonIdForm, forms.DataAnilistPersonRangeForm, forms.DataAnilistPersonPagesForm)
    source_key = "anilist"
    source_label = "AniList"
    task_uno = tasks.import_anilist_id_task
    task_rango = tasks.import_anilist_range_task
    task_barrido = tasks.barrer_anilist_task
    task_ids = tasks.import_anilist_ids_task
    title = _("Importar persona (AniList)")
    label = _("Persona")
    ayuda = _("Descarga al crudo desde la API de AniList: por id, por rango de ids o por páginas. Procesar es otro paso.")
    active_entity = "anilist-person"


class DataAnilistPersonExportView(BaseDataAnilistPerson, BaseExportDumpView):
    prefijo = "anilist-person"

class PersonMALLoadView(BaseDataMalPerson, BaseLoadFileView):
    """Paso 1 de «cargar el dump de personas de MAL»: el formulario deja la ruta en sesión y manda al resumen."""
    template_name = "otaku/mal_dump.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-person"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.PersonMALDumpForm
    title = _("Cargar dump de personas (MAL)")
    active_entity = "dump-mal-person"          # la misma en las dos vistas: es la clave de sesión
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    cancel_url = "panel:otaku-home"
    success_url = "panel:dump-mal-person-summary"
    ayuda = _("Guarda el crudo en datos · Persona (con sus imágenes dentro del registro). No procesa nada.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ultimo"] = mal_dump_load.ultimo_dump("person")   # «Releer el último», si hay alguno en dump/
        return ctx

    def procesar(self, form):
        return form.ruta_dump()


class PersonMALSummaryView(BaseDataMalPerson, BaseLoadSummaryView):
    """Paso 2: el resumen de lo que va a entrar y «Sí, continuar», que guarda el crudo en sus dos tablas."""
    template_name = "otaku/mal_dump_summary.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-person"
    TIPO = "person"
    title = _("Cargar dump de personas (MAL) · resumen")
    active_entity = "dump-mal-person"
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    load_url = "panel:dump-mal-person"
    cancel_url = "panel:dump-mal-person"
    success_url = "panel:data-mal-person_list"

    def resumen(self, ruta):
        return mal_dump_load.resumen("person", mal_dump_load.leer(ruta))

    def aplicar(self, ruta):
        hecho = mal_dump_load.aplicar("person", mal_dump_load.leer(ruta), ruta=ruta)
        log_to(OtakuLog, LogLevel.INFO, "dump mal person", f"{Path(ruta).name}: {hecho['fichas']} fichas, "
                                                      f"{hecho['imagenes']} con imágenes, {hecho['descartados']} sin id")
        messages.success(self.request, _("Dump cargado: %(f)s fichas, %(i)s con imágenes (de %(t)s registros; "
                                         "%(d)s sin id). Nada se ha procesado todavía.")
                         % {"f": hecho["fichas"], "i": hecho["imagenes"], "t": hecho["total"], "d": hecho["descartados"]})


class ProcessMalPersonView(BaseDataMalPerson, BaseImport):
    """Procesar datos de persona de MAL: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataMalPersonProcessForm,)
    source_key = "mal"
    source_label = "MAL"
    task_procesar = tasks.process_mal_task
    title = _("Procesar personas (MAL)")
    ayuda = _("Convierte los datos cargados del dump en fichas reales. Solo enlaza lo que ya existe; no descarga imágenes: "
              "quedan pendientes para su propia tarea.")
    active_entity = "process-mal-person"

class DataMalPersonExportView(BaseDataMalPerson, BaseExportDumpView):
    prefijo = "mal-people"      # el MISMO que busca su cargador: «Releer el último» también lo encuentra en dump/


# ==============================================================================
# Gestión · Personaje
# ==============================================================================

class LoadAnilistDataCharacterView(BaseDataAnilistCharacter, BaseImport):
    """Importar personaje desde AniList al crudo: por id, por rango de ids o por páginas."""
    forms = (forms.DataAnilistCharacterIdForm, forms.DataAnilistCharacterRangeForm, forms.DataAnilistCharacterPagesForm)
    source_key = "anilist"
    source_label = "AniList"
    task_uno = tasks.import_anilist_id_task
    task_rango = tasks.import_anilist_range_task
    task_barrido = tasks.barrer_anilist_task
    task_ids = tasks.import_anilist_ids_task
    title = _("Importar personaje (AniList)")
    label = _("Personaje")
    ayuda = _("Descarga al crudo desde la API de AniList: por id, por rango de ids o por páginas. Procesar es otro paso.")
    active_entity = "anilist-character"


class DataAnilistCharacterExportView(BaseDataAnilistCharacter, BaseExportDumpView):
    prefijo = "anilist-character"

class CharacterMALLoadView(BaseDataMalCharacter, BaseLoadFileView):
    """Paso 1 de «cargar el dump de personajes de MAL»: el formulario deja la ruta en sesión y manda al resumen."""
    template_name = "otaku/mal_dump.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-character"      # fondo PROPIO de la carga (no el de la lista de datos)
    form_class = forms.CharacterMALDumpForm
    title = _("Cargar dump de personajes (MAL)")
    active_entity = "dump-mal-character"          # la misma en las dos vistas: es la clave de sesión
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    cancel_url = "panel:otaku-home"
    success_url = "panel:dump-mal-character-summary"
    ayuda = _("Guarda el crudo en datos · Personaje (con sus imágenes dentro del registro). No procesa nada.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ultimo"] = mal_dump_load.ultimo_dump("character")   # «Releer el último», si hay alguno en dump/
        return ctx

    def procesar(self, form):
        return form.ruta_dump()


class CharacterMALSummaryView(BaseDataMalCharacter, BaseLoadSummaryView):
    """Paso 2: el resumen de lo que va a entrar y «Sí, continuar», que guarda el crudo en sus dos tablas."""
    template_name = "otaku/mal_dump_summary.html"
    page_template = "panel/base.html"
    background_image = "bg-otaku-load-dump-character"
    TIPO = "character"
    title = _("Cargar dump de personajes (MAL) · resumen")
    active_entity = "dump-mal-character"
    section_url = "panel:otaku-home"
    section_label = _("Otaku")
    load_url = "panel:dump-mal-character"
    cancel_url = "panel:dump-mal-character"
    success_url = "panel:data-mal-character_list"

    def resumen(self, ruta):
        return mal_dump_load.resumen("character", mal_dump_load.leer(ruta))

    def aplicar(self, ruta):
        hecho = mal_dump_load.aplicar("character", mal_dump_load.leer(ruta), ruta=ruta)
        log_to(OtakuLog, LogLevel.INFO, "dump mal character", f"{Path(ruta).name}: {hecho['fichas']} fichas, "
                                                      f"{hecho['imagenes']} con imágenes, {hecho['descartados']} sin id")
        messages.success(self.request, _("Dump cargado: %(f)s fichas, %(i)s con imágenes (de %(t)s registros; "
                                         "%(d)s sin id). Nada se ha procesado todavía.")
                         % {"f": hecho["fichas"], "i": hecho["imagenes"], "t": hecho["total"], "d": hecho["descartados"]})


class ProcessMalCharacterView(BaseDataMalCharacter, BaseImport):
    """Procesar datos de personaje de MAL: N pendientes o todos, en background, por lotes y cancelable."""
    forms = (forms.DataMalCharacterProcessForm,)
    source_key = "mal"
    source_label = "MAL"
    task_procesar = tasks.process_mal_task
    title = _("Procesar personajes (MAL)")
    ayuda = _("Convierte los datos cargados del dump en fichas reales. Solo enlaza lo que ya existe; no descarga imágenes: "
              "quedan pendientes para su propia tarea.")
    active_entity = "process-mal-character"

class DataMalCharacterExportView(BaseDataMalCharacter, BaseExportDumpView):
    prefijo = "mal-characters"      # el MISMO que busca su cargador: «Releer el último» también lo encuentra en dump/


# ==============================================================================
# Gestión · Procesar pendientes (MAL)
# ==============================================================================

class MALProcessPendingView(ProcesarPendientesView):
    """POST «Procesar pendientes» de MAL (desde las listas de datos crudos)."""
    process_task = tasks.process_otaku_pending_task
    home_url = "panel:otaku-home"


class CompanyImageMalDownloadView(BaseCompanyImageMal, BaseImport):
    """Descargar a disco las imágenes pendientes de compañías CON ficha MAL."""
    forms = (forms.CompanyImageMalDownloadForm, forms.CompanyImageMalRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de compañías (MAL)")
    ayuda = _("Solo las de compañías con ficha MAL. Un 404 da la URL por muerta al primer intento; un timeout o un error del "
              "servidor, al tercero. Los fallos quedan en el log de la app de la tabla.")
    active_entity = "company-image-mal"


class PersonImageMalDownloadView(BasePersonImageMal, BaseImport):
    """Descargar a disco las imágenes pendientes de personas CON ficha MAL."""
    forms = (forms.PersonImageMalDownloadForm, forms.PersonImageMalRetryForm)
    source_key = "imágenes"
    source_label = _("Imágenes")
    task_procesar = system_tasks.download_images_batch_task
    title = _("Descargar imágenes de personas (MAL)")
    ayuda = _("Solo las de personas con ficha MAL. Un 404 da la URL por muerta al primer intento; un timeout o un error del "
              "servidor, al tercero. Los fallos quedan en el log de la app de la tabla.")
    active_entity = "person-image-mal"

