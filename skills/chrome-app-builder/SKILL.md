---
name: chrome-app-builder
description: Install, update, launch, and troubleshoot websites as dedicated Google Chrome apps on Gabriel's Linux workstation. Use when Gabriel asks to install a website as a Chrome app, web app, standalone app, or dedicated browser window, or when such an app has launch, profile, icon, DRM, or audio-routing problems.
tags: [chrome, web-app, desktop, linux, pipewire]
---

# Chrome App Builder

Build site-specific Chrome apps that behave like native desktop applications while remaining simple, inspectable `.desktop` launchers.

## Local convention

Use the existing workstation pattern unless the request explicitly requires Chrome's managed PWA installation:

- Chrome executable: `/usr/bin/google-chrome-stable`
- Launcher: `~/.local/share/applications/<slug>.desktop`
- Icon: `~/.local/share/icons/hicolor/scalable/apps/<slug>.svg`
- Dedicated profile: `~/.local/share/<slug>/profile`
- Window mode: `--app=<canonical-web-app-url>`
- Stable X11 identity: `--ozone-platform=x11 --class=<slug>`

A dedicated profile gives the app stable process/window identity and isolates its cookies, logins, extensions, permissions, and cache. It also means the user may need to sign in again. Do not silently reuse or modify Chrome's default profile.

## Installation procedure

1. **Inspect before creating.** Detect the Chrome executable and read two existing web-app launchers under `~/.local/share/applications/`. Reuse their naming, `Exec`, categories, and `StartupWMClass` conventions.
2. **Resolve the real app URL.** Prefer the service's official web-player or application URL, not a marketing page. Account for redirects, authentication, and regional endpoints.
3. **Choose a stable slug.** Lowercase ASCII with hyphens, such as `tidal-web`. Use the same slug for launcher filename, profile directory, icon name, `--class`, and `StartupWMClass`.
4. **Create the profile directory.** Create only `~/.local/share/<slug>/profile`; never remove or replace an existing profile without explicit authorization.
5. **Create the icon.** Prefer an official site-provided SVG or a simple brand-faithful SVG. Store it as `~/.local/share/icons/hicolor/scalable/apps/<slug>.svg` and reference it by basename (`Icon=<slug>`).
6. **Create and register the launcher.** Write the `.desktop` file, run `desktop-file-validate`, and refresh `~/.local/share/applications` with `update-desktop-database` when available.
7. **Launch the real app.** Use `gio launch ~/.local/share/applications/<slug>.desktop`.
8. **Verify behavior.** Confirm the exact Chrome parent process contains the expected `--class`, `--user-data-dir`, and `--app` arguments. Exercise the site's primary behavior in the dedicated window.

## Launcher template

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=<Display Name>
GenericName=<Generic purpose>
Comment=<Service> in a dedicated app window
Exec=/usr/bin/google-chrome-stable --ozone-platform=x11 --class=<slug> --user-data-dir=/home/gabrielve/.local/share/<slug>/profile --app=<canonical-url>
Icon=<slug>
Terminal=false
StartupNotify=true
StartupWMClass=<slug>
Categories=<appropriate semicolon-terminated categories>;
Keywords=<appropriate semicolon-terminated keywords>;
```

Do not quote the whole `Exec` command. Escape individual arguments only when the desktop-entry specification requires it. Prefer URLs without shell-sensitive characters; `.desktop` `Exec` is not a shell command.

## Audio preflight for media apps

A new dedicated Chrome profile has no remembered PipeWire route. Its first audio stream follows the current system default sink, which may be an HDMI monitor rather than the output Gabriel expects.

Before declaring a music, video, meeting, or voice app complete:

1. Run `wpctl status`.
2. Record the starred default sink and all connected sinks.
3. If several plausible outputs exist, ask Gabriel which output the app should use. Do not guess between HDMI, Bluetooth, and analog devices.
4. If Gabriel wants to change the system default, use the **current runtime sink ID** from `wpctl status`:

```bash
wpctl set-mute <sink-id> 0
wpctl set-volume <sink-id> <volume>
wpctl set-default <sink-id>
```

PipeWire node IDs are volatile across restarts. Never hardcode an ID learned in an earlier session.

5. Pause and resume playback so Chrome creates or reconnects its output stream.
6. Run `wpctl status` again. Verify an active Google Chrome output stream is routed to the chosen sink.
7. Ask Gabriel to confirm audible output; stream state proves routing, not subjective audibility.

### TIDAL incident retained as the diagnostic model

The TIDAL app played and its progress bar moved, but it was silent. The dedicated app inherited `GB205 High Definition Audio Controller Digital Stereo (HDMI)`, while Gabriel wanted the built-in analog output. The fix was to unmute and select `800 Series Chipset Family Audio Context Engine (ACE) Analog Stereo`, then pause/resume playback. Verification showed an active Google Chrome stream routed to `ALC897 Analog` and Gabriel confirmed audible playback.

This symptom pattern is routing-first:

- **Progress moves, no sound:** inspect sink selection, stream mute, sink mute, and volume before DRM or network debugging.
- **Play never starts:** inspect autoplay policy, authentication, player state, and network requests.
- **Playback error appears:** inspect the exact error, Widevine/CDM state, codec support, and account/device limits.

Do not diagnose all silent playback as DRM. In the TIDAL case Widevine was present; the wrong default sink was the actual fault.

## Per-app routing without changing the global default

`wpctl set-default` changes where future system audio streams go. If Gabriel wants only the Chrome app moved while preserving the global default:

1. Start playback so its sink input exists.
2. Use `pactl list short sink-inputs` and identify the matching active Chrome stream from the dedicated profile/window context.
3. Move only that input:

```bash
pactl move-sink-input <input-id> <sink-name-or-id>
```

4. Verify the stream destination with `wpctl status` and confirm audible playback.

Never move every Chrome stream: Gabriel may have unrelated browser, WhatsApp, Discord, or meeting audio active.

## Troubleshooting order

1. Confirm the launcher resolves and validates.
2. Confirm the dedicated parent process arguments.
3. Confirm the service reached its canonical authenticated app page.
4. For media, verify PipeWire sink and active stream routing.
5. Check Chrome site permissions: sound, autoplay, microphone, camera, notifications.
6. Check Widevine only when protected playback fails to start or reports a DRM error.
7. Inspect service/account errors only after local launch and routing are proven.

Do not terminate unrelated Chrome processes. If this app must restart, identify it by both `--class=<slug>` and its dedicated `--user-data-dir` before stopping it.

## Completion evidence

Report:

- Exact launcher, icon, and profile paths.
- Canonical app URL.
- `desktop-file-validate` result.
- Observed dedicated Chrome process arguments.
- Primary app behavior exercised.
- For media apps: selected sink, active stream destination, and Gabriel's audibility confirmation.

An installed launcher alone is not completion. The site's primary behavior must work in the dedicated app window.
