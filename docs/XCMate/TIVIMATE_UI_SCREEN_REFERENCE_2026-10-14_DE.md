# XCMate – TiviMate 5.3.3: Bildreferenz für die TV-/EPG-/Film-Navigation

**Dokumentiert:** 14.10.2026 · **Grundlage:** 10 Originalfotos der laufenden TiviMate-Installation vom Nutzer, zweite Bildserie. **Status:** UI-Spezifikation, **keine** implementierte Kodi-Oberfläche und **kein** Android-Funktionstest. Die Fotos werden aus Urheberrechts-/Privatheitsgründen **nicht** ins öffentliche Repository geladen; nur ihre Layoutbeobachtungen und lokal sichtbaren Originaldateinamen sind dokumentiert.

**Referenzstandard:** Eigenständiges XCMate-Design (silbernes Logo, Space-Hintergrund, Slate-Grau) und funktional vergleichbare Bedienung. TiviMate-Markenzeichen, originale Icons, Grafiken, Videobilder und Poster werden nicht übernommen. Portale, Zugangsdaten, EPG-Zuordnungen und bestehende Remote-Profile bleiben unangetastet.

## 1. Sichtbare Bildschirmzustände – Fotoindex

| Originalfoto | Zustand (Arbeitsname) | Direkt sichtbare Elemente | Noch zu verifizieren |
| --- | --- | --- | --- |
| `1000118364.jpg` | `PLAYER_REMOTE_COLORS` | Player-Fernbedienungsübersicht: Zurück-/Info-/Guide-Taste; Rot und Grün öffnen EPG-Overlay, Gelb Infofenster, Blau Einstellungen; Reset auf Standard | Auswirkungen auf Zielgerät-/Kodi-Keycodes |
| `1000118365.jpg` | `PLAYER_INFO_CAROUSEL` | TV im Hintergrund; Gruppenname und Datum/Uhrzeit oben; laufende und nächste Sendung mit Zeit, Restlaufzeit, Kanalname, Stream-Tags, Fortschrittsbalken; unten große EPG-/Verlauf-Schaltflächen und horizontale Senderkacheln mit Logos/EPG | Ob das Layout bei allen Streams dieselbe Videogeometrie nutzt |
| `1000118366.jpg` | `PLAYER_EXPANDED_ACTIONS` | TV läuft hinter unterer Aktionsleiste; Suche, Senderliste, Aufnahmen, Multi-View, Bild-in-Bild, technische Statusdaten (Auflösung/FPS, Stereo/Audio, Latenz), Untertitel | Plattformunterstützung jeder Funktion, insbesondere Multi-View/PiP |
| `1000118367.jpg` | `CHANNELS_PROGRAM_LIST_PREVIEW` | Linke Senderliste mit Nummern, Logos, Programmfortschrittsbalken und Fokus; mittlere vertikale Programmliste nach Uhrzeit; TV rechts mit Programmtitel/-beschreibung oben | Exakter Trigger Overlay-/Vorschaumodus, Umschalten auf Sender bei OK |
| `1000118368.jpg` | `GROUPS_CHANNELS_PREVIEW` | Drei nebeneinanderliegende Ebenen: Gruppen links, zugehörige Sender mittig, laufendes TV rechts; aktiver Sender mit Play-Markierung, ausgewählte Gruppe kontrastreich hervorgehoben | Links-/Rechts-/Zurück-Pfade und Fokus-Wiederherstellung |
| `1000118369.jpg` | `EPG_GRID_FULL` | Oben laufendes kleines Vorschaubild und daneben laufender Programmtitel, Uhrzeiten, Beschreibung; unten vollständiges rasterbasiertes EPG mit Sendernummer/-logo/-name, horizontaler Zeitachse, Programmsegmenten und senkrechter Jetzt-Linie | Details von Timeshift/EPG-Scroll und Uhrzeit-Synchronisierung |
| `1000118370.jpg` | `EPG_GRID_GROUPS` | Gruppenliste links, Vorschau oben, EPG-Raster rechts; unabhängige Auswahl von Gruppe, Sender und Sendung; markierter Sender mit Play-Pfeil | Fokusübergang zwischen Gruppen- und EPG-Spalten |
| `1000118371.jpg` | `MAIN_NAV_COMPACT` | Vertikale, schmale Icon-Navigationsleiste ganz links, daneben Gruppenliste und TV-EPG; Videovorschau und Info bleiben sichtbar | Ob dies ein einklappbarer Navigationszustand ist |
| `1000118372.jpg` | `MAIN_NAV_EXPANDED` | Ausgeklappte Navigation mit sichtbaren Rubriken „Suchen“, „TV“, „Filme“, „Serien“, „Aufnahmen“, „Meine Liste“, „Einstellungen“; Gruppenliste und EPG rechts bleiben erkennbar | Startseiten-/Zurück-Pfade und Rubrikfokus |
| `1000118373.jpg` | `MOVIES_CATALOG` | Filmbereich mit eigener linksseitiger Kategorie-/„Meine Liste“-/„Verlauf“-Spalte; Kopfbereich für markierten Film mit großem Bild, Titel, Bewertung, Jahr, Laufzeit, Genres, Darstellern, Regie und Beschreibung; darunter horizontales Poster-Raster mit Ratings | Verhalten bei Fokuswechsel, Poster-Caching, Trailer- und Details-Aktionen |

Die Originalbilder sind Handyaufnahmen eines Fernsehbildschirms. Verzerrung/Perspektive und laufender Inhalt erlauben **keine verlässlichen Pixelmaße**. Die Tabellen erfassen Sichtbares; vermutete Bediengesten sind ausdrücklich als ungeklärt ausgewiesen.

## 2. Player-Farbtasten: ergänzte Nutzerkonfiguration

Diese vier **Player**-Bindungen waren in der ersten Foto-Serie nicht abgebildet und sind nun **direkt bestätigt**:

| Taste | Player-Funktion | Semantik in XCMate |
| --- | --- | --- |
| Rot | EPG im Overlay-Modus anzeigen | `guide_overlay` |
| Grün | EPG im Overlay-Modus anzeigen | `guide_overlay` |
| Gelb | Infofenster zeigen | `show_info` |
| Blau | Einstellungen | `settings` |

**Nicht mit dem EPG-Kontext verwechseln:** Rot = Favoritenstatus, Grün = Kanaloptionen, Gelb = Gruppenoptionen, Blau = Einstellungen; siehe [Tastenmatrix](TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md).

## 3. Navigationsmodell / voraussichtliche Kodi-Zustände

**Visuell nachgewiesene Zustände:** `PLAYER_INFO_CAROUSEL`, `PLAYER_EXPANDED_ACTIONS`, `CHANNELS_PROGRAM_LIST_PREVIEW`, `GROUPS_CHANNELS_PREVIEW`, `EPG_GRID_FULL`, `EPG_GRID_GROUPS`, `MAIN_NAV_COMPACT`, `MAIN_NAV_EXPANDED`, `MOVIES_CATALOG`.

**Vorgesehene XCMate-Interaktionssemantik, nicht als getesteter TiviMate-Übergang ausgeben:**

- `PLAYER_FULLSCREEN` → `PLAYER_INFO_CAROUSEL` (OK laut fotografierter Player-Belegung)
- `PLAYER_FULLSCREEN` → `CHANNELS_OVERLAY` (kurz Links) bzw. `CHANNELS_PREVIEW` (lang Links)
- `PLAYER_FULLSCREEN` → `EPG_GRID_OVERLAY` (Guide / Rücktaste / lang Menü / Rot / Grün)
- `PLAYER_FULLSCREEN` → `PLAYER_MENU` (lang OK / Menü); Zusatzleiste für verfügbare Playerfunktionen
- `EPG_GRID` → `EPG_GRID_GROUPS` (Links bzw. Guide nach dokumentierter EPG-Tastenbelegung)
- `MAIN_NAV` → `TV`, `MOVIES_CATALOG`, `SERIES_CATALOG`, `RECORDINGS`, `MY_LIST`, `SEARCH`, `SETTINGS`
- `MOVIES_CATALOG`: linker Kategorienfokus ↔ Poster-Raster ↔ Filmdetails/Trailer/Play; Fokusstatus pro Rubrik erhalten

Die Fotoreihenfolge beweist nicht den jeweiligen Tastendruck/Transitionspfad. Alle vorgeschlagenen Übergänge benötigen eigenständige Tests. `EPG_GRID_FULL` ist nicht mit der heute vorhandenen XCMate-`_epg()`-Textanzeige gleichzusetzen.

## 4. Technische Umsetzung in XCMate (Stufen)

1. **P0:** Funktionsfähige Erfassung von Links/Hoch/Runter/OK und stabiler Startsender auf der Android-Box; derzeit noch nicht als erfolgreich bestätigt.
2. **P1a (Fotomatrix):** Kontextbezogene Semantik `player`/`epg` aus `tivimate_keys.py`, einschließlich der neuen Player-Farbtasten. Pure-Python-Test allein beweist keine echte Android-Taste.
3. **P1b (GUI):** Kodi `WindowDialog`/Skin-XML oder geeignete lokale Kodi-UI für programmatisches, fokussierbares Overlay, Sendergruppen, Vorschau und EPG-Raster. Insbesondere Fokusmanagement ohne leer laufende Kodi-Verzeichnisansichten.
4. **P1c (Daten):** Cache-first EPG/Metadaten aus den bestehenden Xtream-/XMLTV-Caches; stabile Portal- und Category-IDs, keine synchronen Netzaufrufe im Tastenhandler.
5. **P1d (Zusatzfunktionen):** Sender-Karussell/Verlauf, OSD-Menü, Multi-View/PiP nur bei Kodi-Unterstützung, Audio/Untertitel/Info, Filme-Poster/-Infos sowie Serien.
6. **P1e (QA):** Getrennte Funktionstests für Live-Player, Guide, Gruppen, Filmkatalog und Remote-Kontext; CI, ZIP, Katalog; anschließend Android mit Titan BINGIE MOD. **Kein 1:1- oder Android-Pass bis zum Gerätetest.**

## 5. Bild- und Designvorgabe

- Dunkler, kontrastarmer Hintergrund, Slate-Grau als Standard, silberne XCMate-Marke und dezente freigegebene Planeten-/Space-Grafik.
- Wiederkehrende visuelle Muster: ausgewählter heller Fokus, progressive Seitenleisten (Icon / volle Navigation), EPG als breite horizontale Zeitachse mit Jetzt-Markierung, Sender-/Film-Metadaten, Fortschrittsleisten und Logos/Postern aus den jeweiligen vom Nutzer konfigurierten Quellen.
- Layouts und Symbolik **eigenständig** erstellen, statt TiviMate-Screenshots, geschützte Grafiken, Logos oder Video-Inhalte in Kodi einzubetten.
- Android-Fokus und Fernbedienungsbedienung wichtiger als dekorative Animationen. Ohne Quellasset nicht vorgaukeln, es sei schon eingebunden.

## 6. Nächste Nutzerlieferungen

Weitere **Einstellungsseiten** unter Player, Erscheinungsbild, EPG, Playlists, Filme, Serien und Navigationsrubriken kontextgetrennt an dieselbe Referenz anbinden. Bei neuem Foto Dateiname/Ansicht/sichtbarer Optionswert/Status sowie offene Interpretationsfragen dokumentieren; bestehende Beobachtungen nur korrigieren, wenn klarere Belege vorliegen.
