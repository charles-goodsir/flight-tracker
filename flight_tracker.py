import asyncio
import time
from datetime import datetime, timedelta
from flight_api import get_flight_status
from notifications import send_notifications
import pytz


class FlightTracker:
    def __init__(self, flight_number: str):
        self.flight_number = flight_number
        self.is_tracking = False
        self.last_update = None
        self.nz_tz = pytz.timezone("Pacific/Auckland")

    async def start_tracking(self):
        """Start continuous flight tracking"""
        self.is_tracking = True
        print(f"Starting flight tracking for {self.flight_number}")

        # Send initial notification
        try:
            message = get_flight_status(self.flight_number)
            send_notifications(
                f"🛫 Flight tracking started for {self.flight_number}\n\n{message}"
            )
            self.last_update = datetime.now(self.nz_tz)
        except Exception as e:
            send_notifications(
                f"❌ Failed to start tracking {self.flight_number}: {str(e)}"
            )
            return

        # Start the tracking loop
        await self._tracking_loop()

    async def _tracking_loop(self):
        """Main tracking loop - runs every hour"""
        while self.is_tracking:
            try:
                # Wait for 3 hour (10800 seconds)
                await asyncio.sleep(10800)

                if not self.is_tracking:
                    break

                # Get current flight status
                message = get_flight_status(self.flight_number)

                # Check if flight has landed
                if self._is_flight_landed(message):
                    # Send final notification and stop tracking
                    send_notifications(
                        f"🛬 Flight {self.flight_number} has landed!\n\n{message}"
                    )
                    self.stop_tracking()
                    break
                else:
                    # Send hourly update
                    send_notifications(
                        f"🔄 Hourly update for {self.flight_number}\n\n{message}"
                    )
                    self.last_update = datetime.now(self.nz_tz)

            except Exception as e:
                send_notifications(f"❌ Error tracking {self.flight_number}: {str(e)}")
                # Continue tracking despite errors

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
        print(f"Stopped tracking {self.flight_number}")


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
