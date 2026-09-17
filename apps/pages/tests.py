"""Tests de humo de la app `pages`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app pages
"""
from core.shared import testing


class PagesSmokeTests(testing.AppSmokeTestCase):
    app_label = "pages"
    public_namespace = "pages"
