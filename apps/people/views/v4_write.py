"""people · ESCRITURA de gestión: crear, editar y eliminar."""
from django.utils.translation import gettext_lazy as _

from apps.people import forms as f
from apps.people.views.base import BasePeopleLog, BasePerson, BasePersonImage, BasePersonLink, BasePersonNickname
from core.shared.views.base import BaseCreate, BaseDelete, BaseUpdate


# ==============================================================================
# Gestión
# ==============================================================================


class PersonCreateView(BasePerson, BaseCreate):
    # Django core
    form_class = f.PersonForm
    form_template = "people/form/person.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person_list"
    success_url = "panel:person_list"
    cancel_url = "panel:person_list"
    # UX
    success_message = _("Persona «%(obj)s» creada.")
    title = _("Crear persona")


class PersonUpdateView(BasePerson, BaseUpdate):
    # Django core
    form_class = f.PersonForm
    form_template = "people/form/person.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person_list"
    success_url = "panel:person_list"
    cancel_url = "panel:person_list"
    # UX
    success_message = _("Persona «%(obj)s» actualizada.")
    title = _("Editar persona")


class PersonDeleteView(BasePerson, BaseDelete):
    list_url = "panel:person_list"
    success_url = "panel:person_list"
    cancel_url = "panel:person_list"
    success_message = _("Persona «%(obj)s» eliminada.")
    title = _("Eliminar persona")


class PersonImageCreateView(BasePersonImage, BaseCreate):
    # Django core
    form_class = f.PersonImageForm
    form_template = "people/form/person_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-image_list"
    success_url = "panel:person-image_list"
    cancel_url = "panel:person-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» creada.")
    title = _("Crear imagen")


class PersonImageUpdateView(BasePersonImage, BaseUpdate):
    # Django core
    form_class = f.PersonImageForm
    form_template = "people/form/person_image.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-image_list"
    success_url = "panel:person-image_list"
    cancel_url = "panel:person-image_list"
    # UX
    success_message = _("Imagen «%(obj)s» actualizada.")
    title = _("Editar imagen")


class PersonImageDeleteView(BasePersonImage, BaseDelete):
    list_url = "panel:person-image_list"
    success_url = "panel:person-image_list"
    cancel_url = "panel:person-image_list"
    success_message = _("Imagen «%(obj)s» eliminada.")
    title = _("Eliminar imagen")


class PersonLinkCreateView(BasePersonLink, BaseCreate):
    # Django core
    form_class = f.PersonLinkForm
    form_template = "people/form/person_link.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-link_list"
    success_url = "panel:person-link_list"
    cancel_url = "panel:person-link_list"
    # UX
    success_message = _("Enlace «%(obj)s» creado.")
    title = _("Crear enlace")


class PersonLinkUpdateView(BasePersonLink, BaseUpdate):
    # Django core
    form_class = f.PersonLinkForm
    form_template = "people/form/person_link.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-link_list"
    success_url = "panel:person-link_list"
    cancel_url = "panel:person-link_list"
    # UX
    success_message = _("Enlace «%(obj)s» actualizado.")
    title = _("Editar enlace")


class PersonLinkDeleteView(BasePersonLink, BaseDelete):
    list_url = "panel:person-link_list"
    success_url = "panel:person-link_list"
    cancel_url = "panel:person-link_list"
    success_message = _("Enlace «%(obj)s» eliminado.")
    title = _("Eliminar enlace")


class PersonNicknameCreateView(BasePersonNickname, BaseCreate):
    # Django core
    form_class = f.PersonNicknameForm
    form_template = "people/form/person_nickname.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-nickname_list"
    success_url = "panel:person-nickname_list"
    cancel_url = "panel:person-nickname_list"
    # UX
    success_message = _("Apodo «%(obj)s» creado.")
    title = _("Crear apodo")


class PersonNicknameUpdateView(BasePersonNickname, BaseUpdate):
    # Django core
    form_class = f.PersonNicknameForm
    form_template = "people/form/person_nickname.html"   # HTML de campos que incluye el cuadro admin_panel/form.html
    list_url = "panel:person-nickname_list"
    success_url = "panel:person-nickname_list"
    cancel_url = "panel:person-nickname_list"
    # UX
    success_message = _("Apodo «%(obj)s» actualizado.")
    title = _("Editar apodo")


class PersonNicknameDeleteView(BasePersonNickname, BaseDelete):
    list_url = "panel:person-nickname_list"
    success_url = "panel:person-nickname_list"
    cancel_url = "panel:person-nickname_list"
    success_message = _("Apodo «%(obj)s» eliminado.")
    title = _("Eliminar apodo")


class PeopleLogCreateView(BasePeopleLog, BaseCreate):
    form_class = f.PeopleLogForm
    form_template = "people/form/people_log.html"
    list_url = "panel:people-log_list"
    success_url = "panel:people-log_list"
    cancel_url = "panel:people-log_list"
    success_message = _("Log «%(obj)s» creado.")
    title = _("Crear log")


class PeopleLogUpdateView(BasePeopleLog, BaseUpdate):
    form_class = f.PeopleLogForm
    form_template = "people/form/people_log.html"
    list_url = "panel:people-log_list"
    success_url = "panel:people-log_list"
    cancel_url = "panel:people-log_list"
    success_message = _("Log «%(obj)s» actualizado.")
    title = _("Editar log")


class PeopleLogDeleteView(BasePeopleLog, BaseDelete):
    list_url = "panel:people-log_list"
    success_url = "panel:people-log_list"
    cancel_url = "panel:people-log_list"
    success_message = _("Log «%(obj)s» eliminado.")
    title = _("Eliminar log")
