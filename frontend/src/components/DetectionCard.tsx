/**
 * Detection Card Component
 * Displays a single detection with species name, confidence, time, and classifier badge
 */

import type { Detection } from '../types';
import { useAudio } from '../../src/hooks/useAudio';
import { getConfidenceColor, formatConfidence } from '../../src/hooks/useDetections';
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
	thresholds,
	onClick,
	isNew = false,
}: DetectionCardProps) {
	const { audioUrl } = useAudio(detection.id, detection.file_name);

	return (
		<article
			className={`detection-card ${isNew ? 'detection-card--new' : ''}`}
			onClick={onClick}
			role="button"
			tabIndex={0}
			aria-label={`${detection.com_name}, confidence ${formatConfidence(detection.confidence)}, play audio`}
		>
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
				<audio src={audioUrl} preload="none" style={{ display: 'none' }} />
				<span className="detection-card__classifier">
					<span
						className="detection-card__classifier-dot"
						style={{ backgroundColor: classifierColor ?? getDefaultClassifierColor(detection.classifier) }}
						aria-hidden="true"
					/>
					<span className="detection-card__classifier-name">{getClassifierDisplayName(detection.classifier)}</span>
				</span>
			</div>
		</article>
	);
}
