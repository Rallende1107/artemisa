"""URLs de DATOS del panel de otaku: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.otaku import views as v


urlpatterns = [
    # ---------- anime · Anime ----------
    path('anime/data/', v.AnimeDataView.as_view(), name='anime_data'),
    path('anime/data/<str:tipo>/<str:pk>/', v.AnimeDataView.as_view(), name='anime_data-by'),
    path('anime/select/', v.AnimeSelectView.as_view(), name='anime_select'),

    # ---------- anime-character · AnimeCharacter ----------
    path('anime-character/data/', v.AnimeCharacterDataView.as_view(), name='anime-character_data'),
    path('anime-character/data/<str:tipo>/<str:pk>/', v.AnimeCharacterDataView.as_view(), name='anime-character_data-by'),
    path('anime-character/select/', v.AnimeCharacterSelectView.as_view(), name='anime-character_select'),

    # ---------- anime-image · AnimeImage ----------
    path('anime-image/data/', v.AnimeImageDataView.as_view(), name='anime-image_data'),
    path('anime-image/data/<str:tipo>/<str:pk>/', v.AnimeImageDataView.as_view(), name='anime-image_data-by'),
    path('anime-image/select/', v.AnimeImageSelectView.as_view(), name='anime-image_select'),

    # ---------- anime-song · AnimeSong ----------
    path('anime-song/data/', v.AnimeSongDataView.as_view(), name='anime-song_data'),
    path('anime-song/data/<str:tipo>/<str:pk>/', v.AnimeSongDataView.as_view(), name='anime-song_data-by'),
    # listas FIJAS por tipo de canción (una URL por tipo)
    path('anime-song/select/', v.AnimeSongSelectView.as_view(), name='anime-song_select'),

    # ---------- anime-staff · AnimeStaff ----------
    path('anime-staff/data/', v.AnimeStaffDataView.as_view(), name='anime-staff_data'),
    path('anime-staff/data/<str:tipo>/<str:pk>/', v.AnimeStaffDataView.as_view(), name='anime-staff_data-by'),
    path('anime-staff/select/', v.AnimeStaffSelectView.as_view(), name='anime-staff_select'),

    # ---------- anime-title · AnimeTitle ----------
    path('anime-title/data/', v.AnimeTitleDataView.as_view(), name='anime-title_data'),
    path('anime-title/data/<str:tipo>/<str:pk>/', v.AnimeTitleDataView.as_view(), name='anime-title_data-by'),
    path('anime-title/select/', v.AnimeTitleSelectView.as_view(), name='anime-title_select'),

    # ---------- character · Character ----------
    path('character/data/', v.CharacterDataView.as_view(), name='character_data'),
    path('character/data/<str:tipo>/<str:pk>/', v.CharacterDataView.as_view(), name='character_data-by'),
    path('character/select/', v.CharacterSelectView.as_view(), name='character_select'),

    # ---------- character-image · CharacterImage ----------
    path('character-image/data/', v.CharacterImageDataView.as_view(), name='character-image_data'),
    path('character-image/data/<str:tipo>/<str:pk>/', v.CharacterImageDataView.as_view(), name='character-image_data-by'),
    path('character-image/select/', v.CharacterImageSelectView.as_view(), name='character-image_select'),

    # ---------- character-nickname · CharacterNickname ----------
    path('character-nickname/data/', v.CharacterNicknameDataView.as_view(), name='character-nickname_data'),
    path('character-nickname/data/<str:tipo>/<str:pk>/', v.CharacterNicknameDataView.as_view(), name='character-nickname_data-by'),
    path('character-nickname/select/', v.CharacterNicknameSelectView.as_view(), name='character-nickname_select'),

    # ---------- character-voice · CharacterVoice ----------
    path('character-voice/data/', v.CharacterVoiceDataView.as_view(), name='character-voice_data'),
    path('character-voice/data/<str:tipo>/<str:pk>/', v.CharacterVoiceDataView.as_view(), name='character-voice_data-by'),
    path('character-voice/select/', v.CharacterVoiceSelectView.as_view(), name='character-voice_select'),


    # ---------- vistas FIJAS de Otaku: imágenes con ficha MAL (el modelo vive en otra app) ----------
    path('company-image-mal/data/', v.CompanyImageMalDataView.as_view(), name='company-image-mal_data'),
    path('person-image-mal/data/', v.PersonImageMalDataView.as_view(), name='person-image-mal_data'),

    # ---------- company-mal · CompanyMAL ----------
    path('company-mal/data/', v.CompanyMALDataView.as_view(), name='company-mal_data'),
    path('company-mal/select/', v.CompanyMALSelectView.as_view(), name='company-mal_select'),

    # ---------- data-anilist-anime · DataAnilistAnime ----------
    path('data-anilist-anime/data/', v.DataAnilistAnimeDataView.as_view(), name='data-anilist-anime_data'),
    # ---------- data-anilist-character · DataAnilistCharacter ----------
    path('data-anilist-character/data/', v.DataAnilistCharacterDataView.as_view(), name='data-anilist-character_data'),
    # ---------- data-anilist-manga · DataAnilistManga ----------
    path('data-anilist-manga/data/', v.DataAnilistMangaDataView.as_view(), name='data-anilist-manga_data'),
    # ---------- data-anilist-person · DataAnilistPerson ----------
    path('data-anilist-person/data/', v.DataAnilistPersonDataView.as_view(), name='data-anilist-person_data'),

    # ---------- data-mal-anime · DataMalAnime ----------
    path('data-mal-anime/data/', v.DataMalAnimeDataView.as_view(), name='data-mal-anime_data'),

    # ---------- data-mal-anime-character · DataMalAnimeCharacter ----------
    path('data-mal-anime-character/data/', v.DataMalAnimeCharacterDataView.as_view(), name='data-mal-anime-character_data'),

    # ---------- data-mal-anime-picture · DataMalAnimePicture ----------
    path('data-mal-anime-picture/data/', v.DataMalAnimePictureDataView.as_view(), name='data-mal-anime-picture_data'),

    # ---------- data-mal-anime-staff · DataMalAnimeStaff ----------
    path('data-mal-anime-staff/data/', v.DataMalAnimeStaffDataView.as_view(), name='data-mal-anime-staff_data'),

    # ---------- data-mal-character · DataMalCharacter ----------
    path('data-mal-character/data/', v.DataMalCharacterDataView.as_view(), name='data-mal-character_data'),

    # ---------- data-mal-character-picture · DataMalCharacterPicture ----------
    path('data-mal-character-picture/data/', v.DataMalCharacterPictureDataView.as_view(), name='data-mal-character-picture_data'),

    # ---------- data-mal-manga · DataMalManga ----------
    path('data-mal-manga/data/', v.DataMalMangaDataView.as_view(), name='data-mal-manga_data'),

    # ---------- data-mal-manga-character · DataMalMangaCharacter ----------
    path('data-mal-manga-character/data/', v.DataMalMangaCharacterDataView.as_view(), name='data-mal-manga-character_data'),

    # ---------- data-mal-manga-picture · DataMalMangaPicture ----------
    path('data-mal-manga-picture/data/', v.DataMalMangaPictureDataView.as_view(), name='data-mal-manga-picture_data'),

    # ---------- data-mal-person · DataMalPerson ----------
    path('data-mal-person/data/', v.DataMalPersonDataView.as_view(), name='data-mal-person_data'),

    # ---------- data-mal-person-picture · DataMalPersonPicture ----------
    path('data-mal-person-picture/data/', v.DataMalPersonPictureDataView.as_view(), name='data-mal-person-picture_data'),

    # ---------- demographic · Demographic ----------
    path('demographic/data/', v.DemographicDataView.as_view(), name='demographic_data'),
    path('demographic/select/', v.DemographicSelectView.as_view(), name='demographic_select'),

    # ---------- demographic-alias · DemographicAlias ----------
    path('demographic-alias/data/', v.DemographicAliasDataView.as_view(), name='demographic-alias_data'),
    path('demographic-alias/data/<str:tipo>/<str:pk>/', v.DemographicAliasDataView.as_view(), name='demographic-alias_data-by'),

    # ---------- genre · Genre ----------
    path('genre/data/', v.GenreDataView.as_view(), name='genre_data'),
    path('genre/select/', v.GenreSelectView.as_view(), name='genre_select'),

    # ---------- genre-alias · GenreAlias ----------
    path('genre-alias/data/', v.GenreAliasDataView.as_view(), name='genre-alias_data'),
    path('genre-alias/data/<str:tipo>/<str:pk>/', v.GenreAliasDataView.as_view(), name='genre-alias_data-by'),

    # ---------- manga · Manga ----------
    path('manga/data/', v.MangaDataView.as_view(), name='manga_data'),
    path('manga/data/<str:tipo>/<str:pk>/', v.MangaDataView.as_view(), name='manga_data-by'),
    path('manga/select/', v.MangaSelectView.as_view(), name='manga_select'),

    # ---------- manga-author · MangaAuthor ----------
    path('manga-author/data/', v.MangaAuthorDataView.as_view(), name='manga-author_data'),
    path('manga-author/data/<str:tipo>/<str:pk>/', v.MangaAuthorDataView.as_view(), name='manga-author_data-by'),
    path('manga-author/select/', v.MangaAuthorSelectView.as_view(), name='manga-author_select'),

    # ---------- manga-character · MangaCharacter ----------
    path('manga-character/data/', v.MangaCharacterDataView.as_view(), name='manga-character_data'),
    path('manga-character/data/<str:tipo>/<str:pk>/', v.MangaCharacterDataView.as_view(), name='manga-character_data-by'),
    path('manga-character/select/', v.MangaCharacterSelectView.as_view(), name='manga-character_select'),

    # ---------- manga-image · MangaImage ----------
    path('manga-image/data/', v.MangaImageDataView.as_view(), name='manga-image_data'),
    path('manga-image/data/<str:tipo>/<str:pk>/', v.MangaImageDataView.as_view(), name='manga-image_data-by'),
    path('manga-image/select/', v.MangaImageSelectView.as_view(), name='manga-image_select'),

    # ---------- manga-title · MangaTitle ----------
    path('manga-title/data/', v.MangaTitleDataView.as_view(), name='manga-title_data'),
    path('manga-title/data/<str:tipo>/<str:pk>/', v.MangaTitleDataView.as_view(), name='manga-title_data-by'),
    path('manga-title/select/', v.MangaTitleSelectView.as_view(), name='manga-title_select'),

    # ---------- person-mal · PersonMAL ----------
    path('person-mal/data/', v.PersonMALDataView.as_view(), name='person-mal_data'),
    path('person-mal/data/<str:tipo>/<str:pk>/', v.PersonMALDataView.as_view(), name='person-mal_data-by'),
    path('person-mal/select/', v.PersonMALSelectView.as_view(), name='person-mal_select'),

    # ---------- relation · Relation ----------
    path('relation/data/', v.RelationDataView.as_view(), name='relation_data'),
    path('relation/select/', v.RelationSelectView.as_view(), name='relation_select'),

    # ---------- otaku-role · Role ----------
    path('otaku-role/data/', v.RoleDataView.as_view(), name='otaku-role_data'),
    path('otaku-role/data/<str:tipo>/<str:pk>/', v.RoleDataView.as_view(), name='otaku-role_data-by'),
    path('otaku-role/select/', v.RoleSelectView.as_view(), name='otaku-role_select'),

    # ---------- source · Source ----------
    path('source/data/', v.SourceDataView.as_view(), name='source_data'),
    path('source/select/', v.SourceSelectView.as_view(), name='source_select'),

    # ---------- status · Status ----------
    path('status/data/', v.StatusDataView.as_view(), name='status_data'),
    path('status/select/', v.StatusSelectView.as_view(), name='status_select'),

    # ---------- theme · Theme ----------
    path('theme/data/', v.ThemeDataView.as_view(), name='theme_data'),
    path('theme/select/', v.ThemeSelectView.as_view(), name='theme_select'),

    # ---------- theme-alias · ThemeAlias ----------
    path('theme-alias/data/', v.ThemeAliasDataView.as_view(), name='theme-alias_data'),
    path('theme-alias/data/<str:tipo>/<str:pk>/', v.ThemeAliasDataView.as_view(), name='theme-alias_data-by'),

    # ---------- type · Type ----------
    path('type/data/', v.TypeDataView.as_view(), name='type_data'),
    path('type/select/', v.TypeSelectView.as_view(), name='type_select'),

    # ---------- year · Year ----------
    path('year/data/', v.YearDataView.as_view(), name='year_data'),
    path('year/select/', v.YearSelectView.as_view(), name='year_select'),

    # ---------- otaku-log · OtakuLog ----------
    path('otaku-log/data/', v.OtakuLogDataView.as_view(), name='otaku-log_data'),

    # ---------- vistas fijas ----------
    path('relation-anime-anime/data/', v.RelationAnimeAnimeDataView.as_view(), name='relation-anime-anime_data'),
    path('relation-anime-manga/data/', v.RelationAnimeMangaDataView.as_view(), name='relation-anime-manga_data'),
    path('relation-manga-anime/data/', v.RelationMangaAnimeDataView.as_view(), name='relation-manga-anime_data'),
    path('relation-manga-manga/data/', v.RelationMangaMangaDataView.as_view(), name='relation-manga-manga_data'),
]
