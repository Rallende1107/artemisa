"""series · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.series import forms as f
from apps.series.views.base import BaseGenre, BaseGenreAlias, BaseRating, BaseRole, BaseSerie, BaseSerieCast, BaseSerieImage, BaseSerieLog, BaseSerieRelation, BaseSerieStaff, BaseSerieTitle, BaseType
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class GenreCreateView(BaseGenre, BaseCreate):
    # Django core
    form_class = f.GenreForm
    form_template = "series/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-genre_list"
    success_url = "panel:serie-genre_list"
    cancel_url = "panel:serie-genre_list"
    # UX
    success_message = _("Género «%(obj)s» creado.")
    title = _("Crear género")


class GenreUpdateView(BaseGenre, BaseUpdate):
    # Django core
    form_class = f.GenreForm
    form_template = "series/form/genre.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-genre_list"
    success_url = "panel:serie-genre_list"
    cancel_url = "panel:serie-genre_list"
    # UX
    success_message = _("Género «%(obj)s» actualizado.")
    title = _("Editar género")


class GenreDeleteView(BaseGenre, BaseDelete):
    list_url = "panel:serie-genre_list"
    success_url = "panel:serie-genre_list"
    cancel_url = "panel:serie-genre_list"
    success_message = _("Género «%(obj)s» eliminado.")
    title = _("Eliminar género")


class GenreAliasCreateView(BaseGenreAlias, BaseCreate):
    form_class = f.GenreAliasForm
    list_url = "panel:serie-genre-alias_list"
    success_url = "panel:serie-genre-alias_list"
    cancel_url = "panel:serie-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» creado.")
    title = _("Crear alias de género")


class GenreAliasUpdateView(BaseGenreAlias, BaseUpdate):
    form_class = f.GenreAliasForm
    list_url = "panel:serie-genre-alias_list"
    success_url = "panel:serie-genre-alias_list"
    cancel_url = "panel:serie-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» actualizado.")
    title = _("Editar alias de género")


class GenreAliasDeleteView(BaseGenreAlias, BaseDelete):
    list_url = "panel:serie-genre-alias_list"
    success_url = "panel:serie-genre-alias_list"
    cancel_url = "panel:serie-genre-alias_list"
    success_message = _("Alias de género «%(obj)s» eliminado.")
    title = _("Eliminar alias de género")


class RatingCreateView(BaseRating, BaseCreate):
    # Django core
    form_class = f.RatingForm
    form_template = "series/form/rating.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-rating_list"
    success_url = "panel:serie-rating_list"
    cancel_url = "panel:serie-rating_list"
    # UX
    success_message = _("Clasificación «%(obj)s» creada.")
    title = _("Crear clasificación")


class RatingUpdateView(BaseRating, BaseUpdate):
    # Django core
    form_class = f.RatingForm
    form_template = "series/form/rating.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-rating_list"
    success_url = "panel:serie-rating_list"
    cancel_url = "panel:serie-rating_list"
    # UX
    success_message = _("Clasificación «%(obj)s» actualizada.")
    title = _("Editar clasificación")


class RatingDeleteView(BaseRating, BaseDelete):
    list_url = "panel:serie-rating_list"
    success_url = "panel:serie-rating_list"
    cancel_url = "panel:serie-rating_list"
    success_message = _("Clasificación «%(obj)s» eliminada.")
    title = _("Eliminar clasificación")


class RoleCreateView(BaseRole, BaseCreate):
    # Django core
    form_class = f.RoleForm
    form_template = "series/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-role_list"
    success_url = "panel:serie-role_list"
    cancel_url = "panel:serie-role_list"
    # UX
    success_message = _("Rol «%(obj)s» creado.")
    title = _("Crear rol")


class RoleUpdateView(BaseRole, BaseUpdate):
    # Django core
    form_class = f.RoleForm
    form_template = "series/form/role.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-role_list"
    success_url = "panel:serie-role_list"
    cancel_url = "panel:serie-role_list"
    # UX
    success_message = _("Rol «%(obj)s» actualizado.")
    title = _("Editar rol")


class RoleDeleteView(BaseRole, BaseDelete):
    list_url = "panel:serie-role_list"
    success_url = "panel:serie-role_list"
    cancel_url = "panel:serie-role_list"
    success_message = _("Rol «%(obj)s» eliminado.")
    title = _("Eliminar rol")


class SerieCreateView(BaseSerie, BaseCreate):
    # Django core
    form_class = f.SerieForm
    form_template = "series/form/serie.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie_list"
    success_url = "panel:serie_list"
    cancel_url = "panel:serie_list"
    # UX
    success_message = _("Serie «%(obj)s» creada.")
    title = _("Crear series")


class SerieUpdateView(BaseSerie, BaseUpdate):
    # Django core
    form_class = f.SerieForm
    form_template = "series/form/serie.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie_list"
    success_url = "panel:serie_list"
    cancel_url = "panel:serie_list"
    # UX
    success_message = _("Serie «%(obj)s» actualizada.")
    title = _("Editar series")


class SerieDeleteView(BaseSerie, BaseDelete):
    list_url = "panel:serie_list"
    success_url = "panel:serie_list"
    cancel_url = "panel:serie_list"
    success_message = _("Serie «%(obj)s» eliminada.")
    title = _("Eliminar series")


class SerieCastCreateView(BaseSerieCast, BaseCreate):
    # Django core
    form_class = f.SerieCastForm
    form_template = "series/form/serie_cast.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-cast_list"
    success_url = "panel:serie-cast_list"
    cancel_url = "panel:serie-cast_list"
    # UX
    success_message = _("Reparto «%(obj)s» creado.")
    title = _("Crear reparto")


class SerieCastUpdateView(BaseSerieCast, BaseUpdate):
    # Django core
    form_class = f.SerieCastForm
    form_template = "series/form/serie_cast.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-cast_list"
    success_url = "panel:serie-cast_list"
    cancel_url = "panel:serie-cast_list"
    # UX
    success_message = _("Reparto «%(obj)s» actualizado.")
    title = _("Editar reparto")


class SerieCastDeleteView(BaseSerieCast, BaseDelete):
    list_url = "panel:serie-cast_list"
    success_url = "panel:serie-cast_list"
    cancel_url = "panel:serie-cast_list"
    success_message = _("Reparto «%(obj)s» eliminado.")
    title = _("Eliminar reparto")


class SerieImageCreateView(BaseSerieImage, BaseCreate):
    # Django core
    form_class = f.SerieImageForm
    form_template = "series/form/serie_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-image_list"
    success_url = "panel:serie-image_list"
    cancel_url = "panel:serie-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class SerieImageUpdateView(BaseSerieImage, BaseUpdate):
    # Django core
    form_class = f.SerieImageForm
    form_template = "series/form/serie_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-image_list"
    success_url = "panel:serie-image_list"
    cancel_url = "panel:serie-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class SerieImageDeleteView(BaseSerieImage, BaseDelete):
    list_url = "panel:serie-image_list"
    success_url = "panel:serie-image_list"
    cancel_url = "panel:serie-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class SerieRelationCreateView(BaseSerieRelation, BaseCreate):
    form_class = f.SerieRelationForm
    form_template = "series/form/serie_relation.html"
    list_url = "panel:serie-relation_list"
    success_url = "panel:serie-relation_list"
    cancel_url = "panel:serie-relation_list"
    success_message = _("Relación «%(obj)s» creada.")
    title = _("Crear relación")


class SerieRelationUpdateView(BaseSerieRelation, BaseUpdate):
    form_class = f.SerieRelationForm
    form_template = "series/form/serie_relation.html"
    list_url = "panel:serie-relation_list"
    success_url = "panel:serie-relation_list"
    cancel_url = "panel:serie-relation_list"
    success_message = _("Relación «%(obj)s» actualizada.")
    title = _("Editar relación")


class SerieRelationDeleteView(BaseSerieRelation, BaseDelete):
    list_url = "panel:serie-relation_list"
    success_url = "panel:serie-relation_list"
    cancel_url = "panel:serie-relation_list"
    success_message = _("Relación «%(obj)s» eliminada.")
    title = _("Eliminar relación")


class SerieStaffCreateView(BaseSerieStaff, BaseCreate):
    # Django core
    form_class = f.SerieStaffForm
    form_template = "series/form/serie_staff.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-staff_list"
    success_url = "panel:serie-staff_list"
    cancel_url = "panel:serie-staff_list"
    # UX
    success_message = _("Equipo «%(obj)s» creado.")
    title = _("Crear equipo")


class SerieStaffUpdateView(BaseSerieStaff, BaseUpdate):
    # Django core
    form_class = f.SerieStaffForm
    form_template = "series/form/serie_staff.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-staff_list"
    success_url = "panel:serie-staff_list"
    cancel_url = "panel:serie-staff_list"
    # UX
    success_message = _("Equipo «%(obj)s» actualizado.")
    title = _("Editar equipo")


class SerieStaffDeleteView(BaseSerieStaff, BaseDelete):
    list_url = "panel:serie-staff_list"
    success_url = "panel:serie-staff_list"
    cancel_url = "panel:serie-staff_list"
    success_message = _("Equipo «%(obj)s» eliminado.")
    title = _("Eliminar equipo")


class SerieTitleCreateView(BaseSerieTitle, BaseCreate):
    # Django core
    form_class = f.SerieTitleForm
    form_template = "series/form/serie_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-title_list"
    success_url = "panel:serie-title_list"
    cancel_url = "panel:serie-title_list"
    # UX
    success_message = _("Título «%(obj)s» creado.")
    title = _("Crear título")


class SerieTitleUpdateView(BaseSerieTitle, BaseUpdate):
    # Django core
    form_class = f.SerieTitleForm
    form_template = "series/form/serie_title.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-title_list"
    success_url = "panel:serie-title_list"
    cancel_url = "panel:serie-title_list"
    # UX
    success_message = _("Título «%(obj)s» actualizado.")
    title = _("Editar título")


class SerieTitleDeleteView(BaseSerieTitle, BaseDelete):
    list_url = "panel:serie-title_list"
    success_url = "panel:serie-title_list"
    cancel_url = "panel:serie-title_list"
    success_message = _("Título «%(obj)s» eliminado.")
    title = _("Eliminar título")


class TypeCreateView(BaseType, BaseCreate):
    # Django core
    form_class = f.TypeForm
    form_template = "series/form/type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-type_list"
    success_url = "panel:serie-type_list"
    cancel_url = "panel:serie-type_list"
    # UX
    success_message = _("Tipo «%(obj)s» creado.")
    title = _("Crear tipo")


class TypeUpdateView(BaseType, BaseUpdate):
    # Django core
    form_class = f.TypeForm
    form_template = "series/form/type.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:serie-type_list"
    success_url = "panel:serie-type_list"
    cancel_url = "panel:serie-type_list"
    # UX
    success_message = _("Tipo «%(obj)s» actualizado.")
    title = _("Editar tipo")


class TypeDeleteView(BaseType, BaseDelete):
    list_url = "panel:serie-type_list"
    success_url = "panel:serie-type_list"
    cancel_url = "panel:serie-type_list"
    success_message = _("Tipo «%(obj)s» eliminado.")
    title = _("Eliminar tipo")


class SerieLogCreateView(BaseSerieLog, BaseCreate):
    form_class = f.SerieLogForm
    form_template = "series/form/serie_log.html"
    list_url = "panel:serie-log_list"
    success_url = "panel:serie-log_list"
    cancel_url = "panel:serie-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class SerieLogUpdateView(BaseSerieLog, BaseUpdate):
    form_class = f.SerieLogForm
    form_template = "series/form/serie_log.html"
    list_url = "panel:serie-log_list"
    success_url = "panel:serie-log_list"
    cancel_url = "panel:serie-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class SerieLogDeleteView(BaseSerieLog, BaseDelete):
    list_url = "panel:serie-log_list"
    success_url = "panel:serie-log_list"
    cancel_url = "panel:serie-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
