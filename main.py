from fastapi import FastAPI, BackgroundTasks
from flight_api import get_flight_status
from notifications import send_notifications
from flight_tracker import start_flight_tracking, stop_flight_tracking
import asyncio

app = FastAPI(title="Flight Tracker API")


app.get("/")
def read_root():
    return {"message": "Flight Tracker API"}

@app.get("/track-flight/{flight_number}")
def track_flight(flight_number: str):
    """
    Track a flight by IATA code and send notifications.
    """
    message = get_flight_status(flight_number)
    send_notifications(message)
    return {"message": message}


@app.post("/start-tracking/{flight_number}")
async def start_tracking(flight_number: str, background_tasks: BackgroundTasks):
    """
    Start continuous tracking of a flight with hourly updates.
    """
    # Start tracking in background
    background_tasks.add_task(start_flight_tracking, flight_number)

    return {
        "message": f"Started continuous tracking for flight {flight_number}",
        "status": "tracking_started",
    }


@app.post("/stop-tracking")
def stop_tracking():
    """
    Stop current flight tracking.
    """
    stop_flight_tracking()
    return {"message": "Flight tracking stopped", "status": "tracking_stopped"}


@app.get("/tracking-status")
def get_tracking_status():
    """
    Get current tracking status.
    """
    from flight_tracker import current_tracker

    if current_tracker and current_tracker.is_tracking:
        return {
            "is_tracking": True,
            "flight_number": current_tracker.flight_number,
            "last_update": (
                current_tracker.last_update.isoformat()
                if current_tracker.last_update
                else None
            ),
        }
    else:
        return {"is_tracking": False, "flight_number": None, "last_update": None}
