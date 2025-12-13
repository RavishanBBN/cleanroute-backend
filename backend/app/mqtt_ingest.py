"""
MQTT Ingest Service for CleanRoute.
Subscribes to bin telemetry topics and stores data in PostgreSQL.

Topic format: cleanroute/bins/<BIN_ID>/telemetry
Payload format:
{
    "bin_id": "B001",
    "ts": "2025-12-12T10:00:00Z",
    "fill_pct": 72.5,
    "batt_v": 3.85,
    "temp_c": 31.4,
    "emptied": 0,
    "lat": 6.9102,
    "lon": 79.8623
}

Security: Supports TLS encryption and username/password authentication.
Set MQTT_USE_TLS=true to enable secure connection on port 8883.
"""
import json
import logging
import threading
import ssl
import os
from datetime import datetime
from dateutil import parser as date_parser

import paho.mqtt.client as mqtt

from . import config
from . import db

# ─────────────────────────────────────────────────────────────────────────────
# Logging Setup
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Global State
# ─────────────────────────────────────────────────────────────────────────────
mqtt_client = None
mqtt_connected = False
message_count = 0


# ─────────────────────────────────────────────────────────────────────────────
# MQTT Callbacks
# ─────────────────────────────────────────────────────────────────────────────

def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker."""
    global mqtt_connected
    if rc == 0:
        logger.info(f"✅ Connected to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
        mqtt_connected = True
        # Subscribe to bin telemetry topic with QoS 1
        client.subscribe(config.MQTT_TOPIC, qos=1)
        logger.info(f"📡 Subscribed to: {config.MQTT_TOPIC} (QoS=1)")
    else:
        logger.error(f"❌ Failed to connect to MQTT broker, return code: {rc}")
        mqtt_connected = False


def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker."""
    global mqtt_connected
    mqtt_connected = False
    logger.warning(f"🔌 Disconnected from MQTT broker (rc={rc})")


def on_message(client, userdata, msg):
    """
    Called when a message is received from subscribed topic.
    Parses the payload and stores it in PostgreSQL.
    """
    global message_count
    
    try:
        # Parse topic to extract bin_id (backup)
        # Topic format: cleanroute/bins/<BIN_ID>/telemetry
        topic_parts = msg.topic.split("/")
        topic_bin_id = topic_parts[2] if len(topic_parts) >= 3 else None
        
        # Parse JSON payload
        payload = json.loads(msg.payload.decode("utf-8"))
        
        # Extract required fields
        bin_id = payload.get("bin_id") or topic_bin_id
        ts = payload.get("ts")
        fill_pct = payload.get("fill_pct")
        
        # Validate required fields
        if not bin_id:
            logger.warning(f"⚠️ Missing bin_id in message: {payload}")
            return
        if ts is None:
            logger.warning(f"⚠️ Missing timestamp in message from {bin_id}")
            return
        if fill_pct is None:
            logger.warning(f"⚠️ Missing fill_pct in message from {bin_id}")
            return
        
        # Validate fill_pct range
        if not (0 <= fill_pct <= 100):
            logger.warning(f"⚠️ Invalid fill_pct ({fill_pct}) from {bin_id}, must be 0-100")
            return
        
        # Parse timestamp
        try:
            parsed_ts = date_parser.parse(ts)
        except Exception as e:
            logger.warning(f"⚠️ Invalid timestamp format from {bin_id}: {ts}")
            return
        
        # Extract optional fields
        batt_v = payload.get("batt_v")
        temp_c = payload.get("temp_c")
        emptied = bool(payload.get("emptied", 0))
        lat = payload.get("lat")
        lon = payload.get("lon")
        
        # UPSERT bin record
        db.upsert_bin(
            bin_id=bin_id,
            lat=lat,
            lon=lon,
            last_seen=parsed_ts.isoformat()
        )
        
        # Update device status to online
        db.update_device_status(bin_id, "online")
        
        # If emptied flag is set, update last_emptied
        if emptied:
            db.update_bin_emptied(bin_id, parsed_ts.isoformat())
        
        # INSERT telemetry record
        db.insert_telemetry(
            ts=parsed_ts.isoformat(),
            bin_id=bin_id,
            fill_pct=fill_pct,
            batt_v=batt_v,
            temp_c=temp_c,
            emptied=emptied,
            lat=lat,
            lon=lon
        )
        
        message_count += 1
        logger.info(f"📥 [{message_count}] Stored telemetry for {bin_id}: fill={fill_pct}%")
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON payload: {msg.payload}")
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Ingest Control
# ─────────────────────────────────────────────────────────────────────────────

def start_mqtt_ingest():
    """
    Start the MQTT ingest service in a background thread.
    Call this from your FastAPI startup.
    
    Supports two modes:
    - Insecure (default): Plain MQTT on port 1883
    - Secure (MQTT_USE_TLS=true): TLS + Auth on port 8883
    """
    global mqtt_client
    
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    
    # Determine connection mode
    if config.MQTT_USE_TLS:
        port = config.MQTT_TLS_PORT
        
        # Configure TLS
        ca_cert_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            config.MQTT_CA_CERT
        )
        
        if not os.path.exists(ca_cert_path):
            logger.error(f"❌ CA certificate not found: {ca_cert_path}")
            raise FileNotFoundError(f"CA certificate not found: {ca_cert_path}")
        
        mqtt_client.tls_set(
            ca_certs=ca_cert_path,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        
        # Set username/password authentication
        mqtt_client.username_pw_set(
            config.MQTT_USERNAME,
            config.MQTT_PASSWORD
        )
        
        logger.info(f"🔐 TLS enabled with CA: {ca_cert_path}")
        logger.info(f"🔑 Authenticating as: {config.MQTT_USERNAME}")
    else:
        port = config.MQTT_PORT
        logger.info("⚠️  Running in INSECURE mode (no TLS)")
    
    try:
        mqtt_client.connect(config.MQTT_BROKER, port, keepalive=60)
        # Start network loop in background thread
        mqtt_client.loop_start()
        logger.info(f"🚀 MQTT ingest service started on {config.MQTT_BROKER}:{port}")
    except Exception as e:
        logger.error(f"❌ Failed to start MQTT ingest: {e}")
        raise


def stop_mqtt_ingest():
    """Stop the MQTT ingest service."""
    global mqtt_client
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("🛑 MQTT ingest service stopped")


def get_ingest_status():
    """Get current status of the MQTT ingest service."""
    port = config.MQTT_TLS_PORT if config.MQTT_USE_TLS else config.MQTT_PORT
    return {
        "connected": mqtt_connected,
        "broker": f"{config.MQTT_BROKER}:{port}",
        "topic": config.MQTT_TOPIC,
        "messages_processed": message_count,
        "tls_enabled": config.MQTT_USE_TLS,
        "authenticated": config.MQTT_USE_TLS  # Auth is required with TLS
    }
