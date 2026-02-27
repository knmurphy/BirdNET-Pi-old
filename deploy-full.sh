#!/bin/bash
set -euo pipefail

# BirdNET-Pi React PWA Full Deploy Script
# Pulls latest code from git and restarts FastAPI with React PWA

# Configuration
REMOTE_USER="knmurphy"
REMOTE_HOST="10.0.0.177"
REMOTE_BASE="/home/${REMOTE_USER}/BirdNET-Pi"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=========================================="
echo "BirdNET-Pi React PWA Full Deploy"
echo "=========================================="
echo ""

# Step 1: Build frontend
log_info "Step 1: Building React frontend..."
cd frontend
npm run build
cd ..
log_success "Frontend built"

# Step 2: Pull latest code from git
log_info "Step 2: Pulling latest code from git..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    cd ~/BirdNET-Pi
    git fetch origin
    git reset --hard origin/main
    echo "Code updated"
EOF
log_success "Code updated from git"

# Step 3: Deploy frontend
log_info "Step 3: Deploying frontend to remote..."
rsync -avz --delete \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude 'src' \
    --exclude 'public' \
    --exclude 'vite.config.ts' \
    --exclude 'tsconfig*.json' \
    --exclude 'eslint.config.js' \
    --exclude 'package*.json' \
    --exclude '.gitignore' \
    --exclude '*.log' \
    "frontend/dist/" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_BASE}/frontend-dist/"
log_success "Frontend deployed"

# Step 4: Restart FastAPI with React PWA
log_info "Step 4: Restarting FastAPI with React PWA..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'REMOTE_RESTART'
    pkill -f 'api.main:app' || true
    pkill -f 'homepage/web_app.py' || true
    sleep 2

    cd ~/BirdNET-Pi
    export FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist
    export BIRDNET_DB_PATH=/home/knmurphy/BirdNET-Pi/scripts/birds.db
    export BIRDNET_RECORDINGS_PATH=/home/knmurphy/BirdSongs
    export STATION_MODEL='BirdNET-Pi · RPi 4B'
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
REMOTE_RESTART
log_success "FastAPI (React PWA) restarted"

# Step 5: Verify deployment
log_info "Step 5: Verifying deployment..."
sleep 3

echo ""
log_success "=========================================="
log_success "Deployment Complete!"
log_success "=========================================="
echo ""
log_info "New React PWA system running at:"
echo "  http://${REMOTE_HOST}:8003/"
echo ""
log_info "Old PHP system still running at:"
echo "  http://${REMOTE_HOST}/"
echo ""
log_success "Both systems running side-by-side!"
