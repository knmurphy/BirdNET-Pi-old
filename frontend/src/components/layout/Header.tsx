/**
 * Header Component
 * Sticky header with station name, city, weather, time, and connection status
 */

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSSEContext } from '../../contexts/SSEContext';
import type { LocationWeatherResponse } from '../../types';
import './Header.css';

async function fetchLocationWeather(): Promise<LocationWeatherResponse> {
  const response = await fetch('/api/location-weather');
  if (!response.ok) throw new Error('Failed to fetch location/weather');
  return response.json();
}

interface HeaderProps {
  stationName?: string;
}

export function Header({ stationName = 'Field Station' }: HeaderProps) {
  const { connectionStatus } = useSSEContext();
  const [currentTime, setCurrentTime] = useState(() => formatTime(new Date()));

  const { data: locationWeather } = useQuery({
    queryKey: ['location-weather'],
    queryFn: fetchLocationWeather,
    staleTime: 10 * 60_000, // 10 min
    refetchInterval: 15 * 60_000, // refresh every 15 min
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(formatTime(new Date()));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const showLocation = locationWeather && locationWeather.city !== 'Unknown' && (locationWeather.latitude !== 0 || locationWeather.longitude !== 0);
  const cityStr = showLocation ? locationWeather.city : null;
  const weatherStr = showLocation
    ? `${Math.round(locationWeather.temp_c)}°C ${locationWeather.condition}`
    : null;

  return (
    <header className="header">
      <div className="header-station">
        <span className="station-name">{stationName}</span>
      </div>
      <div className="header-right">
        {cityStr && (
          <span className="header-meta header-location" title="Station location">
            {cityStr}
          </span>
        )}
        {weatherStr && (
          <span className="header-meta header-weather" title="Current weather">
            {weatherStr}
          </span>
        )}
        <span className="header-time">{currentTime}</span>
        <ConnectionIndicator status={connectionStatus} />
      </div>
    </header>
  );
}

function ConnectionIndicator({ status }: { status: string }) {
  return (
    <div className="connection-indicator" aria-label={`Connection: ${status}`}>
      <span className={`connection-dot connection-dot--${status}`} />
    </div>
  );
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}
