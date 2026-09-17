"""Formularios del panel para `mailing` — UNO POR MODELO, AUTÓNOMOS.

Regla del proyecto: cada modelo tiene su formulario propio y completo. Heredan de
`forms.ModelForm` de Django y punto. ÚNICA excepción: las categorías (`ModelBaseCategory`)
heredan `core.shared.forms.base.FormBaseCategory` (nombre, nombre ES, descripción, imagen, activo).
Todo lo que hace el formulario está escrito AQUÍ (campos, widgets, attrs,
mensajes de error y cada `clean_<campo>` con sus reglas).

`EmailMessage` (la bandeja) y `EmailLog` (el log) no tienen formulario a propósito: son registros.
Se consulta, se reenvía y se borra, pero no se escribe a mano.
"""
from django import forms
from django.template import Template, TemplateSyntaxError
from django.utils.translation import gettext_lazy as _

from apps.mailing.models import ContactMessage, ContactReply, EmailLog, EmailMessage, EmailTemplate, MailConfig
from core.shared.forms.widgets import AjaxSelect
from core.shared.models.choices import ContactMessageStatus, LogLevel


class ContactMessageForm(forms.ModelForm):
    """Mensaje de contacto: el staff solo cambia el ESTADO (NEW/READ/REPLIED/
    ARCHIVED/SPAM). El resto del mensaje llega del formulario público y no se edita."""

    class Meta:
        model = ContactMessage
        fields = ['status']

    status = forms.ChoiceField(
        label=_('Estado'),
        help_text=_('En qué punto de la gestión está este mensaje.'),
        required=True,
        choices=ContactMessageStatus.choices,
        widget=forms.Select(attrs={
            'aria-label': _('Estado'), 'required': 'required',
            'title': _('En qué punto de la gestión está este mensaje.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )


# Movido desde apps/system/forms.py: el contacto es correo, así que su gestión
# vive en mailing, incluido el modelo.


class ContactReplyForm(forms.ModelForm):
    """Respuesta del staff a un mensaje de contacto (hilo de «Mis mensajes»)."""

    class Meta:
        model = ContactReply
        fields = ['message', 'body', 'is_active']

    message = forms.ModelChoiceField(
        label=_('Mensaje'),
        help_text=_('Qué mensaje de contacto respondes. Escribe para buscar.'),
        required=True, queryset=None, empty_label=_('—'),
        widget=AjaxSelect(url_name='panel:contact-message_select', attrs={
            'aria-label': _('Mensaje'), 'required': 'required',
            'title': _('Qué mensaje de contacto respondes. Escribe para buscar.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid_choice': _('Selecciona una opción válida.')},
    )
    body = forms.CharField(
        label=_('Respuesta'),
        help_text=_('Lo que verá quien escribió (en «Mis mensajes» si es usuario registrado).'),
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': _('Respuesta'), 'aria-label': _('Respuesta'), 'rows': 6,
            'required': 'required', 'title': _('Texto de la respuesta.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    is_active = forms.BooleanField(
        label=_('Activa'),
        help_text=_('Si está activa, el usuario la ve en su hilo.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activa')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].queryset = ContactMessage.objects.filter(is_active=True)


class EmailMessageForm(forms.ModelForm):
    """correo: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = EmailMessage
        fields = ['template', 'to_email', 'subject', 'body', 'context', 'status', 'error']


class EmailTemplateForm(forms.ModelForm):
    """Plantilla de un correo: asunto + cuerpo editables desde el panel.

    Asunto y cuerpo admiten variables de plantilla Django (`{{ usuario }}`,
    `{{ enlace }}`…). Se validan aquí para que un `{% if %}` mal cerrado se avise
    al guardar y no reviente meses después, al intentar enviar el correo.
    """

    class Meta:
        model = EmailTemplate
        fields = ['key', 'name', 'subject', 'body_html', 'body_text', 'description', 'is_active']

    key = forms.SlugField(
        label=_('Clave'),
        help_text=_('Identificador para el código: password_reset, contact_ack, welcome…'),
        required=True, max_length=60, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('password_reset'), 'aria-label': _('Clave'), 'autocomplete': 'off',
            'maxlength': 60, 'required': 'required',
            'title': _('Identificador para el código: password_reset, contact_ack, welcome…'),
        }),
        error_messages={
            'required': _('Este campo es obligatorio.'),
            'max_length': _('Máximo 60 caracteres.'),
            'invalid': _('Solo letras, números, guiones y guiones bajos (sin espacios ni acentos).'),
        },
    )
    name = forms.CharField(
        label=_('Nombre'),
        help_text=_('Nombre visible de la plantilla en el listado.'),
        required=True, max_length=120, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 120, 'required': 'required',
            'title': _('Nombre visible de la plantilla en el listado.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 120 caracteres.')},
    )
    subject = forms.CharField(
        label=_('Asunto'),
        help_text=_('Admite variables: {{ usuario }}'),
        required=True, max_length=255, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Asunto'), 'aria-label': _('Asunto'), 'autocomplete': 'off',
            'maxlength': 255, 'required': 'required',
            'title': _('Admite variables: {{ usuario }}'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 255 caracteres.')},
    )
    body_html = forms.CharField(
        label=_('Cuerpo (HTML)'),
        help_text=_('Admite variables Django: {{ enlace }}'),
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': _('<p>Hola {{ usuario }}…</p>'), 'aria-label': _('Cuerpo (HTML)'),
            'autocomplete': 'off', 'rows': 12, 'spellcheck': 'false', 'required': 'required',
            'title': _('Admite variables Django: {{ enlace }}'),
        }),
        error_messages={'required': _('Este campo es obligatorio.')},
    )
    body_text = forms.CharField(
        label=_('Cuerpo (texto plano)'),
        help_text=_('Alternativa sin formato. Si se deja vacío se deriva del HTML.'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Hola {{ usuario }}…'), 'aria-label': _('Cuerpo (texto plano)'),
            'autocomplete': 'off', 'rows': 8, 'spellcheck': 'false',
            'title': _('Alternativa sin formato. Si se deja vacío se deriva del HTML.'),
        }),
    )
    description = forms.CharField(
        label=_('Notas / variables disponibles'),
        help_text=_('Para acordarte de qué variables acepta esta plantilla (opcional).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Variables: {{ usuario }}, {{ enlace }}…'),
            'aria-label': _('Notas / variables disponibles'), 'autocomplete': 'off', 'rows': 4,
            'title': _('Para acordarte de qué variables acepta esta plantilla (opcional).'),
        }),
    )
    is_active = forms.BooleanField(
        label=_('Activa'),
        help_text=_('Solo se envían las plantillas activas. Desmárcala en vez de borrarla.'),
        required=False, initial=True,          # el modelo trae default=True
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activa')}),
    )

    def clean_key(self):
        """La clave es la que busca el código al enviar (`send_templated('welcome', …)`),
        así que la normalizamos a minúsculas y avisamos si ya está usada."""
        key = (self.cleaned_data.get('key') or '').strip().lower()
        if not key:
            return key
        duplicadas = EmailTemplate.objects.filter(key=key)
        if self.instance.pk:
            duplicadas = duplicadas.exclude(pk=self.instance.pk)
        if duplicadas.exists():
            raise forms.ValidationError('Ya existe una plantilla con esta clave.')
        return key

    def clean_name(self):
        return ' '.join((self.cleaned_data.get('name') or '').split())

    def clean_subject(self):
        """El asunto viaja en una sola línea y se renderiza como plantilla Django."""
        subject = ' '.join((self.cleaned_data.get('subject') or '').split())
        try:
            Template(subject)
        except TemplateSyntaxError as exc:
            raise forms.ValidationError('Hay un error en las variables del asunto: %s' % exc)
        return subject

    def clean_body_html(self):
        body = (self.cleaned_data.get('body_html') or '').strip()
        try:
            Template(body)
        except TemplateSyntaxError as exc:
            raise forms.ValidationError('Hay un error en las variables del cuerpo: %s' % exc)
        return body

    def clean_body_text(self):
        body = (self.cleaned_data.get('body_text') or '').strip()
        if body:
            try:
                Template(body)
            except TemplateSyntaxError as exc:
                raise forms.ValidationError('Hay un error en las variables del cuerpo: %s' % exc)
        return body

    def clean_description(self):
        return (self.cleaned_data.get('description') or '').strip()


class MailConfigForm(forms.ModelForm):
    """Configuración de correo (singleton, pk=1). Config MÍNIMA: solo el interruptor
    de envío y la firma del pie. El SMTP (host, puerto, usuario, contraseña, TLS)
    vive en el `.env`, no se edita desde el panel."""

    class Meta:
        model = MailConfig
        fields = ['send_email', 'signature']

    send_email = forms.BooleanField(
        label=_('Enviar correos'),
        help_text=_('Master switch. Apagado → los correos quedan EN COLA (se reenvían luego).'),
        required=False, initial=False,         # el modelo trae default=False
        widget=forms.CheckboxInput(attrs={'aria-label': _('Enviar correos')}),
    )
    signature = forms.CharField(
        label=_('Firma'),
        help_text=_('Se añade al pie de TODOS los correos. Admite HTML (enlaces, negritas…).'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('<p>— El equipo de Frikiverso</p>'), 'aria-label': _('Firma'),
            'autocomplete': 'off', 'rows': 6, 'spellcheck': 'false',
            'title': _('Se añade al pie de TODOS los correos. Admite HTML (enlaces, negritas…).'),
        }),
    )

    def clean_signature(self):
        """La firma se pega tal cual al pie de cada correo; se valida como plantilla
        por si alguien mete una variable mal escrita."""
        signature = (self.cleaned_data.get('signature') or '').strip()
        if signature:
            try:
                Template(signature)
            except TemplateSyntaxError as exc:
                raise forms.ValidationError('Hay un error en las variables de la firma: %s' % exc)
        return signature


class EmailLogForm(forms.ModelForm):
    """Log de correo: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = EmailLog
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
