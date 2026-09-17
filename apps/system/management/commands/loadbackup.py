"""loadbackup — restaura el ÚLTIMO backup de dump/ en una BD ya migrada.

    loadbackup                                  el último backup entero (vacía las tablas y carga)
    loadbackup --tabla games.Game               SOLO esa tabla, sin tocar el resto
    loadbackup --tabla games.Game --vaciar      SOLO esa tabla, borrando antes sus filas
    loadbackup --archivo dump/bd-20260915-0030  un backup concreto (carpeta o .json.gz de los antiguos)
    loadbackup --sin-flush                      no vacía antes (puede chocar con los únicos)

RESTAURAR ENTERO = REEMPLAZAR: primero vacía las tablas, porque hasta una BD «recién migrada» trae filas de
migraciones de datos que chocan con el dump. Todas las tablas se cargan en UNA llamada a `loaddata`, que las
mete en una sola transacción: así una fila que apunta a otra tabla no falla por el orden.

RESTAURAR UNA TABLA no vacía nada salvo que se pida con `--vaciar`, y entonces borra solo esa tabla.
"""
import zipfile
from pathlib import Path

from django.apps import apps as registro
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restaura el último backup (entero o una sola tabla) + media."

    def add_arguments(self, parser):
        parser.add_argument("--archivo", default="",
                            help="Backup concreto: la carpeta bd-<fecha>/ o un bd-<fecha>.json.gz antiguo.")
        parser.add_argument("--tabla", action="append", default=[],
                            help="Restaura SOLO esa tabla (app.Modelo). Se puede repetir.")
        parser.add_argument("--vaciar", action="store_true",
                            help="Con --tabla: borra las filas de esa tabla antes de cargarla.")
        parser.add_argument("--sin-flush", action="store_true",
                            help="Restaurando entero: NO vacía las tablas antes.")
        parser.add_argument("--sin-media", action="store_true", help="Solo la BD.")

    def _ultimo(self, patron):
        archivos = sorted((settings.BASE_DIR / "dump").glob(patron))
        return archivos[-1] if archivos else None

    def _origen(self, opts):
        """La carpeta bd-<fecha>/ o el archivo único que toca restaurar."""
        if opts["archivo"]:
            origen = Path(opts["archivo"])
            if not origen.exists():
                raise CommandError(f"No existe {origen}.")
            return origen
        carpetas = sorted(p for p in (settings.BASE_DIR / "dump").glob("bd-*") if p.is_dir())
        return carpetas[-1] if carpetas else self._ultimo("bd-*.json.gz")

    def _archivo_de(self, carpeta, etiqueta):
        """El .json.gz de una tabla dentro de la carpeta, por app.modelo (sin importar mayúsculas)."""
        try:
            modelo = registro.get_model(*etiqueta.split("."))
        except (LookupError, ValueError, TypeError):
            raise CommandError(f"«{etiqueta}» no es una tabla (usa app.Modelo, p. ej. games.Game).")
        if modelo is None:
            raise CommandError(f"«{etiqueta}» no existe.")
        nombre = f"{modelo._meta.app_label}.{modelo._meta.model_name}.json.gz"
        archivo = carpeta / nombre
        if not archivo.exists():
            raise CommandError(f"El backup no trae {nombre} (esa tabla estaba vacía al respaldar).")
        return modelo, archivo

    def handle(self, *args, **opts):
        origen = self._origen(opts)
        if origen is None:
            raise CommandError("No hay backup en dump/ (corre `backup` primero).")

        # --- una o varias tablas sueltas ---
        if opts["tabla"]:
            if origen.is_file():
                raise CommandError("Ese backup es de archivo único: no se puede restaurar una tabla sola. "
                                   "Vuelve a respaldar con `backup` (sin --unico) o restaura entero.")
            for etiqueta in opts["tabla"]:
                modelo, archivo = self._archivo_de(origen, etiqueta)
                if opts["vaciar"]:
                    borradas = modelo.objects.all().delete()[0]
                    self.stdout.write(f"[{etiqueta}] {borradas} filas borradas")
                call_command("loaddata", str(archivo), verbosity=0)
                self.stdout.write(f"[{etiqueta}] restaurada desde {archivo.name}: {modelo.objects.count()} filas")
            return

        # --- el backup entero ---
        if origen.is_dir():
            archivos = sorted(str(p) for p in origen.glob("*.json.gz"))
            if not archivos:
                raise CommandError(f"{origen.name}/ no trae ninguna tabla.")
        else:
            archivos = [str(origen)]
        if not opts["sin_flush"]:
            self.stdout.write("[Vaciando tablas (flush)]")
            call_command("flush", interactive=False, verbosity=0)
        self.stdout.write(f"[Restaurando {origen.name} — {len(archivos)} archivo(s)]")
        call_command("loaddata", *archivos)          # todos juntos: una transacción, sin problemas de orden
        self.stdout.write(f"BD restaurada desde {origen.name}.")

        if opts["sin_media"]:
            return
        zip_media = self._ultimo("media-*.zip")
        if zip_media:
            with zipfile.ZipFile(zip_media) as z:
                z.extractall(settings.MEDIA_ROOT)
            self.stdout.write(f"Media restaurada desde {zip_media.name}.")
        else:
            self.stdout.write("Sin zip de media en dump/: solo BD.")
