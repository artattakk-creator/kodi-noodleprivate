# XCMate .69 – reproduzierbarer Testbericht

Master #315; Draft #316. Exakte endgültige Commit-, Testzahl-, Laufzeit-, ZIP-/SHA256- und Native-Ergebnisse stehen in **build-verification.json**, **test-results.log** und **native-evidence/** des CI-Testartefakts. Ein Artefakt wird erst nach erfolgreichen Host- und nativen Kodi-Jobs erstellt. Fehlgeschlagene/abgebrochene Zwischenläufe sind keine Abnahme.

## Prüfungen

- Gesamte unittest-Discovery; alle 2805 .68-Testmethoden und ihre Skip-Bedingungen bleiben erhalten, ergänzt um .69-Fälle. Historische Skips werden im Originaltestprotokoll ausgewiesen, nicht als ausgeführte PASS gezählt.
- .69: Reserve vs echtes ENOSPC, echter SQLite-Exclusive-Lock, echtes SQLite-FULL, unterschiedliche Lesedeadline, atomare Persistenz ohne Löschen, schreibfehlerbedingter Circuit, 18-fach-Deduplizierung, 667 Ereignisse, kontrollierte Nachpersistenz, Ablauf-/Quellen-/Profilbindung und private URL-Abwehr.
- .69 Return: positiver nativer Stop-ACK erforderlich, sichtbares Home, eigener hängender Directory-Zustand, fremde Modalebene/Verzeichnis/Fenster, neue Sitzung/Player, max. zwei Anfragen, Deadline, genaue Owner-Signale, Init-Ausnahme.
- .69 dynamische Providerreferenzen ohne GUI-SQL/Dateiöffnung, Portal-/Zugangstrennung, Ablauf und Unterdrücken generischer Kacheln.
- Vorhandene Live-TS/HLS/Auto-Decoderfälle, übrige native BINGIE-/Widget-/Helper-/Guide-/Medien-Verträge bleiben CI-Gates.
- Neues native pipeline69.json: zwei vorher ungespeicherte Ereignisse, PNG/JPEG, synthetische eigene-Token-Antworten, echter HTTPS-Preflight und Kodi-Texturabruf mit Zertifikats-/SNI-Prüfung, DB-Reserveblockade, RAM_ONLY, 18 Wiederholungen ohne erneutes Matching, echte Pixel in gemeinsamem Guide/Mini-Renderer, Hero und Detaildialog, kein neues XCMate-Bildarchiv, keine Auth-/Cookieheader am Bildhost. Screenshot- und JSON-Belege im Artefakt.
- ZIP: CRC, vollständige identische Quelldateien, Manifest, Icon/Fanart, keine privaten Profile/Logs/DBs, keine absoluten Pfade oder Symlinks; Repositoryindex wird nur im CI-Arbeitsverzeichnis gebaut. Kein Publish aus Draft-PR.

## Vorher/Nachher

benchmark_xcmate69.py lädt die unveränderte .68-Resolverdatei vom gepinnten Main-Commit und vergleicht denselben simulierten Schreibfehler mit .69. Kontrollierter Hostversuch mit 2-ms-Suchantwort, kein Geräteleistungstest:

| Messung | .68 | .69 |
|---|---:|---:|
| Anfragen derselben Identität | 18 | 18 |
| Matching-Aufrufe | 18 | 1 |
| erfolglose Metadaten-Publikationen | 18 | 1 |
| Ausgabe nach Schreibfehler | PROGRAMME_DB_UNAVAILABLE | READY + RAM_ONLY + Speichergrund |

Ein erster grüner Lauf maß 46,364 ms gesamt / 2,520 ms Median (.68), 4,725 ms gesamt / 0,084 ms Median (.69). Die endgültigen Messwerte stehen in xcmate69-host-evidence.json; synthetische Hostwerte sind keine Behauptung über die Android-Startzeit. Die bisherige unveränderte .66-Kalt-/Warmmessung liefert zusätzliche lokale EPG-Abdeckung. Neue Android-Kalt-/Warmzeiten, CPU-/I/O-Last und tatsächliche Widget-Neuladungen bleiben NOT_TESTED.

## Issue-/Abnahmematrix

| Bereich | Implementierung | Host-/Linux-Beleg | Android |
|---|---|---|---|
| #315/#313 Reserve, DB, Wiederholungen | klassifiziert, Circuit, RAM, atomare Recovery | neue Kapazitäts-/Sessionfälle, Gesamt-CI | NOT_TESTED |
| #315/#313 gemeinsame URL-Bilder | Guide/Mini/Details/Hero, optionales Archiv | Sicherheitsfälle + native HTTPS-Pixel | NOT_TESTED |
| eigener echter TMDB-Zugang | vorhanden erhalten, Produktionsresolver verwendet ihn | API-Antworten im Native-Test synthetisch | NOT_TESTED; echter Token nicht hier zugänglich |
| XMLTV/Provider/TVmaze | vorhandene konservative Quellen im einen Resolver | kumulative Quellen-/Matching-Tests | NOT_TESTED |
| Home-Providerposter/Performance | Vorabworker, DB-unabhängige Referenzen, keine generischen Kacheln | Property-/Sicherheitsfälle, native kumulative Darstellung | NOT_TESTED |
| #307 Rückkehr nach Stop | begrenzte ACK-/Session-/Owner-sichere Recovery | Return-Regressionen; nativer Decoder unverändert | NOT_TESTED |
| großer/kleiner Detaildialog | Owner und Init-/Lesetimeoutschutz | Owner-/Dialogfälle und native Details | NOT_TESTED |
| Profile/EPG/Cover/Resume/Widgets | keine Migration/Löschung/Routenänderung | Quellinventar + alle Altmethoden + Regressionen | NOT_TESTED |
| Kodi-AAC-/Fremdrepo-Startfehler | separat diagnostiziert | kein XCMate-Ursachennachweis | OFFEN, kein Fremdpatch |

Keine Issue-Schließung oder Geräte-Erfolgsmeldung aus Hosttests ableiten. Androidplan: ANDROID_ABNAHME_02969_DE.md. Ursachen: URSACHENANALYSE_02969_DE.md.
