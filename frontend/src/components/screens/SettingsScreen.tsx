/**
 * Settings Screen
 * Station configuration and location
 */

import { useQuery } from '@tanstack/react-query';
import type { SettingsResponse } from '../../types';
import './Screens.css';

async function fetchSettings(): Promise<SettingsResponse> {
	const response = await fetch('/api/settings');
	if (!response.ok) throw new Error('Failed to fetch settings');
	return response.json();
}

/**
 * Generate OpenStreetMap static image URL (free, no API key required)
 */
function getMapImageUrl(lat: number, lon: number): string {
	// Using OpenStreetMap static tiles via staticmap.marker.tech (free service)
	// Or fallback to a simple OSM embed
	const zoom = 12;
	const size = '400x200';
	return `https://staticmap.marker.tech/?center=${lat},${lon}&zoom=${zoom}&size=${size}&markers=${lat},${lon},red-pushpin`;
}

export function SettingsScreen() {
	const { data: settings, isLoading, isError } = useQuery({
		queryKey: ['settings'],
		queryFn: fetchSettings,
		staleTime: 60_000, // 1 minute
	});

	return (
		<div className="screen screen--settings">
			<h2 className="screen__title">Station Settings</h2>
			
			{isLoading && <p className="screen__hint">Loading settings...</p>}
			
			{isError && (
				<div className="screen__placeholder">
					<p className="screen__text">Failed to load settings</p>
				</div>
			)}
			
			{settings && (
				<div className="settings-content">
					{/* Location Map */}
					<section className="settings-section">
						<h3 className="settings-section__title">Location</h3>
						<div className="settings-map">
							<img 
								src={getMapImageUrl(settings.latitude, settings.longitude)}
								alt="Station location map"
								className="settings-map__image"
								onError={(e) => {
									// Fallback to OSM link if static map fails
									(e.target as HTMLImageElement).style.display = 'none';
								}}
							/>
						</div>
						<div className="settings-coords">
							<span>{settings.latitude.toFixed(4)}°N, {settings.longitude.toFixed(4)}°W</span>
						</div>
					</section>
					
					{/* Classifier Settings */}
					<section className="settings-section">
						<h3 className="settings-section__title">Classifier Settings</h3>
						<div className="settings-grid">
							<div className="settings-item">
								<span className="settings-item__label">Confidence Threshold</span>
								<span className="settings-item__value">{(settings.confidence_threshold * 100).toFixed(2)}%</span>
							</div>
							<div className="settings-item">
								<span className="settings-item__label">Overlap</span>
								<span className="settings-item__value">{settings.overlap}s</span>
							</div>
							<div className="settings-item">
								<span className="settings-item__label">Sensitivity</span>
								<span className="settings-item__value">{settings.sensitivity}</span>
							</div>
							<div className="settings-item">
								<span className="settings-item__label">Week</span>
								<span className="settings-item__value">{settings.week === -1 ? 'Auto' : settings.week}</span>
							</div>
						</div>
					</section>
					
					{/* Audio Path */}
					<section className="settings-section">
						<h3 className="settings-section__title">Storage</h3>
						<div className="settings-item settings-item--full">
							<span className="settings-item__label">Audio Path</span>
							<span className="settings-item__value settings-item__value--mono">{settings.audio_path}</span>
						</div>
					</section>
				</div>
			)}
		</div>
	);
}
