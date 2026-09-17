"""Formularios del panel para `people` (personas) — UNO POR MODELO, AUTÓNOMOS.

Regla del proyecto: cada modelo tiene su formulario propio y completo. Heredan de
`forms.ModelForm` de Django y punto. ÚNICA excepción: las categorías (`ModelBaseCategory`)
heredan `core.shared.forms.base.FormBaseCategory` (nombre, nombre ES, descripción, imagen, activo).
Todo lo que hace el formulario está escrito AQUÍ, a la vista:

  * cada campo con su label, help_text, límites, widget, attrs y mensajes de error,
  * cada `clean_<campo>` con su normalización y sus reglas,
  * la comprobación de duplicados contra el `slug` único del modelo,
  * la validación de la imagen (extensión + peso),
  * las FK con su widget AJAX y el endpoint al que buscan, escrito a la vista.

Sí, hay repetición entre formularios parecidos. Es a propósito: se lee y se cambia
uno sin tocar los demás.
"""
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import Country, ExternalSource
from apps.people.models import PeopleLog, Person, PersonImage, PersonLink, PersonNickname
from core.shared.forms.widgets import AjaxSelect
from core.shared.views.imports import DescargarImagenesForm, ReintentarMuertasForm
from core.shared.models.choices import LogLevel
from core.utils.constants import IMAGE_ACCEPT, IMAGE_EXTENSIONS, IMAGE_FORMATS, IMAGE_HINT, IMAGE_MAX_MB, MB


class PersonForm(forms.ModelForm):
    """Persona real: actores, autores, staff, artistas, creadores.

    El desplegable de País NO vuelca la tabla: busca en el servidor por AJAX contra
    `panel:country_select` (ver `core/shared/forms/widgets.py` y `BaseSelectView`)."""

    class Meta:
        model = Person
        fields = ['full_name', 'biography', 'birth_date', 'country', 'is_active']

    full_name = forms.CharField(
        label=_('Nombre completo'),
        help_text=_('Nombre y apellidos tal como se acreditan.'),
        required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre completo'), 'aria-label': _('Nombre completo'),
            'autocomplete': 'off', 'maxlength': 255, 'required': 'required',
            'title': _('Nombre y apellidos tal como se acreditan.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 255 caracteres.')},
    )
    biography = forms.CharField(
        label=_('Biografía'),
        help_text=_('Reseña de la persona (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Biografía'), 'aria-label': _('Biografía'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Reseña de la persona (opcional).'),
        }),
    )
    birth_date = forms.DateField(
        label=_('Fecha de nacimiento'),
        help_text=_('Formato dd-mm-aaaa. Se elige en el calendario.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Fecha de nacimiento'),
            'class': 'js-date', 'autocomplete': 'off',
            'title': _('Formato dd-mm-aaaa. Se elige en el calendario.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    country = forms.ModelChoiceField(
        label=_('País'),
        help_text=_('País de origen (opcional). Escribe para buscar.'),
        required=False, queryset=Country.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:country_select', attrs={
            'aria-label': _('País'), 'title': _('País de origen (opcional). Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_full_name(self):
        """El `slug` de Person NO es único (puede haber homónimos reales), así que
        aquí solo normalizamos: no bloqueamos nombres repetidos."""
        return ' '.join((self.cleaned_data.get('full_name') or '').split())

    def clean_biography(self):
        return (self.cleaned_data.get('biography') or '').strip()

    def clean_birth_date(self):
        """Una fecha de nacimiento en el futuro es siempre un error de tecleo."""
        from django.utils import timezone
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        return birth_date


class PersonImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = PersonImage
        fields = ['person', 'order', 'image', 'image_url', 'is_active']

    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('De quién es la imagen. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('De quién es la imagen. Escribe para buscar.'),
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
        help_text=_('Archivo de la imagen (o deja solo la URL y se descarga después).'),
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'aria-label': _('Imagen'), 'accept': IMAGE_ACCEPT,
            'title': IMAGE_HINT,
        }),
        error_messages={'invalid_image': _('Envía una imagen válida.')},
    )
    image_url = forms.CharField(
        label=_('URL de la imagen'),
        help_text=_('De dónde se descargó, si vino de una fuente externa (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('https://…'), 'aria-label': _('URL de la imagen'),
            'autocomplete': 'off', 'rows': 3,
            'title': _('De dónde se descargó, si vino de una fuente externa (opcional).'),
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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not isinstance(image, UploadedFile):
            return image
        nombre = image.name or ''
        ext = ('.' + nombre.rsplit('.', 1)[-1].lower()) if '.' in nombre else ''
        if ext not in IMAGE_EXTENSIONS:
            raise forms.ValidationError(
                'Formato no permitido (%s). Usa %s.'
                % (ext or 'sin extensión', IMAGE_FORMATS))
        if image.size > IMAGE_MAX_MB * MB:
            raise forms.ValidationError(
                'La imagen pesa %s MB; el máximo son %s MB.' % (round(image.size / MB, 1), IMAGE_MAX_MB))
        return image


class PersonLinkForm(forms.ModelForm):
    """Enlace externo de una persona: sitio oficial, X/Twitter, Instagram, Wikipedia…
    El modelo exige que (persona, fuente, id externo) sea único: se comprueba en `clean()`."""

    class Meta:
        model = PersonLink
        fields = ['person', 'source', 'external_id', 'url', 'is_active']

    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('De quién es el enlace. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('De quién es el enlace. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    source = forms.ModelChoiceField(
        label=_('Fuente'),
        help_text=_('Plataforma del enlace (sitio oficial, X, Instagram…). Escribe para buscar.'),
        required=True, queryset=ExternalSource.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:external-source_select', attrs={
            'aria-label': _('Fuente'), 'required': 'required',
            'title': _('Plataforma del enlace (sitio oficial, X, Instagram…). Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    external_id = forms.CharField(
        label=_('Id externo'),
        help_text=_('Identificador o nombre de usuario en esa plataforma (opcional).'),
        required=False, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('usuario123'), 'aria-label': _('Id externo'), 'autocomplete': 'off',
            'maxlength': 500,
            'title': _('Identificador o nombre de usuario en esa plataforma (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 500 caracteres.')},
    )
    url = forms.CharField(
        label=_('URL'),
        help_text=_('Dirección completa del enlace, con https:// (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('https://www.instagram.com/usuario123'), 'aria-label': _('URL'),
            'autocomplete': 'off', 'rows': 3,
            'title': _('Dirección completa del enlace, con https:// (opcional).'),
        }),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_external_id(self):
        return ' '.join((self.cleaned_data.get('external_id') or '').split())

    def clean_url(self):
        return (self.cleaned_data.get('url') or '').strip()

    def clean(self):
        """`unique_together = (person, source, external_id)` en el modelo."""
        cleaned = super().clean()
        person = cleaned.get('person')
        source = cleaned.get('source')
        if person and source:
            duplicados = PersonLink.objects.filter(
                person=person, source=source, external_id=cleaned.get('external_id') or '')
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('external_id', 'Esta persona ya tiene ese enlace en esa plataforma.')
        return cleaned


class PersonNicknameForm(forms.ModelForm):
    """Apodo/alias de una persona. El modelo exige que el par (persona, apodo) sea
    único: lo comprobamos aquí para dar un mensaje claro en vez de un IntegrityError."""

    class Meta:
        model = PersonNickname
        fields = ['person', 'nickname', 'is_active']

    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('A quién pertenece el apodo. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('A quién pertenece el apodo. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    nickname = forms.CharField(
        label=_('Apodo'),
        help_text=_('Alias por el que también se le conoce.'),
        required=True, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Apodo'), 'aria-label': _('Apodo'), 'autocomplete': 'off',
            'maxlength': 100, 'required': 'required',
            'title': _('Alias por el que también se le conoce.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 100 caracteres.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_nickname(self):
        return ' '.join((self.cleaned_data.get('nickname') or '').split())

    def clean(self):
        """`unique_together = (person, nickname)` en el modelo: avisamos aquí, en el
        campo del apodo, antes de que reviente el UNIQUE de la base."""
        cleaned = super().clean()
        person = cleaned.get('person')
        nickname = cleaned.get('nickname')
        if person and nickname:
            duplicados = PersonNickname.objects.filter(person=person, nickname=nickname)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('nickname', 'Esta persona ya tiene registrado ese apodo.')
        return cleaned


class PeopleLogForm(forms.ModelForm):
    """Log de personas: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = PeopleLog
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


class PersonImageDownloadForm(DescargarImagenesForm):
    TIPO = 'people.PersonImage'
    success_url = 'panel:person-image_list'


class PersonImageRetryForm(ReintentarMuertasForm):
    TIPO = 'people.PersonImage'
    success_url = 'panel:person-image_download'
