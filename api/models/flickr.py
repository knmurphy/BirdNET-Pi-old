"""Pydantic models for Flickr image integration."""

from pydantic import BaseModel


class FlickrImage(BaseModel):
    """Cached Flickr image for a species."""

    image_id: str = ""
    sci_name: str
    com_name: str
    image_url: str
    title: str | None
    author_url: str | None
    license_url: str | None
    image_id: str  # Flickr photo ID for blacklisting


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


class BlacklistRequest(BaseModel):
    """Request to blacklist a Flickr image."""

    image_id: str
    reason: str | None = None


class UnblacklistRequest(BaseModel):
    """Request to remove image from blacklist."""

    image_id: str


class BlacklistResponse(BaseModel):
    """Response for blacklist/unblacklist operations."""

    success: bool
    message: str
