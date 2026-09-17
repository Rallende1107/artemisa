"""BASE de la sección Usuarios del panel: config de la entidad + columnas.

La clase privada `BaseCustomUser` es la ÚNICA fuente de config compartida (modelo,
slug, etiquetas, fondo). Las vistas de los módulos vN_*.py la heredan como
PRIMER mixin — estilo Poseidon.
"""
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.users.models import CustomUser, UserActivity, UserLog


User = get_user_model()


# "Activo" (is_active) se declara aquí como cualquier columna: nadie la añade por detrás.


class _Users:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = "bg-system-home"   # respaldo si falta la imagen
    section_url = "panel:users-home"
    section_label = _("Usuarios")


class BaseCustomUser(_Users):
    model = CustomUser
    entity = "user"
    label = _("usuario")
    label_plural = _("usuarios")
    background_image = "bg-users-user"


class BaseUserActivity(_Users):
    model = UserActivity
    entity = "user-activity"
    label = _("actividad")
    label_plural = _("actividad de usuarios")
    background_image = "bg-users-user-activity"
    background_fallback = ("bg-users-log", "bg-users-home")


class BaseUserLog(_Users):
    model = UserLog
    entity = "user-log"
    label = _("log de usuarios")
    label_plural = _("logs de usuarios")
    background_image = "bg-users-log"
    background_fallback = "bg-users-home"   # respaldo si falta la imagen
    namespace = "panel"
