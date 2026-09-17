# Fondos — cómo crear y usar uno

Cómo funciona el fondo por vista (la imagen de categoría que va **detrás de todo**)
y el **paso a paso** para agregar uno nuevo. Para la _transparencia/opacidad_ de
esos fondos ver [transparencias.md](transparencias.md).
El INVENTARIO completo (qué clases hay, cuáles tienen imagen, cuáles faltan y dónde se ve cada una) está más abajo, en un solo lugar.

Estilo Poseidon: **la vista declara una clase, el CSS mapea esa clase a 4 imágenes,
y el navegador baja solo la que aplica según la forma de la pantalla.**

---

## Las 2 piezas

```
1) IMÁGENES  →  apps/<app>/static/image/screen/<orientación>/bg-<app>-<x>.webp   (cada app las suyas)
                orientaciones: wide · landscape · portrait · tall
                                 │
2) VISTA      →  background_image = "bg-<app>-<x>"
                la plantilla base pega la clase en <div class="bg-layer …"> y el tag
                {% bg_style background_image %} (core/templatetags/fondos.py) le pone en línea
                --bg-wide/landscape/portrait/tall con las 4 rutas; 01-base.css elige por aspect-ratio.
```

- **01-base.css** (`.bg-layer::before`) elige por `aspect-ratio`: wide (default) →
  landscape (≤16/10) → portrait (≤1/1) → tall (≤3/5). Solo se descarga la que aplica.
- Las imágenes viven **en su app** (`apps/<app>/static/image/screen/`), todas las apps. Para el navegador es lo mismo: Django junta los `static/` de todas las apps en la misma
  ruta `/static/image/screen/…` (`AppDirectoriesFinder`). No hay CSS por clase: el tag resuelve las rutas con
  `static()` y comprueba que existan (`finders`), sin importar en qué carpeta esté el archivo.

---

## Paso a paso: agregar un fondo nuevo

Ejemplo: darle fondo propio a la entidad **Álbum** de música (`bg-music-album`).

### 1. Deja las imágenes (idealmente las 4 orientaciones)

```
apps/music/static/image/screen/wide/bg-music-album.webp
apps/music/static/image/screen/landscape/bg-music-album.webp
apps/music/static/image/screen/portrait/bg-music-album.webp
apps/music/static/image/screen/tall/bg-music-album.webp
```

> Con solo `wide` ya se ve (las demás son mejoras para móvil/vertical). El nombre
> del archivo **debe** ser `bg-<app>-<x>.webp` y coincidir con la clase. La carpeta es la de la app **dueña** del
> prefijo (`bg-music-…` → `apps/music/static/`; `bg-coleccions-…` → `apps/collections/static/`).

### 2. Úsalo en la vista

```python
class BaseAlbum:
    background_image = "bg-music-album"   # ← la clase, sin punto
```

La plantilla base ya hace el resto:
`<div class="bg-layer {{ background_image }}"></div>` (en `base.html` y `base_admin.html`).

### 3. Recarga

Nada más: no hay CSS que tocar ni versión que subir. Con hot reload basta refrescar (Ctrl+Shift+R).

---

## Verificar que todo cuadra

```bash
python manage.py fondos_check
```

Avisa: clases `bg-<app>-<x>` **sin imagen**, imágenes **huérfanas** (sin clase),
clases a las que les **falta** alguna de las 4 orientaciones e imágenes guardadas en la **carpeta de otra app**.
Mira `apps/*/static/image/screen/` (y `static/image/screen/` por si quedara algo en la raíz).

---

## Notas útiles

- **Fallback entre clases:** si una vista pone una clase que no existe, `.bg-layer`
  queda en el color base `--ground` (gris oscuro), sin romper.
- **Fondos de las CARDS** de la home de sección (blur) son otra cosa: usan la imagen `wide` de la clase
  que la card DECLARA (4.º elemento de la tupla); si falta, la del home de la sección. Nada se deduce
  del modelo. Ver [README.md](../README.md) §1 y [transparencias.md](transparencias.md).
- **La carpeta es la fuente.** `03-backgrounds.css` murió el 2026-09-11: sus 1.600 líneas solo repetían
  cuatro rutas por clase y había que editarlo a mano con cada imagen. Ahora `{% bg_style %}` las pone en línea.
- **Listas «por»** («Animes del género X», «Personas de Chile»…, `XByListView` / `XByListView` sobre el
  mixin `BaseXBy` de base.py): el fondo es el de la **taxonomía**, no el de lo listado (regla Poseidon), y se DECLARA
  como 3.er elemento de cada entrada del mapa `filter_config`: `"genero": ("genres", _("Animes del género {padre}"), "bg-otaku-genre")`.
  Si esa imagen falta, cae al fondo de la lista (`background_image` de la ListBy). Nada se deduce del modelo.
- **Fichas (detalle de un objeto):** el fondo es el de la CLASE de la vista (`bg-movies-movie`…), igual que en las
  listas; la imagen del objeto va en el póster del lateral, no de fondo (decisión de René, 2026-09-11).
- **Orientación que falta:** si existe la `wide` pero no la `landscape`, el tag usa la `wide` en su lugar
  (antes el CSS apuntaba a un archivo inexistente y esa pantalla quedaba sin fondo).
- Orientaciones y su breakpoint (en `01-base.css`):

    | Variable         | Cuándo se usa                          |
    | ---------------- | -------------------------------------- |
    | `--bg-wide`      | pantalla ancha (desktop) — por defecto |
    | `--bg-landscape` | `aspect-ratio ≤ 16/10`                 |
    | `--bg-portrait`  | `≤ 1/1` (cuadrado o vertical)          |
    | `--bg-tall`      | `≤ 3/5` (móvil muy vertical)           |

## Tamaños

| Carpeta     | Aspecto | Ancho x Alto PX (real, medido el 2026-09-11 en las 185 imágenes) |
| ----------- | ------- | ---------------------------------------------------------------- |
| `wide`      | `16:9`  | `1920 x 1080`                                                    |
| `landscape` | `4:3`   | `1440 x 1080`                                                    |
| `portrait`  | `3:4`   | `1080 x 1440`                                                    |
| `tall`      | `9:16`  | `1080 x 1920`                                                    |

Las 185 imágenes existentes miden exactamente eso (Full HD, no 4K): una imagen nueva debe venir en esas cuatro medidas
para que pese y se vea como las demás (~270 KB de media por archivo). No se corre `optimizar_fondos.py` sobre ellas.

---

## Regla «un modelo, una imagen»

Cada modelo del proyecto tiene UNA entidad en el panel y pide `bg-<app dueña>-<modelo>`: la app donde vive el
modelo, aunque el panel lo muestre en otra sección (las tablas Data de importación piden `bg-otaku-…`, `bg-games-…`,
`bg-music-…`). El nombre lo fija el código; las imágenes se renombran a mano para coincidir (nunca se borran).

**Fuertes y extras.** Un fondo FUERTE es el maestro de una entidad, de un home o de la importación de una app.
Un EXTRA es una variante que lo extiende porque su vista es otra función sobre lo mismo: las vistas fijas por estado o
tipo (`bg-mailing-email-message-queued`, `bg-otaku-anime-song-opening`) y los lanzadores de importación (`bg-otaku-import-anime`).
Cada extra tiene su propia imagen; mientras no exista, cae a su fuerte y luego al home de la app.

**Excepciones** (decididas por René): los homes e index no son modelos; las secciones de pages usan la imagen de su
página pública (`bg-pages-about`, `-terms`, `-privacy`); `mailing.MailConfig` es un registro único cuya página de
configuración pide `bg-mailing-mail-config`; y `otaku.PersonMAL` pide `bg-otaku-person`, porque ES la persona del
mundo otaku (persona, apodo, imagen e imagen extra con `bg-otaku-person-*`).

---

## Inventario (generado desde el código el 2026-09-16)

| | |
|---|---|
| Fondos que pide el código | 196 |
| Con imagen | 196 |
| **Faltan imágenes** | **0** |
| Imágenes en disco | 196 |
| Imágenes que nadie usa | 0 |
| Imágenes sin las 4 orientaciones | 0 |
| Imágenes en la carpeta de otra app | 0 |

| App | Carpeta de sus imágenes | Pide | Con imagen | Faltan |
|---|---|---|---|---|
| catalogs | `apps/catalogs/static/image/screen/` | 9 | 9 | 0 |
| collections | `apps/collections/static/image/screen/` | 14 | 14 | 0 |
| companies | `apps/companies/static/image/screen/` | 3 | 3 | 0 |
| games | `apps/games/static/image/screen/` | 32 | 32 | 0 |
| mailing | `apps/mailing/static/image/screen/` | 7 | 7 | 0 |
| movies | `apps/movies/static/image/screen/` | 14 | 14 | 0 |
| music | `apps/music/static/image/screen/` | 19 | 19 | 0 |
| otaku | `apps/otaku/static/image/screen/` | 58 | 58 | 0 |
| pages | `apps/pages/static/image/screen/` | 8 | 8 | 0 |
| people | `apps/people/static/image/screen/` | 6 | 6 | 0 |
| series | `apps/series/static/image/screen/` | 14 | 14 | 0 |
| system | `apps/system/static/image/screen/` | 8 | 8 | 0 |
| users | `apps/users/static/image/screen/` | 4 | 4 | 0 |

El detalle fondo por fondo (tipo, orientaciones y qué vista lo pide) está en [fondos_estado.md](fondos_estado.md); la lista para producir las que faltan, en [fondos_faltantes.md](fondos_faltantes.md). Se regeneran con el mismo recorrido que `python manage.py fondos_check`.

---

## Ver también

- [transparencias.md](transparencias.md) — opacidad del fondo y de los paneles + blur de las cards
- [README.md](../README.md) — capa de vistas · [usos_vistas.md](usos_vistas.md) — glosario
- [comandos.md](comandos.md) — `fondos_check`, `collectstatic`, `ASSET_VERSION`
