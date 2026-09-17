"""users · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.users.models import CustomUser
from apps.users.views.base import BaseCustomUser, BaseUserActivity, BaseUserLog
from core.shared.views.base import AdminListView


# ==============================================================================
# Gestión
# ==============================================================================


class CustomUserListView(BaseCustomUser, AdminListView):
    home_url = "panel:users-home"
    data_url = "panel:user_data"
    create_url = "panel:user_create"
    title = _("Lista de usuarios")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_create"] = self.request.user.is_superuser  # solo superuser crea
        return ctx


def _etiqueta_usuario(u):
    """«usuario · Nombre Apellido» (lo mismo que pinta el Select2 de usuarios)."""
    full = f"{u.first_name} {u.last_name}".strip()
    return f"{u.username} · {full}" if full and full.lower() != u.username.lower() else u.username


class UserActivityListView(BaseUserActivity, AdminListView):
    home_url = "panel:users-home"
    data_url = "panel:user-activity_data"
    title = _("Lista de actividad de usuarios")
    template_name = "users/usuario_log_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Filtro por usuario (?user=<id>): solo se resuelve el elegido para preseleccionarlo
        # en el Select2 remoto; la búsqueda de usuarios la hace panel:user_select.
        actual = self.request.GET.get("user", "")
        obj = CustomUser.objects.filter(pk=actual).first() if actual.isdigit() else None
        ctx["usuario_actual_obj"] = obj
        ctx["usuario_actual_texto"] = _etiqueta_usuario(obj) if obj else ""
        if obj:
            ctx["data_url"] = reverse("panel:user-activity_data") + f"?user={obj.pk}"
        return ctx


# Vistas FIJAS de «usuario-log» (una URL, una card y un fondo por cada una; sin filtros en página).


class UserLogListView(BaseUserLog, AdminListView):
    home_url = "panel:users-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:user-log_data"
    create_url = "panel:user-log_create"
    title = _("Lista de log de usuarios")
    background_image = "bg-users-log"
    background_fallback = ("bg-users-log", "bg-users-home")
    template_name = "admin_panel/list.html"   # el log completo: sin el selector de usuario
