"""Consultas que aguantan tablas de MILLONES de filas.

«Tiene al menos una obra» NO se escribe `filter(relacion__isnull=False).distinct()`: eso hace JOIN contra la tabla
intermedia (una fila por obra) y luego DISTINCT para quitar repetidos, y la Data lo corre dos veces con COUNT(*).
Con `con_relacion` sale `WHERE EXISTS (SELECT 1 … WHERE fk = id)`: Postgres se detiene en la primera fila que
encuentra, usa el índice de la FK de la tabla intermedia y no hace falta DISTINCT.
"""
from __future__ import annotations

from django.db import models
from django.db.models import Exists, OuterRef, Q


def con_nube(qs: models.QuerySet, campo: str = "image") -> models.QuerySet:
    """Anota `en_nube` (bool): el archivo de `campo` ya está en la nube según `system.CloudFile`. EXISTS por fila de la
    página, con el índice único de `CloudFile.name`."""
    from apps.system.models import CloudFile
    return qs.annotate(en_nube=Exists(CloudFile.objects.filter(name=OuterRef(campo))))


def existe_relacion(model: type[models.Model], nombre: str) -> Exists:
    """EXISTS de una relación de `model` (M2M directa o inversa, o FK inversa) apuntando a la fila exterior."""
    campo = model._meta.get_field(nombre)
    if campo.many_to_many:
        if campo.auto_created:                                   # M2M inversa (Company.movies_produced)
            through = campo.through
            fk = campo.field.m2m_reverse_field_name()            # la columna de la intermedia que apunta a `model`
        else:                                                    # M2M declarada en `model`
            through = campo.remote_field.through
            fk = campo.m2m_field_name()
        return Exists(through.objects.filter(**{fk: OuterRef("pk")}))
    if campo.one_to_many or campo.one_to_one:                    # FK inversa (Person.movie_cast)
        return Exists(campo.related_model.objects.filter(**{campo.field.name: OuterRef("pk")}))
    raise ValueError(f"{model.__name__}.{nombre} no es una relación a muchos")


def con_relacion(model: type[models.Model], *nombres: str) -> Q:
    """Q «tiene al menos una fila en ALGUNA de estas relaciones», con EXISTS (sin JOIN ni DISTINCT).

        Company.objects.filter(con_relacion(Company, "movies_produced", "movies_distributed"))
    """
    condicion = Q()
    for nombre in nombres:
        condicion |= Q(existe_relacion(model, nombre))
    return condicion
