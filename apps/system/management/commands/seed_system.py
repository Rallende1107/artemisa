"""seed_system — datos iniciales de SISTEMA (van primero en `initial_setup`): fuentes externas, tareas
programadas y cursores de lote.
Datos y lógica en apps/system/management/functions/initial_runner.py. Idempotente.
"""
from django.core.management.base import BaseCommand

from apps.system.management.functions.initial_runner import run


class Command(BaseCommand):
    help = "Carga los datos iniciales de sistema (log levels, tipos, fuentes externas)."

    def handle(self, *args, **kwargs):
        self.stdout.write("[Sistema]")
        run(stdout=self.stdout, style=self.style)
        self.stdout.write(f"  tareas programadas: {seed_scheduled_tasks()} nuevas")
        self.stdout.write(f"  cursores de lote: {seed_import_cursors()} nuevos")
        self.stdout.write(("Sistema: listo."))


# ----------------------------- tareas programadas (beat) por defecto -----------------------------
PROGRAMADAS = [
    # (nombre, tarea, cada N minutos, a esta hora, kwargs, activa)  — la hora manda sobre el intervalo.
    # TODAS nacen APAGADAS (pedido de René): beat no corre nada hasta que se encienda a mano en el panel.
    # Los lotes de datos no llevan cantidad: el próximo id y la cantidad viven en su cursor (ImportCursor).
    ("Obtener datos · Deezer: géneros", "apps.music.tasks.import_all_genres_task", None, "02:50", {}, False),
    ("Obtener datos · Deezer: artistas nuevos (lote)", "apps.music.tasks.import_deezer_next_batch_task", None, "03:00", {"kind": "artista"}, False),
    ("Obtener datos · VNDB: juegos nuevos (lote)", "apps.games.tasks.import_vndb_next_batch_task", None, "04:20", {"kind": "juego"}, False),
    ("Re-obtener juegos VNDB viejos (más de 30 días)", "apps.games.tasks.refresh_stale_games_task", None, "04:40", {"days": 30, "cantidad": 20}, False),
    ("Descargar imágenes pendientes (a disco local)", "apps.system.tasks.download_pending_images_task", None, "05:00", {"cantidad": 2000}, False),
    ("Subir imágenes a R2 (solo con USE_R2=1)", "apps.system.tasks.upload_pending_to_cloud_task", None, "05:30", {"cantidad": 100}, False),
    ("Procesar pendientes · Deezer", "apps.music.tasks.process_music_pending_task", 30, None, {}, False),
    ("Procesar pendientes · MAL", "apps.otaku.tasks.process_otaku_pending_task", 30, None, {}, False),
    ("Procesar pendientes · VNDB", "apps.games.tasks.process_games_pending_task", 30, None, {}, False),
    ("Limpiar tareas terminadas (7 días)", "apps.system.tasks.purge_task_runs_task", None, "04:00", {}, False),
    ("Limpiar logs informativos (7 días)", "apps.system.tasks.purge_info_logs_task", None, "04:10", {}, False),
]

# Cursores de lote: por dónde va cada fuente y tipo, y cuántos trae por lote. Nacen en 1 y 100; se editan en el panel.
# Solo los tipos con lanzador manual: en Deezer el artista (la discografía viene con él; los géneros no llevan id),
# en VNDB los cuatro tipos (juego, creador, lanzamiento, personaje). MAL no lleva: entra solo por dump.
CURSORES = [("deezer", "artista"),
            ("vndb", "juego"), ("vndb", "creador"), ("vndb", "lanzamiento"), ("vndb", "personaje")]


def seed_import_cursors():
    """Crea los cursores que falten (next_id 1, cantidad 100). No pisa los que René ya movió."""
    from apps.system.models import ImportCursor
    creados = 0
    for source, kind in CURSORES:
        _, creado = ImportCursor.objects.get_or_create(source=source, type=kind, defaults={"next_id": 1, "batch_size": 100})
        creados += int(creado)
    return creados


def seed_scheduled_tasks():
    """Crea las programadas por defecto si no existen (no pisa lo que René ya ajustó)."""
    from datetime import time as _time
    from apps.system.models import ScheduledTask
    creadas = 0
    for nombre, tarea, cada, hora, kwargs, activa in PROGRAMADAS:
        _, creada = ScheduledTask.objects.get_or_create(name=nombre, defaults={
            "task": tarea, "every_minutes": cada or 1440, "kwargs": kwargs,
            "at_time": _time(*map(int, hora.split(":"))) if hora else None, "is_active": activa})
        creadas += int(creada)
    return creadas
