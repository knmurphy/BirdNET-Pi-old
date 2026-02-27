/**
 * TabBar Component
 * Fixed bottom navigation with 5 tabs
 */

import { NavLink } from 'react-router-dom';
import './TabBar.css';

interface TabConfig {
  path: string;
  label: string;
  icon: string;
}

const tabs: TabConfig[] = [
  { path: '/', label: 'Live', icon: '◉' },
  { path: '/species', label: 'Species', icon: '☰' },
  { path: '/species-stats', label: 'Species Stats', icon: '📊' },
  { path: '/history', label: 'History', icon: '≡' },
  { path: '/stats', label: 'System', icon: '∿' },
  { path: '/settings', label: 'Settings', icon: '⚙' },
];

export function TabBar() {
  return (
    <nav className="tab-bar" role="navigation" aria-label="Main navigation">
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }) =>
            `tab-bar__item ${isActive ? 'tab-bar__item--active' : ''}`
          }
        >
          <span className="tab-bar__icon" aria-hidden="true">{tab.icon}</span>
          <span className="tab-bar__label">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
