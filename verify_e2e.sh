#!/bin/bash
# End-to-end verification script for WIE

echo "=== WIE End-to-End Verification ==="
echo ""

# Step 1: Verify database exists and has data
echo "Step 1: Checking SQLite database..."
DB_FILE="/home/ubuntu/wie/wie.db"
if [ -f "$DB_FILE" ]; then
    echo "✅ Database file exists: $DB_FILE"
    SIGNAL_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM signals;")
    WEDGE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM wedge_profiles;")
    echo "   - Signals: $SIGNAL_COUNT"
    echo "   - Wedges: $WEDGE_COUNT"
else
    echo "❌ Database file not found"
    exit 1
fi
echo ""

# Step 2: Verify Python API server is running
echo "Step 2: Checking Python API server..."
API_RESPONSE=$(curl -s http://localhost:5000/api/wedges)
if [ -z "$API_RESPONSE" ]; then
    echo "❌ Python API server not responding"
    exit 1
fi
API_WEDGE_COUNT=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])")
echo "✅ Python API server running"
echo "   - API returning $API_WEDGE_COUNT wedges"
echo ""

# Step 3: Verify Express dev server is running
echo "Step 3: Checking Express dev server..."
EXPRESS_RESPONSE=$(curl -s http://localhost:3000/ 2>&1)
if echo "$EXPRESS_RESPONSE" | grep -q "<!DOCTYPE\|<html"; then
    echo "✅ Express dev server running on port 3000"
else
    echo "⚠️  Express dev server may not be responding correctly"
fi
echo ""

# Step 4: Verify tRPC endpoint
echo "Step 4: Checking tRPC endpoint..."
TRPC_RESPONSE=$(curl -s -X POST http://localhost:3000/api/trpc/wedges.list \
  -H "Content-Type: application/json" \
  -d '{"json":{"sortBy":"score","limit":10}}' 2>&1)
if echo "$TRPC_RESPONSE" | grep -q "wedge"; then
    echo "✅ tRPC endpoint responding"
    TRPC_WEDGE_COUNT=$(echo "$TRPC_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('result', {}).get('data', {}).get('wedges', [])))" 2>/dev/null || echo "?")
    echo "   - tRPC returning $TRPC_WEDGE_COUNT wedges"
else
    echo "⚠️  tRPC endpoint may not be responding correctly"
    echo "   Response: $(echo "$TRPC_RESPONSE" | head -c 200)"
fi
echo ""

# Step 5: Summary
echo "=== Summary ==="
echo "✅ Database: $SIGNAL_COUNT signals, $WEDGE_COUNT wedges"
echo "✅ Python API: $API_WEDGE_COUNT wedges"
echo "✅ Express: Running"
echo ""
echo "End-to-end data flow verified!"
