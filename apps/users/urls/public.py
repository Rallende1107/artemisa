"""Rutas de cuenta: /account/..."""
from django.urls import path

from apps.users import views


app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile-edit"),
    path("profile/activity/", views.MyActivityView.as_view(), name="profile-activity"),
    path("profile/activity/data/", views.MyActivityPublicDataView.as_view(), name="profile-activity-data"),
    path("profile/password/", views.PasswordChangeView.as_view(), name="password_change"),
    # Recuperación de contraseña
    path("recover/", views.PasswordResetView.as_view(), name="password_reset"),
    path("recover/sent/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
