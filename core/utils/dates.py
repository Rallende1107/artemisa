"""Fechas para pintar (utilidad genérica, estilo Poseidón): un solo formato corto en todo el sitio.

Sin `locale.setlocale`: es global al proceso y no es seguro con hilos en un servidor web. Los nombres de mes los
traduce Django (`date_format` + el idioma activo), y las fechas con hora se pasan a la zona horaria del sitio."""
import datetime

from django.utils import timezone
from django.utils.formats import date_format


class DateUtils:
    FECHA = "d M, Y"                  # 12 sep, 2026
    FECHA_HORA = "d M, Y - H:i:s"     # 12 sep, 2026 - 00:35:49

    @staticmethod
    def calculate_age(birth_date):
        """Edad en años cumplidos a hoy, o None sin fecha."""
        if not birth_date:
            return None
        today = datetime.date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    @staticmethod
    def format_datetime_fields(dt):
        """Fecha → «12 sep, 2026»; fecha con hora → «12 sep, 2026 - 00:35:49» en la hora local del sitio; None → ""."""
        if not dt:
            return ""
        if isinstance(dt, datetime.datetime):
            if timezone.is_aware(dt):
                dt = timezone.localtime(dt)
            return date_format(dt, DateUtils.FECHA_HORA)
        return date_format(dt, DateUtils.FECHA)
