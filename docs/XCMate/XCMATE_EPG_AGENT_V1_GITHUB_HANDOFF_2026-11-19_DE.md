# XCMate EPG-Agent V1 – GitHub-only-Implementierung (19.11.2026)

## Beschlossene Architektur

- Ausschließlich GitHub: kein gs-media.eu, kein Joomla, kein eigener EPG-Proxy.
- Keine manuelle Eingabe langer GitHub-Lesetokens durch Kunden bei Installation oder Aktivierung.
- Ein genau auf das dedizierte, separate Ausgaberepository beschränkter Fine-grained PAT (Contents: Read-only) wird bei einem privaten Installer-/ZIP-Build aus einem geschützten Build-Secret injiziert. **Kein Token im Git-Quellcode oder Git-Historie.**
- Sicherheitsgrenze: Ein Token im ausgelieferten ZIP ist jederzeit extrahierbar. Daher enthält das Ausgaberepository ausschließlich für den gesamten Kundenkreis freigegebene, rechtmäßig auslieferbare EPG-Artefakte; niemals private Providerzugänge, Rohfeeds, Nutzerdaten, Gerätekataloge oder Schreibzugänge. Tokenrotation/Widerruf einplanen.
- XCMate-Nutzer schalten den optionalen EPG-Agenten mit genau einem Schalter ein; Anbieter-EPG bleibt unabhängig verfügbar.

## Abgerufene GitHub-Projektstände

| Projekt | Zustand |
| --- | --- |
| Backend: artattakk-creator/xcmate-epg | Draft PR #7, Branch feat/full-epg-coverage-artwork-issue6; 1.278 Senderquelleneinträge, 185.945 gültige Sendungen, 9.566 mit TVMaze-Bildreferenzen |
| Backend-Tests | Actions #44410782253: 217 Offline-Tests PASS |
| TMDB-Sicherheits-/Live-Smoke | Actions #44210183373: TMDB authentifizierte Konfiguration, Filme/Serien und öffentlicher Posterabruf PASS; dies belegt nicht die Live-Anreicherung des Großexports |
| Private Auslieferung: artattakk-creator/xcmate-epg-private | GitHub bestätigt PRIVATE; synthetischer Upload/Readback Actions #44173864386 PASS; keine produktive XMLTV-Datei |
| Private EPG-API | manifest.json vorhanden, Status PRIVATE_PENDING, noch keine xcmate-epg.xml.gz |
| Kodi/XCMate | kodi-noodleprivate main, bestehende Stream-EPG-/Source-Mapping-Pipeline; PR #486 enthält nur Architekturentwurf |
| Installer | 0.5.27 RAW in Pilot/NeoDark3; Draft PR #491, keine Kodi-22-Geräteabnahme |
| Andere Tokenfunktionen | Draft #418 (TMDB-Pairing), #428 (TMDB GitHub/Drive-Import) sind NICHT identisch mit dem EPG-GitHub-Lesetoken |

Der private Drive-V2-Checkpoint ist bereits vollständig hochgeladen und zurückgeprüft: 26 Teile, 640.688.709 Bytes, SHA256 9babecb7ce7fccb33d16636a64bf8a0d6a36fd155ce254d483fd32762449ecb2, 964 Payload-Dateien, 10 SQLite-Datenbanken. Ein Restore im neuen Arbeitsbereich ist noch nicht belegt. Die vollständige Provider-Kanal-ID-Liste fehlt dort; 0 Feed-Zuordnungen sind bestätigt.

## Feste Endpunkte (ab sofort in XCMate verwendbar)

Manifest:
https://api.github.com/repos/artattakk-creator/xcmate-epg-private/contents/manifest.json

XMLTV-GZIP nach QA:
https://api.github.com/repos/artattakk-creator/xcmate-epg-private/contents/xcmate-epg.xml.gz

Prüfsumme nach QA:
https://api.github.com/repos/artattakk-creator/xcmate-epg-private/contents/xcmate-epg.xml.gz.sha256

Aufruf via HTTPS mit Authorization: Bearer [read-only PAT] und Accept: application/vnd.github.raw+json. Niemals Token in URL, XMLTV, Logs oder Manifest. Redirects mit Autorisierung nicht unkontrolliert verfolgen.

Manifest ist real bereits vorhanden:
{
  "schema_version": 1,
  "status": "PRIVATE_PENDING",
  "file": "xcmate-epg.xml.gz",
  "reason_code": "PRODUCTION_DATA_NOT_APPROVED"
}

PRIVATE_PENDING bedeutet: keine neue EPG-Datei verfügbar, Kodi-Provider-EPG nicht verändern. PRIVATE_READY ist erst erlaubt, wenn echte gzip/XMLTV, SHA, Zuordnungen, Rechte und Auslieferung geprüft sind. Bei READY: bytes, sha256, channel_count, programme_count, generated_at_utc erforderlich. Daten zuerst hochladen und authentifiziert zurücklesen, Manifest zuletzt ändern.

**P0-Schemaabweichung:** Backend xcmate_epg/full_export.py erzeugt intern schema_version 2 und Status PARTIAL_COVERAGE. Der geschützte Liefervertrag erwartet schema_version 1, PRIVATE_PENDING oder PRIVATE_READY. Publisher muss nach QA ein eigenes schema-1-Delivery-Manifest erzeugen. Rohes Backend-Manifest nie direkt als fertiges Liefermanifest ausgeben.

## Bereits implementierter erster Clientbaustein in diesem Featurebranch

- src/plugin.video.xtreammate/resources/lib/epg_agent_github_v1.py: privater GitHub-Manifest-/GZIP-Reader, Header-Auth, geprüfte SHA256, begrenzte Größen, GZIP-XMLTV-Prüfung, versionierter atomarer LastGood-Cache; bei PRIVATE_PENDING, HTTP-, Token- oder Datei-Fehler keinerlei Veränderung an Kodi.
- tests/test_xcmate_epg_agent_github_v1.py: 11 isolierte Transport-/LastGood-/Fehler-/Pakettoken-Tests.
- Für den privaten Paketbau wird optional resources/epg-agent-read-token.txt vorgesehen. Diese Datei darf NUR in einer kontrolliert verteilten ZIP landen, niemals im Quellrepository. Wer die ZIP erhält, kann sie auslesen.
- **Nicht behaupten:** Das Modul ist noch nicht mit UI, Kodi-EPG-Streaming-Importer, BINGIE-Sidecar oder einer tatsächlichen Produktionsdatei verbunden.

## Exakte Kodi-Integrationspunkte für Codex

1. src/plugin.video.xtreammate/resources/settings.xml Kategorie 36002: neuer Schalter epg_agent_enabled_v1 (AUS ab Werk); Status/Diagnose ohne Tokenwert.
2. src/plugin.video.xtreammate/service.py: bestehender Hintergrund-EPG-Worker soll bei opt-in nur das Manifest abrufen; keine blockierenden Anfragen auf GUI-Thread.
3. src/plugin.video.xtreammate/resources/lib/stream_epg.py: vorhandenen source_stream → import_source → staged SQLite → publish_stages44 nutzen. Über epg_sources.configuration(portal_id) bei aktiviertem Agent nur eine zusätzliche intern benannte, lokale EPG-Dateiquelle bereitstellen; niemals Quellen- oder Mapping-Dateien überschreiben.
4. epg_sources.py und epg_binding48.py: Source-IDs qualifizieren, manuelle Senderzuordnungen bleiben prioritär; leeres Geräteprofil niemals als fertigen Import darstellen. Provider-EPG bleibt Basis und Fallback.
5. Der tatsächliche SHA muss vor dem Import stimmen; bei unverändertem Manifest kein unnötiger Vollimport. Token fehlt: CREDENTIAL_PENDING, kein Abbruch des restlichen Players.
6. GS Media Installer: ein gesonderter privater Build-Schritt liest den EPG-PAT aus Build-Secrets, schreibt nur in die final freigegebene ZIP die Datei resources/epg-agent-read-token.txt, berechnet neue SHA256, meldet Kennzeichnung, prüft Tokenscope und keine Tokenwerte in Logs. Kein Token-Publikationsschritt in normalen GitHub-Pages-Pilot oder ungesicherte Artefakte.
7. Artwork-Vertrag aus xcmate-epg/docs/BINGIE_ARTWORK_VERTRAG_2026-11-18_DE.md beachten. Erststufe XMLTV-Sendungs-Icons; getrenntes Poster-/Backdrop-/Episodenstill-Sidecar folgt für Hero, Detail und Widgets. Kein Freischalten der Bilder gegen Opt-out.
8. Gerätetests Android 21.3 und LG webOS 22: echte Sender-ID-Matches, sichtbare Mini-/Groß-EPG-Bilder, LastGood/Provider-Fallback, BINGIE, zwei Kaltstarts.

## Blocker vor dem ersten echten Live-EPG

- Neuer privater Arbeitsbereich muss die geprüfte Drive-Sicherung wiederherstellen und den vollständigen Providerkatalog erhalten.
- Feed↔Provider-ID-Matching (derzeit 0 bestätigt) und unabhängiger Artwork-Identitätsaudit fehlen.
- Erster realer Export + Lizenz-/Weitergaberechtecheck + private Lieferung/Readback + PRIVATE_READY stehen aus.
- Einmalige Einrichtung eines **nur lesenden, auf das EPG-Ausgaberepository begrenzten GitHub-Token** in einem geschützten Build-Secret durch den Eigentümer. Es darf nicht mit einem TMDB-Token verwechselt werden.
- Kodi-Worker/UI-/Import-Anbindung, Installer-Paketbau und echte Geräteabnahme fehlen.

**Freigabegrenze:** Kein Merge, kein Installer-Pilot-Release mit Token, keine öffentliche EPG-Datei, kein 24-Stunden-Scheduler, keine Behauptung produktiver Funktionsfähigkeit ohne explizite Geräteabnahme. Die veröffentlichte 0.5.27 RAW sowie 0.5.26 bleiben unverändert.
