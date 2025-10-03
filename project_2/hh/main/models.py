import uuid
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 40


# https://docs.djangoproject.com/en/5.2/ref/validators/
def validate_min(value: str) -> None:
    if len(value) < MIN_NAME_LENGTH:
        raise ValidationError(
            _("%(value)s is less than 2"),
            params={"value": value},
        )


class Location(models.Model):
    # - Each new location gets a unique id of type UUID4
    # - I can add the name of the location
    # - I can add a slug to the location
    # - Location names can be between 2 and 40 characters long
    # - The slug is automatically populated in admin when I enter the name

    # https://docs.djangoproject.com/en/5.2/ref/models/fields/
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # custom validator possible but we use built in
    # name = models.CharField(max_length=MAX_NAME_LENGTH, validators=[validate_min])  # noqa: ERA001
    name = models.CharField(max_length=MAX_NAME_LENGTH, validators=[MinLengthValidator(2)])
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}"

    # in case slug is ereased in admin, enforce one
    def save(self, *args, **kwargs) -> None:
        if self.name and not self.slug:  # only set slug if name exists and slug is empty
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Sensor(models.Model):
    # - Each new sensor gets a unique id of type UUID4
    # - Each sensor belongs to a specific location
    # - I can add the name of the sensor
    # - I can add a description (optional) to the sensor
    # - Sensor names are unique per location.
    # - Sensor names can be between 2 and 40 characters long.

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=MAX_NAME_LENGTH, validators=[MinLengthValidator(2)])
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="sensors")
    description = models.TextField(blank=True)

    # Django voodoo to enforce name uniqueness within a location
    class Meta:
        constraints: ClassVar[list[models.UniqueConstraint | str]] = [
            models.UniqueConstraint(fields=["name", "location"], name="unique_sensor_per_location")
        ]

    def __str__(self) -> str:
        return f"{self.name}"
