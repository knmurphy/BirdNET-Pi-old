import type { SpeciesSummary } from '../types';
import { useSpeciesImage } from '../hooks/useSpeciesImage';
import './SpeciesRow.css';

interface SpeciesRowProps {
  species: SpeciesSummary;
  isNew?: boolean;
  onClick?: () => void;
}

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function SpeciesRow({ species, isNew, onClick }: SpeciesRowProps) {
  const { data: image } = useSpeciesImage(species.com_name);
  
  return (
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
