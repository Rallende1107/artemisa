"""Ayudantes de core/views/v8_actions.py (y de todo el que pinte una página del sitio):
el fondo con respaldo y la comprobación de campos del modelo. Nada de aquí es una vista."""
from django.contrib.staticfiles import finders
from django.templatetags.static import static


def _bg_from_class(bg_class):
    """URL de la imagen 'wide' de una clase de fondo `bg-<app>-<x>`, o None si no
    existe. Namespace PLANO `image/screen/` (patrón Poseidon): los .webp viven en
    static/image/screen/<orient>/ y collectstatic los fusiona ahí."""
    if not bg_class or bg_class.count("-") < 1:
        return None
    rel = f"image/screen/wide/{bg_class}.webp"
    return static(rel) if finders.find(rel) else None


def resolve_background(view):
    """Fondo de la vista con RESPALDO: si la clase declarada en `background_image`
    no tiene imagen (falta image/screen/wide/<clase>.webp), se usa
    `background_fallback` (si la vista/config lo declara). Así cada entidad
    puede apuntar a su fondo propio sin miedo a quedar sin fondo."""
    bg = getattr(view, "background_image", "")
    fb = getattr(view, "background_fallback", "")
    if _bg_from_class(bg) or not fb:
        return bg
    # `background_fallback` puede ser una cadena o una TUPLA de respaldos en orden
    # (vistas fijas: primero el fondo de su entidad madre, luego el de la sección).
    cadena = [fb] if isinstance(fb, str) else list(fb)
    for c in cadena:
        if c and c != bg and _bg_from_class(c):
            return c
    return cadena[-1] if cadena else bg


def _model_has_field(model, name):
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False
