import uuid

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError

from main.admin import SensorAdmin
from main.models import Sensor

# TODO


@pytest.mark.django_db
def test_sensor_uuid_name():
    a = Sensor.objects.create(name="Stockholm")
    b = Sensor.objects.create(name="Oslo")

    # UUID
    assert isinstance(a.id, uuid.UUID)
    assert isinstance(b.id, uuid.UUID)
    assert a.id != b.id  # ensure unique UUIDs
    assert a.id.version == 4  # ensure UUID4

    # Name & Slug
    assert a.name == "Stockholm"
    assert a.slug == "stockholm"


@pytest.mark.django_db
def test_Sensor_name_length_constraints():
    # create python object in memory only
    # run full_clean to run validators on model class
    # Alert if **not** fail

    loc = Sensor(name="S")
    with pytest.raises(ValidationError):
        loc.full_clean()

    loc = Sensor(name="S" * 41)
    with pytest.raises(ValidationError):
        loc.full_clean()


@pytest.mark.django_db
def test_slug_autopopulated_in_admin():
    # ensure the key "slug" is in prepopulated_fields its value is ("name",)
    model_admin = SensorAdmin(Sensor, admin.site)
    assert "slug" in model_admin.prepopulated_fields
    assert model_admin.prepopulated_fields["slug"] == ("name",)
