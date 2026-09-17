"""Formularios del panel para `otaku` — UNO POR MODELO, AUTÓNOMOS.

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

Sí, hay mucha repetición entre formularios parecidos. Es a propósito: se lee y se
cambia uno sin tocar los demás.

OJO con Anime y Manga: su clave única es `mal_id`, NO el slug (dos entradas pueden
compartir título romanizado). Por eso sus formularios no comprueban duplicados por
título — el `save()` del modelo acuña un `mal_id` negativo para las entradas locales.

`OtakuLog` y las tablas `Data*` no tienen formulario a propósito:
son registro y staging del importador, no se escriben a mano.
"""
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import Language, RelationType
from apps.companies.forms import CompanyForm
from apps.companies.models import Company
from apps.music.models import Artist
from apps.otaku.models import Anime, AnimeCharacter, AnimeImage, AnimeSong, AnimeStaff, AnimeTitle, Character, CharacterImage, CharacterNickname, CharacterVoice, CompanyMAL, DataAnilistAnime, DataAnilistCharacter, DataAnilistManga, DataAnilistPerson, DataMalAnime, DataMalAnimeCharacter, DataMalAnimePicture, DataMalAnimeStaff, DataMalCharacter, DataMalCharacterPicture, DataMalManga, DataMalMangaCharacter, DataMalMangaPicture, DataMalPerson, DataMalPersonPicture, Demographic, DemographicAlias, Genre, GenreAlias, Manga, MangaAuthor, MangaCharacter, MangaImage, MangaTitle, OtakuLog, PersonMAL, Relation, Role, Source, Status, Theme, ThemeAlias, Type, Year
from apps.people.forms import PersonForm
from apps.people.models import Person
from core.shared.forms.base import FormBaseCategory, FormBaseLoadFile
from core.shared.forms.widgets import AjaxSelect, AjaxSelectMultiple
from core.shared.models.choices import AnimeSongType, LogLevel, MalCompanyKind, MalRating, MalSeason
from core.shared.views.imports import DescargarImagenesForm, LanzaTareaMixin, MAX_IDS_POR_LOTE, ProcesarLoteForm, ReintentarMuertasForm
from core.utils.constants import DUMP_EXTENSIONS, DUMP_MAX_MB, IMAGE_ACCEPT, IMAGE_EXTENSIONS, IMAGE_FORMATS, IMAGE_HINT, IMAGE_MAX_MB, MB


class AnilistIdForm(LanzaTareaMixin, forms.Form):
    """«Por id» de AniList: UN id al crudo, con la consulta completa. El tipo y la lista de destino los fija la subclase."""
    slug = 'uno'
    titulo = _('Por id')
    boton = _('Importar')
    success_label = _('datos crudos · sin procesar')
    TIPO = ''
    success_url = ''

    anilist_id = forms.IntegerField(
        label=_('AniList id'),
        help_text=_('El número de su URL en anilist.co.'),
        required=True, min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': _('1'), 'aria-label': _('AniList id'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1, 'required': 'required',
        }),
        error_messages={'required': _('Escribe el id que quieres traer.'),
                        'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de AniList empiezan en 1.')},
    )

    def tarea(self, vista):
        return vista.task_uno, (self.TIPO, self.cleaned_data['anilist_id']), {}

    def resumen(self, vista):
        return _('Importar %(que)s #%(id)s (AniList)') % {'que': vista.label, 'id': self.cleaned_data['anilist_id']}


class AnilistPagesForm(LanzaTareaMixin, forms.Form):
    """«Por páginas» de AniList: el catálogo ordenado por id, 50 por página, desde la página del cursor."""
    slug = 'paginas'
    titulo = _('Por páginas')
    boton = _('Importar')
    success_label = _('datos crudos · sin procesar')
    TIPO = ''
    success_url = ''
    MAX_PAGINAS = 500

    desde_pagina = forms.IntegerField(
        label=_('Desde página'), required=True, min_value=1, max_value=999999,
        widget=forms.NumberInput(attrs={'aria-label': _('Desde página'), 'autocomplete': 'off', 'inputmode': 'numeric',
                                        'step': 1, 'min': 1, 'required': 'required'}),
        error_messages={'required': _('Escribe la página inicial.'), 'invalid': _('La página tiene que ser un número entero.'),
                        'min_value': _('Las páginas empiezan en 1.')},
    )
    paginas = forms.IntegerField(
        label=_('Cuántas páginas'),
        help_text=_('Una petición por página (50 filas), con la espera que pide AniList: 10 páginas son 500 filas.'),
        required=False, min_value=1, max_value=MAX_PAGINAS, initial=10,
        widget=forms.NumberInput(attrs={'placeholder': '10', 'aria-label': _('Cuántas páginas'), 'autocomplete': 'off',
                                        'inputmode': 'numeric', 'step': 1, 'min': 1, 'max': MAX_PAGINAS}),
        error_messages={'invalid': _('Tiene que ser un número entero.'), 'min_value': _('Al menos una página.'),
                        'max_value': _('Máximo %(limit_value)s páginas por tanda.')},
    )
    todo = forms.BooleanField(
        label=_('Traerlas todas'), required=False, initial=False,
        help_text=_('Sigue página a página hasta que AniList diga que no quedan más. Cancelable desde Tareas.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Traerlas todas'), 'data-bloquea': 'paginas'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import siguiente
        self.siguiente_pagina = siguiente('anilist', f'{self.TIPO}-pagina')
        if not self.is_bound:
            self.fields['desde_pagina'].initial = self.siguiente_pagina
        self.fields['desde_pagina'].help_text = _(
            'El catálogo entero, 50 por página y ordenado por id. El cursor va por la %(pag)s y avanza página a página: '
            'si cancelas, sigue donde quedó.') % {'pag': self.siguiente_pagina}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('todo'):
            cleaned['paginas'] = 0
            self.errors.pop('paginas', None)
        elif not cleaned.get('paginas'):
            self.add_error('paginas', _('Escribe cuántas páginas o marca «Traerlas todas».'))
        return cleaned

    def tarea(self, vista):
        """Dos barridos a la vez se pisan el límite por minuto de AniList (429): si ya hay uno, no se apila otro."""
        from django.contrib import messages
        from core.shared.views.imports import tarea_en_curso
        en_curso = tarea_en_curso(vista.task_barrido)
        if en_curso:
            messages.warning(vista.request, _('Ya hay un barrido de AniList %(estado)s. Espera a que termine o '
                                              'cancélalo desde Tareas.') % {'estado': en_curso})
            return None
        return vista.task_barrido, (self.TIPO, self.cleaned_data['desde_pagina'], self.cleaned_data['paginas']), {}

    def resumen(self, vista):
        paginas = self.cleaned_data['paginas']
        return _('Barrido de %(que)s (AniList): %(cuantas)s desde la página %(desde)s') % {
            'que': vista.label, 'desde': self.cleaned_data['desde_pagina'],
            'cuantas': _('TODAS las páginas') if not paginas else _('%(n)s página(s)') % {'n': paginas}}


class AnilistRangeForm(LanzaTareaMixin, forms.Form):
    """«Por rango de ids» de AniList: [inicio, fin] de a 50 por petición; lo ya descargado se salta."""
    slug = 'rango'
    titulo = _('Por rango de ids')
    boton = _('Importar')
    success_label = _('datos crudos · sin procesar')
    TIPO = ''
    success_url = ''
    MAX_IDS = 5000

    inicio = forms.IntegerField(
        label=_('Desde id'), required=True, min_value=1,
        widget=forms.NumberInput(attrs={'aria-label': _('Desde id'), 'autocomplete': 'off', 'inputmode': 'numeric',
                                        'step': 1, 'min': 1, 'required': 'required'}),
        error_messages={'required': _('Escribe el id inicial.'), 'invalid': _('El id tiene que ser un número entero.'),
                        'min_value': _('Los ids de AniList empiezan en 1.')},
    )
    fin = forms.IntegerField(
        label=_('Hasta id'), required=False, min_value=1,
        widget=forms.NumberInput(attrs={'aria-label': _('Hasta id'), 'autocomplete': 'off', 'inputmode': 'numeric',
                                        'step': 1, 'min': 1}),
        error_messages={'invalid': _('El id tiene que ser un número entero.'), 'min_value': _('Los ids de AniList empiezan en 1.')},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.shared.tasks.cursor import cantidad_de, siguiente
        self.siguiente = siguiente('anilist', self.TIPO)
        self.cantidad = cantidad_de('anilist', self.TIPO)
        if not self.is_bound:
            self.fields['inicio'].initial = self.siguiente
            self.fields['fin'].initial = self.siguiente + self.cantidad - 1
        self.fields['inicio'].help_text = _('Primer id. Precargado con #%(sig)s, por donde va el cursor; los ya descargados se saltan.') % {'sig': self.siguiente}
        self.fields['fin'].help_text = _('Último id. Vacío = inicio + %(cant)s (la cantidad del cursor). Máximo %(max)s ids por tanda.') % {
            'cant': self.cantidad, 'max': self.MAX_IDS}

    def clean(self):
        cleaned = super().clean()
        inicio, fin = cleaned.get('inicio'), cleaned.get('fin')
        if inicio is None:
            return cleaned
        if fin is None:
            fin = cleaned['fin'] = inicio + self.cantidad - 1
        if fin < inicio:
            self.add_error('fin', _('El id final no puede ser menor que el inicial.'))
        elif fin - inicio + 1 > self.MAX_IDS:
            self.add_error('fin', _('El rango pide %(n)s ids; el máximo son %(max)s por tanda.') % {'n': fin - inicio + 1, 'max': self.MAX_IDS})
        return cleaned

    def tarea(self, vista):
        """Baja el rango; si continúa desde el cursor, el cursor avanza."""
        from django.contrib import messages
        from core.shared.tasks.cursor import avanzar_si_contiguo
        inicio, fin = self.cleaned_data['inicio'], self.cleaned_data['fin']
        if avanzar_si_contiguo('anilist', self.TIPO, inicio, fin):
            messages.info(vista.request, _('El cursor de AniList avanza a #%(sig)s.') % {'sig': fin + 1})
        return vista.task_rango, (self.TIPO, inicio, fin), {}

    def resumen(self, vista):
        return _('Importar %(que)s [%(a)s-%(b)s] (AniList)') % {'que': vista.label, 'a': self.cleaned_data['inicio'], 'b': self.cleaned_data['fin']}


class AnimeCharacterForm(forms.ModelForm):
    """Aparición de un personaje en un anime, con su rol. El modelo exige que
    (anime, personaje, rol) sea único: se comprueba en `clean()`."""

    class Meta:
        model = AnimeCharacter
        fields = ['anime', 'character', 'role', 'is_active']

    anime = forms.ModelChoiceField(
        label=_('Anime'),
        help_text=_('Anime en el que aparece. Escribe para buscar.'),
        required=True, queryset=Anime.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:anime_select', attrs={
            'aria-label': _('Anime'), 'required': 'required',
            'title': _('Anime en el que aparece. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    character = forms.ModelChoiceField(
        label=_('Personaje'),
        help_text=_('Qué personaje aparece. Escribe para buscar.'),
        required=True, queryset=Character.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:character_select', attrs={
            'aria-label': _('Personaje'), 'required': 'required',
            'title': _('Qué personaje aparece. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.ModelChoiceField(
        label=_('Rol'),
        help_text=_('Principal, secundario… (opcional).'),
        required=False, queryset=Role.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:otaku-role_select', attrs={
            'aria-label': _('Rol'), 'title': _('Principal, secundario… (opcional).'),
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
        """`unique_together = (anime, character, role)` en el modelo."""
        cleaned = super().clean()
        anime = cleaned.get('anime')
        character = cleaned.get('character')
        if anime and character:
            duplicados = AnimeCharacter.objects.filter(
                anime=anime, character=character, role=cleaned.get('role'))
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, 'Ese personaje ya está registrado con ese rol en el anime.')
        return cleaned


class AnimeForm(forms.ModelForm):
    """El anime en sí. Los desplegables NO vuelcan sus tablas: buscan en el servidor
    por AJAX contra `<entidad>/select/` (ver `core/shared/forms/widgets.py`)."""

    class Meta:
        model = Anime
        fields = ['title', 'title_eng', 'title_jap', 'synopsis', 'anime_type', 'source',
                  'rating', 'status', 'season', 'year', 'episodes', 'studios', 'producers',
                  'licensors', 'genres', 'themes', 'demographics', 'from_date', 'to_date',
                  'is_active']

    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título principal (normalmente el romanizado).'),
        required=True, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 500, 'required': 'required',
            'title': _('Título principal (normalmente el romanizado).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 500 caracteres.')},
    )
    title_eng = forms.CharField(
        label=_('Título (EN)'),
        help_text=_('Título en inglés (opcional).'),
        required=False, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título (EN)'), 'aria-label': _('Título (EN)'), 'autocomplete': 'off',
            'maxlength': 500, 'title': _('Título en inglés (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 500 caracteres.')},
    )
    title_jap = forms.CharField(
        label=_('Título (JP)'),
        help_text=_('Título en japonés/kanji (opcional).'),
        required=False, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título (JP)'), 'aria-label': _('Título (JP)'), 'autocomplete': 'off',
            'maxlength': 500, 'title': _('Título en japonés/kanji (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 500 caracteres.')},
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
    anime_type = forms.ModelChoiceField(
        label=_('Tipo'),
        help_text=_('TV, película, OVA, especial… Escribe para buscar.'),
        required=False, queryset=Type.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:type_select', attrs={
            'aria-label': _('Tipo'), 'title': _('TV, película, OVA, especial… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    source = forms.ModelChoiceField(
        label=_('Fuente'),
        help_text=_('De dónde se adapta (manga, novela ligera, original…).'),
        required=False, queryset=Source.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:source_select', attrs={
            'aria-label': _('Fuente'),
            'title': _('De dónde se adapta (manga, novela ligera, original…).'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    rating = forms.ChoiceField(
        label=_('Clasificación'), required=False, choices=[('', '—')] + list(MalRating.choices),
        widget=forms.Select(attrs={'aria-label': _('Clasificación'), 'title': _('Clasificación por edad (MAL).')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    status = forms.ModelChoiceField(
        label=_('Estado'),
        help_text=_('En emisión, finalizado, anunciado… Escribe para buscar.'),
        required=False, queryset=Status.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:status_select', attrs={
            'aria-label': _('Estado'),
            'title': _('En emisión, finalizado, anunciado… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    season = forms.ChoiceField(
        label=_('Temporada'), required=False, choices=[('', '—')] + list(MalSeason.choices),
        widget=forms.Select(attrs={'aria-label': _('Temporada'), 'title': _('Si se deja vacía, se calcula por el mes de la fecha de estreno.')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    year = forms.IntegerField(
        label=_('Año'),
        help_text=_('Año de emisión (1888–2100).'),
        required=False, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('2015'), 'aria-label': _('Año'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'title': _('Año de emisión (1888–2100).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    episodes = forms.IntegerField(
        label=_('Episodios'),
        help_text=_('Número de episodios. 0 si aún no se sabe.'),
        required=False, min_value=0, initial=0,      # el modelo trae default=0
        widget=forms.NumberInput(attrs={
            'placeholder': _('12'), 'aria-label': _('Episodios'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 0,
            'title': _('Número de episodios. 0 si aún no se sabe.'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El valor mínimo es 0.')},
    )
    studios = forms.ModelMultipleChoiceField(
        label=_('Estudios'),
        help_text=_('Estudios de animación. Puedes elegir varios.'),
        required=False, queryset=Company.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:company_select', attrs={
            'aria-label': _('Estudios'), 'title': _('Estudios de animación. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    producers = forms.ModelMultipleChoiceField(
        label=_('Productoras'),
        help_text=_('Empresas que lo produjeron. Puedes elegir varias.'),
        required=False, queryset=Company.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:company_select', attrs={
            'aria-label': _('Productoras'),
            'title': _('Empresas que lo produjeron. Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    licensors = forms.ModelMultipleChoiceField(
        label=_('Licenciatarias'),
        help_text=_('Empresas que lo licenciaron fuera de Japón. Puedes elegir varias.'),
        required=False, queryset=Company.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:company_select', attrs={
            'aria-label': _('Licenciatarias'),
            'title': _('Empresas que lo licenciaron fuera de Japón. Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    genres = forms.ModelMultipleChoiceField(
        label=_('Géneros'),
        help_text=_('Puedes elegir varios. Escribe para buscar.'),
        required=False, queryset=Genre.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:genre_select', attrs={
            'aria-label': _('Géneros'), 'title': _('Puedes elegir varios. Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    themes = forms.ModelMultipleChoiceField(
        label=_('Temas'),
        help_text=_('Temas o etiquetas argumentales. Puedes elegir varios.'),
        required=False, queryset=Theme.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:theme_select', attrs={
            'aria-label': _('Temas'), 'title': _('Temas o etiquetas argumentales. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    demographics = forms.ModelMultipleChoiceField(
        label=_('Demografías'),
        help_text=_('Shōnen, seinen, josei… Puedes elegir varias.'),
        required=False, queryset=Demographic.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:demographic_select', attrs={
            'aria-label': _('Demografías'), 'title': _('Shōnen, seinen, josei… Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    from_date = forms.DateField(
        label=_('Desde'),
        help_text=_('Fecha de inicio de emisión. Formato dd-mm-aaaa.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Desde'), 'class': 'js-date',
            'autocomplete': 'off', 'title': _('Fecha de inicio de emisión. Formato dd-mm-aaaa.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    to_date = forms.DateField(
        label=_('Hasta'),
        help_text=_('Fecha de fin (si terminó). Formato dd-mm-aaaa.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Hasta'), 'class': 'js-date',
            'autocomplete': 'off', 'title': _('Fecha de fin (si terminó). Formato dd-mm-aaaa.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,          # el modelo trae default=True
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        """La clave única de Anime es `mal_id`, no el slug: dos entradas pueden
        compartir título romanizado. Aquí solo normalizamos."""
        return ' '.join((self.cleaned_data.get('title') or '').split())

    def clean_title_eng(self):
        return ' '.join((self.cleaned_data.get('title_eng') or '').split())

    def clean_title_jap(self):
        return ' '.join((self.cleaned_data.get('title_jap') or '').split())

    def clean_synopsis(self):
        return (self.cleaned_data.get('synopsis') or '').strip()

    def clean_episodes(self):
        episodes = self.cleaned_data.get('episodes')
        return 0 if episodes is None else episodes

    def clean(self):
        """Cruce de dos campos: no puede terminar de emitirse antes de empezar."""
        cleaned = super().clean()
        desde = cleaned.get('from_date')
        hasta = cleaned.get('to_date')
        if desde and hasta and hasta < desde:
            self.add_error('to_date', 'La fecha «hasta» no puede ser anterior a «desde».')
        return cleaned


class AnimeImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = AnimeImage
        fields = ['anime', 'order', 'image', 'image_url', 'is_active']

    anime = forms.ModelChoiceField(
        label=_('Anime'),
        help_text=_('Anime al que pertenece la imagen. Escribe para buscar.'),
        required=True, queryset=Anime.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:anime_select', attrs={
            'aria-label': _('Anime'), 'required': 'required',
            'title': _('Anime al que pertenece la imagen. Escribe para buscar.'),
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


class AnimeSongForm(forms.ModelForm):
    """Canción de un anime (opening, ending, insert…). El modelo exige que
    (anime, tipo, nº, título) sea único: se comprueba en `clean()`."""

    class Meta:
        model = AnimeSong
        fields = ['anime', 'type', 'song_id', 'artist_credit', 'artists', 'title',
                  'title_kanji', 'title_eng', 'is_active']

    anime = forms.ModelChoiceField(
        label=_('Anime'),
        help_text=_('Anime al que pertenece la canción. Escribe para buscar.'),
        required=True, queryset=Anime.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:anime_select', attrs={
            'aria-label': _('Anime'), 'required': 'required',
            'title': _('Anime al que pertenece la canción. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    type = forms.ChoiceField(
        label=_('Tipo'), choices=AnimeSongType.choices, initial=AnimeSongType.INSERT,
        widget=forms.Select(attrs={'aria-label': _('Tipo'), 'title': _('Opening, ending o insert song.')}),
        error_messages={'required': _('Este campo es obligatorio.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )
    song_id = forms.IntegerField(
        label=_('Nº'),
        help_text=_('Número dentro de su tipo (OP1, OP2…). 0 si no aplica.'),
        required=False, min_value=0, initial=0,      # el modelo trae default=0
        widget=forms.NumberInput(attrs={
            'placeholder': _('1'), 'aria-label': _('Nº'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 0,
            'title': _('Número dentro de su tipo (OP1, OP2…). 0 si no aplica.'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El valor mínimo es 0.')},
    )
    artist_credit = forms.CharField(
        label=_('Crédito del artista'),
        help_text=_('Como lo escribe la fuente, p. ej. «The Seatbelts feat. Mai Yamane». Se muestra si no hay artistas enlazados.'),
        required=False, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('The Seatbelts feat. Mai Yamane'), 'aria-label': _('Crédito del artista'), 'autocomplete': 'off',
            'maxlength': 500, 'title': _('Como lo escribe la fuente. Se muestra si no hay artistas enlazados.'),
        }),
        error_messages={'max_length': _('Máximo 500 caracteres.')},
    )
    artists = forms.ModelMultipleChoiceField(
        label=_('Artistas'),
        help_text=_('Quién la interpreta. Puedes elegir varios.'),
        required=False, queryset=Artist.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:artist_select', attrs={
            'aria-label': _('Artistas'), 'title': _('Quién la interpreta. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título de la canción, romanizado.'),
        required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 255, 'required': 'required',
            'title': _('Título de la canción, romanizado.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 255 caracteres.')},
    )
    title_kanji = forms.CharField(
        label=_('Título (kanji)'),
        help_text=_('Título en japonés (opcional).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título (kanji)'), 'aria-label': _('Título (kanji)'),
            'autocomplete': 'off', 'maxlength': 255,
            'title': _('Título en japonés (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    title_eng = forms.CharField(
        label=_('Título (EN)'),
        help_text=_('Título en inglés (opcional).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título (EN)'), 'aria-label': _('Título (EN)'),
            'autocomplete': 'off', 'maxlength': 255,
            'title': _('Título en inglés (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        return ' '.join((self.cleaned_data.get('title') or '').split())

    def clean_title_kanji(self):
        return ' '.join((self.cleaned_data.get('title_kanji') or '').split())

    def clean_title_eng(self):
        return ' '.join((self.cleaned_data.get('title_eng') or '').split())

    def clean_song_id(self):
        song_id = self.cleaned_data.get('song_id')
        return 0 if song_id is None else song_id

    def clean(self):
        """`unique_together = (anime, type, song_id, title)` en el modelo."""
        cleaned = super().clean()
        anime = cleaned.get('anime')
        title = cleaned.get('title')
        if anime and title:
            duplicadas = AnimeSong.objects.filter(
                anime=anime, type=cleaned.get('type'),
                song_id=cleaned.get('song_id') or 0, title=title)
            if self.instance.pk:
                duplicadas = duplicadas.exclude(pk=self.instance.pk)
            if duplicadas.exists():
                self.add_error('title', 'Este anime ya tiene esa canción con ese tipo y número.')
        return cleaned


class AnimeStaffForm(forms.ModelForm):
    """Equipo de un anime: una persona con un rol de producción. El modelo exige que
    (anime, persona, rol) sea único: se comprueba en `clean()`."""

    class Meta:
        model = AnimeStaff
        fields = ['anime', 'person', 'role', 'is_active']

    anime = forms.ModelChoiceField(
        label=_('Anime'),
        help_text=_('Anime en el que trabajó. Escribe para buscar.'),
        required=True, queryset=Anime.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:anime_select', attrs={
            'aria-label': _('Anime'), 'required': 'required',
            'title': _('Anime en el que trabajó. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('Quién trabajó en él. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('Quién trabajó en él. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.ModelChoiceField(
        label=_('Rol'),
        help_text=_('Dirección, guion, música… (opcional).'),
        required=False, queryset=Role.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:otaku-role_select', attrs={
            'aria-label': _('Rol'), 'title': _('Dirección, guion, música… (opcional).'),
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
        """`unique_together = (anime, person, role)` en el modelo."""
        cleaned = super().clean()
        anime = cleaned.get('anime')
        person = cleaned.get('person')
        if anime and person:
            duplicados = AnimeStaff.objects.filter(
                anime=anime, person=person, role=cleaned.get('role'))
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, 'Esa persona ya está registrada con ese rol en el anime.')
        return cleaned


class AnimeTitleForm(forms.ModelForm):
    """Título alternativo de un anime, por idioma. El modelo exige que
    (anime, idioma, título) sea único: se comprueba en `clean()`."""

    class Meta:
        model = AnimeTitle
        fields = ['anime', 'title_lang', 'title', 'is_active']

    anime = forms.ModelChoiceField(
        label=_('Anime'),
        help_text=_('Anime al que pertenece el título. Escribe para buscar.'),
        required=True, queryset=Anime.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:anime_select', attrs={
            'aria-label': _('Anime'), 'required': 'required',
            'title': _('Anime al que pertenece el título. Escribe para buscar.'),
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
        """`unique_together = (anime, title_lang, title)` en el modelo."""
        cleaned = super().clean()
        anime = cleaned.get('anime')
        title_lang = cleaned.get('title_lang')
        title = cleaned.get('title')
        if anime and title_lang and title:
            duplicados = AnimeTitle.objects.filter(anime=anime, title_lang=title_lang, title=title)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('title', 'Este anime ya tiene ese título en ese idioma.')
        return cleaned


class CharacterForm(forms.ModelForm):
    """Personaje de una obra otaku. Su clave única es `mal_id` (lo acuña el `save()`
    del modelo para los personajes locales), no el nombre."""

    class Meta:
        model = Character
        fields = ['full_name', 'name_kanji', 'birthday', 'biography', 'is_active']

    full_name = forms.CharField(
        label=_('Nombre'),
        help_text=_('Nombre del personaje, romanizado.'),
        required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 255, 'required': 'required',
            'title': _('Nombre del personaje, romanizado.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 255 caracteres.')},
    )
    name_kanji = forms.CharField(
        label=_('Nombre (kanji)'),
        help_text=_('Nombre en japonés (opcional).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre (kanji)'), 'aria-label': _('Nombre (kanji)'),
            'autocomplete': 'off', 'maxlength': 255,
            'title': _('Nombre en japonés (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )
    birthday = forms.CharField(
        label=_('Cumpleaños'),
        help_text=_('Como en MAL: «24 de septiembre» (texto libre, opcional).'),
        required=False, max_length=100, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Cumpleaños'), 'aria-label': _('Cumpleaños'),
            'autocomplete': 'off', 'maxlength': 100,
            'title': _('Como en MAL: «24 de septiembre» (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 100 caracteres.')},
    )
    biography = forms.CharField(
        label=_('Biografía'),
        help_text=_('Reseña del personaje (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Biografía'), 'aria-label': _('Biografía'), 'autocomplete': 'off',
            'rows': 6, 'title': _('Reseña del personaje (opcional).'),
        }),
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_full_name(self):
        """El `slug` de Character NO es único (hay homónimos entre obras): solo
        normalizamos. La clave real es `mal_id`."""
        return ' '.join((self.cleaned_data.get('full_name') or '').split())

    def clean_name_kanji(self):
        return ' '.join((self.cleaned_data.get('name_kanji') or '').split())

    def clean_biography(self):
        return (self.cleaned_data.get('biography') or '').strip()


class CharacterImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = CharacterImage
        fields = ['character', 'order', 'image', 'image_url', 'is_active']

    character = forms.ModelChoiceField(
        label=_('Personaje'),
        help_text=_('De quién es la imagen. Escribe para buscar.'),
        required=True, queryset=Character.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:character_select', attrs={
            'aria-label': _('Personaje'), 'required': 'required',
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


class CharacterNicknameForm(forms.ModelForm):
    """Apodo/alias de un personaje. El modelo exige que el par (personaje, apodo)
    sea único: se comprueba en `clean()` para dar un mensaje claro."""

    class Meta:
        model = CharacterNickname
        fields = ['character', 'nickname', 'is_active']

    character = forms.ModelChoiceField(
        label=_('Personaje'),
        help_text=_('A quién pertenece el apodo. Escribe para buscar.'),
        required=True, queryset=Character.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:character_select', attrs={
            'aria-label': _('Personaje'), 'required': 'required',
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
        """`unique_together = (character, nickname)` en el modelo."""
        cleaned = super().clean()
        character = cleaned.get('character')
        nickname = cleaned.get('nickname')
        if character and nickname:
            duplicados = CharacterNickname.objects.filter(character=character, nickname=nickname)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('nickname', 'Este personaje ya tiene registrado ese apodo.')
        return cleaned


class CharacterVoiceForm(forms.ModelForm):
    """Quién pone la voz a un personaje, y en qué idioma. El modelo exige que
    (persona, personaje, idioma) sea único: se comprueba en `clean()`."""

    class Meta:
        model = CharacterVoice
        fields = ['person', 'character', 'language', 'is_active']

    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('Seiyū o actor de doblaje. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('Seiyū o actor de doblaje. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    character = forms.ModelChoiceField(
        label=_('Personaje'),
        help_text=_('A quién dobla. Escribe para buscar.'),
        required=True, queryset=Character.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:character_select', attrs={
            'aria-label': _('Personaje'), 'required': 'required',
            'title': _('A quién dobla. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    language = forms.ModelChoiceField(
        label=_('Idioma'),
        help_text=_('Idioma del doblaje. Escribe para buscar.'),
        required=True, queryset=Language.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:language_select', attrs={
            'aria-label': _('Idioma'), 'required': 'required',
            'title': _('Idioma del doblaje. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean(self):
        """`unique_together = (person, character, language)` en el modelo."""
        cleaned = super().clean()
        person = cleaned.get('person')
        character = cleaned.get('character')
        language = cleaned.get('language')
        if person and character and language:
            duplicadas = CharacterVoice.objects.filter(
                person=person, character=character, language=language)
            if self.instance.pk:
                duplicadas = duplicadas.exclude(pk=self.instance.pk)
            if duplicadas.exists():
                self.add_error(None, 'Esa persona ya dobla a ese personaje en ese idioma.')
        return cleaned


class CompanyMALExistentForm(forms.ModelForm):
    """Ficha MAL para una compañía que YA existe: se elige en el select y se rellenan su MAL id y su url. No toca los
    datos de la compañía. Mismo objetivo que `CompanyMALNewForm`, otro punto de partida. Desde la ficha de la compañía
    o desde el «Enlazar» del modal llega con la compañía ya elegida y fija (`compania_fija`)."""

    class Meta:
        model = CompanyMAL
        fields = ['company', 'kind', 'mal_id', 'url', 'name_japanese', 'established', 'favorites', 'about']

    company = forms.ModelChoiceField(
        label=_('Compañía'),
        help_text=_('La compañía que ya existe en el catálogo. Escribe para buscar.'),
        required=True, queryset=Company.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:company_select', attrs={
            'aria-label': _('Compañía'), 'title': _('La compañía que ya existe en el catálogo. Escribe para buscar.'),
        }),
        error_messages={'required': _('Elige la compañía.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )

    kind = forms.ChoiceField(
        label=_('Tipo en MAL'),
        help_text=_('Compañía (anime/producer) o revista (manga/magazine): MAL numera cada una por separado.'),
        required=True, choices=MalCompanyKind.choices, initial=MalCompanyKind.COMPANY,
        widget=forms.Select(attrs={'aria-label': _('Tipo en MAL')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )

    mal_id = forms.IntegerField(
        label=_('MAL id'),
        help_text=_('Número de la URL de MAL (…/producer/<id> o …/magazine/<id>). Único dentro de su tipo.'),
        required=True, min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': _('1'), 'aria-label': _('MAL id'), 'autocomplete': 'off', 'inputmode': 'numeric',
            'step': 1, 'min': 1, 'required': 'required',
            'title': _('Número de la URL de MAL (…/producer/<id> o …/magazine/<id>). Único dentro de su tipo.'),
        }),
        error_messages={'required': _('Escribe el MAL id.'), 'invalid': _('Introduce un número entero.'),
                        'min_value': _('Los ids de MAL empiezan en 1.')},
    )

    url = forms.URLField(
        label=_('URL en MAL'),
        help_text=_('Dirección de su ficha en MyAnimeList (opcional; si falta se deduce del id).'),
        required=False, max_length=500, assume_scheme='https',
        widget=forms.URLInput(attrs={
            'placeholder': _('https://myanimelist.net/anime/producer/1'), 'aria-label': _('URL en MAL'),
            'autocomplete': 'off', 'maxlength': 500,
        }),
        error_messages={'invalid': _('Escribe una URL válida.'), 'max_length': _('Máximo 500 caracteres.')},
    )

    CAMPOS_MAL = ('kind', 'mal_id', 'url')

    def __init__(self, *args, compania_fija=None, **kwargs):
        super().__init__(*args, **kwargs)
        if compania_fija is not None:
            self.fields['company'].initial = compania_fija
            self.fields['company'].disabled = True

    def clean_company(self):
        """Una compañía tiene a lo más una ficha MAL: si ya la tiene, se dice cuál."""
        company = self.cleaned_data.get('company')
        ficha = CompanyMAL.objects.filter(company=company).first() if company else None
        if ficha is not None:
            raise forms.ValidationError('«%s» ya tiene ficha MAL (MAL id %s): edítala en vez de crear otra.' % (company, ficha.mal_id))
        return company

    def save(self, commit=True):
        """La ficha, sin tocar los datos de la compañía."""
        ficha = CompanyMAL.objects.create(company=self.cleaned_data['company'], kind=self.cleaned_data['kind'],
                                          mal_id=self.cleaned_data['mal_id'], url=self.cleaned_data.get('url') or '')
        self.instance = ficha
        return ficha

    def clean(self):
        """(tipo, MAL id) es único: se avisa a quién pertenece si ya está enlazado."""
        cleaned = super().clean()
        kind, mal_id = cleaned.get('kind'), cleaned.get('mal_id')
        if kind and mal_id:
            otro = CompanyMAL.objects.filter(kind=kind, mal_id=mal_id).select_related('company').first()
            if otro is not None:
                self.add_error('mal_id', 'Ese MAL id de %s ya está enlazado a «%s».' % (MalCompanyKind(kind).label.lower(), otro.company))
        return cleaned


class CompanyMALNewForm(CompanyForm):
    """Compañía NUEVA con su ficha MAL, en UN solo formulario (también edita una que ya tiene ficha).

    Es el `CompanyForm` de siempre (hereda sus campos, widgets y validación) más el MAL id y la url, declarados aquí
    mismo. `save()` guarda la compañía y después su ficha. Si el nombre ya existe, no guarda: muestra el modal. Para
    una compañía que YA existe: `CompanyMALExistentForm`."""

    class Meta(CompanyForm.Meta):
        pass

    kind = forms.ChoiceField(
        label=_('Tipo en MAL'),
        help_text=_('Compañía (anime/producer) o revista (manga/magazine): MAL numera cada una por separado.'),
        required=True, choices=MalCompanyKind.choices, initial=MalCompanyKind.COMPANY,
        widget=forms.Select(attrs={'aria-label': _('Tipo en MAL')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )

    mal_id = forms.IntegerField(
        label=_('MAL id'),
        help_text=_('Número de la URL de MAL (…/producer/<id> o …/magazine/<id>). Único dentro de su tipo.'),
        required=True, min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': _('1'), 'aria-label': _('MAL id'), 'autocomplete': 'off', 'inputmode': 'numeric',
            'step': 1, 'min': 1, 'required': 'required',
            'title': _('Número de la URL de MAL (…/producer/<id> o …/magazine/<id>). Único dentro de su tipo.'),
        }),
        error_messages={'required': _('Escribe el MAL id.'), 'invalid': _('Introduce un número entero.'),
                        'min_value': _('Los ids de MAL empiezan en 1.')},
    )

    url = forms.URLField(
        label=_('URL en MAL'),
        help_text=_('Dirección de su ficha en MyAnimeList (opcional; si falta se deduce del id).'),
        required=False, max_length=500, assume_scheme='https',
        widget=forms.URLInput(attrs={
            'placeholder': _('https://myanimelist.net/anime/producer/1'), 'aria-label': _('URL en MAL'),
            'autocomplete': 'off', 'maxlength': 500,
        }),
        error_messages={'invalid': _('Escribe una URL válida.'), 'max_length': _('Máximo 500 caracteres.')},
    )

    CAMPOS_MAL = ('kind', 'mal_id', 'url')

    def clean(self):
        """(tipo, MAL id) es único: se avisa a quién pertenece si ya está enlazado a OTRA compañía."""
        cleaned = super().clean()
        kind, mal_id = cleaned.get('kind'), cleaned.get('mal_id')
        if kind and mal_id:
            otros = CompanyMAL.objects.filter(kind=kind, mal_id=mal_id).select_related('company')
            if self.instance.pk:
                otros = otros.exclude(company_id=self.instance.pk)
            otro = otros.first()
            if otro is not None:
                self.add_error('mal_id', 'Ese MAL id de %s ya está enlazado a «%s».' % (MalCompanyKind(kind).label.lower(), otro.company))
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ficha = CompanyMAL.objects.filter(company=self.instance).first() if self.instance.pk else None
        if ficha is not None:
            self.fields['kind'].initial = ficha.kind
            self.fields['mal_id'].initial = ficha.mal_id
            self.fields['url'].initial = ficha.url

    def save(self, commit=True):
        compania = super().save(commit=commit)
        if commit:
            CompanyMAL.objects.update_or_create(
                company=compania,
                defaults={'kind': self.cleaned_data['kind'], 'mal_id': self.cleaned_data['mal_id'], 'url': self.cleaned_data.get('url') or ''},
            )
        return compania

    def prefill_query(self):
        """Los datos MAL que ya escribiste, como query string: viajan en el «Enlazar» del modal para que la entidad
        existente llegue con ellos puestos y no haya que teclearlos otra vez."""
        from urllib.parse import urlencode
        return urlencode({c: self.data.get(c) for c in self.CAMPOS_MAL if self.data.get(c) not in (None, "")})

    def candidatas(self):
        """La compañía que ya tiene ese nombre (el nombre es único por slug), con su enlace a la ficha MAL."""
        return getattr(self, '_candidatas', [])

    def clean_name(self):
        """Si el nombre ya existe no se duplica (tampoco lo dejaría CompanyForm), pero en vez del error genérico se
        ofrece la compañía existente para añadirle o editar su ficha MAL."""
        from django.utils.text import slugify
        from apps.otaku import fichas_mal
        nombre = ' '.join((self.cleaned_data.get('name') or '').split())
        existentes = Company.objects.filter(slug=slugify(nombre)[:270])
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        existentes = list(existentes)
        if existentes:
            vinculos = fichas_mal.enlaces('company', [c.pk for c in existentes])
            self._candidatas = [{'obj': c, 'enlace': vinculos.get(c.pk), 'iniciales': _iniciales(c)} for c in existentes]
            raise forms.ValidationError(_('Ya existe la compañía «%(c)s»: añádele la ficha MAL (o edítala) desde el '
                                          'enlace de abajo.') % {'c': existentes[0]})
        return super().clean_name()


class DataAnilistAnimeForm(forms.ModelForm):
    """Staging de AniList (anime). Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataAnilistAnime
        fields = ['anilist_id', 'id_mal', 'data_status', 'data_processed', 'is_active']

    data_status = forms.BooleanField(
        label=_('Fetch OK'), help_text=_('La API respondió y el JSON se guardó bien.'), required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'), help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False, widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'), help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataAnilistAnimeIdForm(AnilistIdForm):
    TIPO = 'anime'
    success_url = 'panel:data-anilist-anime_list'


class DataAnilistAnimePagesForm(AnilistPagesForm):
    TIPO = 'anime'
    success_url = 'panel:data-anilist-anime_list'


class DataAnilistAnimeRangeForm(AnilistRangeForm):
    TIPO = 'anime'
    success_url = 'panel:data-anilist-anime_list'


class DataAnilistCharacterForm(forms.ModelForm):
    """Staging de AniList (personaje). Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataAnilistCharacter
        fields = ['anilist_id', 'id_mal', 'data_status', 'data_processed', 'is_active']

    data_status = forms.BooleanField(
        label=_('Fetch OK'), help_text=_('La API respondió y el JSON se guardó bien.'), required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'), help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False, widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'), help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataAnilistCharacterIdForm(AnilistIdForm):
    TIPO = 'character'
    success_url = 'panel:data-anilist-character_list'


class DataAnilistCharacterPagesForm(AnilistPagesForm):
    TIPO = 'character'
    success_url = 'panel:data-anilist-character_list'


class DataAnilistCharacterRangeForm(AnilistRangeForm):
    TIPO = 'character'
    success_url = 'panel:data-anilist-character_list'


class DataAnilistMangaForm(forms.ModelForm):
    """Staging de AniList (manga). Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataAnilistManga
        fields = ['anilist_id', 'id_mal', 'data_status', 'data_processed', 'is_active']

    data_status = forms.BooleanField(
        label=_('Fetch OK'), help_text=_('La API respondió y el JSON se guardó bien.'), required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'), help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False, widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'), help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataAnilistMangaIdForm(AnilistIdForm):
    TIPO = 'manga'
    success_url = 'panel:data-anilist-manga_list'


class DataAnilistMangaPagesForm(AnilistPagesForm):
    TIPO = 'manga'
    success_url = 'panel:data-anilist-manga_list'


class DataAnilistMangaRangeForm(AnilistRangeForm):
    TIPO = 'manga'
    success_url = 'panel:data-anilist-manga_list'


class DataAnilistPersonForm(forms.ModelForm):
    """Staging de AniList (persona). Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataAnilistPerson
        fields = ['anilist_id', 'id_mal', 'data_status', 'data_processed', 'is_active']

    data_status = forms.BooleanField(
        label=_('Fetch OK'), help_text=_('La API respondió y el JSON se guardó bien.'), required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Fetch OK')}),
    )
    data_processed = forms.BooleanField(
        label=_('Procesado'), help_text=_('El JSON ya se transformó en entidades reales. Desmárcalo para reprocesar.'),
        required=False, initial=False, widget=forms.CheckboxInput(attrs={'aria-label': _('Procesado')}),
    )
    is_active = forms.BooleanField(
        label=_('Activo'), help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True, widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataAnilistPersonIdForm(AnilistIdForm):
    TIPO = 'person'
    success_url = 'panel:data-anilist-person_list'


class DataAnilistPersonPagesForm(AnilistPagesForm):
    TIPO = 'person'
    success_url = 'panel:data-anilist-person_list'


class DataAnilistPersonRangeForm(AnilistRangeForm):
    TIPO = 'person'
    success_url = 'panel:data-anilist-person_list'


class DataMalAnimeCharacterForm(forms.ModelForm):
    """Staging de `/anime/{id}/characters`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalAnimeCharacter
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalAnimeForm(forms.ModelForm):
    """Staging de `/anime/{id}/full`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalAnime
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

    data_status = forms.BooleanField(
        label=_('Fetch OK'),
        help_text=_('La API respondió y el JSON se guardó bien.'),
        required=False, initial=False,         # el modelo trae default=False
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
        required=False, initial=True,          # el modelo trae default=True
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )


class DataMalAnimePictureForm(forms.ModelForm):
    """Staging de `/anime/{id}/pictures`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalAnimePicture
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalAnimeStaffForm(forms.ModelForm):
    """Staging de `/anime/{id}/staff`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalAnimeStaff
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalCharacterForm(forms.ModelForm):
    """Staging de `/characters/{id}/full`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalCharacter
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalCharacterPictureForm(forms.ModelForm):
    """Staging de `/characters/{id}/pictures`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalCharacterPicture
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalMangaCharacterForm(forms.ModelForm):
    """Staging de `/manga/{id}/characters`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalMangaCharacter
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalMangaForm(forms.ModelForm):
    """Staging de `/manga/{id}/full`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalManga
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalMangaPictureForm(forms.ModelForm):
    """Staging de `/manga/{id}/pictures`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalMangaPicture
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalPersonForm(forms.ModelForm):
    """Staging de `/people/{id}/full`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalPerson
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DataMalPersonPictureForm(forms.ModelForm):
    """Staging de `/people/{id}/pictures`. Solo se tocan las banderas del proceso."""

    class Meta:
        model = DataMalPersonPicture
        fields = ['mal_id', 'data_status', 'data_processed', 'is_active']   # id externo primero: sin él el alta no tiene sentido

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


class DemographicAliasForm(forms.ModelForm):
    """alias de demografía: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = DemographicAlias
        fields = ['name', 'name_esp', 'is_active', 'demographic']


class DemographicForm(FormBaseCategory):
    """Demografía a la que va dirigida la obra: shōnen, shōjo, seinen, josei…"""

    class Meta:
        model = Demographic
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe una demografía con este nombre.')


class GenreAliasForm(forms.ModelForm):
    """alias de género: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = GenreAlias
        fields = ['name', 'name_esp', 'is_active', 'genre']


class GenreForm(FormBaseCategory):
    """Género otaku. `explicit` marca los géneros +18 (filtran el catálogo público)."""

    class Meta:
        model = Genre
        fields = ['name', 'name_esp', 'description', 'explicit', 'image', 'is_active']

    duplicate_message = _('Ya existe un género otaku con este nombre.')

    explicit = forms.BooleanField(
        label=_('Explícito (+18)'),
        help_text=_('Marca los géneros para adultos. Filtra el catálogo público.'),
        required=False, initial=False,         # el modelo trae default=False
        widget=forms.CheckboxInput(attrs={'aria-label': _('Explícito (+18)')}),
    )


class MALDumpForm(FormBaseLoadFile):
    """El formulario de «cargar un dump de MAL»: subir el archivo o releer el último de dump/. El hijo solo
    dice de qué TIPO es (la clave de `mal_dump_load.TIPOS`); lo demás es igual para los cuatro.

        class PersonMALDumpForm(MALDumpForm):
            TIPO = "person"
    """
    EXTENSIONES = list(DUMP_EXTENSIONS)
    MAX_MB = DUMP_MAX_MB                      # un dump de MAL pesa mucho más que un tags de VNDB
    PASOS = ["subir", "ultimo"]       # sin «descargar»: estos dumps no salen de una URL, los generas tú
    TIPO = ""

    paso = forms.ChoiceField(choices=[(p, p) for p in PASOS], required=False, initial="subir")   # lo manda el botón

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["archivo"].label = _("Subir el dump")
        self.fields["archivo"].widget.attrs["id"] = "archivo"

    def clean(self):
        from apps.otaku.services import mal_dump_load
        datos = super().clean()
        paso = datos.get("paso") or "subir"
        if paso == "subir" and not datos.get("archivo") and "archivo" not in self.errors:
            self.add_error("archivo", _("Elige el archivo del dump (.json o .json.gz), o relee el último."))
        if paso == "ultimo" and not mal_dump_load.ultimo_dump(self.TIPO):
            self.add_error(None, _("No hay ningún dump de este tipo guardado en dump/ que releer."))
        return datos

    def ruta_dump(self):
        """La ruta del dump ya en dump/: guarda el subido o devuelve el último (puede fallar por disco: lo
        captura la vista)."""
        from apps.otaku.services import mal_dump_load
        if (self.cleaned_data.get("paso") or "subir") == "ultimo":
            return mal_dump_load.ultimo_dump(self.TIPO)
        return mal_dump_load.guardar_subido(self.TIPO, self.cleaned_data["archivo"])


class AnimeMALDumpForm(MALDumpForm):
    """Dump de ANIMES de MAL: llena datos · Anime y datos · Anime · imágenes."""
    TIPO = "anime"


class CharacterMALDumpForm(MALDumpForm):
    """Dump de PERSONAJES de MAL: llena datos · Personaje y datos · Personaje · imágenes."""
    TIPO = "character"


class CompanyMALDumpForm(MALDumpForm):
    """Dump de COMPAÑÍAS de MAL: va DIRECTO a Compañía + Compañía (MAL), sin tabla Data."""
    TIPO = "company"


MAL_DEEP_KINDS = ('anime', 'manga')     # los únicos tipos con «profundo»: los demás no tienen qué encadenar


class MangaAuthorForm(forms.ModelForm):
    """Autoría de un manga: una persona con su rol (historia, arte…). El modelo exige
    que (manga, persona, rol) sea único: se comprueba en `clean()`."""

    class Meta:
        model = MangaAuthor
        fields = ['manga', 'person', 'role', 'is_active']

    manga = forms.ModelChoiceField(
        label=_('Manga'),
        help_text=_('Manga en el que trabajó. Escribe para buscar.'),
        required=True, queryset=Manga.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:manga_select', attrs={
            'aria-label': _('Manga'), 'required': 'required',
            'title': _('Manga en el que trabajó. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('Quién lo escribió o dibujó. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'required': 'required',
            'title': _('Quién lo escribió o dibujó. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.ModelChoiceField(
        label=_('Rol'),
        help_text=_('Historia, arte, guion… (opcional).'),
        required=False, queryset=Role.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:otaku-role_select', attrs={
            'aria-label': _('Rol'), 'title': _('Historia, arte, guion… (opcional).'),
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
        """`unique_together = (manga, person, role)` en el modelo."""
        cleaned = super().clean()
        manga = cleaned.get('manga')
        person = cleaned.get('person')
        if manga and person:
            duplicados = MangaAuthor.objects.filter(
                manga=manga, person=person, role=cleaned.get('role'))
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, 'Esa persona ya está registrada con ese rol en el manga.')
        return cleaned


class MangaCharacterForm(forms.ModelForm):
    """Aparición de un personaje en un manga, con su rol. El modelo exige que
    (manga, personaje, rol) sea único: se comprueba en `clean()`."""

    class Meta:
        model = MangaCharacter
        fields = ['manga', 'character', 'role', 'is_active']

    manga = forms.ModelChoiceField(
        label=_('Manga'),
        help_text=_('Manga en el que aparece. Escribe para buscar.'),
        required=True, queryset=Manga.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:manga_select', attrs={
            'aria-label': _('Manga'), 'required': 'required',
            'title': _('Manga en el que aparece. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    character = forms.ModelChoiceField(
        label=_('Personaje'),
        help_text=_('Qué personaje aparece. Escribe para buscar.'),
        required=True, queryset=Character.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:character_select', attrs={
            'aria-label': _('Personaje'), 'required': 'required',
            'title': _('Qué personaje aparece. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    role = forms.ModelChoiceField(
        label=_('Rol'),
        help_text=_('Principal, secundario… (opcional).'),
        required=False, queryset=Role.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:otaku-role_select', attrs={
            'aria-label': _('Rol'), 'title': _('Principal, secundario… (opcional).'),
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
        """`unique_together = (manga, character, role)` en el modelo."""
        cleaned = super().clean()
        manga = cleaned.get('manga')
        character = cleaned.get('character')
        if manga and character:
            duplicados = MangaCharacter.objects.filter(
                manga=manga, character=character, role=cleaned.get('role'))
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error(None, 'Ese personaje ya está registrado con ese rol en el manga.')
        return cleaned


class MangaForm(forms.ModelForm):
    """El manga en sí. Igual que el anime: su clave única es `mal_id`, no el slug."""

    class Meta:
        model = Manga
        fields = ['title', 'title_eng', 'title_jap', 'synopsis', 'manga_type', 'source',
                  'rating', 'status', 'season', 'year', 'chapters', 'volumes', 'serializations',
                  'genres', 'themes', 'demographics', 'from_date', 'to_date',
                  'is_active']

    title = forms.CharField(
        label=_('Título'),
        help_text=_('Título principal (normalmente el romanizado).'),
        required=True, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título'), 'aria-label': _('Título'), 'autocomplete': 'off',
            'maxlength': 500, 'required': 'required',
            'title': _('Título principal (normalmente el romanizado).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 500 caracteres.')},
    )
    title_eng = forms.CharField(
        label=_('Título (EN)'),
        help_text=_('Título en inglés (opcional).'),
        required=False, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título (EN)'), 'aria-label': _('Título (EN)'), 'autocomplete': 'off',
            'maxlength': 500, 'title': _('Título en inglés (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 500 caracteres.')},
    )
    title_jap = forms.CharField(
        label=_('Título (JP)'),
        help_text=_('Título en japonés/kanji (opcional).'),
        required=False, max_length=500, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Título (JP)'), 'aria-label': _('Título (JP)'), 'autocomplete': 'off',
            'maxlength': 500, 'title': _('Título en japonés/kanji (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 500 caracteres.')},
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
    manga_type = forms.ModelChoiceField(
        label=_('Tipo'),
        help_text=_('Manga, novela ligera, one-shot… Escribe para buscar.'),
        required=False, queryset=Type.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:type_select', attrs={
            'aria-label': _('Tipo'), 'title': _('Manga, novela ligera, one-shot… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    source = forms.ModelChoiceField(
        label=_('Fuente'),
        help_text=_('De dónde se adapta, si aplica. Escribe para buscar.'),
        required=False, queryset=Source.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:source_select', attrs={
            'aria-label': _('Fuente'), 'title': _('De dónde se adapta, si aplica. Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    rating = forms.ChoiceField(
        label=_('Clasificación'), required=False, choices=[('', '—')] + list(MalRating.choices),
        widget=forms.Select(attrs={'aria-label': _('Clasificación'), 'title': _('Clasificación por edad (MAL).')}),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    status = forms.ModelChoiceField(
        label=_('Estado'),
        help_text=_('En publicación, finalizado, en pausa… Escribe para buscar.'),
        required=False, queryset=Status.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:status_select', attrs={
            'aria-label': _('Estado'),
            'title': _('En publicación, finalizado, en pausa… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    year = forms.IntegerField(
        label=_('Año'),
        help_text=_('Año de publicación (1888–2100).'),
        required=False, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('2015'), 'aria-label': _('Año'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'title': _('Año de publicación (1888–2100).'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    chapters = forms.IntegerField(
        label=_('Capítulos'),
        help_text=_('Número de capítulos. 0 si aún no se sabe.'),
        required=False, min_value=0, initial=0,      # el modelo trae default=0
        widget=forms.NumberInput(attrs={
            'placeholder': _('120'), 'aria-label': _('Capítulos'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 0,
            'title': _('Número de capítulos. 0 si aún no se sabe.'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El valor mínimo es 0.')},
    )
    volumes = forms.IntegerField(
        label=_('Volúmenes'),
        help_text=_('Número de tomos. 0 si aún no se sabe.'),
        required=False, min_value=0, initial=0,      # el modelo trae default=0
        widget=forms.NumberInput(attrs={
            'placeholder': _('12'), 'aria-label': _('Volúmenes'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 0,
            'title': _('Número de tomos. 0 si aún no se sabe.'),
        }),
        error_messages={'invalid': _('Introduce un número entero.'),
                        'min_value': _('El valor mínimo es 0.')},
    )
    serializations = forms.ModelMultipleChoiceField(
        label=_('Serializaciones'),
        help_text=_('Revistas en las que se publicó. Puedes elegir varias.'),
        required=False, queryset=Company.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:company_select', attrs={
            'aria-label': _('Serializaciones'),
            'title': _('Revistas en las que se publicó. Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    genres = forms.ModelMultipleChoiceField(
        label=_('Géneros'),
        help_text=_('Puedes elegir varios. Escribe para buscar.'),
        required=False, queryset=Genre.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:genre_select', attrs={
            'aria-label': _('Géneros'), 'title': _('Puedes elegir varios. Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    themes = forms.ModelMultipleChoiceField(
        label=_('Temas'),
        help_text=_('Temas o etiquetas argumentales. Puedes elegir varios.'),
        required=False, queryset=Theme.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:theme_select', attrs={
            'aria-label': _('Temas'), 'title': _('Temas o etiquetas argumentales. Puedes elegir varios.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    demographics = forms.ModelMultipleChoiceField(
        label=_('Demografías'),
        help_text=_('Shōnen, seinen, josei… Puedes elegir varias.'),
        required=False, queryset=Demographic.objects.all(),
        widget=AjaxSelectMultiple(url_name='panel:demographic_select', attrs={
            'aria-label': _('Demografías'), 'title': _('Shōnen, seinen, josei… Puedes elegir varias.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    from_date = forms.DateField(
        label=_('Desde'),
        help_text=_('Fecha de inicio de publicación. Formato dd-mm-aaaa.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Desde'), 'class': 'js-date',
            'autocomplete': 'off', 'title': _('Fecha de inicio de publicación. Formato dd-mm-aaaa.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    to_date = forms.DateField(
        label=_('Hasta'),
        help_text=_('Fecha de fin (si terminó). Formato dd-mm-aaaa.'),
        required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'placeholder': _('dd-mm-aaaa'), 'aria-label': _('Hasta'), 'class': 'js-date',
            'autocomplete': 'off', 'title': _('Fecha de fin (si terminó). Formato dd-mm-aaaa.'),
        }, format='%Y-%m-%d'),
        error_messages={'invalid': _('Fecha inválida (usa dd-mm-aaaa).')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio. Desmárcalo en vez de borrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_title(self):
        """La clave única de Manga es `mal_id`, no el slug. Aquí solo normalizamos."""
        return ' '.join((self.cleaned_data.get('title') or '').split())

    def clean_title_eng(self):
        return ' '.join((self.cleaned_data.get('title_eng') or '').split())

    def clean_title_jap(self):
        return ' '.join((self.cleaned_data.get('title_jap') or '').split())

    def clean_synopsis(self):
        return (self.cleaned_data.get('synopsis') or '').strip()

    def clean_chapters(self):
        chapters = self.cleaned_data.get('chapters')
        return 0 if chapters is None else chapters

    def clean_volumes(self):
        volumes = self.cleaned_data.get('volumes')
        return 0 if volumes is None else volumes

    def clean(self):
        """Cruce de dos campos: no puede terminar de publicarse antes de empezar."""
        cleaned = super().clean()
        desde = cleaned.get('from_date')
        hasta = cleaned.get('to_date')
        if desde and hasta and hasta < desde:
            self.add_error('to_date', 'La fecha «hasta» no puede ser anterior a «desde».')
        return cleaned


class MangaImageForm(forms.ModelForm):
    """Imagen de la entidad. La de `orden` más bajo es su portada."""

    class Meta:
        model = MangaImage
        fields = ['manga', 'order', 'image', 'image_url', 'is_active']

    manga = forms.ModelChoiceField(
        label=_('Manga'),
        help_text=_('Manga al que pertenece la imagen. Escribe para buscar.'),
        required=True, queryset=Manga.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:manga_select', attrs={
            'aria-label': _('Manga'), 'required': 'required',
            'title': _('Manga al que pertenece la imagen. Escribe para buscar.'),
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


class MangaMALDumpForm(MALDumpForm):
    """Dump de MANGAS de MAL: llena datos · Manga y datos · Manga · imágenes."""
    TIPO = "manga"


class MangaTitleForm(forms.ModelForm):
    """Título alternativo de un manga, por idioma. El modelo exige que
    (manga, idioma, título) sea único: se comprueba en `clean()`."""

    class Meta:
        model = MangaTitle
        fields = ['manga', 'title_lang', 'title', 'is_active']

    manga = forms.ModelChoiceField(
        label=_('Manga'),
        help_text=_('Manga al que pertenece el título. Escribe para buscar.'),
        required=True, queryset=Manga.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:manga_select', attrs={
            'aria-label': _('Manga'), 'required': 'required',
            'title': _('Manga al que pertenece el título. Escribe para buscar.'),
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
        """`unique_together = (manga, title_lang, title)` en el modelo."""
        cleaned = super().clean()
        manga = cleaned.get('manga')
        title_lang = cleaned.get('title_lang')
        title = cleaned.get('title')
        if manga and title_lang and title:
            duplicados = MangaTitle.objects.filter(manga=manga, title_lang=title_lang, title=title)
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)
            if duplicados.exists():
                self.add_error('title', 'Este manga ya tiene ese título en ese idioma.')
        return cleaned


class PersonMALDumpForm(MALDumpForm):
    """Dump de PERSONAS de MAL: llena datos · Persona y datos · Persona · imágenes."""
    TIPO = "person"


class PersonMALExistentForm(forms.ModelForm):
    """Ficha MAL para una persona que YA existe: se elige en el select y se rellenan sus datos MAL. No toca los datos
    de la persona. Mismo objetivo que `PersonMALNewForm`, otro punto de partida. Desde la ficha de la persona o desde el
    «Enlazar» del modal llega con la persona ya elegida y fija (`persona_fija`)."""

    class Meta:
        model = PersonMAL
        fields = ['person', 'mal_id', 'url', 'given_name', 'family_name', 'about']

    person = forms.ModelChoiceField(
        label=_('Persona'),
        help_text=_('La persona que ya existe en el catálogo. Escribe para buscar.'),
        required=True, queryset=Person.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:person_select', attrs={
            'aria-label': _('Persona'), 'title': _('La persona que ya existe en el catálogo. Escribe para buscar.'),
        }),
        error_messages={'required': _('Elige la persona.'), 'invalid_choice': _('Selecciona una opción válida.')},
    )

    mal_id = forms.IntegerField(
        label=_('MAL id'),
        help_text=_('Número de la URL myanimelist.net/people/<id>. Único.'),
        required=True, min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': _('11'), 'aria-label': _('MAL id'), 'min': 1, 'required': 'required',
            'title': _('Número de la URL myanimelist.net/people/<id>. Único.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'), 'invalid': _('Escribe un número entero.'),
                        'min_value': _('Debe ser mayor que cero.')},
    )

    url = forms.URLField(
        label=_('URL en MAL'),
        help_text=_('Dirección de su ficha en MyAnimeList (opcional; si falta se deduce del id).'),
        required=False, max_length=500, assume_scheme='https',
        widget=forms.URLInput(attrs={
            'placeholder': _('https://myanimelist.net/people/11'), 'aria-label': _('URL en MAL'), 'autocomplete': 'off',
            'maxlength': 500,
        }),
        error_messages={'invalid': _('Escribe una URL válida.'), 'max_length': _('Máximo 500 caracteres.')},
    )

    given_name = forms.CharField(
        label=_('Nombre (given)'),
        help_text=_('Nombre de pila tal como lo da MAL; en kanji para japoneses (p. ej. 奈々).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('奈々'), 'aria-label': _('Nombre (given)'), 'autocomplete': 'off', 'maxlength': 255,
            'title': _('Nombre de pila tal como lo da MAL; en kanji para japoneses.'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )

    family_name = forms.CharField(
        label=_('Apellido (family)'),
        help_text=_('Apellido tal como lo da MAL (p. ej. 水樹).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('水樹'), 'aria-label': _('Apellido (family)'), 'autocomplete': 'off', 'maxlength': 255,
            'title': _('Apellido tal como lo da MAL.'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )

    about = forms.CharField(
        label=_('About (MAL)'),
        help_text=_('Texto «about» de MAL. La biografía neutra de la persona se rellena con él solo si estaba vacía.'),
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': _('About'), 'aria-label': _('About (MAL)')}),
    )

    CAMPOS_MAL = ('mal_id', 'url', 'given_name', 'family_name', 'about')

    def __init__(self, *args, persona_fija=None, **kwargs):
        super().__init__(*args, **kwargs)
        if persona_fija is not None:
            self.fields['person'].initial = persona_fija
            self.fields['person'].disabled = True

    def clean_person(self):
        """Una persona tiene a lo más una ficha MAL: si ya la tiene, se dice cuál."""
        person = self.cleaned_data.get('person')
        ficha = PersonMAL.objects.filter(person=person).first() if person else None
        if ficha is not None:
            raise forms.ValidationError('«%s» ya tiene ficha MAL (MAL id %s): edítala en vez de crear otra.' % (person, ficha.mal_id))
        return person

    def save(self, commit=True):
        """La ficha por el servicio único (el mismo que el importador), sin tocar los datos de la persona."""
        from apps.otaku.services.personas import upsert_persona_mal
        _persona, ficha, _creada = upsert_persona_mal(
            {campo: self.cleaned_data.get(campo) for campo in self.CAMPOS_MAL}, person=self.cleaned_data['person'])
        self.instance = ficha
        return ficha

    def clean_mal_id(self):
        """`mal_id` es único: se avisa a quién pertenece si ya está enlazado."""
        mal_id = self.cleaned_data.get('mal_id')
        otro = PersonMAL.objects.filter(mal_id=mal_id).select_related('person').first()
        if otro is not None:
            raise forms.ValidationError('Ese MAL id ya está enlazado a «%s».' % otro.person)
        return mal_id


def _iniciales(obj):
    """«James Gunn» → «JG»: el avatar de cada candidata en el modal."""
    return "".join(palabra[0] for palabra in str(obj).replace(",", " ").split()[:2]).upper() or "?"


class PersonMALNewForm(PersonForm):
    """Persona NUEVA con su ficha MAL, en UN solo formulario (también edita una que ya tiene ficha).

    Es el `PersonForm` de siempre (hereda sus campos, widgets y validación) más los campos de la ficha MAL, declarados
    aquí mismo. `save()` guarda la persona y después su ficha con el servicio único `upsert_persona_mal`. Si el nombre
    ya existe, no guarda: muestra el modal de candidatas. Para una persona que YA existe: `PersonMALExistentForm`."""

    class Meta(PersonForm.Meta):
        pass

    mal_id = forms.IntegerField(
        label=_('MAL id'),
        help_text=_('Número de la URL myanimelist.net/people/<id>. Único.'),
        required=True, min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': _('11'), 'aria-label': _('MAL id'), 'min': 1, 'required': 'required',
            'title': _('Número de la URL myanimelist.net/people/<id>. Único.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'), 'invalid': _('Escribe un número entero.'),
                        'min_value': _('Debe ser mayor que cero.')},
    )

    url = forms.URLField(
        label=_('URL en MAL'),
        help_text=_('Dirección de su ficha en MyAnimeList (opcional; si falta se deduce del id).'),
        required=False, max_length=500, assume_scheme='https',
        widget=forms.URLInput(attrs={
            'placeholder': _('https://myanimelist.net/people/11'), 'aria-label': _('URL en MAL'), 'autocomplete': 'off',
            'maxlength': 500,
        }),
        error_messages={'invalid': _('Escribe una URL válida.'), 'max_length': _('Máximo 500 caracteres.')},
    )

    given_name = forms.CharField(
        label=_('Nombre (given)'),
        help_text=_('Nombre de pila tal como lo da MAL; en kanji para japoneses (p. ej. 奈々).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('奈々'), 'aria-label': _('Nombre (given)'), 'autocomplete': 'off', 'maxlength': 255,
            'title': _('Nombre de pila tal como lo da MAL; en kanji para japoneses.'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )

    family_name = forms.CharField(
        label=_('Apellido (family)'),
        help_text=_('Apellido tal como lo da MAL (p. ej. 水樹).'),
        required=False, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('水樹'), 'aria-label': _('Apellido (family)'), 'autocomplete': 'off', 'maxlength': 255,
            'title': _('Apellido tal como lo da MAL.'),
        }),
        error_messages={'max_length': _('Máximo 255 caracteres.')},
    )

    about = forms.CharField(
        label=_('About (MAL)'),
        help_text=_('Texto «about» de MAL. La biografía neutra de la persona se rellena con él solo si estaba vacía.'),
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': _('About'), 'aria-label': _('About (MAL)')}),
    )

    CAMPOS_MAL = ('mal_id', 'url', 'given_name', 'family_name', 'about')

    def clean_mal_id(self):
        """`mal_id` es único: se avisa a quién pertenece si ya está enlazado a OTRA persona."""
        mal_id = self.cleaned_data.get('mal_id')
        otros = PersonMAL.objects.filter(mal_id=mal_id).select_related('person')
        if self.instance.pk:
            otros = otros.exclude(person_id=self.instance.pk)
        otro = otros.first()
        if otro is not None:
            raise forms.ValidationError('Ese MAL id ya está enlazado a «%s».' % otro.person)
        return mal_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ficha = PersonMAL.objects.filter(person=self.instance).first() if self.instance.pk else None
        if ficha is not None:
            for campo in self.CAMPOS_MAL:
                self.fields[campo].initial = getattr(ficha, campo)
        self._quita_es_otra_si_no_aplica()

    def clean(self):
        cleaned = super().clean()
        self._candidatas = self._busca_candidatas()
        if self._candidatas:
            raise forms.ValidationError(_('Ya hay %(n)s persona(s) con ese nombre. Si es la misma, añádele la ficha MAL '
                                          'desde la lista de abajo; si es otra distinta, marca «Es otra persona».')
                                        % {'n': len(self._candidatas)})
        return cleaned

    def save(self, commit=True):
        persona = super().save(commit=commit)
        if commit:
            from apps.otaku.services.personas import upsert_persona_mal
            upsert_persona_mal({campo: self.cleaned_data.get(campo) for campo in self.CAMPOS_MAL}, person=persona)
        return persona

    es_otra = forms.BooleanField(
        label=_('Es otra persona distinta: créala igualmente'),
        help_text=_('Márcalo solo si ya existe alguien con ese nombre y NO es la misma persona.'),
        required=False, initial=False,
        widget=forms.HiddenInput(),   # la marca el modal de candidatas («Es otra persona: crearla»)
    )

    def _quita_es_otra_si_no_aplica(self):
        """«Es otra persona» solo tiene sentido al CREAR: en edición y en «añadir ficha» la persona ya está elegida."""
        if self.instance.pk:
            self.fields.pop('es_otra', None)

    def prefill_query(self):
        """Los datos MAL que ya escribiste, como query string: viajan en el «Enlazar» del modal para que la entidad
        existente llegue con ellos puestos y no haya que teclearlos otra vez."""
        from urllib.parse import urlencode
        return urlencode({c: self.data.get(c) for c in self.CAMPOS_MAL if self.data.get(c) not in (None, "")})

    def candidatas(self):
        """Personas con el MISMO nombre (sin mirar mayúsculas ni espacios de más), con su enlace a la ficha MAL.
        Se calcula al validar; la plantilla la pinta para que elijas. Vacía si no aplica."""
        return getattr(self, '_candidatas', [])

    def _busca_candidatas(self):
        if self.instance.pk or self.cleaned_data.get('es_otra'):
            return []
        nombre = ' '.join((self.cleaned_data.get('full_name') or '').split())
        if not nombre:
            return []
        from apps.otaku import fichas_mal
        personas = list(Person.objects.filter(full_name__iexact=nombre).select_related('country').order_by('pk'))
        vinculos = fichas_mal.enlaces('person', [p.pk for p in personas])
        return [{'obj': p, 'enlace': vinculos.get(p.pk), 'iniciales': _iniciales(p)} for p in personas]


class RelationForm(forms.ModelForm):
    """Relación entre dos obras, apuntadas por su MAL id (no por FK: pueden ser de
    anime o de manga). El modelo exige que (origen, destino, tipo) sea único."""

    class Meta:
        model = Relation
        fields = ['relation_type', 'from_type', 'from_mal_id', 'to_type', 'to_mal_id', 'is_active']

    relation_type = forms.ModelChoiceField(
        label=_('Tipo de relación'),
        help_text=_('Secuela, precuela, spin-off… Escribe para buscar.'),
        required=False, queryset=RelationType.objects.all(), empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:relation-type_select', attrs={
            'aria-label': _('Tipo de relación'),
            'title': _('Secuela, precuela, spin-off… Escribe para buscar.'),
        }),
        error_messages={'invalid_choice': _('Selecciona una opción válida.')},
    )
    from_type = forms.ChoiceField(
        label=_('Origen (tipo)'),
        help_text=_('Si la obra de origen es un anime o un manga.'),
        required=True, choices=Relation._meta.get_field('from_type').choices,
        widget=forms.Select(attrs={
            'aria-label': _('Origen (tipo)'), 'required': 'required',
            'title': _('Si la obra de origen es un anime o un manga.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    from_mal_id = forms.IntegerField(
        label=_('Origen (MAL id)'),
        help_text=_('MAL id de la obra de origen.'),
        required=True,
        widget=forms.NumberInput(attrs={
            'placeholder': _('1535'), 'aria-label': _('Origen (MAL id)'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'required': 'required',
            'title': _('MAL id de la obra de origen.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid': _('Introduce un número entero.')},
    )
    to_type = forms.ChoiceField(
        label=_('Destino (tipo)'),
        help_text=_('Si la obra de destino es un anime o un manga.'),
        required=True, choices=Relation._meta.get_field('to_type').choices,
        widget=forms.Select(attrs={
            'aria-label': _('Destino (tipo)'), 'required': 'required',
            'title': _('Si la obra de destino es un anime o un manga.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    to_mal_id = forms.IntegerField(
        label=_('Destino (MAL id)'),
        help_text=_('MAL id de la obra de destino.'),
        required=True,
        widget=forms.NumberInput(attrs={
            'placeholder': _('2994'), 'aria-label': _('Destino (MAL id)'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'required': 'required',
            'title': _('MAL id de la obra de destino.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid': _('Introduce un número entero.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean(self):
        cleaned = super().clean()
        origen = cleaned.get('from_mal_id')
        destino = cleaned.get('to_mal_id')
        # Una obra no se relaciona consigo misma.
        if (origen is not None and destino is not None and origen == destino
                and cleaned.get('from_type') == cleaned.get('to_type')):
            self.add_error('to_mal_id', 'El origen y el destino no pueden ser la misma obra.')
            return cleaned
        # `unique_together = (from_mal_id, to_mal_id, relation_type)` en el modelo.
        if origen is not None and destino is not None:
            duplicadas = Relation.objects.filter(
                from_mal_id=origen, to_mal_id=destino,
                relation_type=cleaned.get('relation_type'))
            if self.instance.pk:
                duplicadas = duplicadas.exclude(pk=self.instance.pk)
            if duplicadas.exists():
                self.add_error(None, 'Ya existe esa relación entre esas dos obras.')
        return cleaned


class RoleForm(forms.ModelForm):
    """Rol en una obra otaku: Protagonista, Director, Seiyū… agrupado por tipo de rol."""

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
                raise forms.ValidationError('Ya existe un rol otaku con este nombre.')
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


class SourceForm(FormBaseCategory):
    """Fuente de la que se adapta la obra: manga, novela ligera, videojuego, original…"""

    class Meta:
        model = Source
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe una fuente con este nombre.')


class StatusForm(FormBaseCategory):
    """Estado de emisión/publicación: en emisión, finalizado, anunciado…
    (Distinto del estado de COLECCIÓN del usuario, que vive en apps.collections.)"""

    class Meta:
        model = Status
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un estado con este nombre.')


class ThemeAliasForm(forms.ModelForm):
    """alias de tema: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = ThemeAlias
        fields = ['name', 'name_esp', 'is_active', 'theme']


class ThemeForm(FormBaseCategory):
    """Tema o etiqueta argumental: mecha, escolar, deportes, isekai…"""

    class Meta:
        model = Theme
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un tema con este nombre.')


class TypeForm(FormBaseCategory):
    """Tipo otaku: TV, película, OVA, manga, novela ligera…"""

    class Meta:
        model = Type
        fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    duplicate_message = _('Ya existe un tipo otaku con este nombre.')


class YearForm(forms.ModelForm):
    """Año de catálogo. El año es ÚNICO: se comprueba aquí para dar un mensaje claro."""

    class Meta:
        model = Year
        fields = ['year', 'is_active']

    year = forms.IntegerField(
        label=_('Año'),
        help_text=_('Año del catálogo (1888–2100). No puede repetirse.'),
        required=True, min_value=1888, max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('2015'), 'aria-label': _('Año'), 'autocomplete': 'off',
            'inputmode': 'numeric', 'step': 1, 'min': 1888, 'max': 2100,
            'required': 'required', 'title': _('Año del catálogo (1888–2100). No puede repetirse.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid': _('Introduce un número entero.'),
                        'min_value': _('El primer año válido es 1888.'),
                        'max_value': _('El último año válido es 2100.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si está activo, se muestra en el sitio.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year is None:
            return year
        duplicados = Year.objects.filter(year=year)
        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise forms.ValidationError('Ese año ya está en el catálogo.')
        return year


class OtakuLogForm(forms.ModelForm):
    """Log de otaku: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = OtakuLog
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


class DataMalAnimeProcessForm(ProcesarLoteForm):
    PENDIENTES = 'apps.otaku.services.mal_dump_process.pendientes'
    TIPO = 'anime'
    success_url = 'panel:data-mal-anime_list'


class DataMalCharacterProcessForm(ProcesarLoteForm):
    PENDIENTES = 'apps.otaku.services.mal_dump_process.pendientes'
    TIPO = 'character'
    success_url = 'panel:data-mal-character_list'


class DataMalMangaProcessForm(ProcesarLoteForm):
    PENDIENTES = 'apps.otaku.services.mal_dump_process.pendientes'
    TIPO = 'manga'
    success_url = 'panel:data-mal-manga_list'


class DataMalPersonProcessForm(ProcesarLoteForm):
    PENDIENTES = 'apps.otaku.services.mal_dump_process.pendientes'
    TIPO = 'person'
    success_url = 'panel:data-mal-person_list'


class AnimeImageDownloadForm(DescargarImagenesForm):
    TIPO = 'otaku.AnimeImage'
    success_url = 'panel:anime-image_list'


class CharacterImageDownloadForm(DescargarImagenesForm):
    TIPO = 'otaku.CharacterImage'
    success_url = 'panel:character-image_list'


class MangaImageDownloadForm(DescargarImagenesForm):
    TIPO = 'otaku.MangaImage'
    success_url = 'panel:manga-image_list'


class AnimeImageRetryForm(ReintentarMuertasForm):
    TIPO = 'otaku.AnimeImage'
    success_url = 'panel:anime-image_download'


class CharacterImageRetryForm(ReintentarMuertasForm):
    TIPO = 'otaku.CharacterImage'
    success_url = 'panel:character-image_download'


class MangaImageRetryForm(ReintentarMuertasForm):
    TIPO = 'otaku.MangaImage'
    success_url = 'panel:manga-image_download'


class CompanyImageMalDownloadForm(DescargarImagenesForm):
    TIPO = 'companies.CompanyImage:mal'
    success_url = 'panel:company-image-mal_list'


class CompanyImageMalRetryForm(ReintentarMuertasForm):
    TIPO = 'companies.CompanyImage:mal'
    success_url = 'panel:company-image-mal_download'


class PersonImageMalDownloadForm(DescargarImagenesForm):
    TIPO = 'people.PersonImage:mal'
    success_url = 'panel:person-image-mal_list'


class PersonImageMalRetryForm(ReintentarMuertasForm):
    TIPO = 'people.PersonImage:mal'
    success_url = 'panel:person-image-mal_download'

