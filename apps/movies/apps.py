from django.apps import AppConfig


class MovieConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.movies"
    label = "movies"
    verbose_name = "Películas"
