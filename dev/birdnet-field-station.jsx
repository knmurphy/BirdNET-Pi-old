import { useState, useEffect, useRef, useCallback } from "react";

// ─── Mock Data ────────────────────────────────────────────────────────────────
const MOCK_DETECTIONS = [
  { id: 1, com: "Black-capped Chickadee", sci: "Poecile atricapillus", conf: 0.97, time: "07:42:11", date: "2025-02-24", file: "chickadee_07421.wav" },
  { id: 2, com: "American Robin", sci: "Turdus migratorius", conf: 0.91, time: "07:38:44", date: "2025-02-24", file: "robin_07384.wav" },
  { id: 3, com: "Dark-eyed Junco", sci: "Junco hyemalis", conf: 0.88, time: "07:31:02", date: "2025-02-24", file: "junco_07310.wav" },
  { id: 4, com: "House Finch", sci: "Haemorhous mexicanus", conf: 0.79, time: "07:22:58", date: "2025-02-24", file: "finch_07225.wav" },
  { id: 5, com: "Steller's Jay", sci: "Cyanocitta stelleri", conf: 0.95, time: "07:18:33", date: "2025-02-24", file: "jay_07183.wav" },
  { id: 6, com: "Red-tailed Hawk", sci: "Buteo jamaicensis", conf: 0.84, time: "06:59:47", date: "2025-02-24", file: "hawk_06594.wav" },
  { id: 7, com: "Song Sparrow", sci: "Melospiza melodia", conf: 0.76, time: "06:44:12", date: "2025-02-24", file: "sparrow_06441.wav" },
  { id: 8, com: "Spotted Towhee", sci: "Pipilo maculatus", conf: 0.82, time: "06:31:05", date: "2025-02-24", file: "towhee_06310.wav" },
  { id: 9, com: "American Crow", sci: "Corvus brachyrhynchos", conf: 0.99, time: "06:15:28", date: "2025-02-24", file: "crow_06152.wav" },
  { id: 10, com: "Pine Siskin", sci: "Spinus pinus", conf: 0.73, time: "05:58:41", date: "2025-02-24", file: "siskin_05584.wav" },
  { id: 11, com: "White-crowned Sparrow", sci: "Zonotrichia leucophrys", conf: 0.87, time: "05:44:19", date: "2025-02-24", file: "wcsparrow_05441.wav" },
  { id: 12, com: "Northern Flicker", sci: "Colaptes auratus", conf: 0.92, time: "05:32:07", date: "2025-02-24", file: "flicker_05320.wav" },
];

const MOCK_SPECIES = [
  { com: "Black-capped Chickadee", sci: "Poecile atricapillus", count: 47, lastSeen: "07:42", maxConf: 0.97, trend: "up" },
  { com: "American Robin", sci: "Turdus migratorius", count: 31, lastSeen: "07:38", maxConf: 0.91, trend: "up" },
  { com: "American Crow", sci: "Corvus brachyrhynchos", count: 28, lastSeen: "06:15", maxConf: 0.99, trend: "stable" },
  { com: "Steller's Jay", sci: "Cyanocitta stelleri", count: 22, lastSeen: "07:18", maxConf: 0.95, trend: "up" },
  { com: "Dark-eyed Junco", sci: "Junco hyemalis", count: 19, lastSeen: "07:31", maxConf: 0.88, trend: "stable" },
  { com: "Northern Flicker", sci: "Colaptes auratus", count: 14, lastSeen: "05:32", maxConf: 0.92, trend: "down" },
  { com: "House Finch", sci: "Haemorhous mexicanus", count: 11, lastSeen: "07:22", maxConf: 0.79, trend: "stable" },
  { com: "Spotted Towhee", sci: "Pipilo maculatus", count: 9, lastSeen: "06:31", maxConf: 0.82, trend: "up" },
  { com: "Song Sparrow", sci: "Melospiza melodia", count: 8, lastSeen: "06:44", maxConf: 0.76, trend: "down" },
  { com: "Red-tailed Hawk", sci: "Buteo jamaicensis", count: 5, lastSeen: "06:59", maxConf: 0.84, trend: "stable" },
  { com: "Pine Siskin", sci: "Spinus pinus", count: 4, lastSeen: "05:58", maxConf: 0.73, trend: "up" },
  { com: "White-crowned Sparrow", sci: "Zonotrichia leucophrys", count: 3, lastSeen: "05:44", maxConf: 0.87, trend: "stable" },
];

const HOURLY_DATA = [
  { h: "00", count: 2 }, { h: "01", count: 0 }, { h: "02", count: 1 }, { h: "03", count: 3 },
  { h: "04", count: 8 }, { h: "05", count: 24 }, { h: "06", count: 41 }, { h: "07", count: 58 },
  { h: "08", count: 47 }, { h: "09", count: 33 }, { h: "10", count: 22 }, { h: "11", count: 18 },
  { h: "12", count: 14 }, { h: "13", count: 12 }, { h: "14", count: 15 }, { h: "15", count: 19 },
  { h: "16", count: 28 }, { h: "17", count: 34 }, { h: "18", count: 31 }, { h: "19", count: 11 },
  { h: "20", count: 5 }, { h: "21", count: 3 }, { h: "22", count: 1 }, { h: "23", count: 0 },
];

const SYSTEM_STATS = {
  cpu: 34,
  temp: 52.4,
  disk: 67,
  uptime: "14d 06h 33m",
  detectionRate: 12,
  model: "BirdNET_6K_V2.4",
  sampleRate: "48000 Hz",
  location: "47.6°N 122.3°W",
};

// ─── Styles ────────────────────────────────────────────────────────────────────
const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,300;1,9..144,400&family=DM+Mono:ital,wght@0,300;0,400;1,300&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

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
    --font-serif: 'Fraunces', Georgia, serif;
    --font-mono: 'DM Mono', 'Courier New', monospace;
    --font-body: 'Source Serif 4', Georgia, serif;
  }

  html, body, #root { height: 100%; background: var(--bg); color: var(--text); }

  .app {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-width: 430px;
    margin: 0 auto;
    background: var(--bg);
    position: relative;
    overflow: hidden;
    font-family: var(--font-body);
  }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px 12px;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
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

  /* Screen area */
  .screen {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  .screen::-webkit-scrollbar { display: none; }

  /* Bottom Nav */
  .bottom-nav {
    display: flex;
    border-top: 1px solid var(--border);
    background: var(--bg);
    z-index: 10;
    position: relative;
  }
  .nav-btn {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    padding: 10px 0 12px;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text3);
    transition: color 0.15s;
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    position: relative;
  }
  .nav-btn.active { color: var(--accent); }
  .nav-btn .nav-icon { font-size: 16px; line-height: 1; }
  .nav-btn::after {
    content: '';
    position: absolute;
    top: 0; left: 20%; right: 20%;
    height: 1px;
    background: transparent;
    transition: background 0.15s;
  }
  .nav-btn.active::after { background: var(--accent); }

  /* ─── LIVE SCREEN ─── */
  .spectrogram-wrapper {
    position: relative;
    height: 120px;
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    overflow: hidden;
  }
  .spectrogram-canvas { width: 100%; height: 100%; display: block; }
  .spec-label {
    position: absolute;
    top: 8px; left: 10px;
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--amber2);
    letter-spacing: 0.15em;
    text-transform: uppercase;
  }
  .spec-freq-labels {
    position: absolute;
    right: 8px;
    top: 0; bottom: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 6px 0;
  }
  .spec-freq {
    font-family: var(--font-mono);
    font-size: 8px;
    color: var(--text3);
  }

  .live-top-detection {
    padding: 16px;
    border-bottom: 1px solid var(--border);
    position: relative;
    animation: slide-in 0.4s ease-out;
  }
  @keyframes slide-in {
    from { opacity: 0; transform: translateY(-8px); }
    to { opacity: 1; transform: translateY(0); }
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
    font-family: var(--font-serif);
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
    margin-bottom: 12px;
  }
  .conf-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
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
    background: var(--accent);
    transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .conf-pct {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--accent);
    min-width: 36px;
    text-align: right;
  }
  .det-time-stamp {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text3);
    position: absolute;
    top: 16px; right: 16px;
  }
  .audio-player-mock {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border: 1px solid var(--border2);
    background: var(--bg3);
  }
  .play-btn {
    width: 28px; height: 28px;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid var(--border2);
    background: var(--bg);
    cursor: pointer;
    color: var(--accent);
    font-size: 10px;
    flex-shrink: 0;
    transition: background 0.15s;
  }
  .play-btn:hover { background: var(--bg3); }
  .waveform-mock {
    flex: 1;
    height: 28px;
    display: flex;
    align-items: center;
    gap: 1px;
  }
  .waveform-bar {
    flex: 1;
    background: var(--border2);
    border-radius: 0;
    transition: height 0.1s;
  }
  .filename-label {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text3);
    letter-spacing: 0.06em;
    white-space: nowrap;
  }

  /* Detection list rows */
  .det-list { }
  .det-row {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    gap: 12px;
    cursor: pointer;
    transition: background 0.1s;
  }
  .det-row:hover { background: var(--bg2); }
  .det-row-conf {
    width: 32px;
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text2);
    text-align: right;
    flex-shrink: 0;
  }
  .det-row-conf.high { color: var(--accent2); }
  .det-row-body { flex: 1; min-width: 0; }
  .det-row-name {
    font-family: var(--font-serif);
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
  .det-row-time {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text3);
    flex-shrink: 0;
  }
  .conf-dot {
    width: 4px; height: 4px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  /* ─── LOG SCREEN ─── */
  .log-header {
    padding: 16px;
    border-bottom: 1px solid var(--border);
  }
  .screen-title {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text3);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }
  .day-strip {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding-bottom: 2px;
    scrollbar-width: none;
  }
  .day-strip::-webkit-scrollbar { display: none; }
  .day-chip {
    flex-shrink: 0;
    padding: 5px 10px;
    border: 1px solid var(--border2);
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text2);
    cursor: pointer;
    background: none;
    letter-spacing: 0.06em;
    transition: all 0.1s;
  }
  .day-chip.active {
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(200,230,160,0.06);
  }
  .search-row {
    display: flex;
    align-items: center;
    border-bottom: 1px solid var(--border);
    background: var(--bg2);
  }
  .search-icon {
    padding: 0 12px;
    color: var(--text3);
    font-size: 12px;
    font-family: var(--font-mono);
  }
  .search-input {
    flex: 1;
    padding: 11px 0;
    background: none;
    border: none;
    outline: none;
    color: var(--text);
    font-family: var(--font-body);
    font-size: 14px;
  }
  .search-input::placeholder { color: var(--text3); }
  .sort-strip {
    display: flex;
    border-bottom: 1px solid var(--border);
    background: var(--bg2);
  }
  .sort-btn {
    flex: 1;
    padding: 8px;
    background: none;
    border: none;
    border-right: 1px solid var(--border);
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text3);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    transition: color 0.1s;
  }
  .sort-btn:last-child { border-right: none; }
  .sort-btn.active { color: var(--accent); }

  /* ─── SPECIES SCREEN ─── */
  .species-header {
    padding: 16px;
    border-bottom: 1px solid var(--border);
  }
  .species-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
  }
  .species-card {
    padding: 14px;
    border-bottom: 1px solid var(--border);
    border-right: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.1s;
  }
  .species-card:nth-child(2n) { border-right: none; }
  .species-card:hover { background: var(--bg2); }
  .sp-count {
    font-family: var(--font-mono);
    font-size: 24px;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 4px;
  }
  .sp-name {
    font-family: var(--font-serif);
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
  .trend-arrow { font-size: 10px; }
  .trend-up { color: var(--accent); }
  .trend-down { color: var(--red); }
  .trend-stable { color: var(--text3); }

  /* ─── STATION SCREEN ─── */
  .station-screen { padding: 0; }
  .stat-block {
    padding: 16px;
    border-bottom: 1px solid var(--border);
  }
  .stat-block-title {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text3);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 14px;
  }
  .readout-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .readout {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .readout-label {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text3);
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  .readout-value {
    font-family: var(--font-mono);
    font-size: 22px;
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
  .gauge-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 4px;
  }
  .gauge-track {
    flex: 1;
    height: 2px;
    background: var(--border2);
    position: relative;
  }
  .gauge-fill {
    position: absolute;
    left: 0; top: 0; bottom: 0;
  }
  .service-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
  }
  .service-row:last-child { border-bottom: none; }
  .service-name {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text2);
    letter-spacing: 0.06em;
  }
  .service-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  .status-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
  }
  .status-ok { color: var(--accent2); }
  .status-ok .status-dot { background: var(--accent2); }
  .status-warn { color: var(--amber); }
  .status-warn .status-dot { background: var(--amber); }
  .ctrl-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .ctrl-btn {
    padding: 12px;
    border: 1px solid var(--border2);
    background: none;
    color: var(--text2);
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s;
  }
  .ctrl-btn:hover { border-color: var(--accent); color: var(--accent); }
  .ctrl-btn.danger:hover { border-color: var(--red); color: var(--red); }
  .ctrl-btn-label { font-size: 8px; color: var(--text3); margin-bottom: 6px; display: block; }

  /* ─── Activity Chart ─── */
  .activity-chart {
    padding: 16px;
    border-bottom: 1px solid var(--border);
  }
  .chart-title {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text3);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
  }
  .chart-bars {
    display: flex;
    align-items: flex-end;
    gap: 2px;
    height: 64px;
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
    transition: background 0.1s;
  }
  .chart-bar.active { background: var(--accent); }
  .chart-bar.current { background: var(--amber); }
  .chart-hour {
    font-family: var(--font-mono);
    font-size: 7px;
    color: var(--text3);
    text-align: center;
  }

  /* Notification toast */
  .toast {
    position: fixed;
    bottom: 70px;
    left: 50%; transform: translateX(-50%);
    background: var(--bg3);
    border: 1px solid var(--accent);
    padding: 10px 16px;
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--accent);
    letter-spacing: 0.1em;
    z-index: 100;
    white-space: nowrap;
    animation: toast-in 0.25s ease-out, toast-out 0.25s ease-in 2.5s forwards;
  }
  @keyframes toast-in {
    from { opacity: 0; transform: translateX(-50%) translateY(8px); }
    to { opacity: 1; transform: translateX(-50%) translateY(0); }
  }
  @keyframes toast-out {
    from { opacity: 1; }
    to { opacity: 0; }
  }

  /* Species detail panel */
  .detail-panel {
    position: absolute;
    inset: 0;
    background: var(--bg);
    z-index: 20;
    display: flex;
    flex-direction: column;
    animation: panel-in 0.25s ease-out;
  }
  @keyframes panel-in {
    from { transform: translateX(30px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  .panel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
  }
  .back-btn {
    background: none;
    border: none;
    color: var(--text2);
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 0.1em;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0;
  }
  .back-btn:hover { color: var(--accent); }
  .panel-content {
    flex: 1;
    overflow-y: auto;
  }
  .panel-content::-webkit-scrollbar { display: none; }
  .panel-name-block {
    padding: 20px 16px 16px;
    border-bottom: 1px solid var(--border);
  }
  .panel-comname {
    font-family: var(--font-serif);
    font-size: 32px;
    font-weight: 400;
    color: var(--text);
    line-height: 1.05;
    margin-bottom: 4px;
  }
  .panel-sciname {
    font-family: var(--font-body);
    font-style: italic;
    font-size: 14px;
    font-weight: 300;
    color: var(--text2);
    margin-bottom: 16px;
  }
  .panel-stats-row {
    display: flex;
    gap: 0;
  }
  .panel-stat {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
    border-right: 1px solid var(--border);
    padding-right: 12px;
    margin-right: 12px;
  }
  .panel-stat:last-child { border-right: none; padding-right: 0; margin-right: 0; }
  .panel-stat-val {
    font-family: var(--font-mono);
    font-size: 20px;
    color: var(--accent);
    line-height: 1;
  }
  .panel-stat-label {
    font-family: var(--font-mono);
    font-size: 8px;
    color: var(--text3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
  .mini-det-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 16px;
    border-bottom: 1px solid var(--border);
  }
  .mini-det-time {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text2);
  }
  .mini-det-conf {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--accent2);
  }
  .mini-det-play {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text3);
    cursor: pointer;
    padding: 4px 8px;
    border: 1px solid var(--border);
    background: none;
    transition: all 0.1s;
  }
  .mini-det-play:hover { color: var(--accent); border-color: var(--accent); }
`;

// ─── Spectrogram Canvas Component ─────────────────────────────────────────────
function SpectrogramCanvas() {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const dataRef = useRef([]);
  const posRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const W = canvas.width = canvas.offsetWidth;
    const H = canvas.height = canvas.offsetHeight;
    const cols = W;

    // Generate noise data
    const generate = () => {
      const col = new Float32Array(32);
      const t = posRef.current / cols;
      for (let i = 0; i < 32; i++) {
        const base = Math.pow(0.15, (i / 32));
        const bird = (Math.sin(t * 8 + i * 0.3) * 0.5 + 0.5) * Math.exp(-Math.pow((i - 8) / 4, 2) * 0.5);
        const bird2 = (Math.sin(t * 13 + i * 0.7 + 1) * 0.5 + 0.5) * Math.exp(-Math.pow((i - 18) / 5, 2) * 0.5);
        col[i] = Math.max(0, Math.min(1, base + bird * 0.6 + bird2 * 0.4 + (Math.random() * 0.08)));
      }
      return col;
    };

    const draw = () => {
      // Scroll left
      const imageData = ctx.getImageData(1, 0, W - 1, H);
      ctx.putImageData(imageData, 0, 0);

      // Draw new column
      const col = generate();
      const bandH = H / col.length;
      for (let i = 0; i < col.length; i++) {
        const v = col[col.length - 1 - i];
        const r = Math.floor(v * 232);
        const g = Math.floor(v * 197 * 0.9);
        const b = Math.floor(v * 71 * 0.3);
        ctx.fillStyle = `rgb(${r},${g},${b})`;
        ctx.fillRect(W - 1, i * bandH, 1, bandH + 1);
      }

      posRef.current = (posRef.current + 1) % cols;
      animRef.current = requestAnimationFrame(draw);
    };

    ctx.fillStyle = "#141610";
    ctx.fillRect(0, 0, W, H);
    draw();

    return () => cancelAnimationFrame(animRef.current);
  }, []);

  return <canvas ref={canvasRef} className="spectrogram-canvas" />;
}

// ─── Waveform Mock ─────────────────────────────────────────────────────────────
function WaveformBars({ playing }) {
  const bars = Array.from({ length: 32 }, (_, i) => {
    const h = playing
      ? 20 + Math.random() * 70
      : 8 + Math.abs(Math.sin(i * 0.7)) * 60;
    return h;
  });
  return (
    <div className="waveform-mock">
      {bars.map((h, i) => (
        <div key={i} className="waveform-bar" style={{ height: `${h}%` }} />
      ))}
    </div>
  );
}

// ─── Activity Chart ─────────────────────────────────────────────────────────────
function ActivityChart() {
  const maxCount = Math.max(...HOURLY_DATA.map(d => d.count));
  const currentHour = 7;
  return (
    <div className="activity-chart">
      <div className="chart-title">
        <span>DETECTIONS / HOUR</span>
        <span style={{ color: "var(--accent)" }}>201 TODAY</span>
      </div>
      <div className="chart-bars">
        {HOURLY_DATA.map((d, i) => (
          <div key={d.h} className="chart-bar-wrap">
            <div
              className={`chart-bar ${d.h === "07" ? "current" : d.count > 0 ? "active" : ""}`}
              style={{ height: `${Math.max(2, (d.count / maxCount) * 100)}%` }}
            />
            {i % 4 === 0 && <span className="chart-hour">{d.h}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Live Screen ──────────────────────────────────────────────────────────────
function LiveScreen({ onToast }) {
  const [playing, setPlaying] = useState(false);
  const [detIndex, setDetIndex] = useState(0);

  useEffect(() => {
    const t = setInterval(() => {
      setDetIndex(i => {
        const next = (i + 1) % MOCK_DETECTIONS.length;
        onToast(`${MOCK_DETECTIONS[next].com} detected`);
        return next;
      });
    }, 8000);
    return () => clearInterval(t);
  }, []);

  const det = MOCK_DETECTIONS[detIndex];
  const confColor = det.conf >= 0.9 ? "var(--accent)" : det.conf >= 0.75 ? "var(--amber)" : "var(--text2)";

  return (
    <div>
      <div className="spectrogram-wrapper">
        <SpectrogramCanvas />
        <div className="spec-label">⬤ LIVE · 48 kHz</div>
        <div className="spec-freq-labels">
          <span className="spec-freq">24k</span>
          <span className="spec-freq">12k</span>
          <span className="spec-freq">6k</span>
          <span className="spec-freq">3k</span>
          <span className="spec-freq">0</span>
        </div>
      </div>

      <div className="live-top-detection" key={det.id}>
        <div className="det-label">MOST RECENT DETECTION</div>
        <span className="det-time-stamp">{det.time}</span>
        <div className="det-comname">{det.com}</div>
        <div className="det-sciname">{det.sci}</div>
        <div className="conf-row">
          <div className="conf-bar-track">
            <div className="conf-bar-fill" style={{ width: `${det.conf * 100}%`, background: confColor }} />
          </div>
          <span className="conf-pct" style={{ color: confColor }}>{Math.round(det.conf * 100)}%</span>
        </div>
        <div className="audio-player-mock">
          <button className="play-btn" onClick={() => setPlaying(p => !p)}>
            {playing ? "▪" : "▶"}
          </button>
          <WaveformBars playing={playing} />
          <span className="filename-label">{det.file}</span>
        </div>
      </div>

      <ActivityChart />

      <div className="det-list">
        <div className="det-label" style={{ padding: "10px 16px 6px", borderBottom: "1px solid var(--border)" }}>
          RECENT DETECTIONS
        </div>
        {MOCK_DETECTIONS.slice(1).map((d) => {
          const c = d.conf >= 0.9 ? "var(--accent2)" : d.conf >= 0.75 ? "var(--amber2)" : "var(--text3)";
          return (
            <div className="det-row" key={d.id}>
              <div className="conf-dot" style={{ background: c }} />
              <div className="det-row-body">
                <div className="det-row-name">{d.com}</div>
                <div className="det-row-sci">{d.sci}</div>
              </div>
              <div className="det-row-conf" style={{ color: c }}>{Math.round(d.conf * 100)}%</div>
              <div className="det-row-time">{d.time}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Log Screen ───────────────────────────────────────────────────────────────
function LogScreen() {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("time");
  const [activeDay, setActiveDay] = useState("MON 24");
  const days = ["SUN 23", "MON 24", "TUE 25", "WED 26", "THU 27"];

  const filtered = MOCK_DETECTIONS.filter(d =>
    d.com.toLowerCase().includes(search.toLowerCase()) ||
    d.sci.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="log-header">
        <div className="screen-title">DETECTION LOG</div>
        <div className="day-strip">
          {days.map(d => (
            <button key={d} className={`day-chip ${d === activeDay ? "active" : ""}`} onClick={() => setActiveDay(d)}>
              {d}
            </button>
          ))}
        </div>
      </div>
      <div className="search-row">
        <span className="search-icon">⌕</span>
        <input
          className="search-input"
          placeholder="Search species…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>
      <div className="sort-strip">
        {["time", "conf", "alpha"].map(s => (
          <button key={s} className={`sort-btn ${sort === s ? "active" : ""}`} onClick={() => setSort(s)}>
            {s === "time" ? "By Time" : s === "conf" ? "Confidence" : "A–Z"}
          </button>
        ))}
      </div>
      <div className="det-list">
        {filtered.map(d => {
          const c = d.conf >= 0.9 ? "var(--accent2)" : d.conf >= 0.75 ? "var(--amber2)" : "var(--text3)";
          return (
            <div className="det-row" key={d.id}>
              <div className="conf-dot" style={{ background: c }} />
              <div className="det-row-body">
                <div className="det-row-name">{d.com}</div>
                <div className="det-row-sci">{d.sci}</div>
              </div>
              <div className="det-row-conf" style={{ color: c }}>{Math.round(d.conf * 100)}%</div>
              <div className="det-row-time">{d.time}</div>
            </div>
          );
        })}
        {filtered.length === 0 && (
          <div style={{ padding: "32px 16px", textAlign: "center", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text3)" }}>
            NO RESULTS
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Species Detail Panel ──────────────────────────────────────────────────────
function SpeciesDetail({ species, onBack }) {
  const dets = MOCK_DETECTIONS.filter(d => d.com === species.com).slice(0, 6);
  const allDets = dets.length > 0 ? dets : MOCK_DETECTIONS.slice(0, 4).map(d => ({ ...d, com: species.com }));

  return (
    <div className="detail-panel">
      <div className="panel-header">
        <button className="back-btn" onClick={onBack}>← BACK</button>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text3)", letterSpacing: "0.15em" }}>SPECIES DETAIL</span>
      </div>
      <div className="panel-content">
        <div className="panel-name-block">
          <div className="panel-comname">{species.com}</div>
          <div className="panel-sciname">{species.sci}</div>
          <div className="panel-stats-row">
            <div className="panel-stat">
              <div className="panel-stat-val">{species.count}</div>
              <div className="panel-stat-label">Detections</div>
            </div>
            <div className="panel-stat">
              <div className="panel-stat-val">{Math.round(species.maxConf * 100)}%</div>
              <div className="panel-stat-label">Peak Conf.</div>
            </div>
            <div className="panel-stat">
              <div className="panel-stat-val">{species.lastSeen}</div>
              <div className="panel-stat-label">Last Seen</div>
            </div>
          </div>
        </div>

        {/* Mini confidence chart */}
        <div className="activity-chart">
          <div className="chart-title"><span>DETECTIONS LAST 7 DAYS</span></div>
          <div className="chart-bars">
            {[3,7,2,8,12,5,species.count].map((v, i) => (
              <div key={i} className="chart-bar-wrap">
                <div className="chart-bar active" style={{ height: `${Math.max(4, (v / 12) * 100)}%` }} />
                <span className="chart-hour">{["M","T","W","T","F","S","S"][i]}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ padding: "12px 16px 6px", fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text3)", letterSpacing: "0.2em", borderBottom: "1px solid var(--border)" }}>
          RECORDINGS TODAY
        </div>
        {allDets.map((d, i) => (
          <div className="mini-det-row" key={i}>
            <span className="mini-det-time">{d.time}</span>
            <span className="mini-det-conf">{Math.round(d.conf * 100)}% conf</span>
            <button className="mini-det-play">▶ PLAY</button>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Species Screen ───────────────────────────────────────────────────────────
function SpeciesScreen() {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [sort, setSort] = useState("count");

  const sorted = [...MOCK_SPECIES]
    .filter(s => s.com.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => sort === "count" ? b.count - a.count : a.com.localeCompare(b.com));

  if (selected) return <SpeciesDetail species={selected} onBack={() => setSelected(null)} />;

  return (
    <div>
      <div className="species-header">
        <div className="screen-title">SPECIES CATALOG — {MOCK_SPECIES.length} TOTAL</div>
        <div className="search-row" style={{ border: "1px solid var(--border2)", margin: "0 0 10px" }}>
          <span className="search-icon">⌕</span>
          <input
            className="search-input"
            placeholder="Filter species…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div style={{ display: "flex", gap: "6px" }}>
          {["count", "alpha"].map(s => (
            <button key={s} className={`day-chip ${sort === s ? "active" : ""}`} onClick={() => setSort(s)}>
              {s === "count" ? "By Count" : "A–Z"}
            </button>
          ))}
        </div>
      </div>
      <div className="species-grid">
        {sorted.map(sp => (
          <div className="species-card" key={sp.com} onClick={() => setSelected(sp)}>
            <div className="sp-count">{sp.count}</div>
            <div className="sp-name">{sp.com}</div>
            <div className="sp-sci">{sp.sci}</div>
            <div className="sp-meta">
              <span className="sp-last">{sp.lastSeen}</span>
              <span className={`trend-arrow trend-${sp.trend}`}>
                {sp.trend === "up" ? "↑" : sp.trend === "down" ? "↓" : "—"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Station Screen ───────────────────────────────────────────────────────────
function StationScreen() {
  const services = [
    { name: "birdnet.service", status: "ok" },
    { name: "extraction.service", status: "ok" },
    { name: "chart_viewer.service", status: "ok" },
    { name: "caddy.service", status: "ok" },
    { name: "sox.service", status: "warn", note: "high cpu" },
    { name: "rtsp_server.service", status: "ok" },
  ];

  return (
    <div className="station-screen">
      <div className="stat-block">
        <div className="stat-block-title">STATION OVERVIEW</div>
        <div className="readout-grid">
          <div className="readout">
            <span className="readout-label">Uptime</span>
            <span className="readout-value" style={{ fontSize: "16px" }}>{SYSTEM_STATS.uptime}</span>
          </div>
          <div className="readout">
            <span className="readout-label">Location</span>
            <span className="readout-value" style={{ fontSize: "14px" }}>{SYSTEM_STATS.location}</span>
          </div>
          <div className="readout">
            <span className="readout-label">Model</span>
            <span className="readout-value" style={{ fontSize: "11px", color: "var(--text2)" }}>{SYSTEM_STATS.model}</span>
          </div>
          <div className="readout">
            <span className="readout-label">Sample Rate</span>
            <span className="readout-value" style={{ fontSize: "14px", color: "var(--text2)" }}>{SYSTEM_STATS.sampleRate}</span>
          </div>
        </div>
      </div>

      <div className="stat-block">
        <div className="stat-block-title">SYSTEM READINGS</div>
        <div className="readout-grid">
          <div className="readout">
            <span className="readout-label">CPU Load</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
              <span className="readout-value accent">{SYSTEM_STATS.cpu}</span>
              <span className="readout-unit">%</span>
            </div>
            <div className="gauge-row">
              <div className="gauge-track" style={{ flex: 1 }}>
                <div className="gauge-fill" style={{ width: `${SYSTEM_STATS.cpu}%`, background: "var(--accent)" }} />
              </div>
            </div>
          </div>
          <div className="readout">
            <span className="readout-label">CPU Temp</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
              <span className={`readout-value ${SYSTEM_STATS.temp > 70 ? "danger" : SYSTEM_STATS.temp > 55 ? "amber" : ""}`}>{SYSTEM_STATS.temp}</span>
              <span className="readout-unit">°C</span>
            </div>
            <div className="gauge-row">
              <div className="gauge-track" style={{ flex: 1 }}>
                <div className="gauge-fill" style={{ width: `${(SYSTEM_STATS.temp / 85) * 100}%`, background: SYSTEM_STATS.temp > 70 ? "var(--red)" : "var(--amber)" }} />
              </div>
            </div>
          </div>
          <div className="readout">
            <span className="readout-label">Disk Used</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
              <span className="readout-value amber">{SYSTEM_STATS.disk}</span>
              <span className="readout-unit">%</span>
            </div>
            <div className="gauge-row">
              <div className="gauge-track" style={{ flex: 1 }}>
                <div className="gauge-fill" style={{ width: `${SYSTEM_STATS.disk}%`, background: "var(--amber)" }} />
              </div>
            </div>
          </div>
          <div className="readout">
            <span className="readout-label">Det / Hour</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
              <span className="readout-value accent">{SYSTEM_STATS.detectionRate}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="stat-block">
        <div className="stat-block-title">SERVICES</div>
        {services.map(s => (
          <div className="service-row" key={s.name}>
            <span className="service-name">{s.name}</span>
            <span className={`service-status status-${s.status}`}>
              <span className="status-dot" />
              {s.status === "ok" ? "RUNNING" : "WARNING"}
            </span>
          </div>
        ))}
      </div>

      <div className="stat-block">
        <div className="stat-block-title">CONTROLS</div>
        <div className="ctrl-grid">
          {[
            { label: "ANALYSIS", action: "Restart Analysis" },
            { label: "SYSTEM", action: "Check Update" },
            { label: "RECORDING", action: "Pause Recording" },
            { label: "DISK", action: "Run Cleanup", danger: true },
          ].map(c => (
            <button key={c.action} className={`ctrl-btn ${c.danger ? "danger" : ""}`}>
              <span className="ctrl-btn-label">{c.label}</span>
              {c.action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("live");
  const [toast, setToast] = useState(null);
  const [time, setTime] = useState("");
  const toastRef = useRef(null);

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setTime(now.toTimeString().slice(0, 8));
    };
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, []);

  const showToast = useCallback((msg) => {
    setToast(msg);
    clearTimeout(toastRef.current);
    toastRef.current = setTimeout(() => setToast(null), 2800);
  }, []);

  const TABS = [
    { id: "live", icon: "⬤", label: "LIVE" },
    { id: "log", icon: "☰", label: "LOG" },
    { id: "species", icon: "◈", label: "SPECIES" },
    { id: "station", icon: "◉", label: "STATION" },
  ];

  return (
    <>
      <style>{CSS}</style>
      <div className="app">
        <div className="header">
          <div className="header-left">
            <div className="station-dot" />
            <div>
              <div className="station-name">FIELD STATION · LYNNWOOD</div>
              <div className="station-id">BirdNET-Pi v0.11 · RPi 4B</div>
            </div>
          </div>
          <div className="header-time">{time}</div>
        </div>

        <div className="screen" style={{ position: "relative" }}>
          {tab === "live" && <LiveScreen onToast={showToast} />}
          {tab === "log" && <LogScreen />}
          {tab === "species" && <SpeciesScreen />}
          {tab === "station" && <StationScreen />}
        </div>

        <nav className="bottom-nav">
          {TABS.map(t => (
            <button
              key={t.id}
              className={`nav-btn ${tab === t.id ? "active" : ""}`}
              onClick={() => setTab(t.id)}
            >
              <span className="nav-icon">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>

        {toast && (
          <div className="toast" key={toast + Date.now()}>
            ↑ {toast.toUpperCase()}
          </div>
        )}
      </div>
    </>
  );
}
