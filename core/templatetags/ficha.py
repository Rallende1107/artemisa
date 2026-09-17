"""Filtros de las FICHAS (detail/base_detail.html y los HTML por entidad)."""
import json
import re

from django import template

from core.shared.views.base import admin_entity, url_by_route
from core.utils.public import resolve_cover
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.filter
def youtube_embed(url):
    """URL de YouTube (watch / youtu.be / shorts) → URL embebible para el iframe; otra URL, tal cual."""
    m = re.search(r"(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)([\w-]{6,})", url or "")
    return f"https://www.youtube.com/embed/{m.group(1)}" if m else (url or "")


@register.simple_tag
def by(ruta, tipo, padre):
    """Enlace a una lista «por» del lado que pinta: {% por by_url 'genero' genero %} → /…/genero/3/accion/."""
    return url_by_route(ruta, tipo, padre)


@register.simple_tag
def url_gestion(obj):
    """URL de la ficha de GESTIÓN de un objeto cualquiera (panel:<entidad>_detail); "" si no la hay."""
    ent = admin_entity(type(obj)) if obj is not None else ""
    try:
        return reverse(f"panel:{ent}_detail", args=[obj.pk]) if ent else ""
    except NoReverseMatch:
        return ""


@register.simple_tag(takes_context=True)
def ficha(context, obj):
    """URL de la ficha de un objeto EN EL LADO QUE PINTA: en gestión la de gestión (si la tiene), en público la
    pública (get_absolute_url). {% ficha persona %} en los parciales de reparto, personajes, obras…"""
    if obj is None:
        return ""
    if context.get("es_gestion"):
        u = url_gestion(obj)
        if u:
            return u
    return obj.get_absolute_url() if hasattr(obj, "get_absolute_url") else ""


@register.filter
def imagen(obj):
    """URL de la imagen de un objeto (la suya; si no, la de su primera imagen relacionada) o ""."""
    return resolve_cover(obj) or ""


@register.filter
def fotos(obj):
    """GALERÍA de un objeto: sus imágenes (XImage, en su orden), activas y con algo que
    mostrar (archivo o URL remota pendiente de descarga). {% with fotos=object|fotos %}."""
    filas = []
    for rel in ("images",):
        qs = getattr(obj, rel, None)
        if qs is None or not hasattr(qs, "all"):
            continue
        for f in qs.all():
            if getattr(f, "is_active", True) and resolve_cover(f):
                filas.append(f)
    return filas


@register.filter
def json_bonito(valor):
    """JSON crudo (dict/list del JSONField) → texto indentado para un <pre> en la ficha de datos."""
    try:
        return json.dumps(valor, ensure_ascii=False, indent=2, sort_keys=True)
    except (TypeError, ValueError):
        return str(valor)


@register.filter
def get_item(d, clave):
    """{{ tab_url|get_item:clave }}: valor de un diccionario por clave variable (o "")."""
    return (d or {}).get(clave, "")
