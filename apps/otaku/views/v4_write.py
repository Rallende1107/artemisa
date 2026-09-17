"""otaku · ESCRITURA de gestión: crear, editar y eliminar."""
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from apps.otaku import forms as f
from apps.otaku.views.base import BaseAnime, BaseAnimeCharacter, BaseAnimeImage, BaseAnimeSong, BaseAnimeStaff, BaseAnimeTitle, BaseCharacter, BaseCharacterImage, BaseCharacterNickname, BaseCharacterVoice, BaseCompanyMAL, BaseDataAnilistAnime, BaseDataAnilistCharacter, BaseDataAnilistManga, BaseDataAnilistPerson, BaseDataMalAnime, BaseDataMalAnimeCharacter, BaseDataMalAnimePicture, BaseDataMalAnimeStaff, BaseDataMalCharacter, BaseDataMalCharacterPicture, BaseDataMalManga, BaseDataMalMangaCharacter, BaseDataMalMangaPicture, BaseDataMalPerson, BaseDataMalPersonPicture, BaseDemographic, BaseDemographicAlias, BaseGenre, BaseGenreAlias, BaseManga, BaseMangaAuthor, BaseMangaCharacter, BaseMangaImage, BaseMangaTitle, BaseOtakuLog, BasePersonMAL, BaseRelation, BaseRole, BaseSource, BaseStatus, BaseTheme, BaseThemeAlias, BaseType, BaseYear
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class AnimeCreateView(BaseAnime, BaseCreate):
    # Django core
    form_class = f.AnimeForm
    form_template = "otaku/form/anime.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime_list"
    success_url = "panel:anime_list"
    cancel_url = "panel:anime_list"
    # UX
    success_message = _("Anime «%(obj)s» creado.")
    title = _("Crear anime")


class AnimeUpdateView(BaseAnime, BaseUpdate):
    # Django core
    form_class = f.AnimeForm
    form_template = "otaku/form/anime.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime_list"
    success_url = "panel:anime_list"
    cancel_url = "panel:anime_list"
    # UX
    success_message = _("Anime «%(obj)s» actualizado.")
    title = _("Editar anime")


class AnimeDeleteView(BaseAnime, BaseDelete):
    list_url = "panel:anime_list"
    success_url = "panel:anime_list"
    cancel_url = "panel:anime_list"
    success_message = _("Anime «%(obj)s» eliminado.")
    title = _("Eliminar anime")


class AnimeCharacterCreateView(BaseAnimeCharacter, BaseCreate):
    # Django core
    form_class = f.AnimeCharacterForm
    form_template = "otaku/form/anime_character.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-character_list"
    success_url = "panel:anime-character_list"
    cancel_url = "panel:anime-character_list"
    # UX
    success_message = _("Personaje «%(obj)s» creado.")
    title = _("Crear personaje")


class AnimeCharacterUpdateView(BaseAnimeCharacter, BaseUpdate):
    # Django core
    form_class = f.AnimeCharacterForm
    form_template = "otaku/form/anime_character.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-character_list"
    success_url = "panel:anime-character_list"
    cancel_url = "panel:anime-character_list"
    # UX
    success_message = _("Personaje «%(obj)s» actualizado.")
    title = _("Editar personaje")


class AnimeCharacterDeleteView(BaseAnimeCharacter, BaseDelete):
    list_url = "panel:anime-character_list"
    success_url = "panel:anime-character_list"
    cancel_url = "panel:anime-character_list"
    success_message = _("Personaje «%(obj)s» eliminado.")
    title = _("Eliminar personaje")


class AnimeImageCreateView(BaseAnimeImage, BaseCreate):
    # Django core
    form_class = f.AnimeImageForm
    form_template = "otaku/form/anime_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-image_list"
    success_url = "panel:anime-image_list"
    cancel_url = "panel:anime-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class AnimeImageUpdateView(BaseAnimeImage, BaseUpdate):
    # Django core
    form_class = f.AnimeImageForm
    form_template = "otaku/form/anime_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-image_list"
    success_url = "panel:anime-image_list"
    cancel_url = "panel:anime-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class AnimeImageDeleteView(BaseAnimeImage, BaseDelete):
    list_url = "panel:anime-image_list"
    success_url = "panel:anime-image_list"
    cancel_url = "panel:anime-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class AnimeSongCreateView(BaseAnimeSong, BaseCreate):
    # Django core
    form_class = f.AnimeSongForm
    form_template = "otaku/form/anime_song.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-song_list"
    success_url = "panel:anime-song_list"
    cancel_url = "panel:anime-song_list"
    # UX
    success_message = _("Canción «%(obj)s» creada.")
    title = _("Crear canción")


class AnimeSongUpdateView(BaseAnimeSong, BaseUpdate):
    # Django core
    form_class = f.AnimeSongForm
    form_template = "otaku/form/anime_song.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-song_list"
    success_url = "panel:anime-song_list"
    cancel_url = "panel:anime-song_list"
    # UX
    success_message = _("Canción «%(obj)s» actualizada.")
    title = _("Editar canción")


class AnimeSongDeleteView(BaseAnimeSong, BaseDelete):
    list_url = "panel:anime-song_list"
    success_url = "panel:anime-song_list"
    cancel_url = "panel:anime-song_list"
    success_message = _("Canción «%(obj)s» eliminada.")
    title = _("Eliminar canción")


class AnimeStaffCreateView(BaseAnimeStaff, BaseCreate):
    # Django core
    form_class = f.AnimeStaffForm
    form_template = "otaku/form/anime_staff.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-staff_list"
    success_url = "panel:anime-staff_list"
    cancel_url = "panel:anime-staff_list"
    # UX
    success_message = _("Staff «%(obj)s» creado.")
    title = _("Crear staff")


class AnimeStaffUpdateView(BaseAnimeStaff, BaseUpdate):
    # Django core
    form_class = f.AnimeStaffForm
    form_template = "otaku/form/anime_staff.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-staff_list"
    success_url = "panel:anime-staff_list"
    cancel_url = "panel:anime-staff_list"
    # UX
    success_message = _("Staff «%(obj)s» actualizado.")
    title = _("Editar staff")


class AnimeStaffDeleteView(BaseAnimeStaff, BaseDelete):
    list_url = "panel:anime-staff_list"
    success_url = "panel:anime-staff_list"
    cancel_url = "panel:anime-staff_list"
    success_message = _("Staff «%(obj)s» eliminado.")
    title = _("Eliminar staff")


class AnimeTitleCreateView(BaseAnimeTitle, BaseCreate):
    # Django core
    form_class = f.AnimeTitleForm
    form_template = "otaku/form/anime_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-title_list"
    success_url = "panel:anime-title_list"
    cancel_url = "panel:anime-title_list"
    # UX
    success_message = _("Título «%(obj)s» creado.")
    title = _("Crear título")


class AnimeTitleUpdateView(BaseAnimeTitle, BaseUpdate):
    # Django core
    form_class = f.AnimeTitleForm
    form_template = "otaku/form/anime_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:anime-title_list"
    success_url = "panel:anime-title_list"
    cancel_url = "panel:anime-title_list"
    # UX
    success_message = _("Título «%(obj)s» actualizado.")
    title = _("Editar título")


class AnimeTitleDeleteView(BaseAnimeTitle, BaseDelete):
    list_url = "panel:anime-title_list"
    success_url = "panel:anime-title_list"
    cancel_url = "panel:anime-title_list"
    success_message = _("Título «%(obj)s» eliminado.")
    title = _("Eliminar título")


class CharacterCreateView(BaseCharacter, BaseCreate):
    # Django core
    form_class = f.CharacterForm
    form_template = "otaku/form/character.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character_list"
    success_url = "panel:character_list"
    cancel_url = "panel:character_list"
    # UX
    success_message = _("Personaje «%(obj)s» creado.")
    title = _("Crear personaje")


class CharacterUpdateView(BaseCharacter, BaseUpdate):
    # Django core
    form_class = f.CharacterForm
    form_template = "otaku/form/character.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character_list"
    success_url = "panel:character_list"
    cancel_url = "panel:character_list"
    # UX
    success_message = _("Personaje «%(obj)s» actualizado.")
    title = _("Editar personaje")


class CharacterDeleteView(BaseCharacter, BaseDelete):
    list_url = "panel:character_list"
    success_url = "panel:character_list"
    cancel_url = "panel:character_list"
    success_message = _("Personaje «%(obj)s» eliminado.")
    title = _("Eliminar personaje")


class CharacterImageCreateView(BaseCharacterImage, BaseCreate):
    # Django core
    form_class = f.CharacterImageForm
    form_template = "otaku/form/character_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character-image_list"
    success_url = "panel:character-image_list"
    cancel_url = "panel:character-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class CharacterImageUpdateView(BaseCharacterImage, BaseUpdate):
    # Django core
    form_class = f.CharacterImageForm
    form_template = "otaku/form/character_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character-image_list"
    success_url = "panel:character-image_list"
    cancel_url = "panel:character-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class CharacterImageDeleteView(BaseCharacterImage, BaseDelete):
    list_url = "panel:character-image_list"
    success_url = "panel:character-image_list"
    cancel_url = "panel:character-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class CharacterNicknameCreateView(BaseCharacterNickname, BaseCreate):
    # Django core
    form_class = f.CharacterNicknameForm
    form_template = "otaku/form/character_nickname.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character-nickname_list"
    success_url = "panel:character-nickname_list"
    cancel_url = "panel:character-nickname_list"
    # UX
    success_message = _("Apodo «%(obj)s» creado.")
    title = _("Crear apodo")


class CharacterNicknameUpdateView(BaseCharacterNickname, BaseUpdate):
    # Django core
    form_class = f.CharacterNicknameForm
    form_template = "otaku/form/character_nickname.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character-nickname_list"
    success_url = "panel:character-nickname_list"
    cancel_url = "panel:character-nickname_list"
    # UX
    success_message = _("Apodo «%(obj)s» actualizado.")
    title = _("Editar apodo")


class CharacterNicknameDeleteView(BaseCharacterNickname, BaseDelete):
    list_url = "panel:character-nickname_list"
    success_url = "panel:character-nickname_list"
    cancel_url = "panel:character-nickname_list"
    success_message = _("Apodo «%(obj)s» eliminado.")
    title = _("Eliminar apodo")


class CharacterVoiceCreateView(BaseCharacterVoice, BaseCreate):
    # Django core
    form_class = f.CharacterVoiceForm
    form_template = "otaku/form/character_voice.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character-voice_list"
    success_url = "panel:character-voice_list"
    cancel_url = "panel:character-voice_list"
    # UX
    success_message = _("Voz «%(obj)s» creada.")
    title = _("Crear voz")


class CharacterVoiceUpdateView(BaseCharacterVoice, BaseUpdate):
    # Django core
    form_class = f.CharacterVoiceForm
    form_template = "otaku/form/character_voice.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:character-voice_list"
    success_url = "panel:character-voice_list"
    cancel_url = "panel:character-voice_list"
    # UX
    success_message = _("Voz «%(obj)s» actualizada.")
    title = _("Editar voz")


class CharacterVoiceDeleteView(BaseCharacterVoice, BaseDelete):
    list_url = "panel:character-voice_list"
    success_url = "panel:character-voice_list"
    cancel_url = "panel:character-voice_list"
    success_message = _("Voz «%(obj)s» eliminada.")
    title = _("Eliminar voz")


class CompanyMALCreateView(BaseCompanyMAL, BaseCreate):
    # Django core
    form_class = f.CompanyMALNewForm
    form_template = "otaku/form/company_mal.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:company-mal_list"
    success_url = "panel:company-mal_list"
    cancel_url = "panel:company-mal_list"
    # UX
    success_message = _("Ficha MAL de «%(obj)s» creada.")
    title = _("Crear compañía (MAL)")


class CompanyMALUpdateView(BaseCompanyMAL, BaseUpdate):
    # Django core
    form_class = f.CompanyMALNewForm
    form_template = "otaku/form/company_mal.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:company-mal_list"
    success_url = "panel:company-mal_list"
    cancel_url = "panel:company-mal_list"
    # UX
    success_message = _("Ficha MAL de «%(obj)s» actualizada.")
    title = _("Editar compañía (MAL)")

    def get_object(self, queryset=None):
        """La URL lleva el id de la FICHA MAL; el formulario edita su compañía (y trae la ficha rellena)."""
        return super().get_object(queryset).company


class CompanyMALDeleteView(BaseCompanyMAL, BaseDelete):
    list_url = "panel:company-mal_list"
    success_url = "panel:company-mal_list"
    cancel_url = "panel:company-mal_list"
    success_message = _("Ficha MAL de «%(obj)s» eliminada (la compañía se conserva).")
    title = _("Eliminar compañía (MAL)")


class CompanyMALLinkView(BaseCompanyMAL, BaseCreate):
    """Ficha MAL para una compañía EXISTENTE (el otro formulario, con select). Sin `company_pk` se elige en el
    select; con él llega fija. Si esa compañía ya tiene ficha, manda a editarla. Los datos MAL que traiga la URL
    (del modal) llegan ya puestos."""
    form_class = f.CompanyMALExistentForm
    form_template = "otaku/form/company_mal_link.html"
    list_url = "panel:company-mal_list"
    success_url = "panel:company-mal_list"
    cancel_url = "panel:company-mal_list"
    success_message = _("Ficha MAL de «%(obj)s» creada.")
    title = _("Enlazar ficha MAL a una compañía existente")

    def _ya_tiene(self):
        pk = self.kwargs.get("company_pk")
        if not pk:
            return None
        from apps.companies.models import Company
        from apps.otaku.models import CompanyMAL
        get_object_or_404(Company, pk=pk)
        ficha = CompanyMAL.objects.filter(company_id=pk).first()
        return redirect("panel:company-mal_update", ficha.pk) if ficha else None

    def get(self, request, *args, **kwargs):
        return self._ya_tiene() or super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._ya_tiene() or super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["compania_fija"] = self.kwargs.get("company_pk")
        return kwargs

    def get_initial(self):
        """Los datos MAL que venían del modal de candidatas («Enlazar»), ya puestos en el formulario."""
        inicial = super().get_initial()
        for campo in self.form_class.CAMPOS_MAL:
            if self.request.GET.get(campo):
                inicial[campo] = self.request.GET[campo]
        return inicial


class DataAnilistAnimeCreateView(BaseDataAnilistAnime, BaseCreate):
    form_class = f.DataAnilistAnimeForm
    list_url = "panel:data-anilist-anime_list"
    success_url = "panel:data-anilist-anime_list"
    cancel_url = "panel:data-anilist-anime_list"
    success_message = _("Datos de anime (AniList) «%(obj)s» creado.")


class DataAnilistAnimeUpdateView(BaseDataAnilistAnime, BaseUpdate):
    form_class = f.DataAnilistAnimeForm
    list_url = "panel:data-anilist-anime_list"
    success_url = "panel:data-anilist-anime_list"
    cancel_url = "panel:data-anilist-anime_list"
    success_message = _("Datos de anime (AniList) «%(obj)s» actualizado.")


class DataAnilistAnimeDeleteView(BaseDataAnilistAnime, BaseDelete):
    list_url = "panel:data-anilist-anime_list"
    success_url = "panel:data-anilist-anime_list"
    cancel_url = "panel:data-anilist-anime_list"
    success_message = _("Datos de anime (AniList) «%(obj)s» eliminado.")


class DataAnilistCharacterCreateView(BaseDataAnilistCharacter, BaseCreate):
    form_class = f.DataAnilistCharacterForm
    list_url = "panel:data-anilist-character_list"
    success_url = "panel:data-anilist-character_list"
    cancel_url = "panel:data-anilist-character_list"
    success_message = _("Datos de personaje (AniList) «%(obj)s» creado.")


class DataAnilistCharacterUpdateView(BaseDataAnilistCharacter, BaseUpdate):
    form_class = f.DataAnilistCharacterForm
    list_url = "panel:data-anilist-character_list"
    success_url = "panel:data-anilist-character_list"
    cancel_url = "panel:data-anilist-character_list"
    success_message = _("Datos de personaje (AniList) «%(obj)s» actualizado.")


class DataAnilistCharacterDeleteView(BaseDataAnilistCharacter, BaseDelete):
    list_url = "panel:data-anilist-character_list"
    success_url = "panel:data-anilist-character_list"
    cancel_url = "panel:data-anilist-character_list"
    success_message = _("Datos de personaje (AniList) «%(obj)s» eliminado.")


class DataAnilistMangaCreateView(BaseDataAnilistManga, BaseCreate):
    form_class = f.DataAnilistMangaForm
    list_url = "panel:data-anilist-manga_list"
    success_url = "panel:data-anilist-manga_list"
    cancel_url = "panel:data-anilist-manga_list"
    success_message = _("Datos de manga (AniList) «%(obj)s» creado.")


class DataAnilistMangaUpdateView(BaseDataAnilistManga, BaseUpdate):
    form_class = f.DataAnilistMangaForm
    list_url = "panel:data-anilist-manga_list"
    success_url = "panel:data-anilist-manga_list"
    cancel_url = "panel:data-anilist-manga_list"
    success_message = _("Datos de manga (AniList) «%(obj)s» actualizado.")


class DataAnilistMangaDeleteView(BaseDataAnilistManga, BaseDelete):
    list_url = "panel:data-anilist-manga_list"
    success_url = "panel:data-anilist-manga_list"
    cancel_url = "panel:data-anilist-manga_list"
    success_message = _("Datos de manga (AniList) «%(obj)s» eliminado.")


class DataAnilistPersonCreateView(BaseDataAnilistPerson, BaseCreate):
    form_class = f.DataAnilistPersonForm
    list_url = "panel:data-anilist-person_list"
    success_url = "panel:data-anilist-person_list"
    cancel_url = "panel:data-anilist-person_list"
    success_message = _("Datos de persona (AniList) «%(obj)s» creado.")


class DataAnilistPersonUpdateView(BaseDataAnilistPerson, BaseUpdate):
    form_class = f.DataAnilistPersonForm
    list_url = "panel:data-anilist-person_list"
    success_url = "panel:data-anilist-person_list"
    cancel_url = "panel:data-anilist-person_list"
    success_message = _("Datos de persona (AniList) «%(obj)s» actualizado.")


class DataAnilistPersonDeleteView(BaseDataAnilistPerson, BaseDelete):
    list_url = "panel:data-anilist-person_list"
    success_url = "panel:data-anilist-person_list"
    cancel_url = "panel:data-anilist-person_list"
    success_message = _("Datos de persona (AniList) «%(obj)s» eliminado.")


class DataMalAnimeUpdateView(BaseDataMalAnime, BaseUpdate):
    # Django core
    form_class = f.DataMalAnimeForm
    list_url = "panel:data-mal-anime_list"
    success_url = "panel:data-mal-anime_list"
    cancel_url = "panel:data-mal-anime_list"
    # UX
    success_message = _("Datos de anime «%(obj)s» actualizados.")


class DataMalAnimeDeleteView(BaseDataMalAnime, BaseDelete):
    list_url = "panel:data-mal-anime_list"
    success_url = "panel:data-mal-anime_list"
    cancel_url = "panel:data-mal-anime_list"
    success_message = _("Datos de anime «%(obj)s» eliminados.")


class DataMalAnimeCreateView(BaseDataMalAnime, BaseCreate):
    form_class = f.DataMalAnimeForm
    list_url = "panel:data-mal-anime_list"
    success_url = "panel:data-mal-anime_list"
    cancel_url = "panel:data-mal-anime_list"
    success_message = _("Datos de anime «%(obj)s» creado.")


class DataMalAnimeCharacterUpdateView(BaseDataMalAnimeCharacter, BaseUpdate):
    # Django core
    form_class = f.DataMalAnimeCharacterForm
    list_url = "panel:data-mal-anime-character_list"
    success_url = "panel:data-mal-anime-character_list"
    cancel_url = "panel:data-mal-anime-character_list"
    # UX
    success_message = _("Datos personajes de anime «%(obj)s» actualizados.")


class DataMalAnimeCharacterDeleteView(BaseDataMalAnimeCharacter, BaseDelete):
    list_url = "panel:data-mal-anime-character_list"
    success_url = "panel:data-mal-anime-character_list"
    cancel_url = "panel:data-mal-anime-character_list"
    success_message = _("Datos personajes de anime «%(obj)s» eliminados.")


class DataMalAnimeCharacterCreateView(BaseDataMalAnimeCharacter, BaseCreate):
    form_class = f.DataMalAnimeCharacterForm
    list_url = "panel:data-mal-anime-character_list"
    success_url = "panel:data-mal-anime-character_list"
    cancel_url = "panel:data-mal-anime-character_list"
    success_message = _("Datos personajes de anime «%(obj)s» creado.")


class DataMalAnimePictureUpdateView(BaseDataMalAnimePicture, BaseUpdate):
    # Django core
    form_class = f.DataMalAnimePictureForm
    list_url = "panel:data-mal-anime-picture_list"
    success_url = "panel:data-mal-anime-picture_list"
    cancel_url = "panel:data-mal-anime-picture_list"
    # UX
    success_message = _("Datos imágenes de anime «%(obj)s» actualizados.")


class DataMalAnimePictureDeleteView(BaseDataMalAnimePicture, BaseDelete):
    list_url = "panel:data-mal-anime-picture_list"
    success_url = "panel:data-mal-anime-picture_list"
    cancel_url = "panel:data-mal-anime-picture_list"
    success_message = _("Datos imágenes de anime «%(obj)s» eliminados.")


class DataMalAnimePictureCreateView(BaseDataMalAnimePicture, BaseCreate):
    form_class = f.DataMalAnimePictureForm
    list_url = "panel:data-mal-anime-picture_list"
    success_url = "panel:data-mal-anime-picture_list"
    cancel_url = "panel:data-mal-anime-picture_list"
    success_message = _("Datos imágenes de anime «%(obj)s» creado.")


class DataMalAnimeStaffUpdateView(BaseDataMalAnimeStaff, BaseUpdate):
    # Django core
    form_class = f.DataMalAnimeStaffForm
    list_url = "panel:data-mal-anime-staff_list"
    success_url = "panel:data-mal-anime-staff_list"
    cancel_url = "panel:data-mal-anime-staff_list"
    # UX
    success_message = _("Datos staff de anime «%(obj)s» actualizados.")


class DataMalAnimeStaffDeleteView(BaseDataMalAnimeStaff, BaseDelete):
    list_url = "panel:data-mal-anime-staff_list"
    success_url = "panel:data-mal-anime-staff_list"
    cancel_url = "panel:data-mal-anime-staff_list"
    success_message = _("Datos staff de anime «%(obj)s» eliminados.")


class DataMalAnimeStaffCreateView(BaseDataMalAnimeStaff, BaseCreate):
    form_class = f.DataMalAnimeStaffForm
    list_url = "panel:data-mal-anime-staff_list"
    success_url = "panel:data-mal-anime-staff_list"
    cancel_url = "panel:data-mal-anime-staff_list"
    success_message = _("Datos staff de anime «%(obj)s» creado.")


class DataMalCharacterUpdateView(BaseDataMalCharacter, BaseUpdate):
    # Django core
    form_class = f.DataMalCharacterForm
    list_url = "panel:data-mal-character_list"
    success_url = "panel:data-mal-character_list"
    cancel_url = "panel:data-mal-character_list"
    # UX
    success_message = _("Datos de personaje «%(obj)s» actualizados.")


class DataMalCharacterDeleteView(BaseDataMalCharacter, BaseDelete):
    list_url = "panel:data-mal-character_list"
    success_url = "panel:data-mal-character_list"
    cancel_url = "panel:data-mal-character_list"
    success_message = _("Datos de personaje «%(obj)s» eliminados.")


class DataMalCharacterCreateView(BaseDataMalCharacter, BaseCreate):
    form_class = f.DataMalCharacterForm
    list_url = "panel:data-mal-character_list"
    success_url = "panel:data-mal-character_list"
    cancel_url = "panel:data-mal-character_list"
    success_message = _("Datos de personaje «%(obj)s» creado.")


class DataMalCharacterPictureUpdateView(BaseDataMalCharacterPicture, BaseUpdate):
    # Django core
    form_class = f.DataMalCharacterPictureForm
    list_url = "panel:data-mal-character-picture_list"
    success_url = "panel:data-mal-character-picture_list"
    cancel_url = "panel:data-mal-character-picture_list"
    # UX
    success_message = _("Datos imágenes de personaje «%(obj)s» actualizados.")


class DataMalCharacterPictureDeleteView(BaseDataMalCharacterPicture, BaseDelete):
    list_url = "panel:data-mal-character-picture_list"
    success_url = "panel:data-mal-character-picture_list"
    cancel_url = "panel:data-mal-character-picture_list"
    success_message = _("Datos imágenes de personaje «%(obj)s» eliminados.")


class DataMalCharacterPictureCreateView(BaseDataMalCharacterPicture, BaseCreate):
    form_class = f.DataMalCharacterPictureForm
    list_url = "panel:data-mal-character-picture_list"
    success_url = "panel:data-mal-character-picture_list"
    cancel_url = "panel:data-mal-character-picture_list"
    success_message = _("Datos imágenes de personaje «%(obj)s» creado.")


class DataMalMangaUpdateView(BaseDataMalManga, BaseUpdate):
    # Django core
    form_class = f.DataMalMangaForm
    list_url = "panel:data-mal-manga_list"
    success_url = "panel:data-mal-manga_list"
    cancel_url = "panel:data-mal-manga_list"
    # UX
    success_message = _("Datos de manga «%(obj)s» actualizados.")


class DataMalMangaDeleteView(BaseDataMalManga, BaseDelete):
    list_url = "panel:data-mal-manga_list"
    success_url = "panel:data-mal-manga_list"
    cancel_url = "panel:data-mal-manga_list"
    success_message = _("Datos de manga «%(obj)s» eliminados.")


class DataMalMangaCreateView(BaseDataMalManga, BaseCreate):
    form_class = f.DataMalMangaForm
    list_url = "panel:data-mal-manga_list"
    success_url = "panel:data-mal-manga_list"
    cancel_url = "panel:data-mal-manga_list"
    success_message = _("Datos de manga «%(obj)s» creado.")


class DataMalMangaCharacterUpdateView(BaseDataMalMangaCharacter, BaseUpdate):
    # Django core
    form_class = f.DataMalMangaCharacterForm
    list_url = "panel:data-mal-manga-character_list"
    success_url = "panel:data-mal-manga-character_list"
    cancel_url = "panel:data-mal-manga-character_list"
    # UX
    success_message = _("Datos personajes de manga «%(obj)s» actualizados.")


class DataMalMangaCharacterDeleteView(BaseDataMalMangaCharacter, BaseDelete):
    list_url = "panel:data-mal-manga-character_list"
    success_url = "panel:data-mal-manga-character_list"
    cancel_url = "panel:data-mal-manga-character_list"
    success_message = _("Datos personajes de manga «%(obj)s» eliminados.")


class DataMalMangaCharacterCreateView(BaseDataMalMangaCharacter, BaseCreate):
    form_class = f.DataMalMangaCharacterForm
    list_url = "panel:data-mal-manga-character_list"
    success_url = "panel:data-mal-manga-character_list"
    cancel_url = "panel:data-mal-manga-character_list"
    success_message = _("Datos personajes de manga «%(obj)s» creado.")


class DataMalMangaPictureUpdateView(BaseDataMalMangaPicture, BaseUpdate):
    # Django core
    form_class = f.DataMalMangaPictureForm
    list_url = "panel:data-mal-manga-picture_list"
    success_url = "panel:data-mal-manga-picture_list"
    cancel_url = "panel:data-mal-manga-picture_list"
    # UX
    success_message = _("Datos imágenes de manga «%(obj)s» actualizados.")


class DataMalMangaPictureDeleteView(BaseDataMalMangaPicture, BaseDelete):
    list_url = "panel:data-mal-manga-picture_list"
    success_url = "panel:data-mal-manga-picture_list"
    cancel_url = "panel:data-mal-manga-picture_list"
    success_message = _("Datos imágenes de manga «%(obj)s» eliminados.")


class DataMalMangaPictureCreateView(BaseDataMalMangaPicture, BaseCreate):
    form_class = f.DataMalMangaPictureForm
    list_url = "panel:data-mal-manga-picture_list"
    success_url = "panel:data-mal-manga-picture_list"
    cancel_url = "panel:data-mal-manga-picture_list"
    success_message = _("Datos imágenes de manga «%(obj)s» creado.")


class DataMalPersonUpdateView(BaseDataMalPerson, BaseUpdate):
    # Django core
    form_class = f.DataMalPersonForm
    list_url = "panel:data-mal-person_list"
    success_url = "panel:data-mal-person_list"
    cancel_url = "panel:data-mal-person_list"
    # UX
    success_message = _("Datos de persona «%(obj)s» actualizados.")


class DataMalPersonDeleteView(BaseDataMalPerson, BaseDelete):
    list_url = "panel:data-mal-person_list"
    success_url = "panel:data-mal-person_list"
    cancel_url = "panel:data-mal-person_list"
    success_message = _("Datos de persona «%(obj)s» eliminados.")


class DataMalPersonCreateView(BaseDataMalPerson, BaseCreate):
    form_class = f.DataMalPersonForm
    list_url = "panel:data-mal-person_list"
    success_url = "panel:data-mal-person_list"
    cancel_url = "panel:data-mal-person_list"
    success_message = _("Datos de persona «%(obj)s» creado.")


class DataMalPersonPictureUpdateView(BaseDataMalPersonPicture, BaseUpdate):
    # Django core
    form_class = f.DataMalPersonPictureForm
    list_url = "panel:data-mal-person-picture_list"
    success_url = "panel:data-mal-person-picture_list"
    cancel_url = "panel:data-mal-person-picture_list"
    # UX
    success_message = _("Datos imágenes de persona «%(obj)s» actualizados.")


class DataMalPersonPictureDeleteView(BaseDataMalPersonPicture, BaseDelete):
    list_url = "panel:data-mal-person-picture_list"
    success_url = "panel:data-mal-person-picture_list"
    cancel_url = "panel:data-mal-person-picture_list"
    success_message = _("Datos imágenes de persona «%(obj)s» eliminados.")


class DataMalPersonPictureCreateView(BaseDataMalPersonPicture, BaseCreate):
    form_class = f.DataMalPersonPictureForm
    list_url = "panel:data-mal-person-picture_list"
    success_url = "panel:data-mal-person-picture_list"
    cancel_url = "panel:data-mal-person-picture_list"
    success_message = _("Datos imágenes de persona «%(obj)s» creado.")


class DemographicCreateView(BaseDemographic, BaseCreate):
    # Django core
    form_class = f.DemographicForm
    form_template = "otaku/form/demographic.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:demographic_list"
    success_url = "panel:demographic_list"
    cancel_url = "panel:demographic_list"
    # UX
    success_message = _("Demografía «%(obj)s» creada.")
    title = _("Crear demografía")


class DemographicUpdateView(BaseDemographic, BaseUpdate):
    # Django core
    form_class = f.DemographicForm
    form_template = "otaku/form/demographic.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:demographic_list"
    success_url = "panel:demographic_list"
    cancel_url = "panel:demographic_list"
    # UX
    success_message = _("Demografía «%(obj)s» actualizada.")
    title = _("Editar demografía")


class DemographicDeleteView(BaseDemographic, BaseDelete):
    list_url = "panel:demographic_list"
    success_url = "panel:demographic_list"
    cancel_url = "panel:demographic_list"
    success_message = _("Demografía «%(obj)s» eliminada.")
    title = _("Eliminar demografía")


class DemographicAliasCreateView(BaseDemographicAlias, BaseCreate):
    form_class = f.DemographicAliasForm
    list_url = "panel:demographic-alias_list"
    success_url = "panel:demographic-alias_list"
    cancel_url = "panel:demographic-alias_list"
    success_message = _("Alias de demografía «%(obj)s» creado.")
    title = _("Crear alias de demografía")


class DemographicAliasUpdateView(BaseDemographicAlias, BaseUpdate):
    form_class = f.DemographicAliasForm
    list_url = "panel:demographic-alias_list"
    success_url = "panel:demographic-alias_list"
    cancel_url = "panel:demographic-alias_list"
    success_message = _("Alias de demografía «%(obj)s» actualizado.")
    title = _("Editar alias de demografía")


class DemographicAliasDeleteView(BaseDemographicAlias, BaseDelete):
    list_url = "panel:demographic-alias_list"
    success_url = "panel:demographic-alias_list"
    cancel_url = "panel:demographic-alias_list"
    success_message = _("Alias de demografía «%(obj)s» eliminado.")
    title = _("Eliminar alias de demografía")


class GenreCreateView(BaseGenre, BaseCreate):
    # Django core
    form_class = f.GenreForm
    form_template = "otaku/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:genre_list"
    success_url = "panel:genre_list"
    cancel_url = "panel:genre_list"
    # UX
    success_message = _("Género «%(obj)s» creado.")
    title = _("Crear género")


class GenreUpdateView(BaseGenre, BaseUpdate):
    # Django core
    form_class = f.GenreForm
    form_template = "otaku/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:genre_list"
    success_url = "panel:genre_list"
    cancel_url = "panel:genre_list"
    # UX
    success_message = _("Género «%(obj)s» actualizado.")
    title = _("Editar género")


class GenreDeleteView(BaseGenre, BaseDelete):
    list_url = "panel:genre_list"
    success_url = "panel:genre_list"
    cancel_url = "panel:genre_list"
    success_message = _("Género «%(obj)s» eliminado.")
    title = _("Eliminar género")


class GenreAliasCreateView(BaseGenreAlias, BaseCreate):
    form_class = f.GenreAliasForm
    list_url = "panel:genre-alias_list"
    success_url = "panel:genre-alias_list"
    cancel_url = "panel:genre-alias_list"
    success_message = _("Alias de género «%(obj)s» creado.")
    title = _("Crear alias de género")


class GenreAliasUpdateView(BaseGenreAlias, BaseUpdate):
    form_class = f.GenreAliasForm
    list_url = "panel:genre-alias_list"
    success_url = "panel:genre-alias_list"
    cancel_url = "panel:genre-alias_list"
    success_message = _("Alias de género «%(obj)s» actualizado.")
    title = _("Editar alias de género")


class GenreAliasDeleteView(BaseGenreAlias, BaseDelete):
    list_url = "panel:genre-alias_list"
    success_url = "panel:genre-alias_list"
    cancel_url = "panel:genre-alias_list"
    success_message = _("Alias de género «%(obj)s» eliminado.")
    title = _("Eliminar alias de género")


class MangaCreateView(BaseManga, BaseCreate):
    # Django core
    form_class = f.MangaForm
    form_template = "otaku/form/manga.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga_list"
    success_url = "panel:manga_list"
    cancel_url = "panel:manga_list"
    # UX
    success_message = _("Manga «%(obj)s» creado.")
    title = _("Crear manga")


class MangaUpdateView(BaseManga, BaseUpdate):
    # Django core
    form_class = f.MangaForm
    form_template = "otaku/form/manga.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga_list"
    success_url = "panel:manga_list"
    cancel_url = "panel:manga_list"
    # UX
    success_message = _("Manga «%(obj)s» actualizado.")
    title = _("Editar manga")


class MangaDeleteView(BaseManga, BaseDelete):
    list_url = "panel:manga_list"
    success_url = "panel:manga_list"
    cancel_url = "panel:manga_list"
    success_message = _("Manga «%(obj)s» eliminado.")
    title = _("Eliminar manga")


class MangaAuthorCreateView(BaseMangaAuthor, BaseCreate):
    # Django core
    form_class = f.MangaAuthorForm
    form_template = "otaku/form/manga_author.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-author_list"
    success_url = "panel:manga-author_list"
    cancel_url = "panel:manga-author_list"
    # UX
    success_message = _("Autor «%(obj)s» creado.")
    title = _("Crear autor")


class MangaAuthorUpdateView(BaseMangaAuthor, BaseUpdate):
    # Django core
    form_class = f.MangaAuthorForm
    form_template = "otaku/form/manga_author.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-author_list"
    success_url = "panel:manga-author_list"
    cancel_url = "panel:manga-author_list"
    # UX
    success_message = _("Autor «%(obj)s» actualizado.")
    title = _("Editar autor")


class MangaAuthorDeleteView(BaseMangaAuthor, BaseDelete):
    list_url = "panel:manga-author_list"
    success_url = "panel:manga-author_list"
    cancel_url = "panel:manga-author_list"
    success_message = _("Autor «%(obj)s» eliminado.")
    title = _("Eliminar autor")


class MangaCharacterCreateView(BaseMangaCharacter, BaseCreate):
    # Django core
    form_class = f.MangaCharacterForm
    form_template = "otaku/form/manga_character.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-character_list"
    success_url = "panel:manga-character_list"
    cancel_url = "panel:manga-character_list"
    # UX
    success_message = _("Personaje «%(obj)s» creado.")
    title = _("Crear personaje")


class MangaCharacterUpdateView(BaseMangaCharacter, BaseUpdate):
    # Django core
    form_class = f.MangaCharacterForm
    form_template = "otaku/form/manga_character.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-character_list"
    success_url = "panel:manga-character_list"
    cancel_url = "panel:manga-character_list"
    # UX
    success_message = _("Personaje «%(obj)s» actualizado.")
    title = _("Editar personaje")


class MangaCharacterDeleteView(BaseMangaCharacter, BaseDelete):
    list_url = "panel:manga-character_list"
    success_url = "panel:manga-character_list"
    cancel_url = "panel:manga-character_list"
    success_message = _("Personaje «%(obj)s» eliminado.")
    title = _("Eliminar personaje")


class MangaImageCreateView(BaseMangaImage, BaseCreate):
    # Django core
    form_class = f.MangaImageForm
    form_template = "otaku/form/manga_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-image_list"
    success_url = "panel:manga-image_list"
    cancel_url = "panel:manga-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class MangaImageUpdateView(BaseMangaImage, BaseUpdate):
    # Django core
    form_class = f.MangaImageForm
    form_template = "otaku/form/manga_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-image_list"
    success_url = "panel:manga-image_list"
    cancel_url = "panel:manga-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class MangaImageDeleteView(BaseMangaImage, BaseDelete):
    list_url = "panel:manga-image_list"
    success_url = "panel:manga-image_list"
    cancel_url = "panel:manga-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class MangaTitleCreateView(BaseMangaTitle, BaseCreate):
    # Django core
    form_class = f.MangaTitleForm
    form_template = "otaku/form/manga_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-title_list"
    success_url = "panel:manga-title_list"
    cancel_url = "panel:manga-title_list"
    # UX
    success_message = _("Título «%(obj)s» creado.")
    title = _("Crear título")


class MangaTitleUpdateView(BaseMangaTitle, BaseUpdate):
    # Django core
    form_class = f.MangaTitleForm
    form_template = "otaku/form/manga_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:manga-title_list"
    success_url = "panel:manga-title_list"
    cancel_url = "panel:manga-title_list"
    # UX
    success_message = _("Título «%(obj)s» actualizado.")
    title = _("Editar título")


class MangaTitleDeleteView(BaseMangaTitle, BaseDelete):
    list_url = "panel:manga-title_list"
    success_url = "panel:manga-title_list"
    cancel_url = "panel:manga-title_list"
    success_message = _("Título «%(obj)s» eliminado.")
    title = _("Eliminar título")


class PersonMALCreateView(BasePersonMAL, BaseCreate):
    # Django core
    form_class = f.PersonMALNewForm
    form_template = "otaku/form/person_mal.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-mal_list"
    success_url = "panel:person-mal_list"
    cancel_url = "panel:person-mal_list"
    # UX
    success_message = _("Ficha MAL de «%(obj)s» creada.")
    title = _("Crear persona (MAL)")


class PersonMALUpdateView(BasePersonMAL, BaseUpdate):
    # Django core
    form_class = f.PersonMALNewForm
    form_template = "otaku/form/person_mal.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-mal_list"
    success_url = "panel:person-mal_list"
    cancel_url = "panel:person-mal_list"
    # UX
    success_message = _("Ficha MAL de «%(obj)s» actualizada.")
    title = _("Editar persona (MAL)")

    def get_object(self, queryset=None):
        """La URL lleva el id de la FICHA MAL; el formulario edita su persona (y trae la ficha rellena)."""
        return super().get_object(queryset).person


class PersonMALDeleteView(BasePersonMAL, BaseDelete):
    list_url = "panel:person-mal_list"
    success_url = "panel:person-mal_list"
    cancel_url = "panel:person-mal_list"
    success_message = _("Ficha MAL de «%(obj)s» eliminada (la persona se conserva).")
    title = _("Eliminar persona (MAL)")


class PersonMALLinkView(BasePersonMAL, BaseCreate):
    """Ficha MAL para una persona EXISTENTE (el otro formulario, con select). Sin `person_pk` se elige en el select;
    con él (desde la ficha de la persona o el «Enlazar» del modal) llega fija. Si esa persona ya tiene ficha, manda
    a editarla. Los datos MAL que traiga la URL (del modal) llegan ya puestos."""
    form_class = f.PersonMALExistentForm
    form_template = "otaku/form/person_mal_link.html"
    list_url = "panel:person-mal_list"
    success_url = "panel:person-mal_list"
    cancel_url = "panel:person-mal_list"
    success_message = _("Ficha MAL de «%(obj)s» creada.")
    title = _("Enlazar ficha MAL a una persona existente")

    def _ya_tiene(self):
        pk = self.kwargs.get("person_pk")
        if not pk:
            return None
        from apps.otaku.models import PersonMAL
        from apps.people.models import Person
        get_object_or_404(Person, pk=pk)
        ficha = PersonMAL.objects.filter(person_id=pk).first()
        return redirect("panel:person-mal_update", ficha.pk) if ficha else None

    def get(self, request, *args, **kwargs):
        return self._ya_tiene() or super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._ya_tiene() or super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["persona_fija"] = self.kwargs.get("person_pk")
        return kwargs

    def get_initial(self):
        """Los datos MAL que venían del modal de candidatas («Enlazar»), ya puestos en el formulario."""
        inicial = super().get_initial()
        for campo in self.form_class.CAMPOS_MAL:
            if self.request.GET.get(campo):
                inicial[campo] = self.request.GET[campo]
        return inicial


class RelationCreateView(BaseRelation, BaseCreate):
    # Django core
    form_class = f.RelationForm
    form_template = "otaku/form/relation.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:relation_list"
    success_url = "panel:relation_list"
    cancel_url = "panel:relation_list"
    # UX
    success_message = _("Relación «%(obj)s» creada.")
    title = _("Crear relación")


class RelationUpdateView(BaseRelation, BaseUpdate):
    # Django core
    form_class = f.RelationForm
    form_template = "otaku/form/relation.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:relation_list"
    success_url = "panel:relation_list"
    cancel_url = "panel:relation_list"
    # UX
    success_message = _("Relación «%(obj)s» actualizada.")
    title = _("Editar relación")


class RelationDeleteView(BaseRelation, BaseDelete):
    list_url = "panel:relation_list"
    success_url = "panel:relation_list"
    cancel_url = "panel:relation_list"
    success_message = _("Relación «%(obj)s» eliminada.")
    title = _("Eliminar relación")


class RoleCreateView(BaseRole, BaseCreate):
    # Django core
    form_class = f.RoleForm
    form_template = "otaku/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:otaku-role_list"
    success_url = "panel:otaku-role_list"
    cancel_url = "panel:otaku-role_list"
    # UX
    success_message = _("Rol «%(obj)s» creado.")
    title = _("Crear rol")


class RoleUpdateView(BaseRole, BaseUpdate):
    # Django core
    form_class = f.RoleForm
    form_template = "otaku/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:otaku-role_list"
    success_url = "panel:otaku-role_list"
    cancel_url = "panel:otaku-role_list"
    # UX
    success_message = _("Rol «%(obj)s» actualizado.")
    title = _("Editar rol")


class RoleDeleteView(BaseRole, BaseDelete):
    list_url = "panel:otaku-role_list"
    success_url = "panel:otaku-role_list"
    cancel_url = "panel:otaku-role_list"
    success_message = _("Rol «%(obj)s» eliminado.")
    title = _("Eliminar rol")


class SourceCreateView(BaseSource, BaseCreate):
    # Django core
    form_class = f.SourceForm
    form_template = "otaku/form/source.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:source_list"
    success_url = "panel:source_list"
    cancel_url = "panel:source_list"
    # UX
    success_message = _("Fuente «%(obj)s» creada.")
    title = _("Crear fuente")


class SourceUpdateView(BaseSource, BaseUpdate):
    # Django core
    form_class = f.SourceForm
    form_template = "otaku/form/source.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:source_list"
    success_url = "panel:source_list"
    cancel_url = "panel:source_list"
    # UX
    success_message = _("Fuente «%(obj)s» actualizada.")
    title = _("Editar fuente")


class SourceDeleteView(BaseSource, BaseDelete):
    list_url = "panel:source_list"
    success_url = "panel:source_list"
    cancel_url = "panel:source_list"
    success_message = _("Fuente «%(obj)s» eliminada.")
    title = _("Eliminar fuente")


class StatusCreateView(BaseStatus, BaseCreate):
    # Django core
    form_class = f.StatusForm
    form_template = "otaku/form/status.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:status_list"
    success_url = "panel:status_list"
    cancel_url = "panel:status_list"
    # UX
    success_message = _("Estado «%(obj)s» creado.")
    title = _("Crear estado")


class StatusUpdateView(BaseStatus, BaseUpdate):
    # Django core
    form_class = f.StatusForm
    form_template = "otaku/form/status.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:status_list"
    success_url = "panel:status_list"
    cancel_url = "panel:status_list"
    # UX
    success_message = _("Estado «%(obj)s» actualizado.")
    title = _("Editar estado")


class StatusDeleteView(BaseStatus, BaseDelete):
    list_url = "panel:status_list"
    success_url = "panel:status_list"
    cancel_url = "panel:status_list"
    success_message = _("Estado «%(obj)s» eliminado.")
    title = _("Eliminar estado")


class ThemeCreateView(BaseTheme, BaseCreate):
    # Django core
    form_class = f.ThemeForm
    form_template = "otaku/form/theme.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:theme_list"
    success_url = "panel:theme_list"
    cancel_url = "panel:theme_list"
    # UX
    success_message = _("Tema «%(obj)s» creado.")
    title = _("Crear tema")


class ThemeUpdateView(BaseTheme, BaseUpdate):
    # Django core
    form_class = f.ThemeForm
    form_template = "otaku/form/theme.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:theme_list"
    success_url = "panel:theme_list"
    cancel_url = "panel:theme_list"
    # UX
    success_message = _("Tema «%(obj)s» actualizado.")
    title = _("Editar tema")


class ThemeDeleteView(BaseTheme, BaseDelete):
    list_url = "panel:theme_list"
    success_url = "panel:theme_list"
    cancel_url = "panel:theme_list"
    success_message = _("Tema «%(obj)s» eliminado.")
    title = _("Eliminar tema")


class ThemeAliasCreateView(BaseThemeAlias, BaseCreate):
    form_class = f.ThemeAliasForm
    list_url = "panel:theme-alias_list"
    success_url = "panel:theme-alias_list"
    cancel_url = "panel:theme-alias_list"
    success_message = _("Alias de tema «%(obj)s» creado.")
    title = _("Crear alias de tema")


class ThemeAliasUpdateView(BaseThemeAlias, BaseUpdate):
    form_class = f.ThemeAliasForm
    list_url = "panel:theme-alias_list"
    success_url = "panel:theme-alias_list"
    cancel_url = "panel:theme-alias_list"
    success_message = _("Alias de tema «%(obj)s» actualizado.")
    title = _("Editar alias de tema")


class ThemeAliasDeleteView(BaseThemeAlias, BaseDelete):
    list_url = "panel:theme-alias_list"
    success_url = "panel:theme-alias_list"
    cancel_url = "panel:theme-alias_list"
    success_message = _("Alias de tema «%(obj)s» eliminado.")
    title = _("Eliminar alias de tema")


class TypeCreateView(BaseType, BaseCreate):
    # Django core
    form_class = f.TypeForm
    form_template = "otaku/form/type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:type_list"
    success_url = "panel:type_list"
    cancel_url = "panel:type_list"
    # UX
    success_message = _("Tipo «%(obj)s» creado.")
    title = _("Crear tipo")


class TypeUpdateView(BaseType, BaseUpdate):
    # Django core
    form_class = f.TypeForm
    form_template = "otaku/form/type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:type_list"
    success_url = "panel:type_list"
    cancel_url = "panel:type_list"
    # UX
    success_message = _("Tipo «%(obj)s» actualizado.")
    title = _("Editar tipo")


class TypeDeleteView(BaseType, BaseDelete):
    list_url = "panel:type_list"
    success_url = "panel:type_list"
    cancel_url = "panel:type_list"
    success_message = _("Tipo «%(obj)s» eliminado.")
    title = _("Eliminar tipo")


class YearCreateView(BaseYear, BaseCreate):
    # Django core
    form_class = f.YearForm
    form_template = "otaku/form/year.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:year_list"
    success_url = "panel:year_list"
    cancel_url = "panel:year_list"
    # UX
    success_message = _("Año «%(obj)s» creado.")
    title = _("Crear año")


class YearUpdateView(BaseYear, BaseUpdate):
    # Django core
    form_class = f.YearForm
    form_template = "otaku/form/year.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:year_list"
    success_url = "panel:year_list"
    cancel_url = "panel:year_list"
    # UX
    success_message = _("Año «%(obj)s» actualizado.")
    title = _("Editar año")


class YearDeleteView(BaseYear, BaseDelete):
    list_url = "panel:year_list"
    success_url = "panel:year_list"
    cancel_url = "panel:year_list"
    success_message = _("Año «%(obj)s» eliminado.")
    title = _("Eliminar año")


class OtakuLogCreateView(BaseOtakuLog, BaseCreate):
    form_class = f.OtakuLogForm
    form_template = "otaku/form/otaku_log.html"
    list_url = "panel:otaku-log_list"
    success_url = "panel:otaku-log_list"
    cancel_url = "panel:otaku-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class OtakuLogUpdateView(BaseOtakuLog, BaseUpdate):
    form_class = f.OtakuLogForm
    form_template = "otaku/form/otaku_log.html"
    list_url = "panel:otaku-log_list"
    success_url = "panel:otaku-log_list"
    cancel_url = "panel:otaku-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class OtakuLogDeleteView(BaseOtakuLog, BaseDelete):
    list_url = "panel:otaku-log_list"
    success_url = "panel:otaku-log_list"
    cancel_url = "panel:otaku-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
