"""pages · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.utils.html import escape

from apps.pages.models import AboutSection, PagesLog, PrivacySection, TermsSection
from apps.pages.views.base import BaseAboutSection, BasePagesLog, BasePrivacySection, BaseTermsSection
from core.shared.views.base import AdminDataView, BaseSelectView
from core.shared.views.filters import LogFilters
from core.utils.views_base import cell


# ==============================================================================
# Gestión
# ==============================================================================

LEGAL_COLUMNS = [("Orden", "order"), ("Título", "title"), ("Activo", "is_active")]


class AboutSectionDataView(BaseAboutSection, AdminDataView):
    columns = LEGAL_COLUMNS

    def get(self, request, tipo=None, pk=None):
        qs = AboutSection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["title", "body"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "order"),
                "c1": cell(obj, "title"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AboutSectionSelectView(BaseAboutSection, BaseSelectView):
    search_fields = ['title']


class PrivacySectionDataView(BasePrivacySection, AdminDataView):
    columns = LEGAL_COLUMNS

    def get(self, request, tipo=None, pk=None):
        qs = PrivacySection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["title", "body"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "order"),
                "c1": cell(obj, "title"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PrivacySectionSelectView(BasePrivacySection, BaseSelectView):
    search_fields = ['title']


class TermsSectionDataView(BaseTermsSection, AdminDataView):
    columns = LEGAL_COLUMNS

    def get(self, request, tipo=None, pk=None):
        qs = TermsSection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["title", "body"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "order"),
                "c1": cell(obj, "title"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class TermsSectionSelectView(BaseTermsSection, BaseSelectView):
    search_fields = ['title']


class PagesLogDataView(BasePagesLog, AdminDataView):
    columns = [('Nivel', 'get_level_display'), ('Proceso', 'process'), ('Mensaje', 'message'), ('Momento', 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = PagesLog.objects.all()
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
