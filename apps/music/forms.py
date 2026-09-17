"""Formularios del panel para `music` — UNO POR MODELO, AUTÓNOMOS.

Regla del proyecto: cada modelo tiene su formulario propio y completo. Heredan de
`forms.ModelForm` de Django y punto. ÚNICA excepción: las categorías (`ModelBaseCategory`)
heredan `core.shared.forms.base.FormBaseCategory` (nombre, nombre ES, descripción, imagen, activo).
Todo lo que hace el formulario está escrito AQUÍ, a la vista:

  * cada campo con su label, help_text, límites, widget, attrs y mensajes de error,
  * cada `clean_<campo>` con su normalización y sus reglas,
  * la comprobación de duplicados contra el `unique_together` del modelo, para dar
    un mensaje claro en el campo en vez de un IntegrityError,
  * la validación de la imagen y del audio (extensión + peso),
  * las FK/M2M con su widget AJAX y el endpoint al que buscan, escrito a la vista.

Sí, hay repetición entre formularios parecidos. Es a propósito: se lee y se cambia
uno sin tocar los demás.

`MusicLog` y las tablas `Data*Deezer` no tienen formulario a propósito: son
registro y staging del importador, no se escriben a mano.
"""
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.music.models import Album, AlbumImage, AlbumType, Artist, ArtistImage, ArtistMember, ArtistType, DataDeezerAlbum, DataDeezerArtist, DataDeezerGenre, DataDeezerTrack, Genre, GenreAlias, MusicLog, Role, Song, SongComposer, SongTranslation
from apps.people.models import Person
from core.shared.forms.base import FormBaseCategory
from core.shared.forms.widgets import AjaxSelect, AjaxSelectMultiple
from core.shared.models.choices import LogLevel
from core.shared.views.imports import DescargarImagenesForm, ReintentarMuertasForm, LanzaTareaMixin, MAX_IDS_POR_LOTE
from core.utils.constants import AUDIO_ACCEPT, AUDIO_EXTENSIONS, AUDIO_FORMATS, AUDIO_HINT, AUDIO_MAX_MB, IMAGE_ACCEPT, IMAGE_EXTENSIONS, IMAGE_FORMATS, IMAGE_HINT, IMAGE_MAX_MB, MB


class AlbumForm(forms.ModelForm):
    """Álbum de un artista."""

    class Meta:
        model = Album
        fields = ['title', 'artist', 'album_type', 'release_date', 'description',
                  'genres', 'is_active']

    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título del álbum.'),
        required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 255, 'required': 'required', 'title': _('Título del álbum.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 255 caracteres.')},
    )
    artist = forms.ModelChoiceField(
        label=_('Artista'),
        help_text=_('De quién es el álbum. Escribe para buscar.'),
        required=True, queryset=Artist.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:artist_select', attrs={
            'aria-label': _('Artista'), 'required': 'required',
            'title': _('De quién es el álbum. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    album_type = forms.ModelChoiceField(
        label=_('Tipo de álbum'),
        help_text=_('LP, EP, single, recopilatorio… Escribe para buscar.'),
        required=False, queryset=AlbumType.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:music-album-type_select', attrs={
            'aria-label': _('Tipo de álbum'),
            'title': _('LP, EP, single, recopilatorio… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    release_date = forms.DateField(
        label=_('Fecha de lanzamiento'),
        help_text=_('Formato dd-mm-aaaa. Se elige en el calendario.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Fecha de lanzamiento'),
            'class': 'js-date', 'autocomplete': 'off',
            'title': _('Formato dd-mm-aaaa. Se elige en el calendario.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    description = forms.CharField(
        label=_('Reseña'),
        help_text=_('Reseña o descripción del álbum (opcional). Se muestra en su ficha pública.'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Reseña'), 'aria-label': _('Reseña'), 'rows': 5,
            'title': _('Reseña o descripción del álbum (opcional).'),
        }),
    )
    genres = forms.ModelMultipleChoiceField(
        label=_('Géneros'),
        help_text=_('Puedes elegir varios. Escribe para buscar.'),
        required=False, queryset=Genre.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:music-genre_select', attrs={
            'aria-label': _('Géneros'), 'title': _('Puedes elegir varios. Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        """El `slug` de Album NO es único: dos artistas distintos pueden tener un
        álbum con el mismo título. Solo normalizamos."""
        return ' '.join((self.cleaned_data.get('title') or '').split())


class AlbumImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = AlbumImage
        fields = ['album', 'order', 'image', 'image_url', 'is_active']

    album = forms.ModelChoiceField(
        label=_('Álbum'),
        help_text=_('De qué álbum es la imagen. Escribe para buscar.'),
        required=True, queryset=Album.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:album_select', attrs={
            'aria-label': _('Álbum'), 'required': 'required',
            'title': _('De qué álbum es la imagen. Escribe para buscar.'),
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


class AlbumTypeForm(FormBaseCategory):
    """Tipo de álbum: LP, EP, single, recopilatorio…"""

    class Meta:
        model = AlbumType
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un tipo de álbum con este nombre.')


class ArtistForm(forms.ModelForm):
    """Artista o banda. Los desplegables NO vuelcan sus tablas: buscan en el servidor
    por AJAX contra `<entidad>/select/` (ver `core/shared/forms/widgets.py` y `BaseSelectView`)."""

    class Meta:
        model = Artist
        fields = ['name', 'biography', 'start_year', 'year_end', 'artist_type', 'genres', 'is_active']

    name = forms.CharField(
        label=_('Nombre'),
        help_text=_('Nombre del artista o de la banda.'),
        required=True, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 150, 'required': 'required',
            'title': _('Nombre del artista o de la banda.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 150 caracteres.')},
    )
    biography = forms.CharField(
        label=_('Biografía'),
        help_text=_('Reseña o historia del artista (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Biografía'), 'aria-label': _('Biografía'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Reseña o historia del artista (opcional).'),
        }),
    )
    start_year = forms.IntegerField(
        label=_('Año de inicio'),
        help_text=_('Año en que empezó su actividad (opcional).'),
        required=False, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('1991'), 'aria-label': _('Año de inicio'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'title': _('Año en que empezó su actividad (opcional).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    year_end = forms.IntegerField(
        label=_('Año de fin'),
        help_text=_('Año en que se disolvió o dejó de publicar (opcional).'),
        required=False, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('2005'), 'aria-label': _('Año de fin'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'title': _('Año en que se disolvió o dejó de publicar (opcional).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    artist_type = forms.ModelChoiceField(
        label=_('Tipo de artista'),
        help_text=_('Solista, banda, dúo… Escribe para buscar.'),
        required=False, queryset=ArtistType.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:music-artist-type_select', attrs={
            'aria-label': _('Tipo de artista'), 'title': _('Solista, banda, dúo… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    genres = forms.ModelMultipleChoiceField(
        label=_('Géneros'),
        help_text=_('Puedes elegir varios. Escribe para buscar.'),
        required=False, queryset=Genre.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:music-genre_select', attrs={
            'aria-label': _('Géneros'), 'title': _('Puedes elegir varios. Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,          # el modelo trae default=True
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_name(self):
        """El `slug` de Artist NO es único (puede haber bandas homónimas reales), así
        que aquí solo normalizamos: no bloqueamos nombres repetidos."""
        return ' '.join((self.cleaned_data.get('name') or '').split())

    def clean_biography(self):
        return (self.cleaned_data.get('biography') or '').strip()

    def clean(self):
        """Cruce de dos campos: un artista no puede terminar antes de empezar."""
        cleaned = super().clean()
        inicio = cleaned.get('start_year')
        fin = cleaned.get('year_end')
        if inicio and fin and fin < inicio:
            self.add_error('year_end', 'El año de fin no puede ser anterior al de inicio.')
        return cleaned


class ArtistImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = ArtistImage
        fields = ['artist', 'order', 'image', 'image_url', 'is_active']

    artist = forms.ModelChoiceField(
        label=_('Artista'),
        help_text=_('De quién es la imagen. Escribe para buscar.'),
        required=True, queryset=Artist.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:artist_select', attrs={
            'aria-label': _('Artista'), 'required': 'required',
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
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_image': _('Envía una imagen válida.')},
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

    def clean_image_url(self):
        return (self.cleaned_data.get('image_url') or '').strip()

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('image') and not cleaned.get('image_url'):
            self.add_error('image', _('Sube un archivo o escribe su URL.'))
        return cleaned

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


class ArtistMemberForm(forms.ModelForm):
    """Miembro de un artista/banda: una persona con un rol y un periodo.
    El modelo exige que (artista, persona, rol) sea único: se comprueba en `clean()`,
    igual que la coherencia del periodo (desde ≤ hasta)."""

    class Meta:
        model = ArtistMember
        fields = ['artist', 'person', 'role', 'join_date', 'leave_date', 'is_active']

    artist = forms.ModelChoiceField(
        label=_('Artista'),
        help_text=_('Banda o proyecto del que es miembro. Escribe para buscar.'),
        required=True, queryset=Artist.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:artist_select', attrs={
            'aria-label': _('Artista'), 'required': 'required',
            'title': _('Banda o proyecto del que es miembro. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('Quién es el miembro. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('Quién es el miembro. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.ModelChoiceField(
        label=_('Rol'),
        help_text=_('Vocalista, guitarra, batería… (opcional).'),
        required=False, queryset=Role.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:music-role_select', attrs={
            'aria-label': _('Rol'), 'title': _('Vocalista, guitarra, batería… (opcional).'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    join_date = forms.DateField(
        label=_('Desde'),
        help_text=_('Cuándo entró en la banda. Formato dd-mm-aaaa.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Desde'), 'class': 'js-date',
            'autocomplete': 'off', 'title': _('Cuándo entró en la banda. Formato dd-mm-aaaa.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    leave_date = forms.DateField(
        label=_('Hasta'),
        help_text=_('Cuándo salió. Vacío si sigue en la banda.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Hasta'), 'class': 'js-date',
            'autocomplete': 'off', 'title': _('Cuándo salió. Vacío si sigue en la banda.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean(self):
        cleaned = super().clean()
        # Periodo coherente: no se puede salir antes de entrar.
        desde = cleaned.get('join_date')
        hasta = cleaned.get('leave_date')
        if desde and hasta and hasta < desde:
            self.add_error('leave_date', 'La fecha «hasta» no puede ser anterior a «desde».')
        # `unique_together = (artist, person, role)` en el modelo.
        artist = cleaned.get('artist')
        person = cleaned.get('person')
        if artist and person:
            duplicados = ArtistMember.objects.filter(
                artist=artist, person=person, role=cleaned.get('role'))
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, 'Esta persona ya está registrada con ese rol en el artista.')
        return cleaned


class ArtistTypeForm(FormBaseCategory):
    """Tipo de artista: solista, banda, dúo, orquesta…"""

    class Meta:
        model = ArtistType
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un tipo de artista con este nombre.')


class DataDeezerAlbumForm(forms.ModelForm):
    """Staging de la ficha completa de un álbum (Deezer). Solo banderas del proceso."""

    class Meta:
        model = DataDeezerAlbum
        fields = ['deezer_id', 'deezer_id_artist', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

    data_status = forms.BooleanField(
        label=_('Fetch OK'),
        help_text=_('La API respondió y el JSON se guardó bien.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'),
        help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataDeezerAlbumImportForm(LanzaTareaMixin, forms.Form):
    """Importa ÁLBUMES de Deezer por un rango de ids [inicio, fin]; para uno solo, el mismo id en los dos.
    Se precarga por donde va el cursor de álbumes."""

    TIPO = 'album'
    slug = 'id'
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-deezer-album_list'
    success_label = _('datos crudos')

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=9999999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 9999999999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un álbum de Deezer.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=9999999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 9999999999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un álbum de Deezer.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        self.siguiente = siguiente('deezer', self.TIPO)
        self.cantidad = cantidad_de('deezer', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van álbumes.') % {'sig': self.siguiente}
        self.fields['fin'].help_text = _(
            'Último id del lote. Vacío = inicio + %(cant)s (la cantidad del cursor; Tareas → Cursores de lote). '
            'Máximo %(max)s ids por tanda.') % {'cant': self.cantidad, 'max': MAX_IDS_POR_LOTE}

    def clean(self):
        cleaned = super().clean()
        inicio, fin = cleaned.get('inicio'), cleaned.get('fin')
        if inicio is None:
            return cleaned
        if fin is None:                # sin fin: la cantidad que diga el cursor
            fin = cleaned['fin'] = inicio + self.cantidad - 1
        if fin < inicio:
            self.add_error('fin', _('El id final no puede ser menor que el inicial.'))
        elif (fin - inicio + 1) > MAX_IDS_POR_LOTE:
            self.add_error('fin', _('El lote pide %(piden)s ids; el máximo son %(max)s por tanda.')
                           % {'piden': fin - inicio + 1, 'max': MAX_IDS_POR_LOTE})
        return cleaned

    def tarea(self, vista):
        """Encola el lote; si continúa donde iba el cursor, el cursor avanza."""
        from django.contrib import messages
        from core.shared.tasks.cursor import avanzar_si_contiguo
        inicio, fin = self.cleaned_data['inicio'], self.cleaned_data['fin']
        if avanzar_si_contiguo('deezer', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de álbumes avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de álbumes [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class DataDeezerAlbumSearchForm(LanzaTareaMixin, forms.Form):
    """Busca ÁLBUMES en Deezer por nombre. Solo es la caja: manda por GET a su vista de resultados, donde se
    marcan los que se quieran y se importan (ficha + pistas + su artista, que se crea si no estaba)."""

    TIPO = 'album'
    slug = 'buscar'
    titulo = _('Por nombre')
    boton = _('Buscar')
    resultados_url = 'panel:deezer-album-search'
    success_url = 'panel:data-deezer-album_list'
    success_label = _('datos crudos')

    q = forms.CharField(
        label=_('Nombre del álbum'),
        help_text=_('Para un artista concreto: artist:"ONE OK ROCK" album:"Ambitions".'),
        required=False, min_length=2, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'type': 'search', 'aria-label': _('Nombre del álbum'), 'autocomplete': 'off',
            'placeholder': _('Nevermind'),
        }),
        error_messages={'min_length': _('Escribe al menos dos letras para buscar.')},
    )

    def tarea_lista(self, vista, ids):
        """Los álbumes marcados → la tarea de lista de álbumes."""
        return vista.task_ids, (self.TIPO, list(ids)), {}


class DataDeezerArtistForm(forms.ModelForm):
    """Staging del artista traído de Deezer. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataDeezerArtist
        fields = ['deezer_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

    data_status = forms.BooleanField(
        label=_('Fetch OK'),
        help_text=_('La API respondió y el JSON se guardó bien.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'),
        help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataDeezerArtistImportForm(LanzaTareaMixin, forms.Form):
    """Importa ARTISTAS de Deezer por un rango de ids [inicio, fin]; para uno solo, el mismo id en los dos.
    Solo descarga al crudo: no procesa. Se precarga por donde va el cursor de artistas."""

    TIPO = 'artista'                   # la clave del tipo en Deezer: cursores, servicio y tarea de rango
    slug = 'id'
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-deezer-artist_list'
    success_label = _('datos crudos · sin procesar')

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=99999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un artista de Deezer.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=99999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un artista de Deezer.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        self.siguiente = siguiente('deezer', self.TIPO)
        self.cantidad = cantidad_de('deezer', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van los artistas.') % {'sig': self.siguiente}
        self.fields['fin'].help_text = _(
            'Último id del lote. Vacío = inicio + %(cant)s (la cantidad del cursor; Tareas → Cursores de lote). '
            'Máximo %(max)s ids por tanda.') % {'cant': self.cantidad, 'max': MAX_IDS_POR_LOTE}

    def clean(self):
        cleaned = super().clean()
        inicio, fin = cleaned.get('inicio'), cleaned.get('fin')
        if inicio is None:
            return cleaned
        if fin is None:                # sin fin: la cantidad que diga el cursor
            fin = cleaned['fin'] = inicio + self.cantidad - 1
        if fin < inicio:
            self.add_error('fin', _('El id final no puede ser menor que el inicial.'))
        elif (fin - inicio + 1) > MAX_IDS_POR_LOTE:
            self.add_error('fin', _('El lote pide %(piden)s ids; el máximo son %(max)s por tanda.')
                           % {'piden': fin - inicio + 1, 'max': MAX_IDS_POR_LOTE})
        return cleaned

    def tarea(self, vista):
        """Baja el lote al crudo; si el lote continúa donde iba el cursor, el cursor avanza."""
        from django.contrib import messages
        from core.shared.tasks.cursor import avanzar_si_contiguo
        inicio, fin = self.cleaned_data['inicio'], self.cleaned_data['fin']
        if avanzar_si_contiguo('deezer', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de artistas avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de artistas [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class DataDeezerArtistSearchForm(LanzaTareaMixin, forms.Form):
    """Busca ARTISTAS en Deezer por nombre. Solo es la caja: manda por GET a su vista de resultados
    (`resultados_url`), donde se marcan los que se quieran y se importan al crudo con la tarea de lista de ids."""

    TIPO = 'artista'
    slug = 'buscar'
    titulo = _('Por nombre')
    boton = _('Buscar')
    resultados_url = 'panel:deezer-artist-search'
    success_url = 'panel:data-deezer-artist_list'
    success_label = _('datos crudos · sin procesar')

    q = forms.CharField(
        label=_('Nombre del artista'),
        help_text=_('Busca en Deezer y elige cuál importar: no hace falta saber el id.'),
        required=False, min_length=2, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'type': 'search', 'aria-label': _('Nombre del artista'), 'autocomplete': 'off',
            'placeholder': _('ONE OK ROCK'),
        }),
        error_messages={'min_length': _('Escribe al menos dos letras para buscar.')},
    )

    def tarea_lista(self, vista, ids):
        """Los ids marcados en los resultados → la tarea de lista del tipo (descarga al crudo)."""
        return vista.task_ids, (self.TIPO, list(ids)), {}


class DataDeezerGenreForm(forms.ModelForm):
    """Staging del género traído de Deezer. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataDeezerGenre
        fields = ['deezer_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

    data_status = forms.BooleanField(
        label=_('Fetch OK'),
        help_text=_('La API respondió y el JSON se guardó bien.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'),
        help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataDeezerTrackForm(forms.ModelForm):
    """Staging de una PISTA de un álbum (Deezer). Solo banderas del proceso."""

    class Meta:
        model = DataDeezerTrack
        fields = ['deezer_id', 'deezer_id_album', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

    data_status = forms.BooleanField(
        label=_('Fetch OK'),
        help_text=_('La API respondió y el JSON se guardó bien.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'),
        help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataDeezerTrackImportForm(LanzaTareaMixin, forms.Form):
    """Importa CANCIONES de Deezer por un rango de ids [inicio, fin]; para uno solo, el mismo id en los dos.
    Se precarga por donde va el cursor de canciones."""

    TIPO = 'cancion'
    slug = 'id'
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-deezer-track_list'
    success_label = _('datos crudos')

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=9999999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 9999999999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser una canción de Deezer.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=9999999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 9999999999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser una canción de Deezer.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        self.siguiente = siguiente('deezer', self.TIPO)
        self.cantidad = cantidad_de('deezer', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van canciones.') % {'sig': self.siguiente}
        self.fields['fin'].help_text = _(
            'Último id del lote. Vacío = inicio + %(cant)s (la cantidad del cursor; Tareas → Cursores de lote). '
            'Máximo %(max)s ids por tanda.') % {'cant': self.cantidad, 'max': MAX_IDS_POR_LOTE}

    def clean(self):
        cleaned = super().clean()
        inicio, fin = cleaned.get('inicio'), cleaned.get('fin')
        if inicio is None:
            return cleaned
        if fin is None:                # sin fin: la cantidad que diga el cursor
            fin = cleaned['fin'] = inicio + self.cantidad - 1
        if fin < inicio:
            self.add_error('fin', _('El id final no puede ser menor que el inicial.'))
        elif (fin - inicio + 1) > MAX_IDS_POR_LOTE:
            self.add_error('fin', _('El lote pide %(piden)s ids; el máximo son %(max)s por tanda.')
                           % {'piden': fin - inicio + 1, 'max': MAX_IDS_POR_LOTE})
        return cleaned

    def tarea(self, vista):
        """Encola el lote; si continúa donde iba el cursor, el cursor avanza."""
        from django.contrib import messages
        from core.shared.tasks.cursor import avanzar_si_contiguo
        inicio, fin = self.cleaned_data['inicio'], self.cleaned_data['fin']
        if avanzar_si_contiguo('deezer', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de canciones avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de canciones [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class DataDeezerTrackSearchForm(LanzaTareaMixin, forms.Form):
    """Busca CANCIONES en Deezer por nombre. Una canción vive dentro de su álbum: lo que se importa al marcarla
    es SU ÁLBUM entero (con el artista y todas las pistas). Por eso el TIPO de la tarea es «album»."""

    TIPO = 'album'                     # los ids de los resultados son de ÁLBUM (ver deezer.buscar_canciones)
    slug = 'buscar'
    titulo = _('Por nombre')
    boton = _('Buscar')
    resultados_url = 'panel:deezer-song-search'
    success_url = 'panel:data-deezer-track_list'
    success_label = _('datos crudos')

    q = forms.CharField(
        label=_('Nombre de la canción'),
        help_text=_('Marcar una canción trae su álbum completo. Para afinar, escribe artista y canción: Nirvana Lithium.'),
        required=False, min_length=2, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'type': 'search', 'aria-label': _('Nombre de la canción'), 'autocomplete': 'off',
            'placeholder': _('Smells Like Teen Spirit'),
        }),
        error_messages={'min_length': _('Escribe al menos dos letras para buscar.')},
    )

    def tarea_lista(self, vista, ids):
        """Los ÁLBUMES de las canciones marcadas → la tarea de lista de álbumes (sin repetir)."""
        return vista.task_ids, (self.TIPO, sorted(set(ids))), {}


class GenreAliasForm(forms.ModelForm):
    """alias de género: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = GenreAlias
        fields = ['name', 'name_esp', 'is_active', 'genre']


class GenreDeezerImportAllForm(LanzaTareaMixin, forms.Form):
    """Géneros de Deezer: NO hay id que teclear (los da todos en una sola llamada, GET /genre). El formulario
    no tiene campos: es el botón, y existe para que el lanzador funcione igual que los demás."""

    TIPO = 'genero'
    slug = 'todos'
    titulo = _('Todos de una vez')
    boton = _('Importar todos los géneros')
    success_url = 'panel:music-genre_list'
    success_label = _('la lista de géneros')

    def tarea(self, vista):
        """La tarea que trae TODOS los géneros; no lleva argumentos."""
        return vista.task_uno, (), {}

    def resumen(self, vista):
        return _('Importar los géneros de Deezer')


class GenreDeezerImportForm(LanzaTareaMixin, forms.Form):
    """Importa GÉNEROS de Deezer por un rango de ids [inicio, fin]; para uno solo, el mismo id en los dos.
    Los ids que no son música (DEEZER_NO_MUSICA) se descargan al crudo pero no crean Género.
    Se precarga por donde va el cursor de géneros."""

    TIPO = 'genero'
    slug = 'id'
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-deezer-genre_list'
    success_label = _('datos crudos')

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=99999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un género de Deezer.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=99999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de Deezer empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un género de Deezer.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        self.siguiente = siguiente('deezer', self.TIPO)
        self.cantidad = cantidad_de('deezer', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van géneros.') % {'sig': self.siguiente}
        self.fields['fin'].help_text = _(
            'Último id del lote. Vacío = inicio + %(cant)s (la cantidad del cursor; Tareas → Cursores de lote). '
            'Máximo %(max)s ids por tanda.') % {'cant': self.cantidad, 'max': MAX_IDS_POR_LOTE}

    def clean(self):
        cleaned = super().clean()
        inicio, fin = cleaned.get('inicio'), cleaned.get('fin')
        if inicio is None:
            return cleaned
        if fin is None:                # sin fin: la cantidad que diga el cursor
            fin = cleaned['fin'] = inicio + self.cantidad - 1
        if fin < inicio:
            self.add_error('fin', _('El id final no puede ser menor que el inicial.'))
        elif (fin - inicio + 1) > MAX_IDS_POR_LOTE:
            self.add_error('fin', _('El lote pide %(piden)s ids; el máximo son %(max)s por tanda.')
                           % {'piden': fin - inicio + 1, 'max': MAX_IDS_POR_LOTE})
        return cleaned

    def tarea(self, vista):
        """Encola el lote; si continúa donde iba el cursor, el cursor avanza."""
        from django.contrib import messages
        from core.shared.tasks.cursor import avanzar_si_contiguo
        inicio, fin = self.cleaned_data['inicio'], self.cleaned_data['fin']
        if avanzar_si_contiguo('deezer', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de géneros avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de géneros [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class GenreForm(FormBaseCategory):
    """Género musical: rock, jazz, electrónica…"""

    class Meta:
        model = Genre
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un género musical con este nombre.')


class RoleForm(forms.ModelForm):
    """Rol dentro de un artista/banda: Vocalista, Guitarra, Batería, Productor…"""

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
                raise forms.ValidationError('Ya existe un rol musical con este nombre.')
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


class SongComposerForm(forms.ModelForm):
    """Compositor de una canción: la PERSONA real que la escribió."""

    class Meta:
        model = SongComposer
        fields = ['song', 'person', 'is_active']

    song = forms.ModelChoiceField(
        label=_('Canción'),
        help_text=_('Qué canción compuso. Escribe para buscar.'),
        required=True, queryset=Song.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:song_select', attrs={
            'aria-label': _('Canción'), 'required': 'required',
            'title': _('Qué canción compuso. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('Quién la compuso o escribió. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('Quién la compuso o escribió. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en la ficha de la canción.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean(self):
        data = super().clean()
        song, person = data.get('song'), data.get('person')
        if song and person:
            repetido = SongComposer.objects.filter(song=song, person=person)
            if self.instance.pk:
                repetido = repetido.exclude(pk=self.instance.pk)
            if repetido.exists():
                self.add_error('person', 'Esa persona ya figura como compositora de esta canción.')
        return data


class SongForm(forms.ModelForm):
    """Canción de un álbum. El modelo exige que (álbum, nº de pista, título) sea
    único: se comprueba en `clean()` para dar un mensaje claro."""

    class Meta:
        model = Song
        fields = ['title', 'title_short', 'title_version', 'album', 'album_song_id',
                  'composers', 'release_year',
                  'audio_file', 'lyrics', 'meaning', 'video_url', 'is_active']

    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título de la canción.'),
        required=True, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 500, 'required': 'required', 'title': _('Título de la canción.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 500 caracteres.')},
    )
    title_short = forms.CharField(
        label=_('Título corto'),
        help_text=_('Versión abreviada del título (opcional).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título corto'), 'aria-label': _('Título corto'), 'autocomplete': 'off',
            'maxlength': 255, 'title': _('Versión abreviada del título (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    title_version = forms.CharField(
        label=_('Versión'),
        help_text=_('Remix, en vivo, acústica… (opcional).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Remix / En vivo'), 'aria-label': _('Versión'), 'autocomplete': 'off',
            'maxlength': 255, 'title': _('Remix, en vivo, acústica… (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    album = forms.ModelChoiceField(
        label=_('Álbum'),
        help_text=_('Álbum al que pertenece. Escribe para buscar.'),
        required=True, queryset=Album.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:album_select', attrs={
            'aria-label': _('Álbum'), 'required': 'required',
            'title': _('Álbum al que pertenece. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    album_song_id = forms.IntegerField(
        label=_('Nº de pista'),
        help_text=_('Posición dentro del álbum. 0 si no aplica.'),
        required=False, min_value=0, initial=0,      # el modelo trae default=0
        widget=forms.NumberInput(attrs={
            'placeholder': _('1'), 'aria-label': _('Nº de pista'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 0,
            'title': _('Posición dentro del álbum. 0 si no aplica.'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El valor mínimo es 0.')},
    )
    audio_file = forms.FileField(
        label=_('Archivo de audio'),
        help_text=AUDIO_HINT,
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'aria-label': _('Archivo de audio'), 'accept': AUDIO_ACCEPT,
            'title': AUDIO_HINT,
        }),
    )
    lyrics = forms.CharField(
        label=_('Letra'),
        help_text=_('Letra de la canción (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Letra'), 'aria-label': _('Letra'), 'autocomplete': 'off',
            'rows': 10, 'title': _('Letra de la canción (opcional).'),
        }),
    )
    meaning = forms.CharField(
        label=_('Significado'),
        help_text=_('Qué cuenta la canción (opcional). Abre el detalle de su ficha.'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Significado'), 'aria-label': _('Significado'), 'rows': 6,
            'title': _('Qué cuenta la canción (opcional).'),
        }),
    )
    composers = forms.CharField(
        label=_('Compuesta por'),
        help_text=_('Quién la escribió o compuso (p. ej. Lennon / McCartney). Opcional.'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Compuesta por'), 'aria-label': _('Compuesta por'),
            'autocomplete': 'off', 'maxlength': 255,
            'title': _('Quién la escribió o compuso (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    release_year = forms.IntegerField(
        label=_('Año'),
        help_text=_('Año de la canción, si difiere del álbum (opcional).'),
        required=False, min_value=1000, max_value=9999,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Año'), 'aria-label': _('Año'), 'min': 1000, 'max': 9999,
            'title': _('Año de la canción (opcional).'),
        }),
        error_messages={'min_value': _('Año inválido.'), 'max_value': _('Año inválido.'),
                        'invalid': _('Escribe un año válido.')},
    )
    video_url = forms.URLField(
        label=_('Video'),
        help_text=_('URL del video (YouTube); se incrusta en la pestaña Letra (opcional).'),
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': _('https://www.youtube.com/watch?v=…'), 'aria-label': _('Video'),
            'title': _('URL del video (YouTube).'),
        }),
        error_messages={'invalid': _('Envía una URL válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        return ' '.join((self.cleaned_data.get('title') or '').split())

    def clean_title_short(self):
        return ' '.join((self.cleaned_data.get('title_short') or '').split())

    def clean_title_version(self):
        return ' '.join((self.cleaned_data.get('title_version') or '').split())

    def clean_lyrics(self):
        return (self.cleaned_data.get('lyrics') or '').strip()

    def clean_album_song_id(self):
        pista = self.cleaned_data.get('album_song_id')
        return 0 if pista is None else pista

    def clean_audio_file(self):
        """Este campo es AUDIO, no un documento: la lista de extensiones y el límite
        de peso son los propios de un archivo de música."""
        audio = self.cleaned_data.get('audio_file')
        if not isinstance(audio, UploadedFile):
            return audio
        nombre = audio.name or ''
        ext = ('.' + nombre.rsplit('.', 1)[-1].lower()) if '.' in nombre else ''
        if ext not in AUDIO_EXTENSIONS:
            raise forms.ValidationError(
                'Formato no permitido (%s). Usa %s.'
                % (ext or 'sin extensión', AUDIO_FORMATS))
        if audio.size > AUDIO_MAX_MB * MB:
            raise forms.ValidationError(
                'El archivo pesa %s MB; el máximo son %s MB.' % (round(audio.size / MB, 1), AUDIO_MAX_MB))
        return audio

    def clean(self):
        """`unique_together = (album, album_song_id, title)` en el modelo."""
        cleaned = super().clean()
        album = cleaned.get('album')
        title = cleaned.get('title')
        if album and title:
            duplicadas = Song.objects.filter(
                album=album, album_song_id=cleaned.get('album_song_id') or 0, title=title)
            if self.instance.pk:
                duplicadas = duplicadas.exclude(pk=self.instance.pk)
            if duplicadas.exists():
                self.add_error('title', 'Ese álbum ya tiene una canción con ese título y nº de pista.')
        return cleaned


class SongTranslationForm(forms.ModelForm):
    """Traducción de la letra de una canción a UN idioma (una fila por idioma)."""

    class Meta:
        model = SongTranslation
        fields = ['song', 'language', 'text', 'is_active']

    song = forms.ModelChoiceField(
        label=_('Canción'),
        help_text=_('Canción a la que pertenece la traducción. Escribe para buscar.'),
        required=True, queryset=Song.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:song_select', attrs={
            'aria-label': _('Canción'), 'required': 'required',
            'title': _('Canción a la que pertenece la traducción.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    language = forms.ModelChoiceField(
        label=_('Idioma'),
        help_text=_('Idioma de la traducción. Escribe para buscar.'),
        required=True, empty_label=_('—'),
        queryset=None,   # se fija en __init__ (import cruzado)
        widget=AjaxSelect(url_name='panel:language_select', attrs={
            'aria-label': _('Idioma'), 'required': 'required',
            'title': _('Idioma de la traducción.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    text = forms.CharField(
        label=_('Traducción'),
        help_text=_('Letra traducida a ese idioma.'),
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': _('Traducción'), 'aria-label': _('Traducción'), 'rows': 10,
            'title': _('Letra traducida a ese idioma.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.catalogs.models import Language
        self.fields['language'].queryset = Language.objects.all()

    def clean(self):
        """Duplicado claro: una canción solo tiene UNA traducción por idioma."""
        cleaned = super().clean()
        cancion, idioma = cleaned.get('song'), cleaned.get('language')
        if cancion and idioma:
            dup = SongTranslation.objects.filter(song=cancion, language=idioma)
            if self.instance.pk:
                dup = dup.exclude(pk=self.instance.pk)
            if dup.exists():
                self.add_error('language', 'Esa canción ya tiene traducción en ese idioma.')
        return cleaned


class MusicLogForm(forms.ModelForm):
    """Log de música: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = MusicLog
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


class AlbumImageDownloadForm(DescargarImagenesForm):
    TIPO = 'music.AlbumImage'
    success_url = 'panel:album-image_list'



class ArtistImageDownloadForm(DescargarImagenesForm):
    TIPO = 'music.ArtistImage'
    success_url = 'panel:artist-image_list'


class AlbumImageRetryForm(ReintentarMuertasForm):
    TIPO = 'music.AlbumImage'
    success_url = 'panel:album-image_download'



class ArtistImageRetryForm(ReintentarMuertasForm):
    TIPO = 'music.ArtistImage'
    success_url = 'panel:artist-image_download'

