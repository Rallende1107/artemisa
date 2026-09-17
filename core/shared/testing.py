"""Base de los tests de humo por app (`apps/<app>/tests.py`).

Cada app declara su `app_label` y la base recorre SOLAS sus rutas: las del panel (como superusuario) y las públicas
(anónimo). Toda ruta sin parámetros debe responder 200 o redirigir; toda lista «by» (`<ent>/<tipo>/<valor>/`) con un
tipo inventado debe dar 404 (así se prueba el mapa `filter_config`: nada de `movie/papafrita/-9999`).

Se corren con `docker compose exec web python manage.py test_changed` (solo las apps modificadas) y el resultado queda
en `dump/tests/`.
"""
import importlib

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import URLPattern, reverse


def _planas(patrones, prefijo=""):
    """(nombre, ruta) de cada `path()` de un urlpatterns, entrando en los include."""
    for p in patrones:
        if isinstance(p, URLPattern):
            yield p.name, prefijo + str(p.pattern)
        else:
            yield from _planas(p.url_patterns, prefijo + str(p.pattern))


class AppSmokeTestCase(TestCase):
    """Humo de UNA app: `app_label` obligatorio. `panel_namespace` es «panel» para todas."""
    app_label = ""
    panel_namespace = "panel"
    public_namespace = ""          # app_name de apps/<app>/urls/public.py (vacío si la app no tiene parte pública)
    saltar = ()                    # nombres de ruta que no aplican (p. ej. requieren POST)

    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser("smoke", "smoke@test.local", "smoke-pass")

    def setUp(self):
        self.client.force_login(self.admin)

    # ---- helpers
    def _rutas(self, modulo):
        try:
            mod = importlib.import_module(f"apps.{self.app_label}.{modulo}")
        except ModuleNotFoundError:
            return []
        return [(n, r) for n, r in _planas(mod.urlpatterns) if n]

    def _get(self, url, ok, quien=""):
        r = self.client.get(url, follow=False)
        self.assertIn(r.status_code, ok, f"{quien}{url} → {r.status_code}")

    # ---- tests
    def test_check(self):
        """`manage.py check` limpio para el proyecto (lo ve la app, lo ve todo)."""
        call_command("check", verbosity=0)

    def test_panel_routes(self):
        """Toda ruta del panel sin parámetros responde (200), redirige (302) o exige POST (405) al superusuario."""
        for nombre, ruta in self._rutas("urls.panel"):
            if "<" in ruta or nombre in self.saltar:
                continue
            with self.subTest(ruta=nombre):
                self._get(reverse(f"{self.panel_namespace}:{nombre}"), (200, 302, 405), "panel ")   # 405: existe pero exige POST (toggle, reenviar…)

    def test_panel_by_rejects_unknown_type(self):
        """Listas «by» y sus Data: tipo fuera del mapa → 404; padre con id no numérico → 404; choice inválido → 404."""
        for nombre, ruta in self._rutas("urls.panel"):
            if not (nombre.endswith("_by") or nombre.endswith("_data-by")):
                continue
            with self.subTest(ruta=nombre):
                self._get(reverse(f"{self.panel_namespace}:{nombre}", args=["papafrita", "1"]), (404,), "by tipo ")
                for tipo in self._mapa(nombre):
                    self._get(reverse(f"{self.panel_namespace}:{nombre}", args=[tipo, "asf-9999"]), (404,), "by valor ")

    def _mapa(self, nombre):
        from django.urls import resolve
        vista = resolve(reverse(f"{self.panel_namespace}:{nombre}", args=["x", "1"])).func.view_class
        return getattr(vista, "filter_config", None) or {}

    def test_public_routes(self):
        """Toda ruta pública sin parámetros responde al anónimo (200, redirección o exige POST)."""
        if not self.public_namespace:
            return
        self.client.logout()
        for nombre, ruta in self._rutas("urls.public"):
            if "<" in ruta or nombre in self.saltar:
                continue
            with self.subTest(ruta=nombre):
                self._get(reverse(f"{self.public_namespace}:{nombre}"), (200, 301, 302, 405), "público ")
