"""URLs del panel para otaku (sección «Otaku»): home + CRUD por entidad.

Rutas EXPLÍCITAS (estilo Hades): una `path()` por vista, con su `name=` editable.
Sin funciones que las generen. Se montan en el namespace `panel` desde core/panel_urls.py.

Rutas por entidad: list · [nuevo] · data (DataTables) · select (AJAX FK/M2M) ·
detail · editar · eliminar · accion (toggle is_active/is_staff/...).

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.otaku import views as v
from apps.otaku.views import v8_import as imp
from core.views import AdminImageActionView, AdminToggleView


urlpatterns = [
    path('', include('apps.otaku.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path('otaku/', v.OtakuHomeView.as_view(), name='otaku-home'),

    # ---------- anime · Anime ----------
    path('anime/', v.AnimeListView.as_view(), name='anime_list'),
    path('anime/create/', v.AnimeCreateView.as_view(), name='anime_create'),
    path('anime/<int:pk>/', v.AnimeDetailView.as_view(), name='anime_detail'),
    path('anime/<int:pk>/update/', v.AnimeUpdateView.as_view(), name='anime_update'),
    path('anime/<int:pk>/delete/', v.AnimeDeleteView.as_view(), name='anime_delete'),
    path('anime/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AnimeListView.model, entity='anime', label='anime', namespace='panel'), name='anime_toggle'),
    path('anime/<str:tipo>/<str:pk>/', v.AnimeListByView.as_view(), name='anime_by'),

    # ---------- anime-character · AnimeCharacter ----------
    path('anime-character/', v.AnimeCharacterListView.as_view(), name='anime-character_list'),
    path('anime-character/create/', v.AnimeCharacterCreateView.as_view(), name='anime-character_create'),
    path('anime-character/<int:pk>/', v.AnimeCharacterDetailView.as_view(), name='anime-character_detail'),
    path('anime-character/<int:pk>/update/', v.AnimeCharacterUpdateView.as_view(), name='anime-character_update'),
    path('anime-character/<int:pk>/delete/', v.AnimeCharacterDeleteView.as_view(), name='anime-character_delete'),
    path('anime-character/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AnimeCharacterListView.model, entity='anime-character', label='personaje', namespace='panel'), name='anime-character_toggle'),
    path('anime-character/<str:tipo>/<str:pk>/', v.AnimeCharacterListByView.as_view(), name='anime-character_by'),

    # ---------- anime-image · AnimeImage ----------
    path('anime-image/', v.AnimeImageListView.as_view(), name='anime-image_list'),
    path('anime-image/download/', v.AnimeImageDownloadView.as_view(), name='anime-image_download'),   # descargar pendientes (N o todas)
    path('anime-image/create/', v.AnimeImageCreateView.as_view(), name='anime-image_create'),
    path('anime-image/<int:pk>/', v.AnimeImageDetailView.as_view(), name='anime-image_detail'),
    path('anime-image/<int:pk>/update/', v.AnimeImageUpdateView.as_view(), name='anime-image_update'),
    path('anime-image/<int:pk>/delete/', v.AnimeImageDeleteView.as_view(), name='anime-image_delete'),
    path('anime-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AnimeImageListView.model, entity='anime-image', label='imagen', namespace='panel'), name='anime-image_toggle'),
    path('anime-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.AnimeImageListView.model), name='anime-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('anime-image/<str:tipo>/<str:pk>/', v.AnimeImageListByView.as_view(), name='anime-image_by'),

    # ---------- anime-song · AnimeSong ----------
    path('anime-song/', v.AnimeSongListView.as_view(), name='anime-song_list'),
    path('anime-song/create/', v.AnimeSongCreateView.as_view(), name='anime-song_create'),
    path('anime-song/<int:pk>/', v.AnimeSongDetailView.as_view(), name='anime-song_detail'),
    path('anime-song/<int:pk>/update/', v.AnimeSongUpdateView.as_view(), name='anime-song_update'),
    path('anime-song/<int:pk>/delete/', v.AnimeSongDeleteView.as_view(), name='anime-song_delete'),
    path('anime-song/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AnimeSongListView.model, entity='anime-song', label='canción', namespace='panel'), name='anime-song_toggle'),
    path('anime-song/<str:tipo>/<str:pk>/', v.AnimeSongListByView.as_view(), name='anime-song_by'),

    # ---------- anime-staff · AnimeStaff ----------
    path('anime-staff/', v.AnimeStaffListView.as_view(), name='anime-staff_list'),
    path('anime-staff/create/', v.AnimeStaffCreateView.as_view(), name='anime-staff_create'),
    path('anime-staff/<int:pk>/', v.AnimeStaffDetailView.as_view(), name='anime-staff_detail'),
    path('anime-staff/<int:pk>/update/', v.AnimeStaffUpdateView.as_view(), name='anime-staff_update'),
    path('anime-staff/<int:pk>/delete/', v.AnimeStaffDeleteView.as_view(), name='anime-staff_delete'),
    path('anime-staff/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AnimeStaffListView.model, entity='anime-staff', label='staff', namespace='panel'), name='anime-staff_toggle'),
    path('anime-staff/<str:tipo>/<str:pk>/', v.AnimeStaffListByView.as_view(), name='anime-staff_by'),

    # ---------- anime-title · AnimeTitle ----------
    path('anime-title/', v.AnimeTitleListView.as_view(), name='anime-title_list'),
    path('anime-title/create/', v.AnimeTitleCreateView.as_view(), name='anime-title_create'),
    path('anime-title/<int:pk>/', v.AnimeTitleDetailView.as_view(), name='anime-title_detail'),
    path('anime-title/<int:pk>/update/', v.AnimeTitleUpdateView.as_view(), name='anime-title_update'),
    path('anime-title/<int:pk>/delete/', v.AnimeTitleDeleteView.as_view(), name='anime-title_delete'),
    path('anime-title/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.AnimeTitleListView.model, entity='anime-title', label='título', namespace='panel'), name='anime-title_toggle'),
    path('anime-title/<str:tipo>/<str:pk>/', v.AnimeTitleListByView.as_view(), name='anime-title_by'),

    # ---------- character · Character ----------
    path('character/', v.CharacterListView.as_view(), name='character_list'),
    path('character/create/', v.CharacterCreateView.as_view(), name='character_create'),
    path('character/<int:pk>/', v.CharacterDetailView.as_view(), name='character_detail'),
    path('character/<int:pk>/update/', v.CharacterUpdateView.as_view(), name='character_update'),
    path('character/<int:pk>/delete/', v.CharacterDeleteView.as_view(), name='character_delete'),
    path('character/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CharacterListView.model, entity='character', label='personaje', namespace='panel'), name='character_toggle'),
    path('character/<str:tipo>/<str:pk>/', v.CharacterListByView.as_view(), name='character_by'),

    # ---------- character-image · CharacterImage ----------
    path('character-image/', v.CharacterImageListView.as_view(), name='character-image_list'),
    path('character-image/download/', v.CharacterImageDownloadView.as_view(), name='character-image_download'),   # descargar pendientes (N o todas)
    path('character-image/create/', v.CharacterImageCreateView.as_view(), name='character-image_create'),
    path('character-image/<int:pk>/', v.CharacterImageDetailView.as_view(), name='character-image_detail'),
    path('character-image/<int:pk>/update/', v.CharacterImageUpdateView.as_view(), name='character-image_update'),
    path('character-image/<int:pk>/delete/', v.CharacterImageDeleteView.as_view(), name='character-image_delete'),
    path('character-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CharacterImageListView.model, entity='character-image', label='imagen', namespace='panel'), name='character-image_toggle'),
    path('character-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.CharacterImageListView.model), name='character-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('character-image/<str:tipo>/<str:pk>/', v.CharacterImageListByView.as_view(), name='character-image_by'),

    # ---------- character-nickname · CharacterNickname ----------
    path('character-nickname/', v.CharacterNicknameListView.as_view(), name='character-nickname_list'),
    path('character-nickname/create/', v.CharacterNicknameCreateView.as_view(), name='character-nickname_create'),
    path('character-nickname/<int:pk>/', v.CharacterNicknameDetailView.as_view(), name='character-nickname_detail'),
    path('character-nickname/<int:pk>/update/', v.CharacterNicknameUpdateView.as_view(), name='character-nickname_update'),
    path('character-nickname/<int:pk>/delete/', v.CharacterNicknameDeleteView.as_view(), name='character-nickname_delete'),
    path('character-nickname/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CharacterNicknameListView.model, entity='character-nickname', label='apodo', namespace='panel'), name='character-nickname_toggle'),
    path('character-nickname/<str:tipo>/<str:pk>/', v.CharacterNicknameListByView.as_view(), name='character-nickname_by'),

    # ---------- character-voice · CharacterVoice ----------
    path('character-voice/', v.CharacterVoiceListView.as_view(), name='character-voice_list'),
    path('character-voice/create/', v.CharacterVoiceCreateView.as_view(), name='character-voice_create'),
    path('character-voice/<int:pk>/', v.CharacterVoiceDetailView.as_view(), name='character-voice_detail'),
    path('character-voice/<int:pk>/update/', v.CharacterVoiceUpdateView.as_view(), name='character-voice_update'),
    path('character-voice/<int:pk>/delete/', v.CharacterVoiceDeleteView.as_view(), name='character-voice_delete'),
    path('character-voice/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CharacterVoiceListView.model, entity='character-voice', label='voz', namespace='panel'), name='character-voice_toggle'),
    path('character-voice/<str:tipo>/<str:pk>/', v.CharacterVoiceListByView.as_view(), name='character-voice_by'),


    # ---------- vistas FIJAS de Otaku sobre tablas de otras apps: imágenes con ficha MAL ----------
    path('company-image-mal/', v.CompanyImageMalListView.as_view(), name='company-image-mal_list'),
    path('company-image-mal/download/', v.CompanyImageMalDownloadView.as_view(), name='company-image-mal_download'),
    path('person-image-mal/', v.PersonImageMalListView.as_view(), name='person-image-mal_list'),
    path('person-image-mal/download/', v.PersonImageMalDownloadView.as_view(), name='person-image-mal_download'),

    # ---------- company-mal · CompanyMAL ----------
    path('company-mal/', v.CompanyMALListView.as_view(), name='company-mal_list'),
    path('company-mal/create/', v.CompanyMALCreateView.as_view(), name='company-mal_create'),
    path('company-mal/link/', v.CompanyMALLinkView.as_view(), name='company-mal_link'),   # compañía EXISTENTE: se elige en el select
    path('company-mal/<int:pk>/', v.CompanyMALDetailView.as_view(), name='company-mal_detail'),
    path('company-mal/<int:pk>/update/', v.CompanyMALUpdateView.as_view(), name='company-mal_update'),
    path('company-mal/<int:pk>/delete/', v.CompanyMALDeleteView.as_view(), name='company-mal_delete'),
    path('company-mal/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CompanyMALListView.model, entity='company-mal', label='compañía (MAL)', namespace='panel'), name='company-mal_toggle'),
    path('company-mal/add/<int:company_pk>/', v.CompanyMALLinkView.as_view(), name='company-mal_add'),   # la misma, con la compañía fija

    # ---------- data-anilist-anime · DataAnilistAnime ----------
    path('data-anilist-anime/', v.DataAnilistAnimeListView.as_view(), name='data-anilist-anime_list'),
    path('data-anilist-anime/create/', v.DataAnilistAnimeCreateView.as_view(), name='data-anilist-anime_create'),
    path('data-anilist-anime/export/', imp.DataAnilistAnimeExportView.as_view(), name='data-anilist-anime_export'),   # «Generar dump»
    path('data-anilist-anime/<int:pk>/', v.DataAnilistAnimeDetailView.as_view(), name='data-anilist-anime_detail'),
    path('data-anilist-anime/<int:pk>/update/', v.DataAnilistAnimeUpdateView.as_view(), name='data-anilist-anime_update'),
    path('data-anilist-anime/<int:pk>/delete/', v.DataAnilistAnimeDeleteView.as_view(), name='data-anilist-anime_delete'),
    # ---------- data-anilist-character · DataAnilistCharacter ----------
    path('data-anilist-character/', v.DataAnilistCharacterListView.as_view(), name='data-anilist-character_list'),
    path('data-anilist-character/create/', v.DataAnilistCharacterCreateView.as_view(), name='data-anilist-character_create'),
    path('data-anilist-character/export/', imp.DataAnilistCharacterExportView.as_view(), name='data-anilist-character_export'),   # «Generar dump»
    path('data-anilist-character/<int:pk>/', v.DataAnilistCharacterDetailView.as_view(), name='data-anilist-character_detail'),
    path('data-anilist-character/<int:pk>/update/', v.DataAnilistCharacterUpdateView.as_view(), name='data-anilist-character_update'),
    path('data-anilist-character/<int:pk>/delete/', v.DataAnilistCharacterDeleteView.as_view(), name='data-anilist-character_delete'),
    # ---------- data-anilist-manga · DataAnilistManga ----------
    path('data-anilist-manga/', v.DataAnilistMangaListView.as_view(), name='data-anilist-manga_list'),
    path('data-anilist-manga/create/', v.DataAnilistMangaCreateView.as_view(), name='data-anilist-manga_create'),
    path('data-anilist-manga/export/', imp.DataAnilistMangaExportView.as_view(), name='data-anilist-manga_export'),   # «Generar dump»
    path('data-anilist-manga/<int:pk>/', v.DataAnilistMangaDetailView.as_view(), name='data-anilist-manga_detail'),
    path('data-anilist-manga/<int:pk>/update/', v.DataAnilistMangaUpdateView.as_view(), name='data-anilist-manga_update'),
    path('data-anilist-manga/<int:pk>/delete/', v.DataAnilistMangaDeleteView.as_view(), name='data-anilist-manga_delete'),
    # ---------- data-anilist-person · DataAnilistPerson ----------
    path('data-anilist-person/', v.DataAnilistPersonListView.as_view(), name='data-anilist-person_list'),
    path('data-anilist-person/create/', v.DataAnilistPersonCreateView.as_view(), name='data-anilist-person_create'),
    path('data-anilist-person/export/', imp.DataAnilistPersonExportView.as_view(), name='data-anilist-person_export'),   # «Generar dump»
    path('data-anilist-person/<int:pk>/', v.DataAnilistPersonDetailView.as_view(), name='data-anilist-person_detail'),
    path('data-anilist-person/<int:pk>/update/', v.DataAnilistPersonUpdateView.as_view(), name='data-anilist-person_update'),
    path('data-anilist-person/<int:pk>/delete/', v.DataAnilistPersonDeleteView.as_view(), name='data-anilist-person_delete'),

    # ---------- data-mal-anime · DataMalAnime ----------
    path('data-mal-anime/', v.DataMalAnimeListView.as_view(), name='data-mal-anime_list'),
    path('data-mal-anime/create/', v.DataMalAnimeCreateView.as_view(), name='data-mal-anime_create'),
    path('data-mal-anime/export/', imp.DataMalAnimeExportView.as_view(), name='data-mal-anime_export'),   # «Generar dump»
    path('data-mal-anime/<int:pk>/', v.DataMalAnimeDetailView.as_view(), name='data-mal-anime_detail'),
    path('data-mal-anime/<int:pk>/update/', v.DataMalAnimeUpdateView.as_view(), name='data-mal-anime_update'),
    path('data-mal-anime/<int:pk>/delete/', v.DataMalAnimeDeleteView.as_view(), name='data-mal-anime_delete'),

    # ---------- data-mal-anime-character · DataMalAnimeCharacter ----------
    path('data-mal-anime-character/', v.DataMalAnimeCharacterListView.as_view(), name='data-mal-anime-character_list'),
    path('data-mal-anime-character/create/', v.DataMalAnimeCharacterCreateView.as_view(), name='data-mal-anime-character_create'),
    path('data-mal-anime-character/<int:pk>/', v.DataMalAnimeCharacterDetailView.as_view(), name='data-mal-anime-character_detail'),
    path('data-mal-anime-character/<int:pk>/update/', v.DataMalAnimeCharacterUpdateView.as_view(), name='data-mal-anime-character_update'),
    path('data-mal-anime-character/<int:pk>/delete/', v.DataMalAnimeCharacterDeleteView.as_view(), name='data-mal-anime-character_delete'),

    # ---------- data-mal-anime-picture · DataMalAnimePicture ----------
    path('data-mal-anime-picture/', v.DataMalAnimePictureListView.as_view(), name='data-mal-anime-picture_list'),
    path('data-mal-anime-picture/create/', v.DataMalAnimePictureCreateView.as_view(), name='data-mal-anime-picture_create'),
    path('data-mal-anime-picture/<int:pk>/', v.DataMalAnimePictureDetailView.as_view(), name='data-mal-anime-picture_detail'),
    path('data-mal-anime-picture/<int:pk>/update/', v.DataMalAnimePictureUpdateView.as_view(), name='data-mal-anime-picture_update'),
    path('data-mal-anime-picture/<int:pk>/delete/', v.DataMalAnimePictureDeleteView.as_view(), name='data-mal-anime-picture_delete'),

    # ---------- data-mal-anime-staff · DataMalAnimeStaff ----------
    path('data-mal-anime-staff/', v.DataMalAnimeStaffListView.as_view(), name='data-mal-anime-staff_list'),
    path('data-mal-anime-staff/create/', v.DataMalAnimeStaffCreateView.as_view(), name='data-mal-anime-staff_create'),
    path('data-mal-anime-staff/<int:pk>/', v.DataMalAnimeStaffDetailView.as_view(), name='data-mal-anime-staff_detail'),
    path('data-mal-anime-staff/<int:pk>/update/', v.DataMalAnimeStaffUpdateView.as_view(), name='data-mal-anime-staff_update'),
    path('data-mal-anime-staff/<int:pk>/delete/', v.DataMalAnimeStaffDeleteView.as_view(), name='data-mal-anime-staff_delete'),

    # ---------- data-mal-character · DataMalCharacter ----------
    path('data-mal-character/', v.DataMalCharacterListView.as_view(), name='data-mal-character_list'),
    path('data-mal-character/create/', v.DataMalCharacterCreateView.as_view(), name='data-mal-character_create'),
    path('data-mal-character/export/', imp.DataMalCharacterExportView.as_view(), name='data-mal-character_export'),   # «Generar dump»
    path('data-mal-character/<int:pk>/', v.DataMalCharacterDetailView.as_view(), name='data-mal-character_detail'),
    path('data-mal-character/<int:pk>/update/', v.DataMalCharacterUpdateView.as_view(), name='data-mal-character_update'),
    path('data-mal-character/<int:pk>/delete/', v.DataMalCharacterDeleteView.as_view(), name='data-mal-character_delete'),

    # ---------- data-mal-character-picture · DataMalCharacterPicture ----------
    path('data-mal-character-picture/', v.DataMalCharacterPictureListView.as_view(), name='data-mal-character-picture_list'),
    path('data-mal-character-picture/create/', v.DataMalCharacterPictureCreateView.as_view(), name='data-mal-character-picture_create'),
    path('data-mal-character-picture/<int:pk>/', v.DataMalCharacterPictureDetailView.as_view(), name='data-mal-character-picture_detail'),
    path('data-mal-character-picture/<int:pk>/update/', v.DataMalCharacterPictureUpdateView.as_view(), name='data-mal-character-picture_update'),
    path('data-mal-character-picture/<int:pk>/delete/', v.DataMalCharacterPictureDeleteView.as_view(), name='data-mal-character-picture_delete'),

    # ---------- data-mal-manga · DataMalManga ----------
    path('data-mal-manga/', v.DataMalMangaListView.as_view(), name='data-mal-manga_list'),
    path('data-mal-manga/create/', v.DataMalMangaCreateView.as_view(), name='data-mal-manga_create'),
    path('data-mal-manga/export/', imp.DataMalMangaExportView.as_view(), name='data-mal-manga_export'),   # «Generar dump»
    path('data-mal-manga/<int:pk>/', v.DataMalMangaDetailView.as_view(), name='data-mal-manga_detail'),
    path('data-mal-manga/<int:pk>/update/', v.DataMalMangaUpdateView.as_view(), name='data-mal-manga_update'),
    path('data-mal-manga/<int:pk>/delete/', v.DataMalMangaDeleteView.as_view(), name='data-mal-manga_delete'),

    # ---------- data-mal-manga-character · DataMalMangaCharacter ----------
    path('data-mal-manga-character/', v.DataMalMangaCharacterListView.as_view(), name='data-mal-manga-character_list'),
    path('data-mal-manga-character/create/', v.DataMalMangaCharacterCreateView.as_view(), name='data-mal-manga-character_create'),
    path('data-mal-manga-character/<int:pk>/', v.DataMalMangaCharacterDetailView.as_view(), name='data-mal-manga-character_detail'),
    path('data-mal-manga-character/<int:pk>/update/', v.DataMalMangaCharacterUpdateView.as_view(), name='data-mal-manga-character_update'),
    path('data-mal-manga-character/<int:pk>/delete/', v.DataMalMangaCharacterDeleteView.as_view(), name='data-mal-manga-character_delete'),

    # ---------- data-mal-manga-picture · DataMalMangaPicture ----------
    path('data-mal-manga-picture/', v.DataMalMangaPictureListView.as_view(), name='data-mal-manga-picture_list'),
    path('data-mal-manga-picture/create/', v.DataMalMangaPictureCreateView.as_view(), name='data-mal-manga-picture_create'),
    path('data-mal-manga-picture/<int:pk>/', v.DataMalMangaPictureDetailView.as_view(), name='data-mal-manga-picture_detail'),
    path('data-mal-manga-picture/<int:pk>/update/', v.DataMalMangaPictureUpdateView.as_view(), name='data-mal-manga-picture_update'),
    path('data-mal-manga-picture/<int:pk>/delete/', v.DataMalMangaPictureDeleteView.as_view(), name='data-mal-manga-picture_delete'),

    # ---------- data-mal-person · DataMalPerson ----------
    path('data-mal-person/', v.DataMalPersonListView.as_view(), name='data-mal-person_list'),
    path('data-mal-person/create/', v.DataMalPersonCreateView.as_view(), name='data-mal-person_create'),
    path('data-mal-person/export/', imp.DataMalPersonExportView.as_view(), name='data-mal-person_export'),   # «Generar dump»
    path('data-mal-person/<int:pk>/', v.DataMalPersonDetailView.as_view(), name='data-mal-person_detail'),
    path('data-mal-person/<int:pk>/update/', v.DataMalPersonUpdateView.as_view(), name='data-mal-person_update'),
    path('data-mal-person/<int:pk>/delete/', v.DataMalPersonDeleteView.as_view(), name='data-mal-person_delete'),

    # ---------- data-mal-person-picture · DataMalPersonPicture ----------
    path('data-mal-person-picture/', v.DataMalPersonPictureListView.as_view(), name='data-mal-person-picture_list'),
    path('data-mal-person-picture/create/', v.DataMalPersonPictureCreateView.as_view(), name='data-mal-person-picture_create'),
    path('data-mal-person-picture/<int:pk>/', v.DataMalPersonPictureDetailView.as_view(), name='data-mal-person-picture_detail'),
    path('data-mal-person-picture/<int:pk>/update/', v.DataMalPersonPictureUpdateView.as_view(), name='data-mal-person-picture_update'),
    path('data-mal-person-picture/<int:pk>/delete/', v.DataMalPersonPictureDeleteView.as_view(), name='data-mal-person-picture_delete'),

    # ---------- demographic · Demographic ----------
    path('demographic/', v.DemographicListView.as_view(), name='demographic_list'),
    path('demographic/create/', v.DemographicCreateView.as_view(), name='demographic_create'),
    path('demographic/<int:pk>/', v.DemographicDetailView.as_view(), name='demographic_detail'),
    path('demographic/<int:pk>/update/', v.DemographicUpdateView.as_view(), name='demographic_update'),
    path('demographic/<int:pk>/delete/', v.DemographicDeleteView.as_view(), name='demographic_delete'),
    path('demographic/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.DemographicListView.model, entity='demographic', label='demografía', namespace='panel'), name='demographic_toggle'),

    # ---------- demographic-alias · DemographicAlias ----------
    path('demographic-alias/', v.DemographicAliasListView.as_view(), name='demographic-alias_list'),
    path('demographic-alias/create/', v.DemographicAliasCreateView.as_view(), name='demographic-alias_create'),
    path('demographic-alias/<int:pk>/', v.DemographicAliasDetailView.as_view(), name='demographic-alias_detail'),
    path('demographic-alias/<int:pk>/update/', v.DemographicAliasUpdateView.as_view(), name='demographic-alias_update'),
    path('demographic-alias/<int:pk>/delete/', v.DemographicAliasDeleteView.as_view(), name='demographic-alias_delete'),
    path('demographic-alias/<str:tipo>/<str:pk>/', v.DemographicAliasListByView.as_view(), name='demographic-alias_by'),

    # ---------- genre · Genre ----------
    path('genre/', v.GenreListView.as_view(), name='genre_list'),
    path('genre/create/', v.GenreCreateView.as_view(), name='genre_create'),
    path('genre/<int:pk>/', v.GenreDetailView.as_view(), name='genre_detail'),
    path('genre/<int:pk>/update/', v.GenreUpdateView.as_view(), name='genre_update'),
    path('genre/<int:pk>/delete/', v.GenreDeleteView.as_view(), name='genre_delete'),
    path('genre/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.GenreListView.model, entity='genre', label='género', namespace='panel'), name='genre_toggle'),

    # ---------- genre-alias · GenreAlias ----------
    path('genre-alias/', v.GenreAliasListView.as_view(), name='genre-alias_list'),
    path('genre-alias/create/', v.GenreAliasCreateView.as_view(), name='genre-alias_create'),
    path('genre-alias/<int:pk>/', v.GenreAliasDetailView.as_view(), name='genre-alias_detail'),
    path('genre-alias/<int:pk>/update/', v.GenreAliasUpdateView.as_view(), name='genre-alias_update'),
    path('genre-alias/<int:pk>/delete/', v.GenreAliasDeleteView.as_view(), name='genre-alias_delete'),
    path('genre-alias/<str:tipo>/<str:pk>/', v.GenreAliasListByView.as_view(), name='genre-alias_by'),

    # ---------- manga · Manga ----------
    path('manga/', v.MangaListView.as_view(), name='manga_list'),
    path('manga/create/', v.MangaCreateView.as_view(), name='manga_create'),
    path('manga/<int:pk>/', v.MangaDetailView.as_view(), name='manga_detail'),
    path('manga/<int:pk>/update/', v.MangaUpdateView.as_view(), name='manga_update'),
    path('manga/<int:pk>/delete/', v.MangaDeleteView.as_view(), name='manga_delete'),
    path('manga/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MangaListView.model, entity='manga', label='manga', namespace='panel'), name='manga_toggle'),
    path('manga/<str:tipo>/<str:pk>/', v.MangaListByView.as_view(), name='manga_by'),

    # ---------- manga-author · MangaAuthor ----------
    path('manga-author/', v.MangaAuthorListView.as_view(), name='manga-author_list'),
    path('manga-author/create/', v.MangaAuthorCreateView.as_view(), name='manga-author_create'),
    path('manga-author/<int:pk>/', v.MangaAuthorDetailView.as_view(), name='manga-author_detail'),
    path('manga-author/<int:pk>/update/', v.MangaAuthorUpdateView.as_view(), name='manga-author_update'),
    path('manga-author/<int:pk>/delete/', v.MangaAuthorDeleteView.as_view(), name='manga-author_delete'),
    path('manga-author/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MangaAuthorListView.model, entity='manga-author', label='autor', namespace='panel'), name='manga-author_toggle'),
    path('manga-author/<str:tipo>/<str:pk>/', v.MangaAuthorListByView.as_view(), name='manga-author_by'),

    # ---------- manga-character · MangaCharacter ----------
    path('manga-character/', v.MangaCharacterListView.as_view(), name='manga-character_list'),
    path('manga-character/create/', v.MangaCharacterCreateView.as_view(), name='manga-character_create'),
    path('manga-character/<int:pk>/', v.MangaCharacterDetailView.as_view(), name='manga-character_detail'),
    path('manga-character/<int:pk>/update/', v.MangaCharacterUpdateView.as_view(), name='manga-character_update'),
    path('manga-character/<int:pk>/delete/', v.MangaCharacterDeleteView.as_view(), name='manga-character_delete'),
    path('manga-character/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MangaCharacterListView.model, entity='manga-character', label='personaje', namespace='panel'), name='manga-character_toggle'),
    path('manga-character/<str:tipo>/<str:pk>/', v.MangaCharacterListByView.as_view(), name='manga-character_by'),

    # ---------- manga-image · MangaImage ----------
    path('manga-image/', v.MangaImageListView.as_view(), name='manga-image_list'),
    path('manga-image/download/', v.MangaImageDownloadView.as_view(), name='manga-image_download'),   # descargar pendientes (N o todas)
    path('manga-image/create/', v.MangaImageCreateView.as_view(), name='manga-image_create'),
    path('manga-image/<int:pk>/', v.MangaImageDetailView.as_view(), name='manga-image_detail'),
    path('manga-image/<int:pk>/update/', v.MangaImageUpdateView.as_view(), name='manga-image_update'),
    path('manga-image/<int:pk>/delete/', v.MangaImageDeleteView.as_view(), name='manga-image_delete'),
    path('manga-image/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MangaImageListView.model, entity='manga-image', label='imagen', namespace='panel'), name='manga-image_toggle'),
    path('manga-image/<int:pk>/imagen/<str:accion>/', AdminImageActionView.as_view(model=v.MangaImageListView.model), name='manga-image_image-action'),   # descargar / subir a la nube ESTA imagen
    path('manga-image/<str:tipo>/<str:pk>/', v.MangaImageListByView.as_view(), name='manga-image_by'),

    # ---------- manga-title · MangaTitle ----------
    path('manga-title/', v.MangaTitleListView.as_view(), name='manga-title_list'),
    path('manga-title/create/', v.MangaTitleCreateView.as_view(), name='manga-title_create'),
    path('manga-title/<int:pk>/', v.MangaTitleDetailView.as_view(), name='manga-title_detail'),
    path('manga-title/<int:pk>/update/', v.MangaTitleUpdateView.as_view(), name='manga-title_update'),
    path('manga-title/<int:pk>/delete/', v.MangaTitleDeleteView.as_view(), name='manga-title_delete'),
    path('manga-title/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.MangaTitleListView.model, entity='manga-title', label='título', namespace='panel'), name='manga-title_toggle'),
    path('manga-title/<str:tipo>/<str:pk>/', v.MangaTitleListByView.as_view(), name='manga-title_by'),

    # ---------- person-mal · PersonMAL ----------
    path('person-mal/', v.PersonMALListView.as_view(), name='person-mal_list'),
    path('person-mal/create/', v.PersonMALCreateView.as_view(), name='person-mal_create'),
    path('person-mal/link/', v.PersonMALLinkView.as_view(), name='person-mal_link'),   # persona EXISTENTE: se elige en el select
    path('person-mal/<int:pk>/', v.PersonMALDetailView.as_view(), name='person-mal_detail'),
    path('person-mal/<int:pk>/update/', v.PersonMALUpdateView.as_view(), name='person-mal_update'),
    path('person-mal/<int:pk>/delete/', v.PersonMALDeleteView.as_view(), name='person-mal_delete'),
    path('person-mal/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.PersonMALListView.model, entity='person-mal', label='persona (MAL)', namespace='panel'), name='person-mal_toggle'),
    path('person-mal/add/<int:person_pk>/', v.PersonMALLinkView.as_view(), name='person-mal_add'),   # la misma, con la persona fija
    path('person-mal/<str:tipo>/<str:pk>/', v.PersonMALListByView.as_view(), name='person-mal_by'),

    # ---------- relation · Relation ----------
    path('relation/', v.RelationListView.as_view(), name='relation_list'),
    path('relation/create/', v.RelationCreateView.as_view(), name='relation_create'),
    path('relation/<int:pk>/', v.RelationDetailView.as_view(), name='relation_detail'),
    path('relation/<int:pk>/update/', v.RelationUpdateView.as_view(), name='relation_update'),
    path('relation/<int:pk>/delete/', v.RelationDeleteView.as_view(), name='relation_delete'),
    path('relation/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RelationListView.model, entity='relation', label='relación', namespace='panel'), name='relation_toggle'),

    # ---------- otaku-role · Role ----------
    path('otaku-role/', v.RoleListView.as_view(), name='otaku-role_list'),
    path('otaku-role/create/', v.RoleCreateView.as_view(), name='otaku-role_create'),
    path('otaku-role/<int:pk>/', v.RoleDetailView.as_view(), name='otaku-role_detail'),
    path('otaku-role/<int:pk>/update/', v.RoleUpdateView.as_view(), name='otaku-role_update'),
    path('otaku-role/<int:pk>/delete/', v.RoleDeleteView.as_view(), name='otaku-role_delete'),
    path('otaku-role/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.RoleListView.model, entity='otaku-role', label='rol', namespace='panel'), name='otaku-role_toggle'),
    path('otaku-role/<str:tipo>/<str:pk>/', v.RoleListByView.as_view(), name='otaku-role_by'),

    # ---------- source · Source ----------
    path('source/', v.SourceListView.as_view(), name='source_list'),
    path('source/create/', v.SourceCreateView.as_view(), name='source_create'),
    path('source/<int:pk>/', v.SourceDetailView.as_view(), name='source_detail'),
    path('source/<int:pk>/update/', v.SourceUpdateView.as_view(), name='source_update'),
    path('source/<int:pk>/delete/', v.SourceDeleteView.as_view(), name='source_delete'),
    path('source/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.SourceListView.model, entity='source', label='fuente', namespace='panel'), name='source_toggle'),

    # ---------- status · Status ----------
    path('status/', v.StatusListView.as_view(), name='status_list'),
    path('status/create/', v.StatusCreateView.as_view(), name='status_create'),
    path('status/<int:pk>/', v.StatusDetailView.as_view(), name='status_detail'),
    path('status/<int:pk>/update/', v.StatusUpdateView.as_view(), name='status_update'),
    path('status/<int:pk>/delete/', v.StatusDeleteView.as_view(), name='status_delete'),
    path('status/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.StatusListView.model, entity='status', label='estado', namespace='panel'), name='status_toggle'),

    # ---------- theme · Theme ----------
    path('theme/', v.ThemeListView.as_view(), name='theme_list'),
    path('theme/create/', v.ThemeCreateView.as_view(), name='theme_create'),
    path('theme/<int:pk>/', v.ThemeDetailView.as_view(), name='theme_detail'),
    path('theme/<int:pk>/update/', v.ThemeUpdateView.as_view(), name='theme_update'),
    path('theme/<int:pk>/delete/', v.ThemeDeleteView.as_view(), name='theme_delete'),
    path('theme/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ThemeListView.model, entity='theme', label='tema', namespace='panel'), name='theme_toggle'),

    # ---------- theme-alias · ThemeAlias ----------
    path('theme-alias/', v.ThemeAliasListView.as_view(), name='theme-alias_list'),
    path('theme-alias/create/', v.ThemeAliasCreateView.as_view(), name='theme-alias_create'),
    path('theme-alias/<int:pk>/', v.ThemeAliasDetailView.as_view(), name='theme-alias_detail'),
    path('theme-alias/<int:pk>/update/', v.ThemeAliasUpdateView.as_view(), name='theme-alias_update'),
    path('theme-alias/<int:pk>/delete/', v.ThemeAliasDeleteView.as_view(), name='theme-alias_delete'),
    path('theme-alias/<str:tipo>/<str:pk>/', v.ThemeAliasListByView.as_view(), name='theme-alias_by'),

    # ---------- type · Type ----------
    path('type/', v.TypeListView.as_view(), name='type_list'),
    path('type/create/', v.TypeCreateView.as_view(), name='type_create'),
    path('type/<int:pk>/', v.TypeDetailView.as_view(), name='type_detail'),
    path('type/<int:pk>/update/', v.TypeUpdateView.as_view(), name='type_update'),
    path('type/<int:pk>/delete/', v.TypeDeleteView.as_view(), name='type_delete'),
    path('type/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.TypeListView.model, entity='type', label='tipo', namespace='panel'), name='type_toggle'),

    # ---------- year · Year ----------
    path('year/', v.YearListView.as_view(), name='year_list'),
    path('year/create/', v.YearCreateView.as_view(), name='year_create'),
    path('year/<int:pk>/', v.YearDetailView.as_view(), name='year_detail'),
    path('year/<int:pk>/update/', v.YearUpdateView.as_view(), name='year_update'),
    path('year/<int:pk>/delete/', v.YearDeleteView.as_view(), name='year_delete'),
    path('year/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.YearListView.model, entity='year', label='año', namespace='panel'), name='year_toggle'),

    # vistas FIJAS de relacion (una URL por cada una)
    path('relation-anime-anime/', v.RelationAnimeAnimeListView.as_view(), name='relation-anime-anime_list'),
    path('relation-anime-manga/', v.RelationAnimeMangaListView.as_view(), name='relation-anime-manga_list'),
    path('relation-manga-anime/', v.RelationMangaAnimeListView.as_view(), name='relation-manga-anime_list'),
    path('relation-manga-manga/', v.RelationMangaMangaListView.as_view(), name='relation-manga-manga_list'),
    # ---------- lanzadores AniList · procesar y cargar dumps de MAL ----------
    # Lanzadores MAL: UNO por tipo y formulario. El individual conserva el nombre de siempre (mal-anime…).
    # Lanzadores AniList: UNA vista por tabla Data (por id · por rango de ids · por páginas).
    path("anilist/anime/", imp.LoadAnilistDataAnimeView.as_view(), name="anilist-anime"),
    path("anilist/character/", imp.LoadAnilistDataCharacterView.as_view(), name="anilist-character"),
    path("anilist/manga/", imp.LoadAnilistDataMangaView.as_view(), name="anilist-manga"),
    path("anilist/person/", imp.LoadAnilistDataPersonView.as_view(), name="anilist-person"),
    path("mal/process/anime/", imp.ProcessMalAnimeView.as_view(), name="process-mal-anime"),
    path("mal/process/character/", imp.ProcessMalCharacterView.as_view(), name="process-mal-character"),
    path("mal/process/manga/", imp.ProcessMalMangaView.as_view(), name="process-mal-manga"),
    path("mal/process/person/", imp.ProcessMalPersonView.as_view(), name="process-mal-person"),
    path("mal/procesar/", imp.MALProcessPendingView.as_view(), name="mal-procesar"),   # POST «Procesar pendientes»
    # Dumps de MAL: dos vistas por tipo (formulario → resumen), como los tags de VNDB.
    path("mal/dump/anime/", imp.AnimeMALLoadView.as_view(), name="dump-mal-anime"),
    path("mal/dump/anime/resumen/", imp.AnimeMALSummaryView.as_view(), name="dump-mal-anime-summary"),
    path("mal/dump/manga/", imp.MangaMALLoadView.as_view(), name="dump-mal-manga"),
    path("mal/dump/manga/resumen/", imp.MangaMALSummaryView.as_view(), name="dump-mal-manga-summary"),
    path("mal/dump/character/", imp.CharacterMALLoadView.as_view(), name="dump-mal-character"),
    path("mal/dump/character/resumen/", imp.CharacterMALSummaryView.as_view(), name="dump-mal-character-summary"),
    path("mal/dump/company/", imp.CompanyMALLoadView.as_view(), name="dump-mal-company"),
    path("mal/dump/company/resumen/", imp.CompanyMALSummaryView.as_view(), name="dump-mal-company-summary"),
    path("mal/dump/person/", imp.PersonMALLoadView.as_view(), name="dump-mal-person"),
    path("mal/dump/person/resumen/", imp.PersonMALSummaryView.as_view(), name="dump-mal-person-summary"),

    # ---------- otaku-log · OtakuLog ----------
    path('otaku-log/', v.OtakuLogListView.as_view(), name='otaku-log_list'),
    path('otaku-log/create/', v.OtakuLogCreateView.as_view(), name='otaku-log_create'),
    path('otaku-log/<int:pk>/', v.OtakuLogDetailView.as_view(), name='otaku-log_detail'),
    path('otaku-log/<int:pk>/update/', v.OtakuLogUpdateView.as_view(), name='otaku-log_update'),
    path('otaku-log/<int:pk>/delete/', v.OtakuLogDeleteView.as_view(), name='otaku-log_delete'),
]
