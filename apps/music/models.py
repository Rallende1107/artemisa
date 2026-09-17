"""
Modelos de music, fieles a Hades/Poseidon (limpios).
Taxonomías (género, tipo de álbum/artista) son TABLAS (ModelBaseCategory).
Genre vive aquí (por dominio): Rock, Metal, Pop… propios de música.
Núcleo: Artist → Album → Song.
(Role/ArtistMember, imágenes y modelos Data* de Deezer: pendientes.)
"""
from django.db import models
from django.utils.text import slugify

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseAlias, ModelBaseCategory, ModelBaseData, ModelBaseImage, ModelBaseLog, ModelBaseRole
from core.shared.models.choices import RoleType
from core.shared.models.uploads import upload_path
from core.utils.text import TextUtils


class Album(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    title = models.CharField(verbose_name="título", max_length=255)
    artist = models.ForeignKey("Artist", on_delete=models.CASCADE, related_name="albums", verbose_name="artista")
    album_type = models.ForeignKey(
        "AlbumType", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="albums", verbose_name="tipo de álbum")
    release_date = models.DateField(verbose_name="fecha de lanzamiento", null=True, blank=True)
    description = models.TextField(verbose_name="reseña", blank=True)
    genres = models.ManyToManyField("Genre", blank=True, related_name="albums", verbose_name="géneros")
    deezer_id = models.BigIntegerField(verbose_name="Deezer id", unique=True, null=True, blank=True)
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=275, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "álbum"
        verbose_name_plural = "álbumes"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.title)
        if not self.slug:
            self.slug = slugify(self.title)[:275]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ficha pública (music:album); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("music:album-detail", self)


class AlbumImage(ModelBaseImage):
    """Imágenes de álbum, todas en una tabla: la de `order` más bajo es la portada."""
    album = models.ForeignKey("Album", on_delete=models.CASCADE, related_name="images", verbose_name="álbum")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de álbum"
        verbose_name_plural = "imágenes de álbum"
        ordering = ["album", "order", "id"]


class AlbumType(ModelBaseCategory):
    """Álbum, EP, Single, Recopilatorio…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "tipo de álbum"
        verbose_name_plural = "tipos de álbum"


class Artist(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    name = models.CharField(verbose_name="nombre", max_length=150)
    deezer_id = models.BigIntegerField(verbose_name="Deezer id", unique=True, null=True, blank=True)
    biography = models.TextField(verbose_name="biografía", blank=True)
    start_year = models.PositiveSmallIntegerField(verbose_name="año de inicio", null=True, blank=True)
    year_end = models.PositiveSmallIntegerField(verbose_name="año de fin", null=True, blank=True)
    artist_type = models.ForeignKey(
        "ArtistType", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="artists", verbose_name="tipo de artista")
    genres = models.ManyToManyField("Genre", blank=True, related_name="artists", verbose_name="géneros")
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=170, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "artista"
        verbose_name_plural = "artistas"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.name)
        if not self.slug:
            self.slug = slugify(self.name)[:170]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ficha pública (music:artista); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("music:artist-detail", self)


class ArtistImage(ModelBaseImage):
    """Imágenes del artista, todas en una tabla: la de `order` más bajo es su portada."""
    artist = models.ForeignKey("Artist", on_delete=models.CASCADE, related_name="images", verbose_name="artista")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de artista"
        verbose_name_plural = "imágenes de artista"
        ordering = ["artist", "order", "id"]


class ArtistMember(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Miembro de un artista/banda: una persona con un rol y un periodo."""
    artist = models.ForeignKey("Artist", on_delete=models.CASCADE, related_name="members", verbose_name="artista")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE, related_name="artist_memberships", verbose_name="persona")
    role = models.ForeignKey("Role", null=True, blank=True, on_delete=models.SET_NULL, related_name="members", verbose_name="rol")
    join_date = models.DateField(verbose_name="desde", null=True, blank=True)
    leave_date = models.DateField(verbose_name="hasta", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "miembro"
        verbose_name_plural = "miembros"
        ordering = ["artist", "person"]
        unique_together = (("artist", "person", "role"),)

    def __str__(self):
        return f"{self.person} — {self.role or 'miembro'}"


class ArtistType(ModelBaseCategory):
    """Solista, Banda, Dúo…"""
    class Meta(ModelBaseCategory.Meta):
        verbose_name = "tipo de artista"
        verbose_name_plural = "tipos de artista"


class DataDeezerAlbum(ModelBaseData):
    """Ficha COMPLETA de un álbum (GET /album/{id}): sello, género, colaboradores, nº de pistas…
    `deezer_id_artist` enlaza al artista. Sus pistas, una por fila, en DataDeezerTrack."""
    deezer_id = models.BigIntegerField(verbose_name="Deezer id (álbum)", unique=True)
    deezer_id_artist = models.BigIntegerField(verbose_name="Deezer id (artista)", null=True, blank=True, db_index=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de álbum (Deezer)"
        verbose_name_plural = "datos de álbum (Deezer)"

    def __str__(self):
        return f"álbum Deezer #{self.deezer_id}"

    @property
    def artista(self):
        """El nombre del artista sacado del JSON (`artist.name`), como `titulo` saca el título. Es lo que
        pinta la columna «Artista» de la lista de datos; vacío si el crudo no trajo artista."""
        d = self.data if isinstance(self.data, dict) else {}
        return ((d.get("artist") or {}).get("name") or "")[:120]


class DataDeezerArtist(ModelBaseData):
    """Artista Deezer: en `data`, el artista + su lista de álbumes."""
    deezer_id = models.BigIntegerField(verbose_name="Deezer id", unique=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de artista (Deezer)"
        verbose_name_plural = "datos de artista (Deezer)"

    def __str__(self):
        return f"artista Deezer #{self.deezer_id}"


class DataDeezerGenre(ModelBaseData):
    """Género Deezer."""
    deezer_id = models.BigIntegerField(verbose_name="Deezer id", unique=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de género (Deezer)"
        verbose_name_plural = "datos de género (Deezer)"

    def __str__(self):
        return f"género Deezer #{self.deezer_id}"


class DataDeezerTrack(ModelBaseData):
    """Una PISTA de un álbum (GET /album/{id}/tracks, todas las páginas): una fila por pista, con
    posición, disco, ISRC, duración y preview. `deezer_id_album` enlaza al álbum."""
    deezer_id = models.BigIntegerField(verbose_name="Deezer id (pista)", unique=True)
    deezer_id_album = models.BigIntegerField(verbose_name="Deezer id (álbum)", db_index=True)

    class Meta(ModelBaseData.Meta):
        verbose_name = "datos de pista del álbum (Deezer)"
        verbose_name_plural = "datos de pistas del álbum (Deezer)"

    def __str__(self):
        return f"pista Deezer #{self.deezer_id} del álbum #{self.deezer_id_album}"


class Genre(ModelBaseCategory):
    """Género musical: Rock, Metal, Pop, Jazz…"""
    deezer_id = models.IntegerField(verbose_name="Deezer id", unique=True, null=True, blank=True)

    class Meta(ModelBaseCategory.Meta):
        verbose_name = "género"
        verbose_name_plural = "géneros"


class GenreAlias(ModelBaseAlias):
    """Alias de un género (music.Genre): «Love» → Romance. Los importadores cruzan por nombre o alias."""
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, related_name="aliases", verbose_name="género")

    class Meta(ModelBaseAlias.Meta):
        verbose_name = "alias de género"
        verbose_name_plural = "alias de géneros"
        unique_together = (("genre", "name"),)


class Role(ModelBaseRole):
    """Rol dentro de un artista/banda: Vocalista, Guitarra, Batería, Productor…"""
    FAMILIAS = (RoleType.MUSIC, RoleType.PRODUCTION, RoleType.STAFF,)          # familias de rol que existen en esta app
    type = models.CharField(verbose_name="tipo de rol", max_length=12, blank=True,
                            choices=[(v, e) for v, e in RoleType.choices if v in (RoleType.MUSIC, RoleType.PRODUCTION, RoleType.STAFF,)])

    class Meta(ModelBaseRole.Meta):
        verbose_name = "rol"
        verbose_name_plural = "roles"


class Song(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    title = models.CharField(verbose_name="título", max_length=500)
    title_short = models.CharField(verbose_name="título corto", max_length=255, blank=True)
    title_version = models.CharField(verbose_name="versión", max_length=255, blank=True)
    album = models.ForeignKey("Album", on_delete=models.PROTECT, related_name="songs", verbose_name="álbum")
    album_song_id = models.PositiveIntegerField(verbose_name="nº de pista", default=0)
    audio_file = models.FileField(verbose_name="archivo de audio", upload_to=upload_path, null=True, blank=True)
    lyrics = models.TextField(verbose_name="letra", blank=True)
    meaning = models.TextField(verbose_name="significado", blank=True)
    composers = models.CharField(verbose_name="compuesta por", max_length=255, blank=True)
    release_year = models.PositiveIntegerField(verbose_name="año", null=True, blank=True)
    video_url = models.URLField(verbose_name="video", blank=True)
    deezer_id = models.BigIntegerField(verbose_name="Deezer id", unique=True, null=True, blank=True)
    initial = models.CharField(verbose_name="inicial", max_length=1, blank=True, editable=False)   # índice alfabético (A–Z, #)
    slug = models.SlugField(verbose_name="slug", max_length=520, editable=False, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "canción"
        verbose_name_plural = "canciones"
        ordering = ["album", "album_song_id", "title"]
        unique_together = (("album", "album_song_id", "title"),)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.initial = TextUtils.get_initial(self.title)
        if not self.slug:
            self.slug = slugify(self.title)[:520]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ficha pública (music:cancion); la usa Mi colección para enlazar el título."""
        from core.utils.public import url_detail
        return url_detail("music:song-detail", self)


class SongComposer(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Quién COMPUSO o escribió una canción: una PERSONA real enlazable
    (el campo de texto `Song.composers` queda solo de respaldo)."""
    song = models.ForeignKey("Song", on_delete=models.CASCADE,
                             related_name="composer_credits", verbose_name="canción")
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE,
                               related_name="composed_songs", verbose_name="persona")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "compositor de canción"
        verbose_name_plural = "compositores de canción"
        ordering = ["song", "person"]
        unique_together = (("song", "person"),)

    def __str__(self):
        return f"{self.person} — {self.song}"


class SongTranslation(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Traducción de la letra de una canción a UN idioma (una fila por idioma,
    estilo letras.com: la pestaña Traducción ofrece los idiomas disponibles)."""
    song = models.ForeignKey("Song", on_delete=models.CASCADE,
                             related_name="translations", verbose_name="canción")
    language = models.ForeignKey("catalogs.Language", on_delete=models.CASCADE,
                                 related_name="song_translations", verbose_name="idioma")
    text = models.TextField(verbose_name="traducción")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "traducción de canción"
        verbose_name_plural = "traducciones de canción"
        ordering = ["song", "language"]
        unique_together = (("song", "language"),)

    def __str__(self):
        return f"{self.song} · {self.language}"


class MusicLog(ModelBaseLog):
    """Log de obtención/procesamiento de datos de música (Deezer)."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de música"
        verbose_name_plural = "logs de música"
