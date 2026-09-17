# people — Personas

Persona real (actores, autores, staff, artistas, creadores) + apodos e imágenes.
Es la entidad **transversal** del catálogo: `movie`, `serie`, `music` y `otaku` la
apuntan por FK, y la ficha pública `/personas/<id>/<slug>/` cruza todas sus obras.

- Panel: sección **Personas** de `/gestion/` (`gestion:people-home`), rutas en `gestion_urls.py`.
- Público: namespace `personas` (`urls/public.py`), montado en `/personas/` desde `core/urls.py`.
- El hub de **compañías** (`/companias/`) sigue en `apps/common` (Company es por app).

## Person es NEUTRA; lo de cada fuente cuelga aparte

Person solo tiene lo que cualquier fuente sabe (nombre, biografía, nacimiento, país,
imagen). Lo que **solo MAL** sabe vive en `otaku.PersonMAL` (OneToOne, accessor
`person_mal`): `mal_id`, nombre en kanji (`family_name`/`given_name`), nombres
alternativos, favoritos, sitio web y about. La escritura pasa SIEMPRE por
`apps/otaku/services/personas.py::upsert_persona_mal` — la usan el procesado del dump
de MAL y el formulario «Personas (MAL)» del panel de Otaku (alta manual, p. ej.
Nana Mizuki con su kanji). Regla: MAL rellena los campos neutros solo si están
vacíos; los campos MAL son de MAL. La ficha pública pinta el bloque MAL si existe.

## Origen

Person nació en `common` (hoy `catalogs`) y se movió aquí el 2026-09-06. Ese mismo día el
historial de migraciones se REINICIÓ desde cero: las tablas son `people_*` y la 0001 de la
app es la única migración (las tablas viejas `common_person…` ya no se renombran: el comando
`rename_apps` cumplió su función y se eliminó).

Comprobar tras migrar: `python manage.py makemigrations --check --dry-run` debe decir
«No changes detected».
