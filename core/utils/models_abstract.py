"""Utilidades de los MODELOS ABSTRACTOS (core/shared/models/abstract.py) y de los modelos que los heredan.

Funciones sueltas que los modelos usan al guardar o al pintar su ficha. Viven aquí, no en models_abstract.py, para que
ese archivo solo tenga bases abstractas. Cada función declara los tipos de entrada y de salida.
"""
from __future__ import annotations

import datetime
from collections.abc import Callable, Iterable
from typing import Any

from django.db import models
from django.db.models import Min

# Lo que `filas_obra` acepta para leer de cada fila: el nombre del atributo o una función que recibe la fila.
Lector = str | Callable[[Any], Any]


def unique_slug(model: type[models.Model], base: str, pk: int | None, maxlen: int) -> str:
    """Devuelve un slug único para `model`: si `base` ya existe (distinto nombre con
    igual slugify, p. ej. «Álbum» y «album»), le añade -2, -3… en vez de romper por
    el UNIQUE. Evita el `UNIQUE constraint failed: …slug`."""
    base = base or "item"
    slug, i = base, 2
    while model.objects.exclude(pk=pk).filter(slug=slug).exists():
        suffix = f"-{i}"
        slug = f"{base[:maxlen - len(suffix)]}{suffix}"
        i += 1
    return slug


def generate_negative_id(model: type[models.Model]) -> int:
    """Acuña un mal_id negativo único para una entidad local sin id de MAL.
    Mantiene mal_id/p_mal_id únicos sin chocar con los ids reales (positivos)."""
    lowest = model.objects.aggregate(v=Min("mal_id"))["v"]
    base = lowest if (lowest is not None and lowest < 0) else 0
    return base - 1


def season_of(fecha: datetime.date | None) -> str:
    """Temporada (invierno/primavera/verano/otoño) por el MES de una fecha: ene-mar, abr-jun, jul-sep, oct-dic."""
    if not fecha:
        return ""
    return ("WINTER", "SPRING", "SUMMER", "FALL")[(fecha.month - 1) // 3]


def filas_obra(filas: Iterable[Any], obra: Lector, rol: Lector | None = None, sub: Lector | None = None) -> list[Any]:
    """Normaliza filas de un puente (reparto, staff, roles de personaje…) para el parcial detail/_obras.html:
    a cada fila le cuelga `obra` (la obra enlazada), `rol` (texto de la derecha) y `rol_sub` (debajo).
    `obra`/`rol`/`sub` son el nombre del atributo o un callable(fila)."""
    def lee(f: Any, x: Lector | None) -> Any:
        if x is None:
            return ""
        return x(f) if callable(x) else getattr(f, x, "")
    out = []
    for f in filas:
        o = lee(f, obra)
        if o is None:
            continue
        f.obra, f.rol, f.rol_sub = o, lee(f, rol), lee(f, sub)
        out.append(f)
    return out


def siguiente_orden(fila: models.Model) -> int:
    """El `order` que le toca a una imagen NUEVA: detrás de las que ya tiene su entidad (0 si es la primera).
    La entidad es la primera FK de la fila."""
    fk = next((f for f in fila._meta.fields if isinstance(f, models.ForeignKey)), None)
    if fk is None or getattr(fila, fk.attname) is None:
        return 0
    ultimo = type(fila).objects.filter(**{fk.attname: getattr(fila, fk.attname)}).aggregate(m=models.Max("order"))["m"]
    return 0 if ultimo is None else ultimo + 1
