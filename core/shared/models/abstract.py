"""
Bases abstractas compartidas (versión LIMPIA de las de Hades/Poseidon:
mismos campos DB, sin los mixins de solo-presentación).

Jerarquía:
    ModelBaseCategory     → taxonomías/tipos (género, tipo, estado, temporada…)
    ModelBaseCompany      → empresas (estudios, editoriales, productoras, devs)
    ModelBaseMalEntity    → Anime / Manga de MyAnimeList (títulos multiidioma + mal_id)
    ModelBaseEntity       → Movie / Serie
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.choices import LogLevel, RoleType
from core.utils.models_abstract import generate_negative_id, siguiente_orden, unique_slug
from core.utils.text import TextUtils


class ModelBaseCollection(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Raíz de TODAS las tablas de colección del usuario. Cada tabla tiene `content` (FK
    al modelo de contenido) y de ahí se deduce todo: su clave (`medio()` = nombre del
    modelo: anime, movie, character…), la ficha pública (`content.get_absolute_url()`)
    La base encuentra las tablas por clave (`por_medio`) o por modelo (`de_contenido`)."""

    class Meta:
        abstract = True

    # ---- las tablas concretas, descubiertas por herencia ----
    @classmethod
    def tablas(cls):
        """Todas las tablas concretas de colección (en orden de definición)."""
        out = []
        for sub in cls.__subclasses__():
            out += [sub] if not sub._meta.abstract else sub.tablas()
        return out

    @classmethod
    def contenido(cls):
        """El modelo de contenido de la tabla (Anime, Movie, Character…)."""
        return cls._meta.get_field("content").remote_field.model

    MEDIO = ""     # clave propia solo si el nombre del modelo choca con otra tabla (games.Character → "game-character")

    @classmethod
    def medio(cls):
        """Clave de la colección: el nombre del modelo de contenido (o `MEDIO` si lo declara). Es el trozo de URL
        (/collection/anime/) y lo que la ficha declara en `collect_kind`."""
        return cls.MEDIO or cls.contenido()._meta.model_name

    @classmethod
    def por_medio(cls, medio):
        return next((t for t in cls.tablas() if t.medio() == medio), None)

    @classmethod
    def de_contenido(cls, content_model):
        """La tabla cuyo `content` es ese modelo (o None si no se colecciona)."""
        return next((t for t in cls.tablas() if t.contenido() is content_model), None)

    # ---- lo que cada tabla sabe de sí misma ----
    STATUS_CHOICES = None     # el TextChoices del medio (AnimeCollectionStatus…); None = sin estados

    @classmethod
    def estados(cls):
        """[(clave, etiqueta)] de los estados de la tabla, en orden; [] si no tiene (personajes y personas)."""
        return [(v, str(e)) for v, e in cls.STATUS_CHOICES.choices] if cls.STATUS_CHOICES else []

    @classmethod
    def estado(cls):
        """Compatibilidad: True si la tabla tiene estados."""
        return bool(cls.STATUS_CHOICES) or None

    @classmethod
    def favoritos(cls):
        """QuerySet de las filas marcadas con ★ (activas)."""
        return cls.objects.filter(is_active=True, is_favorite=True)

    def __str__(self):
        return f"{self.user} · {self.content}"


class ModelBaseCollectionItem(ModelBaseCollection):
    """Una entrada de la colección de un usuario: un título + su seguimiento.
    Cada medio tiene su tabla (subclase) con `content` → el título y `status` →
    el estado DE ESE medio. Aquí va lo común a todas."""
    FORMATO = ""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s_items", verbose_name="usuario")
    score = models.PositiveSmallIntegerField(verbose_name="puntuación", null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    is_favorite = models.BooleanField(verbose_name="favorito", default=False)
    watch_site = models.ForeignKey("catalogs.Website", null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_watched", verbose_name="lo veo en", limit_choices_to={"type": "streaming"})
    download_site = models.ForeignKey("catalogs.Website", null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_downloaded", verbose_name="lo descargué de", limit_choices_to={"type": "descarga"})
    download_format = models.ForeignKey("catalogs.Format", null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_downloads", verbose_name="formato de descarga")
    download_quality = models.ForeignKey("catalogs.Quality", null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s_downloads", verbose_name="calidad de descarga")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="añadido", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta(ModelBaseCollection.Meta):
        abstract = True          # Django no hereda `abstract`: hay que repetirlo
        ordering = ["-updated_at"]


class ModelBaseCategory(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Taxonomía/catálogo simple: género, tipo, estado, temporada, fuente, tema…
    `display_name` («name (name_esp)») es lo que pintan las listas del panel, los selects y
    las tarjetas: una propiedad del modelo (estilo Poseidon), no una columna virtual."""
    name = models.CharField(verbose_name="nombre", max_length=100)
    name_esp = models.CharField(verbose_name="nombre (ES)", max_length=100, blank=True)
    slug = models.SlugField(verbose_name="slug", max_length=120, unique=True, editable=False, blank=True)
    description = models.TextField(verbose_name="descripción", blank=True)
    image = models.ImageField(verbose_name="imagen", upload_to="categorias/", blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    DEFAULT_AVATAR = "image/default/sin-imagen.webp"

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        """«name (name_esp)» cuando hay traducción y difiere: «Spanish (Español)»; si no, name."""
        esp = (self.name_esp or "").strip()
        return f"{self.name} ({esp})" if esp and esp.lower() != self.name.lower() else self.name

    @property
    def display_description(self):
        """La descripción para pintar: el texto, o el aviso de que aún no hay (así la ficha nunca queda muda)."""
        return (self.description or "").strip() or _("Aún no hay descripción.")

    @property
    def avatar(self):
        """URL de la imagen de la categoría: la subida o la por defecto (reemplazable)."""
        try:
            if self.image and self.image.url:
                return self.image.url
        except ValueError:
            pass
        return static(self.DEFAULT_AVATAR)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(type(self), slugify(self.name)[:120], self.pk, 120)
        super().save(*args, **kwargs)

class ModelBaseCompany(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Empresa: estudio, editorial, productora, distribuidora, desarrolladora."""
    name = models.CharField(verbose_name="nombre", max_length=250)
    slug = models.SlugField(verbose_name="slug", max_length=270, unique=True, editable=False, blank=True)
    founded_year = models.PositiveSmallIntegerField(verbose_name="año de fundación", null=True, blank=True)
    disolved_year = models.PositiveSmallIntegerField(verbose_name="año de disolución", null=True, blank=True)
    biography = models.TextField(verbose_name="biografía", blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(type(self), slugify(self.name)[:270], self.pk, 270)
        super().save(*args, **kwargs)

class ModelBaseMalEntity(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Entrada de MyAnimeList (Anime / Manga): títulos multiidioma + id de MAL. Solo para entidades de MAL:
    las demás (películas, series) usan ModelBaseEntity.
    `mal_id` es la clave de MAL; `p_mal_id` = prefijo+id, un handle
    global con tipo (A1 anime, M1 manga…) para referenciar entradas aún no creadas.
    El subclase fija `MAL_PREFIX` ('A'/'M')."""
    MAL_PREFIX = ""

    title = models.CharField(verbose_name="título", max_length=500)
    title_eng = models.CharField(verbose_name="título (EN)", max_length=500, blank=True)
    title_jap = models.CharField(verbose_name="título (JP)", max_length=500, blank=True)
    slug = models.SlugField(verbose_name="slug", max_length=520, editable=False, blank=True)
    synopsis = models.TextField(verbose_name="sinopsis", blank=True)
    from_date = models.DateField(verbose_name="desde", null=True, blank=True)
    to_date = models.DateField(verbose_name="hasta", null=True, blank=True)
    mal_id = models.IntegerField(verbose_name="MAL id", null=True, blank=True, unique=True)
    p_mal_id = models.CharField(verbose_name="MAL id (prefijado)", max_length=15, unique=True, editable=False, blank=True)
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False, db_index=True)   # A–Z o «#»
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["title"]

    def __str__(self):
        return self.title

    # (slug NO es único aquí: la clave única es mal_id/p_mal_id, que se generan
    #  únicos en save() — no se valida el slug.)

    def save(self, *args, **kwargs):
        if self.mal_id is None:
            self.mal_id = generate_negative_id(type(self))
        self.p_mal_id = f"{self.MAL_PREFIX}{self.mal_id}"
        self.initial = TextUtils.get_initial(self.title)
        if not self.slug:
            self.slug = slugify(self.title)[:520]
        super().save(*args, **kwargs)

class ModelBaseEntity(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Entrada tipo Película/Serie."""
    title = models.CharField(verbose_name="título", max_length=255)
    title_secundary = models.CharField(verbose_name="título secundario", max_length=255, blank=True)
    release_year = models.PositiveSmallIntegerField(verbose_name="año", null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(verbose_name="duración (min)", null=True, blank=True)
    synopsis = models.TextField(verbose_name="sinopsis", blank=True)
    slug = models.SlugField(verbose_name="slug", max_length=275, unique=True, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-release_year", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # El AÑO entra al slug: «The Thing» (1982) y «The Thing» (2020) son
            # entidades DISTINTAS y conviven — el slug único ya no las choca.
            base = f"{self.title} {self.release_year}" if self.release_year else self.title
            self.slug = slugify(base)[:275]
        super().save(*args, **kwargs)


# ============================ Bases satélite (1-a-N) ============================
# Tablas hijas de una entidad: apodos, títulos alternativos, imágenes.
# Versión limpia de Hades: sin el helper `initial` (solo servía para indexar/mostrar).

class ModelBaseNickname(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Apodo/alias de una entidad (persona, creador, personaje…)."""
    nickname = models.CharField(verbose_name="apodo", max_length=100)
    slug = models.SlugField(verbose_name="slug", max_length=120, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["nickname"]

    def __str__(self):
        return self.nickname

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nickname)[:120]
        super().save(*args, **kwargs)


class ModelBaseTitle(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Título alternativo por idioma de una entidad. El hijo añade la FK a la
    entidad y `title_lang` (FK → common.Language)."""
    title = models.CharField(verbose_name="título", max_length=500)
    slug = models.SlugField(verbose_name="slug", max_length=520, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:520]
        super().save(*args, **kwargs)


class ModelBaseAlias(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """ALIAS de un catálogo (género, etiqueta, tema, demografía…): otro nombre por el que se conoce, con su inglés y
    su español como el propio catálogo. Una fila por alias: sin texto libre con comas ni ortografías sueltas. El hijo
    añade la FK al padre con `related_name="aliases"`; los importadores cruzan por nombre O alias antes de crear."""
    name = models.CharField(verbose_name="nombre", max_length=100)
    name_esp = models.CharField(verbose_name="nombre (ES)", max_length=100, blank=True)
    slug = models.SlugField(verbose_name="slug", max_length=120, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        return f"{self.name} ({self.name_esp})" if self.name_esp and self.name_esp != self.name else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:120]
        super().save(*args, **kwargs)


MAX_INTENTOS_DESCARGA = 3     # fallos TEMPORALES (timeout, 5xx) antes de dar la URL por muerta; un 404 la mata al primero


class ModelBaseImage(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Imagen de una entidad. El hijo añade `image` (ImageField) y la FK a la entidad.
    La imagen es un ARCHIVO subido o una URL que el sistema descarga (`image_url` → `image`). La misma fila lleva cómo
    le fue a esa descarga: intentos, último error y cuándo. Reglas (en `save`):
      · archivo NUEVO (subido o descargado)       → descargada; intentos y error a cero
      · URL CAMBIADA sin archivo nuevo            → el archivo viejo ya no corresponde: se suelta y vuelve a la cola
      · `download_attempts` >= MAX_INTENTOS       → URL muerta: fuera de la cola hasta «Reintentar»
    `order`: la de número MÁS BAJO es la portada (empate: la más antigua). Si llega vacío, va al final."""
    order = models.PositiveIntegerField(verbose_name="orden", null=True, blank=True)
    image_url = models.TextField(verbose_name="URL de la imagen", blank=True)
    image_downloaded = models.BooleanField(verbose_name="descargada", default=False)
    download_attempts = models.PositiveSmallIntegerField(verbose_name="intentos de descarga", default=0)
    download_error = models.CharField(verbose_name="error de descarga", max_length=300, blank=True)
    download_checked_at = models.DateTimeField(verbose_name="último intento", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        # la cola de descarga (sin archivo y no muertas) y sus contadores, por índice
        indexes = [models.Index(fields=["image_downloaded", "download_attempts"], name="%(app_label)s_%(class)s_dl")]

    def __str__(self):
        """«Imagen de Moxie Studio · 2»: la entidad dueña (su primera FK) y el orden. Nunca la URL ni la ruta del archivo."""
        padre = next((getattr(self, f.name, None) for f in self._meta.fields
                      if isinstance(f, models.ForeignKey) and getattr(self, f.attname, None)), None)
        orden = f" · {self.order}" if self.order else ""
        return f"Imagen de {padre}{orden}" if padre is not None else f"Imagen #{self.pk}"

    @classmethod
    def from_db(cls, db, field_names, values, *args, **kwargs):
        fila = super().from_db(db, field_names, values, *args, **kwargs)   # Django 6 suma `fetch_mode`: se pasa tal cual
        fila._url_inicial = fila.__dict__.get("image_url")
        img = fila.__dict__.get("image")
        fila._archivo_inicial = getattr(img, "name", img) or ""
        return fila

    @property
    def download_dead(self):
        return not self.image_downloaded and self.download_attempts >= MAX_INTENTOS_DESCARGA

    @property
    def estado_descarga(self):
        """Descargada · Pendiente · Muerta · Sin URL (texto para listas y fichas)."""
        if self.image_downloaded:
            return "Descargada"
        if not (self.image_url or "").strip():
            return "Sin URL"
        return "Muerta" if self.download_dead else "Pendiente"

    def save(self, *args, **kwargs):
        if kwargs.get("update_fields") is None and hasattr(self, "image"):
            archivo = getattr(self.image, "name", "") or ""
            archivo_nuevo = bool(archivo) and archivo != getattr(self, "_archivo_inicial", "")
            url_cambiada = self.pk is not None and hasattr(self, "_url_inicial") and \
                (self.image_url or "").strip() != (self._url_inicial or "").strip()
            if url_cambiada and not archivo_nuevo and archivo:
                self.image = None                 # la URL nueva manda: el archivo viejo era de otra imagen
            if archivo_nuevo or url_cambiada:
                self.download_attempts, self.download_error, self.download_checked_at = 0, "", None
            self.image_downloaded = bool(getattr(self.image, "name", ""))
        if self.order is None:
            self.order = siguiente_orden(self)
        super().save(*args, **kwargs)
        self._url_inicial = self.image_url
        self._archivo_inicial = getattr(getattr(self, "image", None), "name", "") or ""


class ModelBaseLink(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Enlace externo de una entidad. Aporta external_id + url + estado; cada
    hijo añade la FK a la entidad y su propia FK `source` al catálogo que le
    corresponde (common.ExternalSource para creadores/juegos —Patreon, Discord…—,
    common.Website para la colección del usuario —Crunchyroll, animeflv…—).
    Así el desplegable de cada formulario queda auto-filtrado por su rol."""
    external_id = models.CharField(verbose_name="id externo", max_length=500, blank=True)
    url = models.TextField(verbose_name="URL", blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return self.url or f"enlace #{self.pk}"


class ModelBaseRole(ModelBaseCategory):
    """Rol dentro de una obra (Protagonista, Director, Guionista, Seiyū…),
    agrupado por una familia fija (`RoleType`). Cada app tiene su propio Role
    (movie.Role, serie.Role…) → el Select2 se auto-filtra por dominio."""
    type = models.CharField(verbose_name="tipo de rol", max_length=12, choices=RoleType.choices, blank=True)

    class Meta(ModelBaseCategory.Meta):
        abstract = True


# ============================ Capa de datos (import de APIs) ============================
class ModelBaseData(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Fila de datos crudos de una API externa (AniList/Deezer/VNDB). Se PERSISTE el JSON
    porque la API puede morir; luego un proceso lo transforma en entidades reales.
    Contrato: `data` (JSON crudo) + `data_status` (fetch OK) + `data_processed`
    (ya consumido) + `status_code` (HTTP). El subclase añade su id (mal_id/deezer_id)."""
    url = models.TextField(verbose_name="URL", blank=True)
    data = models.JSONField(verbose_name="datos", null=True, blank=True)
    data_status = models.BooleanField(verbose_name="fetch OK", default=False)
    data_processed = models.BooleanField(verbose_name="procesado", default=False)
    status_code = models.PositiveSmallIntegerField(verbose_name="código HTTP", default=0)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    @property
    def titulo(self):
        """Cómo se llama lo descargado, sacado del JSON: `title` (juegos, lanzamientos, animes, álbumes) o `name`
        (creadores, personajes, artistas). Es lo que la columna «Título» de las listas de datos pinta."""
        d = self.data if isinstance(self.data, dict) else {}
        return (d.get("title") or d.get("name") or d.get("original") or "")[:120]


class ModelBaseDataAnilist(ModelBaseData):
    """Una fila = lo que devolvió la API GraphQL de AniList para UNA entidad (anime, manga, persona o personaje),
    keyed por su id de AniList. `id_mal` se copia del JSON al guardar: es el cruce con lo que vino de MAL."""
    anilist_id = models.IntegerField(verbose_name="AniList id", unique=True)
    id_mal = models.IntegerField(verbose_name="MAL id", null=True, blank=True, db_index=True)

    class Meta(ModelBaseData.Meta):
        abstract = True

    def __str__(self):
        return f"{self._meta.verbose_name} #{self.anilist_id}"

    @property
    def titulo(self):
        """En AniList el título y el nombre son objetos: `title.userPreferred` / `name.full`."""
        d = self.data if isinstance(self.data, dict) else {}
        t = d.get("title") if isinstance(d.get("title"), dict) else {}
        n = d.get("name") if isinstance(d.get("name"), dict) else {}
        return (t.get("userPreferred") or t.get("romaji") or t.get("english") or n.get("full") or n.get("userPreferred") or "")[:120]


class ModelBaseDataMal(ModelBaseData):
    """Una fila = un bloque del dump de MAL, keyed por mal_id de la obra."""
    mal_id = models.IntegerField(verbose_name="MAL id", unique=True)

    class Meta(ModelBaseData.Meta):
        abstract = True

    def __str__(self):
        return f"{self._meta.verbose_name} #{self.mal_id}"


class ModelBaseLog(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Registro de un evento de obtención/procesamiento de datos."""
    timestamp = models.DateTimeField(verbose_name="momento", auto_now_add=True)
    process = models.CharField(verbose_name="proceso", max_length=255, blank=True)
    level = models.CharField(verbose_name="nivel", max_length=10, choices=LogLevel.choices, default=LogLevel.INFO)
    message = models.TextField(verbose_name="mensaje", blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.get_level_display()}] {self.process}"


