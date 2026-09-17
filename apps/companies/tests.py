"""Tests de humo de la app `companies`: rutas del panel y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app companies
"""
from core.shared import testing


class CompaniesSmokeTests(testing.AppSmokeTestCase):
    app_label = "companies"
    public_namespace = "companias"
