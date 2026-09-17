"""series · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.series.views.base import BaseGenre, BaseGenreAlias, BaseRating, BaseRole, BaseSerie, BaseSerieCast, BaseSerieImage, BaseSerieLog, BaseSerieRelation, BaseSerieStaff, BaseSerieTitle, BaseType
from core.shared.views.base import BaseAdminDetailView, BasePublicDetailView


# Gestión
# ==============================================================================


class GenreDetailView(BaseGenre, BaseAdminDetailView):
    template_name = "series/detail/genre.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-genre_update"
    delete_url = "panel:serie-genre_delete"
    list_url = "panel:serie-genre_list"
    toggle_url = "panel:serie-genre_toggle"


class RatingDetailView(BaseRating, BaseAdminDetailView):
    template_name = "series/detail/rating.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-rating_update"
    delete_url = "panel:serie-rating_delete"
    list_url = "panel:serie-rating_list"
    toggle_url = "panel:serie-rating_toggle"


class RoleDetailView(BaseRole, BaseAdminDetailView):
    template_name = "series/detail/role.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-role_update"
    delete_url = "panel:serie-role_delete"
    list_url = "panel:serie-role_list"
    toggle_url = "panel:serie-role_toggle"


class SerieDetailView(BaseSerie, BaseAdminDetailView):
    template_name = "series/detail/serie.html"   # la misma ficha que el público, con los botones de gestión
    by_url = "panel:serie_by"
    tabs = [("reparto", _("Reparto"), "panel:serie-cast_by", "serie"),
            ("equipo", _("Equipo"), "panel:serie-staff_by", "serie"),
            ("imagenes", _("Imágenes"), "panel:serie-image_by", "serie"),
            ("relaciones", _("Relaciones"), "panel:serie-relation_by", "serie"),
            ("titulos", _("Títulos"), "panel:serie-title_by", "serie")]
    update_url = "panel:serie_update"
    delete_url = "panel:serie_delete"
    list_url = "panel:serie_list"
    toggle_url = "panel:serie_toggle"


class SerieCastDetailView(BaseSerieCast, BaseAdminDetailView):
    template_name = "series/detail/serie_cast.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-cast_update"
    delete_url = "panel:serie-cast_delete"
    list_url = "panel:serie-cast_list"
    toggle_url = "panel:serie-cast_toggle"


class SerieImageDetailView(BaseSerieImage, BaseAdminDetailView):
    template_name = "series/detail/serie_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-image_update"
    delete_url = "panel:serie-image_delete"
    list_url = "panel:serie-image_list"
    toggle_url = "panel:serie-image_toggle"


class SerieRelationDetailView(BaseSerieRelation, BaseAdminDetailView):
    template_name = "series/detail/serie_relation.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-relation_update"
    delete_url = "panel:serie-relation_delete"
    list_url = "panel:serie-relation_list"
    toggle_url = "panel:serie-relation_toggle"


class SerieStaffDetailView(BaseSerieStaff, BaseAdminDetailView):
    template_name = "series/detail/serie_staff.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-staff_update"
    delete_url = "panel:serie-staff_delete"
    list_url = "panel:serie-staff_list"
    toggle_url = "panel:serie-staff_toggle"


class SerieTitleDetailView(BaseSerieTitle, BaseAdminDetailView):
    template_name = "series/detail/serie_title.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-title_update"
    delete_url = "panel:serie-title_delete"
    list_url = "panel:serie-title_list"
    toggle_url = "panel:serie-title_toggle"


class TypeDetailView(BaseType, BaseAdminDetailView):
    template_name = "series/detail/type.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-type_update"
    delete_url = "panel:serie-type_delete"
    list_url = "panel:serie-type_list"
    toggle_url = "panel:serie-type_toggle"


class SerieLogDetailView(BaseSerieLog, BaseAdminDetailView):
    template_name = "series/detail/serie_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:serie-log_update"
    delete_url = "panel:serie-log_delete"
    list_url = "panel:serie-log_list"


# ==============================================================================
# Público
# ==============================================================================


class GenreAliasDetailView(BaseGenreAlias, BaseAdminDetailView):
    template_name = "admin_panel/detail.html"
    list_url = "panel:serie-genre-alias_list"
    update_url = "panel:serie-genre-alias_update"
    delete_url = "panel:serie-genre-alias_delete"
    detail_fields = [('Nombre', 'name'), ('Nombre (es)', 'name_esp'), ('Slug', 'slug'), ('Activo', 'is_active'), ('Creado', 'created_at'), ('Actualizado', 'updated_at'), ('Género', 'genre')]


class SeriePublicDetailView(BaseSerie, BasePublicDetailView):
    """Ficha pública de una serie: el mismo HTML que en gestión, sin botones y con la colección."""
    template_name = "series/detail/serie.html"
    list_url = "series:series-catalog"
    by_url = "series:series-by"
    section = "series"
    collect_kind = "serie"
    background_image = "bg-series-serie"
    background_fallback = "bg-series-home"
    tabs = [("reparto", _("Reparto"), "series:cast-by", "serie"),
            ("equipo", _("Equipo"), "series:crew-by", "serie"),
            ("imagenes", _("Imágenes"), "series:serie-images-by", "serie")]
