"""Formularios del panel para las páginas informativas — UNO POR MODELO, AUTÓNOMOS."""
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.pages.models import AboutSection, PagesLog, PrivacySection, TermsSection
from core.shared.models.choices import LogLevel


class AboutSectionForm(forms.ModelForm):
    """Sección de la página NOSOTROS: el contenido del sitio se edita aquí,
    no en el HTML."""

    class Meta:
        model = AboutSection
        fields = ['order', 'title', 'body', 'is_active']

    order = forms.IntegerField(
        label=_('Orden'),
        help_text=_('Posición dentro de la página (menor = primero).'),
        required=True, min_value=0, initial=0,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Orden'), 'min': 0,
            'title': _('Posición dentro de la página (menor = primero).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título de la sección (aparece en el índice de contenido).'),
        required=True, max_length=120, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 120, 'required': 'required',
            'title': _('Título de la sección (aparece en el índice de contenido).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 120 caracteres.')},
    )
    body = forms.CharField(
        label=_('Contenido'),
        help_text=_('Párrafos separados por una línea en blanco; las líneas que '
                  'comienzan con «- » se muestran como lista.'),
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': _('Contenido'), 'aria-label': _('Contenido'), 'rows': 12,
            'title': _('Párrafos separados por una línea en blanco; «- » crea lista.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        return ' '.join((self.cleaned_data.get('title') or '').split())


class PrivacySectionForm(forms.ModelForm):
    """Sección de la página PRIVACIDAD: el contenido del sitio se edita aquí,
    no en el HTML."""

    class Meta:
        model = PrivacySection
        fields = ['order', 'title', 'body', 'is_active']

    order = forms.IntegerField(
        label=_('Orden'),
        help_text=_('Posición dentro de la página (menor = primero).'),
        required=True, min_value=0, initial=0,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Orden'), 'min': 0,
            'title': _('Posición dentro de la página (menor = primero).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título de la sección (aparece en el índice de contenido).'),
        required=True, max_length=120, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 120, 'required': 'required',
            'title': _('Título de la sección (aparece en el índice de contenido).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 120 caracteres.')},
    )
    body = forms.CharField(
        label=_('Contenido'),
        help_text=_('Párrafos separados por una línea en blanco; las líneas que '
                  'comienzan con «- » se muestran como lista.'),
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': _('Contenido'), 'aria-label': _('Contenido'), 'rows': 12,
            'title': _('Párrafos separados por una línea en blanco; «- » crea lista.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        return ' '.join((self.cleaned_data.get('title') or '').split())


class TermsSectionForm(forms.ModelForm):
    """Sección de la página TÉRMINOS DE USO: el contenido del sitio se edita aquí,
    no en el HTML."""

    class Meta:
        model = TermsSection
        fields = ['order', 'title', 'body', 'is_active']

    order = forms.IntegerField(
        label=_('Orden'),
        help_text=_('Posición dentro de la página (menor = primero).'),
        required=True, min_value=0, initial=0,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Orden'), 'min': 0,
            'title': _('Posición dentro de la página (menor = primero).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título de la sección (aparece en el índice de contenido).'),
        required=True, max_length=120, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 120, 'required': 'required',
            'title': _('Título de la sección (aparece en el índice de contenido).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 120 caracteres.')},
    )
    body = forms.CharField(
        label=_('Contenido'),
        help_text=_('Párrafos separados por una línea en blanco; las líneas que '
                  'comienzan con «- » se muestran como lista.'),
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': _('Contenido'), 'aria-label': _('Contenido'), 'rows': 12,
            'title': _('Párrafos separados por una línea en blanco; «- » crea lista.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        return ' '.join((self.cleaned_data.get('title') or '').split())


class PagesLogForm(forms.ModelForm):
    """Log de páginas: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = PagesLog
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
