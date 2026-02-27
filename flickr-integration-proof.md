# Flickr Species Image Integration - Proof of Work

*2026-02-27T00:28:24Z by Showboat 0.6.1*
<!-- showboat-id: 4374d4af-e605-4fdd-b688-d1689aff157a -->

This document proves the Flickr species image integration is working on the BirdNET-Pi Field Station React PWA.



## Evidence: Species Page with Flickr Images

The Species page displays cached Flickr images for each detected species. The images are loaded from flickr.db cache on the Pi.

```bash
curl -s http://10.0.0.177:8003/api/species/Bewick%27s%20Wren/image | jq .
```

```output
{
  "sci_name": "Thryomanes bewickii",
  "com_name": "Bewick's Wren",
  "image_url": "https://farm5.static.flickr.com/4640/38410728694_8c9ea3e778.jpg",
  "title": "Bewick's Wren",
  "author_url": "https://flickr.com/people/44880465@N02",
  "license_url": "https://creativecommons.org/licenses/by-nc-nd/2.0/",
  "source": "flickr"
}
```

```bash {image}
![Species page with Flickr images](/tmp/flickr-species-page.png)
```

![Species page with Flickr images](b98f8de0-2026-02-27.png)

```bash {image}
![Bewicks Wren with Flickr image](/tmp/flickr-species-row-bewick.png)
```

![Bewicks Wren with Flickr image](4aa0facf-2026-02-27.png)



## Frontend Hook: useSpeciesImage

The React frontend uses the `useSpeciesImage` hook to fetch images from the API endpoint.

```bash
cat frontend/src/hooks/useSpeciesImage.ts
```

```output
import { useQuery } from '@tanstack/react-query';
import type { FlickrImageResponse } from '../types';

async function fetchSpeciesImage(comName: string): Promise<FlickrImageResponse> {
	const response = await fetch(`/api/species/${encodeURIComponent(comName)}/image`);
	if (!response.ok) {
		if (response.status === 404) {
			// No image cached - return null indicator
			throw new Error('No image available');
		}
		throw new Error('Failed to fetch species image');
	}
	return response.json();
}

/**
 * Hook to fetch a species image from the Flickr cache.
 * Returns null if no image is available (graceful degradation).
 */
export function useSpeciesImage(comName: string | null | undefined) {
	return useQuery({
		queryKey: ['species', 'image', comName],
		queryFn: () => fetchSpeciesImage(comName!),
		enabled: !!comName,
		staleTime: 60 * 60 * 1000, // 1 hour - images don't change often
		gcTime: 24 * 60 * 60 * 1000, // Keep in cache for 24 hours
		retry: false, // Don't retry 404s
	});
}
```



## Backend Service: FlickrService

The backend uses `FlickrService` to read cached images from `flickr.db`.

```bash
cat api/services/flickr_service.py
```

```output
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
```



## Tests

Comprehensive tests have been written for the Flickr integration.

```bash
wc -l api/tests/test_flickr.py && head -50 api/tests/test_flickr.py
```

```output
     440 api/tests/test_flickr.py
"""Tests for Flickr image integration."""

import pytest
from unittest.mock import patch, MagicMock
import sqlite3

from fastapi.testclient import TestClient

from api.main import app
from api.services.flickr_service import FlickrService
from api.models.flickr import FlickrImage, FlickrImageResponse


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestFlickrModels:
    """Tests for Flickr Pydantic models."""

    def test_flickr_image_required_fields(self):
        """FlickrImage requires sci_name, com_name, image_url."""
        image = FlickrImage(
            sci_name="Turdus migratorius",
            com_name="American Robin",
            image_url="https://example.com/image.jpg",
        )
        assert image.sci_name == "Turdus migratorius"
        assert image.com_name == "American Robin"
        assert image.image_url == "https://example.com/image.jpg"
        assert image.title is None
        assert image.author_url is None
        assert image.license_url is None

    def test_flickr_image_optional_fields(self):
        """FlickrImage accepts optional attribution fields."""
        image = FlickrImage(
            sci_name="Turdus migratorius",
            com_name="American Robin",
            image_url="https://example.com/image.jpg",
            title="American Robin in flight",
            author_url="https://flickr.com/people/user",
            license_url="https://creativecommons.org/licenses/by/2.0/",
        )
        assert image.title == "American Robin in flight"
        assert image.author_url == "https://flickr.com/people/user"
        assert image.license_url == "https://creativecommons.org/licenses/by/2.0/"

```
