"""Contenido editable de las páginas informativas (Nosotros, Términos, Privacidad).
Cada página tiene SU modelo; el contenido se edita en la BD desde el panel (sección
Páginas de /panel/) y las vistas públicas de esta app lo pintan. Venían de `system`
(2026-09-06); las tablas se renombraron system_* → pages_* (migrations/0002)."""
from django.db import models

from core.mixin.models import BooleanDisplayMixin, CoverMixin, DateDisplayMixin
from core.shared.models.abstract import ModelBaseLog


class ModelBaseInfoSection(CoverMixin, models.Model):
    """BASE abstracta de una sección de página informativa: orden, título,
    contenido, activo y auditoría (creado/actualizado). Cada página tiene SU
    modelo — responsabilidades separadas: AboutSection (Nosotros),
    TermsSection (Términos) y PrivacySection (Privacidad). El contenido del
    sitio se edita en la BD desde el panel; el HTML no se toca."""

    order = models.PositiveSmallIntegerField(verbose_name="orden", default=0)
    title = models.CharField(verbose_name="título", max_length=120)
    body = models.TextField(verbose_name="contenido")
    is_active = models.BooleanField(verbose_name="activo", default=True)
    created_at = models.DateTimeField(verbose_name="creado", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["order", "pk"]

    def __str__(self):
        return self.title


class AboutSection(DateDisplayMixin, BooleanDisplayMixin, ModelBaseInfoSection):
    """Sección de la página NOSOTROS."""
    class Meta(ModelBaseInfoSection.Meta):
        verbose_name = "sección de nosotros"
        verbose_name_plural = "secciones de nosotros"


class PrivacySection(DateDisplayMixin, BooleanDisplayMixin, ModelBaseInfoSection):
    """Sección de la página PRIVACIDAD."""
    class Meta(ModelBaseInfoSection.Meta):
        verbose_name = "sección de privacidad"
        verbose_name_plural = "secciones de privacidad"


class TermsSection(DateDisplayMixin, BooleanDisplayMixin, ModelBaseInfoSection):
    """Sección de la página TÉRMINOS DE USO."""
    class Meta(ModelBaseInfoSection.Meta):
        verbose_name = "sección de términos"
        verbose_name_plural = "secciones de términos"


class PagesLog(ModelBaseLog):
    """Log de la app: auditoría del panel (altas, ediciones, borrados, toggles) y
    cualquier proceso propio. Una tabla por app, para no amontonar."""
    class Meta(ModelBaseLog.Meta):
        verbose_name = "log de páginas"
        verbose_name_plural = "logs de páginas"
