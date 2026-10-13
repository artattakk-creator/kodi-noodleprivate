# GS Media Kodi Repository

Public Kodi repository for GS Media's own add-ons, plugins, scripts and services.

**Repository add-on ID:** `repository.gsmedia`  
**Repository version:** `1.0.0`  
**GitHub host:** `artattakk-creator/kodi-noodleprivate`

## Installation

1. Download the [GS Media Kodi Repository installer ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/repository.gsmedia-1.0.0.zip).
2. In Kodi: **Add-ons → Install from zip file** and select that ZIP (not the GitHub 'RAW' source viewer).
3. **Install from repository → GS Media Kodi Repository**, then install the desired video add-on.
4. Updates are then managed by Kodi from the repository.

If GitHub Pages is enabled (main/(root)), Kodi's optional HTTPS source is `https://artattakk-creator.github.io/kodi-noodleprivate/`.

## Available add-ons

- `plugin.video.noodleprivate` – video lists, search, playback, named favorites, home screen widgets.

## Maintaining multiple add-ons

Every directory `src/<addon.id>/` containing an `addon.xml` becomes its own Kodi package. The automated builder creates:
- `addons.xml` and `addons.xml.md5`
- `<addon.id>/<addon.id>-<version>.zip`
- a root-level repository-installer ZIP for `repository.*` entries.

Increase an add-on's version number in its `addon.xml` when publishing an update. GitHub Actions then generates and publishes the packages.

## Privacy and security

The repository code and downloadable packages are public. Each user's favorites and history stay on their own Kodi device. External services are independent of GS Media. This repository is not affiliated with Team Kodi.