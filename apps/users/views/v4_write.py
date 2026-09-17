"""users · ESCRITURA de gestión: crear, editar y eliminar."""
from django import forms
from django.shortcuts import get_object_or_404, render
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.users import forms as f
from apps.users.notifications import notify_user_action
from apps.users.views.base import BaseCustomUser, BaseUserActivity, BaseUserLog, User
from core.mixin.access import SuperuserRequiredMixin
from core.shared.views.base import BaseCreate, BaseDelete, BaseSoftDelete, BaseUpdate
from core.utils.views import resolve_background


# ==============================================================================
# Gestión
# ==============================================================================


class CustomUserCreateView(SuperuserRequiredMixin, BaseCustomUser, BaseCreate):
    # Django core
    form_class = f.CustomUserForm
    form_template = "users/form/custom_user.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    # Navegación
    section_url = "panel:users-home"
    section_label = _("Usuarios")
    list_url = "panel:user_list"
    success_url = "panel:user_list"
    cancel_url = "panel:user_list"
    # UX
    success_message = _("Usuario «%(obj)s» creado.")
    title = _("Crear usuario")

    def form_valid(self, response):
        response.instance._actor = self.request.user   # leído por la señal de UserLog
        out = super().form_valid(response)
        notify_user_action(self.object, "created", actor=self.request.user)
        return out


class CustomUserUpdateView(SuperuserRequiredMixin, BaseCustomUser, BaseUpdate):
    # Django core
    form_class = f.UserUpdateForm
    form_template = "users/form/custom_user.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    # Navegación
    section_url = "panel:users-home"
    section_label = _("Usuarios")
    list_url = "panel:user_list"
    success_url = "panel:user_list"
    cancel_url = "panel:user_list"
    # UX
    success_message = _("Usuario «%(obj)s» actualizado.")
    title = _("Editar usuario")

    def form_valid(self, form):
        form.instance._actor = self.request.user   # leído por la señal de UserLog
        return super().form_valid(form)


class UserResetPasswordView(SuperuserRequiredMixin, BaseCustomUser, View):
    """Fija una nueva contraseña al usuario y la MUESTRA una vez (no hay correo)."""
    title = _("Resetear contraseña")

    def get(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        return self._render(request, target, UserResetPasswordForm())

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        form = UserResetPasswordForm(request.POST)
        if not form.is_valid():
            return self._render(request, target, form)
        pwd = form.cleaned_data.get("new_password") or get_random_string(12)
        target.set_password(pwd)
        target._actor = request.user   # leído por la señal de UserLog
        target.save(update_fields=["password"])
        notify_user_action(target, "password_reset", actor=request.user)
        return self._render(request, target, UserResetPasswordForm(), new_password=pwd)

    def _render(self, request, target, form, new_password=None):
        ctx = {
            "target": target, "form": form, "new_password": new_password,
            "background_image": resolve_background(self),
            "page_title": self.title, "active_entity": "user",
            "section_url": "panel:users-home", "section_label": "Usuarios",
        }
        return render(request, "admin_panel/usuario_reset.html", ctx)


class CustomUserDeleteView(SuperuserRequiredMixin, BaseCustomUser, BaseDelete):
    success_url = "panel:user_list"
    cancel_url = "panel:user_list"
    success_message = _("Usuario «%(obj)s» eliminado.")
    title = _("Eliminar usuario")
    list_url = "panel:user_list"
    def form_valid(self, response):
        notify_user_action(self.object, "deleted", actor=self.request.user)
        return super().form_valid(response)


class UserActivityDeleteView(BaseUserActivity, BaseSoftDelete):
    list_url = "panel:user-activity_list"
    success_url = "panel:user-activity_list"
    cancel_url = "panel:user-activity_list"
    success_message = _("Actividad «%(obj)s» desactivada.")
    title = _("Desactivar actividad")


class UserActivityCreateView(BaseUserActivity, BaseCreate):
    form_class = f.UserActivityForm
    list_url = "panel:user-activity_list"
    success_url = "panel:user-activity_list"
    cancel_url = "panel:user-activity_list"
    success_message = _("Actividad de usuario «%(obj)s» creado.")
    title = _("Crear actividad de usuario")


class UserActivityUpdateView(BaseUserActivity, BaseUpdate):
    form_class = f.UserActivityForm
    list_url = "panel:user-activity_list"
    success_url = "panel:user-activity_list"
    cancel_url = "panel:user-activity_list"
    success_message = _("Actividad de usuario «%(obj)s» actualizado.")
    title = _("Editar actividad de usuario")


class UserResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="Nueva contraseña", required=False, widget=forms.PasswordInput,
        help_text="Déjala vacía para generar una automáticamente.")


class UserLogCreateView(BaseUserLog, BaseCreate):
    form_class = f.UserLogForm
    form_template = "users/form/user_log.html"
    list_url = "panel:user-log_list"
    success_url = "panel:user-log_list"
    cancel_url = "panel:user-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class UserLogUpdateView(BaseUserLog, BaseUpdate):
    form_class = f.UserLogForm
    form_template = "users/form/user_log.html"
    list_url = "panel:user-log_list"
    success_url = "panel:user-log_list"
    cancel_url = "panel:user-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class UserLogDeleteView(BaseUserLog, BaseDelete):
    list_url = "panel:user-log_list"
    success_url = "panel:user-log_list"
    cancel_url = "panel:user-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
