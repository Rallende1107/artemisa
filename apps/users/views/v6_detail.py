"""users · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.users.views.base import BaseCustomUser, BaseUserActivity, BaseUserLog
from core.shared.views.base import BaseAdminDetailView


# ==============================================================================
# Gestión
# ==============================================================================

USER_DETAIL = [("Usuario", "username"), ("Correo", "email"),
               ("Nombre", "first_name"), ("Apellido", "last_name"),
               ("Teléfono", "phone"), ("Nacimiento", "birth_date"),
               ("Staff", "is_staff"), ("Superusuario", "is_superuser"),
               ("Activo", "is_active"), ("Alta", "date_joined")]


class CustomUserDetailView(BaseCustomUser, BaseAdminDetailView):
    update_url = "panel:user_update"
    delete_url = "panel:user_delete"
    list_url = "panel:user_list"
    toggle_url = "panel:user_toggle"
    detail_fields = USER_DETAIL
    template_name = "admin_panel/usuario_detail.html"


class UserActivityDetailView(BaseUserActivity, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:user-activity_list"
    delete_url = "panel:user-activity_delete"
    detail_fields = [(_("Usuario"), "user"), (_("Acción"), "get_action_display"), (_("Objeto"), "label"),
                     (_("Momento"), "display_created"), (_("Activo"), "display_is_active")]


class UserLogDetailView(BaseUserLog, BaseAdminDetailView):
    template_name = "users/detail/user_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    """Ficha MÍNIMA de un registro de actividad (solo lectura: sin editar ni borrar)."""
    list_url = "panel:user-log_list"
