"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
