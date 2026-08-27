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
function env(name) { var v = (ObjC.deepUnwrap($.NSProcessInfo.processInfo.environment) || {})[name]; return v === undefined ? '' : String(v); }
var LAYOUTS_FILE = env('TILE_LAYOUTS') || (env('HOME') + '/.config/macos-tile/layouts.json');   // saved layouts: {name: {steps: ["<tile args>", …]}}

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
  '  --region R   use only part of the monitor: left, right, top, bottom, top-left, top-right, bottom-left,',
  '               bottom-right, left-third, middle-third, right-third, left-two-thirds, right-two-thirds,',
  '               or x,y,w,h in percent of the usable area (e.g. 0,0,50,100)',
  '  --front N    only the N frontmost windows; the others stay where they are',
  '  --match TEXT only windows whose title contains TEXT (case-insensitive)',
  '  --dry-run    print the plan, move nothing (needs no permissions)',
  '  --list       list monitors and running apps with their on-screen window counts',
  '',
  '  --save NAME  also save this command as layout NAME (replacing NAME); --add NAME appends it as a further step',
  '  --run NAME   run every step of saved layout NAME in order (--dry-run applies to all of them)',
  '  --layouts    list saved layouts; --forget NAME deletes one',
  '               store: ~/.config/macos-tile/layouts.json (env TILE_LAYOUTS)',
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
var REGIONS = {
  full: [0, 0, 1, 1], left: [0, 0, .5, 1], right: [.5, 0, .5, 1], top: [0, 0, 1, .5], bottom: [0, .5, 1, .5],
  'top-left': [0, 0, .5, .5], 'top-right': [.5, 0, .5, .5], 'bottom-left': [0, .5, .5, .5], 'bottom-right': [.5, .5, .5, .5],
  'left-third': [0, 0, 1 / 3, 1], 'middle-third': [1 / 3, 0, 1 / 3, 1], 'right-third': [2 / 3, 0, 1 / 3, 1],
  'left-two-thirds': [0, 0, 2 / 3, 1], 'right-two-thirds': [1 / 3, 0, 2 / 3, 1],
};
// A region is a named part of the monitor's usable area, or x,y,w,h in percent of it.
function parseRegion(v) {
  var raw = String(v).trim();
  var key = raw.toLowerCase().replace(/[\s_]+/g, '-').replace(/-half$/, '').replace(/^(center|centre)/, 'middle').replace(/^upper-/, 'top-').replace(/^lower-/, 'bottom-');
  if (REGIONS[key]) return { name: key, frac: REGIONS[key] };
  var parts = raw.split(',').map(function (n) { return parseFloat(n); });
  if (parts.length === 4 && parts.every(function (n) { return !isNaN(n) && n >= 0 && n <= 100; }) && parts[2] > 0 && parts[3] > 0)
    return { name: raw + '%', frac: parts.map(function (n) { return n / 100; }) };
  die('--region must be one of ' + Object.keys(REGIONS).join(', ') + ', or x,y,w,h in percent (e.g. 0,0,50,100); got: ' + v);
}
function applyRegion(usable, region) {
  var f = region.frac;
  return { x: Math.round(usable.x + usable.w * f[0]), y: Math.round(usable.y + usable.h * f[1]), w: Math.round(usable.w * f[2]), h: Math.round(usable.h * f[3]) };
}
function resolveSize(size, usable) { return size.pct !== undefined ? Math.round(Math.min(usable.w, usable.h) * size.pct / 100) : size.px; }
function describeSize(px, size) { return px + (size.pct !== undefined ? ' (' + size.text + ')' : ''); }

// ---------------------------------------------------------------- saved layouts
function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, $());
  return s.isNil() ? null : ObjC.unwrap(s);
}
function writeFile(path, text) {
  $.NSFileManager.defaultManager.createDirectoryAtPathWithIntermediateDirectoriesAttributesError(path.replace(/\/[^\/]*$/, ''), true, $(), $());
  if (!$.NSString.alloc.initWithUTF8String(text).writeToFileAtomicallyEncodingError(path, true, $.NSUTF8StringEncoding, $())) die('Could not write ' + path);
}
function loadLayouts() {
  var text = readFile(LAYOUTS_FILE); if (text === null) return {};
  try { var d = JSON.parse(text); return (d && typeof d === 'object' && !Array.isArray(d)) ? d : {}; }
  catch (e) { die('Cannot parse ' + LAYOUTS_FILE + ': ' + e.message); }
}
function storeLayouts(d) { writeFile(LAYOUTS_FILE, JSON.stringify(d, null, 2) + '\n'); }
function quoteArgs(tokens) { return tokens.map(function (t) { return /[\s"]/.test(t) || t === '' ? '"' + t.replace(/"/g, '\\"') + '"' : t; }).join(' '); }
function tokenize(line) {   // split on whitespace, honouring double and single quotes
  var res = [], cur = '', q = null, has = false;
  for (var i = 0; i < line.length; i++) {
    var ch = line[i];
    if (q) { if (ch === q) q = null; else if (ch === '\\' && q === '"' && line[i + 1] === '"') { cur += '"'; i++; } else cur += ch; }
    else if (ch === '"' || ch === "'") { q = ch; has = true; }
    else if (/\s/.test(ch)) { if (cur || has) { res.push(cur); cur = ''; has = false; } }
    else cur += ch;
  }
  if (q) die('Unbalanced quote in saved step: ' + line);
  if (cur || has) res.push(cur);
  return res;
}
function saveLayout(name, step, append) {
  var d = loadLayouts();
  if (append) { if (!d[name] || !d[name].steps) die('No saved layout "' + name + '" to add to — use --save ' + name + ' first.'); d[name].steps.push(step); }
  else d[name] = { steps: [step] };
  storeLayouts(d);
  var n = d[name].steps.length;
  out('Saved layout "' + name + '" (' + n + ' step' + (n === 1 ? '' : 's') + ') → ' + LAYOUTS_FILE + '\n');
}
function listLayouts() {
  var d = loadLayouts(), names = Object.keys(d).sort();
  out('Saved layouts (' + LAYOUTS_FILE + '):');
  if (!names.length) { out('  (none — add --save NAME to any tile command)'); return; }
  names.forEach(function (n) { out('  ' + n); (d[n].steps || []).forEach(function (st, i) { out('    ' + (i + 1) + '. ' + st); }); });
}
function forgetLayout(name) { var d = loadLayouts(); if (!d[name]) die('No saved layout "' + name + '".'); delete d[name]; storeLayouts(d); out('Forgot layout "' + name + '".'); }
function runLayout(name, outer, scr) {
  var d = loadLayouts();
  if (!d[name] || !d[name].steps) die('No saved layout "' + name + '". Saved: ' + (Object.keys(d).join(', ') || 'none') + '.');
  var steps = d[name].steps, failed = 0;
  steps.forEach(function (line, i) {
    out((i ? '\n' : '') + '── ' + name + ' · step ' + (i + 1) + '/' + steps.length + ': ' + line + ' ──');
    var o = parseArgs(tokenize(line));
    if (o.run || o.save || o.add || o.list || o.layouts || o.forget || o.help || !o.app) die('Step ' + (i + 1) + ' of "' + name + '" is not a tile command: ' + line);
    o.dry = o.dry || outer.dry;
    failed += tileOnce(o, scr);
  });
  if (failed) $.exit(RELAY ? 0 : 1);
}
function clip(s, n) { return s.length > n ? s.slice(0, n - 1) + '…' : s; }

// ---------------------------------------------------------------- args
function parseArgs(argv) {
  var o = { app: null, cols: null, screen: null, gap: envSize('TILE_GAP', parseSize('default gap', DEFAULT_GAP)), margin: envSize('TILE_MARGIN', null), region: null, front: null, match: null, dry: false, list: false, help: false,
            save: null, add: null, run: null, layouts: false, forget: null, kept: [] };
  var words = [];
  for (var i = 0; i < argv.length; i++) {
    var a = String(argv[i]), v = null, eq = a.indexOf('='), start = i, skip = false;   // skip: not part of the tile command itself
    if (a.charAt(0) === '-' && eq > 0) { v = a.slice(eq + 1); a = a.slice(0, eq); }
    function sval() { if (v === null) v = String(argv[++i]); return v; }
    function val() { var n = parseInt(sval(), 10); if (isNaN(n)) die('Bad value for ' + a + ': ' + v); return n; }
    if (a === '--dry-run' || a === '--print' || a === '-n') { o.dry = true; skip = true; }
    else if (a === '--list' || a === '-l') { o.list = true; skip = true; }
    else if (a === '--help' || a === '-h') { o.help = true; skip = true; }
    else if (a === '--relay') { RELAY = true; skip = true; }
    else if (a === '--save') { o.save = sval(); skip = true; }
    else if (a === '--add') { o.add = sval(); skip = true; }
    else if (a === '--run') { o.run = sval(); skip = true; }
    else if (a === '--layouts') { o.layouts = true; skip = true; }
    else if (a === '--forget') { o.forget = sval(); skip = true; }
    else if (a === '--cols' || a === '-c') o.cols = val();
    else if (a === '--screen' || a === '-s') o.screen = val();
    else if (a === '--gap' || a === '-g') o.gap = parseSize('--gap', sval());
    else if (a === '--margin' || a === '-m') o.margin = parseSize('--margin', sval());
    else if (a === '--region' || a === '-r') o.region = parseRegion(sval());
    else if (a === '--front' || a === '-f') o.front = val();
    else if (a === '--match') o.match = String(sval()).toLowerCase();
    else if (a.charAt(0) === '-') die('Unknown option: ' + a + '\n\n' + USAGE);
    else words.push(a);
    if (!skip) for (var k = start; k <= i; k++) o.kept.push(String(argv[k]));
  }
  if (words.length) o.app = words.join(' ');
  if (o.cols !== null && o.cols < 1) die('--cols must be ≥ 1');
  if (o.margin === null) o.margin = o.gap;
  if (o.front !== null && o.front < 1) die('--front must be ≥ 1');
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
    var byX = scr.slice().sort(function (a, b) { return a.usable.x - b.usable.x; }), hint = {};
    if (scr.length > 1 && byX[0].usable.x !== byX[byX.length - 1].usable.x)
      byX.forEach(function (s, i) { hint[s.index] = i === 0 ? 'left' : i === byX.length - 1 ? 'right' : 'middle'; });
    out('Monitors (index · name · usable area in top-left coords · position):');
    scr.forEach(function (s) {
      var tags = []; if (hint[s.index]) tags.push(hint[s.index]); if (s.index === 1) tags.push('main, menu bar');
      out('  ' + s.index + '  ' + pad(s.name, 22) + ' ' + pad(fmt(s.usable), 24) + (tags.length ? ' ' + tags.join(', ') : ''));
    });
    var counts = {}, where = {};
    cgList().forEach(function (w) {
      var b = w.kCGWindowBounds;
      if (!(w.kCGWindowLayer === 0 && b && b.Width >= MIN_WIN && b.Height >= MIN_WIN)) return;
      var pid = w.kCGWindowOwnerPID, m = screenFor({ x: b.X, y: b.Y, w: b.Width, h: b.Height }, scr).index;
      counts[pid] = (counts[pid] || 0) + 1; where[pid] = where[pid] || {}; where[pid][m] = (where[pid][m] || 0) + 1;
    });
    out('\nRunning apps (on-screen windows in this Space · which monitor they are on):');
    runningApps().sort(function (a, b) { return a.name.localeCompare(b.name); }).forEach(function (a) {
      var c = counts[a.pid] || 0, on = '';
      if (c) on = '  on monitor ' + Object.keys(where[a.pid]).sort().map(function (k) { return k + (where[a.pid][k] > 1 ? ' ×' + where[a.pid][k] : ''); }).join(', ');
      out('  ' + pad(c, 3) + ' ' + pad(a.name, 28) + ' ' + pad(a.bundle, 34) + on);
    });
    out('\nAccessibility granted to ' + hostApp().name + ': ' + ({ true: 'yes', false: 'no', null: 'unknown' })[axTrusted()] + '  (needed to apply; dry runs work without it)');
    return;
  }

  if (o.layouts) { listLayouts(); return; }
  if (o.forget !== null) { forgetLayout(o.forget); return; }
  if (o.run !== null) { runLayout(o.run, o, scr); return; }
  if (!o.app) die(USAGE);
  if (o.save !== null) saveLayout(o.save, quoteArgs(o.kept), false);
  if (o.add !== null) saveLayout(o.add, quoteArgs(o.kept), true);
  if (tileOnce(o, scr)) $.exit(RELAY ? 0 : 1);
}

// One tile command: resolve app, windows, area, layout; apply unless dry. Returns the number of windows that could not be moved.
function tileOnce(o, scr) {
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

  var total = wins.length, selection = [];
  if (o.match !== null) {
    wins = wins.filter(function (w) { return (w.title || '').toLowerCase().indexOf(o.match) >= 0; });
    if (!wins.length) die('No ' + app.name + ' window title contains "' + o.match + '".');
    selection.push('title contains "' + o.match + '"');
  }
  if (o.front !== null && o.front < wins.length) { wins = wins.slice(0, o.front); selection.push('front ' + o.front); }

  var screen;
  if (o.screen !== null) {
    if (o.screen < 1 || o.screen > scr.length) die('--screen must be 1–' + scr.length + ' (see --list)');
    screen = scr[o.screen - 1];
  } else screen = screenFor(wins[0], scr);

  var area = o.region ? applyRegion(screen.usable, o.region) : screen.usable;   // gutters stay relative to the whole monitor
  var cols = o.cols !== null ? Math.min(o.cols, wins.length) : chooseCols(wins.length, area);
  var gap = resolveSize(o.gap, screen.usable), margin = resolveSize(o.margin, screen.usable);
  var L = layout(wins.length, cols, area, gap, margin);
  var empty = L.cols * L.rows - wins.length;

  out('App:     ' + app.name + ' (' + app.bundle + ', pid ' + app.pid + ')');
  out('Monitor: ' + screen.index + ' of ' + scr.length + ' · ' + screen.name + ' · usable ' + fmt(screen.usable) + (o.region ? ' · region ' + o.region.name + ' ' + fmt(area) : ''));
  out('Layout:  ' + wins.length + ' window' + (wins.length === 1 ? '' : 's') + (selection.length ? ' (of ' + total + '; ' + selection.join(', ') + ')' : '') + ' → ' + L.cols + ' col × ' + L.rows + ' row, cell ' + L.cw + '×' + L.ch
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

  if (o.dry) { out('\nDRY RUN — nothing was moved. Re-run without --dry-run to apply.'); return 0; }
  var summary = 'Tiled ' + moved + ' of ' + wins.length + ' window' + (wins.length === 1 ? '' : 's')
    + (refused ? ', ' + refused + ' refused the exact size' : '') + (failed ? ', ' + failed + ' could not be moved' : '') + '.';
  out('\n' + summary);
  return failed;
}
