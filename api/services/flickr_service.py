"""Flickr image service - uses cached images from flickr.db."""

import sqlite3
from pathlib import Path

from api.models.flickr import FlickrImage, FlickrImageResponse


class FlickrService:
    """Service for retrieving cached Flickr images."""

    # Path to the flickr.db created by the old PHP UI
    FLICKR_DB_PATH = Path.home() / "BirdNET-Pi" / "scripts" / "flickr.db"
    BIRDS_DB_PATH = Path.home() / "BirdNET-Pi" / "scripts" / "birds.db"

    def get_cached_image(self, sci_name: str) -> FlickrImage | None:
        """Get a cached image for a species from flickr.db."""
        if not self.FLICKR_DB_PATH.exists():
            return None

        try:
            conn = sqlite3.connect(str(self.FLICKR_DB_PATH))
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT sci_name, com_en_name, image_url, title, author_url, license_url
                FROM images
                WHERE sci_name = ?
                """,
                [sci_name],
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                return FlickrImage(
                    sci_name=row[0],
                    com_name=row[1],
                    image_url=row[2],
                    title=row[3],
                    author_url=row[4],
                    license_url=row[5],
                )
            return None
        except sqlite3.Error:
            return None

    def get_image_for_common_name(self, com_name: str) -> FlickrImage | None:
        """Get a cached image by common name (for detection cards)."""
        if not self.FLICKR_DB_PATH.exists():
            return None

        try:
            conn = sqlite3.connect(str(self.FLICKR_DB_PATH))
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT sci_name, com_en_name, image_url, title, author_url, license_url
                FROM images
                WHERE com_en_name = ? COLLATE NOCASE
                """,
                [com_name],
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                return FlickrImage(
                    sci_name=row[0],
                    com_name=row[1],
                    image_url=row[2],
                    title=row[3],
                    author_url=row[4],
                    license_url=row[5],
                )
            return None
        except sqlite3.Error:
            return None

    def get_or_fetch_image(self, sci_name: str, com_name: str) -> FlickrImageResponse | None:
        """
        Get image from cache. Falls back to placeholder if not cached.
        
        Note: This only reads from the cache. The old PHP UI handles
        the actual Flickr API calls and caching.
        """
        # Try by scientific name first
        cached = self.get_cached_image(sci_name)
        if cached:
            return FlickrImageResponse(
                sci_name=cached.sci_name,
                com_name=cached.com_name,
                image_url=cached.image_url,
                title=cached.title,
                author_url=cached.author_url,
                license_url=cached.license_url,
                source="flickr",
            )

        # Try by common name
        cached = self.get_image_for_common_name(com_name)
        if cached:
            return FlickrImageResponse(
                sci_name=cached.sci_name,
                com_name=cached.com_name,
                image_url=cached.image_url,
                title=cached.title,
                author_url=cached.author_url,
                license_url=cached.license_url,
                source="flickr",
            )

        return None
