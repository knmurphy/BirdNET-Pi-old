# Quick Deployment Reference

## Access URLs

| System | URL | Status |
|--------|-----|--------|
| React PWA | http://10.0.0.177:8003/ | ✅ Running |
| Old PHP | http://10.0.0.177/ | ✅ Running |

## One-Line Deploy

```bash
./deploy-full.sh
```

## Manual Restart

```bash
ssh knmurphy@10.0.0.177 << 'EOF'
  cd ~/BirdNET-Pi
  export FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist
  export PYTHONPATH=/home/knmurphy/BirdNET-Pi
  /home/knmurphy/.pyenv/versions/3.12.12/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --log-level info > /tmp/api.log 2>&1 &
EOF
```

## Verify Systems

```bash
# Check processes
ssh knmurphy@10.0.0.177 "ps aux | grep -E 'api.main|caddy' | grep -v grep"

# Check ports
ssh knmurphy@10.0.0.177 "lsof -i :8003 -i :80"

# Test React PWA
curl -s http://10.0.0.177:8003/ | head -5

# Test old PHP
curl -s http://10.0.0.177/ | head -5

# Test API
curl -s http://10.0.0.177:8003/api/detections/today/summary
```

## Common Commands

### Update and Deploy

```bash
cd frontend && npm run build && cd ..
./deploy-full.sh
```

### View Logs

```bash
ssh knmurphy@10.0.0.177 "tail -f /tmp/api.log"
```

### Kill All FastAPI

```bash
ssh knmurphy@10.0.0.177 "pkill -f 'api.main:app'"
```

### Pull Latest Code

```bash
ssh knmurphy@10.0.0.177 "cd ~/BirdNET-Pi && git fetch origin && git reset --hard origin/main"
```

## Troubleshooting

### FastAPI not starting?

```bash
# Check logs
ssh knmurphy@10.0.0.177 "tail -30 /tmp/api.log"

# Restart manually
./restart-react.sh
```

### React app not loading?

```bash
# Verify files exist
ssh knmurphy@10.0.0.177 "ls -la ~/BirdNET-Pi/frontend-dist/"

# Rebuild and redeploy
cd frontend && npm run build && cd ..
./deploy-full.sh
```

### Old PHP broken?

```bash
# Check PHP-FPM
ssh knmurphy@10.0.0.177 "ps aux | grep php-fpm"

# Restart PHP-FPM (if needed)
ssh knmurphy@10.0.0.177 "sudo systemctl restart php-fpm"
```

## File Locations

| Item | Local Path | Remote Path |
|------|------------|-------------|
| Frontend code | `frontend/src/` | `~/BirdNET-Pi/frontend-dist/` |
| API code | `api/main.py` | `~/BirdNET-Pi/api/main.py` |
| Database | `scripts/birds.db` | `~/BirdNET-Pi/scripts/birds.db` |
| Recordings | (local only) | `~/BirdSongs/` |
| Logs | (local only) | `~/logs/api.log` |
| Build output | `frontend/dist/` | `~/BirdNET-Pi/frontend-dist/` |

## API Endpoints Tested

```bash
# Today's summary
curl http://10.0.0.177:8003/api/detections/today/summary
# Returns: {"total_detections":330, "species_count":20, ...}

# Health check
curl http://10.0.0.177:8003/health
# Returns: {"status":"ok"}

# Documentation
curl http://10.0.0.177:8003/docs
# Returns: OpenAPI JSON
```

## System Requirements

- **Local**:
  - Node.js 18+
  - npm or yarn
  - Git

- **Remote**:
  - Python 3.12.12 (pyenv)
  - FastAPI
  - SQLite database
  - 5GB+ disk space

## Documentation

- **Progress Doc**: `DEPLOYMENT_PROGRESS.md`
- **Guide Doc**: `DEPLOY_GUIDE.md`
- **Frontend Doc**: `FRONTEND_DOCUMENTATION.md`

## Architecture

```
Port 80: Caddy → PHP-FPM → Old PHP System
         ↓

Port 8003: FastAPI → React PWA → API Endpoints
```

**Both systems run simultaneously, no interference.**
