---
name: tile
description: Tile every on-screen window of one app into an even grid on one monitor (macOS). Runs only when the user types /macos:tile.
argument-hint: <App Name> [--cols N] [--screen N] [--gap PX] [--dry-run] [--list]
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/skills/tile/tile.js:*)
---

The tiling script has already run with the user's arguments. Its output:

!`${CLAUDE_PLUGIN_ROOT}/skills/tile/tile.js --relay $ARGUMENTS 2>&1`

Relay the outcome to the user in one or two lines: which app was tiled onto which monitor in what grid, or why nothing happened. Rules:

- Do not run the script again and do not try any other approach.
- If the output says a permission is required, quote the System Settings path from the output verbatim, then stop. Do not offer to change permissions yourself.
- If the output says DRY RUN, say nothing was moved and that re-running without `--dry-run` applies it.
- A line ending in `✓ snapped to …` is a success (the app sizes windows in character cells); do not call it out.
- If a window line ends with ✗, say the app refused the exact size (or could not be moved) and show where it settled.
- If the output is the usage text, show it and ask for an app name. Suggest `/macos:tile --list` to see candidates.
