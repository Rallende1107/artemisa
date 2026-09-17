"""SIDEBAR declarativo y reutilizable del panel de administración.

Un sidebar es DATOS: namespace de URL al que pertenece, título, pie y `nav`
(árbol de link/tree/group). Se declara como una INSTANCIA de `Sidebar` (sin
subclases) y se registra por namespace; el context processor
`core.context_processors.sidebar` lo resuelve por el namespace de la request y
`templates/panel/_sidebar.html` lo pinta genérico, sin HTML a mano.

Uso (apps/<app>/sidebar.py, importado desde AppConfig.ready() para registrarlo):

    GESTION = Sidebar(
        namespace="panel", title=_("Panel de gestión"),
        nav=[tree("Otaku", [...]), group("Logs", [...])],
    )
    register_sidebar(GESTION)

Las URLs y las vistas NO viven aquí (core/panel_urls.py y apps/<app>/views/).
"""

# --------------------------- helpers de navegación ---------------------------
# Cada nodo es un dict. 3 formas:
#   link(...)  -> hoja (<a class="nav-item">)
#   tree(...)  -> colapsable (<details class="nav-tree[ --sub]">)
#   group(...) -> etiqueta eyebrow + hijos (separador de sección, no colapsable)

def _planos(hijos):
    """Hijos declarados: enlaces, o un LazySeq de enlaces por tipo (se lee en la petición, no en ready())."""
    out = []
    for h in hijos:
        if isinstance(h, list) and not isinstance(h, dict) and hasattr(h, "_fabrica"):
            out.extend(list(h))
        else:
            out.append(h)
    return out


def link(label, url=None, icon=None, entity=None, href=None, super_only=False, query="", args=None):
    """Hoja del sidebar. `url` = nombre de ruta (se reversa); `href` = ruta cruda
    (p. ej. '/admin/'); `super_only` = solo visible para superusuarios; `query` =
    cadena que se añade tras «?» (lista filtrada, p. ej. "estado=queued")."""
    return {"kind": "link", "label": label, "url": url, "icon": icon,
            "entity": entity, "href": href, "super_only": super_only, "query": query, "args": list(args or [])}


def tree(label, children, url=None, icon=None, entity=None):
    return {"kind": "tree", "label": label, "url": url, "icon": icon,
            "entity": entity, "children": children}


def group(label, children):
    return {"kind": "group", "label": label, "children": children}


def _entities(node):
    """Todas las `entity` dentro de un nodo (para saber si un árbol top va abierto)."""
    out = set()
    if node.get("entity"):
        out.add(node["entity"])
    for child in _planos(node.get("children") or []):
        out |= _entities(child)
    return out


# ------------------------------- registro ------------------------------------


# ------------------------------- el sidebar ---------------------------------
class Sidebar:
    """Sidebar de un panel: datos puros. Se instancia, no se hereda."""

    def __init__(self, namespace, title, nav, footer=""):
        self.namespace = namespace
        self.title = title
        self.footer = footer or title     # pie del sidebar (por defecto = título)
        self.nav = nav                    # navegación declarativa (link/tree/group)

    def nav_for_context(self):
        """La nav con `open_for` (entidades del subárbol) en CADA árbol, para que el
        sidebar sepa qué sección abrir según `active_entity`."""
        return [_prep(node) for node in self.nav]


def _prep(node):
    """Prepara un nodo recursivamente: a cada `tree` le añade `open_for`."""
    kind = node.get("kind")
    if kind == "tree":
        return {**node, "open_for": _entities(node),
                "children": [_prep(c) for c in _planos(node.get("children") or [])]}
    if kind == "group":
        return {**node, "children": [_prep(c) for c in _planos(node.get("children") or [])]}
    return node


# ------------------------------- registro -----------------------------------
_SIDEBARS = {}


def register_sidebar(sidebar):
    """Registra el sidebar por su namespace (lo lee el context processor)."""
    _SIDEBARS[sidebar.namespace] = sidebar
    return sidebar


def get_sidebar(namespace):
    return _SIDEBARS.get(namespace)
