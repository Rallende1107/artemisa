"""Vistas de users como PAQUETE plano (estilo Poseidón): base.py (mixins _Base<Modelo>, mapas _BaseXBy y helpers) y un
archivo por rol con las DOS caras, gestión y público. Este __init__ SOLO re-exporta: `from apps.users import views`
(urls/public.py) y `views as v` (urls/panel.py, urls/data.py) siguen funcionando y cada clase tiene UN archivo dueño."""
from apps.users.views.v1_home import UsersHomeView  # noqa: F401,E402
from apps.users.views.v3_data import CustomUserDataView, CustomUserSelectView, ActividadFilters, UserActivityDataView, UserLogDataView, USER_COLUMNS  # noqa: F401,E402
from apps.users.views.v4_write import CustomUserCreateView, CustomUserUpdateView, UserResetPasswordView, CustomUserDeleteView, UserResetPasswordForm, UserLogCreateView, UserLogUpdateView, UserLogDeleteView, UserActivityDeleteView, UserActivityCreateView, UserActivityUpdateView  # noqa: F401,E402
from apps.users.views.v5_list import CustomUserListView, UserActivityListView, UserLogListView  # noqa: F401,E402
from apps.users.views.v6_detail import CustomUserDetailView, UserLogDetailView, UserActivityDetailView, USER_DETAIL  # noqa: F401,E402
from apps.users.views.v8_actions import BaseActivity, LoginView, LogoutView, RegisterView, ProfileView, ProfileUpdateView, MyActivityView, MyActivityPublicDataView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView  # noqa: F401,E402
