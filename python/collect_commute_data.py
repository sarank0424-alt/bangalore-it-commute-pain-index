import os
import csv
import sys
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# 1. API SETUP
# --------------------------------------------------

# Load API key from the .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Google Routes API endpoint
URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


# --------------------------------------------------
# 2. FILE PATH SETUP
# --------------------------------------------------

# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Path where the raw dataset will be saved
CSV_FILE = PROJECT_ROOT / "data" / "bangalore_commute_raw.csv"
# Create the data folder if it does not exist
CSV_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 3. RESIDENTIAL AREAS
# --------------------------------------------------

HOMES = [
    "JP Nagar, Bengaluru",
    "Jayanagar, Bengaluru",
    "Banashankari, Bengaluru",
    "Koramangala, Bengaluru",
    "HSR Layout, Bengaluru",
    "Whitefield, Bengaluru",
    "Marathahalli, Bengaluru",
    "Hebbal, Bengaluru",
    "Yelahanka, Bengaluru",
    "Rajajinagar, Bengaluru"
]


# --------------------------------------------------
# 4. IT PARKS / TECH HUBS
# --------------------------------------------------

IT_HUBS = [
    "Manyata Tech Park, Bengaluru",
    "Electronic City, Bengaluru",
    "International Tech Park Bangalore, Bengaluru",
    "Bagmane Tech Park, Bengaluru",
    "RMZ Ecoworld, Bengaluru",
    "Embassy TechVillage, Bengaluru",
    "Global Village Tech Park, Bengaluru",
    "Prestige Tech Park, Bengaluru",
    "Embassy GolfLinks Business Park, Bengaluru",
    "Cessna Business Park, Bengaluru"
]


# --------------------------------------------------
# 5. GOOGLE ROUTES API FUNCTION
# --------------------------------------------------

def get_route_data(origin, destination):

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.staticDuration,routes.distanceMeters"    }

    body = {
        "origin": {
            "address": origin
        },
        "destination": {
            "address": destination
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE"
    }

    response = requests.post(
        URL,
        headers=headers,
        json=body
    )

    if response.status_code == 200:

        data = response.json()

        distance_meters = data["routes"][0]["distanceMeters"]

        duration_seconds = float(
        data["routes"][0]["duration"].replace("s", "")
        )

        static_duration_seconds = float(
        data["routes"][0]["staticDuration"].replace("s", "")
        )

        # Convert meters to kilometers
        distance_km = round(
            distance_meters / 1000,
            2
        )

        # Convert seconds to minutes
        duration_minutes = round(
            duration_seconds / 60,
            2
        )

        static_duration_minutes = round(
        static_duration_seconds / 60,
        2
        )

        return distance_km, duration_minutes,static_duration_minutes

    else:

        print("API Error:", response.status_code)
        print(response.text)

        return None, None,None


# --------------------------------------------------
# 6. DUPLICATE COLLECTION CHECK
# --------------------------------------------------

def collection_already_exists(time_slot):

    # If CSV doesn't exist yet, nothing has been collected
    if not CSV_FILE.exists():
        return False

    today = datetime.now().strftime("%Y-%m-%d")

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row["collection_date"] == today
                and row["time_slot"] == time_slot
            ):
                return True

    return False


# --------------------------------------------------
# 7. DATA COLLECTION FUNCTION
# --------------------------------------------------

def collect_data(time_slot):

    # Prevent duplicate collection
    if collection_already_exists(time_slot):

        print(
            f"Data for '{time_slot}' "
            f"has already been collected today."
        )

        return


    # Decide travel direction based on time slot
    if time_slot in ["morning_peak", "baseline"]:

        direction = "home_to_office"

    elif time_slot == "evening_peak":

        direction = "office_to_home"

    else:

        print("Invalid time slot.")

        return


    # Check whether CSV already exists
    file_exists = CSV_FILE.exists()


    # Open CSV in append mode
    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)


        # Create column headers if this is a new CSV
        if not file_exists:

            writer.writerow([
                "collection_date",
                "collection_timestamp",
                "day_of_week",
                "time_slot",
                "direction",
                "residential_area",
                "it_hub",
                "origin",
                "destination",
                "distance_km",
                "duration_minutes",
                "static_duration",
                "status"
            ])


        # Loop through all 10 residential areas
        for home in HOMES:

            # Loop through all 10 IT hubs
            for it_hub in IT_HUBS:


                # Morning and baseline:
                # Home → Office
                if direction == "home_to_office":

                    origin = home
                    destination = it_hub


                # Evening:
                # Office → Home
                else:

                    origin = it_hub
                    destination = home


                print(
                    f"Collecting: "
                    f"{origin} → {destination}"
                )


                # Call Google Routes API
                distance, duration,static_duration = get_route_data(
                    origin,
                    destination
                )


                # Check whether API call succeeded
                if (
                    distance is not None
                    and duration is not None
                    and static_duration is not None
                ):

                    status = "success"

                else:

                    status = "failed"


                # Get current date and time
                now = datetime.now()


                # Save one route as one CSV row
                writer.writerow([
                    now.strftime("%Y-%m-%d"),
                    now.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    now.strftime("%A"),
                    time_slot,
                    direction,
                    home,
                    it_hub,
                    origin,
                    destination,
                    distance,
                    duration,
                    static_duration,
                    status
                ])


    print("\nCollection complete.")
    print("Data saved to:", CSV_FILE)


# --------------------------------------------------
# 8. VERIFY PROJECT SCOPE
# --------------------------------------------------

print("Residential areas:", len(HOMES))
print("IT hubs:", len(IT_HUBS))
print(
    "Unique routes:",
    len(HOMES) * len(IT_HUBS)
)


# Generate all 100 route combinations
all_routes = []

for home in HOMES:

    for it_hub in IT_HUBS:

        all_routes.append(
            (home, it_hub)
        )


print(
    "\nTotal routes generated:",
    len(all_routes)
)


# Display first 5 routes only
for route in all_routes[:5]:

    print(route)


# --------------------------------------------------
# 9. DATA COLLECTION
# --------------------------------------------------

# DO NOT call collect_data() here yet.
# We will activate the correct time slot
# when we begin the real 7-day collection.
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(
            "Usage: python collect_commute_data.py "
            "[morning_peak|baseline|evening_peak]"
        )
        sys.exit(1)

    time_slot = sys.argv[1]

    if time_slot not in [
        "morning_peak",
        "baseline",
        "evening_peak"
    ]:
        print("Invalid time slot.")
        sys.exit(1)

    collect_data(time_slot)