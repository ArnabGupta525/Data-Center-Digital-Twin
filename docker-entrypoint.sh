#!/bin/bash
# Docker entrypoint script for Data Center Digital Twin

set -e

echo "=========================================="
echo "Data Center Digital Twin - Starting..."
echo "=========================================="

# Check if custom dataset is provided
if [ -d "/data" ] && [ "$(ls -A /data)" ]; then
    echo "✓ Custom dataset directory detected at /data"
    
    # Check for the main dataset file
    if [ -f "/data/datacenter_full_state_list.json" ]; then
        echo "✓ Found datacenter_full_state_list.json"
        # Copy to application data directory
        cp /data/datacenter_full_state_list.json /app/data/datacenter_full_state_list.json
        echo "✓ Dataset loaded successfully"
    else
        echo "⚠ Warning: /data/datacenter_full_state_list.json not found"
        echo "  Using default sample dataset"
    fi
    
    # Copy any other data files
    if [ -f "/data/sample.json" ]; then
        cp /data/sample.json /app/data/sample.json
        echo "✓ Additional sample data loaded"
    fi
else
    echo "ℹ No custom dataset provided, using default sample data"
fi

# Check database
if [ ! -f "/app/db/telemetry.db" ]; then
    echo "Initializing database..."
    python /app/init_db.py
    echo "✓ Database initialized"
else
    echo "✓ Database already exists"
fi

# Check optimizer models
if [ ! -f "/app/models/optimizer_cost.joblib" ] || [ ! -f "/app/models/optimizer_compute.joblib" ]; then
    echo "⚠ Optimizer models not found"
    echo "  Training models (this may take 2-3 minutes)..."
    python /app/train_optimizer.py || {
        echo "⚠ Warning: Model training failed"
        echo "  The application will run without optimization features"
    }
else
    echo "✓ Optimizer models loaded"
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  - Python: $(python --version)"
echo "  - Display: ${DISPLAY:-not set}"
echo "  - Working Directory: $(pwd)"
echo "  - User: $(whoami)"
echo ""

# Check X11 connection
if [ -n "$DISPLAY" ]; then
    echo "Checking X11 connection..."
    if command -v xdpyinfo &> /dev/null; then
        if xdpyinfo &> /dev/null; then
            echo "✓ X11 connection successful"
        else
            echo "⚠ Warning: Cannot connect to X11 display"
            echo "  Make sure X server is running and DISPLAY is set correctly"
        fi
    else
        echo "ℹ xdpyinfo not available, skipping X11 check"
    fi
fi

echo ""
echo "=========================================="
echo "Starting Data Center Digital Twin GUI..."
echo "=========================================="
echo ""

# Execute the main command
exec "$@"
