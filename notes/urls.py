from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_note, name="create_note"),
    path("note/<uuid:url_key>/", views.view_note, name="view_note"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="index"),
        name="logout",
    ),
    path("accounts/register/", views.register, name="register"),
    path(
        "accounts/profile/", RedirectView.as_view(pattern_name="index", permanent=False)
    ),
]
