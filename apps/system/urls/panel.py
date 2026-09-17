"""Rutas de administración de SISTEMA: tareas (ejecuciones + cancelador) y tareas programadas (beat).
Explícitas (estilo Hades). Las incluye core/panel_urls.py como una sección más.

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.system import views as v
from core.views import AdminToggleView


urlpatterns = [
    path('', include('apps.system.urls.data')),        # data · data-by · select (DataTables y AJAX)

    path("tasks/", v.TasksHomeView.as_view(), name="tasks-home"),

    # ---------- cloud-file · CloudFile ----------
    path('cloud-file/', v.CloudFileListView.as_view(), name='cloud-file_list'),
    path('cloud-file/create/', v.CloudFileCreateView.as_view(), name='cloud-file_create'),
    path('cloud-file/<int:pk>/', v.CloudFileDetailView.as_view(), name='cloud-file_detail'),
    path('cloud-file/<int:pk>/update/', v.CloudFileUpdateView.as_view(), name='cloud-file_update'),
    path('cloud-file/<int:pk>/delete/', v.CloudFileDeleteView.as_view(), name='cloud-file_delete'),

    # ---------- import-cursor · ImportCursor ----------
    path('import-cursor/', v.ImportCursorListView.as_view(), name='import-cursor_list'),
    path('import-cursor/create/', v.ImportCursorCreateView.as_view(), name='import-cursor_create'),
    path('import-cursor/<int:pk>/', v.ImportCursorDetailView.as_view(), name='import-cursor_detail'),
    path('import-cursor/<int:pk>/update/', v.ImportCursorUpdateView.as_view(), name='import-cursor_update'),
    path('import-cursor/<int:pk>/delete/', v.ImportCursorDeleteView.as_view(), name='import-cursor_delete'),
    path('import-cursor/<int:pk>/lanzar/', v.ImportCursorLaunchView.as_view(), name='import-cursor_launch'),

    # ---------- scheduled-task · ScheduledTask ----------
    path('scheduled-task/', v.ScheduledTaskListView.as_view(), name='scheduled-task_list'),
    path('scheduled-task/create/', v.ScheduledTaskCreateView.as_view(), name='scheduled-task_create'),
    path('scheduled-task/<int:pk>/', v.ScheduledTaskDetailView.as_view(), name='scheduled-task_detail'),
    path('scheduled-task/<int:pk>/update/', v.ScheduledTaskUpdateView.as_view(), name='scheduled-task_update'),
    path('scheduled-task/<int:pk>/delete/', v.ScheduledTaskDeleteView.as_view(), name='scheduled-task_delete'),
    path('scheduled-task/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.ScheduledTaskListView.model, entity='scheduled-task', label='tarea programada', namespace='panel'),
         name='scheduled-task_toggle'),
    path('scheduled-task/<int:pk>/ejecutar/', v.ScheduledTaskRunView.as_view(), name='scheduled-task_run'),

    # ---------- task-run · TaskRun ----------
    path('task-run/', v.TaskRunListView.as_view(), name='task-run_list'),
    path('task-run/create/', v.TaskRunCreateView.as_view(), name='task-run_create'),
    path('task-run/<int:pk>/', v.TaskRunDetailView.as_view(), name='task-run_detail'),
    path('task-run/<int:pk>/update/', v.TaskRunUpdateView.as_view(), name='task-run_update'),
    path('task-run/<int:pk>/delete/', v.TaskRunDeleteView.as_view(), name='task-run_delete'),
    path('task-run/<int:pk>/cancelar/', v.TaskRunCancelView.as_view(), name='task-run_cancel'),
    path('task-run/<int:pk>/terminar/', v.TaskRunFinishView.as_view(), name='task-run_finish'),
    path('task-run/<str:tipo>/<str:pk>/', v.TaskRunListByView.as_view(), name='task-run_by'),

    # vistas FIJAS de cursor-lote (una URL por cada una)
    path('import-cursor-deezer/', v.ImportCursorDeezerListView.as_view(), name='import-cursor-deezer_list'),
    path('import-cursor-mal/', v.ImportCursorMalListView.as_view(), name='import-cursor-mal_list'),
    path('import-cursor-vndb/', v.ImportCursorVndbListView.as_view(), name='import-cursor-vndb_list'),
]
