from django.utils.translation import gettext_lazy as _

from core.shared.views.base import BaseHomeView


class CatalogsHomeView(BaseHomeView):
    title = "Catálogos"
    active_entity = "catalogs-home"
    background_image = "bg-catalogs-home"
    background_fallback = "bg-catalogs-home"
    groups = [
        (
            _("Localización"),
            [
                (
                    "country",
                    _("Países"),
                    '<i class="bi bi-globe-americas"></i>',
                    "bg-catalogs-country",
                ),
                (
                    "language",
                    _("Idiomas"),
                    '<i class="bi bi-translate"></i>',
                    "bg-catalogs-language",
                ),
            ],
        ),
        (
            _("Referencias"),
            [
                (
                    "format",
                    _("Formatos"),
                    '<i class="bi bi-file-earmark"></i>',
                    "bg-catalogs-format",
                ),
                (
                    "quality",
                    _("Calidades"),
                    '<i class="bi bi-badge-hd"></i>',
                    "bg-catalogs-quality",
                ),
                (
                    "website",
                    _("Sitios web"),
                    '<i class="bi bi-globe"></i>',
                    "bg-catalogs-website",
                ),
                (
                    "external-source",
                    _("Fuentes externas"),
                    '<i class="bi bi-link-45deg"></i>',
                    "bg-catalogs-external-source",
                ),
            ],
        ),
        (
            _("Tipos"),
            [
                (
                    "relation-type",
                    _("Tipos de relación"),
                    '<i class="bi bi-arrow-left-right"></i>',
                    "bg-catalogs-relation-type",
                ),
            ],
        ),
        (
            _("Registro"),
            [
                (
                    "catalogs-log",
                    _("Log de catálogos"),
                    '<i class="bi bi-journal-text"></i>',
                    "bg-catalogs-log",
                ),
            ],
        ),
    ]
