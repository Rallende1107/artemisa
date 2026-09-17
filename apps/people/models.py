"""Modelos de PERSONAS: la persona real (actores, autores, staff, artistas,
creadores) y sus satélites (apodos e imágenes). Es la entidad TRANSVERSAL del
catálogo: movie/serie/music/otaku la apuntan por FK y la ficha pública cruza sus obras.

Nació dentro de `common` (hoy `catalogs`) y se movió aquí el 2026-09-06 (historial de
migraciones reiniciado: las tablas son `people_*` desde la 0001)."""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import Country
from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseImage, ModelBaseLink, ModelBaseLog, ModelBaseNickname
from core.shared.models.uploads import upload_path
from core.utils.models_abstract import filas_obra
from core.utils.text import TextUtils


class Person(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Persona real: actores, autores, staff, artistas, creadores. NEUTRA: solo
    lo que cualquier fuente tiene (Wikipedia, MAL, IMDb…)."""
    full_name = models.CharField(verbose_name="nombre completo", max_length=255)
    biography = models.TextField(verbose_name="biografía", blank=True)
    birth_date = models.DateField(verbose_name="fecha de nacimiento", null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL, related_name="people", verbose_name="país")
    # Sin identidad de fuente: lo que solo MAL sabe (mal_id, kanji…) vive en
    # otaku.PersonMAL (OneToOne, accessor `person_mal`).
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=270, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "persona"
        verbose_name_plural = "personas"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.full_name)
        if not self.slug:
            self.slug = slugify(self.full_name)[:270]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ficha pública (personas:detalle); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("personas:person-detail", self)

    # ---- lo que la FICHA pinta: sus obras por medio, como filas de obra (obra, rol, rol_sub) ----
    def _activas(self, rel, obra, **sel):
        return rel.filter(is_active=True, **{f"{obra}__is_active": True}).select_related(obra, *sel.get("mas", ())).order_by(f"-{obra}__pk")

    def peliculas(self):
        """Reparto en películas: obra = la película, rol = el personaje, debajo el tipo de rol."""
        return filas_obra(self._activas(self.movie_cast, "movie", mas=("role",)), "movie", lambda f: f.character_name or _("Reparto"), lambda f: str(f.role or ""))

    def peliculas_equipo(self):
        return filas_obra(self._activas(self.movie_staff, "movie", mas=("role",)), "movie", lambda f: str(f.role or _("Equipo")))

    def series(self):
        return filas_obra(self._activas(self.serie_cast, "serie", mas=("role",)), "serie", lambda f: f.character_name or _("Reparto"), lambda f: str(f.role or ""))

    def series_equipo(self):
        return filas_obra(self._activas(self.serie_staff, "serie", mas=("role",)), "serie", lambda f: str(f.role or _("Equipo")))

    def animes(self):
        """Staff de anime: obra = el anime, rol = el cargo."""
        return filas_obra(self._activas(self.anime_staff, "anime", mas=("role",)), "anime", lambda f: str(f.role or _("Staff")))

    def mangas(self):
        return filas_obra(self._activas(self.manga_authored, "manga", mas=("role",)), "manga", lambda f: str(f.role or _("Autoría")))

    def voces(self):
        """Roles de voz: obra = el personaje, rol = el idioma."""
        return filas_obra(self._activas(self.voice_roles, "character", mas=("language",)), "character", lambda f: str(f.language or ""))

    def apodos(self):
        return [n.nickname for n in self.nicknames.filter(is_active=True)]

    def ficha_mal(self):
        """Su ficha MAL (otaku.PersonMAL, uno a uno) activa, o None."""
        ext = getattr(self, "person_mal", None)
        return ext if ext is not None and ext.is_active else None


class PersonImage(ModelBaseImage):
    """Imágenes de persona, todas en una tabla: la de `order` más bajo es la portada."""
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE,
        related_name="images", verbose_name="persona")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de persona"
        verbose_name_plural = "imágenes de persona"
        ordering = ["person", "order", "id"]


class PersonLink(ModelBaseLink):
    """Enlace externo de una persona: sitio oficial, X/Twitter, Instagram, Wikipedia… La fuente es el catálogo
    `ExternalSource` (el mismo que usan los enlaces de creadores y juegos). Aquí va, por ejemplo, el «sitio web» que
    trae MAL: es un dato de la PERSONA, no de su ficha MAL."""
    person = models.ForeignKey("Person", on_delete=models.CASCADE, related_name="links", verbose_name="persona")
    source = models.ForeignKey(
        "catalogs.ExternalSource", on_delete=models.CASCADE,
        related_name="person_links", verbose_name="fuente")

    class Meta(ModelBaseLink.Meta):
        verbose_name = "enlace de persona"
        verbose_name_plural = "enlaces de persona"
        ordering = ["person", "source"]
        unique_together = (("person", "source", "external_id"),)


class PersonNickname(ModelBaseNickname):
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE,
        related_name="nicknames", verbose_name="persona")

    class Meta(ModelBaseNickname.Meta):
        verbose_name = "apodo de persona"
        verbose_name_plural = "apodos de persona"
        unique_together = (("person", "nickname"),)


class PeopleLog(ModelBaseLog):
    """Log de la app: auditoría del panel (altas, ediciones, borrados, toggles) y
    cualquier proceso propio. Una tabla por app, para no amontonar."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de personas"
        verbose_name_plural = "logs de personas"
