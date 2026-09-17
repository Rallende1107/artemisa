"""people · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from apps.otaku.views.v2_filters import AnimeStaffFilters, MangaAuthorFilters, VoiceFilters
from apps.people.models import PeopleLog, Person, PersonImage, PersonLink, PersonNickname
from apps.people.views.base import _DOMINIOS, BasePeopleLog, BasePerson, BasePersonContext, BasePersonImage, BasePersonImageContext, BasePersonLink, BasePersonLinkContext, BasePersonNickname, BasePersonNicknameContext
from apps.people.views.v2_filters import PersonAdminFilters, PersonFilters
from core.shared.views.base import AdminDataView, BaseSelectView, PublicDataView
from core.shared.views.filters import ImagenesFilters, LogFilters
from core.utils.queries import con_nube
from core.utils.views_base import cell, cell_cover, cell_miniatura, meta_line


# ==============================================================================
# Gestión
# ==============================================================================


class PersonPublicDataView(BasePersonContext, PublicDataView):
    dominio = ""               # cine / tv / otaku / voces en las subclases
    columns = [(_("Nombre"), "ficha"), (_("País"), "country")]
    filters = PersonFilters
    priority = {"ficha": 1}
    filters_by = {"voces-anime": VoiceFilters, "equipo-anime": AnimeStaffFilters, "autores-manga": MangaAuthorFilters, "voces-personaje": VoiceFilters}
    detail_url_name = "personas:person-detail"

    def get(self, request, tipo=None, pk=None):
        qs = Person.objects.all()
        qs = qs.filter(_DOMINIOS[self.dominio]).distinct() if self.dominio else qs
        p, total, filtrado, objetos = self.query(request, qs, ["full_name", "nicknames__nickname"], {'ficha': 'full_name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.full_name or ''), meta_line(obj)),
                "c1": cell(obj, "country"),
                "acciones": self.row_actions(obj, request, str(obj.full_name or '')),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.full_name or '')), "card_image": obj.cover_url, "card_sub": self.sub(obj) or "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PersonDataView(BasePersonContext, AdminDataView):
    columns = [(_('Nombre'), "ficha"), (_('País'), 'country'), (_('Nacimiento'), 'birth_date'), (_('Activo'), 'is_active')]
    filters = PersonAdminFilters
    priority = {"full_name": 1, "is_active": 2, "country": 3}

    def get(self, request, tipo=None, pk=None):
        qs = Person.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['full_name', 'nicknames__nickname'], {'ficha': 'full_name'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(self.detail_url(obj), obj.cover_url, str(obj.full_name or ''), meta_line(obj)),
                "c1": self.link_by(obj, "country"),
                "c2": cell(obj, "birth_date"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj.full_name or '')), "card_image": obj.cover_url, "card_sub": self.sub(obj) or "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

    def prepare(self, request, objetos):
        """Los enlaces a la ficha MAL de toda la página, en UNA consulta (no una por fila)."""
        super().prepare(request, objetos)
        from apps.otaku import fichas_mal
        self._fichas_mal = fichas_mal.enlaces("person", [o.pk for o in objetos])

    def extra_row_actions(self, obj, request):
        from apps.otaku import fichas_mal
        return fichas_mal.menu("person", obj, getattr(self, "_fichas_mal", None))


class PersonSelectView(BasePerson, BaseSelectView):
    search_fields = ['full_name', 'nicknames__nickname']


class CinePersonPublicDataView(PersonPublicDataView):
    dominio = "cine"


class TvPersonPublicDataView(PersonPublicDataView):
    dominio = "tv"


class OtakuPersonPublicDataView(PersonPublicDataView):
    dominio = "otaku"


class VoicePersonPublicDataView(PersonPublicDataView):
    dominio = "voces"


class PersonImageDataView(BasePersonImageContext, AdminDataView):
    columns = [(_('Imagen'), 'miniatura'), (_('Persona'), 'person'), (_('Orden'), 'order'), (_('URL'), 'image_url'), (_('Estado'), 'estado_descarga'), (_('Intentos'), 'download_attempts'), (_('Error'), 'download_error'), (_('En la nube'), 'en_nube'), (_('Activo'), 'is_active')]
    filters = ImagenesFilters

    def filtrar(self, qs):
        """Las listas FIJAS (p. ej. «(MAL)») acotan aquí; la general no."""
        return qs

    def get(self, request, tipo=None, pk=None):
        qs = self.filtrar(con_nube(PersonImage.objects.select_related("person")))
        p, total, filtrado, objetos = self.query(request, qs, ['image_url'], {'en_nube': 'en_nube'}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell_miniatura(obj),
                "c1": self.link_by(obj, "person"),
                "c2": cell(obj, "order"),
                "c3": cell(obj, "image_url", truncar=60),
                "c4": cell(obj, "estado_descarga"),
                "c5": cell(obj, "download_attempts"),
                "c6": cell(obj, "download_error", truncar=40),
                "c7": cell(obj, "en_nube"),
                "c8": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(getattr(obj, "person", "") or obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)

class PersonImageSelectView(BasePersonImage, BaseSelectView):
    search_fields = ['image_url']


class PersonImagesPublicDataView(BasePersonImageContext, PublicDataView):
    """Galería de un persona: sus imágenes extra en tarjetas."""
    columns = [(_("Imagen"), "image")]
    actions = False

    def get(self, request, tipo=None, pk=None):
        qs = PersonImage.objects.all()
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


class PersonLinkDataView(BasePersonLinkContext, AdminDataView):
    columns = [(_('Persona'), 'person'), (_('Fuente'), 'source'), (_('URL'), 'url'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = PersonLink.objects.select_related("person", "source")
        p, total, filtrado, objetos = self.query(request, qs, ['url', 'external_id', 'person__full_name'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": self.link_by(obj, "person"),
                "c1": cell(obj, "source"),
                "c2": cell(obj, "url"),
                "c3": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PersonLinkSelectView(BasePersonLink, BaseSelectView):
    search_fields = ['url', 'external_id']


class PersonNicknameDataView(BasePersonNicknameContext, AdminDataView):
    columns = [(_('Apodo'), 'nickname'), (_('Persona'), 'person'), (_('Activo'), 'is_active')]

    def get(self, request, tipo=None, pk=None):
        qs = PersonNickname.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['nickname'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "nickname"),
                "c1": self.link_by(obj, "person"),
                "c2": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PersonNicknameSelectView(BasePersonNickname, BaseSelectView):
    search_fields = ['nickname']


class PeopleLogDataView(BasePeopleLog, AdminDataView):
    columns = [('Nivel', 'get_level_display'), ('Proceso', 'process'), ('Mensaje', 'message'), ('Momento', 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = PeopleLog.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, ['process', 'message'], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "get_level_display"),
                "c1": cell(obj, "process"),
                "c2": cell(obj, "message", truncar=120),
                "c3": cell(obj, "timestamp"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)
