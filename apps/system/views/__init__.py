"""Vistas de system como PAQUETE plano (estilo Poseidón): base.py (mixins _Base<Modelo>, mapas _BaseXBy y helpers) y un
archivo por rol con las DOS caras, gestión y público. Este __init__ SOLO re-exporta: `from apps.system import views`
(urls/public.py) y `views as v` (urls/panel.py, urls/data.py) siguen funcionando y cada clase tiene UN archivo dueño."""
from apps.system.views.v1_home import SystemHomeView, TasksHomeView  # noqa: F401,E402
from apps.system.views.v2_filters import TaskRunFilters  # noqa: F401,E402
from apps.system.views.v3_data import TaskRunDataView, ScheduledTaskDataView, CloudFileDataView, ImportCursorDataView, ImportCursorDeezerDataView, ImportCursorMalDataView, ImportCursorVndbDataView, PILDORA  # noqa: F401,E402
from apps.system.views.v4_write import ScheduledTaskCreateView, ScheduledTaskUpdateView, ScheduledTaskDeleteView, ImportCursorCreateView, ImportCursorUpdateView, ImportCursorDeleteView, TaskRunDeleteView, CloudFileDeleteView, CloudFileCreateView, CloudFileUpdateView, TaskRunCreateView, TaskRunUpdateView  # noqa: F401,E402
from apps.system.views.v5_list import TaskRunListView, ScheduledTaskListView, CloudFileListView, ImportCursorListView, ImportCursorDeezerListView, ImportCursorMalListView, ImportCursorVndbListView, TaskRunListByView  # noqa: F401,E402
from apps.system.views.v6_detail import TaskRunDetailView, ScheduledTaskDetailView, CloudFileDetailView, ImportCursorDetailView  # noqa: F401,E402
from apps.system.views.v8_actions import BaseAccionTarea, TaskRunCancelView, TaskRunFinishView, ScheduledTaskRunView, ImportCursorLaunchView  # noqa: F401,E402
