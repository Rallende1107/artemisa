"""
Modelos de movie, fieles a Hades/Poseidon (limpios).
Taxonomías (género, tipo, clasificación) son TABLAS (ModelBaseCategory).
Genre vive aquí (por dominio), con su flag +18.
Núcleo: Movie (ModelBaseEntity). Las compañías (productoras/distribuidoras) viven en apps/companies.
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
    """Alias de un género (movies.Genre): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, related_name="aliases", verbose_name="género")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de género"
        verbose_name_plural = "alias de géneros"
        unique_together = (("genre", "name"),)


class Movie(ModelBaseEntity):
    movie_type = models.ForeignKey(
        "Type", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="movies", verbose_name="tipo",
    )
    movie_rating = models.ForeignKey(
        "Rating", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="movies", verbose_name="clasificación",
    )
    genres = models.ManyToManyField("Genre", blank=True, related_name="movies", verbose_name="géneros")
    producers = models.ManyToManyField("companies.Company", blank=True, related_name="movies_produced", verbose_name="productoras")
    distributors = models.ManyToManyField("companies.Company", blank=True, related_name="movies_distributed", verbose_name="distribuidoras")

    class Meta(ModelBaseEntity.Meta):
        verbose_name = "película"
        verbose_name_plural = "películas"

    def get_absolute_url(self):
        """Ficha pública (movies:detalle); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("movies:movie-detail", self)

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


class MovieCast(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Reparto: una persona interpreta un personaje en una película."""
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="cast", verbose_name="película")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="movie_cast", verbose_name="persona")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="cast", verbose_name="rol")
    character_name = models.CharField(verbose_name="personaje", max_length=150, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "reparto"
        verbose_name_plural = "reparto"
        ordering = ["movie", "person"]
        unique_together = (("movie", "person", "role", "character_name"),)

    def __str__(self):
        return f"{self.person} — {self.character_name or self.role}"


class MovieImage(ModelBaseImage):
    """Imágenes de película, todas en una tabla: la de `order` más bajo es la portada."""
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="images", verbose_name="película")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de película"
        verbose_name_plural = "imágenes de película"
        ordering = ["movie", "order", "id"]


class MovieRelation(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Relación entre películas en UN sentido: «300» → Secuela → «300: El origen de un imperio». El tipo es
    el catálogo GENÉRICO de tipos de relación de Catálogos (secuela, precuela, spin-off, remake…). La vuelta se registra aparte,
    como en MAL (la precuela de la secuela)."""
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="relations", verbose_name="película")
    related = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="related_from", verbose_name="relacionada")
    relation_type = models.ForeignKey("catalogs.RelationType", null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name="movie_relations", verbose_name="tipo de relación")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "relación"
        verbose_name_plural = "relaciones"
        ordering = ["movie", "relation_type", "related"]
        unique_together = (("movie", "related", "relation_type"),)

    def __str__(self):
        return f"{self.movie} → {self.relation_type or 'relación'} → {self.related}"


class MovieStaff(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Equipo técnico: una persona con un rol de producción en una película."""
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="staff", verbose_name="película")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="movie_staff", verbose_name="persona")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="staff", verbose_name="rol")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "equipo"
        verbose_name_plural = "equipo"
        ordering = ["movie", "person"]
        unique_together = (("movie", "person", "role"),)

    def __str__(self):
        return f"{self.person} — {self.role}"


class MovieTitle(ModelBaseTitle):
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="titles", verbose_name="película")
    title_lang = models.ForeignKey(
        "catalogs.Language", on_delete=models.CASCADE,
        related_name="movie_titles", verbose_name="idioma",
    )

    class Meta(ModelBaseTitle.Meta):
        verbose_name = "título de película"
        verbose_name_plural = "títulos de película"
        ordering = ["movie", "title_lang", "title"]
        unique_together = (("movie", "title_lang", "title"),)


class Rating(ModelBaseCategory):
    """Clasificación por edad (con acrónimo: PG-13, R…)."""
    acronym = models.CharField(verbose_name="acrónimo", max_length=15, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "clasificación"
        verbose_name_plural = "clasificaciones"


class Role(ModelBaseRole):
    """Rol en una película: Protagonista, Director, Guionista… (agrupado por tipo)."""
    FAMILIAS = (RoleType.STAFF, RoleType.CAST,)          # familias de rol que existen en esta app
    type = models.CharField(verbose_name="tipo de rol", max_length=12, blank=True,
                            choices=[(v, e) for v, e in RoleType.choices if v in (RoleType.STAFF, RoleType.CAST,)])

    class Meta(ModelBaseRole.Meta):
        verbose_name = "rol"
        verbose_name_plural = "roles"


class Type(ModelBaseCategory):
    """Largometraje, Cortometraje, Documental…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "tipo"
        verbose_name_plural = "tipos"


class MovieLog(ModelBaseLog):
    """Log de películas."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de películas"
        verbose_name_plural = "logs de películas"


# ═══════════════════════════ Estado de colección (movie) ═══════════════════════════

    @property
    def display_name(self):
        """«Título (Título secundario) Año»: dos títulos iguales se distinguen por el año.
        Lo pintan la lista del panel, el select y las tarjetas (mismo texto en todos)."""
        texto = str(self)
        sec = (self.title_secundary or "").strip()
        if sec and sec.lower() != texto.lower():
            texto = f"{texto} ({sec})"
        return f"{texto} {self.release_year}" if self.release_year else texto
