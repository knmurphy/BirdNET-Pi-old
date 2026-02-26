import { useQuery } from '@tanstack/react-query';
import type { SystemResponse } from '../types';

async function fetchSystemHealth(): Promise<SystemResponse> {
	const response = await fetch('/api/system');
	if (!response.ok) throw new Error('Failed to fetch system health');
	return response.json();
}

export function useSystemHealth() {
	return useQuery({
		queryKey: ['system', 'health'],
		queryFn: fetchSystemHealth,
		refetchInterval: 10_000, // Poll every 10 seconds
	});
}
