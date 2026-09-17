"""TODOS los choices del proyecto: valores fijos que no son catálogo (no tienen tabla).
Viven juntos para ver de un vistazo repetidos y duplicidades. Nombre = <Modelo><Campo> (`GameStatus`);
los compartidos llevan nombre propio (`RoleType`, `LogLevel`). Agrupados por app.
En la BD se guarda el NOMBRE de la constante en mayúsculas (`GameStatus.COMPLETED` → "COMPLETED")."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleType(models.TextChoices):
    """Familia de un rol (fija): agrupa los Role de cada app. Antes catálogo catalogs.RoleType."""
    STAFF = "STAFF", _("Personal")
    CAST = "CAST", _("Elenco")
    PRODUCTION = "PRODUCTION", _("Producción")
    MUSIC = "MUSIC", _("Música")
    CHARACTER = "CHARACTER", _("Personaje")
    MANGA = "MANGA", _("Manga")


class LogLevel(models.TextChoices):
    """Niveles de log (escala de Poseidón, NO la de Python). Se guardan como TEXTO; la GRAVEDAD es el ORDEN de
    declaración (de menor a mayor): para «desde WARNING» usar `core.utils.importlog.niveles_desde`."""
    NOT_SET = "NOT_SET", _("No establecido")
    TRACE = "TRACE", _("Rastreo")
    DEBUG = "DEBUG", _("Depuración")
    INFO = "INFO", _("Información")
    NOTICE = "NOTICE", _("Aviso")
    SUCCESS = "SUCCESS", _("Éxito")
    WARNING = "WARNING", _("Advertencia")
    ERROR = "ERROR", _("Error")
    CRITICAL = "CRITICAL", _("Crítico")
    FATAL = "FATAL", _("Error fatal")
    ALERT = "ALERT", _("Alerta")
    EMERGENCY = "EMERGENCY", _("Emergencia")


# ═══════════════════════════ catalogs ═══════════════════════════


class WebsiteType(models.TextChoices):
    """Campo Website.type."""
    STREAMING = "STREAMING", _("Streaming")
    DOWNLOAD = "DOWNLOAD", _("Descarga")
    STORE = "STORE", _("Tienda")
    DATABASE = "DATABASE", _("Base de datos")
    OTHER = "OTHER", _("Otro")


class ExternalSourceType(models.TextChoices):
    """Campo ExternalSource.type."""
    SOCIAL = "SOCIAL", _("Red social")
    MONETIZATION = "MONETIZATION", _("Monetización")
    COMMUNITY = "COMMUNITY", _("Comunidad")
    OFFICIAL = "OFFICIAL", _("Sitio oficial")
    DATABASE = "DATABASE", _("Base de datos")
    OTHER = "OTHER", _("Otro")


# ═══════════════════════════ games ═══════════════════════════


class CreatorType(models.TextChoices):
    """Campo Creator.type. VNDB manda co / in / ng: se traducen en `apps.games.services.vndb._creator_type`."""
    COMPANY = "COMPANY", _("Compañía")
    INDIVIDUAL = "INDIVIDUAL", _("Individual")
    AMATEUR = "AMATEUR", _("Grupo amateur")


class GameStatus(models.TextChoices):
    """Campo Game.status: VNDB devstatus: 0 completed · 1 developing · 2 abandoned; F95: ongoing/completed/abandoned/onhold"""
    UNKNOWN = "UNKNOWN", _("Desconocido")
    DEVELOPING = "DEVELOPING", _("En desarrollo")
    COMPLETED = "COMPLETED", _("Completado")
    ABANDONED = "ABANDONED", _("Abandonado")
    ONHOLD = "ONHOLD", _("En pausa")


class GameType(models.TextChoices):
    """Campo Game.type: lo decide la fuente: VNDB = novela visual; F95 = juego o novela visual"""
    VN = "VN", _("Novela visual")
    GAME = "GAME", _("Juego")
    COLLECTION = "COLLECTION", _("Colección")


# ═══════════════════════════ mailing ═══════════════════════════


class ContactMessageStatus(models.TextChoices):
    """Campo ContactMessage.status."""
    NEW = "NEW", _("Nuevo")
    READ = "READ", _("Leído")
    REPLIED = "REPLIED", _("Respondido")
    ARCHIVED = "ARCHIVED", _("Archivado")
    SPAM = "SPAM", _("Spam")


class EmailMessageStatus(models.TextChoices):
    """Campo EmailMessage.status. QUEUED = SEND_EMAIL apagado: guardado y pendiente de reenvío."""
    SENT = "SENT", _("Enviado")
    QUEUED = "QUEUED", _("En cola")
    ERROR = "ERROR", _("Error")
    SKIPPED = "SKIPPED", _("Omitido (sin plantilla)")


# ═══════════════════════════ otaku ═══════════════════════════


class AnimeSongType(models.TextChoices):
    """Campo AnimeSong.type."""
    OPENING = "OPENING", _("Opening")
    ENDING = "ENDING", _("Ending")
    INSERT = "INSERT", _("Insert song")


class MalCompanyKind(models.TextChoices):
    """Campo CompanyMAL.kind. En MAL las compañías (/anime/producer/<id>) y las revistas (/manga/magazine/<id>) tienen
    numeraciones SEPARADAS: «company 1» es Studio Pierrot y «magazine 1» es Big Comic Original."""
    COMPANY = "COMPANY", _("Compañía")
    MAGAZINE = "MAGAZINE", _("Revista")


class RelationMedia(models.TextChoices):
    """Campo Relation.from_type / to_type."""
    ANIME = "ANIME", _("Anime")
    MANGA = "MANGA", _("Manga")


class MalSeason(models.TextChoices):
    """Temporada de estreno (fija, de MAL): se calcula por el mes de la fecha de estreno si no viene dada."""
    WINTER = "WINTER", _("Invierno")
    SPRING = "SPRING", _("Primavera")
    SUMMER = "SUMMER", _("Verano")
    FALL = "FALL", _("Otoño")


class MalRating(models.TextChoices):
    """Clasificación por edad de MAL (fija)."""
    G = "G", _("G · Todas las edades")
    PG = "PG", _("PG · Niños")
    PG13 = "PG13", _("PG-13 · 13 años o más")
    R17 = "R17", _("R · 17+ (violencia y lenguaje)")
    RPLUS = "RPLUS", _("R+ · Desnudez moderada")
    RX = "RX", _("Rx · Hentai")


# ═══════════════════════════ system ═══════════════════════════


class TaskRunStatus(models.TextChoices):
    """Campo TaskRun.status."""
    QUEUED = "QUEUED", _("En cola")
    RUNNING = "RUNNING", _("Ejecutando")
    DONE = "DONE", _("Terminada")
    FAILED = "FAILED", _("Fallida")
    CANCELLED = "CANCELLED", _("Cancelada")


# ═══════════════════════════ users ═══════════════════════════


class UserActivityAction(models.TextChoices):
    """Campo UserActivity.action."""
    REGISTER = "REGISTER", _("creó su cuenta")
    LOGIN = "LOGIN", _("inició sesión")
    LOGOUT = "LOGOUT", _("cerró sesión")
    PROFILE = "PROFILE", _("actualizó su perfil")
    PASSWORD = "PASSWORD", _("cambió su contraseña")
    COLLECTION_ADD = "COLLECTION_ADD", _("añadió a su colección")
    COLLECTION_UPDATE = "COLLECTION_UPDATE", _("actualizó en su colección")
    COLLECTION_REMOVE = "COLLECTION_REMOVE", _("quitó de su colección")
    CONTACT = "CONTACT", _("envió un mensaje de contacto")


# ═══════════════════════════ collections ═══════════════════════════


class AnimeCollectionStatus(models.TextChoices):
    """Estado de una fila de colección (anime). El PRIMERO es el estado inicial al añadir."""
    PLAN_TO_WATCH = "PLAN_TO_WATCH", _("Por ver")
    AWAITING_RELEASE = "AWAITING_RELEASE", _("Esperando estreno")
    WATCHING = "WATCHING", _("Viendo")
    COMPLETED = "COMPLETED", _("Completado")
    ON_HOLD = "ON_HOLD", _("En pausa")
    DROPPED = "DROPPED", _("Abandonado")
    DISLIKED = "DISLIKED", _("No me gustó")
    DOWNLOADED = "DOWNLOADED", _("Descargado")
    PURCHASED = "PURCHASED", _("Comprado")


class MangaCollectionStatus(models.TextChoices):
    """Estado de una fila de colección (manga). El PRIMERO es el estado inicial al añadir."""
    PLAN_TO_READ = "PLAN_TO_READ", _("Por leer")
    READING = "READING", _("Leyendo")
    COMPLETED = "COMPLETED", _("Completado")
    AWAITING_CHAPTERS = "AWAITING_CHAPTERS", _("Esperando capítulos")
    ON_HOLD = "ON_HOLD", _("En pausa")
    DROPPED = "DROPPED", _("Abandonado")
    DISLIKED = "DISLIKED", _("No me gustó")
    DOWNLOADED = "DOWNLOADED", _("Descargado")
    PURCHASED = "PURCHASED", _("Comprado")


class SerieCollectionStatus(models.TextChoices):
    """Estado de una fila de colección (serie). El PRIMERO es el estado inicial al añadir."""
    PLAN_TO_WATCH = "PLAN_TO_WATCH", _("Por ver")
    AWAITING_PREMIERE = "AWAITING_PREMIERE", _("Esperando estreno")
    WATCHING = "WATCHING", _("Viendo")
    COMPLETED = "COMPLETED", _("Completada")
    ON_HOLD = "ON_HOLD", _("En pausa")
    DROPPED = "DROPPED", _("Abandonada")
    DISLIKED = "DISLIKED", _("No me gustó")
    DOWNLOADED = "DOWNLOADED", _("Descargada")
    PURCHASED = "PURCHASED", _("Comprada")


class MovieCollectionStatus(models.TextChoices):
    """Estado de una fila de colección (movie). El PRIMERO es el estado inicial al añadir."""
    PLAN_TO_WATCH = "PLAN_TO_WATCH", _("Por ver")
    WATCHED = "WATCHED", _("Vista")
    REWATCH = "REWATCH", _("Para revisitar")
    DROPPED = "DROPPED", _("Abandonada")
    DISLIKED = "DISLIKED", _("No me gustó")
    DOWNLOADED = "DOWNLOADED", _("Descargada")
    PURCHASED = "PURCHASED", _("Comprada")


class GameCollectionStatus(models.TextChoices):
    """Estado de una fila de colección (game). El PRIMERO es el estado inicial al añadir."""
    PLAN_TO_PLAY = "PLAN_TO_PLAY", _("Por jugar")
    AWAITING_RELEASE = "AWAITING_RELEASE", _("Esperando lanzamiento")
    PLAYING = "PLAYING", _("Jugando")
    COMPLETED = "COMPLETED", _("Completado")
    PLATINUM = "PLATINUM", _("Platinado")
    ON_HOLD = "ON_HOLD", _("En pausa")
    DROPPED = "DROPPED", _("Abandonado")
    DISLIKED = "DISLIKED", _("No me gustó")
    DOWNLOADED = "DOWNLOADED", _("Descargado")


class MusicCollectionStatus(models.TextChoices):
    """Estado de una fila de colección (music): Álbum, artista y canción de la colección. El PRIMERO es el estado inicial al añadir."""
    PLAN_TO_LISTEN = "PLAN_TO_LISTEN", _("Por escuchar")
    LISTENING = "LISTENING", _("Escuchando")
    LISTENED = "LISTENED", _("Escuchado")
    DROPPED = "DROPPED", _("Abandonado")
    DISLIKED = "DISLIKED", _("No me gustó")
    DOWNLOADED = "DOWNLOADED", _("Descargado")
    PURCHASED = "PURCHASED", _("Comprado")
