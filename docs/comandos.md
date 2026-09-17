# Manual de comandos

Todo lo que se corre a mano en Artemisa, dónde se corre y en qué orden. Actualizado al 2026-09-06.

**Regla de oro:** todo va **en Docker** (`docker compose exec web python manage.py <comando>`),
migraciones incluidas (`clear_migrations`).

---

## 1 · Entorno

Un solo archivo `.env` (no va a git). `.env.example` es su espejo con valores dummy y sí se versiona.

```bash
copy .env.example .env      # primera vez en una máquina; ajustar valores
```

Palancas que importan aquí:

| Palanca | Efecto |
|---|---|
| `DEV=1` | el `web` corre `runserver` con autoreload y el código va montado: tocar un `.py`, una plantilla o un fondo recarga solo, sin rebuild ni collectstatic |
| `DEV=0` | gunicorn pseudo-prod |
| `WEB_PORT` | puerto del sitio (por defecto 8000) |
| `DB_PORT_HOST` | puerto en que el Postgres del stack se publica al host (55432, para no chocar con un Postgres instalado en el equipo) |

Si aparece un `db.sqlite3` en la raíz, al `.env` le falta `DB_NAME` y Django cayó a sqlite.

---

## 2 · Stack Docker

Nginx Proxy Manager → nginx → web (+ worker y beat de Celery) → redis → Postgres → pgAdmin · Dozzle.

```bash
docker compose up -d --build      # levanta todo (reconstruye si cambió el código)
docker compose ps                 # estado de los contenedores
docker compose logs -f web        # logs en vivo (web, worker, beat, nginx, db…)
docker compose restart web        # tras cambiar INSTALLED_APPS, settings o un AppConfig.ready()
docker compose restart worker     # el worker y beat NO se autorecargan con DEV=1
docker compose down               # apaga todo; la base sobrevive en el volumen
docker compose down -v            # ☠ apaga y BORRA la base (volumen pgdata)
```

- Sitio: `http://localhost:8000`. pgAdmin: `http://localhost:5050` (servidor «Artemisa» ya registrado).
- Logs en el navegador: **Dozzle** en `http://localhost:8888`. Solo muestra los contenedores de este proyecto
  y solo escucha en localhost (los logs pueden llevar datos sensibles). Sustituye a `docker compose logs -f`.
- Dominio y HTTPS: **Nginx Proxy Manager**, panel en `http://localhost:81` (solo localhost); publica el sitio
  en el 80 y el 443. Va DELANTE del nginx del stack, no lo sustituye: se crea un *Proxy Host* con el dominio,
  destino `nginx` puerto `80`, y en la pestaña SSL se pide el certificado de Let's Encrypt. Sin dominio
  público no hay certificado: en local basta con el `8000` de siempre.
- Puertos de los dos en el `.env`: `DOZZLE_PORT`, `NPM_HTTP_PORT`, `NPM_HTTPS_PORT`, `NPM_ADMIN_PORT`
  (si el 80 lo tiene ocupado otra cosa en Windows, cámbialo ahí).
- Cambiar `DEV` pide un `docker compose up -d` (recrear, sin build).
- El `web` NO migra al arrancar (desde 2026-09-13): el único migrate del stack es el de `initial_setup` (con candado de Postgres). Si el web migrara solo, aplicaría los 0001 viejos que hubiera en la carpeta y luego `clear_migrations` + `makemigrations` generarían 0001 con el mismo nombre que la base ya cree aplicados: tablas viejas con código nuevo. `migrate` a pelo desde el venv: nunca.

---

## 3 · Comandos principales y de desarrollo

**Principales** (los que se corren en cualquier instalación, todos en Docker con `docker compose exec web python manage.py …`):

| Comando | Qué hace |
|---|---|
| `initial_setup` | migra (con candado de Postgres), corre el seed de cada app en orden y al final pide el superusuario. Idempotente: se puede re-correr. `--dev` crea admin/admin y rallende/rallende123; `--demo` siembra además el catálogo demo |
| `seed_<app>` | los datos iniciales de ESA app: `seed_system`, `seed_pages`, `seed_catalogs`, `seed_movies`, `seed_series`, `seed_music`, `seed_games`, `seed_otaku`, `seed_mailing`. Cada uno vive en su app (`apps/<app>/management/commands/`, datos en `apps/<app>/management/data/seed_data.py`), es idempotente y se reejecuta solo cuando cambian sus datos |
| `backup` | respaldo completo: BD (dumpdata gzip) + zip de `media/` en `dump/` |
| `loadbackup` | restaura el último backup (o `--archivo`): vacía las tablas, carga y descomprime media |
| `statics` | estáticos: `statics` (desde cero) o `statics new` (solo lo nuevo). Con `DEV=1` no hace falta |

**Desarrollo** (herramientas mientras el proyecto cambia; documentadas aquí y no forman parte del arranque):

| Comando | Qué hace |
|---|---|
| `clear_migrations` | borra las `0*.py` de todas las apps (o `--app x`). Solo borra; no genera ni migra |
| `makemigrations` | genera el `0001` de cada app (el de Django, siempre dentro de Docker) |
| `seed_demo` | 5 series, 5 películas, 5 juegos, 5 animes y 5 mangas con portadas (`--imagenes`, `--masivo`, `--repartos`, `--industria N`, `--biblioteca N`, `--limpiar`) |
| `test_changed` | tests de humo de las apps modificadas (o `--app x`, `--all`); reporte en `dump/tests/` |
| `load_vndb_tags` | aplica el dump de tags de VNDB (`--download` o `--file`); también desde el panel |
| `fondos_check` | comprueba fondos referenciados sin imagen y huérfanos |
| `medir_import` | cronometra una importación completa para dimensionar los lotes |
| `sync_forms` | sincroniza las plantillas de formulario por entidad |

---

## 4 · Migraciones (Docker, NO versionadas)

Las migraciones **no viajan en git** (`.gitignore`: `apps/*/migrations/0*.py`; queda solo el `__init__.py`). Mientras
el esquema cambie, nacen en Docker: `clear_migrations` borra y `makemigrations` genera. El día que el esquema se cierre,
se generan unos `0001` definitivos y se versionan; hasta entonces serían cien archivos de parches. `initial_setup` no
las genera: si a una app le falta su `0001`, se detiene y lo dice.

```bash
docker compose exec web python manage.py clear_migrations                 # borra las 0*.py de todas las apps
docker compose exec web python manage.py clear_migrations --app mailing   # solo las de esa app
docker compose exec web python manage.py makemigrations                   # genera el 0001 de cada app
docker compose exec web python manage.py makemigrations --check --dry-run   # «No changes detected» = código y migraciones coinciden
```

Django puede partir alguna app en `0001` + `0002` por FK cruzados: es normal y se aplican en orden.

---

## 5 · Arranque desde cero

```bash
docker compose down -v                                       # base vacía
rmdir /s /q media & mkdir media                              # imágenes de cero
docker compose up -d                                         # stack arriba (el web NO migra al arrancar)
docker compose exec web python manage.py clear_migrations    # desarrollo: borra las 0*.py
docker compose exec web python manage.py makemigrations      # desarrollo: genera las 0001
docker compose exec web python manage.py initial_setup       # migra, seed de cada app y pide el superusuario
docker compose restart worker beat                           # worker y beat con el código nuevo
```

`initial_setup`, paso a paso:

1. comprueba que cada app con modelos tenga su `0001`;
2. `migrate` bajo un candado de Postgres (dos `initial_setup` a la vez se turnan);
3. `seed_system` → `seed_pages` → `seed_catalogs` → `seed_movies` → `seed_series` → `seed_music` → `seed_games` → `seed_otaku` → `seed_mailing` (y `seed_demo` con `--demo`);
4. con `--dev`, admin/admin y rallende/rallende123;
5. al final pide el **superusuario** si no hay ninguno: por consola con terminal, o desde `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` y `DJANGO_SUPERUSER_PASSWORD`.

Estáticos y backup quedan fuera a propósito: `statics` y `backup` cuando hagan falta.

---

## 6 · Seeds por app

Todos idempotentes: crean lo que falta, actualizan lo que cambió en los datos y respetan activo/inactivo del panel.
Cada app es dueña de sus datos (`apps/<app>/management/data/seed_data.py`); las funciones de siembra compartidas están en
`apps/catalogs/management/functions/funciones_seed.py`. Series toma géneros, tipos y roles de los datos de películas
(son los mismos).

| Comando | Qué carga |
|---|---|
| `seed_system` | fuentes externas, tareas programadas (nacen apagadas) y cursores de lote |
| `seed_pages` | secciones de Nosotros, Términos y Privacidad (no pisa lo editado) |
| `seed_catalogs` | tamaños de imagen, calidades, formatos, sitios web, países, idiomas y tipos de relación |
| `seed_movies` / `seed_series` | clasificaciones, compañías, géneros, tipos y roles |
| `seed_music` | tipos de álbum y de artista, roles y géneros (con `deezer_id`) |
| `seed_games` | motores, plataformas, medios y géneros (55 marcados +18) |
| `seed_otaku` | años, roles, géneros, temas, demografías, tipos, estados y fuentes |
| `seed_mailing` | plantillas de correo (`--force` sobrescribe) |

**Géneros musicales y Deezer.** `default_music_genres` (`apps/music/management/data/seed_data.py`) trae el `deezer_id` de los 176 géneros
musicales de Deezer (sondeo de `GET /genre/{id}` del 2026-09-10: los 23 principales más sus subgéneros; 2 = African
Music, 132 = Pop, 116 = Hip Hop, 67 = Salsa…). Los ids que NO son música («Todos», podcasts como Sports o True
crime, moods como Party, audiolibros) están en `DEEZER_NO_MUSICA` (services/deezer.py) y nunca se crean como
género, vengan de `/genre`, de un álbum o de un artista. Un id musical que no esté en el seed se crea igual, pero
deja un aviso (nivel 40) «género nuevo» en el log de música para revisarlo. El importador casa primero por id, luego por
nombre en inglés o español (`name` / `name_esp`, porque Deezer responde en el idioma de la IP) y solo entonces
crea. Al volver a sembrar, si el importador ya había creado el género con el nombre de la API («Música
Africana», id 2), esa fila se queda (con sus artistas y álbumes), toma los nombres del seed y la copia sin id
se funde en ella. Ids nuevos de Deezer: se agregan al seed y se vuelve a correr `seed_music`.

---

## 7 · Backup y restauración (Docker)

`dump/` y `media/` están montados: lo que el contenedor escribe aparece en tu carpeta.

El backup guarda **una tabla por archivo** dentro de `dump/bd-<fecha>/`, para poder restaurar solo la que
haga falta. Las tablas vacías no generan archivo.

```bash
docker compose exec web python manage.py backup            # dump/bd-<fecha>/<app>.<modelo>.json.gz + zip de media
docker compose exec web python manage.py backup --unico    # todo en un dump/bd-<fecha>.json.gz (como antes)
docker compose exec web python manage.py backup --sin-media
```

Restaurar TODO reemplaza: vacía las tablas y carga los archivos en una sola transacción (así el orden entre
tablas no importa).

```bash
docker compose exec web python manage.py loadbackup                  # el último backup, entero
docker compose exec web python manage.py loadbackup --archivo dump/bd-20260915-0034
docker compose exec web python manage.py loadbackup --sin-flush      # no vacía antes (puede chocar con únicos)
```

Restaurar UNA tabla no toca el resto. Con `--vaciar` borra antes las filas de esa tabla (ojo con lo que
cuelgue de ella por clave foránea).

```bash
docker compose exec web python manage.py loadbackup --tabla games.Game
docker compose exec web python manage.py loadbackup --tabla games.Game --vaciar
docker compose exec web python manage.py loadbackup --tabla games.Game --tabla games.Creator
```

### Solo los datos crudos (lo caro de volver a bajar)

Lo bajado de VNDB, MAL o Deezer son horas de scrapeo. `--datos` respalda solo esas tablas (`Data*` y `Raw`),
en `dump/datos-<fecha>/`, para poder migrar o rehacer otra tabla sin miedo y devolverlas después.

```bash
docker compose exec web python manage.py backup --datos
docker compose exec web python manage.py backup --tabla games.DataVndbGame --tabla games.DataVndbCreator
docker compose exec web python manage.py loadbackup --archivo dump/datos-<fecha> --tabla games.DataVndbGame
```

Una migración que toca OTRA tabla no invalida estos respaldos. Lo que sí los invalida es cambiarle los campos
a la propia tabla de datos: el archivo lleva los nombres viejos y `loaddata` se queja. En ese caso, respalda
ANTES de migrar y vuelve a respaldar después.

**Renombrar un modelo también los invalida**, y de forma más silenciosa: el respaldo guarda la etiqueta
`app.modelo` dentro de cada fila y en el nombre del archivo (`games.datavndbgame.json.gz`), así que tras un
renombre `loadbackup --tabla` ya no encuentra su destino. Si hay que renombrar, las opciones son recargar desde el
origen, o reescribir el respaldo (nombre de archivo y clave `model` de dentro) antes de restaurarlo.

### Empezar de cero y recuperar

```bash
docker compose down -v                                        # borra el volumen de Postgres (el dump/ NO: es una carpeta tuya)
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py loadbackup
```

`dump/` no va a git. El backup zero con el superadmin se añade a mano: `git add -f dump/bd-<fecha>.json.gz`.
Los dumps anteriores a un renombre de apps o modelos no cargan: llevan las etiquetas viejas.

---

## 8 · Importación externa

Los datos de fuera entran de DOS maneras, y cada una tiene su pantalla en el panel.

**Por API (lanzador).** Cada tipo tiene el suyo dentro de su app, y se entra por la lista de datos de la entidad,
con su botón «Importar»: Juegos → VNDB (`/panel/vndb/game/`, `creator/`, `release/`, `character/`), Música → Deezer
(`/panel/deezer/artist/`, `album/`, `song/`, `genres/`). En cada uno: por nombre (buscador), por id o rango, y
«Procesar pendientes» de la fuente. Las pistas de Deezer llegan con su álbum. Las tareas van por Celery cuando
`CELERY_ENABLED=1`; si no, corren en línea.

**Por DUMP (archivo).** Dos pasos: se sube el `.json` o `.json.gz` y se ve el RESUMEN de lo que va a entrar antes de
aplicar nada. Se entra por el grupo «Dumps» del home de la app. El archivo queda guardado en `dump/` con su fecha.

| Fuente | Dónde | Qué llena |
|---|---|---|
| MAL · anime, manga, personaje, persona | `/panel/mal/dump/<tipo>/` | `DataMal<Entidad>` y su `…Picture` (las `images_extra`) |
| VNDB · juego, creador, lanzamiento, personaje | `/panel/vndb/dump/<tipo>/` | `DataVndb<Entidad>` |
| VNDB · tags | `/panel/vndb/load-tags/` | `games.Genre` y `games.Tag` (este SÍ crea entidades, no tabla Data) |

MAL entra **solo** por dump. El JSON se guarda tal cual, con las claves del archivo
(`person_id`, `character_id`, `mal_id`, `more`, `image_url`, `images_extra`), sin traducir. Hay ejemplos de los
cuatro en `docs/examples/`.

Los dos caminos escriben SOLO en las tablas `Data*`, con `data_processed=False`. **Procesar es otro paso**, desde la
lista de esa tabla: «Procesar pendientes» para todo lo que falte, o «Procesar» en el menú de una fila para repetir
una sola. Cada importación deja rastro en el log de su app.

**Tags de VNDB (dump oficial)**: `/panel/vndb/load-tags/` sube o descarga `vndb-tags-latest.json.gz`, muestra el
resumen (N en el dump, se crean, cambian, iguales, desaparecen) y al continuar aplica por `vndb_id`: cont y ero →
géneros (ero explícito), tech → etiquetas, y sus alias a `GenreAlias` / `TagAlias`; lo que ya no viene queda inactivo.
Comando: `docker compose exec web python manage.py load_vndb_tags [--download | --file ruta]`. `initial_setup` NO lo
aplica: los tags son externos, no parte del seed. El importador de juegos sigue creando al vuelo los que no existan,
con su `vndb_id`, así el siguiente dump los renombra en vez de duplicarlos.

**Generar nuestro propio dump (export)**: el botón «Generar dump» de cada lista de datos descarga esa tabla como
`.json.gz`. Sirve de respaldo alternativo al de la base y vuelve a entrar por el cargador de su misma entidad.

---

## 9 · Tests por app (Docker)

Cada app tiene su `apps/<app>/tests.py` (humo: todas sus rutas del panel y públicas, y las listas «by» con tipo o id
inválidos → 404) sobre la base `core/shared/testing.py`. Un comando, una acción:

```
docker compose exec web python manage.py test_changed              # solo las apps con archivos modificados desde la última corrida
docker compose exec web python manage.py test_changed --app otaku  # una app (repetible)
docker compose exec web python manage.py test_changed --all        # las 12
```

El reporte queda en `dump/tests/<fecha>-<apps>.md` (visible fuera del contenedor); la marca de «última corrida» es
`dump/tests/.ultima`. Cambios en `core/` o `templates/` cuentan para todas las apps. Usa la base de test (`test_<DB_NAME>`),
creada y destruida en cada corrida (así nunca queda vieja tras un reinicio de migraciones).

## 10 · Plantillas del panel

```bash
docker compose exec web python manage.py sync_forms [app …] [--check] [--force]      # plantillas de campos por entidad
```

`--check` solo reporta; `--force` regenera y pisa ediciones. Las plantillas viven en `apps/<app>/templates/<app>/form/` y `detail/`.

---

## 11 · Diagnóstico

```bash
docker compose exec db psql -U artemisa -d artemisa     # SQL directo
docker compose exec web python manage.py shell          # shell Django dentro del stack
docker compose exec web python manage.py check          # chequeos de Django
docker compose logs worker | Select-String succeeded    # tareas Celery terminadas
python manage.py runserver 8001                         # runserver local contra el Postgres del stack (localhost:55432)
```

## Medir tiempos antes de programar lotes (2026-09-10)

Antes de fijar «100 artistas al día» o «100 juegos al día», se cronometra UNA importación pesada y se
proyecta. Cada importación deja ya en su log una línea de resumen con `N peticiones · T s`; el comando
lo hace en el acto, sin Celery, respetando el rate limit real (Deezer 50 llamadas/5 s, VNDB 200/5 min):

```
docker compose exec web python manage.py medir_import deezer artista --buscar "Mozart"     # el peor caso: miles de álbumes
docker compose exec web python manage.py medir_import deezer artista --buscar "Elvis Presley"
docker compose exec web python manage.py medir_import vndb juego --buscar "Fate/stay night"  # v11: decenas de lanzamientos y personajes
docker compose exec web python manage.py medir_import vndb juego 4 --lote 100                 # Clannad
```

Imprime álbumes/canciones (o lanzamientos/personajes/capturas), peticiones, segundos y cuánto tardaría el
lote (`--lote`, 100 por defecto). Con eso se ajusta la `cantidad` de las tareas programadas «Obtener datos ·
Deezer/VNDB» en el panel de Tareas, y aparte la de imágenes (100 descargas y 100 subidas a R2 al día).
Un artista de Deezer cuesta 2 peticiones + 1 por página de álbumes + 1 por álbum (+1 por página de pistas
si pasa de 25); un juego de VNDB, 1 + 1 por página de lanzamientos y de personajes (100 por página).

**Artistas grandes no frenan el lote.** `import_artist` trae y procesa EN LÍNEA los primeros 25 álbumes
(`ALBUMES_EN_LINEA`); el resto lo reparte en tandas de 25 como tareas aparte (`import_artist_albums_task`),
que otro proceso del worker toma en paralelo (`--concurrency=2` en docker-compose: dos procesos, cada uno con
su propio respeto al límite de Deezer). El lote de artistas sigue con el siguiente mientras las tandas corren;
un Mozart de 5.000 álbumes son 200 tandas que se van despachando solas. Sin broker (`CELERY_ENABLED=0`) las
tandas corren en el acto, una tras otra.

**El lote de Deezer es una tarea por artista.** «Trae 1.000 artistas» (rango, archivo o siguiente lote) encola
1.000 tareas de un artista cada una: los dos procesos del worker importan artistas distintos a la vez, se cancela
artista por artista en Ejecuciones, y el lote en sí termina en segundos (solo reparte). VNDB NO: su límite es
global (200 peticiones cada 5 min, una cada 1,6 s), así que su lote sigue en serie dentro de una sola tarea.

## Correos: maqueta única (2026-09-11)

`apps/mailing/layout.py` envuelve TODO correo (envío y vista previa del panel) en la misma maqueta: tabla
centrada de 600 px, cabecera oscura con la marca, cuerpo blanco, botón cian y pie gris con la firma de la
config. Las plantillas (`seed_mailing`) guardan solo el contenido: título, párrafos y botón. Si tu base ya
tenía las plantillas viejas (tarjeta oscura), restáuralas con `docker compose exec web python manage.py
seed_mailing --force` (pisa las editadas a mano).

## Lanzadores manuales: qué se importa a mano (2026-09-10)

Deezer: **géneros** (todos de una llamada, sin id) y **artista** (trae su discografía completa: álbumes y
pistas; no hay lanzador de álbum suelto). VNDB: **juego** (con lanzamientos, personajes, capturas, editoras)
y **creador** (con «traer todos sus juegos»); no hay lanzador de personaje ni de lanzamiento sueltos. MAL entra solo por dump; lo que
se importa en vivo es AniList. Los servicios de álbum, personaje y
lanzamiento siguen existiendo por dentro (los usan las cadenas), solo no tienen página.

## Cursor de lote: el buscador no mueve el beat (2026-09-10)

El «siguiente lote» y la sugerencia del rango NO parten del mayor id descargado: parten de un **cursor por
fuente y tipo** (`system.ImportCursor`, panel → Tareas → Cursores de lote). Buscar One Ok Rock por nombre e
importarlo (#4531854 en Deezer) deja su fila en Datos crudos pero no toca el cursor, así que el lote de
artistas sigue en el #101. Lo mueven solo el lote programado/«Ejecutar ahora» (avanza N) y un rango manual
que lo continúe (inicio ≤ próximo id ≤ fin: «del 1 al 5.000» avanza; «del 4531854 al 4531854» no). Nunca
retrocede solo; en el panel se edita para saltar o repetir, y borrarlo lo devuelve a 1.

El cursor guarda el **próximo id a intentar**, no el último obtenido: si del 1 al 100 el #99 no existe en la
API, queda en 101 igual (los huecos de ids son normales y no se vuelve a ellos). Un fallo de red deja su fila
en Datos crudos con estado en falso y se repite con «Re-obtener datos». La fila del cursor es el
**mantenedor del lote**: lleva la *cantidad por lote* (la única: ni la programada ni el código la fijan) y
la acción «Lanzar lote ahora», que encola el siguiente lote con esa cantidad. El lanzador de rango precarga
*inicio* con el próximo id del cursor y *fin* con inicio + cantidad − 1; si dejas *fin* vacío, usa esa
cantidad, y si lo cambias (99, 1.000…) manda lo que escribas.

## Lotes de datos: manuales por ahora (2026-09-10)

Las tareas programadas de DATOS (artistas Deezer, animes/mangas MAL, juegos VNDB, re-obtener viejos,
subida a R2) existen desde el seed pero nacen **apagadas**: beat no las toca. No llevan cantidad: el lote
toma el **próximo id y la cantidad por lote del cursor** (`ImportCursor`, sembrado en 1 y 100; se edita en
Tareas → Cursores de lote). Se lanzan a mano con **Ejecutar ahora** (fila de la programada) o **Lanzar lote
ahora** (fila del cursor), esté activa o no, y se siguen en Ejecuciones. Las tareas que no son de lote
(descargar imágenes, subir a R2, re-obtener viejos) llevan su `cantidad` en los argumentos JSON. Cuando las mediciones (`medir_import`) digan cuánto
aguanta una noche, se enciende la fila y queda programada sin cambiar nada más. Siguen activas desde el
seed: procesar pendientes (cada 30 min), descargar imágenes a disco (2.000 a las 05:00) y las limpiezas.

## Tareas Celery: registro, cancelador y programadas (2026-09-10)

- **Niveles de log** (catálogo LogLevel, escala de Poseidon): 20 Info · 30 Success · 40 Warning · 50 Error · 60 Critical. Todo lo que es «hay que mirarlo» es >= 40: es lo que enseñan el dashboard y los lanzadores, y lo que NO borran las limpiezas.
- **Registro**: cada tarea (importación, post-proceso, programada) queda en `system.TaskRun` por las señales de Celery de `core/celery.py`: en cola → ejecutando → terminada / fallida / cancelada, con argumentos, quién la lanzó y duración. Panel → Navegación → Tareas → Ejecuciones.
- **Cancelador** (como el de Poseidon): en la fila, «Cancelar (cooperativa)» marca la bandera y manda `revoke` suave; los bucles largos (rango de ids, álbumes de un artista, ids de archivo) consultan `core.shared.tasks.cancel.cancelado()` entre pasos y se detienen solos, dejando lo ya guardado. «Terminar (forzada)» manda `revoke(terminate=True)` y mata el proceso: último recurso.
- **Programadas (beat)**: la tabla `system.ScheduledTask` (Panel → Tareas → Programadas) dice qué tarea, cada N minutos o a qué hora, y si está activa. `beat` solo corre `apps.system.tasks.dispatch_scheduled_task` cada minuto, que encola lo que toque. `seed_system` crea las cinco por defecto: procesar pendientes de Deezer / MAL / VNDB cada 30 min, limpiar tareas terminadas (04:00) y logs informativos (04:10), ambas de más de 7 días.
- **Obtener datos de X una vez al día**: cada fuente tiene `import_<fuente>_next_batch_task(kind, cantidad)` = el SIGUIENTE LOTE desde el id siguiente al mayor descargado (el «seguir donde me quedé»). El seed programa: géneros Deezer (02:50), 50 artistas Deezer (03:00), 50 animes (03:20) y 50 mangas MAL (03:40), 50 juegos VNDB (04:20). Cambia tipo y cantidad en el panel: `kwargs` = `{"kind": "anime", "cantidad": 50}`.
- **Imágenes**: los importadores dejan la URL en la tabla de imágenes (`image_url`, `image_downloaded`); `apps.system.tasks.download_pending_images_task(cantidad)` baja hasta N al día (programada a las 05:00, 100). En cualquier lista de imágenes, la acción masiva «Descargar imágenes pendientes» baja las marcadas; en Género y Artista de música, «Imagen desde Deezer» la trae del JSON ya descargado. El archivo va **siempre a disco local** (`media/`). La nube es otro paso: con `USE_R2=1`, `apps.system.tasks.upload_pending_to_cloud_task(cantidad)` sube N archivos al día a R2 (programada a las 05:30, 100: el tope de subidas de R2), los anota en `system.CloudFile` y desde entonces la URL pública de ESE archivo apunta al dominio de R2 (`core/storage.py`); el resto sigue en `/media/`. En cualquier lista con imágenes, la acción masiva «Subir a la nube (R2)» sube las marcadas que ya estén descargadas (solo aparece con `USE_R2=1`). Con `USE_R2=0` nada cambia: todo local, y habilitar R2 después no obliga a migrar de golpe.
- **VNDB** (juegos): `import_game(id)` trae la VN, TODOS sus lanzamientos (POST /release por vn, paginado) y sus personajes (POST /character por vn) a `DataVndbGame`, `DataVndbRelease` y `DataVndbCharacter` (con `vndb_id_vn`). El proceso crea el Game con portada, idiomas, plataformas y desarrolladores, y de los lanzamientos suma editoras (productores con `publisher`), plataformas, idiomas y la fecha más antigua; un productor que falta se trae entero (`Creator`). VNDB no tiene géneros: los tags de contenido (sin spoiler, votación >= 2, los 10 mejores) entran como Género del juego. Los lanzamientos son reales: `GameRelease` enlazado al juego con plataformas, idiomas, editoras y desarrolladores. Los personajes son reales: `GameCharacter` con sus roles por juego (`GameCharacterRole`) e imágenes (`GameCharacterImage`, URL que baja el descargador). Importar un personaje (c<id>) o un lanzamiento (r<id>) suelto trae su juego si falta: no viven sin él; un creador sí vive solo. `Game.vndb_fetched_at` guarda la última obtención y la programada «Re-obtener juegos VNDB viejos» vuelve a traer 20 al día con más de 30 días; en la lista de Juegos, «Re-obtener de VNDB» hace lo mismo con los marcados. Los lanzadores de Juego y Creador tienen buscador por nombre; Importar creador con «con todos sus juegos» trae cada VN que desarrolló (POST /vn por developer, paginado), y en la lista de Creadores la acción masiva «Traer todos sus juegos de VNDB» hace lo mismo con los marcados. `DataProducerVNDB` murió: era `DataVndbCreator` con otro nombre. Idiomas y plataformas CASAN con el catálogo: el código VNDB del idioma va contra `Language.iso_639_1` (sin importar mayúsculas) y el de plataforma contra `Platform.vndb_code`; si no existe se crea con nombre legible y su código, nunca con el código como nombre. VNDB permite 200 peticiones / 5 min: ~1 s entre llamadas.
- Tras cambiar código de tareas: `docker compose restart worker beat` (no se autorecargan).

## Reinicio desde cero (2026-09-13)

La secuencia canónica está en §5. `initial_setup --dev` deja el superusuario **admin / admin** y el usuario
**rallende / rallende123** (claves de desarrollo); sin `--dev`, pide el superusuario al final. Las portadas viven en la
tabla de imágenes de cada entidad; la media va en `media/<app>/<entidad>/<slug>/`.
