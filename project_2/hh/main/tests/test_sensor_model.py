import uuid

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from main.models import Location, Sensor


@pytest.mark.django_db
def test_sensor_uuid_name():
    loc = Location.objects.create(name="Stockholm")

    a = Sensor.objects.create(name="SensorA", location=loc)
    b = Sensor.objects.create(name="SensorB", location=loc, description="Humidity sensosor")

    # UUID
    assert isinstance(a.id, uuid.UUID)
    assert isinstance(b.id, uuid.UUID)
    assert a.id != b.id  # ensure unique UUIDs
    assert a.id.version == 4  # ensure UUID4

    # Name
    assert a.name == "SensorA"
    assert b.description == "Humidity sensosor"


@pytest.mark.django_db
def test_sensor_must_have_location():
    # sensor must belong to a location
    with pytest.raises(IntegrityError):
        Sensor.objects.create(name="SensorC")


@pytest.mark.django_db
def test_sensor_uniqueness():
    loc = Location.objects.create(name="Stockholm")
    Sensor.objects.create(name="SensorA", location=loc)

    # sensor names are unique per location
    with pytest.raises(IntegrityError):
        Sensor.objects.create(name="SensorA", location=loc)


@pytest.mark.django_db
def test_sensor_name_length_constraints():
    # create python object in memory only
    # run full_clean to run validators on model class
    # Alert if **not** fail

    sens = Sensor(name="S")
    with pytest.raises(ValidationError):
        sens.full_clean()

    sens = Sensor(name="S" * 41)
    with pytest.raises(ValidationError):
        sens.full_clean()
