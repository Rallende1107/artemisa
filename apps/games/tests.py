"""Tests de humo de la app `games`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app games
"""
from core.shared import testing


class GamesSmokeTests(testing.AppSmokeTestCase):
    app_label = "games"
    public_namespace = "games"
