#MY:"""FastAPI application entry point - React PWA + API Backend."""
#HW:
#MW:Production-ready FastAPI backend serving React PWA frontend.
#HY:All API endpoints and React SPA served from a single FastAPI instance.
#MX:"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.exceptions import HTTPException
import os


from api.routers import detections, species, system, classifiers, settings_router, events, audio, spectrogram


# App configuration
API_TITLE = "Field Station API"
API_VERSION = "0.1.0"
API_DESCRIPTION = "REST API backend for BirdNET-Pi passive acoustic monitoring"


# FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)


# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(detections.router, prefix="/api", tags=["detections"])
app.include_router(species.router, prefix="/api", tags=["species"])
app.include_router(system.router, prefix="/api", tags=["system"])
app.include_router(classifiers.router, prefix="/api", tags=["classifiers"])
app.include_router(settings_router.router, prefix="/api", tags=["settings"])
app.include_router(events.router, prefix="/api", tags=["events"])
app.include_router(audio.router, prefix="/api", tags=["audio"])
app.include_router(spectrogram.router, prefix="/api", tags=["spectrogram"])


# ============================================
# React PWA Serving Configuration
# ============================================

# Get the frontend dist directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")


def serve_react_app(request_path: str):
    """Serve React PWA application."""
    if not os.path.exists(FRONTEND_DIST):
        raise HTTPException(status_code=503, detail="Frontend not built. Run: cd frontend && npm run build")

    # Serve PWA manifest (both manifest.json and manifest.webmanifest)
    if request_path in ["manifest.json", "manifest.webmanifest"]:
        # Try both manifest files
        for manifest_name in ["manifest.webmanifest", "manifest.json"]:
            manifest_path = os.path.join(FRONTEND_DIST, manifest_name)
            if os.path.exists(manifest_path):
                return FileResponse(manifest_path, media_type="application/json")

    # Serve service worker files
    if request_path in ["sw.js", "registerSW.js"] or request_path.startswith("workbox-"):
        # Try to find the service worker file
        sw_patterns = ["sw.js", "registerSW.js", "workbox-*.js"]
        import glob
        for pattern in sw_patterns:
            matches = glob.glob(os.path.join(FRONTEND_DIST, pattern))
            if matches:
                return FileResponse(matches[0], media_type="application/javascript")
    # Serve favicon
    if request_path == "favicon.ico":
        favicon_path = os.path.join(FRONTEND_DIST, "vite.svg")  # Fallback to the vite SVG
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
        favicon_path = os.path.join(FRONTEND_DIST, "vite.svg")  # Fallback to the vite SVG
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)

    # Serve index.html for all other non-API routes
    if not request_path.startswith("api/") and not request_path.startswith("static/"):
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

    # If we get here, the file doesn't exist
    raise HTTPException(status_code=404, detail="Not found")


# Mount static assets (JS, CSS, images)
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve icons directory
    icons_dir = os.path.join(FRONTEND_DIST, "icons")
    if os.path.exists(icons_dir):
        app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")

    # Mount the catch-all route last (to not interfere with API routes)
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        """Serve React PWA for all non-API routes."""
        return serve_react_app(full_path)
else:
    log_warning = lambda msg: None  # No-op if logging not configured
    log_warning("FRONTEND_DIST not found. Run 'cd frontend && npm run build' first.")


# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "frontend": "/",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": API_VERSION}


# ============================================
# Application Lifecycle
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    if os.path.exists(FRONTEND_DIST):
        print(f"[INFO] Serving React PWA from: {FRONTEND_DIST}")
        print(f"[INFO] Static assets mounted at: /assets")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("[INFO] API server shutting down")
