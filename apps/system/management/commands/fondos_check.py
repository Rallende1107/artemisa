"""Chequea la coherencia de los fondos (estilo Poseidon).

Un fondo es una CLASE CSS `bg-<app>-<entidad>` que:
  - la vista declara en `background_image` (o el HTML como clase de .bg-layer),
  - vive en apps/<app>/static/image/screen/<orient>/bg-<app>-<entidad>.webp.
No hay CSS por clase: {% bg_style %} (core/templatetags/fondos.py) pone las 4 rutas en línea.

Reporta:
  · REFERENCIADAS SIN IMAGEN  → la vista/plantilla pide una clase que no tiene .webp (wide).
  · IMÁGENES HUÉRFANAS        → hay .webp que ninguna vista/plantilla usa (informativo).
  · SIN LAS 4 ORIENTACIONES   → falta alguna orientación.
  · EN LA CARPETA DE OTRA APP → la imagen no está en la app dueña de su prefijo.

Uso:  python manage.py fondos_check
"""
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


ORIENTS = ("wide", "landscape", "portrait", "tall")
CENTRALES = set()                          # apps cuyos fondos siguen en static/image/screen/ (hoy ninguna)
PREFIJO_APP = {"coleccions": "collections"}   # prefijo histórico → app dueña
RE_ATTR = re.compile(r"""["'](bg-[a-z0-9]+(?:-[a-z0-9]+)+)["']""")   # todo fondo entre comillas: background_image, tarjetas, mapas «por»…
RE_CLASS = re.compile(r"""\bbg-(?:[a-z]+)-[a-z0-9-]+\b""")


class Command(BaseCommand):
    help = "Verifica que cada fondo (bg-<app>-<ent>) tenga imagen y esté referenciado."

    def handle(self, *args, **opts):
        base = Path(settings.BASE_DIR)

        # Imágenes presentes por clase → orientaciones disponibles, en las DOS ubicaciones:
        # apps/<app>/static/image/screen/<orient>/ y static/image/screen/<orient>/ (otaku).
        present, carpeta = {}, {}
        for patron in ("static/image/screen/*/bg-*.webp", "apps/*/static/image/screen/*/bg-*.webp"):
            for webp in base.glob(patron):
                orient = webp.parent.name
                if orient in ORIENTS:
                    present.setdefault(webp.stem, set()).add(orient)
                    carpeta[webp.stem] = webp.parent.parent.relative_to(base).as_posix()

        # Clases referenciadas en el código (.py: cualquier «bg-…» entre comillas) y plantillas (.html).
        referenced = set()
        for py in base.glob("apps/**/*.py"):
            referenced |= set(RE_ATTR.findall(py.read_text(encoding="utf-8", errors="ignore")))
        for py in (base / "core").glob("**/*.py"):
            referenced |= set(RE_ATTR.findall(py.read_text(encoding="utf-8", errors="ignore")))
        for html in list(base.glob("templates/**/*.html")) + list(base.glob("apps/**/templates/**/*.html")):
            txt = html.read_text(encoding="utf-8", errors="ignore")
            referenced |= set(RE_CLASS.findall(txt))
        referenced.discard("bg-layer")
        # no son fondos de pantalla: un ejemplo de comentario y la imagen de «en construcción» de static/image/default/
        referenced -= {"bg-xxxx-xxxx", "bg-in-progress"}

        # 1) Referenciadas sin imagen (wide).
        missing = sorted(c for c in referenced if "wide" not in present.get(c, set()))
        # 2) Imágenes huérfanas (no referenciadas por ninguna vista/plantilla).
        orphans = sorted(c for c in present if c not in referenced)
        # 3) Sin las 4 orientaciones.
        incomplete = sorted((c, sorted(present[c])) for c in present if len(present[c]) != 4)
        # 4) En la carpeta de otra app.
        def debida(clase):
            app = PREFIJO_APP.get(clase.split("-")[1], clase.split("-")[1])
            return "static/image/screen" if app in CENTRALES or not (base / "apps" / app).is_dir() else f"apps/{app}/static/image/screen"
        misplaced = sorted((c, carpeta[c], debida(c)) for c in carpeta if carpeta[c] != debida(c))

        w = self.stdout.write
        ok = self.style.SUCCESS
        warn = self.style.WARNING
        err = self.style.ERROR

        w(f"Fondos: {len(present)} imagenes / {len(referenced)} referencias\n")

        if missing:
            w(err(f"[X] REFERENCIADAS SIN IMAGEN ({len(missing)}):"))
            for c in missing:
                app = PREFIJO_APP.get(c.split("-")[1], c.split("-")[1])
                destino = "static" if app in CENTRALES or not (base / "apps" / app).is_dir() else f"apps/{app}/static"
                w(f"    {c}  -> falta {destino}/image/screen/wide/{c}.webp")
        else:
            w(ok("[OK] Todas las clases referenciadas tienen imagen."))

        if incomplete:
            w(warn(f"\n[!] SIN LAS 4 ORIENTACIONES ({len(incomplete)}):"))
            for c, os_ in incomplete:
                w(f"    {c}: {os_}")

        if orphans:
            w(warn(f"\n[!] IMAGENES HUERFANAS ({len(orphans)}) - sin vista/plantilla que las use:"))
            for c in orphans:
                w(f"    {c}")

        if misplaced:
            w(warn(f"\n[!] EN LA CARPETA DE OTRA APP ({len(misplaced)}):"))
            for c, esta, debe in misplaced:
                w(f"    {c}: está en {esta}, debería estar en {debe}")

        if missing:
            raise SystemExit(1)
