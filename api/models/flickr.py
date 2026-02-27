"""Pydantic models for Flickr image integration."""

from pydantic import BaseModel


class FlickrImage(BaseModel):
    """Cached Flickr image for a species."""
    
    sci_name: str
    com_name: str
    image_url: str
    title: str | None
    author_url: str | None
    license_url: str | None


class FlickrImageResponse(BaseModel):
    """Response for /api/species/{name}/image."""
    
    sci_name: str
    com_name: str
    image_url: str
    title: str | None
    author_url: str | None
    license_url: str | None
    source: str  # "flickr" or "wikipedia"


class FlickrCacheStatus(BaseModel):
    """Status of Flickr image cache."""
    
    total_cached: int
    total_species: int
