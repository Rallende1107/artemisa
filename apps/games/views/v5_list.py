"""games · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from apps.games import tasks
from apps.games.views.base import BaseCharacter, BaseCharacterImage, BaseCharacterRole, BaseCreator, BaseCreatorLink, BaseCreatorNickname, BaseDataF95Creator, BaseDataF95Game, BaseDataVndbCharacter, BaseDataVndbCreator, BaseDataVndbGame, BaseDataVndbRelease, BaseDevelopmentEngine, BaseGame, BaseGameImage, BaseGameLink, BaseGameLog, BaseGameTitle, BaseGenre, BaseGenreAlias, BaseGenreAliasContext, BaseMedium, BasePlatform, BaseRelease, BaseReleaseImage, BaseReleaseImageContext, BaseTag, BaseTagAlias, BaseTagAliasContext
from core.shared.views import imports as views_import
from core.shared.views.base import AdminListByView, AdminListView, PublicListView
from core.shared.views.imports import DataBulkMixin


# Gestión
# ==============================================================================


class _ReobtenerVndb:
    """Acción masiva extra en Juegos: volver a traer de VNDB los marcados (lanzamientos, personajes, editoras)."""
    extra_bulk_actions = (("reobtener-vndb", "Re-obtener de VNDB (seleccionados)"),)

    @classmethod
    def bulk_run(cls, request, accion, qs):
        if accion != "reobtener-vndb":
            return False
        ids = sorted(set(qs.filter(vndb_id__isnull=False).values_list("vndb_id", flat=True)))
        if not ids:
            messages.warning(request, "Los juegos marcados no tienen id de VNDB.")
            return True
        bg, result = views_import.run_task(tasks.import_vndb_ids_task, "juego", ids)
        views_import.anotar_usuario(result, request.user)
        messages.success(request, f"Re-obtención de {len(ids)} juego(s) de VNDB {'encolada' if bg else 'hecha'}.")
        return True


class _JuegosDelCreador:
    """Acción masiva extra en Creadores: traer de VNDB todos los juegos de los marcados."""
    extra_bulk_actions = (("juegos-vndb", "Traer todos sus juegos de VNDB (seleccionados)"),)

    @classmethod
    def bulk_run(cls, request, accion, qs):
        if accion != "juegos-vndb":
            return False
        ids = sorted(set(qs.filter(vndb_id__isnull=False).values_list("vndb_id", flat=True)))
        if not ids:
            messages.warning(request, "Los creadores marcados no tienen id de VNDB.")
            return True
        bg, result = views_import.run_task(tasks.import_creator_games_task, ids)
        views_import.anotar_usuario(result, request.user)
        messages.success(request, f"Juegos de {len(ids)} creador(es) de VNDB: {'encolado' if bg else 'hecho'}.")
        return True


# ------------------------ personajes de juego (VNDB) ------------------------


class CharacterListView(BaseCharacter, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-character_data"
    create_url = "panel:game-character_create"
    crudo_url = "panel:data-vndb-character_list"                # botón → lo descargado de VNDB, antes de procesar
    crudo_label = _("Datos · Personaje (VNDB)")
    title = _("Lista de personajes de juego")


class CharacterImageListView(BaseCharacterImage, AdminListView):
    home_url = "panel:games-home"
    buttons = (("panel:game-character-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:game-character-image_data"
    create_url = "panel:game-character-image_create"
    title = _("Lista de imágenes de personaje de juego")


class CharacterRoleListView(BaseCharacterRole, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-character-role_data"
    create_url = "panel:game-character-role_create"
    title = _("Lista de roles de personaje")


class CreatorListView(BaseCreator, _JuegosDelCreador, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:creator_data"
    create_url = "panel:creator_create"
    crudo_url = "panel:data-vndb-creator_list"                # botón → lo descargado de VNDB, antes de procesar
    crudo_label = _("Datos · Creador (VNDB)")
    title = _("Lista de creadores")


class CreatorLinkListView(BaseCreatorLink, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:creator-link_data"
    create_url = "panel:creator-link_create"
    title = _("Lista de enlaces")


class CreatorNicknameListView(BaseCreatorNickname, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:creator-nickname_data"
    create_url = "panel:creator-nickname_create"
    title = _("Lista de apodos")


class DataF95CreatorListView(BaseDataF95Creator, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:data-f95-creator_data"
    process_url = "panel:vndb-procesar"   # botón «Procesar pendientes» de la fuente (POST a su vista propia)


class DataF95GameListView(BaseDataF95Game, DataBulkMixin, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:data-f95-game_data"
    process_url = "panel:vndb-procesar"   # botón «Procesar pendientes» de la fuente (POST a su vista propia)
    bulk_process_task = tasks.process_games_pending_task


class DataVndbCharacterListView(BaseDataVndbCharacter, DataBulkMixin, AdminListView):
    home_url = "panel:games-home"
    export_url = "panel:data-vndb-character_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-vndb-character_data"
    procesados_url = "panel:game-character_list"           # botón → las fichas ya procesadas; ahí deja «Procesar pendientes»
    procesados_label = _("Personajes")
    buttons = (("panel:dump-vndb-character", _("Cargar dump"), "filetype-json"), ("panel:process-vndb-character", _("Procesar"), "arrow-repeat"))
    import_url = "panel:vndb-character"   # botón «Importar» → su lanzador
    bulk_process_task = tasks.process_games_pending_task
    bulk_kind = "personaje"
    bulk_ids_task = tasks.import_vndb_ids_task


class DataVndbCreatorListView(BaseDataVndbCreator, DataBulkMixin, AdminListView):
    home_url = "panel:games-home"
    export_url = "panel:data-vndb-creator_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-vndb-creator_data"
    procesados_url = "panel:creator_list"           # botón → las fichas ya procesadas; ahí deja «Procesar pendientes»
    procesados_label = _("Creadores")
    buttons = (("panel:dump-vndb-creator", _("Cargar dump"), "filetype-json"), ("panel:process-vndb-creator", _("Procesar"), "arrow-repeat"))
    import_url = "panel:vndb-creator"   # botón «Importar» → su lanzador
    bulk_process_task = tasks.process_games_pending_task
    bulk_kind = "creador"
    bulk_ids_task = tasks.import_vndb_ids_task


# ------------------------ datos crudos de importación (VNDB; antes en apps/imports) ------------------------


class DataVndbGameListView(BaseDataVndbGame, DataBulkMixin, AdminListView):
    home_url = "panel:games-home"
    export_url = "panel:data-vndb-game_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-vndb-game_data"
    procesados_url = "panel:game_list"           # botón → las fichas ya procesadas; ahí deja «Procesar pendientes»
    procesados_label = _("Juegos")
    buttons = (("panel:dump-vndb-game", _("Cargar dump"), "filetype-json"), ("panel:process-vndb-game", _("Procesar"), "arrow-repeat"))
    import_url = "panel:vndb-game"   # botón «Importar» → su lanzador
    bulk_process_task = tasks.process_games_pending_task
    bulk_kind = "juego"
    bulk_ids_task = tasks.import_vndb_ids_task


class DataVndbReleaseListView(BaseDataVndbRelease, DataBulkMixin, AdminListView):
    home_url = "panel:games-home"
    export_url = "panel:data-vndb-release_export"   # botón «Generar dump» → descarga el .json.gz
    data_url = "panel:data-vndb-release_data"
    procesados_url = "panel:game-release_list"           # botón → las fichas ya procesadas; ahí deja «Procesar pendientes»
    procesados_label = _("Lanzamientos")
    buttons = (("panel:dump-vndb-release", _("Cargar dump"), "filetype-json"), ("panel:process-vndb-release", _("Procesar"), "arrow-repeat"))
    import_url = "panel:vndb-release"   # botón «Importar» → su lanzador
    bulk_process_task = tasks.process_games_pending_task
    bulk_kind = "lanzamiento"
    bulk_ids_task = tasks.import_vndb_ids_task


class DevelopmentEngineListView(BaseDevelopmentEngine, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-engine_data"
    create_url = "panel:game-engine_create"
    title = _("Lista de motores")


class GameListView(BaseGame, _ReobtenerVndb, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game_data"
    create_url = "panel:game_create"
    crudo_url = "panel:data-vndb-game_list"                # botón → lo descargado de VNDB, antes de procesar
    crudo_label = _("Datos · Juego (VNDB)")
    title = _("Lista de juegos")


class GameImageListView(BaseGameImage, AdminListView):
    home_url = "panel:games-home"
    buttons = (("panel:game-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:game-image_data"
    create_url = "panel:game-image_create"
    title = _("Lista de imágenes extra")


class GameLinkListView(BaseGameLink, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-link_data"
    create_url = "panel:game-link_create"
    title = _("Lista de enlaces")


class GameTitleListView(BaseGameTitle, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-title_data"
    create_url = "panel:game-title_create"
    title = _("Lista de títulos")


class GenreListView(BaseGenre, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-genre_data"
    create_url = "panel:game-genre_create"
    title = _("Lista de géneros")


class MediumListView(BaseMedium, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-medium_data"
    create_url = "panel:game-medium_create"
    title = _("Lista de medios")


class PlatformListView(BasePlatform, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-platform_data"
    create_url = "panel:game-platform_create"
    title = _("Lista de plataformas")


class ReleaseListView(BaseRelease, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-release_data"
    create_url = "panel:game-release_create"
    crudo_url = "panel:data-vndb-release_list"                # botón → lo descargado de VNDB, antes de procesar
    crudo_label = _("Datos · Lanzamiento (VNDB)")
    title = _("Lista de lanzamientos de juego")


class GameLogListView(BaseGameLog, AdminListView):
    home_url = "panel:games-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:game-log_data"
    create_url = "panel:game-log_create"
    title = _("Lista de log de juegos")


# ==============================================================================
# Público
# ==============================================================================

# ==============================================================================
# Catálogos sobre la base NUEVA (PublicListView + PublicDataView por data_url)
# ==============================================================================


class CreatorPublicListView(BaseCreator, PublicListView):
    """Catálogo público de CREADORES de juegos: search_words por nombre y llegar
    desde el creador a sus juegos (front cruzado)."""
    data_url = "games:creators-catalog-data"
    background_image = "bg-games-creator"
    background_fallback = "bg-games-home"
    section = "juegos"
    title = _("Creadores")
    # icon = "bi-person-badge"
    # subtitle = _("Desarrolladores de visual novels y juegos.")
    home_url = "games:home"
    home_label = _("juegos")


class PublisherPublicListView(BaseCreator, PublicListView):
    """Catálogo de EDITORAS de juegos (con buscador y filtros)."""
    data_url = "games:publishers-catalog-data"
    background_image = "bg-games-creator"
    background_fallback = "bg-games-home"
    section = "juegos"
    title = _("Editoras")
    icon = "bi-person-badge"
    subtitle = _("Quienes publican y distribuyen juegos.")
    home_url = "games:home"
    home_label = _("juegos")


class GamePublicListView(BaseGame, PublicListView):
    data_url = "games:games-catalog-data"
    background_image = "bg-games-game"
    background_fallback = "bg-games-home"
    section = "juegos"
    title = _("Juegos")
    icon = "bi-controller"
    home_url = "games:home"
    home_label = _("juegos")


class GenreAliasListView(BaseGenreAlias, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:game-genre-alias_data"
    create_url = "panel:game-genre-alias_create"
    title = _("Lista de alias de géneros")


class GenreAliasListByView(BaseGenreAliasContext, AdminListByView):
    """Alias acotados por su padre (`/game-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`."""
    home_url = "panel:games-home"
    create_url = "panel:game-genre-alias_create"
    data_url = "panel:game-genre-alias_data-by"
    full_list_url = "panel:game-genre-alias_list"
    by_url = "panel:game-genre-alias_by"


class ReleaseImageListView(BaseReleaseImage, AdminListView):
    home_url = "panel:games-home"
    buttons = (("panel:game-release-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:game-release-image_data"
    create_url = "panel:game-release-image_create"
    title = _("Lista de imágenes de lanzamiento")


class ReleaseImageListByView(BaseReleaseImageContext, AdminListByView):
    """Imágenes acotadas por su lanzamiento (`/game-release-image/release/<id>/`)."""
    home_url = "panel:games-home"
    create_url = "panel:game-release-image_create"
    data_url = "panel:game-release-image_data-by"
    full_list_url = "panel:game-release-image_list"
    by_url = "panel:game-release-image_by"


class TagListView(BaseTag, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:tag_data"
    create_url = "panel:tag_create"
    title = _("Lista de etiquetas")


class TagAliasListView(BaseTagAlias, AdminListView):
    home_url = "panel:games-home"
    data_url = "panel:tag-alias_data"
    create_url = "panel:tag-alias_create"
    title = _("Lista de alias de etiquetas")


class TagAliasListByView(BaseTagAliasContext, AdminListByView):
    """Alias acotados por su padre (`/tag-alias/tag/<id>/`): los alimenta TagAliasDataView con `/data/tag/<id>/`."""
    home_url = "panel:games-home"
    create_url = "panel:tag-alias_create"
    data_url = "panel:tag-alias_data-by"
    full_list_url = "panel:tag-alias_list"
    by_url = "panel:tag-alias_by"
