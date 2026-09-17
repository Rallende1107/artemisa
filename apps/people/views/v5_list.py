"""people · las listas completas, de gestión y públicas (las «por» viven en v5_list_by.py)."""
from django.utils.translation import gettext_lazy as _

from apps.people.views.base import BasePeopleLog, BasePerson, BasePersonImage, BasePersonLink, BasePersonNickname
from core.shared.views.base import AdminListView, PublicListView


# ==============================================================================
# Gestión
# ==============================================================================


class PersonListView(BasePerson, AdminListView):
    home_url = "panel:people-home"
    data_url = "panel:person_data"
    create_url = "panel:person_create"
    enable_cards = True   # extra de la vista: botones tarjetas/lista
    title = _("Lista de personas")


class PersonImageListView(BasePersonImage, AdminListView):
    home_url = "panel:people-home"
    buttons = (("panel:person-image_download", _("Descargar imágenes"), "cloud-download"),)
    data_url = "panel:person-image_data"
    create_url = "panel:person-image_create"
    title = _("Lista de imágenes extra")


class PersonLinkListView(BasePersonLink, AdminListView):
    home_url = "panel:people-home"
    data_url = "panel:person-link_data"
    create_url = "panel:person-link_create"
    title = _("Lista de enlaces de persona")


class PersonNicknameListView(BasePersonNickname, AdminListView):
    home_url = "panel:people-home"
    data_url = "panel:person-nickname_data"
    create_url = "panel:person-nickname_create"
    title = _("Lista de apodos")


class PeopleLogListView(BasePeopleLog, AdminListView):
    home_url = "panel:people-home"
    buttons = (("panel:task-run_list", _("Tareas"), "list-task"),)   # ejecuciones de tareas (Sistema)
    data_url = "panel:people-log_data"
    create_url = "panel:people-log_create"
    title = _("Lista de log de personas")


# ==============================================================================
# Público
# ==============================================================================


class PersonPublicListView(BasePerson, PublicListView):
    """Catálogo público de personas (actores, directores, autores…)."""
    data_url = "personas:people-catalog-data"
    background_image = "bg-people-person"
    background_fallback = "bg-catalogs-home"
    section = "personas"
    title = _("Personas")
    icon = "bi-people"
    subtitle = _("Actores, directores, autores y más.")
    home_url = "personas:home"
    home_label = _("personas")


class CinePersonPublicListView(BasePerson, PublicListView):
    data_url = "personas:film-catalog-data"
    background_image = "bg-people-person"
    background_fallback = "bg-catalogs-home"
    section = "personas"
    title = _("Personas de cine")
    icon = "bi-people"
    home_url = "personas:home"
    home_label = _("cine")


class TvPersonPublicListView(BasePerson, PublicListView):
    data_url = "personas:tv-catalog-data"
    background_image = "bg-people-person"
    background_fallback = "bg-catalogs-home"
    section = "personas"
    title = _("Personas de TV")
    icon = "bi-people"
    home_url = "personas:home"
    home_label = _("tv")


class OtakuPersonPublicListView(BasePerson, PublicListView):
    data_url = "personas:otaku-catalog-data"
    background_image = "bg-otaku-person"
    background_fallback = "bg-people-person"
    section = "personas"
    title = _("Personas de anime y manga")
    icon = "bi-people"
    home_url = "personas:home"
    home_label = _("anime y manga")


class VoicePersonPublicListView(BasePerson, PublicListView):
    data_url = "personas:voices-catalog-data"
    background_image = "bg-otaku-person"
    background_fallback = "bg-people-person"
    section = "personas"
    title = _("Actores de voz")
    icon = "bi-people"
    home_url = "personas:home"
    home_label = _("voces")
