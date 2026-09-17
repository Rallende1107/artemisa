"""Formularios de system: la tarea programada (beat). Las ejecuciones (TaskRun) no se editan."""
from celery import current_app
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.system.models import CloudFile, ImportCursor, ScheduledTask, TaskRun


class CloudFileForm(forms.ModelForm):
    """archivo en la nube: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = CloudFile
        fields = ['name', 'size']


class ImportCursorForm(forms.ModelForm):
    """Cursor de lote: fuente, tipo y el próximo id por el que seguirá el lote."""

    class Meta:
        model = ImportCursor
        fields = ["source", "type", "next_id", "batch_size"]

    source = forms.ChoiceField(label=_("Fuente"), choices=ImportCursor.FUENTES, required=True,
                               widget=forms.Select(attrs={"aria-label": _("Fuente"), "required": "required"}),
                               error_messages={"required": _("Elige la fuente."), "invalid_choice": _("Fuente no válida.")})
    type = forms.CharField(label=_("Tipo"), max_length=30, required=True,
                           help_text=_("El tipo del lanzador: artista, album, anime, manga, character, person, juego, creador…"),
                           widget=forms.TextInput(attrs={"placeholder": "artista", "aria-label": _("Tipo"), "required": "required"}),
                           error_messages={"required": _("Escribe el tipo."), "max_length": _("El tipo excede los 30 caracteres.")})
    next_id = forms.IntegerField(label=_("Próximo id"), required=True, min_value=1,
                                 help_text=_("Desde aquí parte el próximo lote. Súbelo para saltar, bájalo para repetir."),
                                 widget=forms.NumberInput(attrs={"placeholder": "1", "inputmode": "numeric", "step": 1, "min": 1,
                                                                 "required": "required", "aria-label": _("Próximo id")}),
                                 error_messages={"required": _("Escribe el próximo id."), "invalid": _("Tiene que ser un número entero."),
                                                 "min_value": _("Mínimo 1.")})

    batch_size = forms.IntegerField(label=_("Cantidad por lote"), required=True, min_value=1, initial=100,
                                    help_text=_("Cuántos ids trae cada lote (la tarea programada puede fijar otra)."),
                                    widget=forms.NumberInput(attrs={"placeholder": "100", "inputmode": "numeric", "step": 1, "min": 1,
                                                                    "required": "required", "aria-label": _("Cantidad por lote")}),
                                    error_messages={"required": _("Escribe la cantidad."), "invalid": _("Tiene que ser un número entero."),
                                                    "min_value": _("Mínimo 1.")})

    def clean_type(self):
        return (self.cleaned_data.get("type") or "").strip().lower()


def tareas_registradas():
    """Las tareas Celery del proyecto (las de las apps, sin las internas de Celery), para el select."""
    nombres = sorted(n for n in current_app.tasks.keys() if n.startswith("apps."))
    return [(n, n.replace("apps.", "").replace(".tasks.", " · ")) for n in nombres]


class ScheduledTaskForm(forms.ModelForm):
    """Tarea programada: qué tarea, cada cuántos minutos O a qué hora, y si está activa."""

    class Meta:
        model = ScheduledTask
        fields = ["name", "task", "args", "kwargs", "every_minutes", "at_time", "is_active"]

    task = forms.ChoiceField(
        label=_("Tarea"), required=True, choices=(),
        help_text=_("Qué tarea Celery se encola cuando toque."),
        widget=forms.Select(attrs={"aria-label": _("Tarea"), "required": "required"}),
        error_messages={"required": _("Elige la tarea."), "invalid_choice": _("Selecciona una tarea válida.")},
    )
    name = forms.CharField(
        label=_("Nombre"), max_length=120, required=True,
        widget=forms.TextInput(attrs={"placeholder": _("Procesar pendientes · Deezer"), "aria-label": _("Nombre"), "required": "required"}),
        error_messages={"required": _("Escribe un nombre."), "max_length": _("El nombre excede los 120 caracteres.")},
    )
    every_minutes = forms.IntegerField(
        label=_("Cada N minutos"), required=True, min_value=1, initial=30,
        help_text=_("Intervalo entre ejecuciones."),
        widget=forms.NumberInput(attrs={"placeholder": "30", "inputmode": "numeric", "step": 1, "min": 1, "required": "required",
                                        "aria-label": _("Cada N minutos")}),
        error_messages={"required": _("Escribe cada cuántos minutos."), "invalid": _("Tiene que ser un número entero."),
                        "min_value": _("Mínimo 1 minuto.")},
    )
    at_time = forms.TimeField(
        label=_("A esta hora"), required=False,
        help_text=_("Una vez al día a esta hora (zona horaria del sitio). Si está, manda sobre el intervalo."),
        widget=forms.TimeInput(attrs={"type": "time", "aria-label": _("A esta hora")}, format="%H:%M"),
        input_formats=["%H:%M", "%H:%M:%S"],
        error_messages={"invalid": _("Hora no válida (HH:MM).")},
    )
    is_active = forms.BooleanField(
        label=_("Activa"), required=False, initial=True,
        help_text=_("Si está activa, el despachador la encola cuando toque."),
        widget=forms.CheckboxInput(attrs={"aria-label": _("Activa")}),
    )

    args = forms.JSONField(
        label=_("Argumentos"), required=False, initial=list,
        help_text=_("Lista JSON de argumentos posicionales, p. ej. [\"artista\", 50]."),
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "[]", "aria-label": _("Argumentos")}),
        error_messages={"invalid": _("Tiene que ser JSON válido (una lista).")},
    )
    kwargs = forms.JSONField(
        label=_("Argumentos con nombre"), required=False, initial=dict,
        help_text=_("Objeto JSON, p. ej. {\"kind\": \"anime\"} o {\"cantidad\": 2000}. Los lotes de datos toman cantidad e id del cursor de lote."),
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "{}", "aria-label": _("Argumentos con nombre")}),
        error_messages={"invalid": _("Tiene que ser JSON válido (un objeto).")},
    )

    def clean_args(self):
        v = self.cleaned_data.get("args") or []
        if not isinstance(v, list):
            raise forms.ValidationError(_("Los argumentos posicionales van en una lista JSON."))
        return v

    def clean_kwargs(self):
        v = self.cleaned_data.get("kwargs") or {}
        if not isinstance(v, dict):
            raise forms.ValidationError(_("Los argumentos con nombre van en un objeto JSON."))
        return v

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].choices = tareas_registradas()


class TaskRunForm(forms.ModelForm):
    """tarea: formulario genérico (R0: un modelo, un formulario). Campos editables del modelo."""

    class Meta:
        model = TaskRun
        fields = ['task_id', 'name', 'args', 'status', 'cancel_requested', 'result', 'user', 'started_at', 'finished_at']
