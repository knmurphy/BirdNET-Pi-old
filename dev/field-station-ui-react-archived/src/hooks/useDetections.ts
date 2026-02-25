/**
 * Detection Data Hooks
 * React Query hooks for fetching and subscribing to detection data
 */

import { useQuery } from '@tanstack/react-query';
import type { Detection } from '../types';

// Default confidence thresholds (can be overridden by classifier config)
const DEFAULT_THRESHOLDS = {
	high: 0.85,
	medium: 0.65,
};

interface DetectionsResponse {
	detections: Detection[];
}

/**
 * Fetch today's detections from API
 */
async function fetchDetectionsToday(): Promise<DetectionsResponse> {
	const response = await fetch('/api/detections?date=today');
	if (!response.ok) {
		throw new Error(`Failed to fetch detections: ${response.status}`);
	}
	return response.json();
}

/**
 * Hook for fetching today's detections (initial load)
 * This is called once on mount; subsequent updates come via SSE
 */
export function useDetectionsToday() {
	return useQuery({
		queryKey: ['detections', 'live'],
		queryFn: fetchDetectionsToday,
		staleTime: Infinity, // SSE updates cache, never refetch automatically
		refetchOnWindowFocus: false,
		retry: 3,
		retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
	});
}

/**
 * Hook for subscribing to live detections
 * Returns the cached detections updated by SSE events
 */
export function useLiveDetections() {
	const liveData = useQuery({
		queryKey: ['detections', 'live'],
		queryFn: fetchDetectionsToday,
		staleTime: Infinity,
		refetchOnWindowFocus: false,
	});

	return {
		detections: liveData.data?.detections ?? [],
		isLoading: liveData.isLoading,
		isError: liveData.isError,
		error: liveData.error,
	};
}

/**
 * Get confidence color based on thresholds
 * Returns CSS variable name for the color
 */
export function getConfidenceColor(
	confidence: number,
	classifierThresholds?: { high: number; medium: number }
): string {
	const { high, medium } = classifierThresholds ?? DEFAULT_THRESHOLDS;

	if (confidence >= high) return 'var(--accent)';
	if (confidence >= medium) return 'var(--amber)';
	return 'var(--red)';
}

/**
 * Get confidence level label
 */
export function getConfidenceLevel(
	confidence: number,
	classifierThresholds?: { high: number; medium: number }
): 'high' | 'medium' | 'low' {
	const { high, medium } = classifierThresholds ?? DEFAULT_THRESHOLDS;

	if (confidence >= high) return 'high';
	if (confidence >= medium) return 'medium';
	return 'low';
}

/**
 * Format confidence as percentage string
 */
export function formatConfidence(confidence: number): string {
	return `${Math.round(confidence * 100)}%`;
}
