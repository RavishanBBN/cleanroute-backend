# CleanRoute IoT Design Justification

This document explains how CleanRoute addresses the **constrained nature of IoT devices** and justifies the design decisions made for the smart waste bin monitoring system.

---

## 1. Communication Protocol Selection

### Why MQTT over HTTP?

| Aspect | HTTP | MQTT (Our Choice) |
|--------|------|-------------------|
| **Header Overhead** | 200-800 bytes | 2-4 bytes |
| **Connection** | New connection per request | Persistent connection |
| **Power Usage** | High (TLS handshake each time) | Low (single handshake) |
| **Bandwidth** | High | Very Low |
| **Suitable for IoT** | No | Yes |

### MQTT Configuration

```
Protocol: MQTT v3.1.1
Broker: Mosquitto (self-hosted)
Port: 8883 (TLS encrypted)
QoS Level: 1 (At-least-once delivery)
Keep-alive: 60 seconds
```

**QoS 1 Justification:**
- QoS 0: Too unreliable for waste collection data
- QoS 1: Ensures delivery, minimal overhead (perfect for our use case)
- QoS 2: Unnecessary overhead for telemetry data

---

## 2. Spectrum Usage & Bandwidth Efficiency

### Wireless Communication Stack

```
┌─────────────────────────────────────┐
│  Application Layer: MQTT           │
├─────────────────────────────────────┤
│  Security Layer: TLS 1.2           │
├─────────────────────────────────────┤
│  Transport Layer: TCP              │
├─────────────────────────────────────┤
│  Network Layer: IP (WiFi/Cellular) │
├─────────────────────────────────────┤
│  Physical Layer: 2.4GHz WiFi       │
│  OR GSM/LTE for cellular           │
└─────────────────────────────────────┘
```

### Spectrum Options for Deployment

| Technology | Frequency | Range | Power | Best For |
|------------|-----------|-------|-------|----------|
| **WiFi 2.4GHz** | 2.4 GHz | 50m | Medium | Urban bins near buildings |
| **LoRaWAN** | 868/915 MHz | 5km | Very Low | Rural areas |
| **NB-IoT** | Licensed LTE | 10km | Low | City-wide deployment |
| **Cellular (4G)** | Licensed | Unlimited | High | Mobile/remote bins |

**Current Implementation:** WiFi 2.4GHz for urban Colombo deployment.

### Bandwidth Calculation

```
Single Telemetry Message:
- Payload size: ~150 bytes (JSON)
- MQTT header: 4 bytes
- TLS overhead: ~40 bytes
- Total: ~194 bytes per message

Daily Usage (per bin):
- Normal mode: 1 message/day = 194 bytes
- Collection day: 24 messages (hourly) = 4,656 bytes
- Average: ~500 bytes/day per bin

Fleet Usage (32 bins):
- Normal day: 32 × 194 = 6.2 KB
- Collection day: 32 × 4,656 = 149 KB
- Monthly estimate: ~3 MB total
```

This is extremely efficient - a single photo is larger than a month of telemetry!

---

## 3. Constrained Device Optimizations

### 3.1 Power Management

**Problem:** Battery-powered bins can't be charged frequently.

**Solution:** Sleep/Wake Mode

```
Normal State (Sleep Mode):
├── Device sleeps for 23+ hours
├── No WiFi connection
├── Power consumption: ~10μA
└── Battery life: 2-3 years

Collection Day (Wake Mode):
├── Backend sends "wake_up" command
├── Device connects to WiFi
├── Sends telemetry hourly for 12 hours
├── Power consumption: ~80mA (active)
└── Returns to sleep after collection
```

**Implementation:**
```python
# Backend command to wake device
mqtt_commands.wake_up_bin("COL401", collection_hours=12)

# Backend command to sleep device
mqtt_commands.sleep_bin("COL401")
```

### 3.2 Payload Size Optimization

**Problem:** Limited bandwidth and battery drain from transmitting data.

**Solution:** Minimal JSON payload

```json
{
    "bin_id": "COL401",
    "ts": "2025-12-14T10:00:00Z",
    "fill_pct": 72.5,
    "batt_v": 3.85,
    "temp_c": 31.4,
    "emptied": 0
}
```

| Field | Type | Size | Purpose |
|-------|------|------|---------|
| `bin_id` | string | 6 bytes | Device identifier |
| `ts` | ISO8601 | 24 bytes | Timestamp |
| `fill_pct` | float | 4 bytes | Fill level (0-100) |
| `batt_v` | float | 4 bytes | Battery voltage |
| `temp_c` | float | 4 bytes | Temperature |
| `emptied` | int | 1 byte | Collection flag |

**Total: ~150 bytes** (including JSON formatting)

### 3.3 Memory Constraints

**Problem:** ESP32/ESP8266 devices have limited RAM (4-520KB).

**Solution:**
- Small payload sizes (150 bytes fits in any buffer)
- No complex JSON parsing on device (simple key-value)
- Command responses use single-byte status codes

### 3.4 Processing Power

**Problem:** Microcontrollers have limited CPU.

**Solution:**
- All ML predictions happen on the **backend server**
- Device only measures sensors and transmits
- Simple firmware with minimal computation

---

## 4. Performance Monitoring

### Available Metrics (GET /api/iot/metrics)

| Metric Category | What It Shows |
|-----------------|---------------|
| **Message Throughput** | Messages/day, latency, active devices |
| **Command Delivery** | ACK rate, retry count, failures |
| **Device Connectivity** | Online/offline/sleeping counts |
| **Power Efficiency** | Battery levels, drain rates |
| **Network Performance** | RSSI (signal strength), uptime |

### Key Performance Indicators (KPIs)

| KPI | Target | Why It Matters |
|-----|--------|----------------|
| Message Delivery Rate | >99% | Ensures no data loss |
| Command ACK Rate | >95% | Reliable device control |
| Average Latency | <2 seconds | Real-time awareness |
| Battery Life | >1 year | Reduces maintenance |
| Online Rate | >90% | Fleet availability |

---

## 5. Reliability Features

### 5.1 Command Acknowledgment (ACK)

```
Backend                          Device
   │                               │
   │──── command (wake_up) ───────>│
   │                               │
   │<─── ACK (success/fail) ───────│
   │                               │
   │ (if no ACK in 30s, retry)     │
   │──── command (retry 1) ───────>│
   │                               │
```

**Implementation:** Commands are tracked in `command_acknowledgments` table with retry logic.

### 5.2 Device Shadow (Offline State)

**Problem:** What if device is offline when we query it?

**Solution:** Device Shadow pattern (like AWS IoT)

```
┌─────────────────┐     ┌─────────────────┐
│  Actual Device  │     │  Device Shadow  │
│  (may be off)   │     │  (always on)    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │── reports state ─────>│
         │                       │
    (device sleeps)              │
                                 │
         Backend queries ───────>│
         │                       │
         │<── returns last ──────│
         │    known state        │
```

### 5.3 OTA Firmware Updates

**Problem:** Can't physically access 1000+ bins to update software.

**Solution:** Over-the-air updates

```python
# Push firmware update to device
mqtt_commands.send_firmware_update(
    bin_id="COL401",
    version="2.1.0",
    file_url="https://firmware.cleanroute.lk/v2.1.0.bin",
    checksum="sha256:abc123..."
)
```

---

## 6. Security Measures

| Layer | Protection |
|-------|------------|
| **Transport** | TLS 1.2 encryption (port 8883) |
| **Authentication** | Username/password per device |
| **Authorization** | Topic-level ACLs in Mosquitto |
| **Provisioning** | Unique credentials per device |

---

## 7. Scalability Considerations

| Scale | Bins | Messages/Day | Database Size/Year |
|-------|------|--------------|-------------------|
| Pilot | 32 | 768 | 50 MB |
| District | 500 | 12,000 | 800 MB |
| City-wide | 5,000 | 120,000 | 8 GB |
| National | 50,000 | 1.2M | 80 GB |

The system is designed to scale horizontally by:
- Adding MQTT broker clusters
- Database read replicas
- Load-balanced API servers

---

## 8. Summary: How We Address Constrained IoT

| Constraint | Our Solution |
|------------|--------------|
| **Limited Battery** | Sleep mode, wake-on-demand |
| **Limited Bandwidth** | MQTT (not HTTP), 150-byte payloads |
| **Limited Memory** | Simple JSON, no complex parsing |
| **Limited Processing** | All ML on server, not device |
| **Unreliable Network** | QoS 1, ACK/retry, device shadow |
| **Security Risks** | TLS, per-device auth, ACLs |
| **Remote Location** | OTA updates, remote diagnostics |

---

## 9. API Endpoints for IoT Management

| Endpoint | Purpose |
|----------|---------|
| `GET /api/iot/metrics` | Performance dashboard |
| `POST /api/iot/provision` | Register new device |
| `GET /api/iot/device/{id}/shadow` | Get device shadow state |
| `POST /api/iot/device/{id}/diagnostic` | Request diagnostics |
| `POST /api/iot/firmware/update` | Push OTA update |
| `GET /api/iot/commands/pending` | Check pending commands |
| `POST /api/iot/heartbeat/check` | Monitor device health |

---

*This document demonstrates awareness of IoT constraints and justifies the engineering decisions made in CleanRoute.*
