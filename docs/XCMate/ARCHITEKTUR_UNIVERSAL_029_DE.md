# Universelle Medienverwaltung – Bestandsanalyse und Entwicklungsplan

Stand 20.10.2026. [Vollständiger Nutzerauftrag](CODEX_AUFTRAG_UNIVERSAL_029_DE.md).
Produktiv bleibt 0.1.28 (`63b4cd6`). PR #39 (Start-Hotfix) bleibt separat offen.
Keine automatischen Merges/Veröffentlichungen. Tests in der Cloud ersetzen keine
Abnahme auf Kodi 21.3 / RK3528 / ARM32, BINGIE MOD und Estuary.

## Bestand und Wiederverwendung

| Module | Vorhanden | Lücke / geplanter Eingriff |
|---|---|---|
| `default`, `main`, `home_menu`, `portals` | PR #39: instrumentierter lokaler Start, strenge Portaldatei, atomare Portalliste; neuer Account erst nach Save | Startfehler am Gerät weiterhin nicht lokalisiert. Keine weitere spekulative Startup-Änderung. |
| `media_progress`, `media_state` | Nonce im Kodi-InfoTag, Fortschritt alle 15 s, portal-/serien-/staffel-/episodengetrennte SQLite, Favoriten unabhängig vom Gesehenstatus | Kein Stop beim tatsächlichen Verlassen des Vollbilds, Rückkehrsample kann später vom alten Checkpoint überschrieben werden. Phase A. |
| `media_window`, `XCMateMedia.xml` | WindowXML, lokale Seiten, Gruppen/Grid, Details, Staffeln/Folgen, manuelle Gesehenmarkierung, Progressive Artwork | Weitere Rails/Fokus-/leere Zustände, Favoriten direkt entfernen, alle sichtbaren Bilder aktualisieren. Phase B. |
| `media_art` | Privates persistentes Verzeichnis, atomarer Download, PNG/JPEG-/Pixel-/HTTP-Budgets | Löscht nach 64 Dateien/32 MiB; Queue und Fortschritt nur im RAM. Persistente Jobs, konfigurierbares Budget, freie Bytes, keine stille Eviction. Phase B. |
| `live_overlay`, `tv_data`, `group_selection` | Laufende OK/Back-/Zap-State-Machine, lokale Indizes, Kontrollwiederverwendung | Zeigt deaktivierte Gruppen/AN/AUS und aktiviert bei OK; sichtbare Seitenlinks. Nur ausdrücklich in #37/#42 autorisierte Stellen ändern. Phase C. |
| `setup_wizard`, `portal_manager` | Vier Quellarten, Bestandsdialog ruft denselben Wizard auf | Scannt ganze Kataloge vor Gruppenauswahl, M3U-URL als Server validiert und verliert legitime Parameter; Nachimport modal. Einheitliche Staging-State-Machine mit Auswahl vor Scan. Phase D. |
| `xtream`, `library_index`, `catalog_sync` | Serverseitige Kategorieabfrage, Streaming-JSON, 256er-Batches, atomare Generationen, Aktivfilter, Leases und Wiederaufnahme | Quelle noch Xtream-spezifisch. Vorhandenen Index weiterverwenden, Adapter statt paralleler DB. Phase D. |
| `iptv`, `stalker` | M3U-Parser/Sections; Stalker-Auth, Kategorien, Seitendaten und Playbackresolver | M3U vollständig im RAM, kein privater Editor/Overrides; Stalker sammelte max. 50 Seiten. Stream-/Seitengenerator mit ehrlichen Fähigkeiten, stabile IDs und lokale Arbeitskopie. Phase D. |
| `stream_epg`, `guide_store`, `epg_sources` | Aktive Sender filtern, 10-Tage-Horizont, atomare Veröffentlichung, alte Daten behalten; DE/AT-Presets opt-in; Feedgesamtbytes und gespeicherte Programme getrennt | Gemeinsame Adapter für aktive Sender und Providerquelle; keine neuen Länder automatisch auswählen. Bestehende Quellen/Mapping erhalten. Phase D. |

## Abhängigkeiten und Branches

1. **A – Stabilität (#38/#40)**: neuer Branch auf PR #39. Vollbild→Navigation
   erkennen, ausschließlich verifizierte XCMate-Items stoppen; vor Stop letzten
   Positionswert speichern. Overlay-Back unverändert, kein globales Keymapping.
2. **B – Persistenz/Medien (#41/#44)**: auf A; persistente Download-Jobs und Rails
   unabhängig vom Netzwerk. Episodenstatus verwendet unverändert bestehende IDs/DB.
3. **C – Live-Navigation (#37/#42)**: auf B, eng begrenzte Ausnahme zum Freeze für
   Aktivgruppen und unsichtbare technische Fenster. Zappen/OK/Back-Logik bewahren.
4. **D – Universeller Wizard (#43)**: auf C; Quellenadapter liefern Fähigkeiten,
   Kategorien, Generatoren, Details und Play-Resolver. Staging-ID/Dateien sind nicht
   in `portals.json` sichtbar. Erst nach explizitem Save veröffentlichen; bei Fehler
   kein bestehendes Portal ändern. Lokale M3U-Kopie, Editor-Overrides und Export
   separat vom Original. Alle Clients benutzen danach denselben Wizard/Index/UI.

Gestapelte Draft-PRs weisen ihre jeweilige Basis und Vorbedingungen aus. Kein Cherry-
Pick oder eigenständiger Main-Merge. API-/UI-Tests je Phase, volle Suite vor PR-Abschluss.
Paketversionen müssen eindeutig sein; veröffentlichte 0.1.28-ZIP bleibt unverändert.

## UI und Datensicherheit

Wizardzustände: Quelle/Verbindung → Kategorien je Medienart + explizite EPG-Auswahl →
Weiter → abbrechbarer selektiver Scan mit bestätigten Zählern → Zusammenfassung/Save →
lokales Home, zusätzliche Artwork-/EPG-Jobs im Hintergrund. Unbekannte Provider-
Gesamtzahlen nicht als bereits importiert ausgeben. M3U-Gruppen ohne gesicherte
Medienart manuell zuordnen; keine erfundenen Staffeln. Keine Uploadserver.

Vorhandene SQLite-Tabellen bleiben nutzbar; Erweiterungen sind additiv und wiederholbar.
Portale, aktive/gespeicherte Gruppen, EPG-Quellen/Mapping, Favoriten, Resume, Sprache
und Erscheinungsbild bleiben erhalten. Originalplaylist nie ohne ausdrücklichen
Export überschreiben. Queue enthält private URLs nur im lokalen Profil, niemals in
Log/PR. Fehlende Fähigkeiten sichtbar machen; keine behauptete Live-Provider-Abnahme.

## Phase A – konkrete Fehlerursache und Implementierung

`MediaWindow._play()` startet `PlayMedia`, aber die Vollbild-Rückkehr nach Kodi-
Navigation hat bisher keinen Stop-Pfad. `media_progress.poll()` verfolgt dasselbe
verifizierte Item weiter, auch wenn es hinter dem Dialog läuft. UI-Back navigiert
nur die Hierarchie. Das erklärt den in #40 beschriebenen Hintergrundton im Code;
die ursprüngliche intermittierende Startblockade #38 bleibt unabhängig ungeklärt.

Neu: `playback_exit.py` vergleicht aktuelle Kodi-UniqueID mit Session-Nonce. Erst
nach wirklich beobachtetem Fullscreen wird ein Fullscreen→Navigation-Übergang als
Exit behandelt; Buffering vor erstem Vollbild stoppt nicht. Live-Overlays lassen
`Window.IsVisible(fullscreenvideo)` wahr und bleiben unangetastet. Beim Stop aktuelle
Playerposition vor dem Stop in bestehende SQLite schreiben; Identität danach erneut
prüfen, um zwischenzeitlich gestartete fremde Streams zu schützen. Alten periodischen
Checkpoint nach finaler Speicherung zurücksetzen, damit er den Resume-Wert nicht
zurücksetzt. Mehrfaches Back/Stop ist idempotent.

Integration: `service.py` vor optionalen Hintergrundjobs; `MediaWindow.onInit()` beim
Wiederöffnen des bestehenden Dialogs und dessen explizites Back als schneller
Rückkehrpfad. `live_overlay.py`, Playback-/Live-Freeze-Methoden und Keymaps in A
unverändert. Fehler bei nicht schreibbarem Fortschrittspeicher dürfen Audio nicht
ungewollt weiterlaufen lassen; vorhandener Bookmark bleibt bei Write-Fehler erhalten.
SQLite kann dabei bis zum bestehenden 2-s-Busy-Timeout warten; Gerätelatenz prüfen.

Neue Tests `test_xcmate_exit_040.py`: Movie/Episode-Stop, letzte Position vor Stop,
keine Überschreibung durch alten 15-s-Checkpoint, Fremdstream/anderer Account/staler
Marker, Itemwechsel während DB-Schreiben, Buffering und Overlay-Back, tatsächliche
MediaWindow-Reinitialisierung. Keine Fake-Player-Stop-Annahme allein aufgrund eines
Fensters; jede destruktive Aktion verlangt übereinstimmende aktuelle Item-Identität.

## Android-Abnahme A – alle Fälle OFFEN

- Film und Episode spielen, nach mehreren Minuten Back: zurück zur Detail-/Folgen-
  ansicht, Bild und Ton gestoppt; erneutes Abspielen bietet zuletzt gemessenen Resume.
- Schnell Back nach Start/mehrfach Back: kein versteckter Stream, keine Doppelaktion.
- Fremden Kodi-Stream starten, XCMate öffnen/schließen: fremder Stream bleibt unberührt.
- Live: erstes OK, zweites OK/Runter, Links, zweites Links, Hoch/Runter, Overlay-Back
  unverändert; erst tatsächlicher Wechsel zur Kodi-Navigation beendet Live.
- Audio-/Untertitel-/Videoeinstellungen als Dialog öffnen: kein ungewollter Stop.
- BINGIE und Estuary: Fullscreen-Sichtbarkeit und onInit-Rückkehr auf echtem Kodi prüfen.
- Kodi-Neustart: Fortschritt/Favoriten und alle Konten bestehen unverändert.
- Start-/Widgettest aus [PR-39-Testplan](ANDROID_TESTPLAN_0281_DE.md) zusätzlich ausführen.

Gerätefunktionen und Original-Hänger bleiben bis zum Test offen. Für Regressionen
unveränderten 0.1.28-Kandidaten über dieselbe Add-on-ID installieren, ohne Profil zu
löschen; vorher Kodi beenden und vollständiges Profil einschließlich WAL sichern.

## Prüfnachweis Phase A

406/406 vollständige Tests in 60,162 s bestanden; 7 neue Exit-Regressionen separat
7/7 in 0,253 s. Isolierter offizieller Build, Syntax/CRC und jedes Quellbyte geprüft.
[Test-ZIP 0.1.28.2](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.28.2.zip):
108 Dateien / 340.222 Bytes, SHA256 `6c33c782c04d0cbd0052f55b33054d8c8607ac4f5114939bb38997164b6f72b2`.
Gestapelte PR-Basis ist PR #39; kein Main-Merge oder Release. Android-Fälle bleiben offen.
