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
