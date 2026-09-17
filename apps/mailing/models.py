"""
App mailing — correos configurables + registro de enviados.

- EmailTemplate: el ASUNTO y el CUERPO de cada correo, editables desde el panel.
  Usan variables de plantilla Django: `{{ usuario }}`, `{{ enlace }}`, etc.
- EmailMessage: CADA correo (destinatario, asunto/cuerpo finales, estado: enviado / en cola /
  error / omitido, y el error). Es la bandeja: el DETALLE de cada mensaje vive aquí.
- EmailLog: el LOG de la app (ModelBaseLog): HECHOS con fecha — «correo #12 a x@y: enviado»,
  «falló: SMTP timeout», «reenviado a mano por admin», «envío ACTIVADO por admin»…
  Cada hecho puede apuntar al correo al que se refiere.

Envío: `apps.mailing.services.send_templated(key, to, context)` — busca la
plantilla activa, renderiza asunto+cuerpo con el context, envía, guarda el EmailMessage y
anota el hecho en EmailLog (`services.log_mail`).
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseLog
from core.shared.models.choices import ContactMessageStatus, EmailMessageStatus, LogLevel


class ContactMessage(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Mensaje enviado desde el formulario público de contacto.
    Movido desde apps/system (el contacto es correo); historial de migraciones
    reiniciado, así que la tabla es `mailing_contactmessage` desde la 0001."""

    name = models.CharField(verbose_name="nombre", max_length=120)
    email = models.EmailField(verbose_name="correo")
    subject = models.CharField(verbose_name="asunto", max_length=200, blank=True)
    message = models.TextField(verbose_name="mensaje")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="contact_messages", verbose_name="usuario")
    status = models.CharField(verbose_name="estado", max_length=12, choices=ContactMessageStatus.choices, default=ContactMessageStatus.NEW)
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "mensaje de contacto"
        verbose_name_plural = "mensajes de contacto"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} · {self.subject or '(sin asunto)'}"


class ContactReply(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """RESPUESTA del staff a un mensaje de contacto. El usuario registrado la
    ve en «Mis mensajes» (su hilo con el sitio)."""

    message = models.ForeignKey("ContactMessage", on_delete=models.CASCADE,
                                related_name="replies", verbose_name="mensaje")
    body = models.TextField(verbose_name="respuesta")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="contact_replies", verbose_name="autor")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        verbose_name = "respuesta de contacto"
        verbose_name_plural = "respuestas de contacto"
        ordering = ["created_at"]

    def __str__(self):
        return f"Re: {self.message}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Responder marca el mensaje como REPLIED (estado de gestión).
        if self.is_active and self.message.status != ContactMessageStatus.REPLIED:
            self.message.status = ContactMessageStatus.REPLIED
            self.message.save(update_fields=["status", "updated_at"])


class EmailMessage(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Un correo: lo que se envió (o se intentó), con su estado. La bandeja."""
    # Estados que se pueden REENVIAR (la «cola» / pendientes).
    PENDING = (EmailMessageStatus.QUEUED, EmailMessageStatus.ERROR)
    template = models.ForeignKey(
        "EmailTemplate", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="emails", verbose_name="plantilla")
    to_email = models.CharField(verbose_name="destinatario", max_length=320)
    subject = models.CharField(verbose_name="asunto", max_length=255, blank=True)
    body = models.TextField(verbose_name="cuerpo enviado", blank=True)
    context = models.JSONField(verbose_name="variables", null=True, blank=True)   # para re-render al reenviar
    status = models.CharField(verbose_name="estado", max_length=10, choices=EmailMessageStatus.choices, default=EmailMessageStatus.SENT)
    error = models.TextField(verbose_name="error", blank=True)
    created_at = models.DateTimeField(verbose_name="fecha", auto_now_add=True)

    class Meta:
        verbose_name = "correo"
        verbose_name_plural = "correos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.to_email} · {self.subject}"

    def resend(self, actor=None):
        """Reenvía ESTE correo (en cola / error / omitido). Acción manual → envía SIEMPRE
        (ignora el flag). Si la plantilla sigue, re-renderiza con el context guardado
        (toma ediciones recientes); si no, usa el cuerpo guardado. Usa el SMTP/remitente
        de la config del panel. Actualiza su estado y anota el hecho en EmailLog."""
        from django.template import Context, Template
        from django.utils.html import strip_tags
        from apps.mailing.services import _deliver, log_mail

        subject, body_html = self.subject, self.body
        if self.template and self.context is not None:
            ctx = Context(self.context)
            subject = Template(self.template.subject).render(ctx).strip()
            body_html = Template(self.template.body_html).render(ctx)
        body_text = strip_tags(body_html)
        quien = f" por {actor}" if actor else ""
        try:
            _deliver(subject, body_html, body_text, self.to_email)
            self.subject, self.body = subject, body_html
            self.status, self.error = EmailMessageStatus.SENT, ""
            log_mail(LogLevel.INFO, "reenvío", f"correo #{self.pk} a {self.to_email}: reenviado{quien} → enviado", email=self)
        except Exception as exc:  # noqa: BLE001
            self.status, self.error = EmailMessageStatus.ERROR, str(exc)
            log_mail(LogLevel.WARNING, "reenvío", f"correo #{self.pk} a {self.to_email}: reenvío{quien} FALLÓ — {exc}", email=self)
        self.save(update_fields=["subject", "body", "status", "error"])
        return self


class EmailTemplate(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Plantilla de un correo: asunto + cuerpo editables (con variables {{ }})."""
    key = models.SlugField(
        verbose_name="clave", max_length=60, unique=True)
    name = models.CharField(verbose_name="nombre", max_length=120)
    subject = models.CharField(verbose_name="asunto", max_length=255)
    body_html = models.TextField(verbose_name="cuerpo (HTML)")
    body_text = models.TextField(
        verbose_name="cuerpo (texto plano)", blank=True)
    description = models.TextField(verbose_name="notas / variables disponibles", blank=True)
    is_active = models.BooleanField(verbose_name="activa", default=True)
    created_at = models.DateTimeField(verbose_name="creada", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizada", auto_now=True)

    class Meta:
        verbose_name = "plantilla de correo"
        verbose_name_plural = "plantillas de correo"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.key})"


class MailConfig(CoverMixin, DateDisplayMixin, BooleanDisplayMixin, models.Model):
    """Configuración de correo EDITABLE desde el panel (singleton, pk=1).
    Manda sobre el .env: el flag de envío, el remitente y el SMTP salen de aquí.
    Si un campo SMTP se deja vacío, se cae al backend/valor de settings (.env)."""
    send_email = models.BooleanField(
        verbose_name="enviar correos", default=False)
    signature = models.TextField(
        verbose_name="firma", blank=True)
    from_email = models.CharField(
        verbose_name="remitente (From)", max_length=320, blank=True)
    smtp_host = models.CharField(verbose_name="SMTP host", max_length=200, blank=True)
    smtp_port = models.PositiveIntegerField(verbose_name="SMTP puerto", default=587)
    smtp_user = models.CharField(verbose_name="SMTP usuario", max_length=320, blank=True)
    smtp_password = models.CharField(
        verbose_name="SMTP contraseña", max_length=255, blank=True)
    use_tls = models.BooleanField(verbose_name="usar TLS", default=True)
    updated_at = models.DateTimeField(verbose_name="actualizada", auto_now=True)

    class Meta:
        verbose_name = "configuración de correo"
        verbose_name_plural = "configuración de correo"

    def __str__(self):
        return "Configuración de correo"

    def save(self, *args, **kwargs):
        self.pk = 1                      # singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class EmailLog(ModelBaseLog):
    """LOG de la app de correo: un HECHO por fila (nivel, proceso, mensaje, momento),
    con enlace opcional al correo al que se refiere. Aquí NO va el detalle del
    mensaje (eso es `EmailMessage`): va qué pasó — envío ok, fallo, cola, reenvío,
    interruptor de envío encendido/apagado."""
    email = models.ForeignKey(
        "EmailMessage", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="log_entries", verbose_name="correo")

    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de correo"
        verbose_name_plural = "logs de correo"
