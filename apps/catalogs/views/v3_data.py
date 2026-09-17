from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import CatalogsLog, Country, ExternalSource, Format, Language, Quality, RelationType, Website
from apps.catalogs.views.base import BaseCatalogsLog, BaseCountry, BaseExternalSource, BaseExternalSourceContext, BaseFormat, BaseLanguage, BaseQuality, BaseRelationType, BaseWebsite, BaseWebsiteContext
from apps.catalogs.views.v2_filters import CountryFilters, ExternalSourceFilters, FormatFilters, LanguageFilters, QualityFilters, RelationTypeFilters, WebsiteFilters
from core.shared.views.base import AdminDataView, BaseSelectView
from core.shared.views.filters import LogFilters
from core.utils.views_base import cell


# ==============================================================================
# Gestión
# ==============================================================================

CAT_COLUMNS = [("Nombre", "display_name"), ("Activo", "is_active")]
CAT_SEARCH = ["name", "name_esp"]
OST_COLUMNS = [
    ("Código", "code"),
    ("Clave", "key"),
    ("Nombre", "display_name"),
    ("Activo", "is_active"),
]


class CountryDataView(BaseCountry, AdminDataView):
    columns = [
        (_("Nombre"), "display_name"),
        (_("Código"), "code"),
        (_("Activo"), "is_active"),
    ]
    filters = CountryFilters
    priority = {"display_name": 1, "is_active": 2}

    def get(self, request, tipo=None, pk=None):
        qs = Country.objects.all()
        p, total, filtrado, objetos = self.query(
            request, qs, ["name", "name_esp", "code"], {}, ()
        )
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "display_name"),
                    "c1": cell(obj, "code"),
                    "c2": cell(obj, "is_active"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)


class CountrySelectView(BaseCountry, BaseSelectView):
    search_fields = ["name", "code"]


class ExternalSourceDataView(BaseExternalSourceContext, AdminDataView):
    """La Data de fuentes externas: `/data/` (todas) y `/data/<type>/` (solo un tipo: red social, monetización…)."""

    columns = [
        (_("Nombre"), "display_name"),
        (_("Tipo"), "get_type_display"),
        (_("URL"), "url"),
        (_("Activo"), "is_active"),
    ]
    filters = ExternalSourceFilters

    def get(self, request, tipo=None, pk=None):
        qs = ExternalSource.objects.all()
        p, total, filtrado, objetos = self.query(
            request, qs, ["name", "name_esp", "acronym", "url"], {}, ()
        )
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "display_name"),
                    "c1": cell(obj, "get_type_display"),
                    "c2": cell(obj, "url"),
                    "c3": cell(obj, "is_active"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)


class ExternalSourceSelectView(BaseExternalSource, BaseSelectView):
    search_fields = ["name", "acronym", "url"]


class FormatDataView(BaseFormat, AdminDataView):
    columns = [(_("Nombre"), "display_name"), (_("Activo"), "is_active")]
    filters = FormatFilters

    def get(self, request, tipo=None, pk=None):
        qs = Format.objects.all()
        p, total, filtrado, objetos = self.query(
            request, qs, ["name", "name_esp"], {}, ()
        )
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "display_name"),
                    "c1": cell(obj, "is_active"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)


class FormatSelectView(BaseFormat, BaseSelectView):
    search_fields = ["name", "name_esp"]


class LanguageDataView(BaseLanguage, AdminDataView):
    columns = [
        (_("Nombre"), "display_name"),
        (_("Acrónimo"), "acronym"),
        (_("Activo"), "is_active"),
    ]
    filters = LanguageFilters
    priority = {"display_name": 1, "is_active": 2}

    def get(self, request, tipo=None, pk=None):
        qs = Language.objects.all()
        p, total, filtrado, objetos = self.query(
            request, qs, ["name", "name_esp", "acronym"], {}, ()
        )
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "display_name"),
                    "c1": cell(obj, "acronym"),
                    "c2": cell(obj, "is_active"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)


class LanguageSelectView(BaseLanguage, BaseSelectView):
    search_fields = ["name", "acronym"]


class QualityDataView(BaseQuality, AdminDataView):
    columns = [(_("Nombre"), "display_name"), (_("Activo"), "is_active")]
    filters = QualityFilters

    def get(self, request, tipo=None, pk=None):
        qs = Quality.objects.all()
        p, total, filtrado, objetos = self.query(
            request, qs, ["name", "name_esp"], {}, ()
        )
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "display_name"),
                    "c1": cell(obj, "is_active"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)


class QualitySelectView(BaseQuality, BaseSelectView):
    search_fields = ["name", "name_esp"]


class RelationTypeDataView(BaseRelationType, AdminDataView):
    columns = CAT_COLUMNS
    filters = RelationTypeFilters

    def get(self, request, tipo=None, pk=None):
        qs = RelationType.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, CAT_SEARCH, {}, ())
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "display_name"),
                    "c1": cell(obj, "is_active"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)


class RelationTypeSelectView(BaseRelationType, BaseSelectView):
    search_fields = ["name", "name_esp"]


class WebsiteDataView(BaseWebsiteContext, AdminDataView):
    columns = [
        (_("Nombre"), "display_name"),
        (_("Tipo"), "get_type_display"),
        (_("URL"), "url"),
        (_("Activo"), "is_active"),
    ]
    filters = WebsiteFilters

    def get(self, request, tipo=None, pk=None):
        qs = Website.objects.all()
        p, total, filtrado, objetos = self.query(
            request, qs, ["name", "name_esp", "acronym", "url"], {}, ()
        )
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "display_name"),
                    "c1": cell(obj, "get_type_display"),
                    "c2": cell(obj, "url"),
                    "c3": cell(obj, "is_active"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)


class WebsiteSelectView(BaseWebsite, BaseSelectView):
    search_fields = ["name", "acronym", "url"]


class CatalogsLogDataView(BaseCatalogsLog, AdminDataView):
    columns = [
        (_("#"), "id"),
        (_("Nivel"), "get_level_display"),
        (_("Proceso"), "process"),
        (_("Mensaje"), "message"),
        (_("Momento"), "timestamp"),
    ]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = CatalogsLog.objects.all()
        p, total, filtrado, objetos = self.query(
            request, qs, ["process", "message"], {}, ()
        )
        filas = []
        for obj in objetos:
            filas.append(
                {
                    "id": obj.pk,
                    "c0": cell(obj, "id"),
                    "c1": cell(obj, "get_level_display"),
                    "c2": cell(obj, "process"),
                    "c3": cell(obj, "message", truncar=120),
                    "c4": cell(obj, "timestamp"),
                    "acciones": self.row_actions(obj, request),
                    "detail_url": self.detail_url(obj),
                    "card_title": escape(str(obj)),
                    "card_image": obj.cover_url,
                    "card_sub": "",
                    "card_actions": "",
                }
            )
        return self.response(p, total, filtrado, filas)
