# Codex-Übergabe: XCMate 0.1.29.84 – Artwork-Auslagerung / Journal / Android-Speicher

> **Verbindlicher Arbeitsauftrag vom 09.11.2026.** Source-Basis: `main` bei XCMate 0.1.29.83; Codex soll Code, Tests und einen PR vorbereiten. **Nicht selbständig mergen, veröffentlichen, bestehende Releases entfernen oder auf der konfigurierten Box A migrieren.**

**Tickets:** [#401 – dieser .84-Fix](https://github.com/artattakk-creator/kodi-noodleprivate/issues/401), [#398 – Android Shared Storage](https://github.com/artattakk-creator/kodi-noodleprivate/issues/398), [#106 – flexible Artwork-Ziele](https://github.com/artattakk-creator/kodi-noodleprivate/issues/106), [#395 – Artwork/Home/EPG-Master](https://github.com/artattakk-creator/kodi-noodleprivate/issues/395).

## 1. Anwenderziel

Bestehende Logos, Film-/Serienposter, Fanart sicher und wiederholt zwischen **internem Android-Speicher**, **USB** und **Samba/SMB auf Laptop/NAS** auslagern und zurückmigrieren; später Ziel frei ändern können. Keine automatische Entfernung der Originalbilder. Schwerpunkt: EPG/Startsender und Senderlogos haben Vorrang vor Film-/Serienbildern. XCMate Home/Live/EPG dürfen bei USB-Entfernung/SMB-Ausfall nicht einfrieren.

## 2. Tatsächlich reproduziert

| Zeit (09.11.2026) | Quelldatei, Zeile | Ergebnis |
|---|---|---|
| 12:17:37 | `kodi.old.log` 2, 5, 88 | Kodi 21.3 ARM32, XCMate 0.1.29.83; Android-Release-Label 16.0.0, Runtime API 34 |
| 12:18:44–12:45:35 | `kodi.old.log` 1156 ff. bis 7402 | 13 Beobachtungen FUSE-Pool `total=4,034,297,856 B`, an Kodi-Profil bei Abfrage nur ca. 28.67→27.95 MB verfügbar |
| 12:20:14 | `kodi.old.log` 2312–2313 | Kodi-Dateibrowser kann `/mnt/media_rw/<USB-ID>` nicht öffnen, Benutzer öffnet stattdessen `/storage/<USB-ID>` erfolgreich |
| **12:20:44** | **`kodi.old.log` 2339** | **`[XCMate][ART_STORAGE83] phase=3 code=ARTWORK_JOURNAL_RESERVE_BLOCKED`** |
| 12:37:23 | `kodi.old.log` 5908 | Kodi `SMBFile::OpenForWrite()` für den XCMate-Artwork-Zielordner; Originalzeile enthält Benutzer/Passwort im `smb://`-URI! |
| **12:37:24** | **`kodi.old.log` 5912** | **erneut `phase=3 code=ARTWORK_JOURNAL_RESERVE_BLOCKED`** nach SMB-Zielwahl |
| **12:42:51** | **`kodi.old.log` 6976** | **`phase=3 code=TARGET_SAME_CAPACITY_POOL`** beim internen Android-Ziel |
| 12:46:29 / 12:47:17 | `kodi.old.log` 7692–7693, 7854–7855 | Separates Addon Caber Toss kann SMB-Logexport-Unterordner zweimal nicht erstellen; XCMate-API separat prüfen |
| 12:48:56 und 12:49:31 | `kodi.log` 663–690 und 1255 | Kodi-native Datenbank `MyVideos131.db`: fehlende `movie_view`, `musicvideo_view`, `tvshow_view`; eigener nichtdestruktiver Diagnosepfad |
| 12:49:09/12:49:19 | `kodi.log` 894–896, 1011 | EPG `SAFE_RESERVE_BLOCKED`, `PROGRAMME_DB_IO`, Artwork `DISK_FULL` auch **nach Neustart** |

**Zählung altes Log:** 22× `[XCMate][ARTWORK] role=enrol code=DISK_FULL`; bei `[XCMate][PROGRAMME_DB46]` 50× `PROGRAMME_DB_IO` und 5× `DISK_FULL`; 119× `[XCMate][HOME82] CACHED_ITEMS_READY` (60 VOD, 59 Serien) mit 24 Katalogelementen aber **0 lokalen Bildern, 0 freigegebenen Referenzen, `android_render_verified=false`**. EPG-DB-Leseversuche zeigen viele `EPG_DATA_MISSING`/`EPG_CACHE_UNAVAILABLE`; nicht alle als dauerhafte EPG-Datenverluste fehlinterpretieren.

**Visuelle Bestätigung Nutzer:** Kodi-Systeminfo zeigt `/` voll (1,5 GB), `/storage/emulated/0` 256 GB total/144 GB frei, USB 7,4 GB total/0,4 GB frei. `Movies/XCMate/Artwork/{media,logos,fanart}/<profil>` existiert mit leeren Profil-Unterordnern. USB- und SMB-Quellen lassen sich browsen. Frühere `.83`-Read-only-Zielmessung für `Movies` zeigt denselben FUSE-Mount-/Volume-Key wie Kodi-Profil und ~27 MiB verfügbar. Unterschied zwischen Kodi-Systeminfo und Python `statvfs` offen: keinen fiktiven zusätzlichen Pool annehmen; ordnerbezogene Schreibbarkeit ist kein Kapazitätsnachweis.

## 3. Mechanismus im aktuellen Code

- `src/plugin.video.xtreammate/resources/lib/artwork_ui.py`, `_manage()`: **`choice==3` = externe Zielauswahl**, entsprechend `phase=3` im Fehlerlog. Kein belegter Exit-Bug, auch wenn die Meldung beim Zurückgehen sichtbar wurde.
- `artwork_migration.py`, `_db()`: `check_space(path(), 65536)` vor lokalem SQLite-Journal `artwork_transfer_v1.sqlite` im XCMate-Profil. `import_budget.py` `RESERVE=32*1024*1024`. Bei ~27 MiB `available` ist die Schutzprüfung erwartungsgemäß BLOCKED, **auch wenn USB/SMB reichlich Platz hätten**.
- `artwork_migration.begin()`: für USB/SMB `prepare_target()` vor `_db()`. Dadurch existiert ggf. der Unterordner/`.owner`-Marker, obwohl kein Journal/Copy/Activate erfolgreich war. Für `Movies`-Shared Storage ist dagegen `preflight()` **vor** Erstellung; aus vorhandenen Verzeichnissen nicht den exakten .83-Erstellungszeitpunkt erfinden.
- `artwork_vfs.py` verwendet für SMB `xbmcvfs`, für lokal `os`. Ziel-Unterstruktur `XCMate/Artwork/{media,logos,fanart}/<profil>`, mit profilgebundenem Eigentumsmarker. `SMBFile::OpenForWrite` ohne SHA/Readback nicht als PASS zählen.
- `android_storage83.py`, `measure()/relation()/preflight()`: `statvfs.f_bavail` und `st_dev`/Mountinfo; identische Kapazitätsidentität ⇒ `TARGET_SAME_CAPACITY_POOL`; FUSE- und Firmware-Abweichungen weiter nur-lesend messen. Reserve nie einfach deaktivieren.

## 4. Fix-Reihenfolge

**P0-A Diagnosepfade korrigieren.** Exakt benannten vorhandenen Pfad in gleicher Prozess-/Mountsicht für `statvfs` und Kodi-Systeminfo vergleichen, einschließlich `/data`, `/storage/emulated/0`, `Movies`, Kodi-Profil und USB. Optional Kernel-Blockgrößen, `/proc/partitions`, `/proc/meminfo`, Android API/release anzeigen; Root nicht voraussetzen. `f_bavail`, `f_bfree`, Quotas und FUSE sauber unterscheiden. Eindeutiges Endergebnis oder `UNVERIFIED`, niemals fingierte Kapazität. Redigierter Diagnose-Export ohne privaten Hosts/Paths/Token.

**P0-B Journal-Bootstrap bei knappen internen Reserven.** Vor Start echten Journal-/Checkpoint-Bedarf berechnen. Eine sichere Architektur (klein gehaltenes lokales Journal und geprüftes externes Staging/Manifest oder geeignete alternative transaktionale Speicherung) implementieren; Abriss/Neustart/Timeout/Speicherknappheit ohne Verlust recovern. SQLite mit WAL/Locks nicht ungeprüft aufs SMB-Laufwerk auslagern. Erlaubt nur nach verified target/capacity; falls nicht sicher: klares fail-closed und keine Datenänderung. `RESERVE` nicht still herabsetzen, nichts im bestehenden Cache/Kodi-Profil löschen.

**P0-C End-to-end-Migration und freie Richtungen.** UI `Aktueller Ort → Ziel (intern/USB/SMB) → Lesen/Schreiben/Readback → Inventur → kopieren → SHA256 → Kodi-Anzeige → aktivieren → gesondert autorisierte spätere Originalbereinigung`. Bestehende `.83`-Funktionen erweitern, nicht neu parallel erfinden. Quell-/Zielwechsel intern↔USB↔SMB/USB↔SMB samt idempotentem Resume, offline/online/Fallback, No-Overwrite, Profile-Schutz. Bei nicht getrenntem Pool keinen Platzgewinn suggerieren.

**P0-D UI und Hintergrundjobs.** Subphasen beim `choice==3` aufnehmen (`PICK`, `PREFLIGHT`, `TARGET_PREPARED`, `JOURNAL`, `VERIFY`, `ACTIVATE`), Fehlermeldung am Ursprung; Benutzer darf Artwork-Verwaltung ohne neue Prüfung verlassen. Unter `DISK_FULL` Artwork-/Programme-Jobs budgetiert pausieren und EPG-/Startbild aus existierenden Daten weiter anzeigen, kein unkontrolliertes Retry-Feuer. Startseitenbilder, logos und EPG-Cover auf echter Box nach erfolgreichem externen Backend prüfen; 0 lokal render-verifizierte Bilder nicht als PASS markieren.

**P0-E SMB/USB-Sicherheit.** Kodi-Quelle mit verschlüsselter/gespeicherter Anmeldung bevorzugen; Kodi-Core-Log kann SMB-Credentials in Klartext ausgeben. In **keinem** Report, Issue, PR, Testlog oder ZIP URLs mit Credentials offenlegen. Benutzern Passwortwechsel empfehlen. SMB `mkdir`/Datei-Write/Readback/Kodi-Render in dediziertem Ziel getrennt prüfen. Caber Toss kann nicht untergeordnete Verzeichnisse erstellen, was XCMate nicht automatisch widerlegt; genauen Backendschritt nachweisen. USB unter `/storage/<VOLUME>` statt blind `/mnt/media_rw/<VOLUME>` anbieten, Rechte im konkreten Mount prüfen.

**P1-Eigenbefund** Kodi-native `MyVideos131.db` fehlende Views read-only prüfen (`sqlite_master`, `PRAGMA integrity_check` falls verlässlich und ohne Schreiböffnung), nicht automatisch löschen/rebuilden, keine Providerkataloge damit gleichsetzen.

## 5. Abnahme / Tests

- Unit-Tests für `ARTWORK_JOURNAL_RESERVE_BLOCKED` bei 27 MiB, 32 MiB +64KiB Schwelle, reservierte Blöcke, lokal 256-GB-Anzeige vs FUSE 3,76-GiB-Mount, FUSE gleiche `st_dev`-/Mount-Key, block FS getrennt, unverified; nicht mehr vorhandene USB-Pfade und eingeschränkte Android-API-34-Rechte.
- USB/SMB `Browse` ist separat von `Write`, `Readback`, `SHA`, `Render`; Testfall SMB-Log-URI mit Passwort darf nicht in Diagnose auftauchen; Caber Toss-Fehler ist unabhängig. Kürzlich angeschlossener USB hat nur 0,4 GB frei: richtig warnen.
- Interruptions: USB entfernen während Copy/Verify, SMB off, Kodi kill, Power loss, SQLite Busy/IO/Read-only, Disk full beim Commit, reconnect/resume, Eigentumsmarker-Kollision, fehlende/nicht passende Quellen, unveränderte Originale.
- Hardwaretests **Box B**, alle 6 gerichteten Wechsel intern↔USB/SMB↔USB; Fortschritt und reales Bild in Kodi, Startseite/Logos/EPG, kalt/warm Start. Alle Fälle PASS/FAIL/NOT_TESTED mit echten Receipts. Host-CI ersetzt nicht reale Box-Abnahme.
- Bestandsdaten und ältere Release ZIPs unverändert; Xtream-/Providerdaten, Zugangsdaten, EPG/Mappings, TMDB, Kodi DB, Favoriten, SkinShortcuts, BINGIE MOD und Installer **0.5.26** unverändert. Box A bis Abnahme nicht anfassen.

## 6. Liefervertrag für Codex

Branch: `fix/xcmate-02984-artwork-journal-capacity` von aktuellem `main`. Kumulativ `plugin.video.xtreammate` Version **0.1.29.84** nur nach Implementation, mit Tests, Changelog, ZIP+SHA256 und grünem CI. PR gegen `main`, ausführlicher Statusbericht in Issue #401 und Aktualisierung #398/#106/#395. **Kein automatischer Merge auf `main`, kein Publisher und kein Update der drei Repository-Kanäle** bis Nutzerfreigabe. Reale Android-Box-Fälle offen als `NOT_TESTED` markieren statt behauptetem PASS.

## 7. Datenschutz

Die von Nutzer hochgeladenen Kodi-Logs bleiben private Diagnosequellen. Besonders **`kodi.old.log`, Zeile 5908** enthält einen SMB-URI mit eingebetteten Zugangsdaten. Diese Zeile **niemals im Rohformat** auf GitHub kopieren; auch Rechnername, LAN-IP, Provider-URLs, Xtream-Tokens und sonstige Kennungen aus Befunden entfernen. Im GitHub-Issue stehen nur abstrahierte, nicht-sensitive Zeit-/Zeilenreferenzen.
