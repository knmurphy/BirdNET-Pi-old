# Frontend Architecture Guide (for AI Agents)

This document provides context for AI agents working on the Field Station UI codebase.

## Quick Context

- **Purpose**: Mobile-first PWA for passive acoustic monitoring (bird/bat detection)
- **Hardware target**: Raspberry Pi deployment at `10.0.0.177:8003`
- **Primary users**: Field researchers viewing real-time detection feeds

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  LiveScreen │  │SpeciesScreen│  │HistoryScreen│ ...     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│  ┌──────▼────────────────▼────────────────▼──────┐         │
│  │              TanStack Query (cache)            │         │
│  └──────────────────────┬────────────────────────┘         │
│                         │                                   │
│  ┌──────────────────────▼────────────────────────┐         │
│  │  SSE (EventSource) / Fetch API                 │         │
│  └──────────────────────┬────────────────────────┘         │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTP/SSE
┌─────────────────────────▼───────────────────────────────────┐
│              Python Backend (FastHTML)                      │
│  homepage/web_app.py → Port 8003                            │
│  Database: scripts/birds.db (SQLite)                        │
└─────────────────────────────────────────────────────────────┘
```

## Key Files Reference

| File | Purpose | When to edit |
|------|---------|--------------|
| `src/App.tsx` | Root component, routing, providers | Adding new routes/screens |
| `src/types/index.ts` | TypeScript interfaces for API | API contract changes |
| `src/hooks/*.ts` | Data fetching hooks | New API endpoints, caching logic |
| `src/contexts/SSEProvider.tsx` | SSE connection management | Real-time features |
| `src/components/screens/*.tsx` | Screen components | UI changes per screen |
| `src/components/DetectionCard.tsx` | Single detection display | Detection card UI |
| `src/components/SpeciesRow.tsx` | Species list item | Species list UI |
| `vite.config.ts` | Build config, PWA manifest | Build changes, caching |

## Data Flow Patterns

### 1. Initial Data Load (TanStack Query)

```typescript
// In hooks/useDetections.ts
export function useDetectionsToday() {
  return useQuery({
    queryKey: ['detections', 'live'],
    queryFn: fetchDetectionsToday,
    staleTime: Infinity,  // SSE updates cache, no auto-refetch
  });
}
```

**Pattern**: Query fetches initial data, then SSE updates the cache.

### 2. Real-Time Updates (SSE)

```typescript
// In hooks/useSSE.ts
es.addEventListener('detection', (e) => {
  const detection = JSON.parse(e.data);
  
  // Update TanStack Query cache directly
  queryClient.setQueryData(['detections', 'live'], (old) => ({
    detections: [detection, ...(old?.detections ?? [])]
  }));
  
  // Invalidate related queries
  queryClient.invalidateQueries({ queryKey: ['summary', 'today'] });
});
```

**Pattern**: SSE events prepend to cache, invalidate dependent queries.

### 3. API Response Types

All API types are defined in `src/types/index.ts`. Key types:

- `Detection` - Single detection record
- `SpeciesSummary` - Species aggregation with hourly counts
- `TodaySummaryResponse` - Daily totals
- `SystemResponse` - CPU, temp, disk, uptime

## Backend API Contract

The backend is in `homepage/web_app.py` (FastHTML, not FastAPI).

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/detections?date=today` | GET | Today's detections |
| `/api/detections/today/summary` | GET | Daily totals |
| `/api/species/today` | GET | Species with hourly counts |
| `/api/system` | GET | System health metrics |
| `/api/events` | SSE | Real-time detection stream |
| `/api/audio/{path}` | GET | Serve audio files |

## Confidence Thresholds

Used for color-coding detection confidence:

```typescript
const DEFAULT_THRESHOLDS = {
  high: 0.85,    // Green (--accent)
  medium: 0.65,  // Amber (--amber)
  // < 0.65: Red (--red)
};
```

Helper functions: `getConfidenceColor()`, `getConfidenceLevel()`, `formatConfidence()`

## Design System

CSS variables in `App.css`:

```css
:root {
  --bg: #0D0F0B;      /* Background */
  --bg2: #141610;     /* Elevated background */
  --border: #252820;  /* Borders */
  --text: #F0EAD2;    /* Primary text */
  --text2: #9A9B8A;   /* Secondary text */
  --text3: #5A5C4E;   /* Muted text */
  --accent: #C8E6A0;  /* Primary accent (green) */
  --amber: #E8C547;   /* Warning/medium */
  --red: #E05252;     /* Error/low */
}
```

Fonts:
- Display: Fraunces (serif, for headers)
- Mono: DM Mono (for data/timestamps)
- Body: Source Serif 4

## Adding New Features

### Adding a new screen

1. Create component in `src/components/screens/NewScreen.tsx`
2. Add route in `src/App.tsx` under `<Routes>`
3. Add tab in `src/components/layout/TabBar.tsx` if navigation needed

### Adding a new API endpoint consumer

1. Add type in `src/types/index.ts`
2. Create hook in `src/hooks/useNewData.ts`
3. Use in screen component

### Adding SSE event handling

1. Add event type in `src/types/index.ts`
2. Update `src/hooks/useSSE.ts` to handle new event
3. Update cache or invalidate queries as needed

## Deployment

```bash
# Build
npm run build

# Deploy to RPi
rsync -avz --delete dist/ knmurphy@10.0.0.177:/home/knmurphy/BirdNET-Pi/frontend/dist/
```

Backend serves frontend from `/home/knmurphy/BirdNET-Pi/frontend/dist/` at port 8003.

## Common Gotchas

1. **SSE deduplication**: The `useSSE` hook tracks seen detection IDs to prevent duplicates
2. **Stale time**: Detection queries use `staleTime: Infinity` because SSE updates the cache
3. **Confidence values**: API returns 0.0-1.0, display as percentage
4. **Time format**: API returns `HH:MM:SS`, dates as `YYYY-MM-DD`
5. **Audio paths**: Relative from audio root, served via `/api/audio/{path}`

## Testing

```bash
# Run tests (from project root)
pytest

# Run specific frontend-related tests
pytest tests/test_web_app.py
```

## Related Documentation

- `README.md` - Developer quick start
- `prd.json` - Original product requirements
- `progress.md` - Implementation progress log
