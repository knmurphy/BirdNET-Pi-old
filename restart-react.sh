#!/bin/bash
# Restart FastAPI with React PWA

REMOTE_HOST="10.0.0.177"
REMOTE_USER="knmurphy"
REMOTE_BASE="/home/${REMOTE_USER}/BirdNET-Pi"

echo "Stopping old services..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    pkill -f 'api.main:app' || true
    pkill -f 'homepage/web_app.py' || true
    sleep 2
EOF

echo "Starting FastAPI with React PWA..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    cd ~/BirdNET-Pi
    export FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist
    export BIRDNET_DB_PATH=/home/knmurphy/BirdNET-Pi/scripts/birds.db
    export BIRDNET_RECORDINGS_PATH=/home/knmurphy/BirdSongs
    export STATION_MODEL=BirdNET-Pi · RPi 4B
    export PYTHONPATH=/home/knmurphy/BirdNET-Pi

    PYENV_ROOT=$(/home/knmurphy/.pyenv/bin/pyenv root 2>/dev/null || echo "")
    PYTHON_BIN="${PYENV_ROOT}/versions/3.12.12/bin/python"

    if [ -f "$PYTHON_BIN" ]; then
        $PYTHON_BIN -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --log-level info > /tmp/api.log 2>&1 &
        echo "FastAPI (React PWA) started with PID: $!"
    else
        echo "ERROR: Python 3.12.12 not found in pyenv"
        exit 1
    fi
EOF

echo ""
echo "✅ FastAPI (React PWA) restarted!"
echo ""
echo "Access the new system at:"
echo "  http://${REMOTE_HOST}:8003/"
echo ""
echo "Old PHP system remains at:"
echo "  http://${REMOTE_HOST}/"
