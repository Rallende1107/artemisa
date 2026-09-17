"""statics — los estáticos en dos modos:
  · `statics clear` (default): borra STATIC_ROOT y lo vuelve a juntar entero
    (fuera la basura de archivos renombrados o eliminados).
  · `statics new`: incremental — solo copia lo nuevo o cambiado (ideal tras
    dejar caer una tanda de fondos)."""
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Rejunta los estáticos: `clear` desde cero (default) o `new` solo lo nuevo."

    def add_arguments(self, parser):
        parser.add_argument("modo", nargs="?", default="clear", choices=("clear", "new"),
                            help="clear = limpio desde cero · new = solo lo nuevo")

    def handle(self, *args, **opts):
        limpio = opts["modo"] == "clear"
        call_command("collectstatic", interactive=False, clear=limpio, verbosity=0)
        raiz = settings.STATIC_ROOT
        total = sum(1 for p in raiz.rglob("*") if p.is_file())
        modo = "recargados desde cero" if limpio else "sumados (solo lo nuevo)"
        self.stdout.write((
            f"Estáticos {modo}: {total} archivos en {raiz}."))
