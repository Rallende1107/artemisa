"""Carga de DUMPS de VNDB (json · json.gz), archivo → tablas Data*. NO procesa nada.

Estos dumps son los que genera NUESTRO exportador desde la propia tabla: el respaldo alternativo al de la
base. Por eso lo que se lee es exactamente lo que se guardó al descargar de la API —la ficha de VNDB tal
cual— y vuelve a su tabla sin traducir nada. Procesar es el paso de después, desde la lista de esa tabla.

    juego        {"id": "v17", "title": …}   → DataVndbGame        (vndb_id = 17)
    creador      {"id": "p24", …}            → DataVndbCreator
    lanzamiento  {"id": "r56", …}            → DataVndbRelease
    personaje    {"id": "c99", …}            → DataVndbCharacter

El archivo puede traer una ficha suelta (un objeto), muchas (una lista) o una por línea (JSON Lines).
"""
import gzip
import json
import time
from pathlib import Path

from django.conf import settings
from django.db import transaction

from apps.games.models import DataVndbCharacter, DataVndbCreator, DataVndbGame, DataVndbRelease


CARPETA = Path(settings.BASE_DIR) / "dump"

# Un tipo de dump = a qué tabla va y con qué prefijo se guarda el archivo.
TIPOS = {
    "game": {"modelo": DataVndbGame, "prefijo": "vndb-game"},
    "creator": {"modelo": DataVndbCreator, "prefijo": "vndb-creator"},
    "release": {"modelo": DataVndbRelease, "prefijo": "vndb-release"},
    "character": {"modelo": DataVndbCharacter, "prefijo": "vndb-character"},
}


def guardar_subido(tipo, archivo):
    """Guarda el archivo subido en dump/ con su fecha y devuelve la ruta."""
    CARPETA.mkdir(parents=True, exist_ok=True)
    ext = ".json.gz" if archivo.name.lower().endswith(".gz") else ".json"
    destino = CARPETA / f"{TIPOS[tipo]['prefijo']}-{time.strftime('%Y%m%d-%H%M%S')}{ext}"
    with open(destino, "wb") as f:
        for trozo in archivo.chunks():
            f.write(trozo)
    return destino


def ultimo_dump(tipo):
    """El dump más reciente de ese tipo en dump/ (o None)."""
    ficheros = sorted(CARPETA.glob(f"{TIPOS[tipo]['prefijo']}-*.json*"))
    return ficheros[-1] if ficheros else None


def leer(ruta):
    """Las fichas del dump. Acepta un objeto suelto, una lista, o un objeto por línea (JSON Lines)."""
    ruta = Path(ruta)
    raw = ruta.read_bytes()
    if ruta.suffix == ".gz" or raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    texto = raw.decode("utf-8-sig").strip()
    if not texto:
        return []
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:            # JSON Lines: un objeto por línea
        datos = [json.loads(l) for l in texto.splitlines() if l.strip()]
    if isinstance(datos, dict):
        datos = [datos]
    return [d for d in datos if isinstance(d, dict)]


def _vndb_id(ficha):
    """«v17» → 17 (la misma cuenta que hace el importador). También vale un id ya numérico."""
    valor = ficha.get("id", ficha.get("vndb_id"))
    if isinstance(valor, int):
        return valor
    try:
        return int(str(valor)[1:] if str(valor)[:1].isalpha() else valor)
    except (TypeError, ValueError):
        return None


def resumen(tipo, fichas):
    """Qué pasaría al aplicar: cuántas hay, cuántas se crean, cuántas ya estaban y cuántas se descartan
    por venir sin id."""
    modelo = TIPOS[tipo]["modelo"]
    ids, sin_id = [], 0
    for f in fichas:
        vndb_id = _vndb_id(f)
        if vndb_id is None:
            sin_id += 1
            continue
        ids.append(vndb_id)
    unicos = set(ids)
    ya = set(modelo.objects.filter(vndb_id__in=unicos).values_list("vndb_id", flat=True))
    return {"total": len(fichas), "validos": len(ids), "unicos": len(unicos), "sin_id": sin_id,
            "repetidos": len(ids) - len(unicos), "crear": len(unicos - ya), "actualizar": len(ya),
            "con_imagenes": 0, "label": modelo._meta.verbose_name, "label_imagenes": ""}


@transaction.atomic
def aplicar(tipo, fichas, ruta=None):
    """Guarda las fichas CRUDAS en su tabla, por `vndb_id`. Una ficha repetida en el archivo deja la última
    versión. Devuelve cuántas filas se escribieron."""
    modelo = TIPOS[tipo]["modelo"]
    origen = str(ruta or "")
    guardadas = descartadas = 0
    for ficha in fichas:
        vndb_id = _vndb_id(ficha)
        if vndb_id is None:
            descartadas += 1
            continue
        modelo.objects.update_or_create(vndb_id=vndb_id, defaults={
            "url": origen, "data": ficha,
            "data_status": True, "status_code": 0, "data_processed": False})
        guardadas += 1
    return {"fichas": guardadas, "imagenes": 0, "descartados": descartadas, "total": len(fichas)}
