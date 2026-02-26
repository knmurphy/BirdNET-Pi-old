"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os


from api.routers import detections, species, system, classifiers, settings_router, events, audio, spectrogram

app = FastAPI(
    title="Field Station API",
    version="0.1.0",
    description="REST API backend for BirdNET-Pi passive acoustic monitoring",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
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


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Field Station API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


# Serve React app (must be last to not override API routes)
dist_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, 'assets')), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes."""
        # API routes are handled by routers above
        if full_path.startswith('api/'):
            return None  # Let API routers handle it
        return FileResponse(os.path.join(dist_dir, 'index.html'))
