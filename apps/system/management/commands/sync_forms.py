"""Sincroniza las plantillas de formulario por entidad (patrón Hades/Poseidon).

El CUADRO vive una sola vez en `templates/admin_panel/form.html` (card, csrf,
botones). Cada entidad puede tener su PARCIAL de campos en
`apps/<app>/templates/<app>/form/<modelo>.html` —cada campo con su HTML, editable a
gusto— y cada vista Create/Update lo DECLARA (`form_template = "<app>/form/<modelo>.html"`);
el cuadro lo incluye. Sin declaración, el cuadro usa su loop genérico.

Este comando recorre TODAS las vistas `<entidad>_create` del panel, y por cada una:

  * la CREA si falta (andamiaje con todos los campos no-booleanos explícitos),
  * si ya existe, REPORTA el desfase: campos del Form que no están en el HTML
    (se dejarían de enviar al guardar) y referencias del HTML a campos que el
    Form ya no tiene.

Uso:
  python manage.py sync_forms                # crea las que falten + reporta desfases
  python manage.py sync_forms --check        # solo reporta, no escribe nada
  python manage.py sync_forms --force        # regenera TODAS (pisa ediciones a mano)
  python manage.py sync_forms otaku music    # limita a esas apps

Los booleanos (is_active, +18…) NO se listan: el cuadro los auto-agrupa abajo.
"""
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.forms.widgets import CheckboxInput
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver


FIELD_RE = re.compile(r"form\.(\w+)")


def _snake(nombre):
    """CamelCase → snake_case respetando siglas: DataVndbGame → data_vndb_game."""
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", nombre)).lower()


def _iter_create_views():
    """Devuelve las view_class de todas las URL `*_create` del proyecto."""
    seen = set()
    out = []

    def rec(patterns):
        for p in patterns:
            if isinstance(p, URLResolver):
                rec(p.url_patterns)
            elif isinstance(p, URLPattern) and (p.name or "").endswith("_create"):
                vc = getattr(p.callback, "view_class", None)
                if vc and vc not in seen:
                    seen.add(vc)
                    out.append(vc)

    rec(get_resolver().url_patterns)
    return out


def _field_block(name, is_file):
    """HTML de un campo, espejo del loop genérico de form.html (clases .field)."""
    preview = ""
    if is_file:
        preview = (
            "\n    {% if form." + name + ".value %}"
            '<div class="img-preview">'
            '<img src="{{ MEDIA_URL }}{{ form.' + name + '.value }}" '
            'alt="{{ form.' + name + '.label }} actual">'
            '<span class="img-preview__tag">actual</span></div>{% endif %}'
        )
    return (
        '    <div class="field">\n'
        '      <label for="{{ form.' + name + '.id_for_label }}">'
        "{{ form." + name + ".label }}"
        "{% if form." + name + ".field.required %} "
        '<span class="req">*</span>{% endif %}</label>' + preview + "\n"
        "      {{ form." + name + " }}\n"
        "      {% for e in form." + name + ".errors %}"
        '<span class="field__err">{{ e }}</span>{% endfor %}\n'
        "      {% if form." + name + ".help_text %}"
        '<span class="field__hint">{{ form.' + name + ".help_text }}</span>{% endif %}\n"
        "    </div>"
    )


def _render_template(model_verbose, fields):
    """fields = [(name, is_file), ...] ya sin booleanos."""
    body = "\n".join(_field_block(n, isf) for n, isf in fields)
    return (
        "{% comment %}Campos de " + model_verbose + " — patrón Poseidon.\n"
        "   PARCIAL que INCLUYE admin_panel/form.html (el cuadro: card, botones, csrf) porque la\n"
        "   vista Create/Update lo declara: form_template = \"…/form/<modelo>.html\".\n"
        "   Edita libremente el orden/HTML de cada campo aquí. Los booleanos se\n"
        "   auto-agrupan abajo, no van en este parcial.\n"
        "   Sincroniza:  python manage.py sync_forms{% endcomment %}\n\n" + body + "\n"
    )


class Command(BaseCommand):
    help = "Crea/sincroniza las plantillas de campos por entidad (patrón Hades/Poseidon)."

    def add_arguments(self, parser):
        parser.add_argument("apps", nargs="*", help="Limitar a estas apps (por app_label).")
        parser.add_argument("--check", action="store_true", help="Solo reportar, no escribir.")
        parser.add_argument("--force", action="store_true", help="Regenerar todas (pisa ediciones).")

    def handle(self, *args, **opts):
        only = set(opts["apps"])
        check, force = opts["check"], opts["force"]
        created = drift = ok = skipped = 0

        for vc in _iter_create_views():
            try:
                view = vc()
                model = view.model
                form_fields = view.get_form_class().base_fields
            except Exception as e:  # pragma: no cover - vista atípica
                self.stderr.write(f"  ! {vc.__name__}: no introspectable ({e})")
                continue

            app_label = model._meta.app_label
            if only and app_label not in only:
                continue
            model_name = _snake(model.__name__)   # CharacterRole → character_role.html (como los módulos Python)

            # Campos que SÍ van en el bloque (todo menos los checkbox/booleanos).
            non_bool = [
                (n, getattr(f.widget, "input_type", "") == "file")
                for n, f in form_fields.items()
                if not isinstance(f.widget, CheckboxInput)
            ]
            expected = {n for n, _ in non_bool}

            path = Path("apps") / app_label / "templates" / app_label / "form" / f"{model_name}.html"
            declarado = getattr(view, "form_template", "")
            if path.exists() and declarado != f"{app_label}/form/{model_name}.html":
                drift += 1
                self.stdout.write(self.style.WARNING(
                    f"  ~ {path.as_posix()} existe pero la entidad no lo declara: "
                    f"pon form_template = \"{app_label}/form/{model_name}.html\" en su vista Create/Update (v4_write.py)"))

            if path.exists() and not force:
                text = re.sub(r"\{#.*?#\}|\{% comment %\}.*?\{% endcomment %\}", "", path.read_text(encoding="utf-8"), flags=re.S)   # sin comentarios
                referenced = set(FIELD_RE.findall(text))
                missing = expected - referenced          # en el Form, faltan en el HTML
                extra = referenced - expected             # en el HTML, ya no en el Form
                if missing or extra:
                    drift += 1
                    self.stdout.write(self.style.WARNING(f"  ~ DESFASE {path.as_posix()}"))
                    if missing:
                        self.stdout.write(f"      faltan en HTML (no se enviarían): {sorted(missing)}")
                    if extra:
                        self.stdout.write(f"      sobran en HTML (ya no existen):    {sorted(extra)}")
                else:
                    ok += 1
                continue

            # No existe (o --force): generar.
            content = _render_template(model._meta.verbose_name, non_bool)
            if check:
                skipped += 1
                self.stdout.write(f"  + (crearía) {path.as_posix()}")
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created += 1
            self.stdout.write(self.style.SUCCESS(
                f"  + {path.as_posix()}  → declara form_template = \"{app_label}/form/{model_name}.html\" en su Create/Update (v4_write.py)"))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"creadas={created}  al_día={ok}  con_desfase={drift}" + (f"  pendientes={skipped}" if check else "")
        ))
