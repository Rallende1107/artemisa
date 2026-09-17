# Transparencias · Artemisa

> Dónde y cómo se controla la **transparencia del sitio sobre el fondo** (la imagen de
> categoría que va detrás de todo). Todo son **tokens** en `static/css/00-tokens.css`;
> aquí se listan con su archivo de uso y cómo subir/bajar la visibilidad.

---

## Mapa mental (2 capas)

```
[ imagen de fondo ]      ← capa .bg-layer  (opacidad + velo oscuro)
   ↑ se ve a través de ↑
[ paneles del sitio ]    ← header, sidebar, form-card, footer, cards  (glass + blur)
[ contenido / texto ]
```

- **Capa 1 – el fondo**: qué tan visible se ve la *foto*.
- **Capa 2 – los paneles**: qué tanto se ve el fondo *a través* de header/sidebar/formularios/footer.

Todos los valores viven en **`static/css/00-tokens.css`**.

---

## Capa 1 — La imagen de fondo (`.bg-layer`)

Aplicada en **`static/css/01-base.css`** (`.bg-layer::before` = imagen, `.bg-layer::after` = velo).

| Token (`00-tokens.css`) | Valor | Qué hace |
|---|---|---|
| `--bg-opacity` | `1` | Opacidad de la **imagen** misma. ↑ = foto más nítida · ↓ = más apagada. |
| `--overlay-top` | `rgba(8, 8, 13, 0.34)` | Velo oscuro **arriba**. ↑ alpha = tapa más. |
| `--overlay-bottom` | `rgba(8, 8, 13, 0.34)` | Velo **abajo**. Decisión vigente: IGUAL al top → velo UNIFORME, sin gradiente (mover los dos juntos). |
| `--ground` | `#0a0a0f` | Color base detrás de la imagen (si no carga). |

> **Estado actual**: velo suave para **apreciar la foto** (antes `0.72 / 0.66 / 0.86` la
> apagaba). Si el texto sobre el fondo cuesta de leer, sube `--overlay-bottom` a `0.72`.

`.bg-layer::after` también tiene `backdrop-filter: blur(1px)` (`01-base.css:50`).

**Recetas rápidas** (tocar SOLO estos 3):
- **Fondo más visible** (valores VIGENTES): `--bg-opacity: 1`, overlays parejos a `0.34`.
- **Fondo más apagado** (más legible): `--bg-opacity: 0.7`, overlays parejos a `0.55`.

---

## Capa 2 — Los paneles del sitio (glass + blur)

Cada panel es un `rgba(...)` semitransparente con `backdrop-filter: blur(...)`.

### El CROMO del shell — un solo dial

**header + sidebar + footer** comparten **un único token**: `--chrome-bg`. Cambias
esa línea y los tres se mueven juntos (mismo tono semi-oscuro, visible y translúcido).
Todos llevan `blur(14px)`, así que se ven idénticos.

```css
/* 00-tokens.css */
--chrome-bg:  rgba(0, 0, 0, 0.47);      /* ← EL dial: header+sidebar+footer HOMÓLOGOS (valor René) */
--header-bg:  var(--chrome-bg);         /* heredan del dial */
--sidebar-bg: var(--chrome-bg);
--footer-bg:  var(--chrome-bg);
```

- **Más transparente** (se ve más el fondo): baja el alpha → `0.45`, `0.40`.
- **Más sólido/oscuro** (tapa más): súbelo → `0.65`, `0.72`.
- **Otro tinte**: cambia el RGB `12, 12, 18` (más azulado/neutro/cálido).

### Diales independientes (no son cromo)

| Token (`00-tokens.css`) | Valor | Dónde se usa | Para qué |
|---|---|---|---|
| `--auth-card-bg` | `var(--chrome-bg)` | tarjeta de **login/registro/reset** (`components/auth.css`, `blur(16px)`) | igual al cromo por defecto; **súbele el alpha** con un `rgba(...)` propio si quieres el form más sólido |
| `--panel` | `rgba(18, 18, 26, 0.75)` | **formularios del panel** (`.form-card`) y paneles glass (`components/form.css`, `blur(16px)`) | baja el último número (`0.60`) = más transparente; súbelo (`0.90`) = más sólido |
| `--header-scrim` | gradiente | header público **flotante** sobre la portada | velo de legibilidad del nav; casi nunca hay que tocarlo |

> Para dar al card de login un valor DISTINTO al cromo, reemplaza
> `--auth-card-bg: var(--chrome-bg);` por un `rgba(...)` propio, p. ej.
> `--auth-card-bg: rgba(14, 14, 20, 0.62);` (más sólido, form más legible).

Las **tarjetas** de listado (`components/card.css`) NO son translúcidas: usan un
gradiente sólido `linear-gradient(180deg, var(--elevated), var(--surface))`.

### Listas (DataTables) en cristal — «liquid glass»

Todas las listas del panel y del catálogo público (`.dt-wrap`) son un cristal oscuro que tira a
negro, con blur suave, brillo especular y texto claro. Perillas en `00-tokens.css`
(`components/datatables-theme.css` solo las usa):

| Token | Valor | Para qué |
|---|---|---|
| `--dt-glass-bg` | `rgba(0, 0, 0, 0.42)` | el cristal: ↑ alpha = más oscuro y sólido; ↓ = más transparente |
| `--dt-glass-blur` | `2px` | desenfoque del fondo detrás, al mínimo (2–3 px, valor René) |
| `--dt-glass-saturate` | `140%` | «liquid»: el fondo se ve más vivo a través del cristal; `100%` lo apaga |
| `--dt-glass-shine` | `rgba(255,255,255,0.10)` | brillo especular arriba-izquierda; `0` = sin brillo |
| `--dt-glass-rim` | `rgba(255,255,255,0.14)` | filo de luz de 1 px en el borde superior |
| `--dt-glass-shadow` | `0 12px 32px rgba(0,0,0,.35)` | sombra que despega el cristal |
| `--dt-glass-head` | `rgba(0, 0, 0, 0.35)` | cabecera de la tabla |
| `--dt-glass-row` / `--dt-glass-hover` / `--dt-glass-line` | rayado, fila bajo el ratón, líneas |
| `--dt-glass-ctrl` | `rgba(0, 0, 0, 0.38)` | botones, buscador, «mostrar N», paginación |
| `--dt-glass-menu` | `rgba(0, 0, 0, 0.78)` | desplegables (Acciones de fila, Columnas): más oscuros para leerse sobre cualquier fondo |
| `--dt-glass-menu-blur` | `8px` | desenfoque propio de los desplegables (valor René) |
| `--dt-glass-btn` / `--dt-glass-btn-text` / `--dt-glass-btn-off` | `rgba(0,0,0,0.58)` / `#fff` / `#c9cdd8` | botones de la lista y paginación: fondo, texto activo, texto desactivado |
| `--dt-glass-text` / `--dt-glass-muted` | `#eef0f6` / `#d6d9e3` | texto de celdas / cabeceras y secundario |

Receta: **más cristal** → `--dt-glass-bg: rgba(0,0,0,0.30)` y `--dt-glass-blur: 3px`; **más legible**
→ `rgba(0,0,0,0.58)` y `5px`.

### Cristal líquido en el resto: formularios, login, fichas y detalles

`components/glass.css` (se carga el último en `base.html` y `base_admin.html`) aplica el MISMO cristal a
`.form-card` (formularios del panel), `.auth__card` (login / registro / reset), `.glass` (paneles de
detalle del panel) y `.mal-side` + `.mal-main` (ficha pública estilo MAL). Sus perillas son `--lq-*`
en `00-tokens.css`, con los mismos valores que las listas: `--lq-bg`, `--lq-blur`, `--lq-saturate`,
`--lq-shine`, `--lq-rim`, `--lq-shadow`, `--lq-border`, `--lq-text`, `--lq-muted`. Los antiguos
`--panel` y `--auth-card-bg` quedan sin efecto en esas superficies mientras `glass.css` esté cargado.

---

## Resumen: "quiero tocar la transparencia"

- **Que se vea más/menos la FOTO de fondo** → `--bg-opacity` + `--overlay-top` + `--overlay-bottom`.
- **Cromo del shell (header + sidebar + footer) a la vez** → `--chrome-bg` (un solo dial).
- **Card de login/registro/reset** → `--auth-card-bg`. **Formularios del panel** → `--panel`.
- **Listas (DataTables), cristal líquido** → `--dt-glass-bg` + `--dt-glass-blur` (y el resto de `--dt-glass-*`).
- Tras cambiar cualquiera, **subir `ASSET_VERSION`** en `core/settings.py` y recargar.


---

## Cards de la home de sección — fondo por modelo (blur)

Cada tarjeta de la home de una sección (`/panel/musica/`, `/panel/otaku/`…) muestra la
**imagen única del modelo** detrás, con blur + un velo oscuro para que se lean el título y el
conteo. La imagen se elige sola: `bg-<app>-<modelo-kebab>.webp` (p. ej. `AlbumType` →
`bg-music-album-type`); si no existe, usa la del padre `bg-<app>-home`; si tampoco, la card
queda **gris** (sin `.card--bg`). Lógica en `core/shared/views.py::_card_bg`.

**Clase:** `.card--bg` en **`static/css/components/card.css`**. Los 3 diales:

| Qué | Dónde (en `.card--bg::before` / `::after`) | Valor actual | Cómo |
|---|---|---|---|
| **Intensidad del blur** | `.card--bg::before` → `filter: blur(…)` | `1.5px` | ↑ = más difuso · ↓ = más nítido (`0` = sin blur) |
| **Visibilidad de la foto** | `.card--bg::before` → `opacity: …` | `0.5` | ↑ = foto más visible · ↓ = más apagada |
| **Oscuridad del velo** (para leer el texto) | `.card--bg::after` → `linear-gradient(...)` | `.30 → .55 → .86` | ↑ los alphas = más oscuro/legible · ↓ = se ve más la foto |

- El `transform: scale(1.06)` del `::before` solo evita que el blur deje bordes claros; súbelo si al bajar el blur aparecen filos.
- En hover sube un poco la opacidad (`.card--bg:hover::before { opacity: .68 }`).
- Tras editar, **subir `ASSET_VERSION`** y recargar (el server corre con `--noreload`).

### Cambiar la imagen de una card — control EXPLÍCITO (recomendado)

En la `cards` de la home de sección (`apps/<app>/views/v1_home.py`), cada card acepta
un **5º elemento opcional = la clase de fondo** que quieras. Es el control directo,
en el código, a tu gusto:

```python
cards = [
    #  entity          label                  icono                                  modelo           CLASE DE FONDO (opcional)
    ("tipo-rol", "Tipos de rol", '<i class="bi bi-diagram-3"></i>', RoleType, "bg-catalogs-role-type"),
    ("usuario",  "Usuarios",     '<i class="bi bi-people"></i>',    User,     "bg-users-custom-user"),
    # sin 5º elemento → se deriva del modelo automáticamente:
    ("otro",     "Otro",         '<i class="bi bi-x"></i>',         OtroModel),
]
```

- El string es una **clase** `bg-<app>-<lo-que-sea>`; el archivo va en
  `static/image/screen/wide/<clase>.webp`.
- Podés apuntar a CUALQUIER imagen (reusar una de otra sección, un nombre propio…).
- Si el archivo no existe todavía, la card cae al **fondo del padre** hasta que lo dejes.

**Orden de prioridad:** 5º elemento explícito → si no, `bg-<app>-<modelo-kebab>`
(por nombre de archivo) → si no, fondo del padre → si no, gris.

### Alternativa sin tocar código — por nombre de archivo

Si preferís no editar el `.py`, la imagen también se elige sola por **nombre de
archivo**: cada card busca `bg-<app>-<modelo-kebab>.webp`; si no existe, el fondo
del **padre** (`background_image` de esa home, p. ej. `bg-system-panel`); si tampoco, gris.

Hoy las cards de Sistema no tienen imagen propia → todas muestran la del padre
(`bg-system-panel`). Para darle a cada una **su** imagen, deja el `.webp` con este
nombre EXACTO (orientación `wide`, apaisada):

| Card | Archivo a crear |
|---|---|
| Mensajes de contacto | `static/image/screen/wide/bg-system-contact-message.webp` |
| Usuarios | `static/image/screen/wide/bg-users-custom-user.webp` |
| Tipos de creador | `static/image/screen/wide/bg-games-creator-type.webp` |
| Tipos de rol | `static/image/screen/wide/bg-catalogs-role-type.webp` |
| Tipos de canción | `static/image/screen/wide/bg-otaku-song-type.webp` |
| Tipos de medio otaku | `static/image/screen/wide/bg-catalogs-otaku-media-type.webp` |

Pasos: (1) copia el `.webp` con ese nombre en esa carpeta · (2) `collectstatic`
(o en dev basta recargar) · (3) sube `ASSET_VERSION`. La card lo toma sola, sin
editar plantillas ni vistas. (El nombre = `bg-<app>-<Modelo en kebab>`, p. ej.
`CreatorType` → `creator-type`. Para ver el nombre exacto de cualquier card:
`python manage.py shell` y mirar `Modelo._meta.app_label` + el nombre de la clase.)
