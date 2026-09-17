"""backup — respaldo COMPLETO: la BD + la carpeta media entera, a dump/ (ignorado por git y por Docker).

La BD se guarda UNA TABLA POR ARCHIVO, dentro de `dump/bd-<fecha>/`:

    dump/bd-20260915-0030/games.game.json.gz
    dump/bd-20260915-0030/games.datavndbgame.json.gz
    …

Así se puede restaurar el todo o SOLO una tabla (`loadbackup --tabla games.Game`), que es lo que hace falta
cuando se rompe o se vacía una sola. El formato es `dumpdata` con claves naturales, portable sqlite⇄Postgres.

Con `--unico` se guarda como antes, todo en un `dump/bd-<fecha>.json.gz`.

Para respaldar SOLO lo caro de reconstruir —lo bajado de VNDB, MAL o Deezer, que son horas de scrapeo— está
`--datos`: coge las tablas Data* y Raw de todas las apps. Así se puede migrar o tocar otra tabla sin miedo,
y devolver los datos crudos después:

    backup --datos                     → dump/datos-<fecha>/games.datavndbgame.json.gz, …
    loadbackup --archivo dump/datos-<fecha> --tabla games.DataVndbGame
"""
import gzip
import shutil

from django.apps import apps as registro
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


# Tablas que NO viajan: se regeneran solas y solo estorban al restaurar.
EXCLUIR = ("contenttypes", "auth.permission", "sessions", "admin.logentry")
APPS_EXCLUIDAS = {"contenttypes", "sessions", "admin"}


class Command(BaseCommand):
    help = "Backup COMPLETO (BD por tablas + media) a dump/ con timestamp."

    def add_arguments(self, parser):
        parser.add_argument("--unico", action="store_true",
                            help="Todo en un solo archivo, como antes (no permite restaurar por tabla).")
        parser.add_argument("--sin-media", action="store_true", help="Solo la BD.")
        parser.add_argument("--datos", action="store_true",
                            help="Solo las tablas de datos crudos (Data* y Raw): lo caro de volver a bajar.")
        parser.add_argument("--tabla", action="append", default=[],
                            help="Solo esa tabla (app.Modelo). Se puede repetir.")

    def modelos(self, opts):
        """Los modelos que se respaldan, en el orden en que Django los registró (padres antes que hijos).
        Con `--tabla` solo esas; con `--datos`, las de staging de los importadores."""
        if opts["tabla"]:
            for etiqueta in opts["tabla"]:
                modelo = registro.get_model(*etiqueta.split(".")) if "." in etiqueta else None
                if modelo is None:
                    raise CommandError(f"«{etiqueta}» no es una tabla (usa app.Modelo, p. ej. games.DataVndbGame).")
                yield modelo, f"{modelo._meta.app_label}.{modelo._meta.model_name}"
            return
        for modelo in registro.get_models():
            etiqueta = f"{modelo._meta.app_label}.{modelo._meta.model_name}"
            if modelo._meta.app_label in APPS_EXCLUIDAS or etiqueta in EXCLUIR:
                continue
            if modelo._meta.proxy or not modelo._meta.managed:
                continue
            if opts["datos"] and not (modelo.__name__.startswith("Data") or "Raw" in modelo.__name__):
                continue
            yield modelo, etiqueta

    def volcar(self, destino, *etiquetas):
        """Un `dumpdata` a un .json.gz. Se comprime aquí y no con el -o de Django: ese abre el archivo con la
        codificación del sistema y en Windows (cp1252) revienta con los títulos en japonés."""
        with gzip.open(destino, "wt", encoding="utf-8") as f:
            call_command("dumpdata", *etiquetas, natural_foreign=True, natural_primary=True,
                         exclude=list(EXCLUIR), verbosity=0, stdout=f)
        return destino.stat().st_size / 1024 / 1024

    def handle(self, *args, **opts):
        carpeta = settings.BASE_DIR / "dump"
        carpeta.mkdir(exist_ok=True)
        marca = timezone.localtime().strftime("%Y%m%d-%H%M%S")

        solo_datos = opts["datos"] or opts["tabla"]
        if opts["unico"]:
            archivo = carpeta / f"bd-{marca}.json.gz"
            mb = self.volcar(archivo, *[e for _m, e in self.modelos(opts)] if solo_datos else [])
            self.stdout.write(f"  BD: {archivo.name} ({mb:.1f} MB)")
        else:
            destino = carpeta / f"{'datos' if solo_datos else 'bd'}-{marca}"
            destino.mkdir()
            total = vacias = 0
            for modelo, etiqueta in self.modelos(opts):
                if not modelo.objects.exists():          # una tabla vacía no necesita archivo
                    vacias += 1
                    continue
                mb = self.volcar(destino / f"{etiqueta}.json.gz", etiqueta)
                total += 1
                self.stdout.write(f"  {etiqueta}: {modelo.objects.count()} filas ({mb:.1f} MB)")
            self.stdout.write(f"  BD: {destino.name}/ — {total} tablas ({vacias} vacías, sin archivo)")

        if opts["sin_media"] or solo_datos:      # un respaldo de datos crudos no necesita media
            return
        shutil.make_archive(str(carpeta / f"media-{marca}"), "zip", settings.MEDIA_ROOT)
        mb = (carpeta / f"media-{marca}.zip").stat().st_size / 1024 / 1024
        self.stdout.write(f"  Media: media-{marca}.zip ({mb:.1f} MB)")
