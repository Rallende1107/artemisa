"""seed_companies — datos iniciales de la app `companies` (las compañías por defecto de cine y TV). Idempotente: se
puede reejecutar cuando cambien los datos. Va ANTES que seed_movies y seed_series, que ya no siembran compañías.

    docker compose exec web python manage.py seed_companies
"""
from django.core.management.base import BaseCommand

from apps.catalogs.management.functions.funciones_seed import paso, seed_default_companies
from apps.catalogs.models import Country
from apps.companies.management.data.seed_data import default_companies
from apps.companies.models import Company


class Command(BaseCommand):
    help = "Datos iniciales de companies (compañías por defecto de cine y TV)."

    def handle(self, *args, **opts):
        out = self.stdout
        out.write("[Compañías]")
        paso(out, "Compañías", Company, lambda: seed_default_companies(Company, Country, default_companies))
        out.write("Compañías: listo.")
