"""Tags de VNDB desde el DUMP oficial (no la API): https://dl.vndb.org/dump/vndb-tags-latest.json.gz

Un JSON con TODOS los tags: id, name, description, cat (cont · ero · tech), aliases, parents, meta, searchable,
applicable, vns. Aquí se lee, se compara con la base y se aplica por `vndb_id` (nunca por nombre: el dump de mañana
renombra, no duplica): cont y ero → `Genre` (ero con `explicit`), tech → `Tag`. Lo que ya no viene en el dump queda
INACTIVO (no se borra: puede haber juegos enlazados).
"""
import gzip
import io
import json
import time
import urllib.request
from pathlib import Path

from django.conf import settings
from django.db import transaction

from apps.games.models import Genre, GenreAlias, Tag, TagAlias


URL_DUMP = "https://dl.vndb.org/dump/vndb-tags-latest.json.gz"
CARPETA = Path(settings.BASE_DIR) / "dump"
CATEGORIAS = {"cont": "Contenido", "ero": "Sexual", "tech": "Técnico"}


def descargar():
    """Baja el dump a dump/vndb-tags-<fecha>.json.gz y devuelve la ruta."""
    CARPETA.mkdir(parents=True, exist_ok=True)
    destino = CARPETA / f"vndb-tags-{time.strftime('%Y%m%d-%H%M%S')}.json.gz"
    req = urllib.request.Request(URL_DUMP, headers={"User-Agent": "Frikiverso/1.0 (panel)"})
    with urllib.request.urlopen(req, timeout=60) as r, open(destino, "wb") as f:
        f.write(r.read())
    return destino


def guardar_subido(archivo):
    """Guarda un archivo subido por el formulario (.json o .json.gz) en dump/ y devuelve la ruta."""
    CARPETA.mkdir(parents=True, exist_ok=True)
    nombre = archivo.name.lower()
    ext = ".json.gz" if nombre.endswith(".gz") else ".json"
    destino = CARPETA / f"vndb-tags-{time.strftime('%Y%m%d-%H%M%S')}{ext}"
    with open(destino, "wb") as f:
        for trozo in archivo.chunks():
            f.write(trozo)
    return destino


def ultimo_dump():
    """El dump más reciente en dump/ (o None)."""
    ficheros = sorted(CARPETA.glob("vndb-tags-*.json*"))
    return ficheros[-1] if ficheros else None


def leer(ruta):
    """Lista de tags del dump (dicts con id entero, name, description, cat, aliases…)."""
    ruta = Path(ruta)
    raw = ruta.read_bytes()
    if ruta.suffix == ".gz" or raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    datos = json.load(io.BytesIO(raw))
    tags = []
    for t in datos:
        tid = t.get("id")
        if isinstance(tid, str):          # por si viene «g123»
            tid = int(tid.lstrip("g"))
        if not tid or not t.get("name"):
            continue
        tags.append({"id": int(tid), "name": str(t["name"])[:100], "description": t.get("description") or "",
                     "cat": t.get("cat") or "cont", "aliases": [str(a) for a in (t.get("aliases") or [])],
                     "applicable": bool(t.get("applicable", True))})
    return tags


def _modelo(cat):
    return Tag if cat == "tech" else Genre


def _campos(t):
    campos = {"name": t["name"], "description": t["description"].strip(), "is_active": t["applicable"]}
    if _modelo(t["cat"]) is Genre:
        campos["explicit"] = t["cat"] == "ero"
    return campos


def resumen(tags):
    """Qué pasaría al aplicar: totales por categoría, cuántos se crean, cambian, quedan iguales y desaparecen."""
    ids_dump = {t["id"] for t in tags}
    actuales = {}
    for modelo in (Genre, Tag):
        for fila in modelo.objects.exclude(vndb_id__isnull=True):
            actuales[(modelo, fila.vndb_id)] = fila
    crear = cambian = iguales = 0
    for t in tags:
        fila = actuales.get((_modelo(t["cat"]), t["id"]))
        if fila is None:
            crear += 1
        elif all(getattr(fila, k) == v for k, v in _campos(t).items()):
            iguales += 1
        else:
            cambian += 1
    desaparecen = [f for (m, i), f in actuales.items() if i not in ids_dump and f.is_active]
    por_cat = {CATEGORIAS.get(c, c): sum(1 for t in tags if t["cat"] == c) for c in ("cont", "ero", "tech")}
    return {"total": len(tags), "por_categoria": por_cat, "crear": crear, "cambian": cambian, "iguales": iguales,
            "desaparecen": desaparecen}


def _alias(fila, nombres):
    """Alias del dump → filas GenreAlias / TagAlias del padre (una por alias; los que ya están, se dejan)."""
    modelo = TagAlias if isinstance(fila, Tag) else GenreAlias
    campo = "tag" if isinstance(fila, Tag) else "genre"
    for n in nombres:
        n = n.strip()[:100]
        if n and n.lower() != fila.name.lower():
            modelo.objects.get_or_create(**{campo: fila, "name": n})


@transaction.atomic
def aplicar(tags):
    """Crea / actualiza por vndb_id; desactiva lo que ya no viene. Devuelve el mismo resumen con lo hecho."""
    ids_dump = {t["id"] for t in tags}
    creados = actualizados = 0
    for t in tags:
        modelo = _modelo(t["cat"])
        fila = modelo.objects.filter(vndb_id=t["id"]).first()
        campos = _campos(t)
        if fila is None:
            # si ya existía por NOMBRE (creado al vuelo por el importador, sin id), se le pone el id en vez de duplicar
            fila = modelo.objects.filter(vndb_id__isnull=True, name__iexact=t["name"]).first()
            if fila is None:
                _alias(modelo.objects.create(vndb_id=t["id"], **campos), t["aliases"])
                creados += 1
                continue
            fila.vndb_id = t["id"]
        cambios = {k: v for k, v in campos.items() if getattr(fila, k) != v}
        for k, v in cambios.items():
            setattr(fila, k, v)
        fila.save()
        actualizados += 1 if cambios else 0
        _alias(fila, t["aliases"])
    desactivados = 0
    for modelo in (Genre, Tag):
        desactivados += modelo.objects.exclude(vndb_id__isnull=True).exclude(vndb_id__in=ids_dump).filter(is_active=True).update(is_active=False)
    return {"creados": creados, "actualizados": actualizados, "desactivados": desactivados, "total": len(tags)}
