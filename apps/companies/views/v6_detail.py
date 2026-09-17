"""companies · FICHAS (detalle), de gestión y pública."""
from django.utils.translation import gettext_lazy as _

from apps.companies.views.base import BaseCompany, BaseCompanyImage, BaseCompanyLog
from core.shared.views.base import BaseAdminDetailView, BasePublicDetailView


# Una pestaña por PAPEL, con su lista «por» en el medio: (clave de PAPELES, etiqueta, tipo «por» del medio).
# La clave es la misma que devuelve `Company.obras()`, así la ficha empareja cada grupo con su «Ver en lista».
def _pestanas(rutas):
    """rutas = {medio: nombre de ruta «por»} del lado que toque (gestión o público)."""
    return [
        ("peliculas-producidas", _("Películas producidas"), rutas["movies"], "productora"),
        ("peliculas-distribuidas", _("Películas distribuidas"), rutas["movies"], "distribuidora"),
        ("series-producidas", _("Series producidas"), rutas["series"], "productora"),
        ("series-distribuidas", _("Series distribuidas"), rutas["series"], "distribuidora"),
        ("anime-estudio", _("Anime · estudio"), rutas["anime"], "estudio"),
        ("anime-produccion", _("Anime · producción"), rutas["anime"], "productora"),
        ("anime-licencia", _("Anime · licencia"), rutas["anime"], "licenciataria"),
        ("manga-serializacion", _("Manga · serialización"), rutas["manga"], "revista"),
    ]


# ==============================================================================
# Gestión
# ==============================================================================


class CompanyDetailView(BaseCompany, BaseAdminDetailView):
    template_name = "companies/detail/company.html"   # el detail PROPIO de la entidad
    update_url = "panel:company_update"
    delete_url = "panel:company_delete"
    list_url = "panel:company_list"
    toggle_url = "panel:company_toggle"
    tabs = _pestanas({"movies": "panel:movie_by", "series": "panel:serie_by", "anime": "panel:anime_by", "manga": "panel:manga_by"}) + [
        ("imagenes", _("Imágenes"), "panel:company-image_by", "compania")]

    def acciones_extra(self, obj):
        """«Añadir ficha MAL» / «Ficha MAL» (la ficha vive en otaku; aquí solo se enlaza)."""
        from apps.otaku import fichas_mal
        e = fichas_mal.enlace("company", obj.pk)
        return [e] if e else []


class CompanyImageDetailView(BaseCompanyImage, BaseAdminDetailView):
    template_name = "companies/detail/company_image.html"
    update_url = "panel:company-image_update"
    delete_url = "panel:company-image_delete"
    list_url = "panel:company-image_list"
    toggle_url = "panel:company-image_toggle"


class CompanyLogDetailView(BaseCompanyLog, BaseAdminDetailView):
    template_name = "companies/detail/company_log.html"
    list_url = "panel:company-log_list"


# ==============================================================================
# Público
# ==============================================================================


class CompanyPublicDetailView(BaseCompany, BasePublicDetailView):
    """Ficha pública de una compañía: lo que hizo en TODOS los medios, un grupo por papel."""
    collect_kind = "company"
    template_name = "companies/detail/company.html"
    list_url = "companias:companies-catalog"
    section = "companias"
    tabs = _pestanas({"movies": "movies:movies-by", "series": "series:series-by", "anime": "otaku:anime-by", "manga": "otaku:manga-by"})
