/**
 * Live Screen
 * Real-time detection feed powered by SSE
 */

import { useState, useEffect } from 'react';
import { useLiveDetections } from '../../hooks/useDetections';
import { useTodaySummary } from '../../hooks/useTodaySummary';
import { DetectionCard } from '../DetectionCard';
import './Screens.css';

/** Maximum number of detections to render for performance */
const MAX_VISIBLE_DETECTIONS = 100;

/** Animation duration for new detection highlight (ms) */
const NEW_DETECTION_DURATION = 500;

/**
 * Loading skeleton cards
 */
function DetectionSkeleton({ count = 3 }: { count?: number }) {
	return (
		<>
			{Array.from({ length: count }).map((_, i) => (
				<div key={i} className="detection-card detection-card--skeleton">
					<div className="detection-card__header">
						<div className="detection-card__common-name" />
						<time className="detection-card__time">00:00:00</time>
					</div>
					<p className="detection-card__scientific-name">&nbsp;</p>
					<div className="detection-card__confidence">
						<div className="detection-card__confidence-bar" />
						<span className="detection-card__confidence-value">0%</span>
					</div>
					<div className="detection-card__footer">
						<span className="detection-card__classifier">
							<span className="detection-card__classifier-dot" />
							<span className="detection-card__classifier-name">Loading</span>
						</span>
					</div>
				</div>
			))}
		</>
	);
}

/**
 * Empty state when no detections
 */
function EmptyState() {
	return (
		<div className="screen__placeholder">
			<div className="screen__icon">◉</div>
			<h2 className="screen__title">No detections yet today</h2>
			<p className="screen__hint">
				Detections will appear here in real-time as they're classified
			</p>
		</div>
	);
}

/**
 * Error state
 */
function ErrorState({ message }: { message: string }) {
	return (
		<div className="screen__placeholder">
			<div className="screen__icon" style={{ color: 'var(--red)' }}>⚠</div>
			<h2 className="screen__title">Failed to load detections</h2>
			<p className="screen__hint">{message}</p>
		</div>
	);
}

export function LiveScreen() {
	const { detections, isLoading, isError, error } = useLiveDetections();
	const [newDetectionIds, setNewDetectionIds] = useState<Set<number>>(new Set());


	const { data: summary } = useTodaySummary();

	// Track new detections for animation
	// When a detection arrives, mark it as "new" for a short period
	useEffect(() => {
		if (detections.length === 0) return;

		// Clear any existing timeouts
		const timeouts: ReturnType<typeof setTimeout>[] = [];

		// Mark the first detection as new (it's the most recent)
		const latestId = detections[0]?.id;
		if (latestId !== undefined && !newDetectionIds.has(latestId)) {
			setNewDetectionIds((prev) => new Set([...prev, latestId]));

			// Clear after animation duration
			const timeout = setTimeout(() => {
				setNewDetectionIds((prev) => {
					const next = new Set(prev);
					next.delete(latestId);
					return next;
				});
			}, NEW_DETECTION_DURATION);

			timeouts.push(timeout);
		}

		return () => {
			timeouts.forEach(clearTimeout);
		};
	}, [detections]);

	// Limit rendered detections for performance
	const visibleDetections = detections.slice(0, MAX_VISIBLE_DETECTIONS);

	// Loading state - show skeletons
	if (isLoading && detections.length === 0) {
		return (
			<div className="screen screen--live">
				<div className="live-feed">
					<DetectionSkeleton count={5} />
				</div>
			</div>
		);
	}

	// Error state
	if (isError) {
		return (
			<div className="screen screen--live">
				<ErrorState message={error?.message ?? 'Check your connection and try again'} />
			</div>
		);
	}

	// Empty state
	if (detections.length === 0) {
		return (
			<div className="screen screen--live">
				<EmptyState />
			</div>
		);
	}

	return (
		<div className="screen screen--live">
		{/* Header with summary stats */}
		<div className="live-feed__header">
			<div className="live-feed__summary">
				<div className="live-feed__summary-item">
					<div className="live-feed__summary-value">{summary?.total_detections ?? 0}</div>
					<div className="live-feed__summary-label">Detections</div>
				</div>
				<div className="live-feed__summary-item">
					<div className="live-feed__summary-value">{summary?.species_count ?? 0}</div>
					<div className="live-feed__summary-label">Species</div>
				</div>
			</div>
		</div>

			<div className="live-feed" role="feed" aria-label="Live detection feed">
				{visibleDetections.map((detection) => (
					<DetectionCard
						key={detection.id}
						detection={detection}
						isNew={newDetectionIds.has(detection.id)}
						onClick={() => {
							// TODO: Audio playback (Phase 2)
							console.log('Audio playback not yet implemented:', detection.file_name);
						}}
					/>
				))}
			</div>

			{/* Show count indicator if we have more detections than shown */}
			{detections.length > MAX_VISIBLE_DETECTIONS && (
				<div className="live-feed__overflow">
					+{detections.length - MAX_VISIBLE_DETECTIONS} more today
				</div>
			)}
		</div>
	);
}
