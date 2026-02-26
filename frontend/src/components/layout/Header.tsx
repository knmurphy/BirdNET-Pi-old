/**
 * Header Component
 * Sticky header with station name, time, and connection status
 */

import { useState, useEffect } from 'react';
import { useSSEContext } from '../../contexts/SSEContext';
import './Header.css';

interface HeaderProps {
  stationName?: string;
}

export function Header({ stationName = 'Field Station' }: HeaderProps) {
  const { connectionStatus } = useSSEContext();
  const [currentTime, setCurrentTime] = useState(() => formatTime(new Date()));

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(formatTime(new Date()));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <header className="header">
      <div className="header-station">
        <span className="station-name">{stationName}</span>
      </div>
      <div className="header-right">
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
