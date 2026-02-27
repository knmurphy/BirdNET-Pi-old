# BirdNET-Pi React Frontend Deployment Guide

## Overview

This guide explains how to deploy the new React-based frontend to run **alongside** the existing PHP system on 10.0.0.177 **without any interference**.

## Current System Architecture

```
10.0.0.177 (Remote System)
│
├── Port 80 (Caddy)
│   ├── http://10.0.0.177/         → PHP-FPM (Old System)
│   └── API routes → FastAPI (port 8003)
│
└── Port 8003 (FastAPI)
    ├── http://10.0.0.177:8003/     → New React + FastAPI (NEW)
    ├── /api/*                      → Existing API endpoints
    └── /static/*                   → React static assets (NEW)
```

**Two independent systems running simultaneously:**
- **Old System**: PHP/FPM at http://10.0.0.177/ (existing)
- **New System**: React + FastAPI at http://10.0.0.177:8003/ (to be deployed)

## Quick Start

### Deploy the New System

```bash
./deploy.sh deploy
```

This will:
1. Build the React frontend locally
2. Create deployment directory on remote
3. Sync files to `~/BirdNET-Pi/frontend-dist`
4. Add static file serving route to `web_app.py`
5. Restart FastAPI with the new configuration
6. Verify deployment

### Access the New System

```bash
# New React + FastAPI system
curl http://10.0.0.177:8003/

# Old PHP system (still works)
curl http://10.0.0.177/
```

## Commands

| Command | Description |
|---------|-------------|
| `./deploy.sh build` | Build React frontend locally (no deployment) |
| `./deploy.sh deploy` | Build and deploy to remote system (default) |
| `./deploy.sh rollback` | Remove static route and delete deployed files |
| `./deploy.sh clean` | Same as rollback (remove all files) |

## How It Works

### Deployment Flow

1. **Build** (local): `npm run build` → creates `frontend/dist/`
2. **Sync** (remote): Copies `frontend/dist/*` to `~/BirdNET-Pi/frontend-dist/`
3. **Patch** (remote): Adds static route to `web_app.py` that serves from `frontend-dist`
4. **Restart** (remote): Reloads FastAPI with `FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist`
5. **Serve**: React app served from `/static/*` route on port 8003

### Static File Serving

The FastAPI app now includes this route:

```python
@app.get('/static/{file_name:path}')
def serve_static(file_name: str):
    """Serve static files from React build directory."""
    static_dir = os.environ.get('FRONTEND_DIST', '/home/knmurphy/BirdNET-Pi/frontend-dist')
    file_path = os.path.join(static_dir, file_name)

    if not os.path.exists(file_path):
        return Response(content='Not found', status_code=404)

    if not file_path.startswith(static_dir):
        # Path traversal protection
        return Response(content='Forbidden', status_code=403)

    return FileResponse(file_path)
```

### React Router Handling

The React app uses `react-router-dom` for client-side routing. When deployed:

- `http://10.0.0.177:8003/` → Loads `index.html`
- `http://10.0.0.177:8003/dashboard` → React Router handles routing
- `http://10.0.0.177:8003/api/detections` → FastAPI API endpoint

No special configuration needed! The app works exactly like a development server.

## Running the Systems Side-by-Side

### For Testing

```bash
# Terminal 1: Old PHP system (default)
# Just keep it running (Caddy + PHP-FPM)

# Terminal 2: New React system
cd ~/BirdNET-Pi
python3 homepage/web_app.py
# Running at http://10.0.0.177:8003/
```

### Production Configuration (Optional)

To run FastAPI in production mode with systemd:

```bash
# Create systemd service
sudo tee /etc/systemd/system/birdnet-frontend.service << 'EOF'
[Unit]
Description=BirdNET-Pi React Frontend
After=network.target

[Service]
Type=simple
User=knmurphy
WorkingDirectory=/home/knmurphy/BirdNET-Pi
Environment="FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist"
Environment="BIRDNET_DB_PATH=/home/knmurphy/BirdNET-Pi/scripts/birds.db"
Environment="BIRDNET_RECORDINGS_PATH=/home/knmurphy/BirdSongs"
Environment="STATION_MODEL=BirdNET-Pi · RPi 4B"
ExecStart=/home/knmurphy/.pyenv/versions/3.12.12/bin/python3 homepage/web_app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable birdnet-frontend
sudo systemctl start birdnet-frontend

# Check status
sudo systemctl status birdnet-frontend
```

## Switching Between Systems

### To Use the New System

```bash
# Start FastAPI
cd ~/BirdNET-Pi
python3 homepage/web_app.py
```

Then visit: `http://10.0.0.177:8003/`

### To Use the Old System

Just access: `http://10.0.0.177/`

The old PHP system continues running without any changes.

### To Switch Back and Forth

```bash
# Switch to new system (FastAPI running)
curl http://10.0.0.177:8003/

# Switch to old system (PHP running)
curl http://10.0.0.177/
```

No downtime required - they run independently!

## Troubleshooting

### Access Denied Error

If you get 403 Forbidden when accessing the new system:

```bash
# Check if FastAPI is running
curl http://10.0.0.177:8003/

# Check the logs
ssh knmurphy@10.0.0.177 "tail -f /tmp/web_app.log"
```

### Static Files Not Loading

If JavaScript or CSS files return 404:

```bash
# Verify files are deployed
ssh knmurphy@10.0.0.177 "ls -la ~/BirdNET-Pi/frontend-dist/"

# Check static route is working
curl -I http://10.0.0.177:8003/static/index.js
```

### Build Failures

If `npm run build` fails:

```bash
cd frontend
rm -rf node_modules dist
npm install
npm run build
cd ..
./deploy.sh build
./deploy.sh deploy
```

## Updating the Frontend

After editing the React code:

```bash
# Edit frontend/src/...

# Rebuild and redeploy
./deploy.sh deploy
```

This is instantaneous - no server restart needed beyond the FastAPI reload!

## Rollback Procedure

If the new system has issues:

```bash
./deploy.sh rollback
```

This will:
1. Remove the static route from `web_app.py`
2. Delete the deployed files
3. Restart FastAPI without the new frontend

The old PHP system remains untouched.

## File Sizes

- **index.js**: 277 KB (uncompressed) / ~86 KB (gzipped)
- **index.css**: 16 KB (uncompressed) / ~5 KB (gzipped)
- **Total build output**: ~300 KB

Compared to most React builds, this is quite small thanks to Vite optimizations and tree-shaking.

## Security Considerations

1. **Path Traversal Protection**: The static route includes guards against directory traversal attacks
2. **Environment Variables**: Database and recording paths are configurable via env vars
3. **Isolation**: The new system runs on a different port, isolated from the old PHP system
4. **No Database Access**: The React frontend only reads via API - no direct DB access

## Performance

The new system benefits from:
- **Fast hydration**: React renders instantly with FastAPI backend
- **Tree-shaking**: Only used components are bundled
- **Code splitting**: Lazy-loaded routes for better initial load
- **PWA**: Offline support with Service Worker
- **Cache-friendly**: Static assets with long cache headers

## Questions?

See `FRONTEND_DOCUMENTATION.md` for detailed architecture and implementation notes.
