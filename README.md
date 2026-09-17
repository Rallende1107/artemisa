# Artemisa — Vistas (panel de gestión)

Guía práctica de la **capa de vistas** del panel `/panel/`: cómo se arman las
homes de sección, los formularios por entidad, el sidebar y los fondos. Para el
detalle de cada tema hay docs enlazados al final.

Todo el motor base vive en `core/shared/views.py`; cada app declara lo suyo en
el paquete `apps/<app>/views/` + `urls/` por rol: `panel.py`, `data.py`, `public.py` (explícito, estilo Hades: sin fábricas).

---

> **MIGRACIONES: NO se versionan y NO se generan desde el venv.** El proyecto nace limpio: `apps/*/migrations/` solo
> lleva `__init__.py` (el `.gitignore` excluye `0*.py`). Mientras el esquema cambie, las migraciones se crean en Docker:
> `clear_migrations` las borra y `makemigrations` las genera (un comando, una acción). Arranque desde cero:
>
> ```
> docker compose down -v                                       # base vacía
> rmdir /s /q media & mkdir media                              # imágenes de cero
> docker compose up -d                                         # stack arriba (el web NO migra al arrancar)
> docker compose exec web python manage.py clear_migrations    # desarrollo: borra las 0*.py
> docker compose exec web python manage.py makemigrations      # desarrollo: genera las 0001
> docker compose exec web python manage.py initial_setup       # migra, seed de cada app y pide el superusuario
> docker compose restart worker beat                           # worker y beat con el código nuevo
> ```
>
> `initial_setup` es el único comando principal: migra, corre `seed_<app>` de cada app y al final pide el superusuario
> (`--dev` crea admin/admin y rallende). Detalle y comandos de desarrollo en [docs/comandos.md](docs/comandos.md) §3 a §6.

## 1. Home de sección — las CARDS

Cada sección (Música, Catálogos, Otaku…) tiene una `BaseAdminHomeView` que muestra
una tarjeta por entidad. Se declaran en `apps/<app>/views/v1_home.py`:

```python
class CatalogsAdminHomeView(BaseAdminHomeView):
    title = "Catálogos"
    active_entity = "catalogs-home"
    background_image = "bg-catalogs-home"     # fondo de la página + fallback de las cards
    groups = [
        (_("Referencias"), [
            #  1: entity      2: label                    3: icono (HTML)                    4: fondo (clase bg-…)
            ("contacto",  _("Mensajes de contacto"), '<i class="bi bi-envelope"></i>',  "bg-mailing-contact-message"),
            ("usuario",   _("Usuarios"),             '<i class="bi bi-people"></i>',     "bg-users-user"),
            ("tipo-rol",  _("Tipos de rol"),         '<i class="bi bi-diagram-3"></i>',  "bg-catalogs-role-type"),
        ]),
    ]
```

**Qué es cada campo de la tupla:**

| # | Campo | Qué es | Para qué |
|---|---|---|---|
| 1 | `entity` (slug) | identificador | arma el enlace `panel:<entity>_list` (a dónde va la card); una ruta completa `panel:x` o `x-home` también valen |
| 2 | `label` | texto con `_()` | el título visible de la card (y su enlace en el sidebar, que es espejo del home) |
| 3 | `icono` (HTML) | `<i class="bi ..."></i>` | el icono Bootstrap de la card |
| 4 | `fondo` | clase `bg-<app>-<x>` | la imagen de fondo de esa card |

Las cards NO llevan modelo ni conteo: un home solo navega, y un `COUNT(*)` por card sobre tablas de
millones de filas sería lo más caro de la página. El número exacto se ve en la lista (DataTable).

**Fondo de cada card**: el 4º elemento; si su `.webp` no existe, cae al fondo del **padre**
(`background_image` de la home), así se nota el error.

La imagen va en `static/image/screen/wide/<clase>.webp`. Se
muestra con blur + velo oscuro; se ajusta en `static/css/components/card.css`
(clase `.card--bg`). Ver [transparencias.md](docs/transparencias.md).

---

## 2. Formularios por entidad (crear/editar)

Patrón Poseidon: el **CUADRO** maestro (card, csrf, botones) vive una sola vez en
`templates/admin_panel/form.html`. Cada vista de alta/edición DECLARA qué HTML de campos
le aplica, y el cuadro lo incluye (`{% include form_template %}`); así crear y editar
pueden usar parciales distintos y cambiarlos cuando quieras:

```python
class CountryCreateView(BaseCountry, BaseCreate):
    form_class = f.CountryForm
    form_template = "catalogs/form/country.html"   # parcial de campos (solo los campos)
    list_url = "panel:country_list"                 # breadcrumb
    success_url = "panel:country_list"              # a dónde ir al guardar
    cancel_url = "panel:country_list"               # a dónde va «Cancelar»
    success_message = _("País «%(obj)s» creado.")
    title = _("Crear país")
```

Todo va DIRECTO en la vista, nada se calcula (rutas y título incluidos): `BaseCreate` y
`BaseUpdate` son dos bases separadas y autocontenidas; la sección (breadcrumb) y el fondo
vienen de la `_Entidad` y de la base de su app (`BaseCatalogs`).

```django
{# apps/catalogs/templates/catalogs/form/country.html — solo los campos, sin extends #}
<div class="form-row">                  {# fila → columnas (row > col) #}
  <div class="field"> … {{ form.name }} … </div>
  <div class="field"> … {{ form.name_esp }} … </div>
</div>
```

- **`.form-row`** reparte columnas iguales según cuántos `.field` metas (2 campos → 2
  columnas, 1 → fila completa). También `col-full` / `col-2` por campo.
- Los **booleanos** (is_active, +18…) se auto-agrupan abajo; no van en el bloque.
- Si una entidad no declara `form_template`, se usa el **loop genérico** del cuadro.
- Sincronizar / crear las que falten: **`python manage.py sync_forms`** (crea las
  que faltan y avisa desfases campo↔HTML). Ver [comandos.md](docs/comandos.md).

---

## 3. Sidebar — modo RAIL (solo-iconos)

En desktop el sidebar arranca colapsado a un **rail de iconos**. Aplica a los 3
sidebars (gestión, público, importación); móvil (≤900px) usa drawer aparte.

- **Hover** en una sección con hijos → **flyout** con sus opciones navegables
  (no ensancha el sidebar). Ítems sueltos → tooltip nativo.
- **Toggle** (☰ arriba) → **fija** el sidebar abierto (recordado en `localStorage`).
- La **sección activa** se ilumina en cian (el árbol de la entidad actual queda
  `[open]` y se pinta su icono).

Piezas: `static/css/components/sidebar.css` (rail + flyout), `static/js/sidebar-rail.js`
(flyout), `static/js/admin.js` + `public.js` (toggle). Token `--rail-w` en `00-tokens.css`.

---

## 4. Reglas del motor (recordatorio)

- **Explícito, sin fábricas**: cada vista y URL se escribe a mano y se puede grepear.
- **Validación por capas**: Form = 1ª barrera · Vista = red · Modelo = último cerrojo.
- **Relaciones FK/M2M** por AJAX (Select2 remoto) — no vuelcan la tabla.
- **Cache-busting**: subir `ASSET_VERSION` en `core/settings.py` tras tocar CSS/JS
  (el server corre con `--noreload`, hay que reiniciarlo).

---

## Docs (carpeta `docs/`)

- [usos_vistas.md](docs/usos_vistas.md) — **glosario** de la capa de vistas (qué es qué)
- [comandos.md](docs/comandos.md) — todos los comandos (tests, seeds, sync_forms, estáticos…)
- [fondos.md](docs/fondos.md) — fondos por vista: cómo crear uno + inventario (qué hay, qué falta, dónde se ve)
- [transparencias.md](docs/transparencias.md) — opacidad de fondos/paneles + blur de las cards
- [LEEME.md](docs/LEEME.md) — convención de CSS por componentes
