"""system = app de ADMINISTRACIÓN (sidebar, dashboard, comandos de operación) y, desde 2026-09-10,
dueña de las TAREAS Celery: qué corrió, qué está corriendo, cancelarlas y programarlas.
Los catálogos de tipos viven en `catalogs` y las secciones de páginas en `pages`."""
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.choices import TaskRunStatus


class CloudFile(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Archivo de media que YA está en la nube (R2): su nombre relativo (la misma clave que en /media/).
    Lo escribe la tarea de subida; lo lee el storage para apuntar la URL a R2 (core/storage.py)."""
    name = models.CharField(verbose_name="archivo", max_length=500, unique=True)
    size = models.PositiveBigIntegerField(verbose_name="bytes", default=0)
    uploaded_at = models.DateTimeField(verbose_name="subido", auto_now_add=True)

    class Meta:
        verbose_name = "archivo en la nube"
        verbose_name_plural = "archivos en la nube"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.name


class ScheduledTask(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Tarea PROGRAMADA (beat): qué tarea, cada cuántos minutos O a qué hora del día, y si está
    activa. El despachador `apps.system.tasks.dispatch_scheduled_task` corre cada minuto desde
    CELERY_BEAT_SCHEDULE (core/celery.py), encola las que toquen y anota la última ejecución.
    Sin django-celery-beat: la programación vive en esta tabla y se gestiona en el panel."""
    name = models.CharField(verbose_name="nombre", max_length=120, unique=True)
    task = models.CharField(verbose_name="tarea", max_length=255)
    args = models.JSONField(verbose_name="argumentos", default=list, blank=True)
    kwargs = models.JSONField(verbose_name="argumentos con nombre", default=dict, blank=True)
    every_minutes = models.PositiveIntegerField(verbose_name="cada N minutos", default=30)
    at_time = models.TimeField(verbose_name="a esta hora", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    last_run_at = models.DateTimeField(verbose_name="última ejecución", null=True, blank=True)
    next_run_at = models.DateTimeField(verbose_name="próxima ejecución", null=True, blank=True)
    last_task_id = models.CharField(verbose_name="última tarea", max_length=64, blank=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "tarea programada"
        verbose_name_plural = "tareas programadas"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        if not self.at_time and not self.every_minutes:
            raise ValidationError(_("El intervalo tiene que ser de al menos 1 minuto."))

    # ------------------------------------------------------------ programación
    def _hoy_a_la_hora(self, ahora):
        local = timezone.localtime(ahora)
        return local.replace(hour=self.at_time.hour, minute=self.at_time.minute, second=0, microsecond=0)

    def toca(self, ahora=None):
        """¿Le toca correr ahora? Hora fija (manda si está): ya es la hora de hoy y hoy aún no
        corrió. Intervalo: pasaron N minutos desde la última."""
        ahora = ahora or timezone.now()
        if not self.is_active:
            return False
        if self.at_time:
            hoy = self._hoy_a_la_hora(ahora)
            if timezone.localtime(ahora) < hoy:
                return False
            return self.last_run_at is None or timezone.localtime(self.last_run_at) < hoy
        if self.every_minutes:
            return self.last_run_at is None or ahora >= self.last_run_at + timedelta(minutes=self.every_minutes)
        return False

    def proxima(self, desde=None):
        desde = desde or timezone.now()
        if self.at_time:
            hoy = self._hoy_a_la_hora(desde)
            return hoy if timezone.localtime(desde) < hoy else hoy + timedelta(days=1)
        if self.every_minutes:
            return desde + timedelta(minutes=self.every_minutes)
        return None

    def kwargs_efectivos(self):
        """Los argumentos con nombre que recibe la tarea (el JSON tal cual). Los lotes de datos NO llevan
        cantidad aquí: la toman del cursor de lote (ImportCursor), junto con el próximo id."""
        return dict(self.kwargs or {})

    def encolar(self, ahora=None):
        """Encola la tarea AHORA con sus argumentos (la usa el despachador y «Ejecutar ahora»)."""
        from celery import current_app
        ahora = ahora or timezone.now()
        resultado = current_app.send_task(self.task, args=list(self.args or []), kwargs=self.kwargs_efectivos())
        self.marcar_lanzada(ahora, getattr(resultado, "id", "") or "")
        return resultado

    def marcar_lanzada(self, ahora, task_id=""):
        self.last_run_at = ahora
        self.last_task_id = task_id or ""
        self.next_run_at = self.proxima(ahora)
        self.save(update_fields=["last_run_at", "last_task_id", "next_run_at"])

    def save(self, *args, **kwargs):
        if self.next_run_at is None or not self.is_active:
            self.next_run_at = self.proxima(self.last_run_at) if self.is_active else None
        super().save(*args, **kwargs)


FUENTES = {"deezer": "Deezer", "vndb": "VNDB", "music": "Deezer", "otaku": "MAL / AniList",
           "games": "VNDB", "system": "Sistema"}


class TaskRun(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Una EJECUCIÓN de tarea Celery (importación, post-proceso, programada): qué, con qué argumentos,
    quién la lanzó y cómo terminó. Se llena sola con las señales de Celery (core/celery.py); el panel
    la lista, la cancela (patrón Poseidon TaskCancellation, aquí como bandera) y la limpia."""

    task_id = models.CharField(verbose_name="id de tarea", max_length=64, unique=True)
    name = models.CharField(verbose_name="tarea", max_length=255, db_index=True)          # apps.music.tasks.import_artist_task
    args = models.TextField(verbose_name="argumentos", blank=True)
    status = models.CharField(verbose_name="estado", max_length=12, choices=TaskRunStatus.choices, default=TaskRunStatus.QUEUED, db_index=True)
    cancel_requested = models.BooleanField(verbose_name="cancelación pedida", default=False)
    progress_done = models.PositiveIntegerField(verbose_name="hechos", default=0)       # lo escribe la tarea larga al avanzar
    progress_total = models.PositiveIntegerField(verbose_name="total", default=0)       # 0 = la tarea no informa avance
    result = models.TextField(verbose_name="resultado / error", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="task_runs", verbose_name="lanzada por")
    queued_at = models.DateTimeField(verbose_name="encolada", auto_now_add=True)
    started_at = models.DateTimeField(verbose_name="inicio", null=True, blank=True)
    finished_at = models.DateTimeField(verbose_name="fin", null=True, blank=True)

    class Meta:
        verbose_name = "tarea"
        verbose_name_plural = "tareas"
        ordering = ["-queued_at"]

    def __str__(self):
        return f"{self.corto} #{self.task_id[:8]}"

    @property
    def avance(self):
        """«X de N (P %)» si la tarea informa su avance; si no, vacío."""
        if not self.progress_total:
            return ""
        pct = min(100, round(self.progress_done * 100 / self.progress_total))
        return f"{self.progress_done:,} de {self.progress_total:,} ({pct} %)".replace(",", ".")

    @property
    def corto(self):
        """Nombre legible («Importar artista · Deezer»); si la tarea no está en la lista, el de la función."""
        from apps.system.registro import nombre_tarea
        return nombre_tarea(self.name)

    @property
    def fuente(self):
        partes = self.name.split(".")
        return FUENTES.get(partes[1] if len(partes) > 1 else "", "—")

    @property
    def duracion(self):
        """Segundos entre inicio y fin (o hasta ahora si sigue corriendo)."""
        if not self.started_at:
            return None
        fin = self.finished_at or timezone.now()
        return round((fin - self.started_at).total_seconds(), 1)

    @property
    def activa(self):
        return self.status in (TaskRunStatus.QUEUED, TaskRunStatus.RUNNING)


class ImportCursor(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Por dónde va el LOTE de una fuente y tipo (Deezer artista, MAL anime, VNDB juego…): el próximo id
    que tocará. Lo mueven el lote programado y un rango manual que continúe desde él; una importación
    suelta o una búsqueda por nombre (ids altísimos) NO lo tocan, así el beat no salta. Editable en el panel."""
    FUENTES = (("anilist", "AniList"), ("deezer", "Deezer"), ("vndb", "VNDB"))
    source = models.CharField(verbose_name="fuente", max_length=20, choices=FUENTES)
    type = models.CharField(verbose_name="tipo", max_length=30)
    next_id = models.PositiveIntegerField(verbose_name="próximo id", default=1)
    batch_size = models.PositiveIntegerField(verbose_name="cantidad por lote", default=100)
    is_active = models.BooleanField(verbose_name="activo", default=True)      # borrado LÓGICO desde el panel
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "cursor de lote"
        verbose_name_plural = "cursores de lote"
        unique_together = (("source", "type"),)
        ordering = ["source", "type"]

    def __str__(self):
        return f"{self.get_source_display()} · {self.type} → #{self.next_id}"

    TAREA_LOTE = {"anilist": "apps.otaku.tasks.import_anilist_next_batch_task",
                  "deezer": "apps.music.tasks.import_deezer_next_batch_task",
                  "vndb": "apps.games.tasks.import_vndb_next_batch_task"}

    def lanzar(self):
        """Encola AHORA el siguiente lote de esta fuente y tipo con su cantidad («Lanzar lote ahora»)."""
        from celery import current_app
        return current_app.send_task(self.TAREA_LOTE[self.source], kwargs={"kind": self.type, "cantidad": self.batch_size})
