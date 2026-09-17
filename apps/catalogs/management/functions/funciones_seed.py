from datetime import datetime

from django.utils.text import slugify


def paso(stdout, etiqueta, modelo, sembrar):
    """Siembra un catálogo y deja UNA línea: «Países: 249 (249 nuevos)»."""
    antes = modelo.objects.count()
    sembrar()
    despues = modelo.objects.count()
    if stdout:
        stdout.write(f"  {etiqueta}: {despues} ({despues - antes} nuevos)")


def _slug(name):
    """Slug idéntico al que generan los modelos ModelBaseCategory (slugify(name)[:120]).
    Se usa como CLAVE de búsqueda en update_or_create: el slug es el `unique` real
    del modelo (name no lo es), así el seed normaliza en el sitio filas pre-existentes
    con distinto casing/idioma sin colisionar ni romper FKs/M2M."""
    return slugify(name)[:120]


def seed_defaults_calidades(modelo, items):
    for item in items:
        name = item["name"].strip().upper()
        description = item["description"].strip()
        is_active = True

        modelo.objects.update_or_create(
            name=name,
            defaults={
                "description": description,
                "is_active": is_active,
            }
        )

def seed_defaults_formatos(modelo, items):
    # Format tiene flags for_video/for_music/for_image/for_document/for_other
    # (un formato puede aplicar a varios medios). None → False.
    for item in items:
        name = item["name"].strip().upper()

        modelo.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "for_video": bool(item.get("for_video")),
                "for_music": bool(item.get("for_music")),
                "for_image": bool(item.get("for_image")),
                "for_document": bool(item.get("for_document")),
                "for_other": bool(item.get("for_other")),
                "is_active": True,
            }
        )

def seed_defaults_websites(modelo, items):
    for item in items:
        name = item["name"].strip()
        acronym = item["acronym"].strip().upper()
        URL = item["URL"].strip()
        tipo = item.get("type", item.get("kind", "OTHER"))   # STREAMING / DOWNLOAD / STORE / DATABASE / OTHER
        is_active = True

        modelo.objects.update_or_create(
            name=name,
            defaults={
                "acronym": acronym,
                "url": URL,
                "type": tipo,
                "is_active": is_active,
            }
        )

def seed_defaults_countries(modelo, items):
    for item in items:
        name = item["name"].strip().title()
        name_esp = item["name_esp"].strip().title()
        code = item["code"].strip().upper()
        numeric_code = item["numeric_code"]
        is_active = True

        # Artemisa: la clave única real es el slug (derivado de name). Se busca por
        # `name` y el resto va en defaults, para no colisionar con filas pre-existentes.
        modelo.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "name_esp": name_esp,
                "code": code,
                "numeric_code": numeric_code,
                "is_active": is_active,
            }
        )

def seed_defaults_languages(modelo, items):
    for item in items:
        name = item["name"].strip()
        name_esp = item["name_esp"].strip()
        note = item["note"].strip()

        acronym = item["acronym"].strip().upper()
        iso_639_1 = item["iso_639_1"].strip().upper()
        iso_639_2_t = item.get("iso_639_2_t", "").strip().upper()
        is_active = True


        modelo.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "name_esp": name_esp,
                "acronym": acronym,
                "iso_639_1": iso_639_1,
                "iso_639_2_t": iso_639_2_t,
                "description": note,
                "is_active": is_active,
            }
        )

def seed_defaults_ratings(modelo, items):
    for item in items:
        acronym = item["acronym"].strip().upper()
        name = item["name"].strip().title()
        name_esp = item["name_esp"].strip()
        description = item["description"].strip()
        is_active = True

        modelo.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "acronym": acronym,
                "name_esp": name_esp,
                "description": description,
                "is_active": is_active,
            }
        )

def seed_default_companies(modelo, country_model, items):
    for idx, item in enumerate(items, 1):
        company_name = item.get("name")
        inicio = item.get("inicio")
        termino = item.get("termino")
        is_active = True

        country_data = item.get("country")
        country_obj = None

        if country_data:
            if not isinstance(country_data, dict):
                print(f"Error en item #{idx} ({company_name}): country NO es dict, es {type(country_data)} -> {country_data}")
                continue

            country_code = country_data["code"].strip().upper()
            country_numeric_code = country_data["numeric_code"]

            country_obj = country_model.objects.filter(
                code=country_code,
                numeric_code=country_numeric_code
            ).first()

        defaults = {
            "founded_year": inicio,
            "disolved_year": termino,
            "is_active": is_active,
        }

        if country_obj:
            defaults["country"] = country_obj

        modelo.objects.update_or_create(
            name=company_name,
            defaults=defaults
        )

def _fusionar(destino, origen):
    """Mueve TODAS las relaciones M2M inversas de `origen` a `destino` (artistas, álbumes… que apuntaban al
    duplicado) y borra `origen`. Así un género que el importador creó con otro nombre se funde con el del seed."""
    for f in origen._meta.get_fields():
        if f.many_to_many and f.auto_created:
            accessor = f.get_accessor_name()
            campo = f.field.name
            for obj in getattr(origen, accessor).all():
                getattr(obj, campo).add(destino)
    origen.delete()


def _con_id_externo(modelo, item, slug):
    """Si el ítem trae un id externo (deezer_id) y YA hay una fila con ese id bajo otro slug (la creó el
    importador con el nombre de la API), esa fila ES el género: se le ponen los nombres del seed y, si además
    existe la fila del slug sin id, se funde en ella. Devuelve la fila a actualizar o None."""
    for campo in ("deezer_id",):
        valor = item.get(campo)
        if valor is None or campo not in {f.name for f in modelo._meta.fields}:
            continue
        por_id = modelo.objects.filter(**{campo: valor}).first()
        if por_id is None:
            continue
        if por_id.slug != slug:
            por_slug = modelo.objects.filter(slug=slug).first()
            if por_slug is not None and por_slug.pk != por_id.pk:
                _fusionar(por_id, por_slug)
            por_id.slug = slug
        return por_id
    return None


def seed_defaults_names_description(modelo, items, explicit=False):
    """Catálogo por nombre/slug: nombre EN + ES, descripción, id externo si el modelo lo tiene y, con `explicit=True`,
    la marca +18 de cada fila (`item["explicit"]`, False si falta)."""
    campos_modelo = {f.name for f in modelo._meta.fields}
    for item in items:
        name = item["name"].strip()
        name_esp = item["name_esp"].strip()
        description = item.get("description", "").strip()
        defaults = {"name": name, "name_esp": name_esp, "description": description, "is_active": True}
        defaults.update({k: item[k] for k in ("deezer_id",) if k in item and k in campos_modelo})
        if explicit and "explicit" in campos_modelo:
            defaults["explicit"] = bool(item.get("explicit", False))
        fila = _con_id_externo(modelo, item, _slug(name))
        if fila is not None:
            for k, v in defaults.items():
                setattr(fila, k, v)
            fila.save()
            continue
        modelo.objects.update_or_create(slug=_slug(name), defaults=defaults)

# Código de `role_type` en los datos (10, 20…) → valor del choice RoleType.
ROLE_TYPE_CODE = {10: "STAFF", 20: "CAST", 30: "PRODUCTION", 40: "MUSIC", 50: "CHARACTER", 60: "MANGA"}

def seed_defaults_roles(modelo, items):
    for item in items:
        name = item["name"].strip()
        name_esp = item["name_esp"].strip()
        description = item.get("description","").strip()
        is_active = True

        modelo.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "name_esp": name_esp,
                "type": ROLE_TYPE_CODE.get(item["role_type"], ""),
                "description": description,
                "is_active": is_active,
            }
        )

def seed_defaults_vndb(modelo, items):
    for item in items:
        name = item["name"].strip()
        name_esp = item["name_esp"].strip()
        description = item.get("description","").strip()
        vndb_code = item.get("vndb_code", None)
        is_active = True

        modelo.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "name_esp": name_esp,
                "vndb_code": vndb_code,
                "description": description,
                "is_active": is_active,
            }
        )

def seed_default_game_engines(modelo, items):
    for item in items:
        name = item["name"].strip()
        description = item.get("description", "").strip()
        is_active = True

        modelo.objects.update_or_create(
            name=name,
            defaults={
                "description": description,
                "is_active": is_active,
            }
        )

def seed_defaults_names_description_vndb(modelo, items, explicit=False):
    for item in items:
        name = item["name"].strip()
        name_esp = item["name_esp"].strip()
        description = item.get("description", "").strip()
        vndb_code = item.get("code_vndb", "").strip().upper()
        is_active = True

        modelo.objects.update_or_create(
            slug=_slug(name),
            defaults={
                "name": name,
                "name_esp": name_esp,
                "vndb_code": vndb_code,
                "description": description,
                "is_active": is_active
            }
        )

def seed_default_otaku_years(modelo):
    this_year = datetime.now().year
    first_year = 1960
    years_to_insert = range(first_year, this_year+4)
    for y in years_to_insert:
        modelo.objects.update_or_create(year=y)

########################################################################################################    Common
# def seed_defaults_creators(modelo, items):
#     proceso = ('Cargar Motores de Desarrollo Predeterminados')
#     for item in items:
#         name = item['name'].strip()
#         dev_type = item.get('type','').strip()
#         is_active = True
#         # name_slug = slugify(name)

#         modelo.objects.update_or_create(
#             name=name,
#             defaults={
#                 'type': dev_type,
#                 'is_active': is_active,
#             }
#         )