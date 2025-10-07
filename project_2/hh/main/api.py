from typing import Literal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Query, Schema
from ninja.errors import HttpError
from pydantic import Field

from .models import MAX_NAME_LENGTH, MIN_NAME_LENGTH, Location, Sensor

api = NinjaAPI(title="HH Project API")


class SensorSchema(Schema):
    id: str
    name: str
    location: str


class LocationSchema(Schema):
    id: str
    name: str
    slug: str


# Validate with Pydantic rules
class SensorCreateSchema(Schema):
    name: str = Field(..., min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    location: str  # location slug


class LocationCreateSchema(Schema):
    name: str = Field(..., min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)


# list all sensors or filter by location and/or name
@api.get("/sensors/", response=list[SensorSchema])
def list_sensors(request, location: str | None = Query(None), sensor: str | None = Query(None)) -> list[SensorSchema]:
    # Base queryset
    sensors = Sensor.objects.select_related("location").order_by("name")

    # Apply filters if provided
    if location:
        sensors = sensors.filter(location__slug=location)

    if sensor:
        sensors = sensors.filter(name__iexact=sensor)

    # If both filters applied but nothing found → 404
    if (location or sensor) and not sensors.exists():
        raise HttpError(404, "No sensors found matching the provided criteria")

    return [SensorSchema(id=str(s.id), name=s.name, location=s.location.name) for s in sensors]


# create a new sensor
@api.post("/sensors/", response={201: SensorSchema})
def create_sensor(request, payload: SensorCreateSchema) -> Literal[422] | tuple[Literal[201], SensorSchema]:
    """
    Create a new sensor.
    Returns 201 on success, 422 if validation fails.
    """
    try:
        loc = Location.objects.get(slug=payload.location)
    except Location.DoesNotExist as err:
        raise HttpError(422, f"Location '{payload.location}' does not exist") from err

    try:
        # Will raise IntegrityError if name/slug not unique
        sensor = Sensor.objects.create(name=payload.name, location=loc)
    except IntegrityError as err:
        raise HttpError(422, f"Could not create sensor '{payload.name}' in location '{payload.location}'") from err

    # Return the new Location and HTTP 201 status code
    return 201, SensorSchema(
        id=str(sensor.id),
        name=sensor.name,
        location=sensor.location.name,
    )


# modify a sensor
@api.put("/sensors/{location}/{name}/", response={200: SensorSchema})
def modify_sensor(
    request, location: str, name: str, payload: SensorCreateSchema
) -> Literal[404, 422] | tuple[Literal[200], SensorSchema]:
    """
    Modify an existing sensor.
    Returns 200 on success, 404 if not found, 422 if invalid.
    """
    sensor = get_object_or_404(Sensor, name=name, location__slug=location)

    try:
        sensor.name = payload.name
        sensor.location = get_object_or_404(Location, slug=payload.location)
        sensor.full_clean()  # triggers Django validators (raises ValidationError if invalid)
        sensor.save()
    except IntegrityError as err:
        raise HttpError(422, f"Sensor '{payload.name}' already exists") from err
    except ValidationError as err:
        raise HttpError(422, str(err)) from err

    return 200, SensorSchema(
        id=str(sensor.id),
        name=sensor.name,
        location=sensor.location.name,
    )


# delete a sensor
@api.delete("/sensors/{location}/{name}/", response={204: None})
def delete_sensor(request, location: str, name: str) -> tuple[Literal[204], None]:
    """
    Delete a sensor.
    - 404 if not found
    - 204 No Content on success
    """
    sensor = get_object_or_404(Sensor, name=name, location__slug=location)
    sensor.delete()
    return 204, None


# list all locations or a specific one by slug
@api.get("/locations/", response=list[LocationSchema])
def list_locations(request, slug: str | None = Query(None)) -> list[LocationSchema]:
    """
    List all locations or a specific one by slug.
    """
    if slug:
        loc = get_object_or_404(Location, slug=slug)
        return [LocationSchema(id=str(loc.id), name=loc.name, slug=loc.slug)]

    locations = Location.objects.all().order_by("name")
    return [LocationSchema(id=str(loc.id), name=loc.name, slug=loc.slug) for loc in locations]


# create a new location
@api.post("/locations/", response={201: LocationSchema})
def create_location(request, payload: LocationCreateSchema) -> Literal[422] | tuple[Literal[201], LocationSchema]:
    """
    Create a new location.
    Returns 201 on success, 422 if validation fails.
    """
    try:
        # Will raise IntegrityError if name/slug not unique
        location = Location.objects.create(name=payload.name)
    except IntegrityError as err:
        raise HttpError(422, f"Location '{payload.name}' already exists") from err

    # Return the new Location and HTTP 201 status code
    return 201, LocationSchema(
        id=str(location.id),
        name=location.name,
        slug=location.slug,
    )


# modify a location
@api.put("/locations/{slug}/", response={200: LocationSchema})
def modify_location(
    request, slug: str, payload: LocationCreateSchema
) -> Literal[404, 422] | tuple[Literal[200], LocationSchema]:
    """
    Modify an existing location.
    Returns 200 on success, 404 if not found, 422 if invalid.
    """
    location = get_object_or_404(Location, slug=slug)

    try:
        location.name = payload.name
        location.full_clean()  # triggers Django validators (raises ValidationError if invalid)
        location.save()
    except IntegrityError as err:
        raise HttpError(422, f"Location '{payload.name}' already exists") from err
    except ValidationError as err:
        raise HttpError(422, str(err)) from err

    return 200, LocationSchema(
        id=str(location.id),
        name=location.name,
        slug=location.slug,
    )


# delete a location
@api.delete("/locations/{slug}/", response={204: None})
def delete_location(request, slug: str) -> tuple[Literal[204], None]:
    """
    Delete a location by its slug.
    - 404 if not found
    - 204 No Content on success
    """
    location = get_object_or_404(Location, slug=slug)
    location.delete()
    return 204, None
