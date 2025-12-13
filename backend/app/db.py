"""
Database connection helper for PostgreSQL.
Provides connection pooling and helper functions.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from . import config

# ─────────────────────────────────────────────────────────────────────────────
# Connection Helper
# ─────────────────────────────────────────────────────────────────────────────

def get_connection():
    """Get a new database connection."""
    return psycopg2.connect(config.DATABASE_URL)


@contextmanager
def get_cursor(commit=False):
    """
    Context manager for database cursor.
    Automatically handles connection and cursor cleanup.
    
    Usage:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM bins")
            rows = cur.fetchall()
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────

def check_db_connection() -> bool:
    """Check if database connection is healthy."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Bin Operations
# ─────────────────────────────────────────────────────────────────────────────

def upsert_bin(bin_id: str, lat: float, lon: float, last_seen: str):
    """
    Insert or update a bin record.
    Updates last_seen timestamp on every telemetry message.
    """
    sql = """
        INSERT INTO bins (bin_id, lat, lon, last_seen)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (bin_id) DO UPDATE SET
            lat = EXCLUDED.lat,
            lon = EXCLUDED.lon,
            last_seen = EXCLUDED.last_seen
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (bin_id, lat, lon, last_seen))


def update_bin_emptied(bin_id: str, emptied_at: str):
    """Update the last_emptied timestamp when a bin is emptied."""
    sql = """
        UPDATE bins SET last_emptied = %s WHERE bin_id = %s
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (emptied_at, bin_id))


def get_all_bins_latest():
    """
    Get all bins with their latest telemetry data.
    Returns one row per bin with the most recent fill percentage.
    """
    sql = """
        SELECT DISTINCT ON (b.bin_id)
            b.bin_id,
            b.lat,
            b.lon,
            b.last_seen,
            b.last_emptied,
            t.fill_pct,
            t.batt_v,
            t.temp_c,
            t.ts as last_telemetry_ts
        FROM bins b
        LEFT JOIN telemetry t ON b.bin_id = t.bin_id
        ORDER BY b.bin_id, t.ts DESC
    """
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Telemetry Operations
# ─────────────────────────────────────────────────────────────────────────────

def insert_telemetry(
    ts: str,
    bin_id: str,
    fill_pct: float,
    batt_v: float = None,
    temp_c: float = None,
    emptied: bool = False,
    lat: float = None,
    lon: float = None
):
    """Insert a new telemetry record."""
    sql = """
        INSERT INTO telemetry (ts, bin_id, fill_pct, batt_v, temp_c, emptied, lat, lon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (ts, bin_id, fill_pct, batt_v, temp_c, emptied, lat, lon))


def get_recent_telemetry(bin_id: str, limit: int = 100):
    """Get the most recent telemetry records for a specific bin."""
    sql = """
        SELECT id, ts, bin_id, fill_pct, batt_v, temp_c, emptied, lat, lon, received_at
        FROM telemetry
        WHERE bin_id = %s
        ORDER BY ts DESC
        LIMIT %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (bin_id, limit))
        return cur.fetchall()


def get_all_recent_telemetry(limit: int = 500):
    """Get the most recent telemetry records across all bins."""
    sql = """
        SELECT id, ts, bin_id, fill_pct, batt_v, temp_c, emptied, lat, lon, received_at
        FROM telemetry
        ORDER BY ts DESC
        LIMIT %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (limit,))
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Device Management Operations
# ─────────────────────────────────────────────────────────────────────────────

def register_device(
    bin_id: str,
    user_id: str,
    user_name: str,
    user_phone: str,
    wifi_ssid: str,
    lat: float = None,
    lon: float = None
):
    """Register a new device with user information."""
    sql = """
        INSERT INTO bins (bin_id, user_id, user_name, user_phone, wifi_ssid, lat, lon, registered_at, device_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), 'offline')
        ON CONFLICT (bin_id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            user_name = EXCLUDED.user_name,
            user_phone = EXCLUDED.user_phone,
            wifi_ssid = EXCLUDED.wifi_ssid,
            lat = EXCLUDED.lat,
            lon = EXCLUDED.lon,
            registered_at = NOW()
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (bin_id, user_id, user_name, user_phone, wifi_ssid, lat, lon))


def update_device_status(bin_id: str, status: str):
    """Update device online/offline status."""
    sql = "UPDATE bins SET device_status = %s WHERE bin_id = %s"
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (status, bin_id))


def get_user_bins(user_id: str):
    """Get all bins registered to a user."""
    sql = """
        SELECT bin_id, lat, lon, last_seen, device_status, sleep_mode, registered_at
        FROM bins
        WHERE user_id = %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (user_id,))
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Alerts Operations
# ─────────────────────────────────────────────────────────────────────────────

def create_alert(bin_id: str, alert_type: str, severity: str, message: str) -> int:
    """Create a new alert."""
    sql = """
        INSERT INTO alerts (bin_id, alert_type, severity, message)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (bin_id, alert_type, severity, message))
        return cur.fetchone()['id']


def get_unresolved_alerts(bin_id: str = None):
    """Get unresolved alerts, optionally filtered by bin_id."""
    if bin_id:
        sql = """
            SELECT id, bin_id, alert_type, severity, message, created_at
            FROM alerts
            WHERE bin_id = %s AND resolved = FALSE
            ORDER BY created_at DESC
        """
        with get_cursor() as cur:
            cur.execute(sql, (bin_id,))
            return cur.fetchall()
    else:
        sql = """
            SELECT id, bin_id, alert_type, severity, message, created_at
            FROM alerts
            WHERE resolved = FALSE
            ORDER BY created_at DESC
        """
        with get_cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()


def resolve_alert(alert_id: int):
    """Mark an alert as resolved."""
    sql = "UPDATE alerts SET resolved = TRUE, resolved_at = NOW() WHERE id = %s"
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (alert_id,))


# ─────────────────────────────────────────────────────────────────────────────
# Commands Log Operations
# ─────────────────────────────────────────────────────────────────────────────

def log_command(bin_id: str, command_type: str, payload: dict):
    """Log a command sent to a device."""
    sql = """
        INSERT INTO commands_log (bin_id, command_type, payload)
        VALUES (%s, %s, %s)
    """
    import json
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (bin_id, command_type, json.dumps(payload)))


def get_command_history(bin_id: str, limit: int = 50):
    """Get command history for a bin."""
    sql = """
        SELECT id, command_type, payload, sent_at, acknowledged, ack_at
        FROM commands_log
        WHERE bin_id = %s
        ORDER BY sent_at DESC
        LIMIT %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (bin_id, limit))
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Bin Management (Admin)
# ─────────────────────────────────────────────────────────────────────────────

def delete_bin(bin_id: str) -> bool:
    """
    Delete a bin and all its associated data.
    Returns True if bin was deleted, False if not found.
    """
    # First delete related records
    sql_telemetry = "DELETE FROM telemetry WHERE bin_id = %s"
    sql_alerts = "DELETE FROM alerts WHERE bin_id = %s"
    sql_commands = "DELETE FROM commands_log WHERE bin_id = %s"
    sql_bin = "DELETE FROM bins WHERE bin_id = %s RETURNING bin_id"
    
    with get_cursor(commit=True) as cur:
        cur.execute(sql_telemetry, (bin_id,))
        cur.execute(sql_alerts, (bin_id,))
        cur.execute(sql_commands, (bin_id,))
        cur.execute(sql_bin, (bin_id,))
        result = cur.fetchone()
        return result is not None


def get_bin_by_id(bin_id: str):
    """Get a specific bin by ID."""
    sql = """
        SELECT bin_id, lat, lon, last_seen, last_emptied, device_status,
               user_id, user_name, registered_at
        FROM bins
        WHERE bin_id = %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (bin_id,))
        return cur.fetchone()


def get_all_bins():
    """Get all bins (basic info only)."""
    sql = """
        SELECT bin_id, lat, lon, last_seen, device_status
        FROM bins
        ORDER BY bin_id
    """
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Admin Authentication
# ─────────────────────────────────────────────────────────────────────────────

def init_admin_table():
    """Create admin users table if not exists."""
    sql = """
        CREATE TABLE IF NOT EXISTS admin_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP
        )
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql)


def create_admin_user(username: str, password_hash: str) -> bool:
    """Create a new admin user."""
    sql = """
        INSERT INTO admin_users (username, password_hash)
        VALUES (%s, %s)
        ON CONFLICT (username) DO NOTHING
        RETURNING id
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (username, password_hash))
        result = cur.fetchone()
        return result is not None


def get_admin_by_username(username: str):
    """Get admin user by username."""
    sql = """
        SELECT id, username, password_hash, created_at, last_login
        FROM admin_users
        WHERE username = %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (username,))
        return cur.fetchone()


def update_admin_last_login(username: str):
    """Update admin's last login timestamp."""
    sql = """
        UPDATE admin_users
        SET last_login = NOW()
        WHERE username = %s
    """
    with get_cursor(commit=True) as cur:
        cur.execute(sql, (username,))
