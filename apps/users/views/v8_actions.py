"""users · acciones POST y páginas «a mano», de gestión y públicas."""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.formats import date_format
from django.utils.html import escape
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.users.forms import LoginForm, PasswordChangeCustomForm, ProfileForm, RegisterForm, ResetRequestForm, SetPasswordCustomForm
from apps.users.models import UserActivity
from core.shared.models.choices import UserActivityAction
from core.utils.views import resolve_background


# ==============================================================================
# Público
# ==============================================================================

class _CuentaPage:
    """Pasa el FONDO al contexto (como el resto del front) — se define en la VISTA,
    no en el HTML. Cambia `background_image` aquí para cambiar el fondo de la cuenta."""
    background_image = "bg-users-user"   # existe; cámbialo por uno propio cuando lo tengas
    background_fallback = "bg-users-user"   # respaldo si falta la imagen
    title = ""                            # el TÍTULO también en la vista, no en el HTML

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("background_image", resolve_background(self))
        ctx.setdefault("page_title", self.title)
        return ctx


class BaseActivity(_CuentaPage):
    """Página de cuenta con el fondo de ACTIVIDAD: hereda de _CuentaPage (que es
    quien pasa fondo y título al contexto) y solo cambia el fondo."""
    background_image = "bg-users-log"   # existe; cámbialo por uno propio cuando lo tengas
    background_fallback = "bg-users-home"   # respaldo si falta la imagen


class LoginView(_CuentaPage, auth_views.LoginView):
    title = _("Ingresar")
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    """Cierra sesión y redirige a LOGOUT_REDIRECT_URL."""


class RegisterView(_CuentaPage, CreateView):
    title = _("Crear cuenta")
    template_name = "users/registro.html"
    form_class = RegisterForm
    success_url = reverse_lazy("pages:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("pages:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance._actor = form.instance   # alta = actividad propia (self-registro)
        response = super().form_valid(form)
        # Auto-login tras registrarse (backend explícito por haber varios).
        login(self.request, self.object,
              backend="apps.users.backends.EmailOrUsernameBackend")
        # Correo de bienvenida (respeta SEND_EMAIL; a consola en dev).
        from django.conf import settings
        from apps.mailing.services import send_templated
        if self.object.email:
            send_templated("bienvenida", self.object.email, {
                "usuario": self.object.username,
                "sitio": settings.SITE_NAME,
                "enlace": self.request.build_absolute_uri("/"),
            })
        return response


class ProfileView(_CuentaPage, LoginRequiredMixin, TemplateView):
    title = _("Mi perfil")
    template_name = "users/perfil.html"


class ProfileUpdateView(_CuentaPage, LoginRequiredMixin, UpdateView):
    """Edición del propio perfil (misma página no; página aparte, patrón CRUD)."""
    title = _("Editar perfil")
    form_class = ProfileForm
    template_name = "users/perfil_editar.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance._actor = self.request.user
        resp = super().form_valid(form)
        # Toast ESPECÍFICO: qué cambió y, para el teléfono, cómo quedó.
        cambios = []
        for f in form.changed_data:
            if f == "avatar_clear":
                continue
            if f == "phone":
                # El campo pinta el número SIN el +56, así que has_changed da
                # falso positivo: compara los canónicos antes de anunciarlo.
                from django.core.exceptions import ValidationError as _VE
                from apps.users.validators import normalizar_telefono_chileno
                try:
                    antes = normalizar_telefono_chileno(form.initial.get("phone") or "")
                except _VE:
                    antes = form.initial.get("phone") or ""
                if antes == (form.instance.phone or ""):
                    continue
                cambios.append(f"teléfono → {form.instance.phone or '—'}")
            else:
                cambios.append(str(form.fields[f].label or f).lower())
        if cambios:
            messages.success(self.request, "Perfil actualizado: " + ", ".join(cambios) + ".")
        else:
            messages.info(self.request, "No había cambios que guardar.")
        return resp


class MyActivityView(BaseActivity, LoginRequiredMixin, TemplateView):
    """SHELL de Mi actividad: las filas las trae DataTables por AJAX desde
    MyActivityPublicDataView (server-side). Solo actividad REAL de la cuenta (cambios de
    contraseña/correo/teléfono/perfil, activación, permisos…)."""
    title = _("Mi actividad")
    template_name = "users/actividad.html"


class MyActivityPublicDataView(LoginRequiredMixin, View):
    """Endpoint JSON server-side (protocolo DataTables) de Mi actividad: busca, ordena y pagina en BD SOLO la
    ACTIVIDAD del usuario logueado (UserActivity: no se purga). Los inicios/cierres de sesión no se muestran (ruido)."""
    login_url = "users:login"

    ORDER_FIELDS = {0: "action", 2: "created_at"}

    def get(self, request):
        p = request.GET
        try:
            draw = int(p.get("draw", 1))
            start = int(p.get("start", 0))
            length = int(p.get("length", 15))
        except (TypeError, ValueError):
            draw, start, length = 1, 0, 15
        if length < 0 or length > 200:
            length = 15

        qs = UserActivity.objects.filter(user=request.user, is_active=True).exclude(action__in=(UserActivityAction.LOGIN, UserActivityAction.LOGOUT))
        total = qs.count()

        q = (p.get("search[value]") or "").strip()
        if q:
            qs = qs.filter(label__icontains=q)
        filtered = qs.count()

        try:
            idx = int(p.get("order[0][column]", 2))
        except (TypeError, ValueError):
            idx = 2
        campo = self.ORDER_FIELDS.get(idx, "created_at")
        if p.get("order[0][dir]", "desc") == "desc":
            campo = "-" + campo
        qs = qs.order_by(campo)

        rows = [{
            "c0": escape(a.label if a.action in (UserActivityAction.PROFILE, UserActivityAction.PASSWORD) and a.label else f"{a.get_action_display()}" + (f": {a.label}" if a.label else "")),
            "c1": "Tú",
            "c2": date_format(localtime(a.created_at), "d M Y, H:i:s"),
            "acciones": "",
        } for a in qs[start:start + length]]
        return JsonResponse({"draw": draw, "recordsTotal": total,
                             "recordsFiltered": filtered, "data": rows})


class PasswordChangeView(_CuentaPage, auth_views.PasswordChangeView):
    """Cambio de clave del PROPIO usuario (desde el perfil): pide la ACTUAL y la
    nueva. La base de Django ya mantiene la sesión viva (update_session_auth_hash)."""
    template_name = "users/perfil_clave.html"
    form_class = PasswordChangeCustomForm
    success_url = reverse_lazy("users:profile")
    title = _("Cambiar contraseña")

    def form_valid(self, form):
        form.user._actor = self.request.user   # leído por la señal de UserLog
        resp = super().form_valid(form)
        # Aviso de seguridad (misma plantilla que el reset por correo).
        from apps.mailing.services import send_templated
        if form.user.email:
            send_templated("password_changed", form.user.email, {
                "usuario": form.user.get_username(),
                "sitio": settings.SITE_NAME,
            })
        messages.success(self.request, "Contraseña actualizada.")
        return resp


class PasswordResetView(_CuentaPage, auth_views.PasswordResetView):
    """1) Pide el correo y envía el enlace."""
    title = _("Recuperar contraseña")
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    form_class = ResetRequestForm
    success_url = reverse_lazy("users:password_reset_done")
    extra_email_context = {"site_name": settings.SITE_NAME}


class PasswordResetDoneView(_CuentaPage, auth_views.PasswordResetDoneView):
    """2) "Revisa tu correo"."""
    title = _("Revisa tu correo")
    template_name = "registration/password_reset_done.html"


class PasswordResetConfirmView(_CuentaPage, auth_views.PasswordResetConfirmView):
    """3) Define la nueva contraseña (desde el enlace del correo)."""
    title = _("Nueva contraseña")
    template_name = "registration/password_reset_confirm.html"
    form_class = SetPasswordCustomForm
    success_url = reverse_lazy("users:password_reset_complete")

    def form_valid(self, form):
        if self.user:
            self.user._actor = self.user   # reset por correo = actividad propia
        response = super().form_valid(form)
        # Aviso de seguridad: notificar al usuario que su contraseña cambió.
        from apps.mailing.services import send_templated
        if self.user and self.user.email:
            send_templated("password_changed", self.user.email, {
                "usuario": self.user.get_username(),
                "sitio": settings.SITE_NAME,
            })
        return response


class PasswordResetCompleteView(_CuentaPage, auth_views.PasswordResetCompleteView):
    """4) "Listo, ya puedes entrar"."""
    title = _("Contraseña actualizada")
    template_name = "registration/password_reset_complete.html"
