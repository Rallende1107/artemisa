"""El mapa «POR» (el FILTER_CONFIG de Poseidón): lo comparten la Data y las ListBy de una entidad.

    filter_config = {"genero": ("genres", _("Películas del género {padre}"), "bg-movies-genre"),
                     "status": ("status", _("Juegos · {valor}"), "")}
tipo → (campo que acota | "app.Modelo" cuando el filtro es compuesto, título, fondo[, choices explícitos]).
Con `pk` en la ruta la Data se acota: por PADRE (id entero de otro modelo) o por VALOR (choice del propio modelo).
Tipo fuera del mapa, id no entero / inexistente o valor fuera de los choices → 404 con mensaje (nada de
`movie/papafrita/-9999`). Los tipos compuestos los resuelve el mixin `Base<M>By` sobrescribiendo `filtro()`.
"""
from django.apps import apps
from django.http import Http404
from django.utils.translation import gettext as _

from core.shared.views.filters import _campo
from core.utils.views import _model_has_field

SIN_VALOR = "unknown"     # valor en la URL para «sin valor» en un choice opcional (/anime/season/unknown/)


def _entry_choices(modelo, c):
    """[(valor, etiqueta)] si la entrada del mapa es un CHOICE (4º elemento explícito, o campo con choices); None si es padre."""
    if len(c) >= 4 and c[3]:
        return list(c[3]() if callable(c[3]) else c[3])
    campo = c[0]
    if "." in campo:
        return None
    f = _campo(modelo, campo)
    if f is None or getattr(f, "is_relation", False):
        return None
    if not getattr(f, "flatchoices", None):
        return None
    pares = [(v, e) for v, e in f.flatchoices if v not in ("", None)]
    if getattr(f, "blank", False):
        pares.append((SIN_VALOR, _("Desconocido")))       # lista extra de un choice opcional: las filas sin valor
    return pares


def nav_fields(data):
    """Campos del modelo que el mapa «por» de la Data trata como CHOICE: en el panel son navegación, no filtro."""
    fc = getattr(data, "filter_config", None) or {}
    return {c[0] for c in fc.values() if _entry_choices(data.model, c) is not None}


class ByMixin:
    """Lo que una Data (o una ListBy, a través de su Data) sabe del padre / valor que trae la ruta."""
    filter_config = {}
    filters_by = {}      # {tipo: clase de filtros} cuando la lista «por» filtra distinto que la general
    sub_via = {}          # {tipo: (accessor en el padre, clave, valor)}: subtítulo de tarjeta acotado al padre
    staff_only = True

    def by_type(self):
        return (getattr(self, "kwargs", None) or {}).get("tipo", "")

    def in_by(self):
        """True si la ruta trae un padre (`pk`): la Data se acota a él."""
        return bool(self.filter_config) and "pk" in (getattr(self, "kwargs", None) or {})

    def cfg(self):
        """Entrada del mapa para el tipo en juego; None fuera de una «por». Tipo fuera del mapa → 404 con mensaje."""
        if not self.in_by():
            return None
        c = self.filter_config.get(self.by_type())
        if not c:
            raise Http404(_("El filtro de tipo «%(tipo)s» no es válido para %(que)s.") % {"tipo": self.by_type(), "que": self.label_plural})
        return c

    def is_choice(self):
        c = self.cfg()
        return bool(c) and _entry_choices(self.model, c) is not None

    def value(self):
        """El valor del choice que llega en la URL, validado contra la lista; fuera de ella → 404 con mensaje."""
        pares = dict((str(v), e) for v, e in _entry_choices(self.model, self.cfg()))
        v = str(self.kwargs.get("pk", ""))
        if v not in pares:
            raise Http404(_("El valor «%(v)s» de tipo «%(tipo)s» no es válido para %(que)s.") % {"v": v, "tipo": self.by_type(), "que": self.label_plural})
        return v

    def value_label(self):
        return dict((str(v), e) for v, e in _entry_choices(self.model, self.cfg())).get(self.value(), self.value())

    def parent_model(self):
        if self.is_choice():
            return None
        campo = self.cfg()[0]
        return apps.get_model(campo) if "." in campo else _campo(self.model, campo).related_model

    def parent(self):
        """El objeto al que está acotada la lista; None en la lista completa o si acota por choice.
        Id no entero o inexistente → 404 con mensaje."""
        if not self.cfg() or self.is_choice():
            return None
        if not hasattr(self, "_padre_obj"):
            crudo = self.kwargs.get("pk")
            try:
                pk = int(crudo)
            except (TypeError, ValueError):
                raise Http404(_("El id «%(id)s» de tipo «%(tipo)s» no es válido.") % {"id": crudo, "tipo": self.by_type()})
            modelo = self.parent_model()
            qs = modelo._default_manager.all()
            if _model_has_field(modelo, "is_active") and not self.staff_only:   # gestión ve también a los inactivos
                qs = qs.filter(is_active=True)
            obj = qs.filter(pk=pk).first()
            if obj is None:
                raise Http404(_("El id «%(id)s» de tipo «%(tipo)s» no existe.") % {"id": crudo, "tipo": self.by_type()})
            self._padre_obj = obj
        return self._padre_obj

    def exclude_filter(self, tipo, valor):
        """Para choices «resto»: kwargs de exclude(); {} = filtrar normal."""
        return {}

    def fixed_field(self):
        """El campo que la «por» fija (fuera del panel de filtros); "" si el filtro es compuesto."""
        c = self.cfg()
        return c[0] if c and "." not in c[0] else ""

    def filter_by(self, qs, padre, tipo):
        """Acota `qs` por el campo del tipo al padre (id) o al valor (choice). Los compuestos, en el mixin."""
        campo = self.filter_config[tipo][0]
        if "." in campo:
            raise NotImplementedError(f"{type(self).__name__}: el tipo «{tipo}» es compuesto; declara filtro(qs, padre, tipo) en el mixin")
        if self.is_choice():
            valor = self.value()
            excl = self.exclude_filter(tipo, valor)
            if excl:
                return qs.exclude(**excl)
            if valor == SIN_VALOR and SIN_VALOR not in [str(v) for v, _e in self.model._meta.get_field(campo).flatchoices]:
                return qs.filter(**{campo: ""})            # «desconocido» = sin valor
            return qs.filter(**{campo: valor})
        return qs.filter(**{campo: padre})

    def by(self, qs):
        """`qs` acotado al padre / valor de la ruta (o intacto en la lista completa)."""
        padre = self.parent()
        if padre is not None or (self.in_by() and self.is_choice()):
            return self.filter_by(qs, padre, self.by_type()).distinct()
        return qs

    def active_filters(self):
        """La clase de filtros de esta petición: la del tipo (`filters_by`) o la general."""
        return self.filters_by.get(self.by_type(), self.filters) if self.in_by() else self.filters

    def apply_filters(self, qs):
        """`qs` con el panel lateral aplicado (?country=3&is_active=1)."""
        filters = self.active_filters()
        return filters.apply(qs, self.request.GET, padre=self.parent()) if filters else qs

    def subs_by(self, tipo, padre):
        """{pk de la fila: subtítulo} acotado al padre, desde `sub_via[tipo]`; el mixin puede sobrescribirlo."""
        via = self.sub_via.get(tipo)
        if not via or padre is None:
            return {}
        accessor, clave, valor = via
        out = {}
        for k, v in getattr(padre, accessor).filter(is_active=True).values_list(clave, valor):
            if v:
                out.setdefault(k, []).append(str(v))
        return {k: ", ".join(v) for k, v in out.items()}

    def sub(self, obj):
        """Subtítulo de la fila acotado al padre (el rol EN ESTA obra); "" fuera de una «por»."""
        if not hasattr(self, "_subs_map"):
            self._subs_map = self.subs_by(self.by_type(), self.parent()) if self.in_by() else {}
        return self._subs_map.get(obj.pk, "")
