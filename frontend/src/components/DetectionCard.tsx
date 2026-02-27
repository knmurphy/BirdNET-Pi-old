/**
 * Detection Card Component
 * Displays a single detection with species name, confidence, time, and classifier badge
 */

import type { Detection } from '../types';
import { useAudio } from '../hooks/useAudio';
import { useSpeciesImage } from '../hooks/useSpeciesImage';
import { formatConfidence } from '../hooks/useDetections';
import './DetectionCard.css';

export interface DetectionCardProps {
	detection: Detection;
	/** Optional classifier color override (from classifier config) */
	classifierColor?: string;
	/** Optional confidence thresholds (from classifier config) */
	thresholds?: { high: number; medium: number };
	/** Click handler for audio playback */
	onClick?: () => void;
	/** Whether this is a newly arrived detection (triggers animation) */
	isNew?: boolean;
	/** Age category for time-based fading */
	ageCategory?: 'recent' | 'medium' | 'old';
}

/**
 * Get default classifier color based on classifier ID
 */
function getDefaultClassifierColor(classifier: string): string {
	switch (classifier) {
		case 'birdnet':
			return 'var(--classifier-birdnet)';
		case 'batdetect2':
			return 'var(--classifier-batdetect2)';
		case 'google-perch':
			return 'var(--classifier-google-perch)';
		default:
			return 'var(--classifier-unknown)';
	}
}

/**
 * Get classifier display name
 */
function getClassifierDisplayName(classifier: string): string {
	switch (classifier) {
		case 'birdnet':
			return 'BirdNET';
		case 'batdetect2':
			return 'BatDetect2';
		case 'google-perch':
			return 'Perch';
		default:
			return classifier;
	}
}

export function DetectionCard({
	detection,
	classifierColor,
	// thresholds, // Unused parameter - remove to fix TS6133 error
	onClick,
	isNew = false,
	ageCategory = 'recent',
}: DetectionCardProps) {
	const { playing, toggle } = useAudio(detection.id, detection.file_name);
	const { data: image } = useSpeciesImage(detection.com_name);

	const ageClassName = ageCategory === 'recent' ? '' : `detection-card--age-${ageCategory}`;

	const handleClick = () => {
		toggle();
		onClick?.();
	};

	return (
		<article
			className={`detection-card ${isNew ? 'detection-card--new' : ''} ${ageClassName}`.trim()}
			onClick={handleClick}
			role="button"
			tabIndex={0}
			aria-label={`${detection.com_name}, confidence ${formatConfidence(detection.confidence)}, ${playing ? 'stop audio' : 'play audio'}`}
		>
			<div className="detection-card__content">
				{image && (
					<img
						src={image.image_url}
						alt={detection.com_name}
						className="detection-card__image"
						loading="lazy"
					/>
				)}
				<div className="detection-card__info">
					<div className="detection-card__header">
						<h3 className="detection-card__common-name">{detection.com_name}</h3>
						<time className="detection-card__time" dateTime={detection.iso8601}>
							{detection.time}
						</time>
					</div>

					<p className="detection-card__scientific-name">{detection.sci_name}</p>

					<div className="detection-card__confidence">
						<div className="detection-card__confidence-bar">
							<div
								className="detection-card__confidence-fill"
								style={{
									width: `${detection.confidence * 100}%`,
									backgroundColor: classifierColor ?? getDefaultClassifierColor(detection.classifier),
								}}
							/>
						</div>
						<span className="detection-card__confidence-value">
							{formatConfidence(detection.confidence)}
						</span>
					</div>

					<div className="detection-card__footer">
						<span className="detection-card__classifier">
							<span
								className="detection-card__classifier-dot"
								style={{ backgroundColor: classifierColor ?? getDefaultClassifierColor(detection.classifier) }}
								aria-hidden="true"
							/>
							<span className="detection-card__classifier-name">{getClassifierDisplayName(detection.classifier)}</span>
						</span>
						{playing && <span className="detection-card__playing-indicator">▶</span>}
					</div>
				</div>
			</div>
		</article>
	);
}
