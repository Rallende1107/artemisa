"""collections · acciones POST y páginas «a mano», de gestión y públicas."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, View

from apps.collections.models import ModelBaseCollection
from apps.collections.views.base import _next, _tabla_o_404, _titulo_fila
from apps.collections.views.v1_home import CollectionsPublicHomeView
from apps.users.activity import registrar
from core.shared.models.choices import UserActivityAction
from core.shared.views.base import BasePage


# ==============================================================================
# Público
# ==============================================================================

class AddToCollectionView(LoginRequiredMixin, View):
    """Añade un título del catálogo a la colección del usuario (idempotente).
    El form trae `kind` (collect_kind de la ficha) y `object_id`."""
    login_url = "users:login"

    def post(self, request):
        tabla = ModelBaseCollection.por_medio(request.POST.get("kind", ""))
        oid = (request.POST.get("object_id") or "").strip()
        if tabla is None or not oid.isdigit():
            messages.error(request, _("Contenido inválido."))
            return redirect(_next(request))
        Contenido = tabla.contenido()
        contenido = Contenido.objects.filter(pk=int(oid)).first()
        if contenido is None:
            messages.error(request, _("Contenido desconocido."))
            return redirect(_next(request))
        extra = {}
        if tabla.STATUS_CHOICES:
            extra["status"] = tabla.STATUS_CHOICES.values[0]   # estado inicial = el primero del medio
        fila, created = tabla.objects.get_or_create(user=request.user, content=contenido, defaults=extra)
        if created:
            registrar(request.user, UserActivityAction.COLLECTION_ADD, obj=contenido)
        messages.success(request, _("Añadido a tu colección.") if created else _("Ya estaba en tu colección."))
        return redirect(_next(request))


class RemoveFromCollectionView(LoginRequiredMixin, View):
    """Quita un ítem de la colección del usuario (solo el suyo)."""
    login_url = "users:login"

    def post(self, request, tipo, pk):
        tabla = _tabla_o_404(tipo)
        fila = get_object_or_404(tabla, pk=pk, user=request.user)
        registrar(request.user, UserActivityAction.COLLECTION_REMOVE, obj=fila.content)
        fila.delete()
        messages.success(request, _("Quitado de tu colección."))
        return redirect(_next(request))


class UpdateItemView(LoginRequiredMixin, View):
    """Actualización PARCIAL de una fila propia desde la barra de la ficha o la lista (estado, nota, favorito,
    progreso…): lo que no viene en el POST conserva su valor, y todo pasa por CollectionItemForm. El favorito usa el
    marcador `fav_form` porque un checkbox desmarcado no viaja. Con `ajax=1` responde JSON."""
    login_url = "users:login"

    def post(self, request, tipo, pk):
        from apps.collections.forms import item_form
        tabla = _tabla_o_404(tipo)
        fila = get_object_or_404(tabla, pk=pk, user=request.user)
        Form = item_form(tabla)
        data = {k: ("" if v is None else v) for k, v in Form(instance=fila).initial.items()}   # lo actual
        for k in data:
            if k in request.POST:
                data[k] = request.POST.get(k, "")
        if "is_favorite" in data and ("is_favorite" in request.POST or "fav_form" in request.POST):
            data["is_favorite"] = "true" if (request.POST.get("is_favorite") or "").strip().lower() in ("1", "true", "on") else "false"
        form = Form(data, instance=fila)
        if not form.is_valid():
            if request.POST.get("ajax") == "1":
                return JsonResponse({"ok": False, "errores": form.errors}, status=400)
            messages.error(request, _("No se pudo guardar: %s") % "; ".join(f"{k}: {' '.join(v)}" for k, v in form.errors.items()))
            return redirect(_next(request))
        fila = form.save()
        if request.POST.get("ajax") == "1":
            return JsonResponse({"ok": True, "status": fila.get_status_display() if getattr(fila, "status", "") else ""})
        messages.success(request, _("Colección actualizada."))
        return redirect(_next(request))


class ItemEditView(BasePage, UpdateView):
    """EDICIÓN de una fila de MI colección con CollectionItemForm: seguimiento y dónde la veo / de dónde la
    descargué, en un solo formulario. Solo el dueño de la fila."""
    staff_only = False
    login_only = True   # el área del usuario: logueado, sin exigir staff
    template_name = "collections/item_edit.html"
    login_url = "users:login"
    background_image = "bg-collections-home"
    background_fallback = "bg-users-user"
    title = _("Mi colección")

    @property
    def tabla(self):
        return _tabla_o_404(self.kwargs["tipo"])

    def get_object(self, queryset=None):
        return get_object_or_404(self.tabla, pk=self.kwargs["pk"], user=self.request.user)

    def get_form_class(self):
        from apps.collections.forms import item_form
        return item_form(self.tabla)

    def get_success_url(self):
        return _next(self.request, reverse("collections:edit", args=[self.tabla.medio(), self.object.pk]))

    def form_valid(self, form):
        messages.success(self.request, _("Guardado."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tabla, fila = self.tabla, self.object
        etiqueta, _icono, bg = CollectionsPublicHomeView.card_de(tabla)
        ctx.update({
            "medio": tabla.medio(), "medio_label": etiqueta, "fila": fila,
            "titulo": _titulo_fila(fila), "background_image": bg,
            "page_title": _("Editar · %s") % _titulo_fila(fila),
            "portada": fila.content.cover_url, "ficha_url": fila.content.get_absolute_url(),
            "volver": reverse("collections:list", args=[tabla.medio()]),
        })
        return ctx
