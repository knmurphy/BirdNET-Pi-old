# Field Station UI

React frontend for BirdNET-Pi Field Station OS. Mobile-first PWA with real-time detection feed.

## Tech Stack

- **Vite** - Build tool
- **React 18** - UI framework
- **TypeScript** - Type safety
- **React Router** - Client-side routing
- **TanStack Query** - Server state management
- **SSE (Server-Sent Events)** - Real-time detection feed
- **vite-plugin-pwa** - PWA support

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment

The frontend is deployed to the Raspberry Pi at `10.0.0.177`.

```bash
# Build and deploy
npm run build
rsync -avz --delete dist/ knmurphy@10.0.0.177:/home/knmurphy/BirdNET-Pi/frontend/dist/
```

The backend serves the frontend from `/home/knmurphy/BirdNET-Pi/frontend/dist/` at port 8003.

## Project Structure

```
src/
├── components/
│   ├── DetectionCard.tsx    # Single detection display with audio playback
│   ├── SpeciesRow.tsx       # Species list row with NEW badge
│   ├── layout/
│   │   ├── Header.tsx       # App header with connection status
│   │   └── TabBar.tsx       # Bottom navigation tabs
│   └── screens/
│       ├── LiveScreen.tsx   # Real-time detection feed (SSE)
│       ├── SpeciesScreen.tsx # Today's species list with sorting
│       ├── HistoryScreen.tsx # Paginated detection history
│       ├── StatsScreen.tsx  # System health display
│       └── SettingsScreen.tsx # Station config with location map
├── contexts/
│   ├── SSEContext.ts        # SSE connection context
│   └── SSEProvider.tsx      # SSE provider with React Query integration
├── hooks/
│   ├── useSSE.ts            # SSE connection hook
│   ├── useDetections.ts     # Detection data from SSE
│   ├── useSpeciesToday.ts   # Today's species data
│   ├── useTodaySummary.ts   # Detection totals
│   ├── useSystemHealth.ts   # CPU, temp, disk, uptime
│   └── useAudio.ts          # Audio playback hook
├── types/
│   └── index.ts             # TypeScript interfaces for API
└── App.tsx                  # Main app with routing
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/detections` | Paginated detection list |
| `GET /api/detections/today/summary` | Today's detection totals |
| `GET /api/species/today` | Today's species with hourly counts |
| `GET /api/system` | System health (CPU, temp, disk, uptime) |
| `GET /api/settings` | Station configuration |
| `GET /api/classifiers` | Classifier configs |
| `GET /api/audio/{path}` | Serve audio files |
| `GET /api/events` | SSE stream for real-time detections |

## Features

### Live Screen
- Real-time detection feed via SSE
- Time-based fading (older detections are dimmed)
- Audio playback on tap
- Connection status indicator

### Species Screen
- Sorted species list (by count, recent, confidence, A-Z)
- "NEW" badge for species first seen in last 2 hours
- Detection counts and peak confidence

### History Screen
- Paginated detection history
- Audio playback for each detection

### Stats Screen
- CPU usage, temperature, disk usage
- Formatted uptime display

### Settings Screen
- Location map (OpenStreetMap static image, no API key)
- Classifier settings display
- Audio storage path

## Design System

- **Dark theme** with CSS custom properties
- **Fonts**: DM Mono, Fraunces, Source Serif 4
- **Mobile-first** responsive design
- **PWA** installable on mobile devices
