# XCMate 0.1.29.25 – Benutzer-Abnahme Lightweight (23.10.2026)

**Quelle:** unmittelbare reale Rückmeldung des Nutzers von der Android-TV-Box, **nicht** CI oder Simulation. **Version:** XCMate 0.1.29.25. **Umfang:** ausschließlich Lightweight, kein Test des optionalen Space Premium, dessen Grafiken, Fokus oder Umstellung. Kodi 21.2 Omega / Android 13 ARM32 / Titan BINGIE MOD; genaue Testuhrzeiten nicht vorgelegt.

**Ergebnis:** **23 PASS, 3 FAIL, 1 NOT_TESTED (27 Tests)**. PASS-Quote 23/27 = 85,2 %. Angaben sind als **Einzeltest-Nutzerabnahme** und **nur für den beschriebenen Umfang** zu verstehen, nicht als Gesamtfreigabe oder automatische Erledigung aller verknüpften Issues.

## Vollständiges Ergebnis nach Original-Test-IDs

| ID | Verifizierter Prüfbereich | Status | GitHub-Bezug |
|---|---|---|---|
| B01 | Update auf 0.1.29.25 | **PASS** | PR #116 |
| B02 | Datenbestand Portale/Groups/EPG/Favoriten/Resume | **PASS** | Bestandsregression |
| B03 | Original-XCMate-Icon | **PASS** | #37 |
| B04 | XCMate-Hauptmenü / Back | **PASS** | #59 |
| M01 | Lightweight-Filmübersicht: sichtbarer Fokus | **PASS** | #115 (nur Lightweight) |
| M02 | Filmdetail: OK aktiviert fokussierte Aktion | **PASS** | #115 (nur Lightweight) |
| M03 | Detailaktionen/Favoriten | **PASS** | #115, #111 (nur UI-Teil) |
| M04 | Film-/Seriensuche | **FAIL** | #115 |
| M05 | Serien/Staffeln/Episoden | **PASS** | #115 (nur Lightweight) |
| M06 | Rückkehr nach Film/Episode | **PASS** | #79, #115 (nur Lightweight) |
| M07 | Datei-/Ordnerauswahl | **NOT_TESTED** | #115 |
| P01 | Filmwiedergabe/Resume | **PASS** | #79 |
| P02 | Autoplay nächste Episode derselben Staffel | **PASS** | #85 (Teilabnahme; Staffelübergang B02 offen) |
| P03 | Stop beendet Serien-Autoplay | **PASS** | #85 (Teilabnahme) |
| P04 | VOD-OSD/Player-Bedienleiste | **PASS** | #79 |
| P05 | Live-TV IR Startsender/Overlay/Senderwechsel | **PASS** | Live-Regression |
| E01 | EPG konfig. Startgruppe/Startsender | **PASS** | #88 |
| E02 | Großes EPG Raster-Fokus und Sendungstitel | **PASS** | #57, #92 |
| E03 | EPG Kopfbuttons per IR | **PASS** | #92 |
| E04 | EPG Gruppenwahl | **PASS** | #88 |
| E05 | EPG OK-Menü und Senderstart | **PASS** | #57, #88 |
| E06 | Keine doppelten EPG-Einträge | **PASS** | #58 (sichtbarer Stichprobentest) |
| E07 | EPG Daten/Quellenstatus | **PASS** | #60 (Teilabnahme; keine erneute Coverage-Messung) |
| A01 | Poster nach Scrollen/Back/Neustart dauerhaft | **PASS** | #41 (Teilabnahme) |
| A02 | Posterdiagnose/fehlendes Bild | **FAIL** | #111 (Timeout konkret; Download nicht erfolgreich) |
| A03 | Manueller einzelner Poster-Retry | **FAIL** | #111 (erneuter Timeout) |
| A04 | Artwork-Status und Fehlertrennung | **PASS** | #90, #111 (nur Diagnostik) |

## Konkrete offene Probleme

### M04 – Film-/Seriensuche: FAIL

**Nutzer-Nachtrag 23.10.2026 – P0:** Die Suchmaske öffnet sich in **Lightweight** ordnungsgemäß. Nach Eingabe des Beispiels **`Upload`** und Bestätigung mit **OK** erscheint **keine** Suchergebnisansicht; stattdessen springt XCMate kurz auf die Plugin-Startseite und anschließend **stürzt der gesamte Kodi-Prozess ab/beendet sich**. Das ist ein **reproduzierbarer Kodi-Crash**, kein bloß falsches Suchlayout. Eigenständiges [P0-Issue #118](https://github.com/artattakk-creator/kodi-noodleprivate/issues/118) zur Absturzbehebung eröffnet. Der ursprünglich gewünschte, separat bedienbare **globalen Suchergebnis-Bildschirm mit LIVE-TV / FILME / SERIEN**, echten Trefferzahlen und korrekten Detail-/Player-Aktionen ist in [#25](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25) weiter erfasst. **LIVE-TV soll auch EPG-Jetzt-Treffer („wo läuft das gerade?“) auf Sendern zeigen**, nicht nur nach Sendernamen suchen. Ungeklärt bleibt die technische Crash-Ursache: der vorhandene Übergang `media_window._search()` → `close()` → `open_media():Container.Update(global_search)` sowie Suchindex/GUI-Thread/Lifecycle muss mit Android-Log untersucht werden, nicht als gesicherte Ursache behaupten. M04 bleibt **FAIL**, Gesamtzählung weiter **23 PASS / 3 FAIL / 1 NOT_TESTED**; Space Premium bleibt vom Test ausgeschlossen.

### A02 – Posterdiagnose: FAIL, aber Fehlerklasse verbessert

Statt des früheren generischen „Netzwerkfehlers“ zeigt die Posterdiagnose jetzt **„Zeitüberschreitung“ (TIMEOUT)**. Die Darstellung einer spezifischeren Diagnose ist **positiv**, aber der Nutzer hat A02 **explizit als FAIL** gemeldet, weil das Poster weiterhin nicht abrufbar ist. **Nicht** heimlich in PASS umklassifizieren und keinen HTTP-, DNS- oder TMDB-Fehler unterstellen, für den keine Telemetrie vorliegt.

### A03 – Einzelposter-Retry: FAIL

Beim Antippen von **Posterstatus → erneut versuchen** öffnet sich eine Fortschritts-/Versuchsanzeige, aber das Bild wird nicht geladen. Danach erscheint **erneut „Zeitüberschreitung“**. UI-Button und Jobversuch arbeiten sichtbar, **End-to-End-Ergebnis FAIL**; Quelle/Origin/Transport und Timeout-Budget offen.

### M07 – Datei-/Ordnerauswahl: NOT_TESTED

Hier ist **kein** PASS/FAIL aus der aktuellen Lightweight-Abnahme ableitbar. Kodi-Systemfilepicker und Add-on-interne Listen getrennt beurteilen; Premium-Dateifenster sind vom gesamten Test explizit ausgeschlossen.

## Neues Ziel zu #111: gestufter Poster-Fallback mit TMDB

Im Code von 0.1.29.25 hat `media_art.py::poster_candidates(item)` bislang ausschließlich bereits im Anbieterdatensatz befindliche `cover`/`stream_icon`/`movie_image`/`cover_big`-URLs; `diagnose()` kann innerhalb dieser Kandidaten umschalten, `retry_poster()` wiederholt die ausgewählte URL. **Es gibt in diesem Pfad noch keinen eigenen TMDB-Lookup.**

**Benutzerwunsch:** Wenn die Anbieter-Posterquelle auch nach einem gezielten Retry nur TIMEOUT liefert, verlässlich eine alternative Quelle wie TMDB für das richtige Cover verwenden.

**Architektur-/Implementationsauftrag an Codex für nachfolgende Version (kein bereits implementiertes Feature):**
1. Nur bei **fehlenden** oder klar **ausgefallenen** Anbieterbildern und unter Kontrolle des Nutzers (explizite „Alternatives Cover suchen“-Aktion bzw. klar dokumentierte optionale Fallback-Einstellung) extern nachschlagen; kein TMDB-API-Fanout bei jeder Listennavigation.
2. Wenn vorhanden, eindeutige autoritative TMDB-ID aus erlaubten Anbieter-Metadaten verwenden; ansonsten Titel **plus Jahr plus Medienart** konservativ abgleichen. Mehrdeutige Treffer **nicht automatisch** als richtig abspeichern, sondern Kandidatenwahl/Preview anzeigen. Kein ungeprüftes Matching bei gleichnamigen Filmen/Remakes.
3. TMDB-API/Key-Nutzung, Nutzungsbedingungen, Bild-Attribution, Sprachvarianten und Datenschutz technisch klären; keine API-Secrets oder Abonnements ins Repo/Logs übernehmen. **Nicht** das installierte Kodi-TMDB-Helper-Add-on als garantiertes Datenzugangs-Backend voraussetzen.
4. Für tatsächlich gewähltes korrektes Bild: bestehenden sicheren Artifact-Worker verwenden, Herkunft TMDB/Provider für Diagnose anzeigen, identitätsgebundenes persistentes Mapping und Cache anlegen (keine Ersetzung der funktionierenden Original-Cover); offline aus bestehendem Cache weiter anzeigen.
5. DNS/Timeout/HTTP 4xx/429, Budget, DB_BUSY, A/B-Varianten und kein Treffer unterscheiden; begrenzte Backoff/Cooldown und 0 globaler Retry-Storm; öffentliche Logs niemals mit Session-URLs, Credentials oder ungeschützten Personendaten.
6. Durchgängige Tests: Anbieter TIMEOUT → eindeutiges passendes TMDB-Cover READY, uneindeutiger Titel → keine Fehlzuordnung, bereits READY Provider-Cover bleibt, erneutes Öffnen/Kodi-Neustart/offline behält Bild. **Android-Anwendertest erforderlich**, erst dann #111 schließen.

## Positive Teilabnahmen / keine unbelegten Vollfreigaben

- **Version/Daten/Original-Icon:** B01–B03 PASS.
- **Hauptmenü/Zurück:** B04 PASS für getestete Wege; #59 ggf. weiterhin weitere Grenzen prüfen.
- **Lightweight Medien:** M01/M02/M03/M05/M06 PASS; **M04 FAIL**, M07 nicht getestet; Space-Premium-Fokus bleibt separat in #115 offen.
- **Player:** P01–P05 alle PASS; Autoplay nächste **Folge derselben Staffel** und manueller Stop belegt, **Staffelübergreifender Wechsel B02 nicht getestet**.
- **Großes EPG:** E01–E07 sämtlich Nutzer-PASS im Testumfang. **Kein** impliziter Nachweis von #98 „EPG zuweisen“ mit Vorschau, Timeraufnahmen oder 10-Tage-Langzeittest sämtlicher Sender. Dedupe E06 als praktische sichtbare Prüfung, kein providerweiter mathematischer Beweis. E07 keine neue XMLTV-Quotenbestimmung.
- **Artwork:** A01/A04 PASS für Persistenz, Status/Diagnostik; **A02/A03 FAIL** für den echten Abruf. #41/#90 nicht aufgrund einzelner PASS als vollständig behoben deklarieren; Budget-/SPACE_FULL-Nacharbeiten separat.
- **Nicht Bestandteil .25:** Draft #117 native TS Engine, EPG-Aufnahmen/Timer #62, Meine Medien #113, VOD-Downloads #63 sowie Premium-Design und Premium-Artwork.

## Issue-Verwaltung

Resultate je Referenz-Issue als Android-Teilabnahme kommentieren, offene Restanforderungen belassen und **kein Issue allein wegen eines PASS schließen**, soweit sein ursprünglicher gesamter Definition-of-Done offen bleibt. Diese Datei ist die verbindliche Test-ID-Quelle. Keine Code-Änderungen oder Releases aufgrund dieses reinen Testberichts.
