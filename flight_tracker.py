import asyncio
import time
from datetime import datetime, timedelta
from flight_api import get_flight_status
from notifications import send_notifications
import pytz
import traceback



class FlightTracker:
    def __init__(self, flight_number: str):
        self.flight_number = flight_number
        self.is_tracking = False
        self.last_update = None
        self.start_time = None
        self.error_count = 0
        self.max_errors = 5
        self.update_interval = 10800
        self.last_digest = None
        self.nz_tz = pytz.timezone("Pacific/Auckland")

    async def start_tracking(self):
        """Start continuous flight tracking"""
        self.is_tracking = True
        self.start_time = datetime.now(self.nz_tz)
        print(f"Starting flight tracking for {self.flight_number}")

        # Send initial notification
        try:
            message = get_flight_status(self.flight_number)
            send_notifications(
                f"🛫 Flight tracking started for {self.flight_number}\n\n{message}"
            )
            self.last_update = datetime.now(self.nz_tz)
            self.error_count = 0
        except Exception as e:

            error_msg = f"❌ Failed to start tracking {self.flight_number}: {str(e)}"
            send_notifications(error_msg)
            print(f"CRITICAL ERROR: {error_msg}")
            return

        # Start the tracking loop
        await self._tracking_loop()

    async def _tracking_loop(self):
        """Main tracking loop - runs every hour"""
        while self.is_tracking:
            try:
                # Wait for 3 hour (10800 seconds)
                await asyncio.sleep(self.update_interval)

                if not self.is_tracking:
                    break

                # Get current flight status
                message = get_flight_status(self.flight_number)
                digest = message
                if digest != self.last_digest:
                    changed = True
                    self.last_digest = digest
                else:
                    changed = False

                self.error_count = 0

                # Check if flight has landed
                if self._is_flight_landed(message):
                    duration_txt = ""
                    if self.start_time:
                        dur = datetime.now(self.nz_tz) - self.start_time
                        h = int(dur.total_seconds() // 3600)
                        m = int((dur.total_seconds() % 3600) // 60)
                        duration_txt = f"\nTracked for: {h}h {m}m"
                    send_notifications(
                        f"🛬 Flight {self.flight_number} has landed!{duration_txt}\n\n{message}"
                    )
                    self.stop_tracking()
                    break
                else:
                    if changed:
                        send_notifications(
                            f"🔄 Update for {self.flight_number}\n\n{message}"
                        )
                        self.last_update = datetime.now(self.nz_tz)
                    
            except Exception as e:
                self.error_count += 1
                error_msg = f"❌ Error tracking {self.flight_number}: {str(e)}"
                # Send Error
                send_notifications(error_msg)
                print(f"ERROR: {error_msg}")
                print(f"Traceback: {traceback.format_exc()}")

                if self.error_count >= self.max_errors:
                    crash_msg = f"CRITICAL FAILURE in tracking for {self.flight_number} after {self.max_errors} exceeded. Last error: {str(e)}"
                    send_notifications(crash_msg)
                    print(f"ISSUE: {crash_msg}")
                    self.stop_tracking()
                    break
            await asyncio.sleep(300)

    def _is_flight_landed(self, message: str) -> bool:
        """Check if flight has landed based on status message"""
        landed_statuses = [
            "ARRIVED",
            "LANDED",
            "GATE ARRIVAL",
            "ARRIVED / GATE ARRIVAL",
        ]
        return any(status in message.upper() for status in landed_statuses)

    def stop_tracking(self):
        """Stop the tracking service"""
        self.is_tracking = False
        if self.start_time:
            duration = datetime.now(self.nz_tz) - self.start_time
            print(f"Stopped tracking {self.flight_number} after {duration}")
        else:
            print(f"Stopped tracking {self.flight_number}")

    def set_interval(self, seconds: int):
        """Adjust polling interval (min 300s)"""
        self.update_interval = max(300, int(seconds))


# Global tracker instance
current_tracker = None


async def start_flight_tracking(flight_number: str):
    """Start tracking a flight"""
    global current_tracker

    # Stop any existing tracker
    if current_tracker:
        current_tracker.stop_tracking()

    # Start new tracker
    current_tracker = FlightTracker(flight_number)
    await current_tracker.start_tracking()


def stop_flight_tracking():
    """Stop current flight tracking"""
    global current_tracker
    if current_tracker:
        current_tracker.stop_tracking()
        current_tracker = None
