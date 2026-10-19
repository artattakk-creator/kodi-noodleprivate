# XCMate – VERBINDLICHE PROJEKTÜBERGABE FÜR DEN NÄCHSTEN CHAT

**Stand:** 19.10.2026 (Deutschland) · **Projekt:** GS Media / XCMate / Kodi · **Release:** 0.1.27 · **Zielentwicklung:** 0.1.28

## 0. Sofort-Start / Arbeitsanweisung für neuen Chat

Es handelt sich um die **Fortsetzung** des bestehenden GS-Media-Kodi-Projekts. Keine Neuentwicklung eines separaten Add-ons, keine zweite Beta-Installation, keine zusätzlichen unabhängigen Grafiksets. Als Source of Truth gelten das GitHub-Repository und die zentrale Space-Premium-Masterliste auf Google Drive. Vor Änderungen den aktuellen GitHub-Stand abfragen, da Codex an 0.1.28 weiterarbeiten kann.

**Verbindlich:** 0.1.27-Fernbedienung und funktionierende Live-TV-OSD-Steuerung sind FREEZE. Produktiv auf main nichts ohne ausdrückliche Nutzerfreigabe mergen oder publishen. Keine Portalzugänge, Favoriten, Gruppen, Mapping, Resume oder Caches löschen.

## 1. Projektidentität / GitHub / Umgebung

- Repository: https://github.com/artattakk-creator/kodi-noodleprivate
- Add-on-ID: `plugin.video.xtreammate`; eine einzige reguläre Installation
- Kodi 21 Omega, Android-TV-Box, Skin Titan BINGIE MOD, IR-Fernbedienung
- Aktuelle installierte / auf `main` per Quellprüfung bestätigte Version: **0.1.27**
- `main`-SHA zum Prüfzeitpunkt: `103646f98b21c27973a6a12316dca33c0378ecff`
- 0.1.28-Codex-Arbeit: **Draft PR #36** – https://github.com/artattakk-creator/kodi-noodleprivate/pull/36
- 0.1.28-Branch `feat/xcmate-028-streaming-stability`; beobachteter HEAD `54abd70b61d074c35228947222c033edca22007f`, **offen / nicht gemergt** (erneut prüfen!)
- Relevante Projektdokumentation: https://github.com/artattakk-creator/kodi-noodleprivate/tree/main/docs/XCMate
- GS-Media-Repository-Aktualisierungen werden aus produktivem `main` veröffentlicht; kein Test-/Beta-Add-on auf TV gewünscht.

## 2. Reale Gerätebefunde unter XCMate 0.1.27

**Positiv/FREEZE:** Live-TV startet grundsätzlich, bestehende Info-/Player-/Optionsleisten, D-Pad/OK/Links/Hoch/Runter/Zurück und Sendernavigation funktionieren laut Nutzer weiterhin einwandfrei. Kein regressiver Umbau ohne gezielten Test.

**EPG-Probleme:** Die EPG-Statusfenster meldeten einen Download-/Parserfehler und kaum gültige Daten:

| XMLTV/EPG-Quelle | Gemeldeter Status |
|---|---|
| Anbieter-XMLTV | `HTTP_INPUT_BYTES_LIMIT` / `ResponseLimitError`; Grenze 83.886.080 Bytes (80 MiB) |
| Deutschland Kaimandura Master | `PARSE_FAILED`, `TypeError`, 13.328.523 Bytes |
| Deutschland EPGShare01 | `PARSE_FAILED`, `TypeError`, 4.125.215 Bytes |
| Österreich EPGShare01 | `INVALID_XMLTV`, `ValueError`, 3.719.102 Bytes |

EPG-Gerätediagnose: `Cache-IDs inkl. Aliase = 4446`, nur **4 gültige Programme für +48h**, **3149 aktivierte Xtream-Sender**, **413 XMLTV-ID-Mappings = 13,1 %**, 2736 ohne XMLTV, keine bestätigten erfolgreichen Imports. Exakte Ursache der Parserfehler noch nicht per Traceback nachgewiesen.

**Filme/Serien:** Filmansicht nach Spinner/Kodi-Fehlerton nicht nutzbar; Serieneinstieg nach sehr langem „Lokaler Katalog wird vorbereitet“ endet mit `Data Unavailable ValueError`; beide teilweise mit „Index-Katalog nicht verfügbar“. Filme-Suche liefert keine Treffer. Auch nach Zurück aus Live-TV kann der Ladeindikator weiterdrehen.

**Technische Code-Funde (0.1.27):** globales HTTP-Responsebudget ~80 MiB (`network_io`), separate XMLTV-Grenze ~80 MiB, `library_index.MAX_ROWS=200000` inklusive möglichem `ValueError`, SQLite-Indexbudget ungefähr 64 MiB. `media_window._initial` ruft `library_index.refresh` über Live/VOD/Serien auf, teils globales JSON im RAM vor Gruppenauswahl. Diese Punkte sind plausible Ursachen, aber kein konkret bewiesener Traceback zur Serien-Exception.

## 3. Codex-Aufgaben für XCMate 0.1.28 (Priorität)

1. **P0 Katalogverarbeitung:** nur aktivierte Film-, Serien- und TV-Gruppen, aktuelle Gruppe sofort sichtbar; keine all-kind-Neuindexierung beim Aufruf; serverseitige Xtream-`category_id` verwenden, sofern tatsächlich unterstützt; andernfalls begrenztes Streaming-Parsing, stückweise SQLite-Batches, atomare Cache-Updates, Persistenz auch großer Bestände. Globale 80 MiB/200k/64 MiB als Gesamtbestandsbegrenzung ablösen, aber RAM-/Sicherheitsbudgets pro Chunk beibehalten.
2. **P0 Ladezeiten/Spinner:** GUI nicht blockieren, Warm-Cache nutzen, keine Doppelworker, jederzeit Zurück/Abbrechen, Fenster nicht nach Schließen aktualisieren; Zeiten und RAM auf echter Box und kleinem Stick messen.
3. **P0 Suche:** Ergebnisse nur aus aktiven Gruppen; unindiziert/indexiert/fehlgeschlagen/echte 0 Treffer unterscheiden; bedarfsgesteuerter Indexaufbau und Pagination.
4. **P0 EPG:** Parserfehler beheben, sichere und speicherschonende XMLTV-Verarbeitung, gezieltes Xtream-Kurz-EPG für Startsender zuerst, dann sichtbare aktive Startgruppe, dann weitere aktive Gruppen; Stand/Fehler pro Quelle offen ausweisen, keine Cache-Löschung.
5. **P0 Live-TV-Pre-Play:** **untere Status-/Infoleiste vor eigentlichem Streamaufbau** sofort mit lokalem Senderlogo/Now-Next und echtem Verbindungszustand öffnen. Danach Kodi-Player-Handshake. Daten und UI vorwärmen, keine versteckte zweite Videowiedergabe. Fernbedienungs-FREEZE und Session-/Z-Order-Sicherheit testen.
6. **P1 Sprache:** XCMate-eigener Sprachwähler Deutsch/Englisch/Kodi-Sprache unabhängig von globaler Kodi-Sprache und IPTV-`lang_priority`, English Fallback, DE-Bestandsnutzer nicht ungefragt umstellen. Weitere Sprachpakete später separat optional nachinstallieren.
7. **P1 Skin-Einstellungen:** eigener Bereich Skin & Darstellung für Theme-Auswahl, Hintergrund-/Panel-/Icon-Deckkraft, UI-/Fokus-/Akzentfarben, Schriftfarben und -größen, Vorschau, Speichern/Reset, Leistungsprofile. Kodi-/Titan-Systemskin unverändert. Space Premium optional, nicht im Lightweight Core enthalten.
8. **Test/Release:** Kodi-21-Tests/CI, reproduzierbare große Kataloge, >80MiB-Feeds, Startgruppen-EPG, Rücksprünge, IR-Fernbedienung, Nutzerprofile und Android-TV-Gerätetest. Kein Merge/Publish des 0.1.28-PR ohne ausdrückliche Freigabe.

**GitHub-Links:** [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19), [#21](https://github.com/artattakk-creator/kodi-noodleprivate/issues/21), [#23](https://github.com/artattakk-creator/kodi-noodleprivate/issues/23), [#24](https://github.com/artattakk-creator/kodi-noodleprivate/issues/24), [#25](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25), [#26](https://github.com/artattakk-creator/kodi-noodleprivate/issues/26), [#27](https://github.com/artattakk-creator/kodi-noodleprivate/issues/27), [#29](https://github.com/artattakk-creator/kodi-noodleprivate/issues/29), [#30](https://github.com/artattakk-creator/kodi-noodleprivate/issues/30), [#31](https://github.com/artattakk-creator/kodi-noodleprivate/issues/31), [#32](https://github.com/artattakk-creator/kodi-noodleprivate/issues/32), [#33](https://github.com/artattakk-creator/kodi-noodleprivate/issues/33), [#34](https://github.com/artattakk-creator/kodi-noodleprivate/issues/34), [#35](https://github.com/artattakk-creator/kodi-noodleprivate/issues/35).

## 4. Grafiken – verbindliche Space-Premium-Architektur

**Nur EIN Space-Premium-Design mit genau 98 logischen Slot-Positionen.** Frühere Bezeichnungen Set01/02 und 17–36,37–50 beschreiben bloße Produktionschargen, **keine separaten Themes**. Alte Originale immer bewahren und Revisionen mit neuer Prüfsumme versionieren. Keine Grafiken automatisch in den schlanken XCMate Core übernehmen. Nutzer soll optionales Premiumtheme installieren/deinstallieren können, später unabhängig Deckkraft/Farben/Schrift im XCMate-Skinbereich ändern.

**Stand:** 36 freigegeben (#1–36), 14 produziert und **noch nicht freigegeben** (#37–50), 48 unproduziert (#51–98).

**Masterverzeichnis:** https://drive.google.com/drive/folders/1UPA7fLKIq21GkA4NzAPEVfLp2BvSpm3y
**Grafikbranch:** https://github.com/artattakk-creator/kodi-noodleprivate/tree/artwork/xcmate-space-premium-set-02-20261019/artwork/xcmate/space-premium
**GitHub-Mastertracker:** https://github.com/artattakk-creator/kodi-noodleprivate/tree/artwork/xcmate-space-premium-set-02-20261019/artwork/xcmate/space-premium/MASTER_TRACKER_98_DE.md
**GitHub-Mastertracker JSON:** https://github.com/artattakk-creator/kodi-noodleprivate/tree/artwork/xcmate-space-premium-set-02-20261019/artwork/xcmate/space-premium/MASTER_TRACKER_98.json
**Grafik-Commit (verifiziert):** https://github.com/artattakk-creator/kodi-noodleprivate/commit/0c2fda12099081948c5fa8c2fa7f49d6d7b73e1a

### Kontaktblätter, Einzeldateien, ZIP und Belege

- **Settings #17–36 (20 Dateien, alle freigegeben):** [Drive-Ordner](https://drive.google.com/drive/folders/1hAVCr4SllD6E4saLCbXuF707cvBUSJOy), [Kontaktblatt JPG neu](https://drive.google.com/file/d/1OFGoUK2lZZeQtz5ytqpAWQaAH61ba6gI/view), [Kontaktblatt PDF neu](https://drive.google.com/file/d/1J1hmeFQLvShv1p_Y7Jc0-R2lpLjWBdXB/view), [Original-Archiv ZIP](https://drive.google.com/file/d/1KbF4S_rMdlyMHgG3u0XpgKZysGc_Rnqf/view).
- **Medien #37–50 (14 Dateien, Abnahme offen):** [Drive-Ordner](https://drive.google.com/drive/folders/1FnYj4u1E0fTA1GYwGkRoKwTLwAwH0VrO), [Kontaktblatt JPG](https://drive.google.com/file/d/1OJ6YQXZHoC34ScJ0NcvnLKE6Tk1ijwzG/view), [Kontaktblatt PDF](https://drive.google.com/file/d/1k31fUAQEgF16oBL2hAbLBS_m2_iT-vlt/view), [Original-Archiv ZIP](https://drive.google.com/file/d/1NhdK9GECZt7z3GVqZI7O4_4k8suyyQHR/view).
- **Branding #1–4:** Drive-Masterordner Unterordner `branding/`; unverändert und freigegeben. Die ersten Quellenarchive liegen außerdem im [historischen Grafikordner](https://drive.google.com/drive/folders/1LbwyvuQbGJ__lYdqg-4NgTsJrWK88D7j).
- **Home #5–16:** Drive-Masterordner Unterordner `home/`; unverändert und freigegeben. Historische Quelle #5–14: [Set02-ZIP](https://drive.google.com/file/d/1QvGIv27_xBDplJKjopcbBEFQiQwrYzF_/view).
- **SHA-256-Quellbelege:** `MASTER_TRACKER_98.json` und `SHA256SUMS_50_GRAFIKEN.txt` im beigefügten Übergabe-ZIP. Alle 50 realen Dateien wurden gegen die Tracker-Hashwerte geprüft (50/50 korrekt). Kontaktblatt-Belege im Paket unter `kontaktblaetter/`.
- **GitHub:** Assets 1–4 können in Drive liegen ohne GitHub-Binary; auf dem Grafikbranch liegen die produzierten `home`, `settings` und `media` Dateien. GitHub-Archiv nicht mit Add-on-Core verwechseln.

## 5. Vollständige 98-Slot-Produktionsliste

**✓ = freigegeben, nicht integriert; ◐ = erstellt, Freigabe offen; ○ = noch zu erstellen.**

| Nr. | Status | Einzeldatei |
|---:|:---:|---|
| 1 | ✓ | `branding/icon-512.png` |
| 2 | ✓ | `branding/wordmark-white.png` |
| 3 | ✓ | `branding/splash-1920.jpg` |
| 4 | ✓ | `branding/fanart-1920.jpg` |
| 5 | ✓ | `home/icon-start.png` |
| 6 | ✓ | `home/icon-live.png` |
| 7 | ✓ | `home/icon-epg.png` |
| 8 | ✓ | `home/icon-movies.png` |
| 9 | ✓ | `home/icon-series.png` |
| 10 | ✓ | `home/icon-settings.png` |
| 11 | ✓ | `home/bg-start.jpg` |
| 12 | ✓ | `home/bg-live.jpg` |
| 13 | ✓ | `home/bg-epg.jpg` |
| 14 | ✓ | `home/bg-movies.jpg` |
| 15 | ✓ | `home/bg-series.jpg` |
| 16 | ✓ | `home/bg-settings.jpg` |
| 17 | ✓ | `settings/icon-accounts.png` |
| 18 | ✓ | `settings/bg-accounts.jpg` |
| 19 | ✓ | `settings/icon-start-channel.png` |
| 20 | ✓ | `settings/bg-start-channel.jpg` |
| 21 | ✓ | `settings/icon-epg.png` |
| 22 | ✓ | `settings/bg-epg.jpg` |
| 23 | ✓ | `settings/icon-groups.png` |
| 24 | ✓ | `settings/bg-groups.jpg` |
| 25 | ✓ | `settings/icon-remote.png` |
| 26 | ✓ | `settings/bg-remote.jpg` |
| 27 | ✓ | `settings/icon-player.png` |
| 28 | ✓ | `settings/bg-player.jpg` |
| 29 | ✓ | `settings/icon-recordings.png` |
| 30 | ✓ | `settings/bg-recordings.jpg` |
| 31 | ✓ | `settings/icon-appearance.png` |
| 32 | ✓ | `settings/bg-appearance.jpg` |
| 33 | ✓ | `settings/icon-maintenance.png` |
| 34 | ✓ | `settings/bg-maintenance.jpg` |
| 35 | ✓ | `settings/icon-about.png` |
| 36 | ✓ | `settings/bg-about.jpg` |
| 37 | ◐ | `media/icon-play.png` |
| 38 | ◐ | `media/icon-restart.png` |
| 39 | ◐ | `media/icon-resume.png` |
| 40 | ◐ | `media/icon-favorite-add.png` |
| 41 | ◐ | `media/icon-favorite-remove.png` |
| 42 | ◐ | `media/icon-trailer.png` |
| 43 | ◐ | `media/icon-seasons.png` |
| 44 | ◐ | `media/icon-episodes.png` |
| 45 | ◐ | `media/placeholder-movie-poster.jpg` |
| 46 | ◐ | `media/placeholder-series-poster.jpg` |
| 47 | ◐ | `media/placeholder-movie-backdrop.jpg` |
| 48 | ◐ | `media/placeholder-series-backdrop.jpg` |
| 49 | ◐ | `media/rail-gradient.png` |
| 50 | ◐ | `media/poster-shade.png` |
| 51 | ○ | `epg/icon-today.png` |
| 52 | ○ | `epg/icon-day-prev.png` |
| 53 | ○ | `epg/icon-day-next.png` |
| 54 | ○ | `epg/icon-remind.png` |
| 55 | ○ | `epg/icon-auto-switch.png` |
| 56 | ○ | `epg/icon-record.png` |
| 57 | ○ | `epg/icon-channels.png` |
| 58 | ○ | `epg/icon-clock.png` |
| 59 | ○ | `epg/bg-guide.jpg` |
| 60 | ○ | `epg/bg-detail.jpg` |
| 61 | ○ | `epg/no-data.png` |
| 62 | ○ | `epg/source-error.png` |
| 63 | ○ | `player/icon-play.png` |
| 64 | ○ | `player/icon-pause.png` |
| 65 | ○ | `player/icon-stop.png` |
| 66 | ○ | `player/icon-seek-back.png` |
| 67 | ○ | `player/icon-seek-forward.png` |
| 68 | ○ | `player/icon-skip-back.png` |
| 69 | ○ | `player/icon-skip-forward.png` |
| 70 | ○ | `player/icon-live-edge.png` |
| 71 | ○ | `player/icon-audio.png` |
| 72 | ○ | `player/icon-subtitles.png` |
| 73 | ○ | `player/icon-video-settings.png` |
| 74 | ○ | `player/icon-more.png` |
| 75 | ○ | `player/panel-infobar.png` |
| 76 | ○ | `player/panel-controls.png` |
| 77 | ○ | `player/panel-options.png` |
| 78 | ○ | `player/panel-progress-track.png` |
| 79 | ○ | `shared/icon-search.png` |
| 80 | ○ | `shared/icon-filter.png` |
| 81 | ○ | `shared/icon-sort.png` |
| 82 | ○ | `shared/icon-clear.png` |
| 83 | ○ | `shared/icon-back.png` |
| 84 | ○ | `shared/icon-forward.png` |
| 85 | ○ | `shared/icon-close.png` |
| 86 | ○ | `shared/icon-check.png` |
| 87 | ○ | `shared/icon-warning.png` |
| 88 | ○ | `shared/icon-info.png` |
| 89 | ○ | `shared/focus-ring.png` |
| 90 | ○ | `shared/focus-rail.png` |
| 91 | ○ | `shared/sidebar-bg.png` |
| 92 | ○ | `shared/glass-panel.png` |
| 93 | ○ | `shared/divider.png` |
| 94 | ○ | `shared/loading-skeleton.png` |
| 95 | ○ | `widgets/widget-live-fallback.png` |
| 96 | ○ | `widgets/widget-movie-fallback.png` |
| 97 | ○ | `widgets/widget-series-fallback.png` |
| 98 | ○ | `widgets/widget-header.png` |

## 6. Fortlaufende Grafik-To-do-Liste

**Unmittelbar als Nächstes:** Nutzer soll **Nr. 37–50** anhand des Medien-Kontaktblatts prüfen und ausdrücklich freigeben oder Änderungswünsche nennen. Sie gelten nicht automatisch als abgenommen.

**Danach 48 verbliebene Slots in genau dieser Reihenfolge:**

- **EPG #51–62** (8 Icons, 2 Backdrops, 2 Zustandsillustrationen): `icon-today.png`, `icon-day-prev.png`, `icon-day-next.png`, `icon-remind.png`, `icon-auto-switch.png`, `icon-record.png`, `icon-channels.png`, `icon-clock.png`, `bg-guide.jpg`, `bg-detail.jpg`, `no-data.png`, `source-error.png`.
- **Player/Fernbedienung #63–78** (12 Icons, 4 Panels): `icon-play.png`, `icon-pause.png`, `icon-stop.png`, `icon-seek-back.png`, `icon-seek-forward.png`, `icon-skip-back.png`, `icon-skip-forward.png`, `icon-live-edge.png`, `icon-audio.png`, `icon-subtitles.png`, `icon-video-settings.png`, `icon-more.png`, `panel-infobar.png`, `panel-controls.png`, `panel-options.png`, `panel-progress-track.png`.
- **Suche/Navigation #79–94** (10 Icons, 6 Oberflächen-/Fokuselemente): `icon-search.png`, `icon-filter.png`, `icon-sort.png`, `icon-clear.png`, `icon-back.png`, `icon-forward.png`, `icon-close.png`, `icon-check.png`, `icon-warning.png`, `icon-info.png`, `focus-ring.png`, `focus-rail.png`, `sidebar-bg.png`, `glass-panel.png`, `divider.png`, `loading-skeleton.png`.
- **BINGIE-MOD-Widgets #95–98**: `widget-live-fallback.png`, `widget-movie-fallback.png`, `widget-series-fallback.png`, `widget-header.png`.

**Bei jeder Charge**: zuerst Motive als Einzeldateien in passenden Slot-Pfaden erzeugen, kontaktblatt als JPG/PDF, technische Maße/Transparenz prüfen, SHA-256 je Datei, ins zentrale Drive-Archiv und **nur** auf den separaten GitHub-Artwork-Branch sichern, Tracker freigabekonform aktualisieren. Vor Freigabe Status „◐“, erst nach Nutzerabnahme „✓“. Alte Dateien nicht überschreiben.

**Technische Raster:** transparente Icons 256×256 PNG; Hintergründe 1920×1080 JPG (textfrei); Poster 600×900 JPG; UI-Verläufe echte transparente RGBA-PNG (Rail 1920×280, Poster 600×900). Optimierte Assets für schwache Android-Sticks, keine ungebremste Dekodierung; Originalquellen behalten.

## 7. Sicherungs-/Prüfprotokoll

- Quelle: aktueller Tracker, Nutzerfreigaben, Original-ZIP-Chargen, Google Drive und GitHub-Artwork-Branch.
- `PR #36` ist ein laufender Codex-Entwicklungsauftrag für 0.1.28, **kein fertig abgenommener Release**. Vor Arbeiten PR-Status und Test-/CI-Resultate erneut abrufen.
- Alle 50 im ZIP enthaltenen Einzelgrafiken wurden gegen SHA-256 und durch Bilddekoder auf lesbares Dateiformat geprüft; Namen und Slotnummern stammen aus dem Tracker.
- **Keine Runtime-Integration**; ausschließlich gestalterische und organisatorische Übergabe.
- Falls Chat-Anhänge in neuem Chat nicht zugänglich sind: das ZIP **als Datei hochladen** oder GitHub-/Drive-Links aus Abschnitt 4 verwenden.

## 8. Einstiegssatz für neuen Chat

> Wir setzen XCMate fort. Bitte lies die beigefügte Projektübergabe und den 98er-Grafikmaster, prüfe dann den aktuellen Stand von Draft PR #36 (0.1.28) und entwickle die Grafiken im einzigen optionalen Space-Premium-Theme weiter. Freigegeben sind Nr. 1–36; Nr. 37–50 sind erstellt, aber noch nicht abgenommen; als Nächstes folgen Nr. 51–62 EPG. Die funktionierende Live-TV-Fernbedienung bleibt Freeze. Keine selbstständige Veröffentlichung auf main.
