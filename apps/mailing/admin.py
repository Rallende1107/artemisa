"""Admin de mailing: plantillas + registro con acción REENVIAR."""
from django.contrib import admin, messages
from import_export.admin import ImportExportModelAdmin

from .models import EmailMessage, EmailLog, EmailTemplate
from core.shared.models.choices import EmailMessageStatus


@admin.register(EmailTemplate)
class EmailTemplateAdmin(ImportExportModelAdmin):
    list_display = ("name", "key", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "key", "subject")
    save_on_top = True


@admin.register(EmailMessage)
class EmailAdmin(ImportExportModelAdmin):
    list_display = ("to_email", "subject", "status", "created_at")
    list_filter = ("status", "template")
    search_fields = ("to_email", "subject")
    readonly_fields = ("template", "to_email", "subject", "body", "context", "status", "error", "created_at")
    save_on_top = True

    @admin.action(description="Reenviar los correos seleccionados")
    def reenviar(self, request, queryset):
        ok = err = 0
        for log in queryset:
            log.resend()
            ok += log.status == EmailMessageStatus.SENT
            err += log.status == EmailMessageStatus.ERROR
        self.message_user(request, f"Reenviados: {ok} · con error: {err}",
                          messages.SUCCESS if ok else messages.WARNING)

    actions = ["reenviar"]


@admin.register(EmailLog)
class EmailLogAdmin(ImportExportModelAdmin):
    list_display = ("timestamp", "level", "process", "message", "email")
    list_filter = ("level", "process")
    search_fields = ("process", "message", "email__to_email")
    readonly_fields = ("timestamp",)
