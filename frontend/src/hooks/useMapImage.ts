import { useQuery } from '@tanstack/react-query';

const CACHE_KEY_PREFIX = 'map-image-cache';
const CACHE_VERSION = 1;

interface CachedMapImage {
  version: number;
  lat: number;
  lon: number;
  dataUrl: string;
  timestamp: number;
}

function getCacheKey(lat: number, lon: number): string {
  // Round to 4 decimal places for cache key (~11m precision)
  const roundedLat = lat.toFixed(4);
  const roundedLon = lon.toFixed(4);
  return `${CACHE_KEY_PREFIX}:${roundedLat},${roundedLon}`;
}

function getCachedImage(lat: number, lon: number): string | null {
  try {
    const key = getCacheKey(lat, lon);
    const cached = localStorage.getItem(key);
    if (!cached) return null;

    const parsed: CachedMapImage = JSON.parse(cached);
    if (parsed.version !== CACHE_VERSION) return null;
    
    // Check if coordinates match (within rounding tolerance)
    if (Math.abs(parsed.lat - lat) > 0.0001 || Math.abs(parsed.lon - lon) > 0.0001) {
      return null;
    }

    return parsed.dataUrl;
  } catch {
    return null;
  }
}

function setCachedImage(lat: number, lon: number, dataUrl: string): void {
  try {
    const key = getCacheKey(lat, lon);
    const cacheEntry: CachedMapImage = {
      version: CACHE_VERSION,
      lat,
      lon,
      dataUrl,
      timestamp: Date.now(),
    };
    localStorage.setItem(key, JSON.stringify(cacheEntry));
  } catch (e) {
    // localStorage might be full or disabled - fail silently
    console.warn('Failed to cache map image:', e);
  }
}

async function fetchMapImage(lat: number, lon: number): Promise<string> {
  // Check localStorage cache first
  const cached = getCachedImage(lat, lon);
  if (cached) return cached;

  // Build Yandex Static Maps URL
  const zoom = 11;
  const width = 400;
  const height = 200;
  const url = `https://static-maps.yandex.ru/1.x/?ll=${lon},${lat}&size=${width},${height}&z=${zoom}&l=map&pt=${lon},${lat},pm2rdm&lang=en_US`;

  // Fetch image as blob
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch map image');

  const blob = await response.blob();

  // Convert blob to data URL
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = reader.result as string;
      // Cache the data URL
      setCachedImage(lat, lon, dataUrl);
      resolve(dataUrl);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Hook to fetch and cache a map image for a given location.
 * 
 * - Image is cached in localStorage keyed by lat/lon
 * - Only fetches a new image when location changes
 * - Returns a data URL that can be used directly in an <img> src
 */
export function useMapImage(lat: number | null | undefined, lon: number | null | undefined) {
  return useQuery({
    queryKey: ['map-image', lat?.toFixed(4), lon?.toFixed(4)],
    queryFn: () => fetchMapImage(lat!, lon!),
    enabled: typeof lat === 'number' && typeof lon === 'number',
    staleTime: Infinity, // Never refetch unless location changes
    gcTime: Infinity, // Keep in cache forever
    retry: 1,
  });
}
