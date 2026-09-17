"""seed_series — datos iniciales de la app `series` (clasificaciones, géneros, tipos y roles (géneros, tipos y roles compartidos con películas)). Idempotente: se puede reejecutar cuando cambien los datos.
Datos en apps/series/management/data/seed_data.py; funciones compartidas en apps/catalogs/management/functions/funciones_seed.py.

    docker compose exec web python manage.py seed_series
"""
from django.core.management.base import BaseCommand

from apps.catalogs.management.functions.funciones_seed import paso, seed_defaults_names_description, seed_defaults_ratings, seed_defaults_roles
from apps.movies.management.data.seed_data import default_movie_serie_genres, default_movie_serie_roles, default_movie_serie_types  # compartidos
from apps.series.management.data.seed_data import default_serie_ratings
from apps.series.models import Genre, Rating, Role, Type


class Command(BaseCommand):
    help = "Datos iniciales de series (clasificaciones, géneros, tipos y roles (géneros, tipos y roles compartidos con películas))."

    def handle(self, *args, **opts):
        out = self.stdout
        out.write("[Series]")
        paso(out, "Clasificaciones", Rating, lambda: seed_defaults_ratings(Rating, default_serie_ratings))
        paso(out, "Géneros", Genre, lambda: seed_defaults_names_description(Genre, default_movie_serie_genres, True))
        paso(out, "Tipos", Type, lambda: seed_defaults_names_description(Type, default_movie_serie_types))
        paso(out, "Roles", Role, lambda: seed_defaults_roles(Role, default_movie_serie_roles))
        out.write("Series: listo.")
