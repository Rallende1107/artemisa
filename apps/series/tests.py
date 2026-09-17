"""Tests de humo de la app `series`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app series
"""
from core.shared import testing


class SeriesSmokeTests(testing.AppSmokeTestCase):
    app_label = "series"
    public_namespace = "series"
