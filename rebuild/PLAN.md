# BirdNET-Pi Modern Rebuild — Final Tech Stack

## Context

BirdNET-Pi is a real-time passive acoustic bird classifier for Raspberry Pi. The current codebase is mid-migration (legacy PHP/Streamlit alongside newer FastAPI/FastHTML), with TFLite as the ML runtime (hard to install on ARM), a half-finished SQLite→DuckDB migration, and a complex multi-script install process.

**Goal:** Rebuild as a home bird observation platform — audio detection, real-time dashboard, PWA with smart notifications, citizen science data sharing. Clean, snappy, easy to install and update.

**Key insight:** GitHub Actions builds the frontend (SvelteKit) as a release artifact. The Pi never needs Node.js. This unlocks PWA + push notifications + Tailwind without any build toolchain on the device.

---

## Final Stack

| Layer | Technology | Replaces |
|-------|-----------|---------|
| ML Runtime | ONNX Runtime | TFLite (300MB → 40MB, 3x faster) |
| Preprocessing | librosa | Keep — must match training preprocessing |
| Python env | Python 3.12 + uv | pip + venv (100x faster installs) |
| API | FastAPI (single port) | Split :8003/:8502 ports |
| Frontend | SvelteKit + Tailwind CSS | FastHTML + PHP + Streamlit |
| PWA | SvelteKit PWA adapter | — |
| Spectrogram | WaveSurfer.js (clips) + Web Audio API (live) | sox PNG generation |
| Database | SQLite WAL writes + DuckDB ATTACH reads | Incomplete SQLite→DuckDB migration |
| Config | TOML (stdlib tomllib) | Shell-script birdnet.conf |
| Pi deploy | systemd + uv + .deb from CI | 70 shell scripts |
| Dev/cloud | Docker Compose | — |
| CI/CD | GitHub Actions | — |
| Reverse proxy | Caddy | Keep |
| Notifications | Apprise + Web Push (PWA) | Apprise only |
| Citizen science | BirdWeather (keep) + eBird CSV export | BirdWeather only |

---

## Key Technical Decisions

### ONNX Runtime (replaces TFLite)

TFLite requires platform-specific wheel compilation on ARM — 20-min install, fragile updates. ONNX Runtime is a prebuilt wheel on all platforms.

**One-time model conversion** (runs in Google Colab, no Pi hardware needed):
```bash
pip install tf2onnx onnx
python -m tf2onnx.convert --tflite BirdNET_model.tflite --output birdnet.onnx
```

Caveat: BirdNET model uses RFFT layers that ONNX doesn't support inside the graph. The ONNX model handles neural network inference only; librosa computes the mel-spectrogram beforehand. This is the standard production pattern. A `notebooks/convert_model.ipynb` Colab notebook ships with the repo.

### Database: SQLite WAL + DuckDB ATTACH

DuckDB is OLAP — excellent for analytics, bad for 1-5 writes/second. SQLite WAL is the right write store. But DuckDB can ATTACH directly to a SQLite file and query it:

```python
# Write path (analysis daemon)
conn = sqlite3.connect("birds.db")
conn.execute("PRAGMA journal_mode=WAL")

# Read path (API — analytics queries)
duckdb.connect().execute("ATTACH 'birds.db' AS db (TYPE SQLITE)")
# 12-35x faster aggregations than raw SQLite
```

One file, two query engines, no migration needed. Eliminates the half-finished SQLite→DuckDB migration entirely.

### SvelteKit + CI/CD

GitHub Actions builds the SvelteKit frontend on every tagged release:
```yaml
jobs:
  build-frontend:    # svelte build + tailwind purge → /dist/
  build-backend:     # uv pip compile → requirements.lock
  package-deb:       # fpm → birdnetpi_1.0.0_arm64.deb
  build-docker:      # buildx multi-arch → ghcr.io/birdnetpi:latest
```

The `.deb` package installs via apt — the best Pi UX. Docker Compose ships as an alternative for dev/cloud/x86.

**Why not Docker as primary for Pi:** `/dev/snd` passthrough is finicky with ALSA; Docker's overlay filesystem accelerates SD card wear; daemon overhead ~80MB RAM; image downloads are 1-2GB (slow on rural internet).

### Audio Capture

**sounddevice** as default (Python-native, no subprocess), **arecord** as config fallback for ALSA quirks. Config option in `config.toml`:
```toml
[recording]
backend = "sounddevice"  # or "arecord"
```

### eBird Compatibility

eBird has no write API — automated submission is not possible. BirdWeather's API already includes `ebirdCode` per species. The approach:
1. Store `ebird_code TEXT` in the detections schema (populated from BirdWeather)
2. Build a CSV export in eBird's spreadsheet upload format
3. Users manually import to eBird weekly/monthly from the dashboard

Schema cost: one field. Export cost: one function. Future-compatible from day one.

### Spectrogram Visualization

**WaveSurfer.js** for stored detection clip playback:
- Open source, browser-native, spectrogram plugin
- Custom colorMap function — bespoke palette, artistically designed (not Merlin's warm orange/purple)
- WaveSurfer accepts any 0→1 amplitude→RGB mapping; full creative freedom
- Waveform + spectrogram stacked view per detection card
- No server-side image generation

**Web Audio API** (`AnalyserNode` + Canvas 2D) for real-time live view:
- Stream from Pi mic via WebSocket
- Scrolling spectrogram on dashboard
- ~200 lines of TypeScript in a Svelte component

Sox-generated PNG spectrograms dropped (or kept as thumbnail fallback only).

---

## Database Schema (additions to existing)

```sql
-- Existing columns kept as-is
-- New columns added:
ALTER TABLE detections ADD COLUMN ebird_code TEXT;      -- e.g., "amerob"
ALTER TABLE detections ADD COLUMN source TEXT DEFAULT 'audio';  -- future: 'visual', 'manual'
ALTER TABLE detections ADD COLUMN validation_status TEXT DEFAULT 'unvalidated';
```

---

## Architecture

```
[USB Mic]
    ↓
[sounddevice (or arecord fallback)]
    ↓
[asyncio queue]
    ↓
[librosa → mel-spectrogram]
    ↓
[ONNX Runtime → BirdNET inference]
    ↓
[SQLite WAL write] ──→ [Apprise notifications]
    │                 ──→ [BirdWeather sync + ebird_code lookup]
    │                 ──→ [MQTT publish (optional)]
    │                 ──→ [Web Push (rare species)]
    ↓
[EventBus.publish()]
    ↓
┌────────────────────────────────────────────┐
│         FastAPI app (port 8080)            │
│  /api/*    → DuckDB ATTACH queries         │
│  /app/*    → SvelteKit static files        │
│  /events   → SSE stream                   │
│  /audio/*  → detection clip files         │
│  /ws       → WebSocket (live spectrogram)  │
└──────────────────┬─────────────────────────┘
                   ↓
              Caddy :80/443
                   ↓
        SvelteKit PWA (mobile/browser)
        - Live dashboard with spectrogram
        - Detection feed with WaveSurfer
        - Rare species push notifications
        - eBird CSV export
```

---

## What Gets Deleted

- All PHP (`homepage/*.php`, `scripts/*.php`, `scripts/config.php`)
- Streamlit dependency
- TFLite / TensorFlow
- GoTTY, phpSysInfo
- 60+ of 70 install shell scripts
- Cron jobs (replaced by asyncio schedulers in-process)
- FastHTML

---

## Verification Plan

1. `uv sync` completes in < 3 minutes on Pi 4
2. ONNX inference returns same top-species results as TFLite on a sample `.wav`
3. `curl localhost:8080/api/detections` returns JSON with `ebird_code` populated
4. SvelteKit dashboard loads, SSE stream delivers live detection events
5. WaveSurfer.js spectrogram renders on a detection card audio player
6. Web Audio API live spectrogram is visible and scrolling on dashboard
7. eBird CSV export downloads a correctly formatted spreadsheet
8. BirdWeather sync confirms detections are received
9. PWA installs to homescreen on iOS Safari and Android Chrome
10. Simulated rare-species detection triggers a Web Push notification
11. `.deb` installs cleanly on fresh RaspiOS Bookworm, systemd service starts
12. `sudo apt upgrade birdnetpi` completes in < 60 seconds
