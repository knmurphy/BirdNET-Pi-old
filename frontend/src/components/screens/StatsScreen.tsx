/**
 * Stats Screen
 * System health and activity charts
 */

import { useSystemHealth } from '../../hooks/useSystemHealth';
import './Screens.css';

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
					<div className="screen__stats-value">{Math.floor(systemHealth?.uptime_seconds ?? 0 / 3600)}h</div>
				</div>
			</div>
		</div>
	);
}
