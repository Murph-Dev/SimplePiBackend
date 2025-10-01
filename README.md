# 🌡️ Pi Sensor Data Backend

A lightweight FastAPI backend for Raspberry Pi Zero to collect, store, and manage sensor data from Arduino devices. Features a web dashboard for viewing, editing, and deleting sensor readings.

## Features

- **Arduino Integration**: Receives sensor data via POST requests matching your Arduino JSON structure
- **Web Dashboard**: Clean, responsive interface to view and manage sensor data
- **CRUD Operations**: Create, read, update, and delete sensor readings
- **Real-time Updates**: Dashboard auto-refreshes every 30 seconds
- **Device Tracking**: Supports multiple Arduino devices via X-Device-ID header
- **Lightweight**: Optimized for Raspberry Pi Zero performance

## Sensor Data Structure

The backend expects JSON data from your Arduino in this format:
```json
{
  "temperature": 23.5,
  "humidity": 65.2,
  "lux": 850,
  "pumpActive": true,
  "lastReading": 1640995200
}
```

## API Endpoints

### Arduino Data Submission
- `POST /api/v1/sensor-data` - Receive sensor data from Arduino
  - Headers: `X-Device-ID: your_device_id`
  - Content-Type: `application/json`

### Web Dashboard API
- `GET /api/sensor-data` - List all sensor readings
- `GET /api/sensor-data/{id}` - Get specific reading
- `PUT /api/sensor-data/{id}` - Update reading
- `DELETE /api/sensor-data/{id}` - Delete reading
- `GET /api/health` - Health check

## Quick Start

1. **Install Dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Access the Dashboard**
   Open your browser to `http://your-pi-ip:8000`

4. **Test the API**
   ```bash
   python test_sensor_api.py
   ```

## Arduino Code Integration

Your existing Arduino code should work with minimal changes. The backend automatically:
- Extracts device ID from `X-Device-ID` header
- Handles the `pumpActive` field mapping to `pump_active`
- Stores timestamps and device information

## Web Dashboard Features

- **Latest Readings**: Real-time display of current sensor values
- **Data History**: Table view of all stored readings with filtering
- **Edit Capability**: Modify existing sensor readings
- **Delete Records**: Remove old or incorrect data
- **Responsive Design**: Works on desktop, tablet, and mobile

## Database

Uses SQLite database (`db.sqlite`) for lightweight storage. The database is automatically created on first run.

## Deploy to Raspberry Pi Zero W (LAN-only)

1) Copy the project to the Pi:
```bash
ssh pi@<pi-ip>
sudo apt update && sudo apt -y install python3-venv python3-pip nginx git
cd ~ && git clone <your-repo-url> pi_sensor_backend
cd pi_sensor_backend
```

2) Create venv & install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3) Test locally on the Pi
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
# From another device on your LAN: http://<pi-ip>:8000/
Ctrl+C to stop
```

4) Run under systemd (autostart, stays running)
Create file `/etc/systemd/system/pi_sensor_backend.service`:
```ini
[Unit]
Description=Pi Sensor Data Backend (Uvicorn)
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/pi_sensor_backend
Environment=PATH=/home/pi/pi_sensor_backend/.venv/bin
ExecStart=/home/pi/pi_sensor_backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```
Enable + start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pi_sensor_backend
sudo systemctl start pi_sensor_backend
sudo systemctl status pi_sensor_backend
```

5) Put Nginx in front (port 80, LAN only)
Create `/etc/nginx/sites-available/pi_sensor_backend`:
```nginx
server {
    listen 80;
    server_name _;

    # Basic hardening + small uploads
    client_max_body_size 5m;
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/pi_sensor_backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```
Now open: `http://<pi-ip>/`

6) Keep it LAN-only
- Do **not** set up port-forwarding on your router.
- Optionally add a ufw rule to restrict to your subnet (example for 192.168.1.0/24):
  ```bash
  sudo apt -y install ufw
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw allow from 192.168.1.0/24 to any port 80 proto tcp
  sudo ufw enable
  sudo ufw status
  ```

## Maintenance
- Update code: `git pull && sudo systemctl restart pi_sensor_backend`
- Logs: `sudo journalctl -u pi_sensor_backend -f`
- DB file: `./db.sqlite` (back it up with the app stopped)

## Performance Notes

- Optimized for Raspberry Pi Zero
- SQLite provides fast local storage
- Minimal memory footprint
- Efficient auto-refresh prevents unnecessary API calls