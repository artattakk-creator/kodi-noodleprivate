# XCMate EPG Agent – verbindlicher V1-Vollumfang und GitHub-only-Auslieferung

**Stand:** 19.11.2026 | **Status:** Vollumfang beauftragt, Abnahme nicht erreicht; KEINE vorzeitige Test-/Pilot-Veröffentlichung.

## Nutzerentscheidung

**Kein Demo-/Teil-EPG, keine Auswahl weniger Sender, keine abgespeckte Bilderstrecke, keine vorzeitige Umschaltung.** Erste für den Nutzer installierbare Agent-Version erst, wenn der vollständige private EPG-Datenbestand verarbeitet, alle verfügbaren typisierten Bilder eingebunden, Senderlogos mit verifizierter Herkunft versehen und der tatsächliche lokale Nutzer-Senderkatalog klassifiziert/zugeordnet sind. Bereits funktionierende Anbieter-EPG-Daten und lokale TMDB-/TVMaze-Bilder auf LG Kodi 22 dürfen nicht verloren gehen. Kein zusätzlicher Webserver; GitHub-only.

**Vollständigkeit bedeutet 100 % der vorhandenen und zulässigen Quell-Einträge in der Pipeline, nicht 100 % Bildtreffer oder das Erfinden nicht vorhandener Kanal-IDs.** Jede Nichtzuordnung muss transparent nach Quelle und Grund klassifiziert werden. Keine stille Reduzierung der Datenmenge zur Verbesserung der Abnahmequote. Alle Bilder/Bildtypen der belegten Treffer übernehmen, nicht nur 5 Beispiel-Poster. Kodi selbst lädt Bilder bei Sichtbarkeit nach und speichert höchstens fünf Hero-Assets dauerhaft.

## Gesicherte Datenbasis und aktuelle Risiken

- Privater Komplettimport von EPGShare01 DE, EPGShare01 AT, Kaimandura: **1.278 quellenqualifizierte Sender**, **185.945 gültige Sendungen**, private XMLTV-GZIP **17.411.748 Bytes**. Typisierte TVMaze-Bildreferenzen **23.528**, davon 9.554 Poster, 8.078 Backdrops, 5.896 Episodenbilder, in **9.566** Sendungsplätzen; TMDB-Such-API-Smoke grün, im *echten* Export noch TMDB_LIVE_PENDING. Artwork-Identitätsaudit noch nicht abgeschlossen.
- Der private Drive-Checkpoint vom 18.11. ist durch Readback verifiziert: **26 Teile, 640.688.709 Bytes, 964 Dateien, 10 SQLite-DBs**; **in neuem Arbeitsbereich noch nicht wiederhergestellt**.
- In der früheren privaten XCMate-Sicherung: **2.520 Live-Sender, 519 vorhandene Provider-EPG-IDs**. Provider-ID ist nicht gleich externe XMLTV-Quell-ID. Der gesamte Providerkatalog liegt bislang **nicht** im Agent-Workspace. **0 bestätigte Geräte↔Feed-Matches**, **0 exportierte Senderlogos** (88 lokale Logos liegen nur als geprüfte Kandidaten vor).
- Kodi-XCMate kann große XMLTV über die **streaming**-Pipeline \`xmltv_stream.py\` / \`stream_epg.py\` einlesen, aber die legacy In-Memory-Route hat \`MAX_PROGRAMMES=150000\`. Die vollständigen **185.945** dürfen deshalb **nicht** versehentlich in den Legacy-Parser geschickt werden. Kein hartes globales Limit im Streaming-Pfad, aber disk/time/memory-Monitoring und sichere Staging-/Rollback-Regeln.

## Fester privater GitHub-Auslieferungskanal (bereits reserviert)

- Repositorium \`artattakk-creator/xcmate-epg-private\` (Sichtbarkeit PRIVATE).
- Fest im XCMate-Client zu referenzierendes **Manifest**: \`https://api.github.com/repos/artattakk-creator/xcmate-epg-private/contents/manifest.json\`.
- Geplanter GZIP-Payload: \`https://api.github.com/repos/artattakk-creator/xcmate-epg-private/contents/xcmate-epg.xml.gz\`.
- Zusätzlich erforderlich: **versioniertes typisiertes Artwork-Sidecar** \`xcmate-artwork.jsonl.gz\`, gekoppelter SHA256/Generation im Manifest. Rollen: poster, backdrop/fanart, thumb/episode_still, verified channel_logo, Scope/Provider-/Identitätsnachweis und Attribution.
- \`manifest.json\` ist **tatsächlich angelegt** mit \`PRIVATE_PENDING\`, *noch keine* reale EPG-Datei und **keine** private Freigabe für einen produktiven Import. Das Manifest wird erst nach unveränderlicher Upload-Generation, Prüfsummen, Renderer-Vertrag und vollständiger Qualitätskontrolle auf \`PRIVATE_READY\` geändert.
- Anonyme HTTPS-GETs sollen 404 zurückliefern. GitHub Contents API über \`Authorization: Bearer\` mit eigenem **nur-lesenden Fine-grained PAT** auf ausschließlich \`xcmate-epg-private\`. Token ausschließlich per Header; nie Query, Git-Quellcode, Log, Crashreport oder öffentliches Workflow-Artifact.

## Token ohne Benutzer-Eingabe (explizite Produktentscheidung)

- **Kein gs-media.eu und keine Pflicht zum Tokenabtippen.** Installer/XCMate-ZIP soll den dedizierten Reader-Token *beim privaten/distributionsberechtigten Paketbau* automatisch bereitstellen; XCMate liest ihn aus einem festen Ressourcenpfad, nicht aus einer manuellen Einstellung.
- **Wichtige Sicherheitsrealität:** Ein eingebetteter Read-only-PAT ist aus jedem ausgelieferten ZIP auslesbar und gewährt Dritten vollständigen Lesezugriff auf **alle Inhalte dieses privaten Repositories**, solange er gültig ist. Daher niemals andere private Inhalte im Ausgaberepository speichern, nur für den Nutzer/die vereinbarte Empfängergruppe rechtlich freigegebene Daten, Repo-Scope maximal begrenzen, Ablauf/Widerruf/Rotation dokumentieren; öffentliche Pilot-ZIPs mit Token sind faktisch ein offener Zugang.
- Der konkrete Tokenwert existiert nicht als Chat-/Git-/Drive-Quellcodeparameter und wird hier **nicht** erstellt, angezeigt oder committed. Private Packaging-Strecke aus GitHub Actions Secret und nur in berechtigter Verteilumgebung. Keine allgemeine öffentliche Freigabe für tokenhaltige ZIPs ohne gesonderte Entscheidung.

## V1-Abnahme / Keine-PARTIAL-Auslieferung

1. **Backend:** alle drei vollständigen XMLTV-Quellen, korrekte Provenienz, Dedup, Zeitstempel, 185.945-orientierte Quellabdeckungsprüfung pro Stand; abweichende reale Quellzahlen transparent, kein heimliches Unterdrücken. \`gzip\`/XMLTV/Checksumme pass.
2. **Senderkatalog:** vollständige tatsächliche Kodi/Provider-Senderliste für den Testaccount verfügbar; exakte externe Sender-ID-Matches und sichere Aliaszuordnungen, manuelle Zuordnung erhalten; jede nicht belegbare Zuordnung einzeln als unmapped/ambiguous/fallback geführt, **0 bestätigte Matches blockieren V1**. Keine fremden EPG-Sendungen auf einen ähnlich benannten Kanal überschreiben.
3. **Artwork:** vollständiger BINGIE-Artr Rollenvertrag mit TMDB-Live-Anreicherung, TVMaze-Fallback, XMLTV-Bildern; Poster/Backdrops/Stills werden *als Referenzen* übertragen; Senderlogos nur nach belegtem Feed-Mapping. Fehlende einzelne Bilder sind erlaubt, werden aber gezählt und nie erfunden. Audit offen ⇒ V1 blockiert.
4. **Privater Publish:** XMLTV + Artwork-Sidecar + Version/Hash-/Größenmanifest atomar, \`PRIVATE_READY\` zuletzt; \`PRIVATE_PENDING\` bei Fehlern, LastGood erhalten; Rechte-/Lizenzprüfung einschließlich Weiterverteilung.
5. **XCMate:** \`Einstellungen → EPG → XCMate EPG Agent aktivieren\` (AUS ab Werk), automatischer Lese-Token aus privatem Paket, Manifestcheck, bei gleicher SHA keine 17-MB-Datei neu laden, bei geändertem Feed Hintergrund-Download, Byte-/GZIP-/XMLTV-/ID-/Sidecarprüfung und lokale Zuordnung. **Provider-EPG und existierende Bilder immer weiter verfügbar.** Erst nach erfolgreichem SQL-Staging atomar übernehmen. Bei Fehler/Offline: LastGood + Anbieter-EPG.
6. **Echte Geräteabnahme:** LG webOS/Kodi22 und Android/Kodi21 mit realen Sendern, 48-Komponenten-Installer-Kompatibilität nur falls erforderlich; funktionierender Mini-EPG, großes EPG, Live-TV, BINGIE-Hero/Poster/Details/Logos sowie Neustart/Offline/Token-Rotation/Unmapped-Fälle. Offline-/Hosttests ≠ Geräte-PASS.
7. **Go-live-Verbot bei Teilstand:** Kein V1-Release/NeoDark3-Pilotumschalten/produktiver Job, solange 1–6 nicht erfüllt. Keine unbegründete „100 % Bilder“-Behauptung, aber **100 % Datenbestand in der geprüften Verarbeitung**.

**GitHub-Arbeiten:** Backend Issue #6 / Draft-PR #7; Kodi Issue #485 / Design-PR #486; Installer 0.5.27 RAW ist davon getrennt.
