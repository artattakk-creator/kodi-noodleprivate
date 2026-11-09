# Codex-Folgeauftrag: XCMate 0.1.29.85 – „Ghosts“, sichere Serienerkennung und sichtbare Ladephasen

**Stand:** 09.11.2026 · **Status:** Recherche/Anforderung, KEINE Implementierung · **Vorgänger:** veröffentlichte .84 (PR #405) · **Hauptticket:** #406, Bezug #403.  
**Regel:** .84 ist öffentlich auf regulär/Pilot/NeoDark3; keine stillen Commits/Rebuilds unter .84. Für Fix neue Version .85 als eigener überprüfbarer PR, **noch kein automatischer Merge oder Release**.

## 1. Neu gemeldete echte Android-Beobachtungen (ohne neues Log)

- **Ghosts**: Bei geöffneten Sendungsdetails „Kein bestätigtes Sendungsbild; eigene TMDB-Suche nicht erfolgreich“, obwohl die Nutzer-TMDB-Websuche mehrere Bildserien kennt (Link: https://www.themoviedb.org/search?language=de-DE&query=ghosts). Nutzer vermutet, dass viele gleichnamige Werke eine Rolle spielen; schlägt obersten Treffer vor. **Nicht blind den höchstplatzierten Suchtreffer als richtige Serie übernehmen.**
- **Alarm für Cobra 11**: kein bestätigtes Bild.
- **Rosenheim Cops**: „Quell- oder Sendungsrevision hat sich geändert; kein fremdes Bild“; getrennt von „Ghosts“ behandeln.
- **Morden im Norden** laut naheliegender Werksbezeichnung (der Nutzer sprach zuvor „Morgen im Norden“): TMDB-Bild erfolgreich, positives Kontrollbeispiel. Den *tatsächlichen* EPG-Wortlaut vor Test festhalten.
- Vorherige Erfolge: `taff`, evtl. „Malcolm mittendrin“, Filme über Warner TV Film; Negativbeispiele `M*A*S*H`, `Modern Family`, `The Middle`, `King of Queens`.
- **UX-Muss beim Start:** Zuerst Senderleiste mit echten kleinen Senderlogos und großer Hero-Bereich; Hero sofort mit aktuell fokussiertem Senderlogo oder sauberem neutralem Platzhalter + EPG Jetzt/Danach/Progress, danach asynchron exakt richtiges Eventbild. Darunter Film- und Serienzeilen sofort strukturell vorhanden; **sichtbarer, dezenter Ladezustand** („Filme werden geladen …“, „Serien werden geladen …“) bis zum tatsächlichen Katalog-/Artworkstatus. Kein langes leeres Feld, keine irreführenden Play-Platzhalter, kein blockierender Dialog. Echte Cover schrittweise einblenden.
- **Mini-EPG** weiterhin ohne Eventbilder (gesonderter #406-Anteil, nicht als neuer TMDB-Ausfall missdeuten).
- Weitere private Kodi-Logs wurden angekündigt, **liegen zu dieser Beobachtung noch nicht vor**. Keine Live-Geräte-Ergebnisse oder Root-Cause aus erfundenen Logdaten ableiten.

## 2. „Ghosts“ – kontrollierte externe Identitätsprüfung

Mindestens zwei **real unterschiedliche Serien** tragen denselben Titel:
- `Ghosts` **UK (BBC, 2019)**: Alison/Mike, UK, TVmaze `shows/38241/ghosts`.
- `Ghosts` **USA (CBS, 2021)**: Samantha/Jay, US, TVmaze `shows/46573/ghosts`; amerikanische Fassung lief u.a. auf **Comedy Central Deutschland**. Die korrekte Werkidentität für das *konkret gewählte Kodi-Event* hängt vom tatsächlichen Sender, EPG-Text, Sendungs-/Staffel-/Folgeninformationen ab.

Quelle: https://www.tvmaze.com/shows/38241/ghosts und https://www.tvmaze.com/shows/46573/ghosts ; TMDB offiziell https://developer.themoviedb.org/reference/search-tv . Die TMDB-Website-Suchseite konnte hier **nicht als vollständige Live-Trefferliste inklusive Rangfolge ausgelesen werden**; bei Box-Test API-Response und Seitenzahl nur privat, redigierte Gründe ins GH.

**Verifizierter Quellcode-Engpass der veröffentlichten .84, `programme_tv66.py`:**
- `complete84(data)` akzeptiert `total_pages` nur `0|1` (je nach `empty`), `total_results==len(first_page.results)` und `len<=20`. **Wenn mehr als eine Resultatseite existiert, wird selbst eine später eindeutig identifizierbare Serie ohne tieferen Kandidatenabgleich verworfen.** Mehrseitigkeit und echte Mehrdeutigkeit als unterschiedliche Gründe instrumentieren.
- Nach Normalisierung `matches` ohne EPG-`year` können **mehrere exakte Ghosts-Titel** übrig bleiben. Dann korrekt `NO_MATCH_AMBIGUOUS` statt erster Treffer. **Das ist ein berechtigter Schutz, aber es fehlt die verlässliche Auflösungsschicht.**
- `programme_tvmaze67.py` macht eine eigene strikte Titel-/Trefferzahl-Prüfung und benötigt Freigabe/Setting. TVMaze nicht heimlich aktivieren; wenn erlaubt als zusätzliche Quelle nutzen.
- Bei leerer/fehlender EPG-Jahresangabe sollten zusätzliche **bereits vorhandene vertrauenswürdige Fakten** benutzt werden: Produktionsjahr/Erstausstrahlung (nicht EPG-Ausstrahlungsdatum!), Land, Originalsprache, verifizierte Sender-/Programminfo, Staffel/Episodentitel, Beschreibung (UK Alison/Mike vs. US Samantha/Jay), Provider-IDs/externe IDs. Kein bloßer TV-Senderbeweis, wenn derselbe Kanal beide Versionen ausstrahlen könnte.
- TV / Movie-Unterscheidung vornehmen. Bei unklaren Angaben **keine willkürliche Auswahl nach TMDB-Ranking, Popularität oder erster Position**.
- Wenn mehrere authentisch mögliche Serien übrig bleiben: **manuelle einmalige Zuordnung im EPG-Kontextmenü bzw. Details**: wenige geprüfte Kandidaten mit Jahr/Land/kurzer Inhaltsangabe/Kleinstbild, Auswahl explizit durch Nutzer, dann persistente **profil-/quellen-/werksgebundene** Wahl; widerrufbar/änderbar, nicht an bloßen aktuellen Eventstart gebunden. Niemals unbemerkt auf anderes Konto/Kanal/Event übertragen. Keine Secrets/Kodi-DBs in öffentlicher Doku.
- Bei fehlender Freigabe oder weiterhin unklar: schnelles **Senderlogo im Hero** erhalten; `Kein eindeutiges Serienbild` nur in optionalem Diagnosemodus, keine fremde Illustration.
- Suchstrategie: `/search/tv` mit `language=de-DE`, ggf. `first_air_date_year` bei verlässlich bekanntem Werkjahr. Begrenzte Paginierung (z.B. höchstens drei Seiten / 60 Kandidaten, dann bewusster `SEARCH_INCOMPLETE`), harte Timeouts und Rate-Limits. Kein unbegrenztes Scraping. Kandidaten durch `/tv/{id}` und falls notwendig `alternative_titles` oder `/find` mit vertrauenswürdiger externer ID unabhängig verifizieren. Cache Serien-Werkidentität/Art-Referenz zentral statt jede Ausstrahlung wieder neu aufzulösen; wenige kleine Referenzdatensätze, keine massenhaften Image-Dateien.
- Feste anonymisierte Diagnose getrennt: `TV_SEARCH_MULTIPAGE`, `TV_MULTIPLE_EXACT_TITLES`, `TV_IDENTITY_INSUFFICIENT`, `TV_ALIAS_REJECTED`, `TV_USER_MAPPING_REQUIRED`, `TV_MATCH_EXACT`, `TV_ART_PATH_MISSING`, `TV_IMAGE_DECODED`, `TV_GUI_TEXTURE_REQUESTED`, `TV_VISIBLE`; keinen `VISIBLE`-PASS ohne Native-Hardwarebeleg.

## 3. Weitere konkrete Serien-Fälle: Alias vs. Revision

**Alarm für Cobra 11:** Der offizielle vollständige Serientitel lautet „Alarm für Cobra 11 – Die Autobahnpolizei“ (RTL+), Beginn 1996. Bei EPG-`Alarm für Cobra 11` ist abgekürzter Name plausibel, aber nur mit unabhängigem offiziellen Alias-/Werks-/Jahres-/Beschreibung-/Provider-Nachweis zuzuordnen, nicht per blindem Substring. Quelle: https://plus.rtl.de/alarm-fur-cobra-11-die-autobahnpolizei-p_7968 .

**Rosenheim-Cops:** Offizieller Haupttitel „Die Rosenheim-Cops“, deutsche Serie ab 2002. Der Nutzer sagt „Rosenheim Cops“ – Artikel und Bindestrich können bei exakter Titelprüfung abweichen. Jedoch konkrete Meldung ist **CACHE_MISMATCH**, nicht notwendigerweise Titel-Mismatch. Zuerst `programme_lastgood80.choose()` (`FILE_INVALID` kann ebenfalls `CACHE_MISMATCH` setzen), `programme_urls55.binding()`, `programme_art46.fingerprint()`, `programme_requests68.identity()` und `epg_handoff63` prüfen; Rev/Source/Hash/Expiry strikt trennen und anschließend sauber **neue, aktuelle** Referenz asynchron suchen. Den alten nicht zugelassenen Bildbeleg nicht wiederverwenden. Quellen: https://www.fernsehserien.de/die-rosenheim-cops .

**Weitere Testfälle:** `M*A*S*H` inklusive Punkte/Asterisken (gegen TMDB-/TVmaze-offizielle Alternativtitel), `Modern Family` Revisionswechsel; Positivkontrollen `taff`, `Morden im Norden` und mehrere Warner-TV-Filme zu späterer EPG-Zeit. Weder EPG-Texte verändern noch falsche Episodenstills erfinden.

## 4. Startseite und gestufte Darstellung: verbindliche Zustandsmaschine

Aktueller `home_schedule75.py` besitzt intern Phasen `LIVE_HOME_READY`, `MOVIE_WARM_BEGIN`, `MOVIES_PREPARED`, `SERIES_WARM_BEGIN`, `SERIES_PREPARED` etc. Das ist **kein garantierter gut sichtbarer Ladezustand auf dem Fernseher**; `widget_notice46.py` ist vor allem Reload-Verwaltung.

**Erster sichtbarer Frame:** räumliches Layout in BINGIE stabil, Senderlogo-Leiste und Hero sofort gerendert, Sendungslogo/EPG sofort aus lokalen Daten. Film-/Serienreihen bestehen strukturell von Anfang an. Bei fehlenden Daten an deren Position je ein unaufdringlicher Status mit optional kleiner nativer Animation oder dezentem Fortschritt. Kein Vollbild-Warteoverlay.

**Medienreihen pro Bereich unabhängig:**
- `LOADING_CATALOG`: „Filme werden geladen …“ / „Serien werden geladen …“;
- `LOADING_ART`: Titel bereits sichtbar, statt Play-Icons lokaler neutraler Poster-Skeleton mit „Cover werden geladen …“ (wenige gezielte Bilder);
- `READY_PARTIAL`: echte vorhandene Kacheln anzeigen, fehlende individuell unaufdringlich nachladen, **keine** ganze Reihe leeren, nur weil ein Cover fehlt;
- `READY`: volle aktuell benötigte sichtbare Kacheln;
- `EMPTY`: „Keine Filme/Serien in dieser Auswahl“ **nur** nach bestätigter erfolgreicher Katalogabfrage, nicht bei `LOCKED`/Offline;
- `ERROR_RETRYABLE`: „Katalog momentan nicht erreichbar · Erneut versuchen“; kein endloser Spinner.
- Animation nur wenn tatsächlicher ausstehender Job/Timer bekannt, CPU-/Speicherbudget und Rendering in Kodi-21/ARM32 prüfen, Skin-Bindings/WindowID/Fokus nicht ersetzen.

**Lade-/Datenpriorität:** lokale EPG-Texte → echte Senderlogos horizontal + Startsender im Hero → passendes erstes Eventbild und die nächsten **vier sichtbaren Eventbilder** (fünf insgesamt) → sichtbare Filme/Serienposter; Cursor 1..5→2..6 darf nur neu 6 anfordern. Keine Massen-TMDB-Abfragen beim Start. Kein 24er-Coverarchiv als erste Pflichtaktion; gleichzeitig keine leere Film-/Serienzeile ohne Ladehinweis. Auf Senderwechsel ändert sich nur Event-Bild/Info, nicht Position/Fokus der Reihen. Bei EPG-Rollover schnell wieder auf Senderlogo und aktuelles Event wechseln, alte Treffer schützen.

**Mini-EPG:** später im selben Follow-up mit gebundenem Eventproof und kleiner, unabhängiger Thumbnail-Control, sofern GUI-Kapazität. `mini_epg.py` hat derzeit nur Text-/Fokuscontrols. Bilder dürfen Mini-EPG-Zapping nicht blockieren.

## 5. Abnahmetests .85, Daten-/Release-Schutz

| ID | Auf echter Box B zu beweisen | Status |
|---|---|---|
| GHOST85-01 | Ghosts EPG-Event eindeutig als UK/US mit tatsächlichen Metadaten belegt, korrekter Hero-Backdrop; bei Mehrdeutigkeit begrenztes Logo und auswählbare manuelle Zuordnung, **keine** falsche Serie | NOT_TESTED |
| GHOST85-02 | TMDB-Trefferliste `>1` Seite: begrenzte Paginierung und Eindeutigkeit unabhängig von Suchrang. Such-/Verifikations-HTTP budgetiert | NOT_TESTED |
| SERIES85-03 | Alarm für Cobra 11 (1996, Originaltitel-Suffix) und Die Rosenheim-Cops (2002, Artikel/Bindestrich) korrekt verifiziert, moderne Film-/Serienbilder nicht vertauscht | NOT_TESTED |
| REV85-04 | Rosenheim-Cops/Modern Family nach echter Event-/Source-Revision: altes Bild fail-closed, neuer Fetch erfolgreich oder klar begründeter Fallback; `FILE_INVALID` eigener Status | NOT_TESTED |
| START85-05 | Kaltstart: Sendericons und vollständiger Hero zuerst, ggf. Logo-Fallback; Film-/Serienzeilen haben eindeutig sichtbare Ladezustände, anschließend progressive echte Poster | NOT_TESTED |
| START85-06 | 1080p und 720p, Kodi 21.3 Android RK3528 ARM32: keine Fokus-/Zeit-/Layout-/Player/Back-/Skin-Binding-Regression; offline Start und Fehler ohne Endlosspinner | NOT_TESTED |
| MINI85-07 | Mini-EPG-Bild (wenn enthalten) korrekt zum Fokus/Event, ohne blockierende Downloads; sonst explizit OPEN | NOT_TESTED |
| COVER85-08 | Bilder über mindestens 30 unterschiedliche echte Sendungen pro Genre/Sender nach Quelle/Match/Bild/GUI/Pixel nachverfolgt; ehrlich ausgewiesene Abdeckungs- und Fehlergründe | NOT_TESTED |

**Geheimnisse und Persistenz:** Kein Rohlog/Portal/SMB/Token in public Issues; vorhandene TMDB-Token, EPG/Provider/Favoriten, SkinShortcuts, Kodi-Datenbank und XCMate-Archiv nicht löschen/migrieren. Keine TMDB-Helper-Laufzeitpflicht, kein Google Drive. #401 Speicherjournal und echter Datei-LRU weiter eigenständig OPEN. Alles neu implementierte Artwork-Datenvolumen begrenzen. Box A unverändert lassen.

**Nächster Schritt:** Nutzer kündigt die **aktuellen Kodi-Logs nach .84** an; bei Eintreffen anhand der Event-/Art-/Home-Codes Ursachen pro Ghosts, Cobra 11, Rosenheim-Cops verifizieren und neue Fehlannahmen korrigieren. Dieses Dokument enthält heute **Quellcodebefunde plus öffentliche Werkfakten plus Nutzerbeobachtungen, aber keine tatsächliche Rohlog-Forensik der neuen Fälle**.
