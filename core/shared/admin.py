"""
Admin de Artemisa al estilo Poseidon, pero GENERADO automáticamente.

- Import/Export por tabla (django-import-export).
- ActivableMixin: acciones "Activar/Desactivar" en lote (modelos con is_active).
- ProcesedMixin: "Marcar procesado/no procesado" (modelos Data* con data_processed).
- Admins RICOS auto: list_display, list_filter, search_fields, readonly (slug/fechas),
  ordering — deducidos de los campos de cada modelo.

Cada app llama a `register_all("<app_label>")` en su admin.py. Los ya registrados
(p. ej. CustomUser con su UserAdmin) se respetan.
"""
from django.contrib import admin, messages
from django.apps import apps as django_apps
from django.db import models as dj
from django.utils.translation import ngettext
from import_export.admin import ImportExportModelAdmin


# ───────────────────────── Mixins de acciones (estilo Poseidon) ─────────────────────────
class ActivableMixin:
    """Acciones activar/desactivar para modelos con `is_active`."""

    @admin.action(description="Activar los seleccionados")
    def activar(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, ngettext("Se activó %d elemento.", "Se activaron %d elementos.", n) % n, messages.SUCCESS)

    @admin.action(description="Desactivar los seleccionados")
    def desactivar(self, request, queryset):
        n = queryset.update(is_active=False)
        self.message_user(request, ngettext("Se desactivó %d elemento.", "Se desactivaron %d elementos.", n) % n, messages.SUCCESS)


class ProcesedMixin:
    """Acciones para modelos Data* con `data_processed`."""

    @admin.action(description="Marcar como procesado")
    def marcar_procesado(self, request, queryset):
        n = queryset.update(data_processed=True)
        self.message_user(request, f"{n} marcado(s) como procesado.", messages.SUCCESS)

    @admin.action(description="Marcar como NO procesado")
    def marcar_no_procesado(self, request, queryset):
        n = queryset.update(data_processed=False)
        self.message_user(request, f"{n} marcado(s) como no procesado.", messages.SUCCESS)


# ───────────────────────── Deducción de la config del admin ─────────────────────────
# Prioridad de columnas para la lista (se toman las que existan, en este orden).
_DISPLAY = [
    "name", "title", "full_name", "username", "to_email", "key", "subject", "name_esp",
    "mal_id", "status", "level", "process", "album_type", "artist",
    "initial", "slug", "is_active", "data_processed", "created_at", "timestamp",
]
_SEARCH = ["name", "name_esp", "title", "slug", "key", "email", "username", "full_name",
           "subject", "to_email", "code", "acronym", "message", "process", "url"]
_READONLY = ["slug", "initial", "created_at", "updated_at", "timestamp"]


def _build_attrs(model):
    fields = {f.name: f for f in model._meta.fields}   # concretos (sin M2M)
    names = set(fields)

    list_display = [n for n in _DISPLAY if n in names][:6] or [f.name for f in model._meta.fields[:4]]

    search_fields = [n for n in _SEARCH if n in names]

    list_filter = []
    if "is_active" in names:
        list_filter.append("is_active")
    for f in model._meta.fields:
        if isinstance(f, dj.BooleanField) and f.name not in list_filter:
            list_filter.append(f.name)
    fks = [f.name for f in model._meta.fields if f.is_relation]
    list_filter += [n for n in fks if n not in list_filter][:2]

    readonly = [n for n in _READONLY if n in names]

    if "name" in names:
        ordering = ("name",)
    elif "title" in names:
        ordering = ("title",)
    elif "timestamp" in names:
        ordering = ("-timestamp",)
    elif "created_at" in names:
        ordering = ("-created_at",)
    else:
        ordering = None

    attrs = {
        "list_display": list_display,
        "search_fields": search_fields,
        "list_filter": list_filter[:6],
        "readonly_fields": readonly,
        "save_on_top": True,
        "list_per_page": 50,
    }
    if ordering:
        attrs["ordering"] = ordering
    if "date_hierarchy" not in attrs and "created_at" in names:
        attrs["date_hierarchy"] = "created_at"
    return attrs, names


def register_all(app_label, exclude=(), base=ImportExportModelAdmin):
    """Registra todos los modelos de la app con admin rico + import/export."""
    for model in django_apps.get_app_config(app_label).get_models():
        if model in exclude or admin.site.is_registered(model):
            continue
        attrs, names = _build_attrs(model)
        mixins = ()
        if "is_active" in names:
            mixins += (ActivableMixin,)
            attrs["actions"] = ["activar", "desactivar"]
        if "data_processed" in names:
            mixins += (ProcesedMixin,)
            attrs["actions"] = attrs.get("actions", []) + ["marcar_procesado", "marcar_no_procesado"]
        admin_cls = type(f"{model.__name__}Admin", mixins + (base,), attrs)
        admin.site.register(model, admin_cls)
