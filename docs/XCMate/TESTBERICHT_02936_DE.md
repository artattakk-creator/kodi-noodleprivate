# XCMate .36 – neuer Gesamttest und Artwork-Testkandidat

Stand 25.10.2026 (Europe/Berlin). Regulärer PR **#163**, Basis main **138460b**, Paket-/Testquellen **ce5ad56**. Der alte .36-Head 656be1e, seine 1.214 Tests und SHA256 a7cd88… stammen **vor dem verbindlichen Artwork-Auftrag #168** und sind kein aktueller Liefernachweis.

**Neuer vollständiger Hostlauf: 1.250 PASS, 0 Fehler, 0 Fehlschläge, 131,86 s.** Darin alle bisherigen 1.214 Tests und **36 neue Artwork-Fälle**; insgesamt 94 neue Fälle gegenüber .35/1.156. Realer Dateisystem-/SQLite-/HTTP-/SMB-Testbetrieb und strikte Kodi-Omega-API-/Window-/Remote-/Player-Modelle, Artwork-Status unter 21.2-/21.3-Buildlabels. **Keine native Kodi- oder Android-Ausführung.** Box A/Kodi21.2 und Box B/Kodi21.3: alle S36-/GENRE-/ART36-Gates NOT_TESTED.

Neu zusätzlich geprüft: austauschbarer Artwork-Datei-/Capacity-Adapter im echten Downloadpfad, SHA256-Readback vor atomarer Veröffentlichung, URI-/Traversal-Abweisung, unbekannte Zielkapazität, unveränderte alte Pfade/Inventur und intern bleibende Jobdaten. **Keine USB-/SMB-Speicherortwahl in .36**; verbindliche vollständige Umsetzung/Migration #106 in .37. STOR-01 auf beiden Boxen NOT_TESTED.

Neu geprüft: Source-/cover_big-Erhalt, Persistenz unter Bildreserve bei weiterhin blockiertem Fetch, echte Metadaten-Reserve, Zielmount, BUDGET/RESERVE/ENOSPC, Worker-Liveness/Pause/Stop/Threadgrenze, Service-Datenloop, bestätigte Scancheckpoints und einmalige leere-Queue-Recovery, keine Altjob-/READY-Resets, Lease-Konkurrenz/Expiry, HTTP/DNS/TLS/429/Timeout/Bildvalidierung, read-only Status/Privacy/Staleness, Logo-Persistenz und UI/Search-Fokus bei wartendem HTTP.

Der Ende-zu-Ende-Hosttest lädt über einen **realen lokalen HTTP-Server sieben generierte PNG-Fixtures**: 3 Film-, 2 Serien-, 2 Logo-Dateien. Sieben Requests, sieben individuelle gültige Dateien/READY-Jobs, lokale Wiederverwendung nach Modul-Reload ohne neue Requests, native Coverreihen-Modellaktualisierung ohne Fokusverlust. Vorhandene READY-Zeile und Datei bytegleich erhalten. **Keine echten Providercover, kein Android-Display-PASS.** Zahlen/alte Fehlerreproduktion: [HOST_ARTWORK_MESSWERTE_02936.json](HOST_ARTWORK_MESSWERTE_02936.json).

| Prüfung | Aktuelles Ergebnis |
| --- | --- |
| Repository-Builder | PASS, ausschließlich Scratch-Checkout |
| PO de/en | PASS, jeweils **794 Kontexte** |
| Python compileall / ZIP-AST | PASS; unveränderte Vendor-SyntaxWarning im SMB-Code kein neuer Fehler |
| ZIP / Dateikatalog | **266 Dateien / 2.400.396 Bytes** |
| CRC / sichere eindeutige Pfade / Quellbytes | PASS |
| Reproduzierbare ZIP-Bytes | PASS |
| Datenbanken, Profile, Rohlogs, pycache im Paket | Keine |
| Such-/UI-/Lifecycle-Freeze / Theme | 163 Dateien und 98 Original-Theme-Bilder bytegleich |
| Weitere geschützte Quellpfade | 236 unverändert, 30 explizit geprüfte geänderte/neue Pfade |
| Artwork-DB-Schema/Locks/Backup/Repair | Unverändert; Status nur lesend; keine globale Job-/Policy-Neuinitialisierung |
| Bildreserve / Importreserve | Default **1.024 MiB unverändert** / separate **32 MiB** für Queue-Metadaten |
| Player/Renderer/Autoplay/Resume/Portale/EPG/Favoriten/Originalicon | Geschützt und Regressionen PASS |
| Funktionierende Main-Wizard-Komponenten | Bytegleich; keine #162-/Preview-Dateien übernommen |
| Downloads/Aufnahmen, produktive Indizes/Workflow/.35-ZIP | Unverändert |
| Fremde vorhandene lokale WIP-Dateien | 62 Hashes unverändert |
| Box-B-Kapazität/Provider-/Displayabnahme | **UNKNOWN / NOT_TESTED**, keine falschen Hardwarewerte |

Neues vollständiges Installationspaket: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.36.zip`.

```text
5dc73ef498641854b42b153a29e3f0fbbe9387638af4a633dfc321f44dec0e52  plugin.video.xtreammate-0.1.29.36.zip
```

Reproduktion aus leerem Scratch: `git archive HEAD | tar -x -C SCRATCH`, dort `python tools/build_repository.py`, `python tools/validate_kodi_po.py`, `python -m compileall -q src`, `python -m unittest discover -s tests -v`. Drei historische Noodle-Testpfade wie in CI auf `../src/plugin.video.noodleprivate` normalisieren; Abhängigkeiten gemäß unverändertem Publish-Workflow. Keine Fremd-Addon-Quellen im Arbeitsbranch ändern.

[Vollständiger erfolgreicher Testlog](TESTLOG_02936.txt) · [Maschinenbericht](TESTERGEBNISSE_02936.json) · [Dateikatalog](DATEIKATALOG_02936.json) · [Schutzprüfung](SCHUTZPRUEFUNG_02936.json) · [Ursachen/Messgrenzen](URSACHENANALYSE_02936_DE.md) · [Android ART36-01–08, S36, Genre und Baseline](ANDROID_ABNAHME_02936_DE.md) · [Issue-Abnahmematrix](ISSUE_MATRIX_02936_DE.md).

GitHub-CI muss diesen neuen Head erneut prüfen; Link und Ergebnis im Draft-PR. Publish-Schritt **SKIPPED**. Erst die reale 3/2/2-Android-Abnahme mit erhaltenem .35-Bestand erlaubt Geräte-PASS. Bei Reserve-/Hardwareblock genaue aktuelle Zahlen und BLOCKED dokumentieren; keine Sicherheitsreserve deaktivieren oder fehlende Quelle durch Placeholder-Erfolg ersetzen. Kein Merge, Release, Downgrade, Reset, Issue-Abschluss oder Installation durch Codex.
