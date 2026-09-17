"""Validadores de usuarios."""
import re
from datetime import date

from django.core.exceptions import ValidationError


MIN_AGE = 12


def validate_min_age(value):
    """La persona debe tener al menos MIN_AGE años (y no una fecha futura)."""
    if value is None:
        return
    today = date.today()
    if value > today:
        raise ValidationError("La fecha de nacimiento no puede ser futura.")
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < MIN_AGE:
        raise ValidationError(f"Debes tener al menos {MIN_AGE} años.")


def normalizar_telefono_chileno(valor):
    """Normaliza y valida un CELULAR chileno: acepta lo tecleado con +, espacios,
    guiones o sin prefijo («9 8765 4321», «+56987654321»…) y devuelve SIEMPRE el
    formato canónico «+56 9 XXXXXXXX». Vacío se respeta (el campo es opcional).
    Rechaza cualquier cosa que no sea 56 + 9 + 8 dígitos."""
    if not valor or not valor.strip():
        return ""
    # Solo dígitos y separadores (+, espacio, guion, paréntesis): «569…dddd» no cuela.
    if re.search(r"[^\d\s+\-()]", valor):
        raise ValidationError("Teléfono chileno: +56 9 seguido de 8 dígitos (ej: +56 9 87654321).")
    digitos = "".join(c for c in valor if c.isdigit())
    if len(digitos) == 9 and digitos.startswith("9"):
        digitos = "56" + digitos          # tecleó sin el 56
    if len(digitos) != 11 or not digitos.startswith("569"):
        raise ValidationError("Teléfono chileno: +56 9 seguido de 8 dígitos (ej: +56 9 87654321).")
    return f"+56 9 {digitos[3:]}"
