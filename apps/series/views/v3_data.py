"""series · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.series.models import Genre, GenreAlias, Rating, Role, Serie, SerieCast, SerieImage, SerieLog, SerieRelation, SerieStaff, SerieTitle, Type
from apps.series.views.base import BaseCompany, BaseGenre, BaseGenreAliasContext, BaseRating, BaseRole, BaseRoleContext, BaseSerie, BaseSerieCast, BaseSerieCastContext, BaseSerieContext, BaseSerieImage, BaseSerieImageContext, BaseSerieLog, BaseSerieRelation, BaseSerieRelationContext, BaseSerieStaff, BaseSerieStaffContext, BaseSerieTitle, BaseSerieTitleContext, BaseType
from apps.series.views.v2_filters import CompanyFilters, RoleFilters, SerieCastFilters, SerieFilters, SerieStaffFilters
from core.shared.views.base import AdminDataView, BaseSelectView, PublicDataView
from core.shared.views.filters import ImagenesFilters, LogFilters
from core.utils.queries import con_nube, con_relacion
from core.utils.views_base import cell, cell_cover, cell_miniatura, meta_line


# ==============================================================================
# Gestión
# ==============================================================================


class ProducerPublicDataView(BaseCompany, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = CompanyFilters
    priority = {"ficha": 1}
    detail_url_name = "companias:company-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.all()
        qs = qs.filter(con_relacion(Company, "series_produced"), is_active=True)
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class DistributorPublicDataView(BaseCompany, PublicDataView):
    columns = [(_("Nombre"), "ficha")]
    filters = CompanyFilters
    priority = {"ficha": 1}
    detail_url_name = "companias:company-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Company.objects.all()
        qs = qs.filter(con_relacion(Company, "series_distributed"), is_active=True)
        p, total, filtrado, objetos = self.query(request, qs, ['name'], {'ficha': 'name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.name or ''), meta_line(obj)),
                "acciones": self.row_actions(obj, request, str(obj.name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.name or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GenreDataView(BaseGenre, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('+18'), 'explicit'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Genre.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'aliases__name', 'aliases__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "explicit"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GenreSelectView(BaseGenre, BaseSelectView):
    search_fields = ['name', 'name_esp', 'aliases__name', 'aliases__name_esp']


class GenreAliasDataView(BaseGenreAliasContext, AdminDataView):
    columns = [(_('Alias'), 'name'), (_('Alias (ES)'), 'name_esp'), (_('Género'), 'genre'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = GenreAlias.objects.all().select_related(*('genre',))
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp', 'genre__name', 'genre__name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "name"),
                "c1": cell(obj, "name_esp"),
                "c2": self.link_by(obj, "genre"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RatingDataView(BaseRating, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Acrónimo'), 'acronym'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Rating.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "acronym"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RatingSelectView(BaseRating, BaseSelectView):
    search_fields = ['name', 'name_esp']


class RoleDataView(BaseRoleContext, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Tipo de rol'), 'get_type_display'), (_('Activo'), 'is_active')]
    filters = RoleFilters

    def get(self, request, tipo=None, pk=None):
        qs = Role.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "get_type_display"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class RoleSelectView(BaseRole, BaseSelectView):
    search_fields = ['name', 'name_esp']


class SerieDataView(BaseSerieContext, AdminDataView):
    columns = [(_('Título'), "ficha"), (_('Tipo'), 'serie_type'), (_('Clasificación'), 'serie_rating'), (_('Año'), 'release_year'), (_('Activo'), 'is_active')]
    filters = SerieFilters

    def get(self, request, tipo=None, pk=None):
        qs = Serie.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'title_secundary', 'release_year', 'titles__title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": self.link_by(obj, "serie_type"),
                "c2": self.link_by(obj, "serie_rating"),
                "c3": cell(obj, "release_year"),
                "c4": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieSelectView(BaseSerie, BaseSelectView):
    search_fields = ['title', 'title_secundary', 'release_year', 'titles__title']


class SeriePublicDataView(BaseSerieContext, PublicDataView):
    columns = [(_("Título"), "ficha"), (_("Año"), "release_year")]
    filters = SerieFilters
    priority = {"ficha": 1}
    detail_url_name = "series:serie-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Serie.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title', 'titles__title'], {'ficha': 'title'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.title or ''), meta_line(obj)),
                "c1": cell(obj, "release_year"),
                "acciones": self.row_actions(obj, request, str(obj.title or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.title or '')), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieCastDataView(BaseSerieCastContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('Personaje'), 'character_name'), (_('Rol'), 'role'), (_('Serie'), 'serie'), (_('Activo'), 'is_active')]
    filters = SerieCastFilters

    def get(self, request, tipo=None, pk=None):
        qs = SerieCast.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['character_name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": cell(obj, "character_name"),
                "c2": cell(obj, "role"),
                "c3": self.link_by(obj, "serie"),
                "c4": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieCastSelectView(BaseSerieCast, BaseSelectView):
    search_fields = ['character_name']


class SerieCastPublicDataView(BaseSerieCastContext, PublicDataView):
    """Reparto de una serie: [la persona (foto + nombre → su ficha) · personaje · rol]."""
    columns = [(_("Persona"), "ficha"), (_("Personaje"), "character_name"), (_("Rol"), "role")]
    filters = SerieCastFilters
    priority = {"ficha": 1}
    actions = False
    detail_url_name = "personas:person-detail"

    def get(self, request, tipo=None, pk=None):
        qs = SerieCast.objects.all().select_related(*("person", "role"))
        p, total, filtrado, objetos = self.query(request, qs, ["person__full_name", "person__nicknames__nickname", "character_name"], {'ficha': 'person__full_name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj.person), obj.person.cover_url, str(obj.person.full_name or ''), meta_line(obj.person)),
                "c1": cell(obj, "character_name"),
                "c2": cell(obj, "role"),
                "acciones": self.row_actions(obj, request, str(obj.person.full_name or '')),
                "detail_url": self.detail_url(obj.person), "card_title": escape(str(obj.person.full_name or '')), "card_image": obj.person.cover_url, "card_sub": str(obj.character_name or ''), "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieImageDataView(BaseSerieImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Serie'), 'serie'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def get(self, request, tipo=None, pk=None):
        qs = con_nube(SerieImage.objects.select_related("serie"))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "serie"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "serie", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieImageSelectView(BaseSerieImage, BaseSelectView):
    search_fields = ['image_url']


class SerieImagesPublicDataView(BaseSerieImageContext, PublicDataView):
    """Galería de una serie: sus imágenes extra en tarjetas (la portada va en la ficha)."""
    columns = [(_("Imagen"), "image")]
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = SerieImage.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "image"),
                "acciones": self.row_actions(obj, request, ""),
                "detail_url": self.detail_url(obj), "card_title": escape(""), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieRelationDataView(BaseSerieRelationContext, AdminDataView):
    columns = [(_('Serie'), 'serie'), (_('Tipo'), 'relation_type'), (_('Relacionada'), 'related'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = SerieRelation.objects.all().select_related(*('serie', 'related', 'relation_type'))
        p, total, filtrado, objetos = self.query(request, qs, ['serie__title', 'related__title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "serie"),
                "c1": self.link_by(obj, "relation_type"),
                "c2": cell(obj, "related"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieRelationSelectView(BaseSerieRelation, BaseSelectView):
    search_fields = ['serie__title', 'related__title']


class SerieStaffDataView(BaseSerieStaffContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('Rol'), 'role'), (_('Serie'), 'serie'), (_('Activo'), 'is_active')]
    filters = SerieStaffFilters

    def get(self, request, tipo=None, pk=None):
        qs = SerieStaff.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, [], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": cell(obj, "role"),
                "c2": self.link_by(obj, "serie"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieStaffSelectView(BaseSerieStaff, BaseSelectView):
    search_fields = []


class SerieStaffPublicDataView(BaseSerieStaffContext, PublicDataView):
    """Equipo técnico de una serie: [la persona (foto + nombre → su ficha) · rol]."""
    columns = [(_("Persona"), "ficha"), (_("Rol"), "role")]
    filters = SerieStaffFilters
    priority = {"ficha": 1}
    actions = False
    detail_url_name = "personas:person-detail"

    def get(self, request, tipo=None, pk=None):
        qs = SerieStaff.objects.all().select_related(*("person", "role"))
        p, total, filtrado, objetos = self.query(request, qs, ["person__full_name", "person__nicknames__nickname"], {'ficha': 'person__full_name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj.person), obj.person.cover_url, str(obj.person.full_name or ''), meta_line(obj.person)),
                "c1": cell(obj, "role"),
                "acciones": self.row_actions(obj, request, str(obj.person.full_name or '')),
                "detail_url": self.detail_url(obj.person), "card_title": escape(str(obj.person.full_name or '')), "card_image": obj.person.cover_url, "card_sub": str(obj.role or ''), "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieTitleDataView(BaseSerieTitleContext, AdminDataView):
    columns = [(_('Título'), 'title'), (_('Serie'), 'serie'), (_('Idioma'), 'title_lang'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = SerieTitle.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['title'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "title"),
                "c1": self.link_by(obj, "serie"),
                "c2": cell(obj, "title_lang"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieTitleSelectView(BaseSerieTitle, BaseSelectView):
    search_fields = ['title']


class TypeDataView(BaseType, AdminDataView):
    columns = [(_('Nombre'), 'display_name'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = Type.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['name', 'name_esp'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "display_name"),
                "c1": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class TypeSelectView(BaseType, BaseSelectView):
    search_fields = ['name', 'name_esp']


class SerieLogDataView(BaseSerieLog, AdminDataView):
    columns = [(_('#'), 'id'), (_('Nivel'), 'get_level_display'), (_('Proceso'), 'process'), (_('Mensaje'), 'message'), (_('Momento'), 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = SerieLog.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['process', 'message'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "id"),
                "c1": cell(obj, "get_level_display"),
                "c2": cell(obj, "process"),
                "c3": cell(obj, "message", truncar=120),
                "c4": cell(obj, "timestamp"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)
