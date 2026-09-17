"""Tests de humo de la app `system`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app system
"""
from core.shared import testing


class SystemSmokeTests(testing.AppSmokeTestCase):
    app_label = "system"
    public_namespace = ""
