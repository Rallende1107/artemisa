"""Formularios de autenticación y registro."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, UserCreationForm, UsernameField
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import MaxLengthValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.models import CustomUser, UserActivity, UserLog
from apps.users.validators import normalizar_telefono_chileno, validate_min_age
from core.shared.models.choices import LogLevel
from core.utils.constants import IMAGE_ACCEPT, IMAGE_EXTENSIONS, IMAGE_FORMATS, IMAGE_HINT, IMAGE_MAX_MB, MB


# Movidos desde apps/system/forms.py: el modelo de usuario es de ESTA app, así
# que sus formularios de panel también. Los de arriba son los PÚBLICOS.


User = get_user_model()


class CustomUserForm(forms.ModelForm):
    """Alta de usuario hecha por el superusuario.

    La contraseña se pide aquí y se CIFRA en `save()` (nunca se guarda en claro).
    `is_superuser` no está: no se crean superusuarios desde el panel.
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'phone', 'birth_date', 'is_active', 'is_staff']

    username = forms.CharField(
        label=_('Usuario'),
        help_text=_('Solo letras, números y @ . + - _ (sin espacios).'),
        required=True, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('usuario'), 'aria-label': _('Usuario'), 'autocomplete': 'off',
            'maxlength': 150, 'required': 'required',
            'title': _('Solo letras, números y @ . + - _ (sin espacios).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 150 caracteres.'),
                        'invalid': _('Solo letras, números y @ . + - _ (sin espacios).')},
    )
    email = forms.EmailField(
        label=_('Correo electrónico'),
        help_text=_('Debe ser único: con él se recupera la contraseña.'),
        required=True, max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': _('correo@dominio.cl'), 'aria-label': _('Correo electrónico'),
            'autocomplete': 'off', 'inputmode': 'email', 'required': 'required',
            'title': _('Debe ser único: con él se recupera la contraseña.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid': _('Introduce una dirección de correo válida.')},
    )
    password = forms.CharField(
        label=_('Contraseña'),
        help_text=_('Mínimo 8 caracteres. Se guarda cifrada.'),
        required=True, min_length=8,
        widget=forms.PasswordInput(attrs={
            'aria-label': _('Contraseña'), 'autocomplete': 'new-password',
            'required': 'required', 'title': _('Mínimo 8 caracteres. Se guarda cifrada.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'min_length': _('Mínimo 8 caracteres.')},
    )
    first_name = forms.CharField(
        label=_('Nombre'), help_text=_('Nombre de pila (opcional).'),
        required=False, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 150, 'title': _('Nombre de pila (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 150 caracteres.')},
    )
    last_name = forms.CharField(
        label=_('Apellidos'), help_text=_('Apellidos (opcional).'),
        required=False, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Apellidos'), 'aria-label': _('Apellidos'), 'autocomplete': 'off',
            'maxlength': 150, 'title': _('Apellidos (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 150 caracteres.')},
    )
    phone = forms.CharField(
        label=_('Teléfono'), help_text=_('Teléfono de contacto (opcional).'),
        required=False, max_length=20, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('9 1234 5678'), 'aria-label': _('Teléfono'),
            'autocomplete': 'off', 'maxlength': 20, 'inputmode': 'tel',
            'title': _('Teléfono de contacto (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 20 caracteres.')},
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
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si se desmarca, el usuario queda bloqueado y no puede entrar.'),
        required=False, initial=True,          # el modelo trae default=True
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )
    is_staff = forms.BooleanField(
        label=_('Staff'),
        help_text=_('Marca esto para que pueda entrar al panel de gestión.'),
        required=False, initial=False,         # el modelo trae default=False
        widget=forms.CheckboxInput(attrs={'aria-label': _('Staff')}),
    )

    def clean_username(self):
        username = ' '.join((self.cleaned_data.get('username') or '').split())
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        """El correo es ÚNICO en el modelo: avisamos aquí en vez de reventar."""
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ese correo ya está registrado.')
        return email

    def clean_first_name(self):
        return ' '.join((self.cleaned_data.get('first_name') or '').split())

    def clean_last_name(self):
        return ' '.join((self.cleaned_data.get('last_name') or '').split())

    def clean_phone(self):
        return normalizar_telefono_chileno(self.cleaned_data.get('phone'))

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


def _telefono_sin_prefijo(valor):
    """Para PINTAR el campo: del canónico «+56 9 87654321» deja «9 87654321»
    (el +56 lo muestra la UI como prefijo fijo). Otros valores quedan tal cual."""
    v = (valor or "").strip()
    return v[4:] if v.startswith("+56 ") else v


class LoginForm(AuthenticationForm):
    """Login por usuario o correo."""
    # Mensajes propios (el de Django es largo y genérico). Cubren las dos claves
    # que usa AuthenticationForm: credenciales incorrectas y cuenta inactiva.
    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos. Revisa que estén bien "
                         "escritos (distinguen mayúsculas y minúsculas).",
        "inactive": "Tu cuenta está desactivada. Escríbenos si crees que es un error.",
    }
    username = UsernameField(
        label=_("Usuario o correo"),
        widget=forms.TextInput(attrs={
            "placeholder": _("tu_usuario o correo"),
            "autocomplete": "username",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"),
            "autocomplete": "current-password",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # AuthenticationForm.__init__ pisa max_length con el del modelo (150) DESPUÉS
        # de construir el campo, y ni siquiera agrega validación real (solo el
        # atributo HTML) — se fuerza acá, con validator real, para que 50 se cumpla.
        self.fields["username"].max_length = 50
        self.fields["username"].widget.attrs["maxlength"] = 50
        self.fields["username"].validators.append(MaxLengthValidator(50))
        # Mismo set permitido que el registro: letras, números y @/./+/-/_
        # (cubre usuario Y correo — cualquier email normal cae dentro de esto).
        self.fields["username"].validators.append(UnicodeUsernameValidator())


class PasswordChangeCustomForm(PasswordChangeForm):
    """Cambio de clave desde el PERFIL: pide la contraseña ACTUAL + la nueva (x2).
    Mismos widgets que SetPasswordCustomForm; el autofocus va en la actual."""
    old_password = forms.CharField(
        label=_("Contraseña actual"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"), "autocomplete": "current-password", "autofocus": True,
        }),
    )
    new_password1 = forms.CharField(
        label=_("Nueva contraseña"),
        strip=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"), "autocomplete": "new-password",
        }),
    )
    new_password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        strip=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"), "autocomplete": "new-password",
        }),
    )


class ProfileForm(forms.ModelForm):
    """Edición del propio perfil (datos personales)."""

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone", "birth_date", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": _("Nombre")}),
            "last_name": forms.TextInput(attrs={"placeholder": _("Apellido")}),
            "email": forms.EmailInput(attrs={"placeholder": _("correo@dominio.com")}),
            "phone": forms.TextInput(attrs={"placeholder": _("9 8765 4321"), "inputmode": "tel", "maxlength": "16"}),
            "birth_date": forms.DateInput(attrs={"type": "date", "class": "js-date", "data-min-age": "12"}),
            # FileInput simple: sin el chrome "Actualmente/Limpiar" de Django; el
            # UI (miniatura + Eliminar) lo pone la plantilla.
            "avatar": forms.FileInput,
        }

    # Checkbox propio «Eliminar» (en vez del "Clear/Limpiar" de ClearableFileInput):
    # borra la imagen actual del almacenamiento. La plantilla lo pinta junto al avatar.
    avatar_clear = forms.BooleanField(label=_("Eliminar"), required=False)

    # Datos de IDENTIDAD: el usuario los completa UNA vez; luego quedan fijos (solo
    # el staff los corrige desde gestión). Correo, teléfono y avatar sí se cambian.
    FIJOS_UNA_VEZ = ("first_name", "last_name", "birth_date")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El campo muestra SOLO el celular (9 dígitos); el +56 es un prefijo fijo de la UI.
        self.initial["phone"] = _telefono_sin_prefijo(self.initial.get("phone"))
        for nombre in self.FIJOS_UNA_VEZ:
            campo = self.fields.get(nombre)
            if campo is not None and self.instance.pk and getattr(self.instance, nombre, None):
                campo.disabled = True          # Django ignora el POST y conserva el valor
                campo.help_text = _("Dato fijado. Si hay que corregirlo, escríbenos por contacto.")

    def clean_birth_date(self):
        bd = self.cleaned_data.get("birth_date")
        validate_min_age(bd)  # permite None; rechaza <12 o fecha futura
        return bd

    def clean_phone(self):
        return normalizar_telefono_chileno(self.cleaned_data.get("phone"))

    def clean_avatar(self):
        """Mismo contrato que las imágenes del panel: extensión permitida y 10 MB."""
        avatar = self.cleaned_data.get("avatar")
        from django.core.files.uploadedfile import UploadedFile
        if not isinstance(avatar, UploadedFile):
            return avatar
        nombre = avatar.name or ""
        ext = ("." + nombre.rsplit(".", 1)[-1].lower()) if "." in nombre else ""
        if ext not in IMAGE_EXTENSIONS:
            raise forms.ValidationError(
                'Formato no permitido (%s). Usa %s.' % (ext or 'sin extensión', IMAGE_FORMATS))
        if avatar.size > IMAGE_MAX_MB * MB:
            raise forms.ValidationError(
                'La imagen pesa %s MB; el máximo son %s MB.' % (round(avatar.size / MB, 1), IMAGE_MAX_MB))
        return avatar

    def save(self, commit=True):
        """Si se marcó «Eliminar» (sin subir otra), vacía el avatar. El borrado
        FÍSICO del archivo anterior (al eliminar o reemplazar) lo hace el signal
        global `core.shared.models.file_cleanup` — aplica a todos los modelos."""
        instance = super().save(commit=False)
        if self.cleaned_data.get("avatar_clear") and not self.files.get("avatar"):
            instance.avatar = None
        if commit:
            instance.save()
        return instance


class RegisterForm(UserCreationForm):
    """Registro público: usuario, correo, contraseña + aceptación de términos."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email")

    username = UsernameField(
        label=_("Usuario"),
        max_length=50,
        widget=forms.TextInput(attrs={
            "placeholder": _("nombre_usuario"), "autocomplete": "username", "autofocus": True,
        }),
    )
    email = forms.EmailField(
        label=_("Correo electrónico"),
        required=True,
        max_length=250,   # bajo el tope real de la BD (254): nunca revienta al guardar
        widget=forms.EmailInput(attrs={
            "placeholder": _("correo@dominio.com"),
            "autocomplete": "email",
        }),
    )
    password1 = forms.CharField(
        label=_("Contraseña"),
        strip=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"), "autocomplete": "new-password",
        }),
    )
    password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        strip=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"), "autocomplete": "new-password",
        }),
    )
    acepto = forms.BooleanField(
        required=True,
        label=_("Acepto los términos y la política de privacidad"),
        error_messages={"required": _("Debes aceptar los términos y la privacidad para crear tu cuenta.")},
        widget=forms.CheckboxInput(attrs={"required": "required"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email


class ResetRequestForm(PasswordResetForm):
    """Pide el correo para enviar el enlace de restablecimiento."""
    email = forms.EmailField(
        label=_("Correo electrónico"),
        max_length=250,
        widget=forms.EmailInput(attrs={
            "placeholder": _("correo@dominio.com"), "autocomplete": "email", "autofocus": True,
        }),
    )

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        """Enruta el correo de reset por el sistema de mailing (plantilla editable
        'password_reset' + Email/EmailLog + master switch SEND_EMAIL), en vez de las
        plantillas de Django."""
        from django.urls import reverse
        from apps.mailing.services import send_templated
        path = reverse("users:password_reset_confirm",
                       kwargs={"uidb64": context["uid"], "token": context["token"]})
        enlace = f"{context['protocol']}://{context['domain']}{path}"
        send_templated("password_reset", to_email, {
            "usuario": context["user"].get_username(),
            "sitio": context.get("site_name") or "",
            "enlace": enlace,
        })


class SetPasswordCustomForm(SetPasswordForm):
    """Define la nueva contraseña (tras seguir el enlace del correo)."""
    new_password1 = forms.CharField(
        label=_("Nueva contraseña"),
        strip=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"), "autocomplete": "new-password", "autofocus": True,
        }),
    )
    new_password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        strip=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={
            "placeholder": _("••••••••"), "autocomplete": "new-password",
        }),
    )


class UserActivityForm(forms.ModelForm):
    """actividad de usuario: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = UserActivity
        fields = ['user', 'action', 'content_type', 'object_id', 'label', 'is_active']


class UserUpdateForm(forms.ModelForm):
    """Edición de un usuario por el superusuario.

    NO se edita aquí la contraseña (hay una acción «Resetear» aparte) ni
    `is_superuser` (por seguridad: no se otorga desde el panel).
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone',
                  'birth_date', 'avatar', 'is_active', 'is_staff']

    username = forms.CharField(
        label=_('Usuario'),
        help_text=_('Solo letras, números y @ . + - _ (sin espacios).'),
        required=True, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('usuario'), 'aria-label': _('Usuario'), 'autocomplete': 'off',
            'maxlength': 150, 'required': 'required',
            'title': _('Solo letras, números y @ . + - _ (sin espacios).'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'max_length': _('Máximo 150 caracteres.'),
                        'invalid': _('Solo letras, números y @ . + - _ (sin espacios).')},
    )
    email = forms.EmailField(
        label=_('Correo electrónico'),
        help_text=_('Debe ser único: con él se recupera la contraseña.'),
        required=True, max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': _('correo@dominio.cl'), 'aria-label': _('Correo electrónico'),
            'autocomplete': 'off', 'inputmode': 'email', 'required': 'required',
            'title': _('Debe ser único: con él se recupera la contraseña.'),
        }),
        error_messages={'required': _('Este campo es obligatorio.'),
                        'invalid': _('Introduce una dirección de correo válida.')},
    )
    first_name = forms.CharField(
        label=_('Nombre'), help_text=_('Nombre de pila (opcional).'),
        required=False, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Nombre'), 'aria-label': _('Nombre'), 'autocomplete': 'off',
            'maxlength': 150, 'title': _('Nombre de pila (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 150 caracteres.')},
    )
    last_name = forms.CharField(
        label=_('Apellidos'), help_text=_('Apellidos (opcional).'),
        required=False, max_length=150, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Apellidos'), 'aria-label': _('Apellidos'), 'autocomplete': 'off',
            'maxlength': 150, 'title': _('Apellidos (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 150 caracteres.')},
    )
    phone = forms.CharField(
        label=_('Teléfono'), help_text=_('Teléfono de contacto (opcional).'),
        required=False, max_length=20, strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('9 1234 5678'), 'aria-label': _('Teléfono'),
            'autocomplete': 'off', 'maxlength': 20, 'inputmode': 'tel',
            'title': _('Teléfono de contacto (opcional).'),
        }),
        error_messages={'max_length': _('Máximo 20 caracteres.')},
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
    avatar = forms.ImageField(
        label=_('Avatar'),
        help_text=_('Foto del usuario (opcional).'),
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'aria-label': _('Avatar'), 'accept': IMAGE_ACCEPT,
            'title': IMAGE_HINT,
        }),
        error_messages={'invalid_image': _('Envía una imagen válida.')},
    )
    is_active = forms.BooleanField(
        label=_('Activo'),
        help_text=_('Si se desmarca, el usuario queda bloqueado y no puede entrar.'),
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Activo')}),
    )
    is_staff = forms.BooleanField(
        label=_('Staff'),
        help_text=_('Marca esto para que pueda entrar al panel de gestión.'),
        required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'aria-label': _('Staff')}),
    )

    def clean_username(self):
        username = ' '.join((self.cleaned_data.get('username') or '').split())
        if username:
            otros = User.objects.filter(username__iexact=username)
            if self.instance.pk:
                otros = otros.exclude(pk=self.instance.pk)
            if otros.exists():
                raise forms.ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if email:
            otros = User.objects.filter(email__iexact=email)
            if self.instance.pk:
                otros = otros.exclude(pk=self.instance.pk)
            if otros.exists():
                raise forms.ValidationError('Ese correo ya está registrado.')
        return email

    def clean_first_name(self):
        return ' '.join((self.cleaned_data.get('first_name') or '').split())

    def clean_last_name(self):
        return ' '.join((self.cleaned_data.get('last_name') or '').split())

    def clean_phone(self):
        return normalizar_telefono_chileno(self.cleaned_data.get('phone'))

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        return birth_date

    def clean_avatar(self):
        """Solo revisamos lo que el usuario SUBE ahora (`UploadedFile`); si el campo
        trae el avatar ya guardado, se deja pasar sin tocar el almacenamiento."""
        avatar = self.cleaned_data.get('avatar')
        if not isinstance(avatar, UploadedFile):
            return avatar
        nombre = avatar.name or ''
        ext = ('.' + nombre.rsplit('.', 1)[-1].lower()) if '.' in nombre else ''
        if ext not in IMAGE_EXTENSIONS:
            raise forms.ValidationError(
                'Formato no permitido (%s). Usa %s.'
                % (ext or 'sin extensión', IMAGE_FORMATS))
        if avatar.size > IMAGE_MAX_MB * MB:
            raise forms.ValidationError(
                'La imagen pesa %s MB; el máximo son %s MB.' % (round(avatar.size / MB, 1), IMAGE_MAX_MB))
        return avatar


class UserLogForm(forms.ModelForm):
    """Log de usuarios: nivel, proceso, mensaje y activo. El Create existe por la regla 1:1:N (lo normal es que lo escriba el sistema)."""

    class Meta:
        model = UserLog
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
