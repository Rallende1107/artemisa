"""medir_import — cronometra UNA importación completa (artista de Deezer con todos sus álbumes y
pistas, o juego de VNDB con lanzamientos, personajes e imágenes) y proyecta el lote diario. Sirve
para fijar el tamaño de las tareas de beat con datos reales antes de programarlas.

    docker compose exec web python manage.py medir_import deezer artista 27
    docker compose exec web python manage.py medir_import deezer artista --search_words "Mozart"
    docker compose exec web python manage.py medir_import vndb juego 11
    docker compose exec web python manage.py medir_import vndb juego --search_words "Fate/stay night"
    docker compose exec web python manage.py medir_import vndb juego 11 --lote 100

Imprime tiempo, peticiones HTTP, filas creadas e imágenes que quedan pendientes de descargar, y
cuánto tardaría un lote de N (por defecto 100) a ese ritmo. Corre en el proceso actual (sin Celery)
y respeta el rate limit de cada API, así que la medición es la real."""
import time

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cronometra una importación (deezer artista | vndb juego) y proyecta el lote diario."

    def add_arguments(self, parser):
        parser.add_argument("fuente", choices=["deezer", "vndb"])
        parser.add_argument("tipo", choices=["artista", "juego"])
        parser.add_argument("id", nargs="?", type=int)
        parser.add_argument("--search_words", default="", help="nombre a search_words en la API si no se da el id")
        parser.add_argument("--lote", type=int, default=100, help="tamaño del lote diario a proyectar")

    def handle(self, *args, **opts):
        fuente, tipo, ident, search_words, lote = opts["fuente"], opts["tipo"], opts["id"], opts["search_words"], opts["lote"]
        if (fuente, tipo) not in (("deezer", "artista"), ("vndb", "juego")):
            raise CommandError("Combinaciones válidas: deezer artista · vndb juego")
        if fuente == "deezer":
            from apps.music.services import deezer as srv
            if ident is None:
                ident = self._elegir(srv.buscar_artistas(search_words), search_words)
            correr, filas = srv.import_artist, self._filas_artista
        else:
            from apps.games.services import vndb as srv
            if ident is None:
                ident = self._elegir(srv.buscar_juegos(search_words), search_words)
            correr, filas = srv.import_game, self._filas_juego
        self.stdout.write(f"Importando {fuente} {tipo} #{ident}…")
        t0, p0 = time.monotonic(), srv._stats["peticiones"]
        resultado = correr(ident)
        segundos, peticiones = time.monotonic() - t0, srv._stats["peticiones"] - p0
        if resultado is None:
            raise CommandError(f"No se pudo importar #{ident} (mira el log de {fuente}).")
        self.stdout.write((f"{resultado}"))
        for etiqueta, valor in filas(resultado):
            self.stdout.write(f"  {etiqueta}: {valor}")
        self.stdout.write(f"  peticiones HTTP: {peticiones}")
        self.stdout.write(f"  tiempo: {segundos:.1f} s")
        self.stdout.write((
            f"Lote de {lote} a este ritmo: {segundos * lote / 60:.1f} min y {peticiones * lote} peticiones "
            f"(sin contar la descarga de imágenes, que va aparte: 100 al día)."))

    def _elegir(self, candidatos, search_words):
        if not search_words:
            raise CommandError("Da un id o --search_words \"nombre\".")
        if not candidatos:
            raise CommandError(f"Sin resultados para «{search_words}».")
        for c in candidatos[:8]:
            self.stdout.write(f"  #{c['id']}  {c['titulo']}  ({c.get('sub', '')})")
        elegido = candidatos[0]
        self.stdout.write(f"Uso el primero: #{elegido['id']} {elegido['titulo']}")
        return int(elegido["id"])

    @staticmethod
    def _filas_artista(artista):
        from apps.music.models import ArtistImage, Song
        return [
            ("álbumes", artista.albums.count()),
            ("canciones", Song.objects.filter(album__artist=artista).count()),
            ("imágenes pendientes de descarga", ArtistImage.objects.filter(artist=artista, image_downloaded=False).exclude(image_url="").count()),
        ]

    @staticmethod
    def _filas_juego(juego):
        return [
            ("lanzamientos", juego.releases.count()),
            ("personajes", juego.character_roles.count()),
            ("imágenes", juego.images.count()),
            ("imágenes pendientes de descarga", juego.images.filter(image_downloaded=False).exclude(image_url="").count()
                                                 + juego.images.filter(image_downloaded=False).exclude(image_url="").count()),
        ]
