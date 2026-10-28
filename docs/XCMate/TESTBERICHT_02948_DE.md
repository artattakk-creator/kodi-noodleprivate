# XCMate .48 – vollständiger Host-/Paketbericht

Datum: 28.10.2026. Basis `main` `.47`, `b047ffe7fc26a02f1ae74d99cb3546ce42735275`. Finaler Quellbuild: `3929968409aadbf7e9b2093f208ba89d9c860e76`. Derselbe vereinbarte Entwicklungsbranch; kein neuer Branch, Merge oder produktiver Release.

## Ergebnis

**2.021 Tests PASS in 293.247 s, 0 Fehler, 0 Failures, 0 übersprungene Tests.** Alle 1.952 bisherigen Testmethoden erhalten, 69 neue. Sauberer `git archive`-Checkout; unveränderte Bootstrap-/Buildschritte, PO-Validierung, Icon-/Lizenzprüfung und Python-Syntaxprüfung. Danach vollständige Tests mit freigegebenem Host-Loopback/SMB-Testnetz, synthetischen Daten und Kodi-API-Fixtures. Kein Kodi-/Android-Prozess und keine Nutzerbox wurde damit getestet.

Deutsch/Englisch: jeweils **1.078 gettext-Kontexte gültig**. **92 Original-Navigationstexturen** samt Herkunft/Lizenz gültig. Bekannte unveränderte `SMBProtocol.py`-SyntaxWarning im vendorten Modul; kein neuer Syntaxfehler. Testprotokoll `TESTLOG_02948.txt` vollständig; nur abschließende Zeilen-Leerzeichen normalisiert, beide Log-SHA256 in `TESTERGEBNISSE_02948.json`.

## Was die Tests belegen

- OS-Singleton auch über zweiten Prozess, Legacy-Modus unverändert; kalte automatische Vorbereitung zurückgestellt, explizite Jobs/Timer weiter bedienbar.
- Echter Xtream-Client mit einem Auth-Request, Discovery-Deadline/Retry-/Bytebudget, Cancel/Slot, verwaiste Wizardmarker, native Initgrenze, manuelle Directory-Fortsetzung ohne Root-Kreislauf und Schutz fremder Modals.
- Echte XMLTV-Datei durch Wizard Scan/Save: Source-Archiv, Quellrang, Kanalname, Bildadresse, Synopsis, Cast und Regie nach Veröffentlichung vorhanden; Rollback ausschließlich neuer ID; vorhandener ungesicherter Guide unverändert/blockiert.
- Gemeinsamer Now/Next-Resolver weist bei quellgebundenen Mappings fremde/unbelegte Cacheevents ab; vorbereitete Startdaten sind an die Mappingrevision gebunden und rollen Jetzt/Danach ohne Netzwerk in RAM fort. Race zwischen Vorbereitung und Mapping-Speichern veröffentlicht keinen falsch gestempelten Snapshot.
- Quellkollision mit identischer Kanal-ID, echte Rastervorschau ohne JSON-/Guideänderung, Cancel/Save, Legacy-Mappings, sichtbarer Button/Kontext und freie Zeitachse.
- Bildredirects mit öffentlicher DNS-/TLS-Prüfung, Hop-/Loop-/Downgrade-/Credential-/Privathost-Schutz; offline gespeicherte Originalbilder und reale Thumbnaildateien, kein Placeholder-PASS.
- Volle 88-Sender-Heroauswahl, kein Streamstart bei Fokus, exakter OK-Handoff; Artworkrotation über die erste 16er-Seite hinaus, XMLTV-Programmeicon statt Ratinglogo, dieselben Eventkeys zwischen Oberflächen.
- Home-/App-Exit getrennt, fremde Fenster/Player geschützt, kein zweiter Stop, abgeschlossener Live-Exit blockiert die Filmwidget-Aktualisierung nicht. Native `.42`-Engine bleibt bytegleich.
- Gesamter bisheriger Daten-/Player-/Autoplay-/Resume-/Suche-/Film-/Serien-/Großkatalog-/SQLite-/EPG-/SMB-/Navigationsbestand weiterhin getestet.

Frühere Arbeitsläufe waren keine Abnahme: Sie deckten u.a. notwendige exakte Freeze-/Versionsanpassungen, einen Scheduler-Fixturewechsel, einen mehrfach rekonstruierten Rich-DTO und einen verwaisten Wizardmarker auf. Diese Punkte sind im finalen sauberen Lauf enthalten. Socket-/SMB-Tests benötigen die passende Host-Netzfreigabe; ein entsprechend eingeschränkter Zwischenlauf war kein Produkt-PASS. Keine Testmethode wurde dafür entfernt oder neu übersprungen. Ein zusätzlicher Layoutfix plus Test verhindert die Überlagerung der EPG-Zeitachse durch den neuen Button.

## Paket

- `plugin.video.xtreammate-0.1.29.48.zip`
- **3,069,848 Bytes**, **565 Dateien**.
- SHA256: `1e835520da2a69127f72df0e4a6a799b232b3feb2852ac53f3f2c4c959004ce1`
- CRC, eindeutige/sichere Pfade, keine Symlinks, keine Benutzerprofile/DBs/Rohlogs/Bytecode: PASS.
- **Alle 565 enthaltenen Dateien bytegleich zum finalen Quellstand.** Unabhängige deterministische ZIP-Rekonstruktion mit eigenen ZipInfo-Einträgen ergibt exakt dieselben Bytes: PASS.

`DATEIKATALOG_02948.json`, `PAKETPRUEFUNG_02948.json` und `SCHUTZPRUEFUNG_02948.json` enthalten Prüfnachweise. 550 vorherige Quelldateien erhalten: **512 unverändert, 38 exakt überprüfte Änderungen, 15 additive Dateien, keine entfernte Datei**. Die 62 gesicherten fremden WIP-Dateien sind unverändert. Produktionsindex und alte Pakete bleiben im Branch unverändert.

## Messwerte, keine Android-Prognose

25 synthetische Hostmessungen je Version, frische Reader/Fixtures mit warmem OS-Cache (`PERFORMANCE_02948.json`):

| Messung | .47 p50 / p95 | .48 p50 / p95 |
|---|---:|---:|
| 88 Live-Elemente aus lokalem Bestand publizieren | 55,176 / 61,267 ms | 59,477 / 71,782 ms |
| 24 Filme aus 60.000 Titeln lesen | 0,819 / 1,097 ms | 0,770 / 1,019 ms |
| SQLite-Verbindungen Livepublikation | 31 / 31 | 31 / 31 |

Live-Publikation hat mit zusätzlichen verifizierten Metadaten hier einen kleinen Mehrbedarf; die Filmwerte liegen nah beieinander. Das ist **kein** Nachweis einer verbesserten realen 180-Sekunden-Kaltstartzeit und kein Fokus-/IR-Benchmark. Deterministisch geändert: Auth-Requests **2→1**, Discovery keine Retries/kurze endliche Budgets, Maintenanceintervall **5→300 s** und automatische schwere Arbeit nach der Startphase. Echte Cold/Warm-/First-correct-/Scroll-p50/p95 bleiben NOT_TESTED.

## CI und Gerätefreigabe

GitHub Actions baut den PR unabhängig neu, führt denselben vollständigen Bestand aus, prüft Paket/Quellbytes und stellt das Testartefakt mit berechnetem ZIP-SHA256 bereit. **Der genaue CI-Run und Ergebnis für den Liefer-HEAD werden im Draft-PR geführt**, damit keine nachträgliche Dokumentationsänderung einen rekursiv neuen CI-Stand erzeugt. Produktiver Commit-/Publish-Schritt muss beim PR übersprungen sein. Merge/Release bleibt ausdrücklich gesperrt.

Android: **49 benannte Fälle NOT_TESTED**, zwei klar blockierte Gates (BINGIE-Skinintegration und reale 7-Tage-Historie). Keine aktuelle native Crash-/ANR-Ursache bewiesen; Kodi-Startcrash und langfristiger Live-Hänger sind trotz Add-on-Korrekturen **nicht als real repariert abgenommen**. Keine Rohlogs veröffentlicht. Box A unverändert. Testreihenfolge und Grenzen in `ANDROID_ABNAHME_02948_DE.md`, Details in `URSACHENANALYSE_02948_DE.md` und `ISSUE_MATRIX_02948_DE.md`.
