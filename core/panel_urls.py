"""URLconf de /panel/ (namespace `panel`): el panel de administración.

Igual que core/urls.py con las públicas: el dashboard + un `include` por app de su
`urls/panel.py` (rutas de ADMINISTRACIÓN). Todas cuelgan del MISMO namespace
`panel`, por eso los módulos de sección no declaran `app_name`. El sidebar se declara
aparte, en apps/system/sidebar.py (Sidebar); el dashboard es una vista más
(apps/system/views/v1_home.py).

Convención por app:
    urls/public.py → rutas PÚBLICAS (las monta core/urls.py)
    urls/panel.py  → rutas de ADMINISTRACIÓN (las monta este archivo)
    urls/data.py   → data · data-by · select del panel (las incluye urls/panel.py)"""
from django.urls import include, path

from apps.system.views import SystemHomeView
from core.views import AdminBulkView

app_name = "panel"

urlpatterns = [
    path("", SystemHomeView.as_view(), name="home"),          # dashboard /panel/
    path("bulk/<str:app_label>/<str:model_name>/", AdminBulkView.as_view(), name="bulk"),   # acción masiva de cualquier lista
    # --- secciones de administración (una por app) ---
    path("", include("apps.catalogs.urls.panel")),            # Catálogos (países, idiomas, tipos…)
    path("", include("apps.pages.urls.panel")),             # Páginas (Nosotros, Términos, Privacidad)
    path("", include("apps.people.urls.panel")),            # Personas
    path("", include("apps.companies.urls.panel")),         # Compañías
    path("", include("apps.music.urls.panel")),             # Música
    path("", include("apps.games.urls.panel")),             # Juegos
    path("", include("apps.movies.urls.panel")),             # Películas
    path("", include("apps.series.urls.panel")),             # Series
    path("", include("apps.otaku.urls.panel")),             # Otaku (anime y manga)
    path("", include("apps.collections.urls.panel")),        # Colección
    path("", include("apps.users.urls.panel")),             # Usuarios
    path("", include("apps.mailing.urls.panel")),           # Correo
    path("", include("apps.system.urls.panel")),            # Sistema: tareas Celery (registro, cancelador, programadas)
]
