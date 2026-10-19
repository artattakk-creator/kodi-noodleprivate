# XCMate – Grafiksystem und Asset-Produktionsplan (Ziel 0.1.27+)

> **VERBINDLICHER DESIGN-FREEZE 19.10.2026:** Nutzer hat aus der Dreifach-Muster-Tafel **ausschließlich Design 1 „SPACE PREMIUM“** gewählt (linkes Muster: galaktisches Tiefblau, Erdkrümmung, starkes verchromtes 3D-X, leuchtend cyanblaue UI). **Die vorherige generische Metallgrau-/Anthrazit-Gestaltung wurde abgelehnt**. Alle Angaben weiter unten zu „Slate/Anthrazit“ sind nun **nur Material-/Kontrast-Optionen innerhalb von Space Premium**, keine eigenständige Designvorgabe. Primäre Freigabe und technische Schnittstelle: [DESIGN_FREEZE_SPACE_PREMIUM_THEME_ARCHITECTURE_DE.md](DESIGN_FREEZE_SPACE_PREMIUM_THEME_ARCHITECTURE_DE.md). Spätere Design 2 „Cinematic“ und 3 „Neon Future“ **nur als mögliche zusätzliche installierbare XCMate-Themes vorbereiten, derzeit nicht produzieren**. Funktionaler Freeze der 0.1.26-Live-TV-Navigation bleibt verbindlich. Vorschau zunächst **ein 512×512-App-Icon plus 1920×1080-Hauptmenübild**, danach die 98 logischen Asset-Slots. Kodi BINGIE MOD bleibt unverändert, die Themes gelten für XCMate selbst.

**Stand:** 19.10.2026 · **Art:** Planung und konkretes Asset-Manifest, **keine** bereits erzeugten neuen Bilder, **kein** veröffentlichter Grafik-Patch.  
**Projekt:** `artattakk-creator/kodi-noodleprivate` · aktuelle produktive Version `0.1.26`.  
**Codex-Integration:** [0.1.27-Hauptauftrag](CODEX_AUFTRAG_027_STARTMENUE_SETTINGS_GRUPPEN_EPG_DE.md), [Medien-UX](CODEX_AUFTRAG_027_FILME_SERIEN_NETFLIX_NAV_DETAIL_DE.md), [FREEZE/Suche/BINGIE MOD](CODEX_AUFTRAG_027_FREEZE_GLOBAL_SEARCH_BINGIE_WIDGETS_DE.md).

## 1. Tatsächliche GitHub-Bestandsaufnahme

GitHub-Git-Tree `main` unter `src/plugin.video.xtreammate/` am 19.10.2026:
- **32 vorhandene Grafikdateien**: `icon.png` (12.122 Byte), `fanart.jpg` (64.532 Byte) und **30** PNGs unter `resources/media/` (37.360 Byte). Summe **114.014 Byte / 111,3 KiB**. Diverse der 30 PNGs sind winzige vorhandene OSD-Texturen und **dürfen nicht wegen eines Designsprints entfernt oder blind ersetzt werden**.
- Weitere Grafiken des Repositories gehören anderen Add-ons (`plugin.video.noodleprivate`, `repository.gsmedia`) oder sind nur Entwurfs-Screenshots in `docs/XCMate/assets/`, zählen **nicht** als aktuelle XCMate-Runtime-Assets.
- **Auffälligkeit:** `src/plugin.video.xtreammate/addon.xml` enthält `<fanart>fanart.png</fanart>`, aber im Add-on-Root liegt `fanart.jpg`, **kein** `fanart.png`. Beim Grafik-Integrations-PR korrigieren und mit CI testen; **nicht** produktive 0.1.26 blind ändern.
- [`ARTWORK_ASSET_MANIFEST_DE.md`](ARTWORK_ASSET_MANIFEST_DE.md) dokumentiert ein **bereits vom Nutzer freigegebenes XCMate-Logo und Space-Motiv** sowie ältere abgeleitete Design-Entwürfe. **Die freigegebenen Original-Rasterquellen fehlen laut diesem Manifest noch im GitHub-Repo**: nicht behaupten, sie seien dort hochgeladen. Beim neuen Grafikset diese Originalreferenzen vom Nutzer/bisherigen lokalen Archiv beziehen und SHA-256/Logoform beibehalten, wenn verfügbar.

## 2. Wie viele Bilder sind sinnvoll? Gibt es eine Höchstzahl?

Es gibt **keine feste allgemeine Kodi-Add-on-Höchstzahl** von etwa 100 Bildern. Grenze ist praktische Performance: komprimierte ZIP-Größe, App-/Kodi-Texturcache, VRAM/RAM, Decode/Upload, Anzahl simultaner Kodi-ControlImages, Android-TV-CPU/GPU und sichtbare UI-Komplexität. Große Poster von Xtream werden **dynamisch** geladen und nicht im Add-on mitgeliefert.

**Design-Soll:** **98 logische Asset-Slots** als vollständiges **XCMate Graphics v2**. Bestehende nutzbare Dateien **zählen mit**, und identische Elemente sollen wiederverwendet statt dupliziert werden. Also **nicht** annehmen, dass 98 komplett neue PNG/JPG-Dateien erzeugt werden müssen. Als Produktionsplanung rund 70–85 neue/überarbeitete Dateien nach Mapping; endgültige Zahl erst nach visueller Inventur und Source-Freeze. **Startpaket:** 35–45 priorisierte Dateien; danach bis zum gesamten 98er-Set. Über 120–150 statische Assets nur mit konkretem Nutzen/Profiling.

| Bereich | Logische Asset-Slots |
|---|---:|
| Branding | 4 |
| Hauptmenü | 12 |
| Einstellungen | 20 |
| Filme und Serien | 14 |
| EPG | 12 |
| Player und Fernbedienung | 16 |
| Suche, Navigation und Shared UI | 16 |
| BINGIE MOD Widgets | 4 |
| **SUMME** | **98** |

**Zielbudget:** ca. **8–15 MB** komprimierte finale Grafikdateien im Add-on (grobe Planungsgröße, keine Kodi-Grenze). Durch gemeinsame Texturen/Gradienten und Wiederverwendung möglichst darunter. **Keine** riesige 4K-Panoramaserie ohne gemessenen Android-Vorteil.

## 3. Kreative Vorgabe und Varianten

**Designbasis:** vom Nutzer zuvor freigegebenes **XCMate-Signet** plus Space-/Cinematic-Motiv; hochwertige **slate-/anthrazitgraue** UI, sanfte Metallic-/Glasverläufe, sparsame kalte blaue Highlights, dezente Raum-/Lichtreflexe. Keine bunten Kinder-UI-Icons. 16:9 Full-HD als Standard. Die einst freigegebene Basis muss bei tatsächlicher Quellverfügbarkeit als Referenz dienen; keine frei erfundene „Original-Logo“-Ersetzung.

**Visuelle Regeln:**
- Die bestehende XCMate-0.1.26-TV-Infobar/OSD samt Icon-Geometrie ist **Freeze**. Neue Artwork-Elemente für zusätzliche Screens dürfen es nicht brechen; alte TV-Texturen/Controls vor dem Integrations-PR nicht überschreiben.
- **Bereichs-Hintergründe:** Home Start/Live/EPG/Movie/Series/Settings je eigene thematische Komposition, Hauptmotiv vorzugsweise rechte Bildhälfte, linke dunkle Negativfläche für Schrift/Kategorien. Bei Setting-Unterseiten zehn **subtile** thematische Hintergrundvarianten (Accounts/EPG/Remote/Recording etc.). Keine unruhige Bildfläche unter Lesetexten.
- **Film- und Serien-Backdrops** vorzugsweise echte Poster-/Fanart-Dateien vom IPTV-Provider, per Fokus dynamisch. Packaged `placeholder-*` nur als neutraler Rückfall, keine Fake-Filmposter oder ungeklärte urheberrechtlich geschützte Filmszenen in der App.
- **Iconstil:** konsistente duotone/outline PNG-Symbole, helle Grundfarbe, Fokus in blaugrauem Akzent. Für Status (Warnung/Fehler) semantisch sichtbare Abweichung. Icons nach Möglichkeit farbneutral als Texture + Kodi-DiffuseColor, sodass spätere Benutzer-Themes leicht bleiben.
- **Screenreader/Lesbarkeit:** ausreichender Kontrast, Textgrößen für Wohnzimmerabstand, Fokusmarkierung ohne kleine Glüheffekte als einziges Signal, genügend TV-Safe Area, keine nackten Emoji/Unicode-Icons (Kodi-Font zeigt sonst Kästchen).
- **Dynamische Theme-Farben:** keine separaten 98 Dateien pro Farbe. Shared PNG/Texturen per Kodi-`colordiffuse`/Konfigurationsfarbe färben, feste Foto-Hintergründe wiederverwenden.

## 4. Maße, Formate und Verpackung

| Asset-Typ | Format | Produktion / Nutzung |
|---|---|---|
| Kodi-Add-on-Icon | `icon.png`, PNG ohne transparente Grundfläche | **512×512** Pixel (256×256 zulässig). Kodi-Add-on-Logo aus freigegebenem Branding. |
| Kodi-Add-on-Fanart | `fanart.jpg` | **1920×1080, 16:9**, komprimiert **<1 MB**; Manifest muss auf tatsächlich vorhandene Datei zeigen. |
| Haupt-/Einstellungs-Hintergründe | `.jpg` | Standard **1920×1080**; während des Anzeigens nur 1–2 große Backdrops simultan geladen halten. |
| PNG-Icons | `.png` mit Alpha | **128×128** UI normal; **256×256** Master für große/fokussierte Darstellungen; nicht unnötig 1024×1024. |
| Poster-Fallback | `.jpg` | **500×750** bzw. 2:3, geringe Dateigröße; echte Filmposter dynamisch nachladen. |
| Overlays, Panel-/Gradient-Texturen | Transparente `.png` | Kleine **9-slice**-fähige Paneltexturen, 256–512 px wo möglich; keine separaten gigantischen Panel-Bilder. |
| BINGIE-MOD-Widget-Fallback | `.png`/`.jpg` | zum Ziel-Aspect Ratio passende Fallbacks, echte Metadaten/Poster/Senderlogos über Kodi-`ListItem.setArt`. |
| Master-Dateien zur Weiterentwicklung | SVG/PSD/Quellprojekt **außerhalb** Add-on ZIP | Separater `artwork/xcmate/`-Quellordner mit Herkunft/Nutzungsrechten; im Runtime-ZIP nur benötigte optimierte PNG/JPG, keine PSD/Fontdateien. |

**Kodi-Referenzen:** [Kodi Add-on structure](https://kodi.wiki/view/Add-on_structure) (Icon, Fanart und Artwork-Manifest), [Kodi Artwork/Cache](https://kodi.wiki/view/Artwork/Cache) (typische Cache-Auflösungen), [Kodi Skin Optimizations](https://kodi.wiki/view/Skin_Optimizations) (kleinste sinnvolle Texturen, kein unnötiges Alpha). Langsame Android-TV-GUI wird **nicht** mit großen PNG-Layern überlagert; Fokus-/Asset-Laden via asynchrone Cachepfade.

## 5. Produktionsmanifest – 98 logische Grafikslots

**Logische Dateinamen** unter `resources/media/graphics_v2/` zur Identifikation, nicht automatisch reale Implementierungspfade. Vorhandene Originale können an ihren bisherigen Pfaden bestehen bleiben; Codex erstellt ein Alias-Mapping, damit TV-Freeze nicht gebrochen wird. `icon.png`/`fanart.jpg` bleiben als tatsächliche Kodi-Metadaten-Assetpfade.

### Branding (4)

`resources/media/graphics_v2/brand/`

- `icon-512.png`
- `wordmark-white.png`
- `splash-1920.jpg`
- `fanart-1920.jpg`

### Hauptmenü (12)

`resources/media/graphics_v2/home/`

- `icon-start.png`
- `icon-live.png`
- `icon-epg.png`
- `icon-movies.png`
- `icon-series.png`
- `icon-settings.png`
- `bg-start.jpg`
- `bg-live.jpg`
- `bg-epg.jpg`
- `bg-movies.jpg`
- `bg-series.jpg`
- `bg-settings.jpg`

### Einstellungen (20)

`resources/media/graphics_v2/settings/`

- `icon-accounts.png`
- `bg-accounts.jpg`
- `icon-start-channel.png`
- `bg-start-channel.jpg`
- `icon-epg.png`
- `bg-epg.jpg`
- `icon-groups.png`
- `bg-groups.jpg`
- `icon-remote.png`
- `bg-remote.jpg`
- `icon-player.png`
- `bg-player.jpg`
- `icon-recordings.png`
- `bg-recordings.jpg`
- `icon-appearance.png`
- `bg-appearance.jpg`
- `icon-maintenance.png`
- `bg-maintenance.jpg`
- `icon-about.png`
- `bg-about.jpg`

### Filme und Serien (14)

`resources/media/graphics_v2/media/`

- `icon-play.png`
- `icon-restart.png`
- `icon-resume.png`
- `icon-favorite-add.png`
- `icon-favorite-remove.png`
- `icon-trailer.png`
- `icon-seasons.png`
- `icon-episodes.png`
- `placeholder-movie-poster.jpg`
- `placeholder-series-poster.jpg`
- `placeholder-movie-backdrop.jpg`
- `placeholder-series-backdrop.jpg`
- `rail-gradient.png`
- `poster-shade.png`

### EPG (12)

`resources/media/graphics_v2/epg/`

- `icon-today.png`
- `icon-day-prev.png`
- `icon-day-next.png`
- `icon-remind.png`
- `icon-auto-switch.png`
- `icon-record.png`
- `icon-channels.png`
- `icon-clock.png`
- `bg-guide.jpg`
- `bg-detail.jpg`
- `no-data.png`
- `source-error.png`

### Player und Fernbedienung (16)

`resources/media/graphics_v2/player/`

- `icon-play.png`
- `icon-pause.png`
- `icon-stop.png`
- `icon-seek-back.png`
- `icon-seek-forward.png`
- `icon-skip-back.png`
- `icon-skip-forward.png`
- `icon-live-edge.png`
- `icon-audio.png`
- `icon-subtitles.png`
- `icon-video-settings.png`
- `icon-more.png`
- `panel-infobar.png`
- `panel-controls.png`
- `panel-options.png`
- `panel-progress-track.png`

### Suche, Navigation und Shared UI (16)

`resources/media/graphics_v2/shared/`

- `icon-search.png`
- `icon-filter.png`
- `icon-sort.png`
- `icon-clear.png`
- `icon-back.png`
- `icon-forward.png`
- `icon-close.png`
- `icon-check.png`
- `icon-warning.png`
- `icon-info.png`
- `focus-ring.png`
- `focus-rail.png`
- `sidebar-bg.png`
- `glass-panel.png`
- `divider.png`
- `loading-skeleton.png`

### BINGIE MOD Widgets (4)

`resources/media/graphics_v2/widgets/`

- `widget-live-fallback.png`
- `widget-movie-fallback.png`
- `widget-series-fallback.png`
- `widget-header.png`


## 6. Reihenfolge / Codex-Aufgaben

**Stufe 1 (35–45 wichtigste Assets):** tatsächliche genehmigte Logo-Dateien importieren, Manifest-Fanart-Pfad korrigieren; 6 Hauptmenü-Icons + 6 Homescreen-Backdrops; Einstellungen 10 Icons + 1 allgemeiner Hintergrund (10 spezielle Variationen später); Film/Serie je Fallback-Poster/Backdrop, ein gemeinsames Galerie-Panel und Gruppen-Fokusmarker. Technische Bilder mit optimierten Größen und korrekten Namen integrieren, ohne bestehendes Live-TV-OSD zu überschreiben.

**Stufe 2 (ergänzen bis 98 logische Slots):** restliche Settings-Hintergründe, EPG-Timer-/Kanäle-Icons, neue Film-/Serien-Detailaktionen, globale Suche, Shared Focus/Loading, BINGIE-Widget-Fallbacks; nur wirklich gebrauchte UI-Zustände ergänzen. Doppelte Icons vermeiden.

**Bildproduktion/Abnahme:**
1. Design-Referenz (Logo/Space) lokalisieren und Form-Freeze dokumentieren.
2. **Eine vollständige Design-Tafel/Moodboard** und 2–3 reale Kodi-Mockups für *Hauptmenü*, *Film-/Serien-Landingpage* und *Einstellungen* vorlegen; freigegebene Entwürfe einzeln als Asset exportieren, nicht nur ein einzelnes zusammengesetztes Bild als App-Asset verkaufen.
3. Automatisch bei Build prüfen: alle Dateipfade vorhanden, case-sensitiv, valides PNG/JPG, Mindestmaße/Maximalgrößen, `addon.xml`-Pfade, keine fehlenden Texturen.
4. Nach tatsächlicher Implementierung **Kodi 21 Android-TV** prüfen: Start-/Settings-/EPG-/Media-Screens, Fokus/Zurück, Cold-/Warm-Cache, Load-Latenz, 1080p/4K Skalierung, Einfluss auf BINGIE MOD.
5. Wenn Grafiken separat in `artwork/xcmate/` archiviert werden, Herkunft/Nutzungsrechte/Hash dokumentieren. **Keine unklar lizenzierten Filmstills, App-Icons anderer Anbieter oder proprietären Skin-Assets** in das XCMate-Paket kopieren.

**Wichtiger Workflow-Freeze:** Bis zur Abnahme 0.1.26 TV-Funktionen unverändert lassen. Grafische Ressourcen in eigenem Branch/PR; **kein automatischer Merge nach `main` oder neues Kodi-Update ohne Nutzerfreigabe**. Dieser Plan erzeugt **noch keine Grafikdateien**.
