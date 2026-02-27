# Deployment Script Summary

## What I've Created

### 1. `deploy.sh` - Automated Deployment Script

**Location**: `/Users/knmurphy/Documents/PROJECTS/BirdNET-Pi-old/deploy.sh`

**What it does**:
- Builds React frontend locally (`npm run build`)
- Syncs files to remote server to `~/BirdNET-Pi/frontend-dist/`
- Adds static file serving route to `web_app.py`
- Configures `FRONTEND_DIST` environment variable
- Restarts FastAPI to load the new configuration
- Verifies deployment

**Commands**:
```bash
./deploy.sh build      # Build only
./deploy.sh deploy     # Build + deploy (default)
./deploy.sh rollback   # Remove and clean up
./deploy.sh clean      # Same as rollback
```

### 2. `DEPLOYMENT.md` - Full Documentation

**Location**: `/Users/knmurphy/Documents/PROJECTS/BirdNET-Pi-old/DEPLOYMENT.md`

**Contains**:
- Architecture overview
- Quick start guide
- How it works (detailed explanation)
- Running side-by-side
- Production systemd configuration
- Troubleshooting
- Rollback procedures

## How to Deploy

### Step 1: Make Script Executable (Already Done)

```bash
chmod +x deploy.sh
```

### Step 2: Deploy to Remote System

```bash
./deploy.sh deploy
```

This will:
1. ✅ Build React frontend (`frontend/dist/`)
2. ✅ Create `~/BirdNET-Pi/frontend-dist/` on remote
3. ✅ Copy build files to remote
4. ✅ Add static route to `web_app.py`
5. ✅ Restart FastAPI on port 8003
6. ✅ Verify deployment

### Step 3: Access the New System

```bash
# New React + FastAPI system
curl http://10.0.0.177:8003/

# Old PHP system (still works)
curl http://10.0.0.177/
```

## How It Works

### The Secret: Static File Serving in FastAPI

When you deploy, the script adds this route to `web_app.py`:

```python
@app.get('/static/{file_name:path}')
def serve_static(file_name: str):
    """Serve static files from React build directory."""
    static_dir = os.environ.get('FRONTEND_DIST', '/home/knmurphy/BirdNET-Pi/frontend-dist')
    file_path = os.path.join(static_dir, file_name)
    
    # Path traversal protection
    if not os.path.exists(file_path):
        return Response(content='Not found', status_code=404)
    if not file_path.startswith(static_dir):
        return Response(content='Forbidden', status_code=403)
    
    return FileResponse(file_path)
```

**This is crucial**:
- React app loads `index.html` from `/static/index.html`
- JavaScript loads from `/static/index-*.js`
- CSS loads from `/static/index-*.css`
- **No special proxy needed** - it just works!

### React Router Handling

Since React uses client-side routing:
- `/` → loads index.html
- `/dashboard` → React Router handles it
- `/api/detections` → FastAPI API endpoint

Everything works seamlessly without any server configuration!

## Running Side-by-Side

### Without systemd (Testing)

```bash
# Terminal 1: Keep old system running (Caddy + PHP-FPM)
# It's already running, nothing needed!

# Terminal 2: Start new React system
cd ~/BirdNET-Pi
python3 homepage/web_app.py
# Running at http://10.0.0.177:8003/
```

### With systemd (Production)

See `DEPLOYMENT.md` for systemd configuration to run FastAPI as a service.

## Testing the Deployment

```bash
# Test the new system
curl http://10.0.0.177:8003/

# Check it has JS
curl http://10.0.0.177:8003/static/index.js | head -5

# Verify old system still works
curl http://10.0.0.177/ | grep -i "iss-ocotepec"
```

## Updating the Frontend

After editing React code:

```bash
# Edit frontend/src/...

# Quick rebuild and redeploy
./deploy.sh deploy
```

Done! The new system is updated.

## Rollback if Needed

```bash
./deploy.sh rollback
```

This removes:
- The static route from `web_app.py`
- The deployed files
- Restarts FastAPI without the new frontend

Old system remains untouched.

## Files Changed on Remote

### After Deployment

1. **Added to web_app.py**: Static file serving route
2. **Created directory**: `~/BirdNET-Pi/frontend-dist/`
3. **Files copied**: All files from `frontend/dist/`
4. **Environment**: `FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist`

### Before Deployment

Only local files in `frontend/dist/` are affected.

## Key Benefits

✅ **No interference**: Old system runs on port 80, new on port 8003
✅ **Instant updates**: Redeploy with one command
✅ **Zero downtime**: Switch between systems anytime
✅ **Automatic rollback**: Clean removal of changes
✅ **Production-ready**: Same setup for testing and production

## Next Steps

1. **Run the deploy script**: `./deploy.sh deploy`
2. **Test the new system**: `curl http://10.0.0.177:8003/`
3. **Verify old system still works**: `curl http://10.0.0.177/`
4. **Start using it**: Access at `http://10.0.0.177:8003/`

## Questions?

Check `DEPLOYMENT.md` for detailed troubleshooting and configuration options.
