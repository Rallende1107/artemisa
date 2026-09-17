"""
Modelo de usuario de Artemisa.

Versión limpia del CustomUser de Hades: conserva lo útil (avatar, teléfono,
fecha de nacimiento, slug, nombre para mostrar, rol) sin el acoplamiento a los
mixins/labels del framework de Hades. Autenticación por username o email.
"""
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseLog
from core.shared.models.choices import UserActivityAction


def avatar_upload_path(instance, filename):
    # Nombre ÚNICO por subida (sufijo aleatorio): al reemplazar, la URL cambia y el
    # navegador NO muestra la imagen cacheada. El archivo anterior lo borra el signal
    # global `core.shared.models.file_cleanup` (funciona con cualquier storage: local/R2/S3).
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webp"
    return f"users/avatars/{instance.username}-{uuid.uuid4().hex[:8]}.{ext}"


class CustomUser(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, AbstractUser):
    """Usuario del sitio. Hereda username/password/is_staff/is_superuser de
    AbstractUser y añade datos de perfil."""

    email = models.EmailField(verbose_name="correo electrónico", unique=True)
    phone = models.CharField(verbose_name="teléfono", max_length=20, blank=True)
    birth_date = models.DateField(verbose_name="fecha de nacimiento", null=True, blank=True)
    avatar = models.ImageField(verbose_name="avatar", upload_to=avatar_upload_path, blank=True)
    slug = models.SlugField(verbose_name="slug", max_length=150, unique=True, blank=True, editable=False)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["-created_at", "username"]

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        old = CustomUser.objects.filter(pk=self.pk).first() if self.pk else None

        # Slug automático desde el username (o si el username cambió).
        if not self.slug or (old and self.username != old.username):
            self.slug = slugify(self.username)

        # (El borrado del avatar anterior lo hace el signal global file_cleanup.)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("users:profile")

    # --- Propiedades de presentación ---
    @property
    def get_full_name_display(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or ""

    @property
    def display_name(self):
        full = self.get_full_name_display
        return f"{self.username} ({full})" if full else self.username

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else None

    @property
    def age(self):
        """Edad en años cumplidos a partir de birth_date (None si no hay fecha)."""
        if not self.birth_date:
            return None
        from datetime import date
        t = date.today()
        return t.year - self.birth_date.year - ((t.month, t.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def role(self):
        if self.is_superuser and self.is_staff:
            return "Superadmin"
        if self.is_superuser:
            return "Superusuario"
        if self.is_staff:
            return "Staff"
        return "Miembro"


class UserActivity(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """ACTIVIDAD del usuario (lo que él HACE y ve en su cuenta): NO es un log y NO se purga (R9). `UserLog` es lo que le
    pasa al sistema con las cuentas y sí se purga. `label` guarda el texto del objeto por si este desaparece."""

    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="activities", verbose_name="usuario")
    action = models.CharField(verbose_name="acción", max_length=30, choices=UserActivityAction.choices)
    content_type = models.ForeignKey(
        "contenttypes.ContentType", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="user_activities", verbose_name="tipo de objeto")
    object_id = models.PositiveIntegerField(verbose_name="id del objeto", null=True, blank=True)
    label = models.CharField(verbose_name="objeto", max_length=255, blank=True)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "actividad de usuario"
        verbose_name_plural = "actividad de usuarios"
        ordering = ["-created_at"]

    def __str__(self):
        if self.action in (UserActivityAction.PROFILE, UserActivityAction.PASSWORD) and self.label:      # la frase ya describe el cambio
            return f"{self.user} {self.label}"
        return f"{self.user} {self.get_action_display()}" + (f": {self.label}" if self.label else "")

    @property
    def frase(self):
        return str(self)


class UserLog(ModelBaseLog):
    """Log de actividad de cuentas: qué pasó (`process`) y a quién (`user`).
    `actor` es quién lo hizo (puede ser el propio `user`, otro con permisos,
    o None si vino de un origen sin request — shell, /admin/, etc.)."""
    user = models.ForeignKey(
        "users.CustomUser", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="logs", verbose_name="usuario")
    actor = models.ForeignKey(
        "users.CustomUser", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="acciones_realizadas", verbose_name="realizado por")

    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de usuarios"
        verbose_name_plural = "logs de usuarios"
