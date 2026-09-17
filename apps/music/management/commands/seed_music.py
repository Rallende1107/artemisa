"""seed_music — datos iniciales de la app `music` (tipos de álbum y de artista, roles y géneros). Idempotente: se puede reejecutar cuando cambien los datos.
Datos en apps/music/management/data/seed_data.py; funciones compartidas en apps/catalogs/management/functions/funciones_seed.py.

    docker compose exec web python manage.py seed_music
"""
from django.core.management.base import BaseCommand

from apps.catalogs.management.functions.funciones_seed import paso, seed_defaults_names_description, seed_defaults_roles
from apps.music.management.data.seed_data import default_music_albums_types, default_music_artist_types, default_music_genres, default_music_roles
from apps.music.models import AlbumType, ArtistType, Genre, Role


class Command(BaseCommand):
    help = "Datos iniciales de music (tipos de álbum y de artista, roles y géneros)."

    def handle(self, *args, **opts):
        out = self.stdout
        out.write("[Música]")
        paso(out, "Tipos de álbum", AlbumType, lambda: seed_defaults_names_description(AlbumType, default_music_albums_types))
        paso(out, "Tipos de artista", ArtistType, lambda: seed_defaults_names_description(ArtistType, default_music_artist_types))
        paso(out, "Roles", Role, lambda: seed_defaults_roles(Role, default_music_roles))
        paso(out, "Géneros", Genre, lambda: seed_defaults_names_description(Genre, default_music_genres))
        out.write("Música: listo.")
