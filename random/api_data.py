import random
import time
from datetime import UTC, datetime

import requests

# Endpoint URL
url = "http://localhost:8000/api/data/"

# Fixed fields
sensor_id = "c2e34a4a-9b32-4d9b-92a5-d9fbb733b431"
location_id = "5b19b1ab-0b6a-49c7-8b0a-73ef8f6de47a"

while True:
    # Generate current timestamp in ISO 8601 format with UTC timezone
    timestamp = datetime.now(UTC).isoformat()

    # Randomize temperature between 20 and 30 degrees Celsius
    temperature = round(random.uniform(20.0, 30.0), 2)

    # Prepare payload
    data = {"time": timestamp, "sensor_id": sensor_id, "location_id": location_id, "temperature": temperature}

    try:
        response = requests.post(url, json=data)
        print(f"Sent data: {data} | Response: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")

    # Wait for 5 seconds before sending next data
    time.sleep(5)
