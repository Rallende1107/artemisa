"""URLs de DATOS del panel de games: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.games import views as v


urlpatterns = [
    # ---------- game-character · Character ----------
    path('game-character/data/', v.CharacterDataView.as_view(), name='game-character_data'),
    path('game-character/data/<str:tipo>/<str:pk>/', v.CharacterDataView.as_view(), name='game-character_data-by'),
    path('game-character/select/', v.CharacterSelectView.as_view(), name='game-character_select'),

    # ---------- game-character-image · CharacterImage ----------
    path('game-character-image/data/', v.CharacterImageDataView.as_view(), name='game-character-image_data'),
    path('game-character-image/data/<str:tipo>/<str:pk>/', v.CharacterImageDataView.as_view(), name='game-character-image_data-by'),

    # ---------- game-character-role · CharacterRole ----------
    path('game-character-role/data/', v.CharacterRoleDataView.as_view(), name='game-character-role_data'),
    path('game-character-role/data/<str:tipo>/<str:pk>/', v.CharacterRoleDataView.as_view(), name='game-character-role_data-by'),

    # ---------- creator · Creator ----------
    path('creator/data/', v.CreatorDataView.as_view(), name='creator_data'),
    path('creator/data/<str:tipo>/<str:pk>/', v.CreatorDataView.as_view(), name='creator_data-by'),
    path('creator/select/', v.CreatorSelectView.as_view(), name='creator_select'),

    # ---------- creator-link · CreatorLink ----------
    path('creator-link/data/', v.CreatorLinkDataView.as_view(), name='creator-link_data'),
    path('creator-link/data/<str:tipo>/<str:pk>/', v.CreatorLinkDataView.as_view(), name='creator-link_data-by'),
    path('creator-link/select/', v.CreatorLinkSelectView.as_view(), name='creator-link_select'),

    # ---------- creator-nickname · CreatorNickname ----------
    path('creator-nickname/data/', v.CreatorNicknameDataView.as_view(), name='creator-nickname_data'),
    path('creator-nickname/data/<str:tipo>/<str:pk>/', v.CreatorNicknameDataView.as_view(), name='creator-nickname_data-by'),
    path('creator-nickname/select/', v.CreatorNicknameSelectView.as_view(), name='creator-nickname_select'),

    # ---------- data-f95-creator · DataF95Creator ----------
    path('data-f95-creator/data/', v.DataF95CreatorDataView.as_view(), name='data-f95-creator_data'),

    # ---------- data-f95-game · DataF95Game ----------
    path('data-f95-game/data/', v.DataF95GameDataView.as_view(), name='data-f95-game_data'),

    # ---------- data-vndb-character · DataVndbCharacter ----------
    path('data-vndb-character/data/', v.DataVndbCharacterDataView.as_view(), name='data-vndb-character_data'),

    # ---------- data-vndb-creator · DataVndbCreator ----------
    path('data-vndb-creator/data/', v.DataVndbCreatorDataView.as_view(), name='data-vndb-creator_data'),

    # ---------- data-vndb-game · DataVndbGame ----------
    path('data-vndb-game/data/', v.DataVndbGameDataView.as_view(), name='data-vndb-game_data'),

    # ---------- data-vndb-release · DataVndbRelease ----------
    path('data-vndb-release/data/', v.DataVndbReleaseDataView.as_view(), name='data-vndb-release_data'),

    # ---------- game-engine · DevelopmentEngine ----------
    path('game-engine/data/', v.DevelopmentEngineDataView.as_view(), name='game-engine_data'),
    path('game-engine/select/', v.DevelopmentEngineSelectView.as_view(), name='game-engine_select'),

    # ---------- game · Game ----------
    path('game/data/', v.GameDataView.as_view(), name='game_data'),
    path('game/data/<str:tipo>/<str:pk>/', v.GameDataView.as_view(), name='game_data-by'),
    path('game/select/', v.GameSelectView.as_view(), name='game_select'),

    # ---------- game-image · GameImage ----------
    path('game-image/data/', v.GameImageDataView.as_view(), name='game-image_data'),
    path('game-image/data/<str:tipo>/<str:pk>/', v.GameImageDataView.as_view(), name='game-image_data-by'),
    path('game-image/select/', v.GameImageSelectView.as_view(), name='game-image_select'),

    # ---------- game-link · GameLink ----------
    path('game-link/data/', v.GameLinkDataView.as_view(), name='game-link_data'),
    path('game-link/data/<str:tipo>/<str:pk>/', v.GameLinkDataView.as_view(), name='game-link_data-by'),
    path('game-link/select/', v.GameLinkSelectView.as_view(), name='game-link_select'),

    # ---------- game-title · GameTitle ----------
    path('game-title/data/', v.GameTitleDataView.as_view(), name='game-title_data'),
    path('game-title/data/<str:tipo>/<str:pk>/', v.GameTitleDataView.as_view(), name='game-title_data-by'),
    path('game-title/select/', v.GameTitleSelectView.as_view(), name='game-title_select'),

    # ---------- game-genre · Genre ----------
    path('game-genre/data/', v.GenreDataView.as_view(), name='game-genre_data'),
    path('game-genre/select/', v.GenreSelectView.as_view(), name='game-genre_select'),

    # ---------- game-genre-alias · GenreAlias ----------
    path('game-genre-alias/data/', v.GenreAliasDataView.as_view(), name='game-genre-alias_data'),
    path('game-genre-alias/data/<str:tipo>/<str:pk>/', v.GenreAliasDataView.as_view(), name='game-genre-alias_data-by'),

    # ---------- game-medium · Medium ----------
    path('game-medium/data/', v.MediumDataView.as_view(), name='game-medium_data'),
    path('game-medium/select/', v.MediumSelectView.as_view(), name='game-medium_select'),

    # ---------- game-platform · Platform ----------
    path('game-platform/data/', v.PlatformDataView.as_view(), name='game-platform_data'),
    path('game-platform/select/', v.PlatformSelectView.as_view(), name='game-platform_select'),

    # ---------- game-release · Release ----------
    path('game-release/data/', v.ReleaseDataView.as_view(), name='game-release_data'),
    path('game-release/data/<str:tipo>/<str:pk>/', v.ReleaseDataView.as_view(), name='game-release_data-by'),

    # ---------- game-release-image · ReleaseImage ----------
    path('game-release-image/data/', v.ReleaseImageDataView.as_view(), name='game-release-image_data'),
    path('game-release-image/data/<str:tipo>/<str:pk>/', v.ReleaseImageDataView.as_view(), name='game-release-image_data-by'),

    # ---------- tag · Tag ----------
    path('tag/data/', v.TagDataView.as_view(), name='tag_data'),

    # ---------- tag-alias · TagAlias ----------
    path('tag-alias/data/', v.TagAliasDataView.as_view(), name='tag-alias_data'),
    path('tag-alias/data/<str:tipo>/<str:pk>/', v.TagAliasDataView.as_view(), name='tag-alias_data-by'),

    # ---------- game-log · GameLog ----------
    path('game-log/data/', v.GameLogDataView.as_view(), name='game-log_data'),
]
