---
name: eden
description: Install, configure, mod, launch, optimize, and troubleshoot Nintendo Switch games in the Eden emulator on Gabriel's Linux workstation. Use when Gabriel explicitly names the Eden emulator, asks to install or play a Switch game with Eden, provides an Eden path/log, or asks about Eden mods, shader caches, updates, DLC, networking, or performance. Do not trigger for unrelated uses of the word Eden.
tags: [eden, emulator, switch, gaming, modding, linux]
---

# Eden Emulator Operations

Treat each game as a working, reversible slice: inventory, back up, change one layer, launch the real game, observe, retain or revert.

## Working baseline

These are observed defaults, not timeless assumptions. Verify live state before changing anything.

- Host: CachyOS Linux, x86_64, Niri, NVIDIA RTX 5070, Intel Core Ultra 9 285.
- Standard Eden data: `~/.local/share/eden`.
- Standard Eden config: `~/.config/eden`.
- Per-game settings: `~/.config/eden/custom/<TITLE_ID>.ini`.
- Saves: `~/.local/share/eden/nand/user/save`.
- Emulated SD card: `~/.local/share/eden/sdmc`.
- Shader cache: `~/.local/share/eden/shader/<lowercase-title-id>/`.
- Main gaming output observed as `DP-2`, 3440x1440 at 100 Hz, VRR-capable.
- Secondary portrait output observed as `HDMI-A-1`, not VRR-capable.
- Active network interface observed as `wlan0`; wired `eno1` may exist while disconnected.
- Known working Eden line: 0.2.1. Detect the installed version and current upstream release every time.

Portable installations and custom XDG paths override these defaults. Read `qt-config.ini` storage paths rather than guessing.

## Boundaries

- Use only game, update, DLC, firmware, and key files Gabriel already supplies. Never source ROMs, firmware, title keys, or production keys.
- Never print, transmit, inspect, or duplicate key contents. Presence and file metadata are sufficient.
- Never scan unrelated downloads or personal files. Read only named game directories and required emulator state.
- Preserve saves by default. Any bundled “100% save” option is destructive and must remain disabled unless Gabriel explicitly requests it.
- Close Eden before editing its configuration, saves, SD card, mods, or shader cache.
- Ask before deleting user-created mods, saves, or caches. An installer's “clean” option is not routine maintenance.
- Do not downgrade Eden to fit a shader cache or mod unless Gabriel explicitly accepts the compatibility and rollback cost.

## Source order

Before changing versions, infrastructure, or dependencies, read version-matched primary sources:

1. Eden release and source: `https://git.eden-emu.dev/eden-emu/eden/`
2. Eden handbook and mod guidance: `https://github.com/eden-emulator/mirror/tree/master/docs/user`
3. The mod/framework's upstream repository and exact release notes.
4. Community posts only for symptoms, workarounds, and candidate downloads; verify claims against source or runtime behavior.

Record exact versions, release URLs, and published hashes. Community Discord embeds and old guides are leads, not authority.

## New-game installation workflow

### 1. Inventory without mutation

- Confirm Eden is closed.
- Determine Eden binary/package, version, build type, data root, config root, NAND root, SDMC root, and game directories.
- Identify the base game's title ID and installed version from Eden or its log; do not infer solely from filenames.
- Record supplied base game, update, and DLC files without opening large archives unnecessarily.
- Check storage headroom before installing multi-gigabyte content.

### 2. Make a targeted rollback point

Back up only affected state to a stable path such as `~/Downloads`:

- Existing per-game INI, if present.
- The title-specific save directory when changing saves or updates with migration risk.
- Title-specific `sdmc/atmosphere/contents/<TITLE_ID>` and game framework directory when changing mods.
- Existing shader-cache directory before importing or replacing a cache.

Do not archive keys into the backup. Verify the archive can be listed before proceeding.

### 3. Install in dependency order

1. Confirm compatible keys and firmware are already installed; do not read their contents.
2. Add the base game directory or launch the supplied base file.
3. Install the exact required update and DLC through Eden's supported UI/workflow.
4. Launch unmodded once and verify the title, title ID, and effective game version in `eden_log.txt`.
5. Configure only game-specific settings. Avoid global changes that can regress other games.
6. Add mods only after the vanilla updated game boots.

A directory scan or successful import is not completion. The real game must launch.

## Mod installation decision

First classify the mod:

### Normal RomFS/ExeFS mod

Use Eden's title-specific mod-data location. Keep each mod in its own subdirectory and verify it appears in the game's Add-Ons configuration.

### Framework-managed mod

Frameworks such as Atmosphere, Skyline, or ARCropolis use the emulated SD card, not Eden's ordinary mod folder. Follow the framework's version-matched layout. Typical roots:

- `sdmc/atmosphere/contents/<TITLE_ID>`
- `sdmc/ultimate/mods` for ARCropolis-based Smash mods

Do not create a second convention beside an existing framework layout.

### Installer or optimizer

Before running it, inspect:

- Source repository and current release.
- Published digest/signature.
- Exact directories it writes or deletes.
- Whether it fetches mutable manifests or unsigned latest dependencies at runtime.
- Cleanup defaults.
- Save replacement defaults.
- Emulator/version-specific workarounds.

Back up first, disable destructive categories, select only required mods, and verify the resolved dependency versions from logs. Prefer the official installer when it pins a known-compatible framework build; prefer manual installation when the installer is opaque or over-broad.

## Verification contract

After each meaningful layer, launch the actual game and collect evidence:

- Eden window title shows the expected game and update version.
- `~/.local/share/eden/log/eden_log.txt` shows the effective per-game settings and successful patch application.
- No new `Critical` or relevant `Error` appears on the changed path.
- The game reaches an interactive menu or gameplay surface.
- Mods are proven through their runtime UI, generated runtime directories/logs, or directly observable behavior—not merely file presence.
- Performance claims include observed game FPS and frame time, not only CPU/GPU specifications.

Leave the application open only when useful to Gabriel. Do not move, close, or reassign unrelated windows during testing.

## Performance diagnosis

Classify the symptom before changing settings.

### One-time hitches that improve on repetition: shader compilation

Evidence:

- `CreateGraphicsPipeline` entries appear as new scenes, fighters, effects, or stages load.
- The next run loads a larger `Total Pipeline Count`.
- FPS is otherwise at target.

Actions:

- Keep disk shader cache and Vulkan driver pipeline cache enabled.
- Do not delete `vulkan.bin` or `vulkan_pipelines.bin`.
- Let the cache warm naturally or use CPU-versus-CPU matches with varied characters, stages, player counts, hazards, and effects.
- Some games, including Smash, use different shaders for low and high player counts; exercise both.
- Treat a first-use-per-session particle hitch as a possible emulator bug even when the disk cache is warm.

### Stable FPS but visually uneven motion: presentation/frame pacing

Compare game FPS with output refresh. A 60 FPS game on a fixed 100 Hz output cannot present at an even cadence without VRR.

- Prefer Eden `Fifo` VSync for stable presentation unless a game's upstream guidance requires otherwise.
- On Niri, use on-demand VRR only after confirming the output reports VRR support:

```kdl
output "<OUTPUT>" {
    variable-refresh-rate on-demand=true
}

window-rule {
    match app-id=r#"^dev\.eden_emu\.eden$"#
    open-on-output "<OUTPUT>"
    variable-refresh-rate true
}
```

Reuse existing Niri conventions. Validate with `niri validate`, then confirm live `vrr_enabled` through `niri msg --json outputs`. Never assume `DP-2` is still the correct connector.

### Sustained low FPS

Check, in order:

1. Speed limit is 100%, not slow mode.
2. The intended discrete GPU and Vulkan backend are active.
3. Resolution scale and antialiasing are reasonable.
4. Multicore CPU emulation is enabled.
5. No mod render profile or FPS-unlock mode is creating unstable timing.
6. Thermal/power state is not limiting the host.
7. Eden's recommended PGO build is in use when compatible.

Do not attribute sustained low FPS to shader compilation without pipeline evidence.

### Network-related stalls or log floods

Compare Eden's configured interface with the live active interface. A disconnected or unavailable interface can produce repeated socket errors. Change only the interface name, relaunch, and verify the effective setting in the log.

## Shader-cache compatibility

Eden stores two distinct files:

- `vulkan.bin`: Eden's serialized transferable pipeline descriptions.
- `vulkan_pipelines.bin`: Vulkan driver pipeline data, sensitive to GPU, driver, emulator build, and cache version.

Before importing any community cache:

1. Require the exact game title ID and update compatibility.
2. Require the exact Eden release/build or verify the source `CACHE_VERSION` for both builds.
3. Prefer importing only a verified compatible `vulkan.bin`; treat another machine's `vulkan_pipelines.bin` as non-portable unless GPU, driver, OS, and build closely match.
4. Back up both current files.
5. Never concatenate cache files or overwrite a larger known-good cache without a tested rollback.
6. Launch and verify Eden accepts the cache rather than deleting it as stale or invalid.

A high shader count does not override a cache-version mismatch. Do not trade a working current cache for an older “complete” cache.

## Current SSBU profile

Use this only for Super Smash Bros. Ultimate; do not project it onto other games.

- Title ID: `01006A800016E000`.
- Working game update: 13.0.4.
- Framework: Skyline + ARCropolis under `sdmc`, not Eden's normal mod directory.
- Installed enhancement set: SSBU Online Deluxe with dependencies, CSS Preserve, and Eternal Heart.
- Training Modpack, One Slot Effects, HDR, destructive cleanup, and bundled 100% save were intentionally not selected.
- Required Eden workaround: per-game RNG seed enabled with value `0`.
- Stable presentation baseline: Vulkan, 1x resolution, 100% speed, 4 GiB emulated memory, FIFO VSync, Niri on-demand VRR on the capable gaming output.
- Shader cache directory: `~/.local/share/eden/shader/01006a800016e000`.
- The public 10,519-shader Eden cache targets 0.1.1 cache format 16 and is incompatible with Eden 0.2.1 cache format 17.

Do not rerun the SSBU optimizer merely to update one component. Inspect current upstream compatibility, back up the existing stack, and update the narrowest required layer.

## Final report

State:

- Exact game title ID and effective version.
- Eden version/build.
- Created or modified paths.
- Backup path and rollback boundary.
- Installed update/DLC/mod versions.
- Launch behavior and direct mod evidence.
- Observed FPS/frame time and whether shader compilation was active.
- Any remaining first-run, per-session, online, or compatibility risk.

Separate observed facts from inference. Never call a setup complete because files merely exist.
