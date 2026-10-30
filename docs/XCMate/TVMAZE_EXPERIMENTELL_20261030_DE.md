# XCMate – Experimenteller TVmaze-Adapter (30.10.2026)

**Implementierung im separaten Feature-Branch**, nicht in `main`, nicht als Version .58 freigegeben. Verfolgt in [#279](https://github.com/artattakk-creator/kodi-noodleprivate/issues/279). `A58`-P0-Reparaturen [#277](https://github.com/artattakk-creator/kodi-noodleprivate/issues/277) bleiben unabhängig.

## Funktion
- **Einstellungen → Experimentell (PIN) → TVmaze – Live-TV-Sendungsbilder**.
- Standard **deaktiviert**. Aktivierung/Deaktivierung verlangt eine bewusste Bestätigung; ohne Aktivierung **keine** TVmaze-Abfragen.
- Testmenü führt eine **lesende** API-Suche nach `Tatort` durch, ohne Sender-/EPG-Mapping und ohne Wiedergabestart.
- EPG-Bild-Worker prüft zuerst die bestehenden eindeutigen XMLTV-/Provider-Eventbilder und vorhandene erlaubte Quellen. TVmaze wird danach für eindeutig erkannte **TV-Serien/Episoden** berücksichtigt.
- Titel müssen eindeutig und exakt zum gefundenen Seriennamen passen. Bei Staffel und Folge wird `/shows/{id}/episodebynumber` geprüft; optionale Episodenuntertitel müssen übereinstimmen. Unklare Namen, widersprüchliche Folgen oder Bild-URLs führen **nicht** zu einem Bild.
- Gibt es kein Episodenfoto, darf nur ein ausdrücklich als **Serienbild** markiertes Bild der Serie dienen; kein falsches Episodenfoto.
- Ergebnisse verwenden denselben vorhandenen `programme_urls55`-/`programme_index46`-/`guide_v1.sqlite`-Pfad. **Keine zweite EPG-Datenbank.** Eingeschränkte, explizit erlaubte TVmaze-CDN-Pfade; kein HTTP, kein URL-Query oder Redirect bei der Bildanzeige.
- Der EPG-Text, der Sender und NOW/NEXT werden niemals von TVmaze ersetzt. Die Film-/Serien-VOD-Home-Widgets bleiben vollständig beim IPTV-Provider.
- TVmaze: https://www.tvmaze.com/api · CC BY-SA. Quellenlink pro Treffer, Bilderrechte Dritter zusätzlich beachten; keine unkontrollierte Metadaten-Neuveröffentlichung.
- Keine Token, kein Scraping, 10 Anfragen/10 Sekunden je Kodi-Prozess als konservatives Limit, HTTP 429 mit 60 Sekunden Cooldown. Fehlende Bilder sind zulässiger Fallback-Zustand.

## Geräte-Abnahme (noch offen / NOT_TESTED)
1. **Box B**: Über Experimentell die Option finden; Standardwert AUS prüfen; Test ohne Aktivierung darf nicht die API anfragen.
2. Aktivieren, `TVmaze-API mit Tatort testen` aufrufen. Die Suchergebnisse gelten allein als `API_REACHABLE`, **nicht** als Android-Bild-PASS.
3. Eine echte Serienfolge im EPG suchen, deren Sender-/Folgenidentität zweifelsfrei stimmt. Exakte Event-ID/Quelle prüfen; Bild mit TVmaze-Zuordnung im großen EPG und in der Sendungsvorschau prüfen.
4. Bei falschem Titel, fehlender Episode, gleichnamiger Serie und fehlendem Bild muss XCMate Senderlogo + EPG-Text weiter anzeigen.
5. Kodi neu starten und EPG-Bild-Cache/Quelle prüfen. TVmaze AUS schalten: keine weiteren Anfragen und keine Anzeige neuer TVmaze-Bilder.
6. Kontrollieren, dass Live-TV-Zurück, bestehende P0-BINGIE-Widgets, Portal-Einstellungen und Box A unverändert bleiben.
7. Kein `PASS_ANDROID` ohne echte Screenshot-/Log-Nachweise; Codex/CI-Mocks allein sind **NOT_TESTED**.

## Wartung
- API: `resources/lib/tvmaze59.py`; Experimentell UI: `tvmaze_ui59.py`.
- Workeranbindung: `programme_sources57.py`; Sicherheits-/Quellprüfung: `programme_urls55.py`; Cache-Fingerprint: `programme_art46.py`.
- Offline-Tests: `tests/test_xcmate_tvmaze_experimental_02959.py`.
- **Vor Integration:** Auf die neueste erfolgreiche `main`-Basis nach .58 rebasen, Konflikte mit Codex-Fixes prüfen, Regressionssuite und echte Android-Abnahme. Kein automatischer Merge; separate neue kumulative Version mit ZIP/SHA256.
