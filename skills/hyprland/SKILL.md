---
name: hyprland
description: Safely change Hyprland configuration only when the user explicitly names Hyprland, Hyprlock, Hypridle, Hyprpaper, or a Hyprland-managed path. Niri is this workstation's primary compositor; never infer Hyprland from a generic window-manager, display, or monitor request.
tags: [hyprland, desktop, configuration]
---

# Hyprland Change Control

Hyprland configuration is live desktop infrastructure. Preserve a known-good state before touching it.

## Required pre-change checkpoint

Before **any** change to a Hyprland-managed file:

1. Identify the configuration root. Default: `$XDG_CONFIG_HOME/hypr` or `~/.config/hypr`.
2. Require that root to be its own Git work tree. If it is not one, initialize Git **in that root only**; never initialize a repository from `$HOME` just to manage Hyprland.
3. Stage only Hyprland-managed paths. Inspect the staged diff and ensure it contains no unrelated files or secrets.
4. Create a baseline commit before editing, with a descriptive message such as `chore(hyprland): checkpoint before <change>`.
5. Record the baseline commit SHA in the change report. Do not edit if the checkpoint cannot be created.

A post-change commit is also required after verification. The pre-change commit is the rollback point; restore with `git revert <post-change-sha>` rather than manually reconstructing a failed configuration.

## Change procedure

1. Determine the installed Hyprland version and the active config entrypoint. Do not assume classic `hyprland.conf` syntax: this system may use native Lua (`hyprland.lua`).
2. Read the exact files and existing binding/rule conventions before editing. Reuse the existing style and APIs.
3. Make the smallest change that implements the requested rule. Do not change unrelated bindings, workspace rules, or running windows while diagnosing.
4. Reload only after the edit: `hyprctl reload`.
5. Check `hyprctl configerrors`. For bindings, inspect `hyprctl binds -j`; for workspace/window placement, inspect the relevant live `hyprctl ... -j` state.
6. Exercise the changed behavior only when its desktop side effect is understood and acceptable. Report the precise command and observed result.
7. Commit the verified change with an imperative, descriptive message.

## Failure and rollback

- If reload reports an error, immediately restore the pre-change configuration with Git and reload it. Do not layer fixes on a broken configuration.
- If a binding or window-placement change causes an input/navigation regression, revert the post-change commit first. Diagnose from the known-good baseline in a separate, checkpointed change.
- Never use `hyprctl dispatch` syntax from generic online examples until it is verified against the installed version; use the active configuration API and local stubs/docs.
- Never remove, close, move, or reassign a user window as part of a config test unless the request explicitly authorizes that side effect.

## Evidence required in the final report

State: baseline SHA, changed files, reload result, `configerrors` result, and the exact live-state check performed. State any unexercised desktop behavior as unverified.
