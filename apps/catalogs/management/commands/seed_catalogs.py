"""seed_catalogs — datos iniciales de la app `catalogs` (calidades, formatos, sitios web, países, idiomas y tipos de relación). Idempotente: se puede reejecutar cuando cambien los datos.
Datos en apps/catalogs/management/data/seed_data.py; funciones compartidas en apps/catalogs/management/functions/funciones_seed.py.

    docker compose exec web python manage.py seed_catalogs
"""
from django.core.management.base import BaseCommand

from apps.catalogs.management.data.seed_data import default_common_countries, default_common_formats, default_common_languages, default_common_qualities, default_common_websites, default_relation_types
from apps.catalogs.management.functions.funciones_seed import paso, seed_defaults_calidades, seed_defaults_countries, seed_defaults_formatos, seed_defaults_languages, seed_defaults_names_description, seed_defaults_websites
from apps.catalogs.models import Country, Format, Language, Quality, RelationType, Website


class Command(BaseCommand):
    help = "Datos iniciales de catalogs (calidades, formatos, sitios web, países, idiomas y tipos de relación)."

    def handle(self, *args, **opts):
        out = self.stdout
        out.write("[Catálogos]")
        paso(out, "Calidades", Quality, lambda: seed_defaults_calidades(Quality, default_common_qualities))
        paso(out, "Formatos", Format, lambda: seed_defaults_formatos(Format, default_common_formats))
        paso(out, "Sitios web", Website, lambda: seed_defaults_websites(Website, default_common_websites))
        paso(out, "Países", Country, lambda: seed_defaults_countries(Country, default_common_countries))
        paso(out, "Idiomas", Language, lambda: seed_defaults_languages(Language, default_common_languages))
        paso(out, "Tipos de relación", RelationType, lambda: seed_defaults_names_description(RelationType, default_relation_types))
        out.write("Catálogos: listo.")
