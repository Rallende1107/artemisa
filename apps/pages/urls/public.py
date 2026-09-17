from django.urls import path

from apps.pages import views


app_name = "pages"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("contact/my-messages/", views.MyMessagesView.as_view(), name="my-messages"),
    path("search/", views.GlobalSearchView.as_view(), name="search"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
]
