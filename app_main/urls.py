from django.urls import path

from . import views

urlpatterns = [
    path("analytics/", views.analytics, name="analytics"),
    path("subjects/", views.subjects, name="subjects"),
]
