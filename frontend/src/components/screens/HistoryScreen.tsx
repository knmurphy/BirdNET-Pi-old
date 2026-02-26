/**
 * History Screen
 * Detection log with date navigation (placeholder)
 */

import './Screens.css';

export function HistoryScreen() {
  return (
    <div className="screen screen--history">
      <div className="screen__placeholder">
        <div className="screen__icon">≡</div>
        <h2 className="screen__title">History</h2>
        <p className="screen__text">History coming soon</p>
        <p className="screen__hint">
          Browse past detections with date filters
        </p>
      </div>
    </div>
  );
}
