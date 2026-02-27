#!/bin/bash
set -euo pipefail

# BirdNET-Pi React Frontend Deploy Script
# This script builds the React frontend and deploys it to run alongside
# the existing PHP system on 10.0.0.177 without interference

# Configuration
LOCAL_DIST="frontend/dist"
REMOTE_USER="knmurphy"
REMOTE_HOST="10.0.0.177"
REMOTE_BASE="/home/${REMOTE_USER}/BirdNET-Pi"
REMOTE_FRONTEND_DIST="${REMOTE_BASE}/frontend-dist"  # New React build location

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if remote host is reachable
check_remote() {
    log_info "Checking remote host connectivity..."
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes ${REMOTE_USER}@${REMOTE_HOST} "echo 'reachable'" &>/dev/null; then
        log_error "Cannot connect to ${REMOTE_USER}@${REMOTE_HOST}. Please ensure SSH is set up."
        exit 1
    fi
    log_success "Remote host is reachable"
}

# Build the React frontend
build_frontend() {
    log_info "Building React frontend..."
    cd frontend

    if [ ! -d "node_modules" ]; then
        log_warning "node_modules not found. Installing dependencies..."
        npm install
    fi

    npm run build

    cd ..
    log_success "Frontend build complete"
}

# Create deployment directory on remote
create_remote_dir() {
    log_info "Creating deployment directory on remote..."

    # Create frontend-dist directory
    ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_FRONTEND_DIST}"

    log_success "Remote directory created: ${REMOTE_FRONTEND_DIST}"
}

# Sync build to remote
sync_to_remote() {
    log_info "Syncing build to remote system..."
    
    rsync -avz --delete \
        --exclude 'node_modules' \
        --exclude '.git' \
        --exclude 'dist' \
        --exclude 'src' \
        --exclude 'public' \
        --exclude 'vite.config.ts' \
        --exclude 'tsconfig*.json' \
        --exclude 'eslint.config.js' \
        --exclude 'package*.json' \
        --exclude '.gitignore' \
        --exclude '*.log' \
        "${LOCAL_DIST}/" \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_FRONTEND_DIST}/"

    log_success "Sync complete"
}

# Apply static file serving patch to web_app.py
apply_static_route() {
    log_info "Applying static file serving route to web_app.py..."

    # Check if static route already exists
    if ssh ${REMOTE_USER}@${REMOTE_HOST} "grep -q '/static-route-comment' ${REMOTE_BASE}/homepage/web_app.py"; then
        log_info "Static route already exists, skipping..."
        return
    fi

    # Create a temporary patch file
    ssh ${REMOTE_USER}@${REMOTE_HOST} "cat > /tmp/web_app_patch.txt << 'PATCHEOF'

# Static file serving for React frontend (added by deploy script)
@app.get('/static/{file_name:path}')
def serve_static(file_name: str):
    \"\"\"Serve static files from React build directory.\"\"\"
    static_dir = os.environ.get('FRONTEND_DIST', '${REMOTE_FRONTEND_DIST}')
    file_path = os.path.join(static_dir, file_name)
    
    if not os.path.exists(file_path):
        return Response(content='Not found', status_code=404)
    
    if not file_path.startswith(static_dir):
        # Path traversal protection
        return Response(content='Forbidden', status_code=403)
    
    return FileResponse(file_path)

PATCHEOF"

    # Apply the patch
    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'REMOTE_PATCH'
cd ~/BirdNET-Pi/homepage
# Insert the static route after line 1027 (after app = FastHTML())
sed -i '/^app = FastHTML()/r /tmp/web_app_patch.txt' web_app.py
REMOTE_PATCH

    log_success "Static route applied to web_app.py"
}

# Restart FastAPI to load the new static route
restart_fastapi() {
    log_info "Restarting FastAPI to apply changes..."
    
    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'REMOTE_RESTART'
# Find and kill the running web_app.py process
pkill -f "homepage/web_app.py" || true

# Wait a moment for cleanup
sleep 2

# Start web_app.py with environment variable pointing to frontend
cd ~/BirdNET-Pi
export FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist
python3 homepage/web_app.py > /tmp/web_app.log 2>&1 &
echo "FastAPI restarted with PID: \$!"
REMOTE_RESTART

    log_success "FastAPI restarted"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Check if key files exist on remote
    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} "test -f ${REMOTE_FRONTEND_DIST}/index.html"; then
        log_error "index.html not found on remote!"
        exit 1
    fi

    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} "test -f ${REMOTE_FRONTEND_DIST}/manifest.json"; then
        log_error "manifest.json not found on remote!"
        exit 1
    fi

    # Test the static route via curl
    log_info "Testing static route via curl..."
    curl -s -o /dev/null -w "Static route status: %{http_code}\n" "http://${REMOTE_HOST}:8003/static/index.html"

    log_success "All required files verified"
}

# Show deployment info
show_deployment_info() {
    echo ""
    log_info "=========================================="
    log_info "Deployment Complete!"
    log_info "=========================================="
    echo ""
    log_info "Frontend deployed to: ${REMOTE_FRONTEND_DIST}"
    echo ""
    log_info "To access the new system:"
    echo "  http://${REMOTE_HOST}:8003/           # New React + FastAPI (this server)"
    echo "  http://${REMOTE_HOST}/                # Old PHP system (existing)"
    echo ""
    log_info "API endpoints are still available at:"
    echo "  http://${REMOTE_HOST}:8003/api/*"
    echo ""
    log_warning "Note: The React app's assets are served from the same domain"
    log_info "      using the /static/{file_name} route, so no proxy is needed."
    echo ""
}

# Rollback function
rollback() {
    log_warning "Initiating rollback..."

    # Remove the static route from web_app.py
    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'REMOTE_ROLLBACK'
cd ~/BirdNET-Pi/homepage
sed -i '/# Static file serving for React frontend/,/^PATCHEOF/d' web_app.py
REMOTE_ROLLBACK

    # Restart FastAPI
    ssh ${REMOTE_USER}@${REMOTE_HOST} "pkill -f 'homepage/web_app.py' && sleep 2 && cd ~/BirdNET-Pi && export FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist && python3 homepage/web_app.py > /tmp/web_app.log 2>&1 &"

    # Remove deployed files
    ssh ${REMOTE_USER}@${REMOTE_HOST} "rm -rf ${REMOTE_FRONTEND_DIST}"

    log_success "Rollback complete"
}

# Clean function
clean() {
    log_info "Cleaning deployed files from remote..."

    # Remove the static route from web_app.py
    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'REMOTE_CLEAN'
cd ~/BirdNET-Pi/homepage
sed -i '/# Static file serving for React frontend/,/^PATCHEO/d' web_app.py
REMOTE_CLEAN

    # Restart FastAPI
    ssh ${REMOTE_USER}@${REMOTE_HOST} "pkill -f 'homepage/web_app.py' && sleep 2 && cd ~/BirdNET-Pi && export FRONTEND_DIST=/home/knmurphy/BirdNET-Pi/frontend-dist && python3 homepage/web_app.py > /tmp/web_app.log 2>&1 &"

    # Remove deployed files
    ssh ${REMOTE_USER}@${REMOTE_HOST} "rm -rf ${REMOTE_FRONTEND_DIST}"

    log_success "Cleanup complete"
}

# Parse command line arguments
COMMAND="${1:-deploy}"

case $COMMAND in
    build)
        build_frontend
        ;;
    deploy)
        check_remote
        build_frontend
        create_remote_dir
        sync_to_remote
        apply_static_route
        restart_fastapi
        verify_deployment
        show_deployment_info
        ;;
    rollback)
        rollback
        ;;
    clean)
        clean
        ;;
    *)
        echo "Usage: $0 {build|deploy|rollback|clean}"
        echo ""
        echo "Commands:"
        echo "  build    - Build the React frontend locally (no deployment)"
        echo "  deploy   - Build and deploy to remote system (default)"
        echo "  rollback - Remove static route and delete deployed files"
        echo "  clean    - Remove all deployed files (same as rollback)"
        exit 1
        ;;
esac
