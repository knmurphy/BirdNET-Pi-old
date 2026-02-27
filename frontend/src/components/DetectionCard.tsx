/**
 * Detection Card Component
 * Displays a single detection with species name, confidence, time, and classifier badge
 */

import type { Detection, SpeciesDetectionHistory } from '../types';
import { useAudio } from '../hooks/useAudio';
import { useSpeciesImage } from '../hooks/useSpeciesImage';
import { formatConfidence } from '../hooks/useDetections';
import { useState } from 'react';
import { SpeciesChartDialog } from './SpeciesChartDialog';
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
	/** External chart dialog state (for shared dialog management) */
	chartData?: SpeciesDetectionHistory | null;
	onOpenChart?: (data: SpeciesDetectionHistory) => void;
	onCloseChart?: () => void;
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
	chartData,
	onOpenChart,
	onCloseChart,
}: DetectionCardProps) {
	const { playing, toggle } = useAudio(detection.id, detection.file_name);
	const { data: image } = useSpeciesImage(detection.com_name);
	const [localChartData, setLocalChartData] = useState<SpeciesDetectionHistory | null>(null);
	const [isChartOpen, setIsChartOpen] = useState(false);

	const ageClassName = ageCategory === 'recent' ? '' : `detection-card--age-${ageCategory}`;

	const handleClick = () => {
		toggle();
		onClick?.();
	};

	const handleChartClick = async (e: React.MouseEvent) => {
		e.stopPropagation();
		try {
			const response = await fetch(
				`/api/detections/species/history?com_name=${encodeURIComponent(detection.com_name)}&days=30`
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
							<div className="detection-card__header-actions">
								<time className="detection-card__time" dateTime={detection.iso8601}>
									{detection.time}
								</time>
								<button
									className="detection-card__chart-btn"
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

			<SpeciesChartDialog
				isOpen={isChartActive}
				onClose={handleCloseChart}
				species={activeChartData}
			/>
		</>
	);
}
