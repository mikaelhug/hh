from typing import ClassVar

from django.contrib import admin

from .models import Location, Sensor

# Create your views here.
# default register
# admin.site.register(Location)


# decorator shorthand for registering a model together with a custom ModelAdmin class
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields: ClassVar[dict[str, tuple[str, ...]]] = {"slug": ("name",)}  # type: ignore


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "id")
    list_filter = ("location",)
