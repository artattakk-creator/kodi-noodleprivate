# GS Media Setup 0.1.0 – read-only Kodi wizard scaffold

**Status:** early preview / Draft PR / no installation or cleanup operations.

Open from Kodi **Add-ons > Program add-ons > GS Media Setup (Vorschau)**.
The entry point `default.py` shows profile selection, checks available
installed-add-on versions via Kodi's read-only `xbmcaddon.Addon(id)` metadata
and displays the historically known dependency chain in a text viewer.

## Profiles
- **Basis**: XCMate + Titan BINGIE MOD. Includes direct BINGIE imports and
  partial transitive imports read from archived 2026-10-21 manifests.
- **Medien**: Basis plus xVAULT and Cumination.
- **Musik**: Basis plus MP3 Streams Echoed and SHOUTcast.
- **Kombiniert**: Basis, Medien and Musik.

SlyGuy Common is intentionally **not** a mandatory BINGIE dependency;
further verification of its owning consumer add-ons and upstream repository is
required before adding an optional SlyGuy profile.

Manifest minima are historic lower bounds, **not** current Kodi-compatible
recommendations or live downloadable-package versions. Missing and disabled
add-ons cannot always be distinguished using `xbmcaddon.Addon(id)`; the
wizard labels these cases as unqueryable, not proven missing. For manifests
not yet analyzed, the UI explicitly notes incomplete dependency coverage.

## Strict safety boundary
- Does not call InstallAddon / UninstallAddon, modify addon states, profiles,
  keymaps, skin or databases.
- No auto-start service, network access, token input, deletion or backup restore.
- Does not install the repository, upgrade XCMate or make the box work offline.
- Adds no dependency on SlyGuy or music/video third-party add-ons in its
  own manifest; `xbmc.python >= 3.0.0` only.
- Shows no secrets in diagnostics or UI. No user Kodi profile is bundled.

## Technical follow-up for Codex
1. Take current main as baseline; preserve XCMate .66 and its functioning
   BINGIE EPG textual Now/Next. Image enrichment remains in Issue #300.
2. Before production installer work, build the **complete** recursive dependency
   graph from pinned, verifiable original Kodi manifests / sources, including
   resolution of optional vs mandatory requirements, addon enabled state and
   Kodi 21.2/21.3 platform constraints. Never assume the 109 historical
   folders are all needed.
3. Add a safe **dry-run plan** (repo URL, upstream identity, chosen version,
   dependency reasons, SHA256 when available, blocker states) and tests.
4. Then, in a **new reviewed phase**, add per-addon consented installation
   using supported Kodi APIs; wait for actual installed/updated state and handle
   incomplete downloads/rollback safely. Explicit user interaction required.
5. Only after direct user consent should any optional old addon be disabled
   or removed. Never delete Kodi user data or restore backups silently.
6. Production repository 1.8 Lite remains a separate effort in Draft PR #303,
   currently blocked by failed MP3 source HTTP 404 on CI. No merge while red.
7. Test a clean Kodi 21.3 ARM32 device plus existing-box upgrade path,
   including cold start, skinhelper/TMDbHelper dependency compatibility.
8. Provide exact final commits, CI test results, installable wizard ZIP/SHA,
   Android test status and explicit READY_TO_MERGE/BLOCKED.

## Source inventory (not a fresh installed-device scan)
Google Drive master backup `XCMate_backup_202610211443`, 109 addon directories.
Key manifest examples:
- `skin.titan.bingie.mod` 2.2.3 declares 13 direct imports;
- `plugin.video.themoviedb.helper` 5.4.16 declares seven imports;
- `script.bingie.helper` 1.1.2 declares two imports;
- `script.skinshortcuts` 2.1.0 declares three imports;
- `script.module.slyguy` 0.87.2 depends on `slyguy.dependencies`
  and `repository.slyguy` (not BINGIE direct requirements).

No secret-bearing files or Kodi profile contents were copied to GitHub.
Detailed product requirements are tracked in Issue #305.
