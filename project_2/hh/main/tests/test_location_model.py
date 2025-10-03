import uuid

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError

from main.admin import LocationAdmin
from main.models import Location


@pytest.mark.django_db
def test_location_uuid_name():
    a = Location.objects.create(name="Stockholm")
    b = Location.objects.create(name="Oslo")

    # UUID
    assert isinstance(a.id, uuid.UUID)
    assert isinstance(b.id, uuid.UUID)
    assert a.id != b.id  # ensure unique UUIDs
    assert a.id.version == 4  # ensure UUID4

    # Name & Slug
    assert a.name == "Stockholm"
    assert a.slug == "stockholm"


@pytest.mark.django_db
def test_location_name_length_constraints():
    # create python object in memory only
    # run full_clean to run validators on model class
    # Alert if **not** fail

    loc = Location(name="S")
    with pytest.raises(ValidationError):
        loc.full_clean()

    loc = Location(name="S" * 41)
    with pytest.raises(ValidationError):
        loc.full_clean()


@pytest.mark.django_db
def test_slug_autopopulated_in_admin():
    # ensure the key "slug" is in prepopulated_fields its value is ("name",)
    model_admin = LocationAdmin(Location, admin.site)
    assert "slug" in model_admin.prepopulated_fields
    assert model_admin.prepopulated_fields["slug"] == ("name",)
