# Codex-Masterübergabe – XCMate/BINGIE MOD / Widgets, EPG und Artwork
**Stand:** 12.11.2026 · **Repository:** `artattakk-creator/kodi-noodleprivate` · **Kodi:** 21.3 Omega, Android/RK3528 ARM32 · **XCMate:** 0.1.29.90 · **Skin:** Titan BINGIE MOD 2.2.3

> **Arbeitsauftrag:** Von den konkret belegten Fehlern ausgehend einen kleinen, prüfbaren Android-Hotfix für die Home-Widgets fertigstellen, dann die fehlenden Zusatzreihen, die EPG-/Bildkonsistenz und die kontrollierte Bereinigung abarbeiten. **Nicht** ohne erneute explizite Freigabe auf `main`, Pilot, regulär oder NeoDark3 mergen/publizieren. Bestehende Kodi-Konfiguration, gespeicherte SkinShortcuts, Xtream-/TMDB-Zugangsdaten, manuelle EPG-/Bildzuordnungen, Favoriten und letzte gültige Bilder vollständig schützen.

## 0. Verbindliche GitHub-Einstiege und Beweise
- **Draft-PR #437 (auf diesem Branch):** https://github.com/artattakk-creator/kodi-noodleprivate/pull/437 – minimaler Uhr-Token-Fix plus Regressionstest `tests/test_widget_clock50_consumer_91.py`. **Offen / nicht gemergt**; nach aktueller Auskunft 5 lokale Regressionstests bestanden. CI und Android-Pixel-Abnahme erneut prüfen, nicht als Gerätetest ausgeben.
- **#430:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/430 – Android-.90, `WIDGET79 CONTROL_EMPTY`, EPG-/SQLite-Befunde, gruppenübergreifende Navigation beobachteter PASS, Exit FAIL.
- **#411:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/411 – gewünschtes BINGIE-Layout, Startseiten-Bausteine und SkinShortcuts.
- **#161:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/161 – zentraler EPG-Hub, Zeitintervall-/Mehrquellenmerge.
- **#108:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/108 – Rolling Artwork Cache, Referenzverwaltung, Garbage Collection.
- **#433:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/433 – Galileo: Bild aus XMLTV-Vorschau fehlt in Details, manuelles TMDB-Matching `SAVE_BLOCKED`.
- **#174:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/174 – reproduzierter Player-Exit-Hänger mit fehlendem Native-Stop-ACK.
- **#434 / #435 / PR #436:** Google-Drive-/Multi-Storage-Backup, Guide-/Widget-Restore-Retention; als Nebenstrang behandeln und nicht durch Home-Hotfix anfassen.

**Private Testbasis:** EZ-Maintenance-Masterbackup `Master_backup_202611120818.zip` vom 12.11.2026 (9.134 Dateien; 439.830.659 Bytes), aus Kodi .90, die vom Nutzer auf Google Drive entpackt wurde. Original-ZIP lokal CRC/SHA256-geprüft; ZIP Extractor meldet 9.134 abgeschlossene Dateien. **Der umfassende 9.134-Dateien-Remote-Hash-/Restore-Android-Nachweis steht noch aus.** In Drive lautet der Entpackordner zuletzt `Master_backup_202611120818 (Entpackt - Pruefung offen)`; ältere Sicherung vom 21.10. nicht löschen. **Keine Rohlogs/Providerdaten/Geräte- oder Quellkonfiguration aus der privaten Sicherung in öffentliche GitHub-Kommentare kopieren.**

## 1. P0 – reproduzierter Rootcause: Film-/Serien-MediaRows fehlen trotz Daten
### Beobachtungen
- Gespeicherte BINGIE-SkinShortcuts besitzen drei eigene XCMate-Widget-Routen: `widget_live_start_group`, `widget_recent_vod`, `widget_recent_series`. Die Benutzermenü-ID `xcmate` wird korrekt zu `labelID=plugin.video.xtreammate/` im generierten XML; **das ist kein Bug**.
- Die Source liefert im Android-.90-Log `WIDGET79 DIRECTORY_ITEMS` mit **88 Live-, 24 Film- und 24 Serieneinträgen**, gleichzeitig meldet die Skin `CONTROL_EMPTY` für **1510/1520/1530**. `SOURCE_READY`/Anzahl != gerenderte Kodi-Container != sichtbare Pixel.
- Datei der Benutzerinstallation: `addons/skin.titan.bingie.mod/xml/script-skinshortcuts-includes.xml`; VOD/Serie benutzen noch `include content="widget_base"`, **kein** `XCMate80.MediaRow`; dabei ist `XCMate80.MediaRow` als eigenes Skin-Include schon vorhanden.
- Die generische Header-Logik `widget_header_multi` blendet auf Home Überschriften für XCMate `live|vod|series` aus; der originale Spinner liegt in genau dieser unterdrückten Header-Gruppe. Die XCMate-eigene MediaRow besitzt einen textbasierten Ladezustand, **noch keinen echten rotierenden Spinner**.
### Gesicherte Ursache / Patch
- `src/plugin.video.xtreammate/resources/lib/widget_reload78.py`, `candidate(...,layout80=True)`, `directory_uri89` validiert die XCMate-Widget-URL.
- Die generierte Kodi-URL enthält `clock50=$INFO[System.Time(hh:mm)]`. Der bisherige Validator neutralisiert nur `$INFO[Window(Home).Property(...)]` und scheitert danach am gültigen `System.Time(hh:mm)` mit `INVALID_NAVIGATION`. Der Fehler wird beim Traversal geschluckt, daher **0 MediaRow-Konversionen**.
- **Draft-PR #437** ersetzt den *exakten* Clock-Token **nur vor dem Sicherheitsvalidator**, lässt die tatsächliche URL unverändert und verweigert unbekannte `$INFO[`-Ausdrücke. Das soll auf dem gesicherten Original-Skin **exakt zwei** Konversionen liefern (`Filme`/`Serien`), Live-TV und alle Fremdwidgets unverändert. Lokal berichtet: XML valide, idempotent, fünf Regressionstests PASS. Für Codex nochmals verifizieren:
  `python -m unittest tests.test_widget_clock50_consumer_91 -v` (ggf. mit `discover -s tests -p 'test_widget_clock50_consumer_91.py'`).
### Abnahmekriterien
1. Unveränderte Kodi-Benutzerdaten; kein automatischer SkinShortcuts-Reset, kein ungeschütztes `ReloadSkin`, keine Änderung fremder Widget-URLs.
2. Zwei sichtbare `XCMate80.MediaRow`-Reihen mit **„Filme“** und **„Serien“**, deren Thumbnails, Fokus, Inhalte und Klickziele tatsächlich funktionieren. Live-Hero/Logo-Rail bleibt erhalten.
3. **Ladekreisel** aus normaler BINGIE-Animation korrekt in der MediaRow anzeigen, nur bei realem `IsUpdating`/Ladevorgang; bei leer/Fehler definierter Text statt Dauer-Spinner. Gedrängte Abstände und 1080p-Fokus prüfen.
4. Tests: Kodi-Kaltstart, Skin-Neuladen, Gruppen-/Senderwechsel, Home-Return nach Player-Ende, Online-/Offline-/EPG-BUSY, 24 Items vs sichtbare Container, externe Shortcuts nicht regressieren.
5. Selbst wenn Layout korrekt ist, `CONTROL_EMPTY` nicht allein durch statisches XML als gelöst erklären. Explizit Plugin-Datenpfad → `skinshortcuts`-Property → native Container 1510/1520/1530 → Pixelanzeige/Focus instrumentieren. Gegenprobe echte Android-Box.

## 2. P1 – drei fehlende Zusatzreihen / exaktes Home-Design
**Soll-Startseite:** großer Live-TV-Hero (aktuelles Sendungs-Fanart statt Thumbnail, Senderlogo, NOW/NEXT/Progress, Beschreibung), horizontale dauerhafte Senderlogo-Leiste, darunter **Filme** mit kleiner Überschrift und horizontalen Covern, darunter **Serien** mit Überschrift/Covern, darunter **Neu im Kino**; anschließend vom Benutzer über die BINGIE-Shortcuts ergänzbare freie Reihen. Gut lesbarer Overlay, Fokus stabil, Abstand kompakt, Ladefortschritt sichtbar.

**Ist-Zustand Sicherung:** Drei zusätzliche Einträge existieren **nicht unter** XCMates Hauptmenü-Home-Slots, sondern als TMDB-Helper-Routen in anderen Menüs:
- **Im Kino:** Filme-Menü, Container **2510**, `plugin.video.themoviedb.helper/?info=now_playing`.
- **Diese Woche im Trend:** Serien-Menü, Container **3510**, `info=trending_week&tmdb_type=tv`.
- **Disney Plus:** Serien-Menü, Container **3520**, aber `tmdb_type=movie` (inhaltlich fragwürdig).
Das sind Kandidaten für die Nutzerangabe „drei fehlende Widgets“, **nicht endgültig als exakte drei Home-Reihen bestätigt**. `Addons33.db` zeigte Helper als **installiert/aktiviert**, also nicht pauschal `Helper deaktiviert` behaupten; der eigene XCMate-TMDB-Token autorisiert Helper-Routen nicht zwangsläufig. `Home.xml` enthält `Defs_TMDbHelper_Loader`/`tmdbhelper.directcallauto`. Benutzer wünscht XCMate von TMDB-Helper entkoppeln: **erst Abhängigkeitsprüfung**, dann vorhandene Routen entweder bewusst optional belassen oder XCMate-eigene `Neu im Kino`-/Trends-Routen mit Source-Fallback bereitstellen. `Disney Plus` darf nicht ohne bestätigte Providerdaten als eigener Katalog erfunden werden. Benutzerpräferenzen und Drittwidgets niemals ungefragt überschreiben. `ShowAllWidgets=true` im gesicherten Skin; zusätzliche XCMate-Home-Slots 1540ff ungebunden.

## 3. P0 parallel / danach – EIN EPG-/Bilddatenmodell für alle Oberflächen
- Verbindliche Quellen: Xtream-Provider-EPG, EPGShare 01, Calamura, weitere XMLTV; bestätigte manuelle Kanalmappings haben Vorrang; Alias-/ID-Automatching, Zeitfenstermerge und Quellenprovenienz. `guide_v1.sqlite` als masterguide; nicht weitere widersprüchliche NOW/NEXT-Kopien bauen. Revisionierte, atomare veröffentlichte Snapshots bei Fehlern `last-good` halten.
- **Dieselben Event-/Logo-/Bild-IDs** in BINGIE Hero/Startseite, Mini-EPG, großem EPG und Sendungsdetails. Jetzt/Nächste, Zeit, Titel, Beschreibung und Bildreferenz müssen übereinstimmen; eine fehlende XMLTV-Zeitlücke darf nicht `NO_EPG` über andere erfolgreiche Quellen schreiben.
- Beim Fokussieren/Öffnen einer Sendung im Guide auf das exakte Event einen **deduplizierten asynchronen Bildjob** starten (kein Netz im GUI-Thread). Fallback TMDB-eigener Token → TVMaze → XMLTV → Logo; sichtbare erste fünf Hero-Sendungen priorisieren, Filme/Serien danach. Last-Good nicht flackern lassen.
- **Rolling-Bildcache:** Senderlogos persistent, aktive/Hero/Detail-/EPG-Bilder bis mindestens Sendungsende und anschließende UI-Referenz-/Schonfrist schützen; bei abgelaufener Sendung und fehlender anderer Referenz/Pin in kleinen Idle-Batches sicher freigeben. Serien-/VOD-Poster längere Frist (z.B. 30 Tage) und Fav-/manuelles-Mapping-Schutz. Bestehende `artwork_temp85`-TTL und `poster_store89`-24-MiB-Quota/fehlende Eviction vor Rewrite untersuchen. Keine blind löschenden Kodi-Texture-Cache-Operationen.
- Im .90-Log: **341 `EPG_READ_TIMEOUT`, 37 `SQLITE_BUSY_LOCKED`, 69 `NO_EPG`** im älteren Lauf, dazu P0 Player-Exit-ACK Hänger; separat nach #430, #174 behandeln. `SAVE_BLOCKED` bei manueller TMDB-/Bildzuordnung #433 nicht als bloßen Berechtigungsfehler erklären.

## 4. Datensparsame Altlastenbereinigung, Backup-Schutz
- Gesicherte Bestandsaufnahme: ca. **9.134 ZIP-Dateien**, 85 Add-on-Verzeichnisse; acht kleine `script.gsmedia.upgrade.*`-Resolver (nach Installer-Abhängigkeitscheck optional entfernen, minimale Einsparung); **8 `widget50_plans`-Rollback-Generationen**, letzter aktiv referenzierter Stand behalten (PR #436); zwei `guide_backups44`-DB-Sicherungen, nur letzte **gültig referenzierte und verifizierte** Backupgruppe (DB + beide JSONs) behalten, aktive DB/WAL nie blind löschen; **1.351 `.pyc`** für neue Backups optional ausnehmen; 0B-`.lock` nicht als wesentliche Restoredateien behandeln.
- **Nicht löschen:** `wizard_resume53/current.json` verweist auf Setup-Staging mit `status=ACTIVE`, einschließlich ca. 54,7-MiB-Library; bei SQLite-WAL 40,6 MiB vor Bereinigung kontrollierten DB-Checkpoint verlangen. Artwork/EPG/Favoriten/Tokens und aktuelle SkinShortcuts schützen.
- Neue **Google-Drive-Entpackung**: Benutzer meldete 9.134 extrahiert; zuvor rote ZIP-Extractor-Dateien sind im Drive-Readback wieder vorhanden, aber vollständige Cloud-Checksum- und Android-Restore-Abnahme fehlen. Keine alte Sicherung (`XCMate_backup_202610211443.zip` samt entpackter Kopie) bis echte Wiederherstellungsprüfung löschen. Backup-Addon OAuth/Restore #434 separat ohne Gefährdung des Home-Hotfix entwickeln.

## 5. Umsetzung / Codex-Arbeitsreihenfolge und Lieferobjekte
1. **PR #437 übernehmen/reviewen**, Sicherheits-/Regressionstests und Kodi21/Android-`XCMate80.MediaRow`-Test auf Basis bestehender Daten. Kleine isolierte Änderung, keine Benutzerdatenmigration.
2. **Kleine Skin-Folge-PR:** Banner/Film-/Serienüberschriften, echter Ladeindikator, Header-/Fokus-/Container-Stabilität; Live-Hero/Logos/EPG nicht verschlechtern.
3. **Zusatzwidget-PR:** `Neu im Kino` wieder sichtbar, die drei Fremd-Helper-Menüeinträge sauber diagnostizieren, optional eigene XCMate-Routen/Benutzer-Wahl hinzufügen; Auswahl über BINGIE Shortcuts weiter möglich.
4. **EPG-/Artwork-Konsolidierung** in separaten PRs nach #161/#108/#430: zentraler Snapshot/Key, per-Event-Lookups und Bild-Lifetime/GC, SQLite-BUSY/Reserve-Fallback.
5. **Abnahmedokument:** Vorher/Nachher-Screenshots, fokussierbare Reihen, `WIDGET_ITEMS` vs Skin-`CONTROL_EMPTY`, Senderlogo-Zähler, Hero/EPG-Kompatibilität, ausstehende FAILs, Testfälle PASS/FAIL/NOT_TESTED, aktuelle ZIP/SHA256 und reproduzierbare Testschritte; GitHub-Dokumentation fortführen, **neue Version nur nach bestandenen Tests und separater Freigabe**.

**Nutzersoll:** Stabil funktionierendes Kodi 21.3 mit oben großem Live-TV, darunter kompakten beschrifteten Reihen Filme und Serien, sichtbarem Spinner bei Nachladen, danach Kino-/frei belegbaren Widgets; konsistente EPG-/Art-Daten über alle Ansichten und sichere automatische Bild-/Backup-Retention. Keine neuen großen Architekturbaustellen vor der Widget-/Android-P0-Abnahme.

## 6. Statusmeldung für Codex
- **Implemented:** PR #437 clock50 URI validator fix + Regressionstests im Branch; noch Draft.
- **Observed / verified:** 88 lokale Logo-Referenzen im Backup, Widget-Quellen 88/24/24 aus Android-Log, Kodi-Backup ZIP-CRC-/Dateipfade; Zusatzwidgets und Layout-Fehlzuordnung.
- **Open:** echte Android-GUI/Native-Container-Abnahme, fehlende Zusatzwidget-Routen, Spinner, EPG-/Artwork-Konsolidierung, Exit/SQLite, Cloud-Restore-/Altbackup-Bereinigung.
- **Nicht behaupten:** „Alles gemergt“, „veröffentlicht“, „Restore bestanden“, „Widgets komplett repariert“, „Google Drive entpackt und 9.134 Hashes remote geprüft“ ohne jeweiligen Nachweis.
