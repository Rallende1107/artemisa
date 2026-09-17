from django import forms
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import CatalogsLog, Country, ExternalSource, Format, Language, Quality, RelationType, Website
from core.shared.forms.base import FormBaseCategory
from core.shared.models.choices import ExternalSourceType, LogLevel, WebsiteType


class CountryForm(FormBaseCategory):
    """País: nombre, códigos ISO y bandera."""

    class Meta:
        model = Country
        fields = [
            "name", "name_esp", "code", "numeric_code", "description", "image", "is_active",
        ]

    duplicate_message = _('Ya existe un país con este nombre.')
    image_help = _('Bandera o imagen del país (opcional). Si se deja vacía se usa una por defecto.')

    code = forms.CharField(
        label=_("Código ISO"),
        help_text=_("ISO alfabético del país (CL, AR, JP). Se guarda en MAYÚSCULAS."),
        required=False,
        max_length=4,
        min_length=2,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("CL"),
                "aria-label": _("Código ISO"),
                "autocomplete": "off",
                "maxlength": 4,
                "style": "text-transform:uppercase",
                "title": _(
                    "ISO alfabético del país (CL, AR, JP). Se guarda en MAYÚSCULAS."
                ),
            }
        ),
        error_messages={
            "max_length": _("Máximo 4 caracteres."),
            "min_length": _("Mínimo 2 caracteres."),
        },
    )
    numeric_code = forms.IntegerField(
        label=_("Código numérico"),
        help_text=_("ISO numérico del país (152 para Chile). 0 si no aplica."),
        required=True,
        min_value=0,
        initial=0,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _("152"),
                "aria-label": _("Código numérico"),
                "autocomplete": "off",
                "inputmode": "numeric",
                "step": 1,
                "min": 0,
                "required": "required",
                "title": _("ISO numérico del país (152 para Chile). 0 si no aplica."),
            }
        ),
        error_messages={
            "required": _("Este campo es obligatorio."),
            "invalid": _("Introduce un número entero."),
            "min_value": _("El valor mínimo es 0."),
        },
    )

    def clean_code(self):
        return " ".join((self.cleaned_data.get("code") or "").split()).upper()


class ExternalSourceForm(FormBaseCategory):
    """Plataforma asociada a un creador/persona: blog, Discord, Patreon, X/Twitter…
    (Distinto de Sitio web: aquí es la presencia del autor, no dónde ver el contenido.)
    """

    class Meta:
        model = ExternalSource
        fields = ["name", "acronym", "url", "type", "description", "image", "is_active"]

    duplicate_message = _('Ya existe una fuente externa con este nombre.')
    image_help = _('Logo de la plataforma (opcional). Si se deja vacía se usa una por defecto.')
    name_esp = None                  # el modelo no lo edita aquí

    acronym = forms.CharField(
        label=_("Acrónimo"),
        help_text=_("Abreviatura de la plataforma. Se guarda en MAYÚSCULAS."),
        required=False,
        max_length=15,
        min_length=2,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("PTR"),
                "aria-label": _("Acrónimo"),
                "autocomplete": "off",
                "maxlength": 15,
                "style": "text-transform:uppercase",
                "title": _("Abreviatura de la plataforma. Se guarda en MAYÚSCULAS."),
            }
        ),
        error_messages={
            "max_length": _("Máximo 15 caracteres."),
            "min_length": _("Mínimo 2 caracteres."),
        },
    )
    url = forms.URLField(
        label=_("URL base"),
        help_text=_("Dirección de la plataforma, con https:// (opcional)."),
        required=False,
        max_length=300,
        widget=forms.URLInput(
            attrs={
                "placeholder": _("https://www.patreon.com"),
                "aria-label": _("URL base"),
                "autocomplete": "off",
                "maxlength": 300,
                "inputmode": "url",
                "title": _("Dirección de la plataforma, con https:// (opcional)."),
            }
        ),
        error_messages={
            "invalid": _("Introduce una URL válida."),
            "max_length": _("Máximo 300 caracteres."),
        },
    )
    type = forms.ChoiceField(
        label=_("Tipo"),
        help_text=_("Qué clase de plataforma es: red social, monetización, comunidad…"),
        required=True,
        choices=ExternalSourceType.choices,
        initial=ExternalSourceType.OTHER,
        widget=forms.Select(
            attrs={
                "aria-label": _("Tipo"),
                "required": "required",
                "title": _(
                    "Qué clase de plataforma es: red social, monetización, comunidad…"
                ),
            }
        ),
        error_messages={
            "required": _("Este campo es obligatorio."),
            "invalid_choice": _("Selecciona una opción válida."),
        },
    )

    def clean_acronym(self):
        return " ".join((self.cleaned_data.get("acronym") or "").split()).upper()


class FormatForm(FormBaseCategory):
    """Formato de archivo: mkv, mp4, mp3, flac, pdf, cbz… Lo usa la descarga de la colección."""

    class Meta:
        model = Format
        fields = ["name", "name_esp", "description", "image", "is_active"]

    duplicate_message = _('Ya existe un formato con este nombre.')


class LanguageForm(FormBaseCategory):
    """Idioma. `iso_639_1` es el código de 2 letras (es, en, ja)."""

    class Meta:
        model = Language
        fields = [
            "name",
            "name_esp",
            "acronym",
            "iso_639_1",
            "description",
            "image",
            "is_active",
        ]

    duplicate_message = _('Ya existe un idioma con este nombre.')
    image_help = _('Imagen del idioma (opcional). Si se deja vacía se usa una por defecto.')

    acronym = forms.CharField(
        label=_("Acrónimo"),
        help_text=_("Abreviatura del idioma. Se guarda en MAYÚSCULAS."),
        required=False,
        max_length=10,
        min_length=2,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("ESP"),
                "aria-label": _("Acrónimo"),
                "autocomplete": "off",
                "maxlength": 10,
                "style": "text-transform:uppercase",
                "title": _("Abreviatura del idioma. Se guarda en MAYÚSCULAS."),
            }
        ),
        error_messages={
            "max_length": _("Máximo 10 caracteres."),
            "min_length": _("Mínimo 2 caracteres."),
        },
    )
    iso_639_1 = forms.CharField(
        label=_("ISO 639-1"),
        help_text=_("Código de 2 letras (es, en, ja). Se guarda en MAYÚSCULAS."),
        required=False,
        max_length=10,
        min_length=2,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("ES"),
                "aria-label": _("ISO 639-1"),
                "autocomplete": "off",
                "maxlength": 10,
                "style": "text-transform:uppercase",
                "title": _("Código de 2 letras (es, en, ja). Se guarda en MAYÚSCULAS."),
            }
        ),
        error_messages={
            "max_length": _("Máximo 10 caracteres."),
            "min_length": _("Mínimo 2 caracteres."),
        },
    )

    def clean_acronym(self):
        return " ".join((self.cleaned_data.get("acronym") or "").split()).upper()

    def clean_iso_639_1(self):
        return " ".join((self.cleaned_data.get("iso_639_1") or "").split()).upper()


class QualityForm(FormBaseCategory):
    """Calidad (sobre todo de vídeo): 480p, 720p, 1080p, 4K, BluRay…"""

    class Meta:
        model = Quality
        fields = ["name", "name_esp", "description", "image", "is_active"]

    duplicate_message = _('Ya existe una calidad con este nombre.')


class RelationTypeForm(FormBaseCategory):
    """Tipo de relación entre obras (Secuela, Precuela, Spin-off, Remake…): genérico para todos los medios."""

    class Meta:
        model = RelationType
        fields = ["name", "name_esp", "description", "image", "is_active"]

    duplicate_message = _('Ya existe un tipo de relación con este nombre.')


class WebsiteForm(FormBaseCategory):
    """Sitio donde se CONSUME el contenido: Crunchyroll, animeflv, Netflix…
    Lo usa la colección del usuario (dónde ve o descargó cada cosa)."""

    class Meta:
        model = Website
        fields = ["name", "acronym", "url", "type", "description", "image", "is_active"]

    duplicate_message = _('Ya existe un sitio web con este nombre.')
    image_help = _('Logo del sitio (opcional). Si se deja vacía se usa una por defecto.')
    name_esp = None                  # el modelo no lo edita aquí

    acronym = forms.CharField(
        label=_("Acrónimo"),
        help_text=_(
            "Abreviatura del sitio (CR para Crunchyroll). Se guarda en MAYÚSCULAS."
        ),
        required=False,
        max_length=15,
        min_length=2,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("CR"),
                "aria-label": _("Acrónimo"),
                "autocomplete": "off",
                "maxlength": 15,
                "style": "text-transform:uppercase",
                "title": _(
                    "Abreviatura del sitio (CR para Crunchyroll). Se guarda en MAYÚSCULAS."
                ),
            }
        ),
        error_messages={
            "max_length": _("Máximo 15 caracteres."),
            "min_length": _("Mínimo 2 caracteres."),
        },
    )
    url = forms.URLField(
        label=_("URL base"),
        help_text=_("Dirección del sitio, con https:// (opcional)."),
        required=False,
        max_length=300,
        widget=forms.URLInput(
            attrs={
                "placeholder": _("https://www.crunchyroll.com"),
                "aria-label": _("URL base"),
                "autocomplete": "off",
                "maxlength": 300,
                "inputmode": "url",
                "title": _("Dirección del sitio, con https:// (opcional)."),
            }
        ),
        error_messages={
            "invalid": _("Introduce una URL válida."),
            "max_length": _("Máximo 300 caracteres."),
        },
    )
    type = forms.ChoiceField(
        label=_("Tipo"),
        help_text=_("Qué clase de sitio es: streaming, descarga, tienda…"),
        required=True,
        choices=WebsiteType.choices,
        initial=WebsiteType.OTHER,
        widget=forms.Select(
            attrs={
                "aria-label": _("Tipo"),
                "required": "required",
                "title": _("Qué clase de sitio es: streaming, descarga, tienda…"),
            }
        ),
        error_messages={
            "required": _("Este campo es obligatorio."),
            "invalid_choice": _("Selecciona una opción válida."),
        },
    )

    def clean_acronym(self):
        return " ".join((self.cleaned_data.get("acronym") or "").split()).upper()


class CatalogsLogForm(forms.ModelForm):
    """Log de catálogos: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = CatalogsLog
        fields = ["level", "process", "message", "is_active"]

    level = forms.ChoiceField(
        label=_("Nivel"),
        required=True,
        choices=LogLevel.choices,
        widget=forms.Select(
            attrs={"aria-label": _("Nivel"), "title": _("Nivel del registro.")}
        ),
        error_messages={"invalid_choice": _("Selecciona una opción válida.")},
    )
    process = forms.CharField(
        label=_("Proceso"),
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Proceso u origen"),
                "aria-label": _("Proceso"),
                "autocomplete": "off",
            }
        ),
    )
    message = forms.CharField(
        label=_("Mensaje"),
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": _("Qué pasó"), "aria-label": _("Mensaje")}
        ),
    )
    is_active = forms.BooleanField(
        label=_("Activo"),
        help_text=_(
            "Si está activo, se muestra en el listado. Desmárcalo para archivarlo."
        ),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"aria-label": _("Activo")}),
    )
