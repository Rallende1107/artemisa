# Mejoras por definir

Ideas conversadas y **no aplicadas**. Cada una trae el contexto y las opciones; se elige antes de tocar código.

## Ficha MAL de compañía: formulario más simple (2026-09-17)

**Hoy:** el formulario pide compañía, *Tipo en MAL* (compañía / revista), *MAL id* y *URL*.

**Por qué el tipo no se puede quitar del modelo:** MAL numera compañías y revistas por separado. El mismo id existe dos
veces (Studio Pierrot = compañía 1, Big Comic Original = revista 1). Sin el tipo no hay URL, ni clave única
`(kind, mal_id)`, ni cruce con los dumps (`company_mal_id` de anime = compañía; `serializations` de manga = revista).
La URL ya se calcula sola (`CompanyMAL.mal_url`) cuando no viene guardada.

**Opciones para el formulario:**

1. **Pegar la URL de MAL** (recomendada): un solo campo; `…/manga/magazine/100` → revista 100, `…/anime/producer/14`
   → compañía 14. Tipo e id se llenan solos (solo lectura).
2. **Tipo + id:** como hoy, pero sin el campo URL (se calcula).
3. **Cualquiera de las dos:** si se pega la URL se deduce; si no, tipo + id.

## Lista de compañías (MAL): botones para navegar a lo relacionado (2026-09-17)

**Hoy:** la lista `panel:company-mal_list` solo tiene «Otaku», «Nuevo compañía (MAL)» y «Enlazar a compañía existente».
Para ir a la lista general de compañías o a sus imágenes hay que volver al home y entrar por otro lado.

**Propuesta:** botones extra en la barra (`alta_extra`, con icono):

- **Compañías** → `panel:company_list` (la lista general, neutra, de todos los medios).
- **Imágenes de compañías** → `panel:company-image_list` (logos; desde ahí «Descargar imágenes»).
- **Cargar dump de compañías (MAL)** → `panel:dump-mal-company` (se entra hoy solo desde el home de Otaku).

**Por definir:** si el mismo criterio va también al revés (en la lista general de compañías, un botón a «Compañías
(MAL)» y a sus imágenes) y en las demás extensiones MAL (Personas (MAL) → Personas / Imágenes de personas).

## Listas: recargar los datos sin F5 (2026-09-17) — HECHO

- Botón «Recargar datos» (↻) **antes del buscador**, en las listas de gestión y en las públicas: la misma página, orden,
  búsqueda y filtros.
- **Tareas** se auto-recarga cada 5 s mientras haya ejecuciones en cola o corriendo (el ↻ queda encendido) y se detiene
  sola cuando no queda ninguna. Otra lista puede activarlo con `auto_recarga = N` en su ListView si su Data devuelve
  `activas` en el JSON.

**Por definir:** auto-recarga opcional (interruptor «Actualizar cada N s») en Imágenes y Log.

## Fondos de las tablas de datos crudos: uno por fuente (2026-09-17)

**Hoy:** cada tabla de datos crudos tiene su propio fondo: `bg-otaku-data-mal-anime`, `-manga`, `-character`,
`-person`, `-anime-character`, `-anime-staff`, `-manga-character`, y los `-picture` (que ya no se usan). Lo mismo en
AniList (`bg-otaku-data-anilist-*`, uno por entidad).

**Propuesta:** un solo fondo por FUENTE, como se hizo con ratings, temporadas y tipos:

- `bg-otaku-data-mal` para todas las tablas `DataMal*`.
- `bg-otaku-data-anilist` para todas las `DataAnilist*` (lanzador incluido).

**Implica:** cambiar `background_image` en las clases Base de esas tablas, mover a `renombrar/` las imágenes que
queden sin uso y actualizar `docs/fondos*` y el Excel. Sin migraciones.

**Por definir:** si los «Cargar dump» (`bg-otaku-load-dump-*`) también se unifican en uno solo (`bg-otaku-load-dump`).
