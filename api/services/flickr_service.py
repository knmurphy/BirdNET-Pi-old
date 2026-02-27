"""Flickr image service - uses cached images from flickr.db."""

import sqlite3
from pathlib import Path
from typing import Set

from api.models.flickr import FlickrImage, FlickrImageResponse


class FlickrService:
    """Service for retrieving cached Flickr images."""

    # Path to be flickr.db created by old PHP UI
    FLICKR_DB_PATH = Path.home() / "BirdNET-Pi" / "scripts" / "flickr.db"
    BIRDS_DB_PATH = Path.home() / "BirdNET-Pi" / "scripts" / "birds.db"
    BLACKLIST_FILE = Path.home() / "BirdNET-Pi" / "scripts" / "blacklisted_images.txt"

    def get_blacklisted_ids(self) -> Set[str]:
        """Get set of blacklisted image IDs."""
        if not self.BLACKLIST_FILE.exists():
            return set()

        try:
            with open(self.BLACKLIST_FILE, "r") as f:
                return {line.strip() for line in f if line.strip()}
        except (IOError, OSError):
            return set()

    def blacklist_image(self, image_id: str, reason: str | None = None) -> bool:
        """Add an image ID to the blacklist file."""
        try:
            with open(self.BLACKLIST_FILE, "a") as f:
                f.write(f"{image_id}\n")
            return True
        except (IOError, OSError):
            return False

    def unblacklist_image(self, image_id: str) -> bool:
        """Remove an image ID from the blacklist file."""
        if not self.BLACKLIST_FILE.exists():
            return False

        try:
            with open(self.BLACKLIST_FILE, "r") as f:
                lines = f.readlines()

            lines = [line for line in lines if line.strip() != image_id]

            with open(self.BLACKLIST_FILE, "w") as f:
                f.writelines(lines)

            return True
        except (IOError, OSError):
            return False

    def get_cached_image(self, sci_name: str) -> FlickrImage | None:
        """Get a cached image for a species from flickr.db."""
        if not self.FLICKR_DB_PATH.exists():
            return None

        blacklisted_ids = self.get_blacklisted_ids()

        try:
            conn = sqlite3.connect(str(self.FLICKR_DB_PATH))
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT id, sci_name, com_en_name, image_url, title, author_url, license_url
                    FROM images
                    WHERE sci_name = ?
                    """,
                [sci_name],
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                image_id = str(row[0])
                if image_id in blacklisted_ids:
                    return None

                flickr_image = FlickrImage(
                    sci_name=row[1],
                    com_name=row[2],
                    image_url=row[3],
                    title=row[4],
                    author_url=row[5],
                    license_url=row[6],
                )
                flickr_image.image_id = image_id
                return flickr_image
            return None
        except sqlite3.Error:
            return None

        try:
            conn = sqlite3.connect(str(self.FLICKR_DB_PATH))
            cursor = conn.cursor()
            cursor.execute(
                """
                    SELECT id, sci_name, com_en_name, image_url, title, author_url, license_url
                    FROM images
                    WHERE sci_name = ?
                    """,
                [sci_name],
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                flickr_image = FlickrImage(
                    sci_name=row[1],
                    com_name=row[2],
                    image_url=row[3],
                    title=row[4],
                    author_url=row[5],
                    license_url=row[6],
                )
                flickr_image.image_id = str(row[0])
                return flickr_image
            return None
            return None
        except sqlite3.Error:
            return None

    def get_image_for_common_name(self, com_name: str) -> FlickrImage | None:
        """Get a cached image by common name (for detection cards)."""
        if not self.FLICKR_DB_PATH.exists():
            return None

        blacklisted_ids = self.get_blacklisted_ids()

        try:
            conn = sqlite3.connect(str(self.FLICKR_DB_PATH))
            cursor = conn.cursor()

            cursor.execute(
                """
                    SELECT id, sci_name, com_en_name, image_url, title, author_url, license_url
                    FROM images
                    WHERE com_en_name = ? COLLATE NOCASE
                    """,
                [com_name],
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                image_id = str(row[0])
                if image_id in blacklisted_ids:
                    return None

                flickr_image = FlickrImage(
                    sci_name=row[1],
                    com_name=row[2],
                    image_url=row[3],
                    title=row[4],
                    author_url=row[5],
                    license_url=row[6],
                )
                flickr_image.image_id = image_id
                return flickr_image
            return None
        except sqlite3.Error:
            return None

    def get_or_fetch_image(
        self, sci_name: str, com_name: str
    ) -> FlickrImageResponse | None:
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
