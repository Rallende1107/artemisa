"""Forms del panel para collections.

Las colecciones y los favoritos de los usuarios son solo lectura + moderación (no
se editan desde el panel). Lo que sí se edita son los ESTADOS por medio: un form
por modelo, todos con los mismos campos (nombre EN, nombre ES, descripción, orden,
color de la paleta, activo)."""
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.catalogs.models import Format, Quality, Website
from apps.collections.models import AlbumCollection, AnimeCollection, ArtistCollection, CharacterCollection, CollectionLog, CompanyCollection, GameCharacterCollection, GameCollection, MangaCollection, MovieCollection, PersonCollection, SerieCollection, SongCollection
from core.shared.models.choices import LogLevel, WebsiteType


class AlbumCollectionForm(forms.ModelForm):
    """colección de álbumes: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = AlbumCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


class AnimeCollectionForm(forms.ModelForm):
    """colección de anime: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = AnimeCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


class ArtistCollectionForm(forms.ModelForm):
    """colección de artistas: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = ArtistCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


class CharacterCollectionForm(forms.ModelForm):
    """colección de personajes: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = CharacterCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content']


class CollectionItemForm(forms.ModelForm):
    """La FILA de Mi colección, un solo formulario: seguimiento (estado, nota, favorito) y dónde la
    veo / de dónde la descargué (sitio de streaming; sitio de descarga con formato y calidad). Sirve para las diez
    tablas: `item_form(tabla)` lo arma con los campos que ESA tabla tiene (personajes y personas no tienen estado; sin
    FORMATO no hay enlaces). El formato se filtra por el medio (for_video, for_document…)."""

    class Meta:
        fields = ["status", "score", "is_favorite", "watch_site", "download_site", "download_format", "download_quality"]

    CAMPOS = ["status", "score", "is_favorite", "watch_site", "download_site", "download_format", "download_quality"]
    ENLACES = ["watch_site", "download_site", "download_format", "download_quality"]   # por nombre, no por posición

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tabla = self._meta.model
        f = self.fields
        if "status" in f:
            f["status"].choices = [("", _("sin estado"))] + list(tabla._meta.get_field("status").choices)
        if "score" in f:
            f["score"] = forms.TypedChoiceField(label=_("Nota"), required=False, coerce=int, empty_value=None,
                                                choices=[("", "—")] + [(n, f"★ {n}") for n in range(1, 11)])
        if "watch_site" in f:
            f["watch_site"].queryset = Website.objects.filter(is_active=True, type=WebsiteType.STREAMING).order_by("name")
            f["watch_site"].empty_label = _("— ningún sitio —")
        if "download_site" in f:
            f["download_site"].queryset = Website.objects.filter(is_active=True, type=WebsiteType.DOWNLOAD).order_by("name")
            f["download_site"].empty_label = _("— ningún sitio —")
        if "download_format" in f:
            qs = Format.objects.filter(is_active=True)
            f["download_format"].queryset = (qs.filter(**{tabla.FORMATO: True}) if tabla.FORMATO else qs).order_by("name")
            f["download_format"].empty_label = _("Sin formato")
        if "download_quality" in f:
            f["download_quality"].queryset = Quality.objects.filter(is_active=True).order_by("name")
            f["download_quality"].empty_label = _("Sin calidad")

    def clean(self):
        data = super().clean()
        if "download_site" in self.fields and not data.get("download_site"):   # formato y calidad solo con sitio de descarga
            data["download_format"] = None
            data["download_quality"] = None
        return data


class CompanyCollectionForm(forms.ModelForm):
    """colección de compañías: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = CompanyCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content']


class GameCharacterCollectionForm(forms.ModelForm):
    """colección de personajes de juego: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = GameCharacterCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content']


class GameCollectionForm(forms.ModelForm):
    """colección de juegos: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = GameCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


class MangaCollectionForm(forms.ModelForm):
    """colección de manga: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = MangaCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


class MovieCollectionForm(forms.ModelForm):
    """colección de películas: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = MovieCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


class PersonCollectionForm(forms.ModelForm):
    """colección de personas: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = PersonCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content']


class SerieCollectionForm(forms.ModelForm):
    """colección de series: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = SerieCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


class SongCollectionForm(forms.ModelForm):
    """colección de canciones: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = SongCollection
        fields = ['user', 'score', 'is_favorite', 'watch_site', 'download_site', 'download_format', 'download_quality', 'is_active', 'content', 'status']


def item_form(tabla):
    """El ModelForm de UNA tabla de colección: CollectionItemForm recortado a los campos que esa tabla tiene."""
    nombres = {f.name for f in tabla._meta.fields}
    campos = [c for c in CollectionItemForm.CAMPOS if c in nombres and (tabla.FORMATO or c not in CollectionItemForm.ENLACES)]
    return forms.modelform_factory(tabla, form=CollectionItemForm, fields=campos)


class CollectionLogForm(forms.ModelForm):
    """Log de colecciones: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = CollectionLog
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
