"""URLs del panel para games (sección «Juegos»): home + CRUD por entidad.

Rutas EXPLÍCITAS (estilo Hades): una `path()` por vista, con su `name=` editable.
Sin funciones que las generen. Se montan en el namespace `panel` desde core/panel_urls.py.

Rutas por entidad: list · [nuevo] · data (DataTables) · select (AJAX FK/M2M) ·
detail · editar · eliminar · accion (toggle is_active/is_staff/...).

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.games import views as v
from apps.games.views import v8_import as imp
from apps.games.views.v8_import import VNDBTagsLoadView, VNDBTagsSummaryView
from core.views import AdminImageActionView, AdminToggleView


urlpatterns = [
    path('', include('apps.games.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('games/', v.GamesHomeView.as_view(), name='games-home'),

    # ---------- game-character · Character ----------
    path('game-character/', v.CharacterListView.as_view(), name='game-character_list'),
    path('game-character/create/', v.CharacterCreateView.as_view(), name='game-character_create'),
    path('game-character/<int:pk>/', v.CharacterDetailView.as_view(), name='game-character_detail'),
    path('game-character/<int:pk>/update/', v.CharacterUpdateView.as_view(), name='game-character_update'),
    path('game-character/<int:pk>/delete/', v.CharacterDeleteView.as_view(), name='game-character_delete'),
    path('game-character/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CharacterListView.model, entity='game-character', label='personaje de juego', namespace='panel'), name='game-character_toggle'),
    path('game-character/<str:tipo>/<str:pk>/', v.CharacterListByView.as_view(), name='game-character_by'),

    # ---------- game-character-image · CharacterImage ----------
    path('game-character-image/', v.CharacterImageListView.as_view(), name='game-character-image_list'),
    path('game-character-image/download/', v.CharacterImageDownloadView.as_view(), name='game-character-image_download'),   # descargar pendientes (N o todas)
    path('game-character-image/create/', v.CharacterImageCreateView.as_view(), name='game-character-image_create'),
    path('game-character-image/<int:pk>/', v.CharacterImageDetailView.as_view(), name='game-character-image_detail'),
    path('game-character-image/<int:pk>/update/', v.CharacterImageUpdateView.as_view(), name='game-character-image_update'),
    path('game-character-image/<int:pk>/delete/', v.CharacterImageDeleteView.as_view(), name='game-character-image_delete'),
    path('game-character-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CharacterImageListView.model, entity='game-character-image', label='imagen de personaje', namespace='panel'), name='game-character-image_toggle'),
    path('game-character-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.CharacterImageListView.model), name='game-character-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('game-character-image/<str:tipo>/<str:pk>/', v.CharacterImageListByView.as_view(), name='game-character-image_by'),

    # ---------- game-character-role · CharacterRole ----------
    path('game-character-role/', v.CharacterRoleListView.as_view(), name='game-character-role_list'),
    path('game-character-role/create/', v.CharacterRoleCreateView.as_view(), name='game-character-role_create'),
    path('game-character-role/<int:pk>/', v.CharacterRoleDetailView.as_view(), name='game-character-role_detail'),
    path('game-character-role/<int:pk>/update/', v.CharacterRoleUpdateView.as_view(), name='game-character-role_update'),
    path('game-character-role/<int:pk>/delete/', v.CharacterRoleDeleteView.as_view(), name='game-character-role_delete'),
    path('game-character-role/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CharacterRoleListView.model, entity='game-character-role', label='rol de personaje', namespace='panel'), name='game-character-role_toggle'),
    path('game-character-role/<str:tipo>/<str:pk>/', v.CharacterRoleListByView.as_view(), name='game-character-role_by'),

    # ---------- creator · Creator ----------
    path('creator/', v.CreatorListView.as_view(), name='creator_list'),
    path('creator/create/', v.CreatorCreateView.as_view(), name='creator_create'),
    path('creator/<int:pk>/', v.CreatorDetailView.as_view(), name='creator_detail'),
    path('creator/<int:pk>/update/', v.CreatorUpdateView.as_view(), name='creator_update'),
    path('creator/<int:pk>/delete/', v.CreatorDeleteView.as_view(), name='creator_delete'),
    path('creator/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CreatorListView.model, entity='creator', label='creador', namespace='panel'), name='creator_toggle'),
    path('creator/<str:tipo>/<str:pk>/', v.CreatorListByView.as_view(), name='creator_by'),

    # ---------- creator-link · CreatorLink ----------
    path('creator-link/', v.CreatorLinkListView.as_view(), name='creator-link_list'),
    path('creator-link/create/', v.CreatorLinkCreateView.as_view(), name='creator-link_create'),
    path('creator-link/<int:pk>/', v.CreatorLinkDetailView.as_view(), name='creator-link_detail'),
    path('creator-link/<int:pk>/update/', v.CreatorLinkUpdateView.as_view(), name='creator-link_update'),
    path('creator-link/<int:pk>/delete/', v.CreatorLinkDeleteView.as_view(), name='creator-link_delete'),
    path('creator-link/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CreatorLinkListView.model, entity='creator-link', label='enlace', namespace='panel'), name='creator-link_toggle'),
    path('creator-link/<str:tipo>/<str:pk>/', v.CreatorLinkListByView.as_view(), name='creator-link_by'),

    # ---------- creator-nickname · CreatorNickname ----------
    path('creator-nickname/', v.CreatorNicknameListView.as_view(), name='creator-nickname_list'),
    path('creator-nickname/create/', v.CreatorNicknameCreateView.as_view(), name='creator-nickname_create'),
    path('creator-nickname/<int:pk>/', v.CreatorNicknameDetailView.as_view(), name='creator-nickname_detail'),
    path('creator-nickname/<int:pk>/update/', v.CreatorNicknameUpdateView.as_view(), name='creator-nickname_update'),
    path('creator-nickname/<int:pk>/delete/', v.CreatorNicknameDeleteView.as_view(), name='creator-nickname_delete'),
    path('creator-nickname/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CreatorNicknameListView.model, entity='creator-nickname', label='apodo', namespace='panel'), name='creator-nickname_toggle'),
    path('creator-nickname/<str:tipo>/<str:pk>/', v.CreatorNicknameListByView.as_view(), name='creator-nickname_by'),

    # ---------- data-f95-creator · DataF95Creator ----------
    path('data-f95-creator/', v.DataF95CreatorListView.as_view(), name='data-f95-creator_list'),
    path('data-f95-creator/create/', v.DataF95CreatorCreateView.as_view(), name='data-f95-creator_create'),
    path('data-f95-creator/<int:pk>/', v.DataF95CreatorDetailView.as_view(), name='data-f95-creator_detail'),
    path('data-f95-creator/<int:pk>/update/', v.DataF95CreatorUpdateView.as_view(), name='data-f95-creator_update'),
    path('data-f95-creator/<int:pk>/delete/', v.DataF95CreatorDeleteView.as_view(), name='data-f95-creator_delete'),

    # ---------- data-f95-game · DataF95Game ----------
    path('data-f95-game/', v.DataF95GameListView.as_view(), name='data-f95-game_list'),
    path('data-f95-game/create/', v.DataF95GameCreateView.as_view(), name='data-f95-game_create'),
    path('data-f95-game/<int:pk>/', v.DataF95GameDetailView.as_view(), name='data-f95-game_detail'),
    path('data-f95-game/<int:pk>/update/', v.DataF95GameUpdateView.as_view(), name='data-f95-game_update'),
    path('data-f95-game/<int:pk>/delete/', v.DataF95GameDeleteView.as_view(), name='data-f95-game_delete'),

    # ---------- data-vndb-character · DataVndbCharacter ----------
    path('data-vndb-character/', v.DataVndbCharacterListView.as_view(), name='data-vndb-character_list'),
    path('data-vndb-character/create/', v.DataVndbCharacterCreateView.as_view(), name='data-vndb-character_create'),
    path('data-vndb-character/export/', imp.DataVndbCharacterExportView.as_view(), name='data-vndb-character_export'),   # «Generar dump»
    path('data-vndb-character/<int:pk>/', v.DataVndbCharacterDetailView.as_view(), name='data-vndb-character_detail'),
    path('data-vndb-character/<int:pk>/update/', v.DataVndbCharacterUpdateView.as_view(), name='data-vndb-character_update'),
    path('data-vndb-character/<int:pk>/delete/', v.DataVndbCharacterDeleteView.as_view(), name='data-vndb-character_delete'),

    # ---------- data-vndb-creator · DataVndbCreator ----------
    path('data-vndb-creator/', v.DataVndbCreatorListView.as_view(), name='data-vndb-creator_list'),
    path('data-vndb-creator/create/', v.DataVndbCreatorCreateView.as_view(), name='data-vndb-creator_create'),
    path('data-vndb-creator/export/', imp.DataVndbCreatorExportView.as_view(), name='data-vndb-creator_export'),   # «Generar dump»
    path('data-vndb-creator/<int:pk>/', v.DataVndbCreatorDetailView.as_view(), name='data-vndb-creator_detail'),
    path('data-vndb-creator/<int:pk>/update/', v.DataVndbCreatorUpdateView.as_view(), name='data-vndb-creator_update'),
    path('data-vndb-creator/<int:pk>/delete/', v.DataVndbCreatorDeleteView.as_view(), name='data-vndb-creator_delete'),

    # ---------- data-vndb-game · DataVndbGame ----------
    path('data-vndb-game/', v.DataVndbGameListView.as_view(), name='data-vndb-game_list'),
    path('data-vndb-game/create/', v.DataVndbGameCreateView.as_view(), name='data-vndb-game_create'),
    path('data-vndb-game/export/', imp.DataVndbGameExportView.as_view(), name='data-vndb-game_export'),   # «Generar dump»
    path('data-vndb-game/<int:pk>/', v.DataVndbGameDetailView.as_view(), name='data-vndb-game_detail'),
    path('data-vndb-game/<int:pk>/update/', v.DataVndbGameUpdateView.as_view(), name='data-vndb-game_update'),
    path('data-vndb-game/<int:pk>/delete/', v.DataVndbGameDeleteView.as_view(), name='data-vndb-game_delete'),

    # ---------- data-vndb-release · DataVndbRelease ----------
    path('data-vndb-release/', v.DataVndbReleaseListView.as_view(), name='data-vndb-release_list'),
    path('data-vndb-release/create/', v.DataVndbReleaseCreateView.as_view(), name='data-vndb-release_create'),
    path('data-vndb-release/export/', imp.DataVndbReleaseExportView.as_view(), name='data-vndb-release_export'),   # «Generar dump»
    path('data-vndb-release/<int:pk>/', v.DataVndbReleaseDetailView.as_view(), name='data-vndb-release_detail'),
    path('data-vndb-release/<int:pk>/update/', v.DataVndbReleaseUpdateView.as_view(), name='data-vndb-release_update'),
    path('data-vndb-release/<int:pk>/delete/', v.DataVndbReleaseDeleteView.as_view(), name='data-vndb-release_delete'),

    # ---------- game-engine · DevelopmentEngine ----------
    path('game-engine/', v.DevelopmentEngineListView.as_view(), name='game-engine_list'),
    path('game-engine/create/', v.DevelopmentEngineCreateView.as_view(), name='game-engine_create'),
    path('game-engine/<int:pk>/', v.DevelopmentEngineDetailView.as_view(), name='game-engine_detail'),
    path('game-engine/<int:pk>/update/', v.DevelopmentEngineUpdateView.as_view(), name='game-engine_update'),
    path('game-engine/<int:pk>/delete/', v.DevelopmentEngineDeleteView.as_view(), name='game-engine_delete'),
    path('game-engine/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.DevelopmentEngineListView.model, entity='game-engine', label='motor', namespace='panel'), name='game-engine_toggle'),

    # ---------- game · Game ----------
    path('game/', v.GameListView.as_view(), name='game_list'),
    path('game/create/', v.GameCreateView.as_view(), name='game_create'),
    path('game/<int:pk>/', v.GameDetailView.as_view(), name='game_detail'),
    path('game/<int:pk>/update/', v.GameUpdateView.as_view(), name='game_update'),
    path('game/<int:pk>/delete/', v.GameDeleteView.as_view(), name='game_delete'),
    path('game/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GameListView.model, entity='game', label='juego', namespace='panel'), name='game_toggle'),
    path('game/<str:tipo>/<str:pk>/', v.GameListByView.as_view(), name='game_by'),

    # ---------- game-image · GameImage ----------
    path('game-image/', v.GameImageListView.as_view(), name='game-image_list'),
    path('game-image/download/', v.GameImageDownloadView.as_view(), name='game-image_download'),   # descargar pendientes (N o todas)
    path('game-image/create/', v.GameImageCreateView.as_view(), name='game-image_create'),
    path('game-image/<int:pk>/', v.GameImageDetailView.as_view(), name='game-image_detail'),
    path('game-image/<int:pk>/update/', v.GameImageUpdateView.as_view(), name='game-image_update'),
    path('game-image/<int:pk>/delete/', v.GameImageDeleteView.as_view(), name='game-image_delete'),
    path('game-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GameImageListView.model, entity='game-image', label='imagen', namespace='panel'), name='game-image_toggle'),
    path('game-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.GameImageListView.model), name='game-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('game-image/<str:tipo>/<str:pk>/', v.GameImageListByView.as_view(), name='game-image_by'),

    # ---------- game-link · GameLink ----------
    path('game-link/', v.GameLinkListView.as_view(), name='game-link_list'),
    path('game-link/create/', v.GameLinkCreateView.as_view(), name='game-link_create'),
    path('game-link/<int:pk>/', v.GameLinkDetailView.as_view(), name='game-link_detail'),
    path('game-link/<int:pk>/update/', v.GameLinkUpdateView.as_view(), name='game-link_update'),
    path('game-link/<int:pk>/delete/', v.GameLinkDeleteView.as_view(), name='game-link_delete'),
    path('game-link/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GameLinkListView.model, entity='game-link', label='enlace', namespace='panel'), name='game-link_toggle'),
    path('game-link/<str:tipo>/<str:pk>/', v.GameLinkListByView.as_view(), name='game-link_by'),

    # ---------- game-title · GameTitle ----------
    path('game-title/', v.GameTitleListView.as_view(), name='game-title_list'),
    path('game-title/create/', v.GameTitleCreateView.as_view(), name='game-title_create'),
    path('game-title/<int:pk>/', v.GameTitleDetailView.as_view(), name='game-title_detail'),
    path('game-title/<int:pk>/update/', v.GameTitleUpdateView.as_view(), name='game-title_update'),
    path('game-title/<int:pk>/delete/', v.GameTitleDeleteView.as_view(), name='game-title_delete'),
    path('game-title/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GameTitleListView.model, entity='game-title', label='título', namespace='panel'), name='game-title_toggle'),
    path('game-title/<str:tipo>/<str:pk>/', v.GameTitleListByView.as_view(), name='game-title_by'),

    # ---------- game-genre · Genre ----------
    path('game-genre/', v.GenreListView.as_view(), name='game-genre_list'),
    path('game-genre/create/', v.GenreCreateView.as_view(), name='game-genre_create'),
    path('game-genre/<int:pk>/', v.GenreDetailView.as_view(), name='game-genre_detail'),
    path('game-genre/<int:pk>/update/', v.GenreUpdateView.as_view(), name='game-genre_update'),
    path('game-genre/<int:pk>/delete/', v.GenreDeleteView.as_view(), name='game-genre_delete'),
    path('game-genre/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GenreListView.model, entity='game-genre', label='género', namespace='panel'), name='game-genre_toggle'),

    # ---------- game-genre-alias · GenreAlias ----------
    path('game-genre-alias/', v.GenreAliasListView.as_view(), name='game-genre-alias_list'),
    path('game-genre-alias/create/', v.GenreAliasCreateView.as_view(), name='game-genre-alias_create'),
    path('game-genre-alias/<int:pk>/', v.GenreAliasDetailView.as_view(), name='game-genre-alias_detail'),
    path('game-genre-alias/<int:pk>/update/', v.GenreAliasUpdateView.as_view(), name='game-genre-alias_update'),
    path('game-genre-alias/<int:pk>/delete/', v.GenreAliasDeleteView.as_view(), name='game-genre-alias_delete'),
    path('game-genre-alias/<str:tipo>/<str:pk>/', v.GenreAliasListByView.as_view(), name='game-genre-alias_by'),

    # ---------- game-medium · Medium ----------
    path('game-medium/', v.MediumListView.as_view(), name='game-medium_list'),
    path('game-medium/create/', v.MediumCreateView.as_view(), name='game-medium_create'),
    path('game-medium/<int:pk>/', v.MediumDetailView.as_view(), name='game-medium_detail'),
    path('game-medium/<int:pk>/update/', v.MediumUpdateView.as_view(), name='game-medium_update'),
    path('game-medium/<int:pk>/delete/', v.MediumDeleteView.as_view(), name='game-medium_delete'),
    path('game-medium/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MediumListView.model, entity='game-medium', label='medio', namespace='panel'), name='game-medium_toggle'),

    # ---------- game-platform · Platform ----------
    path('game-platform/', v.PlatformListView.as_view(), name='game-platform_list'),
    path('game-platform/create/', v.PlatformCreateView.as_view(), name='game-platform_create'),
    path('game-platform/<int:pk>/', v.PlatformDetailView.as_view(), name='game-platform_detail'),
    path('game-platform/<int:pk>/update/', v.PlatformUpdateView.as_view(), name='game-platform_update'),
    path('game-platform/<int:pk>/delete/', v.PlatformDeleteView.as_view(), name='game-platform_delete'),
    path('game-platform/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.PlatformListView.model, entity='game-platform', label='plataforma', namespace='panel'), name='game-platform_toggle'),

    # ---------- game-release · Release ----------
    path('game-release/', v.ReleaseListView.as_view(), name='game-release_list'),
    path('game-release/create/', v.ReleaseCreateView.as_view(), name='game-release_create'),
    path('game-release/<int:pk>/', v.ReleaseDetailView.as_view(), name='game-release_detail'),
    path('game-release/<int:pk>/update/', v.ReleaseUpdateView.as_view(), name='game-release_update'),
    path('game-release/<int:pk>/delete/', v.ReleaseDeleteView.as_view(), name='game-release_delete'),
    path('game-release/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ReleaseListView.model, entity='game-release', label='lanzamiento', namespace='panel'), name='game-release_toggle'),
    path('game-release/<str:tipo>/<str:pk>/', v.ReleaseListByView.as_view(), name='game-release_by'),

    # ---------- game-release-image · ReleaseImage ----------
    path('game-release-image/', v.ReleaseImageListView.as_view(), name='game-release-image_list'),
    path('game-release-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.ReleaseImageListView.model), name='game-release-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('game-release-image/download/', v.ReleaseImageDownloadView.as_view(), name='game-release-image_download'),   # descargar pendientes (N o todas)
    path('game-release-image/create/', v.ReleaseImageCreateView.as_view(), name='game-release-image_create'),
    path('game-release-image/<int:pk>/', v.ReleaseImageDetailView.as_view(), name='game-release-image_detail'),
    path('game-release-image/<int:pk>/update/', v.ReleaseImageUpdateView.as_view(), name='game-release-image_update'),
    path('game-release-image/<int:pk>/delete/', v.ReleaseImageDeleteView.as_view(), name='game-release-image_delete'),
    path('game-release-image/<str:tipo>/<str:pk>/', v.ReleaseImageListByView.as_view(), name='game-release-image_by'),

    # ---------- tag · Tag ----------
    path('tag/', v.TagListView.as_view(), name='tag_list'),
    path('tag/create/', v.TagCreateView.as_view(), name='tag_create'),
    path('tag/<int:pk>/', v.TagDetailView.as_view(), name='tag_detail'),
    path('tag/<int:pk>/update/', v.TagUpdateView.as_view(), name='tag_update'),
    path('tag/<int:pk>/delete/', v.TagDeleteView.as_view(), name='tag_delete'),

    # ---------- tag-alias · TagAlias ----------
    path('tag-alias/', v.TagAliasListView.as_view(), name='tag-alias_list'),
    path('tag-alias/create/', v.TagAliasCreateView.as_view(), name='tag-alias_create'),
    path('tag-alias/<int:pk>/', v.TagAliasDetailView.as_view(), name='tag-alias_detail'),
    path('tag-alias/<int:pk>/update/', v.TagAliasUpdateView.as_view(), name='tag-alias_update'),
    path('tag-alias/<int:pk>/delete/', v.TagAliasDeleteView.as_view(), name='tag-alias_delete'),
    path('tag-alias/<str:tipo>/<str:pk>/', v.TagAliasListByView.as_view(), name='tag-alias_by'),

    # ---------- importación VNDB (antes en apps/imports): lanzador + datos crudos ----------
    # Lanzadores VNDB: UNA vista por tabla Data; sus formas de importar (buscar, por id, por páginas) van en la misma página.
    path("vndb/game/", imp.LoadVNDBDataF95GameView.as_view(), name="vndb-game"),
    path("vndb/game/buscar/", imp.LoadVNDBDataF95GameSearchView.as_view(), name="vndb-game-buscar"),     # resultados por nombre
    path("vndb/creator/", imp.LoadVNDBDataCreatorView.as_view(), name="vndb-creator"),
    path("vndb/creator/buscar/", imp.LoadVNDBDataCreatorSearchView.as_view(), name="vndb-creator-buscar"),
    path("vndb/release/", imp.LoadVNDBDataReleaseView.as_view(), name="vndb-release"),
    path("vndb/release/buscar/", imp.LoadVNDBDataReleaseSearchView.as_view(), name="vndb-release-buscar"),
    path("vndb/character/", imp.LoadVNDBDataCharacterView.as_view(), name="vndb-character"),
    path("vndb/character/buscar/", imp.LoadVNDBDataCharacterSearchView.as_view(), name="vndb-character-buscar"),
    path("vndb/process/character/", imp.ProcessVndbCharacterView.as_view(), name="process-vndb-character"),
    path("vndb/process/creator/", imp.ProcessVndbCreatorView.as_view(), name="process-vndb-creator"),
    path("vndb/process/game/", imp.ProcessVndbGameView.as_view(), name="process-vndb-game"),
    path("vndb/process/release/", imp.ProcessVndbReleaseView.as_view(), name="process-vndb-release"),
    path("vndb/procesar/", imp.VNDBProcessPendingView.as_view(), name="vndb-procesar"),   # POST «Procesar pendientes»
    # Dumps de VNDB: dos vistas por tipo (formulario → resumen). El archivo lo genera nuestro exportador.
    path("vndb/dump/game/", imp.VndbGameLoadView.as_view(), name="dump-vndb-game"),
    path("vndb/dump/game/resumen/", imp.VndbGameSummaryView.as_view(), name="dump-vndb-game-summary"),
    path("vndb/dump/creator/", imp.VndbCreatorLoadView.as_view(), name="dump-vndb-creator"),
    path("vndb/dump/creator/resumen/", imp.VndbCreatorSummaryView.as_view(), name="dump-vndb-creator-summary"),
    path("vndb/dump/release/", imp.VndbReleaseLoadView.as_view(), name="dump-vndb-release"),
    path("vndb/dump/release/resumen/", imp.VndbReleaseSummaryView.as_view(), name="dump-vndb-release-summary"),
    path("vndb/dump/character/", imp.VndbCharacterLoadView.as_view(), name="dump-vndb-character"),
    path("vndb/dump/character/resumen/", imp.VndbCharacterSummaryView.as_view(), name="dump-vndb-character-summary"),
    path("vndb/load-tags/", VNDBTagsLoadView.as_view(), name="load-tags-vndb"),
    path("vndb/load-tags/summary/", VNDBTagsSummaryView.as_view(), name="load-tags-vndb-summary"),

    # ---------- game-log · GameLog ----------
    path('game-log/', v.GameLogListView.as_view(), name='game-log_list'),
    path('game-log/create/', v.GameLogCreateView.as_view(), name='game-log_create'),
    path('game-log/<int:pk>/', v.GameLogDetailView.as_view(), name='game-log_detail'),
    path('game-log/<int:pk>/update/', v.GameLogUpdateView.as_view(), name='game-log_update'),
    path('game-log/<int:pk>/delete/', v.GameLogDeleteView.as_view(), name='game-log_delete'),
]
