"""Formularios del panel para `serie` — UNO POR MODELO, AUTÓNOMOS.

Regla del proyecto: cada modelo tiene su formulario propio y completo. Heredan de
`forms.ModelForm` de Django y punto. ÚNICA excepción: las categorías (`ModelBaseCategory`)
heredan `core.shared.forms.base.FormBaseCategory` (nombre, nombre ES, descripción, imagen, activo).
Todo lo que hace el formulario está escrito AQUÍ, a la vista:

  * cada campo con su label, help_text, límites, widget, attrs y mensajes de error,
  * cada `clean_<campo>` con su normalización y sus reglas,
  * la comprobación de duplicados contra el `slug` único (o el `unique_together`)
    del modelo, para dar un mensaje claro en el campo en vez de un IntegrityError,
  * la validación de la imagen (extensión + peso),
  * las FK/M2M con su widget AJAX y el endpoint al que buscan, escrito a la vista.

Sí, hay repetición entre formularios parecidos, y con los de `movie` (son gemelos).
Es a propósito: se lee y se cambia uno sin tocar los demás.

`SerieLog` no tiene formulario a propósito: es un REGISTRO, no se escribe a mano.
"""
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import Language, RelationType
from apps.companies.models import Company
from apps.people.models import Person
from apps.series.models import Genre, GenreAlias, Rating, Role, Serie, SerieCast, SerieImage, SerieLog, SerieRelation, SerieStaff, SerieTitle, Type
from core.shared.forms.base import FormBaseCategory
from core.shared.views.imports import DescargarImagenesForm, ReintentarMuertasForm
from core.shared.forms.widgets import AjaxSelect, AjaxSelectMultiple
from core.shared.models.choices import LogLevel
from core.utils.constants import IMAGE_ACCEPT, IMAGE_EXTENSIONS, IMAGE_FORMATS, IMAGE_HINT, IMAGE_MAX_MB, MB


class GenreAliasForm(forms.ModelForm):
    """alias de género: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = GenreAlias
        fields = ['name', 'name_esp', 'is_active', 'genre']


class GenreForm(FormBaseCategory):
    """Género de serie. `explicit` marca los géneros +18 (filtran el catálogo público)."""

    class Meta:
        model = Genre
        fields = ['name', 'name_esp', 'description', 'explicit', 'image', 'is_active']

    duplicate_message = _('Ya existe un género de serie con este nombre.')

    explicit = forms.BooleanField(
        label=_('Explícito (+18)'),
        help_text=_('Marca los géneros para adultos. Filtra el catálogo público.'),
        required=False, initial=False,         # el modelo trae default=False
        widget=forms.CheckboxInput(attrs={'aria-label': _('Explícito (+18)')}),
    )


class RatingForm(FormBaseCategory):
    """Clasificación por edad de una serie, con su acrónimo (TV-MA, PG…)."""

    class Meta:
        model = Rating
        fields = ['name', 'name_esp', 'description', 'acronym', 'image', 'is_active']

    duplicate_message = _('Ya existe una clasificación con este nombre.')

    acronym = forms.CharField(
        label=_('Acrónimo'),
        help_text=_('Sigla de la clasificación (TV-MA, PG…). Se guarda en MAYÚSCULAS.'),
        required=False, max_length=15, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('TV-MA'), 'aria-label': _('Acrónimo'), 'autocomplete': 'off',
            'maxlength': 15, 'style': 'text-transform:uppercase',
            'title': _('Sigla de la clasificación (TV-MA, PG…). Se guarda en MAYÚSCULAS.'),
        }),
        error_messages={'max_length': _('Máximo 15 caracteres.')},
    )

    def clean_acronym(self):
        return ' '.join((self.cleaned_data.get('acronym') or '').split()).upper()


class RoleForm(forms.ModelForm):
    """Rol en una serie (Protagonista, Director, Guionista…), agrupado por tipo de rol."""

    class Meta:
        model = Role
        fields = ['name', 'name_esp', 'type', 'description', 'image', 'is_active']

    name = forms.CharField(
        label=_('Nombre'),
        help_text=_('Nombre principal. Debe ser único (no puede repetirse).'),
        required=True, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 100, 'required': 'required',
            'title': _('Nombre principal. Debe ser único (no puede repetirse).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 100 caracteres.')},
    )
    name_esp = forms.CharField(
        label=_('Nombre (ES)'),
        help_text=_('Traducción o nombre en español (opcional).'),
        required=False, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre (ES)'), 'aria-label': _('Nombre (ES)'), 'autocomplete': 'off',
            'maxlength': 100, 'title': _('Traducción o nombre en español (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 100 caracteres.')},
    )
    type = forms.ChoiceField(
        label=_('Tipo de rol'), required=False, choices=[('', '—')] + list(Role._meta.get_field('type').choices),   # solo las familias de esta app
        widget=forms.Select(attrs={'aria-label': _('Tipo de rol'), 'title': _('Familia del rol: personal, elenco, producción, música, personaje, manga.')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    description = forms.CharField(
        label=_('Descripción'),
        help_text=_('Descripción o notas (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Descripción'), 'aria-label': _('Descripción'), 'autocomplete': 'off',
            'rows': 4, 'title': _('Descripción o notas (opcional).'),
        }),
    )
    image = forms.ImageField(
        label=_('Imagen'),
        help_text=_('Imagen de la categoría (opcional). Si se deja vacía se usa una por defecto.'),
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'aria-label': _('Imagen'), 'accept': IMAGE_ACCEPT,
            'title': IMAGE_HINT,
        }),
        error_messages={'invalid_image': _('Envía una imagen válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_name(self):
        name = ' '.join((self.cleaned_data.get('name') or '').split())
        slug = slugify(name)[:120]
        if slug:
            duplicados = Role.objects.filter(slug=slug)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                raise forms.ValidationError('Ya existe un rol de serie con este nombre.')
        return name

    def clean_name_esp(self):
        return ' '.join((self.cleaned_data.get('name_esp') or '').split())

    def clean_description(self):
        return (self.cleaned_data.get('description') or '').strip()

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


class SerieCastForm(forms.ModelForm):
    """Reparto: una persona interpreta un personaje en una serie. El modelo exige que
    (serie, persona, rol, personaje) sea único: se comprueba en `clean()`."""

    class Meta:
        model = SerieCast
        fields = ['serie', 'person', 'role', 'character_name', 'is_active']

    serie = forms.ModelChoiceField(
        label=_('Serie'),
        help_text=_('Serie a la que pertenece este reparto. Escribe para buscar.'),
        required=True, queryset=Serie.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie_select', attrs={
            'aria-label': _('Serie'), 'required': 'required',
            'title': _('Serie a la que pertenece este reparto. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('Quién interpreta. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('Quién interpreta. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.ModelChoiceField(
        label=_('Rol'),
        help_text=_('Protagonista, secundario… (opcional).'),
        required=False, queryset=Role.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie-role_select', attrs={
            'aria-label': _('Rol'), 'title': _('Protagonista, secundario… (opcional).'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    character_name = forms.CharField(
        label=_('Personaje'),
        help_text=_('Nombre del personaje que interpreta (opcional).'),
        required=False, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Personaje'), 'aria-label': _('Personaje'), 'autocomplete': 'off',
            'maxlength': 150, 'title': _('Nombre del personaje que interpreta (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 150 caracteres.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_character_name(self):
        return ' '.join((self.cleaned_data.get('character_name') or '').split())

    def clean(self):
        """`unique_together = (serie, person, role, character_name)` en el modelo."""
        cleaned = super().clean()
        serie = cleaned.get('serie')
        person = cleaned.get('person')
        if serie and person:
            duplicados = SerieCast.objects.filter(
                serie=serie, person=person, role=cleaned.get('role'),
                character_name=cleaned.get('character_name') or '',
            )
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, 'Ya existe esta misma línea de reparto para la serie.')
        return cleaned


class SerieForm(forms.ModelForm):
    """La serie en sí. Los desplegables NO vuelcan sus tablas: buscan en el servidor
    por AJAX contra `<entidad>/select/` (ver `core/shared/forms/widgets.py` y `BaseSelectView`)."""

    class Meta:
        model = Serie
        fields = ['title', 'title_secundary', 'release_year', 'duration_minutes',
                  'synopsis', 'serie_type', 'serie_rating', 'genres', 'producers',
                  'distributors', 'is_active']

    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título principal. Debe ser único.'),
        required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 255, 'required': 'required',
            'title': _('Título principal. Debe ser único.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 255 caracteres.')},
    )
    title_secundary = forms.CharField(
        label=_('Título secundario'),
        help_text=_('Título alternativo/original (opcional).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título secundario'), 'aria-label': _('Título secundario'),
            'autocomplete': 'off', 'maxlength': 255,
            'title': _('Título alternativo/original (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    release_year = forms.IntegerField(
        label=_('Año'),
        help_text=_('Año de estreno (1888–2100).'),
        required=False, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('2015'), 'aria-label': _('Año'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'title': _('Año de estreno (1888–2100).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    duration_minutes = forms.IntegerField(
        label=_('Duración (min)'),
        help_text=_('Duración de un episodio, en minutos (opcional).'),
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': _('45'), 'aria-label': _('Duración (min)'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 0,
            'title': _('Duración de un episodio, en minutos (opcional).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El valor mínimo es 0.')},
    )
    synopsis = forms.CharField(
        label=_('Sinopsis'),
        help_text=_('Resumen de la trama (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Sinopsis'), 'aria-label': _('Sinopsis'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Resumen de la trama (opcional).'),
        }),
    )
    serie_type = forms.ModelChoiceField(
        label=_('Tipo'),
        help_text=_('Serie, miniserie, documental… Escribe para buscar.'),
        required=False, queryset=Type.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie-type_select', attrs={
            'aria-label': _('Tipo'), 'title': _('Serie, miniserie, documental… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    serie_rating = forms.ModelChoiceField(
        label=_('Clasificación'),
        help_text=_('Clasificación por edad (TV-MA, PG…). Escribe para buscar.'),
        required=False, queryset=Rating.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie-rating_select', attrs={
            'aria-label': _('Clasificación'),
            'title': _('Clasificación por edad (TV-MA, PG…). Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    genres = forms.ModelMultipleChoiceField(
        label=_('Géneros'),
        help_text=_('Puedes elegir varios. Escribe para buscar.'),
        required=False, queryset=Genre.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:serie-genre_select', attrs={
            'aria-label': _('Géneros'), 'title': _('Puedes elegir varios. Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    producers = forms.ModelMultipleChoiceField(
        label=_('Productoras'),
        help_text=_('Compañías que la produjeron. Puedes elegir varias.'),
        required=False, queryset=Company.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:company_select', attrs={
            'aria-label': _('Productoras'),
            'title': _('Compañías que la produjeron. Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    distributors = forms.ModelMultipleChoiceField(
        label=_('Distribuidoras'),
        help_text=_('Compañías que la distribuyeron. Puedes elegir varias.'),
        required=False, queryset=Company.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:company_select', attrs={
            'aria-label': _('Distribuidoras'),
            'title': _('Compañías que la distribuyeron. Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,          # el modelo trae default=True
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        return ' '.join((self.cleaned_data.get('title') or '').split())

    def clean(self):
        """Duplicados por TÍTULO + AÑO (el slug único lleva el año): dos series
        homónimas de años distintos CONVIVEN; choca solo mismo título y mismo año.
        Se compara también el slug viejo SIN año (registros previos al cambio)."""
        data = super().clean()
        title = data.get('title') or ''
        year = data.get('release_year')
        candidatos = {slugify(f"{title} {year}")[:275] if year else '', slugify(title)[:275]}
        candidatos.discard('')
        if candidatos:
            duplicadas = Serie.objects.filter(slug__in=candidatos)
            if self.instance.pk:
                duplicadas = duplicadas.exclude(pk=self.instance.pk)
            if duplicadas.exists():
                raise forms.ValidationError('Ya existe una serie con este título y ese año.')
        return data

    def clean_title_secundary(self):
        return ' '.join((self.cleaned_data.get('title_secundary') or '').split())

    def clean_synopsis(self):
        return (self.cleaned_data.get('synopsis') or '').strip()


class SerieImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = SerieImage
        fields = ['serie', 'order', 'image', 'image_url', 'is_active']

    serie = forms.ModelChoiceField(
        label=_('Serie'),
        help_text=_('Serie a la que pertenece la imagen. Escribe para buscar.'),
        required=True, queryset=Serie.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie_select', attrs={
            'aria-label': _('Serie'), 'required': 'required',
            'title': _('Serie a la que pertenece la imagen. Escribe para buscar.'),
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


class SerieRelationForm(forms.ModelForm):
    """Relación entre dos series (secuela, precuela, spin-off…), en un sentido."""

    class Meta:
        model = SerieRelation
        fields = ['serie', 'related', 'relation_type', 'is_active']

    serie = forms.ModelChoiceField(
        label=_('Serie'), help_text=_('La serie de la que sale la relación. Escribe para buscar.'),
        required=True, queryset=Serie.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie_select', attrs={'aria-label': _('Serie'), 'required': 'required'}),
        error_messages={'required': _('Este campo es obligatorio.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )
    related = forms.ModelChoiceField(
        label=_('Relacionada'), help_text=_('La otra serie. Escribe para buscar.'),
        required=True, queryset=Serie.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie_select', attrs={'aria-label': _('Relacionada'), 'required': 'required'}),
        error_messages={'required': _('Este campo es obligatorio.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )
    relation_type = forms.ModelChoiceField(
        label=_('Tipo de relación'), help_text=_('Secuela, precuela, spin-off, remake…'),
        required=False, queryset=RelationType.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:relation-type_select', attrs={'aria-label': _('Tipo de relación')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )

    def clean(self):
        cleaned = super().clean()
        serie, related = cleaned.get('serie'), cleaned.get('related')
        if serie and related and serie == related:
            self.add_error('related', _('Una serie no puede relacionarse consigo misma.'))
        if serie and related:
            duplicados = SerieRelation.objects.filter(serie=serie, related=related, relation_type=cleaned.get('relation_type'))
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, _('Ya existe esta relación entre las dos series.'))
        return cleaned


class SerieStaffForm(forms.ModelForm):
    """Equipo técnico: una persona con un rol de producción en una serie. El modelo
    exige que (serie, persona, rol) sea único: se comprueba en `clean()`."""

    class Meta:
        model = SerieStaff
        fields = ['serie', 'person', 'role', 'is_active']

    serie = forms.ModelChoiceField(
        label=_('Serie'),
        help_text=_('Serie en la que trabajó. Escribe para buscar.'),
        required=True, queryset=Serie.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie_select', attrs={
            'aria-label': _('Serie'), 'required': 'required',
            'title': _('Serie en la que trabajó. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('Quién trabajó en ella. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('Quién trabajó en ella. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.ModelChoiceField(
        label=_('Rol'),
        help_text=_('Dirección, guion, fotografía… (opcional).'),
        required=False, queryset=Role.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie-role_select', attrs={
            'aria-label': _('Rol'), 'title': _('Dirección, guion, fotografía… (opcional).'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean(self):
        """`unique_together = (serie, person, role)` en el modelo."""
        cleaned = super().clean()
        serie = cleaned.get('serie')
        person = cleaned.get('person')
        if serie and person:
            duplicados = SerieStaff.objects.filter(
                serie=serie, person=person, role=cleaned.get('role'))
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, 'Esta persona ya está registrada con ese rol en la serie.')
        return cleaned


class SerieTitleForm(forms.ModelForm):
    """Título alternativo de una serie, por idioma. El modelo exige que
    (serie, idioma, título) sea único: se comprueba en `clean()`."""

    class Meta:
        model = SerieTitle
        fields = ['serie', 'title_lang', 'title', 'is_active']

    serie = forms.ModelChoiceField(
        label=_('Serie'),
        help_text=_('Serie a la que pertenece el título. Escribe para buscar.'),
        required=True, queryset=Serie.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:serie_select', attrs={
            'aria-label': _('Serie'), 'required': 'required',
            'title': _('Serie a la que pertenece el título. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    title_lang = forms.ModelChoiceField(
        label=_('Idioma'),
        help_text=_('Idioma de este título. Escribe para buscar.'),
        required=True, queryset=Language.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:language_select', attrs={
            'aria-label': _('Idioma'), 'required': 'required',
            'title': _('Idioma de este título. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    title = forms.CharField(
        label=_('Título'),
        help_text=_('El título tal como se usa en ese idioma.'),
        required=True, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 500, 'required': 'required',
            'title': _('El título tal como se usa en ese idioma.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 500 caracteres.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        return ' '.join((self.cleaned_data.get('title') or '').split())

    def clean(self):
        """`unique_together = (serie, title_lang, title)` en el modelo."""
        cleaned = super().clean()
        serie = cleaned.get('serie')
        title_lang = cleaned.get('title_lang')
        title = cleaned.get('title')
        if serie and title_lang and title:
            duplicados = SerieTitle.objects.filter(serie=serie, title_lang=title_lang, title=title)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('title', 'Esta serie ya tiene ese título en ese idioma.')
        return cleaned


class TypeForm(FormBaseCategory):
    """Tipo de serie: Serie, Miniserie, Documental…"""

    class Meta:
        model = Type
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un tipo de serie con este nombre.')


class SerieLogForm(forms.ModelForm):
    """Log de series: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = SerieLog
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


class SerieImageDownloadForm(DescargarImagenesForm):
    TIPO = 'series.SerieImage'
    success_url = 'panel:serie-image_list'


class SerieImageRetryForm(ReintentarMuertasForm):
    TIPO = 'series.SerieImage'
    success_url = 'panel:serie-image_download'

