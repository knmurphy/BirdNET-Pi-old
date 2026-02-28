/**
 * TabBar Component
 * Fixed bottom navigation with 3 tabs
 *
 * NOTE: Do NOT use emoji as icons in this project.
 * Use SVG icons for consistent, accessible, and professional appearance.
 */

import { NavLink } from 'react-router-dom';
import './TabBar.css';

interface TabConfig {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const tabs: TabConfig[] = [
  {
    path: '/',
    label: 'Live',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <circle cx="12" cy="12" r="3" fill="currentColor" />
      </svg>
    ),
  },
  {
    path: '/species',
    label: 'Species',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    ),
  },
  {
    path: '/info',
    label: 'Info',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="16" x2="12" y2="12" />
        <line x1="12" y1="8" x2="12.01" y2="8" />
      </svg>
    ),
  },
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
