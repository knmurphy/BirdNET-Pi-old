<?php
error_reporting(0);
ini_set('display_errors', 0);

// Handle AJAX stats request — must happen before DB connection attempt so that
// a DB failure returns a proper JSON error rather than HTML.
$isAjax = isset($_GET['ajax_stats']) && $_GET['ajax_stats'] === 'true';

$db = new SQLite3('./scripts/birds.db', SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);
if ($db == False) {
  if ($isAjax) {
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Database busy']);
  } else {
    echo "<p>Database busy</p>";
  }
  exit;
}

if (file_exists('./scripts/thisrun.txt')) {
  $config = parse_ini_file('./scripts/thisrun.txt');
} elseif (file_exists('./scripts/firstrun.ini')) {
  $config = parse_ini_file('./scripts/firstrun.ini');
}

$myDate = date('Y-m-d');
$chart = "Combo-$myDate.png";
$time = time();
$refresh = max(1, intval($config['RECORDING_LENGTH'] ?? 15));

// If this is an AJAX stats refresh, return only the stat widget values
if ($isAjax) {
  $totalcount    = $db->querySingle('SELECT COUNT(*) FROM detections') ?? 0;
  $todaycount    = $db->querySingle("SELECT COUNT(*) FROM detections WHERE Date == DATE('now', 'localtime')") ?? 0;
  $hourcount     = $db->querySingle("SELECT COUNT(*) FROM detections WHERE Date == DATE('now', 'localtime') AND TIME >= TIME('now', 'localtime', '-1 hour')") ?? 0;
  $speciestally  = $db->querySingle("SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date == DATE('now','localtime')") ?? 0;
  $totalspecies  = $db->querySingle('SELECT COUNT(DISTINCT Com_Name) FROM detections') ?? 0;
  $stmt = $db->prepare('SELECT Com_Name, Sci_Name, Confidence, Date, Time FROM detections ORDER BY Date DESC, Time DESC LIMIT 1');
  $latest = $stmt ? $stmt->execute()->fetchArray(SQLITE3_ASSOC) : null;
  header('Content-Type: application/json');
  echo json_encode([
    'total'         => number_format($totalcount),
    'today'         => number_format($todaycount),
    'hour'          => number_format($hourcount),
    'species_today' => number_format($speciestally),
    'species_total' => number_format($totalspecies),
    'latest_name'   => $latest ? htmlspecialchars($latest['Com_Name']) : '',
    'latest_raw'    => $latest ? $latest['Com_Name'] : '',
    'latest_date'   => $latest ? htmlspecialchars($latest['Date'] . ' ' . $latest['Time']) : '',
    'latest_conf'   => $latest ? round(floatval($latest['Confidence']) * 100) : 0,
  ]);
  exit;
}

// Full page load — fetch stats
$totalcount    = $db->querySingle('SELECT COUNT(*) FROM detections') ?? 0;
$todaycount    = $db->querySingle("SELECT COUNT(*) FROM detections WHERE Date == DATE('now', 'localtime')") ?? 0;
$hourcount     = $db->querySingle("SELECT COUNT(*) FROM detections WHERE Date == DATE('now', 'localtime') AND TIME >= TIME('now', 'localtime', '-1 hour')") ?? 0;
$speciestally  = $db->querySingle("SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date == DATE('now','localtime')") ?? 0;
$totalspecies  = $db->querySingle('SELECT COUNT(DISTINCT Com_Name) FROM detections') ?? 0;
$stmt = $db->prepare('SELECT Com_Name, Sci_Name, Confidence, Date, Time FROM detections ORDER BY Date DESC, Time DESC LIMIT 1');
$latest = $stmt ? $stmt->execute()->fetchArray(SQLITE3_ASSOC) : null;
?>
<div class="dashboard">
  <div class="dashboard-header">
    <h2>Dashboard</h2>
    <button class="dash-config-btn" onclick="toggleDashConfig()" title="Configure widgets">&#9881; Configure</button>
  </div>

  <div class="dash-config-panel" id="dashConfigPanel">
    <strong>Show widgets:</strong>
    <label><input type="checkbox" data-widget="stat-total" onchange="toggleWidget(this)"> All-Time Detections</label>
    <label><input type="checkbox" data-widget="stat-today" onchange="toggleWidget(this)"> Today&rsquo;s Detections</label>
    <label><input type="checkbox" data-widget="stat-hour" onchange="toggleWidget(this)"> Last Hour</label>
    <label><input type="checkbox" data-widget="stat-species-today" onchange="toggleWidget(this)"> Species Today</label>
    <label><input type="checkbox" data-widget="stat-species-total" onchange="toggleWidget(this)"> Total Species</label>
    <label><input type="checkbox" data-widget="stat-latest" onchange="toggleWidget(this)"> Latest Detection</label>
    <label><input type="checkbox" data-widget="chart-today" onchange="toggleWidget(this)"> Today&rsquo;s Chart</label>
    <label><input type="checkbox" data-widget="spectrogram-live" onchange="toggleWidget(this)"> Live Spectrogram</label>
  </div>

  <div class="widget-grid">
    <div class="widget" id="stat-total">
      <div class="widget-label">All-Time Detections</div>
      <div class="widget-value" id="val-total"><?php echo number_format($totalcount); ?></div>
    </div>

    <div class="widget" id="stat-today">
      <div class="widget-label">Today&rsquo;s Detections</div>
      <div class="widget-value">
        <form action="" method="GET" style="margin:0">
          <button type="submit" name="view" value="Today's Detections" class="widget-link" id="val-today"><?php echo number_format($todaycount); ?></button>
        </form>
      </div>
    </div>

    <div class="widget" id="stat-hour">
      <div class="widget-label">Last Hour</div>
      <div class="widget-value" id="val-hour"><?php echo number_format($hourcount); ?></div>
    </div>

    <div class="widget" id="stat-species-today">
      <div class="widget-label">Species Today</div>
      <div class="widget-value">
        <form action="" method="GET" style="margin:0">
          <input type="hidden" name="view" value="Recordings">
          <button type="submit" name="date" value="<?php echo $myDate; ?>" class="widget-link" id="val-species-today"><?php echo number_format($speciestally); ?></button>
        </form>
      </div>
    </div>

    <div class="widget" id="stat-species-total">
      <div class="widget-label">Total Species</div>
      <div class="widget-value">
        <form action="" method="GET" style="margin:0">
          <button type="submit" name="view" value="Species Stats" class="widget-link" id="val-species-total"><?php echo number_format($totalspecies); ?></button>
        </form>
      </div>
    </div>

    <div class="widget widget-wide" id="stat-latest">
      <div class="widget-label">Latest Detection</div>
      <div class="widget-value widget-value-sm">
        <?php if ($latest): ?>
        <form action="" method="GET" style="margin:0">
          <input type="hidden" name="view" value="Species Stats">
          <button type="submit" name="species" value="<?php echo htmlspecialchars($latest['Com_Name']); ?>" class="widget-link" id="val-latest-name"><?php echo htmlspecialchars($latest['Com_Name']); ?></button>
        </form>
        <div class="widget-meta" id="val-latest-meta"><?php echo htmlspecialchars($latest['Date'] . ' ' . $latest['Time']); ?> &bull; <?php echo round(floatval($latest['Confidence']) * 100); ?>% confidence</div>
        <?php else: ?>
        <div id="val-latest-name">No detections yet.</div>
        <?php endif; ?>
      </div>
    </div>
  </div>

  <div class="widget-grid">
    <div class="widget widget-chart" id="chart-today">
      <div class="widget-label">Today&rsquo;s Chart</div>
      <?php if (file_exists('./Charts/' . $chart)): ?>
        <img id="dash-chart" src="/Charts/<?php echo htmlspecialchars($chart); ?>?nocache=<?php echo $time; ?>" style="width:100%;max-width:100%;">
      <?php else: ?>
        <p class="widget-no-data">Chart not yet available for today.</p>
      <?php endif; ?>
    </div>

    <div class="widget widget-chart" id="spectrogram-live">
      <div class="widget-label">Live Spectrogram</div>
      <img id="dash-spectrogram" src="/spectrogram.png?nocache=<?php echo $time; ?>" style="width:100%;max-width:100%;">
    </div>
  </div>
</div>

<script>
(function () {
  // Restore saved widget visibility from localStorage
  var cfg = JSON.parse(localStorage.getItem('bnp_dashboard_widgets') || 'null');
  document.querySelectorAll('.dash-config-panel input[type=checkbox]').forEach(function (cb) {
    var wid = cb.getAttribute('data-widget');
    var visible = cfg ? (cfg[wid] !== false) : true;
    cb.checked = visible;
    var el = document.getElementById(wid);
    if (el) el.style.display = visible ? '' : 'none';
  });
}());

function toggleWidget(cb) {
  var wid = cb.getAttribute('data-widget');
  var el = document.getElementById(wid);
  if (el) el.style.display = cb.checked ? '' : 'none';
  var cfg = JSON.parse(localStorage.getItem('bnp_dashboard_widgets') || '{}');
  cfg[wid] = cb.checked;
  localStorage.setItem('bnp_dashboard_widgets', JSON.stringify(cfg));
}

function toggleDashConfig() {
  document.getElementById('dashConfigPanel').classList.toggle('dash-config-open');
}

// Auto-refresh spectrogram
setInterval(function () {
  var img = document.getElementById('dash-spectrogram');
  if (img) img.src = '/spectrogram.png?nocache=' + Date.now();
}, <?php echo $refresh; ?> * 1000);

// Auto-refresh stats every 30 seconds via lightweight JSON endpoint
setInterval(function () {
  var xhr = new XMLHttpRequest();
  xhr.onload = function () {
    if (this.status !== 200) {
      console.error('Stats refresh failed with status:', this.status);
      return;
    }
    try {
      var data = JSON.parse(this.responseText);
      var map = {
        'val-total': data.total,
        'val-hour': data.hour
      };
      for (var id in map) {
        var el = document.getElementById(id);
        if (el) el.textContent = map[id];
      }
      var today = document.getElementById('val-today');
      if (today) today.textContent = data.today;
      var st = document.getElementById('val-species-today');
      if (st) st.textContent = data.species_today;
      var stot = document.getElementById('val-species-total');
      if (stot) stot.textContent = data.species_total;
      if (data.latest_name) {
        var ln = document.getElementById('val-latest-name');
        if (ln) {
          ln.textContent = data.latest_name;
          if (ln.tagName === 'BUTTON') ln.value = data.latest_raw;
        }
        var lm = document.getElementById('val-latest-meta');
        if (lm) lm.textContent = data.latest_date + ' \u2022 ' + data.latest_conf + '% confidence';
      }
    } catch (e) {
      console.error('Stats update failed:', e);
    }
  };
  xhr.onerror = function () {
    console.error('Stats refresh request failed', {
      status: xhr.status,
      statusText: xhr.statusText
    });
  };
  xhr.open('GET', 'dashboard.php?ajax_stats=true', true);
  xhr.send();
}, 30000);
</script>
