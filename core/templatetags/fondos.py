"""Fondo por vista SIN CSS por clase (opción 1, piloto con series).

La vista sigue declarando `background_image = "bg-<app>-<x>"` en su base privada
(BaseSerie, BaseGenre…) o en su propia clase (vistas fijas, lanzadores). Antes esa clase
la traducía a rutas un bloque a mano en 03-backgrounds.css; ahora `{% bg_style %}` pone
las cuatro variables (--bg-wide/landscape/portrait/tall) en línea sobre .bg-layer, y
01-base.css sigue eligiendo por aspect-ratio. La ÚNICA fuente pasa a ser la carpeta
static/image/screen/: dejar el .webp con el nombre de la clase es todo el trabajo.

Si falta una orientación, usa la `wide` (antes el CSS apuntaba a un archivo inexistente y
la vista quedaba sin fondo en esa pantalla). Si falta la `wide`, no pone nada y la clase
queda solo como clase (respaldo: color base --ground o el bloque CSS si aún existe)."""
from django.contrib.staticfiles import finders
from django.template import Library
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = Library()
ORIENTACIONES = ("wide", "landscape", "portrait", "tall")


def rutas_de(clase):
    """{orientación: URL estática} de una clase de fondo, con la wide como respaldo
    de las orientaciones que falten. {} si no hay ni la wide.
    Si `clase` ya es una URL (la imagen del objeto en una ficha: /media/… o https://…),
    esa misma imagen sirve para las cuatro orientaciones."""
    if not clase:
        return {}
    if clase.startswith(("/", "http://", "https://")):
        return {o: clase for o in ORIENTACIONES}
    if not finders.find(f"image/screen/wide/{clase}.webp"):
        return {}
    wide = static(f"image/screen/wide/{clase}.webp")
    rutas = {}
    for o in ORIENTACIONES:
        rel = f"image/screen/{o}/{clase}.webp"
        rutas[o] = static(rel) if finders.find(rel) else wide
    return rutas


@register.simple_tag
def bg_style(clase):
    """Atributo ` style="--bg-wide:url(…); …"` para .bg-layer, o cadena vacía."""
    rutas = rutas_de(clase)
    if not rutas:
        return ""
    css = "; ".join(f"--bg-{o}:url('{u}')" for o, u in rutas.items())
    return mark_safe(f' style="{css}"')


@register.filter
def bg_clase(valor):
    """La clase para el atributo class de .bg-layer: solo si es una clase bg-…; una URL
    (imagen del objeto en una ficha) no es una clase y va únicamente por bg_style."""
    return valor if isinstance(valor, str) and valor.startswith("bg-") else ""
