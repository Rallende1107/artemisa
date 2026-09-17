"""users · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.users.models import CustomUser, UserActivity, UserLog
from apps.users.views.base import BaseCustomUser, BaseUserActivity, BaseUserLog
from core.shared.views.base import AdminDataView, BaseSelectView
from core.shared.views.filters import BaseFilters, BooleanFilter, ChoiceFilter, LogFilters
from core.utils.views_base import cell


# ==============================================================================
# Gestión
# ==============================================================================

USER_COLUMNS = [("Usuario", "username"), ("Correo", "email"),
                ("Staff", "is_staff"), ("Super", "is_superuser"), ("Alta", "date_joined"), ("Activo", "is_active")]


class CustomUserDataView(BaseCustomUser, AdminDataView):
    columns = USER_COLUMNS

    def get(self, request, tipo=None, pk=None):
        qs = CustomUser.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ["username", "email", "first_name", "last_name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "username"),
                "c1": cell(obj, "email"),
                "c2": cell(obj, "is_staff"),
                "c3": cell(obj, "is_superuser"),
                "c4": cell(obj, "date_joined"),
                "c5": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

    def extra_row_actions(self, obj, request):
        # Gestionar usuarios = solo superuser (mismo candado que los toggles).
        if not request.user.is_superuser:
            return []
        url = reverse("panel:user_reset", args=[obj.pk])
        return [f'<a role="menuitem" href="{url}">'
                f'<i class="bi bi-key ic"></i> Resetear contraseña</a>']


class CustomUserSelectView(BaseCustomUser, BaseSelectView):
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def option_label(self, obj):
        """«usuario · Nombre Apellido»: se busca por cualquiera de los dos."""
        full = f"{obj.first_name} {obj.last_name}".strip()
        return f"{obj.username} · {full}" if full and full.lower() != obj.username.lower() else obj.username


class ActividadFilters(BaseFilters):
    generic_filters = [BooleanFilter("is_active", _("Activo"))]
    include_filters = [ChoiceFilter("action", _("Acción"))]


class UserActivityDataView(BaseUserActivity, AdminDataView):
    """Actividad de los usuarios (lo que HACEN): filtrable por usuario (?user=<id>)."""
    columns = [(_("Usuario"), "user"), (_("Acción"), "frase"), (_("Momento"), "created_at"), (_("Activo"), "is_active")]
    filters = ActividadFilters

    def get(self, request, tipo=None, pk=None):
        qs = UserActivity.objects.all()
        qs = qs.select_related("user")
        user_id = self.request.GET.get("user")
        qs = qs.filter(user_id=user_id) if user_id else qs
        p, total, filtrado, objetos = self.query(request, qs, ["label", "action", "user__username", "user__first_name", "user__last_name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "frase"),
                "c2": cell(obj, "created_at"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class UserLogDataView(BaseUserLog, AdminDataView):
    """Log de usuarios (lo que le pasa al SISTEMA con las cuentas)."""
    columns = [(_("Usuario"), "user"), (_("Realizado por"), "actor"), (_("Proceso"), "process"), (_("Momento"), "timestamp")]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = UserLog.objects.select_related("user", "actor")
        p, total, filtrado, objetos = self.query(request, qs, ["process", "message", "user__username", "user__first_name", "user__last_name", "actor__username", "actor__first_name", "actor__last_name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "actor"),
                "c2": cell(obj, "process"),
                "c3": cell(obj, "timestamp"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)
