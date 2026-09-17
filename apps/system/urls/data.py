"""URLs de DATOS del panel de system: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.system import views as v


urlpatterns = [
    # ---------- cloud-file · CloudFile ----------
    path('cloud-file/data/', v.CloudFileDataView.as_view(), name='cloud-file_data'),

    # ---------- import-cursor · ImportCursor ----------
    path('import-cursor/data/', v.ImportCursorDataView.as_view(), name='import-cursor_data'),

    # ---------- scheduled-task · ScheduledTask ----------
    path('scheduled-task/data/', v.ScheduledTaskDataView.as_view(), name='scheduled-task_data'),

    # ---------- task-run · TaskRun ----------
    path('task-run/data/', v.TaskRunDataView.as_view(), name='task-run_data'),
    path('task-run/data/<str:tipo>/<str:pk>/', v.TaskRunDataView.as_view(), name='task-run_data-by'),

    # ---------- vistas fijas ----------
    path('import-cursor-deezer/data/', v.ImportCursorDeezerDataView.as_view(), name='import-cursor-deezer_data'),
    path('import-cursor-mal/data/', v.ImportCursorMalDataView.as_view(), name='import-cursor-mal_data'),
    path('import-cursor-vndb/data/', v.ImportCursorVndbDataView.as_view(), name='import-cursor-vndb_data'),
]
