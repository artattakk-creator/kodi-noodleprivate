# XCMate .85 – Issue- und Abnahmematrix

Ein Draft-PR [#408](https://github.com/artattakk-creator/kodi-noodleprivate/pull/408), kumulativ auf veröffentlichtem .84/main. Keine automatische Issue-Schließung, kein Merge, keine Kanal-Veröffentlichung.

| Bereich | Codeumfang | Automatisierte Prüfung | Hardware / Rest |
|---|---|---|---|
| #401 – neuer eigener Bildcache | Byte-/Objektlimit, LRU/TTL/Pins, SHA256, Crash-Journal, begrenzte Metadaten | Hostfälle für Integrität, Abbruch/Wiederaufnahme, Fremddateien/Symlinks, Limits und Reservesperre | Physische RK3528-Kapazität und Persistenz bei realem Reservedruck ANDROID_NOT_TESTED |
| #401 – Speicherdiagnose | Aktuelle lokale Pfade, statvfs, Mounttyp, Gerätehash und tatsächliche Reserve; VFS-Ziele nicht automatisch testen | Schreibfreie lokale Prüfung; bestehende Speicher-/Migrationsregressionen | Keine Behauptung, dass ein anderer Android-Ordner einen anderen Pool bietet; externe/SMB-Tests nicht freigegeben |
| #401 – EPG / Revisionsstatus | Vorhandene gültige lokale Snapshots erhalten, Checkpoint-Schutz, getrennte Gründe, deduplizierter Retry/Backoff | Rollover, ungültige Datei, Quellen-/Policywechsel und Datenintegrität | Reales EPG auf Box B unter Speicher-/Netzstörung ANDROID_NOT_TESTED |
| #401 – Home / Cover | Bestehende Worker, sichtbare Fünfer-Priorität, Katalogmemo, ehrliche Ladezustände, semantische Reloads | Alte und neue Cover-/Widget-/Geometrie-/Fokusregressionen; native Linux-Gates separat im Testbericht | Alle tatsächlichen Android-Bilder, Ladezeiten, IR und 30-Minuten-Stabilität ANDROID_NOT_TESTED |
| #406 – Serienidentität | Begrenzte Seiten/Details, offizielle Aliase, Werkjahr/Land/IDs; Movie-Abgrenzung; TVMaze nach Zustimmung | Ghosts UK/US und geforderte Serien positiv/negativ, unvollständige Seiten, Opt-out | Produktive Quellenantworten und richtige sichtbare Box-B-Bilder ANDROID_NOT_TESTED |
| #406 – unbestätigte Vorschläge | Keine Episodenfakten; Poster klar unbestätigt; Weitergabe über echten Live-Verzeichnis- und A/B-Heropfad | Eigene DTO-/Puffer-/Rollover-Tests und native Sichtbarkeitsprüfung | Android-Hero/EPG-Details ANDROID_NOT_TESTED |
| #406 – manueller Manager | Kontext/Links, Kandidaten, ausdrückliches Bestätigen, Ändern/Automatik/Ausblenden; atomare private Werkzuordnung | Cold-Readback, Scope-Isolation, Fehlerspeicherung, falsches EPG-Jahr, Abbruch und eigener Exit | Reale Fernbedienung und bestätigte Persistenz nach Kodi-Neustart ANDROID_NOT_TESTED |
| Mini-EPG-Listenbild P1 | Bestehende Details erhalten | Bestehende Regressionen | Zusätzliches neues Eventbild direkt in der Liste weiterhin OPEN |
| Kodi-Library-Views | Keine automatische DB-Recreation | Bestehende nichtdestruktive Diagnose | Historische fehlende Views nicht als durch .85 repariert melden |
| Installer / bestehende Daten | 0.5.26 eingefroren; Routing/Player/Portale/Mappings/Favoriten/Resume/SkinShortcuts geschützt | Byte- und Regressionsschutz der .84-Basis und aller bisherigen Tests | Box A unverändert; keine Installation ausgeführt |
| Release | ZIP/SHA im Draft-Branch, alle drei .84-Kanäle eingefroren | ZIP-Reproduktion und Kanal-Schutzgates | Nutzerfreigabe für Merge/Veröffentlichung ausstehend |

**Bewertung:** Beide beauftragten Code-Arbeitspakete sind im Draft enthalten. #401 bleibt wegen echter Hardware-Speicher-/EPG-Befunde offen; #406 bleibt bis zur echten Bild-/IR-/Persistenzabnahme offen. Ein grüner Linux-Hosttest ist kein Android-PASS.
