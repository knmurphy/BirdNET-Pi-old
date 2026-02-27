import { useQuery } from '@tanstack/react-query';
import type { SystemResponse, SettingsResponse } from '../../types';
import './Screens.css';

/**
 * Info Screen
 *
 * Displays system health information and station settings.
 * Combines the functionality of the old System and Settings screens.
 * System health includes: CPU, temperature (C+F), memory, disk, uptime, classifiers, SSE
 * Settings include: location map, coordinates, classifier config, storage path
 */

async function fetchSystem(): Promise<SystemResponse> {
  const response = await fetch('/api/system');
  if (!response.ok) throw new Error('Failed to fetch system info');
  return response.json();
}

async function fetchSettings(): Promise<SettingsResponse> {
  const response = await fetch('/api/settings');
  if (!response.ok) throw new Error('Failed to fetch settings');
  return response.json();
}

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

function getMapImageUrl(lat: number, lon: number): string {
  const zoom = 12;
  const size = '400x200';
  return `https://staticmap.marker.tech/?center=${lat},${lon}&zoom=${zoom}&size=${size}&markers=${lat},${lon},red-pushpin`;
}

export function InfoScreen() {
  const { data: system, isLoading: loadingSystem, isError: isSystemError, error: systemError, refetch: refetchSystem } = useQuery({
    queryKey: ['system'],
    queryFn: fetchSystem,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: settings, isLoading: loadingSettings, isError: isSettingsError, error: settingsError, refetch: refetchSettings } = useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
    staleTime: 60_000,
  });

  const isLoading = loadingSystem || loadingSettings;
  const isError = isSystemError || isSettingsError;

  return (
    <div className="screen screen--info">
      {isError && (
        <div className="screen__error">
          <p className="screen__error-message">
            {isSystemError ? `Error loading system info: ${systemError?.message || 'Unknown error'}` : null}
            {isSettingsError ? `Error loading settings: ${settingsError?.message || 'Unknown error'}` : null}
          </p>
          <div className="screen__error-actions">
            {isSystemError && (
              <button onClick={() => refetchSystem()} className="button button--primary">
                Retry System
              </button>
            )}
            {isSettingsError && (
              <button onClick={() => refetchSettings()} className="button button--primary">
                Retry Settings
              </button>
            )}
          </div>
        </div>
      )}
      
      {isLoading && !isError && (
        <div className="info-grid">
          <div className="info-item info-item--skeleton">
            <span className="info-item__label"></span>
            <span className="info-item__value"></span>
          </div>
          <div className="info-item info-item--skeleton">
            <span className="info-item__label"></span>
            <span className="info-item__value"></span>
          </div>
          <div className="info-item info-item--skeleton">
            <span className="info-item__label"></span>
            <span className="info-item__value"></span>
          </div>
          <div className="info-item info-item--skeleton">
            <span className="info-item__label"></span>
            <span className="info-item__value"></span>
          </div>
          <div className="info-item info-item--skeleton">
            <span className="info-item__label"></span>
            <span className="info-item__value"></span>
          </div>
          <div className="info-item info-item--skeleton">
            <span className="info-item__label"></span>
            <span className="info-item__value"></span>
          </div>
          <div className="info-item info-item--skeleton">
            <span className="info-item__label"></span>
            <span className="info-item__value"></span>
          </div>
        </div>
      )}
      
      {!isLoading && !isError && system && settings && (
        <>
          {/* System Health Section */}
          <section className="info-section">
            <h2 className="info-section__title">System Health</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-item__label">CPU</span>
                <span className="info-item__value">{system.cpu_percent.toFixed(1)}%</span>
              </div>
              <div className="info-item">
                <span className="info-item__label">Temperature</span>
                <span className="info-item__value">
                  {system.temperature_celsius.toFixed(1)}°C / {system.temperature_fahrenheit.toFixed(1)}°F
                </span>
              </div>
              <div className="info-item">
                <span className="info-item__label">Memory</span>
                <span className="info-item__value">{system.memory_percent.toFixed(1)}%</span>
              </div>
              <div className="info-item">
                <span className="info-item__label">Disk</span>
                <span className="info-item__value">
                  {system.disk_used_gb.toFixed(1)}/{system.disk_total_gb.toFixed(1)} GB
                </span>
              </div>
              <div className="info-item">
                <span className="info-item__label">Uptime</span>
                <span className="info-item__value">{formatUptime(system.uptime_seconds)}</span>
              </div>
              <div className="info-item">
                <span className="info-item__label">Active Classifiers</span>
                <span className="info-item__value">{system.active_classifiers.join(', ')}</span>
              </div>
              <div className="info-item">
                <span className="info-item__label">SSE Subscribers</span>
                <span className="info-item__value">{system.sse_subscribers}</span>
              </div>
            </div>
          </section>
          
          {/* Settings Section */}
          <section className="info-section">
            <h2 className="info-section__title">Station Settings</h2>
            <div className="settings-map">
              <img
                src={getMapImageUrl(settings.latitude, settings.longitude)}
                alt="Station location map"
                className="settings-map__image"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            </div>
            <div className="settings-coords">
              <span>{settings.latitude.toFixed(4)}°N, {settings.longitude.toFixed(4)}°W</span>
            </div>
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
              <div className="settings-item settings-item--full">
                <span className="settings-item__label">Audio Path</span>
                <span className="settings-item__value settings-item__value--mono">{settings.audio_path}</span>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
