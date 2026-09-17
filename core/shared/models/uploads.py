"""Rutas de los archivos subidos/bajados, en UNA función para todas las tablas (`upload_to` de sus ImageField/FileField).

    <app>/<contenido>/<entidad>/<grupo>/<id>-<slug>/<id de la fila>.ext

    otaku/images/anime/27/27423-cowboy-bebop/34.jpg          imagen del anime 27423 (AnimeImage #34)
    otaku/audio/anime/27/27423-cowboy-bebop/7.mp3            audio de una fila de ese anime
    companies/images/company/0/506-mary-jane/12.webp         logo de la compañía 506

· Primero el TIPO de contenido (`images`, `audio`, `videos`, `documents`): todas las imágenes de una app cuelgan de una
  carpeta, para respaldarlas, subirlas o buscarlas aparte del resto.
· `<grupo>` = id del dueño // 1000 (0 = ids 0–999, 27 = 27000–27999). Reparte las carpetas como el CDN de MAL
  (…/images/anime/4/19644.jpg): ningún directorio pasa de ~1000 carpetas aunque haya millones de filas.
· `<id>-<slug>`: una carpeta por objeto dueño; el id va primero (ordena como la base y se encuentra por id).
· El archivo se llama por la pk de SU fila (estable entre descargas y subidas); el nombre original solo aporta la extensión.

`entidad` es el modelo dueño sin el prefijo de su app (movies.MovieCast → «cast»); `slug` el suyo (o su pk si no tiene).
Las categorías con `image` propio siguen en `categorias/`."""
import os

from django.db import models
from django.utils.text import slugify

GRUPO = 1000
AUDIO = {".mp3", ".ogg", ".oga", ".wav", ".flac", ".m4a", ".aac", ".opus"}
VIDEO = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v"}


def _padre(instance):
    """La entidad dueña del archivo: la primera FK del modelo; si no hay, él mismo."""
    for f in instance._meta.get_fields():
        if isinstance(f, models.ForeignKey):
            padre = getattr(instance, f.name, None)
            if padre is not None:
                return padre
    return instance


def _entidad(padre):
    """movies.MovieCast → «cast», games.Game → «game», otaku.Anime → «anime», people.Person → «person»."""
    nombre, app = padre._meta.model_name, padre._meta.app_label
    prefijo = app[:-1] if app.endswith("s") else app          # games → game, movies → movie, series → serie
    return nombre[len(prefijo):] if nombre.startswith(prefijo) and len(nombre) > len(prefijo) else nombre


def _slug(obj):
    s = getattr(obj, "slug", "") or slugify(str(obj))[:80]
    return s or str(obj.pk or "nuevo")


def _contenido(instance, ext):
    """images · audio · videos · documents: las filas con ImageField son imágenes; en un FileField manda la extensión."""
    if not any(isinstance(f, models.FileField) and not isinstance(f, models.ImageField) for f in instance._meta.fields):
        return "images"
    if ext in AUDIO:
        return "audio"
    if ext in VIDEO:
        return "videos"
    return "documents"


def upload_path(instance, filename):
    padre = _padre(instance)
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    slug = _slug(padre)
    partes = [str(padre.pk // GRUPO), f"{padre.pk}-{slug}"] if padre.pk else ["nuevo", slug]
    nombre = f"{instance.pk or 'nuevo'}{ext}"
    return "/".join([instance._meta.app_label, _contenido(instance, ext), _entidad(padre), *partes, nombre])
