"""Vistas de core como PAQUETE, igual que las apps: v8_actions.py trae las acciones genéricas del panel
(AdminToggleView, AdminBulkView y las constantes TOGGLE_* / BULK_FIELDS). Este __init__ solo re-exporta."""
from core.views.v8_actions import (
    NAMESPACE, TOGGLE_STAFF, TOGGLE_SUPERUSER, TOGGLE_FIELDS, TOGGLE_META, BULK_FIELDS, TOGGLE_DONE,
    AdminToggleView, AdminBulkView, AdminImageActionView,
)
