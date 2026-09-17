"""URLs de DATOS del panel de users: data (DataTables) · data-by (acotada por el mapa «por») · select
(AJAX de FK/M2M). Las incluye urls/panel.py; mismo namespace `panel` y mismo orden de entidades."""
from django.urls import path

from apps.users import views as v


urlpatterns = [
    # ---------- user · CustomUser ----------
    path('user/data/', v.CustomUserDataView.as_view(), name='user_data'),
    path('user/select/', v.CustomUserSelectView.as_view(), name='user_select'),

    # ---------- user-activity · UserActivity ----------
    path('user-activity/data/', v.UserActivityDataView.as_view(), name='user-activity_data'),

    # ---------- user-log · UserLog ----------
    path('user-log/data/', v.UserLogDataView.as_view(), name='user-log_data'),
]
