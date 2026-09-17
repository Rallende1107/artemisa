"""CARGAR dumps propios de MAL (json · json.gz): archivo → tablas DataMal*. NO procesa nada (eso es `mal_dump_process`).

Los datos de MAL entran solo por dumps que se generan aparte. Aquí se leen y se guardan CRUDOS, con el formato del
archivo tal cual (no se traduce nada): lo que traduzca a entidades reales vive en `mal_dump_process`.

Cada registro del dump es UNA fila de su tabla Data, con el registro entero en `data`. Las imágenes vienen dentro del
mismo registro (`image_url` + `images_extra`) y ahí se quedan: al procesar salen como filas de imagen pendientes de
descarga. No se copian a otra tabla.

    anime     {"mal_id": 1, "title": …, "image_url": url, "images_extra": [url, …], …}  → DataMalAnime

El archivo puede traer un registro suelto (un objeto), muchos (una lista) o uno por línea (JSON Lines); las tres
formas se leen igual. Pensado para dumps GRANDES: se escribe por lotes con upsert (`bulk_create(update_conflicts)`).
"""
import gzip
import json
import time
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.otaku.models import DataMalAnime, DataMalCharacter, DataMalManga, DataMalPerson


CARPETA = Path(settings.BASE_DIR) / "dump"
LOTE = 500

# Un tipo de dump = de qué clave sale el mal_id, a qué tabla va y con qué prefijo se guarda el archivo.
TIPOS = {
    "anime": {"id": "mal_id", "ficha": DataMalAnime, "prefijo": "mal-anime"},
    "character": {"id": "character_id", "ficha": DataMalCharacter, "prefijo": "mal-characters"},
    "manga": {"id": "mal_id", "ficha": DataMalManga, "prefijo": "mal-manga"},
    "person": {"id": "person_id", "ficha": DataMalPerson, "prefijo": "mal-people"},
    # compañías: NO van a una tabla Data (ver services/mal_companies.py); aquí solo se declara su archivo
    "company": {"prefijo": "mal-companies"},
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
    """Los registros del dump. Acepta un objeto suelto, una lista, o un objeto por línea (JSON Lines)."""
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


def _mal_id(tipo, registro):
    """El id del registro: su clave propia (`person_id`…) o `mal_id` si el dump ya lo trae así."""
    valor = registro.get(TIPOS[tipo]["id"], registro.get("mal_id"))
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _sin_datos(registro):
    """El scraper marca con {"estado": "No Data"} los ids que no existen en MAL: se guardan como fetch KO."""
    return str(registro.get("estado") or "").strip().lower() == "no data"


def _con_imagenes(registro):
    """¿El registro trae portada o imágenes extra?"""
    return bool(registro.get("image_url") or [x for x in (registro.get("images_extra") or []) if x])


def _por_id(tipo, registros):
    """{mal_id: registro} (un repetido deja la última versión) y cuántos vinieron sin id."""
    por_id, sin_id = {}, 0
    for r in registros:
        mal_id = _mal_id(tipo, r)
        if mal_id is None:
            sin_id += 1
            continue
        por_id[mal_id] = r
    return por_id, sin_id


def _ya_cargados(modelo, ids):
    """Los mal_id que ya tienen fila, consultando por lotes."""
    ids, hay = sorted(ids), set()
    for n in range(0, len(ids), LOTE):
        hay |= set(modelo.objects.filter(mal_id__in=ids[n:n + LOTE]).values_list("mal_id", flat=True))
    return hay


def resumen(tipo, registros):
    """Qué pasaría al aplicar: cuántos hay, cuántos se crean, cuántos ya estaban (se actualizan), cuántos traen
    imágenes y cuántos se descartan por venir sin id."""
    conf = TIPOS[tipo]
    por_id, sin_id = _por_id(tipo, registros)
    validos = len(registros) - sin_id
    ya = _ya_cargados(conf["ficha"], por_id)
    return {"total": len(registros), "validos": validos, "unicos": len(por_id), "sin_id": sin_id,
            "repetidos": validos - len(por_id), "crear": len(por_id) - len(ya), "actualizar": len(ya),
            "con_imagenes": sum(1 for r in por_id.values() if _con_imagenes(r)),
            "label": conf["ficha"]._meta.verbose_name}


@transaction.atomic
def aplicar(tipo, registros, ruta=None):
    """Guarda los registros CRUDOS en su tabla, por `mal_id`, en lotes con upsert: lo que ya estaba se pisa y vuelve
    a quedar sin procesar. Devuelve cuántas filas se escribieron."""
    conf = TIPOS[tipo]
    modelo = conf["ficha"]
    origen = str(ruta or "")
    por_id, sin_id = _por_id(tipo, registros)
    ahora = timezone.now()
    filas = [modelo(mal_id=i, url=(r.get("url") or origen)[:500], data=r, data_status=not _sin_datos(r), status_code=0,
                    data_processed=False, updated_at=ahora) for i, r in por_id.items()]
    modelo.objects.bulk_create(filas, batch_size=LOTE, update_conflicts=True, unique_fields=["mal_id"],
                               update_fields=["url", "data", "data_status", "status_code", "data_processed", "updated_at"])
    return {"fichas": len(filas), "imagenes": sum(1 for r in por_id.values() if _con_imagenes(r)),
            "descartados": sin_id, "total": len(registros)}
