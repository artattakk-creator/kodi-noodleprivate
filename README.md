# GS Media Kodi Repository

Public Kodi repository for GS Media's own add-ons, plugins, scripts and services.

**Repository add-on ID:** `repository.gsmedia`  
**Repository version:** `1.7.0`  
**GitHub host:** `artattakk-creator/kodi-noodleprivate`

## XCMate – Entwicklungsdokumentation und Chat-Übergabe

Die aktuellen Projektdokumente für XCMate sind unter **[docs/XCMate/README.md](docs/XCMate/README.md)** verlinkt. Dort stehen vollständige technische Projektübergabe, gesicherte Entscheidungen, Design-Freeze, Android-Teststatus, Roadmap sowie die geplante Serienfunktion (Gesehen-Status, Wiedergabeposition, optional automatisch nächste Folge). Für einen neuen Chat den **[kopierbaren Übergabeblock](docs/XCMate/NEW_CHAT_COPY_BLOCK_DE.md)** verwenden.

**Wichtig:** Die neue Serienfortschrittsfunktion und die konfigurierbaren Grauton-/Akzent-Themes sind am 14.10.2026 spezifiziert, nicht bereits veröffentlicht. Die Android-Gerätefehler beim Startsender und der Vollbild-Fernbedienung bleiben bis zum praktischen Gegenbeweis offen.

**Aktuelle XCMate-Entwicklung:** [0.1.25-Testkandidat, EPG und Android-Testplan](docs/XCMate/IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md): erstes OK Senderinfo, zweites OK/Runter Bedienung, schnelle lokale Senderliste und echte EPG-/Quellenvorschau. 237 lokale Tests bestanden. **Kein Merge/Produktiv-Release, Android-Abnahme offen; produktiv bleibt 0.1.24.**

## Installation

1. Download the [GS Media Kodi Repository installer ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/repository.gsmedia-1.7.0.zip).
2. In Kodi: **Add-ons → Install from zip file** and select that ZIP (not the GitHub 'RAW' source viewer).
3. **Install from repository → GS Media Kodi Repository**, then install the desired video add-on.
4. Updates are then managed by Kodi from the repository.

If GitHub Pages is enabled (main/(root)), Kodi's optional HTTPS source is `https://artattakk-creator.github.io/kodi-noodleprivate/`.

## Available add-ons

- `plugin.video.noodleprivate` – video lists, search, playback, named favorites, home screen widgets.
- `plugin.video.xtreammate` – XCMate 0.1.2, setup wizard, persistent Xtream groups, reversible fullscreen TV remote mapping, startup channel and group, and up/down channel zapping.

## Maintaining multiple add-ons

Every directory `src/<addon.id>/` containing an `addon.xml` becomes its own Kodi package. The automated builder creates:
- `addons.xml` and `addons.xml.md5`
- `<addon.id>/<addon.id>-<version>.zip`
- a root-level repository-installer ZIP for the central `repository.gsmedia`.

Increase an add-on's version number in its `addon.xml` when publishing an update. GitHub Actions then generates and publishes the packages.

## Privacy and security

The repository code and downloadable packages are public. Each user's favorites and history stay on their own Kodi device. External services are independent of GS Media. This repository is not affiliated with Team Kodi.
## Repository-Programme: direkte Kodi-Installation

Der zentral verwaltete Repository-Installer liegt zusätzlich unter [`repository-programme/repository.gsmedia-1.7.0.zip`](repository-programme/repository.gsmedia-1.7.0.zip). Der Build-Prozess spiegelt zukünftige Installer in dieses Verzeichnis. Kodi installiert die ZIP über **Add-ons → Aus ZIP-Datei installieren**. Danach erscheinen die enthaltenen Plugins unter **GS Media Kodi Repository**.

## External provider catalogs (GS Media Repository 1.1.0)

In addition to its own add-ons, GS Media Kodi Repository exposes upstream indexes maintained by [Cumination / Dobbelina](https://github.com/dobbelina/repository.dobbelina) and [Gujal00 / SMR](https://github.com/Gujal00/smrzips). Kodi downloads their packages directly from the original projects. This does not bundle their code inside Noodle Private. The upstream authors control compatibility and updates, and individual video sites may be unavailable. Cumination's own code is distributed under GPL. All private favorites and settings remain on the Kodi device.

## Noodle Private v0.3.0 – selected Cumination providers

Noodle Private now supports **NoodleMagazine** directly and six optional
external Kodi sources routed through an already-installed **Cumination** add-on:

- EPorner, xHamster, Pornhub, XNXX, SpankBang and Tnaflix.
- Unified Kodi-directory search with independent per-provider error handling.
- Named cross-provider favorites using the **same** Kodi add-on profile and `state.json`.
- Provider enable/disable toggles in **Filter, Qualität & Anbieter**.
- Each external provider delegates playback to Cumination's original resolver;
  no scraping engine or resolver is copied into this project.

### Direct Titan BINGIE MOD widget paths

```text
plugin://plugin.video.noodleprivate/?action=providers
plugin://plugin.video.noodleprivate/?action=provider_browse&provider=eporner
plugin://plugin.video.noodleprivate/?action=provider_browse&provider=xhamster
plugin://plugin.video.noodleprivate/?action=provider_browse&provider=pornhub
plugin://plugin.video.noodleprivate/?action=provider_browse&provider=xnxx
plugin://plugin.video.noodleprivate/?action=provider_browse&provider=spankbang
plugin://plugin.video.noodleprivate/?action=provider_browse&provider=tnaflix
plugin://plugin.video.noodleprivate/?action=favorites
plugin://plugin.video.noodleprivate/?action=collection_view&collection_id=default
```

Use the in-app **Anbieterübergreifende Suche** for an interactive search, or
`?action=global_search&query=...` for an explicitly requested term.

### Upgrade and limits

Update Noodle Private via the installed GS Media Kodi Repository. Do **not**
uninstall the add-on or delete its userdata, because those contain your private
favorites and preferences. Existing favorites remain as they were.

All providers depend on Kodi's `Files.GetDirectory` JSON-RPC behavior and
upstream site availability; these functions have passed local regression tests,
but not an end-to-end test on your device. Some sources may require updates in
the upstream Cumination add-on. A provider failure is isolated from the other
results and does not overwrite saved favorites.


## Noodle Private v0.4.0 – Dynamischer Cumination-Katalog

- Alle Anbieter, die Cumination auf dem Kodi-Gerät registriert, werden dynamisch über Kodi-JSON-RPC gelesen. Kein Kopieren externer Scraper-Dateien.
- Anbieter-Einzelseiten: native Kategorien und Unterverzeichnisse; eigene Suche, falls vorhanden.
- Anbieterverwaltung (Admin): Aktivieren/deaktivieren, Katalog aktualisieren, Quellenzugriff einzeln prüfen.
- Bisherige sieben Quellen bleiben aktiv; neu entdeckte Anbieter starten deaktiviert.
- Globale Suche: bis zu zwölf aktive Cumination-Quellen gleichzeitig; jeder Ausfall isoliert.
- Bestehende Favoritenlisten, Verlauf und Einstellungen bleiben unverändert in state.json. Der neue Katalog liegt separat in cumination_catalog.json.
- Widgets: plugin://plugin.video.noodleprivate/?action=providers ; ?action=provider_admin ; ?action=provider_browse&provider=eporner ; ?action=favorites
- Quellencheck prueft Kodi-Verzeichnisauflistung, nicht erfolgreiche Video-Wiedergabe.
- Neue Box: Installiere GS Media Repository, Noodle Private und Cumination. Abhaengigkeiten automatisch bestaetigen. SMR Link Tester / Dobbelina Repository sind optional.

## xVAULT upstream catalog (GS Media Repository 1.2.0)

Kodi can install both `plugin.video.xvault` and the optional `repository.xvault` directly from the official maintainer's index at [mojomedia1812/xVAULT](https://github.com/mojomedia1812/xVAULT). Package and index downloads are referenced through the official GitHub-hosted `docs/` directory over HTTPS, rather than the original repository's plain-HTTP custom domain. GS Media does not mirror or modify upstream ZIP archives. xVAULT's official documentation limits maintainer support to installations made from the official xVAULT repository; GS Media cannot guarantee upstream support, runtime availability or compatibility. Installing `repository.xvault` separately is optional if xVAULT was installed through GS Media.

## Single-repository migration (GS Media 1.3.0 / Noodle Private 0.4.2)

The duplicate `repository.noodleprivate` was retired. The repository's own
`addons.xml` now contains exactly one repository add-on: `repository.gsmedia`.
GS Media indexes and delivers `plugin.video.noodleprivate`; Cumination, SMR and
xVAULT remain separate upstream package catalogs accessed from the **single
installed GS Media repository**. Upstream repository installer entries are
optional and do not need to be installed.

For Kodi devices that previously installed Noodle Private from
`repository.noodleprivate`: update GS Media to 1.3.0 (install the ZIP manually
if Kodi caches old metadata), use **Noodle Private → Information → Versions** to
select the **GS Media Kodi Repository** build 0.4.2, and finally **uninstall
only the old repository.noodleprivate add-on** under Add-on repositories.
Do not uninstall Noodle Private itself or delete userdata. New installations
should install GS Media 1.3.0, then Noodle Private 0.4.2 directly from it.

## Titan BINGIE MOD added in GS Media 1.4.0

The central GS Media repository indexes the original AchillesPunks Titan BINGIE MOD skin and all its upstream dependency add-ons over HTTPS. Kodi 20 (Nexus) uses the upstream `nexus` index; Kodi 21 (Omega) and later use the upstream `omega` index. The Omega skin index currently advertises skin 2.2.3, Nexus 2.1.1. Compatibility with future versions is not guaranteed. No separate BINGIE MOD repository installation is required. BINGIE MOD itself can be installed via `Install from repository > GS Media Kodi Repository > Look and feel > Skins`.

The upstream `omega/addons.xml.md5` currently contains the empty-file MD5, so it would not change on a skin-catalog update. GS Media uses the original `omega/addons.xml` as its Kodi checksum/change-marker body, which Kodi's documentation explicitly permits. No third-party binaries are mirrored or modified.

Kodi's built-in official repository remains installed; optional upstream repository add-ons may appear in the catalog but need not be installed.

## EZ Maintenance+ (GS Media Repository 1.5.0)

Added the official [peno64 repository](https://github.com/peno64/repository.peno64)
as a seventh upstream source via HTTPS `repo/zips/addons.xml`. The catalog
includes `script.ezmaintenanceplus` version `2026.04.05.0` at integration time.
Install from **GS Media Kodi Repository -> Program add-ons -> EZ Maintenance+**.
The add-on requires `script.module.requests >= 1.0.0`, which Kodi can install
from normal dependency sources. No additional peno64 repository installer is
required. Kodi userdata backups are device-local; this repository integration
neither imports nor restores backups. Restoring a full backup can overwrite
current skin settings and other Kodi configuration, so back up the destination
box first. Third-party packages remain maintained and hosted by their owners.

The requested 'TV Mate by Mr. Evil' was not added: no identifiable verifiable
Kodi upstream repository for that precise name/author combination was found.
A source URL or the exact Kodi add-on ID is required before adding it safely.

## mr-evil1 Kodi Media catalog (GS Media 1.6.0)

The entire independently maintained [Kodi Media repository](https://github.com/mr-evil1/kodi-media-repo) is included as a **live upstream index**, alongside Cumination, SMR, xVAULT, Titan BINGIE MOD and peno64. The `<dir>` configuration reads upstream `main/addons.xml`, `addons.xml.md5`, and the original ZIP directories directly over HTTPS. All future and updated upstream packages become available automatically whenever Kodi refreshes the catalog; there is no need to rebuild the GS Media ZIP for each upstream change. GS Media does not mirror, bundle, audit or guarantee those third-party packages. Kodi controls when refreshes occur and can cache the index; updates are not instantaneous.

The requested **TiViMate Kodi** is `plugin.video.iptvmaster` version `2026.06.12.1` at integration, and requires `repository.kodi.media >= 1.0.0` **as a mandatory dependency in the upstream XML**. Consequently, while only GS Media needs to be *manually* installed, Kodi can also automatically install the original mr-evil1 repository for TiViMate. We cannot guarantee a single installed repository without upstream maintainer changes. We deliberately leave the original program and dependency metadata untouched to preserve automatic upstream updates.

All third-party Kodi Media add-ons, including other IPTV and video packages, become selectable under GS Media (category determined by the upstream add-on). Only install addons you trust and use legally authorized streams. The upstream catalog contains multiple versions of some add-on IDs and overlaps existing resolver/dependency IDs; Kodi is responsible for resolving compatibility and origins. Direct external updates carry normal third-party supply-chain risks.

## XCMate 0.1.3 (GS Media 1.7.0)

Independent GPL-2.0 modified derivative of mr-evil1 TiViMate Kodi 2026.06.12.1. Package ID `plugin.video.xtreammate`. The existing original TiViMate is neither modified nor overwritten; all Kodi user data are kept in a separate add-on profile. Reproducible source patch is in `.release/xtreammate_0.1.0.patch.xz.b64`; script `tools/bootstrap_xtreammate.py` verifies the original upstream ZIP SHA256 and reconstructs the GPL source at first build. Full modified Python sources are committed by GitHub Actions.

First-run IPTV installation supports Xtream Codes, M3U files/links, and Stalker. Scan TV, movies and series separately, name lists, select multiple Xtream category IDs and import available EPG. During Xtream live playback from XCMate channel lists, the add-on service uses a transparent Kodi WindowDialog: Back/Left opens channels, a second Back/Left opens groups, Up/Down selects, OK tunes/selects, context/menu toggles category enablement, Right returns to channels. TV remote action maps and Kodi skin behavior require device testing. Streams launched from an external favorite without portal/session metadata may not trigger the overlay.

The original GPL-2.0 attribution and license are preserved. Account credentials remain in the local Kodi profile (plaintext) and are only sent to the IPTV provider; GS Media does not receive them. Restrict Kodi backups to trusted storage. This is a first on-device-test alpha, not a claim to clone the Android TiViMate app.

## XCMate 0.1.2 – TV-Fernbedienung und Startkanal

This version implements optional, reversible Kodi FullscreenVideo key mapping (left, up, down, OK and long OK when supported), a two-stage live channel/group sidebar, and basic pause/seek/stop and secondary audio/video/EPG/settings controls. Left opens channels; left again opens groups. Up/down in hidden-overlay mode zaps to the adjacent channel within the active enabled Xtream category (wrapping at ends). When a list is visible, up/down navigate instead. **Enable the device-specific mapping manually under XCMate → TV-Fernbedienung aktivieren**, then restart Kodi if mappings do not take effect. Kodi device/skin compatibility must be verified on the target device; no device-level test is claimed.

An Xtream portal can store a startup group and startup station, with optional autoplay on opening XtreamMate. No existing portal or playlist data is overwritten. The service refreshes EPG asynchronously so remote commands are not stalled by an EPG import. The independent upstream TiViMate add-on remains untouched. Auto-updates use the existing GS Media Kodi Repository version 1.7.0; an additional repository installer is not required.


## XCMate 0.1.3 catalog acceleration
Live group overlays now rely on a locally stored catalog, while a Kodi background worker refreshes Xtream Live, VOD and Series indexes. Individual category views filter the cached full catalog instead of issuing new per-category requests. A first import still needs the provider server; no local media is downloaded. Old portal settings remain untouched.

 
## XCMate 0.1.7 EPG source management
XCMate now supports multiple user-defined XMLTV URL and file sources,
live enable/disable and ordering, manual Xtream stream-ID to XMLTV channel-ID
mapping, and asynchronous EPG refresh. Use the portal home "EPG verwalten"
entry or the EPG action in Kodi add-on settings. Native Xtream XMLTV remains
the baseline, while custom sources can override matching IDs. Android uses
Kodi's platform file picker and Kodi VFS permissions.


## XCMate 0.1.8 – direct start and Android native TV remote
Startsender direct xbmc.Player playback, RunPlugin autoplay, focused TV overlay and learnable Kodi remote action IDs. Existing portal, EPG and sender group data are untouched. On-device validation of remote model still required.


## XCMate 0.1.9 – Umbenennung ohne Neuinstallation
Kodi zeigt das Add-on nun als **XCMate** an. Die bestehende interne ID `plugin.video.xtreammate` bleibt für automatische Updates und die bestehenden Profile erhalten. Keine Deinstallation erforderlich.
