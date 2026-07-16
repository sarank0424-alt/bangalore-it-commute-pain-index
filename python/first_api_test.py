import os
import json
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

url = "https://routes.googleapis.com/directions/v2:computeRoutes"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
}

body = {
    "origin": {
        "address": "Manyata Tech Park, Bengaluru"
    },
    "destination": {
        "address": "JP Nagar, Bengaluru"
    },
    "travelMode": "DRIVE",
    "routingPreference": "TRAFFIC_AWARE"
}

response = requests.post(url, headers=headers, json=body)

print("Status Code:", response.status_code)
print(json.dumps(response.json(), indent=4))