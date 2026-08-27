---
name: arrange
description: Turn a plain-language window request ("Chrome on the right monitor in three columns with wide gutters", "two Terminal windows in the left half of my screen", "the VS Code window with the docs in the top-right corner") into exact /macos:tile commands. Reads the live monitor and app inventory, plans, dry-runs, prints the commands, and applies on confirmation. Use whenever the user describes how they want an app's windows laid out.
argument-hint: <what you want, in plain language>
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/skills/tile/tile.js:*)
---

# Arrange — plain language → `/macos:tile` commands

Request: **$ARGUMENTS**

Live inventory, captured just now:

!`${CLAUDE_PLUGIN_ROOT}/skills/tile/tile.js --relay --list 2>&1`

## The tool you are driving

Run it with the Bash tool **exactly in this form** — absolute path, invoked directly. It is an executable script with its own interpreter line; never prefix it with `node`, `osascript`, `sh` or `cd`, and never use a relative path. Only this exact executable is pre-approved:

```
${CLAUDE_PLUGIN_ROOT}/skills/tile/tile.js "Google Chrome" --screen 2 --cols 3 --gap 4% --dry-run
```

| Option | Meaning |
|---|---|
| `"<App Name>"` | exact name from the inventory, quoted (case-insensitive; bundle id also works) |
| `--screen N` | monitor index from the inventory. Omit to use the monitor under the app's front window |
| `--region R` | only part of that monitor: `left`, `right`, `top`, `bottom`, `top-left`, `top-right`, `bottom-left`, `bottom-right`, `left-third`, `middle-third`, `right-third`, `left-two-thirds`, `right-two-thirds`, or `x,y,w,h` in percent of the usable area (`0,0,50,100`) |
| `--front N` | only the N frontmost windows; the others stay where they are |
| `--match TEXT` | only windows whose title contains TEXT (case-insensitive) |
| `--cols N` | force N columns. Omit for automatic (chosen from window count and the shape of the area) |
| `--gap SIZE` | gutter between windows and at the edges: `2.5%` of the monitor's shorter side (default) or pixels (`36`) |
| `--margin SIZE` | outer gutter only, when it should differ from `--gap` |
| `--dry-run` | print the plan, move nothing |

One invocation tiles one app's chosen windows into one area. Several apps, or the same app into two areas, means several invocations.

## Procedure

1. **Resolve the request against the inventory.** If the request is empty, ask what they want and stop.
   - **App:** the exact inventory name. "VS Code" → `Code`; "Chrome" → `Google Chrome`; "terminal" → `Terminal` unless another terminal app is also running, then ask. If nothing matches, or the app has 0 on-screen windows, say so and stop.
   - **Monitor vs region — the key distinction.** "The left monitor", "the monitor on the left", "the other monitor", a monitor name → `--screen N` from the inventory tags. "The left side / left half of my monitor", "on the left of the screen", "the top right corner", "the bottom half", "the middle third" → `--region`. A bare "on the left" with more than one monitor → the left monitor; with one monitor → `--region left`. Both can combine: "left half of the right monitor" → `--screen 2 --region left`. Nothing mentioned → omit both.
   - **Which windows.** A count smaller than the app's window count ("two windows", "the front two", "two of them") → `--front N`. A window described by content ("the one with the credentials project", "the docs window") → `--match TEXT` with a word that will appear in its title. "All" or no count → no flag. "Smaller" / "bigger" are achieved by the region and the count; there is no explicit size option.
   - **Layout:** "side by side" / "columns" / "next to each other" → `--cols` = the number of windows being tiled. "Stacked" / "rows" / "on top of each other" → `--cols 1`. "Two columns" / "3 across" → that number. "Grid" or nothing → omit `--cols`.
   - **Gutters:** "no gaps" / "edge to edge" / "flush" → `--gap 0`. "Tight" / "small" → `--gap 1%`. "Wide" / "big" / "roomy" → `--gap 4%`. "Huge" → `--gap 6%`. Nothing → omit (default 2.5%). Explicit numbers pass through as given (`24` px, `3%`). A separate edge margin → `--margin`.
   - **Order:** several apps or areas → one command each, in the order the request names them.
2. **Print the plan** — one line per command, exactly as the user would type it, so they can copy it:
   `/macos:tile Terminal --front 2 --region left`
3. **Dry-run every command** with the Bash tool in the exact form above, with `--dry-run` appended. Show each result's `Monitor:` and `Layout:` lines and its window lines. If a dry run reports a problem (no windows, no title match, ambiguous app, cells too small), fix the plan and repeat from step 2. If `--front` picked windows the user did not mean, say which titles it picked — the user can click the wanted windows to bring them to the front, or you can switch to `--match`. Never substitute your own arithmetic for a dry run.
4. **Apply only with consent.** Ask "Apply?" and wait — unless the request itself says to apply ("apply", "do it", "go", "now"), in which case apply immediately. To apply, run each command without `--dry-run`, in order, and report each `Tiled … of …` summary line; mention any line marked ✗ with where the window settled.
5. If the inventory says Accessibility is **not** granted, say so up front: dry runs work, applying will not until it is enabled for the named app in System Settings → Privacy & Security → Accessibility.

Do not run anything other than `tile.js`. Do not guess an app name that is not in the inventory.
