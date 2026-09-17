"""Widgets de selección por AJAX (Select2 remoto) para relaciones a ESCALA.

Problema: una FK/M2M a un modelo con millones de filas NO puede volcar todas las
opciones en el `<select>` (colapsa el front). Solución (como el `data_url` de Hades):
el `<select>` solo renderiza lo YA seleccionado y busca el resto en el SERVIDOR por
AJAX (endpoint `<entidad>/select/`, ver BaseSelectView y las `XSelectView` de `views/admin/v1_data.py`).

Cada formulario declara EXPLÍCITAMENTE el widget de sus FK/M2M con el nombre de la
ruta `<entidad>_select` (una clase `XSelectView` por entidad, junto a su Data en `v1_data.py`):

    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:movie-genre_select'),
    )

Así se ve, leyendo el propio form, contra qué endpoint busca cada campo.
"""
from django import forms
from django.urls import NoReverseMatch, reverse


def titulo_con_anio(obj):
    """«Título (Título secundario) Año» para medios con título: dos películas con el
    mismo nombre en inglés y español se distinguen por el año. La usan la Data
    (columna Título de la lista) y el Select (opciones) de películas y series."""
    texto = str(obj)
    sec = (getattr(obj, "title_secundary", "") or "").strip()
    if sec and sec.lower() != texto.lower():
        texto = f"{texto} ({sec})"
    anio = getattr(obj, "release_year", None)
    return f"{texto} {anio}" if anio else texto


def etiqueta_select(obj):
    """Texto de una opción de Select2: «name (name_esp)» cuando el modelo tiene
    `name_esp` con valor (y difiere del original), p. ej. «Spanish (Español)»;
    si no, el str() normal. La usan BaseSelectView.option_label (resultados de búsqueda)
    y los widgets Ajax (opciones preseleccionadas) para que el select se vea IGUAL
    en ambos lados. La búsqueda entra por los DOS nombres (ver get_search_fields)."""
    if hasattr(obj, "title_secundary") and hasattr(obj, "release_year"):
        return titulo_con_anio(obj)   # películas y series: la opción preseleccionada igual que la lista
    texto = str(obj)
    esp = (getattr(obj, "name_esp", "") or "").strip()
    if esp and esp.lower() != texto.lower():
        return f"{texto} ({esp})"
    return texto


class _AjaxMixin:
    """Renderiza SOLO las opciones seleccionadas + marca el select para Select2-AJAX."""

    def __init__(self, url_name="", attrs=None):
        self.url_name = url_name
        super().__init__(attrs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        try:
            if self.url_name:
                attrs["data-ajax-url"] = reverse(self.url_name)
        except NoReverseMatch:
            pass
        attrs["class"] = (attrs.get("class", "") + " js-ajax-select").strip()
        return attrs

    def optgroups(self, name, value, attrs=None):
        # value = valores seleccionados. Solo renderizamos ESOS (el resto llega por AJAX).
        selected = [str(v) for v in value if v not in ("", None)]
        if not selected:
            return []
        qs = getattr(self.choices, "queryset", None)
        objs = {}
        if qs is not None:
            objs = {str(o.pk): o for o in qs.filter(pk__in=selected)}
        options = []
        for i, pk in enumerate(selected):
            obj = objs.get(pk)
            if obj is not None:
                options.append(self.create_option(name, obj.pk, etiqueta_select(obj), True, i))
        return [(None, options, 0)] if options else []


class AjaxSelect(_AjaxMixin, forms.Select):
    pass


class AjaxSelectMultiple(_AjaxMixin, forms.SelectMultiple):
    pass


# ── Selector de color por MUESTRAS (paleta del tema) ──────────────────────────
# El usuario elige un color de una fila de swatches (sin ver hex ni RGB). El valor
# guardado sigue siendo hex, pero es interno. Evita errores de tipeo y la confusión
# "decimos hex pero el picker muestra RGB".
from django.utils.safestring import mark_safe  # noqa: E402

COLOR_PALETTE = [
    ("#00e5ff", "Cian"), ("#38d39f", "Verde"), ("#e6b800", "Ámbar"),
    ("#4aa3ff", "Azul"), ("#ff5c7a", "Rojo"), ("#ff8a3d", "Naranja"),
    ("#a97bff", "Morado"), ("#ffcf3d", "Oro"), ("#7f95a8", "Gris"),
]


class ColorSwatchWidget(forms.Widget):
    """Muestra la paleta como botones; el elegido queda en un input hidden."""
    def render(self, name, value, attrs=None, renderer=None):
        value = (value or "#7f95a8").lower()
        wid = (attrs or {}).get("id") or f"id_{name}"
        chips = "".join(
            f'<button type="button" class="sw{" is-sel" if c.lower() == value else ""}" '
            f'data-c="{c}" style="--sw:{c}" title="{lbl}"></button>'
            for c, lbl in COLOR_PALETTE
        )
        return mark_safe(
            f'<div class="swatches" data-for="{wid}">{chips}</div>'
            f'<input type="hidden" name="{name}" id="{wid}" value="{value}">'
            f'<script>(function(){{'
            f'var b=document.querySelector(\'.swatches[data-for="{wid}"]\'),'
            f'h=document.getElementById("{wid}");'
            f'if(!b||!h)return;'
            f'b.addEventListener("click",function(e){{var s=e.target.closest(".sw");'
            f'if(!s)return;h.value=s.getAttribute("data-c");'
            f'b.querySelectorAll(".sw").forEach(function(x){{x.classList.remove("is-sel");}});'
            f's.classList.add("is-sel");}});}})();</script>'
        )
