"""URLs del panel para users (sección «Usuarios»). Se montan en `panel`
vía core/panel_urls.py. Rutas EXPLÍCITAS: una path() por vista.

Orden: home · entidades (orden de views/base.py; en cada una list · create · detail · update · delete ·
toggle · by) · lanzadores · log. Las rutas de datos (data · data-by · select) viven en urls/data.py.
"""
from django.urls import include, path

from apps.users import views as v
from core.views import AdminToggleView


urlpatterns = [
    path('', include('apps.users.urls.data')),        # data · data-by · select (DataTables y AJAX)

    # ---------- home de sección ----------
    path('users/', v.UsersHomeView.as_view(), name='users-home'),

    # ---------- user · CustomUser ----------
    path('user/', v.CustomUserListView.as_view(), name='user_list'),
    path('user/create/', v.CustomUserCreateView.as_view(), name='user_create'),
    path('user/<int:pk>/', v.CustomUserDetailView.as_view(), name='user_detail'),
    path('user/<int:pk>/update/', v.CustomUserUpdateView.as_view(), name='user_update'),
    path('user/<int:pk>/delete/', v.CustomUserDeleteView.as_view(), name='user_delete'),
    path('user/<int:pk>/toggle/<str:field>/', AdminToggleView.as_view(model=v.CustomUserListView.model, entity='user', label='usuario', namespace='panel'), name='user_toggle'),
    # Reset de contraseña (solo superuser). Activar/bloquear/staff/superuser
    # lo hace el toggle genérico (usuario_toggle, campo is_active/is_staff/is_superuser).
    path('user/<int:pk>/reset/', v.UserResetPasswordView.as_view(), name='user_reset'),

    # ---------- user-activity · UserActivity ----------
    path('user-activity/', v.UserActivityListView.as_view(), name='user-activity_list'),
    path('user-activity/create/', v.UserActivityCreateView.as_view(), name='user-activity_create'),
    path('user-activity/<int:pk>/', v.UserActivityDetailView.as_view(), name='user-activity_detail'),
    path('user-activity/<int:pk>/update/', v.UserActivityUpdateView.as_view(), name='user-activity_update'),
    path('user-activity/<int:pk>/delete/', v.UserActivityDeleteView.as_view(), name='user-activity_delete'),

    # ---------- user-log · UserLog ----------
    path('user-log/', v.UserLogListView.as_view(), name='user-log_list'),
    path('user-log/create/', v.UserLogCreateView.as_view(), name='user-log_create'),
    path('user-log/<int:pk>/', v.UserLogDetailView.as_view(), name='user-log_detail'),
    path('user-log/<int:pk>/update/', v.UserLogUpdateView.as_view(), name='user-log_update'),
    path('user-log/<int:pk>/delete/', v.UserLogDeleteView.as_view(), name='user-log_delete'),
]
