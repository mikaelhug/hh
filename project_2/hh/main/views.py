# Create your views here.
from django.http import HttpResponse
from django.urls import reverse

from .models import Location, Sensor


def main(request) -> HttpResponse:
    html = f"""
        <h1>Welcome</h1>
        <p>This is the main page.</p>
        <ul>
            <li><a href="{reverse("locations")}">View Locations</a></li>
            <li><a href="{reverse("sensors")}">View Sensors</a></li>
        </ul>
    """
    return HttpResponse(html)


def locations(request) -> HttpResponse:
    all_locations = Location.objects.all()
    location_names = "<br>".join([loc.name for loc in all_locations]) or "No locations found."
    return HttpResponse(f"Locations:<br>{location_names}")


def sensors(request) -> HttpResponse:
    all_sensors = Sensor.objects.all()
    sensor_names = "<br>".join([sens.name for sens in all_sensors]) or "No sensors found."
    return HttpResponse(f"Sensors:<br>{sensor_names}")
