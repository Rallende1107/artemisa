"""companies · listas «por» (ListBy): «Imágenes de X». El mapa `filter_config` vive en base.py y lo comparte con la Data."""
from apps.companies.views.base import BaseCompanyImageContext
from core.shared.views.base import AdminListByView


# ==============================================================================
# Gestión
# ==============================================================================


class CompanyImageListByView(BaseCompanyImageContext, AdminListByView):
    """compania."""
    home_url = "panel:companies-home"
    data_url = "panel:company-image_data-by"
    full_list_url = "panel:company-image_list"
    create_url = "panel:company-image_create"
