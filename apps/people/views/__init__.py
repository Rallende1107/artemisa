"""Vistas de people como PAQUETE plano (estilo Poseidón): base.py (mixins _Base<Modelo>, mapas _BaseXBy y helpers) y un
archivo por rol con las DOS caras, gestión y público. Este __init__ SOLO re-exporta: `from apps.people import views`
(urls/public.py) y `views as v` (urls/panel.py, urls/data.py) siguen funcionando y cada clase tiene UN archivo dueño."""
from apps.people.views.v1_home import PeopleHomeView, PeoplePublicHomeView, FONDO  # noqa: F401,E402
from apps.people.views.v2_filters import PersonAdminFilters, PersonFilters  # noqa: F401,E402
from apps.people.views.v3_data import PersonDataView, PersonSelectView, PersonNicknameDataView, PersonNicknameSelectView, PersonImageDataView, PersonImageSelectView, PeopleLogDataView, PersonPublicDataView, CinePersonPublicDataView, TvPersonPublicDataView, OtakuPersonPublicDataView, VoicePersonPublicDataView, PersonImagesPublicDataView  # noqa: F401,E402
from apps.people.views.v3_data import PersonLinkDataView, PersonLinkSelectView  # noqa: F401,E402
from apps.people.views.v4_write import PersonCreateView, PersonUpdateView, PersonDeleteView, PersonNicknameCreateView, PersonNicknameUpdateView, PersonNicknameDeleteView, PersonImageCreateView, PersonImageUpdateView, PersonImageDeleteView, PeopleLogCreateView, PeopleLogUpdateView, PeopleLogDeleteView  # noqa: F401,E402
from apps.people.views.v4_write import PersonLinkCreateView, PersonLinkUpdateView, PersonLinkDeleteView  # noqa: F401,E402
from apps.people.views.v5_list import PersonListView, PersonNicknameListView, PersonImageListView, PeopleLogListView, PersonPublicListView, CinePersonPublicListView, TvPersonPublicListView, OtakuPersonPublicListView, VoicePersonPublicListView  # noqa: F401,E402
from apps.people.views.v5_list import PersonLinkListView  # noqa: F401,E402
from apps.people.views.v5_list_by import PersonPublicListByView, PersonImagePublicListByView, PersonListByView, PersonImageListByView, PersonNicknameListByView  # noqa: F401,E402
from apps.people.views.v5_list_by import PersonLinkListByView  # noqa: F401,E402
from apps.people.views.v6_detail import PersonDetailView, PersonNicknameDetailView, PersonImageDetailView, PeopleLogDetailView, PersonPublicDetailView  # noqa: F401,E402
from apps.people.views.v6_detail import PersonLinkDetailView  # noqa: F401,E402
from apps.people.views.v8_images import PersonImageDownloadView  # noqa: F401,E402
