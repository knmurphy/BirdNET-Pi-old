# Field Station OS — UI Product Requirements Document

**Version:** 0.3 Draft
**Date:** 2026-02-25  
**Author:** Kevin Murphy  
**Status:** Pre-implementation planning

---

## 1. Overview

This document defines the requirements for a new web UI for the Field Station OS — a passive acoustic monitoring platform built on a rewritten backend (FastAPI + DuckDB + SSE event bus) that replaces the PHP/polling architecture of BirdNET-Pi.

The UI is a mobile-first progressive web app designed to be the primary interface for monitoring a headless field station from a phone or tablet over local WiFi or reverse proxy. It is not a data analysis platform — it is a near-real-time observation dashboard that surfaces detections as they happen and provides lightweight historical reference.

---

## 2. Background & Motivation

### Current state (BirdNET-Pi)

The existing PHP-based UI polls for new detections every 4–15 seconds using `setInterval`. The detection table refreshes at `RECORDING_LENGTH / 4`, the spectrogram view refreshes at `RECORDING_LENGTH`. This means a detection that has already been classified and written to SQLite may not appear in the browser for up to 15 seconds.

The UI is desktop-optimized, served from Apache, not installable as a PWA, and tightly coupled to BirdNET-specific data structures. Adding a second classifier (e.g. BatDetect2) or a second audio input is not architecturally supported.

### New architecture

The backend has been redesigned as:

- **FastAPI** serving a REST API + SSE event stream
- **DuckDB** replacing SQLite (better analytical queries, parquet-compatible)
- **EventBus** — an asyncio pub/sub bus that publishes detection events immediately after `write_to_db()` commits, delivering them to all connected SSE clients within ~100ms
- **Classifier plugin system** — a Python ABC-based registry supporting BirdNET, Google Perch, BatDetect2, and future classifiers, all publishing through the same EventBus with a `classifier` field on each event

The UI should be built against this backend from the start, not adapted from the old PHP views.

---

## 3. Design Philosophy

**Instrument panel, not spreadsheet.** The UI should feel like monitoring equipment — calm, information-dense, dark by default, with a clear visual hierarchy that makes the most recent detection the most prominent element on screen at all times.

**Mobile-first, one-handed usable.** The primary interaction context is: phone in hand, standing near the field station, checking whether something interesting is happening. Not a laptop with a mouse.

**Minimal chrome, maximum data.** No sidebars, no marketing, no decorative empty states with illustrated birds. When there are no detections, show system status. When there are detections, show detections.

**SSE-native for events.** Detection events arrive via SSE stream — no polling. REST endpoints are used only for initial page load hydration and historical queries. The absence of a loader spinner on the live feed is a feature, not a gap.

**Spectrogram is an exception.** The spectrogram is visual context, not a detection event. Implementation approach (SSE notification + fetch, WebSocket, Canvas/WebGL, Rive, etc.) is determined during design/prototype phase based on aesthetic and performance requirements.

---

## 4. Platform Targets

| Context | Target |
|---|---|
| Primary | Mobile browser (Safari iOS, Chrome Android), portrait |
| Secondary | Tablet browser, landscape |
| Tertiary | Desktop browser (for historical review) |
| Installable | PWA (add-to-home-screen, offline shell) |
| Auth | None (local WiFi), or Caddy basic auth at proxy layer |

Screen width assumptions: 375px minimum (iPhone SE), optimal at 390–430px. Layout should not require horizontal scrolling at any supported width.

---

## 5. Information Architecture

The app has five top-level screens navigated via a bottom tab bar. Tabs are visible at all times.

```
┌──────────────────────────┐
│  Header (station ID, time) │
├──────────────────────────┤
│                          │
│      Active Screen       │
│                          │
├──────────────────────────┤
│  [Live] [Species] [History] [Stats] [Settings] │
└──────────────────────────┘
```

### Tab definitions

| Tab | Icon | Purpose |
|---|---|---|
| **Live** | ◉ | Real-time detection feed + spectrogram |
| **Species** | ☰ | Today's species list, sorted by count |
| **History** | ≡ | Detection log with date/filter controls |
| **Stats** | ∿ | System health, hourly activity chart |
| **Settings** | ⚙ | Station config, classifier enable/disable, threshold |

---

## 6. Screen Specifications

### 6.1 Live Screen (default on open)

The Live screen is the primary view. It has two regions: a spectrogram strip at the top and a live detection feed below it.

**Spectrogram strip**

- Height: ~120px
- Renders a scrolling time-frequency visualization of the current audio recording segment
- **Reference implementation:** [spectrogram-unknown](https://github.com/knmurphy/spectrogram-unknown) — Rust + WebGL with Unknown Pleasures aesthetic (stacked line waves, pulsar CP1919 style). Live demo: https://aestuans.github.io/spectrogram
- **Aesthetic requirements:**
  - Visually refined, poetic quality — inspired by Unknown Pleasures / pulsar visualization style
  - Stacked line/wave rendering (not heat-map)
  - Smooth, fluid motion at 60fps
  - Consistent with the dark, instrument-panel aesthetic
- **Performance requirements:**
  - 60fps rendering on iPhone SE (oldest supported device)
  - Responsive to real-time audio data (updates within 100-250ms)
- **Technical approach:**
  - Primary: Rust → WebAssembly + WebGL (following reference implementation)
  - Alternative: Canvas/WebGL with TypeScript, Rive animation
  - Data delivery: SSE notification + fetch, or WebSocket binary frames
- Frequency axis labeled on left edge (Hz)
- Classifier-detected segments marked with a colored overlay band (color-coded by classifier)
- No interaction required on first implementation; tapping could eventually navigate to a detail view
- **Design/prototype phase required** before implementation to adapt reference implementation to Field Station context

**Live detection feed**

- Reverse-chronological list of detection events, newest at top
- Populated via SSE `detection` events — no polling, no manual refresh
- New detections animate in at the top (slide-down, ~200ms)
- Each detection card shows:
  - Common name (primary text, largest)
  - Scientific name (secondary, italic)
  - Confidence as a horizontal bar + percentage
  - Time (HH:MM:SS, 24-hour format)
  - Classifier badge (e.g. `BirdNET`, `BatDetect2`) — colored dot from classifier config
  - Tappable → audio playback inline (the `.wav` clip for that detection)
- Confidence color: thresholds defined per-classifier via `/api/classifiers`; falls back to global defaults (green ≥ 0.85, amber 0.65–0.84, red < 0.65)
- List is virtualized for performance (no DOM cap, but render only visible rows)
- **Deduplication:** Use detection `id` field. If id already exists in cache, ignore the event.
- "Live" indicator in header pulses green when SSE connection is healthy; turns amber on reconnect, red on disconnect > 5s

**Connection state**

The SSE connection must be surfaced clearly:
- `CONNECTED` — green pulse dot, no banner
- `RECONNECTING` — amber dot, subtle banner: "Reconnecting…"
- `DISCONNECTED` — red dot, banner: "Connection lost — check station"

The browser's built-in EventSource reconnect handles most cases automatically. The UI should reflect the connection state from EventSource `readyState` rather than managing reconnect logic itself.

**Empty state**

- When no detections today: Show "No detections yet today" with system status summary below
- System status: CPU, temperature, disk (same data as Stats panel, compact format)

---

### 6.2 Species Screen

Aggregated view of all species detected today.

- Sorted by detection count descending (default)
- Sort options: count, last seen, confidence max, alphabetical
- Each row:
  - Common name
  - Scientific name (smaller, muted)
  - Detection count (right-aligned, prominent)
  - Last seen time
  - Peak confidence
  - Trend indicator (↑ ↓ → based on count vs. rolling 7-day average for that species/hour)
- Tapping a row opens a **species detail bottom sheet:**
  - Slides up from bottom, drag down to dismiss
  - On tablet/desktop: side panel or modal
  - Contains:
    - Detection timeline for today (mini bar chart by hour)
    - All detections for that species today (time, confidence, audio playback)
    - Link to external reference (eBird, Xeno-canto) — opens in browser
- Data source: REST endpoint, refreshed on tab focus + invalidated by SSE events

**Empty state**

- "No species detected today" with subtitle "Detections will appear here as they're classified"
- Show connection status to confirm system is running

**Error state**

- "Failed to load species list" with retry button
- Show last successful load time if available

**Loading state**

- Skeleton rows (3-5 placeholders) while fetching initial data

---

### 6.3 History Screen

Log of all detections with date navigation and filters.

- Default: today
- Date picker: prev/next day chevrons with date label (MVP); calendar widget in Phase 3
- Filter controls (collapsible, collapsed by default):
  - Species search (text input)
  - Classifier filter (multi-select: All / BirdNET / BatDetect2 / ...)
  - Confidence threshold slider (0–1.0)
  - Hour range (slider or two dropdowns)
- Detection list: same card format as Live, but no animation
- **Infinite scroll:** "Load more" button at bottom (not auto-trigger on scroll, to avoid scroll-janking on mobile)
- 50 detections per page
- Export: "Download CSV" — triggers REST endpoint returning filtered results as CSV download

**Empty state**

- No detections on selected date: "No detections on {date}"
- No results after filtering: "No detections match your filters" with "Clear filters" button

**Error state**

- "Failed to load detections" with retry button

**Loading state**

- Skeleton rows while fetching

---

### 6.4 Stats Screen

System health and activity overview.

**System health panel**

| Metric | Source |
|---|---|
| CPU % | `/api/system` REST, polled every 30s |
| Temperature (°C) | same |
| Disk used / total | same |
| Uptime | same |
| Active classifiers | same |
| SSE subscriber count | same |

Polling every 30s to minimize load on Pi hardware (not user-facing latency requirement).

CPU and temperature shown as gauge bars. Disk shown as fill meter. All values update without full page refresh.

**Activity chart**

- 24-hour bar chart: detection count by hour
- Today vs. yesterday overlay (two series, different opacity)
- Tapping a bar navigates to History filtered to that hour

**Recent classifier activity**

- List of classifiers with: display name, last inference time, inference duration (ms), detection count today
- Toggle to enable/disable a classifier from this view (POST to `/api/classifiers/{id}/toggle`)

**Error state**

- Individual panel failure: show "Unavailable" for that metric, other panels continue
- Complete failure: "Failed to load system stats" with retry button

**Loading state**

- Skeleton for each panel section

---

### 6.5 Settings Screen

Station configuration. Changes POST to the FastAPI settings endpoint and are persisted to `config.ini`.

**Station identity**

- Station name (text input)
- Location (lat/lon — text inputs, or map picker if scope allows)

**Recording**

- Recording length (seconds) — select: 3, 5, 10, 15, 30
- Sample rate — select: 16000, 44100, 48000
- Input device — select populated from `/api/audio/devices`

**Classifiers**

- List of installed classifiers with enable/disable toggle
- Confidence threshold per classifier (slider)
- Species filter: lat/lon radius and week-based filtering toggle (BirdNET-specific)

**Export / data**

- Retention policy: keep audio files for N days (0 = forever)
- Manual "Purge old files" trigger

**System**

- Restart analysis service button
- Reboot station button (with confirmation)
- Software version info

---

### 6.6 Error Handling & Edge Cases

**API errors**

- 4xx (client error): Show inline error message with retry button
- 5xx (server error): Show "Server error — check station" with retry button
- Network timeout: Same as disconnect state
- 429 (rate limited): Show "Too many requests — wait a moment" with auto-retry countdown

**SSE reconnection**

- EventSource auto-reconnects; UI reflects readyState
- On reconnect, refetch `/api/detections/today/summary` and `/api/species/today` to catch any missed events during disconnect
- Missed individual detection events are acceptable for the real-time feed (feature, not bug) — they'll appear in historical queries

**Offline behavior (Phase 3)**

- Service worker serves cached UI shell
- Show "Station offline" banner when all network requests fail
- Cached species/history data shown with "Last updated: X minutes ago"
- No cached data: Show "No cached data available" with retry

**Audio playback edge cases**

- File not found (404): Show "Audio unavailable" with grayed-out, disabled play button
- Large file loading: Show spinner in play button during load
- Playback error: Show "Could not play audio" with retry

**Timezone handling**

- All timestamps from backend in UTC
- UI converts to local browser time via `Intl.DateTimeFormat`
- `iso8601` field includes timezone offset; if missing, assume UTC
- Header time displays in local 24-hour format

---

## 7. Backend API Contract

The UI depends on the following API surface. Endpoints must be implemented in FastAPI before UI development begins on the features that consume them.

### SSE Stream

```
GET /api/events
Content-Type: text/event-stream
```

Events emitted:

```
event: detection
data: {
  "id": 12345,
  "com_name": "Black-capped Chickadee",
  "sci_name": "Poecile atricapillus",
  "confidence": 0.97,
  "date": "2026-02-25",
  "time": "07:42:11",
  "iso8601": "2026-02-25T07:42:11-05:00",
  "file_name": "2026-02-25/birdnet/2026-02-25T074211.wav",
  "classifier": "birdnet"
}

event: heartbeat
data: {}
```

Heartbeat emitted every 15 seconds to keep proxy connections alive. The `X-Accel-Buffering: no` header must be set to prevent Caddy/nginx from buffering the stream.

**Note:** The `id` field is required for deduplication and audio URL construction. The `file_name` includes the relative path from the audio storage root.

### REST Endpoints (minimum viable)

| Method | Path | Description |
|---|---|---|
| GET | `/api/detections` | Paginated detection log. Params: `date`, `classifier`, `min_confidence`, `species`, `page`, `limit` |
| GET | `/api/detections/today/summary` | Aggregated: total count, species count, top species, hourly breakdown |
| GET | `/api/species/today` | Species list for today with counts, max confidence, last seen |
| GET | `/api/spectrogram` | Spectrogram data (format TBD based on implementation approach) |
| GET | `/api/audio/{path}` | Serves .wav files. `{path}` matches `file_name` from detection event. Returns 404 if not found. |
| GET | `/api/system` | CPU, temp, disk, uptime, classifier status |
| GET | `/api/audio/devices` | List of available ALSA input devices |
| GET | `/api/classifiers` | List of installed classifiers with config (including display name, color, confidence thresholds) |
| POST | `/api/classifiers/{id}/toggle` | Enable/disable a classifier |
| GET | `/api/settings` | Current station config |
| POST | `/api/settings` | Update station config |
| POST | `/api/system/restart` | Restart analysis service |

### Response Schemas

**GET /api/classifiers**

```typescript
interface ClassifierConfig {
  id: string;                    // "birdnet", "batdetect2", etc.
  display_name: string;          // "BirdNET", "BatDetect2"
  color: string;                 // Hex color for badges/overlays
  enabled: boolean;
  confidence_high: number;       // Threshold for green (e.g., 0.85)
  confidence_medium: number;     // Threshold for amber (e.g., 0.65)
  model_name: string;            // Full model identifier
  last_inference: string | null; // ISO datetime
  inference_duration_ms: number | null;
  detection_count_today: number;
}

interface ClassifiersResponse {
  classifiers: ClassifierConfig[];
}
```

**GET /api/species/today**

```typescript
interface SpeciesSummary {
  com_name: string;
  sci_name: string;
  detection_count: number;
  max_confidence: number;
  last_seen: string;             // "HH:MM:SS"
  hourly_counts: number[];       // 24-element array, counts per hour
}

interface SpeciesTodayResponse {
  species: SpeciesSummary[];
  generated_at: string;          // ISO datetime
}
```

**GET /api/detections/today/summary**

```typescript
interface TodaySummaryResponse {
  total_detections: number;
  species_count: number;
  top_species: {
    com_name: string;
    count: number;
  }[];
  hourly_counts: number[];       // 24-element array
  generated_at: string;
}
```

**GET /api/system**

```typescript
interface SystemResponse {
  cpu_percent: number;
  temperature_celsius: number;
  disk_used_gb: number;
  disk_total_gb: number;
  uptime_seconds: number;
  active_classifiers: string[];  // Classifier IDs
  sse_subscribers: number;
  generated_at: string;
}
```

### Data model — Detection

```typescript
interface Detection {
  id: number;
  com_name: string;
  sci_name: string;
  confidence: number;         // 0.0–1.0
  date: string;               // ISO date: "2026-02-25"
  time: string;               // "HH:MM:SS"
  iso8601: string;            // Full ISO datetime with timezone
  file_name: string;          // Relative path to .wav from audio root
  classifier: string;         // "birdnet" | "batdetect2" | etc.
}
```

**Note:** The `week` field was removed as it's not used by the UI. Week-based filtering (BirdNET location/week) is handled server-side.

### Audio URL Construction

```
{API_BASE_URL}/api/audio/{file_name}
```

- `API_BASE_URL` from environment (defaults to current origin)
- `file_name` is the relative path from the detection event
- Example: `/api/audio/2026-02-25/birdnet/2026-02-25T074211.wav`
- Returns 404 if file not found

---

## 8. Frontend Technology Stack

| Layer | Choice | Rationale |
|---|---|---|
| Framework | React 18 | Ecosystem, hooks, concurrent rendering |
| Build | Vite | Fast HMR, good PWA plugin support |
| State / fetching | TanStack Query v5 | SSE → cache mutation pattern, background refetch |
| Routing | React Router v6 | Tab-based SPA routing |
| SSE | Native `EventSource` | No library needed, auto-reconnects |
| Charts | Recharts | React-native, composable, no canvas boilerplate |
| Styling | CSS Modules or plain CSS | No Tailwind (avoids build-time class purge complexity on Pi) |
| PWA | vite-plugin-pwa | Workbox service worker, add-to-home-screen manifest |
| Audio playback | Native `<audio>` element | No library, .wav playback supported natively |
| Spectrogram | Rust → WebAssembly + WebGL | Unknown Pleasures aesthetic, 60fps rendering — based on [spectrogram-unknown](https://github.com/knmurphy/spectrogram-unknown) reference |
| TypeScript | Yes | Type safety for Detection interface, API responses |

### React Query + SSE integration pattern

```typescript
// hooks/useSSE.ts
import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { Detection } from '../types';

export function useSSE() {
  const queryClient = useQueryClient();
  const seenIds = useRef(new Set<number>());

  useEffect(() => {
    const es = new EventSource('/api/events');

    es.addEventListener('detection', (e) => {
      const detection: Detection = JSON.parse(e.data);

      // Deduplicate by id
      if (seenIds.current.has(detection.id)) return;
      seenIds.current.add(detection.id);

      // Prepend to live feed cache — zero refetch, instant render
      queryClient.setQueryData<{ detections: Detection[] }>(
        ['detections', 'live'],
        (old) => ({ detections: [detection, ...(old?.detections ?? [])] })
      );

      // Mark summary stale — refetches on next focus
      queryClient.invalidateQueries({ queryKey: ['summary', 'today'] });
      queryClient.invalidateQueries({ queryKey: ['species', 'today'] });
    });

    return () => es.close();
  }, [queryClient]);
}
```

`useSSE()` is called once at the app root. All screens that display live data subscribe to the relevant React Query keys — they receive updates automatically without polling.

---

## 9. Visual Design System

### Color palette (dark theme, default)

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#0D0F0B` | App background |
| `--bg2` | `#141610` | Card / panel background |
| `--bg3` | `#1A1D16` | Input / elevated surface |
| `--border` | `#252820` | Dividers |
| `--text` | `#F0EAD2` | Primary text |
| `--text2` | `#9A9B8A` | Secondary text, labels |
| `--text3` | `#5A5C4E` | Tertiary, placeholders |
| `--accent` | `#C8E6A0` | Active tab, high confidence |
| `--amber` | `#E8C547` | Medium confidence, status indicators |
| `--red` | `#E05252` | Low confidence, errors, alerts |

Light theme tokens should be defined from the start (via CSS custom properties) even if the toggle is deferred to a later milestone.

### Typography

| Use | Font | Size |
|---|---|---|
| Station name, labels | DM Mono | 9–12px |
| Species common name | Fraunces | 17–20px |
| Species scientific name | Source Serif 4 Italic | 13–14px |
| Body / secondary text | Source Serif 4 | 14px |
| Timestamps, codes | DM Mono | 11–12px |

All fonts loaded from Google Fonts. Subset for Latin characters only (reduces payload).

### Classifier color coding

Classifier colors are data-driven, loaded from `/api/classifiers`. The hardcoded table below shows defaults for known classifiers:

| Classifier ID | Display Name | Default Color |
|---|---|---|
| `birdnet` | BirdNET | `#C8E6A0` (accent green) |
| `batdetect2` | BatDetect2 | `#A0C4E8` (blue) |
| `google-perch` | Google Perch | `#E8C4A0` (warm orange) |
| *(unknown)* | *(from config)* | `#9A9B8A` (muted) |

**Implementation:** UI fetches classifier config on app load. Detection cards and spectrogram overlays use the color from config. Unknown classifiers fall back to muted default.

---

## 10. PWA Requirements

The app must be installable to the home screen on iOS Safari and Android Chrome.

**Manifest**

```json
{
  "name": "Field Station",
  "short_name": "Station",
  "display": "standalone",
  "background_color": "#0D0F0B",
  "theme_color": "#0D0F0B",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

**Service worker**

- Cache-first for static assets (JS, CSS, fonts)
- Network-first for API endpoints
- Offline shell: show cached UI with "Station offline" banner if all network requests fail
- Do not cache SSE stream

**No push notifications in v1.** Future milestone: alert on high-confidence rare species detection via web push.

---

## 11. Phased Delivery

### Phase 1 — Core (MVP)

Goal: replace the BirdNET-Pi UI with something that works on mobile and uses SSE.

- Live screen: SSE-connected detection feed with classifier badges
- Species screen: today's species list (no trend indicators, no detail sheet)
- Header with connection status indicator
- Bottom tab navigation (all tabs render, non-implemented screens show placeholder)
- Dark theme only
- PWA manifest (installable, no service worker yet)
- Error/empty/loading states for implemented screens

Depends on: `/api/events` SSE endpoint, `/api/detections` (today), `/api/species/today`, `/api/classifiers`

### Phase 2 — History & Audio

- History screen: full implementation with date nav, filters, infinite scroll
- Audio playback (inline `<audio>`)
- Stats screen: system health panel + hourly activity chart
- CSV export

Depends on: `/api/detections` (date range, filters), `/api/system`, `/api/audio/{path}`

### Phase 3 — Spectrogram & Polish

- Spectrogram strip on Live screen (requires design/prototype phase first)
- Species detail bottom sheet
- Species trend indicators
- Service worker + offline shell
- Light theme toggle

Depends on: Spectrogram endpoint (format TBD), `/api/species/{id}/detections`

### Phase 4 — Settings & Multi-classifier

- Settings screen (full read/write)
- Classifier toggle in Settings / Stats
- BatDetect2 integration (backend prerequisite)
- Per-classifier color coding in spectrogram overlay

Depends on: `/api/settings` (write), `/api/audio/devices`, classifier toggle endpoints

---

## 12. Non-Goals (v1)

- User accounts or multi-user support
- Remote access setup / VPN configuration (handled at network layer by user)
- BirdWeather / eBird upload integration
- Map view of detection locations
- Push notifications
- Android/iOS native app (PWA is sufficient)
- Admin panel for managing multiple stations

---

## 13. Open Questions

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | Spectrogram data delivery — FFT bins via SSE notification + fetch, or WebSocket binary frames? To be determined based on reference implementation adaptation. | Both | Open |
| 2 | DuckDB query for "today's species with hourly breakdown" — confirm query performance on Pi hardware before UI depends on it. | Backend | Open |
| 3 | Station config persistence: does `POST /api/settings` write directly to `config.ini` and trigger service restart, or queue a reload? | Backend | Open |
| 4 | Spectrogram classifier overlay integration — how to overlay detection markers on the Unknown Pleasures-style wave visualization? | Design | Open |

### Resolved Questions

| # | Question | Resolution |
|---|---|---|
| 1 | Spectrogram endpoint format (PNG vs URL) | Deferred to prototype phase; implementation-agnostic in PRD |
| 2 | Audio file serving | Caddy serves `/api/audio/*` as static files via FastAPI route (documented in API contract) |
| 3 | Classifier identifier naming | Lowercase slug: `birdnet`, `batdetect2`, `google-perch` |
| 4 | Light theme | Define tokens now, toggle in Phase 3 |
| 5 | History pagination | Infinite scroll with "Load more" button |
| 6 | History date picker | Prev/next chevrons for MVP, calendar in Phase 3 |
| 7 | Confidence thresholds | Per-classifier via `/api/classifiers`, global fallback |
| 8 | Classifier colors | Data-driven from API, not hardcoded |
| 9 | Species detail interaction | Bottom sheet on mobile, side panel/modal on tablet/desktop |
| 10 | Spectrogram aesthetic direction | Unknown Pleasures / pulsar CP1919 style (stacked line waves) — [spectrogram-unknown](https://github.com/knmurphy/spectrogram-unknown) as reference implementation |

---

## 14. Revision History

| Version | Date | Notes |
|---|---|---|
| 0.1 | 2026-02-25 | Initial draft from architecture sessions |
| 0.2 | 2026-02-25 | Added error/empty/loading states, resolved open questions, clarified spectrogram approach (implementation-agnostic), added API response schemas, fixed phase ordering, added deduplication logic, made classifier colors data-driven |
| 0.3 | 2026-02-25 | Added [spectrogram-unknown](https://github.com/knmurphy/spectrogram-unknown) as reference implementation for Unknown Pleasures aesthetic; updated technical approach to Rust/WebAssembly/WebGL primary |