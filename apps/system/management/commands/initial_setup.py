"""initial_setup — deja el sitio listo en un solo comando (idempotente, se puede re-correr):
migra (con candado de Postgres: nadie más migra a la vez), corre el seed de CADA app en orden y, al final, pide el
superusuario si aún no hay ninguno (interactivo con terminal; sin ella, DJANGO_SUPERUSER_USERNAME/PASSWORD/EMAIL).

    docker compose exec web python manage.py initial_setup            # producción y desarrollo
    docker compose exec web python manage.py initial_setup --dev      # además admin/admin y rallende/rallende123
    docker compose exec web python manage.py initial_setup --demo     # además el catálogo de demostración

Estáticos y backup son comandos aparte (`statics`, `backup`). Las migraciones NO se generan aquí: mientras el
esquema cambie, `clear_migrations` + `makemigrations` (desarrollo); si a una app le falta su 0001, se detiene.
"""
import os
import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


CANDADO = 800_001   # pg_advisory_lock del proyecto: dos initial_setup a la vez se turnan
SEEDS = ["seed_system", "seed_pages", "seed_catalogs", "seed_companies", "seed_movies", "seed_series", "seed_music", "seed_games", "seed_otaku", "seed_mailing"]


class Command(BaseCommand):
    help = "Migra, siembra cada app y pide el superusuario (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument("--dev", action="store_true", help="crea admin/admin y rallende/rallende123 (claves de desarrollo)")
        parser.add_argument("--demo", action="store_true", help="siembra además el catálogo demo (seed_demo)")

    def handle(self, *args, **opts):
        self._exigir_migraciones()
        self.stdout.write("[Migraciones]")
        self._migrar()
        for seed in SEEDS + (["seed_demo"] if opts["demo"] else []):
            call_command(seed)
        if opts["dev"]:
            self._usuarios_dev()
        self._superusuario()
        self.stdout.write("initial_setup completo: el sitio quedó listo.")

    def _exigir_migraciones(self):
        from django.apps import apps as registry
        faltan = [c.label for c in registry.get_app_configs()
                  if c.name.startswith("apps.") and list(c.get_models()) and os.path.isdir(os.path.join(c.path, "migrations"))
                  and not any(f.startswith("0001") for f in os.listdir(os.path.join(c.path, "migrations")))]
        if faltan:
            raise CommandError("Faltan migraciones en: " + ", ".join(faltan) + ". Genéralas: clear_migrations y makemigrations (en Docker).")

    def _migrar(self):
        if connection.vendor != "postgresql":
            call_command("migrate", interactive=False, verbosity=0)
            return
        with connection.cursor() as cur:
            cur.execute("SELECT pg_advisory_lock(%s)", [CANDADO])
            try:
                call_command("migrate", interactive=False, verbosity=0)
            finally:
                cur.execute("SELECT pg_advisory_unlock(%s)", [CANDADO])
        self.stdout.write("  migraciones aplicadas")

    def _usuarios_dev(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.stdout.write("[Usuarios de desarrollo]")
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@frikiverso.local", "admin"); self.stdout.write("  admin / admin")
        if not User.objects.filter(username="rallende").exists():
            User.objects.create_user("rallende", "rallende@frikiverso.local", "rallende123"); self.stdout.write("  rallende / rallende123")

    def _superusuario(self):
        """Al final, como Kiwi TCM: si no hay superusuario, se pide aquí."""
        from django.contrib.auth import get_user_model
        self.stdout.write("[Superusuario]")
        if get_user_model().objects.filter(is_superuser=True).exists():
            self.stdout.write("  ya existe uno; no se pide otro")
            return
        if os.environ.get("DJANGO_SUPERUSER_USERNAME") and os.environ.get("DJANGO_SUPERUSER_PASSWORD"):
            call_command("createsuperuser", interactive=False); self.stdout.write("  creado desde DJANGO_SUPERUSER_*")
        elif sys.stdin.isatty():
            try:
                call_command("createsuperuser")
            except (EOFError, KeyboardInterrupt, SystemExit):
                self.stdout.write("\n  sin entrada interactiva: créalo luego con createsuperuser")
        else:
            self.stdout.write("  sin terminal ni DJANGO_SUPERUSER_*: créalo luego con `createsuperuser` o repite con --dev")
