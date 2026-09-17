# Artemisa — estructura

> **Paneles del backend (Gestión, Importación, nuevos):** ver [paneles.md](paneles.md)
> — cómo se definen con la clase `Panel` y dónde editar el sidebar (la `nav` en Python).

    static/css/
      00-tokens.css          ← la única fuente de verdad: color, tipo, espaciado
      01-base.css            ← reset + capas de fondo
      02-layout.css          ← shell, main, divisores
      components/*.css       ← un archivo por componente
      99-utilities.css       ← utilidades y breakpoint global (siempre al final)

    static/js/               ← views.js (compartido) + admin/datatable/forms/
                               notify/public/sidebar-rail (por área)

    templates/
      base.html              ← el único que carga CSS y arma el esqueleto público
      partials/              ← _header, _sidebar, _public_footer, _seccion_nav, _lightbox
      admin_panel/           ← cuadro del panel: base_admin, list, form, detail, …
      panel/                 ← sidebar genérico data-driven (_sidebar, _nav_node) + home
      catalog/ · collection/ · pages/ · sections/ · registration/ · search/  ← por área

    core/context_processors.py   ← identidad del sitio (SITE_NAME…) + panel activo (sidebar)

    (el fondo por vista NO usa templatetag: cada vista declara `background_image`
     = la clase CSS; ver [fondos.md](fondos.md) y migración §5)

## Las reglas

1. **Ningún componente define colores literales.** Todo sale de
   `00-tokens.css` vía `var(--…)`. Buscar `#` en `components/` debería
   devolver cero resultados.

2. **El orden de carga es la cascada.** Tokens → base → layout → backgrounds →
   componentes → utilidades. No lo cambies: `99-utilities.css` gana a
   propósito.

3. **Cache-busting**: los `<link>` llevan `?v={{ ASSET_VERSION }}` — subir
   `ASSET_VERSION` en `core/settings.py` tras editar CSS/JS.

## Nota

`django-compressor` NO está instalado (idea descartada por ahora): los CSS se
sirven como archivos sueltos vía whitenoise, inspeccionables uno a uno.

## docs/ — qué queda vivo (limpieza 2026-09-12)

- `comandos.md` — todos los comandos (init, seeds, reinicio, descargas).
- `fondos.md` · `transparencias.md` — fondos por vista y su afinado visual.
- `paneles.md` · `usos_vistas.md` — el framework del panel y el glosario de vistas.
- `plan_vndb_barrido.md` — plan y próximos pasos de VNDB.
- `form-rows-pendientes.md` — checklist de formularios sin `.form-row`.
- `mockups/` — maquetas HTML de referencia.

Las reglas de modelos/formularios/vistas y el inventario viven en la raíz: `Modelos_Formularios_Vistas.md`.
