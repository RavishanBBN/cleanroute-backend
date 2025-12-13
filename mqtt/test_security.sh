#!/bin/bash
# =============================================================================
# CleanRoute MQTT TLS Test Script
# Tests both secure (TLS) and insecure connections
# =============================================================================

CERT_DIR="/home/thevinduk/Repositories/cleanroute-backend/mqtt/certs"
PASSWD_FILE="/home/thevinduk/Repositories/cleanroute-backend/mqtt/passwd"

echo "=============================================="
echo "   CleanRoute MQTT Security Test"
echo "=============================================="
echo ""

# Test 1: Insecure connection (should work on port 1883)
echo "📡 Test 1: Insecure connection (port 1883)"
echo "-------------------------------------------"
mosquitto_pub -h localhost -p 1883 \
    -t "cleanroute/test" \
    -m '{"test": "insecure"}' 2>&1 && echo "✅ Insecure publish: SUCCESS" || echo "❌ Insecure publish: FAILED"
echo ""

# Test 2: Secure connection without auth (should FAIL)
echo "🔒 Test 2: TLS without authentication (should FAIL)"
echo "-------------------------------------------"
mosquitto_pub -h localhost -p 8883 \
    --cafile "$CERT_DIR/ca.crt" \
    -t "cleanroute/test" \
    -m '{"test": "no_auth"}' 2>&1 && echo "❌ Should have failed!" || echo "✅ Correctly rejected (no auth)"
echo ""

# Test 3: Secure connection with WRONG password (should FAIL)
echo "🔒 Test 3: TLS with wrong password (should FAIL)"
echo "-------------------------------------------"
mosquitto_pub -h localhost -p 8883 \
    --cafile "$CERT_DIR/ca.crt" \
    -u "B001" -P "wrong_password" \
    -t "cleanroute/test" \
    -m '{"test": "wrong_pass"}' 2>&1 && echo "❌ Should have failed!" || echo "✅ Correctly rejected (wrong password)"
echo ""

# Test 4: Secure connection with CORRECT credentials (should SUCCEED)
echo "🔐 Test 4: TLS with correct credentials (should SUCCEED)"
echo "-------------------------------------------"
mosquitto_pub -h localhost -p 8883 \
    --cafile "$CERT_DIR/ca.crt" \
    -u "B001" -P "bin_B001_secret" \
    -t "cleanroute/bins/B001/telemetry" \
    -m '{"ts":"2025-12-13T16:00:00Z","bin_id":"B001","fill_pct":80.0,"batt_v":3.9,"temp_c":30.0,"lat":6.9271,"lon":79.8612}' \
    2>&1 && echo "✅ Secure publish: SUCCESS" || echo "❌ Secure publish: FAILED"
echo ""

# Test 5: Backend service credentials
echo "🔐 Test 5: Backend service authentication"
echo "-------------------------------------------"
mosquitto_pub -h localhost -p 8883 \
    --cafile "$CERT_DIR/ca.crt" \
    -u "backend_service" -P "CleanRoute@2025" \
    -t "cleanroute/bins/broadcast/command" \
    -m '{"cmd":"wake_up","ts":"2025-12-13T16:00:00Z"}' \
    2>&1 && echo "✅ Backend auth: SUCCESS" || echo "❌ Backend auth: FAILED"
echo ""

echo "=============================================="
echo "   Test Complete"
echo "=============================================="
echo ""
echo "📋 Credentials Reference:"
echo "   Backend:  backend_service / CleanRoute@2025"
echo "   Bin B001: B001 / bin_B001_secret"
echo "   Bin COL001: COL001 / bin_COL001_secret"
echo ""
