"""Tests de humo de la app `people`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app people
"""
from core.shared import testing


class PeopleSmokeTests(testing.AppSmokeTestCase):
    app_label = "people"
    public_namespace = "personas"
