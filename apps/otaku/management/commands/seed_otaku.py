"""seed_otaku — datos iniciales de la app `otaku` (años, roles, géneros, temas, demografías, tipos, estados y fuentes). Idempotente: se puede reejecutar cuando cambien los datos.
Datos en apps/otaku/management/data/seed_data.py; funciones compartidas en apps/catalogs/management/functions/funciones_seed.py.

    docker compose exec web python manage.py seed_otaku
"""
from django.core.management.base import BaseCommand

from apps.catalogs.management.functions.funciones_seed import paso, seed_default_otaku_years, seed_defaults_names_description, seed_defaults_roles
from apps.otaku.management.data.seed_data import default_otaku_demographics, default_otaku_genres, default_otaku_roles, default_otaku_sources, default_otaku_status, default_otaku_themes, default_otaku_types
from apps.otaku.models import Demographic, Genre, Role, Source, Status, Theme, Type, Year


class Command(BaseCommand):
    help = "Datos iniciales de otaku (años, roles, géneros, temas, demografías, tipos, estados y fuentes)."

    def handle(self, *args, **opts):
        out = self.stdout
        out.write("[Otaku]")
        paso(out, "Años", Year, lambda: seed_default_otaku_years(Year))
        paso(out, "Roles", Role, lambda: seed_defaults_roles(Role, default_otaku_roles))
        paso(out, "Géneros", Genre, lambda: seed_defaults_names_description(Genre, default_otaku_genres, True))
        paso(out, "Temas", Theme, lambda: seed_defaults_names_description(Theme, default_otaku_themes))
        paso(out, "Demografías", Demographic, lambda: seed_defaults_names_description(Demographic, default_otaku_demographics))
        paso(out, "Tipos", Type, lambda: seed_defaults_names_description(Type, default_otaku_types))
        paso(out, "Estados", Status, lambda: seed_defaults_names_description(Status, default_otaku_status))
        paso(out, "Fuentes", Source, lambda: seed_defaults_names_description(Source, default_otaku_sources))
        out.write("Otaku: listo.")
