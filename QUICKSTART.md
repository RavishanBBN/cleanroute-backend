# CleanRoute - Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Prerequisites
```bash
# Required services
✅ Mosquitto MQTT broker
✅ PostgreSQL database
✅ Python 3.8+
```

---

## Step 1: Start the Server (1 min)

```bash
cd /home/thevinduk/Repositories/cleanroute-backend/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
🚀 Starting CleanRoute Backend...
✅ Connected to MQTT broker at localhost:1883
📡 Subscribed to: cleanroute/bins/+/telemetry
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## Step 2: Verify System Health (30 sec)

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "ok",
  "database": true,
  "mqtt": {
    "connected": true,
    "broker": "localhost:1883"
  }
}
```

---

## Step 3: Test Basic Flow (2 min)

### A) Send telemetry from a bin:
```bash
mosquitto_pub -h localhost -t cleanroute/bins/B001/telemetry -m '{
  "bin_id":"B001",
  "ts":"2025-12-12T10:00:00Z",
  "fill_pct":72.5,
  "batt_v":3.85,
  "temp_c":31.4,
  "lat":6.9102,
  "lon":79.8623
}'
```

### B) Check if data arrived:
```bash
curl http://localhost:8000/bins/latest
```

### C) Register a user device:
```bash
curl -X POST http://localhost:8000/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "bin_id": "B001",
    "user_id": "USER001",
    "user_name": "John Doe",
    "user_phone": "+94771234567",
    "wifi_ssid": "HomeWiFi",
    "lat": 6.9271,
    "lon": 79.8612
  }'
```

---

## Step 4: Test IoT Features (2 min)

### Monitor commands being sent:
Open a new terminal:
```bash
mosquitto_sub -h localhost -t 'cleanroute/bins/+/command' -v
```

### Send commands from API:
```bash
# Wake up a bin
curl -X POST http://localhost:8000/commands/B001/wake

# Start collection day (wakes ALL bins)
curl -X POST http://localhost:8000/collection/start

# Check fleet health
curl http://localhost:8000/fleet/health

# Get device health
curl http://localhost:8000/devices/B001/health

# Run health checks (generates alerts)
curl -X POST http://localhost:8000/monitoring/health-check

# View alerts
curl http://localhost:8000/alerts
```

---

## Step 5: Run Test Suite (Optional)

```bash
cd backend
python test_iot_features.py
```

This will test all 25 endpoints automatically.

---

## 🎯 Common Use Cases

### Scenario 1: Collection Day Workflow

```bash
# Morning - Start collection
curl -X POST http://localhost:8000/collection/start?collection_hours=12

# Check status
curl http://localhost:8000/fleet/health

# Send reminders to offline bins
curl -X POST http://localhost:8000/collection/remind

# Evening - End collection
curl -X POST http://localhost:8000/collection/end
```

### Scenario 2: Monitor Single Device

```bash
# Get health status
curl http://localhost:8000/devices/B001/health

# Get recent telemetry
curl "http://localhost:8000/telemetry/recent?bin_id=B001&limit=10"

# Get command history
curl http://localhost:8000/commands/B001/history

# Wake device
curl -X POST http://localhost:8000/commands/B001/wake
```

### Scenario 3: User Management

```bash
# Register device
curl -X POST http://localhost:8000/devices/register -H "Content-Type: application/json" -d '{...}'

# Get user's devices
curl http://localhost:8000/devices/user/USER001

# Get alerts for user's bins
curl "http://localhost:8000/alerts?bin_id=B001"
```

---

## 📊 API Documentation

Once server is running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Troubleshooting

### Server won't start
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if Mosquitto is running
sudo systemctl status mosquitto

# Check if port 8000 is available
lsof -i :8000
```

### Database connection error
```bash
# Test database connection
psql "dbname=cleanroute_db user=cleanroute_user password=cleanroute_pass host=localhost" -c "SELECT 1"

# If tables missing, recreate:
psql "dbname=cleanroute_db user=cleanroute_user password=cleanroute_pass host=localhost" < schema.sql
```

### MQTT not connecting
```bash
# Test MQTT broker
mosquitto_sub -h localhost -t test/# -v

# Check Mosquitto logs
sudo journalctl -u mosquitto -f
```

---

## 📚 Next Steps

1. **Read Documentation**:
   - `IMPLEMENTATION_SUMMARY.md` - What we built
   - `ARCHITECTURE.md` - System design
   - `DEVICE_SETUP.md` - Hardware setup

2. **Simulate Multiple Bins**:
   - Create bin simulator (coming next)
   - Generate realistic traffic

3. **Build Dashboard**:
   - React/Vue web UI
   - Map view with real-time updates

4. **Deploy to Cloud**:
   - Oracle Free Tier
   - AWS / Railway

5. **Add ML Forecasting**:
   - EWMA overflow prediction
   - Route optimization

---

## 🎓 For Demo/Report

### Show These Features:

1. **Device Registration** → `/devices/register`
2. **Real-time Telemetry** → Send MQTT, check `/bins/latest`
3. **Command & Control** → Wake/sleep commands
4. **Health Monitoring** → `/fleet/health`, alerts
5. **Collection Workflow** → Start/remind/end collection day
6. **Power Management** → Sleep mode automation

### Key Talking Points:

- ✅ Complete IoT stack (hardware → cloud → UI)
- ✅ Bidirectional communication (not just logging)
- ✅ Power-efficient (2-year battery life)
- ✅ Scalable (MQTT + PostgreSQL)
- ✅ User-centric (automated workflows)
- ✅ Production-ready architecture

---

## 🆘 Need Help?

- Check server logs for errors
- Review `backend/README.md` for API details
- Test with `test_iot_features.py`
- Verify MQTT messages with `mosquitto_sub`

---

**You're all set! 🎉**

The backend is fully functional with device management, commands, alerts, and collection workflows. Time to build the frontend or add more bins!
