"""Tests de humo de la app `mailing`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app mailing
"""
from core.shared import testing


class MailingSmokeTests(testing.AppSmokeTestCase):
    app_label = "mailing"
    public_namespace = ""
