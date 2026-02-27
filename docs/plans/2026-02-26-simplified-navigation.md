# Simplified Navigation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Simplify navigation from 6 tabs to 3 (Live, Info, Species) while enhancing functionality with better system stats, new species badges, and comprehensive species tracking with charts.

**Architecture:**
- Backend: Add memory usage to system health API
- Frontend: Consolidate tabs by merging System+Settings into Info page, and History+SpeciesStats into Species page
- Live page: Add "Most Recent" section with subtle border for top 3-4 non-redundant detections
- Species page: Add filtering, sorting, and Chart.js visualizations
- All temperature displays: Show both Celsius and Fahrenheit

**Tech Stack:**
- Backend: FastAPI, psutil, SQLite
- Frontend: React 19, TypeScript, TanStack Query, Chart.js 4.5.1, React Router DOM 7
- Testing: pytest (backend), TBD (frontend)

---

## Task 1: Add Memory Usage to Backend System API

**Files:**
- Modify: `api/models/system.py`
- Modify: `api/services/system_info.py`
- Modify: `api/routers/system.py`
- Test: `api/tests/test_api.py` (or create new test file)

**Step 1: Add memory_percent to SystemResponse model**

Open: `api/models/system.py`
Add field after temperature_celsius:

```python
class SystemResponse(BaseModel):
    cpu_percent: float
    temperature_celsius: float
    temperature_fahrenheit: float  # NEW
    memory_percent: float  # NEW
    disk_used_gb: float
    disk_total_gb: float
    uptime_seconds: float
    active_classifiers: list[str]
    sse_subscribers: int
    generated_at: str
```

**Step 2: Add get_memory_percent function to system_info.py**

Open: `api/services/system_info.py`
Add this function at the end (after get_memory_percent which already exists at line 69):

```python
def get_memory_percent() -> float:
    """Get memory usage percentage.

    Returns:
        Memory usage as percentage (0-100).
    """
    return psutil.virtual_memory().percent
```

**Step 3: Convert Celsius to Fahrenheit helper**

Add this function to system_info.py:

```python
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit.

    Args:
        celsius: Temperature in Celsius.

    Returns:
        Temperature in Fahrenheit.
    """
    return (celsius * 9/5) + 32
```

**Step 4: Update system router to include memory and Fahrenheit**

Open: `api/routers/system.py`
Update the get_system function (around line 22-49):

```python
@router.get("/system", response_model=SystemResponse)
async def get_system():
    """Get system status including CPU, temperature, disk, and uptime."""
    # CPU (non-blocking quick read)
    cpu = get_cpu_percent(interval=0.1)

    # Temperature (Pi-specific)
    temp_c = get_temperature()
    temp_f = celsius_to_fahrenheit(temp_c)

    # Memory (NEW)
    memory = get_memory_percent()

    # Disk usage
    disk = get_disk_usage("/")

    # Uptime
    uptime = get_uptime()

    # TODO: Get actual active classifiers from config
    active_classifiers = ["birdnet"]

    return SystemResponse(
        cpu_percent=cpu,
        temperature_celsius=temp_c,
        temperature_fahrenheit=temp_f,  # NEW
        memory_percent=memory,  # NEW
        disk_used_gb=disk.used_gb,
        disk_total_gb=disk.total_gb,
        uptime_seconds=uptime,
        active_classifiers=active_classifiers,
        sse_subscribers=event_bus.subscriber_count,
        generated_at=datetime.now().isoformat(),
    )
```

Add import at top of file:

```python
from api.services.system_info import (
    get_cpu_percent,
    get_temperature,
    celsius_to_fahrenheit,  # NEW
    get_disk_usage,
    get_uptime,
    get_memory_percent,  # NEW
)
```

**Step 5: Test the system endpoint**

Run: `python -m uvicorn api.main:app --reload` (from project root)

Then in separate terminal:

```bash
curl http://localhost:8000/api/system
```

Expected: JSON response includes `temperature_fahrenheit` and `memory_percent` fields.

**Step 6: Commit**

```bash
git add api/models/system.py api/services/system_info.py api/routers/system.py
git commit -m "feat: add memory usage and Fahrenheit to system API"
```

---

## Task 2: Update Frontend Types for System Response

**Files:**
- Modify: `frontend/src/types/index.ts`

**Step 1: Add new fields to SystemResponse**

Open: `frontend/src/types/index.ts`
Find SystemResponse interface (around line 139) and update:

```typescript
export interface SystemResponse {
  cpu_percent: number;
  temperature_celsius: number;
  temperature_fahrenheit: number;  // NEW
  memory_percent: number;  // NEW
  disk_used_gb: number;
  disk_total_gb: number;
  uptime_seconds: float;
  active_classifiers: string[]; // Classifier IDs
  sse_subscribers: number;
  generated_at: string;
}
```

**Step 2: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: update SystemResponse type for memory and Fahrenheit"
```

---

## Task 3: Update TabBar to 3 Tabs

**Files:**
- Modify: `frontend/src/components/layout/TabBar.tsx`

**Step 1: Update tabs array**

Open: `frontend/src/components/layout/TabBar.tsx`
Replace tabs array (lines 18-80) with:

```typescript
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
];
```

**Step 2: Commit**

```bash
git add frontend/src/components/layout/TabBar.tsx
git commit -m "feat: reduce tabs to 3 (Live, Info, Species)"
```

---

## Task 4: Update App.tsx Routes

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: Update imports and routes**

Open: `frontend/src/App.tsx`
Update imports (remove old screens, keep Live):

```typescript
import { LiveScreen } from './components/screens/LiveScreen';
import { InfoScreen } from './components/screens/InfoScreen';
import { SpeciesScreen } from './components/screens/SpeciesScreen';
```

Update Routes section (lines 45-52):

```typescript
<Routes>
  <Route path="/" element={<LiveScreen />} />
  <Route path="/info" element={<InfoScreen />} />
  <Route path="/species" element={<SpeciesScreen />} />
</Routes>
```

**Step 2: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: update routes for 3-tab navigation"
```

---

## Task 5: Create InfoScreen Component

**Files:**
- Create: `frontend/src/components/screens/InfoScreen.tsx`
- Create: `frontend/src/components/screens/InfoScreen.css`

**Step 1: Create InfoScreen.tsx**

Create new file `frontend/src/components/screens/InfoScreen.tsx`:

```typescript
import { useQuery } from '@tanstack/react-query';
import type { SystemResponse, SettingsResponse } from '../../types';
import './Screens.css';

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
  const { data: system, isLoading: loadingSystem } = useQuery({
    queryKey: ['system'],
    queryFn: fetchSystem,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: settings, isLoading: loadingSettings } = useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
    staleTime: 60_000,
  });

  const isLoading = loadingSystem || loadingSettings;

  return (
    <div className="screen screen--info">
      {isLoading && <p className="screen__hint">Loading system info...</p>}

      {!isLoading && system && settings && (
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
```

**Step 2: Add InfoScreen styles**

Append to `frontend/src/components/screens/Screens.css`:

```css
.screen--info {
  padding: 1rem;
}

.info-section {
  margin-bottom: 2rem;
}

.info-section__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  padding: 1rem;
  background: var(--color-surface-secondary);
  border-radius: 8px;
}

.info-item__label {
  display: block;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.info-item__value {
  display: block;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/screens/InfoScreen.tsx frontend/src/components/screens/Screens.css
git commit -m "feat: create InfoScreen combining System and Settings"
```

---

## Task 6: Update LiveScreen with "Most Recent" Section

**Files:**
- Modify: `frontend/src/components/screens/LiveScreen.tsx`
- Modify: `frontend/src/components/screens/LiveScreen.css` (or create if doesn't exist)

**Step 1: Add "Today" header and "Most Recent" section**

Open: `frontend/src/components/screens/LiveScreen.tsx`
Update to include header and most recent section at top:

```typescript
// Add at top of component function
const [mostRecentDetections, setMostRecentDetections] = useState<Detection[]>([]);

// Update useEffect or add new one to filter recent detections
useEffect(() => {
  if (data?.detections && data.detections.length > 0) {
    // Filter for non-redundant (top 3-4 unique species or time-separated)
    const recent = data.detections.slice(0, 4);
    setMostRecentDetections(recent);
  }
}, [data?.detections]);

// Update JSX return to add sections
return (
  <div className="screen screen--live">
    {/* Today Header */}
    <div className="live-header">
      <h1 className="live-header__title">Today</h1>
      <p className="live-header__date">{new Date().toLocaleDateString()}</p>
    </div>

    {/* Most Recent Section */}
    {mostRecentDetections.length > 0 && (
      <section className="live-recent">
        <h2 className="live-recent__title">Most Recent</h2>
        <div className="live-recent__list">
          {mostRecentDetections.map((detection) => (
            <DetectionCard key={detection.id} detection={detection} compact />
          ))}
        </div>
      </section>
    )}

    {/* Today's Activity - existing detection list */}
    <section className="live-activity">
      <h2 className="live-activity__title">Activity</h2>
      {/* Existing detection list code */}
    </section>
  </div>
);
```

**Step 2: Add styles for Most Recent section**

Append to LiveScreen.css or create new file:

```css
.live-header {
  padding: 1rem 0;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.live-header__title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.live-header__date {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0.25rem 0 0 0;
}

.live-recent {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 2px solid var(--color-border-subtle);
  border-radius: 12px;
  background: var(--color-surface-secondary);
}

.live-recent__title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 1rem 0;
}

.live-recent__list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.live-activity__title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 1rem 0;
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/screens/LiveScreen.tsx frontend/src/components/screens/LiveScreen.css
git commit -m "feat: add Today header and Most Recent section to LiveScreen"
```

---

## Task 7: Update SpeciesScreen with "New" Badge

**Files:**
- Modify: `frontend/src/components/screens/SpeciesScreen.tsx`
- Modify: `frontend/src/components/screens/SpeciesStatsScreen.tsx` (will be removed later)

**Step 1: Add "New" badge to species rows**

Open: `frontend/src/components/screens/SpeciesScreen.tsx`
Find where species are rendered and add badge:

In SpeciesRow component or in SpeciesScreen, add:

```typescript
{species.is_new && (
  <span className="species-badge species-badge--new">New</span>
)}
```

Add styles:

```css
.species-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 4px;
  margin-left: 0.5rem;
}

.species-badge--new {
  background: var(--color-accent-primary);
  color: white;
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/screens/SpeciesScreen.tsx frontend/src/components/screens/Screens.css
git commit -m "feat: add 'New' badge to species detections"
```

---

## Task 8: Create Enhanced SpeciesScreen with Filters and Charts

**Files:**
- Modify: `frontend/src/components/screens/SpeciesScreen.tsx` (major refactor)
- Create: `frontend/src/components/charts/DetectionChart.tsx`

**Step 1: Install react-chartjs-2 if not present**

Check if installed:

```bash
cd frontend
npm list react-chartjs-2
```

If not present:

```bash
npm install react-chartjs-2
```

**Step 2: Create DetectionChart component**

Create `frontend/src/components/charts/DetectionChart.tsx`:

```typescript
import { useRef, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import './DetectionChart.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

interface DetectionChartProps {
  type: 'line' | 'bar';
  labels: string[];
  data: number[];
  label: string;
  color?: string;
}

export function DetectionChart({ type, labels, data, label, color = '#3b82f6' }: DetectionChartProps) {
  const chartData = {
    labels,
    datasets: [
      {
        label,
        data,
        borderColor: color,
        backgroundColor: color + '20',
        borderWidth: 2,
        fill: true,
        tension: 0.3,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14 },
        bodyFont: { size: 12 },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxTicksLimit: 10,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
  };

  return (
    <div className="detection-chart">
      {type === 'line' ? (
        <Line data={chartData} options={options} />
      ) : (
        <Bar data={chartData} options={options} />
      )}
    </div>
  );
}
```

**Step 3: Create chart styles**

Create `frontend/src/components/charts/DetectionChart.css`:

```css
.detection-chart {
  width: 100%;
  height: 300px;
  margin: 1rem 0;
}
```

**Step 4: Refactor SpeciesScreen with filters and charts**

This is a major refactor. Create comprehensive SpeciesScreen with:

- Filter controls (date range, species, confidence, classifier)
- Preset filters (Last 7 days, This month, High confidence)
- Sortable detection list
- Chart visualizations (daily counts, hourly patterns)

Open: `frontend/src/components/screens/SpeciesScreen.tsx`

Replace entire content with enhanced version including filters, sorting, and charts integration.

Note: This will be a substantial refactor. Key features to add:
1. Filter state (date range, species, min confidence, classifier)
2. Preset filter buttons
3. Sort options (date, species, confidence)
4. DetectionChart components for visualizations
5. Filtered/sorted detection list

**Step 5: Commit**

```bash
git add frontend/src/components/screens/SpeciesScreen.tsx frontend/src/components/charts/
git commit -m "feat: enhance SpeciesScreen with filters, sorting, and charts"
```

---

## Task 9: Remove Unused Screen Files

**Files:**
- Delete: `frontend/src/components/screens/SettingsScreen.tsx`
- Delete: `frontend/src/components/screens/StatsScreen.tsx`
- Delete: `frontend/src/components/screens/HistoryScreen.tsx`
- Delete: `frontend/src/components/screens/SpeciesStatsScreen.tsx`
- Delete: `frontend/src/components/screens/SpeciesStatsScreen.css`

**Step 1: Remove unused imports from App.tsx**

Open: `frontend/src/App.tsx`
Remove any imports for deleted screens.

**Step 2: Delete unused screen files**

```bash
git rm frontend/src/components/screens/SettingsScreen.tsx
git rm frontend/src/components/screens/StatsScreen.tsx
git rm frontend/src/components/screens/HistoryScreen.tsx
git rm frontend/src/components/screens/SpeciesStatsScreen.tsx
git rm frontend/src/components/screens/SpeciesStatsScreen.css
```

**Step 3: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "refactor: remove unused screen files after consolidation"
```

---

## Task 10: Test and Verify

**Files:**
- No new files, run tests

**Step 1: Run backend tests**

```bash
cd /Users/knmurphy/Documents/PROJECTS/BirdNET-Pi-old
pytest api/tests/ -v
```

Expected: All tests pass.

**Step 2: Start development server**

```bash
cd frontend
npm run dev
```

**Step 3: Test navigation manually**

Open browser to http://localhost:5173

Verify:
1. TabBar shows only 3 tabs: Live, Info, Species
2. Live tab shows "Today" header and "Most Recent" section with border
3. Info tab shows System Health (with temp in C+F, memory) and Settings sections
4. Species tab shows filters, sorting, charts
5. All temperature displays show both Celsius and Fahrenheit
6. "New" badges appear on new species
7. Charts render correctly and are performant

**Step 4: Run linting**

```bash
cd frontend
npm run lint
```

Expected: No errors.

**Step 5: Run build**

```bash
cd frontend
npm run build
```

Expected: Build succeeds without errors.

**Step 6: Final commit**

```bash
git add .
git commit -m "test: complete simplified navigation implementation"
```

---

## Summary

This plan simplifies navigation from 6 tabs to 3 while adding significant functionality:

**Backend changes:**
- Add memory usage to system API
- Add Fahrenheit temperature conversion

**Frontend changes:**
- Reduce tabs to 3: Live, Info, Species
- Live: Add "Today" header + "Most Recent" section
- Info: Combine System + Settings
- Species: Absorb History + Stats with filters, sorting, charts
- Add "New" badges for species
- Add Chart.js visualizations

**Total estimated tasks:** 10
**Total estimated time:** 2-3 hours for implementation
