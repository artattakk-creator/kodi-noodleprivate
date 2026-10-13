# GS Media Kodi Repository

Public Kodi repository for GS Media's own add-ons, plugins, scripts and services.

**Repository add-on ID:** `repository.gsmedia`  
**Repository version:** `1.4.0`  
**GitHub host:** `artattakk-creator/kodi-noodleprivate`

## Installation

1. Download the [GS Media Kodi Repository installer ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/repository.gsmedia-1.4.0.zip).
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
- a root-level repository-installer ZIP for the central `repository.gsmedia`.

Increase an add-on's version number in its `addon.xml` when publishing an update. GitHub Actions then generates and publishes the packages.

## Privacy and security

The repository code and downloadable packages are public. Each user's favorites and history stay on their own Kodi device. External services are independent of GS Media. This repository is not affiliated with Team Kodi.
## Repository-Programme: direkte Kodi-Installation

Der zentral verwaltete Repository-Installer liegt zusätzlich unter [`repository-programme/repository.gsmedia-1.4.0.zip`](repository-programme/repository.gsmedia-1.4.0.zip). Der Build-Prozess spiegelt zukünftige Installer in dieses Verzeichnis. Kodi installiert die ZIP über **Add-ons → Aus ZIP-Datei installieren**. Danach erscheinen die enthaltenen Plugins unter **GS Media Kodi Repository**.

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
