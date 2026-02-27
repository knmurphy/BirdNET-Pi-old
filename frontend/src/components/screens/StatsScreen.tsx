/**
 * Stats Screen
 * System health and activity charts
 */

import { useSystemHealth } from '../../hooks/useSystemHealth';
import './Screens.css';

/**
 * Format uptime seconds into human-readable string
 */
function formatUptime(seconds: number): string {
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	
	if (hours >= 24) {
		const days = Math.floor(hours / 24);
		const remainingHours = hours % 24;
		return `${days}d ${remainingHours}h`;
	}
	
	if (hours > 0) {
		return `${hours}h ${minutes}m`;
	}
	
	return `${minutes}m`;
}

export function StatsScreen() {
	const { data: systemHealth } = useSystemHealth();

	return (
		<div className="screen screen--stats">
			<div className="screen__icon">∿</div>
			<h2 className="screen__title">System Health</h2>
			<div className="screen__stats-grid">
				<div className="screen__stats-item">
					<div className="screen__stats-label">CPU</div>
					<div className="screen__stats-value">{systemHealth?.cpu_percent?.toFixed(1) ?? '0'}%</div>
				</div>
				<div className="screen__stats-item">
					<div className="screen__stats-label">Temp</div>
					<div className="screen__stats-value">{systemHealth?.temperature_celsius?.toFixed(1) ?? '0'}°C</div>
				</div>
				<div className="screen__stats-item">
					<div className="screen__stats-label">Disk</div>
					<div className="screen__stats-value">{systemHealth?.disk_used_gb?.toFixed(1)}/{systemHealth?.disk_total_gb?.toFixed(1)} GB</div>
				</div>
				<div className="screen__stats-item">
					<div className="screen__stats-label">Uptime</div>
					<div className="screen__stats-value">{formatUptime(systemHealth?.uptime_seconds ?? 0)}</div>
				</div>
			</div>
		</div>
	);
}
