"""DESCARGA de imágenes pendientes: toda tabla de imágenes (ModelBaseImage) guarda `image_url` y
`image_downloaded`; los importadores dejan la URL y ESTO baja el archivo a `image`. El archivo va SIEMPRE
a disco local (MEDIA_ROOT); subirlo a Cloudflare R2 es otro paso (core/shared/tasks/cloud.py, N al día), y la
URL pública pasa a R2 archivo por archivo (core/storage.py). Respeta la cancelación cooperativa y un tope
por tanda, pensado para la tarea programada «N imágenes al día» y para la acción masiva de las listas."""
import os
from urllib.parse import urlparse

import requests
from django.apps import apps
from django.core.files.base import ContentFile

from core.shared.tasks.cancel import avance, cancelado
from core.shared.models.abstract import MAX_INTENTOS_DESCARGA, ModelBaseImage

TIMEOUT = 20


def modelos_con_imagen():
    """Todas las tablas concretas de imágenes del proyecto (subclases de ModelBaseImage)."""
    return [m for m in apps.get_models() if issubclass(m, ModelBaseImage) and not m._meta.abstract]


def _nombre(fila, url):
    base = os.path.basename(urlparse(url).path) or "imagen"
    raiz, ext = os.path.splitext(base)
    return f"{fila._meta.model_name}-{fila.pk}{ext or '.jpg'}"


DEFINITIVOS = {400, 401, 403, 404, 410, 451}     # la URL no va a volver a servir: muerta al primer intento


def _anotar_fallo(fila, detalle, definitivo):
    """Suma el intento (o la da por muerta) sin pasar por save(): un UPDATE de tres columnas."""
    from django.utils import timezone
    intentos = MAX_INTENTOS_DESCARGA if definitivo else fila.download_attempts + 1
    type(fila).objects.filter(pk=fila.pk).update(download_attempts=intentos, download_error=str(detalle)[:300],
                                                 download_checked_at=timezone.now())
    fila.download_attempts, fila.download_error = intentos, str(detalle)[:300]


def descargar_fila(fila):
    """Baja `image_url` a `image`. Bien → descargada (save limpia intentos y error). Mal → anota el intento: un 404/403/410
    la mata al primero; un timeout o un 5xx suma uno hasta MAX_INTENTOS_DESCARGA. Devuelve (ok, detalle)."""
    from django.utils import timezone
    url = (fila.image_url or "").strip()
    if not url:
        return False, "sin URL"
    if getattr(fila, "image", None) and fila.image.name and fila.image.storage.exists(fila.image.name):
        if not fila.image_downloaded:
            type(fila).objects.filter(pk=fila.pk).update(image_downloaded=True, download_attempts=0, download_error="")
            fila.image_downloaded = True
        return True, "ya tenía archivo"
    # sin archivo en disco (media borrada, carpeta cambiada): se vuelve a bajar a la ruta actual de upload_to
    try:
        r = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as exc:
        detalle = f"{type(exc).__name__}: {exc}"
        _anotar_fallo(fila, detalle, definitivo=False)
        return False, detalle
    if r.status_code != 200 or not r.content:
        detalle = f"HTTP {r.status_code}" if r.status_code != 200 else "respuesta vacía"
        _anotar_fallo(fila, detalle, definitivo=r.status_code in DEFINITIVOS)
        return False, detalle
    fila.image.save(_nombre(fila, url), ContentFile(r.content), save=False)
    fila.download_checked_at = timezone.now()
    fila.save()
    return True, "descargada"


def acciones_fila(fila, en_nube=None):
    """[(accion, etiqueta, icono)] que se pueden hacer con ESTA imagen: «Descargar» si tiene URL y no archivo; «Subir a la
    nube» si ya tiene archivo, R2 está activo y aún no está allá. `en_nube` evita la consulta si la lista ya lo anotó."""
    from core.shared.tasks.cloud import r2_activo
    out = []
    if (fila.image_url or "").strip() and not fila.image_downloaded:
        out.append(("descargar", "Reintentar descarga" if fila.download_dead else "Descargar", "cloud-download"))
    if fila.image_downloaded and r2_activo():
        if en_nube is None:
            from apps.system.models import CloudFile
            en_nube = CloudFile.objects.filter(name=getattr(fila.image, "name", "")).exists()
        if not en_nube:
            out.append(("subir", "Subir a la nube", "cloud-upload"))
    return out


def subir_fila(fila):
    """Sube el archivo de ESTA imagen a R2. Devuelve (ok, detalle)."""
    from core.shared.tasks.cloud import r2_activo, subir_pendientes
    if not r2_activo():
        return False, "USE_R2 apagado"
    r = subir_pendientes(modelo=type(fila), ids=[fila.pk], tope=1)
    if r["ok"]:
        return True, "subida"
    return False, "; ".join(str(d[2]) for d in r["detalle"]) or "no había nada que subir"


LOTE_DESCARGA = 200


def _tabla(etiqueta: str):
    """«companies.CompanyImage» o «companies.CompanyImage:mal» → (modelo, queryset base). Con «:mal», solo las filas cuyo
    dueño tiene ficha MAL (compañía → company_mal, persona → person_mal): un JOIN uno a uno por índice."""
    etiqueta, _sep, filtro = etiqueta.partition(":")
    modelo = apps.get_model(etiqueta)
    qs = modelo.objects.all()
    if filtro == "mal":
        fk = next(f.name for f in modelo._meta.fields if f.is_relation and f.many_to_one)
        qs = qs.filter(**{f"{fk}__{fk}_mal__isnull": False})
    return modelo, qs


def _pendientes_qs(modelo, base=None):
    """La cola: con URL, sin archivo y no muertas."""
    qs = modelo.objects.all() if base is None else base
    return qs.exclude(image_url="").filter(image_downloaded=False, download_attempts__lt=MAX_INTENTOS_DESCARGA)


def _muertas_qs(modelo, base=None):
    qs = modelo.objects.all() if base is None else base
    return qs.exclude(image_url="").filter(image_downloaded=False, download_attempts__gte=MAX_INTENTOS_DESCARGA)


def muertas_de(etiqueta: str) -> int:
    """Cuántas imágenes de la tabla «app.Modelo» tienen la URL dada por muerta."""
    modelo, base = _tabla(etiqueta)
    return _muertas_qs(modelo, base).count()


def reintentar_muertas(etiqueta: str) -> int:
    """Devuelve las muertas a la cola (intentos a cero). Un UPDATE; devuelve cuántas."""
    modelo, base = _tabla(etiqueta)
    return modelo.objects.filter(pk__in=_muertas_qs(modelo, base).values("pk")).update(
        download_attempts=0, download_error="", download_checked_at=None)


def pendientes_de(etiqueta: str) -> int:
    """Cuántas imágenes con URL y sin descargar tiene la tabla «app.Modelo»."""
    modelo, base = _tabla(etiqueta)
    return _pendientes_qs(modelo, base).count()


def _log_de_app(modelo):
    """El log de la app de la tabla (OtakuLog, CompanyLog…): el modelo de esa app que hereda de ModelBaseLog."""
    from core.shared.models.abstract import ModelBaseLog
    return next((m for m in modelo._meta.app_config.get_models() if issubclass(m, ModelBaseLog)), None)


def descargar_lote(etiqueta: str, cantidad: int = 0) -> str:
    """Descarga hasta `cantidad` pendientes de UNA tabla (0 = todas), recorriendo por pk de a lotes: cada fila se intenta
    UNA vez por corrida (las que fallan no atascan la cola). Entre lotes mira si pidieron cancelar. Cada fallo va al log
    de la app con su URL y motivo; al final, una línea de resumen. Devuelve el resumen."""
    from core.utils.importlog import log_to
    from core.shared.models.choices import LogLevel

    modelo, base = _tabla(etiqueta)
    log = _log_de_app(modelo)
    proceso = f"descargar imágenes · {modelo._meta.verbose_name_plural}" + (" (MAL)" if etiqueta.endswith(":mal") else "")
    cantidad = max(int(cantidad or 0), 0)
    ultimo, ok, fallos, vistos, cancelada = 0, 0, 0, 0, False
    por_hacer = _pendientes_qs(modelo, base).count()
    total = por_hacer if cantidad == 0 else min(cantidad, por_hacer)
    avance(0, total)
    if log is not None:          # se ve en el log apenas arranca (los fallos y el resumen llegan después)
        log_to(log, LogLevel.INFO, proceso, f"empieza: {total} de {por_hacer} pendientes")
    while cantidad == 0 or vistos < cantidad:
        if cancelado():
            cancelada = True
            break
        tope = LOTE_DESCARGA if cantidad == 0 else min(LOTE_DESCARGA, cantidad - vistos)
        filas = list(_pendientes_qs(modelo, base).filter(pk__gt=ultimo).order_by("pk")[:tope])
        if not filas:
            break
        for n, fila in enumerate(filas, 1):
            if n % 20 == 0:                         # dentro del lote también: cada descarga puede tardar segundos
                avance(vistos + n, total)
                if cancelado():
                    cancelada = True
                    break
            bien, detalle = descargar_fila(fila)
            if bien:
                ok += 1
            else:
                fallos += 1
                if log is not None:
                    muerta = fila.download_attempts >= MAX_INTENTOS_DESCARGA
                    estado = "URL muerta" if muerta else f"intento {fila.download_attempts}/{MAX_INTENTOS_DESCARGA}"
                    log_to(log, LogLevel.ERROR if muerta else LogLevel.WARNING, f"{proceso} #{fila.pk}",
                           f"{detalle} · {estado} · {fila.image_url[:300]}")
        vistos += len(filas)
        ultimo = filas[-1].pk
        avance(vistos, total)
        if cancelada:
            break
    resumen = (f"{ok} descargadas · {fallos} con error de {vistos} intentadas · quedan {_pendientes_qs(modelo, base).count()} pendientes"
               f" · {_muertas_qs(modelo, base).count()} muertas"
               + (" · cancelada por el usuario" if cancelada else ""))
    if log is not None:
        log_to(log, LogLevel.WARNING if fallos or cancelada else LogLevel.INFO, proceso, resumen)
    return resumen


def descargar_pendientes(modelo=None, ids=None, tope=100):
    """Descarga hasta `tope` imágenes pendientes (con URL y sin descargar). `modelo` limita a una
    tabla; `ids` a unas filas. Devuelve {"ok": n, "fallos": n, "detalle": [(modelo, pk, detalle)…]}."""
    resultado = {"ok": 0, "fallos": 0, "detalle": []}
    modelos = [modelo] if modelo is not None else modelos_con_imagen()
    restantes = max(int(tope), 0)
    for m in modelos:
        if restantes <= 0:
            break
        qs = _pendientes_qs(m)
        if ids:
            qs = qs.filter(pk__in=ids)
        for fila in qs.order_by("pk")[:restantes]:
            if cancelado():
                resultado["detalle"].append((m._meta.label, None, "cancelada por el usuario"))
                return resultado
            ok, detalle = descargar_fila(fila)
            resultado["ok" if ok else "fallos"] += 1
            if not ok:
                resultado["detalle"].append((m._meta.label, fila.pk, detalle))
            restantes -= 1
            if restantes <= 0:
                break
    return resultado


# ----------------------------- IMÁGENES de un objeto = filas en su tabla XImage -----------------------------
def fila_imagen(obj, url=""):
    """La fila de `obj` en su tabla de imágenes (Game→GameImage… por su related `images`) con esa `image_url`; si no
    está, se crea AL FINAL (no cambia la portada, que es la de `order` más bajo). Sin url: la portada, o None."""
    rel = obj.images
    if not url:
        return rel.first()
    return rel.filter(image_url=url).first() or rel.model.objects.create(**{rel.field.name: obj}, image_url=url)


def portada(obj, url, contenido=None, nombre=None):
    """Guarda la imagen `url` de `obj` en su tabla de imágenes (si es la primera, es la portada). Con `contenido`
    (bytes ya bajados) la escribe; sin él, la baja ahora mismo. Si esa imagen ya tiene archivo, no hace nada.
    Devuelve la fila o None."""
    if not url or not hasattr(obj, "images"):
        return None
    fila = fila_imagen(obj, url)
    if fila.image and fila.image.name and fila.image.storage.exists(fila.image.name):
        return fila
    if contenido is None:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code != 200 or not r.content:
                return fila                      # queda pendiente: la baja el descargador por image_url
            contenido = r.content
        except requests.RequestException:
            return fila
    fila.image.save(nombre or _nombre(fila, url), ContentFile(contenido), save=False)
    fila.image_downloaded = True
    fila.save()
    return fila
