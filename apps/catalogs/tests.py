"""Tests de humo de la app `catalogs`: rutas del panel, listas «by» (404 con tipo inválido). Sin parte pública.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app catalogs
"""
from core.shared import testing


class CatalogsSmokeTests(testing.AppSmokeTestCase):
    app_label = "catalogs"
    public_namespace = ""          # su hub público de compañías se mudó a apps/companies
