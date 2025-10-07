# main/tests/test_api_spec.py
import json

import pytest

from main.models import Location, Sensor


@pytest.mark.django_db
class TestApiSpecification:
    # ---------------------------------------------------------------------
    # As a developer I can retrieve all available sensors.
    # - The sensors are ordered alphabetically.
    # - I can access the sensors' attributes such as location and name.
    # - I can filter sensors by location.
    # ---------------------------------------------------------------------
    def test_list_sensors_ordering_attributes_and_filtering(self, client):
        loc1 = Location.objects.create(name="Plant A", slug="plant-a")
        loc2 = Location.objects.create(name="Plant B", slug="plant-b")

        # names chosen so alphabetical ordering is obvious
        Sensor.objects.create(name="TempSensor", location=loc1)
        Sensor.objects.create(name="AlphaSensor", location=loc2)
        Sensor.objects.create(name="BetaSensor", location=loc1)

        # list all sensors
        resp = client.get("/api/sensors/")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # check ordering alphabetically by sensor name
        names = [s["name"] for s in data]
        assert names == sorted(names)

        # check attributes exist and include location and name
        for item in data:
            assert "name" in item
            assert "location" in item

        # filter by location slug (plant-a)
        resp = client.get("/api/sensors/?location=plant-a")
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["location"] == "Plant A" for item in data)

    # ---------------------------------------------------------------------
    # As a developer I can retrieve information about a specific sensor.
    # - I get a 404 if the sensor does not exist.
    # ---------------------------------------------------------------------
    def test_retrieve_specific_sensor_and_404_when_missing(self, client):
        loc = Location.objects.create(name="PowerPlant", slug="powerplant")
        Sensor.objects.create(name="SensorX", location=loc)

        # existing sensor via filters (location + sensor)
        resp = client.get("/api/sensors/?location=powerplant&sensor=SensorX")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "SensorX"
        assert data[0]["location"] == "PowerPlant"

        # non-existent sensor -> should return 404 per implementation
        resp = client.get("/api/sensors/?location=powerplant&sensor=NoSuchSensor")
        assert resp.status_code == 404

    # ---------------------------------------------------------------------
    # As a developer I can create a new location.
    # - I get a 422 if the data is not valid.
    # - I get a 201 on success.
    # - The created location is returned.
    # ---------------------------------------------------------------------
    def test_create_location_validation_and_success(self, client):
        # invalid (too short) -> 422
        resp = client.post(
            "/api/locations/",
            data=json.dumps({"name": "A"}),  # too short
            content_type="application/json",
        )
        assert resp.status_code == 422

        # valid -> 201 and returned location
        resp = client.post(
            "/api/locations/",
            data=json.dumps({"name": "NewTown"}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "NewTown"
        assert "id" in data
        assert "slug" in data
        # confirm persisted
        assert Location.objects.filter(slug=data["slug"]).exists()

    # ---------------------------------------------------------------------
    # As a developer I can modify an existing location.
    # - I get a 404 if the location does not exist.
    # - I get a 422 if the data is not valid.
    # - I get a 200 on success.
    # - The updated location is returned.
    # ---------------------------------------------------------------------
    def test_modify_location_404_422_200_and_returned(self, client):
        loc = Location.objects.create(name="OldName", slug="oldname")

        # 404 for non-existing
        resp = client.put(
            "/api/locations/nonexistent/",
            data=json.dumps({"name": "NewName"}),
            content_type="application/json",
        )
        assert resp.status_code == 404

        # 422 for invalid data (too short)
        resp = client.put(
            f"/api/locations/{loc.slug}/",
            data=json.dumps({"name": "A"}),
            content_type="application/json",
        )
        assert resp.status_code == 422

        # 200 success and returned updated location
        resp = client.put(
            f"/api/locations/{loc.slug}/",
            data=json.dumps({"name": "UpdatedName"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "UpdatedName"

        # DB confirmed
        loc.refresh_from_db()
        assert loc.name == "UpdatedName"

    # ---------------------------------------------------------------------
    # As a developer I can delete an existing location.
    # - I get a 404 if the location does not exist.
    # - I get a 204 on success.
    # ---------------------------------------------------------------------
    def test_delete_location_404_and_204(self, client):
        # 404 when not found
        resp = client.delete("/api/locations/no-such/")
        assert resp.status_code == 404

        loc = Location.objects.create(name="ToDelete", slug="to-delete")
        resp = client.delete(f"/api/locations/{loc.slug}/")
        assert resp.status_code == 204
        assert not Location.objects.filter(slug=loc.slug).exists()

    # ---------------------------------------------------------------------
    # As a developer I can create a new sensor.
    # - I get a 422 if the data is not valid.
    # - I get a 201 on success.
    # - The created sensor is returned.
    # ---------------------------------------------------------------------
    def test_create_sensor_422_201_and_returned(self, client):
        loc = Location.objects.create(name="CreateLoc", slug="create-loc")

        # invalid data (name too short) -> 422
        resp = client.post(
            "/api/sensors/",
            data=json.dumps({"name": "A", "location": loc.slug}),
            content_type="application/json",
        )
        assert resp.status_code == 422

        # invalid location (doesn't exist) -> 422 per implementation
        resp = client.post(
            "/api/sensors/",
            data=json.dumps({"name": "SensorNew", "location": "no-such"}),
            content_type="application/json",
        )
        assert resp.status_code == 422

        # valid -> 201 created and returned
        resp = client.post(
            "/api/sensors/",
            data=json.dumps({"name": "SensorNew", "location": loc.slug}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "SensorNew"
        assert data["location"] == loc.name
        assert Sensor.objects.filter(name="SensorNew", location=loc).exists()

    # ---------------------------------------------------------------------
    # As a developer I can modify an existing sensor.
    # - I get a 404 if the sensor does not exist.
    # - I get a 422 if the data is not valid.
    # - I get a 200 on success.
    # - The updated sensor is returned.
    # ---------------------------------------------------------------------
    def test_modify_sensor_404_422_200_and_returned(self, client):
        loc1 = Location.objects.create(name="Loc1", slug="loc1")
        loc2 = Location.objects.create(name="Loc2", slug="loc2")
        sensor = Sensor.objects.create(name="SensA", location=loc1)

        # 404 when not found
        resp = client.put(
            "/api/sensors/loc1/NoSuchSensor/",
            data=json.dumps({"name": "NewName", "location": loc1.slug}),
            content_type="application/json",
        )
        assert resp.status_code == 404

        # 422 invalid data (name too short)
        resp = client.put(
            f"/api/sensors/{loc1.slug}/{sensor.name}/",
            data=json.dumps({"name": "A", "location": loc1.slug}),
            content_type="application/json",
        )
        assert resp.status_code == 422

        # successful update -> 200 and returned
        resp = client.put(
            f"/api/sensors/{loc1.slug}/{sensor.name}/",
            data=json.dumps({"name": "SensB", "location": loc2.slug}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "SensB"
        assert data["location"] == loc2.name

        sensor.refresh_from_db()
        assert sensor.name == "SensB"
        assert sensor.location == loc2

    # ---------------------------------------------------------------------
    # As a developer I can delete an existing sensor.
    # - I get a 404 if the sensor does not exist.
    # - I get a 204 on success.
    # ---------------------------------------------------------------------
    def test_delete_sensor_404_and_204(self, client):
        # 404 for missing sensor
        resp = client.delete("/api/sensors/no-such-loc/no-such-sensor/")
        assert resp.status_code == 404

        loc = Location.objects.create(name="DelLoc", slug="del-loc")
        sensor = Sensor.objects.create(name="ToDelete", location=loc)
        resp = client.delete(f"/api/sensors/{loc.slug}/{sensor.name}/")
        assert resp.status_code == 204
        assert not Sensor.objects.filter(pk=sensor.pk).exists()
