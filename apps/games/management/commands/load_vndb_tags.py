"""Aplica el dump de tags de VNDB (el último de dump/ o `--file`): cont y ero → géneros, tech → etiquetas, por id.

    docker compose exec web python manage.py load_vndb_tags             # el último dump/vndb-tags-*.json.gz
    docker compose exec web python manage.py load_vndb_tags --download  # lo baja de VNDB y lo aplica
    docker compose exec web python manage.py load_vndb_tags --file dump/vndb-tags-20260913.json.gz
"""
from django.core.management.base import BaseCommand, CommandError

from apps.games.services import vndb_tags


class Command(BaseCommand):
    help = "Carga los tags de VNDB desde el dump oficial (géneros y etiquetas por vndb_id)."

    def add_arguments(self, parser):
        parser.add_argument("--file", help="ruta del dump (.json o .json.gz)")
        parser.add_argument("--download", action="store_true", help="descargar el dump de VNDB antes de aplicar")

    def handle(self, *args, **opts):
        if opts["download"]:
            ruta = vndb_tags.descargar()
        elif opts["file"]:
            ruta = opts["file"]
        else:
            ruta = vndb_tags.ultimo_dump()
            if ruta is None:
                raise CommandError("No hay ningún dump en dump/vndb-tags-*.json.gz; usa --download o --file.")
        tags = vndb_tags.leer(ruta)
        r = vndb_tags.resumen(tags)
        self.stdout.write(f"{ruta}: {r['total']} tags · crear {r['crear']} · cambian {r['cambian']} · iguales {r['iguales']} · desaparecen {len(r['desaparecen'])}")
        h = vndb_tags.aplicar(tags)
        self.stdout.write(f"Aplicado: {h['creados']} creados, {h['actualizados']} actualizados, {h['desactivados']} desactivados.")
