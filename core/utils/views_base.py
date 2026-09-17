"""Ayudantes de core/shared/views/base.py (las Base* del panel): la cáscara
para auditar borrados y las funciones que usan la lista y los endpoints JSON. Nada de aquí es
una vista; las vistas base viven en base_views.py y el cromo/candados en views.py."""
from django.db.models import BooleanField, Q

from core.utils.views import _model_has_field
import datetime
import json
from django.db.models.fields.files import FieldFile
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe


class _Borrado:
    """Cáscara de un objeto ya borrado, para auditarlo: modelo real, pk y nombre."""
    def __init__(self, model, pk, nombre):
        self._model, self.pk, self._nombre = model, pk, nombre

    def __str__(self):
        return self._nombre


def _resolve(obj, attr):
    """Resuelve un atributo/método/relación para pintar una cell."""
    value = getattr(obj, attr, "")
    if callable(value):
        value = value()
    return value


# Etiqueta legible de cada sección (para el breadcrumb "volver a …").


def _is_bool_field(model, attr):
    try:
        return isinstance(model._meta.get_field(attr), BooleanField)
    except Exception:
        return False   # atributos calculados, métodos, relaciones…


JSON_CELL_CHARS = 90      # cuántos caracteres del JSON se ven en la celda «Datos»


def _is_multivalue(model, ruta):
    """True si `ruta` (p. ej. "titles__title") cruza una relación uno-a-muchos o M2M:
    entonces la búsqueda necesita distinct() para no repetir filas."""
    partes = ruta.split("__")
    for nombre in partes[:-1]:
        try:
            f = model._meta.get_field(nombre)
        except Exception:
            return False
        if f.one_to_many or f.many_to_many:
            return True
        model = f.related_model
    return False


def search_words(model, qs, q, campos):
    """Búsqueda por PALABRAS sobre `campos` (icontains): cada palabra tecleada debe aparecer
    en ALGÚN campo, en cualquier orden — «murray bill» y «bill m» dan con Bill Murray;
    «will» no (subcadena, sin tolerancia a erratas). Los campos pueden cruzar relaciones
    («titles__title» = títulos sinónimos, «nicknames__nickname» = apodos)."""
    palabras = [w for w in (q or "").split() if w]
    if not palabras or not campos:
        return qs
    for w in palabras:
        cond = Q()
        for f in campos:
            cond |= Q(**{f"{f}__icontains": w})
        qs = qs.filter(cond)
    if any(_is_multivalue(model, f) for f in campos):
        qs = qs.distinct()
    return qs


def _order_field(model, attr):
    """Devuelve el campo de BD por el que ordenar una columna (o None si no aplica)."""
    field = attr
    if attr.startswith("get_") and attr.endswith("_display"):
        field = attr[4:-8]
    if attr == "display_name":   # columna compuesta: ordena por el nombre/título base
        field = next((f for f in ("name", "title") if _model_has_field(model, f)), attr)
    try:
        model._meta.get_field(field)
        return field
    except Exception:
        return None


# ------------------------------------------------------------------ celdas
def cell(obj, attr, truncar=0):
    """Una cell a partir de un atributo / propiedad / método del objeto: booleano → píldora Sí/No, fecha → legible,
    ImageField → miniatura, JSON → recortado, texto largo → recortado con `truncar`, HTML marcado → tal cual."""
    v = _resolve(obj, attr)
    if isinstance(v, str) and hasattr(obj, f"get_{attr}_display"):   # campo con choices → su etiqueta, no el código
        v = getattr(obj, f"get_{attr}_display")()
    if isinstance(v, SafeData):
        return str(v)
    if isinstance(v, FieldFile):
        try:
            url = v.url if v else ""
        except ValueError:
            url = ""
        return f'<img class="dt-thumb" src="{url}" alt="" loading="lazy">' if url else '<span class="dt-thumb dt-thumb--vacia"></span>'
    if isinstance(v, bool):
        cls, label = ("on", "Sí") if v else ("off", "No")
        return f'<span class="stat {cls}">{label}</span>'
    if isinstance(v, datetime.datetime):
        if timezone.is_aware(v):
            v = timezone.localtime(v)
        return v.strftime("%d-%m-%Y %H:%M:%S")
    if isinstance(v, datetime.date):
        return v.strftime("%d-%m-%Y")
    if truncar and isinstance(v, str) and len(v) > truncar:
        return f'<span title="{escape(v[:600])}">{escape(v[:truncar])}…</span>'
    if isinstance(v, (dict, list)):
        texto = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
        corto = texto[:JSON_CELL_CHARS] + ("…" if len(texto) > JSON_CELL_CHARS else "")
        return f'<code class="json-cell" title="{escape(texto[:600])}">{escape(corto)}</code>'
    return "" if v is None else escape(str(v))


def cell_cover(url, img, titulo, meta=""):
    """Portada 50×70 + título enlazado + línea de meta (columns = [(_("Título"), "ficha"), …])."""
    from django.templatetags.static import static
    src = img or static("image/default/sin-imagen.webp")
    meta_html = f'<span class="dt-meta">{escape(meta)}</span>' if meta else ""
    return mark_safe(f'<a class="dt-title dt-title--col" href="{url or "#"}"><img class="dt-thumb dt-thumb--lg" src="{src}" alt="" loading="lazy">'
                     f'<span><span class="dt-name">{escape(titulo or "")}</span>{meta_html}</span></a>')


def cell_miniatura(obj):
    """Miniatura de una fila de imagen: el archivo si ya está descargado; si no, la URL remota; si no hay nada, vacía."""
    src = getattr(obj, "cover_url", "") or ""
    if not src:
        return '<span class="dt-thumb dt-thumb--vacia"></span>'
    return mark_safe(f'<img class="dt-thumb" src="{escape(src)}" alt="" loading="lazy">')


def link(url, texto):
    """`texto` ya viene escapado (sale de cell()); si no, escápalo antes."""
    return mark_safe(f'<a href="{url}">{texto}</a>') if url else (texto or "")


def meta_line(obj):
    """«TV · 24 eps · 2023» con lo que la obra tenga (tipo, total, año)."""
    partes = []
    tipo = next((getattr(obj, f.name) for f in obj._meta.fields if f.name.endswith("_type") and f.is_relation), None)
    if tipo:
        partes.append(str(getattr(tipo, "display_name", None) or tipo))
    for campo, sufijo in (("episodes", "eps"), ("chapters", "caps")):
        total = getattr(obj, campo, None)
        if total:
            partes.append(f"{total} {sufijo}")
            break
    fecha = getattr(obj, "release_date", None)
    anio = getattr(obj, "year", None) or getattr(obj, "release_year", None) or getattr(obj, "start_year", None) or (fecha.year if fecha else None)
    if anio:
        partes.append(str(anio))
    return " · ".join(partes)


# ------------------------------------------------------------------ parámetros de DataTables
class Params:
    """draw / start / length / búsqueda / orden de la petición, y `orden(columns, order_map, defecto)` → campos de order_by."""

    def __init__(self, request, page_size):
        p = request.GET
        try:
            self.draw, self.start, self.length = int(p.get("draw", 1)), int(p.get("start", 0)), int(p.get("length", page_size))
        except (TypeError, ValueError):
            self.draw, self.start, self.length = 1, 0, page_size
        if self.length < 0 or self.length > 200:
            self.length = page_size
        self.search = (p.get("search[value]") or "").strip()
        self.order_col = p.get("order[0][column]")
        self.order_dir = p.get("order[0][dir]", "asc")
        self.clave = p.get(f"columns[{self.order_col}][data]", "") if self.order_col is not None else ""

    def ordering(self, columns, order_map=None, defecto=("pk",), model=None):
        """Campos para `order_by`: la columna pedida (por `order_map`, o el propio atributo si es campo del modelo) y
        `defecto` de desempate. Sin `order_map` una FK ordena por su id; el atributo «ficha» necesita entrada."""
        order_map = order_map or {}
        campos = []
        signo = "-" if self.order_dir == "desc" else ""
        if self.clave == "id":
            campos.append(signo + "pk")
        elif self.clave.startswith("c"):
            try:
                attr = columns[int(self.clave[1:])][1]
            except (ValueError, IndexError):
                attr = None
            of = order_map.get(attr) or (_order_field(model, attr) if model is not None and attr else None) or (attr if attr and model is None else None)
            if of:
                campos.append(signo + of)
        vistos = {c.lstrip("-") for c in campos}
        campos += [d for d in defecto if d.lstrip("-") not in vistos]
        return campos


class LazySeq(list):
    """Secuencia perezosa: los tipos salen del catálogo (BD) y las cards/enlaces se declaran al importar. Se evalúa al
    iterar (en la petición), nunca al importar ni en `ready()` (sin tabla todavía → vacío)."""
    def __init__(self, fabrica):
        self._fabrica = fabrica
    def _v(self):
        try:
            return list(self._fabrica())
        except Exception:  # noqa: BLE001
            return []
    def __iter__(self):
        return iter(self._v())
    def __len__(self):
        return len(self._v())
    def __bool__(self):
        return True
    def __getitem__(self, i):
        return self._v()[i]
