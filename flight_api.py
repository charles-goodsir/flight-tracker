import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import datetime
import pytz

load_dotenv()
API_KEY = os.getenv("AEROAPI_KEY")


def get_flight_status(flight_number: str) -> str:

    if not API_KEY:
        raise HTTPException(status_code=500, details="Missing AEROAPI_KEY")

    # AeroAPI endpoint for flight information
    url = f"https://aeroapi.flightaware.com/aeroapi/flights/{flight_number}"

    headers = {"x-apikey": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        # Add debug output

        if response.status_code != 200:
            if "message" in data:
                raise HTTPException(
                    status_code=response.status_code, detail=data["message"]
                )
            else:
                raise HTTPException(
                    status_code=response.status_code, detail="API request failed"
                )

        # AeroAPI returns flight data in a 'flights' array
        flights = data.get("flights", [])
        if not flights:
            raise HTTPException(status_code=404, detail="flight not found")

        # Get the first flight (most recent)
        flight = flights[0]

        # Add this after line 25 to see the raw data:
        print("DEBUG: Raw flight data:")
        print(f"Status: {flight.get('status')}")
        print(f"Progress: {flight.get('progress_percent')}")
        print(f"Cancelled: {flight.get('cancelled')}")
        print(f"Diverted: {flight.get('diverted')}")

        # Extract flight information
        airline = flight.get("operator", "Unknown")
        departure_airport = flight.get("origin", {}).get("code_iata", "Unknown")
        arrival_airport = flight.get("destination", {}).get("code_iata", "Unknown")

        # Get multiple status fields for better detection
        main_status = flight.get("status", "Unknown")
        progress = flight.get("progress_percent", 0)
        cancelled = flight.get("cancelled", False)
        diverted = flight.get("diverted", False)

        # Determine the most relevant status
        if cancelled:
            status = "CANCELLED"
        elif diverted:
            status = "DIVERTED"
        elif progress == 100:
            status = "ARRIVED"
        elif main_status in ["Arrived / Gate Arrival", "Arrived"]:
            status = "ARRIVED"
        elif main_status == "Scheduled":
            status = "SCHEDULED"
        else:
            status = main_status.upper()

        # Get departure and arrival times
        departure_time = flight.get("scheduled_out")
        arrival_time = flight.get("scheduled_in")

        # Convert to NZ timezone
        nz_tz = pytz.timezone("Pacific/Auckland")

        if departure_time:
            dep_dt = datetime.fromisoformat(departure_time.replace("Z", "+00:00"))
            dep_nz = dep_dt.astimezone(nz_tz)
            dep_time_str = dep_nz.strftime("%Y-%m-%d %H:%M NZDT")
        else:
            dep_time_str = "Not Available"

        if arrival_time:
            arr_dt = datetime.fromisoformat(arrival_time.replace("Z", "+00:00"))
            arr_nz = arr_dt.astimezone(nz_tz)
            arr_time_str = arr_nz.strftime("%Y-%m-%d %H:%M NZDT")
        else:
            arr_time_str = "Not Available"

        message = (
            f"✈️ {airline} flight {flight_number}\n"
            f"From: {departure_airport}\n"
            f"To: {arrival_airport}\n"
            f"Departure: {dep_time_str}\n"
            f"Arrival: {arr_time_str}\n"
            f"Status: {status.upper()}"
        )
        return message

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
