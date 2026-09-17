"""URLs de la colección del usuario (/collection/). El medio va en la URL porque
cada colección es su propia tabla y el pk solo es único dentro de ella."""
from django.urls import path

from apps.collections import views


app_name = "collections"

urlpatterns = [
    path("", views.CollectionsPublicHomeView.as_view(), name="mine"),
    path("add/", views.AddToCollectionView.as_view(), name="add"),
    path("<str:tipo>/data/", views.collection_data, name="list-data"),
    path("<str:tipo>/<int:pk>/remove/", views.RemoveFromCollectionView.as_view(), name="remove"),
    path("<str:tipo>/<int:pk>/update/", views.UpdateItemView.as_view(), name="update"),
    path("<str:tipo>/<int:pk>/edit/", views.ItemEditView.as_view(), name="edit"),
    path("<str:tipo>/", views.collection_list, name="list"),
]
