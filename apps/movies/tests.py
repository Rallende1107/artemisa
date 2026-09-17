"""Tests de humo de la app `movies`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app movies
"""
from core.shared import testing


class MoviesSmokeTests(testing.AppSmokeTestCase):
    app_label = "movies"
    public_namespace = "movies"
