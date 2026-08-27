#!/usr/bin/osascript -l JavaScript
// tile.js — tile every on-screen window of one app into an even grid on one monitor.
//
//   tile.js "<App Name>" [--cols N] [--screen N] [--gap PX] [--dry-run] [--list]
//
// Exit codes: 0 ok · 1 usage/app error · 2 Accessibility permission needed
//
// Coordinates: everything printed here is in top-left-origin global pixels (the
// system Accessibility/CGWindow convention). NSScreen reports bottom-left-origin
// rects; convert() flips them once, at the edge.

ObjC.import('AppKit');
ObjC.import('CoreGraphics');
ObjC.import('ApplicationServices');
ObjC.import('stdlib');

var CELL_ASPECT = 1.6;  // preferred cell width/height when choosing a column count
var MIN_WIN     = 50;   // CGWindowList: ignore helper windows smaller than this (px); also the smallest sane cell
var DEFAULT_GAP = '2.5%'; // gutter between windows and at the monitor edges, as a share of the monitor's shorter side
                          // (≈36 px on a 1440-px-tall display, scales with the screen). Pixels also accepted. Env TILE_GAP overrides.
var TOL         = 16;   // px: apps that size windows in character cells (Terminal, editors) land a few px short — still tiled

var USAGE = [
  'usage: tile.js "<App Name>" [--cols N] [--screen N] [--gap PX] [--dry-run] [--list]',
  '',
  '  <App Name>   running app: localized name, bundle id, or .app file name (case-insensitive,',
  '               multi-word names may be unquoted). Use --list to see candidates.',
  '  --cols N     force N columns (default: chosen from window count and monitor shape)',
  '  --screen N   monitor index from --list (default: the one under the app\'s front window)',
  '  --gap SIZE   gutter between windows and at the monitor edges: pixels (36) or a percentage of the',
  '               monitor\'s shorter side (2.5%). Default 2.5%; env TILE_GAP',
  '  --margin SIZE  outer gutter only, when it should differ from --gap (env TILE_MARGIN)',
  '  --dry-run    print the plan, move nothing (needs no permissions)',
  '  --list       list monitors and running apps with their on-screen window counts',
  '  --relay      always exit 0 (the /macos:tile skill uses this so the model can relay any message)',
].join('\n');
var RELAY = false;

// Which app macOS holds responsible for this process — the one to enable in System Settings.
// __CFBundleIdentifier is set by LaunchServices on every process a .app spawns (Terminal, VS Code, …).
function hostApp() {
  var env = ObjC.deepUnwrap($.NSProcessInfo.processInfo.environment) || {};
  var bid = env.__CFBundleIdentifier || '', tp = env.TERM_PROGRAM || '';
  var byBundle = { 'com.apple.Terminal': 'Terminal', 'com.googlecode.iterm2': 'iTerm2', 'com.mitchellh.ghostty': 'Ghostty',
                   'com.microsoft.VSCode': 'Visual Studio Code', 'com.microsoft.VSCodeInsiders': 'Visual Studio Code - Insiders',
                   'com.todesktop.230313mzl4w4u92': 'Cursor', 'dev.warp.Warp-Stable': 'Warp', 'com.anthropic.claudefordesktop': 'Claude' };
  var byTerm = { Apple_Terminal: 'Terminal', 'iTerm.app': 'iTerm2', ghostty: 'Ghostty', vscode: 'Visual Studio Code', WarpTerminal: 'Warp' };
  var name = byBundle[bid] || byTerm[tp] || '';
  if (!name && bid) { var m = runningApps().filter(function (a) { return a.bundle === bid; }); if (m.length) name = m[0].name; }
  return { name: name || 'the app that launched this terminal', bundle: bid };
}
function permissionMsg() {
  var h = hostApp();
  return [
    'Accessibility permission is required to move windows, and ' + h.name + ' does not have it.',
    '',
    '  System Settings → Privacy & Security → Accessibility → enable ' + h.name + (h.bundle ? '  (' + h.bundle + ')' : ''),
    '',
    'macOS attributes this script to the app that launched it (Terminal, iTerm2, Ghostty, VS Code, Claude desktop),',
    'so that is the app to enable — not osascript. Then re-run. --dry-run needs no permissions.',
  ].join('\n');
}

// ---------------------------------------------------------------- helpers
function out(s) {
  var str = $.NSString.alloc.initWithUTF8String(String(s) + '\n');
  $.NSFileHandle.fileHandleWithStandardOutput.writeData(str.dataUsingEncoding($.NSUTF8StringEncoding));
}
function die(msg, code) { out(msg); $.exit(RELAY ? 0 : (code === undefined ? 1 : code)); }
function str(v) { try { var s = ObjC.unwrap(v); return typeof s === 'string' ? s : ''; } catch (e) { return ''; } }
function r(n) { return Math.round(n); }
function fmt(b) { return '(' + r(b.x) + ',' + r(b.y) + ' ' + r(b.w) + '×' + r(b.h) + ')'; }
function pad(s, n) { s = String(s); while (s.length < n) s += ' '; return s; }
// A gutter size is pixels ("36") or a percentage of the shorter side of the monitor's usable area ("2.5%").
function parseSize(what, v) {
  var m = /^(\d+(?:\.\d+)?)(%?)$/.exec(String(v).trim());
  if (!m) die(what + ' must be pixels (e.g. 36) or a percentage of the monitor\'s shorter side (e.g. 2.5%), got: ' + v);
  return m[2] ? { pct: parseFloat(m[1]), text: m[1] + '%' } : { px: parseInt(m[1], 10), text: m[1] + ' px' };
}
function envSize(name, dflt) {
  var v = (ObjC.deepUnwrap($.NSProcessInfo.processInfo.environment) || {})[name];
  return (v === undefined || v === '') ? dflt : parseSize(name, v);
}
function resolveSize(size, usable) { return size.pct !== undefined ? Math.round(Math.min(usable.w, usable.h) * size.pct / 100) : size.px; }
function describeSize(px, size) { return px + (size.pct !== undefined ? ' (' + size.text + ')' : ''); }
function clip(s, n) { return s.length > n ? s.slice(0, n - 1) + '…' : s; }

// ---------------------------------------------------------------- args
function parseArgs(argv) {
  var o = { app: null, cols: null, screen: null, gap: envSize('TILE_GAP', parseSize('default gap', DEFAULT_GAP)), margin: envSize('TILE_MARGIN', null), dry: false, list: false, help: false };
  var words = [];
  for (var i = 0; i < argv.length; i++) {
    var a = String(argv[i]), v = null, eq = a.indexOf('=');
    if (a.charAt(0) === '-' && eq > 0) { v = a.slice(eq + 1); a = a.slice(0, eq); }
    function sval() { if (v === null) v = String(argv[++i]); return v; }
    function val() { var n = parseInt(sval(), 10); if (isNaN(n)) die('Bad value for ' + a + ': ' + v); return n; }
    if (a === '--dry-run' || a === '--print' || a === '-n') o.dry = true;
    else if (a === '--list' || a === '-l') o.list = true;
    else if (a === '--help' || a === '-h') o.help = true;
    else if (a === '--relay') RELAY = true;
    else if (a === '--cols' || a === '-c') o.cols = val();
    else if (a === '--screen' || a === '-s') o.screen = val();
    else if (a === '--gap' || a === '-g') o.gap = parseSize('--gap', sval());
    else if (a === '--margin' || a === '-m') o.margin = parseSize('--margin', sval());
    else if (a.charAt(0) === '-') die('Unknown option: ' + a + '\n\n' + USAGE);
    else words.push(a);
  }
  if (words.length) o.app = words.join(' ');
  if (o.cols !== null && o.cols < 1) die('--cols must be ≥ 1');
  if (o.margin === null) o.margin = o.gap;
  return o;
}

// ---------------------------------------------------------------- monitors
function screens() {
  var arr = $.NSScreen.screens, n = arr.count, res = [];
  var primaryH = arr.objectAtIndex(0).frame.size.height;      // screens[0] always has origin (0,0)
  function convert(f) { return { x: f.origin.x, y: primaryH - (f.origin.y + f.size.height), w: f.size.width, h: f.size.height }; }
  for (var i = 0; i < n; i++) {
    var s = arr.objectAtIndex(i), name = '';
    try { name = str(s.localizedName); } catch (e) {}
    res.push({ index: i + 1, name: name || ('Display ' + (i + 1)), full: convert(s.frame), usable: convert(s.visibleFrame) });
  }
  return res;
}
function overlap(a, b) {
  var w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  var h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
  return (w > 0 && h > 0) ? w * h : 0;
}
function screenFor(win, scr) {
  var best = scr[0], bestA = -1;
  scr.forEach(function (s) { var a = overlap(win, s.full); if (a > bestA) { bestA = a; best = s; } });
  return best;
}

// ---------------------------------------------------------------- apps
function runningApps() {
  var arr = $.NSWorkspace.sharedWorkspace.runningApplications, n = arr.count, res = [];
  for (var i = 0; i < n; i++) {
    var a = arr.objectAtIndex(i);
    if (Number(a.activationPolicy) !== 0) continue;              // bridges as a string; regular (Dock-visible) apps only
    var file = '';
    try { file = str(a.bundleURL.lastPathComponent).replace(/\.app$/, ''); } catch (e) {}
    res.push({ name: str(a.localizedName), bundle: str(a.bundleIdentifier), file: file, pid: Number(a.processIdentifier) });
  }
  return res;
}
function findApp(q) {
  var apps = runningApps(), ql = q.toLowerCase();
  function names(a) { return [a.name, a.bundle, a.file]; }
  var exact = apps.filter(function (a) { return names(a).some(function (n) { return n.toLowerCase() === ql; }); });
  if (exact.length === 1) return exact[0];
  var partial = apps.filter(function (a) { return names(a).some(function (n) { return n.toLowerCase().indexOf(ql) >= 0; }); });
  if (partial.length === 1) return partial[0];
  if (partial.length > 1) die('Ambiguous app "' + q + '": ' + partial.map(function (a) { return a.name; }).join(', '));
  die('No running app matches "' + q + '". Use --list to see candidates.');
}

// ---------------------------------------------------------------- windows
// Permission-free listing. Front-to-back, current Space only, minimized excluded.
// The CFArrayRef must be cast to an object before deepUnwrap will turn it into a JS array.
function cgList() {
  try { return ObjC.deepUnwrap(ObjC.castRefToObject($.CGWindowListCopyWindowInfo(1 | 16, 0))) || []; }   // OnScreenOnly | ExcludeDesktopElements
  catch (e) { return []; }
}
function cgWindows(pid) {
  return cgList().filter(function (w) {
    var b = w.kCGWindowBounds;
    return w.kCGWindowOwnerPID === pid && w.kCGWindowLayer === 0 && (w.kCGWindowAlpha === undefined || w.kCGWindowAlpha > 0)
      && b && b.Width >= MIN_WIN && b.Height >= MIN_WIN;
  }).map(function (w) {
    var b = w.kCGWindowBounds;
    return { x: b.X, y: b.Y, w: b.Width, h: b.Height, title: w.kCGWindowName || '', ax: null };
  });
}
// Accessibility listing via System Events. Same ordering; carries the reference we set later.
// References are by index (windows.at(i)), never by title: JXA's default element references are
// byName, and a title that changes between the read and the write (Terminal's does, constantly)
// makes the write fail with -1728 "Can't get object".
function axWindows(pid) {
  var se = Application('System Events');
  if (!se.processes.whose({ unixId: pid })().length) die('System Events cannot see pid ' + pid);
  var proc = se.processes.whose({ unixId: pid })[0];
  var n = proc.windows.length, res = [];
  for (var i = 0; i < n; i++) {
    var w = proc.windows[i];
    var sub = ''; try { sub = w.subrole(); } catch (e) {}
    if (sub && sub !== 'AXStandardWindow') continue;             // skip dialogs, floating panels, sheets
    var mini = false; try { mini = !!w.attributes.byName('AXMinimized').value(); } catch (e) {}
    if (mini) continue;
    var p = w.position(), s = w.size(), t = ''; try { t = w.name() || ''; } catch (e) {}
    res.push({ x: p[0], y: p[1], w: s[0], h: s[1], title: t, ax: w });
  }
  return res;
}
function axTrusted() { try { return !!$.AXIsProcessTrusted(); } catch (e) { return null; } }   // null = could not check
function axPrompt() { try { $.AXIsProcessTrustedWithOptions($({ AXTrustedCheckOptionPrompt: true })); } catch (e) {} }
function explainAxError(e) {
  var m = String(e && e.message || e);
  if (/assistive|-1719|-25211/.test(m)) return permissionMsg();
  if (/-1743|not authorized/i.test(m)) return hostApp().name + ' is not allowed to send Apple events to System Events.\n\n  System Settings → Privacy & Security → Automation → ' + hostApp().name + ' → enable "System Events"\n\nThen re-run.';
  return 'System Events error: ' + m;
}

// ---------------------------------------------------------------- layout
function chooseCols(n, usable) {
  var best = 1, bestScore = Infinity, aspect = usable.w / usable.h;
  for (var c = 1; c <= n; c++) {
    var rows = Math.ceil(n / c), cell = aspect * rows / c;
    var score = Math.abs(Math.log(cell / CELL_ASPECT)) + (c * rows - n) / n;   // shape fit + empty-cell penalty
    if (score < bestScore) { bestScore = score; best = c; }
  }
  return best;
}
// gap: space between cells. margin: space between the outer cells and the monitor's usable edge.
function layout(n, cols, usable, gap, margin) {
  var rows = Math.ceil(n / cols);
  var x0 = usable.x + margin, y0 = usable.y + margin, W = usable.w - 2 * margin, H = usable.h - 2 * margin;
  var cw = Math.floor((W - gap * (cols - 1)) / cols);
  var ch = Math.floor((H - gap * (rows - 1)) / rows);
  if (cw < MIN_WIN || ch < MIN_WIN) die('Cells would be ' + cw + '×' + ch + ' px — reduce --gap, --margin or --cols.');
  var cells = [];
  for (var i = 0; i < n; i++) {
    var col = i % cols, row = Math.floor(i / cols);
    cells.push({ x: x0 + col * (cw + gap), y: y0 + row * (ch + gap), w: cw, h: ch });
  }
  return { cols: cols, rows: rows, cw: cw, ch: ch, cells: cells };
}

// ---------------------------------------------------------------- main
function run(argv) {
  try { return main(argv); }
  catch (e) { die('Error: ' + String(e && e.message || e).split('\n')[0], 1); }
}
function main(argv) {
  var o = parseArgs(argv);
  if (o.help) { out(USAGE); return; }
  var scr = screens();

  if (o.list) {
    out('Monitors (index · name · usable area, top-left coords):');
    scr.forEach(function (s) { out('  ' + s.index + '  ' + pad(s.name, 22) + ' ' + fmt(s.usable)); });
    var counts = {};
    cgList().forEach(function (w) {
      var b = w.kCGWindowBounds;
      if (w.kCGWindowLayer === 0 && b && b.Width >= MIN_WIN && b.Height >= MIN_WIN) counts[w.kCGWindowOwnerPID] = (counts[w.kCGWindowOwnerPID] || 0) + 1;
    });
    out('\nRunning apps (on-screen windows in this Space):');
    runningApps().sort(function (a, b) { return a.name.localeCompare(b.name); }).forEach(function (a) {
      out('  ' + pad(counts[a.pid] || 0, 3) + ' ' + pad(a.name, 28) + ' ' + a.bundle);
    });
    out('\nAccessibility granted to ' + hostApp().name + ': ' + ({ true: 'yes', false: 'no', null: 'unknown' })[axTrusted()]);
    return;
  }

  if (!o.app) die(USAGE);
  var app = findApp(o.app);
  var trusted = axTrusted();

  // Pick the window source. Dry runs never trigger a permission prompt.
  var wins, source;
  if (trusted === false && !o.dry) { axPrompt(); die(permissionMsg(), 2); }
  if (trusted === false) { wins = cgWindows(app.pid); source = 'CGWindowList — ' + hostApp().name + ' lacks Accessibility, so listing is approximate'; }
  else {
    try { wins = axWindows(app.pid); source = 'Accessibility'; }
    catch (e) {
      if (!o.dry) die(explainAxError(e), 2);
      wins = cgWindows(app.pid); source = 'CGWindowList — fell back because: ' + String(e.message || e).split('\n')[0];
    }
  }

  if (!wins.length) die(app.name + ' has no tileable windows in the current Space (minimized and other-Space windows are skipped).');

  var screen;
  if (o.screen !== null) {
    if (o.screen < 1 || o.screen > scr.length) die('--screen must be 1–' + scr.length + ' (see --list)');
    screen = scr[o.screen - 1];
  } else screen = screenFor(wins[0], scr);

  var cols = o.cols !== null ? Math.min(o.cols, wins.length) : chooseCols(wins.length, screen.usable);
  var gap = resolveSize(o.gap, screen.usable), margin = resolveSize(o.margin, screen.usable);
  var L = layout(wins.length, cols, screen.usable, gap, margin);
  var empty = L.cols * L.rows - wins.length;

  out('App:     ' + app.name + ' (' + app.bundle + ', pid ' + app.pid + ')');
  out('Monitor: ' + screen.index + ' of ' + scr.length + ' · ' + screen.name + ' · usable ' + fmt(screen.usable));
  out('Layout:  ' + wins.length + ' window' + (wins.length === 1 ? '' : 's') + ' → ' + L.cols + ' col × ' + L.rows + ' row, cell ' + L.cw + '×' + L.ch
      + ', gap ' + describeSize(gap, o.gap) + ', margin ' + describeSize(margin, o.margin) + (empty ? ', ' + empty + ' empty cell' + (empty === 1 ? '' : 's') + ' in last row' : ''));
  out('Windows (front → back, via ' + source + '):');

  var moved = 0, refused = 0, failed = 0;
  wins.forEach(function (w, i) {
    var c = L.cells[i], label = '  #' + pad(i + 1, 2) + ' ' + pad(clip(w.title || '', 32), 32) + ' ' + fmt(w) + ' → ' + fmt(c);
    if (o.dry) { out(label); return; }
    var p, s;
    try {
      w.ax.size = [c.w, c.h]; w.ax.position = [c.x, c.y]; w.ax.size = [c.w, c.h];   // size-position-size: survives edge clamping
      p = w.ax.position(); s = w.ax.size();
    } catch (e) { failed++; out(label + '  ✗ could not move: ' + String(e && e.message || e).split('\n')[0]); return; }
    var got = { x: p[0], y: p[1], w: s[0], h: s[1] };
    var dx = Math.abs(got.x - c.x), dy = Math.abs(got.y - c.y), dw = Math.abs(got.w - c.w), dh = Math.abs(got.h - c.h);
    var exact = dx + dy + dw + dh === 0, ok = dx <= TOL && dy <= TOL && dw <= TOL && dh <= TOL;
    if (ok) moved++; else refused++;
    out(label + (exact ? '  ✓' : ok ? '  ✓ snapped to ' + fmt(got) : '  ✗ app settled at ' + fmt(got)));
  });

  if (o.dry) { out('\nDRY RUN — nothing was moved. Re-run without --dry-run to apply.'); return; }
  var summary = 'Tiled ' + moved + ' of ' + wins.length + ' window' + (wins.length === 1 ? '' : 's')
    + (refused ? ', ' + refused + ' refused the exact size' : '') + (failed ? ', ' + failed + ' could not be moved' : '') + '.';
  if (failed) die('\n' + summary, 1);
  out('\n' + summary);
}
