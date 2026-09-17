"""
Modelos de serie, fieles a Hades/Poseidon (limpios).
Espejo estructural de movie (mismas taxonomías, mismo núcleo).
Genre vive aquí (por dominio), con su flag +18.
Núcleo: Serie (ModelBaseEntity). Las compañías (productoras/distribuidoras) viven en apps/companies.
(Role/Cast/Staff, títulos alternativos, imágenes: pendientes.)
"""
from django.db import models

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseAlias, ModelBaseCategory, ModelBaseEntity, ModelBaseImage, ModelBaseLog, ModelBaseRole, ModelBaseTitle
from core.shared.models.choices import RoleType
from core.shared.models.uploads import upload_path


class Genre(ModelBaseCategory):
    explicit = models.BooleanField(verbose_name="explícito (+18)", default=False)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "género"
        verbose_name_plural = "géneros"


class GenreAlias(ModelBaseAlias):
    """Alias de un género (series.Genre): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, related_name="aliases", verbose_name="género")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de género"
        verbose_name_plural = "alias de géneros"
        unique_together = (("genre", "name"),)


class Rating(ModelBaseCategory):
    """Clasificación por edad (con acrónimo: TV-MA, PG…)."""
    acronym = models.CharField(verbose_name="acrónimo", max_length=15, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "clasificación"
        verbose_name_plural = "clasificaciones"


class Role(ModelBaseRole):
    """Rol en una serie: Protagonista, Director, Guionista… (agrupado por tipo)."""
    FAMILIAS = (RoleType.STAFF, RoleType.CAST,)          # familias de rol que existen en esta app
    type = models.CharField(verbose_name="tipo de rol", max_length=12, blank=True,
                            choices=[(v, e) for v, e in RoleType.choices if v in (RoleType.STAFF, RoleType.CAST,)])

    class Meta(ModelBaseRole.Meta):
        verbose_name = "rol"
        verbose_name_plural = "roles"


class Serie(ModelBaseEntity):
    serie_type = models.ForeignKey(
        "Type", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="series", verbose_name="tipo",
    )
    serie_rating = models.ForeignKey(
        "Rating", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="series", verbose_name="clasificación",
    )
    genres = models.ManyToManyField("Genre", blank=True, related_name="series", verbose_name="géneros")
    producers = models.ManyToManyField("companies.Company", blank=True, related_name="series_produced", verbose_name="productoras")
    distributors = models.ManyToManyField("companies.Company", blank=True, related_name="series_distributed", verbose_name="distribuidoras")

    class Meta(ModelBaseEntity.Meta):
        verbose_name = "serie"
        verbose_name_plural = "series"

    def get_absolute_url(self):
        """Ficha pública (series:detalle); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("series:serie-detail", self)

    def relaciones(self):
        """Relaciones activas que salen de esta obra (secuelas, precuelas, spin-offs…), para la ficha."""
        return self.relations.filter(is_active=True, related__is_active=True).select_related("related", "relation_type")

    def titulos(self):
        """Títulos alternativos activos con su idioma, ordenados por idioma (la ficha los agrupa)."""
        return self.titles.filter(is_active=True).select_related("title_lang").order_by("title_lang__name_esp", "title_lang__name", "title")

    def reparto(self):
        """Reparto activo con persona y rol cargados (la ficha pinta cientos de filas sin una consulta por fila)."""
        return self.cast.filter(is_active=True, person__is_active=True).select_related("person", "role")

    def equipo(self):
        """Equipo activo con persona y cargo cargados."""
        return self.staff.filter(is_active=True, person__is_active=True).select_related("person", "role")


class SerieCast(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Reparto: una persona interpreta un personaje en una serie."""
    serie = models.ForeignKey("Serie", on_delete=models.CASCADE, related_name="cast", verbose_name="serie")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="serie_cast", verbose_name="persona")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="cast", verbose_name="rol")
    character_name = models.CharField(verbose_name="personaje", max_length=150, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "reparto"
        verbose_name_plural = "reparto"
        ordering = ["serie", "person"]
        unique_together = (("serie", "person", "role", "character_name"),)

    def __str__(self):
        return f"{self.person} — {self.character_name or self.role}"


class SerieImage(ModelBaseImage):
    """Imágenes de serie, todas en una tabla: la de `order` más bajo es la portada."""
    serie = models.ForeignKey("Serie", on_delete=models.CASCADE, related_name="images", verbose_name="serie")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de serie"
        verbose_name_plural = "imágenes de serie"
        ordering = ["serie", "order", "id"]


class SerieRelation(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Relación entre series en UN sentido: «Diarios de vampiros» → Spin-off → «Los originales». El tipo es
    el catálogo GENÉRICO de tipos de relación de Catálogos (secuela, precuela, spin-off, remake…). La vuelta se registra aparte,
    como en MAL (la precuela de la secuela)."""
    serie = models.ForeignKey("Serie", on_delete=models.CASCADE, related_name="relations", verbose_name="serie")
    related = models.ForeignKey("Serie", on_delete=models.CASCADE, related_name="related_from", verbose_name="relacionada")
    relation_type = models.ForeignKey("catalogs.RelationType", null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name="serie_relations", verbose_name="tipo de relación")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "relación"
        verbose_name_plural = "relaciones"
        ordering = ["serie", "relation_type", "related"]
        unique_together = (("serie", "related", "relation_type"),)

    def __str__(self):
        return f"{self.serie} → {self.relation_type or 'relación'} → {self.related}"


class SerieStaff(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Equipo técnico: una persona con un rol de producción en una serie."""
    serie = models.ForeignKey("Serie", on_delete=models.CASCADE, related_name="staff", verbose_name="serie")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="serie_staff", verbose_name="persona")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="staff", verbose_name="rol")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "equipo"
        verbose_name_plural = "equipo"
        ordering = ["serie", "person"]
        unique_together = (("serie", "person", "role"),)

    def __str__(self):
        return f"{self.person} — {self.role}"


class SerieTitle(ModelBaseTitle):
    serie = models.ForeignKey("Serie", on_delete=models.CASCADE, related_name="titles", verbose_name="serie")
    title_lang = models.ForeignKey(
        "catalogs.Language", on_delete=models.CASCADE,
        related_name="serie_titles", verbose_name="idioma",
    )

    class Meta(ModelBaseTitle.Meta):
        verbose_name = "título de serie"
        verbose_name_plural = "títulos de serie"
        ordering = ["serie", "title_lang", "title"]
        unique_together = (("serie", "title_lang", "title"),)


class Type(ModelBaseCategory):
    """Serie, Miniserie, Documental…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "tipo"
        verbose_name_plural = "tipos"


class SerieLog(ModelBaseLog):
    """Log de series."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de series"
        verbose_name_plural = "logs de series"


# ═══════════════════════════ Estado de colección (serie) ═══════════════════════════

    @property
    def display_name(self):
        """«Título (Título secundario) Año»: dos títulos iguales se distinguen por el año.
        Lo pintan la lista del panel, el select y las tarjetas (mismo texto en todos)."""
        texto = str(self)
        sec = (self.title_secundary or "").strip()
        if sec and sec.lower() != texto.lower():
            texto = f"{texto} ({sec})"
        return f"{texto} {self.release_year}" if self.release_year else texto
