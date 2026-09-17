"""Modelos de COMPAÑÍAS: la empresa real (estudio, productora, distribuidora, licenciataria, revista) y el log
de la app. Como `people.Person`, es una entidad TRANSVERSAL y NEUTRA: la misma Disney produce una película,
distribuye una serie y licencia un anime. QUÉ hizo en cada obra no vive aquí, lo dice la relación desde el
medio (`Movie.producers`, `Serie.distributors`, `Anime.studios`, `Manga.serializations`…).

Nació el 2026-09-16 juntando `movies.Company`, `series.Company` y las cuatro de otaku (`Studio`, `Producer`,
`Licensor`, `Serialization`), que eran la misma tabla escrita seis veces."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.shared.models.abstract import ModelBaseCompany, ModelBaseImage, ModelBaseLog
from core.shared.models.uploads import upload_path
from core.utils.models_abstract import filas_obra


# Las obras de una compañía, por PAPEL: (clave, etiqueta, related_name desde el medio, orden).
# El related_name lo declara el campo del medio que apunta aquí; si ese medio aún no lo tiene, se salta.
PAPELES = (
    ("peliculas-producidas", _("Películas producidas"), "movies_produced", ("-release_year", "title")),
    ("peliculas-distribuidas", _("Películas distribuidas"), "movies_distributed", ("-release_year", "title")),
    ("series-producidas", _("Series producidas"), "series_produced", ("-release_year", "title")),
    ("series-distribuidas", _("Series distribuidas"), "series_distributed", ("-release_year", "title")),
    ("anime-estudio", _("Anime · estudio"), "animes_studio", ("-year", "title")),
    ("anime-produccion", _("Anime · producción"), "animes_produced", ("-year", "title")),
    ("anime-licencia", _("Anime · licencia"), "animes_licensed", ("-year", "title")),
    ("manga-serializacion", _("Manga · serialización"), "mangas_serialized", ("-year", "title")),
)


class Company(ModelBaseCompany):
    """Compañía real, NEUTRA: solo lo que cualquier fuente tiene. Lo que sabe un sitio concreto va en su extensión,
    uno a uno y en su app: el id de MyAnimeList en `otaku.CompanyMAL` (como `otaku.PersonMAL` para las personas);
    mañana el de Steam en la suya. Así esta tabla no crece con un `<sitio>_id` por cada fuente."""
    country = models.ForeignKey(
        "catalogs.Country", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="companies", verbose_name="país",
    )

    class Meta(ModelBaseCompany.Meta):
        verbose_name = "compañía"
        verbose_name_plural = "compañías"

    def get_absolute_url(self):
        from core.utils.public import url_detail
        return url_detail("companias:company-detail", self)

    def obras(self):
        """[(clave, etiqueta, filas de obra)] para la ficha: lo que hizo en cada medio, un grupo por papel."""
        grupos = []
        for clave, etiqueta, related, orden in PAPELES:
            manager = getattr(self, related, None)
            if manager is None:
                continue
            grupos.append((clave, etiqueta, filas_obra(manager.filter(is_active=True).order_by(*orden), lambda o: o)))
        return grupos


class CompanyImage(ModelBaseImage):
    """Logos e imágenes de compañía, todas en una tabla: la de `order` más bajo es la portada. Con `image_url` y sin
    archivo queda pendiente: la baja el descargador de imágenes («Descargar imágenes pendientes»)."""
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="images", verbose_name="compañía")
    image = models.ImageField(verbose_name="imagen", upload_to=upload_path, null=True, blank=True)

    class Meta(ModelBaseImage.Meta):
        verbose_name = "imagen de compañía"
        verbose_name_plural = "imágenes de compañía"
        ordering = ["company", "order", "id"]


class CompanyLog(ModelBaseLog):
    """Log de la app: auditoría del panel (altas, ediciones, borrados, toggles) y cualquier proceso propio.
    Una tabla por app, para no amontonar."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de compañías"
        verbose_name_plural = "logs de compañías"
