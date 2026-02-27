/**
 * Species Card Component
 * Full species card for stats view with video player
 */

import { useState } from 'react';
import type { SpeciesStats, SpeciesDetectionHistory } from '../types';
import { useSpeciesImage } from '../hooks/useSpeciesImage';
import { formatConfidence } from '../hooks/useDetections';
import { SpeciesChartDialog } from './SpeciesChartDialog';
import './SpeciesCard.css';

interface SpeciesCardProps {
  species: SpeciesStats;
  chartData?: SpeciesDetectionHistory | null;
  onOpenChart?: (data: SpeciesDetectionHistory) => void;
  onCloseChart?: () => void;
}

export function SpeciesCard({
  species,
  chartData,
  onOpenChart,
  onCloseChart,
}: SpeciesCardProps) {
  const { data: image } = useSpeciesImage(species.com_name);
  const [localChartData, setLocalChartData] = useState<SpeciesDetectionHistory | null>(null);
  const [isChartOpen, setIsChartOpen] = useState(false);

  const handleChartClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const response = await fetch(
        `/api/detections/species/history?com_name=${encodeURIComponent(species.com_name)}&days=30`
      );
      const data: SpeciesDetectionHistory = await response.json();

      if (onOpenChart) {
        onOpenChart(data);
      } else {
        setLocalChartData(data);
        setIsChartOpen(true);
      }
    } catch (error) {
      console.error('Failed to fetch species history:', error);
    }
  };

  const handleCloseChart = () => {
    if (onCloseChart) {
      onCloseChart();
    } else {
      setIsChartOpen(false);
    }
  };

  const activeChartData = chartData ?? localChartData;
  const isChartActive = chartData !== undefined ? chartData !== null : isChartOpen;

  const handleOpenInNewTab = () => {
    const url = `/index.php?filename=${encodeURIComponent(species.best_file_name)}`;
    window.open(url, '_blank');
  };

  return (
    <>
      <article className="species-card">
        <div className="species-card__header">
          {image && (
            <img
              src={image.image_url}
              alt={species.com_name}
              className="species-card__image"
              loading="lazy"
            />
          )}
          <div className="species-card__header-content">
            <div className="species-card__names">
              <h3 className="species-card__common-name">{species.com_name}</h3>
              <p className="species-card__scientific-name">{species.sci_name}</p>
            </div>
            <button
              className="species-card__open-btn"
              onClick={handleOpenInNewTab}
              aria-label="Open best recording in new tab"
              title="Open in new tab"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </button>
          </div>
        </div>

        <div className="species-card__stats">
          <div className="species-card__stat">
            <div className="species-card__stat-label">Occurrences</div>
            <div className="species-card__stat-value">{species.detection_count}</div>
          </div>
          <div className="species-card__stat">
            <div className="species-card__stat-label">Max Confidence</div>
            <div className="species-card__stat-value">{formatConfidence(species.max_confidence)}</div>
          </div>
          <div className="species-card__stat">
            <div className="species-card__stat-label">Best Recording</div>
            <div className="species-card__stat-value">
              <time dateTime={species.best_date}>
                {new Date(species.best_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </time>
              <span className="species-card__stat-time">{species.best_time}</span>
            </div>
          </div>
          <div className="species-card__ref-links">
            <a
              href={`https://allaboutbirds.org/guide/${species.com_name.replace(/ /g, '_')}`}
              target="_blank"
              rel="noopener noreferrer"
              className="species-card__ref-link"
              aria-label={`All About Birds page for ${species.com_name}`}
              title="All About Birds"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6M12 18v6M6 12h12" />
              </svg>
            </a>
            <a
              href={`https://en.wikipedia.org/wiki/${species.sci_name.replace(/ /g, '_')}`}
              target="_blank"
              rel="noopener noreferrer"
              className="species-card__ref-link"
              aria-label={`Wikipedia page for ${species.sci_name}`}
              title="Wikipedia"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="21" />
                <path d="M14.5 17.5L12 20.5L9.5 17.5L7.5 12M9 11l3-3" />
              </svg>
            </a>
          </div>
        </div>

        <div className="species-card__video-wrapper">
          <div className="species-card__video">
            <div className="species-card__poster">
              <div className="species-card__poster-content">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M9 18V5l12-2v13" />
                  <circle cx="6" cy="18" r="3" />
                  <circle cx="18" cy="16" r="3" />
                </svg>
              </div>
            </div>
            <button
              className="species-card__play-btn"
              onClick={handleOpenInNewTab}
              aria-label={`Play ${species.com_name} recording`}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
            </button>
          </div>
        </div>

        <button
          className="species-card__chart-btn"
          onClick={handleChartClick}
          aria-label="View species stats"
          title="View stats chart"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <path d="M3 18 L9 12 L15 14 L21 6" />
          </svg>
          <span>Stats</span>
        </button>
      </article>

      <SpeciesChartDialog
        isOpen={isChartActive}
        onClose={handleCloseChart}
        species={activeChartData}
      />
    </>
  );
}
