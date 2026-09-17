"""companies · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company, CompanyImage, CompanyLog
from apps.companies.views.base import BaseCompany, BaseCompanyImage, BaseCompanyImageContext, BaseCompanyLog
from apps.companies.views.v2_filters import CompanyFilters
from core.shared.views.base import AdminDataView, BaseSelectView, PublicDataView
from core.shared.views.filters import ImagenesFilters, LogFilters
from core.utils.queries import con_nube, con_relacion
from core.utils.views_base import cell, cell_cover, cell_miniatura, meta_line


# ==============================================================================
# Gestión
# ==============================================================================


class CompanyDataView(BaseCompany, AdminDataView):
    columns = [(_('Nombre'), 'name'), (_('País'), 'country'), (_('Fundación'), 'founded_year'), (_('Activo'), 'is_active')]
    filters = CompanyFilters

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.select_related("country")
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "country"),
                "c2": cell(obj, "founded_year"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

    def prepare(self, request, objetos):
        """Los enlaces a la ficha MAL de toda la página, en UNA consulta (no una por fila)."""
        super().prepare(request, objetos)
        from apps.otaku import fichas_mal
        self._fichas_mal = fichas_mal.enlaces("company", [o.pk for o in objetos])

    def extra_row_actions(self, obj, request):
        from apps.otaku import fichas_mal
        return fichas_mal.menu("company", obj, getattr(self, "_fichas_mal", None))


class CompanyMovieDataView(CompanyDataView):
    """Compañías de CINE: productoras o distribuidoras de al menos una película (lista fija del panel)."""

    def get(self, request, tipo=None, pk=None):
        qs = (Company.objects.select_related("country")
              .filter(con_relacion(Company, "movies_produced", "movies_distributed")))
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "country"),
                "c2": cell(obj, "founded_year"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CompanySerieDataView(CompanyDataView):
    """Compañías de TV: productoras o distribuidoras de al menos una serie (lista fija del panel)."""

    def get(self, request, tipo=None, pk=None):
        qs = (Company.objects.select_related("country")
              .filter(con_relacion(Company, "series_produced", "series_distributed")))
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "country"),
                "c2": cell(obj, "founded_year"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CompanySelectView(BaseCompany, BaseSelectView):
    search_fields = ['name']


class CompanyImageDataView(BaseCompanyImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Compañía'), 'company'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def filtrar(self, qs):
        """Las listas FIJAS (p. ej. «(MAL)») acotan aquí; la general no."""
        return qs

    def get(self, request, tipo=None, pk=None):
        qs = self.filtrar(con_nube(CompanyImage.objects.select_related("company")))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url', 'company__name'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "company"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "company", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

class CompanyImageSelectView(BaseCompanyImage, BaseSelectView):
    search_fields = ['image_url']


class CompanyLogDataView(BaseCompanyLog, AdminDataView):
    columns = [('Nivel', 'get_level_display'), ('Proceso', 'process'), ('Mensaje', 'message'), ('Momento', 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = CompanyLog.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['process', 'message'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "get_level_display"),
                "c1": cell(obj, "process"),
                "c2": cell(obj, "message", truncar=120),
                "c3": cell(obj, "timestamp"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


# ==============================================================================
# Público
# ==============================================================================


class CompanyPublicDataView(BaseCompany, PublicDataView):
    """Catálogo de TODAS las compañías, de cualquier medio."""
    columns = [(_("Nombre"), "ficha"), (_("País"), "country")]
    filters = CompanyFilters
    priority = {"ficha": 1}
    detail_url_name = "companias:company-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.select_related("country")
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            nombre = str(obj.name or "")
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, nombre, meta_line(obj)),
                "c1": cell(obj, "country"),
                "acciones": self.row_actions(obj, request, nombre),
                "detail_url": self.detail_url(obj), "card_title": escape(nombre), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)
