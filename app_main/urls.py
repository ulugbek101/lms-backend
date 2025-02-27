from django.urls import path

from . import views

urlpatterns = [
    path("analytics/", views.analytics, name="analytics"),
    path("subjects/", views.SubjectsView.as_view(), name="subjects")
]
