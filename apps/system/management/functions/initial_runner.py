import re

from apps.catalogs.models import ExternalSource
from core.shared.models.choices import ExternalSourceType


# Artemisa: ExternalSource vive en common (no en system).

def generate_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

# ExternalSource.type (choices): mapeo de los tipos del dato original.
EXTERNAL_SOURCE_TYPE_TO_KIND = {
    "distribution": ExternalSourceType.OTHER,        # no hay kind de "tienda"; se usa OTRO
    "database": ExternalSourceType.DATABASE,
    "community": ExternalSourceType.COMMUNITY,
    "monetization": ExternalSourceType.MONETIZATION,
}

default_external_source = [
    # 🎮 Plataformas de distribución
    {"name": "Steam",   "type": "distribution"},
    {"name": "Itch.io", "type": "distribution"},
    {"name": "GOG",     "type": "distribution"},
    {"name": "DLsite",  "type": "distribution"},
    {"name": "Nutaku",  "type": "distribution"},
    # 📚 Bases de datos
    {"name": "VNDB",      "type": "database"},
    {"name": "IGDB",      "type": "database"},
    {"name": "MobyGames", "type": "database"},
    # 🧩 Comunidades
    {"name": "F95Zone",  "type": "community"},
    {"name": "Reddit",   "type": "community"},
    {"name": "Discord",  "type": "community"},
    # 💰 Monetización
    {"name": "Patreon",         "type": "monetization"},
    {"name": "SubscribeStar",   "type": "monetization"},
    {"name": "Boosty",          "type": "monetization"},
    # 🏪 Tiendas alternativas
    {"name": "Erogames",     "type": "distribution"},
    {"name": "JAST USA",     "type": "distribution"},
    {"name": "FAKKU",        "type": "distribution"},
]


def _linea(stdout, etiqueta, creados, existian):
    """Una línea por catálogo: «Niveles de log: 12 (11 nuevos, 1 existía)»."""
    if stdout:
        stdout.write(f"  {etiqueta}: {creados + existian} ({creados} nuevos, {existian} existían)")


def run(stdout=None, style=None):


################################# Creator External Source #################################
    created = 0
    skipped = 0

    for item in default_external_source:
        name = item["name"]
        source_type = item["type"]
        kind = EXTERNAL_SOURCE_TYPE_TO_KIND.get(source_type, ExternalSourceType.OTHER)

        obj, was_created = ExternalSource.objects.get_or_create(
            name=name,
            defaults={
                "type": kind,
            }
        )

        if was_created:
            created += 1
        else:
            skipped += 1

    _linea(stdout, "Fuentes externas", created, skipped)

