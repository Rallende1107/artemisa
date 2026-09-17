"""Admin de users: CustomUser con UserAdmin + Import/Export; el resto (UserLog…)
se registra genérico con import-export vía register_all."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin

from apps.users.models import CustomUser
from core.shared.admin import register_all


@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    list_display = ("username", "email", "role", "is_staff", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    readonly_fields = ("slug", "created_at", "updated_at")
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil Artemisa", {"fields": ("phone", "birth_date", "avatar", "slug", "created_at", "updated_at")}),
    )

    @admin.display(description="Rol")
    def role(self, obj):
        return obj.role


# UserLog y cualquier otro modelo de la app (CustomUser ya registrado → se salta)
register_all("users")
