# PrecisionPulse Desktop

A desktop application for real-time telemetry monitoring and data streaming. Built with PySide6, this app connects to MQTT brokers to stream sensor data and provides automatic synchronization between desktop and web platforms.

## What It Does

- Streams telemetry data every 3 seconds using MQTT protocol
- Syncs users, configurations, and parameters automatically across platforms
- Buffers data locally when offline and syncs when connection is restored
- Provides role-based access control (Admin, Client, User)
- Shows live dashboard with trend charts that update without manual refresh
- Lets admins manage users and configure telemetry parameters

## Built With

- PySide6 (Qt6 for Python)
- SQLite for local storage
- MQTT (paho-mqtt) for telemetry streaming to backend
- WebSocket (python-socketio) for receiving real-time updates from backend (optional)
- Argon2 for secure password hashing
- Python 3.8+

## Architecture

The desktop application uses a **dual protocol** approach:

**MQTT (Outbound):**
- Publishes telemetry data to MQTT broker
- Sends user/config/parameter sync commands
- Handles offline buffering and auto-sync

**WebSocket (Inbound - Optional):**
- Receives real-time updates from backend for dashboard display
- Updates charts and values without manual refresh
- Gracefully degrades if backend is not running

**Standalone Mode:**
The desktop works fully offline, generating and displaying its own telemetry data. WebSocket is only needed if you want to receive data from other sources via the backend.

## Getting Started

**Clone the repo:**
```bash
git clone <repository-url>
cd dspl-precision-pulse-desktop
```

**Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure your environment:**
```bash
cp .env.example .env
```
Then edit `.env` with your MQTT broker details.

**Run the app:**
```bash
python main.py
```

## Login Credentials

The app comes with three default accounts:

- **Admin**: admin@precisionpulse.com / admin123 (full access)
- **Client**: client@precisionpulse.com / client123 (can send data)
- **User**: user@precisionpulse.com / user123 (view only)

## Configuration

You can customize settings in the `.env` file:

```env
MQTT_BROKER=localhost
MQTT_PORT=8883
MQTT_USE_TLS=false
TELEMETRY_INTERVAL=3
HEARTBEAT_INTERVAL=30
DATABASE_PATH=data/precision_pulse.db
```

## How Sync Works

Everything syncs automatically through MQTT:

- User changes (create/update/delete) sync instantly
- Parameter toggles propagate to all connected clients
- Config updates apply without restart
- Telemetry data buffers offline and syncs when reconnected

**MQTT Topics:**
- `precisionpulse/telemetry` - live sensor data
- `precisionpulse/heartbeat` - connection status
- `precisionpulse/sync/users/#` - user sync
- `precisionpulse/sync/config` - config sync
- `precisionpulse/sync/parameters` - parameter sync
- `precisionpulse/commands/config/update` - remote config


## Database

The app uses SQLite with these main tables:

- **users** - credentials (Argon2 hashed), roles, sync status
- **telemetry_buffer** - queues data when offline
- **parameters** - telemetry stream definitions
- **config** - key-value settings


