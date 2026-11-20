# XCMate 0.1.29.100 – EPG-Echtdaten-Test auf eigenen Geräten, 20.11.2026

**Status:** Direktabruf von drei originären Quellen testbar; privater zentraler GitHub-Agent weiterhin `PRIVATE_PENDING`. [P0-Umsetzungsauftrag #504](https://github.com/artattakk-creator/kodi-noodleprivate/issues/504), [Backend #14](https://github.com/artattakk-creator/xcmate-epg/issues/14). Keine ungeprüfte Neuauslieferung fremder EPG-Daten.

## Installierte Umgebung
- Android TV13 / Kodi21.3 mit Titan BINGIE MOD, danach LG webOS/Kodi22 ohne BINGIE.
- XCMate 0.1.29.100 aus GS Media Pilot oder NeoDark3 (verifizierte ZIP SHA256 `9fbea224f9417193b85f8b57a390653eb4d77aeff85196973f3520d51acb26de`).
- Vorher vorhandenes EPG, bestätigte Senderzuordnungen (SAT.1) und manuelle Artwork-Overrides sichern; **keine** DB-/App-Daten zurücksetzen.

## Fernbedienungs-Testablauf
1. In XCMate `Einstellungen → EPG` den **EPG-Manager** öffnen; Anbieter-EPG als Baseline belassen. Der **XCMate EPG Agent** (zentrale GitHub-Quelle) bleibt AUS, solange der Status `PRIVATE_PENDING` meldet.
2. `Zusätzliche Quellen hinzufügen → Deutschland / Österreich / Schweiz` öffnen und **einzeln** die Presets `Deutschland · Kaimandura Master`, `Deutschland · EPGShare01`, `Österreich · EPGShare01` aktivieren. Kein zusätzliches Schweiz-Paket erforderlich, nicht blind `DACH-Paket` (4 Quellen) wählen, wenn exakt drei zu prüfen sind.
3. **Nach jeder** einzelnen Quelle `Jetzt aktualisieren`, Ende abwarten; `Aktualisierungsbericht anzeigen`. Für jede Quelle tatsächliche Sender-/Programmzahlen und Match-/Readback zählen. Bei echter Fehler-/Quota-/Timeoutanzeige **keine** parallelen Wiederholungsimporte starten.
4. Mini-EPG, großes EPG, SAT.1 und Disney Channel (manuelle Zuordnung), Sendergruppenwechsel, Now/Next und belegte Sender-/Sendungsbilder testen. Speichern und **nach Kodi-Neustart** Readback prüfen. Provider-EPG darf auch bei Quellausfall nicht verschwinden.
5. Danach denselben Test auf dem LG mit Kodi22 (ohne BINGIE-Ansichten). Bei Fehlern `kodi.log` und `kodi.old.log` **privat** sichern und Ereigniszeit notieren. Keine Portal-URLs oder Zugangsdaten öffentlich posten.

## Bekannte Grenzen
- Der alte `epg_sources.py::merge_sources`-Pfad ist global auf `MAX_PROGRAMMES=150000` begrenzt, obwohl `xmltv_stream.py` SAX/Expat streamt. Daraus folgt **keine** bestätigte geräteseitige >185.000-Programme-Fähigkeit für **gleichzeitig** drei Quellen. Bei Budgetfehler einzelne Source separat prüfen und in #504 melden; nicht lediglich Budget konstant erhöhen, sondern Codex soll sichere SQLite-/Streaming-Stages integrieren.
- Erst bei vollständigen Nachweisen für Datennutzungsrechte, authentifizierte private GitHub-Auslieferung, aktuelle vollständige Daten und echten Kodi-READ darf das zentrale Manifest auf `PRIVATE_READY` gesetzt werden. Das testweise aktivierte Direkt-EPG ist **nicht** die produktive zentrale Agent-XMLTV-Datei.

QA: `DEVICE`, `SOURCE_ID`, `FETCH_STATUS`, `CHANNELS`, `PROGRAMMES_READ`, `PROGRAMMES_COMMITTED`, `STREAM_MATCHED`, `NOW_NEXT`, `IMAGE_READBACK`, `MANUAL_BINDING_REBOOT`, `PROVIDER_FALLBACK`, `LOG_TIME`. Nur verifizierte Messwerte, sonst `NOT_TESTED`.
