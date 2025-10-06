from ninja import NinjaAPI, Schema

from .models import Sensor

api = NinjaAPI(title="HH Project API")


class SensorSchema(Schema):
    id: str
    name: str
    location: str


@api.get("/sensors/")
def list_sensors(request):
    sensors = Sensor.objects.select_related("location").all()
    return [{"id": str(s.id), "name": s.name, "location": s.location.name} for s in sensors]
