import { useState, useEffect, useRef, useCallback } from "react";

// ─── Data ─────────────────────────────────────────────────────────────────────

const DETECTIONS = [
  { id:1,  com:"Black-capped Chickadee",    sci:"Poecile atricapillus",       conf:0.97, time:"07:42:11", hh:7  },
  { id:2,  com:"American Robin",            sci:"Turdus migratorius",          conf:0.91, time:"07:38:44", hh:7  },
  { id:3,  com:"Dark-eyed Junco",           sci:"Junco hyemalis",              conf:0.88, time:"07:31:02", hh:7  },
  { id:4,  com:"House Finch",               sci:"Haemorhous mexicanus",        conf:0.79, time:"07:22:58", hh:7  },
  { id:5,  com:"Steller's Jay",             sci:"Cyanocitta stelleri",         conf:0.95, time:"07:18:33", hh:7  },
  { id:6,  com:"Red-tailed Hawk",           sci:"Buteo jamaicensis",           conf:0.84, time:"06:59:47", hh:6  },
  { id:7,  com:"Song Sparrow",              sci:"Melospiza melodia",           conf:0.76, time:"06:44:12", hh:6  },
  { id:8,  com:"Spotted Towhee",            sci:"Pipilo maculatus",            conf:0.82, time:"06:31:05", hh:6  },
  { id:9,  com:"American Crow",             sci:"Corvus brachyrhynchos",       conf:0.99, time:"06:15:28", hh:6  },
  { id:10, com:"Pine Siskin",               sci:"Spinus pinus",                conf:0.73, time:"05:58:41", hh:5  },
  { id:11, com:"White-crowned Sparrow",     sci:"Zonotrichia leucophrys",      conf:0.87, time:"05:44:19", hh:5  },
  { id:12, com:"Northern Flicker",          sci:"Colaptes auratus",            conf:0.92, time:"05:32:07", hh:5  },
  { id:13, com:"Cedar Waxwing",             sci:"Bombycilla cedrorum",         conf:0.78, time:"05:14:33", hh:5  },
  { id:14, com:"Bewick's Wren",             sci:"Thryomanes bewickii",         conf:0.83, time:"04:58:22", hh:4  },
  { id:15, com:"Purple Finch",              sci:"Haemorhous purpureus",        conf:0.71, time:"04:43:09", hh:4  },
  { id:16, com:"Black-capped Chickadee",    sci:"Poecile atricapillus",        conf:0.94, time:"04:22:17", hh:4  },
  { id:17, com:"American Robin",            sci:"Turdus migratorius",          conf:0.88, time:"04:01:55", hh:4  },
  { id:18, com:"Steller's Jay",             sci:"Cyanocitta stelleri",         conf:0.91, time:"03:47:30", hh:3  },
];

const SPECIES = [
  { com:"Black-capped Chickadee", sci:"Poecile atricapillus",    n:47, maxC:0.97, trend:[3,5,7,2,8,12,5,9,11,47], lastSeen:"07:42" },
  { com:"American Robin",         sci:"Turdus migratorius",       n:31, maxC:0.91, trend:[1,0,3,6,4,8,11,7,9,31], lastSeen:"07:38" },
  { com:"American Crow",          sci:"Corvus brachyrhynchos",    n:28, maxC:0.99, trend:[8,6,4,9,7,5,12,8,6,28], lastSeen:"06:15" },
  { com:"Steller's Jay",          sci:"Cyanocitta stelleri",       n:22, maxC:0.95, trend:[0,2,1,4,3,7,9,5,8,22], lastSeen:"07:18" },
  { com:"Dark-eyed Junco",        sci:"Junco hyemalis",           n:19, maxC:0.88, trend:[4,3,5,7,6,4,8,5,7,19], lastSeen:"07:31" },
  { com:"Northern Flicker",       sci:"Colaptes auratus",         n:14, maxC:0.92, trend:[7,9,6,8,5,4,6,5,4,14], lastSeen:"05:32" },
  { com:"House Finch",            sci:"Haemorhous mexicanus",     n:11, maxC:0.79, trend:[2,1,3,2,4,3,5,3,4,11], lastSeen:"07:22" },
  { com:"Spotted Towhee",         sci:"Pipilo maculatus",         n:9,  maxC:0.82, trend:[0,1,0,2,1,3,2,4,5,9],  lastSeen:"06:31" },
  { com:"Song Sparrow",           sci:"Melospiza melodia",        n:8,  maxC:0.76, trend:[3,4,3,2,4,3,2,3,4,8],  lastSeen:"06:44" },
  { com:"Red-tailed Hawk",        sci:"Buteo jamaicensis",        n:5,  maxC:0.84, trend:[1,0,2,1,0,2,1,2,1,5],  lastSeen:"06:59" },
  { com:"Pine Siskin",            sci:"Spinus pinus",             n:4,  maxC:0.73, trend:[0,0,1,0,1,0,2,1,0,4],  lastSeen:"05:58" },
  { com:"Cedar Waxwing",          sci:"Bombycilla cedrorum",      n:3,  maxC:0.78, trend:[0,0,0,1,0,1,0,0,1,3],  lastSeen:"05:14" },
];

const HOURLY = [
  {h:0,n:2},{h:1,n:0},{h:2,n:1},{h:3,n:3},{h:4,n:8},{h:5,n:24},
  {h:6,n:41},{h:7,n:58},{h:8,n:47},{h:9,n:33},{h:10,n:22},{h:11,n:18},
  {h:12,n:14},{h:13,n:12},{h:14,n:15},{h:15,n:19},{h:16,n:28},{h:17,n:34},
  {h:18,n:31},{h:19,n:11},{h:20,n:5},{h:21,n:3},{h:22,n:1},{h:23,n:0},
];

const SEVEN_DAY = [
  { date:"Feb 18", n:87,  species:9 },
  { date:"Feb 19", n:112, species:11 },
  { date:"Feb 20", n:94,  species:10 },
  { date:"Feb 21", n:143, species:13 },
  { date:"Feb 22", n:201, species:14 },
  { date:"Feb 23", n:178, species:13 },
  { date:"Feb 24", n:201, species:12 },
];

// ─── Tufte Sparkline (inline svg) ────────────────────────────────────────────
function Sparkline({ values, w = 60, h = 18, color = "#1A1A14" }) {
  const max = Math.max(...values, 1);
  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * w;
    const y = h - (v / max) * h;
    return `${x},${y}`;
  }).join(" ");
  const last = values[values.length - 1];
  const lx = w;
  const ly = h - (last / max) * h;
  return (
    <svg width={w} height={h} style={{ display:"inline-block", verticalAlign:"middle", overflow:"visible" }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="0.8" />
      <circle cx={lx} cy={ly} r="1.5" fill={color} />
    </svg>
  );
}

// ─── Inline confidence bar (hairline) ────────────────────────────────────────
function ConfBar({ conf, w = 48 }) {
  const pct = Math.round(conf * 100);
  const fill = conf >= 0.9 ? "#1A1A14" : conf >= 0.75 ? "#5A5A50" : "#A0A090";
  return (
    <span style={{ display:"inline-flex", alignItems:"center", gap:4, verticalAlign:"middle" }}>
      <svg width={w} height={8} style={{ display:"inline-block" }}>
        <rect x={0} y={3} width={w} height={1} fill="#E0DDD5" />
        <rect x={0} y={3} width={conf * w} height={1} fill={fill} />
        <rect x={0} y={1.5} width={1} height={4} fill={fill} />
        <rect x={conf * w - 0.5} y={1.5} width={1} height={4} fill={fill} />
      </svg>
      <span style={{ fontFamily:"var(--mono)", fontSize:10, color: fill, minWidth:26 }}>{pct}%</span>
    </span>
  );
}

// ─── Live Trace Canvas (seismograph-style, black on cream) ───────────────────
function TraceCanvas() {
  const canvasRef = useRef(null);
  const rafRef = useRef(null);
  const posRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    const W = canvas.width = canvas.offsetWidth * window.devicePixelRatio;
    const H = canvas.height = canvas.offsetHeight * window.devicePixelRatio;
    canvas.style.width = canvas.offsetWidth + "px";
    canvas.style.height = canvas.offsetHeight + "px";
    const ctx = canvas.getContext("2d");
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    const w = canvas.offsetWidth;
    const h = canvas.offsetHeight;

    ctx.fillStyle = "#F7F4EE";
    ctx.fillRect(0, 0, w, h);

    // Draw frequency grid lines (like Tufte's reference lines)
    ctx.strokeStyle = "#E8E4DC";
    ctx.lineWidth = 0.5;
    for (let i = 1; i < 4; i++) {
      ctx.beginPath();
      ctx.moveTo(0, (i / 4) * h);
      ctx.lineTo(w, (i / 4) * h);
      ctx.stroke();
    }

    let t = 0;
    const draw = () => {
      // Scroll image left
      const img = ctx.getImageData(1 * window.devicePixelRatio, 0, (w - 1) * window.devicePixelRatio, h * window.devicePixelRatio);
      ctx.putImageData(img, 0, 0);

      // Clear right column
      ctx.fillStyle = "#F7F4EE";
      ctx.fillRect(w - 1, 0, 1, h);

      // Draw grid line fragment
      ctx.fillStyle = "#E8E4DC";
      ctx.fillRect(w - 1, h * 0.25, 1, 0.5);
      ctx.fillRect(w - 1, h * 0.5, 1, 0.5);
      ctx.fillRect(w - 1, h * 0.75, 1, 0.5);

      // Draw signal traces (multiple frequency bands, like a sonogram)
      const bands = [
        { cy: h * 0.20, freq: 12, amp: 0.12, birdFreq: 4.1, birdAmp: 0.28 },
        { cy: h * 0.42, freq: 7,  amp: 0.08, birdFreq: 2.7, birdAmp: 0.35 },
        { cy: h * 0.65, freq: 5,  amp: 0.06, birdFreq: 1.9, birdAmp: 0.22 },
        { cy: h * 0.84, freq: 3,  amp: 0.04, birdFreq: 1.1, birdAmp: 0.15 },
      ];

      bands.forEach(({ cy, freq, amp, birdFreq, birdAmp }) => {
        const noise = (Math.random() - 0.5) * amp * h;
        const signal = Math.sin(t * birdFreq) * Math.exp(-Math.pow(Math.sin(t * 0.1), 8) * 2) * birdAmp * h;
        const y = cy + noise + signal;
        const intensity = Math.abs(signal) / (birdAmp * h);
        const alpha = 0.15 + intensity * 0.75;
        ctx.fillStyle = `rgba(26, 26, 20, ${Math.min(1, alpha)})`;
        ctx.fillRect(w - 1, y - 0.5, 1, 1);
      });

      t += 0.05;
      posRef.current++;
      rafRef.current = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width:"100%", height:"100%", display:"block" }}
    />
  );
}

// ─── CSS ──────────────────────────────────────────────────────────────────────
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=IBM+Plex+Mono:ital,wght@0,300;0,400;1,300&display=swap');

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

:root {
  --paper: #F7F4EE;
  --paper2: #F0EDE5;
  --ink: #1A1A14;
  --ink2: #4A4A40;
  --ink3: #8A8A7E;
  --ink4: #BFBCB2;
  --rule: #D8D4CA;
  --rule2: #E8E4DC;
  --red: #8B1A1A;
  --serif: 'Playfair Display', Georgia, serif;
  --body: 'Crimson Pro', 'Georgia', serif;
  --mono: 'IBM Plex Mono', 'Courier New', monospace;
}

html, body, #root { height:100%; background:var(--paper); color:var(--ink); }

/* ── Shell ── */
.app {
  display:flex;
  flex-direction:column;
  height:100%;
  max-width:430px;
  margin:0 auto;
  background:var(--paper);
  font-family:var(--body);
}

/* ── Masthead ── */
.masthead {
  padding:12px 16px 0;
  border-bottom:2px solid var(--ink);
}
.masthead-top {
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:4px;
}
.masthead-title {
  font-family:var(--serif);
  font-size:18px;
  font-weight:500;
  letter-spacing:0.02em;
  color:var(--ink);
  line-height:1;
}
.masthead-subtitle {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
  letter-spacing:0.15em;
  text-transform:uppercase;
}
.masthead-meta {
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  padding-bottom:6px;
  border-top:1px solid var(--rule);
  margin-top:6px;
  padding-top:4px;
}
.masthead-date {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
  letter-spacing:0.1em;
}
.live-indicator {
  display:flex;
  align-items:center;
  gap:5px;
  font-family:var(--mono);
  font-size:8px;
  color:var(--red);
  letter-spacing:0.1em;
}
.live-dot {
  width:5px; height:5px;
  border-radius:50%;
  background:var(--red);
  animation:blink 1.8s ease-in-out infinite;
}
@keyframes blink {
  0%,100%{opacity:1} 50%{opacity:0.25}
}

/* ── Section nav (running head) ── */
.section-nav {
  display:flex;
  border-bottom:1px solid var(--rule);
  background:var(--paper);
  position:sticky;
  top:0;
  z-index:10;
}
.section-btn {
  flex:1;
  padding:7px 0 6px;
  background:none;
  border:none;
  border-right:1px solid var(--rule);
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
  letter-spacing:0.14em;
  text-transform:uppercase;
  cursor:pointer;
  transition:color 0.1s;
}
.section-btn:last-child { border-right:none; }
.section-btn.active {
  color:var(--ink);
  border-bottom:1.5px solid var(--ink);
  margin-bottom:-1px;
}

/* ── Scroll area ── */
.scroll {
  flex:1;
  overflow-y:auto;
  overflow-x:hidden;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:thin;
  scrollbar-color:var(--rule) transparent;
}
.scroll::-webkit-scrollbar { width:2px; }
.scroll::-webkit-scrollbar-thumb { background:var(--rule); }

/* ── Section headings (Tufte-style) ── */
.section-head {
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  padding:10px 16px 6px;
  border-bottom:1px solid var(--rule);
}
.section-head-title {
  font-family:var(--mono);
  font-size:8px;
  letter-spacing:0.18em;
  text-transform:uppercase;
  color:var(--ink3);
}
.section-head-meta {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
}

/* ── Trace block ── */
.trace-block {
  height:100px;
  border-bottom:1px solid var(--rule);
  position:relative;
  background:var(--paper);
}
.trace-freq-labels {
  position:absolute;
  right:6px;
  top:0; bottom:0;
  display:flex;
  flex-direction:column;
  justify-content:space-around;
  pointer-events:none;
  padding:8px 0;
}
.trace-freq-label {
  font-family:var(--mono);
  font-size:7px;
  color:var(--ink4);
  text-align:right;
  line-height:1;
}

/* ── Most recent detection ── */
.recent-det {
  padding:12px 16px;
  border-bottom:1px solid var(--rule);
}
.recent-det-head {
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:3px;
}
.recent-det-comname {
  font-family:var(--serif);
  font-size:22px;
  font-weight:400;
  color:var(--ink);
  line-height:1.1;
}
.recent-det-time {
  font-family:var(--mono);
  font-size:9px;
  color:var(--ink3);
}
.recent-det-sciname {
  font-family:var(--body);
  font-style:italic;
  font-size:12px;
  font-weight:300;
  color:var(--ink2);
  margin-bottom:8px;
}
.recent-det-row {
  display:flex;
  align-items:center;
  gap:16px;
  flex-wrap:wrap;
}
.audio-inline {
  display:flex;
  align-items:center;
  gap:6px;
}
.play-tiny {
  width:18px; height:18px;
  border:1px solid var(--ink);
  background:none;
  cursor:pointer;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:7px;
  color:var(--ink);
  flex-shrink:0;
  transition:background 0.12s;
}
.play-tiny:hover { background:var(--ink); color:var(--paper); }
.audio-file {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink4);
}

/* ── Hourly histogram ── */
.histogram-block {
  padding:10px 16px;
  border-bottom:1px solid var(--rule);
}
.histo-bars {
  display:flex;
  align-items:flex-end;
  gap:1px;
  height:40px;
  margin-bottom:2px;
}
.histo-bar-col {
  flex:1;
  display:flex;
  flex-direction:column;
  align-items:center;
  height:100%;
  justify-content:flex-end;
  gap:2px;
}
.histo-bar {
  width:100%;
  background:var(--ink4);
}
.histo-bar.now { background:var(--ink); }
.histo-bar.past { background:var(--ink3); }
.histo-tick {
  font-family:var(--mono);
  font-size:6px;
  color:var(--ink4);
  line-height:1;
  text-align:center;
}
.histo-annot {
  display:flex;
  justify-content:space-between;
  margin-top:4px;
}
.histo-annot span {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
}

/* ── Summary row (Tufte table-like) ── */
.summary-strip {
  display:flex;
  border-bottom:1px solid var(--rule);
}
.sum-cell {
  flex:1;
  padding:8px 10px;
  border-right:1px solid var(--rule);
  text-align:center;
}
.sum-cell:last-child { border-right:none; }
.sum-val {
  font-family:var(--serif);
  font-size:20px;
  font-weight:400;
  color:var(--ink);
  display:block;
  line-height:1;
  margin-bottom:2px;
}
.sum-label {
  font-family:var(--mono);
  font-size:7px;
  color:var(--ink3);
  letter-spacing:0.1em;
  text-transform:uppercase;
  display:block;
}

/* ── Detection table (Tufte-style data table) ── */
.det-table {
  width:100%;
  border-collapse:collapse;
}
.det-table-head tr {
  border-bottom:1.5px solid var(--ink);
}
.det-table th {
  font-family:var(--mono);
  font-size:7px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--ink3);
  padding:6px 8px 5px;
  text-align:left;
  font-weight:400;
}
.det-table th:first-child { padding-left:16px; }
.det-table th:last-child { padding-right:16px; text-align:right; }
.det-table td {
  padding:6px 8px;
  border-bottom:1px solid var(--rule2);
  vertical-align:middle;
}
.det-table td:first-child { padding-left:16px; }
.det-table td:last-child { padding-right:16px; text-align:right; }
.det-table tr:hover td { background:var(--paper2); }
.td-time {
  font-family:var(--mono);
  font-size:9px;
  color:var(--ink3);
  white-space:nowrap;
}
.td-com {
  font-family:var(--body);
  font-size:13px;
  color:var(--ink);
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
  max-width:120px;
}
.td-sci {
  font-family:var(--body);
  font-style:italic;
  font-size:10px;
  color:var(--ink3);
  display:block;
}

/* ── Species table ── */
.sp-table {
  width:100%;
  border-collapse:collapse;
}
.sp-table th {
  font-family:var(--mono);
  font-size:7px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--ink3);
  padding:6px 8px 5px;
  text-align:left;
  font-weight:400;
  border-bottom:1.5px solid var(--ink);
}
.sp-table th:first-child { padding-left:16px; }
.sp-table th.right { text-align:right; }
.sp-table th.right:last-child { padding-right:16px; }
.sp-table td {
  padding:7px 8px;
  border-bottom:1px solid var(--rule2);
  vertical-align:middle;
}
.sp-table td:first-child { padding-left:16px; }
.sp-table td.right { text-align:right; padding-right:16px; }
.sp-table tr:hover td { background:var(--paper2); cursor:pointer; }
.sp-n {
  font-family:var(--serif);
  font-size:18px;
  font-weight:400;
  color:var(--ink);
  line-height:1;
}
.sp-com {
  font-family:var(--body);
  font-size:13px;
  color:var(--ink);
}
.sp-sci-row {
  font-family:var(--body);
  font-style:italic;
  font-size:10px;
  color:var(--ink3);
  display:block;
}
.sp-last {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
}

/* ── Seven-day table ── */
.week-table {
  width:100%;
  border-collapse:collapse;
  margin:0;
}
.week-table th {
  font-family:var(--mono);
  font-size:7px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--ink3);
  padding:6px 8px 5px;
  text-align:left;
  font-weight:400;
  border-bottom:1.5px solid var(--ink);
}
.week-table th:first-child { padding-left:16px; }
.week-table td {
  padding:7px 8px;
  border-bottom:1px solid var(--rule2);
  vertical-align:middle;
}
.week-table td:first-child { padding-left:16px; }
.week-date {
  font-family:var(--mono);
  font-size:9px;
  color:var(--ink2);
}
.week-n {
  font-family:var(--serif);
  font-size:15px;
  color:var(--ink);
}
.week-bar-track {
  width:80px;
  height:4px;
  background:var(--rule2);
  display:inline-block;
  vertical-align:middle;
  position:relative;
}
.week-bar-fill {
  position:absolute;
  left:0; top:0; bottom:0;
  background:var(--ink);
}
.week-species {
  font-family:var(--mono);
  font-size:9px;
  color:var(--ink3);
  text-align:right;
  padding-right:16px;
}

/* ── Station screen ── */
.station-section {
  padding:0;
}
.readings-table {
  width:100%;
  border-collapse:collapse;
}
.readings-table th {
  font-family:var(--mono);
  font-size:7px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--ink3);
  padding:6px 8px 5px;
  text-align:left;
  font-weight:400;
  border-bottom:1.5px solid var(--ink);
}
.readings-table th:first-child { padding-left:16px; }
.readings-table td {
  padding:7px 8px;
  border-bottom:1px solid var(--rule2);
  vertical-align:middle;
  font-family:var(--mono);
}
.readings-table td:first-child { padding-left:16px; }
.rd-label {
  font-size:9px;
  color:var(--ink3);
}
.rd-val {
  font-size:15px;
  color:var(--ink);
}
.rd-val.warn { color:var(--red); }
.rd-unit {
  font-size:8px;
  color:var(--ink3);
  margin-left:2px;
}
.inline-gauge {
  display:inline-block;
  width:56px;
  height:3px;
  background:var(--rule2);
  vertical-align:middle;
  position:relative;
  margin-left:6px;
}
.inline-gauge-fill {
  position:absolute;
  left:0; top:0; bottom:0;
  background:var(--ink);
}
.svc-table {
  width:100%;
  border-collapse:collapse;
}
.svc-table th {
  font-family:var(--mono);
  font-size:7px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--ink3);
  padding:6px 8px 5px;
  text-align:left;
  font-weight:400;
  border-bottom:1.5px solid var(--ink);
}
.svc-table th:first-child { padding-left:16px; }
.svc-table th.right { text-align:right; padding-right:16px; }
.svc-table td {
  padding:7px 8px;
  border-bottom:1px solid var(--rule2);
  font-family:var(--mono);
  font-size:9px;
  color:var(--ink2);
}
.svc-table td:first-child { padding-left:16px; }
.svc-table td.right { text-align:right; padding-right:16px; }
.svc-ok { color:var(--ink); }
.svc-warn { color:var(--red); }

.ctrl-row {
  display:flex;
  flex-wrap:wrap;
  gap:0;
  border-top:1px solid var(--rule);
}
.ctrl-item {
  flex: 0 0 50%;
  padding:10px 16px;
  border-bottom:1px solid var(--rule);
  border-right:1px solid var(--rule);
  display:flex;
  flex-direction:column;
  gap:3px;
}
.ctrl-item:nth-child(2n) { border-right:none; }
.ctrl-item-label {
  font-family:var(--mono);
  font-size:7px;
  color:var(--ink4);
  letter-spacing:0.1em;
  text-transform:uppercase;
}
.ctrl-item-btn {
  background:none;
  border:1px solid var(--ink);
  padding:5px 8px;
  font-family:var(--mono);
  font-size:9px;
  color:var(--ink);
  cursor:pointer;
  letter-spacing:0.06em;
  text-align:left;
  transition:background 0.12s;
}
.ctrl-item-btn:hover { background:var(--ink); color:var(--paper); }
.ctrl-item-btn.danger { border-color:var(--red); color:var(--red); }
.ctrl-item-btn.danger:hover { background:var(--red); color:var(--paper); }

/* ── Log screen ── */
.log-filters {
  display:flex;
  align-items:center;
  gap:0;
  border-bottom:1px solid var(--rule);
}
.log-search {
  flex:1;
  padding:8px 12px;
  border:none;
  background:none;
  font-family:var(--body);
  font-size:13px;
  color:var(--ink);
  outline:none;
}
.log-search::placeholder { color:var(--ink4); font-style:italic; }
.log-filter-sep {
  width:1px; height:24px;
  background:var(--rule);
}
.log-sort-btn {
  padding:8px 10px;
  background:none;
  border:none;
  font-family:var(--mono);
  font-size:7px;
  color:var(--ink4);
  letter-spacing:0.1em;
  text-transform:uppercase;
  cursor:pointer;
}
.log-sort-btn.active { color:var(--ink); text-decoration:underline; text-underline-offset:3px; }
.day-row {
  display:flex;
  overflow-x:auto;
  gap:0;
  border-bottom:1px solid var(--rule);
  scrollbar-width:none;
}
.day-row::-webkit-scrollbar { display:none; }
.day-tab {
  flex-shrink:0;
  padding:5px 12px;
  border-right:1px solid var(--rule);
  background:none;
  border-top:none;
  border-bottom:none;
  border-left:none;
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
  cursor:pointer;
  letter-spacing:0.08em;
  transition:color 0.1s;
}
.day-tab.active { color:var(--ink); border-bottom:1.5px solid var(--ink); }

/* ── Species detail panel ── */
.overlay {
  position:absolute;
  inset:0;
  background:var(--paper);
  z-index:20;
  display:flex;
  flex-direction:column;
  animation:fadein 0.18s ease-out;
}
@keyframes fadein {
  from{opacity:0;transform:translateY(8px)}
  to{opacity:1;transform:translateY(0)}
}
.overlay-head {
  padding:8px 16px;
  border-bottom:2px solid var(--ink);
  display:flex;
  align-items:baseline;
  gap:12px;
}
.back-link {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
  letter-spacing:0.1em;
  text-decoration:none;
  cursor:pointer;
  background:none;
  border:none;
  text-transform:uppercase;
}
.back-link:hover { color:var(--ink); }
.overlay-title {
  font-family:var(--mono);
  font-size:8px;
  color:var(--ink3);
  letter-spacing:0.1em;
  text-transform:uppercase;
}
.overlay-scroll { flex:1; overflow-y:auto; scrollbar-width:thin; scrollbar-color:var(--rule) transparent; }
.overlay-scroll::-webkit-scrollbar { width:2px; }
.overlay-scroll::-webkit-scrollbar-thumb { background:var(--rule); }
.sp-detail-name {
  padding:14px 16px 12px;
  border-bottom:1px solid var(--rule);
}
.sp-detail-comname {
  font-family:var(--serif);
  font-size:28px;
  font-weight:400;
  color:var(--ink);
  line-height:1.05;
  margin-bottom:2px;
}
.sp-detail-sciname {
  font-family:var(--body);
  font-style:italic;
  font-size:13px;
  font-weight:300;
  color:var(--ink2);
}
.sp-stats-row {
  display:flex;
  border-bottom:1px solid var(--rule);
}
.sp-stat {
  flex:1;
  padding:8px 12px;
  border-right:1px solid var(--rule);
  text-align:left;
}
.sp-stat:last-child { border-right:none; }
.sp-stat-val {
  font-family:var(--serif);
  font-size:22px;
  font-weight:400;
  color:var(--ink);
  display:block;
  line-height:1;
  margin-bottom:2px;
}
.sp-stat-label {
  font-family:var(--mono);
  font-size:7px;
  color:var(--ink3);
  letter-spacing:0.1em;
  text-transform:uppercase;
  display:block;
}
.sp-sparkline-block {
  padding:10px 16px;
  border-bottom:1px solid var(--rule);
}
.sp-sparkline-label {
  font-family:var(--mono);
  font-size:7px;
  color:var(--ink3);
  letter-spacing:0.14em;
  text-transform:uppercase;
  margin-bottom:6px;
  display:block;
}
.sp-det-table {
  width:100%;
  border-collapse:collapse;
}
.sp-det-table th {
  font-family:var(--mono);
  font-size:7px;
  letter-spacing:0.14em;
  text-transform:uppercase;
  color:var(--ink3);
  padding:6px 8px 5px;
  text-align:left;
  font-weight:400;
  border-bottom:1.5px solid var(--ink);
}
.sp-det-table th:first-child { padding-left:16px; }
.sp-det-table th:last-child { text-align:right; padding-right:16px; }
.sp-det-table td {
  padding:7px 8px;
  border-bottom:1px solid var(--rule2);
}
.sp-det-table td:first-child { padding-left:16px; }
.sp-det-table td:last-child { text-align:right; padding-right:16px; }

/* ── Marginal note (Tufte) ── */
.marginal {
  font-family:var(--mono);
  font-size:7.5px;
  color:var(--ink4);
  letter-spacing:0.04em;
  padding:4px 16px;
  border-bottom:1px solid var(--rule2);
  font-style:italic;
}
`;

// ─── Screens ──────────────────────────────────────────────────────────────────

function LiveScreen() {
  const [playing, setPlaying] = useState(false);
  const [det, setDet] = useState(DETECTIONS[0]);
  const maxH = Math.max(...HOURLY.map(d => d.n));

  useEffect(() => {
    const t = setInterval(() => {
      setDet(d => {
        const i = DETECTIONS.findIndex(x => x.id === d.id);
        return DETECTIONS[(i + 1) % DETECTIONS.length];
      });
    }, 7000);
    return () => clearInterval(t);
  }, []);

  return (
    <div>
      {/* Summary */}
      <div className="summary-strip">
        <div className="sum-cell">
          <span className="sum-val">201</span>
          <span className="sum-label">Today</span>
        </div>
        <div className="sum-cell">
          <span className="sum-val">12</span>
          <span className="sum-label">Species</span>
        </div>
        <div className="sum-cell">
          <span className="sum-val">58</span>
          <span className="sum-label">Peak/hr</span>
        </div>
        <div className="sum-cell">
          <span className="sum-val">4,821</span>
          <span className="sum-label">Total</span>
        </div>
      </div>

      {/* Trace */}
      <div className="section-head">
        <span className="section-head-title">ACOUSTIC TRACE · LIVE</span>
        <span className="section-head-meta">48 kHz · 4-band</span>
      </div>
      <div className="trace-block">
        <TraceCanvas />
        <div className="trace-freq-labels">
          <span className="trace-freq-label">12 kHz</span>
          <span className="trace-freq-label">6 kHz</span>
          <span className="trace-freq-label">3 kHz</span>
          <span className="trace-freq-label">1 kHz</span>
        </div>
      </div>

      {/* Most recent */}
      <div className="section-head">
        <span className="section-head-title">MOST RECENT DETECTION</span>
        <span className="section-head-meta" style={{ color:"var(--red)" }}>● LIVE</span>
      </div>
      <div className="recent-det" key={det.id}>
        <div className="recent-det-head">
          <div className="recent-det-comname">{det.com}</div>
          <div className="recent-det-time">{det.time}</div>
        </div>
        <div className="recent-det-sciname">{det.sci}</div>
        <div className="recent-det-row">
          <ConfBar conf={det.conf} w={64} />
          <div className="audio-inline">
            <button className="play-tiny" onClick={() => setPlaying(p => !p)}>
              {playing ? "▪" : "▶"}
            </button>
            <span className="audio-file">{det.file || `${det.com.split(" ")[0].toLowerCase()}_${det.time.replace(/:/g,"")}.wav`}</span>
          </div>
        </div>
      </div>

      {/* Hourly histogram */}
      <div className="section-head">
        <span className="section-head-title">DETECTIONS BY HOUR</span>
        <span className="section-head-meta">MONDAY 24 FEB 2025</span>
      </div>
      <div className="histogram-block">
        <div className="histo-bars">
          {HOURLY.map(d => (
            <div key={d.h} className="histo-bar-col">
              <div
                className={`histo-bar ${d.h === 7 ? "now" : d.h < 7 ? "past" : ""}`}
                style={{ height: `${Math.max(1, (d.n / maxH) * 100)}%` }}
              />
              {d.h % 6 === 0 && <span className="histo-tick">{String(d.h).padStart(2,"0")}</span>}
            </div>
          ))}
        </div>
        <div className="histo-annot">
          <span>midnight</span>
          <span>↑ 07:00 peak · 58 detections</span>
          <span>midnight</span>
        </div>
      </div>

      {/* Marginal note */}
      <div className="marginal">
        Confidence threshold 0.70 · Model BirdNET_6K_V2.4 · Station 47.6°N 122.3°W
      </div>

      {/* Recent detections table */}
      <div className="section-head">
        <span className="section-head-title">RECENT DETECTIONS</span>
        <span className="section-head-meta">today</span>
      </div>
      <table className="det-table">
        <thead className="det-table-head">
          <tr>
            <th>Time</th>
            <th>Species</th>
            <th style={{textAlign:"right"}}>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {DETECTIONS.slice(0, 12).map(d => (
            <tr key={d.id}>
              <td className="td-time">{d.time}</td>
              <td>
                <span className="td-com">{d.com}</span>
                <span className="td-sci">{d.sci}</span>
              </td>
              <td>
                <div style={{display:"flex",justifyContent:"flex-end"}}>
                  <ConfBar conf={d.conf} w={44} />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function LogScreen() {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("time");
  const [day, setDay] = useState("24");
  const days = ["20","21","22","23","24"];

  const rows = DETECTIONS.filter(d =>
    d.com.toLowerCase().includes(search.toLowerCase()) ||
    d.sci.toLowerCase().includes(search.toLowerCase())
  ).sort((a, b) => {
    if (sort === "conf") return b.conf - a.conf;
    if (sort === "az") return a.com.localeCompare(b.com);
    return b.time.localeCompare(a.time);
  });

  return (
    <div>
      <div className="day-row">
        {days.map(d => (
          <button key={d} className={`day-tab ${d === day ? "active" : ""}`} onClick={() => setDay(d)}>
            Feb {d}
          </button>
        ))}
      </div>
      <div className="log-filters">
        <input
          className="log-search"
          placeholder="Search by species or name…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div className="log-filter-sep" />
        {[["time","Time"],["conf","Conf"],["az","A–Z"]].map(([k,l]) => (
          <button key={k} className={`log-sort-btn ${sort===k?"active":""}`} onClick={() => setSort(k)}>{l}</button>
        ))}
      </div>
      <div className="marginal">
        {rows.length} detection{rows.length !== 1 ? "s" : ""} · Feb {day}, 2025 · sorted by {sort === "time" ? "time (desc)" : sort === "conf" ? "confidence (desc)" : "name (A–Z)"}
      </div>
      <table className="det-table">
        <thead className="det-table-head">
          <tr>
            <th>Time</th>
            <th>Species</th>
            <th style={{textAlign:"right"}}>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(d => (
            <tr key={d.id}>
              <td className="td-time">{d.time}</td>
              <td>
                <span className="td-com">{d.com}</span>
                <span className="td-sci">{d.sci}</span>
              </td>
              <td>
                <div style={{display:"flex",justifyContent:"flex-end"}}>
                  <ConfBar conf={d.conf} w={44} />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SpeciesDetail({ sp, onBack }) {
  const dets = DETECTIONS.filter(d => d.com === sp.com);
  const show = dets.length > 0 ? dets : DETECTIONS.slice(0, 5).map(d => ({...d, com: sp.com, sci: sp.sci}));
  return (
    <div className="overlay">
      <div className="overlay-head">
        <button className="back-link" onClick={onBack}>← Index</button>
        <span className="overlay-title">Species Record</span>
      </div>
      <div className="overlay-scroll">
        <div className="sp-detail-name">
          <div className="sp-detail-comname">{sp.com}</div>
          <div className="sp-detail-sciname">{sp.sci}</div>
        </div>
        <div className="sp-stats-row">
          <div className="sp-stat">
            <span className="sp-stat-val">{sp.n}</span>
            <span className="sp-stat-label">Detections</span>
          </div>
          <div className="sp-stat">
            <span className="sp-stat-val">{Math.round(sp.maxC * 100)}%</span>
            <span className="sp-stat-label">Peak Conf.</span>
          </div>
          <div className="sp-stat">
            <span className="sp-stat-val">{sp.lastSeen}</span>
            <span className="sp-stat-label">Last Seen</span>
          </div>
        </div>
        <div className="sp-sparkline-block">
          <span className="sp-sparkline-label">Detection count · last 10 days</span>
          <Sparkline values={sp.trend} w={260} h={28} />
          <div style={{display:"flex",justifyContent:"space-between",marginTop:3}}>
            <span style={{fontFamily:"var(--mono)",fontSize:7,color:"var(--ink4)"}}>10 days ago</span>
            <span style={{fontFamily:"var(--mono)",fontSize:7,color:"var(--ink4)"}}>today: {sp.n}</span>
          </div>
        </div>
        <div className="section-head">
          <span className="section-head-title">RECORDINGS · TODAY</span>
        </div>
        <table className="sp-det-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>File</th>
              <th>Conf.</th>
            </tr>
          </thead>
          <tbody>
            {show.map((d, i) => (
              <tr key={i}>
                <td style={{fontFamily:"var(--mono)",fontSize:9,color:"var(--ink2)"}}>{d.time}</td>
                <td style={{fontFamily:"var(--mono)",fontSize:8,color:"var(--ink4)"}}>
                  {d.com.split(" ")[0].toLowerCase()}_{d.time.replace(/:/g,"")}.wav
                </td>
                <td style={{textAlign:"right"}}>
                  <ConfBar conf={d.conf} w={40} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SpeciesScreen() {
  const [sort, setSort] = useState("n");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);

  const rows = [...SPECIES]
    .filter(s => s.com.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => sort === "n" ? b.n - a.n : a.com.localeCompare(b.com));

  if (selected) return <SpeciesDetail sp={selected} onBack={() => setSelected(null)} />;

  return (
    <div>
      <div className="log-filters">
        <input
          className="log-search"
          placeholder="Filter by name…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div className="log-filter-sep" />
        {[["n","Count"],["az","A–Z"]].map(([k,l]) => (
          <button key={k} className={`log-sort-btn ${sort===k?"active":""}`} onClick={() => setSort(k)}>{l}</button>
        ))}
      </div>
      <div className="marginal">
        {rows.length} species detected · all time · tap row for detail
      </div>
      <table className="sp-table">
        <thead>
          <tr>
            <th style={{width:36,textAlign:"right",paddingRight:10}}>N</th>
            <th>Species</th>
            <th style={{textAlign:"right",minWidth:72}}>10-day</th>
            <th className="right">Last</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(sp => (
            <tr key={sp.com} onClick={() => setSelected(sp)}>
              <td style={{textAlign:"right",paddingRight:10,verticalAlign:"middle"}}>
                <span className="sp-n">{sp.n}</span>
              </td>
              <td>
                <span className="sp-com">{sp.com}</span>
                <span className="sp-sci-row">{sp.sci}</span>
              </td>
              <td style={{textAlign:"right",verticalAlign:"middle",paddingRight:8}}>
                <Sparkline values={sp.trend} w={56} h={16} />
              </td>
              <td className="right">
                <span className="sp-last">{sp.lastSeen}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* 7-day summary */}
      <div className="section-head" style={{marginTop:0}}>
        <span className="section-head-title">7-DAY SUMMARY</span>
      </div>
      <table className="week-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Count</th>
            <th style={{paddingLeft:0}}></th>
            <th style={{textAlign:"right",paddingRight:16}}>Species</th>
          </tr>
        </thead>
        <tbody>
          {SEVEN_DAY.map(d => (
            <tr key={d.date}>
              <td><span className="week-date">{d.date}</span></td>
              <td><span className="week-n">{d.n}</span></td>
              <td style={{paddingLeft:0}}>
                <span className="week-bar-track">
                  <span className="week-bar-fill" style={{width:`${(d.n/201)*100}%`}} />
                </span>
              </td>
              <td className="week-species">{d.species} spp.</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StationScreen() {
  const readings = [
    { label:"CPU load", val:"34", unit:"%", gauge:0.34 },
    { label:"CPU temp", val:"52.4", unit:"°C", gauge:0.62, warn: false },
    { label:"Disk used", val:"67", unit:"%", gauge:0.67, warn: true },
    { label:"Uptime", val:"14d 06h", unit:"", gauge:null },
    { label:"Sample rate", val:"48 000", unit:"Hz", gauge:null },
    { label:"Det / hour", val:"12", unit:"", gauge:null },
    { label:"Lat / Lon", val:"47.6 / −122.3", unit:"", gauge:null },
    { label:"Model", val:"BirdNET_6K_V2.4", unit:"", gauge:null, small:true },
  ];

  const services = [
    { name:"birdnet.service",       pid:"1241", mem:"312 MB", state:"active" },
    { name:"extraction.service",    pid:"1308", mem:"48 MB",  state:"active" },
    { name:"chart_viewer.service",  pid:"1399", mem:"24 MB",  state:"active" },
    { name:"caddy.service",         pid:"1102", mem:"18 MB",  state:"active" },
    { name:"sox.service",           pid:"1187", mem:"8 MB",   state:"active" },
    { name:"rtsp_server.service",   pid:"1450", mem:"14 MB",  state:"active" },
  ];

  return (
    <div>
      <div className="section-head">
        <span className="section-head-title">SYSTEM READINGS</span>
        <span className="section-head-meta">RPi 4B · Trixie</span>
      </div>
      <table className="readings-table">
        <thead>
          <tr>
            <th>Parameter</th>
            <th style={{textAlign:"right",paddingRight:16}}>Value</th>
          </tr>
        </thead>
        <tbody>
          {readings.map(r => (
            <tr key={r.label}>
              <td><span className="rd-label">{r.label}</span></td>
              <td style={{textAlign:"right",paddingRight:16}}>
                <span className={`rd-val ${r.warn ? "warn" : ""}`} style={r.small ? {fontSize:10} : {}}>
                  {r.val}
                </span>
                {r.unit && <span className="rd-unit">{r.unit}</span>}
                {r.gauge !== null && (
                  <span className="inline-gauge">
                    <span className="inline-gauge-fill" style={{width:`${r.gauge*100}%`, background: r.warn ? "var(--red)" : "var(--ink)"}} />
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="section-head">
        <span className="section-head-title">SERVICES</span>
      </div>
      <table className="svc-table">
        <thead>
          <tr>
            <th>Unit</th>
            <th>PID</th>
            <th className="right">Memory</th>
          </tr>
        </thead>
        <tbody>
          {services.map(s => (
            <tr key={s.name}>
              <td className="svc-ok">{s.name}</td>
              <td style={{color:"var(--ink3)"}}>{s.pid}</td>
              <td className="right" style={{color:"var(--ink3)"}}>{s.mem}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="section-head">
        <span className="section-head-title">CONTROLS</span>
      </div>
      <div className="ctrl-row">
        {[
          {label:"Analysis",  btn:"Restart",         danger:false},
          {label:"Update",    btn:"Check for update", danger:false},
          {label:"Recording", btn:"Pause capture",    danger:false},
          {label:"Disk",      btn:"Run cleanup",      danger:true},
        ].map(c => (
          <div className="ctrl-item" key={c.label}>
            <span className="ctrl-item-label">{c.label}</span>
            <button className={`ctrl-item-btn ${c.danger?"danger":""}`}>{c.btn}</button>
          </div>
        ))}
      </div>

      <div className="marginal" style={{marginTop:0}}>
        BirdNET-Pi v0.11 · Nachtzuster fork · Lynnwood, WA field station
      </div>
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

const TABS = [
  { id:"live",    label:"Live" },
  { id:"log",     label:"Log" },
  { id:"species", label:"Species" },
  { id:"station", label:"Station" },
];

export default function App() {
  const [tab, setTab] = useState("live");
  const [time, setTime] = useState("");

  useEffect(() => {
    const tick = () => {
      const n = new Date();
      const hms = n.toTimeString().slice(0,8);
      const date = n.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric",year:"numeric"});
      setTime(`${date} · ${hms}`);
    };
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <>
      <style>{CSS}</style>
      <div className="app">
        <div className="masthead">
          <div className="masthead-top">
            <div className="masthead-title">BirdNET-Pi</div>
            <div className="masthead-subtitle">Lynnwood · WA</div>
          </div>
          <div className="masthead-meta">
            <span className="masthead-date">{time}</span>
            <span className="live-indicator">
              <span className="live-dot" />
              RECORDING
            </span>
          </div>
        </div>

        <div className="section-nav">
          {TABS.map(t => (
            <button
              key={t.id}
              className={`section-btn ${tab === t.id ? "active" : ""}`}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="scroll" style={{position:"relative"}}>
          {tab === "live"    && <LiveScreen />}
          {tab === "log"     && <LogScreen />}
          {tab === "species" && <SpeciesScreen />}
          {tab === "station" && <StationScreen />}
        </div>
      </div>
    </>
  );
}
