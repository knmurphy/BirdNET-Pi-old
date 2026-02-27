import { useState, useMemo } from 'react';
import type { SpeciesSummary } from '../../types';
import { useSpeciesToday, type SortOption, getStoredSort, storeSort } from '../../hooks/useSpeciesToday';
import { SpeciesRow } from '../SpeciesRow';
import './Screens.css';

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'count', label: 'Count' },
  { value: 'last_seen', label: 'Recent' },
  { value: 'confidence', label: 'Confidence' },
  { value: 'alpha', label: 'A-Z' },
];

function sortSpecies(species: SpeciesSummary[], sortBy: SortOption): SpeciesSummary[] {
  return [...species].sort((a, b) => {
    switch (sortBy) {
      case 'count':
        return b.detection_count - a.detection_count;
      case 'last_seen':
        return b.last_seen.localeCompare(a.last_seen);
      case 'confidence':
        return b.max_confidence - a.max_confidence;
      case 'alpha':
        return a.com_name.localeCompare(b.com_name);
      default:
        return 0;
    }
  });
}

function SpeciesSkeleton() {
  return (
    <div className="species-list__skeleton" aria-label="Loading species">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="species-skeleton">
          <div className="species-skeleton__main">
            <div className="species-skeleton__info">
              <div className="species-skeleton__common" />
              <div className="species-skeleton__sci" />
            </div>
            <div className="species-skeleton__count" />
          </div>
          <div className="species-skeleton__meta">
            <div className="species-skeleton__time" />
            <div className="species-skeleton__conf" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function SpeciesScreen() {
  const [sortBy, setSortBy] = useState<SortOption>(() => getStoredSort());
  const { data, isLoading, isError, error, refetch } = useSpeciesToday();

  const sortedSpecies = useMemo(() => {
    if (!data?.species) return [];
    return sortSpecies(data.species, sortBy);
  }, [data, sortBy]);

  const handleSortChange = (newSort: SortOption) => {
    setSortBy(newSort);
    storeSort(newSort);
  };

  return (
    <div className="screen screen--species">
      <div className="species-list">
        <div className="species-list__header">
          <h2 className="species-list__title">Today's Species</h2>
          <div className="species-list__sort" role="group" aria-label="Sort species">
            {SORT_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`species-list__sort-btn ${sortBy === option.value ? 'species-list__sort-btn--active' : ''}`}
                onClick={() => handleSortChange(option.value)}
                aria-pressed={sortBy === option.value}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {isLoading && <SpeciesSkeleton />}

        {isError && (
          <div className="species-list__error" role="alert">
            <p className="species-list__error-text">
              {error?.message || 'Failed to load species'}
            </p>
            <button
              type="button"
              className="species-list__retry"
              onClick={() => refetch()}
            >
              Retry
            </button>
          </div>
        )}

        {!isLoading && !isError && sortedSpecies.length === 0 && (
          <div className="species-list__empty">
            <div className="screen__icon">🐦</div>
            <p className="screen__text">No species detected today</p>
            <p className="screen__hint">
              Detections will appear here as birds are identified
            </p>
          </div>
        )}

        {!isLoading && !isError && sortedSpecies.length > 0 && (
          <div className="species-list__items">
            {sortedSpecies.map((species) => (
              <SpeciesRow
                key={species.sci_name}
                species={species}
                isNew={species.is_new}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
