"""MAQUETA de los correos (la misma para el envío y la vista previa del panel).

HTML «de correo»: tablas, estilos en línea y anchos fijos, que es lo único que respetan Gmail, Outlook y
compañía. Fondo gris claro, tarjeta centrada de 600 px: cabecera oscura con la marca en cian, cuerpo
blanco con texto oscuro (legible en cualquier cliente y en modo claro), pie gris con la firma configurada
en el panel. Las plantillas (EmailTemplate.body_html) guardan solo el CONTENIDO: título, párrafos, botón."""
from django.utils.html import escape


ACENTO = "#00c8e0"        # cian de la casa, un punto más oscuro para que contraste sobre blanco
OSCURO = "#0a0a0f"
TEXTO = "#1c1f2a"
MUTED = "#6b7080"
FONDO = "#eef0f5"


def envolver(contenido_html, sitio, firma="", preheader=""):
    """Documento HTML completo listo para enviar o para el iframe de la vista previa."""
    firma_html = (
        f'<tr><td style="padding:0 32px 26px;font-family:Arial,Helvetica,sans-serif;font-size:12px;'
        f'line-height:18px;color:{MUTED}">{firma}</td></tr>' if firma else ""
    )
    pre = f'<div style="display:none;max-height:0;overflow:hidden;opacity:0">{escape(preheader)}</div>' if preheader else ""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{escape(sitio)}</title></head>
<body style="margin:0;padding:0;background:{FONDO}">
{pre}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{FONDO};padding:32px 12px">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;overflow:hidden;box-shadow:0 8px 30px rgba(10,10,15,.10)">
  <tr><td style="background:{OSCURO};padding:22px 32px;font-family:Arial,Helvetica,sans-serif">
    <span style="font-size:20px;font-weight:bold;letter-spacing:.5px;color:{ACENTO}">{escape(sitio)}</span>
    <span style="font-size:12px;color:#8d93a5;margin-left:12px">anime · manga · música · películas · series · juegos</span>
  </td></tr>
  <tr><td style="padding:32px 32px 8px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:24px;color:{TEXTO}">
{contenido_html}
  </td></tr>
  {firma_html}
  <tr><td style="background:#f6f7fa;padding:16px 32px;font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:16px;color:{MUTED};border-top:1px solid #e3e6ee">
    Este correo lo envía {escape(sitio)} por una acción en tu cuenta. Si no fuiste tú, ignóralo.
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


def es_documento(html):
    """True si la plantilla ya trae su propio <html> (no se envuelve dos veces)."""
    return "<html" in (html or "").lower()
