"""Tags de la colección para la cara pública.

`{% collect_bar object collect_kind %}` pinta la barra "añadir a mi colección"
(o estado, nota, favorito y quitar si ya está) en la ficha pública. La vista de
detalle solo declara `collect_kind` = la clave MEDIO de la colección ("serie", "movie",
"anime", "manga", "game", "album", "artist", "song", "character", "person") — sin
importar nada de collections. `ModelBaseCollection.por_medio` da la tabla.
"""
from django import template

from apps.collections.models import ModelBaseCollection


register = template.Library()


@register.inclusion_tag("collections/_collect.html", takes_context=True)
def collect_bar(context, obj, kind):
    request = context["request"]
    tabla = ModelBaseCollection.por_medio(kind)
    data = {"kind": kind, "obj": obj, "next": request.path, "anon": False, "item": None,
            "medio": tabla.medio() if tabla else "",
            "statuses": [], "scores": range(1, 11)}
    if tabla is None:
        return data
    if not request.user.is_authenticated:
        data["anon"] = True
        return data
    item = tabla.objects.filter(user=request.user, content=obj).first()
    data["item"] = item
    if item is None:
        return data
    from django.urls import reverse
    data["edit_url"] = reverse("collections:edit", args=[tabla.medio(), item.pk])
    data["update_url"] = reverse("collections:update", args=[tabla.medio(), item.pk])
    data["statuses"] = tabla.estados()          # [(clave, etiqueta)]
    data["notas"] = range(1, 11)
    return data

