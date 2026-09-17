"""mailing · acciones POST y páginas «a mano», de gestión y públicas."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from apps.mailing.models import EmailMessage, MailConfig
from apps.mailing.services import log_mail
from core.mixin.access import StaffRequiredMixin
from core.shared.models.choices import EmailMessageStatus


# ==============================================================================
# Gestión
# ==============================================================================

class EmailResendView(StaffRequiredMixin, View):
    """Reenvía un correo guardado (POST). Vuelve a donde se pulsó con un aviso."""
    def post(self, request, pk):
        log = get_object_or_404(EmailMessage, pk=pk)
        log.resend(actor=request.user)
        if log.status == EmailMessageStatus.SENT:
            messages.success(request, f"Correo reenviado a {log.to_email}.")
        else:
            messages.error(request, f"No se pudo reenviar: {log.error or 'error desconocido'}")
        # Vuelve a donde se pulsó (la lista filtrada o el detalle); si no, al detalle.
        return redirect(request.META.get("HTTP_REFERER") or reverse("panel:email-message_detail", args=[pk]))


class EmailResendPendingView(StaffRequiredMixin, View):
    """Reenvía TODA la cola (en cola + error) de un clic — el 'encolador'."""
    def post(self, request):
        pend = list(EmailMessage.objects.filter(status__in=EmailMessage.PENDING))
        ok = err = 0
        for log in pend:
            log.resend(actor=request.user)
            ok += 1 if log.status == EmailMessageStatus.SENT else 0
            err += 0 if log.status == EmailMessageStatus.SENT else 1
        if pend:
            log_mail(30 if err else 20, "reenvío masivo",
                     f"{request.user} reenvió la cola: {ok} enviado(s), {err} fallido(s) de {len(pend)}")
        if ok:
            messages.success(request, f"{ok} correo(s) reenviado(s).")
        if err:
            messages.error(request, f"{err} correo(s) fallaron (revisa la config SMTP).")
        if not pend:
            messages.info(request, "No hay correos pendientes en la cola.")
        return redirect(request.POST.get("next") or reverse("panel:mailing-home"))


class MailToggleView(StaffRequiredMixin, View):
    """Enciende/apaga el envío de correos (master switch) desde el panel.
    El SMTP se configura en el .env; aquí solo el on/off."""
    def post(self, request):
        cfg = MailConfig.load()
        cfg.send_email = not cfg.send_email
        cfg.save(update_fields=["send_email", "updated_at"])
        estado = "ACTIVADO" if cfg.send_email else "DESACTIVADO"
        log_mail(20 if cfg.send_email else 40, "interruptor", f"envío de correos {estado} por {request.user}")
        messages.success(request, f"Envío de correos {estado}.")
        return redirect(request.POST.get("next") or reverse("panel:mailing-home"))
