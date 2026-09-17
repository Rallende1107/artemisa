"""
Modelos de juegos (visual novels), fieles a Hades/Poseidon (limpios).
Taxonomías (género, plataforma, medio, estado, tipo, motor) son TABLAS.
Genre vive aquí (por dominio), con su flag +18.
Núcleo: Creator (desarrolladores) → Game.
(Nicknames, títulos alternativos, links externos, imágenes y Data* de VNDB: pendientes.)
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseAlias, ModelBaseCategory, ModelBaseData, ModelBaseImage, ModelBaseLink, ModelBaseLog, ModelBaseNickname, ModelBaseTitle
from core.shared.models.choices import CreatorType, GameStatus, GameType
from core.shared.models.uploads import upload_path
from core.utils.models_abstract import filas_obra
from core.utils.text import TextUtils


class Character(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Personaje de una novela visual (VNDB c<id>). NO vive sin su juego: al importarlo se traen
    los juegos en los que aparece (CharacterRole). La imagen va como fila de CharacterImage."""
    name = models.CharField(verbose_name="nombre", max_length=255)
    original = models.CharField(verbose_name="nombre original", max_length=255, blank=True)
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True, null=True, blank=True)
    p_vndb_id = models.CharField(verbose_name="VNDB id (prefijo)", max_length=15, unique=True, null=True, blank=True, editable=False)
    description = models.TextField(verbose_name="descripción", blank=True)
    sex = models.CharField(verbose_name="sexo", max_length=10, blank=True)
    age = models.PositiveSmallIntegerField(verbose_name="edad", null=True, blank=True)
    birthday = models.CharField(verbose_name="cumpleaños", max_length=5, blank=True)
    games = models.ManyToManyField("Game", through="CharacterRole", related_name="characters", verbose_name="juegos")
    slug = models.SlugField(verbose_name="slug", max_length=275, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "personaje de juego"
        verbose_name_plural = "personajes de juego"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Ficha pública del personaje (games:personaje)."""
        from core.utils.public import url_detail
        return url_detail("games:character-detail", self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:275]
        self.p_vndb_id = f"c{self.vndb_id}" if self.vndb_id is not None else None
        super().save(*args, **kwargs)

    # ---- lo que la FICHA pinta ----
    SEXO = {"m": "Masculino", "f": "Femenino", "b": "Ambos", "n": "Sin sexo"}

    def sexo(self):
        return self.SEXO.get(self.sex, self.sex)

    def juegos(self):
        """Sus juegos como filas de obra (obra = el juego, rol = su rol en él)."""
        filas = self.roles.filter(is_active=True, game__is_active=True).select_related("game").order_by("-game__release_date", "game__title")
        return filas_obra(filas, "game", lambda f: f.role or "")


class CharacterImage(ModelBaseImage):
    """Imágenes del personaje de juego, todas en una tabla: la de `order` más bajo es la portada."""
    character = models.ForeignKey("Character", on_delete=models.CASCADE, related_name="images", verbose_name="personaje")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de personaje de juego"
        verbose_name_plural = "imágenes de personaje de juego"
        ordering = ["character", "order", "id"]

    def __str__(self):
        return f"{self.character} · {self.order}"


class CharacterRole(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """En qué juego aparece un personaje y con qué papel (VNDB: main, primary, side, appears)."""
    character = models.ForeignKey("Character", on_delete=models.CASCADE, related_name="roles", verbose_name="personaje")
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="character_roles", verbose_name="juego")
    role = models.CharField(verbose_name="rol", max_length=20, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "rol de personaje"
        verbose_name_plural = "roles de personaje"
        unique_together = (("character", "game"),)
        ordering = ["game", "role", "character"]

    def __str__(self):
        return f"{self.character} · {self.game} ({self.role or '—'})"


class Creator(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Creador / desarrollador de juegos."""
    name = models.CharField(verbose_name="nombre", max_length=150)
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True, null=True, blank=True)
    p_vndb_id = models.CharField(verbose_name="VNDB id (prefijo)", max_length=15, unique=True, null=True, blank=True)
    type = models.CharField(verbose_name="tipo", max_length=10, choices=CreatorType.choices, blank=True)
    languages = models.ManyToManyField("catalogs.Language", blank=True, related_name="creators", verbose_name="idiomas")
    description = models.TextField(verbose_name="descripción", blank=True)
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=175, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "creador"
        verbose_name_plural = "creadores"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.name)
        # VNDB producer id → prefijo 'p' (solo si viene de VNDB).
        self.p_vndb_id = f"p{self.vndb_id}" if self.vndb_id is not None else None
        if not self.slug:
            self.slug = slugify(self.name)[:175]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from core.utils.public import url_detail
        return url_detail("games:creator-detail", self)

    # ---- lo que la FICHA pinta ----
    def juegos(self):
        """Juegos que desarrolla, como filas de obra."""
        return filas_obra(self.games.filter(is_active=True).order_by("-release_date", "title"), lambda g: g)

    def editados(self):
        return filas_obra(self.published_games.filter(is_active=True).order_by("-release_date", "title"), lambda g: g)

    def enlaces(self):
        return self.links.filter(is_active=True).exclude(url="").select_related("source")

    def apodos(self):
        return [n.nickname for n in self.nicknames.filter(is_active=True)]


class CreatorLink(ModelBaseLink):
    creator = models.ForeignKey("Creator", on_delete=models.CASCADE, related_name="links", verbose_name="creador")
    source = models.ForeignKey(
        "catalogs.ExternalSource", on_delete=models.CASCADE,
        related_name="creator_links", verbose_name="fuente")

    class Meta(ModelBaseLink.Meta):
        verbose_name = "enlace de creador"
        verbose_name_plural = "enlaces de creador"
        ordering = ["creator", "source"]
        unique_together = (("creator", "source", "external_id"),)


class CreatorNickname(ModelBaseNickname):
    creator = models.ForeignKey("Creator", on_delete=models.CASCADE, related_name="nicknames", verbose_name="creador")

    class Meta(ModelBaseNickname.Meta):
        verbose_name = "apodo de creador"
        verbose_name_plural = "apodos de creador"
        unique_together = (("creator", "nickname"),)


class DataF95Creator(ModelBaseData):
    """Staging de creador (F95zone): entra por DUMP, como el de juegos. El JSON del archivo se guarda
    tal cual en `data`; `f95_id` es el id del sitio."""
    f95_id = models.IntegerField(verbose_name="F95 id", null=True, blank=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de creador (F95)"
        verbose_name_plural = "datos de creador (F95)"

    def __str__(self):
        return f"creador F95 {self.f95_id or self.pk}"


class DataF95Game(ModelBaseData):
    """Staging de juego (F95zone)."""
    f95_id = models.IntegerField(verbose_name="F95 id", null=True, blank=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de juego (F95)"
        verbose_name_plural = "datos de juego (F95)"

    def __str__(self):
        return f"juego F95 {self.f95_id or self.pk}"


class DataVndbCharacter(ModelBaseData):
    """Staging VNDB: un PERSONAJE de una VN (POST /character filtrado por vn). `vndb_id_vn` enlaza a su
    juego. Sin modelo real de personaje de juego todavía: se guarda el JSON para cuando exista."""
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True)
    vndb_id_prefix = models.CharField(verbose_name="VNDB id (prefijo)", max_length=15, unique=True, null=True, blank=True)
    vndb_id_vn = models.IntegerField(verbose_name="VNDB id (VN)", null=True, blank=True, db_index=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de personaje (VNDB)"
        verbose_name_plural = "datos de personaje (VNDB)"

    def __str__(self):
        return f"personaje VNDB {self.vndb_id}"


class DataVndbCreator(ModelBaseData):
    """Productor/creador VNDB."""
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de creador (VNDB)"
        verbose_name_plural = "datos de creador (VNDB)"

    def __str__(self):
        return f"creador VNDB p{self.vndb_id}"


class DataVndbGame(ModelBaseData):
    """Juego (visual novel) VNDB."""
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de juego (VNDB)"
        verbose_name_plural = "datos de juego (VNDB)"

    def __str__(self):
        return f"juego VNDB v{self.vndb_id}"


class DataVndbRelease(ModelBaseData):
    """Staging VNDB: un LANZAMIENTO de una VN (POST /release filtrado por vn). `vndb_id_vn` enlaza a su juego."""
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True)
    vndb_id_prefix = models.CharField(verbose_name="VNDB id (prefijo)", max_length=15, unique=True, null=True, blank=True)
    vndb_id_vn = models.IntegerField(verbose_name="VNDB id (VN)", null=True, blank=True, db_index=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de lanzamiento (VNDB)"
        verbose_name_plural = "datos de lanzamiento (VNDB)"

    def __str__(self):
        return f"lanzamiento VNDB {self.vndb_id}"


class DevelopmentEngine(ModelBaseCategory):
    """Motor: Ren'Py, RPG Maker, Unity, Unreal…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "motor de desarrollo"
        verbose_name_plural = "motores de desarrollo"


class Game(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    title = models.CharField(verbose_name="título", max_length=255)
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True, null=True, blank=True)
    p_vndb_id = models.CharField(verbose_name="VNDB id (prefijo)", max_length=15, unique=True, null=True, blank=True, editable=False)
    vndb_fetched_at = models.DateTimeField(verbose_name="obtenido de VNDB", null=True, blank=True)
    version = models.CharField(verbose_name="versión", max_length=50, blank=True, default="0.0.1")
    release_date = models.DateField(verbose_name="fecha de lanzamiento", null=True, blank=True)
    synopsis = models.TextField(verbose_name="sinopsis", blank=True)
    background = models.TextField(verbose_name="trasfondo", blank=True)
    status = models.CharField(verbose_name="estado", max_length=12, choices=GameStatus.choices, default=GameStatus.UNKNOWN)
    type = models.CharField(verbose_name="tipo", max_length=12, choices=GameType.choices, default=GameType.VN)
    engine = models.ManyToManyField("DevelopmentEngine", blank=True, related_name="games", verbose_name="motores")
    mediums = models.ManyToManyField("Medium", blank=True, related_name="games", verbose_name="medios")
    platforms = models.ManyToManyField("Platform", blank=True, related_name="games", verbose_name="plataformas")
    developers = models.ManyToManyField("Creator", blank=True, related_name="games", verbose_name="desarrolladores")
    publishers = models.ManyToManyField("Creator", blank=True, related_name="published_games", verbose_name="editoras")
    languages = models.ManyToManyField("catalogs.Language", blank=True, related_name="games", verbose_name="idiomas")
    genres = models.ManyToManyField("Genre", blank=True, related_name="games", verbose_name="géneros")
    tags = models.ManyToManyField("Tag", blank=True, related_name="games", verbose_name="etiquetas")
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=275, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "juego"
        verbose_name_plural = "juegos"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.title)
        # VNDB visual-novel id → prefijo 'v' (solo si viene de VNDB).
        self.p_vndb_id = f"v{self.vndb_id}" if self.vndb_id is not None else None
        if not self.slug:
            self.slug = slugify(self.title)[:275]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ficha pública (games:detalle); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("games:game-detail", self)

    # ---- lo que la FICHA pinta ----
    ROL_ORDEN = {"main": 0, "primary": 1, "side": 2, "appears": 3}

    def titulos(self):
        return self.titles.filter(is_active=True).select_related("title_lang").order_by("title_lang__name_esp", "title_lang__name", "title")

    def personajes(self):
        """Personajes activos con su rol, los principales primero (main → primary → side → appears)."""
        filas = list(self.character_roles.filter(is_active=True, character__is_active=True).select_related("character").prefetch_related("character__images"))
        filas.sort(key=lambda r: (self.ROL_ORDEN.get(r.role, 9), r.character.name.lower()))
        return filas

    def lanzamientos(self):
        return self.releases.filter(is_active=True).prefetch_related("languages", "platforms", "publishers").order_by("released", "title")

    def enlaces(self):
        return self.links.filter(is_active=True).exclude(url="").select_related("source")


class GameImage(ModelBaseImage):
    """Imágenes de juego, todas en una tabla: la de `order` más bajo es la portada."""
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="images", verbose_name="juego")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de juego"
        verbose_name_plural = "imágenes de juego"
        ordering = ["game", "order", "id"]


class GameLink(ModelBaseLink):
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="links", verbose_name="juego")
    source = models.ForeignKey(
        "catalogs.ExternalSource", on_delete=models.CASCADE,
        related_name="game_links", verbose_name="fuente")

    class Meta(ModelBaseLink.Meta):
        verbose_name = "enlace de juego"
        verbose_name_plural = "enlaces de juego"
        ordering = ["game", "source"]
        unique_together = (("game", "source", "external_id"),)


class GameTitle(ModelBaseTitle):
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="titles", verbose_name="juego")
    title_lang = models.ForeignKey(
        "catalogs.Language", on_delete=models.CASCADE,
        related_name="game_titles", verbose_name="idioma")

    class Meta(ModelBaseTitle.Meta):
        verbose_name = "título de juego"
        verbose_name_plural = "títulos de juego"
        ordering = ["game", "title_lang", "title"]
        unique_together = (("game", "title_lang", "title"),)


class Genre(ModelBaseCategory):
    """Género de juego: los de F95 (seed) y los tags de CONTENIDO de VNDB (llegan con `vndb_id` al procesar un juego)."""
    explicit = models.BooleanField(verbose_name="explícito (+18)", default=False)
    vndb_id = models.PositiveIntegerField(verbose_name="VNDB id", unique=True, null=True, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "género"
        verbose_name_plural = "géneros"


class GenreAlias(ModelBaseAlias):
    """Alias de un género (games.Genre): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, related_name="aliases", verbose_name="género")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de género"
        verbose_name_plural = "alias de géneros"
        unique_together = (("genre", "name"),)


class Medium(ModelBaseCategory):
    """Medio/soporte (según VNDB)."""
    vndb_code = models.CharField(verbose_name="código VNDB", max_length=15, unique=True, null=True, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "medio"
        verbose_name_plural = "medios"


class Platform(ModelBaseCategory):
    """Windows, Linux, macOS, Android…"""
    vndb_code = models.CharField(verbose_name="código VNDB", max_length=15, unique=True, null=True, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "plataforma"
        verbose_name_plural = "plataformas"


class Release(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Un lanzamiento de un juego (VNDB r<id>): edición, fecha, plataformas, idiomas, editoras y
    desarrolladores. NO vive sin su juego. Al importar un juego se traen TODOS; uno suelto trae su juego."""
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="releases", verbose_name="juego")
    vndb_id = models.IntegerField(verbose_name="VNDB id", unique=True, null=True, blank=True)
    p_vndb_id = models.CharField(verbose_name="VNDB id (prefijo)", max_length=15, unique=True, null=True, blank=True, editable=False)
    title = models.CharField(verbose_name="título", max_length=255)
    alttitle = models.CharField(verbose_name="título alternativo", max_length=255, blank=True)
    released = models.DateField(verbose_name="fecha", null=True, blank=True)
    official = models.BooleanField(verbose_name="oficial", default=True)
    patch = models.BooleanField(verbose_name="parche", default=False)
    freeware = models.BooleanField(verbose_name="gratuito", default=False)
    minage = models.PositiveSmallIntegerField(verbose_name="edad mínima", null=True, blank=True)
    platforms = models.ManyToManyField("Platform", blank=True, related_name="releases", verbose_name="plataformas")
    languages = models.ManyToManyField("catalogs.Language", blank=True, related_name="game_releases", verbose_name="idiomas")
    publishers = models.ManyToManyField("Creator", blank=True, related_name="published_releases", verbose_name="editoras")
    developers = models.ManyToManyField("Creator", blank=True, related_name="developed_releases", verbose_name="desarrolladores")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "lanzamiento de juego"
        verbose_name_plural = "lanzamientos de juego"
        ordering = ["game", "released", "title"]

    def __str__(self):
        return f"{self.title} ({self.released or 'TBA'})"

    def save(self, *args, **kwargs):
        self.p_vndb_id = f"r{self.vndb_id}" if self.vndb_id is not None else None
        super().save(*args, **kwargs)


class ReleaseImage(ModelBaseImage):
    """Arte de un LANZAMIENTO (caja frontal/trasera, disco…): es del lanzamiento, no del juego. La URL la deja el
    importador de VNDB y la baja el descargador de imágenes pendientes."""
    release = models.ForeignKey("Release", on_delete=models.CASCADE, related_name="images", verbose_name="lanzamiento")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, blank=True)
    label = models.CharField(verbose_name="tipo de arte", max_length=20, blank=True)   # pkgfront, pkgback, dig, pkgcontent…

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de lanzamiento"
        verbose_name_plural = "imágenes de lanzamiento"
        ordering = ["release", "id"]


class Tag(ModelBaseCategory):
    """Etiqueta TÉCNICA de VNDB (ADV, Voiced, Multiple Endings…): categoría `tech`. Un juego tiene muchas y una
    etiqueta muchos juegos (N:M como los géneros); un juego puede no tener ninguna."""
    vndb_id = models.PositiveIntegerField(verbose_name="VNDB id", unique=True, null=True, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "etiqueta"
        verbose_name_plural = "etiquetas"


class TagAlias(ModelBaseAlias):
    """Alias de un etiqueta (games.Tag): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    tag = models.ForeignKey("Tag", on_delete=models.CASCADE, related_name="aliases", verbose_name="etiqueta")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de etiqueta"
        verbose_name_plural = "alias de etiquetas"
        unique_together = (("tag", "name"),)


class GameLog(ModelBaseLog):
    """Log de obtención/procesamiento de datos de juegos (VNDB)."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de juegos"
        verbose_name_plural = "logs de juegos"
