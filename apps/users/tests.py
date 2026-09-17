"""Tests de humo de la app `users`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app users
"""
from core.shared import testing


class UsersSmokeTests(testing.AppSmokeTestCase):
    app_label = "users"
    public_namespace = "users"
