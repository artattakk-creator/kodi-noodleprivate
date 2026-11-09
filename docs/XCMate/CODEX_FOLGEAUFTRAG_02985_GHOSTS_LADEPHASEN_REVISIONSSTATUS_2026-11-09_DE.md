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

## 6. Nachtrag: echte Kodi-Gerätelogs am 09.11.2026 (16:56–17:57, .83 → .84)

**Status: vollständige lokale Analyse der privaten Dateien, nur bereinigte Ergebnisse in GitHub.**  
Quellen: `kodi.old(20261109-165728).log` (2.969 Zeilen, 16:56:13–17:01:42, beim Start .83) und `kodi(20261109-165729).log` (21.549 Zeilen, 17:02:04–17:57:02, beim Start **.84**). Beide auf **Kodi 21.3, Android ARM32 RK3528, Skin Titan BINGIE MOD 2.2.3, 1920×1080**. **Wichtig:** Fenster von ca. 5,5 versus 55 Minuten; die nackten Ereigniszahlen **sind keine vergleichbaren Erfolgsquoten oder eindeutig verschiedenen Sendungen**. Keine Rohlogs, Geräte-Hostnamen, Netzfreigaben, URLs oder Token publizieren.

### 6.1 Zahlen .84 (55-Minuten-Lauf), nach Ereignistyp

| Pipeline | Beobachtete Einträge |
|---|---:|
| `ART81 TOKEN_PRESENT YES` / `ENABLED YES` / `OPT_OUT NO` | je **117** |
| `ART81 HTTP_REQUEST_SENT OK` und `HTTP_STATUS OK`, alle `status=200` | je **106** |
| `ART81 MATCH_CONFIRMED EXACT` / `IMAGE_BACKDROP_READY OK` | je **42** |
| `ART81 MATCH_REJECTED`: `SERIES_MULTIPLE_MATCHES` / `NO_MATCH` | **9 / 50** |
| `ART81 MATCH_REJECTED SERIES_GENRE_UNKNOWN` / `SERIES_TITLE_SHORT_NEEDS_PROOF` | **82 / 14** – *Hinweis*: die beiden Marker sind in `programme_tv66.py` **nicht unbedingt Abbruch**, der Resolver versucht danach trotzdem weiter |
| `ART81 MATCH_REJECTED SERIES_ALIAS_UNVERIFIED` / `SERIES_ART_MISSING` / `SERIES_YEAR_CONFLICT` | **3 / 3 / 2** |
| `IMAGE77 HTTP_RESPONSE IMAGE_DECODED` / `IMAGE_LEASE BOUND` | je **66** |
| `IMAGE77 BINGIE_SKIN_PROPERTY BOUND` | **47** |
| `IMAGE77 RENDER_CONTROL IMAGE_REQUESTED` / `SOURCE_MISSING` | **52 / 21** |
| `IMAGE77 LOCAL_CACHE RAM_ONLY` / `PERSISTED` / `LOCAL_READY` | **116 / 3 / 6** |
| `DISPLAY84 METADATA_WRITE_DEFERRED` / `METADATA_RESERVE_BLOCKED` | **148 / 87** |
| `DISPLAY84 SOURCE_BLOCKED` | **62**, davon 60 für `kind=vod`; Ursachen pro Trust-/URL-/Policyfall prüfen, keine Security-Bypasses |
| `WIDGET47 kind=live/vod/series ASSETS REFERENCES_READY` | **34 / 33 / 33** |
| `WIDGET79 TEXTURE_REQUESTED`, `SKIN_CONSUMER_READY`, `ACTIVE_CONTROL` | je **116** (über alle drei Widgettypen) |
| `HOME82 CACHED_ITEMS_READY` | **82 VOD / 82 Serie**; Beispiel 17:02:42 VOD 24 Items, 18 lokale Bildreferenzen und 17:02:54 Serie 24 Items, 31 Rollen-Referenzen |
| `HOME82 android_render_verified` | **false in allen protokollierten HOME82-Records**. Dieses Flag ist kein positiver Sichtbarkeitsnachweis und auch nicht automatisch Beweis, dass kein Bild auf dem Fernseher sichtbar war. |
| `EPG63 DB_READ: EPG_DATA_MISSING / EPG_CACHE_UNAVAILABLE / EPG_DB_BUDGET / READY` | **842 / 502 / 208 / 323** |
| `PROGRAMME_DB46 PROGRAMME_DB_IO / DISK_FULL` | **40 / 6** |
| `ART80 EVENT_CHANGED / EXPIRED / POLICY_CHANGED / SAME_EVENT_RETRY` | **3 / 4 / 1 / 1** |
| `PROGRAMME68 CACHE_MISMATCH` | **1** geloggter Eventcode, 17:10:44, bei `PROGRAMME48 LOCAL_EVENT source=UNKNOWN code=UNAVAILABLE` und `NO_SOURCE_FACTS`; dies ist **nicht beweisbar** dem gesprochenen Fall „Rosenheim-Cops“ zuzuordnen |

Alte .83 nur zur historischen Einordnung (5,5 Min): `MATCH_CONFIRMED EXACT` 1, `IMAGE_DECODED` 3, `BINGIE_SKIN_PROPERTY BOUND` 0, `RENDER_CONTROL IMAGE_REQUESTED` 0, `TLS_ERROR` 19; .84 liefert echte erfolgreiche HTTP-200-TMDB-Vorgänge und Kodi-Bildanforderungen. **Keine gleiche Beobachtungsdauer, keine 42-fach höhere Abdeckungsquote ableiten.**

### 6.2 Entscheidend: Tatsächlicher Mount-/Reserve-Druck

`ART_STORAGE82` meldet für die **ausgewählte lokale XCMate-/Kodi-FUSE-Volume** `total=4.034.297.856 B` ≈ 3,76 GiB, **nicht** nachgewiesenen tatsächlichen Bildverbrauch. `free` fällt von **33.976.320 B** (17:03) auf ca. **28.004.352 B** (17:56). `reserve=80.685.957 B` ≈ 77 MiB; `budget=0` (konfiguriertes unlimitiertes Artworkbudget, **kein Null-Speicherverbrauch**). `RESERVE_BLOCKED` bei allen 50 Storage-Samples. **Selbst der erste gemessene Wert unterschreitet bereits die Sicherheitsreserve; der freie Wert verschlechtert sich im Verlauf.** Kein Schluss auf Speicherart/andere Mounts ohne weitere VFS-Messung.

`ART81 CACHE RESERVE_BLOCKED` **217** Ereignisse; `DISPLAY84 METADATA_WRITE_DEFERRED` 148, `METADATA_RESERVE_BLOCKED` 87; `PROGRAMME_DB46` 46 Schreib-/IO-Fehler. **Die Bildfreigabe im RAM funktioniert teilweise, während positive Persistenz / Nachladen / Langzeit-EPG vom Speicherzustand betroffen sein können.** Weder die 28 MB noch die 3,76 GiB mit Androids **anderen** Speicheranzeigen oder belegtem Artwork gleichsetzen. Für #401: Ursachen sicherer freier Space/Volume-Mapping/Journaling prüfen, **ohne** Kodi-DB, Textures13, Backups, alte Kunstwerke oder EPG zu löschen. Nutzer hat private Windows-SMB-Freigabe als separates Testziel, kein automatisch umkonfigurierter Standard und keine Zugangsdaten ins GitHub.

### 6.3 Startup und Re-Load: interne Reihenfolge noch nicht „Logos und Hero immer zuerst“

`home_schedule75.py` protokolliert:
- 17:02:36 `START_GROUP_KNOWN`; 17:03:01 `VISIBLE5_QUEUED count=5`.
- 17:04:46 `MOVIES_VISIBLE_READY`; 17:04:49 `SERIES_VISIBLE_READY`; erst 17:06:44 `LIVE_HOME_READY`. Dies sind intern verschieden definierte Render-/Phasen-Signale, **kein visueller Frame-für-Frame-Beweis**. Die geforderte *sichtbare* Hero+Senderlogos-first-Priorität ist nicht zweifelsfrei gewährleistet.
- Ab 17:06 folgen wiederholt `MOVIE_WARM_BEGIN` **74-mal** und `SERIES_WARM_BEGIN` **76-mal**, mit häufig `WIDGET41 BUDGET` (**145**), `WIDGET47 kind=vod/series DIRECTORY READ_ONLY_RELOAD` (**44/43**), `HOME82 CACHED_ITEMS_READY` (je 82) und erneut Skin-/Texture-Anforderungen. **Prüfen auf unnötige identische Reloads/fehlenden State-Gate**, anstatt den User endlos laden zu lassen; Phasen nicht beim Rücksprung oder Fokuswechsel verlieren.
- 24 Film-/Serienitems waren bereits in frühen Snapshot-Katalogen vorhanden, z.B. VOD 17:02:42, Serie 17:02:54. Es fehlen sichtbare **LOADING_CATALOG, LOADING_ART, READY_PARTIAL, READY, ERROR**-Platzhalter; die Startansicht darf nicht leer wirken.
- Das Mini-EPG implementiert bislang nur Text-/Zeit-/Fokuscontrols, keine sendungsspezifischen Thumbnails; eigener Scope.

### 6.4 Genaues Vorgehen für Codex vor .85-Implementierung

1. **Ghosts**: einzelne TMDB-Kandidatenseiten und `SERIES_MULTIPLE_MATCHES` durch *privaten* reproduzierbaren Fixture-Fall verfolgen. **Das Log enthält keine Klartext-Sendungstitel** und beweist daher **nicht**, dass die neun Serien-Mehrdeutigkeiten Ghosts waren. UK-2019-/US-2021-Werkidentität durch EPG-Jahr, Inhalt, ggf. Sender/Staffel/Folge/Provider-ID oder manuelle Zuordnung; nie „ersten TMDB-Treffer“ ungeprüft wählen. Multi-Page-Vollständigkeit explizit von wirklicher Titelambiguität trennen.
2. **Cobra 11, M*A*S*H, Modern Family, Rosenheim-Cops**: jeweils read-only tatsächliche EPG-Fakten plus anonymisierten Entscheidungspfad protokollieren; vorläufige Titel-/Alias-/Revisionshypothesen nicht als bewiesene konkrete Ursachen ausgeben. `CACHE_MISMATCH` erst anhand internem `FILE_INVALID` / `EVENT_CHANGED` / `SOURCE_CHANGED` / `EXPIRED` / `POLICY_CHANGED` präzisieren; neuer Event-Fingerprint → bounded re-resolve, altes Bild fail-closed.
3. **EPG**: `EPG_DATA_MISSING`, `EPG_CACHE_UNAVAILABLE`, `EPG_DB_BUDGET` systematisch auf Quelle, Kanal-Mapping, Schedule-Lesezeit, Timeouts, wiederholte Read-Volumen trennen. Sendungsmetadaten müssen aus einer kanonischen Quelle erhalten bleiben. Keine manuelle XML-Neuimport-Pflicht.
4. **Storage**: #401 als potenziell kritischen **Blocker für Persistenz und wiederholtes Nachladen** mitnehmen; `statvfs` exakt pro gewähltem Backend, SMB nur nach positiver read/write/rename/readback-Prüfung und Nutzerfreigabe, kein unautorisierter Reset, niemals Reserve pauschal ausschalten.
5. **Homepage**: Anfangszustand **Logo/Hero/NowNext sofort**, Film/Serie darunter mit echter Ladeanzeige (kein Endlosspinner), Karten schrittweise, stable focus; `HOME75`- und `WIDGET79`-Transition-Tests auf echten Box-B-Render; begrenzter, stabiler sichtbarer 5-Event-Cursor.
6. **Kodierte Diagnose**: erlaubte redigierte Gründe zählen, echte Bilddatei-Bytes, Uri-approval, Kodi native texture/pixel und transparente UI-Abnahmematrix; keine sensiblen URL/Token/SMB-Daten in Github.

**Auftrag bleibt OPEN, .85 noch nicht implementiert, keine .84-Rebuilds, kein Merge ohne separate Nutzerfreigabe.**
