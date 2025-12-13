"""
MQTT Command Service - Downlink Commands to Bins
Sends commands FROM backend TO devices.

Command Topics:
- cleanroute/bins/{bin_id}/command
- cleanroute/bins/broadcast/command (all bins)

Command Types:
- wake_up: Activate device and start hourly telemetry
- sleep: Put device to sleep mode
- reset_emptied: Reset the emptied flag
- get_status: Request immediate status update
- update_config: Send new configuration

Security: Supports TLS encryption and username/password authentication.
"""
import json
import logging
import ssl
import os
from datetime import datetime
from typing import Optional, Dict, Any

import paho.mqtt.client as mqtt

from . import config
from . import db

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Global MQTT Client for Commands
# ─────────────────────────────────────────────────────────────────────────────
command_client = None


def init_command_client():
    """
    Initialize a separate MQTT client for publishing commands.
    Supports TLS + authentication when MQTT_USE_TLS=true.
    """
    global command_client
    if command_client is None:
        command_client = mqtt.Client(client_id="cleanroute_command_publisher")
        
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
            
            command_client.tls_set(
                ca_certs=ca_cert_path,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            
            # Set username/password authentication
            command_client.username_pw_set(
                config.MQTT_USERNAME,
                config.MQTT_PASSWORD
            )
            
            logger.info(f"🔐 Command client TLS enabled")
        else:
            port = config.MQTT_PORT
            logger.info("⚠️  Command client running in INSECURE mode")
        
        try:
            command_client.connect(config.MQTT_BROKER, port, keepalive=60)
            command_client.loop_start()
            logger.info(f"📤 Command publisher initialized on {config.MQTT_BROKER}:{port}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize command client: {e}")
            raise


def stop_command_client():
    """Stop the command client."""
    global command_client
    if command_client:
        command_client.loop_stop()
        command_client.disconnect()
        logger.info("🛑 Command publisher stopped")


# ─────────────────────────────────────────────────────────────────────────────
# Command Functions
# ─────────────────────────────────────────────────────────────────────────────

def send_command(
    bin_id: str,
    command_type: str,
    payload: Optional[Dict[str, Any]] = None,
    qos: int = 1,
    retain: bool = False
) -> bool:
    """
    Send a command to a specific bin.
    
    Args:
        bin_id: Target bin ID or "broadcast" for all bins
        command_type: Type of command (wake_up, sleep, etc.)
        payload: Additional command parameters
        qos: MQTT QoS level (0, 1, or 2)
        retain: Whether to retain the message
    
    Returns:
        True if command sent successfully
    """
    if command_client is None:
        init_command_client()
    
    topic = f"cleanroute/bins/{bin_id}/command"
    
    command_payload = {
        "command": command_type,
        "timestamp": datetime.utcnow().isoformat(),
        "params": payload or {}
    }
    
    try:
        result = command_client.publish(
            topic,
            json.dumps(command_payload),
            qos=qos,
            retain=retain
        )
        
        # Log command
        db.log_command(bin_id, command_type, command_payload)
        
        logger.info(f"📤 Sent {command_type} to {bin_id} (QoS={qos})")
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    except Exception as e:
        logger.error(f"❌ Failed to send command to {bin_id}: {e}")
        return False


def wake_up_bin(bin_id: str, collection_hours: int = 12) -> bool:
    """
    Send wake-up command to bin.
    Device should start sending telemetry hourly for specified hours.
    """
    payload = {
        "collection_hours": collection_hours,
        "telemetry_interval_minutes": 60
    }
    
    # Update database
    with db.get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE bins SET last_wake_command = NOW(), sleep_mode = FALSE WHERE bin_id = %s",
            (bin_id,)
        )
    
    return send_command(bin_id, "wake_up", payload, qos=1)


def sleep_bin(bin_id: str) -> bool:
    """Send sleep command to bin. Device enters low-power mode."""
    with db.get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE bins SET sleep_mode = TRUE WHERE bin_id = %s",
            (bin_id,)
        )
    
    return send_command(bin_id, "sleep", qos=1)


def reset_emptied_flag(bin_id: str) -> bool:
    """Reset the emptied flag on the device."""
    payload = {"emptied": False}
    return send_command(bin_id, "reset_emptied", payload, qos=1)


def request_status(bin_id: str) -> bool:
    """Request immediate status update from device."""
    return send_command(bin_id, "get_status", qos=1)


def update_device_config(
    bin_id: str,
    telemetry_interval: Optional[int] = None,
    battery_threshold: Optional[float] = None
) -> bool:
    """Send configuration update to device."""
    payload = {}
    if telemetry_interval:
        payload["telemetry_interval_minutes"] = telemetry_interval
    if battery_threshold:
        payload["battery_threshold_v"] = battery_threshold
    
    return send_command(bin_id, "update_config", payload, qos=1)


# ─────────────────────────────────────────────────────────────────────────────
# Broadcast Commands (All Bins)
# ─────────────────────────────────────────────────────────────────────────────

def broadcast_wake_up(collection_hours: int = 12) -> bool:
    """Wake up ALL bins for collection day."""
    payload = {
        "collection_hours": collection_hours,
        "telemetry_interval_minutes": 60
    }
    
    # Update all bins in database
    with db.get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE bins SET last_wake_command = NOW(), sleep_mode = FALSE"
        )
    
    logger.info(f"📢 Broadcasting wake_up to all bins")
    return send_command("broadcast", "wake_up", payload, qos=1)


def broadcast_sleep() -> bool:
    """Put all bins to sleep."""
    with db.get_cursor(commit=True) as cur:
        cur.execute("UPDATE bins SET sleep_mode = TRUE")
    
    logger.info(f"📢 Broadcasting sleep to all bins")
    return send_command("broadcast", "sleep", qos=1)


# ─────────────────────────────────────────────────────────────────────────────
# Collection Day Workflow
# ─────────────────────────────────────────────────────────────────────────────

def start_collection_day(collection_hours: int = 12) -> Dict[str, Any]:
    """
    Start collection day workflow:
    1. Wake up all bins
    2. Create alerts to remind users
    3. Return status
    """
    success = broadcast_wake_up(collection_hours)
    
    # Get all bins with user info
    with db.get_cursor() as cur:
        cur.execute("""
            SELECT bin_id, user_name, user_phone 
            FROM bins 
            WHERE user_id IS NOT NULL
        """)
        bins = cur.fetchall()
    
    # Create reminder alerts for users
    for bin in bins:
        db.create_alert(
            bin_id=bin['bin_id'],
            alert_type="collection_reminder",
            severity="info",
            message=f"Collection day today! Please ensure your bin device is turned on. User: {bin['user_name']}"
        )
    
    return {
        "success": success,
        "bins_notified": len(bins),
        "collection_hours": collection_hours,
        "started_at": datetime.utcnow().isoformat()
    }


def end_collection_day() -> Dict[str, Any]:
    """
    End collection day workflow:
    1. Send sleep command to all bins
    2. Mark collection complete
    """
    success = broadcast_sleep()
    
    return {
        "success": success,
        "ended_at": datetime.utcnow().isoformat()
    }
