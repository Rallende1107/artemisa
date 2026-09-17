"""Piezas compartidas de la IMPORTACIÓN (MAL / Deezer / VNDB). La vista base es `BaseImport`, y vive con las
demás Base en core/shared/views/base.py; aquí quedan las piezas que usan esa vista, sus formularios y sus listas:

  · `run_task` — patrón Hades: con CELERY_ENABLED (Docker) va al worker; si no, EAGER (corre en el proceso de
    Django, sin tocar el broker). Los tests lo sustituyen aquí: `core.shared.views.imports.run_task`.
  · `LanzaTareaMixin` — lo que un FORMULARIO de importación necesita para lanzar su tarea y contarlo.
  · `tarea_en_curso` / `anotar_usuario` — guardas y autoría sobre system.TaskRun.
  · `DataBulkMixin` — acciones masivas de las listas de datos crudos.
  · `ProcesarPendientesView` — el POST «Procesar pendientes» de una fuente.
  · `ProcesarLoteForm` — el formulario de las vistas «Procesar» por tabla: N pendientes o todos.

Cada app declara sus lanzadores en `views/v8_import.py`: uno por tipo y formulario."""
from django import forms
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from core.shared.views.base import BasePage
from core.shared.models.choices import TaskRunStatus


def run_task(task, *args, **kwargs):
    """Lanza una tarea. Devuelve (backgrounded: bool, result)."""
    result = task.delay(*args, **kwargs)
    return bool(settings.CELERY_ENABLED), result


def tarea_en_curso(task, con_args=""):
    """Nombre del estado («en cola» / «corriendo») si ya hay una TaskRun de esa tarea sin terminar; "" si no.
    `con_args`: solo cuenta la que lleve ese texto en sus argumentos (una descarga por TABLA, varias tablas a la vez)."""
    try:
        from apps.system.models import TaskRun
        qs = TaskRun.objects.filter(name=task.name, status__in=(TaskRunStatus.QUEUED, TaskRunStatus.RUNNING))
        if con_args:
            qs = qs.filter(args__contains=con_args)
        fila = qs.order_by("-queued_at").first()
    except Exception:  # noqa: BLE001
        return ""
    if fila is None:
        return ""
    return "en cola" if fila.status == TaskRunStatus.QUEUED else "corriendo"


def anotar_usuario(result, user):
    """Deja en system.TaskRun quién lanzó la tarea (la fila la crean las señales de Celery)."""
    try:
        from apps.system.models import TaskRun
        TaskRun.objects.filter(task_id=getattr(result, "id", None)).update(user=user if user.is_authenticated else None)
    except Exception:  # noqa: BLE001 — nunca romper el lanzador por el registro
        pass


MAX_IDS_POR_LOTE = 5000


def _siguiente_id(modelo, campo):
    """El id siguiente al mayor ya descargado (o 1 si la tabla está vacía): el `inicio` que sugiere el rango."""
    mayor = modelo.objects.order_by(f"-{campo}").values_list(campo, flat=True).first()
    return (mayor or 0) + 1


class DataBulkMixin:
    """Acción masiva a la medida de una tabla DATA (staging de importación). La lista declara:
      bulk_process_task — post-proceso de la fuente («Reprocesar ahora» = marcar sin procesar + encolarlo);
      bulk_kind + bulk_ids_task — (opcional) tipo e importador por lista de ids («Volver a descargar»).
    Se apoya en la vista genérica panel:masivo, que llama a `bulk_run` con las filas marcadas."""
    bulk_process_task = None
    bulk_kind = ""
    bulk_ids_task = None
    bulk_delete = True


    def _bulk_actions(self):
        acciones = [("set:data_processed:0", _("Marcar para reprocesar")),
                    ("set:data_processed:1", _("Marcar como procesadas")),
                    ("reprocesar", _("Reprocesar ahora"))]
        if self.bulk_kind and self.bulk_ids_task:
            acciones.append(("refetch", _("Re-obtener datos (fetch + process)")))
        acciones.append(("eliminar", _("Eliminar seleccionadas")))
        return acciones

    @classmethod
    def _id_externo(cls, model):
        for campo in ("mal_id", "deezer_id", "vndb_id", "f95_id"):
            if any(f.name == campo for f in model._meta.get_fields()):
                return campo
        return ""

    @classmethod
    def bulk_run(cls, request, accion, qs):
        """True si atendió la acción; False para que siga la vista genérica (set:…, eliminar)."""
        if accion == "reprocesar" and cls.bulk_process_task:
            n = qs.update(data_processed=False)
            en_curso = tarea_en_curso(cls.bulk_process_task)
            if en_curso:
                messages.info(request, f"{n} registro(s) marcados para reprocesar; los toma el procesamiento que ya está {en_curso}.")
                return True
            bg, result = run_task(cls.bulk_process_task)
            anotar_usuario(result, request.user)
            messages.success(request, f"{n} registro(s) marcados para reprocesar; post-proceso {'encolado' if bg else 'ejecutado'}.")
            return True
        if accion == "refetch" and cls.bulk_kind and cls.bulk_ids_task:
            campo = cls._id_externo(qs.model)
            ids = sorted(set(qs.values_list(campo, flat=True))) if campo else []
            if not ids:
                messages.warning(request, "Las filas marcadas no tienen id externo.")
                return True
            bg, result = run_task(cls.bulk_ids_task, cls.bulk_kind, ids)
            anotar_usuario(result, request.user)
            messages.success(request, f"Descarga de {len(ids)} id(s) de {cls.bulk_kind} {'encolada' if bg else 'ejecutada'}.")
            return True
        return False


class LanzaTareaMixin:
    """Lo que un FORMULARIO de importación le dice a su lanzador. Dos métodos, nada más:

      · `tarea(vista)` → (task, args, kwargs) con la tarea que hay que ejecutar, o None si no hay que lanzar
        nada (el formulario ya habrá dicho por qué con un mensaje).
      · `resumen(vista)` → una línea para el aviso («Importar Juego #17»).

    Quién ejecuta y cómo (Celery o aquí mismo) NO es asunto del formulario: lo decide `BaseImport.form_valid`."""

    def tarea(self, vista):
        raise NotImplementedError(f"{type(self).__name__} debe declarar `tarea(vista)`.")

    def resumen(self, vista):
        return _("Importar %(que)s") % {"que": vista.label}


class ProcesarPendientesView(BasePage, TemplateView):
    """POST «Procesar pendientes» de una fuente (pie de los lanzadores y listas de datos): UNA tarea a la vez,
    y vuelve a la página que lo pulsó."""
    process_task = None
    home_url = ""               # a dónde ir si no hay referer del panel

    def get(self, request, *args, **kwargs):
        return redirect(reverse(self.home_url))

    def post(self, request, *args, **kwargs):
        en_curso = tarea_en_curso(self.process_task)
        if en_curso:
            messages.warning(request, f"Ya hay un procesamiento de pendientes {en_curso}; espera a que termine (Tareas → en curso).")
        else:
            bg, result = run_task(self.process_task)
            anotar_usuario(result, request.user)
            if bg:
                messages.info(request, "Procesamiento de pendientes encolado en background.")
            else:
                messages.success(request, f"Procesados {getattr(result, 'result', 0)} registros pendientes.")
        # A dónde dejar al usuario: lo que pida el botón (`destino`, normalmente la lista REAL que se acaba de
        # llenar), si no la página desde la que se pulsó, y si no la home de la sección.
        for candidato in (request.POST.get("destino"), request.META.get("HTTP_REFERER")):
            if candidato and url_has_allowed_host_and_scheme(candidato, allowed_hosts={request.get_host()}) and "/panel/" in candidato:
                return redirect(candidato)
        return redirect(reverse(self.home_url))


class ProcesarLoteForm(LanzaTareaMixin, forms.Form):
    """«Procesar» UNA tabla de datos crudos: N pendientes o todos, en background, por lotes y cancelable. La subclase fija
    `TIPO` (lo que recibe la tarea), `success_url` (la lista de datos) y `PENDIENTES` (ruta de la función que cuenta los
    pendientes de un tipo). La vista declara `task_procesar` (tarea con firma `(tipo, cantidad)`)."""
    slug = 'procesar'
    titulo = _('Procesar pendientes')
    boton = _('Procesar')
    success_label = _('fichas reales')
    TIPO = ''
    success_url = ''
    PENDIENTES = ''
    EN_CURSO_POR = ''          # "" = una a la vez por tarea; la descarga pone su tabla (una por tabla, varias a la vez)
    AVISO_HAY = _('Hay <b>{}</b> por procesar.')
    AVISO_NADA = _('No hay nada por procesar: carga un dump o marca filas para reprocesar.')

    cantidad = forms.IntegerField(
        label=_('Cuántos'),
        help_text=_('Pendientes a procesar en esta tanda, del id más bajo al más alto.'),
        required=False, min_value=1, max_value=10_000_000, initial=1000,
        widget=forms.NumberInput(attrs={'placeholder': '1000', 'aria-label': _('Cuántos'), 'autocomplete': 'off',
                                        'inputmode': 'numeric', 'step': 1, 'min': 1}),
        error_messages={'invalid': _('Tiene que ser un número entero.'), 'min_value': _('Al menos uno.')},
    )
    todo = forms.BooleanField(
        label=_('Todos los pendientes'), required=False, initial=False,
        help_text=_('Sigue lote a lote hasta que no quede ninguno. Cancelable desde Tareas.'),
        widget=forms.CheckboxInput(attrs={'aria-label': _('Todos los pendientes'), 'data-bloquea': 'cantidad'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils.module_loading import import_string
        self.pendientes = import_string(self.PENDIENTES)(self.TIPO)
        from django.utils.html import format_html
        n = f'{self.pendientes:,}'.replace(',', '.')
        self.aviso = format_html(self.AVISO_HAY, n) if self.pendientes else self.AVISO_NADA

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('todo'):
            cleaned['cantidad'] = 0
            self.errors.pop('cantidad', None)
        elif not cleaned.get('cantidad'):
            self.add_error('cantidad', _('Escribe cuántos o marca «Todos los pendientes».'))
        return cleaned

    def tarea(self, vista):
        """Un procesado de la fuente a la vez: dos a la vez se pisarían las mismas filas."""
        en_curso = tarea_en_curso(vista.task_procesar, self.EN_CURSO_POR)
        if en_curso:
            messages.warning(vista.request, _('Ya hay uno igual %(estado)s (%(fuente)s). Espera a que termine o '
                                              'cancélalo desde Tareas.') % {'fuente': vista.source_label, 'estado': en_curso})
            return None
        return vista.task_procesar, (self.TIPO, self.cleaned_data['cantidad']), {}

    def resumen(self, vista):
        cantidad = self.cleaned_data['cantidad']
        return _('Procesar %(que)s (%(fuente)s): %(cuantos)s') % {
            'que': vista.label_plural, 'fuente': vista.source_label,
            'cuantos': _('todos los pendientes') if not cantidad else cantidad}


class DescargarImagenesForm(ProcesarLoteForm):
    """«Descargar imágenes» de UNA tabla: N pendientes o todas. `TIPO` = «app.Modelo» de la tabla. Una descarga en curso
    por tabla: compañías y personas pueden correr a la vez."""
    titulo = _('Descargar pendientes')
    boton = _('Descargar')
    success_label = _('imágenes en disco')
    PENDIENTES = 'core.shared.tasks.images.pendientes_de'
    AVISO_HAY = _('Hay <b>{}</b> imágenes por descargar.')
    AVISO_NADA = _('No hay imágenes por descargar.')

    def __init__(self, *args, **kwargs):
        self.EN_CURSO_POR = repr(self.TIPO)          # así queda en TaskRun.args: 'otaku.AnimeImage'
        super().__init__(*args, **kwargs)
        from django.utils.html import format_html
        from core.shared.tasks.images import muertas_de
        muertas = muertas_de(self.TIPO)
        if muertas:
            self.aviso = format_html('{} · {}', self.aviso, format_html(_('<b>{}</b> con URL muerta (fuera de la cola)'),
                                                                         f'{muertas:,}'.replace(',', '.')))
        self.fields['cantidad'].help_text = _('Imágenes a descargar en esta tanda, de la más antigua a la más nueva. Un 404 da '
                                              'la URL por muerta al primer intento; un timeout o un error del servidor, al tercero.')
        self.fields['todo'].label = _('Todas las pendientes')


class ReintentarMuertasForm(LanzaTareaMixin, forms.Form):
    """«Reintentar muertas» de UNA tabla: las devuelve a la cola (intentos a cero). Es un UPDATE: no encola nada."""
    slug = 'reintentar'
    titulo = _('URLs muertas')
    boton = _('Reintentar muertas')
    success_label = _('vuelven a la cola')
    TIPO = ''
    success_url = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils.html import format_html
        from core.shared.tasks.images import muertas_de
        self.muertas = muertas_de(self.TIPO)
        self.aviso = (format_html(_('<b>{}</b> imágenes con la URL dada por muerta. Reintentar las devuelve a la cola.'),
                                  f'{self.muertas:,}'.replace(',', '.')) if self.muertas else _('No hay URLs muertas.'))

    def tarea(self, vista):
        from core.shared.tasks.images import reintentar_muertas
        n = reintentar_muertas(self.TIPO)
        messages.success(vista.request, _('%(n)s imágenes vuelven a la cola de descarga.') % {'n': n})
        return None

    def resumen(self, vista):
        return _('Reintentar URLs muertas')
