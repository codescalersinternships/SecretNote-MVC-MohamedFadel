from django.urls import path

from . import views

urlpatterns = [
    path("create/", views.create_note, name="create_note"),
    path("note/<uuid:url_key>/", views.view_note, name="view_note"),
]
