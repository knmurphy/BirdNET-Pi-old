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
import { ImageModal } from './ImageModal';
import './DetectionCard.css';
import './ImageModal.css';

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
	/** Delete confirmation dialog state */
	isDeleteDialogOpen?: boolean;
	onOpenDeleteDialog?: () => void;
	onCloseDeleteDialog?: () => void;
	onDelete?: () => void;
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
	isDeleteDialogOpen,
	onOpenDeleteDialog,
	onCloseDeleteDialog,
	onDelete,
}: DetectionCardProps) {
	const { playing, toggle } = useAudio(detection.id, detection.file_name);
	const { data: image } = useSpeciesImage(detection.com_name);
	const [localChartData, setLocalChartData] = useState<SpeciesDetectionHistory | null>(null);
	const [isChartOpen, setIsChartOpen] = useState(false);
	const [localIsDeleteDialogOpen, setLocalIsDeleteDialogOpen] = useState(false);
	const [isImageModalOpen, setIsImageModalOpen] = useState(false);

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

	const handleOpenInNewTab = () => {
		const url = `/index.php?filename=${encodeURIComponent(detection.file_name)}`;
		window.open(url, '_blank');
	};

	const handleDeleteClick = (e: React.MouseEvent) => {
		e.stopPropagation();
		if (onOpenDeleteDialog) {
			onOpenDeleteDialog();
		} else {
			setLocalIsDeleteDialogOpen(true);
		}
	};

	const handleCloseChart = () => {
		if (onCloseChart) {
			onCloseChart();
		} else {
			setIsChartOpen(false);
		}
	};

	const handleCloseDeleteDialog = () => {
		if (onCloseDeleteDialog) {
			onCloseDeleteDialog();
		} else {
			setLocalIsDeleteDialogOpen(false);
		}
	};

	const handleDelete = async () => {
		if (onDelete) {
			onDelete();
		} else {
			try {
				const response = await fetch(`/api/detections/${detection.id}`, {
					method: 'DELETE',
				});

				if (response.ok) {
					handleCloseDeleteDialog();
				} else {
					console.error('Failed to delete detection');
				}
			} catch (error) {
				console.error('Error deleting detection:', error);
			}
		}
	};

	const activeChartData = chartData ?? localChartData;
	const isChartActive = chartData !== undefined ? chartData !== null : isChartOpen;
	const activeDeleteDialogOpen = isDeleteDialogOpen !== undefined ? isDeleteDialogOpen : localIsDeleteDialogOpen;

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
							onClick={() => setIsImageModalOpen(true)}
						/>
					)}
					<div className="detection-card__info">
						<div className="detection-card__header">
							<h3 className="detection-card__common-name">{detection.com_name}</h3>
							<div className="detection-card__header-actions">
								<time className="detection-card__time" dateTime={detection.iso8601}>
									{detection.time}
								</time>
								<div className="detection-card__actions">
									<button
										className="detection-card__action-btn"
										onClick={handleOpenInNewTab}
										aria-label="Open detection in new tab"
										title="Open in new tab"
									>
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
									<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
									<polyline points="15 3 21 3 21 9" />
									<line x1="10" y1="14" x2="21" y2="3" />
								</svg>
									</button>
									<button
										className="detection-card__action-btn"
										onClick={handleChartClick}
										aria-label="View species stats"
										title="View species stats"
									>
										<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
											<rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
											<path d="M3 18 L9 12 L15 14 L21 6" />
										</svg>
									</button>
									<button
										className="detection-card__action-btn detection-card__delete-btn"
										onClick={handleDeleteClick}
										aria-label="Delete detection"
										title="Delete detection"
									>
										<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
											<polyline points="3 6 5 6" />
											<line x1="21" y1="3" x2="21" y2="6" />
											<line x1="21" y1="3" x2="10" y2="8" />
											<circle cx="21" cy="20" r="3" />
										</svg>
									</button>
							</div>
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
							<a
								href={`https://allaboutbirds.org/guide/${detection.com_name.replace(/ /g, '_')}`}
								target="_blank"
								rel="noopener noreferrer"
								className="detection-card__ref-link"
								aria-label={`All About Birds page for ${detection.com_name}`}
								title="All About Birds"
							>
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
									<circle cx="12" cy="12" r="10" />
									<path d="M12 6v6M12 18v6M6 12h12" />
								</svg>
							</a>
							<a
								href={`https://en.wikipedia.org/wiki/${detection.sci_name.replace(/ /g, '_')}`}
								target="_blank"
								rel="noopener noreferrer"
								className="detection-card__ref-link"
								aria-label={`Wikipedia page for ${detection.sci_name}`}
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
				</div>
			</article>

			<SpeciesChartDialog
				isOpen={isChartActive}
				onClose={handleCloseChart}
				species={activeChartData}
			/>

			{activeDeleteDialogOpen && (
				<div className="delete-modal-overlay" onClick={handleCloseDeleteDialog}>
					<div className="delete-modal-content" onClick={(e) => e.stopPropagation()}>
						<button
							className="delete-modal__close"
							onClick={handleCloseDeleteDialog}
							aria-label="Close dialog"
						>
							X
						</button>
						<div className="delete-modal__body">
							<p className="delete-modal__message">Are you sure you want to delete this detection?</p>
							<p className="delete-modal__details">{detection.com_name} — {new Date(detection.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} at {detection.time}</p>
							<div className="delete-modal__actions">
								<button
									type="button"
									className="delete-modal__btn delete-modal__btn--cancel"
									onClick={handleCloseDeleteDialog}
								>
									Cancel
								</button>
								<button
									type="button"
									className="delete-modal__btn delete-modal__btn--confirm"
									onClick={handleDelete}
								>
									Delete
								</button>
							</div>
						</div>
					</div>
				</div>
			)}

			<ImageModal
				isOpen={isImageModalOpen}
				onClose={() => setIsImageModalOpen(false)}
				imageUrl={image?.image_url}
				altText={detection.com_name}
			/>
		</>
	);
}
