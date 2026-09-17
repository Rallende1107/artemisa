"""Vistas BASE del proyecto — el ÚNICO juego de bases de página.

Aquí murieron las Admin* de página (AdminListView/Create/Update/Detail/Delete):
estas Base* son NUESTRAS, con un nivel de herencia (genérica de Django → Base →
vista de entidad) y una regla simple:

    LO EXPLÍCITO GANA, LO NO DECLARADO SE DERIVA.

Cada vista declara sus nombres de ruta como atributos (`list_url`, `create_url`,
`data_url`, `update_url`…, estilo tipo-rol): NADA se deriva. Cada Base arma su
contexto EXPLÍCITO con lo que su plantilla usa (Poseidon):

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.title
        ctx["cancel_url"] = self.cancel_url
        ...

La config compartida vive UNA vez por entidad:

    class BaseCountry:
        model = Country
        entity = "country"
        label = "tipo de rol"
        label_plural = "tipos de rol"
        background_image = "bg-xxxx-xxxx"
        background_fallback = "bg-xxxx-xxxx"   # respaldo si falta la imagen

Los mensajes al usuario usan gettext con placeholders NOMBRADOS (%(label)s),
nunca f-strings: así el traductor puede reordenar las palabras por idioma.

Aquí viven TODAS las Base*: página (BaseList/BaseCreate/BaseUpdate/BaseAdminDetailView/BaseDelete)
y protocolo (BaseDataView para DataTables, BaseSelectView para Select2). En
core/views/v8_actions.py solo queda el cromo: AdminToggleView (acciones booleanas),
las acciones del panel (toggle y masivo).
"""
from django import forms
from django.conf import settings
from pathlib import Path

from django.contrib import messages

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models.deletion import Collector, ProtectedError, RestrictedError
from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.base import ContextMixin
from django.views.generic import (
    FormView,
    TemplateView,
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from core.utils.audit import audit
from core.utils.views_base import LazySeq, Params, _Borrado, _is_bool_field, _resolve, search_words, cell, link
from core.shared.views.filters import _campo
from core.mixin.by import ByMixin, SIN_VALOR, _entry_choices, nav_fields  # noqa: F401
from core.mixin.access import StaffRequiredMixin
from core.views import NAMESPACE, TOGGLE_META
from core.utils.views import _bg_from_class, _model_has_field, resolve_background
from core.utils.public import resolve_cover, cover_cards, url_detail
from core.shared.forms.widgets import etiqueta_select

class BasePage(ContextMixin):
    """La VISTA BASE de página: candado por palanca (`staff_only`, el catálogo público lo apaga),
    las perillas de página y el contexto que las plantillas, las migas y el sidebar leen. Las demás
    Base (lista, crear, editar, ficha, borrar) la heredan y SOLO sobrescriben lo suyo: template_name,
    rutas y su get_context_data (que llama a super() y añade lo de su plantilla).
    La entidad (model, entity, label, label_plural, fondo, sección) la trae la `_Entidad`."""
    template_name = ""    # cada Base pone el suyo (admin_panel/list.html, form.html…)
    staff_only = True     # anónimo → login; logueado no-staff → 403 (lo público pone False)
    login_only = False    # solo logueados, sin exigir staff (el área del usuario: su colección)
    title = ""            # título de la página («Lista de países», «Crear país», «Eliminar país»)
    #  Los títulos también se pueden declarar UNA vez en la Base de la entidad y que cada vista tome el suyo:
    #    title_list   la lista        ·  title_create  el alta      ·  title_update  la edición
    #    title_detail la ficha        ·  title_delete  el borrado
    #  Si la vista trae `title`, ese manda; si no, usa el de su Base; y si tampoco hay, el que arme la vista.
    active_entity = ""    # slug propio de una vista fija (para el sidebar); vacío = entity
    page_template = None  # el CASCARÓN de página (base.html público, admin_panel/base_admin.html gestión, panel/base.html importación); None → admin_panel/base_admin.html
    entity = label = label_plural = ""   # los trae el mixin _Base<Modelo>; una página «a mano» no los tiene
    # Pestañas de una ficha hacia sus listas «por»: [(clave, etiqueta, ruta, tipo)] → la plantilla recibe
    # `tabs` [(etiqueta, href)] y `tab_url` {clave: href} («Ver todo» del adelanto). Ruta = <ruta>/<tipo>/<pk>/.
    tabs = ()

    def dispatch(self, request, *args, **kwargs):
        if (self.staff_only or self.login_only) and not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("users:login"))
        if self.staff_only and not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    # qué `title_*` de la Base usa cada tipo de vista (lo pisa `title` si la vista lo declara)
    title_attr = ""

    @property
    def page_title(self):
        """El título: el de la vista; si no, el `title_<tipo>` que declare su Base; si no, vacío."""
        return self.title or (str(getattr(self, self.title_attr, "") or "") if self.title_attr else "")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "page_title": self.page_title,
            "background_image": resolve_background(self),
            "page_template": self.page_template,
            "active_entity": self.active_entity or self.entity,
            "entity": self.entity, "label": self.label, "label_plural": self.label_plural,
            "section_url": getattr(self, "section_url", ""), "section_label": getattr(self, "section_label", ""),
            "es_gestion": self.staff_only,
        })
        return ctx

    def tabs_de(self, obj):
        """[(etiqueta, href)] y {clave: href} de las pestañas declaradas para este objeto."""
        lista = [(etiqueta, url_by_route(ruta, tipo, obj)) for _clave, etiqueta, ruta, tipo in self.tabs]   # con el slug del padre (URL canónica)
        return lista, {t[0]: href for t, (_e, href) in zip(self.tabs, lista)}


class BaseHomeView(BasePage, TemplateView):
    """Home de una SECCIÓN del panel (música, otaku…): tarjetas de sus entidades con
    fondo propio. El sidebar enlaza aquí; cada card lleva a la lista de su entidad.
    (v0_home por app, junto al home público). La subclase declara
    `groups = [(título, [(entity, label, icono, bg), …]), …]` (o `cards` = grilla plana).
    Las cards NO cuentan filas: un home solo navega, y un COUNT(*) por card sobre
    tablas de millones de filas es lo más caro que podría hacer. El número exacto se
    ve en la lista (DataTable)."""
    template_name = "admin_panel/section_home.html"
    cards = []
    groups = None   # [(título, [(entity, label, icono, bg) …]) …]
    namespace = NAMESPACE
    staff_only = True
    # Reutilizable en OTROS paneles (p. ej. importación): base + breadcrumb propios.
    page_template = "admin_panel/base_admin.html"
    home_url = "panel:home"

    def _card_item(self, card, parent_bg):
        """(entity, label, icono, bg) → dict para la plantilla. El fondo es el explícito de la
        card; si su imagen falta, el del home de la sección (así se nota el error)."""
        if len(card) != 4:
            raise ImproperlyConfigured(f"{type(self).__name__}: cada card es (entity, label, icono, bg); recibí {card!r}")
        entity, label, icon, bg_class = card
        # url: ruta completa si `entity` trae namespace (":"), a la home si termina
        # en «-home», o a la lista de la entidad en el resto. Admite una QUERY al
        # final («panel:email-message_list?estado=queued») para abrir la lista filtrada.
        entity, _sep, query = entity.partition("?")
        args = []
        if ":" in entity and "/" in entity:                 # «panel:external-source_by-type/social» → args del reverse
            entity, _sep2, resto = entity.partition("/")
            args = [a for a in resto.split("/") if a]
        if ":" in entity:
            url = entity
        elif entity.endswith("-home"):
            url = f"{self.namespace}:{entity}"
        else:
            url = f"{self.namespace}:{entity}_list"
        href = reverse(url, args=args or None) + (f"?{query}" if query else "")
        bg = _bg_from_class(bg_class) or parent_bg
        return {"url": url, "href": href, "label": label, "icon": icon, "bg": bg}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["home_url"] = self.home_url
        # Fallback del PADRE = el fondo de esta home. Si un modelo no tiene su
        # propia imagen, la card usa la del padre; si tampoco hay, queda gris.
        parent_bg = _bg_from_class(resolve_background(self))   # con respaldo, como la página
        if self.groups:
            grps = []
            for title, cards in self.groups:
                planas = []
                for c in cards:                       # una card, o un LazySeq de cards por tipo (se lee ahora, no al importar)
                    planas.extend(list(c) if isinstance(c, LazySeq) else [c])
                grps.append({"title": title, "items": [self._card_item(c, parent_bg) for c in planas]})
            ctx["groups"] = grps
        else:
            ctx["items"] = [self._card_item(c, parent_bg) for c in self.cards]
        return ctx


class BasePublicHomeView(TemplateView):
    """HOME público de una SECCIÓN (Series, Otaku, Música…), declarativo como BaseHomeView en gestión: la
    subclase declara sección, títulos y fondo, y sus FILAS en `get_rows()` con `self.row(...)`; cada fila lleva
    con «Ver todo →» a una LISTA (no hay homes intermedios: home de sección → lista). La base arma el contexto de
    `sections/home.html`; la subclase NO escribe get_context_data.

        class MoviesPublicHomeView(BasePublicHomeView):
            section = "peliculas"; title = _("Películas")
            background_image = "bg-movies-home"
            def get_rows(self):
                return [self.row(_("Recientes"), Movie.objects.filter(is_active=True).order_by("-release_year")[:12],
                                 _("Película"), "movies:movie-detail", url="movies:movies-catalog"), …]
    """
    template_name = "sections/home.html"
    section = ""            # active_section: pestaña del nav público
    title = ""              # título de la página: lo ÚNICO que pinta el hero
    title_tab = ""          # pestaña del navegador; vacío = title
    card_tag = ""           # etiqueta por defecto de la tarjeta («Compañía»)
    card_sub = None         # callable opcional para el subtítulo de la tarjeta
    detail_url = ""         # ruta por defecto de la ficha de cada tarjeta
    background_image = ""
    background_fallback = ""

    def row(self, title, objs=None, tag=None, detail_url=None, url=None, sub=None, items=None, empty=None, group=None):
        """Una fila del home: título, «Ver todo» (nombre de ruta de la LISTA) y tarjetas. `items` ya
        armadas (p. ej. canciones con su propio formato) ganan sobre `objs`. La fila se pinta SIEMPRE, con su
        título; si no trae nada, dice `empty` («Sin juegos añadidos.»; sin declarar, «Nada añadido todavía.»)."""
        if items is None:
            items = cover_cards(objs, tag or self.card_tag, detail_url or self.detail_url, sub=sub or self.card_sub)
        return {"title": title, "url": reverse(url) if url else "", "items": items,
                "empty": empty or _("Nada añadido todavía."),
                "group": str(group) if group else "", "group_key": slugify(group) if group else ""}

    def get_rows(self):
        return []

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filas = self.get_rows()
        grupos, vistos = [], set()
        for f in filas:
            if f.get("group_key") and f["group_key"] not in vistos:
                vistos.add(f["group_key"])
                grupos.append({"key": f["group_key"], "label": f["group"]})
        ctx.update({
            "active_section": self.section,
            "background_image": resolve_background(self),
            "title_tab": self.title_tab or self.title,
            "title": self.title,
            "rows": filas,
            # PESTAÑAS (componente templates/components/tabs.html): salen de los `group` de las propias filas, en
            # su orden, con «Todos» delante. Una home cuyas filas no declaren grupo no tiene pestañas y conserva
            # el nav de sección de siempre.
            "nav_tabs": ([{"key": "", "label": _("Todos")}] + grupos) if grupos else [],
        })
        if grupos:
            ctx["SECCION_NAV"] = []      # las pestañas OCUPAN su sitio: no se pintan las dos barras
        return ctx


class BaseCreate(BasePage, CreateView):
    """Alta. Cada vista declara TODO directo (nada se deriva):

        class CountryCreateView(BaseCountry, BaseCreate):
            form_class = f.CountryForm
            form_template = "catalogs/form/country.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
            list_url = "panel:country_list"                 # breadcrumb
            success_url = "panel:country_list"              # a dónde ir al guardar
            cancel_url = "panel:country_list"               # a dónde va «Cancelar»
            success_message = _("País «%(obj)s» creado.")
            title = _("Crear país")                        # título de la página

    Al guardar: mensaje de éxito + auditoría. Al fallar: cada error del form también
    como mensaje (además de verse junto al campo). `get_extra_context()` es el gancho
    para contexto adicional sin tocar get_context_data."""
    title_attr = "title_create"
    template_name = "admin_panel/form.html"   # el CUADRO maestro; el HTML de campos es `form_template`
    form_template = ""    # parcial de campos que incluye el cuadro; vacío → loop genérico
    list_url = ""         # nombre de ruta de la lista (breadcrumb)
    success_url = ""      # nombre de ruta a la que ir al guardar
    cancel_url = ""       # nombre de ruta de «Cancelar»
    success_message = ""  # admite %(label)s y %(obj)s; vacío → el genérico

    def get_success_url(self):
        return reverse(self.success_url)

    def get_initial(self):
        """«Nuevo» desde una lista «por» (?movie=12): el padre llega preseleccionado en el formulario."""
        ini = super().get_initial()
        campos = self.get_form_class().base_fields
        ini.update({k: v for k, v in self.request.GET.items() if k in campos})
        return ini

    def form_valid(self, form):
        try:
            with transaction.atomic():
                resp = super().form_valid(form)
        except IntegrityError:
            form.add_error(None, _("No se pudo guardar: ya existe un registro con un valor único duplicado."))
            return self.form_invalid(form)
        msg = self.success_message or _("%(label)s «%(obj)s» creado correctamente.")
        messages.success(self.request, msg % {
            "label": self.label.capitalize(), "obj": self.object})
        audit(self.request.user, "creó", self.object)
        return resp

    def form_invalid(self, form):
        for campo, errores in form.errors.items():
            etiqueta = "" if campo == "__all__" else f"{form.fields[campo].label}: "
            for i in range(min(len(errores), 3)):          # errores[i] ya viene como texto
                messages.error(self.request, f"{etiqueta}{errores[i]}")
        return super().form_invalid(form)

    def get_extra_context(self):
        """Gancho: contexto adicional de la subclase (dict)."""
        return {}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["list_url"] = self.list_url          # breadcrumb
        ctx["cancel_url"] = self.cancel_url
        ctx["form_template"] = self.form_template   # el cuadro lo incluye; sin él, loop genérico
        ctx["has_bool_fields"] = any(
            getattr(bf.field.widget, "input_type", "") == "checkbox" for bf in ctx["form"])
        ctx["is_create"] = True
        ctx.update(self.get_extra_context())
        return ctx

class BaseUpdate(BasePage, UpdateView):
    """Edición. Mismas perillas que BaseCreate, todas directas en la vista:
    `form_class`, `form_template`, `list_url`, `success_url`, `cancel_url`,
    `success_message` y `title` («Editar país»)."""
    title_attr = "title_update"
    template_name = "admin_panel/form.html"
    form_template = ""
    list_url = ""
    success_url = ""
    cancel_url = ""
    success_message = ""

    def get_success_url(self):
        return reverse(self.success_url)

    def form_valid(self, form):
        try:
            with transaction.atomic():
                resp = super().form_valid(form)
        except IntegrityError:
            form.add_error(None, _("No se pudo guardar: ya existe un registro con un valor único duplicado."))
            return self.form_invalid(form)
        msg = self.success_message or _("%(label)s «%(obj)s» actualizado correctamente.")
        messages.success(self.request, msg % {
            "label": self.label.capitalize(), "obj": self.object})
        cambios = ", ".join(f for f in form.changed_data if f != "avatar_clear")
        audit(self.request.user, "editó", self.object, cambios)
        return resp

    def form_invalid(self, form):
        for campo, errores in form.errors.items():
            etiqueta = "" if campo == "__all__" else f"{form.fields[campo].label}: "
            for i in range(min(len(errores), 3)):
                messages.error(self.request, f"{etiqueta}{errores[i]}")
        return super().form_invalid(form)

    def get_extra_context(self):
        """Gancho: contexto adicional de la subclase (dict)."""
        return {}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["list_url"] = self.list_url
        ctx["cancel_url"] = self.cancel_url
        ctx["form_template"] = self.form_template
        ctx["has_bool_fields"] = any(
            getattr(bf.field.widget, "input_type", "") == "checkbox" for bf in ctx["form"])
        ctx.update(self.get_extra_context())
        return ctx

class BaseDelete(BasePage, DeleteView):
    title_attr = "title_delete"
    template_name = "admin_panel/confirm_delete.html"
    list_url = ""         # nombre de ruta de la lista (breadcrumb)
    success_url = ""      # nombre de ruta a la que ir al borrar
    cancel_url = ""       # nombre de ruta de «Cancelar»
    success_message = ""  # personal de la vista; vacío → el genérico

    def form_valid(self, form):
        nombre = str(self.object)
        obj_model, obj_pk = type(self.object), self.object.pk
        try:
            resp = super().form_valid(form)
        except (ProtectedError, RestrictedError) as e:
            # Una FK con PROTECT/RESTRICT lo impide: se avisa en vez de un error 500.
            n = len(getattr(e, "protected_objects", None) or getattr(e, "restricted_objects", ()))
            messages.error(self.request, _("No se puede eliminar «%(obj)s»: %(n)s registro(s) dependen de él.")
                           % {"obj": nombre, "n": n})
            return redirect(self.request.get_full_path())
        # El objeto ya no existe: se audita con una cáscara (modelo + pk + nombre).
        audit(self.request.user, "eliminó", _Borrado(obj_model, obj_pk, nombre))
        msg = self.success_message or _("%(label)s «%(obj)s» eliminado.")
        messages.success(self.request, msg % {
            "label": self.label.capitalize(), "obj": nombre})
        return resp

    def get_success_url(self):
        return reverse(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["list_url"] = self.list_url
        ctx["cancel_url"] = self.cancel_url
        ctx["arrastra"] = self._arrastra()   # [(nombre plural, cuántos)] que se borran en cascada
        return ctx

    def _arrastra(self):
        """Qué se lleva por delante el borrado (las FK en cascada): [(«títulos», 3), («imágenes», 12)].
        Lo calcula el Collector de Django, el mismo que usa su admin; así el borrado real no da miedo."""
        collector = Collector(using="default")
        collector.collect([self.object])
        cuenta = {}
        for model, objs in collector.data.items():
            n = len([o for o in objs if not (model is type(self.object) and o.pk == self.object.pk)])
            if n:
                cuenta[model] = cuenta.get(model, 0) + n
        for qs in collector.fast_deletes:
            n = qs.count()
            if n:
                cuenta[qs.model] = cuenta.get(qs.model, 0) + n
        return [(str(m._meta.verbose_name_plural), n) for m, n in cuenta.items()]


class BaseImport(BasePage, FormView):
    """Importación de una tabla Data desde su fuente. UNA vista por entidad con un ARREGLO de formularios que
    el HTML (`admin_panel/form_import.html`) recorre con un `for`: uno por forma de pedir los datos.

        class LoadVNDBDataF95GameView(BaseDataVndbGame, BaseImport):
            forms = (f.DataVndbGameSearchForm, f.DataVndbGameImportForm, f.DataVndbGamePagesForm)
            title = _("Importar juegos")
            cancel_url = "panel:games-home"
            task_uno = tasks.import_game_task            # las tareas que esos formularios piden a la vista
            task_rango = tasks.import_vndb_range_task
            task_barrido = tasks.barrer_vndb_task

    Sigue siendo un `FormView` de Django: el que llegó lo elige `get_form_class()` por el `action` del POST, y
    de ahí en adelante Django hace lo de siempre (`form_valid` / `form_invalid`, `get_success_url`). Quitar una
    forma de importar (p. ej. la búsqueda, si la API deja de darla) = quitar su clase del arreglo.

    Cada FORMULARIO es independiente y lleva lo suyo: `slug` (qué botón lo envió y prefijo de sus campos),
    `titulo`, `boton`, `success_url` y `tarea(vista)` → (task, args, kwargs) con lo que hay que ejecutar.
    La vista decide CÓMO: con Celery va al worker, sin él corre en esta misma petición, y avisa. Modelo,
    entidad, sección y fondo de respaldo los trae la `_Entidad` de la tabla Data, como en cualquier alta."""
    template_name = "admin_panel/form_import.html"
    forms = ()                  # las clases de formulario, en el orden en que se pintan
    cancel_url = ""             # «Cancelar»; vacío = la lista de DATOS de la entidad (de donde se vino)
    source_key = ""             # "vndb" / "mal" / "deezer": va en el breadcrumb («importar · vndb · juego»)
    source_label = ""           # "VNDB" / "AniList": el nombre de la fuente en los textos («VNDB ↗»)
    ayuda = ""                  # una línea bajo el título: qué trae
    task_uno = None             # las tareas que los formularios piden a la vista
    task_rango = None
    task_barrido = None
    task_ids = None

    # ------------------------------- el arreglo -------------------------------
    def clases(self):
        """El arreglo declarado; una vista con `form_class` suelto sigue valiendo (un arreglo de uno)."""
        return tuple(self.forms) or ((self.form_class,) if self.form_class else ())

    @staticmethod
    def slug_de(cls):
        return getattr(cls, "slug", cls.__name__.lower())

    # ------------------------------- FormView: cuál es «el» formulario -------------------------------
    def get_form_class(self):
        """El que envió el POST, por su `action`; en un GET, ninguno (la página los pinta todos)."""
        if self.request.method not in ("POST", "PUT"):
            return None
        slug = self.request.POST.get("action", "")
        cls = next((c for c in self.clases() if self.slug_de(c) == slug), None)
        if cls is None:
            raise Http404(_("No sé qué formulario enviaste."))
        return cls

    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        return self.armar(form_class, **self.get_form_kwargs()) if form_class else None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        cls = self.get_form_class()
        if cls is not None:      # prefijo: dos formularios con un campo del mismo nombre no chocan
            kwargs["prefix"] = self.slug_de(cls)
        return kwargs

    def armar(self, cls, **kwargs):
        """Instancia un formulario del arreglo y le cuelga lo que la plantilla necesita para pintarlo."""
        kwargs.setdefault("prefix", self.slug_de(cls))
        form = cls(**kwargs)
        form.slug = self.slug_de(cls)
        form.titulo = getattr(cls, "titulo", "")
        form.boton = getattr(cls, "boton", _("Importar"))
        form.success_label = getattr(cls, "success_label", "")
        form.es_buscador = "q" in form.fields
        form.checks = [c for c in form.visible_fields() if c.field.widget.input_type == "checkbox"]
        if form.es_buscador:     # la caja manda por GET a su vista de resultados
            form.resultados_href = reverse(getattr(cls, "resultados_url", "") or self.request.path)
        return form

    # ------------------------------- FormView: qué pasa al enviar -------------------------------
    def form_valid(self, form):
        """El formulario dice QUÉ ejecutar (`tarea`); aquí se decide CÓMO: con Celery va al worker, sin él
        corre en esta misma petición. Si devuelve None es que no hay nada que lanzar (ya avisó por qué)."""
        from core.shared.views.imports import anotar_usuario, run_task
        que_ejecutar = form.tarea(self)
        if que_ejecutar is None:
            return redirect(self.request.path)
        task, args, kwargs = que_ejecutar
        bg, result = run_task(task, *args, **kwargs)
        anotar_usuario(result, self.request.user)
        if bg:
            messages.info(self.request, _("%(que)s: encolado en background (Celery).") % {"que": form.resumen(self)})
        else:
            messages.success(self.request, _("%(que)s: hecho aquí mismo, sin Celery → %(r)s.")
                             % {"que": form.resumen(self), "r": getattr(result, "result", None)})
        return super().form_valid(form)

    def volver_href(self):
        """A dónde va «Cancelar»: lo que declare la vista o, por defecto, la lista de DATOS de esta entidad —
        que es de donde se entra a importar, igual que a un alta se entra desde su lista."""
        if self.cancel_url:
            return reverse(self.cancel_url)
        if not self.entity:
            return ""
        try:
            return reverse(f"{getattr(self, 'namespace', '') or NAMESPACE}:{self.entity}_list")
        except NoReverseMatch:      # una entidad sin lista propia: sin botón, mejor que reventar
            return ""

    def get_success_url(self):
        """La declara el formulario que se envió; si no, se recarga la página."""
        destino = getattr(self.get_form_class(), "success_url", "") or self.success_url
        return reverse(destino) if destino else self.request.path

    # ------------------------------- la página: todos los formularios -------------------------------
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        enviado = ctx.get("form")            # el que llegó (con sus errores, si los tiene)
        ctx["forms"] = [enviado if enviado is not None and enviado.slug == self.slug_de(c) else self.armar(c)
                        for c in self.clases()]
        ctx.update({
            "source_key": self.source_key, "source_label": self.source_label,
            "label": self.label, "ayuda": self.ayuda,
            "cancel_href": self.volver_href(),
            "celery_enabled": settings.CELERY_ENABLED,
        })
        return ctx


class SeleccionIdsForm(forms.Form):
    """Los candidatos MARCADOS en una página de resultados. Las opciones son los ids que devolvió la búsqueda,
    así que no se puede colar por POST un id que no estaba en pantalla."""

    ids = forms.TypedMultipleChoiceField(
        label=_("Resultados marcados"), coerce=int, required=True,
        error_messages={"required": _("Marca al menos un resultado para importar."),
                        "invalid_choice": _("El resultado «%(value)s» no está entre los de esta búsqueda.")},
    )

    def __init__(self, *args, candidatos=(), **kwargs):
        super().__init__(*args, **kwargs)
        # TODOS los candidatos valen: los nuevos se importan; los que «ya están» se RE-OBTIENEN (fetch + process)
        self.fields["ids"].choices = [(r["id"], r.get("titulo", "")) for r in candidatos]


class BaseImportSearch(BasePage, FormView):
    """RESULTADOS de una búsqueda por nombre en la fuente, en su propia página: la caja está en el lanzador
    (`BaseImport`), que manda aquí por GET (?q=). Se pintan TODOS los candidatos, se marcan los que se quieran
    y un solo botón los importa al crudo. «Volver» regresa al lanzador.

        class LoadVNDBDataF95GameSearchView(BaseDataVndbGame, BaseImportSearch):
            search_form = f.DataVndbGameSearchForm       # el de la caja: valida el texto y dice qué tarea lanza
            buscador = staticmethod(vndb.buscar_juegos)  # query → [{"id", "titulo", "sub", "imagen", "link", "ya"}]
            task_ids = tasks.import_vndb_ids_task
            back_url = "panel:vndb-game"                 # «Volver»
            title = _("Buscar juegos en VNDB")
    """
    template_name = "admin_panel/form_import_results.html"
    form_class = SeleccionIdsForm
    por_pagina = 25             # resultados por página (la fuente ya devolvió todos; se pagina en local)
    search_form = None          # el formulario de la caja (`q` + `tarea_lista`)
    buscador = None             # staticmethod(query) → candidatos
    task_ids = None             # la tarea de lista de ids del tipo
    back_url = ""               # el lanzador del que se viene
    source_key = ""
    source_label = ""
    ayuda = ""                  # una línea bajo el título: qué hace esta página

    # ------------------------------- la búsqueda -------------------------------
    @cached_property
    def caja(self):
        return self.search_form()

    @cached_property
    def q(self):
        """Lo que se tecleó (?q=), validado POR EL CAMPO del formulario de la caja: largo mínimo y máximo."""
        crudo = self.request.GET.get("q")
        if not crudo:
            return ""
        try:
            return self.caja.fields["q"].clean(crudo)
        except ValidationError as exc:
            messages.warning(self.request, " ".join(exc.messages))
            return ""

    guardar_minutos = 10        # la búsqueda se guarda este tiempo: paginar o volver no vuelve a llamar a la fuente

    def clave_cache(self):
        """Una entrada por página de resultados y texto buscado (la ruta ya lleva fuente y entidad)."""
        import hashlib
        return "busqueda:" + hashlib.sha1(f"{self.request.path}|{self.q}".encode()).hexdigest()

    @cached_property
    def candidatos(self):
        """Los resultados de la fuente. Se guardan en caché: cada página, y el POST que importa, leen de ahí
        en vez de repetir la búsqueda (que con las pausas de la API puede tardar minutos)."""
        from django.core.cache import cache
        if not self.q:
            return []
        guardados = cache.get(self.clave_cache())
        if guardados is not None:
            return guardados
        try:
            resultados = self.buscador(self.q)
        except Exception as exc:  # noqa: BLE001 — la API caída no tumba la página
            messages.error(self.request, f"La búsqueda falló: {type(exc).__name__}: {exc}")
            return []
        cache.set(self.clave_cache(), resultados, self.guardar_minutos * 60)
        return resultados

    # ------------------------------- FormView -------------------------------
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["candidatos"] = self.candidatos     # las opciones válidas son los resultados en pantalla
        return kwargs

    def form_valid(self, form):
        """Los ids marcados → la tarea de lista de ids que declara el formulario de la caja."""
        from core.shared.views.imports import anotar_usuario, run_task
        ids = sorted(set(form.cleaned_data["ids"]))
        task, args, kwargs = self.caja.tarea_lista(self, ids)
        bg, result = run_task(task, *args, **kwargs)
        anotar_usuario(result, self.request.user)
        from django.core.cache import cache
        cache.delete(self.clave_cache())          # la próxima vez se vuelve a preguntar: los importados ya «están»
        ya = {r["id"] for r in self.candidatos if r.get("ya")}
        nuevos, otra_vez = [i for i in ids if i not in ya], [i for i in ids if i in ya]
        partes = []
        if nuevos:
            partes.append(_("%(n)s nuevo(s)") % {"n": len(nuevos)})
        if otra_vez:
            partes.append(_("%(n)s re-obtenido(s)") % {"n": len(otra_vez)})
        que = _("Importar %(que)s de la búsqueda (%(detalle)s)") % {"que": self.label.lower(), "detalle": " · ".join(partes)}
        if bg:
            messages.info(self.request, _("%(que)s: encolado en background (Celery).") % {"que": que})
        else:
            messages.success(self.request, _("%(que)s: hecho aquí mismo, sin Celery → %(r)s.")
                             % {"que": que, "r": getattr(result, "result", None)})
        return super().form_valid(form)

    def form_invalid(self, form):
        """Sin marcar nada (o con un id que no salía): se dice y se vuelve a los mismos resultados."""
        for errores in form.errors.values():
            for e in errores:
                messages.warning(self.request, e)
        return redirect(self.request.get_full_path())

    def get_success_url(self):
        destino = getattr(self.search_form, "success_url", "") or self.back_url
        return reverse(destino) if destino else self.request.path

    def get_context_data(self, **kwargs):
        from django.core.paginator import Paginator
        ctx = super().get_context_data(**kwargs)
        paginador = Paginator(self.candidatos, self.por_pagina)
        pagina = paginador.get_page(self.request.GET.get("page") or 1)
        ctx.update({
            "caja": self.caja, "q": self.q, "resultados": pagina.object_list, "pagina": pagina,
            "total": paginador.count,
            "nuevos": sum(1 for r in self.candidatos if not r.get("ya")),
            "con_imagen": any(r.get("imagen") for r in self.candidatos),   # creadores no traen foto: sin columna
            "source_key": self.source_key, "source_label": self.source_label,
            "label": self.label, "ayuda": self.ayuda,
            "back_href": reverse(self.back_url) if self.back_url else "",
            "success_label": getattr(self.search_form, "success_label", ""),
            "celery_enabled": settings.CELERY_ENABLED,
        })
        return ctx


class BaseList(BasePage, ListView):
    """La MADRE de las listas: un DataTable (con tarjetas opcionales) alimentado por su Data.
    Genérica: no sabe de gestión ni de catálogo; eso lo ponen AdminListView y PublicListView.
    La vista declara TODO directo:

        data_url = "panel:person_data"   # la ruta de su Data: de ahí salen columnas, filtros, prioridad y acciones
        title = _("Lista de personas")

    La ruta es el ÚNICO contrato con la Data: la base pregunta al resolver qué vista atiende
    `data_url` y de esa clase toma `columns`, `priority`, `actions` y `filters` (panel lateral,
    opcional y por modelo en v5_filters.py). Las piezas del interior son plantillas aparte:
    list_table.html (tabla), list_cards.html (tarjetas) y filters.html (panel)."""
    data_url = ""          # nombre de ruta del endpoint JSON (obligatoria)
    enable_cards = False   # toggle cards/lista (la Data declara card_title / card_image)
    cards_default = False  # True → la primera vez se abre en tarjetas
    con_id = False         # columna Id (pk) en la tabla (gestión sí, catálogo no)

    @cached_property
    def data(self):
        """La Data que atiende `data_url` (dueña de columnas, filtros, orden y prioridad)."""
        if not self.data_url:
            raise ImproperlyConfigured(f"{type(self).__name__}: declara `data_url` (la ruta de su Data)")
        try:
            url = reverse(self.data_url, args=self.data_url_args() or None)   # «obras de»: la ruta lleva el pk
        except NoReverseMatch:
            url = reverse(self.data_url)                                       # catálogo (y «por»: misma Data)
        return resolve(url).func.view_class

    @property
    def filters(self):
        return self.data.filters   # el panel es el de la Data: es ella quien filtra

    def data_url_args(self):
        """Argumentos de la ruta de la Data (la lista completa no lleva; ver BaseListContext)."""
        return []

    def data_route(self):
        """(nombre de ruta, args) del endpoint JSON."""
        return self.data_url, self.data_url_args()

    def panel(self):
        """Las filas del panel de filtros (la Data decide). Los CHOICES del mapa «por» no van aquí como filtro
        combinable: van como NAVEGACIÓN (selección única que lleva a la lista «por»; ver `type_tabs`)."""
        if not self.filters:
            return []
        nav = nav_fields(self.data())
        return [f for f in self.filters.panel(self.model, self.request.GET) if f[0] not in nav]

    def panel_excluir(self):
        """Las filas del bloque «Excluir» del panel (mismo criterio que `panel`)."""
        if not self.filters:
            return []
        nav = nav_fields(self.data())
        return [f for f in self.filters.panel_excluir(self.model, self.request.GET) if f[0][len("no-"):] not in nav]

    def get_queryset(self):
        return self.model.objects.none()   # el shell no necesita filas

    def boton_extra(self, boton):
        """Un botón declarado → {"href", "texto", "icono", "nueva", "clase", "title"}. Acepta la tupla corta
        (ruta, texto, icono) o un diccionario con `url` + `args`/`query`, o `href` directo (+ `nueva`, `clase`, `title`).
        Si la ruta no existe, el botón se ignora (href vacío)."""
        if not isinstance(boton, dict):
            boton = dict(zip(("url", "texto", "icono"), boton))
        href = boton.get("href") or ""
        if not href and boton.get("url"):
            try:
                href = reverse(boton["url"], args=boton.get("args") or None)
            except NoReverseMatch:
                href = ""
        if href and boton.get("query"):
            href = f"{href}?{boton['query']}"
        return {"href": href, "texto": boton.get("texto", ""), "icono": boton.get("icono", ""),
                "nueva": bool(boton.get("nueva")), "clase": boton.get("clase", "btn-primary"),
                "title": boton.get("title", "")}

    def botones_fijos(self, ctx):
        """Los botones que la lista arma sola con lo que declaró:

          · inicio      `home_url`; si no, el home de su sección (o el volver al padre en una lista «por»).
          · nuevo       `create_url`.
          · especiales  `import_url` (Importar), `crudo_url` (sus datos crudos), `procesados_url` (la lista real que
                        llenan) y `export_url` (Generar dump). Salen después de los `buttons`, en ese orden.

        Lo que no esté declarado, no sale."""
        inicio = []
        if ctx.get("home_href"):                      # lista «por»: volver al padre y a la lista completa
            inicio.append({"href": ctx["home_href"], "texto": ctx.get("home_label", ""), "icono": "arrow-left",
                           "clase": "btn-icon btn-icon--texto"})
            if ctx.get("parent_list_href"):
                inicio.append({"href": ctx["parent_list_href"], "texto": ctx.get("padre_lista_label", ""),
                               "icono": "list-ul", "clase": "btn-icon btn-icon--texto"})
            if ctx.get("lista_href"):
                inicio.append({"href": ctx["lista_href"], "texto": ctx.get("lista_label", ""), "icono": "list-ul",
                               "clase": "btn-icon btn-icon--texto"})
        elif self.home_url or self.section_url:
            inicio.append({"url": self.home_url or self.section_url, "texto": self.section_label, "icono": "house",
                           "clase": "btn-icon btn-icon--texto"})
        especiales = []
        if self.import_url:
            especiales.append({"url": self.import_url, "texto": self.import_label or f"{_('Importar')} {self.label}", "icono": "download",
                               "title": _("Traer de la fuente: por nombre, por id o por páginas")})
        if self.crudo_url:
            especiales.append({"url": self.crudo_url, "texto": self.crudo_label or _("Datos crudos"), "icono": "database",
                               "clase": "btn-cancel", "title": _("Lo descargado de la fuente, antes de procesarlo")})
        if self.procesados_url:
            especiales.append({"url": self.procesados_url, "texto": self.procesados_label or self.label_plural,
                               "icono": "box-arrow-up-right", "clase": "btn-cancel",
                               "title": _("Lo que ya se procesó y es una ficha de verdad")})
        if self.export_url:
            especiales.append({"url": self.export_url, "texto": _("Generar dump"), "icono": "file-earmark-arrow-down",
                               "clase": "btn-cancel", "title": _("Descarga el crudo de esta tabla como .json.gz")})
        return {
            "inicio": inicio,
            "nuevo": [{"href": ctx["create_href"], "icono": "plus-lg",
                       "texto": self.create_label or getattr(self, "title_create", "") or f"{_('Nuevo')} {self.label}"}] if ctx.get("create_href") else [],
            "especiales": especiales,
        }

    def botones_barra(self, ctx):
        """La barra, en orden: inicio · Nuevo · `buttons` de la lista · los especiales. Los que no existen no salen."""
        fijos = self.botones_fijos(ctx)
        barra = [self.boton_extra(b) for b in fijos["inicio"]]
        barra += [self.boton_extra(b) for b in fijos["nuevo"]]
        barra += [self.boton_extra(b) for b in self.buttons]
        barra += [self.boton_extra(b) for b in fijos["especiales"]]
        return [b for b in barra if b["href"]]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Cabeceras: [(texto, es_booleana, prioridad responsive)] — las booleanas se pintan como
        # píldora «Sí»/«No» (col-stat); la prioridad la declara la Data (`priority`) y la lee datatable.js.
        headers = [(lbl, _is_bool_field(self.model, attr), self.data.priority.get(attr, ""), attr not in self.data.no_order)
                   for lbl, attr in self.data.columns]
        ctx.update({
            "headers": headers,
            "data_url": reverse(self.data_route()[0], args=self.data_route()[1] or None),
            "filtros": self.panel(),   # [(param, etiqueta, opciones, actual, modo, grupo)]
            "filtros_excluir": self.panel_excluir(),   # lo mismo para el bloque «Excluir» (param no-<campo>)
            "excluir_activo": any(k.startswith("no-") and v for k, v in self.request.GET.items()),
            "filters_template": self.filters.template if self.filters else "",                    # el mini HTML del panel (pieza aparte)
            "enable_cards": self.enable_cards,
            "cards_default": self.cards_default,
            "con_id": self.con_id,
            "auto_recarga": getattr(self, "auto_recarga", 0),
            "actions": self.data.actions,          # pieza «Acciones»: la Data la enciende o la apaga
        })
        return ctx


class AdminListView(BaseList):
    """La lista de GESTIÓN: [Id + checkbox · foto · datos · menú Acciones], botón «Nuevo», barra
    masiva y «Procesar pendientes». Se declara:

        class PersonAdminListView(BasePerson, AdminListView):
            data_url = "panel:person_data"
            home_url = "panel:people-home"        # vacío → el home de su sección
            create_url = "panel:person_create"    # vacío → sin botón «Nuevo»
            title = _("Lista de personas")
            buttons = [("panel:person-image_list", _("Imágenes"), "images")]   # opcional
    """
    title_attr = "title_list"
    template_name = "admin_panel/list.html"
    con_id = True
    # Lo que declara CADA lista: a dónde vuelve y dónde se da de alta.
    home_url = ""         # ruta del botón de INICIO («panel:otaku-home»); vacío = el home de su sección
    create_url = ""       # ruta del formulario de alta → botón «Nuevo»; vacío = sin botón
    create_label = ""     # el TEXTO del botón de alta; vacío = «Nuevo {label}» (útil cuando el label no cuadra con «Nuevo»)
    import_label = ""     # el TEXTO del botón de importar; vacío = «Importar {label}»
    # Botones EXTRA, en orden, cada uno (ruta, texto, icono de Bootstrap sin «bi-»):
    #   buttons = [("panel:anime-image_list", _("Imágenes"), "images"), ("panel:manga_list", _("Mangas"), "list")]
    # La forma larga, para rutas con argumentos o enlaces externos:
    #   {"url": "panel:anime_by", "args": ["genero", 3], "query": "orden=az", "texto": _("Acción"), "icono": "tags"}
    #   {"href": "https://…", "texto": "MAL", "icono": "box-arrow-up-right", "nueva": True}
    buttons = ()
    bulk_actions = None   # None = automático (activar/desactivar si hay is_active; eliminar si la Data no es de solo lectura); [] = sin selector
    bulk_delete = False   # True: ofrece «Eliminar seleccionadas» aunque la entidad sea de solo lectura (logs, tareas)
    process_url = ""      # tablas de importación: ruta del botón «Procesar pendientes»
    import_url = ""       # tablas de importación: ruta del LANZADOR del tipo → botón «Importar»
    export_url = ""       # tablas de importación: ruta del EXPORTADOR → botón «Generar dump»
    crudo_url = ""        # lista REAL → su lista de DATOS CRUDOS (de dónde salió); vacío = sin botón
    crudo_label = ""      # el texto del botón («Datos · Creador (VNDB)»); vacío = «Datos crudos»
    procesados_url = ""   # lista de DATOS → la lista REAL que llenan; también es a dónde deja «Procesar pendientes»
    procesados_label = "" # el texto del botón («Creadores»); vacío = el plural de la entidad

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "create_href": reverse(self.create_url) if self.create_url else "",
            # «Procesar pendientes»: es un POST, así que va aparte de la barra. Vacío = ni se pinta.
            "process_href": reverse(self.process_url) if self.process_url else "",
            "process_destino": reverse(self.procesados_url) if self.procesados_url else "",   # a dónde deja al terminar
            "type_tabs": type_tabs(self),
            "tipo_actual": (getattr(self, "kwargs", None) or {}).get("tipo", ""),
            "valor_actual": str((getattr(self, "kwargs", None) or {}).get("pk", "")) if (getattr(self, "kwargs", None) or {}).get("tipo") else "",
            "bulk_actions": self._bulk_actions(),
            "bulk_url": reverse("panel:bulk", args=[self.model._meta.app_label, self.model._meta.model_name]),
        })
        # La barra, ya con todas las rutas resueltas: inicio · Nuevo · `buttons` · especiales.
        ctx["botones"] = self.botones_barra(ctx)
        return ctx

    def _bulk_actions(self):
        """[(valor, etiqueta)] de la barra masiva: LAS MISMAS acciones rápidas del menú de fila
        (activar/desactivar, +18, y en usuarios staff/superusuario solo para superusuarios), más
        eliminar si la entidad no es de solo lectura (o lo pide con `bulk_delete`)."""
        if self.bulk_actions is not None:
            return list(self.bulk_actions)
        solo_lectura = self.data.read_only   # la Data manda: sin acciones de fila ni borrado masivo
        es_usuario = self.model is get_user_model()
        superuser = getattr(getattr(self, "request", None), "user", None) is not None and self.request.user.is_superuser
        acciones = []
        if not solo_lectura and not (es_usuario and not superuser):
            campos = [f for f in ("is_active", "explicit") if _model_has_field(self.model, f)]
            if es_usuario:
                campos += [f for f in ("is_staff", "is_superuser") if _model_has_field(self.model, f)]
            for f in campos:
                encender, apagar = TOGGLE_META[f][0], TOGGLE_META[f][1]
                acciones += [(f"set:{f}:1", f"{encender} · seleccionadas"), (f"set:{f}:0", f"{apagar} · seleccionadas")]
            acciones.append(("eliminar", _("Eliminar seleccionadas")))
        elif self.bulk_delete:
            acciones.append(("eliminar", _("Eliminar seleccionadas")))
        if _model_has_field(self.model, "image_url") and _model_has_field(self.model, "image_downloaded"):
            acciones.insert(0, ("descargar-imagenes", _("Descargar imágenes pendientes (URL → archivo local)")))
        if _model_has_field(self.model, "image") and getattr(settings, "USE_R2", False):
            acciones.insert(0, ("subir-nube", _("Subir a la nube (R2) las imágenes descargadas")))
        acciones = list(getattr(self, "extra_bulk_actions", ())) + acciones
        return acciones


class PublicListView(BaseList):
    """La lista PÚBLICA (catálogo): [foto + nombre · Añadir / Quitar de mi colección], sin candado,
    sin Id ni masivo, tarjetas por defecto. Su Data es una PublicDataView (solo activos). Se declara:

        class PersonListView(BasePerson, PublicListView):
            data_url = "personas:people-catalog-data"
            title = _("Personas"); subtitle = _("Actores, directores…"); icon = "bi-people"
            section = "personas"                     # resalta la sección en el nav público
            home_url = "personas:home"; home_label = _("personas")   # miga
    """
    template_name = "public/list.html"
    staff_only = False
    enable_cards = True
    cards_default = True
    section = ""          # active_section del nav público
    subtitle = ""
    icon = ""             # clase Bootstrap (bi-…) del encabezado
    home_url = ""         # ruta del HOME de la sección (miga)
    home_label = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "active_section": self.section,
            "subtitle": self.subtitle,
            "icon": self.icon,
            "home_url": self.home_url,
            "home_label": self.home_label,
        })
        return ctx


class BaseAdminDetailView(BasePage, DetailView):
    """La FICHA DE GESTIÓN, hermana de BasePublicDetailView y con el MISMO HTML por entidad
    (`<app>/detail/<modelo>.html` sobre detail/base_detail.html): aquí con los botones Editar / Activar / Borrar
    y la pestaña «Ficha técnica». La vista SIEMPRE dice qué HTML entrega (como form_template en los formularios):
    el suyo, o el cuadro genérico admin_panel/detail.html con las filas de `detail_fields`. Se declara:

        class MovieAdminDetailView(BaseMovie, BaseAdminDetailView):
            template_name = "movies/detail/movie.html"
            update_url = "panel:movie_update"; delete_url = …; toggle_url = …; list_url = …
            by_url = "panel:movie_by"
            tabs = [("reparto", _("Reparto"), "panel:movie-cast_by", "pelicula"), …]
    """
    title_attr = "title_detail"
    template_name = ""    # SIEMPRE explícito en la vista: su HTML sobre el cuadro, o "admin_panel/detail.html" (el genérico)
    page_template = "admin_panel/base_admin.html"
    detail_fields = []    # [(etiqueta, atributo)] filas del cuadro genérico
    list_url = ""         # miga
    update_url = ""       # vacío → sin «Editar»
    delete_url = ""       # vacío → sin «Borrar»
    toggle_url = ""       # vacío → sin Activar / Desactivar
    by_url = ""          # ruta de las listas «por» de gestión (los enlaces de la ficha: género → «Películas de X»)
    reprocesar = None     # fichas de DATOS CRUDOS: callable(obj) que vuelve a procesar ESA fila → botón «Reprocesar» (POST accion=reprocesar)

    def acciones_extra(self, obj):
        """Botones EXTRA de la ficha, junto a Editar / Borrar: [{"url", "label", "icon"}]. Vacío por defecto; una
        vista lo pisa para ofrecer lo suyo (p. ej. «Añadir ficha MAL» en la persona)."""
        return []

    def post(self, request, *args, **kwargs):
        """Único POST de la ficha: «Reprocesar» una fila de datos crudos (si la vista declara `reprocesar`)."""
        self.object = self.get_object()
        fn = type(self).__dict__.get("reprocesar") or getattr(type(self), "reprocesar", None)
        # La acción viene en el cuerpo (botón de la ficha) o en la query (acción «Procesar» de la fila de la
        # lista, que postea a esta misma URL con ?accion=reprocesar).
        accion = request.POST.get("accion") or request.GET.get("accion")
        if accion != "reprocesar" or not fn:
            return redirect(request.path)
        try:
            resultado = fn(self.object)
        except Exception as exc:  # noqa: BLE001 — el error se muestra, no tumba la ficha
            messages.error(request, _("No se pudo reprocesar: %(e)s") % {"e": exc})
        else:
            if resultado is None:
                messages.warning(request, _("Reprocesado sin resultado (mira el log)."))
            else:
                messages.success(request, _("Reprocesado: %(r)s") % {"r": resultado})
        return redirect(request.path)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        tabs, tab_url = self.tabs_de(obj)
        ctx.update({
            "page_title": str(obj),
            "list_url": self.list_url, "update_url": self.update_url, "delete_url": self.delete_url,
            "can_update": bool(self.update_url), "can_delete": bool(self.delete_url),
            "toggle_actions": self._toggle_actions(),
            "poster": resolve_cover(obj) or getattr(obj, "avatar", None),   # la imagen; una categoría sin imagen, su avatar
            "facts": [{"label": lbl, "value": _resolve(obj, attr)} for lbl, attr in self.detail_fields],
            "tabs": tabs, "tab_url": tab_url, "by_url": self.by_url,
            "can_reprocess": bool(getattr(type(self), "reprocesar", None)),
            "extra_actions": self.acciones_extra(obj),
            "post_actions": self.acciones_imagen(obj),
        })
        return ctx

    def acciones_imagen(self, obj):
        """Ficha de una fila de IMAGEN: «Descargar» / «Subir a la nube» según su estado ([{"url", "label", "icon"}], POST)."""
        from core.shared.models.abstract import ModelBaseImage
        if not isinstance(obj, ModelBaseImage):
            return []
        from core.shared.tasks.images import acciones_fila
        out = []
        for accion, etiqueta, icono in acciones_fila(obj):
            try:
                url = reverse(f"{getattr(self, 'namespace', '') or NAMESPACE}:{self.entity}_image-action", args=[obj.pk, accion])
            except NoReverseMatch:
                continue
            out.append({"url": url, "label": etiqueta, "icon": icono})
        return out

    def _toggle_actions(self):
        """Acciones rápidas (is_active / explicit) de los botones."""
        fields = [f for f in ("is_active", "explicit") if _model_has_field(self.model, f)]
        if not fields or not self.toggle_url:
            return []
        items = []
        for f in fields:
            on, off, icon, confirm = TOGGLE_META[f]
            items.append({
                "url": reverse(self.toggle_url, args=[self.object.pk, f]),
                "label": off if bool(getattr(self.object, f, False)) else on,
                "icon": icon, "confirm": confirm,
            })
        return items


def type_tabs(vista):
    """Botones de tipo de una lista: UNO por entrada CHOICE del mapa `filter_config` de su Data (título = verbose_name del
    campo), cada uno con «Todos» + un link por valor a `panel:<entidad>_by/<tipo>/<valor>`; marca el activo."""
    try:
        data = vista.data()
    except Exception:  # noqa: BLE001
        return []
    fc = getattr(data, "filter_config", None) or {}
    ns = getattr(vista, "namespace", None) or NAMESPACE
    ent = vista.entity
    tipo_actual = (getattr(vista, "kwargs", None) or {}).get("tipo", "")
    valor_actual = str((getattr(vista, "kwargs", None) or {}).get("pk", ""))
    grupos = []
    for tipo, c in fc.items():          # UN botón por entrada choice (Temporada, Clasificación…), no todo junto
        pares = _entry_choices(data.model, c)
        if pares is None:
            continue
        f = _campo(data.model, c[0]) if "." not in c[0] else None
        titulo = str(getattr(f, "verbose_name", "") or tipo).capitalize()
        tabs = []
        try:
            lista = reverse(f"{ns}:{ent}_list")
        except NoReverseMatch:
            lista = ""
        marcados = [v for v in (getattr(getattr(vista, "request", None), "GET", {}).get(c[0], "") or "").split(",") if v]
        for valor, etiqueta in pares:
            tabs.append({"label": str(etiqueta), "valor": str(valor), "href": reverse(f"{ns}:{ent}_by", args=[tipo, valor]),
                         "on": (tipo == tipo_actual and str(valor) == valor_actual) or str(valor) in marcados})
        grupos.append({"label": titulo, "tipo": tipo, "campo": c[0], "lista": lista, "tabs": tabs})
    return grupos




class BaseSoftDelete(BaseDelete):
    """BORRADO LÓGICO: la misma pantalla de confirmación que BaseDelete, pero la fila NO se elimina: queda `is_active=False`
    (mensajes de contacto, cursores de lote, actividad de usuario…). Sigue en la lista con el filtro «Activo: No»."""

    def form_valid(self, form):
        obj = self.object
        obj.is_active = False
        obj.save(update_fields=["is_active"])
        audit(self.request.user, "desactivó", obj)
        msg = self.success_message or _("%(label)s «%(obj)s» desactivado.")
        messages.success(self.request, msg % {"label": self.label.capitalize(), "obj": str(obj)})
        return redirect(self.get_success_url())


class BasePublicDetailView(BasePage, DetailView):
    """La FICHA PÚBLICA, hermana de BaseAdminDetailView y con el MISMO HTML por entidad (`<app>/detail/<modelo>.html`
    sobre detail/base_detail.html): aquí sin botones de gestión y con la barra de colección. Vive en
    /<pk>/<slug>/ (sin slug o con slug viejo → redirect permanente a la canónica), solo activos, y el fondo
    es el de la clase (la imagen del objeto va en el póster). Se declara:

        class MovieDetailView(BaseMovie, BasePublicDetailView):
            template_name = "movies/detail/movie.html"
            list_url = "movies:movies-catalog"; by_url = "movies:movies-by"; section = "peliculas"; collect_kind = "movie"
            tabs = [("reparto", _("Reparto"), "movies:cast-by", "pelicula"), …]
    """
    staff_only = False
    page_template = "base.html"
    list_url = ""         # la lista completa (miga)
    by_url = ""          # ruta de las listas «por» públicas de la entidad (enlaces de la ficha)
    section = ""          # pestaña del nav público
    collect_kind = ""     # barra «Añadir a mi colección» bajo el póster ("" = sin barra)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True) if _model_has_field(self.model, "is_active") else qs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        slug = getattr(self.object, "slug", "") or ""
        if slug and kwargs.get("slug") != slug:
            m = request.resolver_match
            return redirect(reverse(f"{m.namespace}:{m.url_name}", args=[self.object.pk, slug]), permanent=True)
        return self.render_to_response(self.get_context_data(object=self.object))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tabs, tab_url = self.tabs_de(self.object)
        ctx.update({
            "page_title": str(self.object),
            "poster": resolve_cover(self.object),   # el fondo es el de la CLASE (BasePage); la imagen va en el póster
            "active_section": self.section,
            "SECCION_NAV": [],   # la ficha navega con su miga, no con el nav de sección
            "list_url": self.list_url,
            "by_url": self.by_url,
            "collect_kind": self.collect_kind,
            "tabs": tabs, "tab_url": tab_url,
        })
        return ctx


# ============================================================ la DATA (endpoint JSON de DataTables), estilo Poseidón
# La DATA (endpoint JSON de DataTables), estilo Poseidón: cada Data escribe su `get()` y se lee de un vistazo.
#
#     class MovieDataView(BaseMovieContext, AdminDataView):
#         filters = MovieFilters
#         columns = [(_("Título"), "ficha"), (_("Tipo"), "movie_type"), (_("Año"), "release_year"), (_("Activo"), "is_active")]
#
#         def get(self, request, tipo=None, pk=None):
#             p = self.params(request)
#             qs = self.apply_filters(self.by(Movie.objects.select_related("movie_type")))   # mapa «por» + panel lateral
#             total = qs.count()
#             qs = search_words(Movie, qs, p.search, ["title", "titles__title"])
#             filtrado = qs.count()
#             qs = qs.order_by(*p.ordering(self.columns, {"ficha": "title"}))[p.start:p.start + p.length]
#             filas = []
#             for obj in qs:
#                 filas.append({"id": obj.pk,
#                               "c0": cell_cover(self.detail_url(obj), obj.cover_url, obj.title, meta_line(obj)),
#                               "c1": celda(obj, "movie_type"), "c2": cell(obj, "release_year"), "c3": cell(obj, "is_active"),
#                               "acciones": self.row_actions(obj, request),
#                               "card_title": obj.title, "card_image": obj.cover_url, "card_sub": str(obj.release_year or "")})
#             return self.response(p, total, filtrado, filas)
#
# Aquí solo viven las utilidades que TODAS repiten igual (leer los parámetros de DataTables, ordenar por columna,
# pintar una celda, la respuesta) y el menú de acciones de gestión / el botón de colección público. Columnas, filtros
# (`filters`, apps/<app>/views/v2_filters.py), mapa «por» (`filter_config`, en Base<M>By) y fondo se controlan por modelo.
# `columns = [(cabecera, atributo)]` lo lee también la List para las cabeceras; `priority` / `no_order` son perillas de
# DataTables (responsive / columnas sin orden).

class DataView(ByMixin, View):
    """Motor mínimo: candado, parámetros, respuesta. Lo demás lo escribe cada Data en su `get()`."""
    model = None
    entity = ""
    namespace = NAMESPACE
    staff_only = True
    login_only = False
    columns = []          # [(cabecera, atributo)]: cabeceras de la List; `atributo` es la clave de orden
    filters = None        # panel lateral (v3_filters.py)
    priority = {}         # responsive: {"ficha": 1}
    no_order = ()         # columnas sin orden
    actions = True        # columna «Acciones»
    read_only = False     # logs: el menú solo ofrece «Ver»
    page_size = 15

    def dispatch(self, request, *args, **kwargs):
        if (self.staff_only or self.login_only) and not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("users:login"))
        if self.staff_only and not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def params(self, request):
        return Params(request, self.page_size)

    def query(self, request, qs, search_fields=(), order_map=None, default=()):
        """Lo que TODA Data repite: parámetros de DataTables, mapa «por», panel lateral, búsqueda, orden y página.
        Devuelve (p, total, filtrado, objetos); la Data solo arma sus filas. Lo público además deja solo activos y
        marca los que ya están en mi colección."""
        p = self.params(request)
        qs = self.apply_filters(self.by(self.scope(qs)))
        total = qs.count()
        qs = search_words(self.model, qs, p.search, list(search_fields))
        filtrado = qs.count()
        qs = qs.order_by(*self.ordering(p, order_map or {}, tuple(default)))[p.start:p.start + p.length]
        objetos = list(qs)
        self.prepare(request, objetos)
        return p, total, filtrado, objetos

    def scope(self, qs):
        """Gancho: el universo de la Data (lo público lo acota a activos)."""
        return qs

    def prepare(self, request, objetos):
        """Gancho: lo que hay que saber UNA vez por página antes de armar las filas."""

    def ordering(self, p, order_map=None, defecto=("pk",)):
        return p.ordering(self.columns, order_map, defecto, model=self.model)

    def response(self, p, total, filtrado, filas):
        return JsonResponse({"draw": p.draw, "recordsTotal": total, "recordsFiltered": filtrado, "data": filas})

    def detail_url(self, obj):
        return None

    def row_actions(self, obj, request):
        return ""


class AdminDataView(DataView):
    """Gestión: la ficha de gestión y el menú de fila Ver / Editar / extras / activar… / Borrar."""
    staff_only = True

    def _rev(self, obj, action):
        try:
            return reverse(f"{self.namespace}:{self.entity}_{action}", args=[obj.pk])
        except NoReverseMatch:
            return None

    def detail_url(self, obj):
        return self._rev(obj, "detail")

    def link_by(self, obj, attr):
        """Celda de una FK que es un tipo del mapa «por»: enlaza a su lista acotada («Chile» → Personas de Chile)."""
        tipo = next((t for t, c in self.filter_config.items() if c[0] == attr), None)
        fk = getattr(obj, f"{attr}_id", None) if tipo else None
        texto = cell(obj, attr)
        valor = fk or (getattr(obj, attr, None) if tipo else None)          # padre (id) o valor del choice
        if tipo and valor and texto and not texto.startswith("<"):
            try:
                return link(reverse(f"{self.namespace}:{self.entity}_by", args=[tipo, valor]), texto)
            except NoReverseMatch:
                pass
        return texto

    def image_row_actions(self, obj):
        """Menú de la fila de una IMAGEN: las mismas acciones que su ficha (POST). `en_nube` viene anotado por la Data."""
        from core.shared.models.abstract import ModelBaseImage
        if not isinstance(obj, ModelBaseImage):
            return ""
        from core.shared.tasks.images import acciones_fila
        html = ""
        for accion, etiqueta, icono in acciones_fila(obj, en_nube=getattr(obj, "en_nube", None)):
            try:
                url = reverse(f"{self.namespace}:{self.entity}_image-action", args=[obj.pk, accion])
            except NoReverseMatch:
                continue
            html += f'<a role="menuitem" class="js-post" href="{url}"><i class="bi bi-{icono} ic"></i> {etiqueta}</a>'
        return html

    def extra_row_actions(self, obj, request):
        """Enlaces EXTRA del menú de la fila (lista de strings HTML): «Resetear contraseña», «Reprocesar»…"""
        return []

    def _reprocesa(self):
        """¿La FICHA de esta entidad sabe reprocesar una fila? Se le pregunta a la vista de detalle (la que
        declara `reprocesar`), así ninguna Data tiene que repetir el dato. Se resuelve una vez por petición."""
        if not hasattr(self, "_reprocesa_cache"):
            vista = None
            try:
                url = reverse(f"{self.namespace}:{self.entity}_detail", args=[1])
                vista = getattr(resolve(url).func, "view_class", None)
            except (NoReverseMatch, Resolver404):
                pass
            self._reprocesa_cache = bool(getattr(vista, "reprocesar", None))
        return self._reprocesa_cache

    def procesar_action(self, obj, detail):
        """Acción «Procesar» de la fila: postea a la ficha con ?accion=reprocesar, que es el mismo botón
        «Reprocesar» de ahí. Se puede repetir las veces que haga falta (no mira `data_processed`)."""
        if not detail or not self._reprocesa():
            return ""
        return (f'<a role="menuitem" class="js-post" href="{detail}?accion=reprocesar">'
                f'<i class="bi bi-arrow-repeat ic"></i> Procesar</a>')

    def _toggle_fields(self, user):
        es_usuario = self.model is get_user_model()
        if es_usuario and not user.is_superuser:
            return []
        fields = [f for f in ("is_active", "explicit") if _model_has_field(self.model, f)]
        if es_usuario:
            fields += [f for f in ("is_staff", "is_superuser") if _model_has_field(self.model, f)]
        if fields:
            try:
                reverse(f"{self.namespace}:{self.entity}_toggle", args=[0, "is_active"])
            except NoReverseMatch:
                return []
        return fields

    def row_actions(self, obj, request):
        """Menú Ver / Editar / extras / activar… / Borrar."""
        if not self.actions:
            return ""
        if not hasattr(self, "_toggles"):
            self._toggles = [] if self.read_only else self._toggle_fields(request.user)
        es_usuario = self.model is get_user_model()
        detail = self._rev(obj, "detail")
        update = None if self.read_only else self._rev(obj, "update")
        yo_mismo = es_usuario and obj.pk == request.user.pk
        delete = None if (self.read_only or yo_mismo) else self._rev(obj, "delete")
        name = escape(str(obj))
        toggles = ""
        for f in ([] if yo_mismo else self._toggles):
            on, off, icon, confirm = TOGGLE_META[f]
            lbl = off if bool(getattr(obj, f, False)) else on
            url = reverse(f"{self.namespace}:{self.entity}_toggle", args=[obj.pk, f])
            conf = f' data-confirm="¿{escape(lbl)} «{name}»?"' if confirm else ""
            toggles += f'<a role="menuitem" class="js-post" href="{url}"{conf}><i class="bi bi-{icon} ic"></i> {lbl}</a>'
        ver = f'<a role="menuitem" href="{detail}"><i class="bi bi-eye ic"></i> Ver</a>' if detail else ""
        editar = f'<a role="menuitem" href="{update}"><i class="bi bi-pencil ic"></i> Editar</a>' if update else ""
        borrar = (f'<a role="menuitem" class="row-menu__danger js-delete" href="{delete}" data-name="{name}">'
                  f'<i class="bi bi-trash ic"></i> Borrar</a>') if delete else ""
        procesar = self.procesar_action(obj, detail)   # datos crudos: «Procesar», justo después de «Editar»
        imagen = self.image_row_actions(obj)            # filas de imagen: «Descargar» / «Subir a la nube»
        items = f'{ver}{editar}{procesar}{imagen}{"".join(self.extra_row_actions(obj, request))}{toggles}{borrar}'
        if not items:
            return ""
        return ('<div class="row-menu"><button type="button" class="row-menu__btn" aria-haspopup="true" aria-expanded="false">'
                '<span>Acciones</span><span class="row-menu__caret">▾</span></button>'
                f'<div class="row-menu__list" role="menu">{items}</div></div>')


class PublicDataView(DataView):
    """Catálogo público: solo activos, la ficha pública (`detail_url`) y el botón Añadir / En mi colección."""
    staff_only = False
    page_size = 30
    detail_url_name = ""      # ruta de la ficha pública (url_detail la resuelve con pk + slug)

    def active_only(self, qs):
        return qs.filter(is_active=True) if _model_has_field(self.model, "is_active") else qs

    def scope(self, qs):
        return self.active_only(qs)

    def prepare(self, request, objetos):
        self.mark_mine(request, objetos)

    def detail_url(self, obj):
        return url_detail(self.detail_url_name, obj) if self.detail_url_name else None

    def mark_mine(self, request, objetos):
        """Una consulta por página: cuáles de estos objetos ya están en MI colección ({content_id: pk de la fila})."""
        from apps.collections.models import ModelBaseCollection
        self._tabla = ModelBaseCollection.de_contenido(self.model)
        self._mios = {}
        if self._tabla is not None and request.user.is_authenticated and objetos:
            self._mios = dict(self._tabla.objects.filter(user=request.user, content__in=objetos).values_list("content_id", "pk"))

    def row_actions(self, obj, request, titulo=None):
        """«Añadir» o «En mi colección» (quitar), sin entrar a la ficha. Antes, `marcar_mios(request, objetos)`."""
        from django.utils.translation import gettext as _t
        if not self.actions or not request.user.is_authenticated:
            return ""
        if not hasattr(self, "_tabla"):
            self.mark_mine(request, [obj])
        tabla = self._tabla
        if tabla is None:
            return ""
        mio = self._mios.get(obj.pk)
        nombre = escape(titulo if titulo is not None else str(obj))
        if mio:
            return (f'<button type="button" class="cat-btn cat-btn--ok js-remove-col" data-tipo="{tabla.medio()}" '
                    f'data-pk="{mio}" data-name="{nombre}" title="{_t("Quitar de mi colección")}">'
                    f'<i class="bi bi-check-lg"></i> {_t("En mi colección")}</button>')
        return (f'<button type="button" class="cat-btn js-add-col" data-kind="{tabla.medio()}" data-id="{obj.pk}" '
                f'title="{_t("Añadir a mi colección")}"><i class="bi bi-plus-lg"></i> {_t("Añadir")}</button>')


BY_REGISTRY = {}   # modelo → (ruta de la lista pública «por», {campo: tipo}); lo llenan las PublicListByView


def url_by(modelo, campo, padre):
    """URL de la lista pública «por» de `modelo` acotada por `campo` (Anime, "genres", el género →
    «Animes del género X»): `<tipo>/<pk>/<slug>/` si el padre tiene slug. `padre` es el objeto (o su pk).
    "" si ninguna PublicListByView la declara."""
    reg = BY_REGISTRY.get(modelo._meta.label_lower)
    if not reg or campo not in reg[1]:
        return ""
    return url_by_route(reg[0], reg[1][campo], padre)


def url_by_route(ruta, tipo, padre):
    """URL de una lista «por» dada su ruta y tipo: con el slug del padre si lo tiene."""
    pk = getattr(padre, "pk", padre)
    slug = getattr(padre, "slug", "") or ""
    try:
        return reverse(ruta, args=[tipo, pk, slug]) if slug else reverse(ruta, args=[tipo, pk])
    except NoReverseMatch:
        try:
            return reverse(ruta, args=[tipo, pk])
        except NoReverseMatch:
            return ""


class BaseListContext(BaseList):
    """La lista ACOTADA A UN PADRE que llega por la URL («Películas del género Acción», «Reparto de X»,
    «Personas de Chile»), a lo Poseidón: una clase por modelo y lado, ruta `…/por/<tipo>/<pk>/`, y el
    MAPA `filter_config` del mixin `_BaseXBy` (compartido con la Data) diciendo por tipo el título y el fondo. Aquí se
    pinta: título con el padre, fondo del tipo (si su imagen falta, el de la lista), miga y botones
    («← padre», «lista del padre», «lista completa»), y el panel sin el campo fijado. Tipo desconocido o
    id inexistente → 404 (la Data también). Se declara:

        class PersonByListView(BasePersonContext, PublicListByView):
            data_url = "personas:people-by-data"; by_url = "personas:people-by"; full_list_url = "personas:people-catalog"
            parent_urls = {"voces-anime": "otaku:anime-detail"}   # ficha del padre (solo si la hay)
    """
    filter_config = {}            # el mapa del mixin _BaseXBy: tipo → (campo | "app.Modelo", título, fondo)
    by_url = ""        # nombre de la ruta de ESTA lista (url_by desde las fichas; miga)
    full_list_url = ""      # la lista completa (botón y miga)
    parent_urls = {}     # tipo → ruta de la ficha del padre (público); gestión la deriva de la entidad

    # ¿La página hija conserva la barra de sección? Por defecto NO: navega con sus migas, y así no compiten dos
    # navegaciones. Poniéndola a True se mantiene, con su pastilla marcada (hay que tener el nombre de la ruta
    # en el conjunto de esa pastilla); útil cuando se llega desde un catálogo y perderla desorienta.
    keep_nav = False

    def by_type(self):
        return self.kwargs.get("tipo", "")

    def cfg(self):
        c = self.filter_config.get(self.by_type())
        if not c:
            raise Http404(_("El filtro de tipo «%(tipo)s» no es válido para %(que)s.") % {"tipo": self.by_type(), "que": self.label_plural})
        return c

    def data_url_args(self):
        return [self.by_type(), self.kwargs["pk"]]

    @cached_property
    def data_obj(self):
        """Una instancia de la Data con esta petición: sabe quién es el padre."""
        d = self.data(); d.request = self.request; d.kwargs = self.kwargs
        return d

    @cached_property
    def filters(self):
        return self.data_obj.active_filters()

    def panel(self):
        if not self.filters:
            return []
        d = self.data_obj
        nav = nav_fields(d)
        return [f for f in self.filters.panel(self.model, self.request.GET, padre=d.parent(), sin=d.fixed_field()) if f[0] not in nav]

    def panel_excluir(self):
        if not self.filters:
            return []
        d = self.data_obj
        nav = nav_fields(d)
        return [f for f in self.filters.panel_excluir(self.model, self.request.GET, padre=d.parent(), sin=d.fixed_field())
                if f[0][len("no-"):] not in nav]

    def parent_href(self, padre):
        """URL de la ficha del padre («← Chile»); "" si no la hay."""
        ruta = self.parent_urls.get(self.by_type(), "")
        return url_detail(ruta, padre) if ruta else ""

    def parent_list_href(self, padre):
        """URL de la lista del padre («Países», como en Poseidón); "" si no la hay."""
        return ""

    def get_context_data(self, **kwargs):
        c = self.cfg()
        d = self.data_obj
        if d.is_choice():                           # acotada por un CHOICE del modelo (tipo, estado…)
            valor, etiqueta = d.value(), d.value_label()
            # Fondo por valor del choice. El 3er elemento del mapa lo dice EXPLÍCITO: un dict {valor: clase} (uno por
            # valor: {"VALOR": "bg-<app>-<entidad>-<valor>", …}) o una sola clase para todos los valores. Lo que no esté declarado
            # cae en la fórmula bg-<app>-<entidad>[-<campo>]-<valor> (con UN solo choice en el mapa el campo no se nombra;
            # con varios, todos lo llevan). «unknown» (sin valor) usa el fondo de la entidad.
            choices_del_mapa = [t for t, e in d.filter_config.items() if _entry_choices(self.model, e) is not None]
            rama = "" if len(choices_del_mapa) == 1 else f"{self.by_type()}-"
            declarado = c[2].get(str(valor), "") if isinstance(c[2], dict) else c[2]
            fondo = declarado or (type(self).background_image if valor == SIN_VALOR else f"bg-{self.model._meta.app_label}-{self.entity}-{rama}{str(valor).replace('_', '-').lower()}")
            self.background_fallback = type(self).background_image or self.background_fallback
            self.background_image = fondo
            self.active_entity = f"{self.entity}-{str(valor).replace('_', '-').lower()}"
            ctx = super().get_context_data(**kwargs)
            ctx.update({
                "page_title": str(c[1]).format(valor=etiqueta, padre=etiqueta),
                "subtitle": "",
                "home_href": reverse(self.full_list_url) if self.full_list_url else "",
                "home_label": str(self.label_plural),
                "parent_list_href": "", "padre_lista_label": "",
                "lista_href": reverse(self.full_list_url) if self.full_list_url else "",
                "lista_label": str(self.label_plural),
            })
            if not self.keep_nav:
                ctx["SECCION_NAV"] = []
            return ctx
        padre = d.parent()   # 404 con mensaje si el id no es entero o no existe
        if c[2]:   # el fondo del tipo; si su imagen falta, el de la lista
            self.background_fallback = type(self).background_image or self.background_fallback
            self.background_image = c[2]
        ctx = super().get_context_data(**kwargs)
        modelo_padre = d.parent_model()
        ctx.update({
            "page_title": str(c[1]).format(padre=padre),
            "subtitle": "",
            "home_href": self.parent_href(padre) or (reverse(self.full_list_url) if self.full_list_url else ""),
            "home_label": str(padre).lower() if self.parent_href(padre) else str(self.label_plural),
            "parent_list_href": self.parent_list_href(padre),
            "padre_lista_label": str(modelo_padre._meta.verbose_name_plural),
            "lista_href": reverse(self.full_list_url) if self.full_list_url else "",
            "lista_label": str(self.label_plural),
        })
        if not self.keep_nav:
            ctx["SECCION_NAV"] = []   # página hija: sin nav de sección
        return ctx


def admin_entity(modelo):
    """Slug de entidad de gestión de un modelo (Person → "persona"), leído de las Data del panel."""
    if not hasattr(admin_entity, "_mapa"):
        admin_entity._mapa = {}
        pendientes = list(AdminDataView.__subclasses__())
        while pendientes:
            c = pendientes.pop()
            pendientes += c.__subclasses__()
            if getattr(c, "model", None) is not None and getattr(c, "entity", ""):
                admin_entity._mapa.setdefault(c.model, c.entity)
    return admin_entity._mapa.get(modelo, "")


class AdminListByView(BaseListContext, AdminListView):
    """«Reparto de la película X», «Personas de Chile» en gestión: botones «← padre» (su ficha de
    gestión, `panel:<entidad>_detail`), «lista del padre» y «lista completa»; «Nuevo» llega con el padre
    preseleccionado (?movie=12). Rutas: `<entidad>/por/<str:tipo>/<int:pk>/` y `…/data/`.

        class PersonByAdminListView(BasePersonContext, AdminListByView):
            data_url = "panel:person_data-by"; full_list_url = "panel:person_list"
    """
    def _ruta_padre(self, padre, accion):
        ent = admin_entity(type(padre))
        if not ent:
            return ""
        try:
            return reverse(f"panel:{ent}_{accion}", args=[padre.pk] if accion == "detail" else [])
        except NoReverseMatch:
            return ""

    def parent_href(self, padre):
        return self._ruta_padre(padre, "detail")

    def parent_list_href(self, padre):
        return self._ruta_padre(padre, "list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        campo = self.data_obj.fixed_field()
        if ctx.get("create_href") and campo and "__" not in campo:
            ctx["create_href"] += f"?{campo}={self.kwargs['pk']}"
        return ctx


class PublicListByView(BaseListContext, PublicListView):
    """«Animes del género X», «Reparto de X» en el catálogo: la lista pública acotada a un padre.
    Al declararse registra su ruta para `url_by` (los chips de las fichas)."""
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        modelo = getattr(cls, "model", None)
        if modelo is not None and cls.by_url and cls.filter_config:
            BY_REGISTRY[modelo._meta.label_lower] = (
                cls.by_url, {c[0]: tipo for tipo, c in cls.filter_config.items() if "." not in c[0]})


class BaseSelectView(StaffRequiredMixin, View):
    """Endpoint de BÚSQUEDA para Select2-AJAX: `<entidad>/select/?q=&page=` → JSON
    {results:[{id,text}], pagination:{more}}. Busca en el SERVIDOR (icontains sobre
    search_fields) y pagina de a `page_size` — NUNCA vuelca la tabla al front, así
    una FK/M2M a un modelo con millones de filas se relaciona sin colapsar el navegador.

    Cada entidad tiene su clase EXPLÍCITA junto a su Data, en `apps/<app>/views/admin/v1_data.py`:

        class CountrySelectView(BaseCountry, BaseSelectView):
            search_fields = ['name', 'code']

      · search_fields  → campos de búsqueda por PALABRAS: cada palabra tecleada debe
                         aparecer en algún campo, en cualquier orden («murray bill» da con
                         Bill Murray). Admite relaciones: «titles__title» (títulos sinónimos),
                         «nicknames__nickname» (apodos). Si el modelo tiene `name_esp` y se
                         busca por `name`, se suma solo: «español» y «spanish» dan con el mismo.
      · get_queryset() → filtrar (p. ej. solo activos), ordenar, select_related.
      · option_label(obj) → texto de la opción; por defecto el `display_name` del
                         modelo o `etiqueta_select`: «name (name_esp)» cuando hay traducción.
    OJO: los mixins `_Entidad` ya traen `label`/`label_plural` (texto), por eso
    el gancho se llama `option_label` y no `label`."""
    model = None
    search_fields = ()
    page_size = 20
    ordering = ()         # p. ej. ("name",) — si va vacío manda el Meta.ordering del modelo
    select_related = ()   # relaciones que usa `option_label()` (evita N+1 al pintar)

    def get_queryset(self):
        """Universo donde se busca: solo ACTIVOS cuando el modelo tiene `is_active` (desde el
        front nadie enlaza una persona a un país inactivo; por dentro sí se puede).
        Sobrescribir para acotar más (por tipo, por padre…)."""
        qs = self.model._default_manager.all()
        if _model_has_field(self.model, "is_active"):
            qs = qs.filter(is_active=True)
        if self.select_related:
            qs = qs.select_related(*self.select_related)
        if self.ordering:
            qs = qs.order_by(*self.ordering)
        return qs

    def get_search_fields(self):
        """Campos del icontains. Búsqueda BILINGÜE automática: si el modelo tiene
        `name_esp` y la subclase busca por `name`, se suma (las rutas explícitas ganan)."""
        campos = list(self.search_fields)
        if "name" in campos and "name_esp" not in campos and _model_has_field(self.model, "name_esp"):
            campos.append("name_esp")
        return campos

    def option_label(self, obj):
        """Texto de la opción: el `display_name` del modelo si lo tiene (el mismo que la
        lista del panel); si no, `etiqueta_select` (igual que las opciones preseleccionadas)."""
        return getattr(obj, "display_name", None) or etiqueta_select(obj)

    def search(self, qs, q):
        """Aplica `q` sobre `get_search_fields()` por PALABRAS (ver search_words())."""
        return search_words(self.model, qs, q, self.get_search_fields())

    def get(self, request, *args, **kwargs):
        q = (request.GET.get("q") or "").strip()
        try:
            page = max(1, int(request.GET.get("page") or 1))
        except (TypeError, ValueError):
            page = 1
        qs = self.search(self.get_queryset(), q)
        start = (page - 1) * self.page_size
        rows = list(qs[start:start + self.page_size + 1])   # +1 para saber si hay "more"
        more = len(rows) > self.page_size
        rows = rows[:self.page_size]
        return JsonResponse({
            "results": [{"id": o.pk, "text": self.option_label(o)} for o in rows],
            "pagination": {"more": more},
        })


class BaseLoadFileView(BasePage, FormView):
    """Paso 1 de «cargar un ARCHIVO» (dump de tags, listados…): la vista del FORMULARIO. Un FormView con un
    `FormBaseLoadFile` (valida extensión, peso y contenido); `procesar(form)` devuelve la RUTA del archivo ya
    guardado, la vista la deja en sesión y manda al resumen (`success_url`: una `BaseLoadSummaryView`).

        class VNDBTagsLoadView(BaseLoadFileView):
            form_class = forms.VNDBTagsDumpForm
            template_name = "games/vndb_tags.html"
            title = _("Cargar tags de VNDB")
            active_entity = "load-tags-vndb"          # la misma en las dos vistas: es la clave de sesión
            cancel_url = "panel:games-home"
            success_url = "panel:load-tags-vndb-summary"

            def procesar(self, form):
                return form.ruta_dump()

    Si `procesar` falla (red caída, disco…) se avisa y se vuelve a pintar el formulario.
    """
    page_template = "panel/base.html"
    form_class = None
    cancel_url = ""          # nombre de ruta de «Cancelar»
    success_url = ""         # nombre de ruta de la vista de RESUMEN
    ayuda = ""               # una línea bajo el título: qué carga

    def clave_sesion(self):
        return f"load:{self.active_entity or self.entity}"

    def procesar(self, form):
        """Devuelve la ruta (Path) del archivo ya en disco."""
        raise NotImplementedError

    def form_valid(self, form):
        try:
            ruta = self.procesar(form)
        except Exception as e:  # noqa: BLE001 — red caída, disco lleno…: se informa, no se rompe
            messages.error(self.request, _("No se pudo obtener el archivo: %s") % e)
            return self.form_invalid(form)
        self.request.session[self.clave_sesion()] = str(ruta)
        return redirect(reverse(self.success_url))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"title": self.title, "ayuda": self.ayuda,
                    "cancel_href": reverse(self.cancel_url) if self.cancel_url else ""})
        return ctx


class BaseLoadSummaryView(BasePage, TemplateView):
    """Paso 2 de «cargar un ARCHIVO»: el RESUMEN de lo que va a pasar, y el «Sí, continuar» que lo aplica AQUÍ.
    Lee la ruta que dejó en sesión la `BaseLoadFileView` con la misma `active_entity`; sin ruta (o si el archivo
    ya no está) devuelve al formulario (`load_url`).

        class VNDBTagsSummaryView(BaseLoadSummaryView):
            template_name = "games/vndb_tags_summary.html"
            title = _("Cargar tags de VNDB · resumen")
            active_entity = "load-tags-vndb"
            load_url = "panel:load-tags-vndb"
            cancel_url = "panel:load-tags-vndb"
            success_url = "panel:game-genre_list"

            def resumen(self, ruta): ...      # lo que la plantilla pinta
            def aplicar(self, ruta): ...      # hace el trabajo y deja el mensaje de éxito
    """
    page_template = "panel/base.html"
    load_url = ""            # nombre de ruta del FORMULARIO: la miga, y a dónde volver si el archivo ya no está
    cancel_url = ""          # «No, cancelar»: a dónde se sale sin aplicar; vacío = de vuelta al formulario
    success_url = ""         # nombre de ruta a la que ir tras aplicar

    def clave_sesion(self):
        return f"load:{self.active_entity or self.entity}"

    def ruta(self):
        """La ruta dejada en sesión, si el archivo sigue ahí; si no, None."""
        valor = self.request.session.get(self.clave_sesion(), "")
        ruta = Path(valor) if valor else None
        return ruta if ruta and ruta.exists() else None

    def resumen(self, ruta):
        raise NotImplementedError

    def aplicar(self, ruta):
        raise NotImplementedError

    def sin_archivo(self):
        messages.error(self.request, _("El archivo ya no está; súbelo o descárgalo de nuevo."))
        return redirect(reverse(self.load_url))

    def get(self, request, *args, **kwargs):
        ruta = self.ruta()
        if not ruta:
            return self.sin_archivo()
        try:
            resumen = self.resumen(ruta)
        except Exception as e:  # noqa: BLE001 — archivo corrupto: se informa y se vuelve al formulario
            messages.error(request, _("No se pudo leer el archivo: %s") % e)
            return redirect(reverse(self.load_url))
        return self.render_to_response(self.get_context_data(resumen=resumen, ruta=str(ruta), nombre=ruta.name))

    def post(self, request, *args, **kwargs):
        ruta = self.ruta()
        if not ruta:
            return self.sin_archivo()
        self.aplicar(ruta)
        request.session.pop(self.clave_sesion(), None)
        return redirect(reverse(self.success_url))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        load_href = reverse(self.load_url) if self.load_url else ""
        ctx.update({"title": self.title, "load_href": load_href,
                    "cancel_href": reverse(self.cancel_url) if self.cancel_url else load_href})
        return ctx
