# Definición de Modelos, Formularios y Vistas

## Objetivo del documento

Este documento hace dos cosas:

1. **Fija las reglas** de Modelos → Formularios → Vistas del proyecto (R0 a R5): cómo se nombra cada pieza, qué
   vistas tiene un modelo, qué no lleva alta ni edición, cómo van rutas, entidades y fondos, y cómo se aplica un cambio.
2. **Documenta las vistas del proyecto**: el inventario por app, con cada modelo, su
   formulario y las vistas que lo usan (panel y público), sus listas especiales por tipo o estado y sus filtros.

También están las **vistas sin modelo ni formulario**: el index y las páginas informativas, contacto, login y cuenta,
los homes de cada app, los lanzadores de importación y las acciones (reprocesar, cancelar, reenviar). Aparecen al pie
de cada app en el inventario.

Regla base: cada modelo administrable tiene UN formulario y las vistas necesarias para administrar sus registros
(1 : 1 : N, ver R0).

## Reglas

Son las reglas vigentes del código. Cualquier cambio se decide aquí antes de tocarlo.

### R0 · 1 : 1 : N
Un modelo, UN formulario, N vistas. Hay N vistas porque hay dos lados (panel y público) y varias acciones (lista, data,
select, alta, edición, borrado, ficha, «por»). El formulario es uno y del panel: el público no edita.
Cada formulario hereda de `forms.ModelForm` y declara todo a la vista; ÚNICA excepción: las categorías
(`ModelBaseCategory`) heredan `core.shared.forms.base.FormBaseCategory`, que trae nombre, nombre ES, descripción,
imagen y activo con su limpieza. El hijo pone su `duplicate_message`, su `Meta` y sus campos propios.

Los tags de VNDB no son un caso aparte: los de contenido son `games.Genre` (con `vndb_id`) y los técnicos son
`games.Tag` (N:M con `Game`, como los géneros; un juego puede no tener ninguno). Entran TODOS al procesar un juego,
sin umbral ni spoiler.

Cada modelo vive en la app que lo usa. `catalogs` es solo lo que comparten varias apps (`Country`, `Language`,
`LogLevel`, `RoleType`, `RelationType`, `Format`, `Quality`, `Website`, `ExternalSource`); lo que usa una
sola app está en esa app con el nombre limpio (`music.AlbumType`, `games.Tag`), y su fondo se llama por la app
dueña (`bg-music-album-type`). Un tipo con valores FIJOS no es modelo: es un `TextChoices` de `core/shared/models/choices.py`
(`AnimeSongType` OP/ED/IN, `CreatorType` CO/IN/NG, `GameType`, `GameStatus`, `MalSeason` para `Anime/Manga.season` (calculada
por el mes de `from_date` si falta), `MalRating`, `WebsiteType`, `ExternalSourceType`; en las bases
compartidas, `ModelBaseLog.level` texto con `LogLevel` y `ModelBaseRole.type` con `RoleType`) o en un módulo de valores
(`<Medio>CollectionStatus` en `core/shared/models/choices.py`: estados de colección por medio para el campo `status` de cada tabla). Solo es modelo lo que tiene id externo,
crece con las importaciones o es N:M (Genre, Tag, Theme, Platform, Demographic, Role…). Los ALIAS de un catálogo son
modelo, no texto: `ModelBaseAlias` (name, name_esp) y un `<Catálogo>Alias` por app con FK `aliases` al padre (games
GenreAlias/TagAlias, otaku GenreAlias/ThemeAlias/DemographicAlias, movies/series/music GenreAlias); los importadores
cruzan por nombre o alias antes de crear, y las listas y selects del padre buscan también por alias.

```text
Genre ─── GenreForm ─┬─ GenreListView · GenreDataView · GenreSelectView · GenreCreateView · GenreUpdateView
                     │  GenreDeleteView · GenreDetailView · GenreListByView · GenreDataByView        (panel)
                     └─ GenrePublicListView · GenrePublicDataView · GenrePublicDetailView · GenrePublicListByView (público)
```

### R1 · El nombre del modelo manda, dentro de su app
Form, vistas, entidad, rutas, plantillas y fondo salen del nombre del modelo. Dos apps pueden tener un modelo con el
mismo nombre (`movies.Genre`, `series.Genre`): viven en módulos distintos y no chocan, y sus clases no llevan prefijo
de app (`apps/movies/forms.py::GenreForm`, `apps/games/forms.py::StatusForm`). Si dos clases iguales se importan en un
mismo módulo, se usa alias (`from apps.movies.forms import GenreForm as MovieGenreForm`).

Orden de las palabras en el nombre del modelo: `<Entidad><Cosa>`, la entidad primero (`GameTitle`, `GameImage`,
`GameLink`, `MangaAuthor`, `CharacterVoice`, `PersonNickname`, `AnimeStaff`). Excepciones: la familia `Data*` y los
catálogos genéricos (`LogLevel`, `RelationType`, `RoleType`). `CustomUser` sigue el estilo:
`CustomUserForm`, `CustomUserListView`…

Las bases ABSTRACTAS van al revés, con el prefijo primero: `ModelBase<Cosa>` para modelos (`ModelBaseCategory`,
`ModelBaseImage`, `ModelBaseData`, `ModelBaseLog`, `ModelBaseEntity`, `ModelBaseMalEntity`…) y `FormBase<Cosa>` para
formularios (`FormBaseLoadFile`). Los mixins de presentación (`CoverMixin`, `DateDisplayMixin`…) y los mixins de
vista (`Base<Model>`) no cambian.

Los CHOICES (valores fijos sin tabla) viven TODOS en `core/shared/models/choices.py`, agrupados por app, para ver
repetidos y duplicidades de un vistazo. Nombre `<Modelo><Campo>` (`GameStatus`, `AnimeSongType`); los compartidos
llevan nombre propio (`RoleType`, `LogLevel`, `MalSeason`, `MalRating`). Nada de choices anidados ni `models_choices.py`.
`models_abstract.py` queda solo con bases abstractas.

Las tablas de datos externos se nombran **`[Data][Sitio][Entidad]`**: `Data` dice que es crudo de fuera, el SITIO de
dónde salió y luego qué es. El sitio se escribe con el nombre con el que ese sitio se presenta, abreviado a una
palabra: `Vndb`, `Mal`, `Deezer`, `F95`. Que unos sean más cortos que otros no es incoherencia, son nombres propios.

| App | Tablas |
|---|---|
| `games` | `DataVndbGame`, `DataVndbCreator`, `DataVndbRelease`, `DataVndbCharacter`, `DataF95Game`, `DataF95Creator` |
| `music` | `DataDeezerArtist`, `DataDeezerAlbum`, `DataDeezerTrack`, `DataDeezerGenre` |
| `otaku` | `DataMalAnime`, `DataMalManga`, `DataMalCharacter`, `DataMalPerson` y sus `…Picture`; además `DataMalAnimeCharacter`, `DataMalAnimeStaff`, `DataMalMangaCharacter` |

Y todo lo que cuelga del modelo sigue el mismo orden: entidad `data-vndb-game`, rutas `data-vndb-game_list`,
plantilla `detail/data_vndb_game.html`, fondo `bg-games-data-vndb-game`. Cada tabla tiene su `id` propio y, aparte,
el id externo del sitio (`vndb_id`, `mal_id`, `deezer_id`, `f95_id`).

### R2 · Vistas: nombres limpios en el panel, `Public` en el público
Todas las vistas se llaman `<Model><Rol>View`, sin prefijo de app ni `Admin`; las del lado público llevan `Public`
entre el modelo y el rol.

```text
                       panel                        público
formulario             <Model>Form                  (no hay: el público no edita)
lista                  <Model>ListView              <Model>PublicListView
endpoint JSON          <Model>DataView              <Model>PublicDataView
Select2 (destino FK)   <Model>SelectView            —
alta / edición / baja  <Model>CreateView · <Model>UpdateView · <Model>DeleteView
ficha                  <Model>DetailView            <Model>PublicDetailView
lista «por» + JSON     <Model>ListByView · <Model>DataByView     <Model>PublicListByView
home de la APP         <App>HomeView                <App>PublicHomeView
```

Las bases del framework viven en `core/shared/views/base.py` y ahí `Admin`/`Public` nombran el LADO, no una entidad:
el panel hereda de `AdminListView`, `AdminDataView`, `BaseAdminDetailView`, `BaseCreate`, `BaseUpdate`, `BaseDelete`,
`BaseSoftDelete`; el público de `PublicListView`, `PublicDataView`, `BasePublicDetailView`. Los mixins por modelo y por
app se llaman `Base<Model>` y `Base<App>` (`views/base.py` de cada app), sin guion bajo.

Los HOME son el index de la APP, no de un modelo, con la app en plural para no chocar con el modelo (`GamesHomeView`,
`SeriesHomeView`, `OtakuPublicHomeView`).

Listas «by»: UN MAPA por entidad y UNA Data. El mixin `Base<Model>By` (`views/base.py`) declara `filter_config`,
tipo → (campo, título, fondo[, choices]); la Data lo usa para filtrar y la `<Model>ListByView` para el título y el fondo.
Dos clases de entrada: por PADRE (el campo es FK/M2M: el valor de la URL es el id del padre) y por CHOICE (el campo tiene
choices, o la entrada trae la lista explícita: el valor es una de sus claves). Los tipos de sitio web y fuente externa
son choices fijos del campo `type`; los estados de correo, contacto y tarea, del campo `status`.

```text
class BaseMovieContext(BaseMovie):
    filter_config = {"genre": ("genres", "Películas de {padre}", "bg-movies-genre")}          # padre por id
class BaseWebsiteContext(BaseWebsite):
    filter_config = {"type": ("type", "Sitios web · {valor}", "")}                          # choice por valor
class BaseAnimeSongContext(BaseAnimeSong):
    filter_config = {"anime": ("anime", …), "type": ("song_type__key", …, "", SONG_KINDS)}   # choice explícito

/panel/movie/data/                    movie_data       la Data completa (interna: la consume DataTables)
/panel/movie/data/<tipo>/<valor>/     movie_data-by    la misma Data acotada
/panel/movie/genre/12/                movie_by         la lista que ve la persona (ListByView)
/panel/website/type/streaming/        website_by
/panel/email-message/status/sent/     email-message_by
```

Validación, siempre con mensaje y nunca con texto libre en la consulta: tipo fuera del mapa → 404 «El filtro de tipo
«x» no es válido para …»; id de padre no entero o inexistente → 404 «El id «x» de tipo «y» no es válido / no existe»;
valor fuera de los choices → 404 «El valor «x» de tipo «y» no es válido para …». Las homes llevan UNA card por entidad
(sin cards por tipo). Toda lista con choices en su mapa los ofrece en el panel de filtros como NAVEGACIÓN: selección
única que lleva a la lista «por» (otra vista, con su URL y su fondo `bg-<app>-<entidad>-<valor>`); un choice opcional
añade el valor `unknown` (filas sin valor). Los demás filtros del panel (`v3_filters.py`, `ChoiceFilter`/`RelationFilter`/
`BooleanFilter`/`YearFilter`) son combinables dentro de la vista y no cambian de página.

### R6 · La Data es explícita (estilo Poseidón)
Cada `<Modelo>DataView` escribe su `get()`: su queryset, `self.query(request, qs, campos_de_búsqueda, order_map, orden_por_defecto)`
(que hace lo genérico sin lógica de negocio: parámetros de DataTables, mapa «por», panel lateral, búsqueda, orden y página, y
devuelve `p, total, filtrado, objetos`) y UNA fila por objeto con sus celdas (`cell`, `cell_cover`, `meta_line`,
`self.link_by`) y el menú (`self.row_actions`). Tocar la Data de un modelo no toca la de los demás. La base
(`DataView` / `AdminDataView` / `PublicDataView` en `core/shared/views/base.py`, con el resto de vistas base) solo trae lo que todas repiten igual: parámetros de DataTables, orden por columna, pintar una
celda (helpers en `core/utils/views_base.py`), la respuesta, el menú de gestión y el botón de colección; el mapa «por» es
`ByMixin` en `core/mixin/by.py`. La
portada es del modelo (`obj.cover_url`, `CoverMixin`), no de la vista. Nada de `card_title`, `card_image`,
`ficha_via` ni ganchos `_image` / `meta_de` / `col_ficha` en la base.

### R3 · Sin excepciones: todo modelo tiene el CRUD completo
Form, List, Data, Create, Update, Delete y Detail existen para TODOS los modelos, también para los que llena el sistema
(logs, `Data*`, `EmailMessage`, `TaskRun`, `CloudFile`, `UserActivity`, `ContactMessage`, colecciones del usuario,
`MailConfig`): la regla 1 : 1 : N se cumple igual aunque el Create no se use. Los que lo necesitan tienen además su
acción propia (Reprocesar, Reenviar, Cancelar, Lanzar). Borrado LÓGICO (`BaseSoftDelete`, deja `is_active=False`) en
`ContactMessage`, `ImportCursor` y `UserActivity`.

### R4 · Rutas
Dos namespaces por lado:

- **Público**: el namespace de cada app (`movies`, `games`, `otaku`…) con entidad limpia (`movies:genre_list`).
  Paths en inglés: `/catalog/movies/`, `/catalog/games/`, `/catalog/otaku/`, `/catalog/music/`, `/catalog/series/`,
  `/catalog/people/`, `/catalog/companies/`, `/collection/`, `/account/`. Los slugs de contenido son los títulos.
- **Panel**: namespace único `panel` (`core/panel_urls.py` incluye el `panel_urls.py` de cada app), prefijo `/panel/`.
  Como todo cae en el mismo namespace, la entidad lleva el prefijo de la app cuando el nombre del modelo se repite
  (`movie-genre`, `serie-genre`, `game-dev-status`); las entidades únicas van limpias (`anime`, `game`, `country`).

La entidad es el nombre del modelo en kebab-case (`ExternalSource` → `external-source`, `DataVndbGame` →
`data-vndb-game`) más el prefijo de app cuando toca. Nombra la ruta, el path, las plantillas
(`movies/form/genre.html`, `movies/detail/genre.html`: por app, sin prefijo) y el fondo (`bg-movies-genre`).

```text
/panel/movie-genre/                       movie-genre_list
/panel/movie-genre/data/                  movie-genre_data
/panel/movie-genre/select/                movie-genre_select
/panel/movie-genre/create/                movie-genre_create
/panel/movie-genre/<pk>/                  movie-genre_detail
/panel/movie-genre/<pk>/update/           movie-genre_update
/panel/movie-genre/<pk>/delete/           movie-genre_delete
/panel/movie-genre/<pk>/toggle/<field>/   movie-genre_toggle
/panel/movie-genre/<tipo>/<valor>/        movie-genre_by       (lista acotada por el mapa: padre por id o choice por valor)
/panel/movie-genre/data/<tipo>/<valor>/   movie-genre_data-by  (la misma Data, acotada)
```

### R5 · Formularios y vistas que no son de un modelo
Lanzadores de importación, login, cambio de clave, filtros: `<Qué>Form` sin chocar con ningún modelo
(`VndbBarridoForm`, `LoginForm`, `UserResetPasswordForm`), uno por pantalla, en el `forms.py` de su app. Sus vistas
se nombran en inglés: `VndbGameImportView`, `DeezerArtistImportView`, `AboutView`, `ContactView`, `ProfileView`,
`GlobalSearchView`, `ImportCursorLaunchView`, `EmailResendView`. Las vistas sin
modelo (index, páginas informativas, contacto, cuenta, lanzadores, acciones) se listan al pie de cada app en el inventario.

### R7 · Los datos externos entran por API o por DUMP, y salen por EXPORT
Una tabla `Data*` se llena de dos maneras, y cada una tiene su pantalla:

- **Lanzador (API)**: `<Sitio><Entidad>ImportView`, con su arreglo de formularios (por nombre, por id, por rango).
  Se entra desde la lista de datos de la entidad, con su botón «Importar». Lo usan VNDB y Deezer.
- **Cargar dump (archivo)**: DOS vistas, `<Sitio><Entidad>LoadView` → `<Sitio><Entidad>SummaryView`. La primera
  valida y guarda el archivo en `dump/` y deja la ruta en sesión; la segunda enseña el resumen de lo que va a entrar
  y, con «Sí, continuar», lo aplica. Se entra desde el grupo «Dumps» del home de la app. Lo usan MAL (cuyo API,
  Jikan, está muerto), los tags de VNDB y F95. Las bases son `BaseLoadFileView` y `BaseLoadSummaryView`.

Los dos escriben SOLO en las tablas `Data*`, con el JSON tal cual y `data_processed=False`. **Procesar es otro paso**,
desde la lista de esa tabla: «Procesar pendientes» para todo lo que falte, o «Procesar» en el menú de una fila.

La vuelta es el **exportador**: el botón «Generar dump» de la lista (`export_url` de la vista, base
`BaseExportDumpView` en `core/shared/views/export.py`) descarga la tabla como `.json.gz`. Lo que sale por ahí vuelve a
entrar por el cargador de esa misma entidad, así que sirve de respaldo alternativo al de la base de datos.

Un formulario de dump por entidad, heredando del de su fuente (`MALDumpForm`, `VndbDumpForm`), y el hijo solo declara
su `TIPO`. El lector acepta un registro suelto, una lista o un objeto por línea (JSON Lines), en `.json` o `.json.gz`.

### R8 · Funciones sueltas: con tipos, y las de modelos en su utils
Toda función suelta declara los tipos de sus parámetros y de su retorno, también las internas:
`def season_of(fecha: datetime.date | None) -> str:`. Las funciones de apoyo de los modelos no viven en
`core/shared/models/abstract.py` (que solo tiene bases abstractas) sino en `core/utils/models_abstract.py`, y cada
`models.py` las importa de ahí: `unique_slug`, `generate_negative_id`, `season_of`, `filas_obra`, `siguiente_orden`.

### R9 · Imágenes: una tabla por entidad, la primera es la portada
Cada entidad con imágenes tiene UNA tabla `<Entidad>Image` (`related_name="images"`), sin tamaños ni tabla «extra».
`order` decide: la de número más bajo es la **portada** (empate: la más antigua) y el resto es la galería, en ese
orden. Si `order` llega vacío, la imagen va al final. Cada fila lleva archivo o URL (pendiente hasta que el
descargador la baja). Los importadores solo AGREGAN filas al final (sin repetir URL), así nunca cambian la portada.
Cambiar la portada es editar el orden: no se mueven ni se borran archivos. `ReleaseImage` sigue igual (arte del
lanzamiento, con `label`).

---

# Inventario por app

Cómo leer este inventario (para quien entra al proyecto):

- Cada app tiene `models.py`, `forms.py` (un `<Model>Form` por modelo), `views/base.py` (mixins `Base<Model>`: modelo, entidad,
  etiquetas y fondo), `views/v1_data.py` (Data y Select: JSON), `views/v2_write.py` (Create, Update, Delete),
  `views/v2_filters.py` (filtros del panel lateral), `views/v5_list.py` (List), `views/v6_detail.py` (Detail), `urls/panel.py`
  (rutas del panel), `urls/data.py` (data · select) y `urls/public.py` (rutas públicas).
- Una vista del panel se ARMA así: `<Model>ListView(Base<Model>, AdminListView)` pinta el shell y pide sus filas por AJAX a
  `<Model>DataView`; `<Model>CreateView`/`UpdateView` dependen del `<Model>Form`; `DeleteView` confirma y borra (o desactiva).
- Por cada vista: dónde vive, de qué hereda, de qué depende y qué ruta la sirve.

Por app: cada modelo con su formulario, sus vistas (lado, fondo y qué hace cada una) y sus filtros. Al final de cada app,
las vistas y formularios sin modelo (index, contacto, cuenta, lanzadores, homes, acciones).

## Catálogos (`catalogs`)

### Modelo: `CatalogsLog` (`apps/catalogs/models.py`)

- Formulario: `CatalogsLogForm` (`apps/catalogs/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `CatalogsLogCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseCatalogsLog`, `BaseCreate`
    - depende de: formulario `CatalogsLogForm`; vuelve a `panel:catalogs-log_list`; al guardar va a `panel:catalogs-log_list`
    - ruta: `panel:catalogs-log_create` → `/panel/catalogs-log/create/`
    - fondo: `bg-catalogs-logs`
  - `CatalogsLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseCatalogsLog`, `AdminDataView`
    - ruta: `panel:catalogs-log_data` → `/panel/catalogs-log/data/`
    - fondo: `bg-catalogs-logs`
  - `CatalogsLogDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseCatalogsLog`, `BaseDelete`
    - depende de: vuelve a `panel:catalogs-log_list`; al guardar va a `panel:catalogs-log_list`
    - ruta: `panel:catalogs-log_delete` → `/panel/catalogs-log/<int:pk>/delete/`
    - fondo: `bg-catalogs-logs`
  - `CatalogsLogDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseCatalogsLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:catalogs-log_list`; plantilla `catalogs/detail/catalogs_log.html`
    - ruta: `panel:catalogs-log_detail` → `/panel/catalogs-log/<int:pk>/`
    - fondo: `bg-catalogs-logs`
  - `CatalogsLogListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseCatalogsLog`, `AdminListView`
    - depende de: datos de `panel:catalogs-log_data`
    - ruta: `panel:catalogs-log_list` → `/panel/catalogs-log/`
    - fondo: `bg-catalogs-logs`
  - `CatalogsLogUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseCatalogsLog`, `BaseUpdate`
    - depende de: formulario `CatalogsLogForm`; vuelve a `panel:catalogs-log_list`; al guardar va a `panel:catalogs-log_list`
    - ruta: `panel:catalogs-log_update` → `/panel/catalogs-log/<int:pk>/update/`
    - fondo: `bg-catalogs-logs`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `CatalogsLogDataView`

### Modelo: `Country` (`apps/catalogs/models.py`)

- Formulario: `CountryForm` (`apps/catalogs/forms.py`) — campos: `name`, `name_esp`, `code`, `numeric_code`, `description`, `image`, `is_active`
- Vistas:
  - `CountryCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseCountry`, `BaseCreate`
    - depende de: formulario `CountryForm`; vuelve a `panel:country_list`; al guardar va a `panel:country_list`; plantilla `catalogs/form/country.html`
    - ruta: `panel:country_create` → `/panel/country/create/`
    - fondo: `bg-catalogs-country`
  - `CountryDataView` (panel) — datos JSON de la lista
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseCountry`, `AdminDataView`
    - ruta: `panel:country_data` → `/panel/country/data/`
    - fondo: `bg-catalogs-country`
  - `CountryDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseCountry`, `BaseDelete`
    - depende de: vuelve a `panel:country_list`; al guardar va a `panel:country_list`
    - ruta: `panel:country_delete` → `/panel/country/<int:pk>/delete/`
    - fondo: `bg-catalogs-country`
  - `CountryDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseCountry`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:country_list`; plantilla `catalogs/detail/country.html`
    - ruta: `panel:country_detail` → `/panel/country/<int:pk>/`
    - fondo: `bg-catalogs-country`
  - `CountryListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseCountry`, `AdminListView`
    - depende de: datos de `panel:country_data`
    - ruta: `panel:country_list` → `/panel/country/`
    - fondo: `bg-catalogs-country`
  - `CountrySelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseCountry`, `BaseSelectView`
    - ruta: `panel:country_select` → `/panel/country/select/`
    - fondo: `bg-catalogs-country`
  - `CountryUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseCountry`, `BaseUpdate`
    - depende de: formulario `CountryForm`; vuelve a `panel:country_list`; al guardar va a `panel:country_list`; plantilla `catalogs/form/country.html`
    - ruta: `panel:country_update` → `/panel/country/<int:pk>/update/`
    - fondo: `bg-catalogs-country`
- Filtros:
  - `CountryFilters`: Activo (`is_active`) — para `CountryDataView`

### Modelo: `ExternalSource` (`apps/catalogs/models.py`)

- Formulario: `ExternalSourceForm` (`apps/catalogs/forms.py`) — campos: `name`, `acronym`, `url`, `type`, `description`, `image`, `is_active`
- Vistas:
  - `ExternalSourceCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseExternalSource`, `BaseCreate`
    - depende de: formulario `ExternalSourceForm`; vuelve a `panel:external-source_list`; al guardar va a `panel:external-source_list`; plantilla `catalogs/form/external_source.html`
    - ruta: `panel:external-source_create` → `/panel/external-source/create/`
    - fondo: `bg-catalogs-external-source`
  - `ExternalSourceDataView` (panel) — datos JSON de la lista — La Data de fuentes externas: `/data/` (todas) y `/data/<type>/` (solo un tipo: red social, monetización…).
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseExternalSourceContext`, `AdminDataView`
    - ruta: `panel:external-source_data` → `/panel/external-source/data/`, `panel:external-source_data-by` → `/panel/external-source/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `social`, `monetizacion`, `comunidad`, `oficial`, `base_datos`, `otro`
    - fondo: `bg-catalogs-external-source`
  - `ExternalSourceDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseExternalSource`, `BaseDelete`
    - depende de: vuelve a `panel:external-source_list`; al guardar va a `panel:external-source_list`
    - ruta: `panel:external-source_delete` → `/panel/external-source/<int:pk>/delete/`
    - fondo: `bg-catalogs-external-source`
  - `ExternalSourceDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseExternalSource`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:external-source_list`; plantilla `catalogs/detail/external_source.html`
    - ruta: `panel:external-source_detail` → `/panel/external-source/<int:pk>/`
    - fondo: `bg-catalogs-external-source`
  - `ExternalSourceListByView` (panel) — lista «por» (acotada a un padre) — Lista acotada por el mapa (`/external-source/<tipo>/<valor>/`): la alimenta ExternalSourceDataView con `/data/<tipo>/<valor>/`.
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseExternalSourceContext`, `AdminListByView`
    - depende de: datos de `panel:external-source_data-by`
    - ruta: `panel:external-source_by` → `/panel/external-source/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `social`, `monetizacion`, `comunidad`, `oficial`, `base_datos`, `otro`
    - fondo: `bg-catalogs-external-source`
  - `ExternalSourceListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseExternalSource`, `AdminListView`
    - depende de: datos de `panel:external-source_data`
    - ruta: `panel:external-source_list` → `/panel/external-source/`
    - fondo: `bg-catalogs-external-source`
  - `ExternalSourceSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseExternalSource`, `BaseSelectView`
    - ruta: `panel:external-source_select` → `/panel/external-source/select/`
    - fondo: `bg-catalogs-external-source`
  - `ExternalSourceUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseExternalSource`, `BaseUpdate`
    - depende de: formulario `ExternalSourceForm`; vuelve a `panel:external-source_list`; al guardar va a `panel:external-source_list`; plantilla `catalogs/form/external_source.html`
    - ruta: `panel:external-source_update` → `/panel/external-source/<int:pk>/update/`
    - fondo: `bg-catalogs-external-source`
- Filtros:
  - `ExternalSourceFilters`: Tipo (`type`), Activo (`is_active`) — para `ExternalSourceDataView`

### Modelo: `Format` (`apps/catalogs/models.py`)

- Formulario: `FormatForm` (`apps/catalogs/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `FormatCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseFormat`, `BaseCreate`
    - depende de: formulario `FormatForm`; vuelve a `panel:format_list`; al guardar va a `panel:format_list`; plantilla `catalogs/form/format.html`
    - ruta: `panel:format_create` → `/panel/format/create/`
    - fondo: `bg-catalogs-format`
  - `FormatDataView` (panel) — datos JSON de la lista
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseFormat`, `AdminDataView`
    - ruta: `panel:format_data` → `/panel/format/data/`
    - fondo: `bg-catalogs-format`
  - `FormatDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseFormat`, `BaseDelete`
    - depende de: vuelve a `panel:format_list`; al guardar va a `panel:format_list`
    - ruta: `panel:format_delete` → `/panel/format/<int:pk>/delete/`
    - fondo: `bg-catalogs-format`
  - `FormatDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseFormat`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:format_list`; plantilla `catalogs/detail/format.html`
    - ruta: `panel:format_detail` → `/panel/format/<int:pk>/`
    - fondo: `bg-catalogs-format`
  - `FormatListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseFormat`, `AdminListView`
    - depende de: datos de `panel:format_data`
    - ruta: `panel:format_list` → `/panel/format/`
    - fondo: `bg-catalogs-format`
  - `FormatSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseFormat`, `BaseSelectView`
    - ruta: `panel:format_select` → `/panel/format/select/`
    - fondo: `bg-catalogs-format`
  - `FormatUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseFormat`, `BaseUpdate`
    - depende de: formulario `FormatForm`; vuelve a `panel:format_list`; al guardar va a `panel:format_list`; plantilla `catalogs/form/format.html`
    - ruta: `panel:format_update` → `/panel/format/<int:pk>/update/`
    - fondo: `bg-catalogs-format`
- Filtros:
  - `FormatFilters`: Activo (`is_active`) — para `FormatDataView`

### Modelo: `Language` (`apps/catalogs/models.py`)

- Formulario: `LanguageForm` (`apps/catalogs/forms.py`) — campos: `name`, `name_esp`, `acronym`, `iso_639_1`, `description`, `image`, `is_active`
- Vistas:
  - `LanguageCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseLanguage`, `BaseCreate`
    - depende de: formulario `LanguageForm`; vuelve a `panel:language_list`; al guardar va a `panel:language_list`; plantilla `catalogs/form/language.html`
    - ruta: `panel:language_create` → `/panel/language/create/`
    - fondo: `bg-catalogs-language`
  - `LanguageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseLanguage`, `AdminDataView`
    - ruta: `panel:language_data` → `/panel/language/data/`
    - fondo: `bg-catalogs-language`
  - `LanguageDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseLanguage`, `BaseDelete`
    - depende de: vuelve a `panel:language_list`; al guardar va a `panel:language_list`
    - ruta: `panel:language_delete` → `/panel/language/<int:pk>/delete/`
    - fondo: `bg-catalogs-language`
  - `LanguageDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseLanguage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:language_list`; plantilla `catalogs/detail/language.html`
    - ruta: `panel:language_detail` → `/panel/language/<int:pk>/`
    - fondo: `bg-catalogs-language`
  - `LanguageListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseLanguage`, `AdminListView`
    - depende de: datos de `panel:language_data`
    - ruta: `panel:language_list` → `/panel/language/`
    - fondo: `bg-catalogs-language`
  - `LanguageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseLanguage`, `BaseSelectView`
    - ruta: `panel:language_select` → `/panel/language/select/`
    - fondo: `bg-catalogs-language`
  - `LanguageUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseLanguage`, `BaseUpdate`
    - depende de: formulario `LanguageForm`; vuelve a `panel:language_list`; al guardar va a `panel:language_list`; plantilla `catalogs/form/language.html`
    - ruta: `panel:language_update` → `/panel/language/<int:pk>/update/`
    - fondo: `bg-catalogs-language`
- Filtros:
  - `LanguageFilters`: Activo (`is_active`) — para `LanguageDataView`

### Modelo: `Quality` (`apps/catalogs/models.py`)

- Formulario: `QualityForm` (`apps/catalogs/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `QualityCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseQuality`, `BaseCreate`
    - depende de: formulario `QualityForm`; vuelve a `panel:quality_list`; al guardar va a `panel:quality_list`; plantilla `catalogs/form/quality.html`
    - ruta: `panel:quality_create` → `/panel/quality/create/`
    - fondo: `bg-catalogs-quality`
  - `QualityDataView` (panel) — datos JSON de la lista
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseQuality`, `AdminDataView`
    - ruta: `panel:quality_data` → `/panel/quality/data/`
    - fondo: `bg-catalogs-quality`
  - `QualityDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseQuality`, `BaseDelete`
    - depende de: vuelve a `panel:quality_list`; al guardar va a `panel:quality_list`
    - ruta: `panel:quality_delete` → `/panel/quality/<int:pk>/delete/`
    - fondo: `bg-catalogs-quality`
  - `QualityDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseQuality`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:quality_list`; plantilla `catalogs/detail/quality.html`
    - ruta: `panel:quality_detail` → `/panel/quality/<int:pk>/`
    - fondo: `bg-catalogs-quality`
  - `QualityListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseQuality`, `AdminListView`
    - depende de: datos de `panel:quality_data`
    - ruta: `panel:quality_list` → `/panel/quality/`
    - fondo: `bg-catalogs-quality`
  - `QualitySelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseQuality`, `BaseSelectView`
    - ruta: `panel:quality_select` → `/panel/quality/select/`
    - fondo: `bg-catalogs-quality`
  - `QualityUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseQuality`, `BaseUpdate`
    - depende de: formulario `QualityForm`; vuelve a `panel:quality_list`; al guardar va a `panel:quality_list`; plantilla `catalogs/form/quality.html`
    - ruta: `panel:quality_update` → `/panel/quality/<int:pk>/update/`
    - fondo: `bg-catalogs-quality`
- Filtros:
  - `QualityFilters`: Activo (`is_active`) — para `QualityDataView`

### Modelo: `RelationType` (`apps/catalogs/models.py`)

- Formulario: `RelationTypeForm` (`apps/catalogs/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `RelationTypeCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseRelationType`, `BaseCreate`
    - depende de: formulario `RelationTypeForm`; vuelve a `panel:relation-type_list`; al guardar va a `panel:relation-type_list`; plantilla `catalogs/form/relation_type.html`
    - ruta: `panel:relation-type_create` → `/panel/relation-type/create/`
    - fondo: `bg-catalogs-relation-type`
  - `RelationTypeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseRelationType`, `AdminDataView`
    - ruta: `panel:relation-type_data` → `/panel/relation-type/data/`
    - fondo: `bg-catalogs-relation-type`
  - `RelationTypeDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseRelationType`, `BaseDelete`
    - depende de: vuelve a `panel:relation-type_list`; al guardar va a `panel:relation-type_list`
    - ruta: `panel:relation-type_delete` → `/panel/relation-type/<int:pk>/delete/`
    - fondo: `bg-catalogs-relation-type`
  - `RelationTypeDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseRelationType`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:relation-type_list`; plantilla `catalogs/detail/relation_type.html`
    - ruta: `panel:relation-type_detail` → `/panel/relation-type/<int:pk>/`
    - fondo: `bg-catalogs-relation-type`
  - `RelationTypeListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseRelationType`, `AdminListView`
    - depende de: datos de `panel:relation-type_data`
    - ruta: `panel:relation-type_list` → `/panel/relation-type/`
    - fondo: `bg-catalogs-relation-type`
  - `RelationTypeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseRelationType`, `BaseSelectView`
    - ruta: `panel:relation-type_select` → `/panel/relation-type/select/`
    - fondo: `bg-catalogs-relation-type`
  - `RelationTypeUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseRelationType`, `BaseUpdate`
    - depende de: formulario `RelationTypeForm`; vuelve a `panel:relation-type_list`; al guardar va a `panel:relation-type_list`; plantilla `catalogs/form/relation_type.html`
    - ruta: `panel:relation-type_update` → `/panel/relation-type/<int:pk>/update/`
    - fondo: `bg-catalogs-relation-type`
- Filtros:
  - `RelationTypeFilters`: Activo (`is_active`) — para `RelationTypeDataView`

### Modelo: `Website` (`apps/catalogs/models.py`)

- Formulario: `WebsiteForm` (`apps/catalogs/forms.py`) — campos: `name`, `acronym`, `url`, `type`, `description`, `image`, `is_active`
- Vistas:
  - `WebsiteCreateView` (panel) — alta
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseWebsite`, `BaseCreate`
    - depende de: formulario `WebsiteForm`; vuelve a `panel:website_list`; al guardar va a `panel:website_list`; plantilla `catalogs/form/website.html`
    - ruta: `panel:website_create` → `/panel/website/create/`
    - fondo: `bg-catalogs-website`
  - `WebsiteDataView` (panel) — datos JSON de la lista
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseWebsiteContext`, `AdminDataView`
    - ruta: `panel:website_data` → `/panel/website/data/`, `panel:website_data-by` → `/panel/website/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `streaming`, `descarga`, `tienda`, `base_datos`, `otro`
    - fondo: `bg-catalogs-website`
  - `WebsiteDeleteView` (panel) — borrado
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseWebsite`, `BaseDelete`
    - depende de: vuelve a `panel:website_list`; al guardar va a `panel:website_list`
    - ruta: `panel:website_delete` → `/panel/website/<int:pk>/delete/`
    - fondo: `bg-catalogs-website`
  - `WebsiteDetailView` (panel) — ficha
    - archivo: `apps/catalogs/views/v6_detail.py` · hereda de `BaseWebsite`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:website_list`; plantilla `catalogs/detail/website.html`
    - ruta: `panel:website_detail` → `/panel/website/<int:pk>/`
    - fondo: `bg-catalogs-website`
  - `WebsiteListByView` (panel) — lista «por» (acotada a un padre) — Lista acotada por el mapa (`/website/<tipo>/<valor>/`): la alimenta WebsiteDataView con `/data/<tipo>/<valor>/`.
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseWebsiteContext`, `AdminListByView`
    - depende de: datos de `panel:website_data-by`
    - ruta: `panel:website_by` → `/panel/website/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `streaming`, `descarga`, `tienda`, `base_datos`, `otro`
    - fondo: `bg-catalogs-website`
  - `WebsiteListView` (panel) — lista
    - archivo: `apps/catalogs/views/v5_list.py` · hereda de `BaseWebsite`, `AdminListView`
    - depende de: datos de `panel:website_data`
    - ruta: `panel:website_list` → `/panel/website/`
    - fondo: `bg-catalogs-website`
  - `WebsiteSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/catalogs/views/v3_data.py` · hereda de `BaseWebsite`, `BaseSelectView`
    - ruta: `panel:website_select` → `/panel/website/select/`
    - fondo: `bg-catalogs-website`
  - `WebsiteUpdateView` (panel) — edición
    - archivo: `apps/catalogs/views/v4_write.py` · hereda de `BaseWebsite`, `BaseUpdate`
    - depende de: formulario `WebsiteForm`; vuelve a `panel:website_list`; al guardar va a `panel:website_list`; plantilla `catalogs/form/website.html`
    - ruta: `panel:website_update` → `/panel/website/<int:pk>/update/`
    - fondo: `bg-catalogs-website`
- Filtros:
  - `WebsiteFilters`: Tipo (`type`), Activo (`is_active`) — para `WebsiteDataView`

### Sin modelo

- `CatalogsHomeView`
  - archivo: `apps/catalogs/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:catalogs-home` → `/panel/catalogs/` · fondo `bg-catalogs-home`
- `CompaniesHomeView` — Hub GLOBAL de COMPAÑÍAS: la industria de TODAS las apps en un lugar.
  - archivo: `apps/catalogs/views/v1_home.py` · hereda de `BasePublicHomeView` · ruta: `companias:home` → `/catalog/companies/` · fondo `bg-catalogs-home`

## Juegos (`games`)

### Modelo: `Creator` (`apps/games/models.py`)

- Formulario: `CreatorForm` (`apps/games/forms.py`) — campos: `name`, `type`, `languages`, `description`, `is_active`
- Vistas:
  - `CreatorCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreator`, `BaseCreate`
    - depende de: formulario `CreatorForm`; vuelve a `panel:creator_list`; al guardar va a `panel:creator_list`; plantilla `games/form/creator.html`
    - ruta: `panel:creator_create` → `/panel/creator/create/`
    - fondo: `bg-games-creator`
  - `CreatorDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreatorContext`, `AdminDataView`
    - ruta: `panel:creator_data` → `/panel/creator/data/`, `panel:creator_data-by` → `/panel/creator/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `idioma` → padre por id (campo `languages`); `type` → choice: `CO`, `IN`, `NG`, `unknown`
    - fondo: `bg-games-creator`
  - `CreatorDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreator`, `BaseDelete`
    - depende de: vuelve a `panel:creator_list`; al guardar va a `panel:creator_list`
    - ruta: `panel:creator_delete` → `/panel/creator/<int:pk>/delete/`
    - fondo: `bg-games-creator`
  - `CreatorDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCreator`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:creator_list`; plantilla `games/detail/creator.html`
    - ruta: `panel:creator_detail` → `/panel/creator/<int:pk>/`
    - fondo: `bg-games-creator`
  - `CreatorListByView` (panel) — lista «por» (acotada a un padre) — idioma, tipo.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCreatorContext`, `AdminListByView`
    - depende de: datos de `panel:creator_data-by`
    - ruta: `panel:creator_by` → `/panel/creator/<str:tipo>/<str:pk>/`
    - mapa «by»: `idioma` → padre por id (campo `languages`); `type` → choice: `CO`, `IN`, `NG`, `unknown`
    - fondo: `bg-games-creator`
  - `CreatorListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCreator`, `_JuegosDelCreador`, `AdminListView`
    - depende de: datos de `panel:creator_data`
    - ruta: `panel:creator_list` → `/panel/creator/`
    - fondo: `bg-games-creator`
  - `CreatorPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreatorContext`, `PublicDataView`
    - ruta: `games:creadores-catalogo-data` → `/catalog/games/creators/list/data/`, `games:creadores-por-data` → `/catalog/games/creators/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `idioma` → padre por id (campo `languages`); `type` → choice: `CO`, `IN`, `NG`, `unknown`
    - fondo: `bg-games-creator`
  - `CreatorPublicDetailView` (pública) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCreator`, `BasePublicDetailView`
    - depende de: vuelve a `games:creadores-catalogo`; plantilla `games/detail/creator.html`
    - ruta: `games:creador` → `/catalog/games/creator/<int:pk>/<slug:slug>/`, `games:creador` → `/catalog/games/creator/<int:pk>/`
    - fondo: `bg-games-creator`
  - `CreatorPublicListByView` (pública) — lista «por» (acotada a un padre) — idioma, tipo.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCreatorContext`, `PublicListByView`
    - depende de: datos de `games:creadores-por-data`; plantilla `public/list.html`
    - ruta: `games:creadores-por` → `/catalog/games/creators/<str:tipo>/<int:pk>/`, `games:creadores-por` → `/catalog/games/creators/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `idioma` → padre por id (campo `languages`); `type` → choice: `CO`, `IN`, `NG`, `unknown`
    - fondo: `bg-games-creator`
  - `CreatorPublicListView` (pública) — lista — Catálogo público de CREADORES de juegos: search_words por nombre y llegar
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCreator`, `PublicListView`
    - depende de: datos de `games:creadores-catalogo-data`; plantilla `public/list.html`
    - ruta: `games:creadores-catalogo` → `/catalog/games/creators/list/`
    - fondo: `bg-games-creator`
  - `CreatorSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreator`, `BaseSelectView`
    - ruta: `panel:creator_select` → `/panel/creator/select/`
    - fondo: `bg-games-creator`
  - `CreatorUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreator`, `BaseUpdate`
    - depende de: formulario `CreatorForm`; vuelve a `panel:creator_list`; al guardar va a `panel:creator_list`; plantilla `games/form/creator.html`
    - ruta: `panel:creator_update` → `/panel/creator/<int:pk>/update/`
    - fondo: `bg-games-creator`
- Filtros:
  - `CreatorFilters`: Tipo (`type`), Idioma (`languages`) — para `CreatorDataView`, `CreatorPublicDataView`

### Modelo: `CreatorLink` (`apps/games/models.py`)

- Formulario: `CreatorLinkForm` (`apps/games/forms.py`) — campos: `creator`, `source`, `external_id`, `url`, `is_active`
- Vistas:
  - `CreatorLinkCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreatorLink`, `BaseCreate`
    - depende de: formulario `CreatorLinkForm`; vuelve a `panel:creator-link_list`; al guardar va a `panel:creator-link_list`; plantilla `games/form/creator_link.html`
    - ruta: `panel:creator-link_create` → `/panel/creator-link/create/`
    - fondo: `bg-games-creator-link`
  - `CreatorLinkDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreatorLinkContext`, `AdminDataView`
    - ruta: `panel:creator-link_data` → `/panel/creator-link/data/`, `panel:creator-link_data-by` → `/panel/creator-link/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `creador` → padre por id (campo `creator`)
    - fondo: `bg-games-creator-link`
  - `CreatorLinkDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreatorLink`, `BaseDelete`
    - depende de: vuelve a `panel:creator-link_list`; al guardar va a `panel:creator-link_list`
    - ruta: `panel:creator-link_delete` → `/panel/creator-link/<int:pk>/delete/`
    - fondo: `bg-games-creator-link`
  - `CreatorLinkDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCreatorLink`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:creator-link_list`; plantilla `games/detail/creator_link.html`
    - ruta: `panel:creator-link_detail` → `/panel/creator-link/<int:pk>/`
    - fondo: `bg-games-creator-link`
  - `CreatorLinkListByView` (panel) — lista «por» (acotada a un padre) — creador.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCreatorLinkContext`, `AdminListByView`
    - depende de: datos de `panel:creator-link_data-by`
    - ruta: `panel:creator-link_by` → `/panel/creator-link/<str:tipo>/<str:pk>/`
    - mapa «by»: `creador` → padre por id (campo `creator`)
    - fondo: `bg-games-creator-link`
  - `CreatorLinkListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCreatorLink`, `AdminListView`
    - depende de: datos de `panel:creator-link_data`
    - ruta: `panel:creator-link_list` → `/panel/creator-link/`
    - fondo: `bg-games-creator-link`
  - `CreatorLinkSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreatorLink`, `BaseSelectView`
    - ruta: `panel:creator-link_select` → `/panel/creator-link/select/`
    - fondo: `bg-games-creator-link`
  - `CreatorLinkUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreatorLink`, `BaseUpdate`
    - depende de: formulario `CreatorLinkForm`; vuelve a `panel:creator-link_list`; al guardar va a `panel:creator-link_list`; plantilla `games/form/creator_link.html`
    - ruta: `panel:creator-link_update` → `/panel/creator-link/<int:pk>/update/`
    - fondo: `bg-games-creator-link`

### Modelo: `CreatorNickname` (`apps/games/models.py`)

- Formulario: `CreatorNicknameForm` (`apps/games/forms.py`) — campos: `creator`, `nickname`, `is_active`
- Vistas:
  - `CreatorNicknameCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreatorNickname`, `BaseCreate`
    - depende de: formulario `CreatorNicknameForm`; vuelve a `panel:creator-nickname_list`; al guardar va a `panel:creator-nickname_list`; plantilla `games/form/creator_nickname.html`
    - ruta: `panel:creator-nickname_create` → `/panel/creator-nickname/create/`
    - fondo: `bg-games-creator-nickname`
  - `CreatorNicknameDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreatorNicknameContext`, `AdminDataView`
    - ruta: `panel:creator-nickname_data` → `/panel/creator-nickname/data/`, `panel:creator-nickname_data-by` → `/panel/creator-nickname/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `creador` → padre por id (campo `creator`)
    - fondo: `bg-games-creator-nickname`
  - `CreatorNicknameDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreatorNickname`, `BaseDelete`
    - depende de: vuelve a `panel:creator-nickname_list`; al guardar va a `panel:creator-nickname_list`
    - ruta: `panel:creator-nickname_delete` → `/panel/creator-nickname/<int:pk>/delete/`
    - fondo: `bg-games-creator-nickname`
  - `CreatorNicknameDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCreatorNickname`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:creator-nickname_list`; plantilla `games/detail/creator_nickname.html`
    - ruta: `panel:creator-nickname_detail` → `/panel/creator-nickname/<int:pk>/`
    - fondo: `bg-games-creator-nickname`
  - `CreatorNicknameListByView` (panel) — lista «por» (acotada a un padre) — creador.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCreatorNicknameContext`, `AdminListByView`
    - depende de: datos de `panel:creator-nickname_data-by`
    - ruta: `panel:creator-nickname_by` → `/panel/creator-nickname/<str:tipo>/<str:pk>/`
    - mapa «by»: `creador` → padre por id (campo `creator`)
    - fondo: `bg-games-creator-nickname`
  - `CreatorNicknameListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCreatorNickname`, `AdminListView`
    - depende de: datos de `panel:creator-nickname_data`
    - ruta: `panel:creator-nickname_list` → `/panel/creator-nickname/`
    - fondo: `bg-games-creator-nickname`
  - `CreatorNicknameSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreatorNickname`, `BaseSelectView`
    - ruta: `panel:creator-nickname_select` → `/panel/creator-nickname/select/`
    - fondo: `bg-games-creator-nickname`
  - `CreatorNicknameUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCreatorNickname`, `BaseUpdate`
    - depende de: formulario `CreatorNicknameForm`; vuelve a `panel:creator-nickname_list`; al guardar va a `panel:creator-nickname_list`; plantilla `games/form/creator_nickname.html`
    - ruta: `panel:creator-nickname_update` → `/panel/creator-nickname/<int:pk>/update/`
    - fondo: `bg-games-creator-nickname`

### Modelo: `DataVndbCharacter` (`apps/games/models.py`)

- Formulario: `DataVndbCharacterForm` (`apps/games/forms.py`) — campos: `vndb_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataVndbCharacterCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbCharacter`, `BaseCreate`
    - depende de: formulario `DataVndbCharacterForm`; vuelve a `panel:data-vndb-character_list`; al guardar va a `panel:data-vndb-character_list`
    - ruta: `panel:data-vndb-character_create` → `/panel/data-vndb-character/create/`
    - fondo: `bg-games-data-vndb-character`
  - `DataVndbCharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDataVndbCharacter`, `AdminDataView`
    - ruta: `panel:data-vndb-character_data` → `/panel/data-vndb-character/data/`
    - fondo: `bg-games-data-vndb-character`
  - `DataVndbCharacterDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:data-vndb-character_list`; al guardar va a `panel:data-vndb-character_list`
    - ruta: `panel:data-vndb-character_delete` → `/panel/data-vndb-character/<int:pk>/delete/`
    - fondo: `bg-games-data-vndb-character`
  - `DataVndbCharacterDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseDataVndbCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-vndb-character_list`; plantilla `games/detail/data_vndb_character.html`
    - ruta: `panel:data-vndb-character_detail` → `/panel/data-vndb-character/<int:pk>/`
    - fondo: `bg-games-data-vndb-character`
  - `DataVndbCharacterListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseDataVndbCharacter`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-vndb-character_data`
    - ruta: `panel:data-vndb-character_list` → `/panel/data-vndb-character/`
    - fondo: `bg-games-data-vndb-character`
  - `DataVndbCharacterUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbCharacter`, `BaseUpdate`
    - depende de: formulario `DataVndbCharacterForm`; vuelve a `panel:data-vndb-character_list`; al guardar va a `panel:data-vndb-character_list`
    - ruta: `panel:data-vndb-character_update` → `/panel/data-vndb-character/<int:pk>/update/`
    - fondo: `bg-games-data-vndb-character`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataVndbCharacterDataView`

### Modelo: `DataVndbCreator` (`apps/games/models.py`)

- Formulario: `DataVndbCreatorForm` (`apps/games/forms.py`) — campos: `vndb_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataVndbCreatorCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbCreator`, `BaseCreate`
    - depende de: formulario `DataVndbCreatorForm`; vuelve a `panel:data-vndb-creator_list`; al guardar va a `panel:data-vndb-creator_list`
    - ruta: `panel:data-vndb-creator_create` → `/panel/data-vndb-creator/create/`
    - fondo: `bg-games-data-vndb-creator`
  - `DataVndbCreatorDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDataVndbCreator`, `AdminDataView`
    - ruta: `panel:data-vndb-creator_data` → `/panel/data-vndb-creator/data/`
    - fondo: `bg-games-data-vndb-creator`
  - `DataVndbCreatorDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbCreator`, `BaseDelete`
    - depende de: vuelve a `panel:data-vndb-creator_list`; al guardar va a `panel:data-vndb-creator_list`
    - ruta: `panel:data-vndb-creator_delete` → `/panel/data-vndb-creator/<int:pk>/delete/`
    - fondo: `bg-games-data-vndb-creator`
  - `DataVndbCreatorDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseDataVndbCreator`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-vndb-creator_list`; plantilla `games/detail/data_vndb_creator.html`
    - ruta: `panel:data-vndb-creator_detail` → `/panel/data-vndb-creator/<int:pk>/`
    - fondo: `bg-games-data-vndb-creator`
  - `DataVndbCreatorListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseDataVndbCreator`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-vndb-creator_data`
    - ruta: `panel:data-vndb-creator_list` → `/panel/data-vndb-creator/`
    - fondo: `bg-games-data-vndb-creator`
  - `DataVndbCreatorUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbCreator`, `BaseUpdate`
    - depende de: formulario `DataVndbCreatorForm`; vuelve a `panel:data-vndb-creator_list`; al guardar va a `panel:data-vndb-creator_list`
    - ruta: `panel:data-vndb-creator_update` → `/panel/data-vndb-creator/<int:pk>/update/`
    - fondo: `bg-games-data-vndb-creator`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataVndbCreatorDataView`

### Modelo: `DataF95Game` (`apps/games/models.py`)

- Formulario: `DataF95GameForm` (`apps/games/forms.py`) — campos: `f95_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataF95GameCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataF95Game`, `BaseCreate`
    - depende de: formulario `DataF95GameForm`; vuelve a `panel:data-f95-game_list`; al guardar va a `panel:data-f95-game_list`
    - ruta: `panel:data-f95-game_create` → `/panel/data-f95-game/create/`
    - fondo: `bg-games-data-f95-game`
  - `DataF95GameDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDataF95Game`, `AdminDataView`
    - ruta: `panel:data-f95-game_data` → `/panel/data-f95-game/data/`
    - fondo: `bg-games-data-f95-game`
  - `DataF95GameDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataF95Game`, `BaseDelete`
    - depende de: vuelve a `panel:data-f95-game_list`; al guardar va a `panel:data-f95-game_list`
    - ruta: `panel:data-f95-game_delete` → `/panel/data-f95-game/<int:pk>/delete/`
    - fondo: `bg-games-data-f95-game`
  - `DataF95GameDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseDataF95Game`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-f95-game_list`; plantilla `games/detail/data_f95_game.html`
    - ruta: `panel:data-f95-game_detail` → `/panel/data-f95-game/<int:pk>/`
    - fondo: `bg-games-data-f95-game`
  - `DataF95GameListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseDataF95Game`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-f95-game_data`
    - ruta: `panel:data-f95-game_list` → `/panel/data-f95-game/`
    - fondo: `bg-games-data-f95-game`
  - `DataF95GameUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataF95Game`, `BaseUpdate`
    - depende de: formulario `DataF95GameForm`; vuelve a `panel:data-f95-game_list`; al guardar va a `panel:data-f95-game_list`
    - ruta: `panel:data-f95-game_update` → `/panel/data-f95-game/<int:pk>/update/`
    - fondo: `bg-games-data-f95-game`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataF95GameDataView`

### Modelo: `DataF95Creator` (`apps/games/models.py`)

- Formulario: `DataF95CreatorForm` (`apps/games/forms.py`) — campos: `fzone_id`
- Vistas:
  - `DataF95CreatorCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataF95Creator`, `BaseCreate`
    - depende de: formulario `DataF95CreatorForm`; vuelve a `panel:data-f95-creator_list`; al guardar va a `panel:data-f95-creator_list`
    - ruta: `panel:data-f95-creator_create` → `/panel/data-f95-creator/create/`
    - fondo: `bg-games-data-f95-creator`
  - `DataF95CreatorDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDataF95Creator`, `AdminDataView`
    - ruta: `panel:data-f95-creator_data` → `/panel/data-f95-creator/data/`
    - fondo: `bg-games-data-f95-creator`
  - `DataF95CreatorDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataF95Creator`, `BaseDelete`
    - depende de: vuelve a `panel:data-f95-creator_list`; al guardar va a `panel:data-f95-creator_list`
    - ruta: `panel:data-f95-creator_delete` → `/panel/data-f95-creator/<int:pk>/delete/`
    - fondo: `bg-games-data-f95-creator`
  - `DataF95CreatorDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseDataF95Creator`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-f95-creator_list`; plantilla `games/detail/data_f95_creator.html`
    - ruta: `panel:data-f95-creator_detail` → `/panel/data-f95-creator/<int:pk>/`
    - fondo: `bg-games-data-f95-creator`
  - `DataF95CreatorListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseDataF95Creator`, `AdminListView`
    - depende de: datos de `panel:data-f95-creator_data`
    - ruta: `panel:data-f95-creator_list` → `/panel/data-f95-creator/`
    - fondo: `bg-games-data-f95-creator`
  - `DataF95CreatorUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataF95Creator`, `BaseUpdate`
    - depende de: formulario `DataF95CreatorForm`; vuelve a `panel:data-f95-creator_list`; al guardar va a `panel:data-f95-creator_list`
    - ruta: `panel:data-f95-creator_update` → `/panel/data-f95-creator/<int:pk>/update/`
    - fondo: `bg-games-data-f95-creator`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataF95CreatorDataView`

### Modelo: `DataVndbGame` (`apps/games/models.py`)

- Formulario: `DataVndbGameForm` (`apps/games/forms.py`) — campos: `vndb_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataVndbGameCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbGame`, `BaseCreate`
    - depende de: formulario `DataVndbGameForm`; vuelve a `panel:data-vndb-game_list`; al guardar va a `panel:data-vndb-game_list`
    - ruta: `panel:data-vndb-game_create` → `/panel/data-vndb-game/create/`
    - fondo: `bg-games-data-vndb-game`
  - `DataVndbGameDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDataVndbGame`, `AdminDataView`
    - ruta: `panel:data-vndb-game_data` → `/panel/data-vndb-game/data/`
    - fondo: `bg-games-data-vndb-game`
  - `DataVndbGameDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbGame`, `BaseDelete`
    - depende de: vuelve a `panel:data-vndb-game_list`; al guardar va a `panel:data-vndb-game_list`
    - ruta: `panel:data-vndb-game_delete` → `/panel/data-vndb-game/<int:pk>/delete/`
    - fondo: `bg-games-data-vndb-game`
  - `DataVndbGameDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseDataVndbGame`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-vndb-game_list`; plantilla `games/detail/data_vndb_game.html`
    - ruta: `panel:data-vndb-game_detail` → `/panel/data-vndb-game/<int:pk>/`
    - fondo: `bg-games-data-vndb-game`
  - `DataVndbGameListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseDataVndbGame`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-vndb-game_data`
    - ruta: `panel:data-vndb-game_list` → `/panel/data-vndb-game/`
    - fondo: `bg-games-data-vndb-game`
  - `DataVndbGameUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbGame`, `BaseUpdate`
    - depende de: formulario `DataVndbGameForm`; vuelve a `panel:data-vndb-game_list`; al guardar va a `panel:data-vndb-game_list`
    - ruta: `panel:data-vndb-game_update` → `/panel/data-vndb-game/<int:pk>/update/`
    - fondo: `bg-games-data-vndb-game`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataVndbGameDataView`

### Modelo: `DataVndbRelease` (`apps/games/models.py`)

- Formulario: `DataVndbReleaseForm` (`apps/games/forms.py`) — campos: `vndb_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataVndbReleaseCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbRelease`, `BaseCreate`
    - depende de: formulario `DataVndbReleaseForm`; vuelve a `panel:data-vndb-release_list`; al guardar va a `panel:data-vndb-release_list`
    - ruta: `panel:data-vndb-release_create` → `/panel/data-vndb-release/create/`
    - fondo: `bg-games-data-vndb-release`
  - `DataVndbReleaseDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDataVndbRelease`, `AdminDataView`
    - ruta: `panel:data-vndb-release_data` → `/panel/data-vndb-release/data/`
    - fondo: `bg-games-data-vndb-release`
  - `DataVndbReleaseDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbRelease`, `BaseDelete`
    - depende de: vuelve a `panel:data-vndb-release_list`; al guardar va a `panel:data-vndb-release_list`
    - ruta: `panel:data-vndb-release_delete` → `/panel/data-vndb-release/<int:pk>/delete/`
    - fondo: `bg-games-data-vndb-release`
  - `DataVndbReleaseDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseDataVndbRelease`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-vndb-release_list`; plantilla `games/detail/data_vndb_release.html`
    - ruta: `panel:data-vndb-release_detail` → `/panel/data-vndb-release/<int:pk>/`
    - fondo: `bg-games-data-vndb-release`
  - `DataVndbReleaseListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseDataVndbRelease`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-vndb-release_data`
    - ruta: `panel:data-vndb-release_list` → `/panel/data-vndb-release/`
    - fondo: `bg-games-data-vndb-release`
  - `DataVndbReleaseUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDataVndbRelease`, `BaseUpdate`
    - depende de: formulario `DataVndbReleaseForm`; vuelve a `panel:data-vndb-release_list`; al guardar va a `panel:data-vndb-release_list`
    - ruta: `panel:data-vndb-release_update` → `/panel/data-vndb-release/<int:pk>/update/`
    - fondo: `bg-games-data-vndb-release`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataVndbReleaseDataView`

### Modelo: `DevelopmentEngine` (`apps/games/models.py`)

- Formulario: `DevelopmentEngineForm` (`apps/games/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `DevelopmentEngineCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDevelopmentEngine`, `BaseCreate`
    - depende de: formulario `DevelopmentEngineForm`; vuelve a `panel:game-engine_list`; al guardar va a `panel:game-engine_list`; plantilla `games/form/development_engine.html`
    - ruta: `panel:game-engine_create` → `/panel/game-engine/create/`
    - fondo: `bg-games-development-engine`
  - `DevelopmentEngineDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDevelopmentEngine`, `AdminDataView`
    - ruta: `panel:game-engine_data` → `/panel/game-engine/data/`
    - fondo: `bg-games-development-engine`
  - `DevelopmentEngineDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDevelopmentEngine`, `BaseDelete`
    - depende de: vuelve a `panel:game-engine_list`; al guardar va a `panel:game-engine_list`
    - ruta: `panel:game-engine_delete` → `/panel/game-engine/<int:pk>/delete/`
    - fondo: `bg-games-development-engine`
  - `DevelopmentEngineDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseDevelopmentEngine`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-engine_list`; plantilla `games/detail/development_engine.html`
    - ruta: `panel:game-engine_detail` → `/panel/game-engine/<int:pk>/`
    - fondo: `bg-games-development-engine`
  - `DevelopmentEngineListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseDevelopmentEngine`, `AdminListView`
    - depende de: datos de `panel:game-engine_data`
    - ruta: `panel:game-engine_list` → `/panel/game-engine/`
    - fondo: `bg-games-development-engine`
  - `DevelopmentEngineSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseDevelopmentEngine`, `BaseSelectView`
    - ruta: `panel:game-engine_select` → `/panel/game-engine/select/`
    - fondo: `bg-games-development-engine`
  - `DevelopmentEngineUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseDevelopmentEngine`, `BaseUpdate`
    - depende de: formulario `DevelopmentEngineForm`; vuelve a `panel:game-engine_list`; al guardar va a `panel:game-engine_list`; plantilla `games/form/development_engine.html`
    - ruta: `panel:game-engine_update` → `/panel/game-engine/<int:pk>/update/`
    - fondo: `bg-games-development-engine`

### Modelo: `Game` (`apps/games/models.py`)

- Formulario: `GameForm` (`apps/games/forms.py`) — campos: `title`, `version`, `release_date`, `synopsis`, `background`, `status`, `type`, `engine`, `mediums`, `platforms`, `developers`, `publishers`, `languages`, `genres`, `is_active`
- Vistas:
  - `GameCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGame`, `BaseCreate`
    - depende de: formulario `GameForm`; vuelve a `panel:game_list`; al guardar va a `panel:game_list`; plantilla `games/form/game.html`
    - ruta: `panel:game_create` → `/panel/game/create/`
    - fondo: `bg-games-game`
  - `GameDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameContext`, `AdminDataView`
    - ruta: `panel:game_data` → `/panel/game/data/`, `panel:game_data-by` → `/panel/game/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `plataforma` → padre por id (campo `platforms`); `idioma` → padre por id (campo `languages`); `motor` → padre por id (campo `engine`); `medio` → padre por id (campo `mediums`); `creador` → padre por id (campo `developers`); `editora` → padre por id (campo `publishers`); `type` → choice: `vn`, `game`, `collection`; `status` → choice: `unknown`, `developing`, `completed`, `abandoned`, `onhold`
    - fondo: `bg-games-game`
  - `GameDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGame`, `BaseDelete`
    - depende de: vuelve a `panel:game_list`; al guardar va a `panel:game_list`
    - ruta: `panel:game_delete` → `/panel/game/<int:pk>/delete/`
    - fondo: `bg-games-game`
  - `GameDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGame`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game_list`; plantilla `games/detail/game.html`
    - ruta: `panel:game_detail` → `/panel/game/<int:pk>/`
    - fondo: `bg-games-game`
  - `GameListByView` (panel) — lista «por» (acotada a un padre) — genero, plataforma, idioma, motor, medio, creador, editora, tipo, estado.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseGameContext`, `AdminListByView`
    - depende de: datos de `panel:game_data-by`
    - ruta: `panel:game_by` → `/panel/game/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `plataforma` → padre por id (campo `platforms`); `idioma` → padre por id (campo `languages`); `motor` → padre por id (campo `engine`); `medio` → padre por id (campo `mediums`); `creador` → padre por id (campo `developers`); `editora` → padre por id (campo `publishers`); `type` → choice: `vn`, `game`, `collection`; `status` → choice: `unknown`, `developing`, `completed`, `abandoned`, `onhold`
    - fondo: `bg-games-game`
  - `GameListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGame`, `_ReobtenerVndb`, `AdminListView`
    - depende de: datos de `panel:game_data`
    - ruta: `panel:game_list` → `/panel/game/`
    - fondo: `bg-games-game`
  - `GamePublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameContext`, `PublicDataView`
    - ruta: `games:lista-data` → `/catalog/games/list/data/`, `games:por-data` → `/catalog/games/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `plataforma` → padre por id (campo `platforms`); `idioma` → padre por id (campo `languages`); `motor` → padre por id (campo `engine`); `medio` → padre por id (campo `mediums`); `creador` → padre por id (campo `developers`); `editora` → padre por id (campo `publishers`); `type` → choice: `vn`, `game`, `collection`; `status` → choice: `unknown`, `developing`, `completed`, `abandoned`, `onhold`
    - fondo: `bg-games-game`
  - `GamePublicDetailView` (pública) — ficha — Ficha pública de un juego: el mismo HTML que en gestión, sin botones y con la colección.
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGame`, `BasePublicDetailView`
    - depende de: vuelve a `games:lista`; plantilla `games/detail/game.html`
    - ruta: `games:detalle` → `/catalog/games/game/<int:pk>/<slug:slug>/`, `games:detalle` → `/catalog/games/game/<int:pk>/`
    - fondo: `bg-games-game`
  - `GamePublicListByView` (pública) — lista «por» (acotada a un padre) — genero, plataforma, idioma, motor, medio, creador, editora, tipo, estado.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseGameContext`, `PublicListByView`
    - depende de: datos de `games:por-data`; plantilla `public/list.html`
    - ruta: `games:por` → `/catalog/games/<str:tipo>/<int:pk>/`, `games:por` → `/catalog/games/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `plataforma` → padre por id (campo `platforms`); `idioma` → padre por id (campo `languages`); `motor` → padre por id (campo `engine`); `medio` → padre por id (campo `mediums`); `creador` → padre por id (campo `developers`); `editora` → padre por id (campo `publishers`); `type` → choice: `vn`, `game`, `collection`; `status` → choice: `unknown`, `developing`, `completed`, `abandoned`, `onhold`
    - fondo: `bg-games-game`
  - `GamePublicListView` (pública) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGame`, `PublicListView`
    - depende de: datos de `games:lista-data`; plantilla `public/list.html`
    - ruta: `games:lista` → `/catalog/games/list/`
    - fondo: `bg-games-game`
  - `GameSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGame`, `BaseSelectView`
    - ruta: `panel:game_select` → `/panel/game/select/`
    - fondo: `bg-games-game`
  - `GameUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGame`, `BaseUpdate`
    - depende de: formulario `GameForm`; vuelve a `panel:game_list`; al guardar va a `panel:game_list`; plantilla `games/form/game.html`
    - ruta: `panel:game_update` → `/panel/game/<int:pk>/update/`
    - fondo: `bg-games-game`
- Filtros:
  - `GameFilters`: Género (`genres`), Tipo (`type`), Creador (`developers`), Editora (`publishers`), Estado (`status`), Motor (`engine`), Plataforma (`platforms`), Año (`release_date`) — para `GameDataView`, `GamePublicDataView`

### Modelo: `Character` (`apps/games/models.py`)

- Formulario: `CharacterForm` (`apps/games/forms.py`) — campos: `name`, `original`, `description`, `sex`, `age`, `birthday`, `is_active`
- Vistas:
  - `CharacterCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacter`, `BaseCreate`
    - depende de: formulario `CharacterForm`; vuelve a `panel:game-character_list`; al guardar va a `panel:game-character_list`
    - ruta: `panel:game-character_create` → `/panel/game-character/create/`
    - fondo: `bg-games-game-character`
  - `CharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCharacterContext`, `AdminDataView`
    - ruta: `panel:game-character_data` → `/panel/game-character/data/`, `panel:game-character_data-by` → `/panel/game-character/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-character`
  - `CharacterDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:game-character_list`; al guardar va a `panel:game-character_list`
    - ruta: `panel:game-character_delete` → `/panel/game-character/<int:pk>/delete/`
    - fondo: `bg-games-game-character`
  - `CharacterDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-character_list`; plantilla `games/detail/character.html`
    - ruta: `panel:game-character_detail` → `/panel/game-character/<int:pk>/`
    - fondo: `bg-games-game-character`
  - `CharacterListByView` (panel) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCharacterContext`, `AdminListByView`
    - depende de: datos de `panel:game-character_data-by`
    - ruta: `panel:game-character_by` → `/panel/game-character/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-character`
  - `CharacterListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCharacter`, `AdminListView`
    - depende de: datos de `panel:game-character_data`
    - ruta: `panel:game-character_list` → `/panel/game-character/`
    - fondo: `bg-games-game-character`
  - `CharacterPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCharacterContext`, `PublicDataView`
    - ruta: `games:personajes-por-data` → `/catalog/games/characters/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-character`
  - `CharacterPublicDetailView` (pública) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCharacter`, `BasePublicDetailView`
    - depende de: vuelve a `games:lista`; plantilla `games/detail/character.html`
    - ruta: `games:personaje` → `/catalog/games/character/<int:pk>/<slug:slug>/`, `games:personaje` → `/catalog/games/character/<int:pk>/`
    - fondo: `bg-games-game-character`
  - `CharacterPublicListByView` (pública) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCharacterContext`, `PublicListByView`
    - depende de: datos de `games:personajes-por-data`; plantilla `public/list.html`
    - ruta: `games:personajes-por` → `/catalog/games/characters/<str:tipo>/<int:pk>/`, `games:personajes-por` → `/catalog/games/characters/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-character`
  - `CharacterSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCharacter`, `BaseSelectView`
    - ruta: `panel:game-character_select` → `/panel/game-character/select/`
    - fondo: `bg-games-game-character`
  - `CharacterUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacter`, `BaseUpdate`
    - depende de: formulario `CharacterForm`; vuelve a `panel:game-character_list`; al guardar va a `panel:game-character_list`
    - ruta: `panel:game-character_update` → `/panel/game-character/<int:pk>/update/`
    - fondo: `bg-games-game-character`
- Filtros:
  - `CharacterFilters`: Rol (`roles__role`), Sexo (`sex`) — para `CharacterDataView`, `CharacterPublicDataView`

### Modelo: `CharacterImage` (`apps/games/models.py`)

- Formulario: `CharacterImageForm` (`apps/games/forms.py`) — campos: `character`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `CharacterImageCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacterImage`, `BaseCreate`
    - depende de: formulario `CharacterImageForm`; vuelve a `panel:game-character-image_list`; al guardar va a `panel:game-character-image_list`
    - ruta: `panel:game-character-image_create` → `/panel/game-character-image/create/`
    - fondo: `bg-games-game-character-image`
  - `CharacterImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCharacterImageContext`, `AdminDataView`
    - ruta: `panel:game-character-image_data` → `/panel/game-character-image/data/`, `panel:game-character-image_data-by` → `/panel/game-character-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego-personaje` → padre por id (campo `character`)
    - fondo: `bg-games-game-character-image`
  - `CharacterImageDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacterImage`, `BaseDelete`
    - depende de: vuelve a `panel:game-character-image_list`; al guardar va a `panel:game-character-image_list`
    - ruta: `panel:game-character-image_delete` → `/panel/game-character-image/<int:pk>/delete/`
    - fondo: `bg-games-game-character-image`
  - `CharacterImageDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCharacterImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-character-image_list`; plantilla `games/detail/character_image.html`
    - ruta: `panel:game-character-image_detail` → `/panel/game-character-image/<int:pk>/`
    - fondo: `bg-games-game-character-image`
  - `CharacterImageListByView` (panel) — lista «por» (acotada a un padre) — juego-personaje.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCharacterImageContext`, `AdminListByView`
    - depende de: datos de `panel:game-character-image_data-by`
    - ruta: `panel:game-character-image_by` → `/panel/game-character-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego-personaje` → padre por id (campo `character`)
    - fondo: `bg-games-game-character-image`
  - `CharacterImageListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCharacterImage`, `AdminListView`
    - depende de: datos de `panel:game-character-image_data`
    - ruta: `panel:game-character-image_list` → `/panel/game-character-image/`
    - fondo: `bg-games-game-character-image`
  - `CharacterImageUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacterImage`, `BaseUpdate`
    - depende de: formulario `CharacterImageForm`; vuelve a `panel:game-character-image_list`; al guardar va a `panel:game-character-image_list`
    - ruta: `panel:game-character-image_update` → `/panel/game-character-image/<int:pk>/update/`
    - fondo: `bg-games-game-character-image`

### Modelo: `CharacterRole` (`apps/games/models.py`)

- Formulario: `CharacterRoleForm` (`apps/games/forms.py`) — campos: `character`, `game`, `role`, `is_active`
- Vistas:
  - `CharacterRoleCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacterRole`, `BaseCreate`
    - depende de: formulario `CharacterRoleForm`; vuelve a `panel:game-character-role_list`; al guardar va a `panel:game-character-role_list`
    - ruta: `panel:game-character-role_create` → `/panel/game-character-role/create/`
    - fondo: `bg-games-game-character-role`
  - `CharacterRoleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCharacterRoleContext`, `AdminDataView`
    - ruta: `panel:game-character-role_data` → `/panel/game-character-role/data/`, `panel:game-character-role_data-by` → `/panel/game-character-role/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego-personaje` → padre por id (campo `character`); `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game-character-role`
  - `CharacterRoleDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacterRole`, `BaseDelete`
    - depende de: vuelve a `panel:game-character-role_list`; al guardar va a `panel:game-character-role_list`
    - ruta: `panel:game-character-role_delete` → `/panel/game-character-role/<int:pk>/delete/`
    - fondo: `bg-games-game-character-role`
  - `CharacterRoleDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseCharacterRole`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-character-role_list`; plantilla `games/detail/character_role.html`
    - ruta: `panel:game-character-role_detail` → `/panel/game-character-role/<int:pk>/`
    - fondo: `bg-games-game-character-role`
  - `CharacterRoleListByView` (panel) — lista «por» (acotada a un padre) — juego-personaje, juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseCharacterRoleContext`, `AdminListByView`
    - depende de: datos de `panel:game-character-role_data-by`
    - ruta: `panel:game-character-role_by` → `/panel/game-character-role/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego-personaje` → padre por id (campo `character`); `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game-character-role`
  - `CharacterRoleListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCharacterRole`, `AdminListView`
    - depende de: datos de `panel:game-character-role_data`
    - ruta: `panel:game-character-role_list` → `/panel/game-character-role/`
    - fondo: `bg-games-game-character-role`
  - `CharacterRoleUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseCharacterRole`, `BaseUpdate`
    - depende de: formulario `CharacterRoleForm`; vuelve a `panel:game-character-role_list`; al guardar va a `panel:game-character-role_list`
    - ruta: `panel:game-character-role_update` → `/panel/game-character-role/<int:pk>/update/`
    - fondo: `bg-games-game-character-role`

### Modelo: `GameImage` (`apps/games/models.py`)

- Formulario: `GameImageForm` (`apps/games/forms.py`) — campos: `game`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `GameImageCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameImage`, `BaseCreate`
    - depende de: formulario `GameImageForm`; vuelve a `panel:game-image_list`; al guardar va a `panel:game-image_list`; plantilla `games/form/game_image.html`
    - ruta: `panel:game-image_create` → `/panel/game-image/create/`
    - fondo: `bg-games-game-image`
  - `GameImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameImageContext`, `AdminDataView`
    - ruta: `panel:game-image_data` → `/panel/game-image/data/`, `panel:game-image_data-by` → `/panel/game-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game-image`
  - `GameImageDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameImage`, `BaseDelete`
    - depende de: vuelve a `panel:game-image_list`; al guardar va a `panel:game-image_list`
    - ruta: `panel:game-image_delete` → `/panel/game-image/<int:pk>/delete/`
    - fondo: `bg-games-game-image`
  - `GameImageDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGameImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-image_list`; plantilla `games/detail/game_image.html`
    - ruta: `panel:game-image_detail` → `/panel/game-image/<int:pk>/`
    - fondo: `bg-games-game-image`
  - `GameImageListByView` (panel) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseGameImageContext`, `AdminListByView`
    - depende de: datos de `panel:game-image_data-by`
    - ruta: `panel:game-image_by` → `/panel/game-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game-image`
  - `GameImageListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGameImage`, `AdminListView`
    - depende de: datos de `panel:game-image_data`
    - ruta: `panel:game-image_list` → `/panel/game-image/`
    - fondo: `bg-games-game-image`
  - `GameImagePublicListByView` (pública) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseGameImageContext`, `PublicListByView`
    - depende de: datos de `games:imagenes-por-data`; plantilla `public/list.html`
    - ruta: `games:imagenes-por` → `/catalog/games/images/<str:tipo>/<int:pk>/`, `games:imagenes-por` → `/catalog/games/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game`
  - `GameImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameImage`, `BaseSelectView`
    - ruta: `panel:game-image_select` → `/panel/game-image/select/`
    - fondo: `bg-games-game-image`
  - `GameImageUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameImage`, `BaseUpdate`
    - depende de: formulario `GameImageForm`; vuelve a `panel:game-image_list`; al guardar va a `panel:game-image_list`; plantilla `games/form/game_image.html`
    - ruta: `panel:game-image_update` → `/panel/game-image/<int:pk>/update/`
    - fondo: `bg-games-game-image`
  - `GameImagesPublicDataView` (panel) — datos JSON de la lista (sPublic)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameImageContext`, `PublicDataView`
    - ruta: `games:imagenes-por-data` → `/catalog/games/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game-image`

### Modelo: `GameLink` (`apps/games/models.py`)

- Formulario: `GameLinkForm` (`apps/games/forms.py`) — campos: `game`, `source`, `external_id`, `url`, `is_active`
- Vistas:
  - `GameLinkCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameLink`, `BaseCreate`
    - depende de: formulario `GameLinkForm`; vuelve a `panel:game-link_list`; al guardar va a `panel:game-link_list`; plantilla `games/form/game_link.html`
    - ruta: `panel:game-link_create` → `/panel/game-link/create/`
    - fondo: `bg-games-game-link`
  - `GameLinkDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameLinkContext`, `AdminDataView`
    - ruta: `panel:game-link_data` → `/panel/game-link/data/`, `panel:game-link_data-by` → `/panel/game-link/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game-link`
  - `GameLinkDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameLink`, `BaseDelete`
    - depende de: vuelve a `panel:game-link_list`; al guardar va a `panel:game-link_list`
    - ruta: `panel:game-link_delete` → `/panel/game-link/<int:pk>/delete/`
    - fondo: `bg-games-game-link`
  - `GameLinkDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGameLink`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-link_list`; plantilla `games/detail/game_link.html`
    - ruta: `panel:game-link_detail` → `/panel/game-link/<int:pk>/`
    - fondo: `bg-games-game-link`
  - `GameLinkListByView` (panel) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseGameLinkContext`, `AdminListByView`
    - depende de: datos de `panel:game-link_data-by`
    - ruta: `panel:game-link_by` → `/panel/game-link/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-game-link`
  - `GameLinkListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGameLink`, `AdminListView`
    - depende de: datos de `panel:game-link_data`
    - ruta: `panel:game-link_list` → `/panel/game-link/`
    - fondo: `bg-games-game-link`
  - `GameLinkSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameLink`, `BaseSelectView`
    - ruta: `panel:game-link_select` → `/panel/game-link/select/`
    - fondo: `bg-games-game-link`
  - `GameLinkUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameLink`, `BaseUpdate`
    - depende de: formulario `GameLinkForm`; vuelve a `panel:game-link_list`; al guardar va a `panel:game-link_list`; plantilla `games/form/game_link.html`
    - ruta: `panel:game-link_update` → `/panel/game-link/<int:pk>/update/`
    - fondo: `bg-games-game-link`

### Modelo: `GameLog` (`apps/games/models.py`)

- Formulario: `GameLogForm` (`apps/games/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `GameLogCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameLog`, `BaseCreate`
    - depende de: formulario `GameLogForm`; vuelve a `panel:game-log_list`; al guardar va a `panel:game-log_list`
    - ruta: `panel:game-log_create` → `/panel/game-log/create/`
    - fondo: `bg-games-game-log`
  - `GameLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameLog`, `AdminDataView`
    - ruta: `panel:game-log_data` → `/panel/game-log/data/`
    - fondo: `bg-games-game-log`
  - `GameLogDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameLog`, `BaseDelete`
    - depende de: vuelve a `panel:game-log_list`; al guardar va a `panel:game-log_list`
    - ruta: `panel:game-log_delete` → `/panel/game-log/<int:pk>/delete/`
    - fondo: `bg-games-game-log`
  - `GameLogDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGameLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-log_list`; plantilla `games/detail/game_log.html`
    - ruta: `panel:game-log_detail` → `/panel/game-log/<int:pk>/`
    - fondo: `bg-games-game-log`
  - `GameLogListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGameLog`, `AdminListView`
    - depende de: datos de `panel:game-log_data`
    - ruta: `panel:game-log_list` → `/panel/game-log/`
    - fondo: `bg-games-game-log`
  - `GameLogUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameLog`, `BaseUpdate`
    - depende de: formulario `GameLogForm`; vuelve a `panel:game-log_list`; al guardar va a `panel:game-log_list`
    - ruta: `panel:game-log_update` → `/panel/game-log/<int:pk>/update/`
    - fondo: `bg-games-game-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `GameLogDataView`

### Modelo: `Release` (`apps/games/models.py`)

- Formulario: `ReleaseForm` (`apps/games/forms.py`) — campos: `game`, `title`, `alttitle`, `released`, `minage`, `official`, `patch`, `freeware`, `is_active`
- Vistas:
  - `ReleaseCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseRelease`, `BaseCreate`
    - depende de: formulario `ReleaseForm`; vuelve a `panel:game-release_list`; al guardar va a `panel:game-release_list`
    - ruta: `panel:game-release_create` → `/panel/game-release/create/`
    - fondo: `bg-games-game-release`
  - `ReleaseDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseReleaseContext`, `AdminDataView`
    - ruta: `panel:game-release_data` → `/panel/game-release/data/`, `panel:game-release_data-by` → `/panel/game-release/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-release`
  - `ReleaseDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseRelease`, `BaseDelete`
    - depende de: vuelve a `panel:game-release_list`; al guardar va a `panel:game-release_list`
    - ruta: `panel:game-release_delete` → `/panel/game-release/<int:pk>/delete/`
    - fondo: `bg-games-game-release`
  - `ReleaseDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseRelease`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-release_list`; plantilla `games/detail/release.html`
    - ruta: `panel:game-release_detail` → `/panel/game-release/<int:pk>/`
    - fondo: `bg-games-game-release`
  - `ReleaseListByView` (panel) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseReleaseContext`, `AdminListByView`
    - depende de: datos de `panel:game-release_data-by`
    - ruta: `panel:game-release_by` → `/panel/game-release/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-release`
  - `ReleaseListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseRelease`, `AdminListView`
    - depende de: datos de `panel:game-release_data`
    - ruta: `panel:game-release_list` → `/panel/game-release/`
    - fondo: `bg-games-game-release`
  - `ReleasePublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseReleaseContext`, `PublicDataView`
    - ruta: `games:lanzamientos-por-data` → `/catalog/games/releases/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-release`
  - `ReleasePublicListByView` (pública) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseReleaseContext`, `PublicListByView`
    - depende de: datos de `games:lanzamientos-por-data`; plantilla `public/list.html`
    - ruta: `games:lanzamientos-por` → `/catalog/games/releases/<str:tipo>/<int:pk>/`, `games:lanzamientos-por` → `/catalog/games/releases/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `juego` → padre por id (campo `games.Game`)
    - fondo: `bg-games-game-release`
  - `ReleaseUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseRelease`, `BaseUpdate`
    - depende de: formulario `ReleaseForm`; vuelve a `panel:game-release_list`; al guardar va a `panel:game-release_list`
    - ruta: `panel:game-release_update` → `/panel/game-release/<int:pk>/update/`
    - fondo: `bg-games-game-release`
- Filtros:
  - `ReleaseFilters`: Año (`released`) — para `ReleaseDataView`, `ReleasePublicDataView`

### Modelo: `GameTitle` (`apps/games/models.py`)

- Formulario: `GameTitleForm` (`apps/games/forms.py`) — campos: `game`, `title_lang`, `title`, `is_active`
- Vistas:
  - `GameTitleCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameTitle`, `BaseCreate`
    - depende de: formulario `GameTitleForm`; vuelve a `panel:game-title_list`; al guardar va a `panel:game-title_list`; plantilla `games/form/game_title.html`
    - ruta: `panel:game-title_create` → `/panel/game-title/create/`
    - fondo: `bg-games-title-game`
  - `GameTitleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameTitleContext`, `AdminDataView`
    - ruta: `panel:game-title_data` → `/panel/game-title/data/`, `panel:game-title_data-by` → `/panel/game-title/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-title-game`
  - `GameTitleDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameTitle`, `BaseDelete`
    - depende de: vuelve a `panel:game-title_list`; al guardar va a `panel:game-title_list`
    - ruta: `panel:game-title_delete` → `/panel/game-title/<int:pk>/delete/`
    - fondo: `bg-games-title-game`
  - `GameTitleDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGameTitle`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-title_list`; plantilla `games/detail/game_title.html`
    - ruta: `panel:game-title_detail` → `/panel/game-title/<int:pk>/`
    - fondo: `bg-games-title-game`
  - `GameTitleListByView` (panel) — lista «por» (acotada a un padre) — juego.
    - archivo: `apps/games/views/v5_list_by.py` · hereda de `BaseGameTitleContext`, `AdminListByView`
    - depende de: datos de `panel:game-title_data-by`
    - ruta: `panel:game-title_by` → `/panel/game-title/<str:tipo>/<str:pk>/`
    - mapa «by»: `juego` → padre por id (campo `game`)
    - fondo: `bg-games-title-game`
  - `GameTitleListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGameTitle`, `AdminListView`
    - depende de: datos de `panel:game-title_data`
    - ruta: `panel:game-title_list` → `/panel/game-title/`
    - fondo: `bg-games-title-game`
  - `GameTitleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGameTitle`, `BaseSelectView`
    - ruta: `panel:game-title_select` → `/panel/game-title/select/`
    - fondo: `bg-games-title-game`
  - `GameTitleUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGameTitle`, `BaseUpdate`
    - depende de: formulario `GameTitleForm`; vuelve a `panel:game-title_list`; al guardar va a `panel:game-title_list`; plantilla `games/form/game_title.html`
    - ruta: `panel:game-title_update` → `/panel/game-title/<int:pk>/update/`
    - fondo: `bg-games-title-game`

### Modelo: `Genre` (`apps/games/models.py`)

- Formulario: `GenreForm` (`apps/games/forms.py`) — campos: `name`, `name_esp`, `description`, `explicit`, `image`, `is_active`
- Vistas:
  - `GenreCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGenre`, `BaseCreate`
    - depende de: formulario `GenreForm`; vuelve a `panel:game-genre_list`; al guardar va a `panel:game-genre_list`; plantilla `games/form/genre.html`
    - ruta: `panel:game-genre_create` → `/panel/game-genre/create/`
    - fondo: `bg-games-genre`
  - `GenreDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGenre`, `AdminDataView`
    - ruta: `panel:game-genre_data` → `/panel/game-genre/data/`
    - fondo: `bg-games-genre`
  - `GenreDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGenre`, `BaseDelete`
    - depende de: vuelve a `panel:game-genre_list`; al guardar va a `panel:game-genre_list`
    - ruta: `panel:game-genre_delete` → `/panel/game-genre/<int:pk>/delete/`
    - fondo: `bg-games-genre`
  - `GenreDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGenre`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-genre_list`; plantilla `games/detail/genre.html`
    - ruta: `panel:game-genre_detail` → `/panel/game-genre/<int:pk>/`
    - fondo: `bg-games-genre`
  - `GenreListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGenre`, `AdminListView`
    - depende de: datos de `panel:game-genre_data`
    - ruta: `panel:game-genre_list` → `/panel/game-genre/`
    - fondo: `bg-games-genre`
  - `GenreSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGenre`, `BaseSelectView`
    - ruta: `panel:game-genre_select` → `/panel/game-genre/select/`
    - fondo: `bg-games-genre`
  - `GenreUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGenre`, `BaseUpdate`
    - depende de: formulario `GenreForm`; vuelve a `panel:game-genre_list`; al guardar va a `panel:game-genre_list`; plantilla `games/form/genre.html`
    - ruta: `panel:game-genre_update` → `/panel/game-genre/<int:pk>/update/`
    - fondo: `bg-games-genre`

### Modelo: `GenreAlias` (`apps/games/models.py`)

- Formulario: `GenreAliasForm` (`apps/games/forms.py`) — campos: `name`, `name_esp`, `is_active`, `genre`
- Vistas:
  - `GenreAliasCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseCreate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:game-genre-alias_list`; al guardar va a `panel:game-genre-alias_list`
    - ruta: `panel:game-genre-alias_create` → `/panel/game-genre-alias/create/`
    - fondo: `bg-games-game-genre`
  - `GenreAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseGenreAliasContext`, `AdminDataView`
    - ruta: `panel:game-genre-alias_data` → `/panel/game-genre-alias/data/`, `panel:game-genre-alias_data-by` → `/panel/game-genre-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-games-game-genre`
  - `GenreAliasDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseDelete`
    - depende de: vuelve a `panel:game-genre-alias_list`; al guardar va a `panel:game-genre-alias_list`
    - ruta: `panel:game-genre-alias_delete` → `/panel/game-genre-alias/<int:pk>/delete/`
    - fondo: `bg-games-game-genre`
  - `GenreAliasDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseGenreAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-genre-alias_list`
    - ruta: `panel:game-genre-alias_detail` → `/panel/game-genre-alias/<int:pk>/`
    - fondo: `bg-games-game-genre`
  - `GenreAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/game-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`.
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGenreAliasContext`, `AdminListByView`
    - depende de: datos de `panel:game-genre-alias_data-by`
    - ruta: `panel:game-genre-alias_by` → `/panel/game-genre-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-games-game-genre`
  - `GenreAliasListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseGenreAlias`, `AdminListView`
    - depende de: datos de `panel:game-genre-alias_data`
    - ruta: `panel:game-genre-alias_list` → `/panel/game-genre-alias/`
    - fondo: `bg-games-game-genre`
  - `GenreAliasUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseUpdate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:game-genre-alias_list`; al guardar va a `panel:game-genre-alias_list`
    - ruta: `panel:game-genre-alias_update` → `/panel/game-genre-alias/<int:pk>/update/`
    - fondo: `bg-games-game-genre`

### Modelo: `Medium` (`apps/games/models.py`)

- Formulario: `MediumForm` (`apps/games/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `MediumCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseMedium`, `BaseCreate`
    - depende de: formulario `MediumForm`; vuelve a `panel:game-medium_list`; al guardar va a `panel:game-medium_list`; plantilla `games/form/medium.html`
    - ruta: `panel:game-medium_create` → `/panel/game-medium/create/`
    - fondo: `bg-games-medium`
  - `MediumDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseMedium`, `AdminDataView`
    - ruta: `panel:game-medium_data` → `/panel/game-medium/data/`
    - fondo: `bg-games-medium`
  - `MediumDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseMedium`, `BaseDelete`
    - depende de: vuelve a `panel:game-medium_list`; al guardar va a `panel:game-medium_list`
    - ruta: `panel:game-medium_delete` → `/panel/game-medium/<int:pk>/delete/`
    - fondo: `bg-games-medium`
  - `MediumDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseMedium`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-medium_list`; plantilla `games/detail/medium.html`
    - ruta: `panel:game-medium_detail` → `/panel/game-medium/<int:pk>/`
    - fondo: `bg-games-medium`
  - `MediumListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseMedium`, `AdminListView`
    - depende de: datos de `panel:game-medium_data`
    - ruta: `panel:game-medium_list` → `/panel/game-medium/`
    - fondo: `bg-games-medium`
  - `MediumSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseMedium`, `BaseSelectView`
    - ruta: `panel:game-medium_select` → `/panel/game-medium/select/`
    - fondo: `bg-games-medium`
  - `MediumUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseMedium`, `BaseUpdate`
    - depende de: formulario `MediumForm`; vuelve a `panel:game-medium_list`; al guardar va a `panel:game-medium_list`; plantilla `games/form/medium.html`
    - ruta: `panel:game-medium_update` → `/panel/game-medium/<int:pk>/update/`
    - fondo: `bg-games-medium`

### Modelo: `Platform` (`apps/games/models.py`)

- Formulario: `PlatformForm` (`apps/games/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `PlatformCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BasePlatform`, `BaseCreate`
    - depende de: formulario `PlatformForm`; vuelve a `panel:game-platform_list`; al guardar va a `panel:game-platform_list`; plantilla `games/form/platform.html`
    - ruta: `panel:game-platform_create` → `/panel/game-platform/create/`
    - fondo: `bg-games-platform`
  - `PlatformDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BasePlatform`, `AdminDataView`
    - ruta: `panel:game-platform_data` → `/panel/game-platform/data/`
    - fondo: `bg-games-platform`
  - `PlatformDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BasePlatform`, `BaseDelete`
    - depende de: vuelve a `panel:game-platform_list`; al guardar va a `panel:game-platform_list`
    - ruta: `panel:game-platform_delete` → `/panel/game-platform/<int:pk>/delete/`
    - fondo: `bg-games-platform`
  - `PlatformDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BasePlatform`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-platform_list`; plantilla `games/detail/platform.html`
    - ruta: `panel:game-platform_detail` → `/panel/game-platform/<int:pk>/`
    - fondo: `bg-games-platform`
  - `PlatformListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BasePlatform`, `AdminListView`
    - depende de: datos de `panel:game-platform_data`
    - ruta: `panel:game-platform_list` → `/panel/game-platform/`
    - fondo: `bg-games-platform`
  - `PlatformSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/games/views/v3_data.py` · hereda de `BasePlatform`, `BaseSelectView`
    - ruta: `panel:game-platform_select` → `/panel/game-platform/select/`
    - fondo: `bg-games-platform`
  - `PlatformUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BasePlatform`, `BaseUpdate`
    - depende de: formulario `PlatformForm`; vuelve a `panel:game-platform_list`; al guardar va a `panel:game-platform_list`; plantilla `games/form/platform.html`
    - ruta: `panel:game-platform_update` → `/panel/game-platform/<int:pk>/update/`
    - fondo: `bg-games-platform`

### Modelo: `Tag` (`apps/games/models.py`)

- Formulario: `TagForm` (`apps/games/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`, `vndb_id`
- Vistas:
  - `TagCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseTag`, `BaseCreate`
    - depende de: formulario `TagForm`; vuelve a `panel:tag_list`; al guardar va a `panel:tag_list`
    - ruta: `panel:tag_create` → `/panel/tag/create/`
    - fondo: `bg-games-tag`
  - `TagDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseTag`, `AdminDataView`
    - ruta: `panel:tag_data` → `/panel/tag/data/`
    - fondo: `bg-games-tag`
  - `TagDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseTag`, `BaseDelete`
    - depende de: vuelve a `panel:tag_list`; al guardar va a `panel:tag_list`
    - ruta: `panel:tag_delete` → `/panel/tag/<int:pk>/delete/`
    - fondo: `bg-games-tag`
  - `TagDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseTag`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:tag_list`
    - ruta: `panel:tag_detail` → `/panel/tag/<int:pk>/`
    - fondo: `bg-games-tag`
  - `TagListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseTag`, `AdminListView`
    - depende de: datos de `panel:tag_data`
    - ruta: `panel:tag_list` → `/panel/tag/`
    - fondo: `bg-games-tag`
  - `TagUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseTag`, `BaseUpdate`
    - depende de: formulario `TagForm`; vuelve a `panel:tag_list`; al guardar va a `panel:tag_list`
    - ruta: `panel:tag_update` → `/panel/tag/<int:pk>/update/`
    - fondo: `bg-games-tag`

### Modelo: `TagAlias` (`apps/games/models.py`)

- Formulario: `TagAliasForm` (`apps/games/forms.py`) — campos: `name`, `name_esp`, `is_active`, `tag`
- Vistas:
  - `TagAliasCreateView` (panel) — alta
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseTagAlias`, `BaseCreate`
    - depende de: formulario `TagAliasForm`; vuelve a `panel:tag-alias_list`; al guardar va a `panel:tag-alias_list`
    - ruta: `panel:tag-alias_create` → `/panel/tag-alias/create/`
    - fondo: `bg-games-tag`
  - `TagAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/games/views/v3_data.py` · hereda de `BaseTagAliasContext`, `AdminDataView`
    - ruta: `panel:tag-alias_data` → `/panel/tag-alias/data/`, `panel:tag-alias_data-by` → `/panel/tag-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `tag` → padre por id (campo `tag`)
    - fondo: `bg-games-tag`
  - `TagAliasDeleteView` (panel) — borrado
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseTagAlias`, `BaseDelete`
    - depende de: vuelve a `panel:tag-alias_list`; al guardar va a `panel:tag-alias_list`
    - ruta: `panel:tag-alias_delete` → `/panel/tag-alias/<int:pk>/delete/`
    - fondo: `bg-games-tag`
  - `TagAliasDetailView` (panel) — ficha
    - archivo: `apps/games/views/v6_detail.py` · hereda de `BaseTagAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:tag-alias_list`
    - ruta: `panel:tag-alias_detail` → `/panel/tag-alias/<int:pk>/`
    - fondo: `bg-games-tag`
  - `TagAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/tag-alias/tag/<id>/`): los alimenta TagAliasDataView con `/data/tag/<id>/`.
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseTagAliasContext`, `AdminListByView`
    - depende de: datos de `panel:tag-alias_data-by`
    - ruta: `panel:tag-alias_by` → `/panel/tag-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `tag` → padre por id (campo `tag`)
    - fondo: `bg-games-tag`
  - `TagAliasListView` (panel) — lista
    - archivo: `apps/games/views/v5_list.py` · hereda de `BaseTagAlias`, `AdminListView`
    - depende de: datos de `panel:tag-alias_data`
    - ruta: `panel:tag-alias_list` → `/panel/tag-alias/`
    - fondo: `bg-games-tag`
  - `TagAliasUpdateView` (panel) — edición
    - archivo: `apps/games/views/v4_write.py` · hereda de `BaseTagAlias`, `BaseUpdate`
    - depende de: formulario `TagAliasForm`; vuelve a `panel:tag-alias_list`; al guardar va a `panel:tag-alias_list`
    - ruta: `panel:tag-alias_update` → `/panel/tag-alias/<int:pk>/update/`
    - fondo: `bg-games-tag`

### Sin modelo

- `GamesHomeView`
  - archivo: `apps/games/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:games-home` → `/panel/games/` · fondo `bg-games-home`
- `GamesPublicHomeView`
  - archivo: `apps/games/views/v1_home.py` · hereda de `BasePublicHomeView` · ruta: `games:home` → `/catalog/games/` · fondo `bg-games-home`
- `PublisherPublicDataView`
  - archivo: `apps/games/views/v3_data.py` · hereda de `BaseCreator`, `PublicDataView` · ruta: `games:editoras-catalogo-data` → `/catalog/games/publishers/list/data/` · fondo `bg-games-creator`
- `PublisherPublicListView` — Catálogo de EDITORAS de juegos (con buscador y filtros).
  - archivo: `apps/games/views/v5_list.py` · hereda de `BaseCreator`, `PublicListView` · ruta: `games:editoras-catalogo` → `/catalog/games/publishers/list/` · fondo `bg-games-creator`
- `VndbCharacterImportView`
  - archivo: `apps/games/views/v8_import.py` · hereda de `BaseVndbTipo`, `TipoImportView` · ruta: `panel:vndb-character` → `/panel/vndb/character/` · fondo `bg-games-import-personaje`
- `VndbCreatorImportView`
  - archivo: `apps/games/views/v8_import.py` · hereda de `BaseVndbTipo`, `TipoImportView` · ruta: `panel:vndb-creator` → `/panel/vndb/creator/` · fondo `bg-games-import-creador`
- `VndbGameImportView`
  - archivo: `apps/games/views/v8_import.py` · hereda de `BaseVndbTipo`, `TipoImportView` · ruta: `panel:vndb-game` → `/panel/vndb/game/` · fondo `bg-games-import-juego`
- `VndbReleaseImportView`
  - archivo: `apps/games/views/v8_import.py` · hereda de `BaseVndbTipo`, `TipoImportView` · ruta: `panel:vndb-release` → `/panel/vndb/release/` · fondo `bg-games-import-lanzamiento`
- `VndbTagsLoadView` — Carga de TAGS desde el dump oficial de VNDB, en dos pasos: (1) subir el .json(.gz) o descargarlo → resumen
  - archivo: `apps/games/views/v8_import.py` · hereda de `LoginRequiredMixin`, `UserPassesTestMixin`, `TemplateView` · ruta: `panel:vndb-tags` → `/panel/vndb/tags/` · fondo `bg-games-import-tags`
- `VndbGameLoadView` / `VndbGameSummaryView` — Cargar dump de JUEGOS (VNDB): archivo → `DataVndbGame`, sin procesar
  - archivo: `apps/games/views/v8_import.py` · hereda de `BaseDataVndbGame`, `VndbDumpLoadView` / `VndbDumpSummaryView` · rutas: `panel:dump-vndb-game` → `/panel/vndb/dump/game/` y `panel:dump-vndb-game-summary`
- `VndbCreatorLoadView` / `VndbCreatorSummaryView` — Ídem para `DataVndbCreator` · `/panel/vndb/dump/creator/`
- `VndbReleaseLoadView` / `VndbReleaseSummaryView` — Ídem para `DataVndbRelease` · `/panel/vndb/dump/release/`
- `VndbCharacterLoadView` / `VndbCharacterSummaryView` — Ídem para `DataVndbCharacter` · `/panel/vndb/dump/character/`
- Form `VndbDumpForm` (base) y sus hijos `VndbGameDumpForm`, `VndbCreatorDumpForm`, `VndbReleaseDumpForm`, `VndbCharacterDumpForm`
- Servicio `apps/games/services/vndb_dump.py` — lee el archivo y lo guarda crudo por `vndb_id`
- Form `VndbBarridoForm`
- Form `VndbImportarRangoForm`
- Form `VndbImportarUnoForm`

## Películas (`movies`)


### Modelo: `Genre` (`apps/movies/models.py`)

- Formulario: `GenreForm` (`apps/movies/forms.py`) — campos: `name`, `name_esp`, `description`, `explicit`, `image`, `is_active`
- Vistas:
  - `GenreCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseGenre`, `BaseCreate`
    - depende de: formulario `GenreForm`; vuelve a `panel:movie-genre_list`; al guardar va a `panel:movie-genre_list`; plantilla `movies/form/genre.html`
    - ruta: `panel:movie-genre_create` → `/panel/movie-genre/create/`
    - fondo: `bg-movies-genre`
  - `GenreDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseGenre`, `AdminDataView`
    - ruta: `panel:movie-genre_data` → `/panel/movie-genre/data/`
    - fondo: `bg-movies-genre`
  - `GenreDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseGenre`, `BaseDelete`
    - depende de: vuelve a `panel:movie-genre_list`; al guardar va a `panel:movie-genre_list`
    - ruta: `panel:movie-genre_delete` → `/panel/movie-genre/<int:pk>/delete/`
    - fondo: `bg-movies-genre`
  - `GenreDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseGenre`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-genre_list`; plantilla `movies/detail/genre.html`
    - ruta: `panel:movie-genre_detail` → `/panel/movie-genre/<int:pk>/`
    - fondo: `bg-movies-genre`
  - `GenreListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseGenre`, `AdminListView`
    - depende de: datos de `panel:movie-genre_data`
    - ruta: `panel:movie-genre_list` → `/panel/movie-genre/`
    - fondo: `bg-movies-genre`
  - `GenreSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseGenre`, `BaseSelectView`
    - ruta: `panel:movie-genre_select` → `/panel/movie-genre/select/`
    - fondo: `bg-movies-genre`
  - `GenreUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseGenre`, `BaseUpdate`
    - depende de: formulario `GenreForm`; vuelve a `panel:movie-genre_list`; al guardar va a `panel:movie-genre_list`; plantilla `movies/form/genre.html`
    - ruta: `panel:movie-genre_update` → `/panel/movie-genre/<int:pk>/update/`
    - fondo: `bg-movies-genre`

### Modelo: `GenreAlias` (`apps/movies/models.py`)

- Formulario: `GenreAliasForm` (`apps/movies/forms.py`) — campos: `name`, `name_esp`, `is_active`, `genre`
- Vistas:
  - `GenreAliasCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseCreate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:movie-genre-alias_list`; al guardar va a `panel:movie-genre-alias_list`
    - ruta: `panel:movie-genre-alias_create` → `/panel/movie-genre-alias/create/`
    - fondo: `bg-movies-movie-genre`
  - `GenreAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseGenreAliasContext`, `AdminDataView`
    - ruta: `panel:movie-genre-alias_data` → `/panel/movie-genre-alias/data/`, `panel:movie-genre-alias_data-by` → `/panel/movie-genre-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-movies-movie-genre`
  - `GenreAliasDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseDelete`
    - depende de: vuelve a `panel:movie-genre-alias_list`; al guardar va a `panel:movie-genre-alias_list`
    - ruta: `panel:movie-genre-alias_delete` → `/panel/movie-genre-alias/<int:pk>/delete/`
    - fondo: `bg-movies-movie-genre`
  - `GenreAliasDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseGenreAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-genre-alias_list`
    - ruta: `panel:movie-genre-alias_detail` → `/panel/movie-genre-alias/<int:pk>/`
    - fondo: `bg-movies-movie-genre`
  - `GenreAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/movie-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`.
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseGenreAliasContext`, `AdminListByView`
    - depende de: datos de `panel:movie-genre-alias_data-by`
    - ruta: `panel:movie-genre-alias_by` → `/panel/movie-genre-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-movies-movie-genre`
  - `GenreAliasListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseGenreAlias`, `AdminListView`
    - depende de: datos de `panel:movie-genre-alias_data`
    - ruta: `panel:movie-genre-alias_list` → `/panel/movie-genre-alias/`
    - fondo: `bg-movies-movie-genre`
  - `GenreAliasUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseUpdate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:movie-genre-alias_list`; al guardar va a `panel:movie-genre-alias_list`
    - ruta: `panel:movie-genre-alias_update` → `/panel/movie-genre-alias/<int:pk>/update/`
    - fondo: `bg-movies-movie-genre`

### Modelo: `Movie` (`apps/movies/models.py`)

- Formulario: `MovieForm` (`apps/movies/forms.py`) — campos: `title`, `title_secundary`, `release_year`, `duration_minutes`, `synopsis`, `movie_type`, `movie_rating`, `genres`, `producers`, `distributors`, `is_active`
- Vistas:
  - `MovieCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovie`, `BaseCreate`
    - depende de: formulario `MovieForm`; vuelve a `panel:movie_list`; al guardar va a `panel:movie_list`; plantilla `movies/form/movie.html`
    - ruta: `panel:movie_create` → `/panel/movie/create/`
    - fondo: `bg-movies-movie`
  - `MovieDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieContext`, `AdminDataView`
    - ruta: `panel:movie_data` → `/panel/movie/data/`, `panel:movie_data-by` → `/panel/movie/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `movie_type`); `clasificacion` → padre por id (campo `movie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-movies-movie`
  - `MovieDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovie`, `BaseDelete`
    - depende de: vuelve a `panel:movie_list`; al guardar va a `panel:movie_list`
    - ruta: `panel:movie_delete` → `/panel/movie/<int:pk>/delete/`
    - fondo: `bg-movies-movie`
  - `MovieDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovie`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie_list`; plantilla `movies/detail/movie.html`
    - ruta: `panel:movie_detail` → `/panel/movie/<int:pk>/`
    - fondo: `bg-movies-movie`
  - `MovieListByView` (panel) — lista «por» (acotada a un padre) — genero, productora, distribuidora, tipo, clasificacion, persona.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieContext`, `AdminListByView`
    - depende de: datos de `panel:movie_data-by`
    - ruta: `panel:movie_by` → `/panel/movie/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `movie_type`); `clasificacion` → padre por id (campo `movie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-movies-movie`
  - `MovieListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovie`, `AdminListView`
    - depende de: datos de `panel:movie_data`
    - ruta: `panel:movie_list` → `/panel/movie/`
    - fondo: `bg-movies-movie`
  - `MoviePublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieContext`, `PublicDataView`
    - ruta: `movies:lista-data` → `/catalog/movies/list/data/`, `movies:por-data` → `/catalog/movies/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `movie_type`); `clasificacion` → padre por id (campo `movie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-movies-movie`
  - `MoviePublicDetailView` (pública) — ficha — Ficha pública de una película: el mismo HTML que en gestión, sin botones y con la colección.
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovie`, `BasePublicDetailView`
    - depende de: vuelve a `movies:lista`; plantilla `movies/detail/movie.html`
    - ruta: `movies:detalle` → `/catalog/movies/movie/<int:pk>/<slug:slug>/`, `movies:detalle` → `/catalog/movies/movie/<int:pk>/`
    - fondo: `bg-movies-movie`
  - `MoviePublicListByView` (pública) — lista «por» (acotada a un padre) — genero, productora, distribuidora, tipo, clasificacion, persona.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieContext`, `PublicListByView`
    - depende de: datos de `movies:por-data`; plantilla `public/list.html`
    - ruta: `movies:por` → `/catalog/movies/<str:tipo>/<int:pk>/`, `movies:por` → `/catalog/movies/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `movie_type`); `clasificacion` → padre por id (campo `movie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-movies-movie`
  - `MoviePublicListView` (pública) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovie`, `PublicListView`
    - depende de: datos de `movies:lista-data`; plantilla `public/list.html`
    - ruta: `movies:lista` → `/catalog/movies/list/`
    - fondo: `bg-movies-movie`
  - `MovieSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovie`, `BaseSelectView`
    - ruta: `panel:movie_select` → `/panel/movie/select/`
    - fondo: `bg-movies-movie`
  - `MovieUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovie`, `BaseUpdate`
    - depende de: formulario `MovieForm`; vuelve a `panel:movie_list`; al guardar va a `panel:movie_list`; plantilla `movies/form/movie.html`
    - ruta: `panel:movie_update` → `/panel/movie/<int:pk>/update/`
    - fondo: `bg-movies-movie`
- Filtros:
  - `MovieFilters`: Género (`genres`), Tipo (`movie_type`), Productora (`producers`), Clasificación (`movie_rating`), Distribuidora (`distributors`), Año (`release_year`) — para `MovieDataView`, `MoviePublicDataView`

### Modelo: `MovieCast` (`apps/movies/models.py`)

- Formulario: `MovieCastForm` (`apps/movies/forms.py`) — campos: `movie`, `person`, `role`, `character_name`, `is_active`
- Vistas:
  - `MovieCastCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieCast`, `BaseCreate`
    - depende de: formulario `MovieCastForm`; vuelve a `panel:movie-cast_list`; al guardar va a `panel:movie-cast_list`; plantilla `movies/form/movie_cast.html`
    - ruta: `panel:movie-cast_create` → `/panel/movie-cast/create/`
    - fondo: `bg-movies-movie-cast`
  - `MovieCastDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieCastContext`, `AdminDataView`
    - ruta: `panel:movie-cast_data` → `/panel/movie-cast/data/`, `panel:movie-cast_data-by` → `/panel/movie-cast/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie-cast`
  - `MovieCastDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieCast`, `BaseDelete`
    - depende de: vuelve a `panel:movie-cast_list`; al guardar va a `panel:movie-cast_list`
    - ruta: `panel:movie-cast_delete` → `/panel/movie-cast/<int:pk>/delete/`
    - fondo: `bg-movies-movie-cast`
  - `MovieCastDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovieCast`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-cast_list`; plantilla `movies/detail/movie_cast.html`
    - ruta: `panel:movie-cast_detail` → `/panel/movie-cast/<int:pk>/`
    - fondo: `bg-movies-movie-cast`
  - `MovieCastListByView` (panel) — lista «por» (acotada a un padre) — pelicula, persona.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieCastContext`, `AdminListByView`
    - depende de: datos de `panel:movie-cast_data-by`
    - ruta: `panel:movie-cast_by` → `/panel/movie-cast/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie-cast`
  - `MovieCastListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovieCast`, `AdminListView`
    - depende de: datos de `panel:movie-cast_data`
    - ruta: `panel:movie-cast_list` → `/panel/movie-cast/`
    - fondo: `bg-movies-movie-cast`
  - `MovieCastPublicDataView` (pública) — datos JSON de la lista — Reparto de una película: [la persona (foto + nombre → su ficha) · personaje · rol].
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieCastContext`, `PublicDataView`
    - ruta: `movies:reparto-por-data` → `/catalog/movies/cast/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie-cast`
  - `MovieCastPublicListByView` (pública) — lista «por» (acotada a un padre) — pelicula, persona.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieCastContext`, `PublicListByView`
    - depende de: datos de `movies:reparto-por-data`; plantilla `public/list.html`
    - ruta: `movies:reparto-por` → `/catalog/movies/cast/<str:tipo>/<int:pk>/`, `movies:reparto-por` → `/catalog/movies/cast/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie`
  - `MovieCastSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieCast`, `BaseSelectView`
    - ruta: `panel:movie-cast_select` → `/panel/movie-cast/select/`
    - fondo: `bg-movies-movie-cast`
  - `MovieCastUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieCast`, `BaseUpdate`
    - depende de: formulario `MovieCastForm`; vuelve a `panel:movie-cast_list`; al guardar va a `panel:movie-cast_list`; plantilla `movies/form/movie_cast.html`
    - ruta: `panel:movie-cast_update` → `/panel/movie-cast/<int:pk>/update/`
    - fondo: `bg-movies-movie-cast`
- Filtros:
  - `MovieCastFilters`: Rol (`role`) — para `MovieCastDataView`, `MovieCastPublicDataView`

### Modelo: `MovieImage` (`apps/movies/models.py`)

- Formulario: `MovieImageForm` (`apps/movies/forms.py`) — campos: `movie`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `MovieImageCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieImage`, `BaseCreate`
    - depende de: formulario `MovieImageForm`; vuelve a `panel:movie-image_list`; al guardar va a `panel:movie-image_list`; plantilla `movies/form/movie_image.html`
    - ruta: `panel:movie-image_create` → `/panel/movie-image/create/`
    - fondo: `bg-movies-movie-image`
  - `MovieImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieImageContext`, `AdminDataView`
    - ruta: `panel:movie-image_data` → `/panel/movie-image/data/`, `panel:movie-image_data-by` → `/panel/movie-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`)
    - fondo: `bg-movies-movie-image`
  - `MovieImageDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieImage`, `BaseDelete`
    - depende de: vuelve a `panel:movie-image_list`; al guardar va a `panel:movie-image_list`
    - ruta: `panel:movie-image_delete` → `/panel/movie-image/<int:pk>/delete/`
    - fondo: `bg-movies-movie-image`
  - `MovieImageDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovieImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-image_list`; plantilla `movies/detail/movie_image.html`
    - ruta: `panel:movie-image_detail` → `/panel/movie-image/<int:pk>/`
    - fondo: `bg-movies-movie-image`
  - `MovieImageListByView` (panel) — lista «por» (acotada a un padre) — pelicula.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieImageContext`, `AdminListByView`
    - depende de: datos de `panel:movie-image_data-by`
    - ruta: `panel:movie-image_by` → `/panel/movie-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`)
    - fondo: `bg-movies-movie-image`
  - `MovieImageListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovieImage`, `AdminListView`
    - depende de: datos de `panel:movie-image_data`
    - ruta: `panel:movie-image_list` → `/panel/movie-image/`
    - fondo: `bg-movies-movie-image`
  - `MovieImagePublicListByView` (pública) — lista «por» (acotada a un padre) — pelicula.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieImageContext`, `PublicListByView`
    - depende de: datos de `movies:imagenes-por-data`; plantilla `public/list.html`
    - ruta: `movies:imagenes-por` → `/catalog/movies/images/<str:tipo>/<int:pk>/`, `movies:imagenes-por` → `/catalog/movies/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`)
    - fondo: `bg-movies-movie`
  - `MovieImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieImage`, `BaseSelectView`
    - ruta: `panel:movie-image_select` → `/panel/movie-image/select/`
    - fondo: `bg-movies-movie-image`
  - `MovieImageUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieImage`, `BaseUpdate`
    - depende de: formulario `MovieImageForm`; vuelve a `panel:movie-image_list`; al guardar va a `panel:movie-image_list`; plantilla `movies/form/movie_image.html`
    - ruta: `panel:movie-image_update` → `/panel/movie-image/<int:pk>/update/`
    - fondo: `bg-movies-movie-image`
  - `MovieImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de una película: sus imágenes en tarjetas (la portada va en la ficha).
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieImageContext`, `PublicDataView`
    - ruta: `movies:imagenes-por-data` → `/catalog/movies/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`)
    - fondo: `bg-movies-movie-image`

### Modelo: `MovieLog` (`apps/movies/models.py`)

- Formulario: `MovieLogForm` (`apps/movies/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `MovieLogCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieLog`, `BaseCreate`
    - depende de: formulario `MovieLogForm`; vuelve a `panel:movie-log_list`; al guardar va a `panel:movie-log_list`
    - ruta: `panel:movie-log_create` → `/panel/movie-log/create/`
    - fondo: `bg-movies-movie-log`
  - `MovieLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieLog`, `AdminDataView`
    - ruta: `panel:movie-log_data` → `/panel/movie-log/data/`
    - fondo: `bg-movies-movie-log`
  - `MovieLogDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieLog`, `BaseDelete`
    - depende de: vuelve a `panel:movie-log_list`; al guardar va a `panel:movie-log_list`
    - ruta: `panel:movie-log_delete` → `/panel/movie-log/<int:pk>/delete/`
    - fondo: `bg-movies-movie-log`
  - `MovieLogDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovieLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-log_list`; plantilla `movies/detail/movie_log.html`
    - ruta: `panel:movie-log_detail` → `/panel/movie-log/<int:pk>/`
    - fondo: `bg-movies-movie-log`
  - `MovieLogListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovieLog`, `AdminListView`
    - depende de: datos de `panel:movie-log_data`
    - ruta: `panel:movie-log_list` → `/panel/movie-log/`
    - fondo: `bg-movies-movie-log`
  - `MovieLogUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieLog`, `BaseUpdate`
    - depende de: formulario `MovieLogForm`; vuelve a `panel:movie-log_list`; al guardar va a `panel:movie-log_list`
    - ruta: `panel:movie-log_update` → `/panel/movie-log/<int:pk>/update/`
    - fondo: `bg-movies-movie-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `MovieLogDataView`

### Modelo: `MovieRelation` (`apps/movies/models.py`)

- Formulario: `MovieRelationForm` (`apps/movies/forms.py`) — campos: `movie`, `related`, `relation_type`, `is_active`
- Vistas:
  - `MovieRelationCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieRelation`, `BaseCreate`
    - depende de: formulario `MovieRelationForm`; vuelve a `panel:movie-relation_list`; al guardar va a `panel:movie-relation_list`; plantilla `movies/form/movie_relation.html`
    - ruta: `panel:movie-relation_create` → `/panel/movie-relation/create/`
    - fondo: `bg-movies-movie-relation`
  - `MovieRelationDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieRelationContext`, `AdminDataView`
    - ruta: `panel:movie-relation_data` → `/panel/movie-relation/data/`, `panel:movie-relation_data-by` → `/panel/movie-relation/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `tipo` → padre por id (campo `relation_type`)
    - fondo: `bg-movies-movie-relation`
  - `MovieRelationDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieRelation`, `BaseDelete`
    - depende de: vuelve a `panel:movie-relation_list`; al guardar va a `panel:movie-relation_list`
    - ruta: `panel:movie-relation_delete` → `/panel/movie-relation/<int:pk>/delete/`
    - fondo: `bg-movies-movie-relation`
  - `MovieRelationDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovieRelation`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-relation_list`; plantilla `movies/detail/movie_relation.html`
    - ruta: `panel:movie-relation_detail` → `/panel/movie-relation/<int:pk>/`
    - fondo: `bg-movies-movie-relation`
  - `MovieRelationListByView` (panel) — lista «por» (acotada a un padre) — pelicula, tipo.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieRelationContext`, `AdminListByView`
    - depende de: datos de `panel:movie-relation_data-by`
    - ruta: `panel:movie-relation_by` → `/panel/movie-relation/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `tipo` → padre por id (campo `relation_type`)
    - fondo: `bg-movies-movie-relation`
  - `MovieRelationListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovieRelation`, `AdminListView`
    - depende de: datos de `panel:movie-relation_data`
    - ruta: `panel:movie-relation_list` → `/panel/movie-relation/`
    - fondo: `bg-movies-movie-relation`
  - `MovieRelationSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieRelation`, `BaseSelectView`
    - ruta: `panel:movie-relation_select` → `/panel/movie-relation/select/`
    - fondo: `bg-movies-movie-relation`
  - `MovieRelationUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieRelation`, `BaseUpdate`
    - depende de: formulario `MovieRelationForm`; vuelve a `panel:movie-relation_list`; al guardar va a `panel:movie-relation_list`; plantilla `movies/form/movie_relation.html`
    - ruta: `panel:movie-relation_update` → `/panel/movie-relation/<int:pk>/update/`
    - fondo: `bg-movies-movie-relation`

### Modelo: `MovieStaff` (`apps/movies/models.py`)

- Formulario: `MovieStaffForm` (`apps/movies/forms.py`) — campos: `movie`, `person`, `role`, `is_active`
- Vistas:
  - `MovieStaffCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieStaff`, `BaseCreate`
    - depende de: formulario `MovieStaffForm`; vuelve a `panel:movie-staff_list`; al guardar va a `panel:movie-staff_list`; plantilla `movies/form/movie_staff.html`
    - ruta: `panel:movie-staff_create` → `/panel/movie-staff/create/`
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieStaffContext`, `AdminDataView`
    - ruta: `panel:movie-staff_data` → `/panel/movie-staff/data/`, `panel:movie-staff_data-by` → `/panel/movie-staff/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieStaff`, `BaseDelete`
    - depende de: vuelve a `panel:movie-staff_list`; al guardar va a `panel:movie-staff_list`
    - ruta: `panel:movie-staff_delete` → `/panel/movie-staff/<int:pk>/delete/`
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovieStaff`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-staff_list`; plantilla `movies/detail/movie_staff.html`
    - ruta: `panel:movie-staff_detail` → `/panel/movie-staff/<int:pk>/`
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffListByView` (panel) — lista «por» (acotada a un padre) — pelicula, persona.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieStaffContext`, `AdminListByView`
    - depende de: datos de `panel:movie-staff_data-by`
    - ruta: `panel:movie-staff_by` → `/panel/movie-staff/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovieStaff`, `AdminListView`
    - depende de: datos de `panel:movie-staff_data`
    - ruta: `panel:movie-staff_list` → `/panel/movie-staff/`
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffPublicDataView` (pública) — datos JSON de la lista — Equipo técnico de una película: [la persona (foto + nombre → su ficha) · rol].
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieStaffContext`, `PublicDataView`
    - ruta: `movies:equipo-por-data` → `/catalog/movies/staff/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffPublicListByView` (pública) — lista «por» (acotada a un padre) — pelicula, persona.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieStaffContext`, `PublicListByView`
    - depende de: datos de `movies:equipo-por-data`; plantilla `public/list.html`
    - ruta: `movies:equipo-por` → `/catalog/movies/staff/<str:tipo>/<int:pk>/`, `movies:equipo-por` → `/catalog/movies/staff/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-movies-movie`
  - `MovieStaffSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieStaff`, `BaseSelectView`
    - ruta: `panel:movie-staff_select` → `/panel/movie-staff/select/`
    - fondo: `bg-movies-movie-staff`
  - `MovieStaffUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieStaff`, `BaseUpdate`
    - depende de: formulario `MovieStaffForm`; vuelve a `panel:movie-staff_list`; al guardar va a `panel:movie-staff_list`; plantilla `movies/form/movie_staff.html`
    - ruta: `panel:movie-staff_update` → `/panel/movie-staff/<int:pk>/update/`
    - fondo: `bg-movies-movie-staff`
- Filtros:
  - `MovieStaffFilters`: Rol (`role`) — para `MovieStaffDataView`, `MovieStaffPublicDataView`

### Modelo: `MovieTitle` (`apps/movies/models.py`)

- Formulario: `MovieTitleForm` (`apps/movies/forms.py`) — campos: `movie`, `title_lang`, `title`, `is_active`
- Vistas:
  - `MovieTitleCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieTitle`, `BaseCreate`
    - depende de: formulario `MovieTitleForm`; vuelve a `panel:movie-title_list`; al guardar va a `panel:movie-title_list`; plantilla `movies/form/movie_title.html`
    - ruta: `panel:movie-title_create` → `/panel/movie-title/create/`
    - fondo: `bg-movies-title-movie`
  - `MovieTitleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieTitleContext`, `AdminDataView`
    - ruta: `panel:movie-title_data` → `/panel/movie-title/data/`, `panel:movie-title_data-by` → `/panel/movie-title/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`)
    - fondo: `bg-movies-title-movie`
  - `MovieTitleDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieTitle`, `BaseDelete`
    - depende de: vuelve a `panel:movie-title_list`; al guardar va a `panel:movie-title_list`
    - ruta: `panel:movie-title_delete` → `/panel/movie-title/<int:pk>/delete/`
    - fondo: `bg-movies-title-movie`
  - `MovieTitleDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseMovieTitle`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-title_list`; plantilla `movies/detail/movie_title.html`
    - ruta: `panel:movie-title_detail` → `/panel/movie-title/<int:pk>/`
    - fondo: `bg-movies-title-movie`
  - `MovieTitleListByView` (panel) — lista «por» (acotada a un padre) — pelicula.
    - archivo: `apps/movies/views/v5_list_by.py` · hereda de `BaseMovieTitleContext`, `AdminListByView`
    - depende de: datos de `panel:movie-title_data-by`
    - ruta: `panel:movie-title_by` → `/panel/movie-title/<str:tipo>/<str:pk>/`
    - mapa «by»: `pelicula` → padre por id (campo `movie`)
    - fondo: `bg-movies-title-movie`
  - `MovieTitleListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseMovieTitle`, `AdminListView`
    - depende de: datos de `panel:movie-title_data`
    - ruta: `panel:movie-title_list` → `/panel/movie-title/`
    - fondo: `bg-movies-title-movie`
  - `MovieTitleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseMovieTitle`, `BaseSelectView`
    - ruta: `panel:movie-title_select` → `/panel/movie-title/select/`
    - fondo: `bg-movies-title-movie`
  - `MovieTitleUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseMovieTitle`, `BaseUpdate`
    - depende de: formulario `MovieTitleForm`; vuelve a `panel:movie-title_list`; al guardar va a `panel:movie-title_list`; plantilla `movies/form/movie_title.html`
    - ruta: `panel:movie-title_update` → `/panel/movie-title/<int:pk>/update/`
    - fondo: `bg-movies-title-movie`

### Modelo: `Rating` (`apps/movies/models.py`)

- Formulario: `RatingForm` (`apps/movies/forms.py`) — campos: `name`, `name_esp`, `description`, `acronym`, `image`, `is_active`
- Vistas:
  - `RatingCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseRating`, `BaseCreate`
    - depende de: formulario `RatingForm`; vuelve a `panel:movie-rating_list`; al guardar va a `panel:movie-rating_list`; plantilla `movies/form/rating.html`
    - ruta: `panel:movie-rating_create` → `/panel/movie-rating/create/`
    - fondo: `bg-movies-rating`
  - `RatingDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseRating`, `AdminDataView`
    - ruta: `panel:movie-rating_data` → `/panel/movie-rating/data/`
    - fondo: `bg-movies-rating`
  - `RatingDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseRating`, `BaseDelete`
    - depende de: vuelve a `panel:movie-rating_list`; al guardar va a `panel:movie-rating_list`
    - ruta: `panel:movie-rating_delete` → `/panel/movie-rating/<int:pk>/delete/`
    - fondo: `bg-movies-rating`
  - `RatingDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseRating`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-rating_list`; plantilla `movies/detail/rating.html`
    - ruta: `panel:movie-rating_detail` → `/panel/movie-rating/<int:pk>/`
    - fondo: `bg-movies-rating`
  - `RatingListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseRating`, `AdminListView`
    - depende de: datos de `panel:movie-rating_data`
    - ruta: `panel:movie-rating_list` → `/panel/movie-rating/`
    - fondo: `bg-movies-rating`
  - `RatingSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseRating`, `BaseSelectView`
    - ruta: `panel:movie-rating_select` → `/panel/movie-rating/select/`
    - fondo: `bg-movies-rating`
  - `RatingUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseRating`, `BaseUpdate`
    - depende de: formulario `RatingForm`; vuelve a `panel:movie-rating_list`; al guardar va a `panel:movie-rating_list`; plantilla `movies/form/rating.html`
    - ruta: `panel:movie-rating_update` → `/panel/movie-rating/<int:pk>/update/`
    - fondo: `bg-movies-rating`

### Modelo: `Role` (`apps/movies/models.py`)

- Formulario: `RoleForm` (`apps/movies/forms.py`) — campos: `name`, `name_esp`, `type`, `description`, `image`, `is_active`
- Vistas:
  - `RoleCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseRole`, `BaseCreate`
    - depende de: formulario `RoleForm`; vuelve a `panel:movie-role_list`; al guardar va a `panel:movie-role_list`; plantilla `movies/form/role.html`
    - ruta: `panel:movie-role_create` → `/panel/movie-role/create/`
    - fondo: `bg-movies-role`
  - `RoleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseRoleContext`, `AdminDataView`
    - ruta: `panel:movie-role_data` → `/panel/movie-role/data/`, `panel:movie-role_data-by` → `/panel/movie-role/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `cast`, `unknown`
    - fondo: `bg-movies-role`
  - `RoleDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseRole`, `BaseDelete`
    - depende de: vuelve a `panel:movie-role_list`; al guardar va a `panel:movie-role_list`
    - ruta: `panel:movie-role_delete` → `/panel/movie-role/<int:pk>/delete/`
    - fondo: `bg-movies-role`
  - `RoleDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseRole`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-role_list`; plantilla `movies/detail/role.html`
    - ruta: `panel:movie-role_detail` → `/panel/movie-role/<int:pk>/`
    - fondo: `bg-movies-role`
  - `RoleListByView` (panel) — lista «por» (acotada a un padre) — Lista de roles acotada por familia (`/movie-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`.
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseRoleContext`, `AdminListByView`
    - depende de: datos de `panel:movie-role_data-by`
    - ruta: `panel:movie-role_by` → `/panel/movie-role/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `cast`, `unknown`
    - fondo: `bg-movies-role`
  - `RoleListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseRole`, `AdminListView`
    - depende de: datos de `panel:movie-role_data`
    - ruta: `panel:movie-role_list` → `/panel/movie-role/`
    - fondo: `bg-movies-role`
  - `RoleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseRole`, `BaseSelectView`
    - ruta: `panel:movie-role_select` → `/panel/movie-role/select/`
    - fondo: `bg-movies-role`
  - `RoleUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseRole`, `BaseUpdate`
    - depende de: formulario `RoleForm`; vuelve a `panel:movie-role_list`; al guardar va a `panel:movie-role_list`; plantilla `movies/form/role.html`
    - ruta: `panel:movie-role_update` → `/panel/movie-role/<int:pk>/update/`
    - fondo: `bg-movies-role`
- Filtros:
  - `RoleFilters`: Tipo de rol (`type`), Activo (`is_active`) — para `RoleDataView`

### Modelo: `Type` (`apps/movies/models.py`)

- Formulario: `TypeForm` (`apps/movies/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `TypeCreateView` (panel) — alta
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseType`, `BaseCreate`
    - depende de: formulario `TypeForm`; vuelve a `panel:movie-type_list`; al guardar va a `panel:movie-type_list`; plantilla `movies/form/type.html`
    - ruta: `panel:movie-type_create` → `/panel/movie-type/create/`
    - fondo: `bg-movies-type`
  - `TypeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseType`, `AdminDataView`
    - ruta: `panel:movie-type_data` → `/panel/movie-type/data/`
    - fondo: `bg-movies-type`
  - `TypeDeleteView` (panel) — borrado
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseType`, `BaseDelete`
    - depende de: vuelve a `panel:movie-type_list`; al guardar va a `panel:movie-type_list`
    - ruta: `panel:movie-type_delete` → `/panel/movie-type/<int:pk>/delete/`
    - fondo: `bg-movies-type`
  - `TypeDetailView` (panel) — ficha
    - archivo: `apps/movies/views/v6_detail.py` · hereda de `BaseType`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-type_list`; plantilla `movies/detail/type.html`
    - ruta: `panel:movie-type_detail` → `/panel/movie-type/<int:pk>/`
    - fondo: `bg-movies-type`
  - `TypeListView` (panel) — lista
    - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseType`, `AdminListView`
    - depende de: datos de `panel:movie-type_data`
    - ruta: `panel:movie-type_list` → `/panel/movie-type/`
    - fondo: `bg-movies-type`
  - `TypeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseType`, `BaseSelectView`
    - ruta: `panel:movie-type_select` → `/panel/movie-type/select/`
    - fondo: `bg-movies-type`
  - `TypeUpdateView` (panel) — edición
    - archivo: `apps/movies/views/v4_write.py` · hereda de `BaseType`, `BaseUpdate`
    - depende de: formulario `TypeForm`; vuelve a `panel:movie-type_list`; al guardar va a `panel:movie-type_list`; plantilla `movies/form/type.html`
    - ruta: `panel:movie-type_update` → `/panel/movie-type/<int:pk>/update/`
    - fondo: `bg-movies-type`

### Sin modelo

- `DistributorPublicDataView`
  - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseCompany`, `PublicDataView` · ruta: `movies:distribuidoras-catalogo-data` → `/catalog/movies/distributors/list/data/` · fondo `bg-movies-company`
- `DistributorPublicListView` — Catálogo de DISTRIBUIDORAS de cine (con buscador y filtros).
  - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseCompany`, `PublicListView` · ruta: `movies:distribuidoras-catalogo` → `/catalog/movies/distributors/list/` · fondo `bg-movies-movie`
- `MoviesHomeView`
  - archivo: `apps/movies/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:movies-home` → `/panel/movies/` · fondo `bg-movies-home`
- `MoviesPublicHomeView`
  - archivo: `apps/movies/views/v1_home.py` · hereda de `BasePublicHomeView` · ruta: `movies:home` → `/catalog/movies/` · fondo `bg-movies-home`
- `ProducerPublicDataView`
  - archivo: `apps/movies/views/v3_data.py` · hereda de `BaseCompany`, `PublicDataView` · ruta: `movies:productoras-catalogo-data` → `/catalog/movies/producers/list/data/` · fondo `bg-movies-company`
- `ProducerPublicListView` — Catálogo de PRODUCTORAS de cine (con buscador y filtros).
  - archivo: `apps/movies/views/v5_list.py` · hereda de `BaseCompany`, `PublicListView` · ruta: `movies:productoras-catalogo` → `/catalog/movies/producers/list/` · fondo `bg-movies-movie`

## Series (`series`)


### Modelo: `Genre` (`apps/series/models.py`)

- Formulario: `GenreForm` (`apps/series/forms.py`) — campos: `name`, `name_esp`, `description`, `explicit`, `image`, `is_active`
- Vistas:
  - `GenreCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseGenre`, `BaseCreate`
    - depende de: formulario `GenreForm`; vuelve a `panel:serie-genre_list`; al guardar va a `panel:serie-genre_list`; plantilla `series/form/genre.html`
    - ruta: `panel:serie-genre_create` → `/panel/serie-genre/create/`
    - fondo: `bg-series-genre`
  - `GenreDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseGenre`, `AdminDataView`
    - ruta: `panel:serie-genre_data` → `/panel/serie-genre/data/`
    - fondo: `bg-series-genre`
  - `GenreDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseGenre`, `BaseDelete`
    - depende de: vuelve a `panel:serie-genre_list`; al guardar va a `panel:serie-genre_list`
    - ruta: `panel:serie-genre_delete` → `/panel/serie-genre/<int:pk>/delete/`
    - fondo: `bg-series-genre`
  - `GenreDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseGenre`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-genre_list`; plantilla `series/detail/genre.html`
    - ruta: `panel:serie-genre_detail` → `/panel/serie-genre/<int:pk>/`
    - fondo: `bg-series-genre`
  - `GenreListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseGenre`, `AdminListView`
    - depende de: datos de `panel:serie-genre_data`
    - ruta: `panel:serie-genre_list` → `/panel/serie-genre/`
    - fondo: `bg-series-genre`
  - `GenreSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseGenre`, `BaseSelectView`
    - ruta: `panel:serie-genre_select` → `/panel/serie-genre/select/`
    - fondo: `bg-series-genre`
  - `GenreUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseGenre`, `BaseUpdate`
    - depende de: formulario `GenreForm`; vuelve a `panel:serie-genre_list`; al guardar va a `panel:serie-genre_list`; plantilla `series/form/genre.html`
    - ruta: `panel:serie-genre_update` → `/panel/serie-genre/<int:pk>/update/`
    - fondo: `bg-series-genre`

### Modelo: `GenreAlias` (`apps/series/models.py`)

- Formulario: `GenreAliasForm` (`apps/series/forms.py`) — campos: `name`, `name_esp`, `is_active`, `genre`
- Vistas:
  - `GenreAliasCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseCreate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:serie-genre-alias_list`; al guardar va a `panel:serie-genre-alias_list`
    - ruta: `panel:serie-genre-alias_create` → `/panel/serie-genre-alias/create/`
    - fondo: `bg-series-serie-genre`
  - `GenreAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseGenreAliasContext`, `AdminDataView`
    - ruta: `panel:serie-genre-alias_data` → `/panel/serie-genre-alias/data/`, `panel:serie-genre-alias_data-by` → `/panel/serie-genre-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-series-serie-genre`
  - `GenreAliasDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseDelete`
    - depende de: vuelve a `panel:serie-genre-alias_list`; al guardar va a `panel:serie-genre-alias_list`
    - ruta: `panel:serie-genre-alias_delete` → `/panel/serie-genre-alias/<int:pk>/delete/`
    - fondo: `bg-series-serie-genre`
  - `GenreAliasDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseGenreAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-genre-alias_list`
    - ruta: `panel:serie-genre-alias_detail` → `/panel/serie-genre-alias/<int:pk>/`
    - fondo: `bg-series-serie-genre`
  - `GenreAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/serie-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`.
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseGenreAliasContext`, `AdminListByView`
    - depende de: datos de `panel:serie-genre-alias_data-by`
    - ruta: `panel:serie-genre-alias_by` → `/panel/serie-genre-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-series-serie-genre`
  - `GenreAliasListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseGenreAlias`, `AdminListView`
    - depende de: datos de `panel:serie-genre-alias_data`
    - ruta: `panel:serie-genre-alias_list` → `/panel/serie-genre-alias/`
    - fondo: `bg-series-serie-genre`
  - `GenreAliasUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseUpdate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:serie-genre-alias_list`; al guardar va a `panel:serie-genre-alias_list`
    - ruta: `panel:serie-genre-alias_update` → `/panel/serie-genre-alias/<int:pk>/update/`
    - fondo: `bg-series-serie-genre`

### Modelo: `Rating` (`apps/series/models.py`)

- Formulario: `RatingForm` (`apps/series/forms.py`) — campos: `name`, `name_esp`, `description`, `acronym`, `image`, `is_active`
- Vistas:
  - `RatingCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseRating`, `BaseCreate`
    - depende de: formulario `RatingForm`; vuelve a `panel:serie-rating_list`; al guardar va a `panel:serie-rating_list`; plantilla `series/form/rating.html`
    - ruta: `panel:serie-rating_create` → `/panel/serie-rating/create/`
    - fondo: `bg-series-rating`
  - `RatingDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseRating`, `AdminDataView`
    - ruta: `panel:serie-rating_data` → `/panel/serie-rating/data/`
    - fondo: `bg-series-rating`
  - `RatingDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseRating`, `BaseDelete`
    - depende de: vuelve a `panel:serie-rating_list`; al guardar va a `panel:serie-rating_list`
    - ruta: `panel:serie-rating_delete` → `/panel/serie-rating/<int:pk>/delete/`
    - fondo: `bg-series-rating`
  - `RatingDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseRating`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-rating_list`; plantilla `series/detail/rating.html`
    - ruta: `panel:serie-rating_detail` → `/panel/serie-rating/<int:pk>/`
    - fondo: `bg-series-rating`
  - `RatingListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseRating`, `AdminListView`
    - depende de: datos de `panel:serie-rating_data`
    - ruta: `panel:serie-rating_list` → `/panel/serie-rating/`
    - fondo: `bg-series-rating`
  - `RatingSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseRating`, `BaseSelectView`
    - ruta: `panel:serie-rating_select` → `/panel/serie-rating/select/`
    - fondo: `bg-series-rating`
  - `RatingUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseRating`, `BaseUpdate`
    - depende de: formulario `RatingForm`; vuelve a `panel:serie-rating_list`; al guardar va a `panel:serie-rating_list`; plantilla `series/form/rating.html`
    - ruta: `panel:serie-rating_update` → `/panel/serie-rating/<int:pk>/update/`
    - fondo: `bg-series-rating`

### Modelo: `Role` (`apps/series/models.py`)

- Formulario: `RoleForm` (`apps/series/forms.py`) — campos: `name`, `name_esp`, `type`, `description`, `image`, `is_active`
- Vistas:
  - `RoleCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseRole`, `BaseCreate`
    - depende de: formulario `RoleForm`; vuelve a `panel:serie-role_list`; al guardar va a `panel:serie-role_list`; plantilla `series/form/role.html`
    - ruta: `panel:serie-role_create` → `/panel/serie-role/create/`
    - fondo: `bg-series-role`
  - `RoleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseRoleContext`, `AdminDataView`
    - ruta: `panel:serie-role_data` → `/panel/serie-role/data/`, `panel:serie-role_data-by` → `/panel/serie-role/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `cast`, `unknown`
    - fondo: `bg-series-role`
  - `RoleDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseRole`, `BaseDelete`
    - depende de: vuelve a `panel:serie-role_list`; al guardar va a `panel:serie-role_list`
    - ruta: `panel:serie-role_delete` → `/panel/serie-role/<int:pk>/delete/`
    - fondo: `bg-series-role`
  - `RoleDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseRole`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-role_list`; plantilla `series/detail/role.html`
    - ruta: `panel:serie-role_detail` → `/panel/serie-role/<int:pk>/`
    - fondo: `bg-series-role`
  - `RoleListByView` (panel) — lista «por» (acotada a un padre) — Lista de roles acotada por familia (`/serie-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`.
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseRoleContext`, `AdminListByView`
    - depende de: datos de `panel:serie-role_data-by`
    - ruta: `panel:serie-role_by` → `/panel/serie-role/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `cast`, `unknown`
    - fondo: `bg-series-role`
  - `RoleListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseRole`, `AdminListView`
    - depende de: datos de `panel:serie-role_data`
    - ruta: `panel:serie-role_list` → `/panel/serie-role/`
    - fondo: `bg-series-role`
  - `RoleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseRole`, `BaseSelectView`
    - ruta: `panel:serie-role_select` → `/panel/serie-role/select/`
    - fondo: `bg-series-role`
  - `RoleUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseRole`, `BaseUpdate`
    - depende de: formulario `RoleForm`; vuelve a `panel:serie-role_list`; al guardar va a `panel:serie-role_list`; plantilla `series/form/role.html`
    - ruta: `panel:serie-role_update` → `/panel/serie-role/<int:pk>/update/`
    - fondo: `bg-series-role`
- Filtros:
  - `RoleFilters`: Tipo de rol (`type`), Activo (`is_active`) — para `RoleDataView`

### Modelo: `Serie` (`apps/series/models.py`)

- Formulario: `SerieForm` (`apps/series/forms.py`) — campos: `title`, `title_secundary`, `release_year`, `duration_minutes`, `synopsis`, `serie_type`, `serie_rating`, `genres`, `producers`, `distributors`, `is_active`
- Vistas:
  - `SerieCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerie`, `BaseCreate`
    - depende de: formulario `SerieForm`; vuelve a `panel:serie_list`; al guardar va a `panel:serie_list`; plantilla `series/form/serie.html`
    - ruta: `panel:serie_create` → `/panel/serie/create/`
    - fondo: `bg-series-serie`
  - `SerieDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieContext`, `AdminDataView`
    - ruta: `panel:serie_data` → `/panel/serie/data/`, `panel:serie_data-by` → `/panel/serie/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `serie_type`); `clasificacion` → padre por id (campo `serie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-series-serie`
  - `SerieDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerie`, `BaseDelete`
    - depende de: vuelve a `panel:serie_list`; al guardar va a `panel:serie_list`
    - ruta: `panel:serie_delete` → `/panel/serie/<int:pk>/delete/`
    - fondo: `bg-series-serie`
  - `SerieDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerie`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie_list`; plantilla `series/detail/serie.html`
    - ruta: `panel:serie_detail` → `/panel/serie/<int:pk>/`
    - fondo: `bg-series-serie`
  - `SerieListByView` (panel) — lista «por» (acotada a un padre) — genero, productora, distribuidora, tipo, clasificacion, persona.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieContext`, `AdminListByView`
    - depende de: datos de `panel:serie_data-by`
    - ruta: `panel:serie_by` → `/panel/serie/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `serie_type`); `clasificacion` → padre por id (campo `serie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-series-serie`
  - `SerieListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerie`, `AdminListView`
    - depende de: datos de `panel:serie_data`
    - ruta: `panel:serie_list` → `/panel/serie/`
    - fondo: `bg-series-serie`
  - `SeriePublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieContext`, `PublicDataView`
    - ruta: `series:lista-data` → `/catalog/series/list/data/`, `series:por-data` → `/catalog/series/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `serie_type`); `clasificacion` → padre por id (campo `serie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-series-serie`
  - `SeriePublicDetailView` (pública) — ficha — Ficha pública de una serie: el mismo HTML que en gestión, sin botones y con la colección.
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerie`, `BasePublicDetailView`
    - depende de: vuelve a `series:lista`; plantilla `series/detail/serie.html`
    - ruta: `series:detalle` → `/catalog/series/series/<int:pk>/<slug:slug>/`, `series:detalle` → `/catalog/series/series/<int:pk>/`
    - fondo: `bg-series-serie`
  - `SeriePublicListByView` (pública) — lista «por» (acotada a un padre) — genero, productora, distribuidora, tipo, clasificacion, persona.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieContext`, `PublicListByView`
    - depende de: datos de `series:por-data`; plantilla `public/list.html`
    - ruta: `series:por` → `/catalog/series/<str:tipo>/<int:pk>/`, `series:por` → `/catalog/series/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `productora` → padre por id (campo `producers`); `distribuidora` → padre por id (campo `distributors`); `tipo` → padre por id (campo `serie_type`); `clasificacion` → padre por id (campo `serie_rating`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-series-serie`
  - `SeriePublicListView` (pública) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerie`, `PublicListView`
    - depende de: datos de `series:lista-data`; plantilla `public/list.html`
    - ruta: `series:lista` → `/catalog/series/list/`
    - fondo: `bg-series-serie`
  - `SerieSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerie`, `BaseSelectView`
    - ruta: `panel:serie_select` → `/panel/serie/select/`
    - fondo: `bg-series-serie`
  - `SerieUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerie`, `BaseUpdate`
    - depende de: formulario `SerieForm`; vuelve a `panel:serie_list`; al guardar va a `panel:serie_list`; plantilla `series/form/serie.html`
    - ruta: `panel:serie_update` → `/panel/serie/<int:pk>/update/`
    - fondo: `bg-series-serie`
- Filtros:
  - `SerieFilters`: Género (`genres`), Tipo (`serie_type`), Productora (`producers`), Clasificación (`serie_rating`), Distribuidora (`distributors`), Año (`release_year`) — para `SerieDataView`, `SeriePublicDataView`

### Modelo: `SerieCast` (`apps/series/models.py`)

- Formulario: `SerieCastForm` (`apps/series/forms.py`) — campos: `serie`, `person`, `role`, `character_name`, `is_active`
- Vistas:
  - `SerieCastCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieCast`, `BaseCreate`
    - depende de: formulario `SerieCastForm`; vuelve a `panel:serie-cast_list`; al guardar va a `panel:serie-cast_list`; plantilla `series/form/serie_cast.html`
    - ruta: `panel:serie-cast_create` → `/panel/serie-cast/create/`
    - fondo: `bg-series-serie-cast`
  - `SerieCastDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieCastContext`, `AdminDataView`
    - ruta: `panel:serie-cast_data` → `/panel/serie-cast/data/`, `panel:serie-cast_data-by` → `/panel/serie-cast/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie-cast`
  - `SerieCastDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieCast`, `BaseDelete`
    - depende de: vuelve a `panel:serie-cast_list`; al guardar va a `panel:serie-cast_list`
    - ruta: `panel:serie-cast_delete` → `/panel/serie-cast/<int:pk>/delete/`
    - fondo: `bg-series-serie-cast`
  - `SerieCastDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerieCast`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-cast_list`; plantilla `series/detail/serie_cast.html`
    - ruta: `panel:serie-cast_detail` → `/panel/serie-cast/<int:pk>/`
    - fondo: `bg-series-serie-cast`
  - `SerieCastListByView` (panel) — lista «por» (acotada a un padre) — serie, persona.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieCastContext`, `AdminListByView`
    - depende de: datos de `panel:serie-cast_data-by`
    - ruta: `panel:serie-cast_by` → `/panel/serie-cast/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie-cast`
  - `SerieCastListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerieCast`, `AdminListView`
    - depende de: datos de `panel:serie-cast_data`
    - ruta: `panel:serie-cast_list` → `/panel/serie-cast/`
    - fondo: `bg-series-serie-cast`
  - `SerieCastPublicDataView` (pública) — datos JSON de la lista — Reparto de una serie: [la persona (foto + nombre → su ficha) · personaje · rol].
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieCastContext`, `PublicDataView`
    - ruta: `series:reparto-por-data` → `/catalog/series/cast/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie-cast`
  - `SerieCastPublicListByView` (pública) — lista «por» (acotada a un padre) — serie, persona.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieCastContext`, `PublicListByView`
    - depende de: datos de `series:reparto-por-data`; plantilla `public/list.html`
    - ruta: `series:reparto-por` → `/catalog/series/cast/<str:tipo>/<int:pk>/`, `series:reparto-por` → `/catalog/series/cast/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie`
  - `SerieCastSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieCast`, `BaseSelectView`
    - ruta: `panel:serie-cast_select` → `/panel/serie-cast/select/`
    - fondo: `bg-series-serie-cast`
  - `SerieCastUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieCast`, `BaseUpdate`
    - depende de: formulario `SerieCastForm`; vuelve a `panel:serie-cast_list`; al guardar va a `panel:serie-cast_list`; plantilla `series/form/serie_cast.html`
    - ruta: `panel:serie-cast_update` → `/panel/serie-cast/<int:pk>/update/`
    - fondo: `bg-series-serie-cast`
- Filtros:
  - `SerieCastFilters`: Rol (`role`) — para `SerieCastDataView`, `SerieCastPublicDataView`

### Modelo: `SerieImage` (`apps/series/models.py`)

- Formulario: `SerieImageForm` (`apps/series/forms.py`) — campos: `serie`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `SerieImageCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieImage`, `BaseCreate`
    - depende de: formulario `SerieImageForm`; vuelve a `panel:serie-image_list`; al guardar va a `panel:serie-image_list`; plantilla `series/form/serie_image.html`
    - ruta: `panel:serie-image_create` → `/panel/serie-image/create/`
    - fondo: `bg-series-serie-image`
  - `SerieImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieImageContext`, `AdminDataView`
    - ruta: `panel:serie-image_data` → `/panel/serie-image/data/`, `panel:serie-image_data-by` → `/panel/serie-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`)
    - fondo: `bg-series-serie-image`
  - `SerieImageDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieImage`, `BaseDelete`
    - depende de: vuelve a `panel:serie-image_list`; al guardar va a `panel:serie-image_list`
    - ruta: `panel:serie-image_delete` → `/panel/serie-image/<int:pk>/delete/`
    - fondo: `bg-series-serie-image`
  - `SerieImageDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerieImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-image_list`; plantilla `series/detail/serie_image.html`
    - ruta: `panel:serie-image_detail` → `/panel/serie-image/<int:pk>/`
    - fondo: `bg-series-serie-image`
  - `SerieImageListByView` (panel) — lista «por» (acotada a un padre) — serie.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieImageContext`, `AdminListByView`
    - depende de: datos de `panel:serie-image_data-by`
    - ruta: `panel:serie-image_by` → `/panel/serie-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`)
    - fondo: `bg-series-serie-image`
  - `SerieImageListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerieImage`, `AdminListView`
    - depende de: datos de `panel:serie-image_data`
    - ruta: `panel:serie-image_list` → `/panel/serie-image/`
    - fondo: `bg-series-serie-image`
  - `SerieImagePublicListByView` (pública) — lista «por» (acotada a un padre) — serie.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieImageContext`, `PublicListByView`
    - depende de: datos de `series:imagenes-por-data`; plantilla `public/list.html`
    - ruta: `series:imagenes-por` → `/catalog/series/images/<str:tipo>/<int:pk>/`, `series:imagenes-por` → `/catalog/series/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `serie` → padre por id (campo `serie`)
    - fondo: `bg-series-serie`
  - `SerieImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieImage`, `BaseSelectView`
    - ruta: `panel:serie-image_select` → `/panel/serie-image/select/`
    - fondo: `bg-series-serie-image`
  - `SerieImageUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieImage`, `BaseUpdate`
    - depende de: formulario `SerieImageForm`; vuelve a `panel:serie-image_list`; al guardar va a `panel:serie-image_list`; plantilla `series/form/serie_image.html`
    - ruta: `panel:serie-image_update` → `/panel/serie-image/<int:pk>/update/`
    - fondo: `bg-series-serie-image`
  - `SerieImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de una serie: sus imágenes en tarjetas (la portada va en la ficha).
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieImageContext`, `PublicDataView`
    - ruta: `series:imagenes-por-data` → `/catalog/series/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `serie` → padre por id (campo `serie`)
    - fondo: `bg-series-serie-image`

### Modelo: `SerieLog` (`apps/series/models.py`)

- Formulario: `SerieLogForm` (`apps/series/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `SerieLogCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieLog`, `BaseCreate`
    - depende de: formulario `SerieLogForm`; vuelve a `panel:serie-log_list`; al guardar va a `panel:serie-log_list`
    - ruta: `panel:serie-log_create` → `/panel/serie-log/create/`
    - fondo: `bg-series-serie-log`
  - `SerieLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieLog`, `AdminDataView`
    - ruta: `panel:serie-log_data` → `/panel/serie-log/data/`
    - fondo: `bg-series-serie-log`
  - `SerieLogDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieLog`, `BaseDelete`
    - depende de: vuelve a `panel:serie-log_list`; al guardar va a `panel:serie-log_list`
    - ruta: `panel:serie-log_delete` → `/panel/serie-log/<int:pk>/delete/`
    - fondo: `bg-series-serie-log`
  - `SerieLogDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerieLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-log_list`; plantilla `series/detail/serie_log.html`
    - ruta: `panel:serie-log_detail` → `/panel/serie-log/<int:pk>/`
    - fondo: `bg-series-serie-log`
  - `SerieLogListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerieLog`, `AdminListView`
    - depende de: datos de `panel:serie-log_data`
    - ruta: `panel:serie-log_list` → `/panel/serie-log/`
    - fondo: `bg-series-serie-log`
  - `SerieLogUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieLog`, `BaseUpdate`
    - depende de: formulario `SerieLogForm`; vuelve a `panel:serie-log_list`; al guardar va a `panel:serie-log_list`
    - ruta: `panel:serie-log_update` → `/panel/serie-log/<int:pk>/update/`
    - fondo: `bg-series-serie-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `SerieLogDataView`

### Modelo: `SerieRelation` (`apps/series/models.py`)

- Formulario: `SerieRelationForm` (`apps/series/forms.py`) — campos: `serie`, `related`, `relation_type`, `is_active`
- Vistas:
  - `SerieRelationCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieRelation`, `BaseCreate`
    - depende de: formulario `SerieRelationForm`; vuelve a `panel:serie-relation_list`; al guardar va a `panel:serie-relation_list`; plantilla `series/form/serie_relation.html`
    - ruta: `panel:serie-relation_create` → `/panel/serie-relation/create/`
    - fondo: `bg-series-serie-relation`
  - `SerieRelationDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieRelationContext`, `AdminDataView`
    - ruta: `panel:serie-relation_data` → `/panel/serie-relation/data/`, `panel:serie-relation_data-by` → `/panel/serie-relation/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `tipo` → padre por id (campo `relation_type`)
    - fondo: `bg-series-serie-relation`
  - `SerieRelationDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieRelation`, `BaseDelete`
    - depende de: vuelve a `panel:serie-relation_list`; al guardar va a `panel:serie-relation_list`
    - ruta: `panel:serie-relation_delete` → `/panel/serie-relation/<int:pk>/delete/`
    - fondo: `bg-series-serie-relation`
  - `SerieRelationDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerieRelation`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-relation_list`; plantilla `series/detail/serie_relation.html`
    - ruta: `panel:serie-relation_detail` → `/panel/serie-relation/<int:pk>/`
    - fondo: `bg-series-serie-relation`
  - `SerieRelationListByView` (panel) — lista «por» (acotada a un padre) — serie, tipo.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieRelationContext`, `AdminListByView`
    - depende de: datos de `panel:serie-relation_data-by`
    - ruta: `panel:serie-relation_by` → `/panel/serie-relation/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `tipo` → padre por id (campo `relation_type`)
    - fondo: `bg-series-serie-relation`
  - `SerieRelationListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerieRelation`, `AdminListView`
    - depende de: datos de `panel:serie-relation_data`
    - ruta: `panel:serie-relation_list` → `/panel/serie-relation/`
    - fondo: `bg-series-serie-relation`
  - `SerieRelationSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieRelation`, `BaseSelectView`
    - ruta: `panel:serie-relation_select` → `/panel/serie-relation/select/`
    - fondo: `bg-series-serie-relation`
  - `SerieRelationUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieRelation`, `BaseUpdate`
    - depende de: formulario `SerieRelationForm`; vuelve a `panel:serie-relation_list`; al guardar va a `panel:serie-relation_list`; plantilla `series/form/serie_relation.html`
    - ruta: `panel:serie-relation_update` → `/panel/serie-relation/<int:pk>/update/`
    - fondo: `bg-series-serie-relation`

### Modelo: `SerieStaff` (`apps/series/models.py`)

- Formulario: `SerieStaffForm` (`apps/series/forms.py`) — campos: `serie`, `person`, `role`, `is_active`
- Vistas:
  - `SerieStaffCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieStaff`, `BaseCreate`
    - depende de: formulario `SerieStaffForm`; vuelve a `panel:serie-staff_list`; al guardar va a `panel:serie-staff_list`; plantilla `series/form/serie_staff.html`
    - ruta: `panel:serie-staff_create` → `/panel/serie-staff/create/`
    - fondo: `bg-series-serie-staff`
  - `SerieStaffDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieStaffContext`, `AdminDataView`
    - ruta: `panel:serie-staff_data` → `/panel/serie-staff/data/`, `panel:serie-staff_data-by` → `/panel/serie-staff/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie-staff`
  - `SerieStaffDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieStaff`, `BaseDelete`
    - depende de: vuelve a `panel:serie-staff_list`; al guardar va a `panel:serie-staff_list`
    - ruta: `panel:serie-staff_delete` → `/panel/serie-staff/<int:pk>/delete/`
    - fondo: `bg-series-serie-staff`
  - `SerieStaffDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerieStaff`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-staff_list`; plantilla `series/detail/serie_staff.html`
    - ruta: `panel:serie-staff_detail` → `/panel/serie-staff/<int:pk>/`
    - fondo: `bg-series-serie-staff`
  - `SerieStaffListByView` (panel) — lista «por» (acotada a un padre) — serie, persona.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieStaffContext`, `AdminListByView`
    - depende de: datos de `panel:serie-staff_data-by`
    - ruta: `panel:serie-staff_by` → `/panel/serie-staff/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie-staff`
  - `SerieStaffListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerieStaff`, `AdminListView`
    - depende de: datos de `panel:serie-staff_data`
    - ruta: `panel:serie-staff_list` → `/panel/serie-staff/`
    - fondo: `bg-series-serie-staff`
  - `SerieStaffPublicDataView` (pública) — datos JSON de la lista — Equipo técnico de una serie: [la persona (foto + nombre → su ficha) · rol].
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieStaffContext`, `PublicDataView`
    - ruta: `series:equipo-por-data` → `/catalog/series/staff/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie-staff`
  - `SerieStaffPublicListByView` (pública) — lista «por» (acotada a un padre) — serie, persona.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieStaffContext`, `PublicListByView`
    - depende de: datos de `series:equipo-por-data`; plantilla `public/list.html`
    - ruta: `series:equipo-por` → `/catalog/series/staff/<str:tipo>/<int:pk>/`, `series:equipo-por` → `/catalog/series/staff/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `serie` → padre por id (campo `serie`); `persona` → padre por id (campo `person`)
    - fondo: `bg-series-serie`
  - `SerieStaffSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieStaff`, `BaseSelectView`
    - ruta: `panel:serie-staff_select` → `/panel/serie-staff/select/`
    - fondo: `bg-series-serie-staff`
  - `SerieStaffUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieStaff`, `BaseUpdate`
    - depende de: formulario `SerieStaffForm`; vuelve a `panel:serie-staff_list`; al guardar va a `panel:serie-staff_list`; plantilla `series/form/serie_staff.html`
    - ruta: `panel:serie-staff_update` → `/panel/serie-staff/<int:pk>/update/`
    - fondo: `bg-series-serie-staff`
- Filtros:
  - `SerieStaffFilters`: Rol (`role`) — para `SerieStaffDataView`, `SerieStaffPublicDataView`

### Modelo: `SerieTitle` (`apps/series/models.py`)

- Formulario: `SerieTitleForm` (`apps/series/forms.py`) — campos: `serie`, `title_lang`, `title`, `is_active`
- Vistas:
  - `SerieTitleCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieTitle`, `BaseCreate`
    - depende de: formulario `SerieTitleForm`; vuelve a `panel:serie-title_list`; al guardar va a `panel:serie-title_list`; plantilla `series/form/serie_title.html`
    - ruta: `panel:serie-title_create` → `/panel/serie-title/create/`
    - fondo: `bg-series-title-serie`
  - `SerieTitleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieTitleContext`, `AdminDataView`
    - ruta: `panel:serie-title_data` → `/panel/serie-title/data/`, `panel:serie-title_data-by` → `/panel/serie-title/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`)
    - fondo: `bg-series-title-serie`
  - `SerieTitleDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieTitle`, `BaseDelete`
    - depende de: vuelve a `panel:serie-title_list`; al guardar va a `panel:serie-title_list`
    - ruta: `panel:serie-title_delete` → `/panel/serie-title/<int:pk>/delete/`
    - fondo: `bg-series-title-serie`
  - `SerieTitleDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseSerieTitle`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-title_list`; plantilla `series/detail/serie_title.html`
    - ruta: `panel:serie-title_detail` → `/panel/serie-title/<int:pk>/`
    - fondo: `bg-series-title-serie`
  - `SerieTitleListByView` (panel) — lista «por» (acotada a un padre) — serie.
    - archivo: `apps/series/views/v5_list_by.py` · hereda de `BaseSerieTitleContext`, `AdminListByView`
    - depende de: datos de `panel:serie-title_data-by`
    - ruta: `panel:serie-title_by` → `/panel/serie-title/<str:tipo>/<str:pk>/`
    - mapa «by»: `serie` → padre por id (campo `serie`)
    - fondo: `bg-series-title-serie`
  - `SerieTitleListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseSerieTitle`, `AdminListView`
    - depende de: datos de `panel:serie-title_data`
    - ruta: `panel:serie-title_list` → `/panel/serie-title/`
    - fondo: `bg-series-title-serie`
  - `SerieTitleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseSerieTitle`, `BaseSelectView`
    - ruta: `panel:serie-title_select` → `/panel/serie-title/select/`
    - fondo: `bg-series-title-serie`
  - `SerieTitleUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseSerieTitle`, `BaseUpdate`
    - depende de: formulario `SerieTitleForm`; vuelve a `panel:serie-title_list`; al guardar va a `panel:serie-title_list`; plantilla `series/form/serie_title.html`
    - ruta: `panel:serie-title_update` → `/panel/serie-title/<int:pk>/update/`
    - fondo: `bg-series-title-serie`

### Modelo: `Type` (`apps/series/models.py`)

- Formulario: `TypeForm` (`apps/series/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `TypeCreateView` (panel) — alta
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseType`, `BaseCreate`
    - depende de: formulario `TypeForm`; vuelve a `panel:serie-type_list`; al guardar va a `panel:serie-type_list`; plantilla `series/form/type.html`
    - ruta: `panel:serie-type_create` → `/panel/serie-type/create/`
    - fondo: `bg-series-type`
  - `TypeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseType`, `AdminDataView`
    - ruta: `panel:serie-type_data` → `/panel/serie-type/data/`
    - fondo: `bg-series-type`
  - `TypeDeleteView` (panel) — borrado
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseType`, `BaseDelete`
    - depende de: vuelve a `panel:serie-type_list`; al guardar va a `panel:serie-type_list`
    - ruta: `panel:serie-type_delete` → `/panel/serie-type/<int:pk>/delete/`
    - fondo: `bg-series-type`
  - `TypeDetailView` (panel) — ficha
    - archivo: `apps/series/views/v6_detail.py` · hereda de `BaseType`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-type_list`; plantilla `series/detail/type.html`
    - ruta: `panel:serie-type_detail` → `/panel/serie-type/<int:pk>/`
    - fondo: `bg-series-type`
  - `TypeListView` (panel) — lista
    - archivo: `apps/series/views/v5_list.py` · hereda de `BaseType`, `AdminListView`
    - depende de: datos de `panel:serie-type_data`
    - ruta: `panel:serie-type_list` → `/panel/serie-type/`
    - fondo: `bg-series-type`
  - `TypeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/series/views/v3_data.py` · hereda de `BaseType`, `BaseSelectView`
    - ruta: `panel:serie-type_select` → `/panel/serie-type/select/`
    - fondo: `bg-series-type`
  - `TypeUpdateView` (panel) — edición
    - archivo: `apps/series/views/v4_write.py` · hereda de `BaseType`, `BaseUpdate`
    - depende de: formulario `TypeForm`; vuelve a `panel:serie-type_list`; al guardar va a `panel:serie-type_list`; plantilla `series/form/type.html`
    - ruta: `panel:serie-type_update` → `/panel/serie-type/<int:pk>/update/`
    - fondo: `bg-series-type`

### Sin modelo

- `DistributorPublicDataView`
  - archivo: `apps/series/views/v3_data.py` · hereda de `BaseCompany`, `PublicDataView` · ruta: `series:distribuidoras-catalogo-data` → `/catalog/series/distributors/list/data/` · fondo `bg-series-company`
- `DistributorPublicListView` — Catálogo de DISTRIBUIDORAS de series (con buscador y filtros).
  - archivo: `apps/series/views/v5_list.py` · hereda de `BaseCompany`, `PublicListView` · ruta: `series:distribuidoras-catalogo` → `/catalog/series/distributors/list/` · fondo `bg-series-serie`
- `ProducerPublicDataView`
  - archivo: `apps/series/views/v3_data.py` · hereda de `BaseCompany`, `PublicDataView` · ruta: `series:productoras-catalogo-data` → `/catalog/series/producers/list/data/` · fondo `bg-series-company`
- `ProducerPublicListView` — Catálogo de PRODUCTORAS de series (con buscador y filtros).
  - archivo: `apps/series/views/v5_list.py` · hereda de `BaseCompany`, `PublicListView` · ruta: `series:productoras-catalogo` → `/catalog/series/producers/list/` · fondo `bg-series-serie`
- `SeriesHomeView`
  - archivo: `apps/series/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:series-home` → `/panel/series/` · fondo `bg-series-home`
- `SeriesPublicHomeView`
  - archivo: `apps/series/views/v1_home.py` · hereda de `BasePublicHomeView` · ruta: `series:home` → `/catalog/series/` · fondo `bg-series-home`

## Anime & Manga (`otaku`)

### Modelo: `Anime` (`apps/otaku/models.py`)

- Formulario: `AnimeForm` (`apps/otaku/forms.py`) — campos: `title`, `title_eng`, `title_jap`, `synopsis`, `anime_type`, `source`, `rating`, `status`, `season`, `year`, `episodes`, `studios`, `producers`, `licensors`, `genres`, `themes`, `demographics`, `from_date`, `to_date`, `is_active`
- Vistas:
  - `AnimeCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnime`, `BaseCreate`
    - depende de: formulario `AnimeForm`; vuelve a `panel:anime_list`; al guardar va a `panel:anime_list`; plantilla `otaku/form/anime.html`
    - ruta: `panel:anime_create` → `/panel/anime/create/`
    - fondo: `bg-otaku-anime`
  - `AnimeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeContext`, `AdminDataView`
    - ruta: `panel:anime_data` → `/panel/anime/data/`, `panel:anime_data-by` → `/panel/anime/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `estudio` → padre por id (campo `studios`); `productora` → padre por id (campo `producers`); `licenciataria` → padre por id (campo `licensors`); `tipo` → padre por id (campo `anime_type`); `estado` → padre por id (campo `status`); `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-anime`
  - `AnimeDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnime`, `BaseDelete`
    - depende de: vuelve a `panel:anime_list`; al guardar va a `panel:anime_list`
    - ruta: `panel:anime_delete` → `/panel/anime/<int:pk>/delete/`
    - fondo: `bg-otaku-anime`
  - `AnimeDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseAnime`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:anime_list`; plantilla `otaku/detail/anime.html`
    - ruta: `panel:anime_detail` → `/panel/anime/<int:pk>/`
    - fondo: `bg-otaku-anime`
  - `AnimeListByView` (panel) — lista «por» (acotada a un padre) — genero, tema, demografia, estudio, productora, licenciataria, tipo, estado, temporada, fuente, clasificacion, personaje, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeContext`, `AdminListByView`
    - depende de: datos de `panel:anime_data-by`
    - ruta: `panel:anime_by` → `/panel/anime/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `estudio` → padre por id (campo `studios`); `productora` → padre por id (campo `producers`); `licenciataria` → padre por id (campo `licensors`); `tipo` → padre por id (campo `anime_type`); `estado` → padre por id (campo `status`); `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-anime`
  - `AnimeListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseAnime`, `AdminListView`
    - depende de: datos de `panel:anime_data`
    - ruta: `panel:anime_list` → `/panel/anime/`
    - fondo: `bg-otaku-anime`
  - `AnimePublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeContext`, `PublicDataView`
    - ruta: `otaku:anime-catalogo-data` → `/catalog/otaku/anime/list/data/`, `otaku:anime-por-data` → `/catalog/otaku/anime/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `estudio` → padre por id (campo `studios`); `productora` → padre por id (campo `producers`); `licenciataria` → padre por id (campo `licensors`); `tipo` → padre por id (campo `anime_type`); `estado` → padre por id (campo `status`); `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-anime`
  - `AnimePublicDetailView` (pública) — ficha — Ficha pública de un anime: el mismo HTML que en gestión, sin botones y con la colección.
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseAnime`, `BasePublicDetailView`
    - depende de: vuelve a `otaku:anime-catalogo`; plantilla `otaku/detail/anime.html`
    - ruta: `otaku:detalle-anime` → `/catalog/otaku/anime/<int:pk>/<slug:slug>/`, `otaku:detalle-anime` → `/catalog/otaku/anime/<int:pk>/`
    - fondo: `bg-otaku-anime`
  - `AnimePublicListByView` (pública) — lista «por» (acotada a un padre) — genero, tema, demografia, estudio, productora, licenciataria, tipo, estado, temporada, fuente, clasificacion, personaje, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeContext`, `PublicListByView`
    - depende de: datos de `otaku:anime-por-data`; plantilla `public/list.html`
    - ruta: `otaku:anime-por` → `/catalog/otaku/anime/<str:tipo>/<int:pk>/`, `otaku:anime-por` → `/catalog/otaku/anime/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `estudio` → padre por id (campo `studios`); `productora` → padre por id (campo `producers`); `licenciataria` → padre por id (campo `licensors`); `tipo` → padre por id (campo `anime_type`); `estado` → padre por id (campo `status`); `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-anime`
  - `AnimePublicListView` (pública) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseAnime`, `PublicListView`
    - depende de: datos de `otaku:anime-catalogo-data`; plantilla `public/list.html`
    - ruta: `otaku:anime-catalogo` → `/catalog/otaku/anime/list/`
    - fondo: `bg-otaku-anime`
  - `AnimeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnime`, `BaseSelectView`
    - ruta: `panel:anime_select` → `/panel/anime/select/`
    - fondo: `bg-otaku-anime`
  - `AnimeUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnime`, `BaseUpdate`
    - depende de: formulario `AnimeForm`; vuelve a `panel:anime_list`; al guardar va a `panel:anime_list`; plantilla `otaku/form/anime.html`
    - ruta: `panel:anime_update` → `/panel/anime/<int:pk>/update/`
    - fondo: `bg-otaku-anime`
- Filtros:
  - `AnimeFilters`: Género (`genres`), Tipo (`anime_type`), Temas (`themes`), Demografías (`demographics`), Estudios (`studios`), Productoras (`producers`), Licenciatarias (`licensors`), Estado (`status`), Fuente (`source`), Clasificación (`rating`), Temporada (`season`), Año (`year`) — para `AnimeDataView`, `AnimePublicDataView`

### Modelo: `AnimeCharacter` (`apps/otaku/models.py`)

- Formulario: `AnimeCharacterForm` (`apps/otaku/forms.py`) — campos: `anime`, `character`, `role`, `is_active`
- Vistas:
  - `AnimeCharacterCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeCharacter`, `BaseCreate`
    - depende de: formulario `AnimeCharacterForm`; vuelve a `panel:anime-character_list`; al guardar va a `panel:anime-character_list`; plantilla `otaku/form/anime_character.html`
    - ruta: `panel:anime-character_create` → `/panel/anime-character/create/`
    - fondo: `bg-otaku-anime-character`
  - `AnimeCharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeCharacterContext`, `AdminDataView`
    - ruta: `panel:anime-character_data` → `/panel/anime-character/data/`, `panel:anime-character_data-by` → `/panel/anime-character/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`); `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-anime-character`
  - `AnimeCharacterDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:anime-character_list`; al guardar va a `panel:anime-character_list`
    - ruta: `panel:anime-character_delete` → `/panel/anime-character/<int:pk>/delete/`
    - fondo: `bg-otaku-anime-character`
  - `AnimeCharacterDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseAnimeCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:anime-character_list`; plantilla `otaku/detail/anime_character.html`
    - ruta: `panel:anime-character_detail` → `/panel/anime-character/<int:pk>/`
    - fondo: `bg-otaku-anime-character`
  - `AnimeCharacterListByView` (panel) — lista «por» (acotada a un padre) — anime, personaje.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeCharacterContext`, `AdminListByView`
    - depende de: datos de `panel:anime-character_data-by`
    - ruta: `panel:anime-character_by` → `/panel/anime-character/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`); `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-anime-character`
  - `AnimeCharacterListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseAnimeCharacter`, `AdminListView`
    - depende de: datos de `panel:anime-character_data`
    - ruta: `panel:anime-character_list` → `/panel/anime-character/`
    - fondo: `bg-otaku-anime-character`
  - `AnimeCharacterSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeCharacter`, `BaseSelectView`
    - ruta: `panel:anime-character_select` → `/panel/anime-character/select/`
    - fondo: `bg-otaku-anime-character`
  - `AnimeCharacterUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeCharacter`, `BaseUpdate`
    - depende de: formulario `AnimeCharacterForm`; vuelve a `panel:anime-character_list`; al guardar va a `panel:anime-character_list`; plantilla `otaku/form/anime_character.html`
    - ruta: `panel:anime-character_update` → `/panel/anime-character/<int:pk>/update/`
    - fondo: `bg-otaku-anime-character`

### Modelo: `AnimeImage` (`apps/otaku/models.py`)

- Formulario: `AnimeImageForm` (`apps/otaku/forms.py`) — campos: `anime`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `AnimeImageCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeImage`, `BaseCreate`
    - depende de: formulario `AnimeImageForm`; vuelve a `panel:anime-image_list`; al guardar va a `panel:anime-image_list`; plantilla `otaku/form/anime_image.html`
    - ruta: `panel:anime-image_create` → `/panel/anime-image/create/`
    - fondo: `bg-otaku-anime-image`
  - `AnimeImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeImageContext`, `AdminDataView`
    - ruta: `panel:anime-image_data` → `/panel/anime-image/data/`, `panel:anime-image_data-by` → `/panel/anime-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`)
    - fondo: `bg-otaku-anime-image`
  - `AnimeImageDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeImage`, `BaseDelete`
    - depende de: vuelve a `panel:anime-image_list`; al guardar va a `panel:anime-image_list`
    - ruta: `panel:anime-image_delete` → `/panel/anime-image/<int:pk>/delete/`
    - fondo: `bg-otaku-anime-image`
  - `AnimeImageDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseAnimeImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:anime-image_list`; plantilla `otaku/detail/anime_image.html`
    - ruta: `panel:anime-image_detail` → `/panel/anime-image/<int:pk>/`
    - fondo: `bg-otaku-anime-image`
  - `AnimeImageListByView` (panel) — lista «por» (acotada a un padre) — anime.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeImageContext`, `AdminListByView`
    - depende de: datos de `panel:anime-image_data-by`
    - ruta: `panel:anime-image_by` → `/panel/anime-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`)
    - fondo: `bg-otaku-anime-image`
  - `AnimeImageListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseAnimeImage`, `AdminListView`
    - depende de: datos de `panel:anime-image_data`
    - ruta: `panel:anime-image_list` → `/panel/anime-image/`
    - fondo: `bg-otaku-anime-image`
  - `AnimeImagePublicListByView` (pública) — lista «por» (acotada a un padre) — anime.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeImageContext`, `PublicListByView`
    - depende de: datos de `otaku:anime-imagenes-por-data`; plantilla `public/list.html`
    - ruta: `otaku:anime-imagenes-por` → `/catalog/otaku/anime/images/<str:tipo>/<int:pk>/`, `otaku:anime-imagenes-por` → `/catalog/otaku/anime/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `anime` → padre por id (campo `anime`)
    - fondo: `bg-otaku-anime-image`
  - `AnimeImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeImage`, `BaseSelectView`
    - ruta: `panel:anime-image_select` → `/panel/anime-image/select/`
    - fondo: `bg-otaku-anime-image`
  - `AnimeImageUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeImage`, `BaseUpdate`
    - depende de: formulario `AnimeImageForm`; vuelve a `panel:anime-image_list`; al guardar va a `panel:anime-image_list`; plantilla `otaku/form/anime_image.html`
    - ruta: `panel:anime-image_update` → `/panel/anime-image/<int:pk>/update/`
    - fondo: `bg-otaku-anime-image`
  - `AnimeImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de un anime: sus imágenes en tarjetas.
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeImageContext`, `PublicDataView`
    - ruta: `otaku:anime-imagenes-por-data` → `/catalog/otaku/anime/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `anime` → padre por id (campo `anime`)
    - fondo: `bg-otaku-anime-image`

### Modelo: `AnimeSong` (`apps/otaku/models.py`)

- Formulario: `AnimeSongForm` (`apps/otaku/forms.py`) — campos: `anime`, `type`, `song_id`, `artists`, `title`, `title_kanji`, `title_eng`, `is_active`
- Vistas:
  - `AnimeSongCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeSong`, `BaseCreate`
    - depende de: formulario `AnimeSongForm`; vuelve a `panel:anime-song_list`; al guardar va a `panel:anime-song_list`; plantilla `otaku/form/anime_song.html`
    - ruta: `panel:anime-song_create` → `/panel/anime-song/create/`
    - fondo: `bg-otaku-anime-song`
  - `AnimeSongDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeSongContext`, `AdminDataView`
    - ruta: `panel:anime-song_data` → `/panel/anime-song/data/`, `panel:anime-song_data-by` → `/panel/anime-song/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`); `type` → choice: `OP`, `ED`, `IN`
    - fondo: `bg-otaku-anime-song`
  - `AnimeSongDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeSong`, `BaseDelete`
    - depende de: vuelve a `panel:anime-song_list`; al guardar va a `panel:anime-song_list`
    - ruta: `panel:anime-song_delete` → `/panel/anime-song/<int:pk>/delete/`
    - fondo: `bg-otaku-anime-song`
  - `AnimeSongDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseAnimeSong`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:anime-song_list`; plantilla `otaku/detail/anime_song.html`
    - ruta: `panel:anime-song_detail` → `/panel/anime-song/<int:pk>/`
    - fondo: `bg-otaku-anime-song`
  - `AnimeSongListByView` (panel) — lista «por» (acotada a un padre) — anime.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeSongContext`, `AdminListByView`
    - depende de: datos de `panel:anime-song_data-by`
    - ruta: `panel:anime-song_by` → `/panel/anime-song/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`); `type` → choice: `OP`, `ED`, `IN`
    - fondo: `bg-otaku-anime-song`
  - `AnimeSongListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseAnimeSong`, `AdminListView`
    - depende de: datos de `panel:anime-song_data`
    - ruta: `panel:anime-song_list` → `/panel/anime-song/`
    - fondo: `bg-otaku-anime-song`
  - `AnimeSongSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeSong`, `BaseSelectView`
    - ruta: `panel:anime-song_select` → `/panel/anime-song/select/`
    - fondo: `bg-otaku-anime-song`
  - `AnimeSongUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeSong`, `BaseUpdate`
    - depende de: formulario `AnimeSongForm`; vuelve a `panel:anime-song_list`; al guardar va a `panel:anime-song_list`; plantilla `otaku/form/anime_song.html`
    - ruta: `panel:anime-song_update` → `/panel/anime-song/<int:pk>/update/`
    - fondo: `bg-otaku-anime-song`
- Filtros:
  - `AnimeSongFilters`: Tipo (`type`), Activo (`is_active`), Anime (`anime`) — para `AnimeSongDataView`

### Modelo: `AnimeStaff` (`apps/otaku/models.py`)

- Formulario: `AnimeStaffForm` (`apps/otaku/forms.py`) — campos: `anime`, `person`, `role`, `is_active`
- Vistas:
  - `AnimeStaffCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeStaff`, `BaseCreate`
    - depende de: formulario `AnimeStaffForm`; vuelve a `panel:anime-staff_list`; al guardar va a `panel:anime-staff_list`; plantilla `otaku/form/anime_staff.html`
    - ruta: `panel:anime-staff_create` → `/panel/anime-staff/create/`
    - fondo: `bg-otaku-anime-staff`
  - `AnimeStaffDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeStaffContext`, `AdminDataView`
    - ruta: `panel:anime-staff_data` → `/panel/anime-staff/data/`, `panel:anime-staff_data-by` → `/panel/anime-staff/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`); `persona` → padre por id (campo `person`)
    - fondo: `bg-otaku-anime-staff`
  - `AnimeStaffDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeStaff`, `BaseDelete`
    - depende de: vuelve a `panel:anime-staff_list`; al guardar va a `panel:anime-staff_list`
    - ruta: `panel:anime-staff_delete` → `/panel/anime-staff/<int:pk>/delete/`
    - fondo: `bg-otaku-anime-staff`
  - `AnimeStaffDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseAnimeStaff`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:anime-staff_list`; plantilla `otaku/detail/anime_staff.html`
    - ruta: `panel:anime-staff_detail` → `/panel/anime-staff/<int:pk>/`
    - fondo: `bg-otaku-anime-staff`
  - `AnimeStaffListByView` (panel) — lista «por» (acotada a un padre) — anime, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeStaffContext`, `AdminListByView`
    - depende de: datos de `panel:anime-staff_data-by`
    - ruta: `panel:anime-staff_by` → `/panel/anime-staff/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`); `persona` → padre por id (campo `person`)
    - fondo: `bg-otaku-anime-staff`
  - `AnimeStaffListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseAnimeStaff`, `AdminListView`
    - depende de: datos de `panel:anime-staff_data`
    - ruta: `panel:anime-staff_list` → `/panel/anime-staff/`
    - fondo: `bg-otaku-anime-staff`
  - `AnimeStaffSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeStaff`, `BaseSelectView`
    - ruta: `panel:anime-staff_select` → `/panel/anime-staff/select/`
    - fondo: `bg-otaku-anime-staff`
  - `AnimeStaffUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeStaff`, `BaseUpdate`
    - depende de: formulario `AnimeStaffForm`; vuelve a `panel:anime-staff_list`; al guardar va a `panel:anime-staff_list`; plantilla `otaku/form/anime_staff.html`
    - ruta: `panel:anime-staff_update` → `/panel/anime-staff/<int:pk>/update/`
    - fondo: `bg-otaku-anime-staff`

### Modelo: `AnimeTitle` (`apps/otaku/models.py`)

- Formulario: `AnimeTitleForm` (`apps/otaku/forms.py`) — campos: `anime`, `title_lang`, `title`, `is_active`
- Vistas:
  - `AnimeTitleCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeTitle`, `BaseCreate`
    - depende de: formulario `AnimeTitleForm`; vuelve a `panel:anime-title_list`; al guardar va a `panel:anime-title_list`; plantilla `otaku/form/anime_title.html`
    - ruta: `panel:anime-title_create` → `/panel/anime-title/create/`
    - fondo: `bg-otaku-title-anime`
  - `AnimeTitleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeTitleContext`, `AdminDataView`
    - ruta: `panel:anime-title_data` → `/panel/anime-title/data/`, `panel:anime-title_data-by` → `/panel/anime-title/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`)
    - fondo: `bg-otaku-title-anime`
  - `AnimeTitleDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeTitle`, `BaseDelete`
    - depende de: vuelve a `panel:anime-title_list`; al guardar va a `panel:anime-title_list`
    - ruta: `panel:anime-title_delete` → `/panel/anime-title/<int:pk>/delete/`
    - fondo: `bg-otaku-title-anime`
  - `AnimeTitleDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseAnimeTitle`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:anime-title_list`; plantilla `otaku/detail/anime_title.html`
    - ruta: `panel:anime-title_detail` → `/panel/anime-title/<int:pk>/`
    - fondo: `bg-otaku-title-anime`
  - `AnimeTitleListByView` (panel) — lista «por» (acotada a un padre) — anime.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseAnimeTitleContext`, `AdminListByView`
    - depende de: datos de `panel:anime-title_data-by`
    - ruta: `panel:anime-title_by` → `/panel/anime-title/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `anime`)
    - fondo: `bg-otaku-title-anime`
  - `AnimeTitleListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseAnimeTitle`, `AdminListView`
    - depende de: datos de `panel:anime-title_data`
    - ruta: `panel:anime-title_list` → `/panel/anime-title/`
    - fondo: `bg-otaku-title-anime`
  - `AnimeTitleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseAnimeTitle`, `BaseSelectView`
    - ruta: `panel:anime-title_select` → `/panel/anime-title/select/`
    - fondo: `bg-otaku-title-anime`
  - `AnimeTitleUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseAnimeTitle`, `BaseUpdate`
    - depende de: formulario `AnimeTitleForm`; vuelve a `panel:anime-title_list`; al guardar va a `panel:anime-title_list`; plantilla `otaku/form/anime_title.html`
    - ruta: `panel:anime-title_update` → `/panel/anime-title/<int:pk>/update/`
    - fondo: `bg-otaku-title-anime`

### Modelo: `Character` (`apps/otaku/models.py`)

- Formulario: `CharacterForm` (`apps/otaku/forms.py`) — campos: `full_name`, `name_kanji`, `birthday`, `biography`, `is_active`
- Vistas:
  - `CharacterCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacter`, `BaseCreate`
    - depende de: formulario `CharacterForm`; vuelve a `panel:character_list`; al guardar va a `panel:character_list`; plantilla `otaku/form/character.html`
    - ruta: `panel:character_create` → `/panel/character/create/`
    - fondo: `bg-otaku-character`
  - `CharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterContext`, `AdminDataView`
    - ruta: `panel:character_data` → `/panel/character/data/`, `panel:character_data-by` → `/panel/character/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `otaku.Anime`); `manga` → padre por id (campo `otaku.Manga`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-character`
  - `CharacterDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:character_list`; al guardar va a `panel:character_list`
    - ruta: `panel:character_delete` → `/panel/character/<int:pk>/delete/`
    - fondo: `bg-otaku-character`
  - `CharacterDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:character_list`; plantilla `otaku/detail/character.html`
    - ruta: `panel:character_detail` → `/panel/character/<int:pk>/`
    - fondo: `bg-otaku-character`
  - `CharacterListByView` (panel) — lista «por» (acotada a un padre) — anime, manga, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseCharacterContext`, `AdminListByView`
    - depende de: datos de `panel:character_data-by`
    - ruta: `panel:character_by` → `/panel/character/<str:tipo>/<str:pk>/`
    - mapa «by»: `anime` → padre por id (campo `otaku.Anime`); `manga` → padre por id (campo `otaku.Manga`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-character`
  - `CharacterListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseCharacter`, `AdminListView`
    - depende de: datos de `panel:character_data`
    - ruta: `panel:character_list` → `/panel/character/`
    - fondo: `bg-otaku-character`
  - `CharacterPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterContext`, `PublicDataView`
    - ruta: `otaku:personajes-catalogo-data` → `/catalog/otaku/characters/list/data/`, `otaku:personajes-por-data` → `/catalog/otaku/characters/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `anime` → padre por id (campo `otaku.Anime`); `manga` → padre por id (campo `otaku.Manga`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-character`
  - `CharacterPublicDetailView` (pública) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseCharacter`, `BasePublicDetailView`
    - depende de: vuelve a `otaku:personajes-catalogo`; plantilla `otaku/detail/character.html`
    - ruta: `otaku:personaje` → `/catalog/otaku/character/<int:pk>/<slug:slug>/`, `otaku:personaje` → `/catalog/otaku/character/<int:pk>/`
    - fondo: `bg-otaku-character`
  - `CharacterPublicListByView` (pública) — lista «por» (acotada a un padre) — anime, manga, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseCharacterContext`, `PublicListByView`
    - depende de: datos de `otaku:personajes-por-data`; plantilla `public/list.html`
    - ruta: `otaku:personajes-por` → `/catalog/otaku/characters/<str:tipo>/<int:pk>/`, `otaku:personajes-por` → `/catalog/otaku/characters/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `anime` → padre por id (campo `otaku.Anime`); `manga` → padre por id (campo `otaku.Manga`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-character`
  - `CharacterPublicListView` (pública) — lista — Catálogo público de PERSONAJES de anime y manga (estilo MAL).
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseCharacter`, `PublicListView`
    - depende de: datos de `otaku:personajes-catalogo-data`; plantilla `public/list.html`
    - ruta: `otaku:personajes-catalogo` → `/catalog/otaku/characters/list/`
    - fondo: `bg-otaku-character`
  - `CharacterSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacter`, `BaseSelectView`
    - ruta: `panel:character_select` → `/panel/character/select/`
    - fondo: `bg-otaku-character`
  - `CharacterUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacter`, `BaseUpdate`
    - depende de: formulario `CharacterForm`; vuelve a `panel:character_list`; al guardar va a `panel:character_list`; plantilla `otaku/form/character.html`
    - ruta: `panel:character_update` → `/panel/character/<int:pk>/update/`
    - fondo: `bg-otaku-character`
- Filtros:
  - `AnimeCharacterFilters`: Rol (`anime_appearances__role`) — para `CharacterDataView`
  - `CharacterFilters`: — — para `CharacterPublicDataView`

### Modelo: `CharacterImage` (`apps/otaku/models.py`)

- Formulario: `CharacterImageForm` (`apps/otaku/forms.py`) — campos: `character`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `CharacterImageCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterImage`, `BaseCreate`
    - depende de: formulario `CharacterImageForm`; vuelve a `panel:character-image_list`; al guardar va a `panel:character-image_list`; plantilla `otaku/form/character_image.html`
    - ruta: `panel:character-image_create` → `/panel/character-image/create/`
    - fondo: `bg-otaku-character-image`
  - `CharacterImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterImageContext`, `AdminDataView`
    - ruta: `panel:character-image_data` → `/panel/character-image/data/`, `panel:character-image_data-by` → `/panel/character-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-character-image`
  - `CharacterImageDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterImage`, `BaseDelete`
    - depende de: vuelve a `panel:character-image_list`; al guardar va a `panel:character-image_list`
    - ruta: `panel:character-image_delete` → `/panel/character-image/<int:pk>/delete/`
    - fondo: `bg-otaku-character-image`
  - `CharacterImageDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseCharacterImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:character-image_list`; plantilla `otaku/detail/character_image.html`
    - ruta: `panel:character-image_detail` → `/panel/character-image/<int:pk>/`
    - fondo: `bg-otaku-character-image`
  - `CharacterImageListByView` (panel) — lista «por» (acotada a un padre) — personaje.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseCharacterImageContext`, `AdminListByView`
    - depende de: datos de `panel:character-image_data-by`
    - ruta: `panel:character-image_by` → `/panel/character-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-character-image`
  - `CharacterImageListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseCharacterImage`, `AdminListView`
    - depende de: datos de `panel:character-image_data`
    - ruta: `panel:character-image_list` → `/panel/character-image/`
    - fondo: `bg-otaku-character-image`
  - `CharacterImagePublicListByView` (pública) — lista «por» (acotada a un padre) — personaje.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseCharacterImageContext`, `PublicListByView`
    - depende de: datos de `otaku:personaje-imagenes-por-data`; plantilla `public/list.html`
    - ruta: `otaku:personaje-imagenes-por` → `/catalog/otaku/character/images/<str:tipo>/<int:pk>/`, `otaku:personaje-imagenes-por` → `/catalog/otaku/character/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-character`
  - `CharacterImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterImage`, `BaseSelectView`
    - ruta: `panel:character-image_select` → `/panel/character-image/select/`
    - fondo: `bg-otaku-character-image`
  - `CharacterImageUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterImage`, `BaseUpdate`
    - depende de: formulario `CharacterImageForm`; vuelve a `panel:character-image_list`; al guardar va a `panel:character-image_list`; plantilla `otaku/form/character_image.html`
    - ruta: `panel:character-image_update` → `/panel/character-image/<int:pk>/update/`
    - fondo: `bg-otaku-character-image`
  - `CharacterImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de un personaje: sus imágenes en tarjetas.
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterImageContext`, `PublicDataView`
    - ruta: `otaku:personaje-imagenes-por-data` → `/catalog/otaku/character/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-character-image`

### Modelo: `CharacterNickname` (`apps/otaku/models.py`)

- Formulario: `CharacterNicknameForm` (`apps/otaku/forms.py`) — campos: `character`, `nickname`, `is_active`
- Vistas:
  - `CharacterNicknameCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterNickname`, `BaseCreate`
    - depende de: formulario `CharacterNicknameForm`; vuelve a `panel:character-nickname_list`; al guardar va a `panel:character-nickname_list`; plantilla `otaku/form/character_nickname.html`
    - ruta: `panel:character-nickname_create` → `/panel/character-nickname/create/`
    - fondo: `bg-otaku-character-nickname`
  - `CharacterNicknameDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterNicknameContext`, `AdminDataView`
    - ruta: `panel:character-nickname_data` → `/panel/character-nickname/data/`, `panel:character-nickname_data-by` → `/panel/character-nickname/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-character-nickname`
  - `CharacterNicknameDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterNickname`, `BaseDelete`
    - depende de: vuelve a `panel:character-nickname_list`; al guardar va a `panel:character-nickname_list`
    - ruta: `panel:character-nickname_delete` → `/panel/character-nickname/<int:pk>/delete/`
    - fondo: `bg-otaku-character-nickname`
  - `CharacterNicknameDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseCharacterNickname`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:character-nickname_list`; plantilla `otaku/detail/character_nickname.html`
    - ruta: `panel:character-nickname_detail` → `/panel/character-nickname/<int:pk>/`
    - fondo: `bg-otaku-character-nickname`
  - `CharacterNicknameListByView` (panel) — lista «por» (acotada a un padre) — personaje.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseCharacterNicknameContext`, `AdminListByView`
    - depende de: datos de `panel:character-nickname_data-by`
    - ruta: `panel:character-nickname_by` → `/panel/character-nickname/<str:tipo>/<str:pk>/`
    - mapa «by»: `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-character-nickname`
  - `CharacterNicknameListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseCharacterNickname`, `AdminListView`
    - depende de: datos de `panel:character-nickname_data`
    - ruta: `panel:character-nickname_list` → `/panel/character-nickname/`
    - fondo: `bg-otaku-character-nickname`
  - `CharacterNicknameSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterNickname`, `BaseSelectView`
    - ruta: `panel:character-nickname_select` → `/panel/character-nickname/select/`
    - fondo: `bg-otaku-character-nickname`
  - `CharacterNicknameUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterNickname`, `BaseUpdate`
    - depende de: formulario `CharacterNicknameForm`; vuelve a `panel:character-nickname_list`; al guardar va a `panel:character-nickname_list`; plantilla `otaku/form/character_nickname.html`
    - ruta: `panel:character-nickname_update` → `/panel/character-nickname/<int:pk>/update/`
    - fondo: `bg-otaku-character-nickname`

### Modelo: `CharacterVoice` (`apps/otaku/models.py`)

- Formulario: `CharacterVoiceForm` (`apps/otaku/forms.py`) — campos: `person`, `character`, `language`, `is_active`
- Vistas:
  - `CharacterVoiceCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterVoice`, `BaseCreate`
    - depende de: formulario `CharacterVoiceForm`; vuelve a `panel:character-voice_list`; al guardar va a `panel:character-voice_list`; plantilla `otaku/form/character_voice.html`
    - ruta: `panel:character-voice_create` → `/panel/character-voice/create/`
    - fondo: `bg-otaku-voice-character`
  - `CharacterVoiceDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterVoiceContext`, `AdminDataView`
    - ruta: `panel:character-voice_data` → `/panel/character-voice/data/`, `panel:character-voice_data-by` → `/panel/character-voice/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`); `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-voice-character`
  - `CharacterVoiceDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterVoice`, `BaseDelete`
    - depende de: vuelve a `panel:character-voice_list`; al guardar va a `panel:character-voice_list`
    - ruta: `panel:character-voice_delete` → `/panel/character-voice/<int:pk>/delete/`
    - fondo: `bg-otaku-voice-character`
  - `CharacterVoiceDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseCharacterVoice`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:character-voice_list`; plantilla `otaku/detail/character_voice.html`
    - ruta: `panel:character-voice_detail` → `/panel/character-voice/<int:pk>/`
    - fondo: `bg-otaku-voice-character`
  - `CharacterVoiceListByView` (panel) — lista «por» (acotada a un padre) — persona, personaje.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseCharacterVoiceContext`, `AdminListByView`
    - depende de: datos de `panel:character-voice_data-by`
    - ruta: `panel:character-voice_by` → `/panel/character-voice/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`); `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-voice-character`
  - `CharacterVoiceListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseCharacterVoice`, `AdminListView`
    - depende de: datos de `panel:character-voice_data`
    - ruta: `panel:character-voice_list` → `/panel/character-voice/`
    - fondo: `bg-otaku-voice-character`
  - `CharacterVoiceSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseCharacterVoice`, `BaseSelectView`
    - ruta: `panel:character-voice_select` → `/panel/character-voice/select/`
    - fondo: `bg-otaku-voice-character`
  - `CharacterVoiceUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseCharacterVoice`, `BaseUpdate`
    - depende de: formulario `CharacterVoiceForm`; vuelve a `panel:character-voice_list`; al guardar va a `panel:character-voice_list`; plantilla `otaku/form/character_voice.html`
    - ruta: `panel:character-voice_update` → `/panel/character-voice/<int:pk>/update/`
    - fondo: `bg-otaku-voice-character`

### Modelo: `DataMalAnime` (`apps/otaku/models.py`)

- Formulario: `DataMalAnimeForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalAnimeCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnime`, `BaseCreate`
    - depende de: formulario `DataMalAnimeForm`; vuelve a `panel:data-mal-anime_list`; al guardar va a `panel:data-mal-anime_list`
    - ruta: `panel:data-mal-anime_create` → `/panel/data-mal-anime/create/`
    - fondo: `bg-otaku-data-mal-anime`
  - `DataMalAnimeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalAnime`, `AdminDataView`
    - ruta: `panel:data-mal-anime_data` → `/panel/data-mal-anime/data/`
    - fondo: `bg-otaku-data-mal-anime`
  - `DataMalAnimeDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnime`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-anime_list`; al guardar va a `panel:data-mal-anime_list`
    - ruta: `panel:data-mal-anime_delete` → `/panel/data-mal-anime/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-anime`
  - `DataMalAnimeDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalAnime`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-anime_list`; plantilla `otaku/detail/data_mal_anime.html`
    - ruta: `panel:data-mal-anime_detail` → `/panel/data-mal-anime/<int:pk>/`
    - fondo: `bg-otaku-data-mal-anime`
  - `DataMalAnimeListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalAnime`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-anime_data`
    - ruta: `panel:data-mal-anime_list` → `/panel/data-mal-anime/`
    - fondo: `bg-otaku-data-mal-anime`
  - `DataMalAnimeUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnime`, `BaseUpdate`
    - depende de: formulario `DataMalAnimeForm`; vuelve a `panel:data-mal-anime_list`; al guardar va a `panel:data-mal-anime_list`
    - ruta: `panel:data-mal-anime_update` → `/panel/data-mal-anime/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-anime`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalAnimeDataView`

### Modelo: `DataMalAnimeCharacter` (`apps/otaku/models.py`)

- Formulario: `DataMalAnimeCharacterForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalAnimeCharacterCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimeCharacter`, `BaseCreate`
    - depende de: formulario `DataMalAnimeCharacterForm`; vuelve a `panel:data-mal-anime-character_list`; al guardar va a `panel:data-mal-anime-character_list`
    - ruta: `panel:data-mal-anime-character_create` → `/panel/data-mal-anime-character/create/`
    - fondo: `bg-otaku-data-mal-anime-character`
  - `DataMalAnimeCharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalAnimeCharacter`, `AdminDataView`
    - ruta: `panel:data-mal-anime-character_data` → `/panel/data-mal-anime-character/data/`
    - fondo: `bg-otaku-data-mal-anime-character`
  - `DataMalAnimeCharacterDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimeCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-anime-character_list`; al guardar va a `panel:data-mal-anime-character_list`
    - ruta: `panel:data-mal-anime-character_delete` → `/panel/data-mal-anime-character/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-anime-character`
  - `DataMalAnimeCharacterDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalAnimeCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-anime-character_list`; plantilla `otaku/detail/data_mal_anime_character.html`
    - ruta: `panel:data-mal-anime-character_detail` → `/panel/data-mal-anime-character/<int:pk>/`
    - fondo: `bg-otaku-data-mal-anime-character`
  - `DataMalAnimeCharacterListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalAnimeCharacter`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-anime-character_data`
    - ruta: `panel:data-mal-anime-character_list` → `/panel/data-mal-anime-character/`
    - fondo: `bg-otaku-data-mal-anime-character`
  - `DataMalAnimeCharacterUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimeCharacter`, `BaseUpdate`
    - depende de: formulario `DataMalAnimeCharacterForm`; vuelve a `panel:data-mal-anime-character_list`; al guardar va a `panel:data-mal-anime-character_list`
    - ruta: `panel:data-mal-anime-character_update` → `/panel/data-mal-anime-character/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-anime-character`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalAnimeCharacterDataView`

### Modelo: `DataMalAnimePicture` (`apps/otaku/models.py`)

- Formulario: `DataMalAnimePictureForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalAnimePictureCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimePicture`, `BaseCreate`
    - depende de: formulario `DataMalAnimePictureForm`; vuelve a `panel:data-mal-anime-picture_list`; al guardar va a `panel:data-mal-anime-picture_list`
    - ruta: `panel:data-mal-anime-picture_create` → `/panel/data-mal-anime-picture/create/`
    - fondo: `bg-otaku-data-mal-anime-picture`
  - `DataMalAnimePictureDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalAnimePicture`, `AdminDataView`
    - ruta: `panel:data-mal-anime-picture_data` → `/panel/data-mal-anime-picture/data/`
    - fondo: `bg-otaku-data-mal-anime-picture`
  - `DataMalAnimePictureDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimePicture`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-anime-picture_list`; al guardar va a `panel:data-mal-anime-picture_list`
    - ruta: `panel:data-mal-anime-picture_delete` → `/panel/data-mal-anime-picture/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-anime-picture`
  - `DataMalAnimePictureDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalAnimePicture`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-anime-picture_list`; plantilla `otaku/detail/data_mal_anime_picture.html`
    - ruta: `panel:data-mal-anime-picture_detail` → `/panel/data-mal-anime-picture/<int:pk>/`
    - fondo: `bg-otaku-data-mal-anime-picture`
  - `DataMalAnimePictureListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalAnimePicture`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-anime-picture_data`
    - ruta: `panel:data-mal-anime-picture_list` → `/panel/data-mal-anime-picture/`
    - fondo: `bg-otaku-data-mal-anime-picture`
  - `DataMalAnimePictureUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimePicture`, `BaseUpdate`
    - depende de: formulario `DataMalAnimePictureForm`; vuelve a `panel:data-mal-anime-picture_list`; al guardar va a `panel:data-mal-anime-picture_list`
    - ruta: `panel:data-mal-anime-picture_update` → `/panel/data-mal-anime-picture/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-anime-picture`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalAnimePictureDataView`

### Modelo: `DataMalAnimeStaff` (`apps/otaku/models.py`)

- Formulario: `DataMalAnimeStaffForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalAnimeStaffCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimeStaff`, `BaseCreate`
    - depende de: formulario `DataMalAnimeStaffForm`; vuelve a `panel:data-mal-anime-staff_list`; al guardar va a `panel:data-mal-anime-staff_list`
    - ruta: `panel:data-mal-anime-staff_create` → `/panel/data-mal-anime-staff/create/`
    - fondo: `bg-otaku-data-mal-anime-staff`
  - `DataMalAnimeStaffDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalAnimeStaff`, `AdminDataView`
    - ruta: `panel:data-mal-anime-staff_data` → `/panel/data-mal-anime-staff/data/`
    - fondo: `bg-otaku-data-mal-anime-staff`
  - `DataMalAnimeStaffDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimeStaff`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-anime-staff_list`; al guardar va a `panel:data-mal-anime-staff_list`
    - ruta: `panel:data-mal-anime-staff_delete` → `/panel/data-mal-anime-staff/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-anime-staff`
  - `DataMalAnimeStaffDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalAnimeStaff`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-anime-staff_list`; plantilla `otaku/detail/data_mal_anime_staff.html`
    - ruta: `panel:data-mal-anime-staff_detail` → `/panel/data-mal-anime-staff/<int:pk>/`
    - fondo: `bg-otaku-data-mal-anime-staff`
  - `DataMalAnimeStaffListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalAnimeStaff`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-anime-staff_data`
    - ruta: `panel:data-mal-anime-staff_list` → `/panel/data-mal-anime-staff/`
    - fondo: `bg-otaku-data-mal-anime-staff`
  - `DataMalAnimeStaffUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalAnimeStaff`, `BaseUpdate`
    - depende de: formulario `DataMalAnimeStaffForm`; vuelve a `panel:data-mal-anime-staff_list`; al guardar va a `panel:data-mal-anime-staff_list`
    - ruta: `panel:data-mal-anime-staff_update` → `/panel/data-mal-anime-staff/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-anime-staff`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalAnimeStaffDataView`

### Modelo: `DataMalCharacter` (`apps/otaku/models.py`)

- Formulario: `DataMalCharacterForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalCharacterCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalCharacter`, `BaseCreate`
    - depende de: formulario `DataMalCharacterForm`; vuelve a `panel:data-mal-character_list`; al guardar va a `panel:data-mal-character_list`
    - ruta: `panel:data-mal-character_create` → `/panel/data-mal-character/create/`
    - fondo: `bg-otaku-data-mal-character`
  - `DataMalCharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalCharacter`, `AdminDataView`
    - ruta: `panel:data-mal-character_data` → `/panel/data-mal-character/data/`
    - fondo: `bg-otaku-data-mal-character`
  - `DataMalCharacterDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-character_list`; al guardar va a `panel:data-mal-character_list`
    - ruta: `panel:data-mal-character_delete` → `/panel/data-mal-character/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-character`
  - `DataMalCharacterDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-character_list`; plantilla `otaku/detail/data_mal_character.html`
    - ruta: `panel:data-mal-character_detail` → `/panel/data-mal-character/<int:pk>/`
    - fondo: `bg-otaku-data-mal-character`
  - `DataMalCharacterListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalCharacter`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-character_data`
    - ruta: `panel:data-mal-character_list` → `/panel/data-mal-character/`
    - fondo: `bg-otaku-data-mal-character`
  - `DataMalCharacterUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalCharacter`, `BaseUpdate`
    - depende de: formulario `DataMalCharacterForm`; vuelve a `panel:data-mal-character_list`; al guardar va a `panel:data-mal-character_list`
    - ruta: `panel:data-mal-character_update` → `/panel/data-mal-character/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-character`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalCharacterDataView`

### Modelo: `DataMalCharacterPicture` (`apps/otaku/models.py`)

- Formulario: `DataMalCharacterPictureForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalCharacterPictureCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalCharacterPicture`, `BaseCreate`
    - depende de: formulario `DataMalCharacterPictureForm`; vuelve a `panel:data-mal-character-picture_list`; al guardar va a `panel:data-mal-character-picture_list`
    - ruta: `panel:data-mal-character-picture_create` → `/panel/data-mal-character-picture/create/`
    - fondo: `bg-otaku-data-mal-character-picture`
  - `DataMalCharacterPictureDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalCharacterPicture`, `AdminDataView`
    - ruta: `panel:data-mal-character-picture_data` → `/panel/data-mal-character-picture/data/`
    - fondo: `bg-otaku-data-mal-character-picture`
  - `DataMalCharacterPictureDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalCharacterPicture`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-character-picture_list`; al guardar va a `panel:data-mal-character-picture_list`
    - ruta: `panel:data-mal-character-picture_delete` → `/panel/data-mal-character-picture/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-character-picture`
  - `DataMalCharacterPictureDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalCharacterPicture`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-character-picture_list`; plantilla `otaku/detail/data_mal_character_picture.html`
    - ruta: `panel:data-mal-character-picture_detail` → `/panel/data-mal-character-picture/<int:pk>/`
    - fondo: `bg-otaku-data-mal-character-picture`
  - `DataMalCharacterPictureListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalCharacterPicture`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-character-picture_data`
    - ruta: `panel:data-mal-character-picture_list` → `/panel/data-mal-character-picture/`
    - fondo: `bg-otaku-data-mal-character-picture`
  - `DataMalCharacterPictureUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalCharacterPicture`, `BaseUpdate`
    - depende de: formulario `DataMalCharacterPictureForm`; vuelve a `panel:data-mal-character-picture_list`; al guardar va a `panel:data-mal-character-picture_list`
    - ruta: `panel:data-mal-character-picture_update` → `/panel/data-mal-character-picture/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-character-picture`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalCharacterPictureDataView`


### Modelo: `DataMalManga` (`apps/otaku/models.py`)

- Formulario: `DataMalMangaForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalMangaCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalManga`, `BaseCreate`
    - depende de: formulario `DataMalMangaForm`; vuelve a `panel:data-mal-manga_list`; al guardar va a `panel:data-mal-manga_list`
    - ruta: `panel:data-mal-manga_create` → `/panel/data-mal-manga/create/`
    - fondo: `bg-otaku-data-mal-manga`
  - `DataMalMangaDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalManga`, `AdminDataView`
    - ruta: `panel:data-mal-manga_data` → `/panel/data-mal-manga/data/`
    - fondo: `bg-otaku-data-mal-manga`
  - `DataMalMangaDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalManga`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-manga_list`; al guardar va a `panel:data-mal-manga_list`
    - ruta: `panel:data-mal-manga_delete` → `/panel/data-mal-manga/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-manga`
  - `DataMalMangaDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalManga`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-manga_list`; plantilla `otaku/detail/data_mal_manga.html`
    - ruta: `panel:data-mal-manga_detail` → `/panel/data-mal-manga/<int:pk>/`
    - fondo: `bg-otaku-data-mal-manga`
  - `DataMalMangaListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalManga`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-manga_data`
    - ruta: `panel:data-mal-manga_list` → `/panel/data-mal-manga/`
    - fondo: `bg-otaku-data-mal-manga`
  - `DataMalMangaUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalManga`, `BaseUpdate`
    - depende de: formulario `DataMalMangaForm`; vuelve a `panel:data-mal-manga_list`; al guardar va a `panel:data-mal-manga_list`
    - ruta: `panel:data-mal-manga_update` → `/panel/data-mal-manga/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-manga`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalMangaDataView`

### Modelo: `DataMalMangaCharacter` (`apps/otaku/models.py`)

- Formulario: `DataMalMangaCharacterForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalMangaCharacterCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalMangaCharacter`, `BaseCreate`
    - depende de: formulario `DataMalMangaCharacterForm`; vuelve a `panel:data-mal-manga-character_list`; al guardar va a `panel:data-mal-manga-character_list`
    - ruta: `panel:data-mal-manga-character_create` → `/panel/data-mal-manga-character/create/`
    - fondo: `bg-otaku-data-mal-manga-character`
  - `DataMalMangaCharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalMangaCharacter`, `AdminDataView`
    - ruta: `panel:data-mal-manga-character_data` → `/panel/data-mal-manga-character/data/`
    - fondo: `bg-otaku-data-mal-manga-character`
  - `DataMalMangaCharacterDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalMangaCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-manga-character_list`; al guardar va a `panel:data-mal-manga-character_list`
    - ruta: `panel:data-mal-manga-character_delete` → `/panel/data-mal-manga-character/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-manga-character`
  - `DataMalMangaCharacterDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalMangaCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-manga-character_list`; plantilla `otaku/detail/data_mal_manga_character.html`
    - ruta: `panel:data-mal-manga-character_detail` → `/panel/data-mal-manga-character/<int:pk>/`
    - fondo: `bg-otaku-data-mal-manga-character`
  - `DataMalMangaCharacterListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalMangaCharacter`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-manga-character_data`
    - ruta: `panel:data-mal-manga-character_list` → `/panel/data-mal-manga-character/`
    - fondo: `bg-otaku-data-mal-manga-character`
  - `DataMalMangaCharacterUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalMangaCharacter`, `BaseUpdate`
    - depende de: formulario `DataMalMangaCharacterForm`; vuelve a `panel:data-mal-manga-character_list`; al guardar va a `panel:data-mal-manga-character_list`
    - ruta: `panel:data-mal-manga-character_update` → `/panel/data-mal-manga-character/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-manga-character`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalMangaCharacterDataView`

### Modelo: `DataMalMangaPicture` (`apps/otaku/models.py`)

- Formulario: `DataMalMangaPictureForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalMangaPictureCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalMangaPicture`, `BaseCreate`
    - depende de: formulario `DataMalMangaPictureForm`; vuelve a `panel:data-mal-manga-picture_list`; al guardar va a `panel:data-mal-manga-picture_list`
    - ruta: `panel:data-mal-manga-picture_create` → `/panel/data-mal-manga-picture/create/`
    - fondo: `bg-otaku-data-mal-manga-picture`
  - `DataMalMangaPictureDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalMangaPicture`, `AdminDataView`
    - ruta: `panel:data-mal-manga-picture_data` → `/panel/data-mal-manga-picture/data/`
    - fondo: `bg-otaku-data-mal-manga-picture`
  - `DataMalMangaPictureDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalMangaPicture`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-manga-picture_list`; al guardar va a `panel:data-mal-manga-picture_list`
    - ruta: `panel:data-mal-manga-picture_delete` → `/panel/data-mal-manga-picture/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-manga-picture`
  - `DataMalMangaPictureDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalMangaPicture`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-manga-picture_list`; plantilla `otaku/detail/data_mal_manga_picture.html`
    - ruta: `panel:data-mal-manga-picture_detail` → `/panel/data-mal-manga-picture/<int:pk>/`
    - fondo: `bg-otaku-data-mal-manga-picture`
  - `DataMalMangaPictureListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalMangaPicture`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-manga-picture_data`
    - ruta: `panel:data-mal-manga-picture_list` → `/panel/data-mal-manga-picture/`
    - fondo: `bg-otaku-data-mal-manga-picture`
  - `DataMalMangaPictureUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalMangaPicture`, `BaseUpdate`
    - depende de: formulario `DataMalMangaPictureForm`; vuelve a `panel:data-mal-manga-picture_list`; al guardar va a `panel:data-mal-manga-picture_list`
    - ruta: `panel:data-mal-manga-picture_update` → `/panel/data-mal-manga-picture/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-manga-picture`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalMangaPictureDataView`

### Modelo: `DataMalPerson` (`apps/otaku/models.py`)

- Formulario: `DataMalPersonForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalPersonCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalPerson`, `BaseCreate`
    - depende de: formulario `DataMalPersonForm`; vuelve a `panel:data-mal-person_list`; al guardar va a `panel:data-mal-person_list`
    - ruta: `panel:data-mal-person_create` → `/panel/data-mal-person/create/`
    - fondo: `bg-otaku-data-mal-person`
  - `DataMalPersonDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalPerson`, `AdminDataView`
    - ruta: `panel:data-mal-person_data` → `/panel/data-mal-person/data/`
    - fondo: `bg-otaku-data-mal-person`
  - `DataMalPersonDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalPerson`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-person_list`; al guardar va a `panel:data-mal-person_list`
    - ruta: `panel:data-mal-person_delete` → `/panel/data-mal-person/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-person`
  - `DataMalPersonDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalPerson`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-person_list`; plantilla `otaku/detail/data_mal_person.html`
    - ruta: `panel:data-mal-person_detail` → `/panel/data-mal-person/<int:pk>/`
    - fondo: `bg-otaku-data-mal-person`
  - `DataMalPersonListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalPerson`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-person_data`
    - ruta: `panel:data-mal-person_list` → `/panel/data-mal-person/`
    - fondo: `bg-otaku-data-mal-person`
  - `DataMalPersonUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalPerson`, `BaseUpdate`
    - depende de: formulario `DataMalPersonForm`; vuelve a `panel:data-mal-person_list`; al guardar va a `panel:data-mal-person_list`
    - ruta: `panel:data-mal-person_update` → `/panel/data-mal-person/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-person`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalPersonDataView`

### Modelo: `DataMalPersonPicture` (`apps/otaku/models.py`)

- Formulario: `DataMalPersonPictureForm` (`apps/otaku/forms.py`) — campos: `mal_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataMalPersonPictureCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalPersonPicture`, `BaseCreate`
    - depende de: formulario `DataMalPersonPictureForm`; vuelve a `panel:data-mal-person-picture_list`; al guardar va a `panel:data-mal-person-picture_list`
    - ruta: `panel:data-mal-person-picture_create` → `/panel/data-mal-person-picture/create/`
    - fondo: `bg-otaku-data-mal-person-picture`
  - `DataMalPersonPictureDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDataMalPersonPicture`, `AdminDataView`
    - ruta: `panel:data-mal-person-picture_data` → `/panel/data-mal-person-picture/data/`
    - fondo: `bg-otaku-data-mal-person-picture`
  - `DataMalPersonPictureDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalPersonPicture`, `BaseDelete`
    - depende de: vuelve a `panel:data-mal-person-picture_list`; al guardar va a `panel:data-mal-person-picture_list`
    - ruta: `panel:data-mal-person-picture_delete` → `/panel/data-mal-person-picture/<int:pk>/delete/`
    - fondo: `bg-otaku-data-mal-person-picture`
  - `DataMalPersonPictureDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDataMalPersonPicture`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-mal-person-picture_list`; plantilla `otaku/detail/data_mal_person_picture.html`
    - ruta: `panel:data-mal-person-picture_detail` → `/panel/data-mal-person-picture/<int:pk>/`
    - fondo: `bg-otaku-data-mal-person-picture`
  - `DataMalPersonPictureListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDataMalPersonPicture`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-mal-person-picture_data`
    - ruta: `panel:data-mal-person-picture_list` → `/panel/data-mal-person-picture/`
    - fondo: `bg-otaku-data-mal-person-picture`
  - `DataMalPersonPictureUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDataMalPersonPicture`, `BaseUpdate`
    - depende de: formulario `DataMalPersonPictureForm`; vuelve a `panel:data-mal-person-picture_list`; al guardar va a `panel:data-mal-person-picture_list`
    - ruta: `panel:data-mal-person-picture_update` → `/panel/data-mal-person-picture/<int:pk>/update/`
    - fondo: `bg-otaku-data-mal-person-picture`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataMalPersonPictureDataView`

### Modelo: `Demographic` (`apps/otaku/models.py`)

- Formulario: `DemographicForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `DemographicCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDemographic`, `BaseCreate`
    - depende de: formulario `DemographicForm`; vuelve a `panel:demographic_list`; al guardar va a `panel:demographic_list`; plantilla `otaku/form/demographic.html`
    - ruta: `panel:demographic_create` → `/panel/demographic/create/`
    - fondo: `bg-otaku-demographic`
  - `DemographicDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDemographic`, `AdminDataView`
    - ruta: `panel:demographic_data` → `/panel/demographic/data/`
    - fondo: `bg-otaku-demographic`
  - `DemographicDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDemographic`, `BaseDelete`
    - depende de: vuelve a `panel:demographic_list`; al guardar va a `panel:demographic_list`
    - ruta: `panel:demographic_delete` → `/panel/demographic/<int:pk>/delete/`
    - fondo: `bg-otaku-demographic`
  - `DemographicDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDemographic`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:demographic_list`; plantilla `otaku/detail/demographic.html`
    - ruta: `panel:demographic_detail` → `/panel/demographic/<int:pk>/`
    - fondo: `bg-otaku-demographic`
  - `DemographicListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDemographic`, `AdminListView`
    - depende de: datos de `panel:demographic_data`
    - ruta: `panel:demographic_list` → `/panel/demographic/`
    - fondo: `bg-otaku-demographic`
  - `DemographicSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDemographic`, `BaseSelectView`
    - ruta: `panel:demographic_select` → `/panel/demographic/select/`
    - fondo: `bg-otaku-demographic`
  - `DemographicUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDemographic`, `BaseUpdate`
    - depende de: formulario `DemographicForm`; vuelve a `panel:demographic_list`; al guardar va a `panel:demographic_list`; plantilla `otaku/form/demographic.html`
    - ruta: `panel:demographic_update` → `/panel/demographic/<int:pk>/update/`
    - fondo: `bg-otaku-demographic`

### Modelo: `DemographicAlias` (`apps/otaku/models.py`)

- Formulario: `DemographicAliasForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `is_active`, `demographic`
- Vistas:
  - `DemographicAliasCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDemographicAlias`, `BaseCreate`
    - depende de: formulario `DemographicAliasForm`; vuelve a `panel:demographic-alias_list`; al guardar va a `panel:demographic-alias_list`
    - ruta: `panel:demographic-alias_create` → `/panel/demographic-alias/create/`
    - fondo: `bg-otaku-demographic`
  - `DemographicAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseDemographicAliasContext`, `AdminDataView`
    - ruta: `panel:demographic-alias_data` → `/panel/demographic-alias/data/`, `panel:demographic-alias_data-by` → `/panel/demographic-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `demographic` → padre por id (campo `demographic`)
    - fondo: `bg-otaku-demographic`
  - `DemographicAliasDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDemographicAlias`, `BaseDelete`
    - depende de: vuelve a `panel:demographic-alias_list`; al guardar va a `panel:demographic-alias_list`
    - ruta: `panel:demographic-alias_delete` → `/panel/demographic-alias/<int:pk>/delete/`
    - fondo: `bg-otaku-demographic`
  - `DemographicAliasDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseDemographicAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:demographic-alias_list`
    - ruta: `panel:demographic-alias_detail` → `/panel/demographic-alias/<int:pk>/`
    - fondo: `bg-otaku-demographic`
  - `DemographicAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/demographic-alias/demographic/<id>/`): los alimenta DemographicAliasDataView con `/data/demographic/<id>/`.
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDemographicAliasContext`, `AdminListByView`
    - depende de: datos de `panel:demographic-alias_data-by`
    - ruta: `panel:demographic-alias_by` → `/panel/demographic-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `demographic` → padre por id (campo `demographic`)
    - fondo: `bg-otaku-demographic`
  - `DemographicAliasListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseDemographicAlias`, `AdminListView`
    - depende de: datos de `panel:demographic-alias_data`
    - ruta: `panel:demographic-alias_list` → `/panel/demographic-alias/`
    - fondo: `bg-otaku-demographic`
  - `DemographicAliasUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseDemographicAlias`, `BaseUpdate`
    - depende de: formulario `DemographicAliasForm`; vuelve a `panel:demographic-alias_list`; al guardar va a `panel:demographic-alias_list`
    - ruta: `panel:demographic-alias_update` → `/panel/demographic-alias/<int:pk>/update/`
    - fondo: `bg-otaku-demographic`

### Modelo: `Genre` (`apps/otaku/models.py`)

- Formulario: `GenreForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `description`, `explicit`, `image`, `is_active`
- Vistas:
  - `GenreCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseGenre`, `BaseCreate`
    - depende de: formulario `GenreForm`; vuelve a `panel:genre_list`; al guardar va a `panel:genre_list`; plantilla `otaku/form/genre.html`
    - ruta: `panel:genre_create` → `/panel/genre/create/`
    - fondo: `bg-otaku-genre`
  - `GenreDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseGenre`, `AdminDataView`
    - ruta: `panel:genre_data` → `/panel/genre/data/`
    - fondo: `bg-otaku-genre`
  - `GenreDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseGenre`, `BaseDelete`
    - depende de: vuelve a `panel:genre_list`; al guardar va a `panel:genre_list`
    - ruta: `panel:genre_delete` → `/panel/genre/<int:pk>/delete/`
    - fondo: `bg-otaku-genre`
  - `GenreDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseGenre`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:genre_list`; plantilla `otaku/detail/genre.html`
    - ruta: `panel:genre_detail` → `/panel/genre/<int:pk>/`
    - fondo: `bg-otaku-genre`
  - `GenreListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseGenre`, `AdminListView`
    - depende de: datos de `panel:genre_data`
    - ruta: `panel:genre_list` → `/panel/genre/`
    - fondo: `bg-otaku-genre`
  - `GenreSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseGenre`, `BaseSelectView`
    - ruta: `panel:genre_select` → `/panel/genre/select/`
    - fondo: `bg-otaku-genre`
  - `GenreUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseGenre`, `BaseUpdate`
    - depende de: formulario `GenreForm`; vuelve a `panel:genre_list`; al guardar va a `panel:genre_list`; plantilla `otaku/form/genre.html`
    - ruta: `panel:genre_update` → `/panel/genre/<int:pk>/update/`
    - fondo: `bg-otaku-genre`

### Modelo: `GenreAlias` (`apps/otaku/models.py`)

- Formulario: `GenreAliasForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `is_active`, `genre`
- Vistas:
  - `GenreAliasCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseCreate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:genre-alias_list`; al guardar va a `panel:genre-alias_list`
    - ruta: `panel:genre-alias_create` → `/panel/genre-alias/create/`
    - fondo: `bg-otaku-genre`
  - `GenreAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseGenreAliasContext`, `AdminDataView`
    - ruta: `panel:genre-alias_data` → `/panel/genre-alias/data/`, `panel:genre-alias_data-by` → `/panel/genre-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-otaku-genre`
  - `GenreAliasDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseDelete`
    - depende de: vuelve a `panel:genre-alias_list`; al guardar va a `panel:genre-alias_list`
    - ruta: `panel:genre-alias_delete` → `/panel/genre-alias/<int:pk>/delete/`
    - fondo: `bg-otaku-genre`
  - `GenreAliasDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseGenreAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:genre-alias_list`
    - ruta: `panel:genre-alias_detail` → `/panel/genre-alias/<int:pk>/`
    - fondo: `bg-otaku-genre`
  - `GenreAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`.
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseGenreAliasContext`, `AdminListByView`
    - depende de: datos de `panel:genre-alias_data-by`
    - ruta: `panel:genre-alias_by` → `/panel/genre-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-otaku-genre`
  - `GenreAliasListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseGenreAlias`, `AdminListView`
    - depende de: datos de `panel:genre-alias_data`
    - ruta: `panel:genre-alias_list` → `/panel/genre-alias/`
    - fondo: `bg-otaku-genre`
  - `GenreAliasUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseUpdate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:genre-alias_list`; al guardar va a `panel:genre-alias_list`
    - ruta: `panel:genre-alias_update` → `/panel/genre-alias/<int:pk>/update/`
    - fondo: `bg-otaku-genre`


### Modelo: `Manga` (`apps/otaku/models.py`)

- Formulario: `MangaForm` (`apps/otaku/forms.py`) — campos: `title`, `title_eng`, `title_jap`, `synopsis`, `manga_type`, `source`, `rating`, `status`, `season`, `year`, `chapters`, `volumes`, `serializations`, `genres`, `themes`, `demographics`, `from_date`, `to_date`, `is_active`
- Vistas:
  - `MangaCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseManga`, `BaseCreate`
    - depende de: formulario `MangaForm`; vuelve a `panel:manga_list`; al guardar va a `panel:manga_list`; plantilla `otaku/form/manga.html`
    - ruta: `panel:manga_create` → `/panel/manga/create/`
    - fondo: `bg-otaku-manga`
  - `MangaDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaContext`, `AdminDataView`
    - ruta: `panel:manga_data` → `/panel/manga/data/`, `panel:manga_data-by` → `/panel/manga/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `revista` → padre por id (campo `serializations`); `tipo` → padre por id (campo `manga_type`); `estado` → padre por id (campo `status`); `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-manga`
  - `MangaDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseManga`, `BaseDelete`
    - depende de: vuelve a `panel:manga_list`; al guardar va a `panel:manga_list`
    - ruta: `panel:manga_delete` → `/panel/manga/<int:pk>/delete/`
    - fondo: `bg-otaku-manga`
  - `MangaDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseManga`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:manga_list`; plantilla `otaku/detail/manga.html`
    - ruta: `panel:manga_detail` → `/panel/manga/<int:pk>/`
    - fondo: `bg-otaku-manga`
  - `MangaListByView` (panel) — lista «por» (acotada a un padre) — genero, tema, demografia, revista, tipo, estado, fuente, clasificacion, personaje, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseMangaContext`, `AdminListByView`
    - depende de: datos de `panel:manga_data-by`
    - ruta: `panel:manga_by` → `/panel/manga/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `revista` → padre por id (campo `serializations`); `tipo` → padre por id (campo `manga_type`); `estado` → padre por id (campo `status`); `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-manga`
  - `MangaListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseManga`, `AdminListView`
    - depende de: datos de `panel:manga_data`
    - ruta: `panel:manga_list` → `/panel/manga/`
    - fondo: `bg-otaku-manga`
  - `MangaPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaContext`, `PublicDataView`
    - ruta: `otaku:manga-catalogo-data` → `/catalog/otaku/manga/list/data/`, `otaku:manga-por-data` → `/catalog/otaku/manga/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `revista` → padre por id (campo `serializations`); `tipo` → padre por id (campo `manga_type`); `estado` → padre por id (campo `status`); `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-manga`
  - `MangaPublicDetailView` (pública) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseManga`, `BasePublicDetailView`
    - depende de: vuelve a `otaku:manga-catalogo`; plantilla `otaku/detail/manga.html`
    - ruta: `otaku:detalle-manga` → `/catalog/otaku/manga/<int:pk>/<slug:slug>/`, `otaku:detalle-manga` → `/catalog/otaku/manga/<int:pk>/`
    - fondo: `bg-otaku-manga`
  - `MangaPublicListByView` (pública) — lista «por» (acotada a un padre) — genero, tema, demografia, revista, tipo, estado, fuente, clasificacion, personaje, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseMangaContext`, `PublicListByView`
    - depende de: datos de `otaku:manga-por-data`; plantilla `public/list.html`
    - ruta: `otaku:manga-por` → `/catalog/otaku/manga/<str:tipo>/<int:pk>/`, `otaku:manga-por` → `/catalog/otaku/manga/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tema` → padre por id (campo `themes`); `demografia` → padre por id (campo `demographics`); `revista` → padre por id (campo `serializations`); `tipo` → padre por id (campo `manga_type`); `estado` → padre por id (campo `status`); `fuente` → padre por id (campo `source`); `rating` → choice: `g`, `pg`, `pg13`, `r17`, `rplus`, `rx`, `unknown`; `season` → choice: `winter`, `spring`, `summer`, `fall`, `unknown`; `personaje` → padre por id (campo `otaku.Character`); `persona` → padre por id (campo `people.Person`)
    - fondo: `bg-otaku-manga`
  - `MangaPublicListView` (pública) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseManga`, `PublicListView`
    - depende de: datos de `otaku:manga-catalogo-data`; plantilla `public/list.html`
    - ruta: `otaku:manga-catalogo` → `/catalog/otaku/manga/list/`
    - fondo: `bg-otaku-manga`
  - `MangaSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseManga`, `BaseSelectView`
    - ruta: `panel:manga_select` → `/panel/manga/select/`
    - fondo: `bg-otaku-manga`
  - `MangaUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseManga`, `BaseUpdate`
    - depende de: formulario `MangaForm`; vuelve a `panel:manga_list`; al guardar va a `panel:manga_list`; plantilla `otaku/form/manga.html`
    - ruta: `panel:manga_update` → `/panel/manga/<int:pk>/update/`
    - fondo: `bg-otaku-manga`
- Filtros:
  - `MangaFilters`: Género (`genres`), Tipo (`manga_type`), Estado (`status`), Demografía (`demographics`), Revista (`serializations`), Clasificación (`rating`), Temporada (`season`), Año (`year`) — para `MangaDataView`, `MangaPublicDataView`

### Modelo: `MangaAuthor` (`apps/otaku/models.py`)

- Formulario: `MangaAuthorForm` (`apps/otaku/forms.py`) — campos: `manga`, `person`, `role`, `is_active`
- Vistas:
  - `MangaAuthorCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaAuthor`, `BaseCreate`
    - depende de: formulario `MangaAuthorForm`; vuelve a `panel:manga-author_list`; al guardar va a `panel:manga-author_list`; plantilla `otaku/form/manga_author.html`
    - ruta: `panel:manga-author_create` → `/panel/manga-author/create/`
    - fondo: `bg-otaku-author-manga`
  - `MangaAuthorDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaAuthorContext`, `AdminDataView`
    - ruta: `panel:manga-author_data` → `/panel/manga-author/data/`, `panel:manga-author_data-by` → `/panel/manga-author/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`); `persona` → padre por id (campo `person`)
    - fondo: `bg-otaku-author-manga`
  - `MangaAuthorDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaAuthor`, `BaseDelete`
    - depende de: vuelve a `panel:manga-author_list`; al guardar va a `panel:manga-author_list`
    - ruta: `panel:manga-author_delete` → `/panel/manga-author/<int:pk>/delete/`
    - fondo: `bg-otaku-author-manga`
  - `MangaAuthorDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseMangaAuthor`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:manga-author_list`; plantilla `otaku/detail/manga_author.html`
    - ruta: `panel:manga-author_detail` → `/panel/manga-author/<int:pk>/`
    - fondo: `bg-otaku-author-manga`
  - `MangaAuthorListByView` (panel) — lista «por» (acotada a un padre) — manga, persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseMangaAuthorContext`, `AdminListByView`
    - depende de: datos de `panel:manga-author_data-by`
    - ruta: `panel:manga-author_by` → `/panel/manga-author/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`); `persona` → padre por id (campo `person`)
    - fondo: `bg-otaku-author-manga`
  - `MangaAuthorListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseMangaAuthor`, `AdminListView`
    - depende de: datos de `panel:manga-author_data`
    - ruta: `panel:manga-author_list` → `/panel/manga-author/`
    - fondo: `bg-otaku-author-manga`
  - `MangaAuthorSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaAuthor`, `BaseSelectView`
    - ruta: `panel:manga-author_select` → `/panel/manga-author/select/`
    - fondo: `bg-otaku-author-manga`
  - `MangaAuthorUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaAuthor`, `BaseUpdate`
    - depende de: formulario `MangaAuthorForm`; vuelve a `panel:manga-author_list`; al guardar va a `panel:manga-author_list`; plantilla `otaku/form/manga_author.html`
    - ruta: `panel:manga-author_update` → `/panel/manga-author/<int:pk>/update/`
    - fondo: `bg-otaku-author-manga`

### Modelo: `MangaCharacter` (`apps/otaku/models.py`)

- Formulario: `MangaCharacterForm` (`apps/otaku/forms.py`) — campos: `manga`, `character`, `role`, `is_active`
- Vistas:
  - `MangaCharacterCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaCharacter`, `BaseCreate`
    - depende de: formulario `MangaCharacterForm`; vuelve a `panel:manga-character_list`; al guardar va a `panel:manga-character_list`; plantilla `otaku/form/manga_character.html`
    - ruta: `panel:manga-character_create` → `/panel/manga-character/create/`
    - fondo: `bg-otaku-manga-character`
  - `MangaCharacterDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaCharacterContext`, `AdminDataView`
    - ruta: `panel:manga-character_data` → `/panel/manga-character/data/`, `panel:manga-character_data-by` → `/panel/manga-character/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`); `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-manga-character`
  - `MangaCharacterDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaCharacter`, `BaseDelete`
    - depende de: vuelve a `panel:manga-character_list`; al guardar va a `panel:manga-character_list`
    - ruta: `panel:manga-character_delete` → `/panel/manga-character/<int:pk>/delete/`
    - fondo: `bg-otaku-manga-character`
  - `MangaCharacterDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseMangaCharacter`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:manga-character_list`; plantilla `otaku/detail/manga_character.html`
    - ruta: `panel:manga-character_detail` → `/panel/manga-character/<int:pk>/`
    - fondo: `bg-otaku-manga-character`
  - `MangaCharacterListByView` (panel) — lista «por» (acotada a un padre) — manga, personaje.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseMangaCharacterContext`, `AdminListByView`
    - depende de: datos de `panel:manga-character_data-by`
    - ruta: `panel:manga-character_by` → `/panel/manga-character/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`); `personaje` → padre por id (campo `character`)
    - fondo: `bg-otaku-manga-character`
  - `MangaCharacterListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseMangaCharacter`, `AdminListView`
    - depende de: datos de `panel:manga-character_data`
    - ruta: `panel:manga-character_list` → `/panel/manga-character/`
    - fondo: `bg-otaku-manga-character`
  - `MangaCharacterSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaCharacter`, `BaseSelectView`
    - ruta: `panel:manga-character_select` → `/panel/manga-character/select/`
    - fondo: `bg-otaku-manga-character`
  - `MangaCharacterUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaCharacter`, `BaseUpdate`
    - depende de: formulario `MangaCharacterForm`; vuelve a `panel:manga-character_list`; al guardar va a `panel:manga-character_list`; plantilla `otaku/form/manga_character.html`
    - ruta: `panel:manga-character_update` → `/panel/manga-character/<int:pk>/update/`
    - fondo: `bg-otaku-manga-character`

### Modelo: `MangaImage` (`apps/otaku/models.py`)

- Formulario: `MangaImageForm` (`apps/otaku/forms.py`) — campos: `manga`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `MangaImageCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaImage`, `BaseCreate`
    - depende de: formulario `MangaImageForm`; vuelve a `panel:manga-image_list`; al guardar va a `panel:manga-image_list`; plantilla `otaku/form/manga_image.html`
    - ruta: `panel:manga-image_create` → `/panel/manga-image/create/`
    - fondo: `bg-otaku-manga-image`
  - `MangaImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaImageContext`, `AdminDataView`
    - ruta: `panel:manga-image_data` → `/panel/manga-image/data/`, `panel:manga-image_data-by` → `/panel/manga-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`)
    - fondo: `bg-otaku-manga-image`
  - `MangaImageDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaImage`, `BaseDelete`
    - depende de: vuelve a `panel:manga-image_list`; al guardar va a `panel:manga-image_list`
    - ruta: `panel:manga-image_delete` → `/panel/manga-image/<int:pk>/delete/`
    - fondo: `bg-otaku-manga-image`
  - `MangaImageDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseMangaImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:manga-image_list`; plantilla `otaku/detail/manga_image.html`
    - ruta: `panel:manga-image_detail` → `/panel/manga-image/<int:pk>/`
    - fondo: `bg-otaku-manga-image`
  - `MangaImageListByView` (panel) — lista «por» (acotada a un padre) — manga.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseMangaImageContext`, `AdminListByView`
    - depende de: datos de `panel:manga-image_data-by`
    - ruta: `panel:manga-image_by` → `/panel/manga-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`)
    - fondo: `bg-otaku-manga-image`
  - `MangaImageListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseMangaImage`, `AdminListView`
    - depende de: datos de `panel:manga-image_data`
    - ruta: `panel:manga-image_list` → `/panel/manga-image/`
    - fondo: `bg-otaku-manga-image`
  - `MangaImagePublicListByView` (pública) — lista «por» (acotada a un padre) — manga.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseMangaImageContext`, `PublicListByView`
    - depende de: datos de `otaku:manga-imagenes-por-data`; plantilla `public/list.html`
    - ruta: `otaku:manga-imagenes-por` → `/catalog/otaku/manga/images/<str:tipo>/<int:pk>/`, `otaku:manga-imagenes-por` → `/catalog/otaku/manga/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `manga` → padre por id (campo `manga`)
    - fondo: `bg-otaku-manga-image`
  - `MangaImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaImage`, `BaseSelectView`
    - ruta: `panel:manga-image_select` → `/panel/manga-image/select/`
    - fondo: `bg-otaku-manga-image`
  - `MangaImageUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaImage`, `BaseUpdate`
    - depende de: formulario `MangaImageForm`; vuelve a `panel:manga-image_list`; al guardar va a `panel:manga-image_list`; plantilla `otaku/form/manga_image.html`
    - ruta: `panel:manga-image_update` → `/panel/manga-image/<int:pk>/update/`
    - fondo: `bg-otaku-manga-image`
  - `MangaImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de un manga: sus imágenes en tarjetas.
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaImageContext`, `PublicDataView`
    - ruta: `otaku:manga-imagenes-por-data` → `/catalog/otaku/manga/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `manga` → padre por id (campo `manga`)
    - fondo: `bg-otaku-manga-image`

### Modelo: `MangaTitle` (`apps/otaku/models.py`)

- Formulario: `MangaTitleForm` (`apps/otaku/forms.py`) — campos: `manga`, `title_lang`, `title`, `is_active`
- Vistas:
  - `MangaTitleCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaTitle`, `BaseCreate`
    - depende de: formulario `MangaTitleForm`; vuelve a `panel:manga-title_list`; al guardar va a `panel:manga-title_list`; plantilla `otaku/form/manga_title.html`
    - ruta: `panel:manga-title_create` → `/panel/manga-title/create/`
    - fondo: `bg-otaku-title-manga`
  - `MangaTitleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaTitleContext`, `AdminDataView`
    - ruta: `panel:manga-title_data` → `/panel/manga-title/data/`, `panel:manga-title_data-by` → `/panel/manga-title/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`)
    - fondo: `bg-otaku-title-manga`
  - `MangaTitleDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaTitle`, `BaseDelete`
    - depende de: vuelve a `panel:manga-title_list`; al guardar va a `panel:manga-title_list`
    - ruta: `panel:manga-title_delete` → `/panel/manga-title/<int:pk>/delete/`
    - fondo: `bg-otaku-title-manga`
  - `MangaTitleDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseMangaTitle`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:manga-title_list`; plantilla `otaku/detail/manga_title.html`
    - ruta: `panel:manga-title_detail` → `/panel/manga-title/<int:pk>/`
    - fondo: `bg-otaku-title-manga`
  - `MangaTitleListByView` (panel) — lista «por» (acotada a un padre) — manga.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BaseMangaTitleContext`, `AdminListByView`
    - depende de: datos de `panel:manga-title_data-by`
    - ruta: `panel:manga-title_by` → `/panel/manga-title/<str:tipo>/<str:pk>/`
    - mapa «by»: `manga` → padre por id (campo `manga`)
    - fondo: `bg-otaku-title-manga`
  - `MangaTitleListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseMangaTitle`, `AdminListView`
    - depende de: datos de `panel:manga-title_data`
    - ruta: `panel:manga-title_list` → `/panel/manga-title/`
    - fondo: `bg-otaku-title-manga`
  - `MangaTitleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseMangaTitle`, `BaseSelectView`
    - ruta: `panel:manga-title_select` → `/panel/manga-title/select/`
    - fondo: `bg-otaku-title-manga`
  - `MangaTitleUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseMangaTitle`, `BaseUpdate`
    - depende de: formulario `MangaTitleForm`; vuelve a `panel:manga-title_list`; al guardar va a `panel:manga-title_list`; plantilla `otaku/form/manga_title.html`
    - ruta: `panel:manga-title_update` → `/panel/manga-title/<int:pk>/update/`
    - fondo: `bg-otaku-title-manga`

### Modelo: `OtakuLog` (`apps/otaku/models.py`)

- Formulario: `OtakuLogForm` (`apps/otaku/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `OtakuLogCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseOtakuLog`, `BaseCreate`
    - depende de: formulario `OtakuLogForm`; vuelve a `panel:otaku-log_list`; al guardar va a `panel:otaku-log_list`
    - ruta: `panel:otaku-log_create` → `/panel/otaku-log/create/`
    - fondo: `bg-otaku-otaku-log`
  - `OtakuLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseOtakuLog`, `AdminDataView`
    - ruta: `panel:otaku-log_data` → `/panel/otaku-log/data/`
    - fondo: `bg-otaku-otaku-log`
  - `OtakuLogDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseOtakuLog`, `BaseDelete`
    - depende de: vuelve a `panel:otaku-log_list`; al guardar va a `panel:otaku-log_list`
    - ruta: `panel:otaku-log_delete` → `/panel/otaku-log/<int:pk>/delete/`
    - fondo: `bg-otaku-otaku-log`
  - `OtakuLogDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseOtakuLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:otaku-log_list`; plantilla `otaku/detail/otaku_log.html`
    - ruta: `panel:otaku-log_detail` → `/panel/otaku-log/<int:pk>/`
    - fondo: `bg-otaku-otaku-log`
  - `OtakuLogListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseOtakuLog`, `AdminListView`
    - depende de: datos de `panel:otaku-log_data`
    - ruta: `panel:otaku-log_list` → `/panel/otaku-log/`
    - fondo: `bg-otaku-otaku-log`
  - `OtakuLogUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseOtakuLog`, `BaseUpdate`
    - depende de: formulario `OtakuLogForm`; vuelve a `panel:otaku-log_list`; al guardar va a `panel:otaku-log_list`
    - ruta: `panel:otaku-log_update` → `/panel/otaku-log/<int:pk>/update/`
    - fondo: `bg-otaku-otaku-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `OtakuLogDataView`

### Modelo: `PersonMAL` (`apps/otaku/models.py`)

- Formulario: `PersonMALNewForm` (`apps/otaku/forms.py`) — campos: `person`, `mal_id`, `given_name`, `family_name`, `alternate_names`, `favorites`, `website_url`, `about`, `is_active`
- Vistas:
  - `PersonMALCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BasePersonMAL`, `BaseCreate`
    - depende de: formulario `PersonMALNewForm`; vuelve a `panel:person-mal_list`; al guardar va a `panel:person-mal_list`; plantilla `otaku/form/person_mal.html`
    - ruta: `panel:person-mal_create` → `/panel/person-mal/create/`
    - fondo: `bg-otaku-person`
  - `PersonMALDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BasePersonMALContext`, `AdminDataView`
    - ruta: `panel:person-mal_data` → `/panel/person-mal/data/`, `panel:person-mal_data-by` → `/panel/person-mal/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-otaku-person`
  - `PersonMALDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BasePersonMAL`, `BaseDelete`
    - depende de: vuelve a `panel:person-mal_list`; al guardar va a `panel:person-mal_list`
    - ruta: `panel:person-mal_delete` → `/panel/person-mal/<int:pk>/delete/`
    - fondo: `bg-otaku-person`
  - `PersonMALDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BasePersonMAL`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:person-mal_list`; plantilla `otaku/detail/person_mal.html`
    - ruta: `panel:person-mal_detail` → `/panel/person-mal/<int:pk>/`
    - fondo: `bg-otaku-person`
  - `PersonMALListByView` (panel) — lista «por» (acotada a un padre) — persona.
    - archivo: `apps/otaku/views/v5_list_by.py` · hereda de `BasePersonMALContext`, `AdminListByView`
    - depende de: datos de `panel:person-mal_data-by`
    - ruta: `panel:person-mal_by` → `/panel/person-mal/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-otaku-person`
  - `PersonMALListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BasePersonMAL`, `AdminListView`
    - depende de: datos de `panel:person-mal_data`
    - ruta: `panel:person-mal_list` → `/panel/person-mal/`
    - fondo: `bg-otaku-person`
  - `PersonMALSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BasePersonMAL`, `BaseSelectView`
    - ruta: `panel:person-mal_select` → `/panel/person-mal/select/`
    - fondo: `bg-otaku-person`
  - `PersonMALUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BasePersonMAL`, `BaseUpdate`
    - depende de: formulario `PersonMALNewForm`; vuelve a `panel:person-mal_list`; al guardar va a `panel:person-mal_list`; plantilla `otaku/form/person_mal.html`
    - ruta: `panel:person-mal_update` → `/panel/person-mal/<int:pk>/update/`
    - fondo: `bg-otaku-person`


### Modelo: `Relation` (`apps/otaku/models.py`)

- Formulario: `RelationForm` (`apps/otaku/forms.py`) — campos: `relation_type`, `from_type`, `from_mal_id`, `to_type`, `to_mal_id`, `is_active`
- Vistas:
  - `RelationAnimeAnimeDataView` (panel) — datos JSON de la lista fija: from_type='anime', to_type='anime'
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `RelationDataView`
    - ruta: `panel:relation-anime-anime_data` → `/panel/relation-anime-anime/data/`
    - fondo: `bg-otaku-relation`
  - `RelationAnimeAnimeListView` (panel) — lista fija: from_type='anime', to_type='anime'
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseRelation`, `AdminListView`
    - depende de: datos de `panel:relation-anime-anime_data`
    - ruta: `panel:relation-anime-anime_list` → `/panel/relation-anime-anime/`
    - fondo: `bg-otaku-relation-anime-anime`
  - `RelationAnimeMangaDataView` (panel) — datos JSON de la lista fija: from_type='anime', to_type='manga'
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `RelationDataView`
    - ruta: `panel:relation-anime-manga_data` → `/panel/relation-anime-manga/data/`
    - fondo: `bg-otaku-relation`
  - `RelationAnimeMangaListView` (panel) — lista fija: from_type='anime', to_type='manga'
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseRelation`, `AdminListView`
    - depende de: datos de `panel:relation-anime-manga_data`
    - ruta: `panel:relation-anime-manga_list` → `/panel/relation-anime-manga/`
    - fondo: `bg-otaku-relation-anime-manga`
  - `RelationCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseRelation`, `BaseCreate`
    - depende de: formulario `RelationForm`; vuelve a `panel:relation_list`; al guardar va a `panel:relation_list`; plantilla `otaku/form/relation.html`
    - ruta: `panel:relation_create` → `/panel/relation/create/`
    - fondo: `bg-otaku-relation`
  - `RelationDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseRelation`, `AdminDataView`
    - ruta: `panel:relation_data` → `/panel/relation/data/`
    - fondo: `bg-otaku-relation`
  - `RelationDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseRelation`, `BaseDelete`
    - depende de: vuelve a `panel:relation_list`; al guardar va a `panel:relation_list`
    - ruta: `panel:relation_delete` → `/panel/relation/<int:pk>/delete/`
    - fondo: `bg-otaku-relation`
  - `RelationDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseRelation`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:relation_list`; plantilla `otaku/detail/relation.html`
    - ruta: `panel:relation_detail` → `/panel/relation/<int:pk>/`
    - fondo: `bg-otaku-relation`
  - `RelationListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseRelation`, `AdminListView`
    - depende de: datos de `panel:relation_data`
    - ruta: `panel:relation_list` → `/panel/relation/`
    - fondo: `bg-otaku-relation`
  - `RelationMangaAnimeDataView` (panel) — datos JSON de la lista fija: from_type='manga', to_type='anime'
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `RelationDataView`
    - ruta: `panel:relation-manga-anime_data` → `/panel/relation-manga-anime/data/`
    - fondo: `bg-otaku-relation`
  - `RelationMangaAnimeListView` (panel) — lista fija: from_type='manga', to_type='anime'
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseRelation`, `AdminListView`
    - depende de: datos de `panel:relation-manga-anime_data`
    - ruta: `panel:relation-manga-anime_list` → `/panel/relation-manga-anime/`
    - fondo: `bg-otaku-relation-manga-anime`
  - `RelationMangaMangaDataView` (panel) — datos JSON de la lista fija: from_type='manga', to_type='manga'
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `RelationDataView`
    - ruta: `panel:relation-manga-manga_data` → `/panel/relation-manga-manga/data/`
    - fondo: `bg-otaku-relation`
  - `RelationMangaMangaListView` (panel) — lista fija: from_type='manga', to_type='manga'
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseRelation`, `AdminListView`
    - depende de: datos de `panel:relation-manga-manga_data`
    - ruta: `panel:relation-manga-manga_list` → `/panel/relation-manga-manga/`
    - fondo: `bg-otaku-relation-manga-manga`
  - `RelationSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseRelation`, `BaseSelectView`
    - ruta: `panel:relation_select` → `/panel/relation/select/`
    - fondo: `bg-otaku-relation`
  - `RelationUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseRelation`, `BaseUpdate`
    - depende de: formulario `RelationForm`; vuelve a `panel:relation_list`; al guardar va a `panel:relation_list`; plantilla `otaku/form/relation.html`
    - ruta: `panel:relation_update` → `/panel/relation/<int:pk>/update/`
    - fondo: `bg-otaku-relation`

### Modelo: `Role` (`apps/otaku/models.py`)

- Formulario: `RoleForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `type`, `description`, `image`, `is_active`
- Vistas:
  - `RoleCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseRole`, `BaseCreate`
    - depende de: formulario `RoleForm`; vuelve a `panel:otaku-role_list`; al guardar va a `panel:otaku-role_list`; plantilla `otaku/form/role.html`
    - ruta: `panel:otaku-role_create` → `/panel/otaku-role/create/`
    - fondo: `bg-otaku-role`
  - `RoleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseRoleContext`, `AdminDataView`
    - ruta: `panel:otaku-role_data` → `/panel/otaku-role/data/`, `panel:otaku-role_data-by` → `/panel/otaku-role/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `character`, `manga`, `unknown`
    - fondo: `bg-otaku-role`
  - `RoleDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseRole`, `BaseDelete`
    - depende de: vuelve a `panel:otaku-role_list`; al guardar va a `panel:otaku-role_list`
    - ruta: `panel:otaku-role_delete` → `/panel/otaku-role/<int:pk>/delete/`
    - fondo: `bg-otaku-role`
  - `RoleDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseRole`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:otaku-role_list`; plantilla `otaku/detail/role.html`
    - ruta: `panel:otaku-role_detail` → `/panel/otaku-role/<int:pk>/`
    - fondo: `bg-otaku-role`
  - `RoleListByView` (panel) — lista «por» (acotada a un padre) — Lista de roles acotada por familia (`/otaku-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`.
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseRoleContext`, `AdminListByView`
    - depende de: datos de `panel:otaku-role_data-by`
    - ruta: `panel:otaku-role_by` → `/panel/otaku-role/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `character`, `manga`, `unknown`
    - fondo: `bg-otaku-role`
  - `RoleListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseRole`, `AdminListView`
    - depende de: datos de `panel:otaku-role_data`
    - ruta: `panel:otaku-role_list` → `/panel/otaku-role/`
    - fondo: `bg-otaku-role`
  - `RoleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseRole`, `BaseSelectView`
    - ruta: `panel:otaku-role_select` → `/panel/otaku-role/select/`
    - fondo: `bg-otaku-role`
  - `RoleUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseRole`, `BaseUpdate`
    - depende de: formulario `RoleForm`; vuelve a `panel:otaku-role_list`; al guardar va a `panel:otaku-role_list`; plantilla `otaku/form/role.html`
    - ruta: `panel:otaku-role_update` → `/panel/otaku-role/<int:pk>/update/`
    - fondo: `bg-otaku-role`
- Filtros:
  - `RoleFilters`: Tipo de rol (`type`), Activo (`is_active`) — para `RoleDataView`


### Modelo: `Source` (`apps/otaku/models.py`)

- Formulario: `SourceForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `SourceCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseSource`, `BaseCreate`
    - depende de: formulario `SourceForm`; vuelve a `panel:source_list`; al guardar va a `panel:source_list`; plantilla `otaku/form/source.html`
    - ruta: `panel:source_create` → `/panel/source/create/`
    - fondo: `bg-otaku-source`
  - `SourceDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseSource`, `AdminDataView`
    - ruta: `panel:source_data` → `/panel/source/data/`
    - fondo: `bg-otaku-source`
  - `SourceDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseSource`, `BaseDelete`
    - depende de: vuelve a `panel:source_list`; al guardar va a `panel:source_list`
    - ruta: `panel:source_delete` → `/panel/source/<int:pk>/delete/`
    - fondo: `bg-otaku-source`
  - `SourceDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseSource`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:source_list`; plantilla `otaku/detail/source.html`
    - ruta: `panel:source_detail` → `/panel/source/<int:pk>/`
    - fondo: `bg-otaku-source`
  - `SourceListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseSource`, `AdminListView`
    - depende de: datos de `panel:source_data`
    - ruta: `panel:source_list` → `/panel/source/`
    - fondo: `bg-otaku-source`
  - `SourceSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseSource`, `BaseSelectView`
    - ruta: `panel:source_select` → `/panel/source/select/`
    - fondo: `bg-otaku-source`
  - `SourceUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseSource`, `BaseUpdate`
    - depende de: formulario `SourceForm`; vuelve a `panel:source_list`; al guardar va a `panel:source_list`; plantilla `otaku/form/source.html`
    - ruta: `panel:source_update` → `/panel/source/<int:pk>/update/`
    - fondo: `bg-otaku-source`

### Modelo: `Status` (`apps/otaku/models.py`)

- Formulario: `StatusForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `StatusCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseStatus`, `BaseCreate`
    - depende de: formulario `StatusForm`; vuelve a `panel:status_list`; al guardar va a `panel:status_list`; plantilla `otaku/form/status.html`
    - ruta: `panel:status_create` → `/panel/status/create/`
    - fondo: `bg-otaku-status`
  - `StatusDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseStatus`, `AdminDataView`
    - ruta: `panel:status_data` → `/panel/status/data/`
    - fondo: `bg-otaku-status`
  - `StatusDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseStatus`, `BaseDelete`
    - depende de: vuelve a `panel:status_list`; al guardar va a `panel:status_list`
    - ruta: `panel:status_delete` → `/panel/status/<int:pk>/delete/`
    - fondo: `bg-otaku-status`
  - `StatusDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseStatus`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:status_list`; plantilla `otaku/detail/status.html`
    - ruta: `panel:status_detail` → `/panel/status/<int:pk>/`
    - fondo: `bg-otaku-status`
  - `StatusListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseStatus`, `AdminListView`
    - depende de: datos de `panel:status_data`
    - ruta: `panel:status_list` → `/panel/status/`
    - fondo: `bg-otaku-status`
  - `StatusSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseStatus`, `BaseSelectView`
    - ruta: `panel:status_select` → `/panel/status/select/`
    - fondo: `bg-otaku-status`
  - `StatusUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseStatus`, `BaseUpdate`
    - depende de: formulario `StatusForm`; vuelve a `panel:status_list`; al guardar va a `panel:status_list`; plantilla `otaku/form/status.html`
    - ruta: `panel:status_update` → `/panel/status/<int:pk>/update/`
    - fondo: `bg-otaku-status`


### Modelo: `Theme` (`apps/otaku/models.py`)

- Formulario: `ThemeForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `ThemeCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseTheme`, `BaseCreate`
    - depende de: formulario `ThemeForm`; vuelve a `panel:theme_list`; al guardar va a `panel:theme_list`; plantilla `otaku/form/theme.html`
    - ruta: `panel:theme_create` → `/panel/theme/create/`
    - fondo: `bg-otaku-theme`
  - `ThemeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseTheme`, `AdminDataView`
    - ruta: `panel:theme_data` → `/panel/theme/data/`
    - fondo: `bg-otaku-theme`
  - `ThemeDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseTheme`, `BaseDelete`
    - depende de: vuelve a `panel:theme_list`; al guardar va a `panel:theme_list`
    - ruta: `panel:theme_delete` → `/panel/theme/<int:pk>/delete/`
    - fondo: `bg-otaku-theme`
  - `ThemeDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseTheme`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:theme_list`; plantilla `otaku/detail/theme.html`
    - ruta: `panel:theme_detail` → `/panel/theme/<int:pk>/`
    - fondo: `bg-otaku-theme`
  - `ThemeListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseTheme`, `AdminListView`
    - depende de: datos de `panel:theme_data`
    - ruta: `panel:theme_list` → `/panel/theme/`
    - fondo: `bg-otaku-theme`
  - `ThemeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseTheme`, `BaseSelectView`
    - ruta: `panel:theme_select` → `/panel/theme/select/`
    - fondo: `bg-otaku-theme`
  - `ThemeUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseTheme`, `BaseUpdate`
    - depende de: formulario `ThemeForm`; vuelve a `panel:theme_list`; al guardar va a `panel:theme_list`; plantilla `otaku/form/theme.html`
    - ruta: `panel:theme_update` → `/panel/theme/<int:pk>/update/`
    - fondo: `bg-otaku-theme`

### Modelo: `ThemeAlias` (`apps/otaku/models.py`)

- Formulario: `ThemeAliasForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `is_active`, `theme`
- Vistas:
  - `ThemeAliasCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseThemeAlias`, `BaseCreate`
    - depende de: formulario `ThemeAliasForm`; vuelve a `panel:theme-alias_list`; al guardar va a `panel:theme-alias_list`
    - ruta: `panel:theme-alias_create` → `/panel/theme-alias/create/`
    - fondo: `bg-otaku-theme`
  - `ThemeAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseThemeAliasContext`, `AdminDataView`
    - ruta: `panel:theme-alias_data` → `/panel/theme-alias/data/`, `panel:theme-alias_data-by` → `/panel/theme-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `theme` → padre por id (campo `theme`)
    - fondo: `bg-otaku-theme`
  - `ThemeAliasDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseThemeAlias`, `BaseDelete`
    - depende de: vuelve a `panel:theme-alias_list`; al guardar va a `panel:theme-alias_list`
    - ruta: `panel:theme-alias_delete` → `/panel/theme-alias/<int:pk>/delete/`
    - fondo: `bg-otaku-theme`
  - `ThemeAliasDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseThemeAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:theme-alias_list`
    - ruta: `panel:theme-alias_detail` → `/panel/theme-alias/<int:pk>/`
    - fondo: `bg-otaku-theme`
  - `ThemeAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/theme-alias/theme/<id>/`): los alimenta ThemeAliasDataView con `/data/theme/<id>/`.
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseThemeAliasContext`, `AdminListByView`
    - depende de: datos de `panel:theme-alias_data-by`
    - ruta: `panel:theme-alias_by` → `/panel/theme-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `theme` → padre por id (campo `theme`)
    - fondo: `bg-otaku-theme`
  - `ThemeAliasListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseThemeAlias`, `AdminListView`
    - depende de: datos de `panel:theme-alias_data`
    - ruta: `panel:theme-alias_list` → `/panel/theme-alias/`
    - fondo: `bg-otaku-theme`
  - `ThemeAliasUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseThemeAlias`, `BaseUpdate`
    - depende de: formulario `ThemeAliasForm`; vuelve a `panel:theme-alias_list`; al guardar va a `panel:theme-alias_list`
    - ruta: `panel:theme-alias_update` → `/panel/theme-alias/<int:pk>/update/`
    - fondo: `bg-otaku-theme`

### Modelo: `Type` (`apps/otaku/models.py`)

- Formulario: `TypeForm` (`apps/otaku/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `TypeCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseType`, `BaseCreate`
    - depende de: formulario `TypeForm`; vuelve a `panel:type_list`; al guardar va a `panel:type_list`; plantilla `otaku/form/type.html`
    - ruta: `panel:type_create` → `/panel/type/create/`
    - fondo: `bg-otaku-type`
  - `TypeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseType`, `AdminDataView`
    - ruta: `panel:type_data` → `/panel/type/data/`
    - fondo: `bg-otaku-type`
  - `TypeDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseType`, `BaseDelete`
    - depende de: vuelve a `panel:type_list`; al guardar va a `panel:type_list`
    - ruta: `panel:type_delete` → `/panel/type/<int:pk>/delete/`
    - fondo: `bg-otaku-type`
  - `TypeDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseType`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:type_list`; plantilla `otaku/detail/type.html`
    - ruta: `panel:type_detail` → `/panel/type/<int:pk>/`
    - fondo: `bg-otaku-type`
  - `TypeListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseType`, `AdminListView`
    - depende de: datos de `panel:type_data`
    - ruta: `panel:type_list` → `/panel/type/`
    - fondo: `bg-otaku-type`
  - `TypeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseType`, `BaseSelectView`
    - ruta: `panel:type_select` → `/panel/type/select/`
    - fondo: `bg-otaku-type`
  - `TypeUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseType`, `BaseUpdate`
    - depende de: formulario `TypeForm`; vuelve a `panel:type_list`; al guardar va a `panel:type_list`; plantilla `otaku/form/type.html`
    - ruta: `panel:type_update` → `/panel/type/<int:pk>/update/`
    - fondo: `bg-otaku-type`

### Modelo: `Year` (`apps/otaku/models.py`)

- Formulario: `YearForm` (`apps/otaku/forms.py`) — campos: `year`, `is_active`
- Vistas:
  - `YearCreateView` (panel) — alta
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseYear`, `BaseCreate`
    - depende de: formulario `YearForm`; vuelve a `panel:year_list`; al guardar va a `panel:year_list`; plantilla `otaku/form/year.html`
    - ruta: `panel:year_create` → `/panel/year/create/`
    - fondo: `bg-otaku-year`
  - `YearDataView` (panel) — datos JSON de la lista
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseYear`, `AdminDataView`
    - ruta: `panel:year_data` → `/panel/year/data/`
    - fondo: `bg-otaku-year`
  - `YearDeleteView` (panel) — borrado
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseYear`, `BaseDelete`
    - depende de: vuelve a `panel:year_list`; al guardar va a `panel:year_list`
    - ruta: `panel:year_delete` → `/panel/year/<int:pk>/delete/`
    - fondo: `bg-otaku-year`
  - `YearDetailView` (panel) — ficha
    - archivo: `apps/otaku/views/v6_detail.py` · hereda de `BaseYear`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:year_list`; plantilla `otaku/detail/year.html`
    - ruta: `panel:year_detail` → `/panel/year/<int:pk>/`
    - fondo: `bg-otaku-year`
  - `YearListView` (panel) — lista
    - archivo: `apps/otaku/views/v5_list.py` · hereda de `BaseYear`, `AdminListView`
    - depende de: datos de `panel:year_data`
    - ruta: `panel:year_list` → `/panel/year/`
    - fondo: `bg-otaku-year`
  - `YearSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/otaku/views/v3_data.py` · hereda de `BaseYear`, `BaseSelectView`
    - ruta: `panel:year_select` → `/panel/year/select/`
    - fondo: `bg-otaku-year`
  - `YearUpdateView` (panel) — edición
    - archivo: `apps/otaku/views/v4_write.py` · hereda de `BaseYear`, `BaseUpdate`
    - depende de: formulario `YearForm`; vuelve a `panel:year_list`; al guardar va a `panel:year_list`; plantilla `otaku/form/year.html`
    - ruta: `panel:year_update` → `/panel/year/<int:pk>/update/`
    - fondo: `bg-otaku-year`

### Sin modelo

- `MalAnimeImportView`
  - archivo: `apps/otaku/views/v8_import.py` · hereda de `BaseMalTipo`, `TipoImportView` · ruta: `panel:mal-anime` → `/panel/mal/anime/` · fondo `bg-otaku-import-anime`
- `MalCharacterImportView`
  - archivo: `apps/otaku/views/v8_import.py` · hereda de `BaseMalTipo`, `TipoImportView` · ruta: `panel:mal-character` → `/panel/mal/character/` · fondo `bg-otaku-import-personaje`
- `MalMangaImportView`
  - archivo: `apps/otaku/views/v8_import.py` · hereda de `BaseMalTipo`, `TipoImportView` · ruta: `panel:mal-manga` → `/panel/mal/manga/` · fondo `bg-otaku-import-manga`
- `MalPersonImportView`
  - archivo: `apps/otaku/views/v8_import.py` · hereda de `BaseMalTipo`, `TipoImportView` · ruta: `panel:mal-person` → `/panel/mal/person/` · fondo `bg-otaku-import-persona`
- `OtakuHomeView` — Home de Otaku en UNA página con secciones colapsables (Anime, Manga,
  - archivo: `apps/otaku/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:otaku-home` → `/panel/otaku/` · fondo `bg-otaku-home`
- `OtakuPublicHomeView` — Home ÚNICO de la sección Otaku: anime y manga juntos, con su industria
  - archivo: `apps/otaku/views/v1_home.py` · hereda de `BasePublicHomeView` · ruta: `otaku:home` → `/catalog/otaku/` · fondo `bg-otaku-home`
- `AnimeMALLoadView` / `AnimeMALSummaryView` — Cargar dump de ANIMES (MAL): archivo → `DataMalAnime` + `DataMalAnimePicture`, sin procesar
  - archivo: `apps/otaku/views/v8_import.py` · hereda de `BaseDataMalAnime`, `MALDumpLoadView` / `MALDumpSummaryView` · rutas: `panel:dump-mal-anime` → `/panel/mal/dump/anime/` y `panel:dump-mal-anime-summary`
- `MangaMALLoadView` / `MangaMALSummaryView` — Ídem para `DataMalManga` (+ `…Picture`) · `/panel/mal/dump/manga/`
- `CharacterMALLoadView` / `CharacterMALSummaryView` — Ídem para `DataMalCharacter` (+ `…Picture`) · `/panel/mal/dump/character/`
- `PersonMALLoadView` / `PersonMALSummaryView` — Ídem para `DataMalPerson` (+ `…Picture`) · `/panel/mal/dump/person/`
- Form `MALDumpForm` (base) y sus hijos `AnimeMALDumpForm`, `MangaMALDumpForm`, `CharacterMALDumpForm`, `PersonMALDumpForm`
- Servicio `apps/otaku/services/mal_dump.py` — un archivo alimenta DOS tablas: la ficha y sus `images_extra`, con el mismo `mal_id`.
  El JSON se guarda TAL CUAL (claves propias del dump: `person_id`, `character_id`, `mal_id`, `more`, `image_url`…), sin traducir:
  la API de Jikan está muerta y quien traduzca a entidades será un helper del procesado. Ejemplos en `docs/examples/`.
- Form `MalImportarRangoForm`
- Form `MalImportarUnoForm`

## Compañías (`companies`)

App TRANSVERSAL, como `people`: la compañía real y neutra que apuntan cine, TV y otaku. Nació el 2026-09-16 juntando
`movies.Company`, `series.Company` y las cuatro de otaku (`Studio`, `Producer`, `Licensor`, `Serialization`), que eran
la misma tabla escrita seis veces. **El papel no vive en la compañía, vive en la relación** desde el medio: la misma
Disney produce una película, distribuye una serie y licencia un anime.

| Medio | Campo (M2M a `companies.Company`) | `related_name` |
|---|---|---|
| `movies.Movie` | `producers` · `distributors` | `movies_produced` · `movies_distributed` |
| `series.Serie` | `producers` · `distributors` | `series_produced` · `series_distributed` |
| `otaku.Anime` | `studios` · `producers` · `licensors` | `animes_studio` · `animes_produced` · `animes_licensed` |
| `otaku.Manga` | `serializations` | `mangas_serialized` |

`PAPELES` (en `apps/companies/models.py`) enumera esos papeles una sola vez: de ahí salen `Company.obras()`, las filas
del hub público y las pestañas de la ficha. Un papel nuevo se declara ahí.

Los creadores de juegos (`games.Creator`) **no** entran: son personas y estudios a la vez.

### Modelo: `Company` (`apps/companies/models.py`)

Nombre, slug, fundación, disolución, biografía y país. **Nada de ids de un sitio concreto**: igual que `people.Person`,
lo que solo sabe una fuente va en su EXTENSIÓN uno a uno, en la app de esa fuente. El id de MyAnimeList vive en
`otaku.CompanyMAL` (accesor `company.company_mal`); el día que lleguen compañías de Steam, irá en la suya. Así esta
tabla no crece con un `<sitio>_id` por fuente.

- Formulario: `CompanyForm` — valida nombre único por slug y que la disolución no sea anterior a la fundación.
- Panel: `CompanyListView` → `CompanyDataView`, `CompanySelectView` (el selector que usan los formularios de Movie,
  Serie, Anime y Manga), `CompanyCreateView`, `CompanyUpdateView`, `CompanyDeleteView`, `CompanyDetailView`.
  Rutas `panel:company_*` → `/panel/company/…`. Fondo `bg-companies-company`.
- Público: `CompanyPublicListView` → `CompanyPublicDataView` (`companias:companies-catalog`) y
  `CompanyPublicDetailView` (`companias:company-detail` → `/catalog/companies/<id>/<slug>/`).
- La ficha tiene una pestaña por papel, cada una hacia la lista «por» de su medio (`movie_by` productora, `anime_by`
  estudio, `manga_by` revista…), en gestión y en público.
- Seed: `seed_companies`, con las compañías por defecto de cine y TV juntas y sin repetir. Va antes que `seed_movies`.

Los catálogos por papel **se quedan en su medio**, porque son navegación de esa sección: `movies:producers-catalog`,
`series:distributors-catalog`, `otaku:studios-catalog`, `otaku:magazines-catalog`… Filtran `Company` por su
`related_name` y enlazan a la ficha global. Por eso `BaseStudio`, `BaseProducer`, etc. siguen existiendo en
`apps/otaku/views/base.py`, pero con `model = Company`.

### Extensión: `CompanyMAL` (`apps/otaku/models.py`)

La ficha MAL de una compañía: `company` (uno a uno), `mal_id` (único; los dumps lo traen como `company_id`) y `url`. Es la
clave con la que el procesador encuentra la compañía sin duplicarla.

**`CompanyMALNewForm` y `PersonMALNewForm` son el formulario de la entidad neutra MÁS los campos de MAL.** Heredan de
`CompanyForm` / `PersonForm` (así no se copian campos, widgets ni validación, y cada modelo sigue con un solo formulario),
añaden `mal_id`, `url` y, en personas, lo demás que solo sabe MAL. `save()` guarda la entidad con `super().save()` y
después la ficha: `CompanyMAL.objects.update_or_create(company=…)` y, en personas, `upsert_persona_mal` (el mismo camino
que el importador). En edición la vista recibe el id de la FICHA pero abre su entidad (`get_object` devuelve
`ficha.company` / `ficha.person`), y los campos MAL llegan rellenos. `mal_id` es obligatorio en estas pantallas; la
entidad sin MAL se crea desde su propia app. Borrar quita solo la ficha. La `url` y los ids viven en la ficha: la
entidad neutra no los tiene.

**Dos formularios, mismo objetivo** (que la entidad tenga su ficha MAL), según de dónde se parte:

| Formulario | Para | Campos | Ruta |
|---|---|---|---|
| `PersonMALNewForm` / `CompanyMALNewForm` | entidad NUEVA (y editar) | los de la entidad + los MAL | `*-mal_create`, `*-mal_update` |
| `PersonMALExistentForm` / `CompanyMALExistentForm` | entidad EXISTENTE | select de la entidad + los MAL | `*-mal_link` (se elige), `*-mal_add/<pk>` (llega fija) |

Son dos pantallas DISTINTAS, cada una con su vista, su formulario y su HTML propios y planos: cada formulario declara
sus campos MAL y cada plantilla los pinta (se repiten a propósito, sin clases de «solo campos» ni parciales compartidos
entre las dos). Nueva: `person_mal.html` / `company_mal.html`; existente: `person_mal_link.html` / `company_mal_link.html`.
El de enlazar no toca los datos de la entidad y rechaza una que ya tenga ficha. La lista de fichas MAL ofrece los dos:
«Nuevo» y «Enlazar a … existente» (`alta_extra` de `AdminListView`).

**`PersonMAL` solo guarda lo que es de MAL:** `mal_id`, `url`, el nombre en kanji (`given_name` / `family_name`) y `about`.
Lo que MAL trae pero es de la PERSONA va a la persona: `alternate_names` → apodos (`PersonNickname`) y `website_url` →
enlaces (`PersonLink`, fuente «Sitio web»). Los favoritos de MAL no se guardan. Lo reparte `upsert_persona_mal`, que
solo AÑADE (no borra apodos ni enlaces puestos a mano) y no duplica al repetir.

**Nunca se enlaza por nombre a ciegas.** Crear desde «Persona (MAL)» o «Compañía (MAL)» con un nombre que ya existe (sin
mirar mayúsculas ni espacios de más) no guarda nada ni gasta ids: lista las candidatas con sus datos (id, nacimiento o
fundación, país) y, en cada una, «añadirle la ficha MAL» o «ya tiene ficha MAL: editarla». En personas, si de verdad es
otra, se marca «Es otra persona distinta» y se crea (los homónimos se permiten a propósito). En compañías no hay esa
casilla: el nombre es único.

«Añadir ficha MAL» a una entidad que ya existe: `PersonMALLinkView` / `CompanyMALLinkView` (el formulario de enlazar),
con la entidad fija si la URL trae su id; si ya tiene ficha, mandan a editarla. El botón está en la ficha y en el menú de fila de personas y de compañías, y lo resuelve
`apps/otaku/fichas_mal.py` (en la lista, una sola consulta para toda la página). La ficha de gestión admite botones extra
con `acciones_extra(obj)` en `BaseAdminDetailView`.

Vistas:
`CompanyMALListView` → `CompanyMALDataView`, `CompanyMALSelectView`, alta, edición, borrado y ficha. Rutas
`panel:company-mal_*`. Tarjeta en el home de Otaku, junto a «Personas (MAL)».

### Modelo: `CompanyLog` (`apps/companies/models.py`)

El log de la app, como el de las demás. `CompanyLogForm`; `CompanyLogListView` → `CompanyLogDataView`, alta, edición,
borrado y ficha. Rutas `panel:company-log_*`.

### Sin modelo

- `CompaniesHomeView` — home de gestión (`panel:companies-home` → `/panel/companies/`).
- `CompaniesPublicHomeView` — el hub público de la industria de todos los medios (`companias:home` →
  `/catalog/companies/`). Vivía en `catalogs`, que se queda sin parte pública.

## Música (`music`)

### Modelo: `Album` (`apps/music/models.py`)

- Formulario: `AlbumForm` (`apps/music/forms.py`) — campos: `title`, `artist`, `album_type`, `release_date`, `description`, `genres`, `is_active`
- Vistas:
  - `AlbumCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbum`, `BaseCreate`
    - depende de: formulario `AlbumForm`; vuelve a `panel:album_list`; al guardar va a `panel:album_list`; plantilla `music/form/album.html`
    - ruta: `panel:album_create` → `/panel/album/create/`
    - fondo: `bg-music-album`
  - `AlbumDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbumContext`, `AdminDataView`
    - ruta: `panel:album_data` → `/panel/album/data/`, `panel:album_data-by` → `/panel/album/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `album_type`); `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-album`
  - `AlbumDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbum`, `BaseDelete`
    - depende de: vuelve a `panel:album_list`; al guardar va a `panel:album_list`
    - ruta: `panel:album_delete` → `/panel/album/<int:pk>/delete/`
    - fondo: `bg-music-album`
  - `AlbumDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseAlbum`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:album_list`; plantilla `music/detail/album.html`
    - ruta: `panel:album_detail` → `/panel/album/<int:pk>/`
    - fondo: `bg-music-album`
  - `AlbumListByView` (panel) — lista «por» (acotada a un padre) — genero, tipo, artista.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseAlbumContext`, `AdminListByView`
    - depende de: datos de `panel:album_data-by`
    - ruta: `panel:album_by` → `/panel/album/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `album_type`); `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-album`
  - `AlbumListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseAlbum`, `AdminListView`
    - depende de: datos de `panel:album_data`
    - ruta: `panel:album_list` → `/panel/album/`
    - fondo: `bg-music-album`
  - `AlbumPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbumContext`, `PublicDataView`
    - ruta: `music:albumes-catalogo-data` → `/catalog/music/albums/list/data/`, `music:albumes-por-data` → `/catalog/music/albums/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `album_type`); `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-album`
  - `AlbumPublicDetailView` (pública) — ficha — Ficha pública de un álbum: reseña, pistas numeradas e imágenes.
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseAlbum`, `BasePublicDetailView`
    - depende de: vuelve a `music:albumes-catalogo`; plantilla `music/detail/album.html`
    - ruta: `music:album` → `/catalog/music/album/<int:pk>/<slug:slug>/`, `music:album` → `/catalog/music/album/<int:pk>/`
    - fondo: `bg-music-album`
  - `AlbumPublicListByView` (pública) — lista «por» (acotada a un padre) — genero, tipo, artista.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseAlbumContext`, `PublicListByView`
    - depende de: datos de `music:albumes-por-data`; plantilla `public/list.html`
    - ruta: `music:albumes-por` → `/catalog/music/albums/<str:tipo>/<int:pk>/`, `music:albumes-por` → `/catalog/music/albums/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `album_type`); `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-album`
  - `AlbumPublicListView` (pública) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseAlbum`, `PublicListView`
    - depende de: datos de `music:albumes-catalogo-data`; plantilla `public/list.html`
    - ruta: `music:albumes-catalogo` → `/catalog/music/albums/list/`
    - fondo: `bg-music-album`
  - `AlbumSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbum`, `BaseSelectView`
    - ruta: `panel:album_select` → `/panel/album/select/`
    - fondo: `bg-music-album`
  - `AlbumUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbum`, `BaseUpdate`
    - depende de: formulario `AlbumForm`; vuelve a `panel:album_list`; al guardar va a `panel:album_list`; plantilla `music/form/album.html`
    - ruta: `panel:album_update` → `/panel/album/<int:pk>/update/`
    - fondo: `bg-music-album`
- Filtros:
  - `AlbumFilters`: Género (`genres`), Año (`release_date`) — para `AlbumDataView`, `AlbumPublicDataView`

### Modelo: `AlbumImage` (`apps/music/models.py`)

- Formulario: `AlbumImageForm` (`apps/music/forms.py`) — campos: `album`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `AlbumImageCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbumImage`, `BaseCreate`
    - depende de: formulario `AlbumImageForm`; vuelve a `panel:album-image_list`; al guardar va a `panel:album-image_list`; plantilla `music/form/album_image.html`
    - ruta: `panel:album-image_create` → `/panel/album-image/create/`
    - fondo: `bg-music-album-image`
  - `AlbumImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbumImageContext`, `AdminDataView`
    - ruta: `panel:album-image_data` → `/panel/album-image/data/`, `panel:album-image_data-by` → `/panel/album-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `album` → padre por id (campo `album`)
    - fondo: `bg-music-album-image`
  - `AlbumImageDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbumImage`, `BaseDelete`
    - depende de: vuelve a `panel:album-image_list`; al guardar va a `panel:album-image_list`
    - ruta: `panel:album-image_delete` → `/panel/album-image/<int:pk>/delete/`
    - fondo: `bg-music-album-image`
  - `AlbumImageDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseAlbumImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:album-image_list`; plantilla `music/detail/album_image.html`
    - ruta: `panel:album-image_detail` → `/panel/album-image/<int:pk>/`
    - fondo: `bg-music-album-image`
  - `AlbumImageListByView` (panel) — lista «por» (acotada a un padre) — album.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseAlbumImageContext`, `AdminListByView`
    - depende de: datos de `panel:album-image_data-by`
    - ruta: `panel:album-image_by` → `/panel/album-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `album` → padre por id (campo `album`)
    - fondo: `bg-music-album-image`
  - `AlbumImageListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseAlbumImage`, `AdminListView`
    - depende de: datos de `panel:album-image_data`
    - ruta: `panel:album-image_list` → `/panel/album-image/`
    - fondo: `bg-music-album-image`
  - `AlbumImagePublicListByView` (pública) — lista «por» (acotada a un padre) — album.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseAlbumImageContext`, `PublicListByView`
    - depende de: datos de `music:album-imagenes-por-data`; plantilla `public/list.html`
    - ruta: `music:album-imagenes-por` → `/catalog/music/album/images/<str:tipo>/<int:pk>/`, `music:album-imagenes-por` → `/catalog/music/album/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `album` → padre por id (campo `album`)
    - fondo: `bg-music-album`
  - `AlbumImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbumImage`, `BaseSelectView`
    - ruta: `panel:album-image_select` → `/panel/album-image/select/`
    - fondo: `bg-music-album-image`
  - `AlbumImageUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbumImage`, `BaseUpdate`
    - depende de: formulario `AlbumImageForm`; vuelve a `panel:album-image_list`; al guardar va a `panel:album-image_list`; plantilla `music/form/album_image.html`
    - ruta: `panel:album-image_update` → `/panel/album-image/<int:pk>/update/`
    - fondo: `bg-music-album-image`
  - `AlbumImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de un álbum: sus imágenes en tarjetas (la portada va en la ficha).
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbumImageContext`, `PublicDataView`
    - ruta: `music:album-imagenes-por-data` → `/catalog/music/album/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `album` → padre por id (campo `album`)
    - fondo: `bg-music-album-image`

### Modelo: `AlbumType` (`apps/music/models.py`)

- Formulario: `AlbumTypeForm` (`apps/music/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `AlbumTypeCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbumType`, `BaseCreate`
    - depende de: formulario `AlbumTypeForm`; vuelve a `panel:music-album-type_list`; al guardar va a `panel:music-album-type_list`; plantilla `music/form/album_type.html`
    - ruta: `panel:music-album-type_create` → `/panel/music-album-type/create/`
    - fondo: `bg-music-album-type`
  - `AlbumTypeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbumType`, `AdminDataView`
    - ruta: `panel:music-album-type_data` → `/panel/music-album-type/data/`
    - fondo: `bg-music-album-type`
  - `AlbumTypeDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbumType`, `BaseDelete`
    - depende de: vuelve a `panel:music-album-type_list`; al guardar va a `panel:music-album-type_list`
    - ruta: `panel:music-album-type_delete` → `/panel/music-album-type/<int:pk>/delete/`
    - fondo: `bg-music-album-type`
  - `AlbumTypeDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseAlbumType`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:music-album-type_list`; plantilla `music/detail/album_type.html`
    - ruta: `panel:music-album-type_detail` → `/panel/music-album-type/<int:pk>/`
    - fondo: `bg-music-album-type`
  - `AlbumTypeListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseAlbumType`, `AdminListView`
    - depende de: datos de `panel:music-album-type_data`
    - ruta: `panel:music-album-type_list` → `/panel/music-album-type/`
    - fondo: `bg-music-album-type`
  - `AlbumTypeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseAlbumType`, `BaseSelectView`
    - ruta: `panel:music-album-type_select` → `/panel/music-album-type/select/`
    - fondo: `bg-music-album-type`
  - `AlbumTypeUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseAlbumType`, `BaseUpdate`
    - depende de: formulario `AlbumTypeForm`; vuelve a `panel:music-album-type_list`; al guardar va a `panel:music-album-type_list`; plantilla `music/form/album_type.html`
    - ruta: `panel:music-album-type_update` → `/panel/music-album-type/<int:pk>/update/`
    - fondo: `bg-music-album-type`

### Modelo: `Artist` (`apps/music/models.py`)

- Formulario: `ArtistForm` (`apps/music/forms.py`) — campos: `name`, `biography`, `start_year`, `year_end`, `artist_type`, `genres`, `is_active`
- Vistas:
  - `ArtistCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtist`, `BaseCreate`
    - depende de: formulario `ArtistForm`; vuelve a `panel:artist_list`; al guardar va a `panel:artist_list`; plantilla `music/form/artist.html`
    - ruta: `panel:artist_create` → `/panel/artist/create/`
    - fondo: `bg-music-artist`
  - `ArtistDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistContext`, `AdminDataView`
    - ruta: `panel:artist_data` → `/panel/artist/data/`, `panel:artist_data-by` → `/panel/artist/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `artist_type`)
    - fondo: `bg-music-artist`
  - `ArtistDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtist`, `BaseDelete`
    - depende de: vuelve a `panel:artist_list`; al guardar va a `panel:artist_list`
    - ruta: `panel:artist_delete` → `/panel/artist/<int:pk>/delete/`
    - fondo: `bg-music-artist`
  - `ArtistDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseArtist`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:artist_list`; plantilla `music/detail/artist.html`
    - ruta: `panel:artist_detail` → `/panel/artist/<int:pk>/`
    - fondo: `bg-music-artist`
  - `ArtistListByView` (panel) — lista «por» (acotada a un padre) — genero, tipo.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseArtistContext`, `AdminListByView`
    - depende de: datos de `panel:artist_data-by`
    - ruta: `panel:artist_by` → `/panel/artist/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `artist_type`)
    - fondo: `bg-music-artist`
  - `ArtistListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseArtist`, `_ImagenDeezer`, `AdminListView`
    - depende de: datos de `panel:artist_data`
    - ruta: `panel:artist_list` → `/panel/artist/`
    - fondo: `bg-music-artist`
  - `ArtistPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistContext`, `PublicDataView`
    - ruta: `music:artistas-catalogo-data` → `/catalog/music/artists/list/data/`, `music:artistas-por-data` → `/catalog/music/artists/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `artist_type`)
    - fondo: `bg-music-artist`
  - `ArtistPublicDetailView` (pública) — ficha — Ficha pública de un artista: el mismo HTML que en gestión, sin botones y con la colección.
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseArtist`, `BasePublicDetailView`
    - depende de: vuelve a `music:artistas-catalogo`; plantilla `music/detail/artist.html`
    - ruta: `music:artista` → `/catalog/music/artist/<int:pk>/<slug:slug>/`, `music:artista` → `/catalog/music/artist/<int:pk>/`
    - fondo: `bg-music-artist`
  - `ArtistPublicListByView` (pública) — lista «por» (acotada a un padre) — genero, tipo.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseArtistContext`, `PublicListByView`
    - depende de: datos de `music:artistas-por-data`; plantilla `public/list.html`
    - ruta: `music:artistas-por` → `/catalog/music/artists/<str:tipo>/<int:pk>/`, `music:artistas-por` → `/catalog/music/artists/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `genres`); `tipo` → padre por id (campo `artist_type`)
    - fondo: `bg-music-artist`
  - `ArtistPublicListView` (pública) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseArtist`, `PublicListView`
    - depende de: datos de `music:artistas-catalogo-data`; plantilla `public/list.html`
    - ruta: `music:artistas-catalogo` → `/catalog/music/artists/list/`
    - fondo: `bg-music-artist`
  - `ArtistSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtist`, `BaseSelectView`
    - ruta: `panel:artist_select` → `/panel/artist/select/`
    - fondo: `bg-music-artist`
  - `ArtistUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtist`, `BaseUpdate`
    - depende de: formulario `ArtistForm`; vuelve a `panel:artist_list`; al guardar va a `panel:artist_list`; plantilla `music/form/artist.html`
    - ruta: `panel:artist_update` → `/panel/artist/<int:pk>/update/`
    - fondo: `bg-music-artist`
- Filtros:
  - `ArtistAdminFilters`: Activo (`is_active`), Tipo de artista (`artist_type`), Género (`genres`), Año de inicio (`start_year`) — para `ArtistDataView`
  - `ArtistFilters`: Género (`genres`) — para `ArtistPublicDataView`

### Modelo: `ArtistImage` (`apps/music/models.py`)

- Formulario: `ArtistImageForm` (`apps/music/forms.py`) — campos: `artist`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `ArtistImageCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistImage`, `BaseCreate`
    - depende de: formulario `ArtistImageForm`; vuelve a `panel:artist-image_list`; al guardar va a `panel:artist-image_list`; plantilla `music/form/artist_image.html`
    - ruta: `panel:artist-image_create` → `/panel/artist-image/create/`
    - fondo: `bg-music-artist-image`
  - `ArtistImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistImageContext`, `AdminDataView`
    - ruta: `panel:artist-image_data` → `/panel/artist-image/data/`, `panel:artist-image_data-by` → `/panel/artist-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-artist-image`
  - `ArtistImageDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistImage`, `BaseDelete`
    - depende de: vuelve a `panel:artist-image_list`; al guardar va a `panel:artist-image_list`
    - ruta: `panel:artist-image_delete` → `/panel/artist-image/<int:pk>/delete/`
    - fondo: `bg-music-artist-image`
  - `ArtistImageDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseArtistImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:artist-image_list`; plantilla `music/detail/artist_image.html`
    - ruta: `panel:artist-image_detail` → `/panel/artist-image/<int:pk>/`
    - fondo: `bg-music-artist-image`
  - `ArtistImageListByView` (panel) — lista «por» (acotada a un padre) — artista.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseArtistImageContext`, `AdminListByView`
    - depende de: datos de `panel:artist-image_data-by`
    - ruta: `panel:artist-image_by` → `/panel/artist-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-artist-image`
  - `ArtistImageListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseArtistImage`, `AdminListView`
    - depende de: datos de `panel:artist-image_data`
    - ruta: `panel:artist-image_list` → `/panel/artist-image/`
    - fondo: `bg-music-artist-image`
  - `ArtistImagePublicListByView` (pública) — lista «por» (acotada a un padre) — artista.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseArtistImageContext`, `PublicListByView`
    - depende de: datos de `music:artista-imagenes-por-data`; plantilla `public/list.html`
    - ruta: `music:artista-imagenes-por` → `/catalog/music/artist/images/<str:tipo>/<int:pk>/`, `music:artista-imagenes-por` → `/catalog/music/artist/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-artist`
  - `ArtistImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistImage`, `BaseSelectView`
    - ruta: `panel:artist-image_select` → `/panel/artist-image/select/`
    - fondo: `bg-music-artist-image`
  - `ArtistImageUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistImage`, `BaseUpdate`
    - depende de: formulario `ArtistImageForm`; vuelve a `panel:artist-image_list`; al guardar va a `panel:artist-image_list`; plantilla `music/form/artist_image.html`
    - ruta: `panel:artist-image_update` → `/panel/artist-image/<int:pk>/update/`
    - fondo: `bg-music-artist-image`
  - `ArtistImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de un artista: sus imágenes en tarjetas.
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistImageContext`, `PublicDataView`
    - ruta: `music:artista-imagenes-por-data` → `/catalog/music/artist/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `artista` → padre por id (campo `artist`)
    - fondo: `bg-music-artist-image`

### Modelo: `ArtistMember` (`apps/music/models.py`)

- Formulario: `ArtistMemberForm` (`apps/music/forms.py`) — campos: `artist`, `person`, `role`, `join_date`, `leave_date`, `is_active`
- Vistas:
  - `ArtistMemberCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistMember`, `BaseCreate`
    - depende de: formulario `ArtistMemberForm`; vuelve a `panel:artist-member_list`; al guardar va a `panel:artist-member_list`; plantilla `music/form/artist_member.html`
    - ruta: `panel:artist-member_create` → `/panel/artist-member/create/`
    - fondo: `bg-music-artist-member`
  - `ArtistMemberDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistMemberContext`, `AdminDataView`
    - ruta: `panel:artist-member_data` → `/panel/artist-member/data/`, `panel:artist-member_data-by` → `/panel/artist-member/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `artista` → padre por id (campo `artist`); `persona` → padre por id (campo `person`)
    - fondo: `bg-music-artist-member`
  - `ArtistMemberDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistMember`, `BaseDelete`
    - depende de: vuelve a `panel:artist-member_list`; al guardar va a `panel:artist-member_list`
    - ruta: `panel:artist-member_delete` → `/panel/artist-member/<int:pk>/delete/`
    - fondo: `bg-music-artist-member`
  - `ArtistMemberDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseArtistMember`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:artist-member_list`; plantilla `music/detail/artist_member.html`
    - ruta: `panel:artist-member_detail` → `/panel/artist-member/<int:pk>/`
    - fondo: `bg-music-artist-member`
  - `ArtistMemberListByView` (panel) — lista «por» (acotada a un padre) — artista, persona.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseArtistMemberContext`, `AdminListByView`
    - depende de: datos de `panel:artist-member_data-by`
    - ruta: `panel:artist-member_by` → `/panel/artist-member/<str:tipo>/<str:pk>/`
    - mapa «by»: `artista` → padre por id (campo `artist`); `persona` → padre por id (campo `person`)
    - fondo: `bg-music-artist-member`
  - `ArtistMemberListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseArtistMember`, `AdminListView`
    - depende de: datos de `panel:artist-member_data`
    - ruta: `panel:artist-member_list` → `/panel/artist-member/`
    - fondo: `bg-music-artist-member`
  - `ArtistMemberSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistMember`, `BaseSelectView`
    - ruta: `panel:artist-member_select` → `/panel/artist-member/select/`
    - fondo: `bg-music-artist-member`
  - `ArtistMemberUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistMember`, `BaseUpdate`
    - depende de: formulario `ArtistMemberForm`; vuelve a `panel:artist-member_list`; al guardar va a `panel:artist-member_list`; plantilla `music/form/artist_member.html`
    - ruta: `panel:artist-member_update` → `/panel/artist-member/<int:pk>/update/`
    - fondo: `bg-music-artist-member`

### Modelo: `ArtistType` (`apps/music/models.py`)

- Formulario: `ArtistTypeForm` (`apps/music/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `ArtistTypeCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistType`, `BaseCreate`
    - depende de: formulario `ArtistTypeForm`; vuelve a `panel:music-artist-type_list`; al guardar va a `panel:music-artist-type_list`; plantilla `music/form/artist_type.html`
    - ruta: `panel:music-artist-type_create` → `/panel/music-artist-type/create/`
    - fondo: `bg-music-artist-type`
  - `ArtistTypeDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistType`, `AdminDataView`
    - ruta: `panel:music-artist-type_data` → `/panel/music-artist-type/data/`
    - fondo: `bg-music-artist-type`
  - `ArtistTypeDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistType`, `BaseDelete`
    - depende de: vuelve a `panel:music-artist-type_list`; al guardar va a `panel:music-artist-type_list`
    - ruta: `panel:music-artist-type_delete` → `/panel/music-artist-type/<int:pk>/delete/`
    - fondo: `bg-music-artist-type`
  - `ArtistTypeDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseArtistType`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:music-artist-type_list`; plantilla `music/detail/artist_type.html`
    - ruta: `panel:music-artist-type_detail` → `/panel/music-artist-type/<int:pk>/`
    - fondo: `bg-music-artist-type`
  - `ArtistTypeListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseArtistType`, `AdminListView`
    - depende de: datos de `panel:music-artist-type_data`
    - ruta: `panel:music-artist-type_list` → `/panel/music-artist-type/`
    - fondo: `bg-music-artist-type`
  - `ArtistTypeSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseArtistType`, `BaseSelectView`
    - ruta: `panel:music-artist-type_select` → `/panel/music-artist-type/select/`
    - fondo: `bg-music-artist-type`
  - `ArtistTypeUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseArtistType`, `BaseUpdate`
    - depende de: formulario `ArtistTypeForm`; vuelve a `panel:music-artist-type_list`; al guardar va a `panel:music-artist-type_list`; plantilla `music/form/artist_type.html`
    - ruta: `panel:music-artist-type_update` → `/panel/music-artist-type/<int:pk>/update/`
    - fondo: `bg-music-artist-type`


### Modelo: `DataDeezerAlbum` (`apps/music/models.py`)

- Formulario: `DataDeezerAlbumForm` (`apps/music/forms.py`) — campos: `deezer_id`, `deezer_id_artist`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataDeezerAlbumCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerAlbum`, `BaseCreate`
    - depende de: formulario `DataDeezerAlbumForm`; vuelve a `panel:data-deezer-album_list`; al guardar va a `panel:data-deezer-album_list`
    - ruta: `panel:data-deezer-album_create` → `/panel/data-deezer-album/create/`
    - fondo: `bg-music-data-deezer-album`
  - `DataDeezerAlbumDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseDataDeezerAlbum`, `AdminDataView`
    - ruta: `panel:data-deezer-album_data` → `/panel/data-deezer-album/data/`
    - fondo: `bg-music-data-deezer-album`
  - `DataDeezerAlbumDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerAlbum`, `BaseDelete`
    - depende de: vuelve a `panel:data-deezer-album_list`; al guardar va a `panel:data-deezer-album_list`
    - ruta: `panel:data-deezer-album_delete` → `/panel/data-deezer-album/<int:pk>/delete/`
    - fondo: `bg-music-data-deezer-album`
  - `DataDeezerAlbumDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseDataDeezerAlbum`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-deezer-album_list`; plantilla `music/detail/data_deezer_album.html`
    - ruta: `panel:data-deezer-album_detail` → `/panel/data-deezer-album/<int:pk>/`
    - fondo: `bg-music-data-deezer-album`
  - `DataDeezerAlbumListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseDataDeezerAlbum`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-deezer-album_data`
    - ruta: `panel:data-deezer-album_list` → `/panel/data-deezer-album/`
    - fondo: `bg-music-data-deezer-album`
  - `DataDeezerAlbumUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerAlbum`, `BaseUpdate`
    - depende de: formulario `DataDeezerAlbumForm`; vuelve a `panel:data-deezer-album_list`; al guardar va a `panel:data-deezer-album_list`
    - ruta: `panel:data-deezer-album_update` → `/panel/data-deezer-album/<int:pk>/update/`
    - fondo: `bg-music-data-deezer-album`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataDeezerAlbumDataView`

### Modelo: `DataDeezerTrack` (`apps/music/models.py`)

- Formulario: `DataDeezerTrackForm` (`apps/music/forms.py`) — campos: `deezer_id`, `deezer_id_album`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataDeezerTrackCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerTrack`, `BaseCreate`
    - depende de: formulario `DataDeezerTrackForm`; vuelve a `panel:data-deezer-track_list`; al guardar va a `panel:data-deezer-track_list`
    - ruta: `panel:data-deezer-track_create` → `/panel/data-deezer-track/create/`
    - fondo: `bg-music-data-track-deezer`
  - `DataDeezerTrackDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseDataDeezerTrack`, `AdminDataView`
    - ruta: `panel:data-deezer-track_data` → `/panel/data-deezer-track/data/`
    - fondo: `bg-music-data-track-deezer`
  - `DataDeezerTrackDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerTrack`, `BaseDelete`
    - depende de: vuelve a `panel:data-deezer-track_list`; al guardar va a `panel:data-deezer-track_list`
    - ruta: `panel:data-deezer-track_delete` → `/panel/data-deezer-track/<int:pk>/delete/`
    - fondo: `bg-music-data-track-deezer`
  - `DataDeezerTrackDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseDataDeezerTrack`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-deezer-track_list`; plantilla `music/detail/data_deezer_track.html`
    - ruta: `panel:data-deezer-track_detail` → `/panel/data-deezer-track/<int:pk>/`
    - fondo: `bg-music-data-track-deezer`
  - `DataDeezerTrackListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseDataDeezerTrack`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-deezer-track_data`
    - ruta: `panel:data-deezer-track_list` → `/panel/data-deezer-track/`
    - fondo: `bg-music-data-track-deezer`
  - `DataDeezerTrackUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerTrack`, `BaseUpdate`
    - depende de: formulario `DataDeezerTrackForm`; vuelve a `panel:data-deezer-track_list`; al guardar va a `panel:data-deezer-track_list`
    - ruta: `panel:data-deezer-track_update` → `/panel/data-deezer-track/<int:pk>/update/`
    - fondo: `bg-music-data-track-deezer`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataDeezerTrackDataView`

### Modelo: `DataDeezerArtist` (`apps/music/models.py`)

- Formulario: `DataDeezerArtistForm` (`apps/music/forms.py`) — campos: `deezer_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataDeezerArtistCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerArtist`, `BaseCreate`
    - depende de: formulario `DataDeezerArtistForm`; vuelve a `panel:data-deezer-artist_list`; al guardar va a `panel:data-deezer-artist_list`
    - ruta: `panel:data-deezer-artist_create` → `/panel/data-deezer-artist/create/`
    - fondo: `bg-music-data-deezer-artist`
  - `DataDeezerArtistDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseDataDeezerArtist`, `AdminDataView`
    - ruta: `panel:data-deezer-artist_data` → `/panel/data-deezer-artist/data/`
    - fondo: `bg-music-data-deezer-artist`
  - `DataDeezerArtistDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerArtist`, `BaseDelete`
    - depende de: vuelve a `panel:data-deezer-artist_list`; al guardar va a `panel:data-deezer-artist_list`
    - ruta: `panel:data-deezer-artist_delete` → `/panel/data-deezer-artist/<int:pk>/delete/`
    - fondo: `bg-music-data-deezer-artist`
  - `DataDeezerArtistDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseDataDeezerArtist`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-deezer-artist_list`; plantilla `music/detail/data_deezer_artist.html`
    - ruta: `panel:data-deezer-artist_detail` → `/panel/data-deezer-artist/<int:pk>/`
    - fondo: `bg-music-data-deezer-artist`
  - `DataDeezerArtistListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseDataDeezerArtist`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-deezer-artist_data`
    - ruta: `panel:data-deezer-artist_list` → `/panel/data-deezer-artist/`
    - fondo: `bg-music-data-deezer-artist`
  - `DataDeezerArtistUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerArtist`, `BaseUpdate`
    - depende de: formulario `DataDeezerArtistForm`; vuelve a `panel:data-deezer-artist_list`; al guardar va a `panel:data-deezer-artist_list`
    - ruta: `panel:data-deezer-artist_update` → `/panel/data-deezer-artist/<int:pk>/update/`
    - fondo: `bg-music-data-deezer-artist`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataDeezerArtistDataView`

### Modelo: `DataDeezerGenre` (`apps/music/models.py`)

- Formulario: `DataDeezerGenreForm` (`apps/music/forms.py`) — campos: `deezer_id`, `data_status`, `data_processed`, `is_active`
- Vistas:
  - `DataDeezerGenreCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerGenre`, `BaseCreate`
    - depende de: formulario `DataDeezerGenreForm`; vuelve a `panel:data-deezer-genre_list`; al guardar va a `panel:data-deezer-genre_list`
    - ruta: `panel:data-deezer-genre_create` → `/panel/data-deezer-genre/create/`
    - fondo: `bg-music-data-deezer-genre`
  - `DataDeezerGenreDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseDataDeezerGenre`, `AdminDataView`
    - ruta: `panel:data-deezer-genre_data` → `/panel/data-deezer-genre/data/`
    - fondo: `bg-music-data-deezer-genre`
  - `DataDeezerGenreDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerGenre`, `BaseDelete`
    - depende de: vuelve a `panel:data-deezer-genre_list`; al guardar va a `panel:data-deezer-genre_list`
    - ruta: `panel:data-deezer-genre_delete` → `/panel/data-deezer-genre/<int:pk>/delete/`
    - fondo: `bg-music-data-deezer-genre`
  - `DataDeezerGenreDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseDataDeezerGenre`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:data-deezer-genre_list`; plantilla `music/detail/data_deezer_genre.html`
    - ruta: `panel:data-deezer-genre_detail` → `/panel/data-deezer-genre/<int:pk>/`
    - fondo: `bg-music-data-deezer-genre`
  - `DataDeezerGenreListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseDataDeezerGenre`, `DataBulkMixin`, `AdminListView`
    - depende de: datos de `panel:data-deezer-genre_data`
    - ruta: `panel:data-deezer-genre_list` → `/panel/data-deezer-genre/`
    - fondo: `bg-music-data-deezer-genre`
  - `DataDeezerGenreUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseDataDeezerGenre`, `BaseUpdate`
    - depende de: formulario `DataDeezerGenreForm`; vuelve a `panel:data-deezer-genre_list`; al guardar va a `panel:data-deezer-genre_list`
    - ruta: `panel:data-deezer-genre_update` → `/panel/data-deezer-genre/<int:pk>/update/`
    - fondo: `bg-music-data-deezer-genre`
- Filtros:
  - `DatosFilters`: Fetch OK (`data_status`), Procesado (`data_processed`), Activo (`is_active`), HTTP (`status_code`) — para `DataDeezerGenreDataView`

### Modelo: `Genre` (`apps/music/models.py`)

- Formulario: `GenreForm` (`apps/music/forms.py`) — campos: `name`, `name_esp`, `description`, `image`, `is_active`
- Vistas:
  - `GenreCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseGenre`, `BaseCreate`
    - depende de: formulario `GenreForm`; vuelve a `panel:music-genre_list`; al guardar va a `panel:music-genre_list`; plantilla `music/form/genre.html`
    - ruta: `panel:music-genre_create` → `/panel/music-genre/create/`
    - fondo: `bg-music-genre`
  - `GenreDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseGenre`, `AdminDataView`
    - ruta: `panel:music-genre_data` → `/panel/music-genre/data/`
    - fondo: `bg-music-genre`
  - `GenreDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseGenre`, `BaseDelete`
    - depende de: vuelve a `panel:music-genre_list`; al guardar va a `panel:music-genre_list`
    - ruta: `panel:music-genre_delete` → `/panel/music-genre/<int:pk>/delete/`
    - fondo: `bg-music-genre`
  - `GenreDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseGenre`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:music-genre_list`; plantilla `music/detail/genre.html`
    - ruta: `panel:music-genre_detail` → `/panel/music-genre/<int:pk>/`
    - fondo: `bg-music-genre`
  - `GenreListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseGenre`, `_ImagenDeezer`, `AdminListView`
    - depende de: datos de `panel:music-genre_data`
    - ruta: `panel:music-genre_list` → `/panel/music-genre/`
    - fondo: `bg-music-genre`
  - `GenreSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseGenre`, `BaseSelectView`
    - ruta: `panel:music-genre_select` → `/panel/music-genre/select/`
    - fondo: `bg-music-genre`
  - `GenreUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseGenre`, `BaseUpdate`
    - depende de: formulario `GenreForm`; vuelve a `panel:music-genre_list`; al guardar va a `panel:music-genre_list`; plantilla `music/form/genre.html`
    - ruta: `panel:music-genre_update` → `/panel/music-genre/<int:pk>/update/`
    - fondo: `bg-music-genre`

### Modelo: `GenreAlias` (`apps/music/models.py`)

- Formulario: `GenreAliasForm` (`apps/music/forms.py`) — campos: `name`, `name_esp`, `is_active`, `genre`
- Vistas:
  - `GenreAliasCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseCreate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:music-genre-alias_list`; al guardar va a `panel:music-genre-alias_list`
    - ruta: `panel:music-genre-alias_create` → `/panel/music-genre-alias/create/`
    - fondo: `bg-music-music-genre`
  - `GenreAliasDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseGenreAliasContext`, `AdminDataView`
    - ruta: `panel:music-genre-alias_data` → `/panel/music-genre-alias/data/`, `panel:music-genre-alias_data-by` → `/panel/music-genre-alias/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-music-music-genre`
  - `GenreAliasDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseDelete`
    - depende de: vuelve a `panel:music-genre-alias_list`; al guardar va a `panel:music-genre-alias_list`
    - ruta: `panel:music-genre-alias_delete` → `/panel/music-genre-alias/<int:pk>/delete/`
    - fondo: `bg-music-music-genre`
  - `GenreAliasDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseGenreAlias`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:music-genre-alias_list`
    - ruta: `panel:music-genre-alias_detail` → `/panel/music-genre-alias/<int:pk>/`
    - fondo: `bg-music-music-genre`
  - `GenreAliasListByView` (panel) — lista «por» (acotada a un padre) — Alias acotados por su padre (`/music-genre-alias/genre/<id>/`): los alimenta GenreAliasDataView con `/data/genre/<id>/`.
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseGenreAliasContext`, `AdminListByView`
    - depende de: datos de `panel:music-genre-alias_data-by`
    - ruta: `panel:music-genre-alias_by` → `/panel/music-genre-alias/<str:tipo>/<str:pk>/`
    - mapa «by»: `genre` → padre por id (campo `genre`)
    - fondo: `bg-music-music-genre`
  - `GenreAliasListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseGenreAlias`, `AdminListView`
    - depende de: datos de `panel:music-genre-alias_data`
    - ruta: `panel:music-genre-alias_list` → `/panel/music-genre-alias/`
    - fondo: `bg-music-music-genre`
  - `GenreAliasUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseGenreAlias`, `BaseUpdate`
    - depende de: formulario `GenreAliasForm`; vuelve a `panel:music-genre-alias_list`; al guardar va a `panel:music-genre-alias_list`
    - ruta: `panel:music-genre-alias_update` → `/panel/music-genre-alias/<int:pk>/update/`
    - fondo: `bg-music-music-genre`

### Modelo: `MusicLog` (`apps/music/models.py`)

- Formulario: `MusicLogForm` (`apps/music/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `MusicLogCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseMusicLog`, `BaseCreate`
    - depende de: formulario `MusicLogForm`; vuelve a `panel:music-log_list`; al guardar va a `panel:music-log_list`
    - ruta: `panel:music-log_create` → `/panel/music-log/create/`
    - fondo: `bg-music-music-log`
  - `MusicLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseMusicLog`, `AdminDataView`
    - ruta: `panel:music-log_data` → `/panel/music-log/data/`
    - fondo: `bg-music-music-log`
  - `MusicLogDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseMusicLog`, `BaseDelete`
    - depende de: vuelve a `panel:music-log_list`; al guardar va a `panel:music-log_list`
    - ruta: `panel:music-log_delete` → `/panel/music-log/<int:pk>/delete/`
    - fondo: `bg-music-music-log`
  - `MusicLogDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseMusicLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:music-log_list`; plantilla `music/detail/music_log.html`
    - ruta: `panel:music-log_detail` → `/panel/music-log/<int:pk>/`
    - fondo: `bg-music-music-log`
  - `MusicLogListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseMusicLog`, `AdminListView`
    - depende de: datos de `panel:music-log_data`
    - ruta: `panel:music-log_list` → `/panel/music-log/`
    - fondo: `bg-music-music-log`
  - `MusicLogUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseMusicLog`, `BaseUpdate`
    - depende de: formulario `MusicLogForm`; vuelve a `panel:music-log_list`; al guardar va a `panel:music-log_list`
    - ruta: `panel:music-log_update` → `/panel/music-log/<int:pk>/update/`
    - fondo: `bg-music-music-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `MusicLogDataView`

### Modelo: `Role` (`apps/music/models.py`)

- Formulario: `RoleForm` (`apps/music/forms.py`) — campos: `name`, `name_esp`, `type`, `description`, `image`, `is_active`
- Vistas:
  - `RoleCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseRole`, `BaseCreate`
    - depende de: formulario `RoleForm`; vuelve a `panel:music-role_list`; al guardar va a `panel:music-role_list`; plantilla `music/form/role.html`
    - ruta: `panel:music-role_create` → `/panel/music-role/create/`
    - fondo: `bg-music-role`
  - `RoleDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseRoleContext`, `AdminDataView`
    - ruta: `panel:music-role_data` → `/panel/music-role/data/`, `panel:music-role_data-by` → `/panel/music-role/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `production`, `music`, `unknown`
    - fondo: `bg-music-role`
  - `RoleDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseRole`, `BaseDelete`
    - depende de: vuelve a `panel:music-role_list`; al guardar va a `panel:music-role_list`
    - ruta: `panel:music-role_delete` → `/panel/music-role/<int:pk>/delete/`
    - fondo: `bg-music-role`
  - `RoleDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseRole`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:music-role_list`; plantilla `music/detail/role.html`
    - ruta: `panel:music-role_detail` → `/panel/music-role/<int:pk>/`
    - fondo: `bg-music-role`
  - `RoleListByView` (panel) — lista «por» (acotada a un padre) — Lista de roles acotada por familia (`/music-role/type/<valor>/`): la alimenta RoleDataView con `/data/type/<valor>/`.
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseRoleContext`, `AdminListByView`
    - depende de: datos de `panel:music-role_data-by`
    - ruta: `panel:music-role_by` → `/panel/music-role/<str:tipo>/<str:pk>/`
    - mapa «by»: `type` → choice: `staff`, `production`, `music`, `unknown`
    - fondo: `bg-music-role`
  - `RoleListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseRole`, `AdminListView`
    - depende de: datos de `panel:music-role_data`
    - ruta: `panel:music-role_list` → `/panel/music-role/`
    - fondo: `bg-music-role`
  - `RoleSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseRole`, `BaseSelectView`
    - ruta: `panel:music-role_select` → `/panel/music-role/select/`
    - fondo: `bg-music-role`
  - `RoleUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseRole`, `BaseUpdate`
    - depende de: formulario `RoleForm`; vuelve a `panel:music-role_list`; al guardar va a `panel:music-role_list`; plantilla `music/form/role.html`
    - ruta: `panel:music-role_update` → `/panel/music-role/<int:pk>/update/`
    - fondo: `bg-music-role`
- Filtros:
  - `RoleFilters`: Tipo de rol (`type`), Activo (`is_active`) — para `RoleDataView`

### Modelo: `Song` (`apps/music/models.py`)

- Formulario: `SongForm` (`apps/music/forms.py`) — campos: `title`, `title_short`, `title_version`, `album`, `album_song_id`, `composers`, `release_year`, `audio_file`, `lyrics`, `meaning`, `video_url`, `is_active`
- Vistas:
  - `SongCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSong`, `BaseCreate`
    - depende de: formulario `SongForm`; vuelve a `panel:song_list`; al guardar va a `panel:song_list`; plantilla `music/form/song.html`
    - ruta: `panel:song_create` → `/panel/song/create/`
    - fondo: `bg-music-song`
  - `SongDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseSongContext`, `AdminDataView`
    - ruta: `panel:song_data` → `/panel/song/data/`, `panel:song_data-by` → `/panel/song/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `album__genres`); `artista` → padre por id (campo `album__artist`); `album` → padre por id (campo `album`)
    - fondo: `bg-music-song`
  - `SongDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSong`, `BaseDelete`
    - depende de: vuelve a `panel:song_list`; al guardar va a `panel:song_list`
    - ruta: `panel:song_delete` → `/panel/song/<int:pk>/delete/`
    - fondo: `bg-music-song`
  - `SongDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseSong`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:song_list`; plantilla `music/detail/song.html`
    - ruta: `panel:song_detail` → `/panel/song/<int:pk>/`
    - fondo: `bg-music-song`
  - `SongListByView` (panel) — lista «por» (acotada a un padre) — genero, artista, album.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseSongContext`, `AdminListByView`
    - depende de: datos de `panel:song_data-by`
    - ruta: `panel:song_by` → `/panel/song/<str:tipo>/<str:pk>/`
    - mapa «by»: `genero` → padre por id (campo `album__genres`); `artista` → padre por id (campo `album__artist`); `album` → padre por id (campo `album`)
    - fondo: `bg-music-song`
  - `SongListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseSong`, `AdminListView`
    - depende de: datos de `panel:song_data`
    - ruta: `panel:song_list` → `/panel/song/`
    - fondo: `bg-music-song`
  - `SongPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseSongContext`, `PublicDataView`
    - ruta: `music:canciones-catalogo-data` → `/catalog/music/songs/list/data/`, `music:canciones-por-data` → `/catalog/music/songs/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `genero` → padre por id (campo `album__genres`); `artista` → padre por id (campo `album__artist`); `album` → padre por id (campo `album`)
    - fondo: `bg-music-song`
  - `SongPublicDetailView` (pública) — ficha — Ficha pública de una canción: significado, letra con traducciones y el resto del álbum.
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseSong`, `BasePublicDetailView`
    - depende de: vuelve a `music:canciones-catalogo`; plantilla `music/detail/song.html`
    - ruta: `music:cancion` → `/catalog/music/song/<int:pk>/<slug:slug>/`, `music:cancion` → `/catalog/music/song/<int:pk>/`
    - fondo: `bg-music-song`
  - `SongPublicListByView` (pública) — lista «por» (acotada a un padre) — genero, artista, album.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseSongContext`, `PublicListByView`
    - depende de: datos de `music:canciones-por-data`; plantilla `public/list.html`
    - ruta: `music:canciones-por` → `/catalog/music/songs/<str:tipo>/<int:pk>/`, `music:canciones-por` → `/catalog/music/songs/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `genero` → padre por id (campo `album__genres`); `artista` → padre por id (campo `album__artist`); `album` → padre por id (campo `album`)
    - fondo: `bg-music-song`
  - `SongPublicListView` (pública) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseSong`, `PublicListView`
    - depende de: datos de `music:canciones-catalogo-data`; plantilla `public/list.html`
    - ruta: `music:canciones-catalogo` → `/catalog/music/songs/list/`
    - fondo: `bg-music-song`
  - `SongSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseSong`, `BaseSelectView`
    - ruta: `panel:song_select` → `/panel/song/select/`
    - fondo: `bg-music-song`
  - `SongUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSong`, `BaseUpdate`
    - depende de: formulario `SongForm`; vuelve a `panel:song_list`; al guardar va a `panel:song_list`; plantilla `music/form/song.html`
    - ruta: `panel:song_update` → `/panel/song/<int:pk>/update/`
    - fondo: `bg-music-song`
- Filtros:
  - `ArtistSongFilters`: Álbum (`album`) — para `SongDataView`
  - `SongFilters`: Año (`release_year`) — para `SongPublicDataView`

### Modelo: `SongComposer` (`apps/music/models.py`)

- Formulario: `SongComposerForm` (`apps/music/forms.py`) — campos: `song`, `person`, `is_active`
- Vistas:
  - `SongComposerCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSongComposer`, `BaseCreate`
    - depende de: formulario `SongComposerForm`; vuelve a `panel:song-composer_list`; al guardar va a `panel:song-composer_list`
    - ruta: `panel:song-composer_create` → `/panel/song-composer/create/`
    - fondo: `bg-music-song-composer`
  - `SongComposerDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseSongComposerContext`, `AdminDataView`
    - ruta: `panel:song-composer_data` → `/panel/song-composer/data/`, `panel:song-composer_data-by` → `/panel/song-composer/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `cancion` → padre por id (campo `song`); `persona` → padre por id (campo `person`)
    - fondo: `bg-music-song-composer`
  - `SongComposerDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSongComposer`, `BaseDelete`
    - depende de: vuelve a `panel:song-composer_list`; al guardar va a `panel:song-composer_list`
    - ruta: `panel:song-composer_delete` → `/panel/song-composer/<int:pk>/delete/`
    - fondo: `bg-music-song-composer`
  - `SongComposerDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseSongComposer`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:song-composer_list`; plantilla `music/detail/song_composer.html`
    - ruta: `panel:song-composer_detail` → `/panel/song-composer/<int:pk>/`
    - fondo: `bg-music-song-composer`
  - `SongComposerListByView` (panel) — lista «por» (acotada a un padre) — cancion, persona.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseSongComposerContext`, `AdminListByView`
    - depende de: datos de `panel:song-composer_data-by`
    - ruta: `panel:song-composer_by` → `/panel/song-composer/<str:tipo>/<str:pk>/`
    - mapa «by»: `cancion` → padre por id (campo `song`); `persona` → padre por id (campo `person`)
    - fondo: `bg-music-song-composer`
  - `SongComposerListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseSongComposer`, `AdminListView`
    - depende de: datos de `panel:song-composer_data`
    - ruta: `panel:song-composer_list` → `/panel/song-composer/`
    - fondo: `bg-music-song-composer`
  - `SongComposerSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseSongComposer`, `BaseSelectView`
    - ruta: `panel:song-composer_select` → `/panel/song-composer/select/`
    - fondo: `bg-music-song-composer`
  - `SongComposerUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSongComposer`, `BaseUpdate`
    - depende de: formulario `SongComposerForm`; vuelve a `panel:song-composer_list`; al guardar va a `panel:song-composer_list`
    - ruta: `panel:song-composer_update` → `/panel/song-composer/<int:pk>/update/`
    - fondo: `bg-music-song-composer`

### Modelo: `SongTranslation` (`apps/music/models.py`)

- Formulario: `SongTranslationForm` (`apps/music/forms.py`) — campos: `song`, `language`, `text`, `is_active`
- Vistas:
  - `SongTranslationCreateView` (panel) — alta
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSongTranslation`, `BaseCreate`
    - depende de: formulario `SongTranslationForm`; vuelve a `panel:song-translation_list`; al guardar va a `panel:song-translation_list`
    - ruta: `panel:song-translation_create` → `/panel/song-translation/create/`
    - fondo: `bg-music-song-translation`
  - `SongTranslationDataView` (panel) — datos JSON de la lista
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseSongTranslationContext`, `AdminDataView`
    - ruta: `panel:song-translation_data` → `/panel/song-translation/data/`, `panel:song-translation_data-by` → `/panel/song-translation/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `cancion` → padre por id (campo `song`)
    - fondo: `bg-music-song-translation`
  - `SongTranslationDeleteView` (panel) — borrado
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSongTranslation`, `BaseDelete`
    - depende de: vuelve a `panel:song-translation_list`; al guardar va a `panel:song-translation_list`
    - ruta: `panel:song-translation_delete` → `/panel/song-translation/<int:pk>/delete/`
    - fondo: `bg-music-song-translation`
  - `SongTranslationDetailView` (panel) — ficha
    - archivo: `apps/music/views/v6_detail.py` · hereda de `BaseSongTranslation`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:song-translation_list`; plantilla `music/detail/song_translation.html`
    - ruta: `panel:song-translation_detail` → `/panel/song-translation/<int:pk>/`
    - fondo: `bg-music-song-translation`
  - `SongTranslationListByView` (panel) — lista «por» (acotada a un padre) — cancion.
    - archivo: `apps/music/views/v5_list_by.py` · hereda de `BaseSongTranslationContext`, `AdminListByView`
    - depende de: datos de `panel:song-translation_data-by`
    - ruta: `panel:song-translation_by` → `/panel/song-translation/<str:tipo>/<str:pk>/`
    - mapa «by»: `cancion` → padre por id (campo `song`)
    - fondo: `bg-music-song-translation`
  - `SongTranslationListView` (panel) — lista
    - archivo: `apps/music/views/v5_list.py` · hereda de `BaseSongTranslation`, `AdminListView`
    - depende de: datos de `panel:song-translation_data`
    - ruta: `panel:song-translation_list` → `/panel/song-translation/`
    - fondo: `bg-music-song-translation`
  - `SongTranslationSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/music/views/v3_data.py` · hereda de `BaseSongTranslation`, `BaseSelectView`
    - ruta: `panel:song-translation_select` → `/panel/song-translation/select/`
    - fondo: `bg-music-song-translation`
  - `SongTranslationUpdateView` (panel) — edición
    - archivo: `apps/music/views/v4_write.py` · hereda de `BaseSongTranslation`, `BaseUpdate`
    - depende de: formulario `SongTranslationForm`; vuelve a `panel:song-translation_list`; al guardar va a `panel:song-translation_list`
    - ruta: `panel:song-translation_update` → `/panel/song-translation/<int:pk>/update/`
    - fondo: `bg-music-song-translation`

### Sin modelo

- `DeezerArtistImportView`
  - archivo: `apps/music/views/v8_import.py` · hereda de `_Deezer`, `TipoImportView` · ruta: `panel:deezer-artist` → `/panel/deezer/artist/` · fondo `bg-music-import-artista`
- `DeezerGenresImportView`
  - archivo: `apps/music/views/v8_import.py` · hereda de `_Deezer`, `TipoImportView` · ruta: `panel:deezer-genres` → `/panel/deezer/genres/` · fondo `bg-music-import-generos`
- `MusicHomeView`
  - archivo: `apps/music/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:music-home` → `/panel/music/` · fondo `bg-music-home`
- `MusicPublicHomeView`
  - archivo: `apps/music/views/v1_home.py` · hereda de `BasePublicHomeView` · ruta: `music:home` → `/catalog/music/` · fondo `bg-music-home`
- Form `DeezerImportarRangoForm`
- Form `DeezerImportarUnoForm`

## Personas (`people`)

### Modelo: `PeopleLog` (`apps/people/models.py`)

- Formulario: `PeopleLogForm` (`apps/people/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `PeopleLogCreateView` (panel) — alta
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePeopleLog`, `BaseCreate`
    - depende de: formulario `PeopleLogForm`; vuelve a `panel:people-log_list`; al guardar va a `panel:people-log_list`
    - ruta: `panel:people-log_create` → `/panel/people-log/create/`
    - fondo: `bg-people-log`
  - `PeopleLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePeopleLog`, `AdminDataView`
    - ruta: `panel:people-log_data` → `/panel/people-log/data/`
    - fondo: `bg-people-log`
  - `PeopleLogDeleteView` (panel) — borrado
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePeopleLog`, `BaseDelete`
    - depende de: vuelve a `panel:people-log_list`; al guardar va a `panel:people-log_list`
    - ruta: `panel:people-log_delete` → `/panel/people-log/<int:pk>/delete/`
    - fondo: `bg-people-log`
  - `PeopleLogDetailView` (panel) — ficha
    - archivo: `apps/people/views/v6_detail.py` · hereda de `BasePeopleLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:people-log_list`; plantilla `people/detail/people_log.html`
    - ruta: `panel:people-log_detail` → `/panel/people-log/<int:pk>/`
    - fondo: `bg-people-log`
  - `PeopleLogListView` (panel) — lista
    - archivo: `apps/people/views/v5_list.py` · hereda de `BasePeopleLog`, `AdminListView`
    - depende de: datos de `panel:people-log_data`
    - ruta: `panel:people-log_list` → `/panel/people-log/`
    - fondo: `bg-people-log`
  - `PeopleLogUpdateView` (panel) — edición
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePeopleLog`, `BaseUpdate`
    - depende de: formulario `PeopleLogForm`; vuelve a `panel:people-log_list`; al guardar va a `panel:people-log_list`
    - ruta: `panel:people-log_update` → `/panel/people-log/<int:pk>/update/`
    - fondo: `bg-people-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `PeopleLogDataView`

### Modelo: `Person` (`apps/people/models.py`)

- Formulario: `PersonForm` (`apps/people/forms.py`) — campos: `full_name`, `biography`, `birth_date`, `country`, `is_active`
- Vistas:
  - `PersonCreateView` (panel) — alta
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePerson`, `BaseCreate`
    - depende de: formulario `PersonForm`; vuelve a `panel:person_list`; al guardar va a `panel:person_list`; plantilla `people/form/person.html`
    - ruta: `panel:person_create` → `/panel/person/create/`
    - fondo: `bg-people-person`
  - `PersonDataView` (panel) — datos JSON de la lista
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePersonContext`, `AdminDataView`
    - ruta: `panel:person_data` → `/panel/person/data/`, `panel:person_data-by` → `/panel/person/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `voces-anime` → padre por id (campo `otaku.Anime`); `equipo-anime` → padre por id (campo `otaku.Anime`); `autores-manga` → padre por id (campo `otaku.Manga`); `voces-personaje` → padre por id (campo `otaku.Character`); `pais` → padre por id (campo `country`); `integrantes-artista` → padre por id (campo `music.Artist`)
    - fondo: `bg-people-person`
  - `PersonDeleteView` (panel) — borrado
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePerson`, `BaseDelete`
    - depende de: vuelve a `panel:person_list`; al guardar va a `panel:person_list`
    - ruta: `panel:person_delete` → `/panel/person/<int:pk>/delete/`
    - fondo: `bg-people-person`
  - `PersonDetailView` (panel) — ficha
    - archivo: `apps/people/views/v6_detail.py` · hereda de `BasePerson`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:person_list`; plantilla `people/detail/person.html`
    - ruta: `panel:person_detail` → `/panel/person/<int:pk>/`
    - fondo: `bg-people-person`
  - `PersonListByView` (panel) — lista «por» (acotada a un padre) — voces-anime, equipo-anime, autores-manga, voces-personaje, pais, integrantes-artista.
    - archivo: `apps/people/views/v5_list_by.py` · hereda de `BasePersonContext`, `AdminListByView`
    - depende de: datos de `panel:person_data-by`
    - ruta: `panel:person_by` → `/panel/person/<str:tipo>/<str:pk>/`
    - mapa «by»: `voces-anime` → padre por id (campo `otaku.Anime`); `equipo-anime` → padre por id (campo `otaku.Anime`); `autores-manga` → padre por id (campo `otaku.Manga`); `voces-personaje` → padre por id (campo `otaku.Character`); `pais` → padre por id (campo `country`); `integrantes-artista` → padre por id (campo `music.Artist`)
    - fondo: `bg-people-person`
  - `PersonListView` (panel) — lista
    - archivo: `apps/people/views/v5_list.py` · hereda de `BasePerson`, `AdminListView`
    - depende de: datos de `panel:person_data`
    - ruta: `panel:person_list` → `/panel/person/`
    - fondo: `bg-people-person`
  - `PersonPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePersonContext`, `PublicDataView`
    - ruta: `personas:catalogo-data` → `/catalog/people/list/data/`, `personas:por-data` → `/catalog/people/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `voces-anime` → padre por id (campo `otaku.Anime`); `equipo-anime` → padre por id (campo `otaku.Anime`); `autores-manga` → padre por id (campo `otaku.Manga`); `voces-personaje` → padre por id (campo `otaku.Character`); `pais` → padre por id (campo `country`); `integrantes-artista` → padre por id (campo `music.Artist`)
    - fondo: `bg-people-person`
  - `PersonPublicDetailView` (pública) — ficha — Ficha pública de una persona: el mismo HTML que en gestión, sin botones y con la colección.
    - archivo: `apps/people/views/v6_detail.py` · hereda de `BasePerson`, `BasePublicDetailView`
    - depende de: vuelve a `personas:catalogo`; plantilla `people/detail/person.html`
    - ruta: `personas:detalle` → `/catalog/people/<int:pk>/<slug:slug>/`, `personas:detalle` → `/catalog/people/<int:pk>/`
    - fondo: `bg-people-person`
  - `PersonPublicListByView` (pública) — lista «por» (acotada a un padre) — voces-anime, equipo-anime, autores-manga, voces-personaje, pais, integrantes-artista.
    - archivo: `apps/people/views/v5_list_by.py` · hereda de `BasePersonContext`, `PublicListByView`
    - depende de: datos de `personas:por-data`; plantilla `public/list.html`
    - ruta: `personas:por` → `/catalog/people/<str:tipo>/<int:pk>/`, `personas:por` → `/catalog/people/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `voces-anime` → padre por id (campo `otaku.Anime`); `equipo-anime` → padre por id (campo `otaku.Anime`); `autores-manga` → padre por id (campo `otaku.Manga`); `voces-personaje` → padre por id (campo `otaku.Character`); `pais` → padre por id (campo `country`); `integrantes-artista` → padre por id (campo `music.Artist`)
    - fondo: `bg-people-person`
  - `PersonPublicListView` (pública) — lista — Catálogo público de personas (actores, directores, autores…).
    - archivo: `apps/people/views/v5_list.py` · hereda de `BasePerson`, `PublicListView`
    - depende de: datos de `personas:catalogo-data`; plantilla `public/list.html`
    - ruta: `personas:catalogo` → `/catalog/people/list/`
    - fondo: `bg-people-person`
  - `PersonSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePerson`, `BaseSelectView`
    - ruta: `panel:person_select` → `/panel/person/select/`
    - fondo: `bg-people-person`
  - `PersonUpdateView` (panel) — edición
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePerson`, `BaseUpdate`
    - depende de: formulario `PersonForm`; vuelve a `panel:person_list`; al guardar va a `panel:person_list`; plantilla `people/form/person.html`
    - ruta: `panel:person_update` → `/panel/person/<int:pk>/update/`
    - fondo: `bg-people-person`
- Filtros:
  - `PersonAdminFilters`: Activo (`is_active`), País (`country`), Año de nacimiento (`birth_date`) — para `PersonDataView`
  - `PersonFilters`: País (`country`), Año de nacimiento (`birth_date`) — para `PersonPublicDataView`

### Modelo: `PersonImage` (`apps/people/models.py`)

- Formulario: `PersonImageForm` (`apps/people/forms.py`) — campos: `person`, `order`, `image`, `image_url`, `is_active`
- Vistas:
  - `PersonImageCreateView` (panel) — alta
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePersonImage`, `BaseCreate`
    - depende de: formulario `PersonImageForm`; vuelve a `panel:person-image_list`; al guardar va a `panel:person-image_list`; plantilla `people/form/person_image.html`
    - ruta: `panel:person-image_create` → `/panel/person-image/create/`
    - fondo: `bg-people-person-image`
  - `PersonImageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePersonImageContext`, `AdminDataView`
    - ruta: `panel:person-image_data` → `/panel/person-image/data/`, `panel:person-image_data-by` → `/panel/person-image/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-people-person-image`
  - `PersonImageDeleteView` (panel) — borrado
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePersonImage`, `BaseDelete`
    - depende de: vuelve a `panel:person-image_list`; al guardar va a `panel:person-image_list`
    - ruta: `panel:person-image_delete` → `/panel/person-image/<int:pk>/delete/`
    - fondo: `bg-people-person-image`
  - `PersonImageDetailView` (panel) — ficha
    - archivo: `apps/people/views/v6_detail.py` · hereda de `BasePersonImage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:person-image_list`; plantilla `people/detail/person_image.html`
    - ruta: `panel:person-image_detail` → `/panel/person-image/<int:pk>/`
    - fondo: `bg-people-person-image`
  - `PersonImageListByView` (panel) — lista «por» (acotada a un padre) — persona.
    - archivo: `apps/people/views/v5_list_by.py` · hereda de `BasePersonImageContext`, `AdminListByView`
    - depende de: datos de `panel:person-image_data-by`
    - ruta: `panel:person-image_by` → `/panel/person-image/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-people-person-image`
  - `PersonImageListView` (panel) — lista
    - archivo: `apps/people/views/v5_list.py` · hereda de `BasePersonImage`, `AdminListView`
    - depende de: datos de `panel:person-image_data`
    - ruta: `panel:person-image_list` → `/panel/person-image/`
    - fondo: `bg-people-person-image`
  - `PersonImagePublicListByView` (pública) — lista «por» (acotada a un padre) — persona.
    - archivo: `apps/people/views/v5_list_by.py` · hereda de `BasePersonImageContext`, `PublicListByView`
    - depende de: datos de `personas:imagenes-por-data`; plantilla `public/list.html`
    - ruta: `personas:imagenes-por` → `/catalog/people/images/<str:tipo>/<int:pk>/`, `personas:imagenes-por` → `/catalog/people/images/<str:tipo>/<int:pk>/<slug:slug>/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-people-person`
  - `PersonImageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePersonImage`, `BaseSelectView`
    - ruta: `panel:person-image_select` → `/panel/person-image/select/`
    - fondo: `bg-people-person-image`
  - `PersonImageUpdateView` (panel) — edición
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePersonImage`, `BaseUpdate`
    - depende de: formulario `PersonImageForm`; vuelve a `panel:person-image_list`; al guardar va a `panel:person-image_list`; plantilla `people/form/person_image.html`
    - ruta: `panel:person-image_update` → `/panel/person-image/<int:pk>/update/`
    - fondo: `bg-people-person-image`
  - `PersonImagesPublicDataView` (panel) — datos JSON de la lista (sPublic) — Galería de un persona: sus imágenes en tarjetas.
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePersonImageContext`, `PublicDataView`
    - ruta: `personas:imagenes-por-data` → `/catalog/people/images/<str:tipo>/<int:pk>/data/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-people-person-image`

### Modelo: `PersonLink` (`apps/people/models.py`)

Enlace externo de una persona (sitio oficial, X, Instagram, Wikipedia…), calcado de `games.CreatorLink`: `person`,
`source` (catálogo `ExternalSource`), `external_id` y `url`; único por (persona, fuente, id externo).
`PersonLinkForm`; `PersonLinkListView` → `PersonLinkDataView`, `PersonLinkSelectView`, alta, edición, borrado, ficha
y la lista «por persona» (`PersonLinkListByView`, tipo `persona`). Rutas `panel:person-link_*`. Tarjeta «Enlaces» en el
home de Personas y en el sidebar. Fondo `bg-people-person-link`.

### Modelo: `PersonNickname` (`apps/people/models.py`)

- Formulario: `PersonNicknameForm` (`apps/people/forms.py`) — campos: `person`, `nickname`, `is_active`
- Vistas:
  - `PersonNicknameCreateView` (panel) — alta
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePersonNickname`, `BaseCreate`
    - depende de: formulario `PersonNicknameForm`; vuelve a `panel:person-nickname_list`; al guardar va a `panel:person-nickname_list`; plantilla `people/form/person_nickname.html`
    - ruta: `panel:person-nickname_create` → `/panel/person-nickname/create/`
    - fondo: `bg-people-person-nickname`
  - `PersonNicknameDataView` (panel) — datos JSON de la lista
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePersonNicknameContext`, `AdminDataView`
    - ruta: `panel:person-nickname_data` → `/panel/person-nickname/data/`, `panel:person-nickname_data-by` → `/panel/person-nickname/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-people-person-nickname`
  - `PersonNicknameDeleteView` (panel) — borrado
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePersonNickname`, `BaseDelete`
    - depende de: vuelve a `panel:person-nickname_list`; al guardar va a `panel:person-nickname_list`
    - ruta: `panel:person-nickname_delete` → `/panel/person-nickname/<int:pk>/delete/`
    - fondo: `bg-people-person-nickname`
  - `PersonNicknameDetailView` (panel) — ficha
    - archivo: `apps/people/views/v6_detail.py` · hereda de `BasePersonNickname`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:person-nickname_list`; plantilla `people/detail/person_nickname.html`
    - ruta: `panel:person-nickname_detail` → `/panel/person-nickname/<int:pk>/`
    - fondo: `bg-people-person-nickname`
  - `PersonNicknameListByView` (panel) — lista «por» (acotada a un padre) — persona.
    - archivo: `apps/people/views/v5_list_by.py` · hereda de `BasePersonNicknameContext`, `AdminListByView`
    - depende de: datos de `panel:person-nickname_data-by`
    - ruta: `panel:person-nickname_by` → `/panel/person-nickname/<str:tipo>/<str:pk>/`
    - mapa «by»: `persona` → padre por id (campo `person`)
    - fondo: `bg-people-person-nickname`
  - `PersonNicknameListView` (panel) — lista
    - archivo: `apps/people/views/v5_list.py` · hereda de `BasePersonNickname`, `AdminListView`
    - depende de: datos de `panel:person-nickname_data`
    - ruta: `panel:person-nickname_list` → `/panel/person-nickname/`
    - fondo: `bg-people-person-nickname`
  - `PersonNicknameSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/people/views/v3_data.py` · hereda de `BasePersonNickname`, `BaseSelectView`
    - ruta: `panel:person-nickname_select` → `/panel/person-nickname/select/`
    - fondo: `bg-people-person-nickname`
  - `PersonNicknameUpdateView` (panel) — edición
    - archivo: `apps/people/views/v4_write.py` · hereda de `BasePersonNickname`, `BaseUpdate`
    - depende de: formulario `PersonNicknameForm`; vuelve a `panel:person-nickname_list`; al guardar va a `panel:person-nickname_list`; plantilla `people/form/person_nickname.html`
    - ruta: `panel:person-nickname_update` → `/panel/person-nickname/<int:pk>/update/`
    - fondo: `bg-people-person-nickname`

### Sin modelo

- `CinePersonPublicDataView`
  - archivo: `apps/people/views/v3_data.py` · hereda de `PersonPublicDataView` · ruta: `personas:cine-catalogo-data` → `/catalog/people/cinema/list/data/` · fondo `bg-people-person`
- `CinePersonPublicListView`
  - archivo: `apps/people/views/v5_list.py` · hereda de `BasePerson`, `PublicListView` · ruta: `personas:cine-catalogo` → `/catalog/people/cinema/list/` · fondo `bg-people-person`
- `OtakuPersonPublicDataView`
  - archivo: `apps/people/views/v3_data.py` · hereda de `PersonPublicDataView` · ruta: `personas:otaku-catalogo-data` → `/catalog/people/otaku/list/data/` · fondo `bg-people-person`
- `OtakuPersonPublicListView`
  - archivo: `apps/people/views/v5_list.py` · hereda de `BasePerson`, `PublicListView` · ruta: `personas:otaku-catalogo` → `/catalog/people/otaku/list/` · fondo `bg-otaku-person`
- `PeopleHomeView`
  - archivo: `apps/people/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:people-home` → `/panel/people/` · fondo `bg-people-home`
- `PeoplePublicHomeView` — Landing de PERSONAS (`personas:home`, como games/movies): resumen global
  - archivo: `apps/people/views/v1_home.py` · hereda de `BasePublicHomeView` · ruta: `personas:home` → `/catalog/people/` · fondo `bg-people-home`
- `TvPersonPublicDataView`
  - archivo: `apps/people/views/v3_data.py` · hereda de `PersonPublicDataView` · ruta: `personas:tv-catalogo-data` → `/catalog/people/tv/list/data/` · fondo `bg-people-person`
- `TvPersonPublicListView`
  - archivo: `apps/people/views/v5_list.py` · hereda de `BasePerson`, `PublicListView` · ruta: `personas:tv-catalogo` → `/catalog/people/tv/list/` · fondo `bg-people-person`
- `VoicePersonPublicDataView`
  - archivo: `apps/people/views/v3_data.py` · hereda de `PersonPublicDataView` · ruta: `personas:voces-catalogo-data` → `/catalog/people/voices/list/data/` · fondo `bg-people-person`
- `VoicePersonPublicListView`
  - archivo: `apps/people/views/v5_list.py` · hereda de `BasePerson`, `PublicListView` · ruta: `personas:voces-catalogo` → `/catalog/people/voices/list/` · fondo `bg-otaku-person`

## Usuarios (`users`)

### Modelo: `CustomUser` (`apps/users/models.py`)

- Formulario: `CustomUserForm` (`apps/users/forms.py`) — campos: `username`, `email`, `first_name`, `last_name`, `phone`, `birth_date`, `is_active`, `is_staff`
- Vistas:
  - `CustomUserCreateView` (panel) — alta
    - archivo: `apps/users/views/v4_write.py` · hereda de `SuperuserRequiredMixin`, `BaseCustomUser`, `BaseCreate`
    - depende de: formulario `CustomUserForm`; vuelve a `panel:user_list`; al guardar va a `panel:user_list`; plantilla `users/form/custom_user.html`
    - ruta: `panel:user_create` → `/panel/user/create/`
    - fondo: `bg-users-user`
  - `CustomUserDataView` (panel) — datos JSON de la lista
    - archivo: `apps/users/views/v3_data.py` · hereda de `BaseCustomUser`, `AdminDataView`
    - ruta: `panel:user_data` → `/panel/user/data/`
    - fondo: `bg-users-user`
  - `CustomUserDeleteView` (panel) — borrado
    - archivo: `apps/users/views/v4_write.py` · hereda de `SuperuserRequiredMixin`, `BaseCustomUser`, `BaseDelete`
    - depende de: vuelve a `panel:user_list`; al guardar va a `panel:user_list`
    - ruta: `panel:user_delete` → `/panel/user/<int:pk>/delete/`
    - fondo: `bg-users-user`
  - `CustomUserDetailView` (panel) — ficha
    - archivo: `apps/users/views/v6_detail.py` · hereda de `BaseCustomUser`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:user_list`
    - ruta: `panel:user_detail` → `/panel/user/<int:pk>/`
    - fondo: `bg-users-user`
  - `CustomUserListView` (panel) — lista
    - archivo: `apps/users/views/v5_list.py` · hereda de `BaseCustomUser`, `AdminListView`
    - depende de: datos de `panel:user_data`
    - ruta: `panel:user_list` → `/panel/user/`
    - fondo: `bg-users-user`
  - `CustomUserSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/users/views/v3_data.py` · hereda de `BaseCustomUser`, `BaseSelectView`
    - ruta: `panel:user_select` → `/panel/user/select/`
    - fondo: `bg-users-user`
  - `CustomUserUpdateView` (panel) — edición
    - archivo: `apps/users/views/v4_write.py` · hereda de `SuperuserRequiredMixin`, `BaseCustomUser`, `BaseUpdate`
    - depende de: formulario `UserUpdateForm`; vuelve a `panel:user_list`; al guardar va a `panel:user_list`; plantilla `users/form/custom_user.html`
    - ruta: `panel:user_update` → `/panel/user/<int:pk>/update/`
    - fondo: `bg-users-user`

### Modelo: `UserActivity` (`apps/users/models.py`)

- Formulario: `UserActivityForm` (`apps/users/forms.py`) — campos: `user`, `action`, `content_type`, `object_id`, `label`, `is_active`
- Vistas:
  - `UserActivityCreateView` (panel) — alta
    - archivo: `apps/users/views/v4_write.py` · hereda de `BaseUserActivity`, `BaseCreate`
    - depende de: formulario `UserActivityForm`; vuelve a `panel:user-activity_list`; al guardar va a `panel:user-activity_list`
    - ruta: `panel:user-activity_create` → `/panel/user-activity/create/`
    - fondo: `bg-users-user-activity`
  - `UserActivityDataView` (panel) — datos JSON de la lista — Actividad de los usuarios (lo que HACEN): filtrable por usuario (?user=<id>).
    - archivo: `apps/users/views/v3_data.py` · hereda de `BaseUserActivity`, `AdminDataView`
    - ruta: `panel:user-activity_data` → `/panel/user-activity/data/`
    - fondo: `bg-users-user-activity`
  - `UserActivityDeleteView` (panel) — borrado
    - archivo: `apps/users/views/v4_write.py` · hereda de `BaseUserActivity`, `BaseSoftDelete`
    - depende de: vuelve a `panel:user-activity_list`; al guardar va a `panel:user-activity_list`
    - ruta: `panel:user-activity_delete` → `/panel/user-activity/<int:pk>/delete/`
    - fondo: `bg-users-user-activity`
  - `UserActivityDetailView` (panel) — ficha
    - archivo: `apps/users/views/v6_detail.py` · hereda de `BaseUserActivity`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:user-activity_list`
    - ruta: `panel:user-activity_detail` → `/panel/user-activity/<int:pk>/`
    - fondo: `bg-users-user-activity`
  - `UserActivityListView` (panel) — lista
    - archivo: `apps/users/views/v5_list.py` · hereda de `BaseUserActivity`, `AdminListView`
    - depende de: datos de `panel:user-activity_data`; plantilla `users/usuario_log_list.html`
    - ruta: `panel:user-activity_list` → `/panel/user-activity/`
    - fondo: `bg-users-user-activity`
  - `UserActivityUpdateView` (panel) — edición
    - archivo: `apps/users/views/v4_write.py` · hereda de `BaseUserActivity`, `BaseUpdate`
    - depende de: formulario `UserActivityForm`; vuelve a `panel:user-activity_list`; al guardar va a `panel:user-activity_list`
    - ruta: `panel:user-activity_update` → `/panel/user-activity/<int:pk>/update/`
    - fondo: `bg-users-user-activity`
- Filtros:
  - `ActividadFilters`: Activo (`is_active`), Acción (`action`) — para `UserActivityDataView`

### Modelo: `UserLog` (`apps/users/models.py`)

- Formulario: `UserLogForm` (`apps/users/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `UserLogCreateView` (panel) — alta
    - archivo: `apps/users/views/v4_write.py` · hereda de `BaseUserLog`, `BaseCreate`
    - depende de: formulario `UserLogForm`; vuelve a `panel:user-log_list`; al guardar va a `panel:user-log_list`
    - ruta: `panel:user-log_create` → `/panel/user-log/create/`
    - fondo: `bg-users-logs`
  - `UserLogDataView` (panel) — datos JSON de la lista — Log de usuarios (lo que le pasa al SISTEMA con las cuentas).
    - archivo: `apps/users/views/v3_data.py` · hereda de `BaseUserLog`, `AdminDataView`
    - ruta: `panel:user-log_data` → `/panel/user-log/data/`
    - fondo: `bg-users-logs`
  - `UserLogDeleteView` (panel) — borrado
    - archivo: `apps/users/views/v4_write.py` · hereda de `BaseUserLog`, `BaseDelete`
    - depende de: vuelve a `panel:user-log_list`; al guardar va a `panel:user-log_list`
    - ruta: `panel:user-log_delete` → `/panel/user-log/<int:pk>/delete/`
    - fondo: `bg-users-logs`
  - `UserLogDetailView` (panel) — ficha
    - archivo: `apps/users/views/v6_detail.py` · hereda de `BaseUserLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:user-log_list`; plantilla `users/detail/user_log.html`
    - ruta: `panel:user-log_detail` → `/panel/user-log/<int:pk>/`
    - fondo: `bg-users-logs`
  - `UserLogListView` (panel) — lista
    - archivo: `apps/users/views/v5_list.py` · hereda de `BaseUserLog`, `AdminListView`
    - depende de: datos de `panel:user-log_data`
    - ruta: `panel:user-log_list` → `/panel/user-log/`
    - fondo: `bg-users-logs-full`
  - `UserLogUpdateView` (panel) — edición
    - archivo: `apps/users/views/v4_write.py` · hereda de `BaseUserLog`, `BaseUpdate`
    - depende de: formulario `UserLogForm`; vuelve a `panel:user-log_list`; al guardar va a `panel:user-log_list`
    - ruta: `panel:user-log_update` → `/panel/user-log/<int:pk>/update/`
    - fondo: `bg-users-logs`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `UserLogDataView`

### Sin modelo

- `LoginView`
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `LoginView` · ruta: `users:login` → `/account/login/` · fondo `bg-users-user`
- `LogoutView` — Cierra sesión y redirige a LOGOUT_REDIRECT_URL.
  - archivo: `apps/users/views/v8_actions.py` · hereda de `LogoutView` · ruta: `users:logout` → `/account/logout/`
- `MyActivityPublicDataView` — Endpoint JSON server-side (protocolo DataTables) de Mi actividad: busca, ordena y pagina en BD SOLO la
  - archivo: `apps/users/views/v8_actions.py` · hereda de `LoginRequiredMixin`, `View` · ruta: `users:perfil_actividad_data` → `/account/profile/activity/data/`
- `MyActivityView` — SHELL de Mi actividad: las filas las trae DataTables por AJAX desde
  - archivo: `apps/users/views/v8_actions.py` · hereda de `BaseActivity`, `LoginRequiredMixin`, `TemplateView` · ruta: `users:perfil_actividad` → `/account/profile/activity/` · fondo `bg-users-logs`
- `PasswordChangeView` — Cambio de clave del PROPIO usuario (desde el perfil): pide la ACTUAL y la
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `PasswordChangeView` · ruta: `users:password_change` → `/account/profile/password/` · fondo `bg-users-user`
- `PasswordResetCompleteView` — 4) "Listo, ya puedes entrar".
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `PasswordResetCompleteView` · ruta: `users:password_reset_complete` → `/account/reset/done/` · fondo `bg-users-user`
- `PasswordResetConfirmView` — 3) Define la nueva contraseña (desde el enlace del correo).
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `PasswordResetConfirmView` · ruta: `users:password_reset_confirm` → `/account/reset/<uidb64>/<token>/` · fondo `bg-users-user`
- `PasswordResetDoneView` — 2) "Revisa tu correo".
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `PasswordResetDoneView` · ruta: `users:password_reset_done` → `/account/recover/sent/` · fondo `bg-users-user`
- `PasswordResetView` — 1) Pide el correo y envía el enlace.
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `PasswordResetView` · ruta: `users:password_reset` → `/account/recover/` · fondo `bg-users-user`
- `ProfileUpdateView` — Edición del propio perfil (misma página no; página aparte, patrón CRUD).
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `LoginRequiredMixin`, `UpdateView` · ruta: `users:perfil_editar` → `/account/profile/edit/` · fondo `bg-users-user`
- `ProfileView`
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `LoginRequiredMixin`, `TemplateView` · ruta: `users:perfil` → `/account/profile/` · fondo `bg-users-user`
- `RegisterView`
  - archivo: `apps/users/views/v8_actions.py` · hereda de `_CuentaPage`, `CreateView` · ruta: `users:registro` → `/account/register/` · fondo `bg-users-user`
- `UserResetPasswordView` — Fija una nueva contraseña al usuario y la MUESTRA una vez (no hay correo).
  - archivo: `apps/users/views/v4_write.py` · hereda de `SuperuserRequiredMixin`, `BaseCustomUser`, `View` · ruta: `panel:user_reset` → `/panel/user/<int:pk>/reset/` · fondo `bg-users-user`
- `UsersHomeView`
  - archivo: `apps/users/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:users-home` → `/panel/users/` · fondo `bg-users-home`
- Form `LoginForm`
- Form `PasswordChangeCustomForm`
- Form `ProfileForm`
- Form `RegisterForm`
- Form `ResetRequestForm`
- Form `SetPasswordCustomForm`
- Form `UserUpdateForm`

## Sistema (`system`)

### Modelo: `CloudFile` (`apps/system/models.py`)

- Formulario: `CloudFileForm` (`apps/system/forms.py`) — campos: `name`, `size`
- Vistas:
  - `CloudFileCreateView` (panel) — alta
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseCloudFile`, `BaseCreate`
    - depende de: formulario `CloudFileForm`; vuelve a `panel:cloud-file_list`; al guardar va a `panel:cloud-file_list`
    - ruta: `panel:cloud-file_create` → `/panel/cloud-file/create/`
    - fondo: `bg-system-cloud-file`
  - `CloudFileDataView` (panel) — datos JSON de la lista
    - archivo: `apps/system/views/v3_data.py` · hereda de `BaseCloudFile`, `AdminDataView`
    - ruta: `panel:cloud-file_data` → `/panel/cloud-file/data/`
    - fondo: `bg-system-cloud-file`
  - `CloudFileDeleteView` (panel) — borrado
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseCloudFile`, `BaseDelete`
    - depende de: vuelve a `panel:cloud-file_list`; al guardar va a `panel:cloud-file_list`
    - ruta: `panel:cloud-file_delete` → `/panel/cloud-file/<int:pk>/delete/`
    - fondo: `bg-system-cloud-file`
  - `CloudFileDetailView` (panel) — ficha
    - archivo: `apps/system/views/v6_detail.py` · hereda de `BaseCloudFile`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:cloud-file_list`; plantilla `system/detail/cloud_file.html`
    - ruta: `panel:cloud-file_detail` → `/panel/cloud-file/<int:pk>/`
    - fondo: `bg-system-cloud-file`
  - `CloudFileListView` (panel) — lista — Archivos de media que YA están en R2 (los anota la tarea de subida). Borrar una fila hace que
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseCloudFile`, `AdminListView`
    - depende de: datos de `panel:cloud-file_data`
    - ruta: `panel:cloud-file_list` → `/panel/cloud-file/`
    - fondo: `bg-system-cloud-file`
  - `CloudFileUpdateView` (panel) — edición
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseCloudFile`, `BaseUpdate`
    - depende de: formulario `CloudFileForm`; vuelve a `panel:cloud-file_list`; al guardar va a `panel:cloud-file_list`
    - ruta: `panel:cloud-file_update` → `/panel/cloud-file/<int:pk>/update/`
    - fondo: `bg-system-cloud-file`

### Modelo: `ImportCursor` (`apps/system/models.py`)

- Formulario: `ImportCursorForm` (`apps/system/forms.py`) — campos: `source`, `type`, `next_id`, `batch_size`
- Vistas:
  - `ImportCursorCreateView` (panel) — alta
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseImportCursor`, `BaseCreate`
    - depende de: formulario `ImportCursorForm`; vuelve a `panel:import-cursor_list`; al guardar va a `panel:import-cursor_list`
    - ruta: `panel:import-cursor_create` → `/panel/import-cursor/create/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorDataView` (panel) — datos JSON de la lista
    - archivo: `apps/system/views/v3_data.py` · hereda de `BaseImportCursor`, `AdminDataView`
    - ruta: `panel:import-cursor_data` → `/panel/import-cursor/data/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorDeezerDataView` (panel) — datos JSON de la lista fija: source='deezer'
    - archivo: `apps/system/views/v3_data.py` · hereda de `ImportCursorDataView`
    - ruta: `panel:import-cursor-deezer_data` → `/panel/import-cursor-deezer/data/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorDeezerListView` (panel) — lista fija: source='deezer'
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseImportCursor`, `AdminListView`
    - depende de: datos de `panel:import-cursor-deezer_data`
    - ruta: `panel:import-cursor-deezer_list` → `/panel/import-cursor-deezer/`
    - fondo: `bg-system-import-cursor-deezer`
  - `ImportCursorDeleteView` (panel) — borrado
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseImportCursor`, `BaseSoftDelete`
    - depende de: vuelve a `panel:import-cursor_list`; al guardar va a `panel:import-cursor_list`
    - ruta: `panel:import-cursor_delete` → `/panel/import-cursor/<int:pk>/delete/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorDetailView` (panel) — ficha
    - archivo: `apps/system/views/v6_detail.py` · hereda de `BaseImportCursor`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:import-cursor_list`; plantilla `system/detail/import_cursor.html`
    - ruta: `panel:import-cursor_detail` → `/panel/import-cursor/<int:pk>/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorLaunchView` (panel) — LaunchView — «Lanzar lote ahora» desde el cursor: encola el siguiente lote de esa fuente y tipo con la cantidad de
    - archivo: `apps/system/views/v8_actions.py` · hereda de `BasePage`, `BaseImportCursor`, `TemplateView`
    - ruta: `panel:import-cursor_launch` → `/panel/import-cursor/<int:pk>/lanzar/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorListView` (panel) — lista — Por dónde va el lote de cada fuente y tipo. Se crean solos al primer lote; aquí se corrigen.
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseImportCursor`, `AdminListView`
    - depende de: datos de `panel:import-cursor_data`
    - ruta: `panel:import-cursor_list` → `/panel/import-cursor/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorMalDataView` (panel) — datos JSON de la lista fija: source='mal'
    - archivo: `apps/system/views/v3_data.py` · hereda de `ImportCursorDataView`
    - ruta: `panel:import-cursor-mal_data` → `/panel/import-cursor-mal/data/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorMalListView` (panel) — lista fija: source='mal'
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseImportCursor`, `AdminListView`
    - depende de: datos de `panel:import-cursor-mal_data`
    - ruta: `panel:import-cursor-mal_list` → `/panel/import-cursor-mal/`
    - fondo: `bg-system-import-cursor-mal`
  - `ImportCursorUpdateView` (panel) — edición
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseImportCursor`, `BaseUpdate`
    - depende de: formulario `ImportCursorForm`; vuelve a `panel:import-cursor_list`; al guardar va a `panel:import-cursor_list`
    - ruta: `panel:import-cursor_update` → `/panel/import-cursor/<int:pk>/update/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorVndbDataView` (panel) — datos JSON de la lista fija: source='vndb'
    - archivo: `apps/system/views/v3_data.py` · hereda de `ImportCursorDataView`
    - ruta: `panel:import-cursor-vndb_data` → `/panel/import-cursor-vndb/data/`
    - fondo: `bg-system-import-cursor`
  - `ImportCursorVndbListView` (panel) — lista fija: source='vndb'
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseImportCursor`, `AdminListView`
    - depende de: datos de `panel:import-cursor-vndb_data`
    - ruta: `panel:import-cursor-vndb_list` → `/panel/import-cursor-vndb/`
    - fondo: `bg-system-import-cursor-vndb`

### Modelo: `ScheduledTask` (`apps/system/models.py`)

- Formulario: `ScheduledTaskForm` (`apps/system/forms.py`) — campos: `name`, `task`, `args`, `kwargs`, `every_minutes`, `at_time`, `is_active`
- Vistas:
  - `ScheduledTaskCreateView` (panel) — alta
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseScheduledTask`, `BaseCreate`
    - depende de: formulario `ScheduledTaskForm`; vuelve a `panel:scheduled-task_list`; al guardar va a `panel:scheduled-task_list`
    - ruta: `panel:scheduled-task_create` → `/panel/scheduled-task/create/`
    - fondo: `bg-system-scheduled-task`
  - `ScheduledTaskDataView` (panel) — datos JSON de la lista
    - archivo: `apps/system/views/v3_data.py` · hereda de `BaseScheduledTask`, `AdminDataView`
    - ruta: `panel:scheduled-task_data` → `/panel/scheduled-task/data/`
    - fondo: `bg-system-scheduled-task`
  - `ScheduledTaskDeleteView` (panel) — borrado
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseScheduledTask`, `BaseDelete`
    - depende de: vuelve a `panel:scheduled-task_list`; al guardar va a `panel:scheduled-task_list`
    - ruta: `panel:scheduled-task_delete` → `/panel/scheduled-task/<int:pk>/delete/`
    - fondo: `bg-system-scheduled-task`
  - `ScheduledTaskDetailView` (panel) — ficha
    - archivo: `apps/system/views/v6_detail.py` · hereda de `BaseScheduledTask`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:scheduled-task_list`; plantilla `system/detail/scheduled_task.html`
    - ruta: `panel:scheduled-task_detail` → `/panel/scheduled-task/<int:pk>/`
    - fondo: `bg-system-scheduled-task`
  - `ScheduledTaskListView` (panel) — lista
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseScheduledTask`, `AdminListView`
    - depende de: datos de `panel:scheduled-task_data`
    - ruta: `panel:scheduled-task_list` → `/panel/scheduled-task/`
    - fondo: `bg-system-scheduled-task`
  - `ScheduledTaskRunView` (panel) — RunView — «Ejecutar ahora»: encola la tarea programada en este momento con sus argumentos y su cantidad,
    - archivo: `apps/system/views/v8_actions.py` · hereda de `BasePage`, `BaseScheduledTask`, `TemplateView`
    - ruta: `panel:scheduled-task_run` → `/panel/scheduled-task/<int:pk>/ejecutar/`
    - fondo: `bg-system-scheduled-task`
  - `ScheduledTaskUpdateView` (panel) — edición
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseScheduledTask`, `BaseUpdate`
    - depende de: formulario `ScheduledTaskForm`; vuelve a `panel:scheduled-task_list`; al guardar va a `panel:scheduled-task_list`
    - ruta: `panel:scheduled-task_update` → `/panel/scheduled-task/<int:pk>/update/`
    - fondo: `bg-system-scheduled-task`

### Modelo: `TaskRun` (`apps/system/models.py`)

- Formulario: `TaskRunForm` (`apps/system/forms.py`) — campos: `task_id`, `name`, `args`, `status`, `cancel_requested`, `result`, `user`, `started_at`, `finished_at`
- Vistas:
  - `TaskRunCancelView` (panel) — CancelView
    - archivo: `apps/system/views/v8_actions.py` · hereda de `BaseAccionTarea`
    - ruta: `panel:task-run_cancel` → `/panel/task-run/<int:pk>/cancelar/`
    - fondo: `bg-system-task-run`
  - `TaskRunCreateView` (panel) — alta
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseTaskRun`, `BaseCreate`
    - depende de: formulario `TaskRunForm`; vuelve a `panel:task-run_list`; al guardar va a `panel:task-run_list`
    - ruta: `panel:task-run_create` → `/panel/task-run/create/`
    - fondo: `bg-system-task-run`
  - `TaskRunDataView` (panel) — datos JSON de la lista
    - archivo: `apps/system/views/v3_data.py` · hereda de `BaseTaskRunContext`, `AdminDataView`
    - ruta: `panel:task-run_data` → `/panel/task-run/data/`, `panel:task-run_data-by` → `/panel/task-run/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `status` → choice: `queued`, `running`, `done`, `failed`, `cancelled`
    - fondo: `bg-system-task-run`
  - `TaskRunDeleteView` (panel) — borrado
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseTaskRun`, `BaseDelete`
    - depende de: vuelve a `panel:task-run_list`; al guardar va a `panel:task-run_list`
    - ruta: `panel:task-run_delete` → `/panel/task-run/<int:pk>/delete/`
    - fondo: `bg-system-task-run`
  - `TaskRunDetailView` (panel) — ficha
    - archivo: `apps/system/views/v6_detail.py` · hereda de `BaseTaskRun`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:task-run_list`; plantilla `system/detail/task_run.html`
    - ruta: `panel:task-run_detail` → `/panel/task-run/<int:pk>/`
    - fondo: `bg-system-task-run`
  - `TaskRunFinishView` (panel) — FinishView
    - archivo: `apps/system/views/v8_actions.py` · hereda de `BaseAccionTarea`
    - ruta: `panel:task-run_finish` → `/panel/task-run/<int:pk>/terminar/`
    - fondo: `bg-system-task-run`
  - `TaskRunListByView` (panel) — lista «por» (acotada a un padre) — Lista acotada por el mapa (`/task-run/<tipo>/<valor>/`): la alimenta TaskRunDataView con `/data/<tipo>/<valor>/`.
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseTaskRunContext`, `AdminListByView`
    - depende de: datos de `panel:task-run_data-by`
    - ruta: `panel:task-run_by` → `/panel/task-run/<str:tipo>/<str:pk>/`
    - mapa «by»: `status` → choice: `queued`, `running`, `done`, `failed`, `cancelled`
    - fondo: `bg-system-task-run`
  - `TaskRunListView` (panel) — lista
    - archivo: `apps/system/views/v5_list.py` · hereda de `BaseTaskRun`, `AdminListView`
    - depende de: datos de `panel:task-run_data`
    - ruta: `panel:task-run_list` → `/panel/task-run/`
    - fondo: `bg-system-task-run`
  - `TaskRunUpdateView` (panel) — edición
    - archivo: `apps/system/views/v4_write.py` · hereda de `BaseTaskRun`, `BaseUpdate`
    - depende de: formulario `TaskRunForm`; vuelve a `panel:task-run_list`; al guardar va a `panel:task-run_list`
    - ruta: `panel:task-run_update` → `/panel/task-run/<int:pk>/update/`
    - fondo: `bg-system-task-run`
- Filtros:
  - `TaskRunFilters`: Estado (`status`) — para `TaskRunDataView`

### Sin modelo

- `SystemHomeView`
  - archivo: `apps/system/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:home` → `/panel/` · fondo `bg-system-home`
- `TasksHomeView` — Home de la sección SISTEMA (/panel/tareas/): las tareas programadas (beat) con su
  - archivo: `apps/system/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:tasks-home` → `/panel/tasks/` · fondo `bg-system-tasks-home`

## Correos (`mailing`)

### Modelo: `ContactMessage` (`apps/mailing/models.py`)

- Formulario: `ContactMessageForm` (`apps/mailing/forms.py`) — campos: `status`
- Vistas:
  - `ContactMessageCreateView` (panel) — alta
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseContactMessage`, `BaseCreate`
    - depende de: formulario `ContactMessageForm`; vuelve a `panel:contact-message_list`; al guardar va a `panel:contact-message_list`
    - ruta: `panel:contact-message_create` → `/panel/contact-message/create/`
    - fondo: `bg-mailing-contact-message`
  - `ContactMessageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/mailing/views/v3_data.py` · hereda de `BaseContactMessageContext`, `AdminDataView`
    - ruta: `panel:contact-message_data` → `/panel/contact-message/data/`, `panel:contact-message_data-by` → `/panel/contact-message/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `status` → choice: `nuevo`, `leido`, `respondido`, `archivado`, `spam`
    - fondo: `bg-mailing-contact-message`
  - `ContactMessageDeleteView` (panel) — borrado
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseContactMessage`, `BaseSoftDelete`
    - depende de: vuelve a `panel:contact-message_list`; al guardar va a `panel:contact-message_list`
    - ruta: `panel:contact-message_delete` → `/panel/contact-message/<int:pk>/delete/`
    - fondo: `bg-mailing-contact-message`
  - `ContactMessageDetailView` (panel) — ficha
    - archivo: `apps/mailing/views/v6_detail.py` · hereda de `BaseContactMessage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:contact-message_list`; plantilla `mailing/detail/contact_message.html`
    - ruta: `panel:contact-message_detail` → `/panel/contact-message/<int:pk>/`
    - fondo: `bg-mailing-contact-message`
  - `ContactMessageListByView` (panel) — lista «por» (acotada a un padre) — Lista acotada por el mapa (`/contact-message/<tipo>/<valor>/`): la alimenta ContactMessageDataView con `/data/<tipo>/<valor>/`.
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseContactMessageContext`, `AdminListByView`
    - depende de: datos de `panel:contact-message_data-by`
    - ruta: `panel:contact-message_by` → `/panel/contact-message/<str:tipo>/<str:pk>/`
    - mapa «by»: `status` → choice: `nuevo`, `leido`, `respondido`, `archivado`, `spam`
    - fondo: `bg-mailing-contact-message`
  - `ContactMessageListView` (panel) — lista
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseContactMessage`, `AdminListView`
    - depende de: datos de `panel:contact-message_data`
    - ruta: `panel:contact-message_list` → `/panel/contact-message/`
    - fondo: `bg-mailing-contact-message`
  - `ContactMessageSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/mailing/views/v3_data.py` · hereda de `BaseContactMessage`, `BaseSelectView`
    - ruta: `panel:contact-message_select` → `/panel/contact-message/select/`
    - fondo: `bg-mailing-contact-message`
  - `ContactMessageUpdateView` (panel) — edición
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseContactMessage`, `BaseUpdate`
    - depende de: formulario `ContactMessageForm`; vuelve a `panel:contact-message_list`; al guardar va a `panel:contact-message_list`
    - ruta: `panel:contact-message_update` → `/panel/contact-message/<int:pk>/update/`
    - fondo: `bg-mailing-contact-message`
- Filtros:
  - `ContactMessageFilters`: Estado (`status`), Activo (`is_active`) — para `ContactMessageDataView`

### Modelo: `ContactReply` (`apps/mailing/models.py`)

- Formulario: `ContactReplyForm` (`apps/mailing/forms.py`) — campos: `message`, `body`, `is_active`
- Vistas:
  - `ContactReplyCreateView` (panel) — alta
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseContactReply`, `BaseCreate`
    - depende de: formulario `ContactReplyForm`; vuelve a `panel:contact-reply_list`; al guardar va a `panel:contact-reply_list`
    - ruta: `panel:contact-reply_create` → `/panel/contact-reply/create/`
    - fondo: `bg-mailing-contact-reply`
  - `ContactReplyDataView` (panel) — datos JSON de la lista
    - archivo: `apps/mailing/views/v3_data.py` · hereda de `BaseContactReply`, `AdminDataView`
    - ruta: `panel:contact-reply_data` → `/panel/contact-reply/data/`
    - fondo: `bg-mailing-contact-reply`
  - `ContactReplyDeleteView` (panel) — borrado
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseContactReply`, `BaseDelete`
    - depende de: vuelve a `panel:contact-reply_list`; al guardar va a `panel:contact-reply_list`
    - ruta: `panel:contact-reply_delete` → `/panel/contact-reply/<int:pk>/delete/`
    - fondo: `bg-mailing-contact-reply`
  - `ContactReplyDetailView` (panel) — ficha
    - archivo: `apps/mailing/views/v6_detail.py` · hereda de `BaseContactReply`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:contact-reply_list`; plantilla `mailing/detail/contact_reply.html`
    - ruta: `panel:contact-reply_detail` → `/panel/contact-reply/<int:pk>/`
    - fondo: `bg-mailing-contact-reply`
  - `ContactReplyListView` (panel) — lista
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseContactReply`, `AdminListView`
    - depende de: datos de `panel:contact-reply_data`
    - ruta: `panel:contact-reply_list` → `/panel/contact-reply/`
    - fondo: `bg-mailing-contact-reply`
  - `ContactReplyUpdateView` (panel) — edición
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseContactReply`, `BaseUpdate`
    - depende de: formulario `ContactReplyForm`; vuelve a `panel:contact-reply_list`; al guardar va a `panel:contact-reply_list`
    - ruta: `panel:contact-reply_update` → `/panel/contact-reply/<int:pk>/update/`
    - fondo: `bg-mailing-contact-reply`

### Modelo: `EmailLog` (`apps/mailing/models.py`)

- Formulario: `EmailLogForm` (`apps/mailing/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `EmailLogCreateView` (panel) — alta
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailLog`, `BaseCreate`
    - depende de: formulario `EmailLogForm`; vuelve a `panel:email-log_list`; al guardar va a `panel:email-log_list`
    - ruta: `panel:email-log_create` → `/panel/email-log/create/`
    - fondo: `bg-mailing-email-log`
  - `EmailLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/mailing/views/v3_data.py` · hereda de `BaseEmailLog`, `AdminDataView`
    - ruta: `panel:email-log_data` → `/panel/email-log/data/`
    - fondo: `bg-mailing-email-log`
  - `EmailLogDeleteView` (panel) — borrado
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailLog`, `BaseDelete`
    - depende de: vuelve a `panel:email-log_list`; al guardar va a `panel:email-log_list`
    - ruta: `panel:email-log_delete` → `/panel/email-log/<int:pk>/delete/`
    - fondo: `bg-mailing-email-log`
  - `EmailLogDetailView` (panel) — ficha
    - archivo: `apps/mailing/views/v6_detail.py` · hereda de `BaseEmailLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:email-log_list`; plantilla `mailing/detail/email_log.html`
    - ruta: `panel:email-log_detail` → `/panel/email-log/<int:pk>/`
    - fondo: `bg-mailing-email-log`
  - `EmailLogListView` (panel) — lista
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseEmailLog`, `AdminListView`
    - depende de: datos de `panel:email-log_data`
    - ruta: `panel:email-log_list` → `/panel/email-log/`
    - fondo: `bg-mailing-email-log`
  - `EmailLogUpdateView` (panel) — edición
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailLog`, `BaseUpdate`
    - depende de: formulario `EmailLogForm`; vuelve a `panel:email-log_list`; al guardar va a `panel:email-log_list`
    - ruta: `panel:email-log_update` → `/panel/email-log/<int:pk>/update/`
    - fondo: `bg-mailing-email-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `EmailLogDataView`

### Modelo: `EmailMessage` (`apps/mailing/models.py`)

- Formulario: `EmailMessageForm` (`apps/mailing/forms.py`) — campos: `template`, `to_email`, `subject`, `body`, `context`, `status`, `error`
- Vistas:
  - `EmailMessageCreateView` (panel) — alta
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailMessage`, `BaseCreate`
    - depende de: formulario `EmailMessageForm`; vuelve a `panel:email-message_list`; al guardar va a `panel:email-message_list`
    - ruta: `panel:email-message_create` → `/panel/email-message/create/`
    - fondo: `bg-mailing-email`
  - `EmailMessageDataView` (panel) — datos JSON de la lista
    - archivo: `apps/mailing/views/v3_data.py` · hereda de `BaseEmailMessageContext`, `AdminDataView`
    - ruta: `panel:email-message_data` → `/panel/email-message/data/`, `panel:email-message_data-by` → `/panel/email-message/data/<str:tipo>/<str:pk>/`
    - mapa «by»: `status` → choice: `sent`, `queued`, `error`, `skipped`
    - fondo: `bg-mailing-email`
  - `EmailMessageDeleteView` (panel) — borrado
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailMessage`, `BaseDelete`
    - depende de: vuelve a `panel:email-message_list`; al guardar va a `panel:email-message_list`
    - ruta: `panel:email-message_delete` → `/panel/email-message/<int:pk>/delete/`
    - fondo: `bg-mailing-email`
  - `EmailMessageDetailView` (panel) — ficha
    - archivo: `apps/mailing/views/v6_detail.py` · hereda de `BaseEmailMessage`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:email-message_list`
    - ruta: `panel:email-message_detail` → `/panel/email-message/<int:pk>/`
    - fondo: `bg-mailing-email`
  - `EmailMessageListByView` (panel) — lista «por» (acotada a un padre) — Lista acotada por el mapa (`/email-message/<tipo>/<valor>/`): la alimenta EmailMessageDataView con `/data/<tipo>/<valor>/`.
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseEmailMessageContext`, `AdminListByView`
    - depende de: datos de `panel:email-message_data-by`
    - ruta: `panel:email-message_by` → `/panel/email-message/<str:tipo>/<str:pk>/`
    - mapa «by»: `status` → choice: `sent`, `queued`, `error`, `skipped`
    - fondo: `bg-mailing-email`
  - `EmailMessageListView` (panel) — lista
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseEmailMessage`, `AdminListView`
    - depende de: datos de `panel:email-message_data`
    - ruta: `panel:email-message_list` → `/panel/email-message/`
    - fondo: `bg-mailing-email`
  - `EmailMessageUpdateView` (panel) — edición
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailMessage`, `BaseUpdate`
    - depende de: formulario `EmailMessageForm`; vuelve a `panel:email-message_list`; al guardar va a `panel:email-message_list`
    - ruta: `panel:email-message_update` → `/panel/email-message/<int:pk>/update/`
    - fondo: `bg-mailing-email`
- Filtros:
  - `EmailMessageFilters`: Estado (`status`) — para `EmailMessageDataView`

### Modelo: `EmailTemplate` (`apps/mailing/models.py`)

- Formulario: `EmailTemplateForm` (`apps/mailing/forms.py`) — campos: `key`, `name`, `subject`, `body_html`, `body_text`, `description`, `is_active`
- Vistas:
  - `EmailTemplateCreateView` (panel) — alta
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailTemplate`, `BaseCreate`
    - depende de: formulario `EmailTemplateForm`; vuelve a `panel:email-template_list`; al guardar va a `panel:email-template_list`; plantilla `mailing/form/email_template.html`
    - ruta: `panel:email-template_create` → `/panel/email-template/create/`
    - fondo: `bg-mailing-email-template`
  - `EmailTemplateDataView` (panel) — datos JSON de la lista
    - archivo: `apps/mailing/views/v3_data.py` · hereda de `BaseEmailTemplate`, `AdminDataView`
    - ruta: `panel:email-template_data` → `/panel/email-template/data/`
    - fondo: `bg-mailing-email-template`
  - `EmailTemplateDeleteView` (panel) — borrado
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailTemplate`, `BaseDelete`
    - depende de: vuelve a `panel:email-template_list`; al guardar va a `panel:email-template_list`
    - ruta: `panel:email-template_delete` → `/panel/email-template/<int:pk>/delete/`
    - fondo: `bg-mailing-email-template`
  - `EmailTemplateDetailView` (panel) — ficha
    - archivo: `apps/mailing/views/v6_detail.py` · hereda de `BaseEmailTemplate`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:email-template_list`; plantilla `mailing/detail/email_template.html`
    - ruta: `panel:email-template_detail` → `/panel/email-template/<int:pk>/`
    - fondo: `bg-mailing-email-template`
  - `EmailTemplateListView` (panel) — lista
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseEmailTemplate`, `AdminListView`
    - depende de: datos de `panel:email-template_data`
    - ruta: `panel:email-template_list` → `/panel/email-template/`
    - fondo: `bg-mailing-email-template`
  - `EmailTemplateUpdateView` (panel) — edición
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseEmailTemplate`, `BaseUpdate`
    - depende de: formulario `EmailTemplateForm`; vuelve a `panel:email-template_list`; al guardar va a `panel:email-template_list`; plantilla `mailing/form/email_template.html`
    - ruta: `panel:email-template_update` → `/panel/email-template/<int:pk>/update/`
    - fondo: `bg-mailing-email-template`

### Modelo: `MailConfig` (`apps/mailing/models.py`)

- Formulario: `MailConfigForm` (`apps/mailing/forms.py`) — campos: `send_email`, `signature`
- Vistas:
  - `MailConfigCreateView` (panel) — alta
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseMailConfig`, `BaseCreate`
    - depende de: formulario `MailConfigForm`; vuelve a `panel:mail-config_list`; al guardar va a `panel:mail-config_list`
    - ruta: `panel:mail-config_create` → `/panel/mail-config/create/`
    - fondo: `bg-mailing-mail-config`
  - `MailConfigDataView` (panel) — datos JSON de la lista
    - archivo: `apps/mailing/views/v3_data.py` · hereda de `BaseMailConfig`, `AdminDataView`
    - ruta: `panel:mail-config_data` → `/panel/mail-config/data/`
    - fondo: `bg-mailing-mail-config`
  - `MailConfigDeleteView` (panel) — borrado
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BaseMailConfig`, `BaseDelete`
    - depende de: vuelve a `panel:mail-config_list`; al guardar va a `panel:mail-config_list`
    - ruta: `panel:mail-config_delete` → `/panel/mail-config/<int:pk>/delete/`
    - fondo: `bg-mailing-mail-config`
  - `MailConfigDetailView` (panel) — ficha
    - archivo: `apps/mailing/views/v6_detail.py` · hereda de `BaseMailConfig`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:mail-config_list`
    - ruta: `panel:mail-config_detail` → `/panel/mail-config/<int:pk>/`
    - fondo: `bg-mailing-mail-config`
  - `MailConfigListView` (panel) — lista
    - archivo: `apps/mailing/views/v5_list.py` · hereda de `BaseMailConfig`, `AdminListView`
    - depende de: datos de `panel:mail-config_data`
    - ruta: `panel:mail-config_list` → `/panel/mail-config/`
    - fondo: `bg-mailing-mail-config`
  - `MailConfigUpdateView` (panel) — edición — Config MÍNIMA: el interruptor de envío + la firma al pie. (SMTP → .env).
    - archivo: `apps/mailing/views/v4_write.py` · hereda de `BasePage`, `UpdateView`
    - depende de: formulario `MailConfigForm`; plantilla `mailing/config.html`
    - ruta: `panel:mail-config` → `/panel/mailing/config/`
    - fondo: `bg-mailing-mail-config`

### Sin modelo

- `EmailResendPendingView` — Reenvía TODA la cola (en cola + error) de un clic — el 'encolador'.
  - archivo: `apps/mailing/views/v8_actions.py` · hereda de `StaffRequiredMixin`, `View` · ruta: `panel:email-message_resend_pending` → `/panel/email-template/reenviar-pendientes/`
- `EmailResendView` — Reenvía un correo guardado (POST). Vuelve a donde se pulsó con un aviso.
  - archivo: `apps/mailing/views/v8_actions.py` · hereda de `StaffRequiredMixin`, `View` · ruta: `panel:email-message_resend` → `/panel/email-message/<int:pk>/reenviar/`
- `MailToggleView` — Enciende/apaga el envío de correos (master switch) desde el panel.
  - archivo: `apps/mailing/views/v8_actions.py` · hereda de `StaffRequiredMixin`, `View` · ruta: `panel:mail-config_toggle` → `/panel/mail-config/config/toggle/`
- `MailingHomeView`
  - archivo: `apps/mailing/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:mailing-home` → `/panel/mailing/` · fondo `bg-mailing-home`

## Páginas (`pages`)

### Modelo: `AboutSection` (`apps/pages/models.py`)

- Formulario: `AboutSectionForm` (`apps/pages/forms.py`) — campos: `order`, `title`, `body`, `is_active`
- Vistas:
  - `AboutSectionCreateView` (panel) — alta
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BaseAboutSection`, `BaseCreate`
    - depende de: formulario `AboutSectionForm`; vuelve a `panel:about-section_list`; al guardar va a `panel:about-section_list`
    - ruta: `panel:about-section_create` → `/panel/about-section/create/`
    - fondo: `bg-pages-about`
  - `AboutSectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/pages/views/v3_data.py` · hereda de `BaseAboutSection`, `AdminDataView`
    - ruta: `panel:about-section_data` → `/panel/about-section/data/`
    - fondo: `bg-pages-about`
  - `AboutSectionDeleteView` (panel) — borrado
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BaseAboutSection`, `BaseDelete`
    - depende de: vuelve a `panel:about-section_list`; al guardar va a `panel:about-section_list`
    - ruta: `panel:about-section_delete` → `/panel/about-section/<int:pk>/delete/`
    - fondo: `bg-pages-about`
  - `AboutSectionDetailView` (panel) — ficha
    - archivo: `apps/pages/views/v6_detail.py` · hereda de `BaseAboutSection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:about-section_list`; plantilla `pages/detail/about_section.html`
    - ruta: `panel:about-section_detail` → `/panel/about-section/<int:pk>/`
    - fondo: `bg-pages-about`
  - `AboutSectionListView` (panel) — lista
    - archivo: `apps/pages/views/v5_list.py` · hereda de `BaseAboutSection`, `AdminListView`
    - depende de: datos de `panel:about-section_data`
    - ruta: `panel:about-section_list` → `/panel/about-section/`
    - fondo: `bg-pages-about`
  - `AboutSectionSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/pages/views/v3_data.py` · hereda de `BaseAboutSection`, `BaseSelectView`
    - ruta: `panel:about-section_select` → `/panel/about-section/select/`
    - fondo: `bg-pages-about`
  - `AboutSectionUpdateView` (panel) — edición
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BaseAboutSection`, `BaseUpdate`
    - depende de: formulario `AboutSectionForm`; vuelve a `panel:about-section_list`; al guardar va a `panel:about-section_list`
    - ruta: `panel:about-section_update` → `/panel/about-section/<int:pk>/update/`
    - fondo: `bg-pages-about`

### Modelo: `PagesLog` (`apps/pages/models.py`)

- Formulario: `PagesLogForm` (`apps/pages/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `PagesLogCreateView` (panel) — alta
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BasePagesLog`, `BaseCreate`
    - depende de: formulario `PagesLogForm`; vuelve a `panel:pages-log_list`; al guardar va a `panel:pages-log_list`
    - ruta: `panel:pages-log_create` → `/panel/pages-log/create/`
    - fondo: `bg-pages-log`
  - `PagesLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/pages/views/v3_data.py` · hereda de `BasePagesLog`, `AdminDataView`
    - ruta: `panel:pages-log_data` → `/panel/pages-log/data/`
    - fondo: `bg-pages-log`
  - `PagesLogDeleteView` (panel) — borrado
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BasePagesLog`, `BaseDelete`
    - depende de: vuelve a `panel:pages-log_list`; al guardar va a `panel:pages-log_list`
    - ruta: `panel:pages-log_delete` → `/panel/pages-log/<int:pk>/delete/`
    - fondo: `bg-pages-log`
  - `PagesLogDetailView` (panel) — ficha
    - archivo: `apps/pages/views/v6_detail.py` · hereda de `BasePagesLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:pages-log_list`; plantilla `pages/detail/pages_log.html`
    - ruta: `panel:pages-log_detail` → `/panel/pages-log/<int:pk>/`
    - fondo: `bg-pages-log`
  - `PagesLogListView` (panel) — lista
    - archivo: `apps/pages/views/v5_list.py` · hereda de `BasePagesLog`, `AdminListView`
    - depende de: datos de `panel:pages-log_data`
    - ruta: `panel:pages-log_list` → `/panel/pages-log/`
    - fondo: `bg-pages-log`
  - `PagesLogUpdateView` (panel) — edición
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BasePagesLog`, `BaseUpdate`
    - depende de: formulario `PagesLogForm`; vuelve a `panel:pages-log_list`; al guardar va a `panel:pages-log_list`
    - ruta: `panel:pages-log_update` → `/panel/pages-log/<int:pk>/update/`
    - fondo: `bg-pages-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `PagesLogDataView`

### Modelo: `PrivacySection` (`apps/pages/models.py`)

- Formulario: `PrivacySectionForm` (`apps/pages/forms.py`) — campos: `order`, `title`, `body`, `is_active`
- Vistas:
  - `PrivacySectionCreateView` (panel) — alta
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BasePrivacySection`, `BaseCreate`
    - depende de: formulario `PrivacySectionForm`; vuelve a `panel:privacy-section_list`; al guardar va a `panel:privacy-section_list`
    - ruta: `panel:privacy-section_create` → `/panel/privacy-section/create/`
    - fondo: `bg-pages-privacy`
  - `PrivacySectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/pages/views/v3_data.py` · hereda de `BasePrivacySection`, `AdminDataView`
    - ruta: `panel:privacy-section_data` → `/panel/privacy-section/data/`
    - fondo: `bg-pages-privacy`
  - `PrivacySectionDeleteView` (panel) — borrado
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BasePrivacySection`, `BaseDelete`
    - depende de: vuelve a `panel:privacy-section_list`; al guardar va a `panel:privacy-section_list`
    - ruta: `panel:privacy-section_delete` → `/panel/privacy-section/<int:pk>/delete/`
    - fondo: `bg-pages-privacy`
  - `PrivacySectionDetailView` (panel) — ficha
    - archivo: `apps/pages/views/v6_detail.py` · hereda de `BasePrivacySection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:privacy-section_list`; plantilla `pages/detail/privacy_section.html`
    - ruta: `panel:privacy-section_detail` → `/panel/privacy-section/<int:pk>/`
    - fondo: `bg-pages-privacy`
  - `PrivacySectionListView` (panel) — lista
    - archivo: `apps/pages/views/v5_list.py` · hereda de `BasePrivacySection`, `AdminListView`
    - depende de: datos de `panel:privacy-section_data`
    - ruta: `panel:privacy-section_list` → `/panel/privacy-section/`
    - fondo: `bg-pages-privacy`
  - `PrivacySectionSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/pages/views/v3_data.py` · hereda de `BasePrivacySection`, `BaseSelectView`
    - ruta: `panel:privacy-section_select` → `/panel/privacy-section/select/`
    - fondo: `bg-pages-privacy`
  - `PrivacySectionUpdateView` (panel) — edición
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BasePrivacySection`, `BaseUpdate`
    - depende de: formulario `PrivacySectionForm`; vuelve a `panel:privacy-section_list`; al guardar va a `panel:privacy-section_list`
    - ruta: `panel:privacy-section_update` → `/panel/privacy-section/<int:pk>/update/`
    - fondo: `bg-pages-privacy`

### Modelo: `TermsSection` (`apps/pages/models.py`)

- Formulario: `TermsSectionForm` (`apps/pages/forms.py`) — campos: `order`, `title`, `body`, `is_active`
- Vistas:
  - `TermsSectionCreateView` (panel) — alta
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BaseTermsSection`, `BaseCreate`
    - depende de: formulario `TermsSectionForm`; vuelve a `panel:terms-section_list`; al guardar va a `panel:terms-section_list`
    - ruta: `panel:terms-section_create` → `/panel/terms-section/create/`
    - fondo: `bg-pages-terms`
  - `TermsSectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/pages/views/v3_data.py` · hereda de `BaseTermsSection`, `AdminDataView`
    - ruta: `panel:terms-section_data` → `/panel/terms-section/data/`
    - fondo: `bg-pages-terms`
  - `TermsSectionDeleteView` (panel) — borrado
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BaseTermsSection`, `BaseDelete`
    - depende de: vuelve a `panel:terms-section_list`; al guardar va a `panel:terms-section_list`
    - ruta: `panel:terms-section_delete` → `/panel/terms-section/<int:pk>/delete/`
    - fondo: `bg-pages-terms`
  - `TermsSectionDetailView` (panel) — ficha
    - archivo: `apps/pages/views/v6_detail.py` · hereda de `BaseTermsSection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:terms-section_list`; plantilla `pages/detail/terms_section.html`
    - ruta: `panel:terms-section_detail` → `/panel/terms-section/<int:pk>/`
    - fondo: `bg-pages-terms`
  - `TermsSectionListView` (panel) — lista
    - archivo: `apps/pages/views/v5_list.py` · hereda de `BaseTermsSection`, `AdminListView`
    - depende de: datos de `panel:terms-section_data`
    - ruta: `panel:terms-section_list` → `/panel/terms-section/`
    - fondo: `bg-pages-terms`
  - `TermsSectionSelectView` (panel) — buscador Select2 (FK)
    - archivo: `apps/pages/views/v3_data.py` · hereda de `BaseTermsSection`, `BaseSelectView`
    - ruta: `panel:terms-section_select` → `/panel/terms-section/select/`
    - fondo: `bg-pages-terms`
  - `TermsSectionUpdateView` (panel) — edición
    - archivo: `apps/pages/views/v4_write.py` · hereda de `BaseTermsSection`, `BaseUpdate`
    - depende de: formulario `TermsSectionForm`; vuelve a `panel:terms-section_list`; al guardar va a `panel:terms-section_list`
    - ruta: `panel:terms-section_update` → `/panel/terms-section/<int:pk>/update/`
    - fondo: `bg-pages-terms`

### Sin modelo

- `AboutView`
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `BasePaginaInformativa` · ruta: `pages:nosotros` → `/about/` · fondo `bg-pages-about`
- `ContactView`
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `TemplateView` · ruta: `pages:contacto` → `/contact/` · fondo `bg-pages-contact`
- `Error400View` — DisallowedHost y peticiones malformadas.
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `BaseErrorStandaloneView` · ruta: `prev_400` → `/prev/400/`
- `Error403CsrfView` — CSRF_FAILURE_VIEW: el 403 bonito también para fallos CSRF (sesión
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `Error403View` · ruta: `prev_403_csrf` → `/prev/403/csrf/`
- `Error403View`
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `BaseErrorStandaloneView` · ruta: `prev_403` → `/prev/403/`
- `Error404View`
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `BaseErrorStandaloneView` · ruta: `prev_404` → `/prev/404/`
- `Error500View`
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `BaseErrorStandaloneView` · ruta: `prev_500` → `/prev/500/`
- `GlobalSearchView` — BUSCADOR GLOBAL del sitio: cruza todos los medios. Pensado para
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `TemplateView` · ruta: `pages:buscar` → `/search/` · fondo `bg-pages-index`
- `IndexView` — Landing general (identidad + secciones + arte).
  - archivo: `apps/pages/views/v1_home.py` · hereda de `TemplateView` · ruta: `pages:index` → `/` · fondo `bg-pages-index`
- `MyMessagesView` — MIS MENSAJES: el hilo del usuario registrado con el sitio — cada vez
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `LoginRequiredMixin`, `TemplateView` · ruta: `pages:mis-mensajes` → `/contact/my-messages/` · fondo `bg-pages-contact`
- `PagesHomeView`
  - archivo: `apps/pages/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:pages-home` → `/panel/pages/` · fondo `bg-pages-home`
- `PrivacyView`
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `BasePaginaInformativa` · ruta: `pages:privacidad` → `/privacy/` · fondo `bg-pages-privacy`
- `TermsView`
  - archivo: `apps/pages/views/v8_actions.py` · hereda de `BasePaginaInformativa` · ruta: `pages:terminos` → `/terms/` · fondo `bg-pages-terms`

## Colección (`collections`)

### Modelo: `AlbumCollection` (`apps/collections/models.py`)

- Formulario: `AlbumCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `AlbumCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseAlbumCollection`, `BaseCreate`
    - depende de: formulario `AlbumCollectionForm`; vuelve a `panel:album-collection_list`; al guardar va a `panel:album-collection_list`
    - ruta: `panel:album-collection_create` → `/panel/album-collection/create/`
    - fondo: `bg-coleccions-albums`
  - `AlbumCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseAlbumCollection`, `AdminDataView`
    - ruta: `panel:album-collection_data` → `/panel/album-collection/data/`
    - fondo: `bg-coleccions-albums`
  - `AlbumCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseAlbumCollection`, `BaseDelete`
    - depende de: vuelve a `panel:album-collection_list`; al guardar va a `panel:album-collection_list`
    - ruta: `panel:album-collection_delete` → `/panel/album-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-albums`
  - `AlbumCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseAlbumCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:album-collection_list`; plantilla `collections/detail/album_collection.html`
    - ruta: `panel:album-collection_detail` → `/panel/album-collection/<int:pk>/`
    - fondo: `bg-coleccions-albums`
  - `AlbumCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseAlbumCollection`, `AdminListView`
    - depende de: datos de `panel:album-collection_data`
    - ruta: `panel:album-collection_list` → `/panel/album-collection/`
    - fondo: `bg-coleccions-albums`
  - `AlbumCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseAlbumCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-albums`
  - `AlbumCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseAlbumCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-albums`
  - `AlbumCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseAlbumCollection`, `BaseUpdate`
    - depende de: formulario `AlbumCollectionForm`; vuelve a `panel:album-collection_list`; al guardar va a `panel:album-collection_list`
    - ruta: `panel:album-collection_update` → `/panel/album-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-albums`
- Filtros:
  - `AlbumCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `AlbumCollectionDataView`
  - `AlbumCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Género (`content__genres`), Año (`content__release_date`) — para `AlbumCollectionPublicDataView`

### Modelo: `AnimeCollection` (`apps/collections/models.py`)

- Formulario: `AnimeCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `AnimeCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseAnimeCollection`, `BaseCreate`
    - depende de: formulario `AnimeCollectionForm`; vuelve a `panel:anime-collection_list`; al guardar va a `panel:anime-collection_list`
    - ruta: `panel:anime-collection_create` → `/panel/anime-collection/create/`
    - fondo: `bg-coleccions-animes`
  - `AnimeCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseAnimeCollection`, `AdminDataView`
    - ruta: `panel:anime-collection_data` → `/panel/anime-collection/data/`
    - fondo: `bg-coleccions-animes`
  - `AnimeCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseAnimeCollection`, `BaseDelete`
    - depende de: vuelve a `panel:anime-collection_list`; al guardar va a `panel:anime-collection_list`
    - ruta: `panel:anime-collection_delete` → `/panel/anime-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-animes`
  - `AnimeCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseAnimeCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:anime-collection_list`; plantilla `collections/detail/anime_collection.html`
    - ruta: `panel:anime-collection_detail` → `/panel/anime-collection/<int:pk>/`
    - fondo: `bg-coleccions-animes`
  - `AnimeCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseAnimeCollection`, `AdminListView`
    - depende de: datos de `panel:anime-collection_data`
    - ruta: `panel:anime-collection_list` → `/panel/anime-collection/`
    - fondo: `bg-coleccions-animes`
  - `AnimeCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseAnimeCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-animes`
  - `AnimeCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseAnimeCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-animes`
  - `AnimeCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseAnimeCollection`, `BaseUpdate`
    - depende de: formulario `AnimeCollectionForm`; vuelve a `panel:anime-collection_list`; al guardar va a `panel:anime-collection_list`
    - ruta: `panel:anime-collection_update` → `/panel/anime-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-animes`
- Filtros:
  - `AnimeCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `AnimeCollectionDataView`
  - `AnimeCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Género (`content__genres`), Tipo (`content__anime_type`), Temas (`content__themes`), Demografías (`content__demographics`), Estudios (`content__studios`), Productoras (`content__producers`), Licenciatarias (`content__licensors`), Estado (`content__status`), Fuente (`content__source`), Clasificación (`content__rating`), Temporada (`content__season`), Año (`content__year`) — para `AnimeCollectionPublicDataView`

### Modelo: `ArtistCollection` (`apps/collections/models.py`)

- Formulario: `ArtistCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `ArtistCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseArtistCollection`, `BaseCreate`
    - depende de: formulario `ArtistCollectionForm`; vuelve a `panel:artist-collection_list`; al guardar va a `panel:artist-collection_list`
    - ruta: `panel:artist-collection_create` → `/panel/artist-collection/create/`
    - fondo: `bg-coleccions-artists`
  - `ArtistCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseArtistCollection`, `AdminDataView`
    - ruta: `panel:artist-collection_data` → `/panel/artist-collection/data/`
    - fondo: `bg-coleccions-artists`
  - `ArtistCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseArtistCollection`, `BaseDelete`
    - depende de: vuelve a `panel:artist-collection_list`; al guardar va a `panel:artist-collection_list`
    - ruta: `panel:artist-collection_delete` → `/panel/artist-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-artists`
  - `ArtistCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseArtistCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:artist-collection_list`; plantilla `collections/detail/artist_collection.html`
    - ruta: `panel:artist-collection_detail` → `/panel/artist-collection/<int:pk>/`
    - fondo: `bg-coleccions-artists`
  - `ArtistCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseArtistCollection`, `AdminListView`
    - depende de: datos de `panel:artist-collection_data`
    - ruta: `panel:artist-collection_list` → `/panel/artist-collection/`
    - fondo: `bg-coleccions-artists`
  - `ArtistCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseArtistCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-artists`
  - `ArtistCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseArtistCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-artists`
  - `ArtistCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseArtistCollection`, `BaseUpdate`
    - depende de: formulario `ArtistCollectionForm`; vuelve a `panel:artist-collection_list`; al guardar va a `panel:artist-collection_list`
    - ruta: `panel:artist-collection_update` → `/panel/artist-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-artists`
- Filtros:
  - `ArtistCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `ArtistCollectionDataView`
  - `ArtistCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Género (`content__genres`) — para `ArtistCollectionPublicDataView`

### Modelo: `CharacterCollection` (`apps/collections/models.py`)

- Formulario: `CharacterCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`
- Vistas:
  - `CharacterCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseCharacterCollection`, `BaseCreate`
    - depende de: formulario `CharacterCollectionForm`; vuelve a `panel:character-collection_list`; al guardar va a `panel:character-collection_list`
    - ruta: `panel:character-collection_create` → `/panel/character-collection/create/`
    - fondo: `bg-coleccions-characters`
  - `CharacterCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseCharacterCollection`, `AdminDataView`
    - ruta: `panel:character-collection_data` → `/panel/character-collection/data/`
    - fondo: `bg-coleccions-characters`
  - `CharacterCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseCharacterCollection`, `BaseDelete`
    - depende de: vuelve a `panel:character-collection_list`; al guardar va a `panel:character-collection_list`
    - ruta: `panel:character-collection_delete` → `/panel/character-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-characters`
  - `CharacterCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseCharacterCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:character-collection_list`; plantilla `collections/detail/character_collection.html`
    - ruta: `panel:character-collection_detail` → `/panel/character-collection/<int:pk>/`
    - fondo: `bg-coleccions-characters`
  - `CharacterCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseCharacterCollection`, `AdminListView`
    - depende de: datos de `panel:character-collection_data`
    - ruta: `panel:character-collection_list` → `/panel/character-collection/`
    - fondo: `bg-coleccions-characters`
  - `CharacterCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseCharacterCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-characters`
  - `CharacterCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseCharacterCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-characters`
  - `CharacterCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseCharacterCollection`, `BaseUpdate`
    - depende de: formulario `CharacterCollectionForm`; vuelve a `panel:character-collection_list`; al guardar va a `panel:character-collection_list`
    - ruta: `panel:character-collection_update` → `/panel/character-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-characters`
- Filtros:
  - `CharacterCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`) — para `CharacterCollectionDataView`
  - `CharacterCollectionFilters`: Favorito (`is_favorite`) — para `CharacterCollectionPublicDataView`

### Modelo: `CollectionLog` (`apps/collections/models.py`)

- Formulario: `CollectionLogForm` (`apps/collections/forms.py`) — campos: `level`, `process`, `message`, `is_active`
- Vistas:
  - `CollectionLogCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseCollectionLog`, `BaseCreate`
    - depende de: formulario `CollectionLogForm`; vuelve a `panel:collection-log_list`; al guardar va a `panel:collection-log_list`
    - ruta: `panel:collection-log_create` → `/panel/collection-log/create/`
    - fondo: `bg-coleccions-log`
  - `CollectionLogDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseCollectionLog`, `AdminDataView`
    - ruta: `panel:collection-log_data` → `/panel/collection-log/data/`
    - fondo: `bg-coleccions-log`
  - `CollectionLogDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseCollectionLog`, `BaseDelete`
    - depende de: vuelve a `panel:collection-log_list`; al guardar va a `panel:collection-log_list`
    - ruta: `panel:collection-log_delete` → `/panel/collection-log/<int:pk>/delete/`
    - fondo: `bg-coleccions-log`
  - `CollectionLogDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseCollectionLog`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:collection-log_list`; plantilla `collections/detail/collection_log.html`
    - ruta: `panel:collection-log_detail` → `/panel/collection-log/<int:pk>/`
    - fondo: `bg-coleccions-log`
  - `CollectionLogListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseCollectionLog`, `AdminListView`
    - depende de: datos de `panel:collection-log_data`
    - ruta: `panel:collection-log_list` → `/panel/collection-log/`
    - fondo: `bg-coleccions-log`
  - `CollectionLogUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseCollectionLog`, `BaseUpdate`
    - depende de: formulario `CollectionLogForm`; vuelve a `panel:collection-log_list`; al guardar va a `panel:collection-log_list`
    - ruta: `panel:collection-log_update` → `/panel/collection-log/<int:pk>/update/`
    - fondo: `bg-coleccions-log`
- Filtros:
  - `LogFilters`: Activo (`is_active`), Nivel (`level`) — para `CollectionLogDataView`

### Modelo: `GameCollection` (`apps/collections/models.py`)

- Formulario: `GameCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `GameCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseGameCollection`, `BaseCreate`
    - depende de: formulario `GameCollectionForm`; vuelve a `panel:game-collection_list`; al guardar va a `panel:game-collection_list`
    - ruta: `panel:game-collection_create` → `/panel/game-collection/create/`
    - fondo: `bg-coleccions-games`
  - `GameCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseGameCollection`, `AdminDataView`
    - ruta: `panel:game-collection_data` → `/panel/game-collection/data/`
    - fondo: `bg-coleccions-games`
  - `GameCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseGameCollection`, `BaseDelete`
    - depende de: vuelve a `panel:game-collection_list`; al guardar va a `panel:game-collection_list`
    - ruta: `panel:game-collection_delete` → `/panel/game-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-games`
  - `GameCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseGameCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:game-collection_list`; plantilla `collections/detail/game_collection.html`
    - ruta: `panel:game-collection_detail` → `/panel/game-collection/<int:pk>/`
    - fondo: `bg-coleccions-games`
  - `GameCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseGameCollection`, `AdminListView`
    - depende de: datos de `panel:game-collection_data`
    - ruta: `panel:game-collection_list` → `/panel/game-collection/`
    - fondo: `bg-coleccions-games`
  - `GameCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseGameCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-games`
  - `GameCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseGameCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-games`
  - `GameCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseGameCollection`, `BaseUpdate`
    - depende de: formulario `GameCollectionForm`; vuelve a `panel:game-collection_list`; al guardar va a `panel:game-collection_list`
    - ruta: `panel:game-collection_update` → `/panel/game-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-games`
- Filtros:
  - `GameCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `GameCollectionDataView`
  - `GameCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Género (`content__genres`), Tipo (`content__type`), Creador (`content__developers`), Editora (`content__publishers`), Estado (`content__status`), Motor (`content__engine`), Plataforma (`content__platforms`), Año (`content__release_date`) — para `GameCollectionPublicDataView`

### Modelo: `MangaCollection` (`apps/collections/models.py`)

- Formulario: `MangaCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `MangaCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseMangaCollection`, `BaseCreate`
    - depende de: formulario `MangaCollectionForm`; vuelve a `panel:manga-collection_list`; al guardar va a `panel:manga-collection_list`
    - ruta: `panel:manga-collection_create` → `/panel/manga-collection/create/`
    - fondo: `bg-coleccions-mangas`
  - `MangaCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseMangaCollection`, `AdminDataView`
    - ruta: `panel:manga-collection_data` → `/panel/manga-collection/data/`
    - fondo: `bg-coleccions-mangas`
  - `MangaCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseMangaCollection`, `BaseDelete`
    - depende de: vuelve a `panel:manga-collection_list`; al guardar va a `panel:manga-collection_list`
    - ruta: `panel:manga-collection_delete` → `/panel/manga-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-mangas`
  - `MangaCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseMangaCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:manga-collection_list`; plantilla `collections/detail/manga_collection.html`
    - ruta: `panel:manga-collection_detail` → `/panel/manga-collection/<int:pk>/`
    - fondo: `bg-coleccions-mangas`
  - `MangaCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseMangaCollection`, `AdminListView`
    - depende de: datos de `panel:manga-collection_data`
    - ruta: `panel:manga-collection_list` → `/panel/manga-collection/`
    - fondo: `bg-coleccions-mangas`
  - `MangaCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseMangaCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-mangas`
  - `MangaCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseMangaCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-mangas`
  - `MangaCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseMangaCollection`, `BaseUpdate`
    - depende de: formulario `MangaCollectionForm`; vuelve a `panel:manga-collection_list`; al guardar va a `panel:manga-collection_list`
    - ruta: `panel:manga-collection_update` → `/panel/manga-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-mangas`
- Filtros:
  - `MangaCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `MangaCollectionDataView`
  - `MangaCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Género (`content__genres`), Tipo (`content__manga_type`), Estado (`content__status`), Demografía (`content__demographics`), Revista (`content__serializations`), Clasificación (`content__rating`), Temporada (`content__season`), Año (`content__year`) — para `MangaCollectionPublicDataView`

### Modelo: `MovieCollection` (`apps/collections/models.py`)

- Formulario: `MovieCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `MovieCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseMovieCollection`, `BaseCreate`
    - depende de: formulario `MovieCollectionForm`; vuelve a `panel:movie-collection_list`; al guardar va a `panel:movie-collection_list`
    - ruta: `panel:movie-collection_create` → `/panel/movie-collection/create/`
    - fondo: `bg-coleccions-movies`
  - `MovieCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseMovieCollection`, `AdminDataView`
    - ruta: `panel:movie-collection_data` → `/panel/movie-collection/data/`
    - fondo: `bg-coleccions-movies`
  - `MovieCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseMovieCollection`, `BaseDelete`
    - depende de: vuelve a `panel:movie-collection_list`; al guardar va a `panel:movie-collection_list`
    - ruta: `panel:movie-collection_delete` → `/panel/movie-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-movies`
  - `MovieCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseMovieCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:movie-collection_list`; plantilla `collections/detail/movie_collection.html`
    - ruta: `panel:movie-collection_detail` → `/panel/movie-collection/<int:pk>/`
    - fondo: `bg-coleccions-movies`
  - `MovieCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseMovieCollection`, `AdminListView`
    - depende de: datos de `panel:movie-collection_data`
    - ruta: `panel:movie-collection_list` → `/panel/movie-collection/`
    - fondo: `bg-coleccions-movies`
  - `MovieCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseMovieCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-movies`
  - `MovieCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseMovieCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-movies`
  - `MovieCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseMovieCollection`, `BaseUpdate`
    - depende de: formulario `MovieCollectionForm`; vuelve a `panel:movie-collection_list`; al guardar va a `panel:movie-collection_list`
    - ruta: `panel:movie-collection_update` → `/panel/movie-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-movies`
- Filtros:
  - `MovieCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `MovieCollectionDataView`
  - `MovieCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Género (`content__genres`), Tipo (`content__movie_type`), Productora (`content__producers`), Clasificación (`content__movie_rating`), Distribuidora (`content__distributors`), Año (`content__release_year`) — para `MovieCollectionPublicDataView`

### Modelo: `PersonCollection` (`apps/collections/models.py`)

- Formulario: `PersonCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`
- Vistas:
  - `PersonCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BasePersonCollection`, `BaseCreate`
    - depende de: formulario `PersonCollectionForm`; vuelve a `panel:person-collection_list`; al guardar va a `panel:person-collection_list`
    - ruta: `panel:person-collection_create` → `/panel/person-collection/create/`
    - fondo: `bg-coleccions-people`
  - `PersonCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BasePersonCollection`, `AdminDataView`
    - ruta: `panel:person-collection_data` → `/panel/person-collection/data/`
    - fondo: `bg-coleccions-people`
  - `PersonCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BasePersonCollection`, `BaseDelete`
    - depende de: vuelve a `panel:person-collection_list`; al guardar va a `panel:person-collection_list`
    - ruta: `panel:person-collection_delete` → `/panel/person-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-people`
  - `PersonCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BasePersonCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:person-collection_list`; plantilla `collections/detail/person_collection.html`
    - ruta: `panel:person-collection_detail` → `/panel/person-collection/<int:pk>/`
    - fondo: `bg-coleccions-people`
  - `PersonCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BasePersonCollection`, `AdminListView`
    - depende de: datos de `panel:person-collection_data`
    - ruta: `panel:person-collection_list` → `/panel/person-collection/`
    - fondo: `bg-coleccions-people`
  - `PersonCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BasePersonCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-people`
  - `PersonCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BasePersonCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-people`
  - `PersonCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BasePersonCollection`, `BaseUpdate`
    - depende de: formulario `PersonCollectionForm`; vuelve a `panel:person-collection_list`; al guardar va a `panel:person-collection_list`
    - ruta: `panel:person-collection_update` → `/panel/person-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-people`
- Filtros:
  - `PersonCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`) — para `PersonCollectionDataView`
  - `PersonCollectionFilters`: Favorito (`is_favorite`), País (`content__country`), Año de nacimiento (`content__birth_date`) — para `PersonCollectionPublicDataView`

### Modelo: `SerieCollection` (`apps/collections/models.py`)

- Formulario: `SerieCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `SerieCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseSerieCollection`, `BaseCreate`
    - depende de: formulario `SerieCollectionForm`; vuelve a `panel:serie-collection_list`; al guardar va a `panel:serie-collection_list`
    - ruta: `panel:serie-collection_create` → `/panel/serie-collection/create/`
    - fondo: `bg-coleccions-series`
  - `SerieCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseSerieCollection`, `AdminDataView`
    - ruta: `panel:serie-collection_data` → `/panel/serie-collection/data/`
    - fondo: `bg-coleccions-series`
  - `SerieCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseSerieCollection`, `BaseDelete`
    - depende de: vuelve a `panel:serie-collection_list`; al guardar va a `panel:serie-collection_list`
    - ruta: `panel:serie-collection_delete` → `/panel/serie-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-series`
  - `SerieCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseSerieCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:serie-collection_list`; plantilla `collections/detail/serie_collection.html`
    - ruta: `panel:serie-collection_detail` → `/panel/serie-collection/<int:pk>/`
    - fondo: `bg-coleccions-series`
  - `SerieCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseSerieCollection`, `AdminListView`
    - depende de: datos de `panel:serie-collection_data`
    - ruta: `panel:serie-collection_list` → `/panel/serie-collection/`
    - fondo: `bg-coleccions-series`
  - `SerieCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseSerieCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-series`
  - `SerieCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseSerieCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-series`
  - `SerieCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseSerieCollection`, `BaseUpdate`
    - depende de: formulario `SerieCollectionForm`; vuelve a `panel:serie-collection_list`; al guardar va a `panel:serie-collection_list`
    - ruta: `panel:serie-collection_update` → `/panel/serie-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-series`
- Filtros:
  - `SerieCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `SerieCollectionDataView`
  - `SerieCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Género (`content__genres`), Tipo (`content__serie_type`), Productora (`content__producers`), Clasificación (`content__serie_rating`), Distribuidora (`content__distributors`), Año (`content__release_year`) — para `SerieCollectionPublicDataView`

### Modelo: `SongCollection` (`apps/collections/models.py`)

- Formulario: `SongCollectionForm` (`apps/collections/forms.py`) — campos: `user`, `score`, `is_favorite`, `progress`, `watch_site`, `download_site`, `download_format`, `download_quality`, `is_active`, `content`, `status`
- Vistas:
  - `SongCollectionCreateView` (panel) — alta
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseSongCollection`, `BaseCreate`
    - depende de: formulario `SongCollectionForm`; vuelve a `panel:song-collection_list`; al guardar va a `panel:song-collection_list`
    - ruta: `panel:song-collection_create` → `/panel/song-collection/create/`
    - fondo: `bg-coleccions-songs`
  - `SongCollectionDataView` (panel) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseSongCollection`, `AdminDataView`
    - ruta: `panel:song-collection_data` → `/panel/song-collection/data/`
    - fondo: `bg-coleccions-songs`
  - `SongCollectionDeleteView` (panel) — borrado
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseSongCollection`, `BaseDelete`
    - depende de: vuelve a `panel:song-collection_list`; al guardar va a `panel:song-collection_list`
    - ruta: `panel:song-collection_delete` → `/panel/song-collection/<int:pk>/delete/`
    - fondo: `bg-coleccions-songs`
  - `SongCollectionDetailView` (panel) — ficha
    - archivo: `apps/collections/views/v6_detail.py` · hereda de `BaseSongCollection`, `BaseAdminDetailView`
    - depende de: vuelve a `panel:song-collection_list`; plantilla `collections/detail/song_collection.html`
    - ruta: `panel:song-collection_detail` → `/panel/song-collection/<int:pk>/`
    - fondo: `bg-coleccions-songs`
  - `SongCollectionListView` (panel) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseSongCollection`, `AdminListView`
    - depende de: datos de `panel:song-collection_data`
    - ruta: `panel:song-collection_list` → `/panel/song-collection/`
    - fondo: `bg-coleccions-songs`
  - `SongCollectionPublicDataView` (pública) — datos JSON de la lista
    - archivo: `apps/collections/views/v3_data.py` · hereda de `BaseSongCollection`, `BaseCollectionData`
    - ruta: —
    - fondo: `bg-coleccions-songs`
  - `SongCollectionPublicListView` (pública) — lista
    - archivo: `apps/collections/views/v5_list.py` · hereda de `BaseSongCollection`, `BaseCollectionList`
    - depende de: datos de `collections:lista_data`; plantilla `collections/list.html`
    - ruta: —
    - fondo: `bg-coleccions-songs`
  - `SongCollectionUpdateView` (panel) — edición
    - archivo: `apps/collections/views/v4_write.py` · hereda de `BaseSongCollection`, `BaseUpdate`
    - depende de: formulario `SongCollectionForm`; vuelve a `panel:song-collection_list`; al guardar va a `panel:song-collection_list`
    - ruta: `panel:song-collection_update` → `/panel/song-collection/<int:pk>/update/`
    - fondo: `bg-coleccions-songs`
- Filtros:
  - `SongCollectionAdminFilters`: Activo (`is_active`), Favorito (`is_favorite`), Usuario (`user`), Estado (`status`) — para `SongCollectionDataView`
  - `SongCollectionFilters`: Favorito (`is_favorite`), Mi estado (`status`), Año (`content__release_year`) — para `SongCollectionPublicDataView`

### Sin modelo

- `AddToCollectionView` — Añade un título del catálogo a la colección del usuario (idempotente).
  - archivo: `apps/collections/views/v8_actions.py` · hereda de `LoginRequiredMixin`, `View` · ruta: `collections:add` → `/collection/add/`
- `CollectionsHomeView`
  - archivo: `apps/collections/views/v1_home.py` · hereda de `BaseHomeView` · ruta: `panel:collections-home` → `/panel/collections/` · fondo `bg-collections-home`
- `CollectionsPublicHomeView` — DASHBOARD de Mi colección (estilo panel de gestión): una tarjeta por
  - archivo: `apps/collections/views/v1_home.py` · hereda de `BasePage`, `TemplateView` · ruta: `collections:mine` → `/collection/` · fondo `bg-collections-home`
- `ItemEditView` — EDICIÓN de una fila de MI colección con CollectionItemForm: seguimiento y dónde la veo / de dónde la
  - archivo: `apps/collections/views/v8_actions.py` · hereda de `BasePage`, `UpdateView` · ruta: `collections:edit` → `/collection/<str:tipo>/<int:pk>/edit/` · fondo `bg-collections-home`
- `RemoveFromCollectionView` — Quita un ítem de la colección del usuario (solo el suyo).
  - archivo: `apps/collections/views/v8_actions.py` · hereda de `LoginRequiredMixin`, `View` · ruta: `collections:remove` → `/collection/<str:tipo>/<int:pk>/remove/`
- `UpdateItemView` — Actualización PARCIAL de una fila propia desde la barra de la ficha o la lista (estado, nota, favorito,
  - archivo: `apps/collections/views/v8_actions.py` · hereda de `LoginRequiredMixin`, `View` · ruta: `collections:update` → `/collection/<str:tipo>/<int:pk>/update/`
- Form `CollectionItemForm`


# Regla general

Todo modelo administrable mediante interfaz mantiene la relación **1 : 1 : N** (R0): un modelo, un formulario, N vistas,
con exactamente estos nombres:

```text
<ModelName>
<ModelName>Form
<ModelName>ListView · <ModelName>DataView · <ModelName>SelectView
<ModelName>CreateView · <ModelName>UpdateView · <ModelName>DeleteView · <ModelName>DetailView
<ModelName>ListByView · <ModelName>DataByView
<ModelName>PublicListView · <ModelName>PublicDataView · <ModelName>PublicDetailView · <ModelName>PublicListByView
<ModelName>KindListView · <ModelName>KindDataView            (listas por tipo)
```

Las implementaciones concretas respetan las bases del proyecto (`core/shared/views/base.py`).
