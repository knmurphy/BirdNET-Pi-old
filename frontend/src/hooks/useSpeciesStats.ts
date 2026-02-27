/**
 * Species Stats Hook
 * Fetches full statistics for all species
 */

import { useQuery } from '@tanstack/react-query';
import type { SpeciesStatsResponse } from '../types';

const API_BASE = '/api';

export function useSpeciesStats() {
  return useQuery<SpeciesStatsResponse>({
    queryKey: ['species-stats'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/species/stats`);
      if (!response.ok) {
        throw new Error('Failed to fetch species stats');
      }
      return response.json();
    },
    refetchInterval: 60000,
    staleTime: 30000,
  });
}
