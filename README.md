# Flight Tracker API

A comprehensive FastAPI-based flight tracking service that provides real-time flight information, background tracking, and notifications via Discord and Telegram. Designed for continuous monitoring of flights with automatic updates and landing notifications.

## Features

- ✈️ **Real-time flight tracking** using AeroAPI by FlightAware
- 🔄 **Background tracking** with configurable update intervals (5 minutes to 24 hours)
- 📱 **Multi-platform notifications** via Discord and Telegram
- 🏥 **Health monitoring** with system resource tracking
- 🛡️ **Admin controls** with secure token-based authentication
- 🕐 **Timezone conversion** - all times displayed in New Zealand timezone
- 🚀 **Production ready** with systemd service and crash recovery
- 📊 **Comprehensive logging** and error handling
- 🔧 **RESTful API** with automatic documentation

## API Endpoints

### Public Endpoints

#### Track Flight (One-time)
```
GET /track-flight/{flight_number}
```
**Parameters:**
- `flight_number` (string): IATA flight code (e.g., "NZ1", "BA123")

#### Health Check
```
GET /health
```
Returns system health status and tracking information.

### Admin Endpoints (Require Admin Token)

#### Start Background Tracking
```
POST /start-tracking/{flight_number}
```
Starts continuous background tracking for a flight.

#### Stop Tracking
```
POST /stop-tracking
```
Stops all background tracking.

#### Set Update Interval
```
POST /set-interval/{seconds}
```
Sets the tracking update interval (minimum 300 seconds).

#### Manual Update
```
POST /update-now/{flight_number}
```
Triggers an immediate flight status update.

#### Tracking Status
```
GET /tracking-status
```
Returns current tracking status and configuration.

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd flight-tracker
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# AeroAPI Configuration (Required)
AEROAPI_KEY=your_aeroapi_key_here

# Admin Security (Required for production)
ADMIN_TOKEN=your_secure_admin_token_here

# Discord Configuration (Optional)
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# Telegram Configuration (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 5. Get API Keys

#### AeroAPI (Required)
1. Sign up at [AeroAPI by FlightAware](https://aeroapi.flightaware.com/)
2. Get your API key from the dashboard
3. Add it to your `.env` file as `AEROAPI_KEY`

#### Discord (Optional)
1. Create a Discord webhook in your server
2. Copy the webhook URL to `DISCORD_WEBHOOK_URL`

#### Telegram (Optional)
1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token and add it to `TELEGRAM_BOT_TOKEN`
3. Get your chat ID and add it to `TELEGRAM_CHAT_ID`

## Running the Application

### Development Mode
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## AWS Lightsail Deployment

### 1. Launch Lightsail Instance
- Choose Ubuntu 20.04 or 22.04 LTS
- Select appropriate instance size (nano is sufficient for basic usage)

### 2. Configure Security Groups
- Open ports 22 (SSH), 80 (HTTP), and 443 (HTTPS)
- For API access only, you can restrict to specific IPs

### 3. Deploy Application
```bash
# Connect to your instance
ssh ubuntu@your-instance-ip

# Clone your repository
git clone <your-repo-url>
cd flight-tracker

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your API keys
nano .env

# Test the application
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Set up as Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/flight-tracker.service

# Add the service configuration (see below)
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable flight-tracker
sudo systemctl start flight-tracker
```

### 5. Configure Nginx (Optional)
For HTTPS and domain access:
```bash
# Install Nginx
sudo apt update
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/default

# Install SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Systemd Service Configuration

Create `/etc/systemd/system/flight-tracker.service`:

```ini
[Unit]
Description=Flight Tracker API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/flight-tracker
ExecStart=/home/ubuntu/flight-tracker/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
RestartPreventExitStatus=0

[Install]
WantedBy=multi-user.target
```

## Usage Examples

### Start tracking a flight
```bash
curl -X POST "http://your-server:8000/start-tracking/NZ1" \
  -H "Authorization: Bearer your_admin_token"
```

### Check tracking status
```bash
curl "http://your-server:8000/tracking-status" \
  -H "Authorization: Bearer your_admin_token"
```

### Manual flight check
```bash
curl "http://your-server:8000/track-flight/NZ1"
```

### Set update interval to 1 hour
```bash
curl -X POST "http://your-server:8000/set-interval/3600" \
  -H "Authorization: Bearer your_admin_token"
```

## Background Tracking Features

### Automatic Updates
- Configurable interval (default: 3 hours)
- Minimum interval: 5 minutes
- Maximum interval: 24 hours

### Smart Notifications
- **Start notification**: When tracking begins
- **Progress updates**: At each interval with status changes
- **Landing notification**: When flight arrives with summary
- **Error notifications**: If tracking fails repeatedly
- **Crash notifications**: If the service stops unexpectedly

### Landing Detection
The system automatically detects when a flight has landed based on status messages like:
- "Arrived / Gate Arrival"
- "Landed"
- "Arrived"

### Error Handling
- Automatic retry on API failures
- Graceful shutdown after max errors (default: 5)
- Comprehensive logging for debugging

## Project Structure

```
flight-tracker/
├── main.py              # FastAPI application with all endpoints
├── flight_api.py        # AeroAPI integration and data parsing
├── flight_tracker.py    # Background tracking logic
├── notifications.py     # Discord and Telegram notifications
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── README.md           # This file
├── venv/               # Virtual environment
└── flight-tracker.service  # Systemd service file
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **AeroAPI**: Flight data provider by FlightAware
- **pytz**: Timezone handling
- **requests**: HTTP client
- **python-dotenv**: Environment variable management
- **psutil**: System resource monitoring
- **uvicorn**: ASGI server

## Security Features

- **Admin token authentication** for sensitive endpoints
- **Input validation** for all parameters
- **Rate limiting** through configurable intervals
- **Error sanitization** to prevent information leakage

## Monitoring and Health Checks

The `/health` endpoint provides:
- Service uptime
- Current tracking status
- System resource usage (CPU, memory, disk)
- Last update timestamp
- Error count

## Timezone Handling

All flight times are automatically converted to New Zealand timezone (NZDT/NZST) for easy local reference. The system handles:
- Departure times (scheduled, estimated, actual)
- Arrival times (scheduled, estimated, actual)
- Status timestamps

## Error Handling

The API handles various error scenarios:
- Invalid API keys
- Flight not found
- Network errors
- Missing environment variables
- Service crashes
- API rate limiting

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://your-server:8000/docs`
- **ReDoc**: `http://your-server:8000/redoc`

## Troubleshooting

### Service won't start
```bash
# Check service status
sudo systemctl status flight-tracker

# View logs
sudo journalctl -u flight-tracker -f

# Check for missing dependencies
sudo /path/to/venv/bin/python -m pip install -r requirements.txt
```

### API calls failing
1. Verify your AeroAPI key is valid
2. Check if you have sufficient API quota
3. Ensure the flight number exists and is active
4. Check network connectivity

### Notifications not working
1. Verify webhook URLs and tokens are correct
2. Check Discord server permissions
3. Ensure Telegram bot is properly configured
4. Test with manual API calls

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues or questions:
1. Check the [API documentation](http://your-server:8000/docs)
2. Review the service logs: `sudo journalctl -u flight-tracker -f`
3. Ensure all environment variables are set correctly
4. Verify your API keys are valid and have sufficient quota
5. Check the health endpoint: `curl http://your-server:8000/health`

## Changelog

### v2.0.0
- Added background tracking with configurable intervals
- Implemented admin token authentication
- Added health monitoring and system resource tracking
- Enhanced notification system with landing detection
- Added systemd service configuration
- Improved error handling and crash recovery
- Added comprehensive logging

### v1.0.0
- Initial release
- AeroAPI integration
- Discord and Telegram notifications
- New Zealand timezone support
- FastAPI with automatic documentation

---

**Note**: This flight tracker is designed for personal use and monitoring. Ensure you comply with AeroAPI's terms of service and rate limits. The system is optimized for cost-effectiveness with configurable update intervals to minimize API calls.