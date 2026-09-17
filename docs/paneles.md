# Paneles (framework declarativo)

Un **panel** (Gestión, y los que vengan) son tres piezas: un urlconf explícito
(`core/panel_urls.py`), un dashboard (vista) y un **sidebar declarado como datos**
(instancia de `Sidebar` en `apps/<app>/sidebar.py`, registrada en `AppConfig.ready()`).
El sidebar se pinta desde datos (`nav`), no desde HTML. El dashboard es un
`BaseAdminHomeView` con sus `cards`. Mismo molde para todos; cambia solo el contenido.

- Sidebar declarativo (genérico): `core/shared/views/sidebar.py`
- Sidebar genérico: `templates/panel/_sidebar.html` + `_nav_node.html`
- Context processor: `core.context_processors.sidebar` (resuelve el sidebar por namespace)

## ¿Dónde vive cada panel?

| Panel | Archivo | Clase |
|---|---|---|
| Gestión | `apps/system/sidebar.py` (sidebar) · `apps/system/views/v1_home.py` (dashboard) · `core/panel_urls.py` (URLs) | `GESTION` (instancia de `Sidebar`) |
| ~~Importación~~ | app ELIMINADA (2026-09-10): cada lanzador vive en su app (un lanzador POR TIPO: `panel:mal-anime`… en otaku, `panel:deezer-artista`… en music, `panel:vndb-juego`… en games) con base compartida en `core/shared/views/imports.py`; las tablas Data y los logs siempre fueron de cada app. |

> Los paneles concretos viven en su **app**, no en `core/`. `core/urls.py` solo los
> incluye (`path("panel/", include("core.panel_urls"))`).

## ¿Dónde toco qué? (cheat-sheet)

| Quiero cambiar… | Dónde |
|---|---|
| Textos/enlaces del **sidebar** | `Panel.nav` (en el archivo del panel) |
| **Título** del panel (H1 + pestaña) | `title` del `home_view` |
| **Subtítulo** del dashboard | `page_sub` del `home_view` |
| **Tarjetas** del dashboard | `cards` del `home_view` |
| **Pie** del sidebar | `Panel.footer` |
| Agregar entidad **CRUD** | el `panel_urls.py` de la app (ya incluido en `core/panel_urls.py`) |

Todo es **Python** → tras editar hay que **reiniciar el server** (`--noreload` no recarga).

## Los 3 ladrillos de la navegación (`nav`)

```python
from core.shared.views.sidebar import link, tree, group

link("Animes", "panel:anime_list", entity="anime")   # enlace (hoja)
link("Admin Django", href="/admin/", super_only=True)  # ruta cruda + solo superuser
tree("Otaku", [ ...hijos... ], icon="bi-stars", url="panel:otaku-home", entity="otaku-home")  # desplegable
group("FUENTES", [ ...hijos... ])                       # separador gris (etiqueta)
```

- `entity` = se compara con `active_entity` de la vista para marcar el activo y auto-abrir
  la sección donde estás.
- `tree` de primer nivel = sección del acordeón; `tree` anidado = sub-grupo colapsable.

## Ejemplo REAL: la sección "Otaku" del sidebar de gestión

Esto es lo que hoy vive en `apps/system/sidebar.py` dentro de `GESTION.nav`. Un
`tree` de primer nivel ("Otaku") con sub-grupos `tree` ("Anime", "Manga"…) y sus `link`.
**Para renombrar "Animes", cambiar un icono o agregar un enlace, editas AQUÍ:**

```python
tree("Otaku", icon="bi-stars", url="panel:otaku-home", entity="otaku-home", children=[
    tree("Anime", children=[
        link("Animes", "panel:anime_list", entity="anime"),          # ← renombra el texto aquí
        link("Estudios", "panel:studio_list", entity="studio"),
        link("Productoras", "panel:producer_list", entity="producer"),
        link("Temporadas", "panel:season_list", entity="season"),
        link("Canciones", "panel:anime-song_list", entity="anime-song"),
        link("Personajes", "panel:anime-character_list", entity="anime-character"),
        link("Staff", "panel:anime-staff_list", entity="anime-staff"),
        link("Títulos", "panel:anime-title_list", entity="anime-title"),
        link("Imágenes", "panel:anime-image_list", entity="anime-image"),
        link("Imágenes extra", "panel:anime-image-extra_list", entity="anime-image-extra"),
    ]),
    tree("Manga", children=[
        link("Mangas", "panel:manga_list", entity="manga"),
        link("Autores", "panel:manga-author_list", entity="manga-author"),
        link("Serializaciones", "panel:serialization_list", entity="serialization"),
        # …
    ]),
    tree("Taxonomías", children=[
        link("Géneros", "panel:genre_list", entity="genre"),
        link("Tipos", "panel:type_list", entity="type"),
        # …
    ]),
]),
```

**Para AGREGAR un enlace nuevo** (p. ej. "Openings") a la sub-sección Anime, agregas una
línea `link(...)` dentro de sus `children` — nada de HTML:

```python
link("Openings", "panel:opening_list", entity="opening"),
```

*(la ruta `panel:opening_list` debe existir en `apps/otaku/urls/panel.py`)*.

---

## Ejemplo COMPLETO: crear un panel nuevo "Reportes"

**1) Vistas** — `apps/reportes/views.py`

```python
from core.shared.views.base import BaseAdminHomeView
from apps.reportes.models import Venta, Cliente

class ReportesHome(BaseAdminHomeView):
    title = "Reportes"                      # H1 + pestaña
    page_sub = "Elige un reporte."          # subtítulo
    active_entity = "reportes-home"
    page_template = "panel/base.html"       # opcional (base_admin ya lo detecta)
    def get_contact_count(self):            # el contador de contacto es de gestión
        return None
    cards = [
        ("reportes:ventas_list", "Ventas", '<i class="bi bi-graph-up"></i>', [Venta]),
        ("reportes:clientes_list", "Clientes", '<i class="bi bi-people"></i>', [Cliente]),
    ]
```

**2) URLs de administración** — `apps/reportes/urls/panel.py` (explícitas, sin `app_name`)

```python
from django.urls import path
from apps.reportes.views import VentaList, ClienteList

urlpatterns = [
    path("ventas/", VentaList.as_view(), name="ventas_list"),
    path("clientes/", ClienteList.as_view(), name="clientes_list"),
]
```

**3) Sidebar (título + navegación)** — `apps/reportes/sidebar.py` (impórtalo en `ReportesConfig.ready()`)

```python
from core.shared.views.sidebar import Sidebar, group, link, register_sidebar, tree

REPORTES = Sidebar(
    namespace="reportes",
    title="Reportes",
    footer="Panel de reportes",
    nav=[
        tree("Navegación", icon="bi-compass", url="reportes:home", entity="reportes-home", children=[
            link("Reportes", "reportes:home", entity="reportes-home"),
            link("Panel de gestión", "panel:home"),
        ]),
        group("Datos", [
            tree("Comercial", icon="bi-graph-up", url="reportes:ventas_list", entity="ventas", children=[
                link("Ventas", "reportes:ventas_list", entity="ventas"),
                link("Clientes", "reportes:clientes_list", entity="clientes"),
            ]),
        ]),
    ],
)
register_sidebar(REPORTES)
```

**4) URLconf del panel** — `core/reportes_urls.py` (como `core/panel_urls.py`)

```python
from django.urls import include, path
from apps.reportes.views import ReportesHome

app_name = "reportes"
urlpatterns = [
    path("", ReportesHome.as_view(), name="home"),          # dashboard
    path("", include("apps.reportes.urls.panel")),        # secciones
]
```

**3) Enchufar en `core/urls.py`** (una línea)

```python
path("reportes/", include("apps.reportes.panel")),
```

Listo. `/reportes/` tiene dashboard + sidebar propio (por fuente/tema) + permisos staff,
**sin escribir una línea de HTML de sidebar**. Reinicia el server y `Ctrl+F5`.

## Notas

- Todas las vistas del panel deben heredar de las bases con `StaffRequiredMixin`
  (`AdminListView`, `BaseAdminHomeView`) → permisos automáticos.
- `BaseAdminHomeView.cards` acepta `[(url_name, label, icono_html, modelo|[modelos]|None[, bg])]`.
  Si `entity` trae `:` es ruta completa; si termina en `-home` va a esa home; si no, a
  `{namespace}:{entity}_list`.
- ⚠️ Comentarios de plantilla **siempre en una línea** (`{# … #}`): uno multilínea se
  imprime como texto y descuadra el layout.
