import type { SpeciesSummary, SpeciesDetectionHistory } from '../types';
import { useSpeciesImage } from '../hooks/useSpeciesImage';
import { useState } from 'react';
import { SpeciesChartDialog } from './SpeciesChartDialog';
import './SpeciesRow.css';

interface SpeciesRowProps {
  species: SpeciesSummary;
  isNew?: boolean;
  onClick?: () => void;
  chartData?: SpeciesDetectionHistory | null;
  onOpenChart?: (data: SpeciesDetectionHistory) => void;
  onCloseChart?: () => void;
}

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function SpeciesRow({ species, isNew, onClick, chartData, onOpenChart, onCloseChart }: SpeciesRowProps) {
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

  return (
    <>
      <button
        type="button"
        className="species-row"
        onClick={onClick}
        aria-label={`${species.com_name}, ${species.detection_count} detections`}
      >
        <div className="species-row__main">
          {image && (
            <img
              src={image.image_url}
              alt={species.com_name}
              className="species-row__image"
              loading="lazy"
            />
          )}
          <div className="species-row__info">
            <span className="species-row__common-name">
              {species.com_name}
              {isNew && <span className="species-row__new-badge">NEW</span>}
            </span>
            <span className="species-row__scientific-name">{species.sci_name}</span>
          </div>
          <div className="species-row__right">
            <div className="species-row__count" aria-label="detection count">
              {species.detection_count}
            </div>
            <button
              className="species-row__chart-btn"
              onClick={handleChartClick}
              aria-label="View species stats"
              title="View species stats"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <path d="M3 18 L9 12 L15 14 L21 6" />
              </svg>
            </button>
          </div>
        </div>
        <div className="species-row__meta">
          <span className="species-row__time">
            Last: {species.last_seen}
          </span>
          <span className="species-row__confidence">
            Peak: {formatConfidence(species.max_confidence)}
          </span>
        </div>
      </button>

      <SpeciesChartDialog
        isOpen={isChartActive}
        onClose={handleCloseChart}
        species={activeChartData}
      />
    </>
  );
}
