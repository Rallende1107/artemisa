from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        # Limpieza automática de archivos al reemplazar/eliminar registros.
        from core.shared.models.file_cleanup import register
        register()
