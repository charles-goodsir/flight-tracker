from fastapi import FastAPI, BackgroundTasks
from flight_api import get_flight_status
from notifications import send_notifications
from flight_tracker import start_flight_tracking, stop_flight_tracking, current_tracker
import psutil
import os
from datetime import datetime
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")

def require_admin(token: str):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="unauthorised")

app = FastAPI(title="Flight Tracker API")


@app.get("/")
def read_root():
    return {"message": "Flight Tracker API"}


@app.get("/health")
def health_check():
    """System health check with notifications for issues"""
    try:
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent
        cpu_usage = psutil.cpu_percent(interval=1)

        service_running = current_tracker is not None and current_tracker.is_tracking

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service_running": service_running,
            "system:": {
                "memory_usuage_percent": memory_usage,
                "disk_usuage_percent": disk_usage,
                "cpu_usage_percent": cpu_usage,
            },
            "tracking": {
                "is_tracking": service_running,
                "flight_number": (
                    current_tracker.flight_number if current_tracker else None
                ),
                "error_count": current_tracker.error_count if current_tracker else 0,
            },
        }

        if memory_usage > 80 or disk_usage > 90 or cpu_usage > 90:
            alert_msg = f"⚠️ System Alert: Memory: {memory_usage}%, Disk: {disk_usage}%, CPU: {cpu_usage}%"
            send_notifications(alert_msg)
            health_status["alerts"] = [alert_msg]
        return health_status
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        send_notifications(error_msg)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/track-flight/{flight_number}")
def track_flight(flight_number: str):
    """
    Track a flight by IATA code and send notifications.
    """
    message = get_flight_status(flight_number)
    send_notifications(message)
    return {"message": message}


@app.post("/start-tracking/{flight_number}")
async def start_tracking(flight_number: str, token: str, background_tasks: BackgroundTasks):
    """
    Start continuous tracking of a flight with hourly updates.
    """
    require_admin(token)
    # Start tracking in background
    background_tasks.add_task(start_flight_tracking, flight_number)

    return {
        "message": f"Started continuous tracking for flight {flight_number}",
        "status": "tracking_started",
    }


@app.post("/stop-tracking")
def stop_tracking(token: str):
    """
    Stop current flight tracking.
    """
    require_admin(token)
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

@app.post("/set-interval/{seconds}")
def set_interval(seconds: int, token: str):
    require_admin(token)
    from flight_tracker import current_tracker
    if not current_tracker or not current_tracker.is_tracking:
        return {"message": "not tracking; interval saved for next run", "interval_sec": max(300, seconds)}
    current_tracker.set_interval(seconds)
    return {"message": "interval updated", "interval_sec": max(300, seconds)}

@app.post("/update-now/{flight_number}")
def update_now(flight_number: str, token: str):
    require_admin(token)
    from flight_api import get_flight_status
    msg = get_flight_status(flight_number)
    send_notifications(f"🔔 Manual update for {flight_number}\n\n{msg}")
    return {"message": "sent"}