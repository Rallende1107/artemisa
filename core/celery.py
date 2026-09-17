"""
App Celery de Artemisa (importaciones en background y tareas programadas, como en Hades/Poseidon).
El broker/worker se levanta con Docker (Redis). Sin worker, los servicios corren síncronos por
fallback (ver core/shared/views/imports.py: run_task).

· Cada ejecución queda en system.TaskRun gracias a las SEÑALES de abajo (encolada → ejecutando →
  terminada / fallida / cancelada). El panel las lista y las cancela.
· BEAT: una sola entrada fija, `dispatch_scheduled_task` cada minuto, que lee la tabla
  system.ScheduledTask y encola lo que toque. La programación se gestiona en el panel.
"""
import os

from celery import Celery
from celery.signals import before_task_publish, task_failure, task_postrun, task_prerun, task_revoked, task_unknown
from core.shared.models.choices import TaskRunStatus

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("artemisa")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "tareas-programadas": {"task": "apps.system.tasks.dispatch_scheduled_task", "schedule": 60.0},
}


# ----------------------------- registro de ejecuciones (system.TaskRun) -----------------------------
def _seguro(fn):
    """Las señales NUNCA rompen una tarea: si la BD no está lista o falla, se ignora."""
    def envuelta(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:  # noqa: BLE001
            return None
    return envuelta


def _run():
    from apps.system.models import TaskRun
    return TaskRun


def _sin_registro(nombre):
    """Tareas que NO dejan fila en Ejecuciones: las internas de Celery y el despachador de beat, que corre
    cada minuto y solo encola a otras (esas sí se registran)."""
    nombre = nombre or ""
    return nombre.startswith("celery.") or nombre.endswith(".dispatch_scheduled_task")


@before_task_publish.connect
@_seguro
def _encolada(sender=None, headers=None, body=None, **kw):
    """Al publicar (web o despachador): fila «en cola». `headers` trae id, nombre y argsrepr."""
    h = headers or {}
    if not h.get("id") or _sin_registro(sender or h.get("task", "")):
        return
    args = ", ".join(x for x in (h.get("argsrepr", ""), h.get("kwargsrepr", "")) if x and x not in ("()", "{}"))
    _run().objects.get_or_create(task_id=h["id"], defaults={"name": sender or h.get("task", ""), "args": args})


@task_prerun.connect
@_seguro
def _empieza(task_id=None, task=None, args=None, kwargs=None, **kw):
    from django.utils import timezone
    nombre = getattr(task, "name", "") or ""
    if _sin_registro(nombre):
        return
    texto = ", ".join(x for x in (repr(tuple(args or ())) if args else "", repr(dict(kwargs or {})) if kwargs else "") if x)
    fila, creada = _run().objects.get_or_create(task_id=task_id, defaults={"name": nombre, "args": texto})
    fila.status = TaskRunStatus.RUNNING
    fila.started_at = timezone.now()
    if creada is False and not fila.args:
        fila.args = texto
    fila.save(update_fields=["status", "started_at", "args"])


@task_postrun.connect
@_seguro
def _termina(task_id=None, task=None, retval=None, state=None, **kw):
    from django.utils import timezone
    fila = _run().objects.filter(task_id=task_id).first()
    if not fila:
        return
    if fila.cancel_requested:
        fila.status = TaskRunStatus.CANCELLED
    elif state == "FAILURE" or fila.status == TaskRunStatus.FAILED:
        fila.status = TaskRunStatus.FAILED
    else:
        fila.status = TaskRunStatus.DONE
        fila.result = repr(retval)[:2000] if retval is not None else ""
    fila.finished_at = timezone.now()
    fila.save(update_fields=["status", "result", "finished_at"])


@task_failure.connect
@_seguro
def _falla(task_id=None, exception=None, **kw):
    from django.utils import timezone
    _run().objects.filter(task_id=task_id).update(
        status=TaskRunStatus.FAILED, result=f"{type(exception).__name__}: {exception}"[:2000], finished_at=timezone.now())


@task_unknown.connect
@_seguro
def _desconocida(name=None, id=None, **kw):
    """El worker recibió una tarea que NO conoce (se agregó código y el worker no se reinició): Celery la descarta, así
    que la fila quedaría «en cola» para siempre y bloquearía «ya hay una en curso». Se marca fallida y se dice por qué."""
    from django.utils import timezone
    _run().objects.filter(task_id=id).update(
        status=TaskRunStatus.FAILED, finished_at=timezone.now(),
        result=f"el worker no conoce la tarea {name}: reinicia el worker (docker compose restart worker) y vuelve a lanzarla")


@task_revoked.connect
@_seguro
def _revocada(request=None, terminated=None, signum=None, expired=None, **kw):
    from django.utils import timezone
    _run().objects.filter(task_id=getattr(request, "id", None)).update(
        status=TaskRunStatus.CANCELLED, finished_at=timezone.now(),
        result="terminada por el usuario" if terminated else "cancelada antes de empezar")
