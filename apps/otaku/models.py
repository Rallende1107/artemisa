"""
Modelos de otaku, fieles a Hades/Poseidon (limpios).
Los "tipos/estados/temporadas/ratings/géneros" son TABLAS (ModelBaseCategory),
no enums — así el staff los gestiona desde el panel.
Genre vive aquí (por dominio): sus campos y descripciones son propios de otaku.
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseAlias, ModelBaseCategory, ModelBaseDataAnilist, ModelBaseDataMal, ModelBaseImage, ModelBaseLog, ModelBaseMalEntity, ModelBaseNickname, ModelBaseRole, ModelBaseTitle
from core.shared.models.choices import AnimeSongType, MalCompanyKind, MalRating, MalSeason, RelationMedia, RoleType
from core.shared.models.uploads import upload_path
from core.utils.creditos import trozos_credito
from core.utils.models_abstract import filas_obra, generate_negative_id, season_of
from core.utils.text import TextUtils


class Anime(ModelBaseMalEntity):
    MAL_PREFIX = "A"
    episodes = models.PositiveIntegerField(verbose_name="episodios", default=0)
    year = models.PositiveSmallIntegerField(verbose_name="año", null=True, blank=True)
    anime_type = models.ForeignKey("Type", null=True, blank=True, on_delete=models.SET_NULL, related_name="animes", verbose_name="tipo")
    source = models.ForeignKey("Source", null=True, blank=True, on_delete=models.SET_NULL, related_name="animes", verbose_name="fuente")
    rating = models.CharField(verbose_name="clasificación", max_length=6, choices=MalRating.choices, blank=True)
    status = models.ForeignKey("Status", null=True, blank=True, on_delete=models.SET_NULL, related_name="animes", verbose_name="estado")
    season = models.CharField(verbose_name="temporada", max_length=6, choices=MalSeason.choices, blank=True)   # si falta, se calcula de from_date (estreno)
    studios = models.ManyToManyField("companies.Company", blank=True, related_name="animes_studio", verbose_name="estudios")
    producers = models.ManyToManyField("companies.Company", blank=True, related_name="animes_produced", verbose_name="productoras")
    licensors = models.ManyToManyField("companies.Company", blank=True, related_name="animes_licensed", verbose_name="licenciatarias")
    genres = models.ManyToManyField("Genre", blank=True, related_name="animes", verbose_name="géneros")
    themes = models.ManyToManyField("Theme", blank=True, related_name="animes", verbose_name="temas")
    demographics = models.ManyToManyField("Demographic", blank=True, related_name="animes", verbose_name="demografías")

    def save(self, *args, **kwargs):
        if not self.season and self.from_date:
            self.season = season_of(self.from_date)
        if not self.year and self.from_date:
            self.year = self.from_date.year
        super().save(*args, **kwargs)

    class Meta(ModelBaseMalEntity.Meta):
        verbose_name = "anime"
        verbose_name_plural = "animes"

    def get_absolute_url(self):
        """Ficha pública (otaku:anime-detail); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("otaku:anime-detail", self)

    # ---- lo que la FICHA pinta (la vista solo pasa pestañas y «por»; el HTML llama a estos métodos) ----
    def titulos(self):
        """Títulos alternativos activos, por idioma."""
        return self.titles.filter(is_active=True).select_related("title_lang").order_by("title_lang__name_esp", "title_lang__name", "title")

    def personajes(self):
        """Personajes activos con su rol (principales primero) y, colgada en `.voz`, su voz principal."""
        return _personajes_con_voz(self.characters)

    def equipo(self):
        """Staff activo: persona y cargo."""
        return self.staff.filter(is_active=True, person__is_active=True).select_related("person", "role").order_by("role__name", "person__full_name")

    def voces(self):
        """Actores de voz de sus personajes, idioma original (japonés) primero."""
        voces = (CharacterVoice.objects.filter(is_active=True, person__is_active=True, character__is_active=True,
                                               character__anime_appearances__anime=self,
                                               character__anime_appearances__is_active=True)
                 .select_related("person", "character", "language").distinct())
        return sorted(voces, key=lambda v: (str(v.language or "").lower() not in IDIOMA_ORIGINAL, str(v.language or ""), str(v.person)))

    def canciones(self):
        """Canciones activas (openings, endings, inserts) con sus artistas."""
        return self.songs.filter(is_active=True).prefetch_related("artists")

    def banda_sonora(self):
        """[(etiqueta, canciones)] SIEMPRE los tres grupos, en orden Openings · Inserts · Endings (las tres
        columnas de la ficha); una lista vacía si el grupo no tiene canciones."""
        grupos = {"op": [], "in": [], "ed": []}
        for c in self.canciones():
            grupos[c.clase].append(c)
        return [(etiqueta, grupos[k]) for k, etiqueta in AnimeSong.CLASES]

    def relaciones(self):
        """Relaciones activas hacia otras obras, con `.related` resuelta (None si esa obra no está importada)."""
        return Relation.de("anime", self.mal_id)


class AnimeCharacter(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Personaje que aparece en un anime, con su rol (principal/secundario)."""
    anime = models.ForeignKey("Anime", on_delete=models.CASCADE, related_name="characters", verbose_name="anime")
    character = models.ForeignKey("Character", on_delete=models.CASCADE, related_name="anime_appearances", verbose_name="personaje")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="anime_characters", verbose_name="rol")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "personaje de anime"
        verbose_name_plural = "personajes de anime"
        ordering = ["anime", "character"]
        unique_together = (("anime", "character", "role"),)

    def __str__(self):
        return f"{self.character} — {self.anime}"


class AnimeImage(ModelBaseImage):
    """Imágenes de anime, todas en una tabla: la de `order` más bajo es la portada."""
    anime = models.ForeignKey("Anime", on_delete=models.CASCADE, related_name="images", verbose_name="anime")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de anime"
        verbose_name_plural = "imágenes de anime"
        ordering = ["anime", "order", "id"]


class AnimeSong(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Canción de un anime (opening/ending/insert), con su(s) artista(s)."""
    anime = models.ForeignKey("Anime", on_delete=models.CASCADE, related_name="songs", verbose_name="anime")
    type = models.CharField(verbose_name="tipo", max_length=10, choices=AnimeSongType.choices, default=AnimeSongType.INSERT)
    song_id = models.PositiveIntegerField(verbose_name="nº", default=0)
    artists = models.ManyToManyField("music.Artist", blank=True, related_name="anime_songs", verbose_name="artistas")
    title = models.CharField(verbose_name="título", max_length=255)
    title_kanji = models.CharField(verbose_name="título (kanji)", max_length=255, blank=True)
    title_eng = models.CharField(verbose_name="título (EN)", max_length=255, blank=True)
    # El crédito TAL CUAL lo escribe la fuente («The Seatbelts feat. Mai Yamane»). `artists` enlaza solo los que existen
    # en Música; el crédito se ve siempre y permite completar los enlaces cuando lleguen los artistas.
    artist_credit = models.CharField(verbose_name="crédito del artista", max_length=500, blank=True)
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=275, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    CLASES = (("op", "Openings"), ("in", "Inserts y otras"), ("ed", "Endings"))   # el orden de las columnas de la ficha

    def credito(self):
        """El crédito en trozos [(texto, artista o None)] para pintarlo con link solo en los artistas enlazados."""
        return trozos_credito(self.artist_credit, self.artists.all())

    @property
    def clase(self):
        """op / ed / in: columna de la ficha según el tipo."""
        return {AnimeSongType.OPENING: "op", AnimeSongType.ENDING: "ed"}.get(self.type, "in")

    class Meta:
        verbose_name = "canción de anime"
        verbose_name_plural = "canciones de anime"
        ordering = ["anime", "type", "song_id", "title"]
        unique_together = (("anime", "type", "song_id", "title"),)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.title)
        if not self.slug:
            self.slug = slugify(self.title)[:275]
        super().save(*args, **kwargs)


class AnimeStaff(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Persona del staff de un anime con su rol (director, guionista…)."""
    anime = models.ForeignKey("Anime", on_delete=models.CASCADE, related_name="staff", verbose_name="anime")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="anime_staff", verbose_name="persona")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="anime_staff", verbose_name="rol")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "staff de anime"
        verbose_name_plural = "staff de anime"
        ordering = ["anime", "person"]
        unique_together = (("anime", "person", "role"),)

    def __str__(self):
        return f"{self.person} — {self.anime}"


class AnimeTitle(ModelBaseTitle):
    anime = models.ForeignKey("Anime", on_delete=models.CASCADE, related_name="titles", verbose_name="anime")
    title_lang = models.ForeignKey(
        "catalogs.Language", on_delete=models.CASCADE,
        related_name="anime_titles", verbose_name="idioma")

    class Meta(ModelBaseTitle.Meta):
        verbose_name = "título de anime"
        verbose_name_plural = "títulos de anime"
        ordering = ["anime", "title_lang", "title"]
        unique_together = (("anime", "title_lang", "title"),)


class Character(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Personaje de anime/manga. Se enlaza a las obras vía puentes (AnimeCharacter…)."""
    full_name = models.CharField(verbose_name="nombre", max_length=255)
    name_kanji = models.CharField(verbose_name="nombre (kanji)", max_length=255, blank=True)
    birthday = models.CharField(verbose_name="cumpleaños", max_length=100, blank=True)
    biography = models.TextField(verbose_name="biografía", blank=True)
    mal_id = models.IntegerField(verbose_name="MAL id", null=True, blank=True, unique=True)
    p_mal_id = models.CharField(verbose_name="MAL id (prefijado)", max_length=15, unique=True, editable=False, blank=True)
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=275, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "personaje"
        verbose_name_plural = "personajes"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.full_name)
        if self.mal_id is None:
            self.mal_id = generate_negative_id(type(self))
        self.p_mal_id = f"C{self.mal_id}"
        if not self.slug:
            self.slug = slugify(self.full_name)[:275]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ficha pública (otaku:character-detail); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("otaku:character-detail", self)

    # ---- lo que la FICHA pinta ----
    def voces(self):
        """Actores de voz activos, idioma original (japonés) primero."""
        voces = self.voices.filter(is_active=True, person__is_active=True).select_related("person", "language")
        return sorted(voces, key=lambda v: (str(v.language or "").lower() not in IDIOMA_ORIGINAL, str(v.language or "")))

    def animes(self):
        """Sus apariciones en anime como filas de obra (obra = el anime, rol = su rol)."""
        filas = self.anime_appearances.filter(is_active=True, anime__is_active=True).select_related("anime", "role").order_by("-anime__year", "anime__title")
        return filas_obra(filas, "anime", lambda f: str(f.role or ""))

    def mangas(self):
        filas = self.manga_appearances.filter(is_active=True, manga__is_active=True).select_related("manga", "role").order_by("-manga__year", "manga__title")
        return filas_obra(filas, "manga", lambda f: str(f.role or ""))

    def apodos(self):
        return [n.nickname for n in self.nicknames.filter(is_active=True)]


class CharacterImage(ModelBaseImage):
    """Imágenes de personaje, todas en una tabla: la de `order` más bajo es la portada."""
    character = models.ForeignKey("Character", on_delete=models.CASCADE, related_name="images", verbose_name="personaje")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de personaje"
        verbose_name_plural = "imágenes de personaje"
        ordering = ["character", "order", "id"]


class CharacterNickname(ModelBaseNickname):
    character = models.ForeignKey("Character", on_delete=models.CASCADE, related_name="nicknames", verbose_name="personaje")

    class Meta(ModelBaseNickname.Meta):
        verbose_name = "apodo de personaje"
        verbose_name_plural = "apodos de personaje"
        unique_together = (("character", "nickname"),)


class CharacterVoice(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Actor de voz (seiyū) que interpreta a un personaje en un idioma."""
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="voice_roles", verbose_name="persona")
    character = models.ForeignKey("Character", on_delete=models.CASCADE, related_name="voices", verbose_name="personaje")
    language = models.ForeignKey("catalogs.Language", on_delete=models.CASCADE, related_name="voice_roles", verbose_name="idioma")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "voz de personaje"
        verbose_name_plural = "voces de personaje"
        ordering = ["character", "person"]
        unique_together = (("person", "character", "language"),)

    def __str__(self):
        return f"{self.person} → {self.character}"


class CompanyMAL(DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """EXTENSIÓN MAL de una compañía. `companies.Company` es NEUTRA (lo que cualquier fuente tiene); aquí vive lo
    que solo MyAnimeList sabe: su id (los dumps lo traen como `company_id`) y su TIPO, porque compañías y revistas se
    numeran aparte en MAL: la clave es (kind, mal_id). Una compañía tiene a lo más una ficha MAL."""
    company = models.OneToOneField("companies.Company", on_delete=models.CASCADE,
                                   related_name="company_mal", verbose_name="compañía")
    kind = models.CharField(verbose_name="tipo en MAL", max_length=10, choices=MalCompanyKind.choices, default=MalCompanyKind.COMPANY)
    mal_id = models.IntegerField(verbose_name="MAL id")
    url = models.URLField(verbose_name="URL en MAL", max_length=500, blank=True)
    # Lo que SOLO MAL sabe de la compañía (del dump): nombre japonés, favoritos, su «about», la fecha de fundación tal
    # como la escribe MAL y sus enlaces. Lo neutro (año de fundación, biografía, logo) va a la compañía si está vacío.
    name_japanese = models.CharField(verbose_name="nombre japonés", max_length=255, blank=True)
    favorites = models.PositiveIntegerField(verbose_name="favoritos (MAL)", default=0)
    about = models.TextField(verbose_name="about (MAL)", blank=True)
    established = models.CharField(verbose_name="fundada (texto MAL)", max_length=100, blank=True)
    links = models.JSONField(verbose_name="enlaces", default=list, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "compañía (MAL)"
        verbose_name_plural = "compañías (MAL)"
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["kind", "mal_id"], name="otaku_companymal_kind_mal_id_uniq")]

    def __str__(self):
        return str(self.company)

    @property
    def mal_url(self):
        """La URL guardada; si no hay, la que se deduce del tipo y el id."""
        if self.url:
            return self.url
        ruta = "manga/magazine" if self.kind == MalCompanyKind.MAGAZINE else "anime/producer"
        return f"https://myanimelist.net/{ruta}/{self.mal_id}"


class DataAnilistAnime(ModelBaseDataAnilist):
    class Meta(ModelBaseDataAnilist.Meta):
        verbose_name = "datos de anime (AniList)"
        verbose_name_plural = "datos · Anime (AniList)"


class DataAnilistCharacter(ModelBaseDataAnilist):
    class Meta(ModelBaseDataAnilist.Meta):
        verbose_name = "datos de personaje (AniList)"
        verbose_name_plural = "datos · Personaje (AniList)"


class DataAnilistManga(ModelBaseDataAnilist):
    class Meta(ModelBaseDataAnilist.Meta):
        verbose_name = "datos de manga (AniList)"
        verbose_name_plural = "datos · Manga (AniList)"


class DataAnilistPerson(ModelBaseDataAnilist):
    class Meta(ModelBaseDataAnilist.Meta):
        verbose_name = "datos de persona (AniList)"
        verbose_name_plural = "datos · Persona (AniList)"


class DataMalAnime(ModelBaseDataMal):  # /anime/{id}/full
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos de anime"
        verbose_name_plural = "datos de anime"


class DataMalAnimeCharacter(ModelBaseDataMal):  # /anime/{id}/characters
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos personajes de anime"
        verbose_name_plural = "datos personajes de anime"


class DataMalAnimePicture(ModelBaseDataMal):  # /anime/{id}/pictures
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos imágenes de anime"
        verbose_name_plural = "datos imágenes de anime"


class DataMalAnimeStaff(ModelBaseDataMal):  # /anime/{id}/staff
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos staff de anime"
        verbose_name_plural = "datos staff de anime"


class DataMalCharacter(ModelBaseDataMal):  # /characters/{id}/full
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos de personaje"
        verbose_name_plural = "datos de personaje"


class DataMalCharacterPicture(ModelBaseDataMal):  # /characters/{id}/pictures
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos imágenes de personaje"
        verbose_name_plural = "datos imágenes de personaje"


class DataMalManga(ModelBaseDataMal):  # /manga/{id}/full
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos de manga"
        verbose_name_plural = "datos de manga"


class DataMalMangaCharacter(ModelBaseDataMal):  # /manga/{id}/characters
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos personajes de manga"
        verbose_name_plural = "datos personajes de manga"


class DataMalMangaPicture(ModelBaseDataMal):  # /manga/{id}/pictures
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos imágenes de manga"
        verbose_name_plural = "datos imágenes de manga"


class DataMalPerson(ModelBaseDataMal):  # /people/{id}/full
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos de persona"
        verbose_name_plural = "datos de persona"


class DataMalPersonPicture(ModelBaseDataMal):  # /people/{id}/pictures
    class Meta(ModelBaseDataMal.Meta):
        verbose_name = "datos imágenes de persona"
        verbose_name_plural = "datos imágenes de persona"


class Demographic(ModelBaseCategory):
    """Shōnen, Seinen, Shōjo, Josei, Kids."""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "demografía"
        verbose_name_plural = "demografías"


class DemographicAlias(ModelBaseAlias):
    """Alias de un demografía (otaku.Demographic): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    demographic = models.ForeignKey("Demographic", on_delete=models.CASCADE, related_name="aliases", verbose_name="demografía")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de demografía"
        verbose_name_plural = "alias de demografías"
        unique_together = (("demographic", "name"),)


IDIOMA_ORIGINAL = ("japanese", "japonés", "japones")   # el idioma original del medio va primero en las voces


def _personajes_con_voz(puentes, con_voz=True):
    """Filas AnimeCharacter/MangaCharacter activas (rol y personaje), principales primero; con `con_voz` cuelga
    en `.voz` la voz principal del personaje (idioma original primero) SIN una consulta por fila."""
    filas = list(puentes.filter(is_active=True, character__is_active=True).select_related("character", "role")
                 .prefetch_related("character__images").order_by("role__name", "character__full_name"))
    if con_voz and filas:
        voces = {}
        for v in (CharacterVoice.objects.filter(is_active=True, person__is_active=True, character_id__in=[f.character_id for f in filas])
                  .select_related("person", "language")):
            voces.setdefault(v.character_id, []).append(v)
        for f in filas:
            mias = sorted(voces.get(f.character_id, []), key=lambda v: (str(v.language or "").lower() not in IDIOMA_ORIGINAL, str(v.language or "")))
            f.voz = mias[0] if mias else None
    return filas


class Genre(ModelBaseCategory):
    explicit = models.BooleanField(verbose_name="explícito (+18)", default=False)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "género"
        verbose_name_plural = "géneros"


class GenreAlias(ModelBaseAlias):
    """Alias de un género (otaku.Genre): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, related_name="aliases", verbose_name="género")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de género"
        verbose_name_plural = "alias de géneros"
        unique_together = (("genre", "name"),)


class Manga(ModelBaseMalEntity):
    MAL_PREFIX = "M"
    chapters = models.PositiveIntegerField(verbose_name="capítulos", default=0)
    volumes = models.PositiveIntegerField(verbose_name="volúmenes", default=0)
    year = models.PositiveSmallIntegerField(verbose_name="año", null=True, blank=True)
    manga_type = models.ForeignKey("Type", null=True, blank=True, on_delete=models.SET_NULL, related_name="mangas", verbose_name="tipo")
    source = models.ForeignKey("Source", null=True, blank=True, on_delete=models.SET_NULL, related_name="mangas", verbose_name="fuente")
    rating = models.CharField(verbose_name="clasificación", max_length=6, choices=MalRating.choices, blank=True)
    season = models.CharField(verbose_name="temporada", max_length=6, choices=MalSeason.choices, blank=True)   # si falta, se calcula de from_date (inicio de publicación)
    status = models.ForeignKey("Status", null=True, blank=True, on_delete=models.SET_NULL, related_name="mangas", verbose_name="estado")
    serializations = models.ManyToManyField("companies.Company", blank=True, related_name="mangas_serialized", verbose_name="serializaciones")
    genres = models.ManyToManyField("Genre", blank=True, related_name="mangas", verbose_name="géneros")
    themes = models.ManyToManyField("Theme", blank=True, related_name="mangas", verbose_name="temas")
    demographics = models.ManyToManyField("Demographic", blank=True, related_name="mangas", verbose_name="demografías")

    def save(self, *args, **kwargs):
        if not self.season and self.from_date:
            self.season = season_of(self.from_date)
        if not self.year and self.from_date:
            self.year = self.from_date.year
        super().save(*args, **kwargs)

    class Meta(ModelBaseMalEntity.Meta):
        verbose_name = "manga"
        verbose_name_plural = "mangas"

    def get_absolute_url(self):
        """Ficha pública (otaku:manga-detail); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("otaku:manga-detail", self)

    # ---- lo que la FICHA pinta ----
    def titulos(self):
        return self.titles.filter(is_active=True).select_related("title_lang").order_by("title_lang__name_esp", "title_lang__name", "title")

    def personajes(self):
        """Personajes activos con su rol (principales primero); un manga no tiene voces."""
        return _personajes_con_voz(self.characters, con_voz=False)

    def autores(self):
        """Autores activos: persona y cargo (historia, dibujo…)."""
        return self.authors.filter(is_active=True, person__is_active=True).select_related("person", "role").order_by("role__name", "person__full_name")

    def relaciones(self):
        return Relation.de("manga", self.mal_id)


class MangaAuthor(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Autor/a de un manga con su rol (historia, arte…)."""
    manga = models.ForeignKey("Manga", on_delete=models.CASCADE, related_name="authors", verbose_name="manga")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="manga_authored", verbose_name="persona")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="manga_authors", verbose_name="rol")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "autor de manga"
        verbose_name_plural = "autores de manga"
        ordering = ["manga", "person"]
        unique_together = (("manga", "person", "role"),)

    def __str__(self):
        return f"{self.person} — {self.manga}"


class MangaCharacter(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Personaje que aparece en un manga, con su rol."""
    manga = models.ForeignKey("Manga", on_delete=models.CASCADE, related_name="characters", verbose_name="manga")
    character = models.ForeignKey("Character", on_delete=models.CASCADE, related_name="manga_appearances", verbose_name="personaje")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="manga_characters", verbose_name="rol")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "personaje de manga"
        verbose_name_plural = "personajes de manga"
        ordering = ["manga", "character"]
        unique_together = (("manga", "character", "role"),)

    def __str__(self):
        return f"{self.character} — {self.manga}"


class MangaImage(ModelBaseImage):
    """Imágenes de manga, todas en una tabla: la de `order` más bajo es la portada."""
    manga = models.ForeignKey("Manga", on_delete=models.CASCADE, related_name="images", verbose_name="manga")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de manga"
        verbose_name_plural = "imágenes de manga"
        ordering = ["manga", "order", "id"]


class MangaTitle(ModelBaseTitle):
    manga = models.ForeignKey("Manga", on_delete=models.CASCADE, related_name="titles", verbose_name="manga")
    title_lang = models.ForeignKey(
        "catalogs.Language", on_delete=models.CASCADE,
        related_name="manga_titles", verbose_name="idioma")

    class Meta(ModelBaseTitle.Meta):
        verbose_name = "título de manga"
        verbose_name_plural = "títulos de manga"
        ordering = ["manga", "title_lang", "title"]
        unique_together = (("manga", "title_lang", "title"),)


class PersonMAL(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """EXTENSIÓN MAL de una persona. `people.Person` es NEUTRA (lo que cualquier
    fuente tiene); aquí vive lo que solo MyAnimeList sabe: su id, su url, el nombre en
    kanji (given/family) y el about. Lo que MAL trae pero es de la PERSONA va a la
    persona: los nombres alternativos a sus apodos y el sitio web a sus enlaces.
    Una persona tiene a lo más una ficha MAL. La ESCRITURA pasa siempre por
    `apps.otaku.services.personas.upsert_persona_mal` — el procesado del dump de MAL y
    el formulario del panel usan la misma función (nada de lógica duplicada)."""
    person = models.OneToOneField("people.Person", on_delete=models.CASCADE,
                                  related_name="person_mal", verbose_name="persona")
    mal_id = models.IntegerField(verbose_name="MAL id", unique=True)
    url = models.URLField(verbose_name="URL en MAL", max_length=500, blank=True)
    p_mal_id = models.CharField(verbose_name="MAL id (prefijado)", max_length=15, unique=True, blank=True, editable=False)
    given_name = models.CharField(verbose_name="nombre (given)", max_length=255, blank=True)
    family_name = models.CharField(verbose_name="apellido (family)", max_length=255, blank=True)
    about = models.TextField(verbose_name="about (MAL)", blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "persona (MAL)"
        verbose_name_plural = "personas (MAL)"
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.person)

    @property
    def mal_url(self):
        """La URL guardada; si no hay, la que se deduce del id."""
        return self.url or f"https://myanimelist.net/people/{self.mal_id}"

    @property
    def nombre_japones(self):
        """«Apellido Nombre» tal como lo da MAL (kanji para japoneses)."""
        return " ".join(x for x in (self.family_name, self.given_name) if x).strip()

    def save(self, *args, **kwargs):
        self.p_mal_id = f"P{self.mal_id}"
        super().save(*args, **kwargs)


class Relation(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Relación entre dos obras (anime/manga), guardada por mal_id para poder
    apuntar a entradas aún no importadas (ej. 'este anime adapta el manga X')."""

    relation_type = models.ForeignKey(
        "catalogs.RelationType", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="otaku_relations", verbose_name="tipo de relación")
    from_type = models.CharField(verbose_name="origen (tipo)", max_length=10, choices=RelationMedia.choices)
    from_mal_id = models.IntegerField(verbose_name="origen (MAL id)")
    to_type = models.CharField(verbose_name="destino (tipo)", max_length=10, choices=RelationMedia.choices)
    to_mal_id = models.IntegerField(verbose_name="destino (MAL id)")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "relación"
        verbose_name_plural = "relaciones"
        ordering = ["from_mal_id", "to_mal_id"]
        unique_together = (("from_mal_id", "to_mal_id", "relation_type"),)
        indexes = [models.Index(fields=["from_type", "to_type"], name="otaku_relation_tipos_idx")]   # listas fijas anime → manga…

    def __str__(self):
        return f"{self.from_type} {self.from_mal_id} → {self.to_type} {self.to_mal_id}"

    def _resolve(self, kind, mal_id):
        model = {"anime": Anime, "manga": Manga}.get(kind)
        return model.objects.filter(mal_id=mal_id).first() if model else None

    @property
    def from_object(self):
        return self._resolve(self.from_type, self.from_mal_id)

    @property
    def to_object(self):
        return self._resolve(self.to_type, self.to_mal_id)

    @classmethod
    def de(cls, kind, mal_id):
        """Relaciones activas que salen de una obra, con `.related` (la obra destino) resuelta en DOS consultas
        (animes y mangas por mal_id) en vez de una por fila; None si el destino no está importado."""
        filas = list(cls.objects.filter(is_active=True, from_type=kind, from_mal_id=mal_id)
                     .select_related("relation_type").order_by("relation_type__name", "to_type", "to_mal_id"))
        ids = {k: [f.to_mal_id for f in filas if f.to_type == k] for k in ("anime", "manga")}
        obras = {("anime", o.mal_id): o for o in Anime.objects.filter(mal_id__in=ids["anime"], is_active=True)}
        obras.update({("manga", o.mal_id): o for o in Manga.objects.filter(mal_id__in=ids["manga"], is_active=True)})
        for f in filas:
            f.related = obras.get((f.to_type, f.to_mal_id))
        return filas


class Role(ModelBaseRole):
    """Rol en anime/manga: Principal, Secundario, Director, Guión, Autor… (por tipo)."""
    FAMILIAS = (RoleType.STAFF, RoleType.CHARACTER, RoleType.MANGA,)          # familias de rol que existen en esta app
    type = models.CharField(verbose_name="tipo de rol", max_length=12, blank=True,
                            choices=[(v, e) for v, e in RoleType.choices if v in (RoleType.STAFF, RoleType.CHARACTER, RoleType.MANGA,)])

    class Meta(ModelBaseRole.Meta):
        verbose_name = "rol"
        verbose_name_plural = "roles"


class Source(ModelBaseCategory):
    """Manga, Novela ligera, Original, Videojuego…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "fuente"
        verbose_name_plural = "fuentes"


class Status(ModelBaseCategory):
    """En emisión, Finalizado, Próximamente…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "estado"
        verbose_name_plural = "estados"


class Theme(ModelBaseCategory):
    """Escolar, Militar, Mecha, Isekai…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "tema"
        verbose_name_plural = "temas"


class ThemeAlias(ModelBaseAlias):
    """Alias de un tema (otaku.Theme): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    theme = models.ForeignKey("Theme", on_delete=models.CASCADE, related_name="aliases", verbose_name="tema")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de tema"
        verbose_name_plural = "alias de temas"
        unique_together = (("theme", "name"),)


class Type(ModelBaseCategory):
    """TV, Película, OVA, ONA, Especial, Música…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "tipo"
        verbose_name_plural = "tipos"


class Year(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Año de emisión/publicación (tabla, como Hades)."""
    year = models.PositiveSmallIntegerField(verbose_name="año", unique=True)
    slug = models.SlugField(verbose_name="slug", max_length=6, unique=True, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "año"
        verbose_name_plural = "años"
        ordering = ["-year"]

    def __str__(self):
        return str(self.year)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(self.year)
        super().save(*args, **kwargs)


# Una tabla por bloque del dump de MAL → cada fila con su data_status/data_processed,
# obtenible/procesable/re-obtenible por separado. Keyed por mal_id de la obra.
class OtakuLog(ModelBaseLog):
    """Log de obtención/procesamiento de datos de otaku (MAL / AniList)."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de otaku"
        verbose_name_plural = "logs de otaku"
