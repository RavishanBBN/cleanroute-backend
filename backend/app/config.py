"""
Configuration settings for CleanRoute Backend.
Uses environment variables with sensible defaults for local development.
"""
import os

# ─────────────────────────────────────────────────────────────────────────────
# MQTT Broker Settings
# ─────────────────────────────────────────────────────────────────────────────
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "cleanroute/bins/+/telemetry")

# MQTT Security Settings (TLS + Authentication)
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "false").lower() == "true"
MQTT_TLS_PORT = int(os.getenv("MQTT_TLS_PORT", 8883))
MQTT_CA_CERT = os.getenv("MQTT_CA_CERT", "mqtt/certs/ca.crt")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "backend_service")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "CleanRoute@2025")

# ─────────────────────────────────────────────────────────────────────────────
# PostgreSQL Settings
# ─────────────────────────────────────────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "cleanroute_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "cleanroute_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "cleanroute_pass")

# Connection string for psycopg2
DATABASE_URL = f"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}"

# ─────────────────────────────────────────────────────────────────────────────
# API Settings
# ─────────────────────────────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
