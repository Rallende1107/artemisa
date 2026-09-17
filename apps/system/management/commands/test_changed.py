"""Corre los tests de humo SOLO de las apps modificadas y deja un reporte en `dump/tests/`.

    docker compose exec web python manage.py test_changed              # apps con archivos más nuevos que el último reporte
    docker compose exec web python manage.py test_changed --app otaku  # una app concreta (repetible)
    docker compose exec web python manage.py test_changed --all        # las 12

«Modificada» = algún archivo de `apps/<app>/` (o de `core/`, que cuenta para todas) cambió después de la última
corrida; la marca es `dump/tests/.ultima`. Un comando, una acción: no migra ni toca la base real (usa la de test,
que se crea y destruye en cada corrida: así nunca queda vieja tras un reinicio de migraciones).
"""
import io
import os
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.utils import get_runner


CARPETA = Path(settings.BASE_DIR) / "dump" / "tests"
MARCA = CARPETA / ".ultima"


def _apps_proyecto():
    return sorted(a.label for a in django_apps.get_app_configs() if a.name.startswith("apps."))


def _mas_nuevo(carpeta, desde):
    for raiz, _d, archivos in os.walk(carpeta):
        if "__pycache__" in raiz or "migrations" in raiz:
            continue
        for f in archivos:
            if os.path.getmtime(os.path.join(raiz, f)) > desde:
                return True
    return False


class Command(BaseCommand):
    help = "Tests de humo por app (solo las modificadas) con reporte en dump/tests/."

    def add_arguments(self, parser):
        parser.add_argument("--app", action="append", default=[], help="app concreta (repetible)")
        parser.add_argument("--all", action="store_true", help="todas las apps")

    def handle(self, *args, **opts):
        base = Path(settings.BASE_DIR)
        todas = _apps_proyecto()
        if opts["all"]:
            elegidas = todas
        elif opts["app"]:
            malas = [a for a in opts["app"] if a not in todas]
            if malas:
                self.stderr.write(f"apps desconocidas: {', '.join(malas)} · válidas: {', '.join(todas)}")
                sys.exit(2)
            elegidas = opts["app"]
        else:
            desde = MARCA.stat().st_mtime if MARCA.exists() else 0
            if _mas_nuevo(base / "core", desde) or _mas_nuevo(base / "templates", desde):
                elegidas = todas          # core/ o templates/ afectan a todas
            else:
                elegidas = [a for a in todas if _mas_nuevo(base / "apps" / a, desde)]
        if not elegidas:
            self.stdout.write("Sin cambios desde la última corrida: nada que probar.")
            return

        CARPETA.mkdir(parents=True, exist_ok=True)
        Runner = get_runner(settings)
        lineas = [f"# Tests · {time.strftime('%Y-%m-%d %H:%M:%S')}", "", f"Apps: {', '.join(elegidas)}", ""]
        fallos_total = 0
        for app in elegidas:
            salida = io.StringIO()
            t0 = time.time()
            with redirect_stdout(salida), redirect_stderr(salida):
                fallos = Runner(verbosity=2, keepdb=False, interactive=False).run_tests([f"apps.{app}"])
            fallos_total += fallos
            estado = "OK" if fallos == 0 else f"FALLA ({fallos})"
            self.stdout.write(f"{app:12} {estado:12} {time.time() - t0:5.1f}s")
            lineas += [f"## {app} · {estado} · {time.time() - t0:.1f}s", "", "```", salida.getvalue().strip(), "```", ""]
        nombre = CARPETA / f"{time.strftime('%Y%m%d-%H%M%S')}-{'todas' if elegidas == todas else '-'.join(elegidas)}.md"
        nombre.write_text("\n".join(lineas), encoding="utf-8")
        MARCA.touch()
        self.stdout.write(f"Reporte: {nombre.relative_to(base)}")
        if fallos_total:
            sys.exit(1)
