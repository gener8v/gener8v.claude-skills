# gener8v macOS utilities

Desktop utilities for Claude Code on macOS. Two skills: `/macos:tile` does the work; `/macos:arrange` plans it from plain language.

## `/macos:tile` — tile one app's windows into an even grid

```
/macos:tile <App Name> [--cols N] [--screen N] [--region R] [--front N] [--match TEXT] [--gap SIZE] [--margin SIZE] [--dry-run] [--list]
/macos:tile --save NAME … · --add NAME … · --run NAME · --layouts · --forget NAME
```

Takes every on-screen window of one app and lays them out as equal cells that fill the usable area of one monitor (menu bar and Dock excluded), with a gutter between windows and at the edges that scales with the monitor (2.5 % of its shorter side — 36 px on a 1440-px-tall display). Windows on other monitors are pulled onto the target monitor. Minimized windows and windows in other Spaces are left alone.

```
/macos:tile --list                       # monitors (with left/right hints), running apps, window counts, which monitor
/macos:tile Terminal --dry-run           # print the plan; move nothing
/macos:tile Google Chrome                # apply (multi-word names may be unquoted; "chrome" also matches)
/macos:tile Code --cols 2 --screen 2     # force 2 columns, target the second monitor
/macos:tile Slack --gap 0                # edge to edge, no gutters
/macos:tile Slack --gap 1% --margin 4%   # 1 % between windows, 4 % at the monitor edges
/macos:tile Slack --gap 24               # fixed 24 px everywhere
/macos:tile Terminal --front 2 --region left      # the two frontmost Terminal windows, left half of the monitor
/macos:tile Code --match docs --region top-right  # the VS Code window whose title contains "docs", top-right corner
```

`<App Name>` matches the app's name, bundle id, or `.app` file name, case-insensitively — `Code`, `vscode`, and `Visual Studio Code` all find VS Code. When the name is ambiguous the skill lists the candidates instead of guessing.

`--gap` is the gutter between windows and at the monitor edges: a percentage of the monitor's shorter side (`2.5%`, the default) or pixels (`36`). `--margin` sets the outer gutter separately when it should differ. The plan line shows the resolved pixels, e.g. `gap 36 (2.5%)`. To change the defaults for every run, set `TILE_GAP` and/or `TILE_MARGIN` to either form — for the skill, in Claude Code's `settings.json` `env` block, since the pre-execution shell does not read your shell profile:

```json
{ "env": { "TILE_GAP": "3%" } }
```

`--region` tiles into part of the monitor instead of all of it: `left`, `right`, `top`, `bottom`, the four corners (`top-left` …), `left-third` / `middle-third` / `right-third`, `left-two-thirds` / `right-two-thirds`, or `x,y,w,h` in percent of the usable area. `--front N` keeps only the N frontmost windows and leaves the others where they are; `--match TEXT` keeps only windows whose title contains TEXT. Gutters stay relative to the whole monitor, so a half-region layout lines up with a full one.

The column count is chosen from the window count and the shape of the area being tiled, so two windows on an ultrawide become two tall columns and eight become a 4×2 grid. `--cols` overrides it. The target monitor defaults to the one under the app's front window; `--screen N` uses the index from `--list`.

Every window line in the output shows the window's current rect and its target rect. After an apply, each line ends with `✓` (`✓ snapped to …` when an app that sizes windows in character cells, such as Terminal, landed a few pixels short), or with `✗` and the rect the app actually settled on when it refused the exact size (apps with a minimum or maximum window size do this).

## `/macos:arrange` — plain language in, tile commands out

```
/macos:arrange Chrome on the right monitor in three columns with wide gutters
/macos:arrange spread my VS Code windows out, no gaps
/macos:arrange two Terminal windows in the left half of my monitor
/macos:arrange the VS Code window with the docs in the top-right corner of the right monitor
/macos:arrange Terminal side by side on the OLED, then Slack stacked on the other one — go
```

`arrange` captures the live inventory (`tile --list`: monitors with left/right hints, running apps with window counts and which monitor they are on; `tile --layouts`: your saved layouts), translates the request into exact `/macos:tile` commands, prints them so you can copy them, dry-runs each one and shows the plan, then asks before applying. When a phrase has two reasonable readings (a "quadrant" on an ultrawide, "on the left" with two monitors) it prints both commands as A and B with their dry runs and asks which. Say "go", "apply" or "do it" in the request to skip the question. Because it has a description, Claude also reaches for it on its own when you describe a layout in conversation; `/macos:tile` stays a typed command only.

### Saved layouts

Any tile command can be saved by name and run again later, and a layout can have several steps:

```
/macos:tile Terminal --front 2 --cols 1 --region 0,0,25,100 --save dev    # save (and run) step 1
/macos:tile Code --region right-two-thirds --add dev                      # append step 2
/macos:tile --run dev                                                      # run both, in order
/macos:tile --run dev --dry-run                                            # preview both
/macos:tile --layouts                                                      # list; --forget dev deletes
```

Layouts live in `~/.config/macos-tile/layouts.json` (override with `TILE_LAYOUTS`) as `{"dev": {"steps": ["Terminal --front 2 …", "Code --region …"]}}` — plain text, edit freely. `arrange` sees the list too, so "run my dev layout" and "save this as dev" work in plain language.

### Permissions

The dry run needs no permissions. Applying needs **Accessibility** for the app that launched Claude Code — macOS attributes the script to that app, not to `osascript`:

    System Settings → Privacy & Security → Accessibility → enable Terminal / iTerm2 / Ghostty / Visual Studio Code / Claude

The skill detects which one it is running under and names it in the message. The first apply also raises a one-time Automation prompt ("… wants access to control System Events"); allow it.

Without the permission, an apply exits with code 2 and the instructions above; nothing is moved.

### How it works

`skills/tile/tile.js` is a JavaScript for Automation script with no dependencies beyond macOS.

- Monitor geometry comes from `NSScreen` (`visibleFrame`), converted once from Cocoa's bottom-left origin to the top-left origin that Accessibility uses.
- Running apps come from `NSWorkspace`; regular (Dock-visible) apps only.
- The dry run lists windows through `CGWindowListCopyWindowInfo`, which needs no permission. Once Accessibility is granted, both modes list through System Events so the plan and the apply see exactly the same windows in the same order.
- Each window is set size → position → size, which survives the edge clamping some apps do when a window would otherwise leave the screen.

The script runs before the model sees anything (dynamic context in `SKILL.md`), so the model only relays the result. It is marked `disable-model-invocation`; only a typed `/macos:tile` runs it.

The script also works on its own: `skills/tile/tile.js Terminal --dry-run`. Exit codes: `0` ok, `1` usage or app error, `2` permission needed.

### Limits

- macOS only; tested on macOS 26.
- Windows in native full-screen live in their own Space and are not touched.
- Some Electron apps ignore Accessibility resizing entirely; the output shows where they settled.
- CGWindowList (the pre-permission dry run) can include a helper window that Accessibility later filters out, so the pre-permission plan is approximate.

## Installation

```bash
claude plugin marketplace add gener8v/gener8v.claude-skills
claude plugin install macos@gener8v-claude-skills
```

For development, load the checkout directly:

```bash
claude --plugin-dir /path/to/gener8v.claude-skills/plugins/macos
```
