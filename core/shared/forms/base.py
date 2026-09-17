"""Formularios base compartidos (los de modelo viven en cada app: `apps/<app>/forms.py`; las categorías heredan `FormBaseCategory`)."""
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.utils.constants import IMAGE_ACCEPT, IMAGE_EXTENSIONS, IMAGE_FORMATS, IMAGE_HINT, IMAGE_MAX_MB, MB


class FormBaseLoadFile(forms.Form):
    """El formulario de «cargar un ARCHIVO»: un `archivo` que solo acepta las extensiones declaradas y comprueba que
    el contenido sea lo que la extensión dice (un Excel o un PDF renombrados a .json no pasan).

        class VNDBTagsDumpForm(FormBaseLoadFile):
            EXTENSIONES = [".json", ".json.gz"]

    `archivo` es opcional AQUÍ porque hay pantallas con otras vías (descargar, releer el último); el formulario
    hijo decide en su `clean()` cuándo es obligatorio.
    """
    EXTENSIONES = []      # [".json", ".json.gz"]; vacío = cualquiera
    MAX_MB = 50           # peso máximo del archivo

    archivo = forms.FileField(required=False, label=_("Archivo"))

    # Con qué empieza cada tipo de archivo («número mágico»): lo que no cuadra, no es ese archivo.
    CABECERAS = {
        ".gz": (b"\x1f\x8b",),
        ".zip": (b"PK\x03\x04",),
        ".pdf": (b"%PDF",),
        ".json": (b"{", b"["),
        ".xml": (b"<",),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.EXTENSIONES:   # el navegador ya filtra el diálogo; la validación de verdad es clean_archivo
            self.fields["archivo"].widget.attrs["accept"] = ",".join(self.EXTENSIONES)

    def extension_de(self, nombre):
        """La extensión declarada que lleva el nombre (la más larga primero: «.json.gz» antes que «.gz»)."""
        nombre = nombre.lower()
        for ext in sorted(self.EXTENSIONES, key=len, reverse=True):
            if nombre.endswith(ext):
                return ext
        return ""

    def contenido_valido(self, archivo, ext):
        """Los primeros bytes cuadran con la extensión (por la ÚLTIMA parte: «.json.gz» se mira como .gz)."""
        cabecera = archivo.read(64)
        archivo.seek(0)
        if cabecera.startswith(b"\xef\xbb\xbf"):                       # BOM de UTF-8
            cabecera = cabecera[3:]
        firmas = self.CABECERAS.get("." + ext.rsplit(".", 1)[-1])
        return True if not firmas else cabecera.lstrip().startswith(firmas)

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")
        if not archivo:
            return archivo
        ext = self.extension_de(archivo.name)
        if self.EXTENSIONES and not ext:
            raise ValidationError(_("Solo se aceptan archivos %(ext)s.") % {"ext": ", ".join(self.EXTENSIONES)})
        if archivo.size > self.MAX_MB * MB:
            raise ValidationError(_("El archivo pesa más de %(mb)s MB.") % {"mb": self.MAX_MB})
        if not self.contenido_valido(archivo, ext):
            raise ValidationError(_("El archivo no es un %(ext)s de verdad (el contenido no cuadra con la extensión).") % {"ext": ext})
        return archivo




class FormBaseCategory(forms.ModelForm):
    """Formulario de una CATEGORÍA (`ModelBaseCategory`: género, tipo, estado…). Única excepción a «un formulario
    autónomo por modelo»: los campos comunes y su limpieza viven aquí; el hijo escribe su docstring, su `Meta`
    (modelo y orden de campos), su `duplicate_message`, su `image_help` si la imagen es otra cosa (bandera, logo) y los
    campos PROPIOS (acronym, explicit, url…).

        class TypeForm(FormBaseCategory):
            duplicate_message = _('Ya existe un tipo de película con este nombre.')

            class Meta:
                model = Type
                fields = ['name', 'name_esp', 'description', 'image', 'is_active']

    Un campo común que el modelo no edita se quita en el hijo con `name_esp = None`; uno distinto, se redeclara."""

    duplicate_message = _('Ya existe un registro con este nombre.')
    image_help = _('Imagen de la categoría (opcional). Si se deja vacía se usa una por defecto.')

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
        help_text=_('Imagen de la categoría (opcional). Si se deja vacía se usa una por defecto.'),   # el hijo la cambia con `image_help`
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'image' in self.fields:
            self.fields['image'].help_text = self.image_help

    def otros(self):
        """Los demás registros del modelo (sin el que se está editando)."""
        qs = self._meta.model.objects.all()
        return qs.exclude(pk=self.instance.pk) if self.instance.pk else qs

    def clean_name(self):
        """Único como nombre (por slug) y sin chocar con el nombre en español de OTRO registro."""
        name = ' '.join((self.cleaned_data.get('name') or '').split())
        slug = slugify(name)[:120]
        if slug and self.otros().filter(slug=slug).exists():
            raise forms.ValidationError(self.duplicate_message)
        cruce = self.otros().filter(name_esp__iexact=name).first() if name else None
        if cruce:
            raise forms.ValidationError(_('«%(nombre)s» ya es el nombre en español de «%(otro)s».') % {'nombre': name, 'otro': cruce.name})
        return name

    def clean_name_esp(self):
        """Opcional; si viene, único entre los nombres en español y sin chocar con el nombre de OTRO registro."""
        name_esp = ' '.join((self.cleaned_data.get('name_esp') or '').split())
        if not name_esp:
            return name_esp
        repetido = self.otros().filter(name_esp__iexact=name_esp).first()
        if repetido:
            raise forms.ValidationError(_('«%(nombre)s» ya es el nombre en español de «%(otro)s».') % {'nombre': name_esp, 'otro': repetido.name})
        cruce = self.otros().filter(name__iexact=name_esp).first()
        if cruce:
            raise forms.ValidationError(_('Ya existe un registro llamado «%(nombre)s».') % {'nombre': cruce.name})
        return name_esp

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
                _('Formato no permitido (%s). Usa %s.')
                % (ext or 'sin extensión', IMAGE_FORMATS))
        if image.size > IMAGE_MAX_MB * MB:
            raise forms.ValidationError(
                _('La imagen pesa %s MB; el máximo son %s MB.') % (round(image.size / MB, 1), IMAGE_MAX_MB))
        return image
