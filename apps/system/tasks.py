"""Tareas Celery de SISTEMA: el despachador de tareas programadas (beat) y las limpiezas.

`dispatch_scheduled_task` corre cada minuto (CELERY_BEAT_SCHEDULE en core/celery.py), mira la tabla
ScheduledTask y encola por nombre las que toquen. Así la programación vive en el panel, sin
django-celery-beat."""
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.system.models import ScheduledTask, TaskRun
from core.shared.models.choices import LogLevel, TaskRunStatus
from core.utils.importlog import niveles_desde


@shared_task
def dispatch_scheduled_task():
    """Encola las tareas programadas que toquen ahora. Devuelve cuántas lanzó."""
    ahora = timezone.now()
    lanzadas = 0
    for programada in ScheduledTask.objects.filter(is_active=True):
        if not programada.toca(ahora):
            continue
        programada.encolar(ahora)
        lanzadas += 1
    return lanzadas


@shared_task
def purge_task_runs_task(days=7):
    """Borra las ejecuciones terminadas, fallidas o canceladas de hace más de `days` días."""
    limite = timezone.now() - timedelta(days=days)
    borradas, _ = (TaskRun.objects.exclude(status__in=(TaskRunStatus.QUEUED, TaskRunStatus.RUNNING))
                   .filter(queued_at__lt=limite).delete())
    return borradas


@shared_task
def purge_info_logs_task(days=7):
    """Borra las líneas INFORMATIVAS (nivel bajo WARNING: debug, info, notice, success) de los doce logs con más de `days` días.
    Los avisos y errores se quedan: son lo que hay que mirar."""
    from apps.system.registro import LOGS
    limite = timezone.now() - timedelta(days=days)
    total = 0
    for _label, _url, modelo in LOGS:
        borradas, _ = modelo.objects.filter(timestamp__lt=limite).exclude(level__in=niveles_desde(LogLevel.WARNING)).delete()
        total += borradas
    return total


# ----------------------------- imágenes pendientes (URL → archivo / nube) -----------------------------
@shared_task
def download_pending_images_task(cantidad=100):
    """Baja hasta `cantidad` imágenes pendientes de TODAS las tablas de imágenes (programable: N al día).
    Siempre a disco local; la subida a R2 es otra tarea (`upload_pending_to_cloud_task`)."""
    from core.shared.tasks.images import descargar_pendientes
    r = descargar_pendientes(tope=cantidad)
    return f"{r['ok']} descargadas, {r['fallos']} fallos"


@shared_task
def download_images_batch_task(etiqueta, cantidad=0):
    """Descarga `cantidad` imágenes pendientes de UNA tabla («otaku.AnimeImage»; 0 = todas), por lotes, cancelable y con
    su log en la app de la tabla (vistas «Descargar imágenes» de cada lista)."""
    from core.shared.tasks.images import descargar_lote
    return descargar_lote(etiqueta, cantidad)


@shared_task
def download_images_task(app_label, model_name, ids):
    """Baja las imágenes pendientes de las filas marcadas en una lista (acción masiva)."""
    from django.apps import apps as registro
    from core.shared.tasks.images import descargar_pendientes
    modelo = registro.get_model(app_label, model_name)
    r = descargar_pendientes(modelo=modelo, ids=list(ids), tope=len(ids))
    return f"{r['ok']} descargadas, {r['fallos']} fallos"


# ----------------------------- nube (R2): subir lo que ya está en disco -----------------------------
@shared_task
def upload_pending_to_cloud_task(cantidad=100):
    """Sube hasta `cantidad` archivos de media locales que aún no están en R2 (programable: 100 al día,
    el tope de subidas de R2). Sin USE_R2 no hace nada."""
    from core.shared.tasks.cloud import subir_pendientes
    r = subir_pendientes(tope=cantidad)
    return f"{r['ok']} subidas, {r['fallos']} fallos"


@shared_task
def upload_to_cloud_task(app_label, model_name, ids):
    """Sube a R2 los archivos de las filas marcadas en una lista (acción masiva «Subir a la nube»)."""
    from django.apps import apps as registro
    from core.shared.tasks.cloud import subir_pendientes
    modelo = registro.get_model(app_label, model_name)
    r = subir_pendientes(modelo=modelo, ids=list(ids), tope=len(ids))
    return f"{r['ok']} subidas, {r['fallos']} fallos"
