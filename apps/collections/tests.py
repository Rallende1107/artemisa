"""Tests de humo de la app `collections`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app collections
"""
from core.shared import testing


class CollectionsSmokeTests(testing.AppSmokeTestCase):
    app_label = "collections"
    public_namespace = "collections"
