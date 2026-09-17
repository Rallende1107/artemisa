# Fondos que faltan — manual para crearlos

Generado el 2026-09-16 desde el código. Cada fondo es UNA imagen `.webp` en **cuatro tamaños**, con el mismo nombre en las cuatro carpetas de su app:

| Carpeta | Uso | Medida |
|---|---|---|
| `…/image/screen/wide/` | pantallas anchas (escritorio) | 1920 × 1080 (16:9) |
| `…/image/screen/landscape/` | tablet horizontal | 1440 × 1080 (4:3) |
| `…/image/screen/portrait/` | tablet vertical | 1080 × 1440 (3:4) |
| `…/image/screen/tall/` | móvil | 1080 × 1920 (9:16) |

`…` es `apps/<app>/static` en todas las apps.
Nombre del archivo = clase: no hay CSS ni código que tocar; mientras falte, la vista cae a su fondo de respaldo.

Total que faltan: **0** (de 196 que pide el código).
