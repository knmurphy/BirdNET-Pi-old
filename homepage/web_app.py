"""
Field Station OS - FastHTML Web Application

A Python-native web UI for passive acoustic monitoring.
Built with FastHTML for HTMX-based navigation (no iframe, no full page reload).
"""
import json
import os
import shutil
import sqlite3
import logging
import time
from datetime import datetime
from urllib.parse import quote as url_quote

from starlette.responses import FileResponse, Response
from fasthtml.common import (
    FastHTML, serve,
    Html, Head, Body, Title, Meta, Link, Style, Script,
    Main, Nav, Header,
    Div, H2, H3, P, A, Audio, Source,
)

# Database path - can be overridden via environment variable
DB_PATH = os.environ.get(
    "BIRDNET_DB_PATH",
    os.path.join(os.path.dirname(__file__), '..', 'scripts', 'birds.db')
)

# Recordings path for disk usage calculation
RECORDINGS_PATH = os.environ.get(
    "BIRDNET_RECORDINGS_PATH",
    os.path.expanduser("~/BirdSongs")
)

# Simple time-based cache for recordings size (expensive os.walk)
_RECORDINGS_SIZE_CACHE: dict = {"value": 0.0, "ts": 0.0}
_RECORDINGS_CACHE_TTL = 300  # seconds


def _get_recordings_size_gb() -> float:
    """Return total size of recordings in GB, cached for 5 minutes."""
    now = time.monotonic()
    if now - _RECORDINGS_SIZE_CACHE["ts"] < _RECORDINGS_CACHE_TTL:
        return _RECORDINGS_SIZE_CACHE["value"]
    total_bytes = 0
    if os.path.exists(RECORDINGS_PATH):
        total_bytes = sum(
            os.path.getsize(os.path.join(dirpath, fname))
            for dirpath, _, fnames in os.walk(RECORDINGS_PATH)
            for fname in fnames
        )
    result = total_bytes / (1024 ** 3)
    _RECORDINGS_SIZE_CACHE["value"] = result
    _RECORDINGS_SIZE_CACHE["ts"] = now
    return result

# Station display name shown in the header (override via env var)
STATION_MODEL = os.environ.get("STATION_MODEL", "BirdNET-Pi · RPi 4B")

# Confidence thresholds for visual indicators
CONF_HIGH = 0.80
CONF_MEDIUM = 0.50

# System health warning thresholds
CPU_WARN = 60
CPU_DANGER = 80
TEMP_WARN = 55
TEMP_DANGER = 70
TEMP_GAUGE_MAX = 85   # Maximum temperature used for gauge scaling (°C)
DISK_WARN = 70
DISK_DANGER = 85


def get_today_detection_count() -> int:
    """Return the total number of detections today."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute("SELECT COUNT(*) FROM detections WHERE Date = ?", (today,))
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_today_species_count() -> int:
    """Return the count of distinct species detected today."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date = ?", (today,)
        )
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_total_detection_count() -> int:
    """Return the total number of detections (all time)."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cur = con.execute("SELECT COUNT(*) FROM detections")
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_total_species_count() -> int:
    """Return the count of distinct species (all time)."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cur = con.execute("SELECT COUNT(DISTINCT Com_Name) FROM detections")
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_latest_detection() -> dict | None:
    """Return the most recent detection, or None if unavailable."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        cur = con.execute(
            "SELECT Com_Name, Sci_Name, Date, Time, Confidence, File_Name "
            "FROM detections ORDER BY Date DESC, Time DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            return {
                "com_name": row["Com_Name"],
                "sci_name": row["Sci_Name"],
                "date": row["Date"],
                "time": row["Time"],
                "confidence": row["Confidence"],
                "file_name": row["File_Name"],
            }
        return None
    except sqlite3.Error:
        return None
    finally:
        if con:
            con.close()


def get_hourly_detections() -> dict:
    """Return a dict mapping hour (int 0-23) to detection count for today."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT CAST(strftime('%H', Time) AS INTEGER) as hour, COUNT(*) "
            "FROM detections WHERE Date = ? GROUP BY hour",
            (today,)
        )
        rows = cur.fetchall()
        return {int(row[0]): row[1] for row in rows}
    except sqlite3.Error:
        return {}
    finally:
        if con:
            con.close()


def get_system_health() -> dict:
    """Return system health metrics including disk, database, and recordings size."""
    try:
        disk = shutil.disk_usage("/")
        disk_used_gb = (disk.total - disk.free) / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        disk_percent = (disk_used_gb / disk_total_gb * 100) if disk_total_gb > 0 else 0.0

        db_path = os.path.abspath(DB_PATH)
        db_size_mb = os.path.getsize(db_path) / (1024 ** 2) if os.path.exists(db_path) else 0.0

        recordings_gb = _get_recordings_size_gb()

        return {
            "disk_used_gb": disk_used_gb,
            "disk_total_gb": disk_total_gb,
            "disk_percent": disk_percent,
            "db_size_mb": db_size_mb,
            "recordings_gb": recordings_gb,
        }
    except Exception:
        return {
            "disk_used_gb": 0.0,
            "disk_total_gb": 0.0,
            "disk_percent": 0.0,
            "db_size_mb": 0.0,
            "recordings_gb": 0.0,
        }


# Design System - Dark Theme (adapted from birdnet-field-station.jsx)
APP_CSS = """
:root {
  --bg: #0D0F0B;
  --bg2: #141610;
  --bg3: #1A1D16;
  --border: #252820;
  --border2: #2E3228;
  --text: #F0EAD2;
  --text2: #9A9B8A;
  --text3: #5A5C4E;
  --accent: #C8E6A0;
  --accent2: #9FBD73;
  --amber: #E8C547;
  --amber2: #C4A030;
  --red: #E05252;
  --font-mono: 'DM Mono', 'Courier New', monospace;
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Source Serif 4', Georgia, serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  line-height: 1.5;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── App Shell ── */
.app-shell {
  display: flex;
  flex-direction: column;
  max-width: 430px;
  margin: 0 auto;
  min-height: 100dvh;
  position: relative;
}

/* ── Header ── */
.topbar {
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 12px;
  position: relative;
  z-index: 10;
}
.header-left { display: flex; align-items: center; gap: 10px; }
.station-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 6px var(--amber);
  animation: pulse-amber 2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes pulse-amber {
  0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--amber); }
  50% { opacity: 0.4; box-shadow: 0 0 2px var(--amber); }
}
.station-name {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text2);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  line-height: 1.3;
}
.station-id {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 0.08em;
}
.header-time {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--amber);
  letter-spacing: 0.06em;
}

/* ── Main content area ── */
#content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 64px;
}
#content::-webkit-scrollbar { display: none; }

/* ── Bottom Navigation ── */
.bottom-nav {
  display: flex;
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 430px;
  z-index: 100;
  background: var(--bg);
  border-top: 1px solid var(--border);
}
.bottom-nav a {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 10px 0 12px;
  color: var(--text3);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  transition: color 0.15s;
  position: relative;
}
.bottom-nav a::before {
  content: '';
  position: absolute;
  top: 0; left: 20%; right: 20%;
  height: 1px;
  background: transparent;
  transition: background 0.15s;
}
.bottom-nav a:hover { color: var(--text2); text-decoration: none; }
.bottom-nav a.active { color: var(--accent); }
.bottom-nav a.active::before { background: var(--accent); }
.nav-icon { font-size: 14px; line-height: 1; }

/* ── Summary strip ── */
.summary-strip {
  display: flex;
  border-bottom: 1px solid var(--border);
}
.sum-cell {
  flex: 1;
  padding: 10px 8px;
  border-right: 1px solid var(--border);
  text-align: center;
}
.sum-cell:last-child { border-right: none; }
.sum-val {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 400;
  color: var(--text);
  display: block;
  line-height: 1;
  margin-bottom: 3px;
}
.sum-label {
  font-family: var(--font-mono);
  font-size: 8px;
  color: var(--text3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  display: block;
}

/* ── Section label ── */
.section-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 10px 16px 6px;
  border-bottom: 1px solid var(--border);
}
.section-label-title {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text3);
}
.section-label-meta {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
}

/* ── Spectrogram placeholder ── */
.spectrogram-wrapper {
  height: 80px;
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.spec-label {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

/* ── Detection card (most recent) ── */
.det-card {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.det-label {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.det-comname {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 400;
  color: var(--text);
  line-height: 1.1;
  margin-bottom: 2px;
}
.det-sciname {
  font-family: var(--font-body);
  font-style: italic;
  font-size: 13px;
  font-weight: 300;
  color: var(--text2);
  margin-bottom: 10px;
}
.det-timestamp {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
  position: absolute;
  top: 14px; right: 16px;
}
.conf-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.conf-bar-track {
  flex: 1;
  height: 2px;
  background: var(--border2);
  position: relative;
}
.conf-bar-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  transition: width 0.4s ease;
}
.conf-pct {
  font-family: var(--font-mono);
  font-size: 11px;
  min-width: 36px;
  text-align: right;
}
.audio-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.audio-filename {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.04em;
}

/* ── Detection list rows ── */
.det-row {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  gap: 10px;
  transition: background 0.1s;
}
.det-row:hover { background: var(--bg2); }
.det-row-body { flex: 1; min-width: 0; }
.det-row-name {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 400;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.det-row-sci {
  font-family: var(--font-body);
  font-style: italic;
  font-size: 11px;
  font-weight: 300;
  color: var(--text3);
}
.det-row-conf {
  width: 32px;
  font-family: var(--font-mono);
  font-size: 10px;
  text-align: right;
  flex-shrink: 0;
}
.det-row-time {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
  flex-shrink: 0;
}
.conf-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ── Confidence color coding ── */
.conf-high { color: var(--accent); }
.conf-medium { color: var(--amber); }
.conf-low { color: var(--red); }

/* ── Activity chart ── */
.activity-chart {
  padding: 12px 16px 14px;
  border-bottom: 1px solid var(--border);
}
.chart-title {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
}
.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 56px;
}
.chart-bar-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  height: 100%;
  justify-content: flex-end;
}
.chart-bar {
  width: 100%;
  background: var(--border2);
  min-height: 2px;
}
.chart-bar.active { background: var(--accent2); }
.chart-bar.current { background: var(--amber); }
.chart-hour {
  font-family: var(--font-mono);
  font-size: 7px;
  color: var(--text3);
}

/* ── Species grid ── */
.species-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
.species-card {
  padding: 14px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  transition: background 0.1s;
}
.species-card:nth-child(2n) { border-right: none; }
.species-card:hover { background: var(--bg2); }
.sp-count {
  font-family: var(--font-mono);
  font-size: 22px;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 4px;
}
.sp-name {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 400;
  color: var(--text);
  line-height: 1.2;
  margin-bottom: 2px;
}
.sp-sci {
  font-family: var(--font-body);
  font-style: italic;
  font-size: 10px;
  font-weight: 300;
  color: var(--text3);
  margin-bottom: 6px;
}
.sp-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sp-last {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
}
.trend-up { color: var(--accent); font-size: 11px; }
.trend-down { color: var(--red); font-size: 11px; }
.trend-stable { color: var(--text3); font-size: 11px; }

/* ── Widget (legacy, kept for tests) ── */
.widget {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 12px 14px;
}
.widget-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  font-family: var(--font-mono);
  margin-bottom: 4px;
}
.widget-value {
  font-size: 24px;
  font-weight: 400;
  color: var(--accent);
  font-family: var(--font-display);
}

/* ── Readout grid (stats) ── */
.stat-block {
  padding: 0 0 4px;
  border-bottom: 1px solid var(--border);
}
.stat-block-title {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  padding: 10px 16px 8px;
}
.readout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 16px 14px;
}
.readout { display: flex; flex-direction: column; gap: 2px; }
.readout-label {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.readout-value {
  font-family: var(--font-mono);
  font-size: 20px;
  color: var(--text);
  line-height: 1;
}
.readout-value.accent { color: var(--accent); }
.readout-value.amber { color: var(--amber); }
.readout-value.danger { color: var(--red); }
.readout-unit {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
}
.gauge-row { margin-top: 3px; }
.gauge-track {
  width: 100%;
  height: 2px;
  background: var(--border2);
  position: relative;
}
.gauge-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
}

/* ── Services ── */
.service-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 16px;
  border-bottom: 1px solid var(--border);
}
.service-name {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text2);
  letter-spacing: 0.04em;
}
.service-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.status-dot { width: 5px; height: 5px; border-radius: 50%; }
.status-ok { color: var(--accent2); }
.status-ok .status-dot { background: var(--accent2); }
.status-warn { color: var(--amber); }
.status-warn .status-dot { background: var(--amber); }

/* ── Health grid (legacy, kept for tests) ── */
.health-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}
.health-item {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
}
.health-item:nth-child(2n) { border-right: none; }
.health-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  font-family: var(--font-mono);
  margin-bottom: 4px;
}
.health-value {
  font-size: 16px;
  font-weight: 400;
  color: var(--accent);
  font-family: var(--font-mono);
}
.health-detail {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--font-mono);
  margin-top: 2px;
}

/* ── Error state ── */
.error-message {
  color: var(--red);
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 10px 16px;
  background: var(--bg3);
  border-bottom: 1px solid var(--red);
  border-left: 2px solid var(--red);
  margin: 12px 16px;
}

/* Live status indicator */
.live-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text2);
}
.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text3);
}
.live-dot.connected {
  background: var(--accent);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* Live feed */
.live-feed {
  margin-top: var(--space-4);
}
.live-feed-item {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  margin-bottom: var(--space-2);
  font-family: var(--font-mono);
  font-size: 13px;
  animation: fadeIn 0.3s ease;
}
.live-feed-item .feed-time {
  color: var(--text3);
  font-size: 11px;
}
.live-feed-item .feed-species {
  color: var(--accent);
  font-weight: bold;
}
.live-feed-item .feed-confidence {
  color: var(--text2);
  font-size: 11px;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* HTMX swap transitions */
.htmx-swapping { opacity: 0.5; transition: opacity 0.2s ease; }

/* Hourly activity chart */
.hourly-chart {
  margin-bottom: var(--space-4);
}
.hourly-bar-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
  font-family: var(--font-mono);
  font-size: 12px;
}
.hourly-label {
  width: 40px;
  color: var(--text2);
  text-align: right;
  flex-shrink: 0;
}
.hourly-bar-container {
  flex: 1;
  height: 16px;
  background: var(--bg3);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.hourly-bar {
  height: 100%;
  background: var(--accent);
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
}
.hourly-count {
  width: 40px;
  color: var(--text);
  text-align: right;
  flex-shrink: 0;
}

/* System health section */
.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-4);
}
.health-item {
  background: var(--bg3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}
.health-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text2);
  font-family: var(--font-mono);
  margin-bottom: var(--space-1);
}
.health-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--accent);
  font-family: var(--font-display);
}
.health-detail {
  font-size: 11px;
  color: var(--text3);
  margin-top: var(--space-1);
}

/* Error state */
.error-message {
  color: var(--red);
  font-family: var(--font-mono);
  font-size: 12px;
  padding: var(--space-3);
  background: var(--bg3);
  border-radius: var(--radius-md);
  border: 1px solid var(--red);
}

/* Responsive */
@media (max-width: 640px) {
  .bottom-nav { display: flex; }
  #content { padding-bottom: 72px; }
  .widget-grid { grid-template-columns: 1fr 1fr; }
  .widget-value { font-size: 22px; }
}
"""

# JavaScript for SSE live updates
LIVE_JS = """
(function() {
  var API_URL = %s;
  var evtSrc = null;
  var feedMax = 20;

  function setStatus(connected) {
    var dot = document.getElementById('live-dot');
    var label = document.getElementById('live-label');
    if (dot) dot.className = connected ? 'live-dot connected' : 'live-dot';
    if (label) label.textContent = connected ? 'LIVE' : 'OFFLINE';
  }

  function connect() {
    if (!document.getElementById('live-feed')) return;
    if (evtSrc) { evtSrc.close(); }
    evtSrc = new EventSource(API_URL + '/api/events');

    evtSrc.addEventListener('connected', function() { setStatus(true); });

    evtSrc.addEventListener('detection', function(e) {
      try {
        var d = JSON.parse(e.data);
        addFeedItem(d);
        incrementCounter('today-count');
      } catch(err) {}
    });

    evtSrc.onerror = function() {
      setStatus(false);
      evtSrc.close();
      setTimeout(connect, 5000);
    };
  }

  function addFeedItem(d) {
    var feed = document.getElementById('live-feed');
    if (!feed) return;
    var empty = document.getElementById('feed-empty');
    if (empty) empty.remove();
    var conf = (d.confidence * 100).toFixed(0);
    var item = document.createElement('div');
    item.className = 'live-feed-item';
    item.innerHTML = '<span class="feed-time">' + d.time + '</span> '
      + '<span class="feed-species">' + escapeHtml(d.com_name) + '</span> '
      + '<span class="feed-confidence">(' + conf + '%%)</span>';
    feed.insertBefore(item, feed.firstChild);
    while (feed.children.length > feedMax) { feed.removeChild(feed.lastChild); }
  }

  function incrementCounter(id) {
    var el = document.getElementById(id);
    if (el) {
      var n = parseInt(el.textContent, 10);
      if (!isNaN(n)) el.textContent = String(n + 1);
    }
  }

  function escapeHtml(s) {
    var d = document.createElement('div');
    d.appendChild(document.createTextNode(s));
    return d.innerHTML;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', connect);
  } else {
    connect();
  }
})();
"""


# HTMX polling configuration (shared between initial render and partials)
DASHBOARD_STATS_POLL = {
    "hx-get": "/app/partials/dashboard-stats",
    "hx-trigger": "every 30s",
    "hx-swap": "outerHTML",
}
SYSTEM_HEALTH_POLL = {
    "hx-get": "/app/partials/system-health",
    "hx-trigger": "every 60s",
    "hx-swap": "outerHTML",
}

# Create the FastHTML application
app = FastHTML()


@app.get("/audio/{file_name:path}")
def serve_audio(file_name: str):
    """Serve a recording audio file, guarding against path traversal."""
    recordings_dir = os.path.realpath(RECORDINGS_PATH)
    requested = os.path.realpath(os.path.join(recordings_dir, file_name))
    # Only allow paths strictly inside the recordings directory
    if not requested.startswith(recordings_dir + os.sep):
        return Response(status_code=404)
    if not os.path.isfile(requested):
        return Response(status_code=404)
    return FileResponse(requested, media_type="audio/wav")


@app.get("/app/dashboard")
def dashboard():
    """Render the dashboard page."""
    return _shell(_dashboard_content(), "/app/dashboard")


def _dashboard_content():
    """Generate the dashboard content using direct database queries."""
    today_count = get_today_detection_count()
    species_count = get_today_species_count()
    latest = get_latest_detection()

    if latest:
        latest_widget = Div(
            Div("Latest Detection", cls="widget-label"),
            Div(latest["com_name"], cls="widget-value", style="font-size: 14px;"),
            cls="widget"
        )
    else:
        latest_widget = Div(
            Div("Latest Detection", cls="widget-label"),
            Div("No detections yet", cls="widget-value", style="font-size: 14px;"),
            cls="widget"
        )

    return Div(
        H2("Dashboard"),
        Div(
            Div(
                Div("Today's Detections", cls="widget-label"),
                Div(str(today_count), cls="widget-value", id="today-count"),
                cls="widget"
            ),
            Div(
                Div("Today's Species", cls="widget-label"),
                Div(str(species_count), cls="widget-value", id="species-count"),
                cls="widget"
            ),
            *(
                [Div(
                    Div("Top Species", cls="widget-label"),
                    Div(
                        ", ".join([s["com_name"] for s in top_species[:3]]),
                        cls="widget-value", style="font-size: 14px;",
                        id="top-species",
                    ),
                    cls="widget"
                )] if top_species else []
            ),
            cls="widget-grid",
            id="dashboard-stats",
            **DASHBOARD_STATS_POLL,
        ),
        # Live detection feed
        H3("Live Feed"),
        Div(
            Span("", id="live-dot", cls="live-dot"),
            Span("CONNECTING", id="live-label"),
            cls="live-indicator",
        ),
        latest_widget,
        cls="widget-grid"
    )


def _shell(content, current_path: str = "/app/dashboard"):
    """Wrap content in the app shell with header and navigation."""
    current_time = datetime.now().strftime("%H:%M:%S")

    tabs = [
        ("⬤", "LIVE", "/app/dashboard", "Dashboard – Live view"),
        ("☰", "LOG", "/app/detections", "Detection log"),
        ("◈", "SPECIES", "/app/species", "Species catalog"),
        ("∿", "STATS", "/app/stats", "Statistics"),
        ("⚙", "CONFIG", "/app/settings", "Configuration"),
    ]

    nav_links = [
        A(
            Span(icon, cls="nav-icon", aria_hidden="true"),
            label,
            href=path,
            cls="active" if current_path == path else "",
            aria_label=aria_label,
        )
        for icon, label, path, aria_label in tabs
    ]

    # Safely inject the API URL into the SSE JavaScript via JSON encoding
    live_js = LIVE_JS % json.dumps(API_BASE_URL.rstrip("/"))

    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Meta(name="theme-color", content="#0D0F0B"),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
            Link(
                rel="stylesheet",
                href=(
                    "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500"
                    "&family=Fraunces:wght@400;700"
                    "&family=Source+Serif+4:ital,wght@0,400;1,400&display=swap"
                ),
            ),
            Title("Field Station"),
            Style(APP_CSS),
            Script(src="https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js",
                   integrity="sha384-OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb",
                   crossorigin="anonymous"),
        ),
        Body(
            Div(
                Header(
                    Div(
                        Div(cls="station-dot"),
                        Div(
                            Div("FIELD STATION", cls="station-name"),
                            Div(STATION_MODEL, cls="station-id"),
                        ),
                        cls="header-left",
                    ),
                    Div(current_time, cls="header-time", id="clock"),
                    cls="topbar",
                ),
                Main(content, id="content"),
                Nav(*nav_links, cls="bottom-nav", aria_label="Main navigation"),
                cls="app-shell",
            ),
            Script(live_js),
        ),
        Div(*bars, cls="chart-bars"),
        cls="activity-chart",
    )


@app.get("/app/detections")
def detections():
    """Render the detections page."""
    return _shell(_detections_content(), "/app/detections")


def _confidence_class(confidence: float) -> str:
    """Return the appropriate confidence color class."""
    if confidence >= CONF_HIGH:
        return "conf-high"
    elif confidence >= CONF_MEDIUM:
        return "conf-medium"
    else:
        return "conf-low"


def _conf_dot_color(confidence: float) -> str:
    """Return dot color for confidence level."""
    if confidence >= CONF_HIGH:
        return "var(--accent2)"
    elif confidence >= CONF_MEDIUM:
        return "var(--amber2)"
    else:
        return "var(--red)"


def _detections_content():
    """Generate the detections list content using direct database queries."""
    con = None
    rows = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT Com_Name, Sci_Name, Time, Confidence, File_Name "
            "FROM detections WHERE Date = ? ORDER BY Time DESC LIMIT 50",
            (today,)
        )
        rows = cur.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error in _detections_content: {e}")
        return Div(
            H2("Today's Detections"),
            P("Unable to load detections", cls="error-message"),
        )
    finally:
        if con:
            con.close()

    if not rows:
        return Div(H2("Today's Detections"), P("No detections yet today."))

    items = []
    for row in rows:
        com_name, sci_name, time, confidence, file_name = row
        conf_class = _confidence_class(confidence or 0.0)
        audio_el = Audio(
            Source(src=f"/audio/{file_name}", type="audio/wav"),
            controls=True,
        ) if file_name else P("(no audio)")
        items.append(
            Div(
                Div(f"{com_name} ({sci_name}) — {time} — {(confidence or 0)*100:.0f}%",
                    cls=conf_class),
                audio_el,
                cls="detection-item"
            )
        )

    return Div(H2("Today's Detections"), *items)


@app.get("/app/species")
def species():
    """Render the species page."""
    return _shell(_species_content(), "/app/species")


def _species_content():
    """Generate the species list content using direct database queries."""
    con = None
    rows = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT Com_Name, Sci_Name, COUNT(*) as cnt, MAX(Confidence) as max_conf "
            "FROM detections WHERE Date = ? GROUP BY Sci_Name ORDER BY Com_Name ASC",
            (today,)
        )
        rows = cur.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error in _species_content: {e}")
        return Div(
            H2("Today's Species"),
            P("Error loading species", cls="error-message"),
        )
    finally:
        if con:
            con.close()

    if not rows:
        return Div(H2("Today's Species"), P("No species detected today."))

    items = [
        Div(
            f"{row[0]} ({row[1]}) — {row[2]} detections (max: {(row[3] or 0)*100:.0f}%)",
            cls=_confidence_class(row[3] or 0.0)
        )
        for row in rows
    ]
    return Div(H2("Today's Species"), *items)


@app.get("/app/stats")
def stats():
    """Render the stats page."""
    return _shell(_stats_content(), "/app/stats")


def _hourly_activity_section() -> Div:
    """Generate hourly activity bar chart for today using database data."""
    hourly_data = get_hourly_detections()

    if not hourly_data:
        return Div(
            H3("Today's Activity"),
            P("No detections yet today.", cls="text2"),
            cls="hourly-chart"
        )

    max_count = max(hourly_data.values()) if hourly_data else 1

    bar_rows = []
    for hour in range(24):
        count = hourly_data.get(hour, 0)
        bar_width = (count / max_count * 100) if max_count > 0 else 0
        bar_rows.append(
            Div(
                Div("Today's Activity", cls="section-label-title"),
                cls="section-label",
            ),
            Div(
                "No detections yet today.",
                style="font-family:var(--font-mono);font-size:11px;color:var(--text3);padding:16px;",
            ),
        )

    return Div(
        Div(
            Div("Today's Activity", cls="section-label-title"),
            cls="section-label",
        ),
        chart,
    )


def _system_health_section() -> Div:
    """Generate system health widgets using direct system queries."""
    health = get_system_health()

    return Div(
        H3("System Health"),
        Div(
            Div(
                Div("Disk Usage", cls="health-label"),
                Div(f"{health['disk_used_gb']:.1f} / {health['disk_total_gb']:.0f} GB", cls="health-value"),
                Div(f"{health['disk_percent']:.1f}% used", cls="health-detail"),
                cls="health-item"
            ),
            Div(
                Div("Database", cls="health-label"),
                Div(f"{health['db_size_mb']:.1f} MB", cls="health-value"),
                cls="health-item"
            ),
            Div("Unable to load system data.", cls="error-message"),
        )

    cpu = system.get("cpu_percent", 0)
    temp = system.get("temperature_celsius", 0)
    disk_used = system.get("disk_used_gb", 0)
    disk_total = system.get("disk_total_gb", 1)
    disk_pct = int(disk_used / disk_total * 100) if disk_total > 0 else 0
    uptime_s = system.get("uptime_seconds", 0)
    uptime_h = uptime_s / 3600

    cpu_color = "var(--red)" if cpu > CPU_DANGER else "var(--amber)" if cpu > CPU_WARN else "var(--accent)"
    temp_color = "var(--red)" if temp > TEMP_DANGER else "var(--amber)" if temp > TEMP_WARN else "var(--text)"
    disk_color = "var(--red)" if disk_pct > DISK_DANGER else "var(--amber)" if disk_pct > DISK_WARN else "var(--accent)"

    def readout(label, value, unit="", gauge_pct=None, color="var(--text)"):
        children = [
            Div(label, cls="readout-label"),
            Div(
                Div("Recordings", cls="health-label"),
                Div(f"{health['recordings_gb']:.2f} GB", cls="health-value"),
                cls="health-item"
            ),
        ]
        if gauge_pct is not None:
            children.append(
                Div(
                    Div(cls="gauge-fill", style=f"width:{gauge_pct}%;background:{color}"),
                    cls="gauge-track",
                    style="margin-top:4px;",
                )
            )
        return Div(*children, cls="readout")

    return Div(
        Div(
            Div("System Health", cls="section-label-title"),
            cls="section-label",
        ),
        Div(
            readout("CPU Load", f"{cpu:.0f}", "%", int(cpu), cpu_color),
            readout("Temperature", f"{temp:.1f}", "°C", int(temp / TEMP_GAUGE_MAX * 100), temp_color),
            readout("Disk Usage", f"{disk_used:.1f}/{disk_total:.0f}", "GB", disk_pct, disk_color),
            readout("Uptime", f"{uptime_h:.1f}", "h"),
            cls="readout-grid",
            style="padding: 12px 16px 14px;",
        ),
        id="system-health",
        **SYSTEM_HEALTH_POLL,
    )


def _stats_content():
    """Generate the stats content using direct database queries."""
    today_count = get_today_detection_count()
    total_count = get_total_detection_count()
    today_species = get_today_species_count()
    total_species = get_total_species_count()

    return Div(
        H2("Statistics"),
        Div(
            Div("Today's Detections", cls="widget-label"),
            Div(f"{today_count:,}", cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Total Detections", cls="widget-label"),
            Div(f"{total_count:,}", cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Today's Species", cls="widget-label"),
            Div(f"{today_species:,}", cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Total Species", cls="widget-label"),
            Div(f"{total_species:,}", cls="widget-value"),
            cls="widget"
        ),
        _hourly_activity_section(),
        _system_health_section(),
    )


@app.get("/app/settings")
def settings():
    """Render the settings page."""
    return _shell(_settings_content(), "/app/settings")


def _settings_content():
    """Generate the settings content."""
    return Div(
        H2("Settings"),
        P("Settings are managed via the BirdNET-Pi configuration file.", cls="text2"),
    )


# --- HTMX Partial Routes (return fragments, not full pages) ---


@app.get("/app/partials/dashboard-stats")
def partial_dashboard_stats():
    """Return just the dashboard stats widget grid (for HTMX polling)."""
    summary = api_get("/api/detections/today/summary")

    if summary is None:
        return Div(
            P("Unable to refresh stats.", cls="error-message"),
            cls="widget-grid", id="dashboard-stats",
            **DASHBOARD_STATS_POLL,
        )

    today_count = summary.get("total_detections", 0)
    species_count = summary.get("species_count", 0)
    top_species = summary.get("top_species", [])

    children = [
        Div(
            Div("Today's Detections", cls="widget-label"),
            Div(str(today_count), cls="widget-value", id="today-count"),
            cls="widget"
        ),
        Div(
            Div("Today's Species", cls="widget-label"),
            Div(str(species_count), cls="widget-value", id="species-count"),
            cls="widget"
        ),
    ]

    if top_species:
        children.append(
            Div(
                Div("Top Species", cls="widget-label"),
                Div(
                    ", ".join([s["com_name"] for s in top_species[:3]]),
                    cls="widget-value", style="font-size: 14px;",
                    id="top-species",
                ),
                cls="widget"
            )
        )

    return Div(
        *children,
        cls="widget-grid", id="dashboard-stats",
        **DASHBOARD_STATS_POLL,
    )


@app.get("/app/partials/system-health")
def partial_system_health():
    """Return just the system health section (for HTMX polling)."""
    return _system_health_section()


if __name__ == "__main__":
    serve(port=8502)
