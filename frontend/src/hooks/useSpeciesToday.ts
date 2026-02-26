import { useQuery } from '@tanstack/react-query';
import type { SpeciesTodayResponse } from '../types';

const SORT_STORAGE_KEY = 'field-station-species-sort';

export type SortOption = 'count' | 'last_seen' | 'confidence' | 'alpha';

export function getStoredSort(): SortOption {
  if (typeof window === 'undefined') return 'count';
  const stored = localStorage.getItem(SORT_STORAGE_KEY);
  if (stored && ['count', 'last_seen', 'confidence', 'alpha'].includes(stored)) {
    return stored as SortOption;
  }
  return 'count';
}

export function storeSort(sort: SortOption): void {
  localStorage.setItem(SORT_STORAGE_KEY, sort);
}


async function fetchSpeciesToday(): Promise<SpeciesTodayResponse> {
  const response = await fetch('/api/species/today');
  if (!response.ok) throw new Error('Failed to fetch species');
  return response.json();
}

export function useSpeciesToday() {
  return useQuery({
    queryKey: ['species', 'today'],
    queryFn: fetchSpeciesToday,
    staleTime: 30_000, // 30 seconds
    refetchOnWindowFocus: true,
  });
}
