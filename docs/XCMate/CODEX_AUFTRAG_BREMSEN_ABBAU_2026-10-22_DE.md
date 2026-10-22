# XCMate – Codex-Auftrag: künstliche Bremsen abbauen, Daten schützen

**Nutzerfreigabe vom 22.10.2026:** „Also alle Sperren auch für SQLite und was uns jetzt noch blockiert, bitte alles aufheben.“

## Auslegung

**Erwünscht:** Alle *künstlichen* Kapazitätsgrenzen, dauerhaften Sackgassen in Retry-/Downloadqueues und unnötigen SQLite-Warte-/Fehlerzustände entfernen. **Nicht erwünscht:** Integritätsschutz (SQLite-WAL/-Transaktionen/-Wartungslocks), echte physische Speicherreserven, RAM-/Codec-/Archiv-Validierung, sichere Dateilimits, API-Rate-Limits und Nutzer-/Portal-Schutz deaktivieren.

**Entwicklungsbasis:** `main` = XCMate 0.1.29.13. Bereits regulär veröffentlicht, aber Android-EPG nicht freigegeben wegen [P0-Absturz #89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89), Gruppen/Logos/Mapping [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88), Artworkblockade [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90) und SQLite-/Queue-Diagnose [#91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91). **0.1.29.11** bleibt real getestet als Rückfallbasis, mit separaten Restbefunden.

## Arbeitsreihenfolge (verbindlich)

1. **P0 #89 sofort:** Vollständigen Kodi-Absturz bei EPG → OK → „Jetzt Sender ansehen“ isoliert beheben. Sicherer Übergang nach Schließen des modalem GuideWindows zum stabilen Live-TV-Player, ohne Reentrancy/Doppelstart; nur sichere Android-Test-ZIP, noch kein OTA-Release.
2. **P1 #90 dringlich:** 512-MiB-Artwork-Default und 4096-MiB-Maximum entfernen (Option „kein festes Sammlungsbudget, reale Freispeicherreserve“). Auch alte `SPACE_FULL`-Jobs mit `attempts>=3` unter neuem Budget automatisch und begrenzt wieder aktivieren. Die Codezweige `art_store.budget`, `media_art.fetch`, `art_store.run_one`, `art_store.enqueue`, `artwork_health_ui.status_text` und Addon-`settings.xml` einheitlich umstellen. Bestehende Bilder/Konten nicht löschen. EPG-Senderlogos in Jobpriorität vor VOD-Background-Scans setzen.
3. **P1 #91 SQLite:** `artwork_db._failure` setzt bereits bei flüchtigem `SQLITE_BUSY` einen 5-sekündigen globalen Pausenzustand; `connect()` hat .05s Gate-/SQLite-Timeout. Ursachen messen, begrenzte Retry-/Backoff-Politik nur für transienten BUSY entwickeln, Reader und Writer entflechten, Status-Snapshots nonblocking halten; keine GUI-Threads mit I/O blockieren. `library_index.connect(write=True)` wiederholte Schema-/WAL-DDL pro Schreibverbindung prüfen und entlasten, ohne Schema-Migrationssicherheit zu verlieren. `guide_grid_data.page` bei 50ms Lock-/400ms Querylimit und `catalog_sync` beim Resume unter transientem Fehler untersuchen; Daten statt `FAILED` verlieren nicht überschreiben. Kein blindes Öffnen beschädigter SQLite-Datenbanken.
4. **P1 #88:** Startsendergruppe + Startsender direkt als EPG-Einstieg, Links öffnet Gruppenliste, Logos und direkte manuelle XMLTV-Zuordnung, Programmdetails/Episodenbilder nur mit belastbaren Metadaten. Horizontalen Rasterstil beibehalten.
5. **QA:** Korrupter Index, Writer-Lock, paralleles Backup/WAL, knappes Speicherbudget, Offline-Stream, 17k alte `SPACE_FULL`-Jobs, 2.400+ Sender, zehnmal Statuspopup und Doppel-Zurück, Film/Serie/Resume/Live-Overlays; alle Testlogs ohne Portal-URLs/Auth-Header. Vorher-Nachher-Zähler für BUSY/READY/PENDING/BUDGET_FULL/DISK_FULL; Nutzerbestätigung auf Android RK3528 ARM32/Kodi 21.2/BINGIE MOD.
6. **Lieferung:** Codex erstellt getrennte sichere Draft-PR(s) **auf Basis von main**, rebase/Integration der voneinander unabhängigen Feature-Drafts **0.1.29.14/.15** nur explizit später. Keine Versionskollision mit geplantem .16. Reviewbericht, Hosttests, ZIP/CRC/SHA256, Rückfallweg. **Kein automatischer Merge, Produktivindex-/Repository-Release, Cache-/DB-Reset ohne erneute ausdrückliche Nutzerfreigabe.**

## Zu vermeidende Pseudofixes

- Kein `PRAGMA journal_mode=OFF`, `synchronous=OFF`, `read_uncommitted=ON` oder pauschales Entfernen von SQLite Locks.
- Keine endlosen Netzwerk-Retries, ungeprüftes Deaktivieren von HTTP-Fristen oder unlimitiertes Zwischenspeichern im RAM/Android-Gerät.
- Kein globales `art_store.retry()` über sämtliche FAILED-/READY-Jobs und keine automatische DB-/WAL-/SHM-Löschung.
- Kein stilles Setzen aller EPG-IDs auf vermutete Matches.
- Keine Beschönigung der Android-Regression: der P0-Kodi-Prozessabsturz ist nach wie vor vorhanden, solange nicht durch neuen Gerätetest widerlegt.

## Quellen

- [P0 Kodi-Crash #89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89)
- [Artwork-Grenze & SPACE_FULL #90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90)
- [SQLite-/Queue-/Importhemmnisse #91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91)
- [EPG Gruppen/Logos/Mapping #88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88)
- [Früheres Artwork-DB-Indexproblem #69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69)
- [Android-Logauswertung](ANDROID_LOG_AUSWERTUNG_02911_2026-10-22_DE.md)
