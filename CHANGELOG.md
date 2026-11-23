# Changelog

## 1.0.7 - 2026-11-23

### Fixed
- Mixer scene names, the heartbeat and all other feedback from Mixbus were missing after the plugin had been reloaded, for example by a store update. The old backend kept the OSC port, so the new one could not receive anything. A new backend now stops its predecessor first.
- Calls that arrive before the OSC client exists no longer raise an error; the heartbeat loop registers again shortly afterwards.

## 1.0.6 - 2026-11-23

### Added
- Long press on a **Mixer Scene** key stores the current mixer state in that scene. Mixbus names a new scene with a timestamp. A long press overwrites an existing scene without asking.

### Changed
- A short press on a Mixer Scene key recalls the scene on release, no longer on press.

## 1.0.5 - 2026-11-20

### Added
- **Trigger Clip** action: starts the clip in one slot of the Mixbus/Ardour trigger grid (route and row, counted from 1 as in Mixbus). The key shows whether the slot is empty, stopped or playing.
- **Trigger Control** action: scrolls the visible clip rows up or down and stops all clips.
- **Trigger page**: a "Create" button in the plugin settings builds a page with the trigger grid for the connected deck. All rows hold clips, the last column holds the controls.
- **Mixer Scene** keys show the name of their scene, a small faded mixer icon in the background, and the scene recalled last from the deck is highlighted.
- Reconnects to Mixbus/Ardour after a restart: the heartbeat retries with increasing delays (3 s, 5 s, then 10 s) while Mixbus does not answer, and logs only when the connection is lost or comes back.

### Changed
- The plugin settings (server and client address and port, trigger page) moved from the "Open Config" button on every action to the plugin's page in the app settings (Settings, Plugins).
- Mixer scene numbers now count from 1, as in the Mixbus scene list. A key set to scene *n* now recalls scene *n*; before, it recalled scene *n+1*. Check the keys you configured earlier.
- Inactive icons are brighter again (opacity 0.7), which fits the darker rendering of the current StreamController release.
- The Mute and Solo icons are redrawn in the line style of the Loop icon.
- Icons are rendered once per state and reused.
- The plugin version is taken from `manifest.json` only.
- `/strip/list` is requested once after Mixbus answers with its first heartbeat, not with every registration.
- The mixer scene label is shown at the top in the same style as the other actions.

### Fixed
- Mixbus crashed when the plugin sent `/set_surface` without a server port. The port now defaults to 8000.
- The action list failed to load with current StreamController releases because action holders passed their arguments in the wrong order.
- The strip list could only be loaded once.
- Marker events raised an error when the value was not a string.
- The mixer scene settings raised an error when no scene had been chosen yet.
- The trigger setting was read from the mixer scene setting.
- Registration with Mixbus no longer blocks plugin start and the OSC receive loop for two seconds.
