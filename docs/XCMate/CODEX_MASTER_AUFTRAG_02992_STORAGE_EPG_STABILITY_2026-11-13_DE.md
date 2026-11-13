# Codex-Masterauftrag XCMate 0.1.29.92 – Speicher, USB, EPG, Stabilität
**Datum:** 13.11.2026  
**GitHub:** artattakk-creator/kodi-noodleprivate  
**Master-Issue:** #445, ausgehend von #443  
**Baseline:** main @ 77bdce8d84a6377241fcc7a7f3840ca293d80c4f, plugin.video.xtreammate 0.1.29.91  
**Zielversion:** 0.1.29.92, zunächst Entwicklungs-/Release-Kandidat.  
**Freigabe:** Entwicklung, Dokumentation, isolierte PRs und Tests beauftragt. **Kein Auto-Merge und keine Veröffentlichung** in regulär/Pilot/NeoDark3.  
**Geschütztes Fallback:** 0.1.29.90, SHA256 e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f (reguläres und verschachteltes Pilot-ZIP/SHA erhalten, kein Auto-Delete).

## 0. Verbindliche Reihenfolge und Qualitätsregeln
1. P0-A Speicherursache messen und wirkliche interne Platzentlastung, XCMate-eigene Altlastenbereinigung, USB-Migration und Installer-/Einstellungs-Integration (#443, #401, #106, #108).
2. P0-B Manuelles Bildmapping atomar und dauerhaft; SQLite/EPG/Cache-Last so entschärfen, dass Speicherung und GUI-Start nicht wieder scheitern (#433, #413, #442).
3. P0-C Player-Stopp, Live-Stream-Exit, Home75/ungültige Skin-Expressions, Widget-Timeouts ohne verschwundene Reihen (#442, #174).
4. P1-D EPG-Kanalzuordnung per langem OK aus Senderliste/Mini-EPG/Guide, XMLTV-Bildfallback, zentrale Retention (#161, #98); Film-Home-Gruppenfilter (#444), MP3-Neuheiten und Bilddetail-Layout; Kodi-Streambuffer-Optionen gemäß #107 nur korrekt als Kodi-global und nicht als Scheinfeature.
5. Kann ein P1-Fix nicht ohne Risiko abgeschlossen werden, muss er als OPEN mit isoliertem Nachfolge-Issue markiert werden. Die .92 darf nicht fälschlich alle Punkte als FIXED ausweisen.
**Nur nach Nutzerfreigabe** einen Release-Merge; bestehende offenen Draft-PRs #428 (Installer/TMDB Pairing) und #436 (Retention) NICHT ungeprüft in .92 einbeziehen.

## 1. Reale Fehler und evidenzbasierte Hypothesen
- Android-TV/RK3528 ARM32, Kodi 21.3, Skin Titan BINGIE MOD 2.2.3, XCMate .91. Interne Android-/App-Daten nach Nutzeranzeige >1,3 GB. Nach Löschen von etwa 75 MB Cache Start wieder gelungen und viele Funktionen stabiler. Dies ist ein **starkes Indiz für Speicher-/Quota-/Reservemangel**, keine bestätigte Größe des konkreten Mounts.
- 13.11. erster fehlgeschlagener Kodi-Start 06:32:04–05: Kodi: audioencoder.kodi.builtin.aac not installed or not enabled; CServiceManager::InitStageTwo: Unable to start CAddonMgr. Zweiter Start 06:34:15: AAC wieder installiert, Kodi bootet. Dies ist ein **eigener Kodi-Addon-Bootstrapfehler vor XCMate-Start**; Zusammenhang mit Cache und Dateisystem nur Hypothese, gesondert testen.
- .91 zweite Sitzung 13.11. 06:34–07:24: RESERVE_BLOCKED 85, EPG_READ_TIMEOUT 111, SQLITE_BUSY_LOCKED 32, ReminderMonitor profile write busy 22, PROGRAMME_CACHE_BUDGET 21. Home-Reihen mit elapsed_ms bis ~188141 ms. Vier Home.xml Boolean-/Misplaced-[ Parsermeldungen für Film-/Serienwidget-Bedingungen; CONTROL_EMPTY/NATIVE_HOME_EMPTY trotz Widget-Items.
- Logs am 12.11. und 13.11. zeigen unterschiedliche Player-Exit-Pfade, RETURN48/STOP_TIMEOUT, stream stalled, Demux-Open-Fail, sporadisches ungeplantes Home. Home75-Test in RC und vorheriger Main-Baseline FAIL: Down 2530 → 2540 NATIVE_DIRECTION_DID_NOT_MOVE, setfocus() invalid; nicht stummschalten.
- Manuelle TMDB-/TVMaze-Bildsuche findet Treffer und nimmt Auswahl scheinbar an, aber Zuordnung nicht persistent/kein Fehlerdialog. Positiv: automatische Bilder oft schnell, Senderlogos, XMLTV-Bilder im Mini-EPG, TVMaze/TMDB und teils Ghosts-Mapping funktionierten; diese Pfade schützen.
- Keine Logs mit eindeutiger MANUAL_ASSIGN_SAVE → DB_READBACK Kette. Eigene Instrumentierung statt Ursachenerfindung. Logdateien enthalten private Provider-/Streaming-URLs: nicht öffentlich einchecken.

## 2. Speicherinventur, Prioritäten und Platzgewinn
Vor JEDEM Cleanup und jeder Migration read-only Inventur mit Mount-/Volume-ID, freier Kapazität, Android-Datenquota, statvfs bavail, Byte/Anzahl je Datenklasse sowie Snapshot-Zeitpunkt.
Datenklassen: XCMate Cover/Poster/Fanart, programme_images/EPG-Artwork, Senderlogos, aktive/alte EPG SQLite (programmes, guide44_inputs, weitere Metadatentabellen), SQLite -wal/-shm und Backup, normalisierter epg2 Cache, temporäre XMLTV/XML.GZ-Dateien (falls vorhanden), Migrationsjournal, Kodi special://thumbnails und Textures13.db, weitere Kodi caches/Addon ZIPs, Installer-Reste, Logs/Restore-Daten. VIRTUAL/RSS-KiB nie mit dauerhaftem Datenträgerverbrauch verwechseln.
**Nachweisziel:** freier interner Speicher vor/nach verifiziert; Quellpool im Gegensatz zu emulated/Movie-Pfad auf gleichem physischen Volume. Keine unbelegte Behauptung, die 1,3 GB seien das tatsächliche Gesamtlimit.
USB derzeit laut Nutzer etwa 3 GB frei, NICHT mit früherer 0,4GB-Messung verwechseln. Livemessung, echte Schreib-/Lese-/Hash-/Renderprobe. Mindestens geräteabhängige Reserve (Pilot beispielhaft 300–500 MiB), kein voller 3GB-Transfer auf Verdacht. Zuerst maximal 1–2 GB Pilotbestand, falls Platz tatsächlich verfügbar. NAS als gesonderter VFS-/Offline-Test.
Bei Root-Quellpool mit zu wenig Reserve keine riesige interne Journalingdatenbank erzeugen: begrenztes staging/journal-Design mit externem Ziel, Signatur/Reboot/Resume prüfen. TARGET_SAME_CAPACITY_POOL erkennen und ablehnen.

## 3. EPG: eine begrenzte Datenhaltung statt wachsender Kopien (verbindliche Nutzerentscheidung)
**Soll:** EPG-Provider und aktivierte XMLTV-Feeds herunterladen, validieren, deduplizieren, quellenbewusst abgleichen, stufenweise in die aktive lokale EPG-Datenbank übernehmen und **erfolgreich verarbeitete Download-Zwischendaten unmittelbar entfernen**. Keine dauerhafte Sammlung alter XMLTV-Rohdateien/monatlich wachsender Rohfeed-Archive als Standardeinstellung.
**Ist-Code .91 (prüfen und präzisieren):** epg.py ruft http_get(...MAX_XML_BYTES...) auf, hält Raw-Bytes im Speicher, parse_xmltv und import_cache, zusätzlich _save_disk(per-portal normalized cache) und _mem_set. epg_sources.py:merge_sources lädt jede externe Quelle als raw, parst, merged. guide_store.py speichert in SQLite/WAL; guide_publish44.py schreibt quellbezogene guide44_inputs und publizierte programmes **ohne Retention**. programme_store46 besitzt zusätzliche Metadaten-Stagingebene; guide_backup44 separat. Das ist **nicht** bereits ein einziges schlankes Datenschema. Löschung von .xml-Dateien allein reicht nicht.
- Für große Feeds bevorzugt inkrementellen, speicherbegrenzten Download/Parser; wenn lokales Staging nötig, expliziter Temp-Speicher auf geprüftem USB, nach erfolgreichem Import SHA/Revision und normaler Löschung, auch bei Abbruch in sicherem nächsten Recovery. Wichtig: fehlgeschlagene/verkürzte Downloads dürfen den letzten gültigen Guide nicht überschreiben.
- Eine logisch zentrale aktive SQLite-EPG-Datenbank intern für schnelle Leser; nur tatsächlich für Mehrquellen-Konflikte, Quellprovenienz, manuelles EPG-Mapping oder last-good notwendige Quellfakten behalten. Doppelte Vollkopien in cache_set/guide44_inputs/programmes/Metadaten minimieren oder an klar definierte kurze Lebensdauer binden. Migration/Reader-Kompatibilität mit Tests, keine übereilte Tabellenlöschung.
- Historie: Nutzerpräferenz 7 Tage rück, bis 20 Tage vor soweit Feeds Daten liefern. Retention auf UTC/Zeitzonen, Sendungsende und Quellfenster, indexgestützte bounded batches; obsolete historische, quellenbezogene und staging Datensätze tatsächlich purgen. Keine Löschung von manuell gebundenen Senderzuordnungen, Favoriten, Remindern/Catch-up-Referenzen oder laufenden Events. Konfiguration für künftig kürzere Historie optional; NICHT eigenmächtig auf 0 Tage setzen.
- Freier physischer Platz nur nach WAL-/Checkpoint/Compaction, jeweils Speicherreserve/Locks/Backup prüfen: DELETE allein macht Datei nicht sicher kleiner, VACUUM kann massiv temporären Platz benötigen. Keine automatische ungeprüfte VACUUM-Aktion.
- Mehrquellen-Merge: Xtream-Anbieter-EPG plus EPGShare01/andere aktivierte XMLTV, per source ID + channel mapping, vorgezogene manuelle Zuordnungen, Fallback bei Ausfall. Source identity darf nicht verloren gehen, obwohl temporäre Download-Datei verschwindet. Bei Quelle offline den letzten gültigen relevanten Guide behalten.
- XMLTV-Sendungsbilder: bereits eingelesenen icon-Verweis konsistent in Mini-EPG und Details verwenden; separate „XMLTV-Bild verwenden“-Aktion als gültige manuelle Auswahl, vollständiger event/source/revision write/readback. Artwork-Datei bzw. URL ist unabhängig von XMLTV-Rohfeed und darf nicht versehentlich mit diesem gelöscht werden.
**Test:** große gezippte/XMLTV-Feeds, 3 Quellen mit Kollisionen, abgeschnittene gzip-Datei, DNS/HTTP-Timeout, 7 Tage Vergangenheit/20 Tage Zukunft, Daylight Savings/UTC, mehrere Aktualisierungen, Storage fast voll, USB fehlt. Vorher/nachher Bytes der Rohdownloads, persistenter Caches, aller aktiven EPG-Tabellen, WAL und Backups nachweisen.

## 4. Cleanup-Vertrag – automatisch, einmalig, wiederholbar
GS Media Installer: nach Basisinstallation, aber **vor** massenhaftem EPG/Artwork-Prefetch, automatische Prüfung und tatsächliche Löschung ausschließlich eindeutig entbehrlicher *XCMate-eigener* temporärer/abgelaufener Daten. Auf Upgrade genau einmal je Profil/Version mit wiederanlaufbarem Journal; keine wiederholten Massenlöschungen in Boot-Schleife. Spätere kleine periodische Wartung mit begrenztem I/O und manueller Option XCMate → Einstellungen → Speicher.
Kandidaten: abgelaufene unbenutzte XCMate Temp-/Part-Dateien und Download-Stage-Reste; EPG-Sendungsdaten außerhalb des aufbewahrten Horizonts soweit ohne aktive Referenzen; tatsächlich verwaistes Artwork nach mehreren bestätigten vollständigen Katalog-Snapshots/Schonfrist (siehe #108). Sicherer Eigentums-/Referenzbeweis, transaktionssicherer Batch, Resume, readback, physische Bytes frei gemessen; unbekannte Daten NICHT löschen.
**Verbote:** Kodi-Userdata/Addon-Skin/Textures-DB/Thumbnail-Cache nicht pauschal löschen, keine fremden Addons, persönliche Einstellungen, TMDB-Token, EPG-Mappings, last-good, manuelle Bildzuordnung, aktuelle Backups, Arbeitsjournale oder .90-Fallback ZIP/SHA. Option für separat bestätigte Kodi-Core-Thumbnail-Pflege nur mit vollständigem Kodi-kompatiblem Beweis, Backup und eigener Rollbackstrecke.
Achtung: Ein vor XCMate gescheiterter Kodi CAddonMgr-Start ist nicht direkt durch einen später startenden Installer zu reparieren. Eigenständige Kodi-Bootstrap-/Addon-Verfügbarkeit untersuchen.

## 5. USB-Auslagerung und UI/Installer
**XCMate → Einstellungen → Speicher** als echte eigene Seite (bisher storage-Alias von system), Unterpunkte: Gesamtübersicht je Volume, Bild-EPG Ja/Nein/Später, interne vs externe Pfade, XCMate-Poster/Fanart/Sendungsbilder/Logos, temporäre EPG-Rohdownloads, Daten übertragen, Prüfergebnis/Status, sichere Bereinigung, Wiederherstellung und USB-Offlinestatus. Bereits vorhandene XCMate Artwork-Verwaltung weiterverwenden, keine zweite konkurrierende Datenhaltung.
**GS Media Setup Wizard:** in eigener Version >0.5.26 nach Komponenteninstallation und vor Vorabdownloads UI: Bild-EPG verwenden? Ja / Nein / später; Wo Bilder und ggf. große temporäre XMLTV-Downloads ablegen? intern / USB auswählen / NAS auswählen / später. Aktive EPG-SQLite, WAL und Mapping DB vorerst intern. Bei aktivierter externer Wahl Probezugriff/Volume-Kapazität vor Work. Bei fehlendem USB nicht abstürzen; Setup kann mit Text-EPG und temporär deaktiviertem Bildvorabladen weitergehen. Upgrade ohne Verlust bestehender Einstellungen, Altlasten-Scan idempotent.
Migration: Pinned source manifest, Hash/Readback/Renderable Test, Reboot und USB-Offline-Fallback, atomarer Target-Switch; **interne Originale erst NACH bestätigter Zielintegrität und gesonderter Löschbestätigung** entfernen. Live-TV erste fünf Herobilder schnell; übrige Cover in Hintergrund mit geringer Priorität.

## 6. Weitere Reparaturen: Priorisierte Regressionen
### P0 Bildmapping / GUI-EPG
- TMDB-/TVMaze-Suche bleibt erhalten, einschließlich Ghosts-Mehrfachtreffer; manuelle Auswahl muss echte Writer-/DB-Commitbestätigung + separaten persistenten Readback + UI-Refresh erhalten. Transaktionsergebnis und Source-/Event-Revision erfassen, bei SQLITE_BUSY, RESERVE_BLOCKED, EXTERNAL_UNAVAILABLE, SOURCE_CHANGED, EVENT_CHANGED eindeutigen Fehler anzeigen, bei gespeichert aber Artwork noch nicht materialisiert eigenen Status. XMLTV-Bild zu Eventdetails und manuelle XMLTV-Quelle.
- EPG/Bild-Read-Timeouts und Profile-Busy mit begrenzter Worker-Konkurrenz und eindeutiger Ownership. EPG zuerst → Senderlogos → erste 5 Hero → Cover; kein endloses aggressives polling.
### P0 Player/Start/Home
- Kodi AAC-Encoder-Builtin-/CAddonMgr-Startup (06:32 scheitert, 06:34 verfügbar) mit nativen Logs/Android Start testen; getrennt von XCMate Profil-/Artwork-Mangel. Geen Kodi-Core-APK Patch ohne Nachweis.
- XCMate PLAYER_EXIT STOP_TIMEOUT, RETURN48 failed, Kodi is not playing any media file, ungewollte Home-Wechsel, Stream stalled, OpenDemuxStream fehlgeschlagen; STOP/USER_BACK vs. echter Streamfehler differenzieren; begrenzter Reconnect nur bei unbeabsichtigtem Abbruch. Fremde über TMDB Helper gestartete Serien nicht in XCMate-Spezialplayer zwingen.
- Home75 Test Down 2530→2540 und setfocus() unknown; außerdem echte vier Skin Home.xml boolean Misplaced [ Parserfehler beheben. 720p/1080p sowie Android-Fernbedienung testen, nicht Skips erhöhen. Film/Serien/Live Widgets dürfen unter BUDGET/PROFILE_BUSY nicht verschwinden; last-good ohne endlose Stale-Loop.
### P1 UX und Wunschfunktionen
- EPG-Kanalzuordnung per lang OK in Senderliste/Mini-EPG/Haupt-Guide: Quelle/ID auswählen, Vorschau, Bestätigung, persistenter Readback; kurzes OK unverändert. Siehe #98/#161.
- Home-only Film-Neuheiten-Auswahl nach Portal und Providergruppen-ID, insbesondere Adult/Erotik und Sport/Boxen ausblenden, ohne gesamte VOD-Bibliothek zu filtern; neue Kategorien nach Nutzerentscheidung. Siehe #444.
- MP3-Widget soll Neuheiten/Alben und Cover statt Kategorien im Add-on-Hauptmenü anzeigen. Niemals funktionierende Wiedergabe löschen.
- Senderlogo oben links in Sendungsdetails; korrekte TMDB/TVMaze-Quellenlogos und klickbare werkbezogene Links, TMDB-Attribution im gut erreichbaren Credits-Bereich gemäß Pflicht; kein pauschaler falscher „/movie“-Link. XMLTV fallback.
- Poster proportional moderat vergrößern; **exakter Layoutwert nach zukünftigem Screenshot**, keine blinde Layoutänderung vor Screenshot.
- Einstellbarer Stream-Puffer gemäß #107 (Kodi 21 global, sichere echte UI zu Kodi-Einstellungen, kein per-Stream-Pseudoregler), Status ggf. OPEN, sofern ohne Risiko nicht machbar.

## 7. Umsetzung und Abnahme
Codex soll 1) reproduzierbare Fehler-/Ursachenmatrix in docs/XCMate, 2) isolierte Source-PR auf .91-main für .92, 3) getrennte GS Media Installer-Draft-PR, 4) gezielte unit-/host/native-Kodi 720p/1080p Tests + Android-IR-Checkliste, 5) verifizierbares ZIP mit SHA256 und versionierter Änderungs-/Rollbackliste, 6) Speicher-Vorher/Nachher-Bericht je Volume einschließlich tatsächlichem LastGood/EPG-Coverage-Bericht liefern.
Minimal sichere Abnahmekriterien:
- Android RK3528 aus nahezu vollem internen Zustand startfähig, keine zerstörten Profile, reale Reduktion mindestens jener Bytes, die als entbehrlich belegt sind; falls Null bereinigbar, klare ehrlich dokumentierte Grenze.
- USB-Pilot mit wirklicher freier interner Kapazität nach bestätigter Freigabe, automatische und manuelle Speicherverwaltung, Installer opt-in, Abzieh-/Stromausfall-Test, Recovery.
- EPG überlebt mehrere Quellenupdates/ausgefallene Quelle; Downloadzwischenstände nach erfolgreichem Update beseitigt, keine unlimitierten Quellkopien; 7d/20d Schutz.
- Manuelle TMDB-/TVMaze-Bildzuweisung nach Reopen und Reboot tatsächlich persistent; bei Fehler echte UI-Diagnose.
- Home75 720p/1080p pass ohne gefälschte Move-Mocks; keine Skin Parserfehler; sechs .91-Reihen wieder geladen; MP3/Provider-Tokens und Logo-/Sendungsbildpfade erhalten.
- Player-Exit-Reproduktionsfälle (Live, VOD, Serie, extern TMDB Helper), STOP_TIMEOUT, UserBack, StreamLoss, kurzer OK und lang OK, kein unerwarteter Home-Sprung.
- Ausgewiesener Teststatus pro Feature: FIXED_HOST / FIXED_NATIVE / ANDROID_NOT_TESTED / ANDROID_PASS / OPEN. GitHub Merge/Release NICHT autonom.

## 8. Querverweise und Schutz
Master #445; Storage #443; Stabilität #442; manuelles Bild #433/#413; EPG #161/#98; Artwork GC #108; USB #106/#401; Player #174; Streambuffer #107; Widget-Filter #444; offene Drafts #428/#436. 
Nur redigierte, minimal notwendige Logzeilen in Issues; niemals Stream-URLs mit Zugangsdaten, TMDB-API-Token, MACs oder Portalpasswörter veröffentlichen. 
**Codex beginnt auf HEAD von main, sperrt .90-Fallback gegen Cleanup und erstellt DRAFT-PRs. Keine Änderung an produktiven Online-Repository-Katalogen bis erneuter Freigabe.**
