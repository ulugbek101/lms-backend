from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.user_profile, name="profile"),
    path("profile/update", views.user_profile_update, name="user_profile_update"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]
