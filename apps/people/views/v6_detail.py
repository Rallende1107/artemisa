"""people · fichas, de gestión y públicas."""
from django.utils.translation import gettext_lazy as _

from apps.people.views.base import BasePeopleLog, BasePerson, BasePersonImage, BasePersonLink, BasePersonNickname
from core.shared.views.base import BaseAdminDetailView, BasePublicDetailView


# ==============================================================================
# Gestión
# ==============================================================================


class PersonDetailView(BasePerson, BaseAdminDetailView):
    template_name = "people/detail/person.html"
    update_url = "panel:person_update"
    delete_url = "panel:person_delete"
    list_url = "panel:person_list"
    toggle_url = "panel:person_toggle"
    by_url = "panel:person_by"
    tabs = [("voces", _("Voces"), "panel:character-voice_by", "persona"),
            ("peliculas", _("Cine · reparto"), "panel:movie-cast_by", "persona"),
            ("peliculas_equipo", _("Cine · equipo"), "panel:movie-staff_by", "persona"),
            ("series", _("Series · reparto"), "panel:serie-cast_by", "persona"),
            ("series_equipo", _("Series · equipo"), "panel:serie-staff_by", "persona"),
            ("animes", _("Anime"), "panel:anime-staff_by", "persona"),
            ("mangas", _("Manga"), "panel:manga-author_by", "persona"),
            ("imagenes", _("Imágenes"), "panel:person-image_by", "persona"),
            ("apodos", _("Apodos"), "panel:person-nickname_by", "persona")]

    def acciones_extra(self, obj):
        """«Añadir ficha MAL» / «Ficha MAL» (la ficha vive en otaku; aquí solo se enlaza)."""
        from apps.otaku import fichas_mal
        e = fichas_mal.enlace("person", obj.pk)
        return [e] if e else []


class PersonImageDetailView(BasePersonImage, BaseAdminDetailView):
    template_name = "people/detail/person_image.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:person-image_update"
    delete_url = "panel:person-image_delete"
    list_url = "panel:person-image_list"
    toggle_url = "panel:person-image_toggle"


class PersonLinkDetailView(BasePersonLink, BaseAdminDetailView):
    template_name = "people/detail/person_link.html"   # el detail PROPIO de la entidad
    update_url = "panel:person-link_update"
    delete_url = "panel:person-link_delete"
    list_url = "panel:person-link_list"
    toggle_url = "panel:person-link_toggle"


class PersonNicknameDetailView(BasePersonNickname, BaseAdminDetailView):
    template_name = "people/detail/person_nickname.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    update_url = "panel:person-nickname_update"
    delete_url = "panel:person-nickname_delete"
    list_url = "panel:person-nickname_list"
    toggle_url = "panel:person-nickname_toggle"


class PeopleLogDetailView(BasePeopleLog, BaseAdminDetailView):
    template_name = "people/detail/people_log.html"   # el detail PROPIO de la entidad (hoy extiende el cuadro compartido)
    list_url = "panel:people-log_list"
    section_label = "Personas"


# ==============================================================================
# Público
# ==============================================================================


class PersonPublicDetailView(BasePerson, BasePublicDetailView):
    """Ficha pública de una persona: el mismo HTML que en gestión, sin botones y con la colección."""
    template_name = "people/detail/person.html"
    list_url = "personas:people-catalog"
    by_url = "personas:people-by"
    section = "personas"
    collect_kind = "person"
    tabs = [("voces", _("Roles de voz"), "otaku:characters-by", "persona"),
            ("peliculas", _("Cine"), "movies:movies-by", "persona"),
            ("series", _("Series"), "series:series-by", "persona"),
            ("animes", _("Anime"), "otaku:anime-by", "persona"),
            ("mangas", _("Manga"), "otaku:manga-by", "persona"),
            ("imagenes", _("Imágenes"), "personas:person-images-by", "persona")]
