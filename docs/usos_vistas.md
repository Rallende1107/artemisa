# Usos de Vistas — glosario del panel

Diccionario de la capa de vistas del panel `/panel/`: **qué es cada cosa, cómo
se llama y para qué sirve**. Complementa a [README.md](../README.md) (la guía práctica).

Motor base: `core/shared/views/base.py` (páginas) + `core/views/v8_actions.py`
(protocolo y chrome). Cada app declara lo suyo en el paquete `apps/<app>/views/`
(+ `urls/panel.py` y `urls/data.py`).

---

## 1. Conceptos base (vocabulario)

| Término | Qué es | Ejemplo |
|---|---|---|
| **entity** | slug corto de una entidad; identifica sus rutas | `"anime"`, `"tipo-rol"` |
| **label** | nombre singular legible | `"anime"`, `"tipo de rol"` |
| **label_plural** | nombre plural legible (títulos, breadcrumbs) | `"animes"` |
| **model** | la clase del modelo Django que gestiona la vista | `Anime`, `RoleType` |
| **background_image** | clase CSS del fondo de esa vista/página | `"bg-otaku-anime"` |
| **background_fallback** | fondo de respaldo si la clase no tiene imagen | `"bg-otaku-home"` |
| **namespace** | espacio de nombres de URLs del panel | `"gestion"` (importación usa `"importacion"`) |
| **sección** | grupo de entidades de una app (Música, Otaku…) | derivada de `background_image` |

---

## 2. El paquete `views/` de cada app (estilo Poseidón, plano)

Un archivo por ROL, con las DOS caras dentro (sección «Gestión» y sección «Público»), y `base.py` compartido:

| Archivo | Qué contiene |
|---|---|
| `base.py` | los mixins `_Base<Modelo>` (model, entity, label, fondo), los mapas `_Base<Modelo>By` de las listas «por» (§9) y los helpers de la cara pública |
| `v0_home.py` | los DOS homes: `<X>AdminHomeView(BaseAdminHomeView)` (tarjetas de entidades del panel) y `<X>HomeView(BasePublicHomeView)` (filas de portadas), más los homes de cuerpos (productoras, artistas…) |
| `v1_data.py` | Datas (JSON de DataTables) y Selects: `XDataView(BaseX, AdminDataView)`, `XSelectView(BaseX, BaseSelectView)`, `XDataView(BaseXBy, PublicDataView)` |
| `v2_write.py` | ESCRITURA de gestión: `BaseCreate`, `BaseUpdate`, `BaseDelete`; cada vista declara todo directo (`form_class`, `form_template`, `list_url`, `success_url`, `cancel_url`, `success_message`, `title`) |
| `v3_filters.py` | panel de filtros POR MODELO: `XFilters(BaseFilters)` públicos (y `XAdminFilters` de gestión donde exista), con `Booleano` / `Relacion` / `Opciones` / `Anio` en dos grupos (genéricos e incluir) |
| `v4_list.py` | las listas completas: `XListView(BaseX, AdminListView)` (`data_url`, `create_url`, `title`) y `XPublicListView(BaseX, PublicListView)` |
| `v4_list_by.py` | las listas «por» de los dos lados: `XListByView` (panel) / `XPublicListByView` (público) sobre el mapa `BaseXBy` (§9) |
| `v5_detail.py` | fichas: `XDetailView(BaseX, BaseDetailView)` de gestión (`update_url`, `delete_url`, `toggle_url`) y `XDetailView(BaseX, BasePublicDetailView)`, las dos sobre el mismo HTML `<app>/templates/<app>/detail/<modelo>.html` (solo `{% block side %}` y `{% block cuerpo %}`; el cuadro es `templates/detail/base_detail.html`) |
| `v8_actions.py` · `v8_import.py` | acciones POST, páginas «a mano» (`BasePage`) y lanzadores de importación |

`views/__init__.py` SOLO reexporta (una línea por archivo, nombres explícitos): `from apps.<app> import views`
sigue funcionando y cada clase tiene UN archivo dueño.

El mixin `_Entidad` es la ÚNICA fuente de config de la entidad; las vistas lo
heredan como PRIMER mixin:

```python
class BaseAnime:
    model = Anime
    entity = "anime"
    label = "anime"
    label_plural = "animes"
    background_image = "bg-otaku-anime"
    background_fallback = "bg-otaku-home"   # respaldo si falta la imagen

class AnimeListView(BaseAnime, AdminListView): ...
```

---

## 3. Las VISTAS base

Páginas (`core/shared/views/base.py`) — un nivel de herencia: genérica de
Django → Base → vista de entidad. Regla: **lo explícito gana, lo no declarado
se deriva** (de `entity` + `namespace`, vía `entity_context()`).

| Clase base | Qué hace | Ruta típica |
|---|---|---|
| **BasePage** | la MADRE de toda página: candado (`staff_only` / `login_only`), `title`, fondo, `page_template`, contexto de entidad. Las páginas «a mano» (TemplateView, UpdateView…) la usan directa: `class MiVista(BasePage, TemplateView)` | — |
| **BaseAdminHomeView** | home de una SECCIÓN del panel (grupos de tarjetas); el dashboard `/panel/` (`SystemHomeView`) es una de ellas con otra plantilla | `gestion/<app>/` |
| **BasePublicHomeView** | home público de una SECCIÓN: filas de portadas en `get_rows()`, cada una con «Ver todo» a una LISTA (no hay homes intermedios; las URL viejas de los cuerpos redirigen a la lista) | `catalog/<app>/` |
| **AdminListView / PublicListView** | *shell* del listado (tabla + toolbar); NO carga filas: apunta a su Data por `data_url` | `<entity>/` |
| **ListByView / PublicListByView** | la lista acotada a un padre de la URL (§9) | `<entity>/by/<tipo>/<pk>/` |
| **BaseCreate** | formulario de alta | `<entity>/create/` |
| **BaseUpdate** | formulario de edición | `<entity>/<pk>/update/` |
| **BaseDetailView / BasePublicDetailView** | la FICHA, misma familia y MISMO HTML por entidad (`<app>/detail/<modelo>.html` sobre `detail/base_detail.html`): gestión con Editar / Activar / Borrar; público con la colección, solo activos y URL canónica `/<pk>/<slug>/`. Las dos declaran `template_name`, `list_url`, `por_url` y `tabs = [(clave, etiqueta, ruta «por», tipo)]` | `<entity>/<pk>/` |
| **BaseDelete** | borrado (con confirmación SweetAlert) | `<entity>/<pk>/delete/` |

Protocolo (`core/shared/views/base.py`) y acciones del panel (`core/views/v8_actions.py`: `AdminToggleView`, `AdminBulkView`):

| Clase | Qué hace | Ruta típica |
|---|---|---|
| **BaseDataView → AdminDataView / PublicDataView** | `BaseDataView` es el MOTOR genérico (búsqueda por palabras, orden, paginación, miniaturas, tarjetas, filtros, palanca `staff_only`); nadie lo usa directo. `AdminDataView` (gestión: Id + checkbox · foto · datos · menú Acciones, `read_only`, toggles) y `PublicDataView` (catálogo: solo activos, sin candado, celda `ficha` = miniatura + título a la ficha vía `detail_url`, acciones = Añadir / Quitar de mi colección). |
| **DataView** | endpoint **JSON server-side** que alimenta la DataTable (busca/ordena/pagina) | `<entity>/data/` · PIEZAS: `actions = False` quita la columna «Acciones» y su menú; `row_actions(obj, request, ctx)` es lo que se pinta en ella (la Data pública lo sustituirá por «Añadir / Quitar de mi colección»); una columna ImageField se pinta como miniatura, y `(_("Título"), "ficha")` es la celda estilo MAL del motor (portada 50×70 + título enlazado + meta «tipo · eps · año» de `meta_de`), ordenable por `card_title`; `no_order = ("donde",)` quita el orden a una columna compuesta |
| **AdminToggleView** | invierte un booleano (activar/bloquear/+18) | `<entity>/<pk>/toggle/` |
| **BaseSelectView** | busca en servidor para los Select2 remotos (FK/M2M) y pagina de a 20 (escala a millones de filas). Una clase por entidad junto a su Data en `v1_data.py` (`class CountrySelectView(BaseCountry, BaseSelectView)`) con `search_fields` (búsqueda por PALABRAS: cada palabra debe aparecer en algún campo, en cualquier orden; admite relaciones como `titles__title` para títulos sinónimos y `nicknames__nickname` para apodos — anime, manga, película, serie, juego, persona, personaje y creador ya los llevan); ganchos `get_queryset()` (solo activos si hay `is_active`) y `option_label(obj)` (texto de la opción: `display_name` del modelo o «name (name_esp)», buscable por los dos nombres) | `<entity>/select/` |

Y estas dan permisos / contexto (no son vistas por sí solas):

| Clase / helper | Qué es |
|---|---|
| **StaffRequiredMixin** | exige `is_staff`; si no, 403 |
| **SuperuserRequiredMixin** | exige `is_superuser` (usuarios: crear/borrar) |
| **entity_context(view)** | (base_views) contexto común de las páginas de una entidad: labels, rutas, fondo, sección |
| **resolve_background(view)** | fondo con respaldo (`background_image` → `background_fallback`) |

---

## 4. Atributos configurables por entidad

Se declaran en cada vista (o en el mixin `_Entidad`). Los leen las bases:

| Atributo | En qué vista | Qué controla |
|---|---|---|
| **data** | List | la Data dueña de la tabla: `data = CountryDataView`. La List toma de ahí las cabeceras y no declara columnas. |
| **columns** | Data | columnas de la tabla: `[("Cabecera", "atributo"), …]`. La ÚNICA fuente (estilo Poseidon): nadie añade columnas por detrás; `("Activo", "is_active")` se declara como cualquier otra (booleanos → píldora «Sí»/«No», `<th>` con `col-stat`). `display_name` es una PROPIEDAD del modelo («name (name_esp)»; en películas y series «Título (Título ES) Año»). |
| **search_fields / default_order / page_size** | Data | búsqueda (icontains, OR), orden base + desempate, filas por página. |
| **select_related / prefetch_related** | Data | relaciones que pintan las columnas (sin N+1). |
| **order_map** | Data | columna → campo de BD para ordenar: `{"movie_type": "movie_type__name"}` (una FK sin esto ordena por su id). |
| **search_fields** | List / Data | campos por los que busca el buscador (icontains) |
| **detail_fields** | Detail | filas de la ficha: `[("Etiqueta", "atributo"), …]` |
| **form_class** | Create / Update | el `Form` explícito de la entidad (`apps/<app>/forms.py`) |
| **success_message** | Create / Update / Delete | mensaje personal (admite `%(label)s` y `%(obj)s`); vacío → el genérico |
| **card_image** | Data | atributo con la imagen para la vista de tarjetas del listado |
| **card_title** | Data | atributo para el título de esas tarjetas |
| **can_create** | List | `False` oculta el botón "Nuevo" (entidades solo-gestión, p. ej. Contacto) |
| **list_url / section_url…** | todas | nombre de ruta explícito; sin declarar se deriva de `entity` |
| **cards / groups** | BaseAdminHomeView | las tarjetas de la home de sección (ver README §1) |

---

## 5. Registros y constantes (globales del motor)

| Nombre | Qué es |
|---|---|
| **NAMESPACE** | `"gestion"` — namespace de URLs del panel |
| **SECTION_LABELS** | mapa `slug → nombre` de sección (`"music" → "Música"`) para breadcrumbs |
| **TOGGLE_FIELDS** | booleanos que se pueden invertir (`is_active`, `explicit`, `is_staff`, `is_superuser`) |
| **TOGGLE_META / TOGGLE_DONE** | textos y gating de cada toggle (quién puede, qué mensaje) |
| **AjaxSelect / AjaxSelectMultiple** | widgets Select2 remoto: `AjaxSelect(url_name='panel:<entidad>_select')` en el form; renderizan solo lo elegido y buscan por AJAX |

---

## 6. Helpers (funciones internas)

| Helper | Qué hace |
|---|---|
| **_card_bg(model)** | URL de la imagen de una card por el nombre del modelo (`bg-<app>-<modelo-kebab>`) |
| **_bg_from_class("bg-…")** | URL de la imagen wide de una clase de fondo, o `None` si no existe |
| **_cell(obj, attr)** | pinta una celda de la tabla (booleano→punto de color, FK, método…) |
| **_status_pill(...)** | pinta el estado activo/inactivo como punto de color |
| **_order_field(model, attr)** | mapea una columna a su campo de BD para ordenar |
| **_model_has_field(model, name)** | ¿el modelo tiene ese campo? (para añadir `is_active` auto, etc.) |
| **_resolve(obj, attr)** | resuelve atributo/método/relación para mostrar un valor |
| **route_name(view, suffix)** | (base_views) nombre de ruta derivado `<ns>:<entity>_<suffix>` |
| **_form_templates(view)** | (base_views) resuelve la plantilla del form: la de la entidad si existe, si no el cuadro genérico |

---

## 7. Convenciones de nombres (dónde va qué)

| Cosa | Patrón | Ejemplo |
|---|---|---|
| **Clave de entidad (`entity`)** | slug en INGLÉS, con prefijo de app cuando el modelo se repite | `movie`, `movie-genre`, `anime-song`, `website-streaming` |
| **Nombre de ruta** | `panel:<entity>_<accion>` (inglés) | `panel:movie_list`, `panel:movie-genre_create`, `panel:task_finish` |
| **URL de la ruta** | el segmento público NO cambia (puede seguir en español); toda la entidad bajo el mismo segmento | `panel:movie-genre_list` → `/panel/movie-genero/` |
| **Clase de gestión** | `<Model><Rol>View`, sin prefijos ni `Admin` | `MovieListView`, `MovieDataView`, `MovieDetailView`, `MovieListByView`, `MoviesHomeView` |
| **Clase pública** | `<Model>Public<Rol>View` | `MoviePublicListView`, `MoviePublicDataView`, `MoviePublicDetailView`, `MoviePublicListByView`, `MoviesPublicHomeView` |
| **Form / Filters** | `<Entity>Form`; `<Entity>Filters` (público) y `<Entity>AdminFilters` si hay gemelo | `MovieForm`, `MovieFilters`, `PersonAdminFilters` |
| **Home de sección** | `panel:<seccion>-home` | `panel:music-home` |
| **Clase de fondo** | `bg-<app>-<x>` | `bg-otaku-anime`, `bg-system-panel` |
| **Imagen de fondo** | `static/image/screen/<orient>/bg-<app>-<x>.webp` | orient = wide/landscape/portrait/tall |
| **Form (HTML) por entidad** | `apps/<app>/templates/<app>/form/<modelo>.html`, modelo en snake_case | `otaku/form/anime.html`, `games/form/game_character.html` |
| **Detail (HTML) por entidad** | `apps/<app>/templates/<app>/detail/<modelo>.html`, modelo en snake_case | `movies/detail/movie.html`, `games/detail/data_vndb_game.html` |
| **Vistas de la entidad** | paquete `apps/<app>/views/` | `base.py` (mixin `_X`) + `admin/v1_data/v3_list/v5_filters/…` |
| **Rutas de la entidad** | `apps/<app>/urls/panel.py` (data · select en `urls/data.py`) | un `path()` explícito por vista |

---

## 8. Flujo de una petición (quién llama a quién)

```
Navegador  →  URL (panel:anime_list)  →  AnimeListView (AdminListView)
                                             └─ renderiza list.html (shell)
list.html  →  DataTable pide JSON  →  AnimeDataView (AdminDataView)
                                       └─ busca/ordena/pagina  →  JSON (filas + acciones)
"Nuevo"    →  AnimeCreateView (BaseCreate)  →  form.html + apps/otaku/form/anime.html
Select2    →  AnimeSelectView (BaseSelectView, v1_data)  →  JSON {id, text}  (búsqueda en servidor)
"Borrar"   →  AnimeDeleteView (BaseDelete)  (confirma con SweetAlert)
toggle     →  AnimeToggle (AdminToggleView)  (invierte is_active/+18…)
```

---

## 9. Listas «por» (ListBy): un padre en la URL

«Animes del género X», «Personas de Chile», «Reparto de Parasite», «Películas de Bill Murray»: la misma
lista (tabla/tarjetas, buscador, orden, panel de filtros) acotada a UN padre que llega por la ruta, en
público y en gestión. Es el `FILTER_CONFIG` de Poseidón compactado en tres piezas:

1. **El mapa, en `base.py`**, un mixin por modelo que extiende su `_Base<Modelo>`:

```python
class BasePersonBy(BasePerson):
    filter_config = {   # tipo → (campo que acota | "app.Modelo" del padre si el filtro es compuesto, título, fondo)
        "pais": ("country", _("Personas de {padre}"), "bg-catalogs-country"),
        "voces-anime": ("otaku.Anime", _("Actores de voz de {padre}"), "bg-otaku-voice-character"),
    }
    sub_via = {"equipo-anime": ("staff", "person_id", "role__name")}   # subtítulo de tarjeta acotado al padre

    def filtro(self, qs, padre, tipo):          # solo los tipos compuestos; el resto lo hace el motor
        if tipo == "voces-anime":
            return qs.filter(voice_roles__character__anime_appearances__anime=padre, …)
        return super().filtro(qs, padre, tipo)
```

2. **La Data solo filtra**: `PersonPublicDataView(BasePersonBy, PublicDataView)` y `PersonDataView(BasePersonBy,
   AdminDataView)`. Con `pk` en la ruta (`…/by/<tipo>/<pk>/data/`) se acota; sin él, lista todo. El campo
   fijado sale del panel de filtros; `filters_por = {"voces-anime": VoiceFilters}` sustituye los filtros en
   esa «por» (el rol EN ESTA obra, con `ancla=`).

3. **Las ListBy, en `apps/<app>/views/v5_list_by.py`**, una por modelo y lado:

```python
class PersonByListView(BasePersonBy, PublicListByView):
    data_url = "personas:por-data"; por_url = "personas:por"; lista_url = "personas:catalogo"
    padre_urls = {"voces-anime": "otaku:detalle-anime"}   # ficha del padre, solo donde la hay
    background_image = "bg-people-person"; background_fallback = "bg-catalogs-home"; section = "personas"

class PersonByListView(BasePersonBy, ListByView):
    data_url = "panel:person_by-data"; lista_url = "panel:person_list"; create_url = "panel:person_create"
```

- Rutas, siempre iguales: `…/by/<str:tipo>/<int:pk>/` (la lista) y `…/data/` (la Data). Tipo desconocido
  o id inexistente → 404 en las dos; en público el padre inactivo también es 404, en gestión se ve.
- La página: título del mapa con el padre, fondo del tipo (si su imagen falta, el de la lista), miga, y en
  gestión los botones «← padre» (`panel:<entidad>_detail`), «lista del padre» y «lista completa», con
  «Nuevo» llegando con el padre preseleccionado (`?country=3`; `BaseCreate.get_initial` lo toma del GET).
- En gestión, una columna FK que sea un tipo del mapa se pinta como enlace a su «por» (País →
  «Personas de Chile»); en público la celda es texto.
- `url_por(modelo, campo, pk)` (registro `REGISTRO_POR`, lo llenan las `PublicListByView` con `por_url`) lo
  usan los chips de las fichas: cada género/estudio/país de una ficha lleva a su lista.
- Filas que muestran un relacionado (reparto: la fila es un MovieCast, se ve la persona): `ficha_via = "person"`
  en la Data; galerías: la Data de la tabla de imágenes **extra** en tarjetas sin título.

## 10. Fichas (DetailView) sobre el cuadro `detail/base_detail.html`

Una ficha son **tres piezas**, y cada una hace solo lo suyo:

| Pieza | Qué hace | Ejemplo |
| --- | --- | --- |
| **Modelo** | métodos con lo que la ficha pinta (Poseidón): `Movie.reparto()`, `Anime.personajes()` (con la voz principal colgada en `.voz`), `Anime.banda_sonora()` (tres grupos: Openings · Inserts · Endings), `Relation.de()`, `Person.peliculas()` / `Character.animes()` (filas de obra vía `filas_obra`), `Studio.obras()` | `apps/<app>/models.py` |
| **Vista** | SOLO lo básico: `template_name` (siempre explícito, como `form_template`), rutas de botones, `por_url`, `tabs` | `MovieDetailView(BaseMovie, BaseDetailView)` · `MovieDetailView(BaseMovie, BasePublicDetailView)` |
| **HTML** | mínimo, `{% extends 'detail/base_detail.html' %}` y rellena `{% block titulos %}`, `{% block side %}`, `{% block cuerpo %}` | `apps/<app>/templates/<app>/detail/<modelo>.html` (compañías: `templates/detail/company.html` para todas) |

El cuadro `templates/detail/base_detail.html` es el ÚNICO que carga `ficha.css`, arma migas, póster,
botones (gestión) o barra de colección (público) y las **pestañas EN la página** (una por `<section data-tab>` del cuerpo; el
lateral no se mueve). Cada pestaña muestra sus filas completas y, si son muchas (> 30, fotos > 40),
«Ver en lista →» hacia la lista «por» del lado (`tabs` de la vista → `tab_url`, con el slug del padre).
`page_template` es solo el cascarón de página (`base.html` público, `admin_panel/base_admin.html` gestión).

Parciales compartidos en `templates/detail/`: `_personas` (persona + personaje/idioma/cargo), `_personajes`
(personaje + su voz), `_obras` (obra + rol; filas con `.obra/.rol/.rol_sub`), `_relaciones` (obra relacionada +
tipo), `_titulos` (una fila por idioma, títulos separados por « · », 4 idiomas / 3 títulos visibles),
`_canciones` (tabla MAL). Etiquetas de `core/templatetags/ficha.py`: `{% ficha obj %}` (URL de la ficha del
lado que pinta), `{% por por_url 'genero' g %}`, filtros `obj|imagen` (portada, `resolve_cover`) y `dict|get_item`.

CADA entidad tiene su detail PROPIO con su HTML escrito (como los `form/<modelo>.html`): la vista declara
`template_name = "<app>/detail/<modelo>.html"` y ese archivo extiende `detail/base_detail.html` con SU lateral (una
fila por campo, con el formato que le toca: fecha, sí/no, enlace a la ficha de la FK, `{% ficha obj as href %}`) y SU
cuerpo (textos largos; en los logs el mensaje como traza `.log-traza`; en las compañías `obras()`). Fechas y booleanos se pintan con las
propiedades de los mixins de modelo (`core/mixin/models.py`): `{{ object.display_created }}`, `{{ object.display_release_date }}`,
`{{ object.display_is_active }}`…; nunca `|date` ni `|yesno` en la plantilla. Las vistas ya no
declaran `detail_fields`: el HTML es el dueño de lo que se pinta. `detail_fields` + `admin_panel/detail.html` quedan
solo para las cuatro fichas con cuadro propio (usuario, correo, plantilla, contacto).

Comentarios en plantillas: `{# … #}` solo en UNA línea (multilínea se PINTA como texto); lo largo va en
`{% comment %}…{% endcomment %}`. `sync_forms` ya genera así.

## Ver también

- [README.md](../README.md) — guía práctica (cards, forms, sidebar, fondos)
- [comandos.md](comandos.md) — comandos
- [transparencias.md](transparencias.md) — fondos y blur

## URLs públicas

Todo lo navegable cuelga de `/catalog/…` (como gestión de `/panel/…`): `/catalog/personas/` es el home de la sección, `/catalog/personas/lista/` su lista y `/catalog/personas/lista/data/` la Data que la alimenta (`PublicDataView`). En la raíz solo quedan index, contacto y las páginas; `coleccion/` y `cuenta/` son el área del usuario. Los nombres de ruta (`personas:catalogo`, `movies:lista`, `<name>-data`) son el contrato: las vistas y plantillas siempre usan `{% url %}` / `reverse`.

## Colecciones del usuario

Una Data por medio en `apps/collections/views/public/v1_data.py` (`XCollectionDataView`, `login_only`, siempre `user=request.user`: nadie ve la colección de otro) y una lista por medio en `v3_list.py` sobre `PublicListView`; las rutas `/collection/<medio>/` y `…/data/` despachan por medio. Filtros: Favorito, «Mi estado» y los del catálogo del medio sobre `content__`. En gestión, las 10 Data de moderación ven a todos los usuarios y filtran por usuario y estado (`admin/v5_filters.py`).
