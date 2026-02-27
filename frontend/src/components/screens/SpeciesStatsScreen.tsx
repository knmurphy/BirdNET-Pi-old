/**
 * Species Stats Screen
 * Full species list with sorting and detailed cards
 */

import { useState, useMemo } from 'react';
import type { SpeciesStats, SpeciesDetectionHistory } from '../../types';
import { useSpeciesStats } from '../../hooks/useSpeciesStats';
import { SpeciesCard } from '../SpeciesCard';
import './Screens.css';

type SortOption = 'count' | 'alpha' | 'confidence' | 'date';

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'alpha', label: 'A-Z' },
  { value: 'count', label: 'Occurrences' },
  { value: 'confidence', label: 'Confidence' },
  { value: 'date', label: 'Date' },
];

function sortSpeciesStats(species: SpeciesStats[], sortBy: SortOption): SpeciesStats[] {
  return [...species].sort((a, b) => {
    switch (sortBy) {
      case 'count':
        return b.detection_count - a.detection_count;
      case 'confidence':
        return b.max_confidence - a.max_confidence;
      case 'date': {
        const dateA = `${a.best_date} ${a.best_time}`;
        const dateB = `${b.best_date} ${b.best_time}`;
        return dateB.localeCompare(dateA);
      }
      case 'alpha':
        return a.com_name.localeCompare(b.com_name);
      default:
        return 0;
    }
  });
}

function StatsSkeleton() {
  return (
    <div className="species-stats__grid" aria-label="Loading species stats">
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} className="species-card--skeleton">
          <div className="species-card__header--skeleton" />
          <div className="species-card__stats--skeleton">
            <div className="species-card__stat--skeleton" />
            <div className="species-card__stat--skeleton" />
            <div className="species-card__stat--skeleton" />
          </div>
          <div className="species-card__player--skeleton" />
        </div>
      ))}
    </div>
  );
}

export function SpeciesStatsScreen() {
  const [sortBy, setSortBy] = useState<SortOption>('count');
  const [chartData, setChartData] = useState<SpeciesDetectionHistory | null>(null);
  const { data, isLoading, isError, error } = useSpeciesStats();

  const sortedSpecies = useMemo(() => {
    const speciesList = data?.species;
    if (!speciesList) return [];
    return sortSpeciesStats(speciesList, sortBy);
  }, [data, sortBy]);

  const handleOpenChart = (data: SpeciesDetectionHistory) => {
    setChartData(data);
  };

  const handleCloseChart = () => {
    setChartData(null);
  };

  return (
    <div className="screen screen--species-stats">
      <div className="species-stats__container">
        <div className="species-stats__header">
          <h2 className="species-stats__title">
            Species Stats
            <span className="species-stats__count">
              {data?.total_species ?? 0}
            </span>
          </h2>
          <div className="species-stats__sort" role="group" aria-label="Sort species">
            {SORT_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`species-stats__sort-btn ${sortBy === option.value ? 'species-stats__sort-btn--active' : ''}`}
                onClick={() => setSortBy(option.value)}
                aria-pressed={sortBy === option.value}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {isLoading && <StatsSkeleton />}

        {isError && (
          <div className="species-stats__error" role="alert">
            <p className="species-stats__error-text">
              {error?.message || 'Failed to load species stats'}
            </p>
          </div>
        )}

        {!isLoading && !isError && sortedSpecies.length === 0 && (
          <div className="species-stats__empty">
            <div className="screen__icon">🐦</div>
            <p className="screen__text">No species detected yet</p>
            <p className="screen__hint">
              Species statistics will appear here as detections are recorded
            </p>
          </div>
        )}

        {!isLoading && !isError && sortedSpecies.length > 0 && (
          <div className="species-stats__grid">
            {sortedSpecies.map((species) => (
              <SpeciesCard
                key={species.sci_name}
                species={species}
                chartData={chartData}
                onOpenChart={handleOpenChart}
                onCloseChart={handleCloseChart}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
