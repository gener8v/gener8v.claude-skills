# gener8v macOS utilities

Desktop utilities for Claude Code on macOS. One skill so far.

## `/macos:tile` — tile one app's windows into an even grid

```
/macos:tile <App Name> [--cols N] [--screen N] [--gap PX] [--dry-run] [--list]
```

Takes every on-screen window of one app and lays them out as equal cells that fill the usable area of one monitor (menu bar and Dock excluded). Windows on other monitors are pulled onto the target monitor. Minimized windows and windows in other Spaces are left alone.

```
/macos:tile --list                       # monitors, and running apps with their window counts
/macos:tile Terminal --dry-run           # print the plan; move nothing
/macos:tile Google Chrome                # apply (multi-word names may be unquoted; "chrome" also matches)
/macos:tile Code --cols 2 --screen 2     # force 2 columns, target the second monitor
/macos:tile Slack --gap 8                # 8 px between cells
```

`<App Name>` matches the app's name, bundle id, or `.app` file name, case-insensitively — `Code`, `vscode`, and `Visual Studio Code` all find VS Code. When the name is ambiguous the skill lists the candidates instead of guessing.

The column count is chosen from the window count and the monitor's shape, so two windows on an ultrawide become two tall columns and eight become a 4×2 grid. `--cols` overrides it. The target monitor defaults to the one under the app's front window; `--screen N` uses the index from `--list`.

Every window line in the output shows the window's current rect and its target rect. After an apply, each line ends with `✓` (`✓ snapped to …` when an app that sizes windows in character cells, such as Terminal, landed a few pixels short), or with `✗` and the rect the app actually settled on when it refused the exact size (apps with a minimum or maximum window size do this).

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
