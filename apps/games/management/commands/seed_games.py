"""seed_games — datos iniciales de la app `games` (motores, plataformas, medios y géneros). Idempotente: se puede reejecutar cuando cambien los datos.
Datos en apps/games/management/data/seed_data.py; funciones compartidas en apps/catalogs/management/functions/funciones_seed.py.

    docker compose exec web python manage.py seed_games
"""
from django.core.management.base import BaseCommand

from apps.catalogs.management.functions.funciones_seed import paso, seed_default_game_engines, seed_defaults_names_description, seed_defaults_names_description_vndb
from apps.games.management.data.seed_data import default_game_engines, default_game_genres, default_game_mediums, default_game_platforms
from apps.games.models import DevelopmentEngine, Genre, Medium, Platform


class Command(BaseCommand):
    help = "Datos iniciales de games (motores, plataformas, medios y géneros)."

    def handle(self, *args, **opts):
        out = self.stdout
        out.write("[Juegos]")
        paso(out, "Motores", DevelopmentEngine, lambda: seed_default_game_engines(DevelopmentEngine, default_game_engines))
        paso(out, "Plataformas", Platform, lambda: seed_defaults_names_description_vndb(Platform, default_game_platforms))
        paso(out, "Medios", Medium, lambda: seed_defaults_names_description_vndb(Medium, default_game_mediums))
        paso(out, "Géneros", Genre, lambda: seed_defaults_names_description(Genre, default_game_genres, True))
        out.write("Juegos: listo.")
