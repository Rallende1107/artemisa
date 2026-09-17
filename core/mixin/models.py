"""MIXINS de MODELO (estilo Poseidón): propiedades listas para pintar, para que las plantillas no lleven filtros
(`|date:"…"`, `|yesno:…`) repetidos en cada archivo. Los llevan TODAS las bases abstractas (models_abstract.py) y los
modelos que no heredan de una base. Si el modelo no tiene el campo, la propiedad devuelve ""."""
from django.utils.translation import gettext_lazy as _

from core.utils.dates import DateUtils


class CoverMixin:
    """`obj.cover_url` / `{{ object.cover_url }}`: la URL de la PORTADA del objeto (su `image`; si no, la primera de
    `images`; si esa aún no se descargó, su URL remota) o "". La llevan todas las bases y los modelos sueltos.
    Nada que ver con el FONDO de pantalla de una vista (resolve_background)."""

    @property
    def cover_url(self):
        from core.utils.public import resolve_cover
        return resolve_cover(self) or ""


class DateDisplayMixin:
    """Fechas en el formato único del sitio (DateUtils): `{{ object.display_created }}`, `{{ object.display_release_date }}`…"""

    def display_date(self, field_name):
        return DateUtils.format_datetime_fields(getattr(self, field_name, None))

    @property
    def display_created(self):
        return self.display_date("created_at")

    @property
    def display_updated(self):
        return self.display_date("updated_at")

    @property
    def display_timestamp(self):
        return self.display_date("timestamp")

    @property
    def display_release_date(self):
        return self.display_date("release_date")

    @property
    def display_birth_date(self):
        return self.display_date("birth_date")

    @property
    def display_last_login(self):
        return self.display_date("last_login")

    @property
    def display_date_joined(self):
        return self.display_date("date_joined")

    @property
    def display_age(self):
        return DateUtils.calculate_age(getattr(self, "birth_date", None))


class BooleanDisplayMixin:
    """Booleanos como «Sí» / «No» (traducido): `{{ object.display_is_active }}`, `{{ object.display_explicit }}`…
    `display_bool("campo")` sirve para cualquier otro; las propiedades cubren los campos booleanos del proyecto."""

    def display_bool(self, field_name):
        valor = getattr(self, field_name, None)
        if valor is None:
            return ""
        return _("Sí") if valor else _("No")

    @property
    def display_is_active(self):
        return self.display_bool("is_active")

    @property
    def display_is_favorite(self):
        return self.display_bool("is_favorite")

    @property
    def display_explicit(self):
        return self.display_bool("explicit")

    @property
    def display_data_status(self):
        return self.display_bool("data_status")

    @property
    def display_data_processed(self):
        return self.display_bool("data_processed")

    @property
    def display_image_downloaded(self):
        return self.display_bool("image_downloaded")

    @property
    def display_official(self):
        return self.display_bool("official")

    @property
    def display_patch(self):
        return self.display_bool("patch")

    @property
    def display_freeware(self):
        return self.display_bool("freeware")

    @property
    def display_is_staff(self):
        return self.display_bool("is_staff")

    @property
    def display_is_superuser(self):
        return self.display_bool("is_superuser")
