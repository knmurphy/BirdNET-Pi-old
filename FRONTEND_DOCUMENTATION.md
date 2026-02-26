# Frontend Architecture Documentation

This document describes the React frontend for BirdNET-Pi, including project structure, API integration, and deployment instructions for Raspberry Pi.

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── DetectionCard.tsx       # Individual detection card with audio playback
│   │   ├── SpeciesRow.tsx          # Species row component
│   │   ├── layout/
│   │   │   ├── Header.tsx          # Header component with title
│   │   │   └── TabBar.tsx          # Tab navigation
│   │   └── screens/
│   │       ├── LiveScreen.tsx      # Real-time detection feed
│   │       ├── HistoryScreen.tsx   # Historical detections
│   │       ├── StatsScreen.tsx     # System health metrics
│   │       ├── SpeciesScreen.tsx   # Species list
│   │       └── SettingsScreen.tsx  # Application settings
│   ├── contexts/
│   │   └── SSEContext.tsx          # Server-Sent Events context
│   ├── hooks/
│   │   ├── useSSE.ts               # SSE connection hook
│   │   ├── useDetections.ts        # Fetch detections hook
│   │   ├── useSpeciesToday.ts      # Fetch today's species hook
│   │   ├── useSystemHealth.ts      # Fetch system health hook
│   │   ├── useTodaySummary.ts      # Fetch detection summary hook
│   │   └── useAudio.ts             # Audio playback hook
│   ├── types/
│   │   └── index.ts                # TypeScript type definitions
│   ├── styles/
│   │   ├── fonts.css               # Font imports
│   │   ├── global.css              # Global styles
│   │   └── variables.css           # CSS custom properties
│   ├── App.tsx                     # Main app component
│   ├── main.tsx                    # Application entry point
│   └── index.css                   # Global styles
├── public/
│   ├── icons/                      # PWA icons
│   └── manifest.json               # PWA manifest
├── dist/                           # Production build output
├── package.json                    # Dependencies and scripts
├── vite.config.ts                  # Vite configuration (PWA)
├── tsconfig.json                   # TypeScript configuration
└── README.md                       # Frontend README
```

## API Integration

The frontend connects to the backend API endpoints via custom hooks. All API calls use `fetch` with proper error handling.

### Available Hooks

#### 1. useSSE.ts
- **Purpose**: Establishes and manages SSE connection to `/api/events`
- **Features**:
  - Auto-reconnect on connection loss
  - Real-time detection updates
  - Connection status tracking
- **Usage**:
  ```tsx
  const { events, connectionStatus } = useSSE();
  ```

#### 2. useDetections.ts
- **Purpose**: Fetches detection logs via GET `/api/detections`
- **Features**:
  - Paginated results
  - Filtering and sorting support
  - Loading and error states
- **Usage**:
  ```tsx
  const { detections, isLoading, isError, error } = useDetections();
  ```

#### 3. useSpeciesToday.ts
- **Purpose**: Fetches today's species list via GET `/api/species/today`
- **Features**:
  - Species count and statistics
  - Sorting options (count, last_seen, confidence, alpha)
  - Last seen timestamps
- **Usage**:
  ```tsx
  const { species, generatedAt } = useSpeciesToday();
  ```

#### 4. useSystemHealth.ts
- **Purpose**: Fetches system metrics via GET `/api/system`
- **Features**:
  - CPU usage percentage
  - Temperature (celsius)
  - Disk usage (GB used/total)
  - Uptime in seconds
  - Active classifiers
  - SSE subscriber count
  - Polls every 10 seconds
- **Usage**:
  ```tsx
  const { data: systemHealth } = useSystemHealth();
  // Access: systemHealth.cpu_percent, systemHealth.temperature_celsius, etc.
  ```

#### 5. useTodaySummary.ts
- **Purpose**: Fetches daily detection summary via GET `/api/detections/today/summary`
- **Features**:
  - Total detections today
  - Unique species count
  - Top species by count
  - Hourly activity distribution
  - Generated timestamp
- **Usage**:
  ```tsx
  const { data: summary } = useTodaySummary();
  // Access: summary.total_detections, summary.species_count, summary.hourly_counts
  ```

#### 6. useAudio.ts
- **Purpose**: Manages audio playback for detection recordings
- **Features**:
  - Audio URL generation for `/api/audio/{path}`
  - Play/pause state management
  - Supports multiple audio files
- **Usage**:
  ```tsx
  const { audioUrl, playing, toggle } = useAudio(detectionId, fileName);
  // Returns: audioUrl (string), playing (boolean), toggle (function)
  ```

### TypeScript Types

All API responses are typed using the interfaces in `src/types/index.ts`:

- **Detection**: Individual detection record
- **SpeciesSummary**: Species with detection count, confidence, last seen time
- **SpeciesTodayResponse**: Array of species with metadata
- **TodaySummaryResponse**: Daily summary with totals and hourly data
- **SystemResponse**: System health metrics
- **ClassifierConfig**: Classifier configuration with thresholds and status
- **ClassifiersResponse**: Array of classifiers

## Build System

### Development Build
```bash
npm run dev
```
- Runs Vite dev server
- Auto-reload on file changes
- API proxy to `http://localhost:8000` (configured in `vite.config.ts`)
- Source maps enabled for debugging

### Production Build
```bash
npm run build
```
- TypeScript compilation with strict checks
- Vite production bundling
- Generates optimized `dist/` folder with:
  - `index.html` - SPA entry point
  - `assets/` - Minified JS and CSS bundles
  - `sw.js`, `workbox-*.js` - PWA service worker
  - `manifest.webmanifest` - PWA manifest

### Build Output Size
- JavaScript bundle: ~276-277 KB (gzipped: ~86 KB)
- CSS bundle: ~16.5 KB (gzipped: ~3.6 KB)
- Total precache: ~330-334 KB
- **Target**: Raspberry Pi 4 (limited memory, but efficient)

### Preview Build
```bash
npm run preview
```
- Serves the production build locally
- Useful for testing before deployment

## PWA Features

The application is configured as a Progressive Web App with:

- **Service Worker**: Caches static assets for offline use
- **Manifest**: App name, icons, display mode
- **App Shell**: Works offline after first load
- **Installable**: Can be installed on mobile devices

**Installation** (in Chrome/Edge):
1. Open the app
2. Click "Add to Home Screen" or install prompt
3. App icon appears on home screen

## Deployment on Raspberry Pi

### Build on Development Machine

```bash
# Install dependencies
npm install

# Build production bundle
npm run build
```

This creates the `frontend/dist/` folder with all optimized assets.

### Deploy to Raspberry Pi

```bash
# Option 1: rsync from dev machine
rsync -avz frontend/dist/ pi@birdnet:~/BirdNET-Pi/frontend/

# Option 2: Copy via SSH
scp -r frontend/dist/* pi@birdnet:~/BirdNET-Pi/frontend/

# Option 3: Git push + SSH pull
git push
ssh pi@birdnet "cd ~/BirdNET-Pi && git pull && git checkout main"
```

### Serve with FastAPI

The FastAPI backend (`api/main.py`) serves the React SPA:

```python
# Serve React app (must be last to not override API routes)
dist_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, 'assets')), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes."""
        # API routes are handled by routers above
        if full_path.startswith('api/'):
            return None  # Let API routers handle it
        return FileResponse(os.path.join(dist_dir, 'index.html'))
```

**Important**: This must be the last router to ensure API routes take priority.

### Alternative: Caddy Web Server

If using Caddy for reverse proxy:

```caddy
# Caddyfile
root * /path/to/BirdNET-Pi/frontend/dist
try_files {path} /index.html

# API proxy
handle /api/* {
    reverse_proxy localhost:8000
}
```

## Performance Considerations

### Raspberry Pi Optimization

1. **Production Build Only**: Never run `npm run dev` on RPi
   - Dev server consumes ~100-200 MB RAM
   - Production build is optimized and memory-efficient

2. **No Node.js Required on RPi**:
   - Static files are served by FastAPI (built-in)
   - No Node runtime needed on target system

3. **Lazy Loading**: Components load on-demand
   - Only screens and components needed for navigation are loaded
   - Reduces initial bundle size

4. **Efficient Rendering**:
   - Limit rendered detections (MAX_VISIBLE_DETECTIONS = 100)
   - Virtualization for long lists (implemented in HistoryScreen)
   - Skeleton loaders for perceived performance

### Network Optimization

1. **API Polling**: System health polls every 10 seconds
   - Lightweight request (~1 KB)
   - Doesn't block UI

2. **Audio Playback**:
   - Files loaded on-demand (not preloaded)
   - Supports streaming from API

3. **Service Worker Caching**:
   - Cache static assets after first visit
   - Works offline after initial load

## State Management

### Local State (useState/useReducer)
- UI state (playing, playingIndex, etc.)
- Component-specific state

### Server State (React Query)
- API responses are cached
- Automatic refetching (SSE invalidates on new detections)
- Background refetch intervals

### Global State (Context)
- SSE connection status (SSEContext)
- Shared across components

## Future Enhancements

### Potential Features

1. **Real-time Filters**:
   - Filter detections by species, date range, classifier
   - Apply filters via URL query params

2. **Export/Import**:
   - Export detection logs as CSV/JSON
   - Import settings/configurations

3. **Advanced Charts**:
   - Replace static charts with Recharts/D3.js
   - Interactive activity graphs

4. **Multi-language**:
   - i18n support for internationalization

5. **User Authentication**:
   - Login/registration
   - Role-based access control

### Technical Debt

1. **Refine Error Handling**:
   - More specific error messages
   - User-friendly error UI

2. **Unit Tests**:
   - Add Jest/Vitest tests for hooks and components
   - Target 80%+ code coverage

3. **E2E Tests**:
   - Playwright/Cypress tests for critical paths

4. **Code Splitting**:
   - Dynamic imports for screens not immediately visible
   - Further reduce initial bundle size

## Troubleshooting

### Build Errors

**Error: "Cannot find module"**
- Check import paths use correct relative paths
- Ensure hooks directory exists at `src/hooks/`
- Run `npm install` to ensure dependencies are installed

**Error: TypeScript compilation fails**
- Run `tsc --noEmit` for detailed errors
- Check `tsconfig.json` for correct settings

### Runtime Errors

**Audio doesn't play**
- Check browser console for CORS errors
- Verify `/api/audio/{path}` endpoint is accessible
- Check file name/path in detection record

**API requests fail**
- Verify FastAPI backend is running on `http://localhost:8000`
- Check CORS middleware allows frontend origin
- Verify network connectivity

**PWA not working offline**
- Ensure service worker is registered in `main.tsx`
- Check cache size (should include all static assets)
- Hard reload page after PWA installation

## Resources

- **React Documentation**: https://react.dev
- **Vite Documentation**: https://vitejs.dev
- **React Query Documentation**: https://tanstack.com/query
- **PWA Documentation**: https://web.dev/progressive-web-apps/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/
