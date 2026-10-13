# GS Media Kodi Repository

Public Kodi repository for GS Media's own add-ons, plugins, scripts and services.

**Repository add-on ID:** `repository.gsmedia`  
**Repository version:** `1.1.0`  
**GitHub host:** `artattakk-creator/kodi-noodleprivate`

## Installation

1. Download the [GS Media Kodi Repository installer ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/repository.gsmedia-1.1.0.zip).
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
## Repository-Programme: direkte Kodi-Installation

Der zentral verwaltete Repository-Installer liegt zusätzlich unter [`repository-programme/repository.gsmedia-1.1.0.zip`](repository-programme/repository.gsmedia-1.1.0.zip). Der Build-Prozess spiegelt zukünftige Installer in dieses Verzeichnis. Kodi installiert die ZIP über **Add-ons → Aus ZIP-Datei installieren**. Danach erscheinen die enthaltenen Plugins unter **GS Media Kodi Repository**.

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
