"""collections · Datas (JSON de DataTables) y Selects, de gestión y públicas."""
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import get_language, gettext_lazy as _

from apps.collections.models import AlbumCollection, AnimeCollection, ArtistCollection, CharacterCollection, CollectionLog, CompanyCollection, GameCharacterCollection, GameCollection, MangaCollection, ModelBaseCollection, MovieCollection, PersonCollection, SerieCollection, SongCollection
from apps.collections.views.base import BaseAlbumCollection, BaseAnimeCollection, BaseArtistCollection, BaseCharacterCollection, BaseCollectionLog, BaseCompanyCollection, BaseGameCharacterCollection, BaseGameCollection, BaseMangaCollection, BaseMovieCollection, BasePersonCollection, BaseSerieCollection, BaseSongCollection
from apps.collections.views.v2_filters import AlbumCollectionAdminFilters, AlbumCollectionFilters, AnimeCollectionAdminFilters, AnimeCollectionFilters, ArtistCollectionAdminFilters, ArtistCollectionFilters, CharacterCollectionAdminFilters, CharacterCollectionFilters, CompanyCollectionAdminFilters, CompanyCollectionFilters, GameCharacterCollectionAdminFilters, GameCharacterCollectionFilters, GameCollectionAdminFilters, GameCollectionFilters, MangaCollectionAdminFilters, MangaCollectionFilters, MovieCollectionAdminFilters, MovieCollectionFilters, PersonCollectionAdminFilters, PersonCollectionFilters, SerieCollectionAdminFilters, SerieCollectionFilters, SongCollectionAdminFilters, SongCollectionFilters
from core.shared.views.base import AdminDataView, PublicDataView
from core.shared.views.filters import LogFilters
from core.utils.views_base import cell, cell_cover, meta_line


# ==============================================================================
# Gestión
# ==============================================================================

# Colecciones (moderación): quién, qué, cómo lo sigue.
COL_COLUMNS = [(_("Usuario"), "user"), (_("Contenido"), "content"), (_("Estado"), "status"),
               (_("Nota"), "score"), (_("Favorito"), "is_favorite"), (_("Añadido"), "created_at"), (_("Activo"), "is_active")]
# Estados: nombre EN (ES) en una sola columna, búsqueda por los dos.
USUARIO_SEARCH = ["user__username", "user__email"]


def _nombre(obj):
    """Nombre en el idioma del sitio (solo hay inglés y español): name_esp si estamos en español y existe."""
    if obj is None:
        return ""
    esp = (getattr(obj, "name_esp", "") or "").strip()
    return esp if esp and (get_language() or "").startswith("es") else str(getattr(obj, "name", obj))


class BaseCollectionData(PublicDataView):
    """Mi colección: las 10 tablas comparten columnas y celdas (estado y nota editables en línea, dónde lo veo);
    cada tabla pone su búsqueda, su orden y sus filtros. Solo MIS filas."""
    login_only = True
    columns = [(_("Título"), "ficha"), (_("Estado"), "estado"), (_("Nota"), "nota"), (_("Favorito"), "is_favorite"), (_("Dónde"), "donde")]
    no_order = ("donde",)
    priority = {"ficha": 1, "estado": 2, "nota": 3, "is_favorite": 4}
    search_fields = []
    order_map = {"estado": "status", "nota": "score"}

    def get(self, request, tipo=None, pk=None):
        M = self.model
        qs = M.objects.filter(user=request.user).select_related("content", "watch_site", "download_site", "download_format", "download_quality")
        p, total, filtrado, objetos = self.query(request, qs, self.search_fields, self.order_map, ("-id",))
        estados, medio = M.estados(), M.medio()
        filas = []
        for obj in objetos:
            c = obj.content
            titulo = str(getattr(c, "title", None) or getattr(c, "name", None) or getattr(c, "full_name", None) or c)
            url = c.get_absolute_url()
            estado = self._select_estado(obj, estados, medio)
            editar = reverse("collections:edit", args=[medio, obj.pk])
            filas.append({
                "id": obj.pk,
                "c0": cell_cover(url, c.cover_url, titulo, meta_line(c)),
                "c1": estado or "—",
                "c2": self._select_nota(obj, medio),
                "c3": cell(obj, "is_favorite"),
                "c4": self._donde(obj),
                "acciones": self._menu(obj, medio, titulo, url),
                "detail_url": url, "card_title": escape(titulo), "card_image": c.cover_url,
                "card_sub": str(getattr(c, "release_year", None) or getattr(c, "year", None) or ""),
                "card_actions": estado + f'<a class="card-btn" href="{editar}" title="{_("Editar en mi colección")}"><i class="bi bi-pencil"></i></a>',
            })
        return self.response(p, total, filtrado, filas)

    # ---- celdas propias de la colección
    def _select_estado(self, obj, estados, medio):
        """<select> del estado, guarda al vuelo (collections:update); "" si el medio no tiene estados."""
        if not estados:
            return ""
        update_url = reverse("collections:update", args=[medio, obj.pk])
        partes = [f'<select class="st-inline" data-url="{update_url}" data-campo="status" aria-label="{_("Estado")}">',
                  f'<option value="">{_("sin estado")}</option>']
        for clave, nombre in estados:
            sel = " selected" if obj.status == clave else ""
            partes.append(f'<option value="{clave}"{sel}>{escape(nombre)}</option>')
        return "".join(partes) + "</select>"

    def _select_nota(self, obj, medio):
        """Nota 1-10 como número, editable en línea."""
        update_url = reverse("collections:update", args=[medio, obj.pk])
        return "".join([f'<select class="st-inline" data-url="{update_url}" data-campo="score" aria-label="{_("Nota")}"><option value="">—</option>']
                       + [f'<option value="{n}"{" selected" if obj.score == n else ""}>{n}</option>' for n in range(1, 11)] + ["</select>"])

    def _donde(self, obj):
        """Dónde lo veo y de dónde lo descargué (sitio · formato · calidad); se edita en «Editar»."""
        lineas = []
        if obj.watch_site_id:
            lineas.append(f'<span class="dt-linea"><span class="dt-k">{_("Veo")}</span> {escape(_nombre(obj.watch_site))}</span>')
        desc = [escape(_nombre(x)) for x in (obj.download_site, obj.download_format, obj.download_quality) if x]
        if desc:
            lineas.append(f'<span class="dt-linea"><span class="dt-k">{_("Descarga")}</span> {" · ".join(desc)}</span>')
        return "".join(lineas) if lineas else "—"

    def _menu(self, obj, medio, titulo, ficha):
        """Menú de fila: Ver ficha · Editar · favorito · Quitar."""
        ver = f'<a role="menuitem" href="{ficha}"><i class="bi bi-eye ic"></i> {_("Ver ficha")}</a>' if ficha else ""
        editar = f'<a role="menuitem" href="{reverse("collections:edit", args=[medio, obj.pk])}"><i class="bi bi-pencil ic"></i> {_("Editar")}</a>'
        update_url = reverse("collections:update", args=[medio, obj.pk])
        fav = (f'<a role="menuitem" class="js-fav" href="#" data-url="{update_url}" data-value="{"0" if obj.is_favorite else "1"}">'
               f'<i class="bi bi-star{"-fill" if obj.is_favorite else ""} ic"></i> {_("Quitar favorito") if obj.is_favorite else _("Marcar favorito")}</a>')
        quitar = (f'<a role="menuitem" class="row-menu__danger js-quitar" href="{reverse("collections:remove", args=[medio, obj.pk])}" '
                  f'data-name="{escape(titulo)}"><i class="bi bi-trash ic"></i> {_("Quitar")}</a>')
        return ('<div class="row-menu"><button type="button" class="row-menu__btn" aria-haspopup="true" aria-expanded="false">'
                f'<span>{_("Acciones")}</span><span class="row-menu__caret">▾</span></button>'
                f'<div class="row-menu__list" role="menu">{ver}{editar}{fav}{quitar}</div></div>')


class AlbumCollectionDataView(BaseAlbumCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = AlbumCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = AlbumCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__title"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AlbumCollectionPublicDataView(BaseAlbumCollection, BaseCollectionData):
    search_fields = ["content__title"]
    order_map = {"ficha": "content__title", "estado": "status", "nota": "score"}
    filters = AlbumCollectionFilters


# ---------------------------------------------------------------- colecciones
class AnimeCollectionDataView(BaseAnimeCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = AnimeCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = AnimeCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__title"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class AnimeCollectionPublicDataView(BaseAnimeCollection, BaseCollectionData):
    search_fields = ["content__title"]
    order_map = {"ficha": "content__title", "estado": "status", "nota": "score"}
    filters = AnimeCollectionFilters


class ArtistCollectionDataView(BaseArtistCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = ArtistCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = ArtistCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class ArtistCollectionPublicDataView(BaseArtistCollection, BaseCollectionData):
    search_fields = ["content__name"]
    order_map = {"ficha": "content__name", "estado": "status", "nota": "score"}
    filters = ArtistCollectionFilters


class CharacterCollectionDataView(BaseCharacterCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = CharacterCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = CharacterCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__full_name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CharacterCollectionPublicDataView(BaseCharacterCollection, BaseCollectionData):
    search_fields = ["content__full_name"]
    order_map = {"ficha": "content__full_name", "estado": "status", "nota": "score"}
    filters = CharacterCollectionFilters


class CompanyCollectionDataView(BaseCompanyCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = CompanyCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = CompanyCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class CompanyCollectionPublicDataView(BaseCompanyCollection, BaseCollectionData):
    search_fields = ["content__name"]
    order_map = {"ficha": "content__name", "estado": "status", "nota": "score"}
    filters = CompanyCollectionFilters


class GameCharacterCollectionDataView(BaseGameCharacterCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = GameCharacterCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = GameCharacterCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameCharacterCollectionPublicDataView(BaseGameCharacterCollection, BaseCollectionData):
    search_fields = ["content__name"]
    order_map = {"ficha": "content__name", "estado": "status", "nota": "score"}
    filters = GameCharacterCollectionFilters


class GameCollectionDataView(BaseGameCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = GameCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = GameCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__title"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class GameCollectionPublicDataView(BaseGameCollection, BaseCollectionData):
    search_fields = ["content__title"]
    order_map = {"ficha": "content__title", "estado": "status", "nota": "score"}
    filters = GameCollectionFilters


class MangaCollectionDataView(BaseMangaCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = MangaCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = MangaCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__title"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MangaCollectionPublicDataView(BaseMangaCollection, BaseCollectionData):
    search_fields = ["content__title"]
    order_map = {"ficha": "content__title", "estado": "status", "nota": "score"}
    filters = MangaCollectionFilters


class MovieCollectionDataView(BaseMovieCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = MovieCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = MovieCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__title", "content__title_secundary"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class MovieCollectionPublicDataView(BaseMovieCollection, BaseCollectionData):
    search_fields = ["content__title", "content__title_secundary"]
    order_map = {"ficha": "content__title", "estado": "status", "nota": "score"}
    filters = MovieCollectionFilters


class PersonCollectionDataView(BasePersonCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = PersonCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = PersonCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__full_name"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class PersonCollectionPublicDataView(BasePersonCollection, BaseCollectionData):
    search_fields = ["content__full_name"]
    order_map = {"ficha": "content__full_name", "estado": "status", "nota": "score"}
    filters = PersonCollectionFilters


class SerieCollectionDataView(BaseSerieCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = SerieCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = SerieCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__title", "content__title_secundary"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SerieCollectionPublicDataView(BaseSerieCollection, BaseCollectionData):
    search_fields = ["content__title", "content__title_secundary"]
    order_map = {"ficha": "content__title", "estado": "status", "nota": "score"}
    filters = SerieCollectionFilters


class SongCollectionDataView(BaseSongCollection, AdminDataView):
    columns = COL_COLUMNS
    filters = SongCollectionAdminFilters

    def get(self, request, tipo=None, pk=None):
        qs = SongCollection.objects.all()
        p, total, filtrado, objetos = self.query(request, qs, USUARIO_SEARCH + ["content__title"], {}, ())
        filas = []
        for obj in objetos:
            filas.append({
                "id": obj.pk,
                "c0": cell(obj, "user"),
                "c1": cell(obj, "content"),
                "c2": cell(obj, "status"),
                "c3": cell(obj, "score"),
                "c4": cell(obj, "is_favorite"),
                "c5": cell(obj, "created_at"),
                "c6": cell(obj, "is_active"),
                "acciones": self.row_actions(obj, request),
                "detail_url": self.detail_url(obj), "card_title": escape(str(obj)), "card_image": obj.cover_url, "card_sub": "", "card_actions": "",
            })
        return self.response(p, total, filtrado, filas)


class SongCollectionPublicDataView(BaseSongCollection, BaseCollectionData):
    search_fields = ["content__title"]
    order_map = {"ficha": "content__title", "estado": "status", "nota": "score"}
    filters = SongCollectionFilters


# ---------------------------------------------------------------- registro
class CollectionLogDataView(BaseCollectionLog, AdminDataView):
    columns = [(_('Nivel'), 'get_level_display'), (_('Proceso'), 'process'), (_('Mensaje'), 'message'), (_('Momento'), 'timestamp')]
    filters = LogFilters

    def get(self, request, tipo=None, pk=None):
        qs = CollectionLog.objects.all()
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


# Una URL por tipo (/collection/<medio>/data/): despacha a la Data del medio.
DATAS = {t.medio(): globals()[f"{t.__name__}PublicDataView"] for t in ModelBaseCollection.tablas()}   # la Data del USUARIO (sus filas), no la de gestión


def collection_data(request, tipo):
    from apps.collections.views.base import _tabla_o_404
    tabla = _tabla_o_404(tipo)
    return DATAS[tabla.medio()].as_view()(request, tipo=tipo)
