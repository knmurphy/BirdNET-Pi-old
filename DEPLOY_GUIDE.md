# React PWA Deployment Guide

## Overview

This guide deploys the new React PWA system alongside the existing PHP system without any interference.

## Current Architecture

```
10.0.0.177 (Remote System)
│
├── Port 80 (Caddy/PHP-FPM)
│   └── http://10.0.0.177/              # Old PHP system (unchanged)
│
└── Port 8003 (FastAPI + React PWA)
    └── http://10.0.0.177:8003/         # New React PWA system
        ├── /                           # React PWA (index.html)
        ├── /api/*                      # API endpoints
        ├── /assets/*                   # React assets
        ├── /manifest.json              # PWA manifest
        └── /sw.js                      # Service worker
```

## Quick Deploy

### Step 1: Build the React Frontend

```bash
cd frontend
npm run build
cd ..
```

### Step 2: Deploy to Remote

```bash
./deploy.sh deploy
```

This will:
- ✅ Build React frontend
- ✅ Sync files to `~/BirdNET-Pi/frontend-dist/`
- ✅ Create deployment directory

### Step 3: Start the React PWA

The deploy script won't start api/main.py automatically (to avoid breaking anything if it fails), so run:

```bash
./restart-react.sh
```

Or manually:

```bash
ssh knmurphy@10.0.0.177 << 'EOF'
cd ~/BirdNET-Pi
export FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist
export BIRDNET_DB_PATH=/home/knmurphy/BirdNET-Pi/scripts/birds.db
export BIRDNET_RECORDINGS_PATH=/home/knmurphy/BirdSongs
export STATION_MODEL=BirdNET-Pi · RPi 4B
export PYTHONPATH=/home/knmurphy/BirdNET-Pi

PYENV_ROOT=$(/home/knmurphy/.pyenv/bin/pyenv root 2>/dev/null || echo "")
PYTHON_BIN="${PYENV_ROOT}/versions/3.12.12/bin/python"

$PYTHON_BIN -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --log-level info > /tmp/api.log 2>&1 &
echo "FastAPI (React PWA) started"
EOF
```

## Access the Systems

```bash
# New React PWA system
curl http://10.0.0.177:8003/

# Old PHP system
curl http://10.0.0.177/
```

In your browser:
- **New system**: http://10.0.0.177:8003/
- **Old system**: http://10.0.0.177/

## Updating the Frontend

After editing the React code:

```bash
# Rebuild
cd frontend
npm run build
cd ..

# Deploy (syncs files)
./deploy.sh build

# Restart FastAPI
./restart-react.sh
```

## What's Running

### api/main.py Features

1. **All API Routes**: `/api/detections/*`, `/api/species/*`, `/api/system/*`, etc.
2. **React PWA Serving**: Serves index.html, static assets, manifest.json, service worker
3. **CORS**: Configured for frontend access
4. **Health Checks**: `/health` endpoint
5. **Documentation**: `/docs` for OpenAPI schema

### api/main.py Structure

```python
# 1. FastAPI app setup
app = FastAPI(title="Field Station API", version="0.1.0")

# 2. CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# 3. Include all routers
app.include_router(detections.router, prefix="/api", ...)
app.include_router(species.router, prefix="/api", ...)
app.include_router(system.router, prefix="/api", ...)
# ... etc

# 4. React PWA serving
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

# Mount static assets
app.mount("/assets", StaticFiles(...), name="assets")
app.mount("/icons", StaticFiles(...), name="icons")

# Catch-all for React Router
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return serve_react_app(full_path)
```

## Troubleshooting

### FastAPI not starting

Check logs:
```bash
ssh knmurphy@10.0.0.177 "tail -20 /tmp/api.log"
```

### React app not loading

Check files exist:
```bash
ssh knmurphy@10.0.0.177 "ls -la ~/BirdNET-Pi/frontend-dist/"
```

### API endpoints returning 404

Check that api/main.py is running:
```bash
ssh knmurphy@10.0.0.177 "ps aux | grep api.main"
```

### Check which port is being used
```bash
ssh knmurphy@10.0.0.177 "lsof -i :8003"
```

## Files Modified/Created

- `api/main.py` - Enhanced to serve React PWA
- `frontend/dist/` - React build output
- `deploy.sh` - Automated deployment script
- `restart-react.sh` - Quick restart script

## Architecture Comparison

### Old System (PHP)
- Location: `/home/knmurphy/BirdNET-Pi/homepage/`
- Technology: PHP-FPM, Caddy web server
- Access: http://10.0.0.177/
- Status: Unchanged, running as-is

### New System (React PWA)
- Location: `/home/knmurphy/BirdNET-Pi/frontend-dist/`
- Technology: React 19, Vite, FastAPI, PWA
- Access: http://10.0.0.177:8003/
- Status: Deployed and running

Both systems run independently on different ports with no interference.
