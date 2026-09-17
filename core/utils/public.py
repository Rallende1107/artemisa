"""Ayudantes de la cara PÚBLICA (sin vistas): imagen de un objeto, URL canónica de una ficha, tarjetas de
portada de los homes, favoritos de la colección y voces ordenadas."""
from django.urls import reverse


_THEMES = ("t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8")


def resolve_cover(obj):
    """PORTADA de un objeto (hermano de resolve_background, que da el fondo de la clase): la URL de su imagen: su archivo; si no, el de su primera imagen relacionada; y si
    esa aún no se descargó, su URL REMOTA (`image_url`), para no mostrar un hueco mientras el
    descargador de imágenes hace lo suyo."""
    img = getattr(obj, "image", None)
    try:
        if img:
            return img.url
    except (ValueError, AttributeError):
        pass
    if getattr(obj, "image_url", "") and not getattr(obj, "download_dead", False):   # fila con URL pendiente (no muerta)
        return obj.image_url
    # Sin imagen propia (p. ej. Character): la primera relacionada que sirva (archivo, o URL que no esté muerta).
    rel = getattr(obj, "images", None)
    if rel is not None and hasattr(rel, "all"):
        for fila in rel.all()[:5]:
            f = getattr(fila, "image", None)
            try:
                if f:
                    return f.url
            except (ValueError, AttributeError):
                pass
            if getattr(fila, "image_url", "") and not getattr(fila, "download_dead", False):
                return fila.image_url
    return None


def url_detail(ruta, obj):
    """URL CANÓNICA de una ficha, estilo MAL: /<pk>/<slug>/ — el pk resuelve,
    el slug solo decora. Si la ruta no acepta slug (o el objeto no tiene),
    cae a /<pk>/."""
    from django.urls import NoReverseMatch

    slug = getattr(obj, "slug", "") or ""
    if slug:
        try:
            return reverse(ruta, args=[obj.pk, slug])
        except NoReverseMatch:
            pass
    return reverse(ruta, args=[obj.pk])


def cover_cards(objs, tag, url_name=None, sub=None):
    """Tarjetas para las filas del home público. `sub` es un callable opcional
    (por defecto: el año si el objeto lo tiene). Sin portada → tinte tN."""
    out = []
    for i, o in enumerate(objs):
        year = getattr(o, "release_year", None) or getattr(o, "year", None)
        out.append({
            "tag": tag,
            "name": str(o),
            "sub": sub(o) if sub else (str(year) if year else ""),
            "theme": _THEMES[i % len(_THEMES)],
            "image": resolve_cover(o),
            "url": url_detail(url_name, o) if url_name else "",
        })
    return out


def favorites_of(usuario, modelo, tope=12):
    """Los favoritos DEL USUARIO para ese modelo (sin login, vacío). Orden: lo último marcado."""
    from apps.collections.models import ModelBaseCollection

    if not getattr(usuario, "is_authenticated", False):
        return []
    tabla = ModelBaseCollection.de_contenido(modelo)
    if tabla is None:
        return []
    qs = tabla.favoritos()
    pks = list(qs.filter(user=usuario).order_by("-updated_at").values_list("content_id", flat=True)[:tope])
    objs = {o.pk: o for o in modelo.objects.filter(pk__in=pks, is_active=True)}
    return [objs[pk] for pk in pks if pk in objs]


def populares_de(modelo, tope=12):
    """Los que MÁS usuarios tienen en su colección (fila «X populares» de los homes), sea o no favorito: cuenta
    filas por contenido y devuelve los objetos activos de más a menos. Un modelo sin tabla de colección → vacío."""
    from django.db.models import Count

    from apps.collections.models import ModelBaseCollection

    tabla = ModelBaseCollection.de_contenido(modelo)
    if tabla is None:
        return []
    filas = (tabla.objects.values("content_id").annotate(n=Count("id")).order_by("-n", "content_id")[:tope])
    pks = [f["content_id"] for f in filas]
    objs = {o.pk: o for o in modelo.objects.filter(pk__in=pks, is_active=True)}
    return [objs[pk] for pk in pks if pk in objs]


