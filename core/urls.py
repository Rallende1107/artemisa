"""URLs raíz de Artemisa."""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.views import serve as static_serve
from django.urls import include, path, re_path
from django.views.static import serve as media_serve

from apps.pages import views as pages_views

urlpatterns = [
    path("", include("apps.pages.urls.public")),
    path("admin/", admin.site.urls),
    # set_language (cambio de idioma)
    path("i18n/", include("django.conf.urls.i18n")),
    # panel de gestión (framework Panel)
    path("panel/", include("core.panel_urls")),   # panel de gestión (dashboard + secciones; sidebar en apps/system/sidebar.py)

    path("collection/", include("apps.collections.urls.public")),
    # CATÁLOGO público: todo lo navegable cuelga de /catalog/… (como gestión de /panel/…);
    # solo index, contacto y las páginas quedan limpias en la raíz.
    path("catalog/", include([
        path("companies/", include("apps.companies.urls.public")),
        # Secciones públicas de contenido
        path("otaku/", include("apps.otaku.urls.public")),
        path("music/", include("apps.music.urls.public")),
        path("movies/", include("apps.movies.urls.public")),
        path("series/", include("apps.series.urls.public")),
        path("games/", include("apps.games.urls.public")),
        path("people/", include("apps.people.urls.public")),
    ])),
    path("account/", include("apps.users.urls.public")),


    # Previsualizar las páginas de error: en este proyecto DEBUG=False es fijo
    # (dev y prod), así que los handler* de abajo YA están siempre activos —
    # esto solo da una URL estable para no tener que provocar cada error de
    # verdad (sobre todo el 500). Mismas CBV que usan los handlers reales.
    path("prev/400/", pages_views.Error400View.as_view(), name="prev_400"),
    path("prev/403/", pages_views.Error403View.as_view(), name="prev_403"),
    path("prev/403/csrf/", pages_views.Error403CsrfView.as_view(), name="prev_403_csrf"),
    path("prev/404/", pages_views.Error404View.as_view(), name="prev_404"),
    path("prev/500/", pages_views.Error500View.as_view(), name="prev_500"),
]

# Servir estáticos con DEBUG=False usando los finders (encuentra el static de
# CADA app: staticfiles/finders busca en STATICFILES_DIRS + apps/*/static/).
# insecure=True permite servir aunque DEBUG=False (solo desarrollo).
urlpatterns += [
    re_path(r"^static/(?P<path>.*)$", static_serve, {"insecure": True}),
    re_path(r"^media/(?P<path>.*)$", media_serve, {"document_root": str(settings.MEDIA_ROOT)}),
]

# Manejadores de error personalizados (se activan con DEBUG=False)
handler404 = "apps.pages.views.error_404"
handler500 = "apps.pages.views.error_500"
handler403 = "apps.pages.views.error_403"
handler400 = "apps.pages.views.error_400"
