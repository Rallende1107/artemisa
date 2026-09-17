# Plan · VNDB por páginas («Barrido por páginas»)

Estado: PLAN, pendiente del visto bueno de René. Nada de esto está escrito todavía.

## 0. Qué se quiere

Hoy el lanzador de VNDB trae **id por id**: un juego = su VN + todos sus lanzamientos + todos sus personajes
(3 peticiones o más) y, si falta un desarrollador, otra más. Un rango de 100 juegos son 300–500 peticiones,
8–15 minutos. VNDB permite pedir **100 elementos por petición** con filtro de id y orden por id, así que el mismo
lote cabe en 15–30 peticiones.

Decisión de René (sesión 2026-09-12):

* **No se tocan** las tres secciones que ya existen en cada lanzador: *Buscar por nombre*, *Importar uno*,
  *Importar en masa (rango de ids)*. Siguen id por id, con la cadena completa por elemento.
* **Nace una cuarta sección**, con formulario y tarea PROPIOS, que barre páginas de 100 y procesa lo traído de
  golpe. Cuerpo fijo: los campos que se piden a VNDB son siempre los mismos; lo único que varía es desde qué id
  y cuántas páginas.
* Los **cuatro tipos** tendrán lanzador: juego, creador, **lanzamiento** y **personaje** (hoy solo juego y creador).
  Así lanzamientos y personajes tienen lote propio y no dependen de venir «con su juego».

Nombre de la sección (a elegir): **«Barrido por páginas»** (propuesta), «Importar lotes», «Importar catálogo».
En el código: `barrido` (acción del POST, formulario `VndbBarridoForm`, tarea `barrer_vndb_task`).

## 1. Lo validado en la API de VNDB (https://api.vndb.org/kana)

| Punto | Confirmado |
|---|---|
| Filtro `id` | admite `>`, `>=`, `<`, `<=`; combinadores `["and", …]` / `["or", …]`; hasta 1000 predicados |
| Tamaño de página | `results` máximo 100; `more: true` indica que hay más |
| Orden | `sort: "id"` en los cuatro endpoints |
| Productores anidados | `/vn` → `developers{…}` y `/release` → `producers{…}` aceptan **todos** los campos de `/producer` (+ `developer`, `publisher`) |
| Filtro por VN anidado | `/release` y `/character` aceptan `["vn", "=", <filtro de vn>]` |
| Límites | 200 peticiones / 5 min · 1 s de ejecución por minuto · corte a los 3 s por petición → HTTP 400 «Too much data selected» |
| Campos caros | `description`, `tags`, `screenshots` (vn); `vns` (character) |

Paginación **por último id**, no por número de página: `["id", ">", "p11669"]` + `page: 1` en cada vuelta. Un
catálogo vivo (altas y bajas entre páginas) no se corre, y el barrido se reanuda desde el último id guardado.

## 2. Pantalla del lanzador (una por tipo)

```
BUSCAR POR NOMBRE            (igual que hoy; solo juego y creador)
IMPORTAR UNO                 (igual que hoy)
IMPORTAR EN MASA (RANGO)     (igual que hoy: id por id)
BARRIDO POR PÁGINAS          ← NUEVA
  Desde id  [ cursor ]       el próximo id del cursor de lote de ese tipo (system.ImportCursor)
  Páginas   [ 10 ]           cuántas peticiones de 100; vacío = hasta el final del catálogo (o cancelar)
  [Encolar barrido]          «10 páginas ≈ 1.000 ids ≈ 20 s». Background (Celery) o síncrono.
PENDIENTES DE VNDB           (igual que hoy)
```

* Formulario `VndbBarridoForm(kind, inicio, paginas)`: `inicio` precargado con el cursor; `paginas` entero
  1–200 opcional (200 páginas = el tope de 5 min de VNDB; vacío = sin tope, se para con `more: false` o cancelar).
* La sección se pinta **solo si la vista declara `form_barrido_class`** (MAL y Deezer no la declaran: nada cambia allí).
* `TipoImportView.post` gana `action == "barrido"` → `_barrido(request)` → `run_task(self.task_barrido, kind, inicio, paginas)`.
  El cursor NO se mueve al encolar (no se sabe hasta dónde llegará): lo mueve la tarea al terminar, al último id + 1.

## 3. Servicio `apps/games/services/vndb.py` (un solo módulo, dos puertas)

Se comparte todo lo de abajo (transporte, tablas Data, proceso). Solo se añade la obtención por páginas.

### 3.1 Campos ampliados (los mismos para «uno», «rango» y «barrido»)

| Endpoint | Hoy | Se añade |
|---|---|---|
| `/producer` | id, name, original, description, lang, type | `aliases`, `extlinks{url,label,name,id}` |
| `/vn` | id, title, alttitle, description, released, languages, platforms, olang, devstatus, length, rating, votecount, developers{id,name}, image.url, tags, screenshots | `aliases`, `titles{lang,title,latin,official,main}`, `length_minutes`, `image.thumbnail`, `extlinks`, **`developers` con todos los campos de productor** |
| `/release` | id, title, alttitle, released, languages.lang/main, platforms, official, patch, freeware, minage, producers{id,name,developer,publisher}, vns{id} | `languages.title/latin`, `media{medium,qty}`, `engine`, `resolution`, `voiced`, `uncensored`, `has_ero`, `notes`, `gtin`, `catalog`, `extlinks`, `vns.rtype`, **`producers` completos** |
| `/character` | id, name, original, description, sex, age, birthday, image.url, vns{id,role} | `aliases`, `gender`, `blood_type`, `height`, `weight`, `bust`, `waist`, `hips`, `cup`, `vns.spoiler` |

Todo lo que llega se guarda tal cual en el JSON de la fila Data (`data`). El proceso usa lo que tiene columna o
tabla propia (§3.4); el resto queda disponible en el crudo para cuando haga falta.

### 3.2 Transporte

* `_post(endpoint, filters, fields, page, results, sort=None)`: solo gana `sort`.
* `_guardar_crudo(kind, item, code, vn=None)`: **una fila por elemento** (`update_or_create` por `vndb_id`), la usan
  el fetch por id y el barrido. Lanzamientos y personajes guardan `vndb_id_vn` (la VN por la que se pidieron o,
  en barrido, la primera de sus `vns`; las demás quedan en el JSON — la columna es un solo entero).

### 3.3 Barrido

```python
barrer(kind, desde, paginas=None, hasta=None, por_pagina=100) -> (ids_guardados, ultimo_id, quedan_mas)
```
* tabla `_CRUDO = {kind: (modelo Data, prefijo v/p/r/c, endpoint, campos)}` para los 4 tipos.
* bucle: `filtro = ["id", ">", f"{pref}{ultimo}"]` (+ `["id", "<=", hasta]` si se da), `sort="id"`, `page=1`,
  `results=por_pagina`; guarda cada elemento; `ultimo` = mayor id recibido; para con `more: false`, con
  `paginas` cumplidas, si el usuario cancela, o si una página no avanzó el id.
* HTTP 400 (VNDB cortó la consulta) → `por_pagina //= 2` (mínimo 10) y repite la misma vuelta. Queda en el log.
* **No toca el cursor** (lo decide quien llama). No procesa (lo hace `procesar_ids`).

```python
procesar_ids(kind, ids) -> armados
```
proceso LOCAL, sin peticiones: `process_creator` / `process_game` / `process_release(traer_juego=False)` /
`process_character(traer_juegos=False)`.

### 3.4 Proceso (lo que gana con los campos nuevos)

* Productor: `aliases` → `CreatorNickname`; `extlinks` → `CreatorLink` con su `ExternalSource` (casa por acrónimo
  = clave de VNDB `patreon`, `itch_dev`… o por nombre = etiqueta; si no existe se crea con tipo: monetización /
  red social / comunidad / base de datos / oficial / otro).
* `_creator_del_juego(stub)`: si el productor viene completo anidado (trae `type` o `lang`) → fila Data + proceso
  local, **sin petición**; si viene solo `{id, name}` → como hoy, se trae entero.
* Juego: `titles` → `GameTitle` (por idioma, sin repetir el principal); `extlinks` → `GameLink`.
* Lanzamiento: `engine` → `DevelopmentEngine` y se suma a `game.engine`.
* Personaje: por ahora solo columnas existentes; medidas, sangre, género quedan en el JSON.

### 3.5 Lanzamientos y personajes que llegan por barrido

Regla que se mantiene: **no viven sin su juego**. En barrido no se trae el juego uno a uno (rompería el ahorro):

* `process_release(id, traer_juego=False)` / `process_character(id, traer_juegos=False)`: si ninguno de sus
  juegos está, devuelven `None` y la fila **sigue pendiente** (`data_processed=False`).
* Los consume `process_game` cuando llega su juego (ya lo hace hoy por `vndb_id_vn`) o **«Procesar pendientes»**,
  que pasa a mirar también `DataVndbRelease` y `DataVndbCharacter` **solo** de juegos que ya existen.
* Orden recomendado del barrido de catálogo: creadores → juegos → lanzamientos → personajes.

### 3.6 Lo que NO cambia
`fetch_game`, `import_game`, `import_creator(deep)`, `import_character`, `import_release`, `import_range`,
`import_ids`, `refrescar_juegos_viejos`, `buscar_*`, `_sin_ruido`, `medir_import`. Solo ven más campos.

## 4. Tareas, cursor y panel

* `barrer_vndb_task(kind, inicio=None, paginas=None)`: `inicio` vacío = cursor; al terminar `avanzar("vndb", kind,
  ultimo)`; luego `procesar_ids`. Devuelve armados. Registrada en `apps/system/registro.py` («Barrido por páginas · VNDB»).
* Programable desde el panel de Tareas: p. ej. `{"kind": "creador", "paginas": 50}` a las 04:30. El seed NO crea
  ninguna nueva (todas nacen apagadas y René las enciende).
* Cursores sembrados: se añaden `("vndb", "lanzamiento")` y `("vndb", "personaje")`.
* Lanzadores nuevos: `VndbLanzamientoImportView` y `VndbPersonajeImportView` (URLs `vndb/lanzamiento/`,
  `vndb/personaje/`; tarjetas en el home de Juegos; entradas en el menú; fondos `bg-games-import-lanzamiento` /
  `bg-games-import-personaje` con respaldo en `bg-games-import`).

## 5. Estimación (1,6 s por petición, 100 por página)

| Catálogo | Filas aprox. | Peticiones | Tiempo |
|---|---|---|---|
| Productores | 15.000 | 150 | 4 min |
| Novelas visuales | 50.000 | 500 | 14 min |
| Lanzamientos | 120.000 | 1.200 | 32 min |
| Personajes | 130.000 | 1.300 | 35 min |

Cifras estimadas; el primer barrido con `"count": true` da las reales. Si VNDB corta páginas de lanzamientos o
VN (campos caros), el propio barrido baja a 50 y sigue.

## 6. Tests

* `_post_falso` aprende `sort` y los filtros `["id", ">", …]` / `["and", …]` (devuelve el catálogo falso en orden).
* Nuevos: barrido de creadores guarda filas, procesa alias y enlaces y hace 1 petición; barrido de juegos con
  productor anidado no pide `/producer`; lanzamientos barridos sin juego quedan pendientes y se consumen al
  importar el juego; «Procesar pendientes» los toma cuando el juego existe; página 400 → media página.
* `test_lanzadores`: los dos lanzadores nuevos entran en `TIPOS`; `action=barrido` lanza `task_barrido` con
  `(kind, inicio, paginas)`; MAL/Deezer no pintan la sección.

## 7. Orden de trabajo

1. Servicio: campos, `_post(sort)`, `_guardar_crudo`, `barrer`, `procesar_ids`, proceso con datos nuevos, pendientes.
2. Tareas + registro + cursores.
3. Formulario `VndbBarridoForm`, `TipoImportView._barrido`, sección en `lanzador_tipo.html`.
4. Lanzadores de lanzamiento y personaje (vistas, URLs, home, menú).
5. Tests y `docs/comandos.md`.

## 8. Decisiones abiertas para René

1. Nombre de la sección: «Barrido por páginas» / «Importar lotes» / «Importar catálogo».
2. Tope de `paginas` en el formulario: 200 (= 5 min de VNDB) o sin tope.
3. Personaje: ¿tabla de apodos (`GameCharacterNickname`) para sus `aliases`, o quedan en el JSON por ahora?

## 9. Próximos pasos (mejoras anotadas el 2026-09-12)

* **Fichas de datos crudos** (hecho): sin póster ni pestañas; lateral «Información» con id externo, URL, fetch, HTTP,
  estado, obtenido, actualizado; JSON entero en el cuerpo; botón **Reprocesar** (POST `accion=reprocesar` en la misma
  ficha; la vista declara `reprocesar = staticmethod(lambda obj: …)`). Games (VNDB), Otaku (MAL) y Music (Deezer).
* **Pendiente con migración** (no se hace hasta que René lo pida): `processed_at` (fecha del último procesamiento) y
  `process_count` (cuántas veces se procesó) en `core.shared.models.abstract.ModelBaseData`; `Reprocesar` y `process_*`
  los actualizan y la ficha los muestra bajo «Estado». Genera una migración en games, otaku y music.
* **Staff de VNDB** (DESCARTADO por René el 2026-09-12: personas y empresas mezcladas lo complican; el `staff` queda solo en el JSON crudo). Idea si algún día vuelve: `games.Role` (catálogo de roles VNDB) y `games.GameStaff`
  (juego, `people.Person` por nombre + vndb sN, rol, nota, idioma; único por juego-persona-rol). Los `va` (voces)
  a `GameCharacterRole` o `GameCharacterVoice`, a decidir.
* **Imágenes**: `process_game` y `process_character` ya bajan capturas y fotos al momento; lo que falle queda con URL
  para el descargador programado.

