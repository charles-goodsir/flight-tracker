# Flight Tracker API

A FastAPI-based flight tracking service that provides real-time flight information and sends notifications via Discord and Telegram.

## Features

- ✈️ Real-time flight tracking using AeroAPI
- 🕐 Departure and arrival times converted to New Zealand timezone
- 📱 Discord and Telegram notifications
- 🚀 FastAPI with automatic API documentation
- 🔄 Hot reload for development

## API Endpoints

### Track Flight
```
GET /track-flight/{flight_number}
```

**Parameters:**
- `flight_number` (string): IATA flight code (e.g., "NZ1", "BA123")

**Response:**
```json
{
  "message": "✈️ ANZ flight NZ1\nFrom: JFK\nTo: AKL\nDeparture: 2025-09-09 13:55 NZDT\nArrival: 2025-09-10 07:45 NZDT\nStatus: SCHEDULED"
}
```

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
# AeroAPI Configuration
AEROAPI_KEY=your_aeroapi_key_here

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

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Usage Examples

### Track a flight
```bash
curl "http://127.0.0.1:8000/track-flight/NZ1"
```

### Track another airline
```bash
curl "http://127.0.0.1:8000/track-flight/BA123"
```

## Project Structure

```
flight-tracker/
├── main.py              # FastAPI application
├── flight_api.py        # Flight data fetching logic
├── notifications.py     # Discord and Telegram notifications
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── README.md           # This file
└── venv/               # Virtual environment
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **AeroAPI**: Flight data provider
- **pytz**: Timezone handling
- **requests**: HTTP client
- **python-dotenv**: Environment variable management

## Timezone Handling

All flight times are automatically converted to New Zealand timezone (NZDT/NZST) for easy local reference.

## Error Handling

The API handles various error scenarios:
- Invalid API keys
- Flight not found
- Network errors
- Missing environment variables



## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues or questions:
1. Check the [API documentation](http://127.0.0.1:8000/docs)
2. Review the error messages in the terminal
3. Ensure all environment variables are set correctly
4. Verify your API keys are valid and have sufficient quota

## Changelog

### v1.0.0
- Initial release
- AeroAPI integration
- Discord and Telegram notifications
- New Zealand timezone support
- FastAPI with automatic documentation

This README provides comprehensive documentation for your flight tracker project, including setup instructions, API usage, and all the necessary configuration details.
