Use pyenv to manage different python versions.
Install and enable in specific directory
```
sudo apt install pyenv
pyenv local 3.11.11
```

Install uv (venv alternative) and install ruff
```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.11.11 hh_env
source hh_env/bin/activate
uv pip install ruff
```

Run commands on the django docker container
```
docker exec hh_app python manage.py startapp main
docker exec hh_app python manage.py makemigrations main
docker exec hh_app python manage.py migrate
```

Add port settings to forward ports automatically for all needed services
when using remote-dev in VScode
```
"remote.SSH.defaultForwardedPorts": [
     {
          "localPort": 8000,
          "remotePort": 8000,
          "name": "Django"
     },
     {
          "localPort": 15672,
          "remotePort": 15672,
          "name": "RabbitMQ"
     }
]
```

API Calls
Sensor
```
<!-- List all -->
curl -X GET "http://localhost:8000/api/sensors/"

<!-- List all for a location -->
curl -X GET "http://localhost:8000/api/sensors/?location=loc_a"

<!-- List specific sensor in location loc_a -->
curl -X GET "http://localhost:8000/api/sensors/?location=powerplant1&sensor=sensor3"

<!-- List all sensors with name -->
curl -X GET "http://localhost:8000/api/sensors/?sensor=sensor2"

<!-- Create -->
curl -X POST "http://localhost:8000/api/sensors/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Sensor4", "location": "Sensor4"}'

<!-- Modify -->
curl -X PUT "http://localhost:8000/api/sensors/location-c/Stockholm%20Updated/" \
     -H "Content-Type: application/json" \
     -d '{"name": "sensor_updated", "location": "powerplant1"}'

<!-- Delete -->
curl -X DELETE "http://localhost:8000/api/sensors/powerplant1/sensor_updated/"
```

Location
```
<!-- List all -->
curl -X GET "http://localhost:8000/api/locations/"

<!-- List specific -->
curl -X GET "http://localhost:8000/api/locations/?slug=berlin"

<!-- Create -->
curl -X POST "http://localhost:8000/api/locations/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Comet"}'

<!-- Modify -->
curl -X PUT "http://localhost:8000/api/locations/comets/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Stockholm Updated"}'

<!-- Delete -->
curl -X DELETE "http://localhost:8000/api/locations/comets/"

```