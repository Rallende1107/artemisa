"""Candados de acceso del panel: quién puede entrar a una vista (staff / superusuario).
Las Base* (core/shared/views/base.py), el cromo (views.py) y las vistas de importación los heredan."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo usuarios staff. Anónimos → login; logueados no-staff → 403."""
    login_url = "users:login"

    def test_func(self):
        u = self.request.user
        return u.is_authenticated and u.is_staff


class SuperuserRequiredMixin(StaffRequiredMixin):
    """Solo superusuarios. Para acciones sensibles (gestión de usuarios)."""

    def test_func(self):
        u = self.request.user
        return u.is_authenticated and u.is_superuser
