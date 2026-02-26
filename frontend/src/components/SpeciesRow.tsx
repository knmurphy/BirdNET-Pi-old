import type { SpeciesSummary } from '../types';
import './SpeciesRow.css';

interface SpeciesRowProps {
  species: SpeciesSummary;
  onClick?: () => void;
}

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function SpeciesRow({ species, onClick }: SpeciesRowProps) {
  return (
    <button
      type="button"
      className="species-row"
      onClick={onClick}
      aria-label={`${species.com_name}, ${species.detection_count} detections`}
    >
      <div className="species-row__main">
        <div className="species-row__info">
          <span className="species-row__common-name">{species.com_name}</span>
          <span className="species-row__scientific-name">{species.sci_name}</span>
        </div>
        <div className="species-row__count" aria-label="detection count">
          {species.detection_count}
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
  );
}
