"""Vistas de companies como PAQUETE plano (estilo Poseidón): base.py (mixins _Base<Modelo>) y un archivo por rol con
las DOS caras, gestión y público. Este __init__ SOLO re-exporta: `from apps.companies import views`."""
from apps.companies.views.v1_home import CompaniesHomeView, CompaniesPublicHomeView  # noqa: F401,E402
from apps.companies.views.v2_filters import CompanyFilters  # noqa: F401,E402
from apps.companies.views.v3_data import CompanyDataView, CompanyMovieDataView, CompanySerieDataView, CompanySelectView, CompanyImageDataView, CompanyImageSelectView, CompanyLogDataView, CompanyPublicDataView  # noqa: F401,E402
from apps.companies.views.v4_write import CompanyCreateView, CompanyUpdateView, CompanyDeleteView, CompanyImageCreateView, CompanyImageUpdateView, CompanyImageDeleteView, CompanyLogCreateView, CompanyLogUpdateView, CompanyLogDeleteView  # noqa: F401,E402
from apps.companies.views.v5_list import CompanyListView, CompanyMovieListView, CompanySerieListView, CompanyImageListView, CompanyLogListView, CompanyPublicListView  # noqa: F401,E402
from apps.companies.views.v5_list_by import CompanyImageListByView  # noqa: F401,E402
from apps.companies.views.v6_detail import CompanyDetailView, CompanyImageDetailView, CompanyLogDetailView, CompanyPublicDetailView  # noqa: F401,E402
from apps.companies.views.v8_images import CompanyImageDownloadView  # noqa: F401,E402
