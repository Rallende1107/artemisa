from django.db import models
from django.utils.translation import gettext_lazy as _

from core.shared.models.abstract import ModelBaseCategory, ModelBaseLog
from core.shared.models.choices import ExternalSourceType, WebsiteType
from core.utils.text import TextUtils


class Country(ModelBaseCategory):
    code = models.CharField(verbose_name="código ISO", max_length=4, blank=True)
    numeric_code = models.PositiveIntegerField(verbose_name="código numérico", default=0)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "país"
        verbose_name_plural = "países"


class ExternalSource(ModelBaseCategory):
    """Plataforma asociada a un creador/persona: blog, Discord, Patreon,
    SubscribeStar, X/Twitter, sitio oficial… Lo usan CreatorLink/GameLink.
    (Distinto de Website: aquí es la presencia del autor, no dónde ver el contenido.)"""

    acronym = models.CharField(verbose_name="acrónimo", max_length=15, blank=True)
    url = models.URLField(verbose_name="URL base", max_length=300, blank=True)
    type = models.CharField(
        verbose_name="tipo", max_length=20, choices=ExternalSourceType.choices, default=ExternalSourceType.OTHER
    )

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "fuente externa"
        verbose_name_plural = "fuentes externas"


class Format(ModelBaseCategory):
    """Formato de archivo, transversal a varias apps: mkv, mp4 (vídeo),
    mp3, flac, mp2 (audio), pdf, cbz… Lo usa la descarga de la colección.
    Los `for_*` marcan a qué tipo de medio aplica (un formato puede servir a varios)."""

    for_video = models.BooleanField(verbose_name="para vídeo", default=False)
    for_music = models.BooleanField(verbose_name="para música", default=False)
    for_image = models.BooleanField(verbose_name="para imagen", default=False)
    for_document = models.BooleanField(verbose_name="para documento", default=False)
    for_other = models.BooleanField(verbose_name="para otro", default=False)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "formato"
        verbose_name_plural = "formatos"


class Language(ModelBaseCategory):
    acronym = models.CharField(verbose_name="acrónimo", max_length=10, blank=True)
    iso_639_1 = models.CharField(verbose_name="ISO 639-1", max_length=10, blank=True)
    iso_639_2_t = models.CharField(verbose_name="ISO 639-2/T", max_length=10, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "idioma"
        verbose_name_plural = "idiomas"


class Quality(ModelBaseCategory):
    """Calidad (sobre todo de vídeo): 480p, 720p, 1080p, 4K, BluRay…"""

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "calidad"
        verbose_name_plural = "calidades"


class RelationType(ModelBaseCategory):
    """Tipo de relación entre obras (Secuela, Precuela, Spin-off, Remake, Adaptación…): UN solo catálogo para
    películas, series, anime, manga y juegos."""

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "tipo de relación"
        verbose_name_plural = "tipos de relación"


class Website(ModelBaseCategory):
    """Sitio donde se CONSUME el contenido: Crunchyroll, animeflv, Netflix,
    xxx.com, fff.cl… Lo usa la colección del usuario (dónde ve/descargó)."""

    acronym = models.CharField(verbose_name="acrónimo", max_length=15, blank=True)
    url = models.URLField(verbose_name="URL base", max_length=300, blank=True)
    type = models.CharField(verbose_name="tipo", max_length=20, choices=WebsiteType.choices, default=WebsiteType.OTHER)

    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "sitio web"
        verbose_name_plural = "sitios web"

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.name)
        super().save(*args, **kwargs)


class CatalogsLog(ModelBaseLog):
    """Log de catálogos."""

    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de catálogos"
        verbose_name_plural = "logs de catálogos"
