"""clear_migrations — UNA acción: borra las migraciones (`0*.py` y su bytecode) de las apps del proyecto. No genera
ni migra: generar es `makemigrations`, migrar es `init`.

  docker compose exec web python manage.py clear_migrations
  docker compose exec web python manage.py makemigrations
  docker compose exec web python manage.py clear_migrations --app collections   # una app"""
import os

from django.apps import apps as registry
from django.core.management.base import BaseCommand, CommandError


def apps_del_proyecto():
    """Apps propias (apps.*) con carpeta migrations/."""
    return [c for c in registry.get_app_configs()
            if c.name.startswith("apps.") and os.path.isdir(os.path.join(c.path, "migrations"))]


class Command(BaseCommand):
    help = "Borra las migraciones (0*.py) de las apps del proyecto. Solo eso: generar es makemigrations."

    def add_arguments(self, parser):
        parser.add_argument("--app", action="append", default=[],
                            help="Limitar a esta app (repetible). Por defecto, todas las apps.*")

    def handle(self, *args, **opts):
        configs = apps_del_proyecto()
        if opts["app"]:
            faltan = set(opts["app"]) - {c.label for c in configs}
            if faltan:
                raise CommandError(f"App(s) desconocida(s): {', '.join(sorted(faltan))}")
            configs = [c for c in configs if c.label in opts["app"]]

        self.stdout.write(("[Borrando migraciones]"))
        borradas = 0
        for c in configs:
            carpeta = os.path.join(c.path, "migrations")
            for f in sorted(os.listdir(carpeta)):
                if f[:4].isdigit() and f.endswith(".py"):
                    os.remove(os.path.join(carpeta, f)); borradas += 1
                    self.stdout.write(f"  {c.label}/migrations/{f}")
            # cache de bytecode de las borradas, para que Django no vea fantasmas
            pyc = os.path.join(carpeta, "__pycache__")
            if os.path.isdir(pyc):
                for f in os.listdir(pyc):
                    if f[:4].isdigit():
                        os.remove(os.path.join(pyc, f))
        self.stdout.write(f"  {borradas} archivo(s) borrado(s). Ahora: makemigrations.")
