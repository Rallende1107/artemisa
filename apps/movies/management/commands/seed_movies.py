"""seed_movies — datos iniciales de la app `movies` (clasificaciones, géneros, tipos y roles). Idempotente: se puede reejecutar cuando cambien los datos.
Datos en apps/movies/management/data/seed_data.py; funciones compartidas en apps/catalogs/management/functions/funciones_seed.py.

    docker compose exec web python manage.py seed_movies
"""
from django.core.management.base import BaseCommand

from apps.catalogs.management.functions.funciones_seed import paso, seed_defaults_names_description, seed_defaults_ratings, seed_defaults_roles
from apps.movies.management.data.seed_data import default_movie_ratings, default_movie_serie_genres, default_movie_serie_roles, default_movie_serie_types
from apps.movies.models import Genre, Rating, Role, Type


class Command(BaseCommand):
    help = "Datos iniciales de movies (clasificaciones, géneros, tipos y roles)."

    def handle(self, *args, **opts):
        out = self.stdout
        out.write("[Películas]")
        paso(out, "Clasificaciones", Rating, lambda: seed_defaults_ratings(Rating, default_movie_ratings))
        paso(out, "Géneros", Genre, lambda: seed_defaults_names_description(Genre, default_movie_serie_genres, True))
        paso(out, "Tipos", Type, lambda: seed_defaults_names_description(Type, default_movie_serie_types))
        paso(out, "Roles", Role, lambda: seed_defaults_roles(Role, default_movie_serie_roles))
        out.write("Películas: listo.")
