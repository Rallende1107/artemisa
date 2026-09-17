"""
Envío de correos por plantilla + registro. El flag de envío y el SMTP salen de
la CONFIG del panel (MailConfig), con fallback a settings/.env:
  - send_email = True  → envía (SMTP de la config si está, si no el backend de settings).
  - send_email = False → NO envía; deja el correo EN COLA (status=queued) para reenviar.
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import Context, Template
from django.utils.html import strip_tags

from .models import EmailMessage, EmailLog, EmailTemplate, MailConfig
from core.shared.models.choices import EmailMessageStatus, LogLevel


def _render(text, context):
    return Template(text or "").render(Context(context or {}))


def mail_enabled():
    """¿Se envían correos? Manda MailConfig; si no existe fila, cae a settings.SEND_EMAIL."""
    try:
        return MailConfig.load().send_email
    except Exception:
        return getattr(settings, "SEND_EMAIL", False)


def from_address():
    return (MailConfig.load().from_email or "").strip() or settings.DEFAULT_FROM_EMAIL


def connection():
    """Conexión SMTP desde la config del panel si hay host; si no, el backend de settings."""
    cfg = MailConfig.load()
    if cfg.smtp_host:
        return get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=cfg.smtp_host, port=cfg.smtp_port,
            username=cfg.smtp_user or None, password=cfg.smtp_password or None,
            use_tls=cfg.use_tls,
        )
    return get_connection()   # el de settings (consola en dev, SMTP si .env lo define)


def _deliver(subject, body_html, body_text, to):
    """Envía UN correo con la conexión configurada, dentro de la MAQUETA (apps/mailing/layout.py) y con la
    FIRMA de la config al pie. Lanza si falla."""
    from .layout import envolver, es_documento
    sig = (MailConfig.load().signature or "").strip()
    if body_html and not es_documento(body_html):
        body_html = envolver(body_html, settings.SITE_NAME, firma=sig, preheader=strip_tags(body_text or "")[:120])
    elif sig and body_html:
        body_html = f"{body_html}\n{sig}"
    if sig:
        body_text = f"{body_text}\n\n{strip_tags(sig)}"
    msg = EmailMultiAlternatives(subject, body_text, from_address(), [to], connection=connection())
    if body_html:
        msg.attach_alternative(body_html, "text/html")
    msg.send()


def log_mail(code, process, message, email=None):
    """Anota un HECHO en el log de correo (EmailLog). code = nivel (LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR…)."""
    from core.utils.importlog import log_to
    return log_to(EmailLog, code, process, message, email=email)


def send_templated(key, to, context=None, from_email=None):
    """Envía el correo de la plantilla `key` a `to` con `context`, guarda el EmailMessage y
    anota el hecho en el log. Devuelve el EmailMessage. Nunca lanza."""
    context = context or {}
    tpl = EmailTemplate.objects.filter(key=key, is_active=True).first()

    if not tpl:
        correo = EmailMessage.objects.create(
            to_email=to, status=EmailMessageStatus.SKIPPED, context=context,
            error=f"No hay plantilla activa con key='{key}'.",
        )
        log_mail(LogLevel.SUCCESS, "envío", f"correo #{correo.pk} a {to}: OMITIDO, no hay plantilla activa «{key}»", email=correo)
        return correo

    # Siempre renderizamos y guardamos (queda completo aunque no se envíe).
    subject = _render(tpl.subject, context).strip()
    body_html = _render(tpl.body_html, context)
    body_text = _render(tpl.body_text, context) if tpl.body_text else strip_tags(body_html)
    correo = EmailMessage(template=tpl, to_email=to, subject=subject, body=body_html, context=context)

    if not mail_enabled():
        # Master switch OFF: EN COLA (guardado) para reenviar al activar.
        correo.status = EmailMessageStatus.QUEUED
        correo.error = "Envío desactivado: en cola, pendiente de reenvío."
        correo.save()
        log_mail(LogLevel.INFO, "envío", f"correo #{correo.pk} a {to} («{tpl.key}»): EN COLA, envío desactivado", email=correo)
        return correo

    try:
        _deliver(subject, body_html, body_text, to)
        correo.status = EmailMessageStatus.SENT
        correo.save()
        log_mail(LogLevel.INFO, "envío", f"correo #{correo.pk} a {to} («{tpl.key}»): enviado", email=correo)
    except Exception as exc:  # noqa: BLE001
        correo.status = EmailMessageStatus.ERROR
        correo.error = str(exc)
        correo.save()
        log_mail(LogLevel.WARNING, "envío", f"correo #{correo.pk} a {to} («{tpl.key}»): FALLÓ — {exc}", email=correo)
    return correo


def avisar_respuesta(respuesta, enlace):
    """Correo «te respondimos» al autor de un mensaje de contacto — lo usan
    la vista de alta de respuestas Y el responder inline del detalle."""
    from django.conf import settings
    m = respuesta.message
    if not (respuesta.is_active and m.email):
        return None
    return send_templated("contacto_respuesta", m.email, {
        "nombre": m.name,
        "asunto": m.subject or "(sin asunto)",
        "respuesta": respuesta.body,
        "sitio": settings.SITE_NAME,
        "enlace": enlace,
    })
