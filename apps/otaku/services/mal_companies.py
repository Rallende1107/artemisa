"""Carga del DUMP de COMPAÑÍAS de MAL (json · json.gz), archivo → `companies.Company` + `otaku.CompanyMAL`.

A diferencia de los dumps de anime, manga, personaje y persona, este NO pasa por una tabla Data: una compañía de MAL
no tiene nada que procesar después. Va directo a la entidad, como los tags de VNDB.

El archivo trae DOS listas: `companies` (estudios, productoras, licenciatarias) y `magazines` (revistas de manga).
De cada registro se usan `mal_id`, `name`, `url` y, si vienen (dump enriquecido), `japanese_name`, `favorites`, `about`,
`links`, `established` e `image_url`. Lo de MAL va a la ficha MAL (siempre se actualiza); lo neutro —año de fundación,
biografía— va a la compañía SOLO si está vacío, y el logo queda como imagen pendiente de descarga. Se ignoran
works_in_mal, roles, loaded, from_index y enriched:

    {"companies": [{"mal_id": 1, "name": "Studio Pierrot",     "url": "https://myanimelist.net/anime/producer/1", …}],
     "magazines": [{"mal_id": 1, "name": "Big Comic Original", "url": "https://myanimelist.net/manga/magazine/1/…", …}]}

OJO: MAL numera compañías y revistas por SEPARADO (los dos de arriba son id 1). La clave es (tipo, mal_id), y el
tipo lo da la LISTA donde viene. También acepta una lista plana con `kind` ("company" / "magazine") y `company_id`.

Cada registro cae en uno de tres casos, por este orden:
  1. ya tiene ficha MAL con ese (tipo, id)               → no se duplica; si la ficha no tenía URL, se le pone
  2. la compañía existe por NOMBRE y no tiene ficha MAL → se le crea la ficha (no se duplica la compañía)
  3. no existe                                          → se crean la compañía y su ficha MAL

Pensado para dumps GRANDES: las consultas van por lotes (nada de traer la tabla entera a memoria) y las altas son
`bulk_create` por lotes, con el slug calculado aquí (bulk_create no pasa por `save()`).
"""
from __future__ import annotations
from collections.abc import Iterable, Iterator

from django.db import transaction
from django.db.models.functions import Lower
from django.utils.text import slugify

from apps.companies.models import Company, CompanyImage
from apps.otaku.models import CompanyMAL
from core.shared.models.choices import MalCompanyKind


LOTE = 1000
Clave = tuple[str, int]                     # (kind, mal_id)
TIPOS_DUMP = {"company": MalCompanyKind.COMPANY, "magazine": MalCompanyKind.MAGAZINE}


def _lotes(items: list, n: int = LOTE) -> Iterator[list]:
    for i in range(0, len(items), n):
        yield items[i:i + n]


LISTAS = {"companies": "company", "magazines": "magazine"}     # clave del archivo → `kind` de cada registro


def _aplanar(registros: Iterable[dict]) -> Iterator[dict]:
    """Registros sueltos: abre el objeto {"companies": […], "magazines": […]} poniéndole a cada uno su `kind`;
    un registro que ya es plano pasa tal cual."""
    for r in registros:
        listas = [k for k in LISTAS if isinstance(r.get(k), list)]
        if not listas:
            yield r
            continue
        for clave in listas:
            for item in r[clave]:
                if isinstance(item, dict):
                    yield {**item, "kind": LISTAS[clave]}


def _clave_nombre_url(registro: dict) -> tuple[Clave | None, str, str]:
    """((kind, mal_id), nombre, url) del registro; (None, "", "") si le falta el id, el nombre o el tipo es otro."""
    try:
        mal_id = int(registro.get("company_id", registro.get("mal_id")))
    except (TypeError, ValueError):
        return None, "", ""
    kind = TIPOS_DUMP.get(str(registro.get("kind") or "company").strip().lower())
    nombre = " ".join(str(registro.get("name") or "").split())[:250]
    if kind is None or not nombre or mal_id < 1:
        return None, "", ""
    return (kind, mal_id), nombre, str(registro.get("url") or "").strip()[:500]


def _limpios(registros: Iterable[dict]) -> tuple[dict[Clave, tuple[str, str, dict]], int, int]:
    """{(kind, mal_id): (nombre, url, registro)} sin repetir la clave (gana el último), descartados y total leído."""
    por_clave, descartados, total = {}, 0, 0
    for r in _aplanar(registros):
        total += 1
        clave, nombre, url = _clave_nombre_url(r)
        if clave is None:
            descartados += 1
            continue
        por_clave[clave] = (nombre, url, r)
    return por_clave, descartados, total


def _ya_con_ficha(claves: list[Clave]) -> set[Clave]:
    """Las (kind, mal_id) que ya tienen ficha, consultando por lotes y por tipo."""
    hay = set()
    for kind in {k for k, _i in claves}:
        ids = [i for k, i in claves if k == kind]
        for lote in _lotes(ids):
            hay |= {(kind, i) for i in CompanyMAL.objects.filter(kind=kind, mal_id__in=lote).values_list("mal_id", flat=True)}
    return hay


def _libres_por_nombre(nombres: set[str]) -> dict[str, int]:
    """{nombre en minúsculas: pk} de las compañías SIN ficha MAL con esos nombres (solo esos, por lotes)."""
    libres = {}
    for lote in _lotes(sorted(nombres)):
        filas = (Company.objects.filter(company_mal__isnull=True).annotate(nombre_min=Lower("name"))
                 .filter(nombre_min__in=lote).order_by("pk").values_list("nombre_min", "pk"))
        for nombre, pk in filas:
            libres.setdefault(nombre, pk)          # si hay dos con el mismo nombre, la más antigua
    return libres


def _plan(por_clave: dict[Clave, tuple[str, str, dict]]) -> tuple[set[Clave], dict[Clave, int], list[Clave]]:
    """(con_ficha, enlazar {clave: company_pk}, crear [clave])."""
    con_ficha = _ya_con_ficha(list(por_clave))
    pendientes = [c for c in por_clave if c not in con_ficha]
    libres = _libres_por_nombre({por_clave[c][0].lower() for c in pendientes})
    enlazar, crear, usados = {}, [], set()
    for clave in pendientes:
        pk = libres.get(por_clave[clave][0].lower())
        if pk is not None and pk not in usados:     # una compañía tiene a lo más UNA ficha MAL
            enlazar[clave] = pk
            usados.add(pk)
        else:
            crear.append(clave)
    return con_ficha, enlazar, crear


def resumen(registros: Iterable[dict]) -> dict:
    """Qué pasaría al aplicar, sin escribir nada."""
    por_clave, descartados, total = _limpios(registros)
    con_ficha, enlazar, crear = _plan(por_clave)
    return {"total": total, "validos": len(por_clave), "sin_datos": descartados,
            "con_url_nueva": len(_fichas_sin_url(por_clave, con_ficha)),
            "repetidos": total - descartados - len(por_clave),
            "ya_estaban": len(con_ficha), "enlazar": len(enlazar), "crear": len(crear),
            "companias": sum(1 for k, _i in por_clave if k == MalCompanyKind.COMPANY),
            "revistas": sum(1 for k, _i in por_clave if k == MalCompanyKind.MAGAZINE),
            "con_logo": sum(1 for *_x, r in por_clave.values() if _logo(r)),
            "enriquecidas": sum(1 for *_x, r in por_clave.values() if r.get("about") or r.get("japanese_name") or r.get("links")),
            "ejemplos_enlazar": [(por_clave[c][0], c[1]) for c in list(enlazar)[:10]]}


def _fichas_sin_url(por_clave: dict[Clave, tuple[str, str, dict]], con_ficha: set[Clave]) -> list[CompanyMAL]:
    """Las fichas que YA existían, no tienen URL y el archivo sí la trae (por lotes y por tipo)."""
    faltan = []
    for kind in {k for k, _i in con_ficha}:
        ids = [i for k, i in con_ficha if k == kind and por_clave[(k, i)][1]]
        for lote in _lotes(ids):
            faltan += list(CompanyMAL.objects.filter(kind=kind, mal_id__in=lote, url=""))
    return faltan


def _slugs_libres(nombres: list[str]) -> list[str]:
    """Un slug único por nombre, sin chocar con la tabla ni entre ellos (bulk_create no llama a save())."""
    bases = [slugify(n)[:250] or "compania" for n in nombres]
    ocupados = set()
    for lote in _lotes(sorted(set(bases))):
        ocupados |= set(Company.objects.filter(slug__in=lote).values_list("slug", flat=True))
        for b in lote:                                  # y los ya numerados: base-2, base-3…
            ocupados |= set(Company.objects.filter(slug__startswith=f"{b}-").values_list("slug", flat=True)) if b in ocupados else set()
    slugs = []
    for b in bases:
        slug, n = b, 2
        while slug in ocupados:
            slug, n = f"{b}-{n}", n + 1
        ocupados.add(slug)
        slugs.append(slug)
    return slugs


CAMPOS_MAL = ["name_japanese", "favorites", "about", "established", "links"]


def _logo(registro: dict) -> str:
    return str(registro.get("image_url") or "").strip()


def _anio(registro: dict) -> int | None:
    """`established.date.year` del dump (o None)."""
    fecha = ((registro.get("established") or {}).get("date") or {}) if isinstance(registro.get("established"), dict) else {}
    try:
        anio = int(fecha.get("year"))
    except (TypeError, ValueError):
        return None
    return anio if 1000 <= anio <= 9999 else None


def _datos_mal(registro: dict) -> dict:
    """Los campos de la ficha MAL que salen del registro (vacíos si el dump no los trae)."""
    fundada = registro.get("established")
    try:
        favoritos = max(int(registro.get("favorites") or 0), 0)
    except (TypeError, ValueError):
        favoritos = 0
    return {"name_japanese": " ".join(str(registro.get("japanese_name") or "").split())[:255],
            "favorites": favoritos,
            "about": str(registro.get("about") or "").strip(),
            "established": str((fundada or {}).get("raw") if isinstance(fundada, dict) else (fundada or ""))[:100],
            "links": [str(u).strip() for u in registro.get("links") or [] if str(u or "").strip()]}


def _completar_compania(compania: Company, registro: dict) -> bool:
    """Lo NEUTRO que trae MAL, solo donde la compañía está vacía. Devuelve si cambió algo."""
    cambio = False
    anio = _anio(registro)
    if anio and not compania.founded_year:
        compania.founded_year, cambio = anio, True
    about = str(registro.get("about") or "").strip()
    if about and not compania.biography:
        compania.biography, cambio = about, True
    return cambio


def _logos_pendientes(por_clave: dict[Clave, tuple[str, str, dict]], compania_de: dict[Clave, int]) -> int:
    """El logo de cada compañía como imagen pendiente (orden 0), sin repetir la URL si ya la tiene. Por lotes."""
    quiere = {compania_de[c]: _logo(r) for c, (*_x, r) in por_clave.items() if c in compania_de and _logo(r)}
    nuevas = 0
    pks = list(quiere)
    for lote in _lotes(pks):
        ya = set(CompanyImage.objects.filter(company_id__in=lote).values_list("company_id", "image_url"))
        filas = [CompanyImage(company_id=pk, image_url=quiere[pk], order=0) for pk in lote if (pk, quiere[pk]) not in ya]
        CompanyImage.objects.bulk_create(filas, batch_size=LOTE)
        nuevas += len(filas)
    return nuevas


@transaction.atomic
def aplicar(registros: Iterable[dict]) -> dict:
    """Crea, enlaza o ACTUALIZA, por lotes. Devuelve lo hecho con las mismas claves que el resumen."""
    por_clave, descartados, total = _limpios(registros)
    con_ficha, enlazar, crear = _plan(por_clave)
    compania_de: dict[Clave, int] = {}
    con_url_nueva = 0
    # 1) fichas que ya estaban: datos MAL al día, URL si faltaba, y lo neutro de la compañía donde esté vacío
    for kind in {k for k, _i in con_ficha}:
        ids = [i for k, i in con_ficha if k == kind]
        for lote in _lotes(ids):
            fichas = list(CompanyMAL.objects.select_related("company").filter(kind=kind, mal_id__in=lote))
            companias = []
            for ficha in fichas:
                _n, url, registro = por_clave[(kind, ficha.mal_id)]
                if url and not ficha.url:
                    ficha.url, con_url_nueva = url, con_url_nueva + 1
                for campo, valor in _datos_mal(registro).items():
                    setattr(ficha, campo, valor)
                if _completar_compania(ficha.company, registro):
                    companias.append(ficha.company)
                compania_de[(kind, ficha.mal_id)] = ficha.company_id
            CompanyMAL.objects.bulk_update(fichas, ["url", *CAMPOS_MAL, "updated_at"], batch_size=LOTE)
            Company.objects.bulk_update(companias, ["founded_year", "biography", "updated_at"], batch_size=LOTE)
    # 2) compañías que ya existían por nombre: su ficha MAL, y lo neutro donde esté vacío
    for lote in _lotes(list(enlazar.items())):
        companias = Company.objects.in_bulk([pk for _c, pk in lote])
        tocadas = [companias[pk] for c, pk in lote if pk in companias and _completar_compania(companias[pk], por_clave[c][2])]
        Company.objects.bulk_update(tocadas, ["founded_year", "biography", "updated_at"], batch_size=LOTE)
        CompanyMAL.objects.bulk_create(
            [CompanyMAL(company_id=pk, kind=k, mal_id=i, url=por_clave[(k, i)][1], **_datos_mal(por_clave[(k, i)][2]))
             for (k, i), pk in lote], batch_size=LOTE)
        compania_de.update(dict(lote))
    # 3) compañías nuevas + su ficha
    for lote in _lotes(crear):
        nombres = [por_clave[c][0] for c in lote]
        nuevas = Company.objects.bulk_create(
            [Company(name=n, slug=s, founded_year=_anio(por_clave[c][2]), biography=str(por_clave[c][2].get("about") or "").strip())
             for n, s, c in zip(nombres, _slugs_libres(nombres), lote)], batch_size=LOTE)
        CompanyMAL.objects.bulk_create(
            [CompanyMAL(company=co, kind=k, mal_id=i, url=por_clave[(k, i)][1], **_datos_mal(por_clave[(k, i)][2]))
             for co, (k, i) in zip(nuevas, lote)], batch_size=LOTE)
        compania_de.update({c: co.pk for co, c in zip(nuevas, lote)})
    logos = _logos_pendientes(por_clave, compania_de)
    return {"total": total, "sin_datos": descartados, "ya_estaban": len(con_ficha), "con_url_nueva": con_url_nueva,
            "enlazadas": len(enlazar), "creadas": len(crear), "logos": logos}
