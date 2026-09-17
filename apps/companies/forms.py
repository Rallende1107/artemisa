"""Formularios de COMPAÑÍAS: uno por modelo (R0 · 1 : 1 : N)."""
from django import forms
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import Country
from apps.companies.models import Company, CompanyImage, CompanyLog
from core.shared.forms.widgets import AjaxSelect
from core.shared.views.imports import DescargarImagenesForm, ReintentarMuertasForm
from core.shared.models.choices import LogLevel
from core.utils.constants import IMAGE_ACCEPT, IMAGE_HINT


class CompanyForm(forms.ModelForm):
    """Compañía (global y neutra). El papel —estudio, productora, distribuidora…— no se elige aquí: lo pone
    cada obra desde su medio. El año de disolución no puede ser anterior al de fundación."""

    class Meta:
        model = Company
        fields = ['name', 'founded_year', 'disolved_year', 'biography', 'country', 'is_active']

    name = forms.CharField(
        label=_('Nombre'),
        help_text=_('Nombre de la empresa. Debe ser único.'),
        required=True, max_length=250, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 250, 'required': 'required',
            'title': _('Nombre de la empresa. Debe ser único.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 250 caracteres.')},
    )
    founded_year = forms.IntegerField(
        label=_('Año de fundación'),
        help_text=_('Año en que se fundó (opcional).'),
        required=False, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('1923'), 'aria-label': _('Año de fundación'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'title': _('Año en que se fundó (opcional).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    disolved_year = forms.IntegerField(
        label=_('Año de disolución'),
        help_text=_('Año en que se disolvió, si aplica (opcional).'),
        required=False, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('2005'), 'aria-label': _('Año de disolución'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'title': _('Año en que se disolvió, si aplica (opcional).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    biography = forms.CharField(
        label=_('Biografía'),
        help_text=_('Reseña o historia de la empresa (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Biografía'), 'aria-label': _('Biografía'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Reseña o historia de la empresa (opcional).'),
        }),
    )
    country = forms.ModelChoiceField(
        label=_('País'),
        help_text=_('País de la empresa (opcional). Escribe para buscar.'),
        required=False, queryset=Country.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:country_select', attrs={
            'aria-label': _('País'), 'title': _('País de la empresa (opcional). Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_name(self):
        name = ' '.join((self.cleaned_data.get('name') or '').split())
        slug = slugify(name)[:270]
        if slug:
            duplicadas = Company.objects.filter(slug=slug)
            if self.instance.pk:
                duplicadas = duplicadas.exclude(pk=self.instance.pk)
            if duplicadas.exists():
                raise forms.ValidationError('Ya existe una compañía con este nombre.')
        return name

    def clean_biography(self):
        return (self.cleaned_data.get('biography') or '').strip()

    def clean(self):
        """Cruce de dos campos: una empresa no puede disolverse antes de fundarse."""
        cleaned = super().clean()
        fundacion = cleaned.get('founded_year')
        disolucion = cleaned.get('disolved_year')
        if fundacion and disolucion and disolucion < fundacion:
            self.add_error('disolved_year',
                           'El año de disolución no puede ser anterior al de fundación.')
        return cleaned


class CompanyImageForm(forms.ModelForm):
    """Logo o imagen de la compañía. La de `orden` más bajo es su portada."""

    class Meta:
        model = CompanyImage
        fields = ['company', 'order', 'image', 'image_url', 'is_active']

    company = forms.ModelChoiceField(
        label=_('Compañía'),
        help_text=_('De qué compañía es la imagen. Escribe para buscar.'),
        required=True, queryset=Company.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:company_select', attrs={
            'aria-label': _('Compañía'), 'required': 'required',
            'title': _('De qué compañía es la imagen. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    order = forms.IntegerField(
        label=_('Orden'),
        help_text=_('La de número más bajo es la portada. Vacío: va al final.'),
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Orden'), 'min': 0,
            'title': _('La de número más bajo es la portada. Vacío: va al final.'),
        }),
        error_messages={'invalid': _('Escribe un número entero.')},
    )
    image = forms.ImageField(
        label=_('Imagen'),
        help_text=_('Archivo del logo (o deja solo la URL y se descarga después).'),
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'aria-label': _('Imagen'), 'accept': IMAGE_ACCEPT,
            'title': IMAGE_HINT,
        }),
        error_messages={'invalid_image': _('Envía una imagen válida.')},
    )
    image_url = forms.CharField(
        label=_('URL de la imagen'),
        help_text=_('De dónde se descarga, si viene de una fuente externa (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('https://…'), 'aria-label': _('URL de la imagen'),
            'autocomplete': 'off', 'rows': 3,
            'title': _('De dónde se descarga, si viene de una fuente externa (opcional).'),
        }),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('image') and not cleaned.get('image_url'):
            self.add_error('image', _('Sube un archivo o escribe su URL.'))
        return cleaned

    def clean_image_url(self):
        return (self.cleaned_data.get('image_url') or '').strip()


class CompanyLogForm(forms.ModelForm):
    """Log de compañías: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = CompanyLog
        fields = ['level', 'process', 'message', 'is_active']

    level = forms.ChoiceField(
        label=_('Nivel'), required=True, choices=LogLevel.choices,
        widget=forms.Select(attrs={'aria-label': _('Nivel'), 'title': _('Nivel del registro.')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    process = forms.CharField(
        label=_('Proceso'), required=False, max_length=255,
        widget=forms.TextInput(attrs={'placeholder': _('Proceso u origen'), 'aria-label': _('Proceso'), 'autocomplete': 'off'}),
    )
    message = forms.CharField(
        label=_('Mensaje'), required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': _('Qué pasó'), 'aria-label': _('Mensaje')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el listado. Desmárcalo para archivarlo.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class CompanyImageDownloadForm(DescargarImagenesForm):
    TIPO = 'companies.CompanyImage'
    success_url = 'panel:company-image_list'


class CompanyImageRetryForm(ReintentarMuertasForm):
    TIPO = 'companies.CompanyImage'
    success_url = 'panel:company-image_download'
