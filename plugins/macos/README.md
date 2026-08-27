# gener8v macOS utilities

Desktop utilities for Claude Code on macOS. Two skills: **`/macos:tile`** does the work — it lays an app's windows out in an even grid; **`/macos:arrange`** turns plain language into the right `tile` command, shows you the plan, and applies it when you say so. No third-party window manager needed.

```
/macos:tile Terminal --front 2 --cols 1 --region 0,0,25,100 --save dev
/macos:arrange two terminals stacked in the left quarter of my monitor, save it as dev
/macos:tile --run dev
```

## `/macos:tile`

```
/macos:tile <App Name> [--screen N] [--region R] [--front N] [--match TEXT] [--cols N] [--gap SIZE] [--margin SIZE] [--dry-run]
/macos:tile --list
/macos:tile … --save NAME | … --add NAME | --run NAME | --layouts | --forget NAME
```

By default it takes every on-screen window of one app and lays them out as equal cells that fill the usable area of one monitor (menu bar and Dock excluded), with a gutter between windows and at the edges. `--region` narrows the area, `--front` and `--match` narrow the windows. Windows on other monitors are pulled onto the target; minimized windows and windows in other Spaces are left alone.

| Option | Meaning |
|---|---|
| `<App Name>` | name, bundle id or `.app` file name, case-insensitive — `Code`, `vscode`, `Visual Studio Code` all find VS Code; multi-word names may be unquoted. An ambiguous name lists the candidates instead of guessing |
| `--screen N` | target monitor, by the index `--list` prints. Default: the monitor under the app's front window |
| `--region R` | part of that monitor: `left`, `right`, `top`, `bottom`, the four corners (`top-left` …), `left-third` / `middle-third` / `right-third`, `left-two-thirds` / `right-two-thirds`, or `x,y,w,h` in percent of the usable area (`0,0,25,100` = left quarter). Synonyms normalise ("Left Half", "upper right") |
| `--front N` | only the N frontmost windows; the others stay where they are |
| `--match TEXT` | only windows whose title contains TEXT, case-insensitive |
| `--cols N` | force N columns. Default: chosen from the window count and the shape of the area — two windows on an ultrawide become two tall columns, eight become 4×2 |
| `--gap SIZE` | gutter between windows and at the edges: a percentage of the monitor's shorter side (`2.5%`, the default — 36 px on a 1440-px-tall display) or pixels (`36`). `--gap 0` is edge to edge |
| `--margin SIZE` | outer gutter only, when it should differ from `--gap` |
| `--dry-run` | print the plan, move nothing. Needs no permissions |
| `--list` | monitors (index, name, usable area, `left` / `right` / `main` tags) and running apps with their window counts and which monitor they are on |

```
/macos:tile --list
/macos:tile Terminal --dry-run                     # plan only
/macos:tile Google Chrome                          # every Chrome window, whole monitor, auto grid
/macos:tile Code --cols 2 --screen 2               # two columns on the second monitor
/macos:tile Terminal --front 2 --region left       # the two frontmost Terminal windows, left half
/macos:tile Code --match docs --region top-right   # the VS Code window whose title contains "docs", top-right corner
/macos:tile Slack --gap 0                          # no gutters
/macos:tile Slack --gap 1% --margin 4%             # 1 % between windows, 4 % at the monitor edges
```

Gutters stay relative to the whole monitor, so a half-region layout lines up with a full one. To change the gutter defaults for every run, set `TILE_GAP` and/or `TILE_MARGIN` (either form). For the skill they go in Claude Code's `settings.json` `env` block, because the pre-execution shell does not read your shell profile:

```json
{ "env": { "TILE_GAP": "3%" } }
```

### Output

The plan names the app, the monitor (and region), and the layout — `2 windows (of 3; front 2) → 1 col × 2 row, cell 1210×652, gap 35 (2.5%), margin 35 (2.5%)` — then one line per window with its current rect and its target. After an apply each line ends with `✓`; `✓ snapped to …` when an app that sizes windows in character cells (Terminal) landed a few pixels short; `✗ app settled at …` when the app refused the size (minimum or maximum window sizes); `✗ could not move` when the write failed. A summary closes it: `Tiled 2 of 2 windows.`

### Saved layouts

Any tile command can be saved by name and replayed, and a layout can have several steps:

```
/macos:tile Terminal --front 2 --cols 1 --region 0,0,25,100 --save dev   # save (and run) step 1
/macos:tile Code --region right-two-thirds --add dev                     # append step 2
/macos:tile --run dev                # run every step, in order   (--dry-run previews them all)
/macos:tile --layouts                # list                        (--forget dev deletes one)
```

Layouts live in `~/.config/macos-tile/layouts.json` (override with `TILE_LAYOUTS`) as plain JSON — `{"dev": {"steps": ["Terminal --front 2 --cols 1 --region 0,0,25,100", "Code --region right-two-thirds"]}}` — and can be edited by hand. `--save` records the command as written, minus `--dry-run`.

## `/macos:arrange`

```
/macos:arrange Chrome on the right monitor in three columns with wide gutters
/macos:arrange two Terminal windows in the left half of my monitor
/macos:arrange the VS Code window with the docs in the top-right corner of the right monitor
/macos:arrange Terminal side by side on the OLED, then Slack stacked on the other one — go
/macos:arrange set up my dev layout
/macos:arrange stack the front two terminals on the left, save it as dev
```

`arrange` starts from the live inventory (`tile --list` and `tile --layouts`, captured the moment you run it), resolves the request against it, and:

1. prints the exact `/macos:tile` command(s) — one per app or area — so you can copy them;
2. dry-runs each one and shows the plan;
3. asks **Apply?** — or applies at once when the request says "go", "apply", "do it" or "now".

It knows the difference between *the left monitor* (`--screen`) and *the left side of my monitor* (`--region`); "two windows" becomes `--front 2`, "the one with the docs" becomes `--match docs`; a named layout becomes `--run NAME`, and "save this as X" adds `--save X`. When a phrase has two reasonable readings — a "quadrant" on an ultrawide, "on the left" with two monitors — it prints both commands as **A** and **B** with their dry runs, says which it recommends and why, and asks which to apply rather than choosing silently. When `--front` may have picked the wrong windows it names the titles it chose; click the ones you meant to bring them forward, or give it a title word.

Because `arrange` has a description, Claude also reaches for it when you describe a layout in conversation. `/macos:tile` stays a typed command only.

## Permissions

The dry run needs no permissions. Applying needs **Accessibility** for the app that launched Claude Code — macOS attributes the script to that app, not to `osascript`:

    System Settings → Privacy & Security → Accessibility → enable Terminal / iTerm2 / Ghostty / Visual Studio Code / Claude

The script detects which app it is running under and names it in the message. The first apply also raises a one-time Automation prompt ("… wants access to control System Events"); allow it. Without the permission an apply exits with code 2 and these instructions; nothing is moved.

## How it works

`skills/tile/tile.js` is a JavaScript for Automation script with no dependencies beyond macOS.

- Monitor geometry comes from `NSScreen` (`visibleFrame`), converted once from Cocoa's bottom-left origin to the top-left origin that Accessibility uses.
- Running apps come from `NSWorkspace`; regular (Dock-visible) apps only.
- Windows are listed through System Events, by index — never by title, because a title that changes between the read and the write (Terminal's does, constantly) would make the write fail. Before Accessibility is granted, dry runs list through `CGWindowListCopyWindowInfo` instead, which needs no permission.
- Each window is set size → position → size, which survives the edge clamping some apps do, then read back so the output reports what actually happened.
- The host app is read from `__CFBundleIdentifier` / `TERM_PROGRAM` so permission messages name the right thing.

`/macos:tile` runs the script before the model sees anything (dynamic context in `SKILL.md`); the model only relays the result. `/macos:arrange` gets the inventory the same way, then runs the script through the Bash tool, which is pre-approved for that one executable and nothing else.

The script also works on its own: `skills/tile/tile.js Terminal --dry-run`. Exit codes: `0` ok, `1` usage or app error, `2` permission needed; `--relay` (used by the skills) always exits 0 so the message reaches the model.

## Limits

- macOS only; tested on macOS 26.
- One app per invocation; `arrange` chains several.
- `--front` picks by stacking order. Click the windows you mean to bring them forward, or use `--match`.
- Windows in native full-screen live in their own Space and are not touched.
- Some Electron apps ignore Accessibility resizing entirely; the output shows where they settled.
- Before Accessibility is granted, the dry run's window list (from CGWindowList) can include a helper window that Accessibility later filters out, so that plan is approximate.

## Installation

```bash
claude plugin marketplace add gener8v/gener8v.claude-skills
claude plugin install macos@gener8v-claude-skills
```

Restart Claude Code after installing or updating — skills load at session start. For development, load the checkout directly:

```bash
claude --plugin-dir /path/to/gener8v.claude-skills/plugins/macos
```
