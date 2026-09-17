"""UNA sola puerta de escritura para «persona + su extensión MAL».

`people.Person` es NEUTRA y `otaku.PersonMAL` es la ficha MAL. Para no duplicar
lógica, tanto el procesado del dump de MAL (`mal_dump_process.process_person`) como el formulario del
panel (`PersonMALNewForm.save`) llaman a `upsert_persona_mal(datos, person=…)`.

Regla de convivencia: MAL rellena los campos NEUTROS solo si están vacíos (no
pisa una biografía escrita a mano); los campos MAL son de MAL y se sobreescriben.
Lo que MAL trae pero es de la PERSONA no va a la ficha: `alternate_names` → apodos
(`PersonNickname`) y `website_url` → enlaces (`PersonLink`, fuente «Sitio web»). Solo
se añaden: nunca se borra un apodo o un enlace puesto a mano.
"""
import datetime

from django.db import transaction

from apps.otaku.models import PersonMAL
from apps.people.models import Person, PersonLink, PersonNickname


CAMPOS_MAL = ("url", "given_name", "family_name", "about")


def _lineas(valor):
    """alternate_names llega como lista (MAL) o como texto (formulario) → una por línea."""
    if not valor:
        return ""
    if isinstance(valor, (list, tuple)):
        return "\n".join(str(x).strip() for x in valor if str(x).strip())
    return "\n".join(l.strip() for l in str(valor).splitlines() if l.strip())


def _fecha(valor):
    """birthday de MAL es ISO ("1980-01-21T00:00:00+00:00"); acepta date o None."""
    if not valor:
        return None
    if isinstance(valor, datetime.date):
        return valor
    try:
        return datetime.date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


class MalIdEnUso(ValueError):
    """El MAL id ya está enlazado a OTRA persona."""


@transaction.atomic
def upsert_persona_mal(datos, person=None):
    """Crea/actualiza la persona neutra y su extensión MAL.

    datos: dict con la forma de la ficha de persona de MAL — `mal_id` (obligatorio),
      `name`, `url`, `given_name`, `family_name`, `birthday`, `about`, y los de la
      persona `alternate_names` (→ apodos) y `website_url` (→ enlace). Solo se tocan
      las claves presentes.
    person: persona ya elegida (alta manual sobre una existente). Si no se da, se
      busca por `mal_id`; si tampoco existe, se crea NEUTRA con `name`.
    Devuelve (person, person_mal, persona_creada)."""
    mal_id = int(datos["mal_id"])
    ext = PersonMAL.objects.select_related("person").filter(mal_id=mal_id).first()
    if person is not None and ext is not None and ext.person_id != person.pk:
        raise MalIdEnUso(f"El MAL id {mal_id} ya está enlazado a «{ext.person}».")
    if person is None and ext is not None:
        person = ext.person

    creada = False
    if person is None:
        person = Person(full_name=(datos.get("name") or f"Persona {mal_id}")[:255])
        creada = True
    # --- campos NEUTROS: solo si están vacíos ---
    if not person.biography and datos.get("about"):
        person.biography = datos["about"]
    if not person.birth_date and datos.get("birthday"):
        person.birth_date = _fecha(datos["birthday"])
    person.save()

    # --- extensión MAL: manda MAL ---
    if ext is None:
        ext = PersonMAL.objects.filter(person=person).first() or PersonMAL(person=person)
    ext.mal_id = mal_id
    for campo in CAMPOS_MAL:
        if campo in datos:
            setattr(ext, campo, datos[campo] or "")
    if "is_active" in datos:
        ext.is_active = bool(datos["is_active"])
    ext.save()
    _apodos(person, datos.get("alternate_names"))
    _enlace_web(person, datos.get("website_url"))
    return person, ext, creada


def _apodos(person, valor):
    """`alternate_names` de MAL (lista o texto, uno por línea) → apodos de la persona. Solo añade."""
    for apodo in _lineas(valor).splitlines():
        apodo = apodo.strip()[:100]
        if apodo and apodo.lower() != person.full_name.lower():
            PersonNickname.objects.get_or_create(person=person, nickname=apodo)


def _enlace_web(person, url):
    """`website_url` de MAL → un enlace de la persona con la fuente «Sitio web» (se crea si falta). Solo añade."""
    url = (url or "").strip()
    if not url:
        return
    from apps.catalogs.models import ExternalSource
    fuente = (ExternalSource.objects.filter(acronym__iexact="web").first()
              or ExternalSource.objects.filter(name__iexact="Sitio web").first()
              or ExternalSource.objects.create(name="Sitio web", acronym="web"))
    PersonLink.objects.get_or_create(person=person, source=fuente, url=url)
