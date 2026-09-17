"""El enlace a la FICHA MAL de una persona o compañía neutra, para quien lo pinte desde fuera de otaku (la ficha y el
menú de fila de personas y compañías, el aviso de candidatas del formulario MAL).

Si ya tiene ficha → «Ficha MAL» (editarla). Si no → «Añadir ficha MAL» (el mismo formulario, con la entidad cargada).
Vive en otaku porque MAL es cosa de otaku: people y companies solo lo importan donde lo pintan."""
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

from apps.otaku.models import CompanyMAL, PersonMAL


# tipo → (modelo de la ficha, campo que apunta a la entidad, ruta «añadir», ruta «editar»)
_TIPOS = {
    "person": (PersonMAL, "person_id", "panel:person-mal_add", "panel:person-mal_update"),
    "company": (CompanyMAL, "company_id", "panel:company-mal_add", "panel:company-mal_update"),
}


def enlace(tipo, entidad_pk, ficha=None):
    """{"url", "label", "icon", "tiene"} hacia la ficha MAL de esa entidad, o None si la ruta no existe."""
    modelo, campo, ruta_add, ruta_edit = _TIPOS[tipo]
    if ficha is None:
        ficha = modelo.objects.filter(**{campo: entidad_pk}).first()
    try:
        if ficha is not None:
            return {"url": reverse(ruta_edit, args=[ficha.pk]), "label": _("Ficha MAL"), "icon": "stars", "tiene": True}
        return {"url": reverse(ruta_add, args=[entidad_pk]), "label": _("Añadir ficha MAL"), "icon": "plus-circle", "tiene": False}
    except NoReverseMatch:
        return None


def enlaces(tipo, pks):
    """Lo mismo para muchas entidades de una vez (una sola consulta): {pk: enlace}. Para los menús de fila."""
    modelo, campo, _add, _edit = _TIPOS[tipo]
    fichas = {getattr(f, campo): f for f in modelo.objects.filter(**{f"{campo}__in": list(pks)})}
    return {pk: enlace(tipo, pk, fichas.get(pk)) for pk in pks}


def menu(tipo, obj, cache):
    """El <a> del menú de fila; `cache` es el dict de `enlaces()` de esa página."""
    e = cache.get(obj.pk) if cache is not None else enlace(tipo, obj.pk)
    if not e:
        return []
    return [f'<a role="menuitem" href="{e["url"]}"><i class="bi bi-{e["icon"]} ic"></i> {e["label"]}</a>']
