"""Tests de humo de la app `music`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app music
"""
from core.shared import testing


class MusicSmokeTests(testing.AppSmokeTestCase):
    app_label = "music"
    public_namespace = "music"
