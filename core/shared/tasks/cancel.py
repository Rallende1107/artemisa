"""Cancelación COOPERATIVA de tareas Celery (patrón Poseidon: TaskCancellation; aquí la bandera
vive en system.TaskRun). Un bucle largo (rango de ids, álbumes de un artista…) llama a `cancelado()`
entre pasos y, si el usuario pidió cancelar desde el panel, se detiene solo. El `revoke` de Celery
solo alcanza a las tareas que aún no empezaron; para las que ya corren, esto es lo que funciona."""
from celery import current_task


def tarea_actual_id():
    """id de la tarea Celery en curso (también en modo síncrono), o None fuera de una tarea."""
    try:
        return current_task.request.id if current_task else None
    except Exception:  # noqa: BLE001 — fuera de Celery no hay request
        return None


def avance(hechos: int, total: int) -> None:
    """Anota «hechos de total» en la TaskRun de la tarea en curso (una UPDATE; fuera de Celery no hace nada).
    Llamar entre lotes, no por fila."""
    task_id = tarea_actual_id()
    if not task_id:
        return
    from apps.system.models import TaskRun
    TaskRun.objects.filter(task_id=task_id).update(progress_done=max(int(hechos), 0), progress_total=max(int(total), 0))


def cancelado():
    """¿Pidieron cancelar la tarea en curso? Consulta barata; llamar entre pasos, no por fila."""
    task_id = tarea_actual_id()
    if not task_id:
        return False
    from apps.system.models import TaskRun
    return TaskRun.objects.filter(task_id=task_id, cancel_requested=True).exists()


def reentregada():
    """¿Este mensaje ya se había entregado antes (el worker murió a mitad y el broker lo volvió a repartir)?
    Con CELERY_TASK_ACKS_LATE la tarea se reintenta con sus argumentos ORIGINALES; los bucles largos con
    cursor lo usan para seguir por donde iban y no repetir desde el principio."""
    try:
        return bool((current_task.request.delivery_info or {}).get("redelivered"))
    except Exception:  # noqa: BLE001 — fuera de Celery no hay request
        return False
