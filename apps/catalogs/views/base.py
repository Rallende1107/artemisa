from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import CatalogsLog, Country, ExternalSource, Format, Language, Quality, RelationType, Website


class _Catalogs:
    background_fallback = "bg-catalogs-home"
    section_url = "panel:catalogs-home"
    section_label = _("Catálogos")


class BaseCountry(_Catalogs):
    model = Country
    entity = "country"
    label = _("país")
    label_plural = _("países")
    background_image = "bg-catalogs-country"


class BaseExternalSource(_Catalogs):
    model = ExternalSource
    entity = "external-source"
    label = _("fuente externa")
    label_plural = _("fuentes externas")
    background_image = "bg-catalogs-external-source"


class BaseExternalSourceContext(BaseExternalSource):
    """Mapa «por» de fuentes externas: tipo → (campo, título, fondo). `type` acota por el CHOICE del campo `type`
    (valor en la URL, validado contra sus choices); lo comparten la Data (filtra) y la ListBy (título, fondo).
    """

    filter_config = {
        "type": (
            "type",
            _("Fuentes externas · {valor}"),
            "bg-catalogs-external-source",
        ),
    }


class BaseFormat(_Catalogs):
    model = Format
    entity = "format"
    label = _("formato")
    label_plural = _("formatos")
    background_image = "bg-catalogs-format"


class BaseLanguage(_Catalogs):
    model = Language
    entity = "language"
    label = _("idioma")
    label_plural = _("idiomas")
    background_image = "bg-catalogs-language"


class BaseQuality(_Catalogs):
    model = Quality
    entity = "quality"
    label = _("calidad")
    label_plural = _("calidades")
    background_image = "bg-catalogs-quality"


class BaseRelationType(_Catalogs):
    model = RelationType
    entity = "relation-type"
    label = _("tipo de relación")
    label_plural = _("tipos de relación")
    background_image = "bg-catalogs-relation-type"


class BaseWebsite(_Catalogs):
    model = Website
    entity = "website"
    label = _("sitio web")
    label_plural = _("sitios web")
    background_image = "bg-catalogs-website"


class BaseWebsiteContext(BaseWebsite):
    """Mapa «por» de sitios web: tipo → (campo, título, fondo). `type` acota por el CHOICE del campo `type`
    (valor en la URL, validado contra sus choices); lo comparten la Data (filtra) y la ListBy (título, fondo).
    """

    filter_config = {
        "type": (
            "type",
            _("Sitios web · {valor}"),
            "bg-catalogs-website",
        ),
    }


class BaseCatalogsLog(_Catalogs):
    model = CatalogsLog
    entity = "catalogs-log"
    label = _("log")
    label_plural = _("log de catálogos")
    background_image = "bg-catalogs-log"
