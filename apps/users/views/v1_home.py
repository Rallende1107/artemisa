"""users · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from core.shared.views.base import BaseHomeView


# ==============================================================================
# Gestión
# ==============================================================================


class UsersHomeView(BaseHomeView):
    title = _("Usuarios")
    active_entity = "usuario-home"
    background_image = "bg-users-home"
    background_fallback = "bg-users-home"   # respaldo si falta la imagen
    # Cada card = (entidad, etiqueta, icono, FONDO). El fondo es la clase bg-… de ESA card
    # (static/image/screen/wide/<clase>.webp); si el .webp no existe, cae al fondo de la sección.
    # Sin modelo ni conteo: el home solo navega (nada de COUNT(*) sobre tablas grandes).
    groups = [
        (_("Usuarios"), [
            ("user", _("Usuarios"), '<i class="bi bi-people"></i>', "bg-users-user"),
        ]),
        (_("Registro"), [
            ("user-activity", _("Actividad de usuarios"), '<i class="bi bi-activity"></i>', "bg-users-user-activity"),
            ("user-log", _("Log de usuarios"), '<i class="bi bi-journal-text"></i>', "bg-users-log"),
        ]),
    ]
