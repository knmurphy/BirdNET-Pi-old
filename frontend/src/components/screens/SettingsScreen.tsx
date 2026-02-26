/**
 * Settings Screen
 * Station configuration (placeholder)
 */

import './Screens.css';

export function SettingsScreen() {
  return (
    <div className="screen screen--settings">
      <div className="screen__placeholder">
        <div className="screen__icon">⚙</div>
        <h2 className="screen__title">Settings</h2>
        <p className="screen__text">Settings coming soon</p>
        <p className="screen__hint">
          Configure station, classifiers, and thresholds
        </p>
      </div>
    </div>
  );
}
