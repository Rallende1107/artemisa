from django.apps import AppConfig


class SerieConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.series"
    label = "series"
    verbose_name = "Series"
