"""Filtros laterales de las listas del panel (como el FILTRO del admin de Django).

Cada modelo declara los suyos A MANO en `apps/<app>/views/admin/v5_filters.py`, con tipos
cerrados — nada genérico que adivine campos — y en TRES grupos (ver BaseFilters):

    class PersonAdminFilters(BaseFilters):
        model = Person
        generic_filters = [BooleanFilter("is_active", _("Activo"))]
        include_filters = [RelationFilter("country", _("País")), YearFilter("birth_date", _("Año de nacimiento"))]

La Data declara la clase (`filters = PersonAdminFilters`) y la List la toma de ella: la List pinta
el panel y la Data aplica lo que llega en la petición (`?country=3,55&is_active=1`), que es lo
que DataTables reenvía y lo que queda en la URL de la lista para poder compartirla.

Dos modos de pintar cada filtro (`modo`): «select» (Sí/No/Todo) y «lista» = DESPLEGABLE con
buscador y casillas, MULTI-selección (varios valores separados por coma en la URL: país Chile o
Japón, año 1996 o 1989). Por defecto: lista para todo filtro multi (relaciones, choices, años).
Sin recuentos por opción: el panel es barato aunque la tabla tenga millones de filas.

Los filtros son OPCIONALES: una lista sin `filters` no tiene panel ni botón (un catálogo como
países solo lleva el buscador). `LogFilters` / `DatosFilters` son los paneles compartidos para quien
solo quiera eso. Si el modelo no tiene `is_active`, ese filtro se omite solo."""
from django.utils.translation import gettext_lazy as _

def _campo(model, ruta):
    """El Field al final de una ruta `a__b__c` (None si no existe)."""
    try:
        for parte in ruta.split("__"):
            f = model._meta.get_field(parte)
            model = f.related_model
        return f
    except Exception:
        return None


class Filtro:
    """Un filtro del panel: `param` (nombre en la URL) = campo del modelo (admite rutas `a__b`).
    `modo`: "select" | "lista" | None (automático: lista si es multi, select si no).
    `ancla`: para listas ACOTADAS a un padre («Personajes de X» con la faceta Rol): lookup del
    padre en la MISMA relación (p. ej. "anime_appearances__anime"), así el rol se mira EN ESTA obra
    y no en cualquier otra. La Data lo pasa como `padre` al aplicar."""
    multi = False   # admite varios valores (a,b,c en la URL)

    def __init__(self, campo, etiqueta, modo=None, ancla="", padre_en=""):
        self.campo = campo
        self.etiqueta = etiqueta
        self.modo = modo
        self.ancla = ancla          # lookup del padre en la misma relación (filtrar)
        self.padre_en = padre_en    # campo del modelo relacionado que apunta al padre (acotar opciones)

    @property
    def param(self):
        return self.campo.replace("__", "-")

    def existe(self, model):
        return _campo(model, self.campo) is not None

    def options(self, model, padre=None):
        """[(valor, etiqueta)] que ofrece el <select>; sin «Todo», que lo pone la plantilla."""
        return []

    def _kw(self, valor, padre):
        """kwargs de UNA llamada filter(): el valor + (si hay ancla y padre) el padre en la misma relación."""
        kw = {self.campo: valor}
        if self.ancla and padre is not None:
            kw[self.ancla] = padre
        return kw

    def apply(self, qs, valor, padre=None):
        return qs.filter(**self._kw(valor, padre))

    def excluir(self, qs, valor, padre=None):
        """Lo CONTRARIO de `apply`: quita las filas que casan con cualquiera de los valores (sin el género X, sin
        Información…). Un `NOT IN (subconsulta)` por pk: vale igual para M2M, FK, choices y años."""
        base = qs.model._default_manager.all()
        casan = self.apply(base, valor, padre=padre)
        if casan is base:                       # valor vacío o inválido: no excluye nada
            return qs
        return qs.exclude(pk__in=casan.values("pk"))


EXCLUIR = "no-"      # prefijo del parámetro de exclusión en la URL / la petición: ?genres=1&no-genres=5


class BooleanFilter(Filtro):
    """Sí / No (texto, no solo color)."""
    def options(self, model, padre=None):
        return [("1", _("Sí")), ("0", _("No"))]

    def apply(self, qs, valor, padre=None):
        if valor not in ("1", "0"):
            return qs
        return qs.filter(**{self.campo: valor == "1"})


class RelationFilter(Filtro):
    """FK o M2M: las opciones son las filas del catálogo relacionado (solo activas si tiene
    `is_active`), en su orden natural, con `display_name` si el modelo lo tiene. MULTI: varios
    valores = cualquiera de ellos (país Chile o Japón)."""
    multi = True

    def options(self, model, padre=None):
        rel = _campo(model, self.campo).related_model
        qs = rel._default_manager.all()
        if any(f.name == "is_active" for f in rel._meta.fields):
            qs = qs.filter(is_active=True)
        if self.padre_en and padre is not None:          # acotadas al padre (los álbumes DEL artista)
            qs = qs.filter(**{self.padre_en: padre}).distinct()
        return [(str(o.pk), getattr(o, "display_name", None) or str(o)) for o in qs]

    def apply(self, qs, valor, padre=None):
        ids = [int(v) for v in valor.split(",") if v.strip().isdigit()]
        if not ids:
            return qs
        kw = self._kw(ids, padre); kw[f"{self.campo}__in"] = kw.pop(self.campo)
        return qs.filter(**kw).distinct() if "__" in self.campo or _campo(qs.model, self.campo).many_to_many or _campo(qs.model, self.campo).one_to_many else qs.filter(**kw)


class ChoiceFilter(Filtro):
    """Campo de TEXTO corto o con `choices` (estado, tipo, sexo, rol…). MULTI. ChoiceFilter: las
    `choices` del modelo o, si no las tiene, los valores distintos que haya en la tabla
    (acotados al padre si hay `ancla`). `etiquetas={"m": _("Masculino")}` traduce los valores."""
    multi = True

    def __init__(self, campo, etiqueta, modo=None, ancla="", padre_en="", etiquetas=None):
        super().__init__(campo, etiqueta, modo=modo, ancla=ancla, padre_en=padre_en)
        self.etiquetas = etiquetas or {}

    def options(self, model, padre=None):
        f = _campo(model, self.campo)
        if getattr(f, "flatchoices", None):
            return [(str(v), str(self.etiquetas.get(v, e))) for v, e in f.flatchoices]
        qs = model._default_manager.all()
        if self.ancla and padre is not None:
            qs = qs.filter(**{self.ancla: padre})
        valores = sorted({v for v in qs.order_by().values_list(self.campo, flat=True).distinct() if v})
        return [(str(v), str(self.etiquetas.get(v, v))) for v in valores]

    def apply(self, qs, valor, padre=None):
        valores = [v for v in valor.split(",") if v]
        if not valores:
            return qs
        kw = self._kw(valores, padre); kw[f"{self.campo}__in"] = kw.pop(self.campo)
        qs = qs.filter(**kw)
        return qs.distinct() if "__" in self.campo else qs


class YearFilter(Filtro):
    """Año de un campo fecha o un campo entero de año (admite rutas: `content__release_year`):
    opciones = los años que hay en la tabla (acotados al padre si hay ancla). MULTI."""
    multi = True

    def _campo_anio(self, model):
        f = _campo(model, self.campo)
        return f"{self.campo}__year" if f.get_internal_type() in ("DateField", "DateTimeField") else self.campo

    def options(self, model, padre=None):
        qs = model._default_manager.all()
        if self.ancla and padre is not None:
            qs = qs.filter(**{self.ancla: padre})
        anios = qs.exclude(**{f"{self.campo}__isnull": True}).order_by().values_list(self._campo_anio(model), flat=True).distinct()
        return [(str(a), str(a)) for a in sorted({a for a in anios if a}, reverse=True)]

    def apply(self, qs, valor, padre=None):
        anios = [int(v) for v in valor.split(",") if v.strip().isdigit()]
        if not anios:
            return qs
        kw = self._kw(anios, padre); kw[f"{self._campo_anio(qs.model)}__in"] = kw.pop(self.campo)
        return qs.filter(**kw)


class InicialFilter(Filtro):
    """Índice alfabético: A–Z y «#» (números, símbolos, japonés). MULTI. Campo `initial` con índice."""
    multi = True

    def options(self, model, padre=None):
        return [(c, c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ#"]

    def apply(self, qs, valor, padre=None):
        letras = [v for v in valor.split(",") if v in "ABCDEFGHIJKLMNOPQRSTUVWXYZ#" and len(v) == 1]
        if not letras:
            return qs
        kw = self._kw(letras, padre); kw[f"{self.campo}__in"] = kw.pop(self.campo)
        return qs.filter(**kw)


class BaseFilters:
    """La declaración de filtros de UN modelo, en DOS grupos (los mismos para gestión y público):

        class PersonAdminFilters(BaseFilters):
            model = Person
            generic_filters = [BooleanFilter("is_active", _("Activo"))]                 # Sí / No / Todo
            include_filters = [RelationFilter("country", _("País")), YearFilter("birth_date", _("Nacimiento"))]

    Incluir = «cualquiera de los marcados» (China o Japón). En la URL cada filtro usa el nombre del campo
    (`?country=1,5`). Lo que no está declarado no existe para esa lista (el público no puede ni pedir
    `?is_active=0` si su clase no lleva el genérico Activo)."""
    model = None
    generic_filters = []   # BooleanFilter, ChoiceFilter, YearFilter… (select o desplegable)
    include_filters = []   # RelationFilter / ChoiceFilter / YearFilter: cualquiera de los marcados
    template = "components/list_filters.html"   # el mini HTML del panel; una clase puede traer el suyo

    @classmethod
    def declared(cls, model=None):
        """[(filtro, grupo)] que aplican a este modelo (los de campos inexistentes se omiten)."""
        model = model or cls.model
        out = []
        for grupo, lista in (("generic", cls.generic_filters), ("include", cls.include_filters)):
            out += [(f, grupo) for f in lista if f.existe(model)]
        return out

    @classmethod
    def apply(cls, qs, params, padre=None):
        """Filtra `qs` con lo que venga en `params` (request.GET); lo vacío no filtra.
        `padre`: el objeto al que está acotada la lista (vistas «por» / «obras de»), para las anclas."""
        for f, _grupo in cls.declared(qs.model):
            valor = (params.get(f.param) or "").strip()
            if valor:
                qs = f.apply(qs, valor, padre=padre)
            fuera = (params.get(EXCLUIR + f.param) or "").strip()
            if fuera:
                qs = f.excluir(qs, fuera, padre=padre)
        return qs

    @classmethod
    def panel(cls, model, params, padre=None, sin=""):
        """Lo que pinta la plantilla: [(param, etiqueta, [(valor, etiqueta)], [valores actuales], modo, grupo)].
        `modo` = "lista" (desplegable con buscador + casillas, multi) o "select"; `grupo` = generic/include.
        `sin`: campo fijado por la URL (vistas «por»): ese filtro no se ofrece."""
        filas = []
        for f, grupo in cls.declared(model):
            if sin and f.campo == sin:
                continue
            opciones = f.options(model, padre=padre)
            param = f.param
            actual = [v for v in (params.get(param) or "").split(",") if v]
            modo = f.modo or ("lista" if f.multi else "select")
            filas.append((param, f.etiqueta, opciones, actual, modo, grupo))
        return filas

    @classmethod
    def panel_excluir(cls, model, params, padre=None, sin=""):
        """Las filas del bloque EXCLUIR: los MISMOS filtros que Incluir, con su parámetro `no-<param>` y el mismo control
        (lista o select). Excluir un valor = quitar las filas que casan con él (`Filtro.excluir`). Mismo formato que `panel`."""
        filas = []
        for f, grupo in cls.declared(model):
            if sin and f.campo == sin:
                continue
            param = EXCLUIR + f.param
            actual = [v for v in (params.get(param) or "").split(",") if v]
            filas.append((param, f.etiqueta, f.options(model, padre=padre), actual, f.modo or ("lista" if f.multi else "select"), grupo))
        return filas


class LogFilters(BaseFilters):
    """Panel de las listas de LOG (GameLog, OtakuLog, MusicLog…): nivel (info/warning/error) y activo."""
    generic_filters = [BooleanFilter("is_active", _("Activo"))]
    include_filters = [ChoiceFilter("level", _("Nivel"))]


class DatosFilters(BaseFilters):
    """Panel de las tablas de DATOS CRUDOS (Data*): fetch OK, procesado, código HTTP y activo."""
    generic_filters = [BooleanFilter("data_status", _("Fetch OK")), BooleanFilter("data_processed", _("Procesado")), BooleanFilter("is_active", _("Activo"))]
    include_filters = [ChoiceFilter("status_code", _("HTTP"))]


class EnNubeFilter(Filtro):
    """Sí / No: el archivo de la fila ya está en la nube (R2), según `system.CloudFile`. EXISTS por nombre, sin JOIN."""
    def options(self, model, padre=None):
        return [("1", _("Sí")), ("0", _("No"))]

    def apply(self, qs, valor, padre=None):
        if valor not in ("1", "0"):
            return qs
        from django.db.models import Exists, OuterRef
        from apps.system.models import CloudFile
        subida = Exists(CloudFile.objects.filter(name=OuterRef(self.campo)))
        return qs.filter(subida) if valor == "1" else qs.exclude(subida)


class EstadoDescargaFilter(Filtro):
    """Estado de descarga de una fila de imagen: descargada, pendiente, muerta o sin URL (por índice)."""
    def options(self, model, padre=None):
        return [("descargada", _("Descargada")), ("pendiente", _("Pendiente")), ("muerta", _("Muerta")), ("sin-url", _("Sin URL"))]

    def apply(self, qs, valor, padre=None):
        from core.shared.models.abstract import MAX_INTENTOS_DESCARGA as MAX
        if valor == "descargada":
            return qs.filter(image_downloaded=True)
        if valor == "pendiente":
            return qs.filter(image_downloaded=False, download_attempts__lt=MAX).exclude(image_url="")
        if valor == "muerta":
            return qs.filter(image_downloaded=False, download_attempts__gte=MAX).exclude(image_url="")
        if valor == "sin-url":
            return qs.filter(image_downloaded=False, image_url="")
        return qs


class ImagenesFilters(BaseFilters):
    """Panel de las tablas de IMÁGENES (AnimeImage, CompanyImage…): estado de descarga, en la nube y activo."""
    generic_filters = [EstadoDescargaFilter("image_downloaded", _("Estado de descarga")), EnNubeFilter("image", _("En la nube")),
                       BooleanFilter("is_active", _("Activo"))]
