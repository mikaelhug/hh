from django.urls import path

from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path("locations", views.locations, name="locations"),
    path("sensors", views.sensors, name="sensors"),
]
