# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

from .models import Location, Sensor


def main(request) -> HttpResponse:
    return render(
        request,
        "base.html",
    )


def locations(request) -> HttpResponse:
    locations = Location.objects.all()
    context = {"title": "Locations", "items": locations}

    if request.htmx:
        return render(request, "list_inner.html", context)
    return render(request, "list.html", context)


def sensors(request) -> HttpResponse:
    sensors = Sensor.objects.all()
    items = [f"{s.name} — {s.location.name}" for s in sensors]
    context = {"title": "Sensors", "items": items}

    if request.htmx:
        return render(request, "list_inner.html", context)
    return render(request, "list.html", context)
