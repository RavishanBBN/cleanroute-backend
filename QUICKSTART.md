# CleanRoute - Quick Start Guide

## Prerequisites

- PostgreSQL running with database `cleanroute_db`
- Python 3.10+ with venv
- Mosquitto MQTT broker installed

---

## 🚀 Start the Full Stack (4 Terminals)

### Terminal 1: MQTT Broker (Secure Mode)

```bash
# Stop system mosquitto if running
sudo systemctl stop mosquitto

# Start with TLS + Authentication
mosquitto -c /home/thevinduk/Repositories/cleanroute-backend/mqtt/mosquitto_secure.conf -v
```

**Expected output:**
```
mosquitto version 2.0.x starting
Opening ipv4 listen socket on port 1883 (localhost only)
Opening ipv4 listen socket on port 8883 (TLS)
```

---

### Terminal 2: FastAPI Backend (Secure Mode)

```bash
cd /home/thevinduk/Repositories/cleanroute-backend/backend && \
source .venv/bin/activate && \
source .env.secure && \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
🚀 Starting CleanRoute Backend...
🔐 TLS enabled with CA: .../mqtt/certs/ca.crt
🔑 Authenticating as: backend_service
✅ Connected to MQTT broker at localhost:8883
📡 Subscribed to: cleanroute/bins/+/telemetry (QoS=1)
Uvicorn running on http://0.0.0.0:8000
```

---

### Terminal 3: Flask Frontend

```bash
cd /home/thevinduk/Repositories/cleanroute-backend/frontend && \
source ../backend/.venv/bin/activate && \
python app.py
```

**Expected output:**
```
🚀 Starting CleanRoute Frontend...
�� Dashboard: http://localhost:5001
🔗 Backend: http://localhost:8000 (enabled)
Running on http://0.0.0.0:5001
```

---

### Terminal 4: Test / Simulate Devices

#### Publish as a device (secure):
```bash
mosquitto_pub -h localhost -p 8883 \
  --cafile /home/thevinduk/Repositories/cleanroute-backend/mqtt/certs/ca.crt \
  -u "GAL001" -P "galle_bin_001_secret" \
  -t "cleanroute/bins/GAL001/telemetry" \
  -m '{"ts":"2025-12-13T10:00:00Z","bin_id":"GAL001","fill_pct":55.0,"batt_v":4.0,"temp_c":29.5,"lat":6.0328,"lon":80.2170}'
```

#### Publish multiple bins:
```bash
# Colombo bin
mosquitto_pub -h localhost -p 8883 \
  --cafile /home/thevinduk/Repositories/cleanroute-backend/mqtt/certs/ca.crt \
  -u "COL001" -P "bin_COL001_secret" \
  -t "cleanroute/bins/COL001/telemetry" \
  -m '{"ts":"2025-12-13T10:00:00Z","bin_id":"COL001","fill_pct":78.0,"batt_v":3.9,"temp_c":30.0,"lat":6.9271,"lon":79.8612}'

# Kandy bin
mosquitto_pub -h localhost -p 8883 \
  --cafile /home/thevinduk/Repositories/cleanroute-backend/mqtt/certs/ca.crt \
  -u "KAN001" -P "kandy_bin_001_secret" \
  -t "cleanroute/bins/KAN001/telemetry" \
  -m '{"ts":"2025-12-13T10:00:00Z","bin_id":"KAN001","fill_pct":42.0,"batt_v":4.1,"temp_c":26.0,"lat":7.2906,"lon":80.6337}'
```

---

## 🌐 Access URLs

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:5001 |
| Districts View | http://localhost:5001/districts |
| Backend API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## 🔐 Device Credentials

| Bin ID | Username | Password |
|--------|----------|----------|
| Backend | `backend_service` | `CleanRoute@2025` |
| B001 | `B001` | `bin_B001_secret` |
| COL001 | `COL001` | `bin_COL001_secret` |
| COL002 | `COL002` | `bin_COL002_secret` |
| KUR001 | `KUR001` | `bin_KUR001_secret` |
| GAL001 | `GAL001` | `galle_bin_001_secret` |
| GAL002 | `GAL002` | `galle_bin_002_secret` |
| GAL003 | `GAL003` | `galle_bin_003_secret` |
| KAN001 | `KAN001` | `kandy_bin_001_secret` |
| KAN002 | `KAN002` | `kandy_bin_002_secret` |
| MAT001 | `MAT001` | `matara_bin_001_secret` |

### Add new device:
```bash
mosquitto_passwd -b mqtt/passwd <BIN_ID> <PASSWORD>
```

---

## 🛑 Stopping Services

- **Terminal 1-3:** Press `Ctrl+C`
- **Kill by port:** `sudo kill $(sudo lsof -t -i:8000)`

---

## 🔧 Troubleshooting

### "Address already in use"
```bash
# Kill process on port
sudo kill $(sudo lsof -t -i:8000)  # Backend
sudo kill $(sudo lsof -t -i:5001)  # Frontend
sudo systemctl stop mosquitto       # Broker
```

### Backend can't connect to MQTT
- Make sure Terminal 1 (Mosquitto) is running first
- Check TLS is enabled: `source .env.secure`

### Bins not showing on map
- Click "Fit All Bins" button
- Check bins have valid lat/lon coordinates
- View console (F12) for errors
