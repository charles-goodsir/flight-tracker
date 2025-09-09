from fastapi import FastAPI
from flight_api import get_flight_status
from notifications import send_notifications


app = FastAPI(title="Flight Tracker API")


@app.get("/track-flight/{flight_number}")
def track_flight(flight_number: str):
    """
    Track a flight by IATA code and send notifications.
    """
    message = get_flight_status(flight_number)
    send_notifications(message)
    return {"message": message}
