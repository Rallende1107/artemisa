from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.system"
    label = "system"
    verbose_name = "Sistema"

    def ready(self):
        # Registra el sidebar de /panel/ (core.shared.views.sidebar) al arrancar: nadie
        # más importa ese módulo, así que sin esto el sidebar no se pintaría.
        from apps.system import sidebar  # noqa: F401
