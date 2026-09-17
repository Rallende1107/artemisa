"""
PROTOCOLO y CHROME del panel de administración propio (distinto del /admin/).

Las vistas de PÁGINA (lista/alta/edición/detalle/borrado) viven en
core/shared/views/base.py (Base*, estilo Poseidon). Aquí queda lo demás:

  · BaseDataView / BaseSelectView viven con las demás Base* en core/shared/views/base.py
  · AdminToggleView  → acciones rápidas de campos booleanos
  · StaffRequiredMixin / SuperuserRequiredMixin → core/mixin/access.py
  · resolve_background / _model_has_field → core/utils/views.py

Cada entidad se declara EXPLÍCITA en su app (apps/<app>/views/, paquete estilo
Poseidon) y sus rutas en urls/public.py y urls/panel.py: una path() por vista. Solo staff.
"""

from django.apps import apps as django_apps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import NoReverseMatch, resolve, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View

from core.mixin.access import StaffRequiredMixin
from core.utils.views import _model_has_field


NAMESPACE = "panel"

# ---- Acciones rápidas (toggles booleanos) declarativas ----------------------
# Reemplazo del ActionView monolítico de Hades (model_map de ~1500 líneas +
# códigos numéricos). Aquí cada campo booleano se declara UNA vez con sus
# etiquetas (hacer/deshacer, estado-hecho) y su nivel de permiso.
TOGGLE_STAFF = ("is_active", "explicit")          # cualquier staff
TOGGLE_SUPERUSER = ("is_staff", "is_superuser")   # solo superuser
TOGGLE_FIELDS = TOGGLE_STAFF + TOGGLE_SUPERUSER

# (etiqueta para ACTIVAR, etiqueta para DESACTIVAR, icono bi, ¿pedir confirmación?)
TOGGLE_META = {
    "is_active":    (_("Activar"), _("Desactivar"), "toggle-on", False),
    "explicit":     (_("Marcar +18"), _("Quitar +18"), "shield-exclamation", False),
    "is_staff":     (_("Hacer staff"), _("Quitar staff"), "person-gear", True),
    "is_superuser": (_("Hacer superusuario"), _("Quitar superusuario"), "shield-lock", True),
}
# Booleanos que la ACCIÓN MASIVA puede fijar además de los de TOGGLE_META (sin acción por fila):
# campo → (texto al poner True, texto al poner False)
BULK_FIELDS = {
    "data_processed": (_("marcados como procesados"), _("marcados para reprocesar")),
    "data_status": (_("marcados con fetch OK"), _("marcados con fetch pendiente")),
}
# Texto del mensaje de éxito (estado resultante): (al activar, al desactivar)
TOGGLE_DONE = {
    "is_active":    (_("activado"), _("desactivado")),
    "explicit":     (_("marcado como +18"), _("desmarcado de +18")),
    "is_staff":     (_("ahora es staff"), _("ya no es staff")),
    "is_superuser": (_("ahora es superusuario"), _("ya no es superusuario")),
}


class AdminImageActionView(StaffRequiredMixin, View):
    """Acción sobre UNA fila de imagen: `descargar` (baja su URL ahora) o `subir` (su archivo a la nube). Se registra por
    entidad con `model` vía as_view(), como AdminToggleView; vuelve a la página que la pidió."""
    model = None

    def post(self, request, pk, accion):
        from core.shared.tasks.images import descargar_fila, subir_fila
        obj = get_object_or_404(self.model, pk=pk)
        if accion == "descargar":
            if obj.download_dead:                       # «Reintentar descarga»: vuelve a tener sus intentos
                self.model.objects.filter(pk=pk).update(download_attempts=0, download_error="")
                obj.download_attempts = 0
            ok, detalle = descargar_fila(obj)
            (messages.success if ok else messages.error)(request, f"Descarga de «{obj}»: {detalle}")
        elif accion == "subir":
            ok, detalle = subir_fila(obj)
            (messages.success if ok else messages.error)(request, f"Subida de «{obj}»: {detalle}")
        else:
            return HttpResponseBadRequest("acción no permitida")
        volver = request.META.get("HTTP_REFERER") or ""
        if not url_has_allowed_host_and_scheme(volver, allowed_hosts={request.get_host()}):
            volver = reverse("panel:home")
        return redirect(volver)


class AdminToggleView(StaffRequiredMixin, View):
    """Acción rápida: invierte un campo booleano de un registro (is_active, explicit,
    is_staff, is_superuser). Sustituye al ActionView monolítico de Hades. Se registra
    por entidad con `model`/`entity`/`label`/`namespace` vía as_view()."""
    model = None
    entity = ""
    label = ""
    namespace = NAMESPACE

    def post(self, request, pk, field):
        if field not in TOGGLE_FIELDS or not _model_has_field(self.model, field):
            return HttpResponseBadRequest("campo no permitido")
        # Gestionar usuarios (cualquier toggle sobre el modelo de usuario) = solo superuser.
        es_usuario = self.model is get_user_model()
        if (field in TOGGLE_SUPERUSER or es_usuario) and not request.user.is_superuser:
            return HttpResponseForbidden()
        obj = get_object_or_404(self.model, pk=pk)
        if es_usuario and obj.pk == request.user.pk and field in ("is_active", "is_staff", "is_superuser"):
            messages.error(request, "No puedes desactivarte ni quitarte permisos a ti mismo.")
            return redirect(request.META.get("HTTP_REFERER") or reverse("panel:home"))
        new = not bool(getattr(obj, field))
        setattr(obj, field, new)
        fields = [field]
        if field == "is_superuser" and new:   # superuser implica staff
            obj.is_staff = True
            fields.append("is_staff")
        obj._actor = request.user   # leído por la señal de UserLog si obj es CustomUser
        obj.save(update_fields=fields)
        done = TOGGLE_DONE[field][0 if new else 1]
        from core.utils.audit import audit   # import tardío: audit importa este módulo
        audit(request.user, "cambió", obj, f"{field} = {new}")
        messages.success(request, f"«{obj}» {done}.")
        # Volver a donde se llamó (lista o detalle) o, si no, a la lista.
        back = request.META.get("HTTP_REFERER")
        if not back:
            try:
                back = reverse(f"{self.namespace}:{self.entity}_list")
            except NoReverseMatch:
                back = "/"
        return redirect(back)


class AdminBulkView(StaffRequiredMixin, View):
    """ACCIÓN MASIVA sobre las filas marcadas en una lista (checkbox + «Aplicar»): activar o
    desactivar (cualquier booleano de TOGGLE_META, con el mismo candado de superusuario) y eliminar.
    Una sola ruta para todas las entidades: panel:bulk <app>/<modelo>/. La lista manda
    `accion` («set:<campo>:<1|0>» o «eliminar»), `ids` (separados por coma) y `volver`."""

    def post(self, request, app_label, model_name):
        try:
            model = django_apps.get_model(app_label, model_name)
        except LookupError:
            raise Http404("modelo desconocido")
        volver = request.POST.get("volver") or reverse("panel:home")
        if not url_has_allowed_host_and_scheme(volver, allowed_hosts={request.get_host()}):
            volver = reverse("panel:home")
        ids = [int(x) for x in (request.POST.get("ids") or "").split(",") if x.strip().isdigit()]
        accion = request.POST.get("accion") or ""
        if not ids:
            messages.warning(request, "No hay filas seleccionadas.")
            return redirect(volver)
        qs = model.objects.filter(pk__in=ids)
        if model is get_user_model():
            if not request.user.is_superuser:      # gestionar usuarios = solo superusuario (como los toggles)
                raise PermissionDenied
            if qs.filter(pk=request.user.pk).exists():
                qs = qs.exclude(pk=request.user.pk)
                messages.warning(request, "Tu propio usuario quedó fuera: no puedes desactivarte, quitarte permisos ni borrarte a ti mismo.")
                if not qs.exists():
                    return redirect(volver)
        # 1º la LISTA de la entidad puede atender la acción (p. ej. tablas Data: reprocesar, volver a descargar)
        entidad = request.POST.get("entidad") or ""
        if entidad:
            try:
                vista = resolve(reverse(f"panel:{entidad}_list")).func.view_class
            except (NoReverseMatch, AttributeError):
                vista = None
            gancho = getattr(vista, "bulk_run", None)
            if gancho and gancho(request, accion, qs):
                return redirect(volver)
        if accion == "descargar-imagenes" and _model_has_field(model, "image_url"):
            from apps.system.tasks import download_images_task
            from core.shared.views.imports import anotar_usuario, run_task
            ids_pend = list(qs.exclude(image_url="").filter(image_downloaded=False).values_list("pk", flat=True))
            if not ids_pend:
                messages.info(request, "Las filas marcadas no tienen imágenes pendientes.")
                return redirect(volver)
            bg, result = run_task(download_images_task, model._meta.app_label, model._meta.model_name, ids_pend)
            anotar_usuario(result, request.user)
            messages.success(request, f"Descarga de {len(ids_pend)} imagen(es) {'encolada' if bg else 'hecha'}.")
        elif accion == "subir-nube" and _model_has_field(model, "image"):
            from apps.system.tasks import upload_to_cloud_task
            from core.shared.views.imports import anotar_usuario, run_task
            from core.shared.tasks.cloud import archivos_pendientes, r2_activo
            if not r2_activo():
                messages.error(request, "La nube (R2) está apagada: USE_R2=0.")
                return redirect(volver)
            ids_pend = [pk for _m, pk, _n, _r in archivos_pendientes(model, list(qs.values_list("pk", flat=True)))]
            if not ids_pend:
                messages.info(request, "Las filas marcadas no tienen archivos pendientes de subir (o aún no están descargados).")
                return redirect(volver)
            bg, result = run_task(upload_to_cloud_task, model._meta.app_label, model._meta.model_name, ids_pend)
            anotar_usuario(result, request.user)
            messages.success(request, f"Subida de {len(ids_pend)} archivo(s) a R2 {'encolada' if bg else 'hecha'}.")
        elif accion == "eliminar":
            n = qs.count()
            qs.delete()
            messages.success(request, f"{n} registro(s) eliminado(s).")
        elif accion.startswith("set:"):
            partes = accion.split(":")
            campo, valor = (partes[1], partes[2]) if len(partes) == 3 else ("", "")
            if (campo not in TOGGLE_META and campo not in BULK_FIELDS) or not _model_has_field(model, campo):
                messages.error(request, "Acción no permitida.")
                return redirect(volver)
            if campo in TOGGLE_META and TOGGLE_META[campo][3] and not request.user.is_superuser:
                raise PermissionDenied
            encender = valor == "1"
            n = qs.update(**{campo: encender})
            if campo in BULK_FIELDS:
                hecho = BULK_FIELDS[campo][0 if encender else 1]
            else:
                hecho = str(TOGGLE_DONE.get(campo, ("activado", "desactivado"))[0 if encender else 1]) + "s"
            messages.success(request, f"{n} registro(s) {hecho}.")
        else:
            messages.error(request, "Acción desconocida.")
        return redirect(volver)
