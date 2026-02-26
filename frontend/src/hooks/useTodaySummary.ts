import { useQuery } from '@tanstack/react-query';
import type { TodaySummaryResponse } from '../types';

async function fetchTodaySummary(): Promise<TodaySummaryResponse> {
	const response = await fetch('/api/detections/today/summary');
	if (!response.ok) throw new Error('Failed to fetch summary');
	return response.json();
}

export function useTodaySummary() {
	return useQuery({
		queryKey: ['summary', 'today'],
		queryFn: fetchTodaySummary,
		staleTime: 5_000, // SSE will invalidate on new detections
	});
}
