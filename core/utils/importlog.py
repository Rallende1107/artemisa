"""Helper de logging de importación, genérico: escribe en el `*Log` (ModelBaseLog) que
le pases (cada app tiene el suyo: OtakuLog, MusicLog, GameLog). El nivel es el TEXTO
del choice `core.shared.models.choices.LogLevel` (su orden de declaración es la gravedad)."""
from core.shared.models.choices import LogLevel


def get_level(code: str) -> str:
    """Nivel válido del choice; lo desconocido cae a INFO."""
    return code if code in LogLevel.values else LogLevel.INFO


def niveles_desde(nivel: str) -> list[str]:
    """Niveles de gravedad IGUAL O MAYOR que `nivel` (orden del choice): `level__in=niveles_desde(LogLevel.WARNING)`."""
    valores = LogLevel.values
    return valores[valores.index(nivel):]


def log_to(log_model, code, process, message="", **extra):
    """Crea una fila de log en `log_model` (subclase de ModelBaseLog). `**extra` pasa
    directo a `.objects.create(...)` (p. ej. `user=`/`actor=` en UserLog)."""
    return log_model.objects.create(
        level=get_level(code), process=str(process)[:255], message=str(message)[:5000], **extra)


def sin_ruido(log_model, proceso, fn, *args, peticiones=None):
    """Corre un proceso largo y deja en el log SOLO lo que salió mal: si al terminar no hay ninguna
    fila de nivel >= WARNING («Advertencia»; ojo, la escala NO es la de Python), borra las
    informativas de esa ventana y deja una línea de resumen.
    Si hubo avisos o errores, NO borra nada: el log completo es justo lo que hay que mirar.

    `peticiones` es un invocable que devuelve el contador de peticiones HTTP del servicio
    (cada servicio tiene el suyo en `_stats`); si no se pasa, el resumen solo lleva el tiempo."""
    import time
    from django.utils import timezone
    desde = timezone.now()
    t0 = time.monotonic()
    p0 = peticiones() if peticiones else None
    resultado = fn(*args)
    medida = f"{time.monotonic() - t0:.1f} s"
    if p0 is not None:
        medida = f"{peticiones() - p0} peticiones · {medida}"
    de_la_tanda = log_model.objects.filter(timestamp__gte=desde)
    if de_la_tanda.filter(level__in=niveles_desde(LogLevel.WARNING)).exists():
        log_to(log_model, LogLevel.INFO, proceso, f"terminó con avisos: {resultado} · {medida}")
    else:
        borradas, _ = de_la_tanda.exclude(level__in=niveles_desde(LogLevel.WARNING)).delete()
        log_to(log_model, LogLevel.INFO, proceso, f"OK: {resultado} · {medida} (sin avisos; {borradas} líneas informativas limpiadas)")
    return resultado
