"""Formularios del panel para `games` — UNO POR MODELO, AUTÓNOMOS.

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

Sí, hay repetición entre formularios parecidos. Es a propósito: se lee y se cambia
uno sin tocar los demás.

`GameLog` y las tablas `Data*VNDB` / `DataF95Creator` no tienen formulario a propósito:
son registro y staging del importador, no se escriben a mano.
"""
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import ExternalSource, Language
from apps.games.models import Character, CharacterImage, CharacterRole, Creator, CreatorLink, CreatorNickname, DataF95Creator, DataF95Game, DataVndbCharacter, DataVndbCreator, DataVndbGame, DataVndbRelease, DevelopmentEngine, Game, GameImage, GameLink, GameLog, GameTitle, Genre, GenreAlias, Medium, Platform, Release, ReleaseImage, Tag, TagAlias
from core.shared.forms.base import FormBaseCategory, FormBaseLoadFile
from core.shared.forms.widgets import AjaxSelect, AjaxSelectMultiple
from core.shared.models.choices import CreatorType, GameStatus, GameType, LogLevel
from core.shared.views.imports import DescargarImagenesForm, ReintentarMuertasForm, LanzaTareaMixin, MAX_IDS_POR_LOTE, ProcesarLoteForm
from core.utils.constants import DUMP_EXTENSIONS, DUMP_MAX_MB, IMAGE_ACCEPT, IMAGE_EXTENSIONS, IMAGE_FORMATS, IMAGE_HINT, IMAGE_MAX_MB, MB


class CharacterForm(forms.ModelForm):
    """Personaje de novela visual: nombre, original, descripción y datos de VNDB."""

    class Meta:
        model = Character
        fields = ['name', 'original', 'description', 'sex', 'age', 'birthday', 'is_active']

    name = forms.CharField(
        label=_('Nombre'), required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off', 'maxlength': 255, 'required': 'required'}),
        error_messages={'required': _('Este campo es obligatorio.'), 'max_length': _('Máximo 255 caracteres.')},
    )
    original = forms.CharField(
        label=_('Nombre original'), required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={'placeholder': _('Nombre original'), 'aria-label': _('Nombre original'), 'autocomplete': 'off', 'maxlength': 255}),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    description = forms.CharField(
        label=_('Descripción'), required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': _('Descripción'), 'aria-label': _('Descripción')}),
    )
    sex = forms.CharField(
        label=_('Sexo'), required=False, max_length=10, help_text=_('Como lo da VNDB: m, f, b, n.'),
        widget=forms.TextInput(attrs={'placeholder': 'f', 'aria-label': _('Sexo'), 'maxlength': 10}),
    )
    age = forms.IntegerField(
        label=_('Edad'), required=False, min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': '17', 'aria-label': _('Edad'), 'inputmode': 'numeric', 'step': 1, 'min': 0}),
        error_messages={'invalid': _('Tiene que ser un número entero.'), 'min_value': _('No puede ser negativa.')},
    )
    birthday = forms.CharField(
        label=_('Cumpleaños'), required=False, max_length=5, help_text=_('MM-DD.'),
        widget=forms.TextInput(attrs={'placeholder': '05-16', 'aria-label': _('Cumpleaños'), 'maxlength': 5}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'), required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class CharacterImageForm(forms.ModelForm):
    """Imagen de un personaje de juego: archivo o URL (la baja el descargador de imágenes)."""

    class Meta:
        model = CharacterImage
        fields = ['character', 'order', 'image', 'image_url', 'is_active']

    character = forms.ModelChoiceField(
        label=_('Personaje'), required=True, queryset=Character.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:game-character_select', attrs={'aria-label': _('Personaje'), 'required': 'required'}),
        error_messages={'required': _('Elige el personaje.'), 'invalid_choice': _('Selecciona una opción válida.')},
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
    image = forms.ImageField(label=_('Imagen'), required=False, widget=forms.ClearableFileInput(attrs={'accept': IMAGE_ACCEPT, 'aria-label': _('Imagen')}))
    image_url = forms.CharField(
        label=_('URL de la imagen'), required=False, help_text=_('Si no subes archivo, el descargador la baja desde aquí.'),
        widget=forms.TextInput(attrs={'placeholder': 'https://t.vndb.org/ch/…', 'aria-label': _('URL de la imagen')}),
    )
    is_active = forms.BooleanField(label=_('Activo'), required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}))

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('image') and not cleaned.get('image_url'):
            self.add_error('image', _('Sube un archivo o escribe su URL.'))
        return cleaned


class CharacterRoleForm(forms.ModelForm):
    """En qué juego aparece un personaje y con qué papel."""

    class Meta:
        model = CharacterRole
        fields = ['character', 'game', 'role', 'is_active']

    character = forms.ModelChoiceField(
        label=_('Personaje'), required=True, queryset=Character.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:game-character_select', attrs={'aria-label': _('Personaje'), 'required': 'required'}),
        error_messages={'required': _('Elige el personaje.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )
    game = forms.ModelChoiceField(
        label=_('Juego'), required=True, queryset=Game.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:game_select', attrs={'aria-label': _('Juego'), 'required': 'required'}),
        error_messages={'required': _('Elige el juego.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.CharField(
        label=_('Rol'), required=False, max_length=20, help_text=_('main, primary, side, appears.'),
        widget=forms.TextInput(attrs={'placeholder': 'main', 'aria-label': _('Rol'), 'maxlength': 20}),
    )
    is_active = forms.BooleanField(label=_('Activo'), required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}))


class CreatorForm(forms.ModelForm):
    """Creador / desarrollador: estudio, círculo o persona que hace los juegos."""

    class Meta:
        model = Creator
        fields = ['name', 'type', 'languages', 'description', 'is_active']

    name = forms.CharField(
        label=_('Nombre'),
        help_text=_('Nombre del estudio, círculo o persona.'),
        required=True, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 150, 'required': 'required',
            'title': _('Nombre del estudio, círculo o persona.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 150 caracteres.')},
    )
    type = forms.ChoiceField(
        label=_('Tipo'), required=False, choices=[('', '—')] + list(CreatorType.choices),
        widget=forms.Select(attrs={'aria-label': _('Tipo'), 'title': _('Compañía, individual o grupo amateur.')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    languages = forms.ModelMultipleChoiceField(
        label=_('Idiomas'),
        help_text=_('Idiomas en los que publica. Puedes elegir varios.'),
        required=False, queryset=Language.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:language_select', attrs={
            'aria-label': _('Idiomas'), 'title': _('Idiomas en los que publica. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    description = forms.CharField(
        label=_('Descripción'),
        help_text=_('Reseña del creador (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Descripción'), 'aria-label': _('Descripción'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Reseña del creador (opcional).'),
        }),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_name(self):
        """El `slug` de Creator NO es único: solo normalizamos."""
        return ' '.join((self.cleaned_data.get('name') or '').split())

    def clean_description(self):
        return (self.cleaned_data.get('description') or '').strip()


class CreatorLinkForm(forms.ModelForm):
    """Enlace externo de un creador: Patreon, Discord, X/Twitter, sitio oficial…
    El modelo exige que (creador, fuente, id externo) sea único: se comprueba en `clean()`."""

    class Meta:
        model = CreatorLink
        fields = ['creator', 'source', 'external_id', 'url', 'is_active']

    creator = forms.ModelChoiceField(
        label=_('Creador'),
        help_text=_('De quién es el enlace. Escribe para buscar.'),
        required=True, queryset=Creator.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:creator_select', attrs={
            'aria-label': _('Creador'), 'required': 'required',
            'title': _('De quién es el enlace. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    source = forms.ModelChoiceField(
        label=_('Fuente'),
        help_text=_('Plataforma del enlace (Patreon, Discord…). Escribe para buscar.'),
        required=True, queryset=ExternalSource.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:external-source_select', attrs={
            'aria-label': _('Fuente'), 'required': 'required',
            'title': _('Plataforma del enlace (Patreon, Discord…). Escribe para buscar.'),
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
            'placeholder': _('https://www.patreon.com/usuario123'), 'aria-label': _('URL'),
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
        """`unique_together = (creator, source, external_id)` en el modelo."""
        cleaned = super().clean()
        creator = cleaned.get('creator')
        source = cleaned.get('source')
        if creator and source:
            duplicados = CreatorLink.objects.filter(
                creator=creator, source=source, external_id=cleaned.get('external_id') or '')
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('external_id',
                               'Este creador ya tiene ese enlace en esa plataforma.')
        return cleaned


class CreatorNicknameForm(forms.ModelForm):
    """Apodo/alias de un creador. El modelo exige que el par (creador, apodo) sea
    único: se comprueba en `clean()` para dar un mensaje claro."""

    class Meta:
        model = CreatorNickname
        fields = ['creator', 'nickname', 'is_active']

    creator = forms.ModelChoiceField(
        label=_('Creador'),
        help_text=_('A quién pertenece el apodo. Escribe para buscar.'),
        required=True, queryset=Creator.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:creator_select', attrs={
            'aria-label': _('Creador'), 'required': 'required',
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
        """`unique_together = (creator, nickname)` en el modelo."""
        cleaned = super().clean()
        creator = cleaned.get('creator')
        nickname = cleaned.get('nickname')
        if creator and nickname:
            duplicados = CreatorNickname.objects.filter(creator=creator, nickname=nickname)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('nickname', 'Este creador ya tiene registrado ese apodo.')
        return cleaned


class DataF95CreatorForm(forms.ModelForm):
    """Staging del creador (F95zone) que entra por dump, antes de crear la entidad `games.Creator`.

    Este formulario NO tiene campos a propósito: la fila es un volcado tal cual del
    scraping y no se edita a mano. La pantalla de edición existe solo para poder
    abrirla desde el listado; para descartar una fila se usa Eliminar.
    """

    class Meta:
        model = DataF95Creator
        fields = ['f95_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido


class DataF95GameForm(forms.ModelForm):
    """Staging del juego ya consolidado, antes de crear la entidad `games.Game`."""

    class Meta:
        model = DataF95Game
        fields = ['f95_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

    data_status = forms.BooleanField(
        label=_('Fetch OK'),
        help_text=_('Los datos se recogieron bien.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'),
        help_text=_('Ya se creó el juego a partir de estos datos. Desmárcalo para reprocesar.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataVndbCharacterForm(forms.ModelForm):
    """Staging del personaje traído de VNDB. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataVndbCharacter
        fields = ['vndb_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataVndbCharacterImportForm(LanzaTareaMixin, forms.Form):
    """Importa personajes de VNDB por un rango de ids [inicio, fin]; para uno solo, el mismo id en los dos.
    Solo descarga al crudo: no procesa. Se precarga por donde van los personajes: lo más alto entre el cursor de
    lote y lo ya descargado, así no se vuelve a pedir lo que ya está."""

    slug = 'id'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-vndb-character_list'
    success_label = _('datos crudos · sin procesar')

    TIPO = 'personaje'                    # la clave del tipo en VNDB: cursores, servicio y tarea de rango

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un personaje de VNDB.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un personaje de VNDB.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        from apps.games.services.vndb import siguiente_id_descargado
        self.siguiente = max(siguiente('vndb', self.TIPO), siguiente_id_descargado(self.TIPO))
        self.cantidad = cantidad_de('vndb', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van los personajes. Los ids ya descargados se saltan.'
        ) % {'sig': self.siguiente}
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
        if avanzar_si_contiguo('vndb', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de personajes avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de personajes [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class DataVndbCharacterPagesForm(LanzaTareaMixin, forms.Form):
    """Importa personajes por páginas del catálogo de VNDB: 100 filas por página, desde la página del cursor.
    Cada página es UNA petición a VNDB (100 filas es su máximo); el tope por tanda es su presupuesto antes del 429."""

    slug = 'paginas'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por páginas')
    boton = _('Importar')
    success_url = 'panel:data-vndb-character_list'
    success_label = _('datos crudos · sin procesar')

    MAX_PAGINAS = 200
    CURSOR = 'personaje-pagina'          # la fila de system.ImportCursor que dice por dónde va el barrido de personajes

    desde_pagina = forms.IntegerField(
        label=_('Desde página'),
        required=True, min_value=1, max_value=99999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde página'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe la página inicial.'),
                        'invalid': _('La página tiene que ser un número entero.'),
                        'min_value': _('Las páginas empiezan en 1.'),
                        'max_value': _('El catálogo de VNDB no llega a esa página.')},
    )
    paginas = forms.IntegerField(
        label=_('Cuántas páginas'),
        help_text=_('Una petición por página, con la espera que marca VNDB. 10 páginas son 1.000 personajes.'),
        required=False, min_value=1, max_value=MAX_PAGINAS, initial=10,
        widget=forms.NumberInput(attrs={
            'placeholder': '10', 'aria-label': _('Cuántas páginas'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': MAX_PAGINAS,
        }),
        error_messages={'invalid': _('Tiene que ser un número entero.'),
                        'min_value': _('Al menos una página.'),
                        'max_value': _('Máximo %(limit_value)s páginas por tanda.')},
    )
    todo = forms.BooleanField(
        label=_('Traerlas todas'), required=False, initial=False,
        help_text=_('Sigue página a página hasta que VNDB diga que no quedan más personajes. Cancelable desde Tareas.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Traerlas todas'), 'data-bloquea': 'paginas'}),
    )
    procesar = forms.BooleanField(
        label=_('Procesar al bajar'), required=False, initial=False,
        help_text=_('Convierte cada página en personajes nada más bajarla. Sin marcar, solo se deja el crudo y se '
                    'procesa luego con «Procesar pendientes» desde la lista de datos.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesar al bajar')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import siguiente
        self.siguiente_pagina = siguiente('vndb', self.CURSOR)
        if not self.is_bound:
            self.fields['desde_pagina'].initial = self.siguiente_pagina
        self.fields['desde_pagina'].help_text = _(
            'El catálogo entero de personajes, 100 por página. El cursor va por la %(pag)s; avanza página a página, '
            'así que si cancelas sigue donde quedó.') % {'pag': self.siguiente_pagina}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('todo'):
            cleaned['paginas'] = 0                    # 0 = sin tope: hasta que VNDB diga que no quedan más
            self.errors.pop('paginas', None)
        elif not cleaned.get('paginas'):
            self.add_error('paginas', _('Escribe cuántas páginas o marca «Traerlas todas».'))
        return cleaned

    def tarea(self, vista):
        """Dos barridos a la vez se pisan el presupuesto de VNDB (429), así que si ya hay uno no se apila otro."""
        from django.contrib import messages
        from core.shared.views.imports import tarea_en_curso
        en_curso = tarea_en_curso(vista.task_barrido)
        if en_curso:
            messages.warning(vista.request, _('Ya hay un barrido %(estado)s. Espera a que termine o cancélalo '
                                              'desde Tareas.') % {'estado': en_curso})
            return None
        return (vista.task_barrido,
                ('personaje', self.cleaned_data['desde_pagina'], self.cleaned_data['paginas']),
                {'procesar': self.cleaned_data['procesar']})

    def resumen(self, vista):
        paginas = self.cleaned_data['paginas']
        return _('Barrido de personajes (%(modo)s): %(cuantas)s de 100 desde la página %(desde)s') % {
            'modo': _('importar y procesar') if self.cleaned_data['procesar'] else _('importar al crudo'),
            'cuantas': _('TODAS las páginas') if not paginas else _('%(n)s página(s)') % {'n': paginas},
            'desde': self.cleaned_data['desde_pagina']}


class DataVndbCharacterSearchForm(LanzaTareaMixin, forms.Form):
    """Busca PERSONAJES en VNDB por nombre. Solo es la caja: manda por GET a su vista de resultados
    (`resultados_url`), donde se marcan los que se quieran y se importan al crudo con la tarea de lista de ids."""

    TIPO = 'personaje'
    slug = 'buscar'
    titulo = _('Por nombre')
    boton = _('Buscar')
    resultados_url = 'panel:vndb-character-buscar'
    success_url = 'panel:data-vndb-character_list'
    success_label = _('datos crudos · sin procesar')

    q = forms.CharField(
        label=_('Nombre del personaje'),
        help_text=_('Busca en VNDB y elige cuál importar: no hace falta saber el id.'),
        required=False, min_length=2, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'type': 'search', 'aria-label': _('Nombre del personaje'), 'autocomplete': 'off',
            'placeholder': _('Tsugumi'),
        }),
        error_messages={'min_length': _('Escribe al menos dos letras para buscar.')},
    )

    def tarea_lista(self, vista, ids):
        """Los ids marcados en los resultados → la tarea de lista del tipo (descarga al crudo)."""
        return vista.task_ids, (self.TIPO, list(ids)), {}


class DataVndbCreatorForm(forms.ModelForm):
    """Staging del creador traído de VNDB. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataVndbCreator
        fields = ['vndb_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataVndbCreatorImportForm(LanzaTareaMixin, forms.Form):
    """Importa creadores de VNDB por un rango de ids [inicio, fin]; para uno solo, el mismo id en los dos.
    Solo descarga al crudo: no procesa. Se precarga por donde van los creadores: lo más alto entre el cursor de
    lote y lo ya descargado, así no se vuelve a pedir lo que ya está."""

    slug = 'id'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-vndb-creator_list'
    success_label = _('datos crudos · sin procesar')

    TIPO = 'creador'                    # la clave del tipo en VNDB: cursores, servicio y tarea de rango

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un creador de VNDB.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un creador de VNDB.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        from apps.games.services.vndb import siguiente_id_descargado
        self.siguiente = max(siguiente('vndb', self.TIPO), siguiente_id_descargado(self.TIPO))
        self.cantidad = cantidad_de('vndb', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van los creadores. Los ids ya descargados se saltan.'
        ) % {'sig': self.siguiente}
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
        if avanzar_si_contiguo('vndb', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de creadores avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de creadores [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class DataVndbCreatorPagesForm(LanzaTareaMixin, forms.Form):
    """Importa creadores por páginas del catálogo de VNDB: 100 filas por página, desde la página del cursor.
    Cada página es UNA petición a VNDB (100 filas es su máximo); el tope por tanda es su presupuesto antes del 429."""

    slug = 'paginas'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por páginas')
    boton = _('Importar')
    success_url = 'panel:data-vndb-creator_list'
    success_label = _('datos crudos · sin procesar')

    MAX_PAGINAS = 200
    CURSOR = 'creador-pagina'          # la fila de system.ImportCursor que dice por dónde va el barrido de creadores

    desde_pagina = forms.IntegerField(
        label=_('Desde página'),
        required=True, min_value=1, max_value=99999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde página'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe la página inicial.'),
                        'invalid': _('La página tiene que ser un número entero.'),
                        'min_value': _('Las páginas empiezan en 1.'),
                        'max_value': _('El catálogo de VNDB no llega a esa página.')},
    )
    paginas = forms.IntegerField(
        label=_('Cuántas páginas'),
        help_text=_('Una petición por página, con la espera que marca VNDB. 10 páginas son 1.000 creadores.'),
        required=False, min_value=1, max_value=MAX_PAGINAS, initial=10,
        widget=forms.NumberInput(attrs={
            'placeholder': '10', 'aria-label': _('Cuántas páginas'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': MAX_PAGINAS,
        }),
        error_messages={'invalid': _('Tiene que ser un número entero.'),
                        'min_value': _('Al menos una página.'),
                        'max_value': _('Máximo %(limit_value)s páginas por tanda.')},
    )
    todo = forms.BooleanField(
        label=_('Traerlas todas'), required=False, initial=False,
        help_text=_('Sigue página a página hasta que VNDB diga que no quedan más creadores. Cancelable desde Tareas.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Traerlas todas'), 'data-bloquea': 'paginas'}),
    )
    procesar = forms.BooleanField(
        label=_('Procesar al bajar'), required=False, initial=False,
        help_text=_('Convierte cada página en creadores nada más bajarla. Sin marcar, solo se deja el crudo y se '
                    'procesa luego con «Procesar pendientes» desde la lista de datos.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesar al bajar')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import siguiente
        self.siguiente_pagina = siguiente('vndb', self.CURSOR)
        if not self.is_bound:
            self.fields['desde_pagina'].initial = self.siguiente_pagina
        self.fields['desde_pagina'].help_text = _(
            'El catálogo entero de creadores, 100 por página. El cursor va por la %(pag)s; avanza página a página, '
            'así que si cancelas sigue donde quedó.') % {'pag': self.siguiente_pagina}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('todo'):
            cleaned['paginas'] = 0                    # 0 = sin tope: hasta que VNDB diga que no quedan más
            self.errors.pop('paginas', None)
        elif not cleaned.get('paginas'):
            self.add_error('paginas', _('Escribe cuántas páginas o marca «Traerlas todas».'))
        return cleaned

    def tarea(self, vista):
        """Dos barridos a la vez se pisan el presupuesto de VNDB (429), así que si ya hay uno no se apila otro."""
        from django.contrib import messages
        from core.shared.views.imports import tarea_en_curso
        en_curso = tarea_en_curso(vista.task_barrido)
        if en_curso:
            messages.warning(vista.request, _('Ya hay un barrido %(estado)s. Espera a que termine o cancélalo '
                                              'desde Tareas.') % {'estado': en_curso})
            return None
        return (vista.task_barrido,
                ('creador', self.cleaned_data['desde_pagina'], self.cleaned_data['paginas']),
                {'procesar': self.cleaned_data['procesar']})

    def resumen(self, vista):
        paginas = self.cleaned_data['paginas']
        return _('Barrido de creadores (%(modo)s): %(cuantas)s de 100 desde la página %(desde)s') % {
            'modo': _('importar y procesar') if self.cleaned_data['procesar'] else _('importar al crudo'),
            'cuantas': _('TODAS las páginas') if not paginas else _('%(n)s página(s)') % {'n': paginas},
            'desde': self.cleaned_data['desde_pagina']}


class DataVndbCreatorSearchForm(LanzaTareaMixin, forms.Form):
    """Busca CREADORES en VNDB por nombre. Solo es la caja: manda por GET a su vista de resultados
    (`resultados_url`), donde se marcan los que se quieran y se importan al crudo con la tarea de lista de ids."""

    TIPO = 'creador'
    slug = 'buscar'
    titulo = _('Por nombre')
    boton = _('Buscar')
    resultados_url = 'panel:vndb-creator-buscar'
    success_url = 'panel:data-vndb-creator_list'
    success_label = _('datos crudos · sin procesar')

    q = forms.CharField(
        label=_('Nombre del creador'),
        help_text=_('Busca en VNDB y elige cuál importar: no hace falta saber el id.'),
        required=False, min_length=2, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'type': 'search', 'aria-label': _('Nombre del creador'), 'autocomplete': 'off',
            'placeholder': _('KID'),
        }),
        error_messages={'min_length': _('Escribe al menos dos letras para buscar.')},
    )

    def tarea_lista(self, vista, ids):
        """Los ids marcados en los resultados → la tarea de lista del tipo (descarga al crudo)."""
        return vista.task_ids, (self.TIPO, list(ids)), {}


class DataVndbGameForm(forms.ModelForm):
    """Staging del juego traído de VNDB. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataVndbGame
        fields = ['vndb_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataVndbGameImportForm(LanzaTareaMixin, forms.Form):
    """Importa JUEGOS por un rango de ids [inicio, fin]. Solo descarga al crudo: no procesa.

    Se precarga por donde va este tipo, que es lo más alto entre el cursor de lote y lo ya descargado
    (por páginas, por rango o uno a uno), así no se vuelve a pedir lo que ya está.
    """

    slug = 'id'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-vndb-game_list'
    success_label = _('datos crudos · sin procesar')

    TIPO = 'juego'                     # la clave del tipo en VNDB: cursores, servicio y tarea de rango

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un juego de VNDB.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un juego de VNDB.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        from apps.games.services.vndb import siguiente_id_descargado
        self.siguiente = max(siguiente('vndb', self.TIPO), siguiente_id_descargado(self.TIPO))
        self.cantidad = cantidad_de('vndb', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van los juegos. Los ids ya descargados se saltan.'
        ) % {'sig': self.siguiente}
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
        if avanzar_si_contiguo('vndb', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de juegos avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de juegos [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class DataVndbGamePagesForm(LanzaTareaMixin, forms.Form):
    """Importa JUEGOS por páginas del catálogo de VNDB: 100 filas por página, desde la página del cursor.

    Cada página es UNA petición a VNDB (100 filas es su máximo). El tope por tanda es el presupuesto que
    da VNDB antes de contestar 429.
    """

    slug = 'paginas'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por páginas')
    boton = _('Importar')
    success_url = 'panel:data-vndb-game_list'
    success_label = _('datos crudos · sin procesar')

    MAX_PAGINAS = 200
    CURSOR = 'juego-pagina'            # la fila de system.ImportCursor que dice por dónde va el barrido de juegos

    desde_pagina = forms.IntegerField(
        label=_('Desde página'),
        required=True, min_value=1, max_value=99999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde página'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe la página inicial.'),
                        'invalid': _('La página tiene que ser un número entero.'),
                        'min_value': _('Las páginas empiezan en 1.'),
                        'max_value': _('El catálogo de VNDB no llega a esa página.')},
    )
    paginas = forms.IntegerField(
        label=_('Cuántas páginas'),
        help_text=_('Una petición por página, con la espera que marca VNDB. 10 páginas son 1.000 juegos.'),
        required=False, min_value=1, max_value=MAX_PAGINAS, initial=10,
        widget=forms.NumberInput(attrs={
            'placeholder': '10', 'aria-label': _('Cuántas páginas'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': MAX_PAGINAS,
        }),
        error_messages={'invalid': _('Tiene que ser un número entero.'),
                        'min_value': _('Al menos una página.'),
                        'max_value': _('Máximo %(limit_value)s páginas por tanda.')},
    )
    todo = forms.BooleanField(
        label=_('Traerlas todas'), required=False, initial=False,
        help_text=_('Sigue página a página hasta que VNDB diga que no quedan más juegos. Cancelable desde Tareas.'),
        # data-bloquea: mientras esté marcada, el cuadro desactiva «Cuántas páginas», que aquí no se usa
        widget=forms.CheckboxInput(attrs={'aria-label': _('Traerlas todas'), 'data-bloquea': 'paginas'}),
    )
    procesar = forms.BooleanField(
        label=_('Procesar al bajar'), required=False, initial=False,
        help_text=_('Convierte cada página en juegos nada más bajarla. Sin marcar, solo se deja el crudo y se '
                    'procesa luego con «Procesar pendientes» desde la lista de datos.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesar al bajar')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import siguiente
        self.siguiente_pagina = siguiente('vndb', self.CURSOR)
        if not self.is_bound:
            self.fields['desde_pagina'].initial = self.siguiente_pagina
        self.fields['desde_pagina'].help_text = _(
            'El catálogo entero de juegos, 100 por página. El cursor va por la %(pag)s; avanza página a página, '
            'así que si cancelas sigue donde quedó.') % {'pag': self.siguiente_pagina}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('todo'):
            cleaned['paginas'] = 0                    # 0 = sin tope: hasta que VNDB diga que no quedan más
            self.errors.pop('paginas', None)
        elif not cleaned.get('paginas'):
            self.add_error('paginas', _('Escribe cuántas páginas o marca «Traerlas todas».'))
        return cleaned

    def tarea(self, vista):
        """Dos barridos a la vez se pisan el presupuesto de VNDB (429), así que si ya hay uno no se apila otro."""
        from django.contrib import messages
        from core.shared.views.imports import tarea_en_curso
        en_curso = tarea_en_curso(vista.task_barrido)
        if en_curso:
            messages.warning(vista.request, _('Ya hay un barrido %(estado)s. Espera a que termine o cancélalo '
                                              'desde Tareas.') % {'estado': en_curso})
            return None                               # no se lanza nada
        return (vista.task_barrido,
                ('juego', self.cleaned_data['desde_pagina'], self.cleaned_data['paginas']),
                {'procesar': self.cleaned_data['procesar']})

    def resumen(self, vista):
        paginas = self.cleaned_data['paginas']
        return _('Barrido de juegos (%(modo)s): %(cuantas)s de 100 desde la página %(desde)s') % {
            'modo': _('importar y procesar') if self.cleaned_data['procesar'] else _('importar al crudo'),
            'cuantas': _('TODAS las páginas') if not paginas else _('%(n)s página(s)') % {'n': paginas},
            'desde': self.cleaned_data['desde_pagina']}


class DataVndbGameSearchForm(LanzaTareaMixin, forms.Form):
    """Busca JUEGOS en VNDB por nombre. Solo es la caja: manda por GET a su vista de resultados
    (`resultados_url`), donde se marcan los que se quieran y se importan al crudo con la tarea de lista de ids."""

    TIPO = 'juego'
    slug = 'buscar'
    titulo = _('Por nombre')
    boton = _('Buscar')
    resultados_url = 'panel:vndb-game-buscar'
    success_url = 'panel:data-vndb-game_list'
    success_label = _('datos crudos · sin procesar')

    q = forms.CharField(
        label=_('Título del juego'),
        required=False,
        min_length=2,
        max_length=100,
        strip=True,
        widget=forms.TextInput(attrs={
            'type': 'search',
            'aria-label': _('Título del juego'),
            'autocomplete': 'off',
            'placeholder': _('Ever17'),
        }),
        error_messages={
            'min_length': _('Escribe al menos dos letras para buscar.')
            },
    )

    def tarea_lista(self, vista, ids):
        """Los ids marcados en los resultados → la tarea de lista del tipo (descarga al crudo)."""
        return vista.task_ids, (self.TIPO, list(ids)), {}


class DataVndbReleaseForm(forms.ModelForm):
    """Staging del lanzamiento traído de VNDB. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataVndbRelease
        fields = ['vndb_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataVndbReleaseImportForm(LanzaTareaMixin, forms.Form):
    """Importa lanzamientos de VNDB por un rango de ids [inicio, fin]; para uno solo, el mismo id en los dos.
    Solo descarga al crudo: no procesa. Se precarga por donde van los lanzamientos: lo más alto entre el cursor de
    lote y lo ya descargado, así no se vuelve a pedir lo que ya está."""

    slug = 'id'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por id')
    boton = _('Importar')
    success_url = 'panel:data-vndb-release_list'
    success_label = _('datos crudos · sin procesar')

    TIPO = 'lanzamiento'                    # la clave del tipo en VNDB: cursores, servicio y tarea de rango

    inicio = forms.IntegerField(
        label=_('Desde id'),
        required=True, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id inicial.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un lanzamiento de VNDB.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'),
        required=False, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Hasta id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 999999,
        }),
        error_messages={'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de VNDB empiezan en 1.'),
                        'max_value': _('Ese id es demasiado alto para ser un lanzamiento de VNDB.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        from apps.games.services.vndb import siguiente_id_descargado
        self.siguiente = max(siguiente('vndb', self.TIPO), siguiente_id_descargado(self.TIPO))
        self.cantidad = cantidad_de('vndb', self.TIPO)
        if not self.is_bound:          # precarga: del cursor al cursor + cantidad
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _(
            'Primer id del lote. Precargado con #%(sig)s, por donde van los lanzamientos. Los ids ya descargados se saltan.'
        ) % {'sig': self.siguiente}
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
        if avanzar_si_contiguo('vndb', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor del lote de lanzamientos avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Carga masiva de lanzamientos [%(a)s-%(b)s]') % {
            'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class DataVndbReleasePagesForm(LanzaTareaMixin, forms.Form):
    """Importa lanzamientos por páginas del catálogo de VNDB: 100 filas por página, desde la página del cursor.
    Cada página es UNA petición a VNDB (100 filas es su máximo); el tope por tanda es su presupuesto antes del 429."""

    slug = 'paginas'                      # qué botón lo envió (action=) y prefijo de sus campos
    titulo = _('Por páginas')
    boton = _('Importar')
    success_url = 'panel:data-vndb-release_list'
    success_label = _('datos crudos · sin procesar')

    MAX_PAGINAS = 200
    CURSOR = 'lanzamiento-pagina'          # la fila de system.ImportCursor que dice por dónde va el barrido de lanzamientos

    desde_pagina = forms.IntegerField(
        label=_('Desde página'),
        required=True, min_value=1, max_value=99999,
        widget=forms.NumberInput(attrs={
            'aria-label': _('Desde página'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': 99999, 'required': 'required',
        }),
        error_messages={'required': _('Escribe la página inicial.'),
                        'invalid': _('La página tiene que ser un número entero.'),
                        'min_value': _('Las páginas empiezan en 1.'),
                        'max_value': _('El catálogo de VNDB no llega a esa página.')},
    )
    paginas = forms.IntegerField(
        label=_('Cuántas páginas'),
        help_text=_('Una petición por página, con la espera que marca VNDB. 10 páginas son 1.000 lanzamientos.'),
        required=False, min_value=1, max_value=MAX_PAGINAS, initial=10,
        widget=forms.NumberInput(attrs={
            'placeholder': '10', 'aria-label': _('Cuántas páginas'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': MAX_PAGINAS,
        }),
        error_messages={'invalid': _('Tiene que ser un número entero.'),
                        'min_value': _('Al menos una página.'),
                        'max_value': _('Máximo %(limit_value)s páginas por tanda.')},
    )
    todo = forms.BooleanField(
        label=_('Traerlas todas'), required=False, initial=False,
        help_text=_('Sigue página a página hasta que VNDB diga que no quedan más lanzamientos. Cancelable desde Tareas.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Traerlas todas'), 'data-bloquea': 'paginas'}),
    )
    procesar = forms.BooleanField(
        label=_('Procesar al bajar'), required=False, initial=False,
        help_text=_('Convierte cada página en lanzamientos nada más bajarla. Sin marcar, solo se deja el crudo y se '
                    'procesa luego con «Procesar pendientes» desde la lista de datos.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Procesar al bajar')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import siguiente
        self.siguiente_pagina = siguiente('vndb', self.CURSOR)
        if not self.is_bound:
            self.fields['desde_pagina'].initial = self.siguiente_pagina
        self.fields['desde_pagina'].help_text = _(
            'El catálogo entero de lanzamientos, 100 por página. El cursor va por la %(pag)s; avanza página a página, '
            'así que si cancelas sigue donde quedó.') % {'pag': self.siguiente_pagina}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('todo'):
            cleaned['paginas'] = 0                    # 0 = sin tope: hasta que VNDB diga que no quedan más
            self.errors.pop('paginas', None)
        elif not cleaned.get('paginas'):
            self.add_error('paginas', _('Escribe cuántas páginas o marca «Traerlas todas».'))
        return cleaned

    def tarea(self, vista):
        """Dos barridos a la vez se pisan el presupuesto de VNDB (429), así que si ya hay uno no se apila otro."""
        from django.contrib import messages
        from core.shared.views.imports import tarea_en_curso
        en_curso = tarea_en_curso(vista.task_barrido)
        if en_curso:
            messages.warning(vista.request, _('Ya hay un barrido %(estado)s. Espera a que termine o cancélalo '
                                              'desde Tareas.') % {'estado': en_curso})
            return None
        return (vista.task_barrido,
                ('lanzamiento', self.cleaned_data['desde_pagina'], self.cleaned_data['paginas']),
                {'procesar': self.cleaned_data['procesar']})

    def resumen(self, vista):
        paginas = self.cleaned_data['paginas']
        return _('Barrido de lanzamientos (%(modo)s): %(cuantas)s de 100 desde la página %(desde)s') % {
            'modo': _('importar y procesar') if self.cleaned_data['procesar'] else _('importar al crudo'),
            'cuantas': _('TODAS las páginas') if not paginas else _('%(n)s página(s)') % {'n': paginas},
            'desde': self.cleaned_data['desde_pagina']}


class DataVndbReleaseSearchForm(LanzaTareaMixin, forms.Form):
    """Busca LANZAMIENTOS en VNDB por nombre. Solo es la caja: manda por GET a su vista de resultados
    (`resultados_url`), donde se marcan los que se quieran y se importan al crudo con la tarea de lista de ids."""

    TIPO = 'lanzamiento'
    slug = 'buscar'
    titulo = _('Por nombre')
    boton = _('Buscar')
    resultados_url = 'panel:vndb-release-buscar'
    success_url = 'panel:data-vndb-release_list'
    success_label = _('datos crudos · sin procesar')

    q = forms.CharField(
        label=_('Título del lanzamiento'),
        help_text=_('Busca en VNDB y elige cuál importar: no hace falta saber el id.'),
        required=False, min_length=2, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'type': 'search', 'aria-label': _('Título del lanzamiento'), 'autocomplete': 'off',
            'placeholder': _('Ever17 PS2'),
        }),
        error_messages={'min_length': _('Escribe al menos dos letras para buscar.')},
    )

    def tarea_lista(self, vista, ids):
        """Los ids marcados en los resultados → la tarea de lista del tipo (descarga al crudo)."""
        return vista.task_ids, (self.TIPO, list(ids)), {}


class DevelopmentEngineForm(FormBaseCategory):
    """Motor de desarrollo: Ren'Py, Unity, RPG Maker, Godot…"""

    class Meta:
        model = DevelopmentEngine
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un motor con este nombre.')


class GameForm(forms.ModelForm):
    """El juego / visual novel. Los desplegables NO vuelcan sus tablas: buscan en el
    servidor por AJAX contra `<entidad>/select/` (ver `core/shared/forms/widgets.py`)."""

    class Meta:
        model = Game
        fields = ['title', 'version', 'release_date', 'synopsis', 'background', 'status',
                  'type', 'engine', 'mediums', 'platforms', 'developers', 'publishers',
                  'languages', 'genres', 'is_active']

    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título principal del juego.'),
        required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 255, 'required': 'required',
            'title': _('Título principal del juego.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 255 caracteres.')},
    )
    version = forms.CharField(
        label=_('Versión'),
        help_text=_('Versión publicada (0.0.1, 1.2 final…).'),
        required=False, max_length=50, strip=True, initial='0.0.1',
        widget=forms.TextInput(attrs={
            'placeholder': _('0.0.1'), 'aria-label': _('Versión'), 'autocomplete': 'off',
            'maxlength': 50, 'title': _('Versión publicada (0.0.1, 1.2 final…).'),
        }),
        error_messages={'max_length': _('Máximo 50 caracteres.')},
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
    synopsis = forms.CharField(
        label=_('Sinopsis'),
        help_text=_('Resumen de la trama (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Sinopsis'), 'aria-label': _('Sinopsis'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Resumen de la trama (opcional).'),
        }),
    )
    background = forms.CharField(
        label=_('Trasfondo'),
        help_text=_('Contexto, notas de desarrollo, curiosidades (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Trasfondo'), 'aria-label': _('Trasfondo'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Contexto, notas de desarrollo, curiosidades (opcional).'),
        }),
    )
    status = forms.ChoiceField(
        label=_('Estado'), required=True, choices=GameStatus.choices,
        widget=forms.Select(attrs={'aria-label': _('Estado'), 'title': _('En desarrollo, completado, abandonado, en pausa.')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    type = forms.ChoiceField(
        label=_('Tipo'), required=True, choices=GameType.choices,
        widget=forms.Select(attrs={'aria-label': _('Tipo'), 'title': _('Novela visual, juego o colección.')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    engine = forms.ModelMultipleChoiceField(
        label=_('Motores'),
        help_text=_("Ren'Py, Unity, RPG Maker… Puedes elegir varios."),
        required=False, queryset=DevelopmentEngine.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:game-engine_select', attrs={
            'aria-label': _('Motores'), 'title': _("Ren'Py, Unity, RPG Maker… Puedes elegir varios."),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    mediums = forms.ModelMultipleChoiceField(
        label=_('Medios'),
        help_text=_('En qué soporte se distribuye. Puedes elegir varios.'),
        required=False, queryset=Medium.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:game-medium_select', attrs={
            'aria-label': _('Medios'), 'title': _('En qué soporte se distribuye. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    platforms = forms.ModelMultipleChoiceField(
        label=_('Plataformas'),
        help_text=_('Windows, Linux, Android… Puedes elegir varias.'),
        required=False, queryset=Platform.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:game-platform_select', attrs={
            'aria-label': _('Plataformas'), 'title': _('Windows, Linux, Android… Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    developers = forms.ModelMultipleChoiceField(
        label=_('Desarrolladores'),
        help_text=_('Quién lo desarrolló. Puedes elegir varios.'),
        required=False, queryset=Creator.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:creator_select', attrs={
            'aria-label': _('Desarrolladores'), 'title': _('Quién lo desarrolló. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    publishers = forms.ModelMultipleChoiceField(
        label=_('Editoras'),
        help_text=_('Quién lo publica o distribuye. Puedes elegir varias.'),
        required=False, queryset=Creator.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:creator_select', attrs={
            'aria-label': _('Editoras'), 'title': _('Quién lo publica o distribuye. Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    languages = forms.ModelMultipleChoiceField(
        label=_('Idiomas'),
        help_text=_('Idiomas en los que está disponible. Puedes elegir varios.'),
        required=False, queryset=Language.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:language_select', attrs={
            'aria-label': _('Idiomas'),
            'title': _('Idiomas en los que está disponible. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    genres = forms.ModelMultipleChoiceField(
        label=_('Géneros'),
        help_text=_('Puedes elegir varios. Escribe para buscar.'),
        required=False, queryset=Genre.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:game-genre_select', attrs={
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

    def clean_title(self):
        """El `slug` de Game NO es único (hay remakes y homónimos), así que aquí solo
        normalizamos: no bloqueamos títulos repetidos."""
        return ' '.join((self.cleaned_data.get('title') or '').split())

    def clean_version(self):
        return ' '.join((self.cleaned_data.get('version') or '').split())

    def clean_synopsis(self):
        return (self.cleaned_data.get('synopsis') or '').strip()

    def clean_background(self):
        return (self.cleaned_data.get('background') or '').strip()


class GameImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = GameImage
        fields = ['game', 'order', 'image', 'image_url', 'is_active']

    game = forms.ModelChoiceField(
        label=_('Juego'),
        help_text=_('Juego al que pertenece la imagen. Escribe para buscar.'),
        required=True, queryset=Game.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:game_select', attrs={
            'aria-label': _('Juego'), 'required': 'required',
            'title': _('Juego al que pertenece la imagen. Escribe para buscar.'),
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


class GameLinkForm(forms.ModelForm):
    """Enlace externo de un juego: itch.io, Steam, descarga oficial…
    El modelo exige que (juego, fuente, id externo) sea único: se comprueba en `clean()`."""

    class Meta:
        model = GameLink
        fields = ['game', 'source', 'external_id', 'url', 'is_active']

    game = forms.ModelChoiceField(
        label=_('Juego'),
        help_text=_('De qué juego es el enlace. Escribe para buscar.'),
        required=True, queryset=Game.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:game_select', attrs={
            'aria-label': _('Juego'), 'required': 'required',
            'title': _('De qué juego es el enlace. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    source = forms.ModelChoiceField(
        label=_('Fuente'),
        help_text=_('Plataforma del enlace (itch.io, Steam…). Escribe para buscar.'),
        required=True, queryset=ExternalSource.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:external-source_select', attrs={
            'aria-label': _('Fuente'), 'required': 'required',
            'title': _('Plataforma del enlace (itch.io, Steam…). Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    external_id = forms.CharField(
        label=_('Id externo'),
        help_text=_('Identificador del juego en esa plataforma (opcional).'),
        required=False, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('mi-juego'), 'aria-label': _('Id externo'), 'autocomplete': 'off',
            'maxlength': 500, 'title': _('Identificador del juego en esa plataforma (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 500 caracteres.')},
    )
    url = forms.CharField(
        label=_('URL'),
        help_text=_('Dirección completa del enlace, con https:// (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('https://autor.itch.io/mi-juego'), 'aria-label': _('URL'),
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
        """`unique_together = (game, source, external_id)` en el modelo."""
        cleaned = super().clean()
        game = cleaned.get('game')
        source = cleaned.get('source')
        if game and source:
            duplicados = GameLink.objects.filter(
                game=game, source=source, external_id=cleaned.get('external_id') or '')
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('external_id', 'Este juego ya tiene ese enlace en esa plataforma.')
        return cleaned


class GameTitleForm(forms.ModelForm):
    """Título alternativo de un juego, por idioma. El modelo exige que
    (juego, idioma, título) sea único: se comprueba en `clean()`."""

    class Meta:
        model = GameTitle
        fields = ['game', 'title_lang', 'title', 'is_active']

    game = forms.ModelChoiceField(
        label=_('Juego'),
        help_text=_('Juego al que pertenece el título. Escribe para buscar.'),
        required=True, queryset=Game.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:game_select', attrs={
            'aria-label': _('Juego'), 'required': 'required',
            'title': _('Juego al que pertenece el título. Escribe para buscar.'),
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
        """`unique_together = (game, title_lang, title)` en el modelo."""
        cleaned = super().clean()
        game = cleaned.get('game')
        title_lang = cleaned.get('title_lang')
        title = cleaned.get('title')
        if game and title_lang and title:
            duplicados = GameTitle.objects.filter(game=game, title_lang=title_lang, title=title)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('title', 'Este juego ya tiene ese título en ese idioma.')
        return cleaned


class GenreAliasForm(forms.ModelForm):
    """alias de género: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = GenreAlias
        fields = ['name', 'name_esp', 'is_active', 'genre']


class GenreForm(FormBaseCategory):
    """Género de juego. `explicit` marca los géneros +18 (filtran el catálogo público)."""

    class Meta:
        model = Genre
        fields = ['name', 'name_esp', 'description', 'explicit', 'image', 'is_active']

    duplicate_message = _('Ya existe un género de juego con este nombre.')

    explicit = forms.BooleanField(
        label=_('Explícito (+18)'),
        help_text=_('Marca los géneros para adultos. Filtra el catálogo público.'),
        required=False, initial=False,         # el modelo trae default=False
        widget=forms.CheckboxInput(attrs={'aria-label': _('Explícito (+18)')}),
    )


class MediumForm(FormBaseCategory):
    """Medio de distribución del juego: descarga digital, DVD, físico…"""

    class Meta:
        model = Medium
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un medio con este nombre.')


class PlatformForm(FormBaseCategory):
    """Plataforma donde corre el juego: Windows, Linux, macOS, Android…"""

    class Meta:
        model = Platform
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe una plataforma con este nombre.')


class ReleaseForm(forms.ModelForm):
    """Lanzamiento de un juego: edición, fecha y banderas. Plataformas, idiomas y editoras las pone el importador."""

    class Meta:
        model = Release
        fields = ['game', 'title', 'alttitle', 'released', 'minage', 'official', 'patch', 'freeware', 'is_active']

    game = forms.ModelChoiceField(
        label=_('Juego'), required=True, queryset=Game.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:game_select', attrs={'aria-label': _('Juego'), 'required': 'required'}),
        error_messages={'required': _('Elige el juego.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )
    title = forms.CharField(
        label=_('Título'), required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={'placeholder': _('Título de la edición'), 'aria-label': _('Título'), 'autocomplete': 'off', 'maxlength': 255, 'required': 'required'}),
        error_messages={'required': _('Este campo es obligatorio.'), 'max_length': _('Máximo 255 caracteres.')},
    )
    alttitle = forms.CharField(
        label=_('Título alternativo'), required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={'placeholder': _('Título original'), 'aria-label': _('Título alternativo'), 'maxlength': 255}),
    )
    released = forms.DateField(
        label=_('Fecha'), required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date', 'aria-label': _('Fecha')}, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha no válida (AAAA-MM-DD).')},
    )
    minage = forms.IntegerField(
        label=_('Edad mínima'), required=False, min_value=0, max_value=21,
        widget=forms.NumberInput(attrs={'placeholder': '18', 'aria-label': _('Edad mínima'), 'inputmode': 'numeric', 'step': 1, 'min': 0, 'max': 21}),
        error_messages={'invalid': _('Tiene que ser un número entero.'), 'min_value': _('No puede ser negativa.'), 'max_value': _('Máximo 21.')},
    )
    official = forms.BooleanField(label=_('Oficial'), required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Oficial')}))
    patch = forms.BooleanField(label=_('Parche'), required=False, initial=False, widget=forms.CheckboxInput(attrs={'aria-label': _('Parche')}))
    freeware = forms.BooleanField(label=_('Gratuito'), required=False, initial=False, widget=forms.CheckboxInput(attrs={'aria-label': _('Gratuito')}))
    is_active = forms.BooleanField(label=_('Activo'), required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}))


class ReleaseImageForm(forms.ModelForm):
    """imagen de lanzamiento: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = ReleaseImage
        fields = ['image_url', 'image_downloaded', 'is_active', 'release', 'image', 'label']


class TagAliasForm(forms.ModelForm):
    """alias de etiqueta: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = TagAlias
        fields = ['name', 'name_esp', 'is_active', 'tag']


class TagFileForm(forms.Form):
    """El ARCHIVO del dump de tags de VNDB: un solo campo, el archivo. No toca la base: solo comprueba
    que venga algo, que sea `.json` o `.json.gz` y que no esté vacío; leerlo y aplicarlo es de
    `services/vndb_tags.py`. Se llama `archivo` porque así lo recoge la pantalla de carga de tags."""

    titulo = _('Desde un archivo')
    boton = _('Subir')

    archivo = forms.FileField(
        label=_('Archivo del dump'),
        help_text=_('El dump de tags de VNDB: .json o .json.gz. No puede estar vacío.'),
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'aria-label': _('Archivo del dump'), 'accept': '.json,.gz,application/json,application/gzip',
            'title': _('El dump de tags de VNDB: .json o .json.gz.'),
        }),
        error_messages={'required': _('Elige el archivo del dump.'),
                        'empty': _('El archivo está vacío.')},
    )

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not isinstance(archivo, UploadedFile):
            return archivo
        nombre = (archivo.name or '').lower()
        if not (nombre.endswith('.json') or nombre.endswith('.gz')):
            ext = ('.' + nombre.rsplit('.', 1)[-1]) if '.' in nombre else ''
            raise forms.ValidationError(
                'Formato no permitido (%s). Usa .json o .json.gz.' % (ext or 'sin extensión'))
        if not archivo.size:
            raise forms.ValidationError('El archivo está vacío.')
        return archivo


class TagForm(FormBaseCategory):
    """etiqueta: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = Tag
        fields = ['name', 'name_esp', 'description', 'image', 'is_active', 'vndb_id']

    duplicate_message = _('Ya existe una etiqueta con este nombre.')


class GameLogForm(forms.ModelForm):
    """Log de juegos: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = GameLog
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


# ==============================================================================
# Carga de TAGS desde el dump oficial de VNDB (dos pasos: leer → confirmar)
# ==============================================================================


class VndbDumpForm(FormBaseLoadFile):
    """El formulario de «cargar un dump de VNDB»: subir el archivo o releer el último de dump/. El hijo solo
    dice de qué TIPO es (la clave de `vndb_dump.TIPOS`); lo demás es igual para los cuatro.

        class VndbGameDumpForm(VndbDumpForm):
            TIPO = "game"
    """
    EXTENSIONES = list(DUMP_EXTENSIONS)
    MAX_MB = DUMP_MAX_MB                      # un dump de la tabla entera pesa
    PASOS = ["subir", "ultimo"]       # sin «descargar»: el dump lo genera NUESTRO exportador
    TIPO = ""

    paso = forms.ChoiceField(choices=[(p, p) for p in PASOS], required=False, initial="subir")   # lo manda el botón

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["archivo"].label = _("Subir el dump")
        self.fields["archivo"].widget.attrs["id"] = "archivo"

    def clean(self):
        from apps.games.services import vndb_dump
        datos = super().clean()
        paso = datos.get("paso") or "subir"
        if paso == "subir" and not datos.get("archivo") and "archivo" not in self.errors:
            self.add_error("archivo", _("Elige el archivo del dump (.json o .json.gz), o relee el último."))
        if paso == "ultimo" and not vndb_dump.ultimo_dump(self.TIPO):
            self.add_error(None, _("No hay ningún dump de este tipo guardado en dump/ que releer."))
        return datos

    def ruta_dump(self):
        """La ruta del dump ya en dump/: guarda el subido o devuelve el último."""
        from apps.games.services import vndb_dump
        if (self.cleaned_data.get("paso") or "subir") == "ultimo":
            return vndb_dump.ultimo_dump(self.TIPO)
        return vndb_dump.guardar_subido(self.TIPO, self.cleaned_data["archivo"])


class VndbCharacterDumpForm(VndbDumpForm):
    """Dump de PERSONAJES de VNDB: llena datos · Personaje (VNDB)."""
    TIPO = "character"


class VndbCreatorDumpForm(VndbDumpForm):
    """Dump de CREADORES de VNDB: llena datos · Creador (VNDB)."""
    TIPO = "creator"


class VndbGameDumpForm(VndbDumpForm):
    """Dump de JUEGOS de VNDB: llena datos · Juego (VNDB)."""
    TIPO = "game"


class VndbReleaseDumpForm(VndbDumpForm):
    """Dump de LANZAMIENTOS de VNDB: llena datos · Lanzamiento (VNDB)."""
    TIPO = "release"


class VNDBTagsDumpForm(FormBaseLoadFile):
    """El formulario de «Cargar tags de VNDB»: de dónde sale el dump. Tres vías, una por botón (`paso`): subir el
    archivo (.json o .json.gz de verdad: se mira la cabecera), descargarlo de VNDB, o releer el último de dump/."""
    EXTENSIONES = list(DUMP_EXTENSIONS)
    MAX_MB = 100
    PASOS = ["subir", "descargar", "ultimo"]

    paso = forms.ChoiceField(choices=[(p, p) for p in PASOS], required=False, initial="subir")   # lo manda el botón

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["archivo"].label = _("Subir el dump")
        self.fields["archivo"].widget.attrs["id"] = "archivo"

    def clean(self):
        from apps.games.services import vndb_tags
        datos = super().clean()
        paso = datos.get("paso") or "subir"
        if paso == "subir" and not datos.get("archivo") and "archivo" not in self.errors:
            self.add_error("archivo", _("Elige el archivo del dump (.json o .json.gz), o usa una de las otras vías."))
        if paso == "ultimo" and not vndb_tags.ultimo_dump():
            self.add_error(None, _("No hay ningún dump guardado en dump/ que releer."))
        return datos

    def ruta_dump(self):
        """La ruta del dump ya en dump/: guarda el subido, descarga de VNDB o devuelve el último (puede fallar por
        red o disco: lo captura la vista)."""
        from apps.games.services import vndb_tags
        paso = self.cleaned_data.get("paso") or "subir"
        if paso == "descargar":
            return vndb_tags.descargar()
        if paso == "ultimo":
            return vndb_tags.ultimo_dump()
        return vndb_tags.guardar_subido(self.cleaned_data["archivo"])


class DataVndbCharacterProcessForm(ProcesarLoteForm):
    TIPO = 'personaje'
    PENDIENTES = 'apps.games.services.vndb.pendientes'
    success_url = 'panel:data-vndb-character_list'



class DataVndbCreatorProcessForm(ProcesarLoteForm):
    TIPO = 'creador'
    PENDIENTES = 'apps.games.services.vndb.pendientes'
    success_url = 'panel:data-vndb-creator_list'



class DataVndbGameProcessForm(ProcesarLoteForm):
    TIPO = 'juego'
    PENDIENTES = 'apps.games.services.vndb.pendientes'
    success_url = 'panel:data-vndb-game_list'



class DataVndbReleaseProcessForm(ProcesarLoteForm):
    TIPO = 'lanzamiento'
    PENDIENTES = 'apps.games.services.vndb.pendientes'
    success_url = 'panel:data-vndb-release_list'


class CharacterImageDownloadForm(DescargarImagenesForm):
    TIPO = 'games.CharacterImage'
    success_url = 'panel:game-character-image_list'



class GameImageDownloadForm(DescargarImagenesForm):
    TIPO = 'games.GameImage'
    success_url = 'panel:game-image_list'



class ReleaseImageDownloadForm(DescargarImagenesForm):
    TIPO = 'games.ReleaseImage'
    success_url = 'panel:game-release-image_list'


class CharacterImageRetryForm(ReintentarMuertasForm):
    TIPO = 'games.CharacterImage'
    success_url = 'panel:game-character-image_download'



class GameImageRetryForm(ReintentarMuertasForm):
    TIPO = 'games.GameImage'
    success_url = 'panel:game-image_download'



class ReleaseImageRetryForm(ReintentarMuertasForm):
    TIPO = 'games.ReleaseImage'
    success_url = 'panel:game-release-image_download'

