/**
 * Live Screen
 * Real-time detection feed powered by SSE
 */

import { useState, useEffect, useRef } from 'react';
import { useLiveDetections } from '../../hooks/useDetections';
import { DetectionCard } from '../DetectionCard';
import './Screens.css';

/** Maximum number of detections to render for performance */
const MAX_VISIBLE_DETECTIONS = 100;

/** Animation duration for new detection highlight (ms) */
const NEW_DETECTION_DURATION = 500;

/** Age thresholds for fading (in seconds) */
const AGE_THRESHOLD_MEDIUM = 60; // 1 minute
const AGE_THRESHOLD_OLD = 300; // 5 minutes

/**
 * Calculate age category for a detection based on its time
 */
function getAgeCategory(detectionTime: string): 'recent' | 'medium' | 'old' {
	try {
		const detectionDate = new Date(detectionTime);
		const now = new Date();
		const ageSeconds = (now.getTime() - detectionDate.getTime()) / 1000;
		
		if (ageSeconds >= AGE_THRESHOLD_OLD) return 'old';
		if (ageSeconds >= AGE_THRESHOLD_MEDIUM) return 'medium';
		return 'recent';
	} catch {
		return 'recent';
	}
}

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
			<div className="screen__icon" aria-hidden>
				<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
					<path d="M12 2a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3Z" />
					<path d="M19 10v2a7 7 0 0 1-14 0v-2" />
					<line x1="12" y1="19" x2="12" y2="22" />
					<line x1="8" y1="22" x2="16" y2="22" />
				</svg>
			</div>
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
			<div className="screen__icon" style={{ color: 'var(--red)' }} aria-hidden>
				<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
					<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
					<path d="M12 9v4" />
					<path d="M12 17h.01" />
				</svg>
			</div>
			<h2 className="screen__title">Failed to load detections</h2>
			<p className="screen__hint">{message}</p>
		</div>
	);
}

export function LiveScreen() {
	const { detections, isLoading, isError, error } = useLiveDetections();
	const [newDetectionIds, setNewDetectionIds] = useState<Set<number>>(new Set());
	const [tick, setTick] = useState(0);
	const seenIdsRef = useRef<Set<number>>(new Set());

	const mostRecentDetections = detections.slice(0, 4);

	// Recalculate age categories every 60s so dimming updates without re-render
	useEffect(() => {
		const id = setInterval(() => setTick((t) => t + 1), 60_000);
		return () => clearInterval(id);
	}, []);

	// Track new detections for animation
	useEffect(() => {
		if (detections.length === 0) return;

		const timeouts: ReturnType<typeof setTimeout>[] = [];
		const latestId = detections[0]?.id;

		if (latestId !== undefined && !seenIdsRef.current.has(latestId)) {
			seenIdsRef.current.add(latestId);
			setTimeout(() => {
				setNewDetectionIds((prev) => new Set([...prev, latestId]));
			}, 0);

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

	// Activity excludes top 4 (shown in Most Recent); limit for performance
	const activityDetections = detections.slice(4, 4 + MAX_VISIBLE_DETECTIONS);

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
		<div className="screen screen--live" data-age-tick={tick}>
			{/* Today Header */}
			<div className="live-header">
				<h1 className="live-header__title">Today</h1>
				<p className="live-header__date">{new Date().toLocaleDateString()}</p>
			</div>

			{/* Most Recent Section */}
			{mostRecentDetections.length > 0 && (
				<section className="live-recent">
					<h2 className="live-recent__title">Most Recent</h2>
					<div className="live-recent__list">
						{mostRecentDetections.map((detection) => (
							<DetectionCard
								key={detection.id}
								detection={detection}
								isNew={newDetectionIds.has(detection.id)}
								ageCategory={getAgeCategory(detection.iso8601)}
							/>
						))}
					</div>
				</section>
			)}

			{/* Today's Activity */}
			<section className="live-activity">
				<h2 className="live-activity__title">Activity</h2>
				<div className="live-feed" role="feed" aria-label="Live detection feed">
					{activityDetections.map((detection) => (
						<DetectionCard
							key={detection.id}
							detection={detection}
							isNew={newDetectionIds.has(detection.id)}
							ageCategory={getAgeCategory(detection.iso8601)}
						/>
					))}
				</div>

				{/* Show count indicator if more detections exist beyond Most Recent + visible */}
				{detections.length > 4 + MAX_VISIBLE_DETECTIONS && (
					<div className="live-feed__overflow">
						+{detections.length - 4 - MAX_VISIBLE_DETECTIONS} more today
					</div>
				)}
			</section>
		</div>
	);
}
