# CODEX-Übergabe – XCMate 0.1.29.81: Stabilisierung Artwork, Senderlogos, Full-bleed-Hero und Widget-Rails

**Datum:** 08.11.2026  
**Repo:** artattakk-creator/kodi-noodleprivate  
**Basis:** main / plugin.video.xtreammate 0.1.29.80; nur darauf aufbauen, nicht auf .79 zurückfallen  
**Ziel:** 0.1.29.81 als nichtdestruktives Stabilitäts-Update; zunächst Entwicklungsbranch + PR und Test-ZIP; **kein selbstständiger Merge/Release**  
**Neuer Arbeitsauftrag:** #392  
**Übergeordnet:** #389, gemergter .80-Quellcode #390, .80-Verteilung #391  
**Technische Primäranalyse:** docs/XCMate/LOGANALYSE_02980_ANDROID_2026-11-08_1638_1706_DE.md  

## 0. Genau lesen, bevor du änderst

1. Die technische Primäranalyse vollständig einlesen; anschließend #389, #392 und die Änderungsdateien aus PR #390.
2. Fehler in den vier neuen Android-Logs korrekt abgrenzen: .79 bis 16:38 Uhr; **.80 startet 16:38:36**. Die beiden .79-Logs ab 16:24 Uhr überschneiden sich. Zahlen aus der .80-Sitzung NICHT mit .79 mischen.
3. Keine Original-Kodi-Logs, Hostnamen, Portal-/Accountdaten, Tokens, personenbezogene Daten oder geschützte Bildressourcen öffentlich in GitHub stellen. Status-/Timing-/Hashangaben genügen.
4. Positiven Code von .80 erhalten: der konkrete VOD80-Pfad PLAY_ACTION (16:41:17) → KODI_RESOLVED (16:41:24) → PLAYING (16:41:29–16:43:59) ist auf Android nachgewiesen. Live-TV-Start/Exit und Now/Next-Progress ebenfalls nicht regressieren.
5. Fehleranalyse zuerst **Publisher, Ref-Ownership, Cache-/Texture-Lifetime und Skin-Control-Bindung**; KEIN reflexartiger Vollscan, Reset, Löschen von Datenbanken oder Neueinrichten von Widgets.

## 1. P0-A: VOD-Poster dürfen niemals durch Hintergrund-Rebuild verschwinden

**Belegt:** .80: HOME74 31 VOD-COMMITs bei je 24 Filmobjekten, darunter **10 Übergänge REFERENCE_READY→REFERENCE_PARTIAL ohne Änderung von Source-Revision/Count**; 10 zurück zu READY. Gerätefotos: vollständige Filmreihe → große Play-Icons → vollständige Filmreihe. In einzelnen WIDGET47-Snapshots bis zu 16 Platzhalter.

**Technische Pfade prüfen:**
- resources/lib/home_publication74.py – old_frame, merge, art_status, source_refs, signature; besonders Merge- und Revisionsschutz.
- resources/lib/home_publication80.py – capture/reconcile von Provider-Artwork.
- resources/lib/widget_refresh45.py – publish/poll, Refresh-Cursor, Signature/Gegenprüfung, Datei-Snapshot/Reload.
- resources/lib/widget_refs74.py – Revisionsjournal/Renderbarkeit.
- resources/lib/widget_runtime79.py – Native-Consumer/Control-ACK; ACK allein ist kein Beweis sichtbarer Textur.
- resources/lib/widget_items45.py, widget_cache79.py, widget_art44.py, widget_assets69.py, widget_skin80.py – Erzeugung, Revalidierung und veröffentlichte Art-Property.

**Verbindliche Korrektur:**
- Last-good als sicher bestätigte (ID+Art-Rolle+Source-Identität+Rev+Pfad) Referenz pro Film/Serie aufbewahren; Update nie aus bloßem temporärem Missing durch Placeholder ersetzen.
- Bei unverändertem Provider-Katalog und gleicher Auswahl nur **effektive Diffs** publishen. Generation-Counter dürfen nicht durch periodischen Poll alte Texturen ungültig machen.
- Atomare Veröffentlichung der **gesamten** gefüllten Rail (kein Zwischensnapshot mit 16 leeren Art-Feldern); vollständig validierte neue Quellen erst nach Art-/Texture-Verfügbarkeit freischalten.
- Echte Löschungen/Änderungen des Providers, Konto-/Gruppenwechsel und ausdrücklich revoked/deaktivierte Medien müssen weiterhin korrekt behandelt werden. Last-good **nicht** über fremde Portal-/Profile/Content-IDs retten.
- Unterscheide disk-persisted, valid artwork URL, Kodi texture requested, Kodi texture cached, Skin property bound und wirklich visible; nichts als VISIBLE etikettieren, nur weil ein Write erfolgreich war.

**Gate P0-A:** dieselben 24 Filme über mindestens drei Katalog- und Bild-Poll-Zyklen ohne Benutzerfokus anzeigen; keine READY→PARTIAL-Rückschritte bei identischer Quellrevision, kein Wechsel von bestätigt sichtbaren Covern zu Play-Icons.

## 2. P0-B: 88 Senderlogos dauerhaft anzeigen

**Belegt:** .80 HOME74 18 Live-COMMITs, immer 88 Kanäle und gleiche Quellrevision. WIDGET47 live stage=ASSETS: Angebotene Logos fallen von **88 (16:44:32) auf 41 (16:45:33), 35 (16:47:38), 32 (16:49:28)**; später erneuter Anstieg. Zweimal **NO_RENDERABLE_REFERENCE**. Benutzer sieht häufig nur gekürzte Sendernamen statt Logos.

**Technische Pfade:** home_publication74.py, home_publication80.py, logo_cache.py, widget_live47.py, widget_assets69.py, widget_refs74.py, widget_skin80.py, widget_runtime79.py.

**Fix:**
- Kanal-ID/Stream-ID→Provider-Streamicon→geprüfter persistenter lokaler Icon-Verweis getrennt von EPG-Sendungsbild- und VOD-Bild-Pipelines.
- Wiederholte EPG-/Event-Polls oder fehlende aktuelle Fanart dürfen bereits bestätigte Logos nicht löschen.
- Fallback ausschließlich für einzelne Sender, die wirklich kein Bild besitzen. 88 Kanalobjekte ≠ 88 sichtbar dekodierte Logos; messen und unterscheiden.
- Kodi Skin-Properties und echten Texture-Status mit anonymisierten Kanal-IDs und Gründen diagnostizieren. Keine vollständige rail-weite Skin-Neuladung bei einem Sender.
- Beim Fokus-/Gruppenwechsel richtige Icons, kein Stale-Logo einer anderen Gruppe anzeigen.

**Gate P0-B:** horizontaler Rail mit verifizierten Provider-/lokalen Logos bleibt während Idle, Katalogscan, Sendungswechsel und VOD-Fokus stabil. **Keine unmotivierte 88→41→32-Reduktion.**

## 3. P0-C: Bildquelle TMDB/XMLTV/TVMaze stabil und schnell auswählen

**Belegt:** Für mindestens zwei Eventkennungen folgt SOURCE_MISSING auf LOCAL_CACHE PERSISTED; konkretes Beispiel **16:48:48 PERSISTED → 16:50:53 SOURCE_MISSING → 16:50:54 BOUND → 16:51:24 SOURCE_MISSING**. Nutzer berichtet bei unverändertem Croods-Sender TMDB-Bild ↔ XMLTV-Bild ↔ Schwarzbild.

**Technische Pfade:** programme_lastgood80.py, programme_pipeline77.py, programme_sources57.py, programme_requests68.py, programme_title80.py, programme_image69.py, programme_art46.py, image_reference78.py, tmdb_epg60.py, tmdb_connection60.py.

**Designvertrag:**
- Ein Event-Key (Portal/Profil/Kanal+Event-Start+Event-Ende+Titelrevision) bekommt deterministische Auswahl und **Wechselhysterese**.
- Für Live-Hero: **bestätigtes passendes TMDB-Breitbild-Backdrop** bevorzugen, XMLTV-Eventbild/TVMaze/Provider-Fanart als validierte Rückfallquellen; senderbezogenes Logo nur als Notfall-Fallback. Falls das bereits sichtbare Bild noch die beste tatsächlich bestätigte Option ist: **behalten**.
- Bei bestätigter höherwertiger Quelle erst neues Bild herunterladen, Format/URL/Texture prüfen und dann **atomar** sichtbar umschalten. Nicht erst alte Quelle löschen, dann neue laden.
- Keine schwarzen Zwischenframes, kein SOURCE_CHANGED wegen reiner Retry-/Policy-Neuberechnung und kein periodisches Neu-Publish identischer Daten. Echte Sendungswechsel müssen natürlich umschalten.
- Quelle im UI korrekt ausweisen: z. B. TMDB, XMLTV, TVMaze, Provider; nicht eine ausgewählte XMLTV-Anzeige als Beweis eines TMDB-Requests ausgeben.

**Gate P0-C:** Croods/VOX mindestens zehn Minuten bei unverändertem Fokus und Hintergrund-Kataloglauf, **kein TMDB↔XMLTV-Flattern**, kein Schwarzbild. Beim echten nächsten EPG-Event konsistenter Bildwechsel.

## 4. P0-D: Eigene TMDB-Anbindung belastbar und nachvollziehbar nutzen

**Belegt in .80:** 14 ART70/source=tmdb/FOUND bei 14 unterschiedlichen anonymisierten Events. Es gibt aber 117 NO_CONFIRMED_IMAGE für TMDB, 187 PROGRAMME68 FETCH_FAILED und 128 AWAITING_BACKGROUND_REFRESH. Helper-Timeouts sind im .80-Log **null**; alte externe Helper-Abhängigkeit keinesfalls wieder zur Pflicht machen.

**Codeprüfung:** programme_sources57.attempts aktiviert eigene Suche nur, wenn **programme_tmdb46 UND tmdb_research43** wahr sind. tmdb_epg60.candidate hat dieselbe Vorbedingung. Erfolgreicher Token-Import kann die Flags setzen; aus Code-Defaults allein kann nicht geschlossen werden, dass sie auf der Box aus sind. Respektiere Opt-out/Consent und vorhandenes Token. Ohne Auth-Diagnose keinen blinden Token-Reset.

**Konkreter Debugvertrag:**
- Für Live-Event anonymisiert unterscheiden: TOKEN_PRESENT, ENABLED, OPT_OUT, QUEUED, SKIPPED_REASON, HTTP_REQUEST_SENT, HTTP_STATUS, TITLE_NORMALIZED, MATCH_CONFIRMED / REJECTED, IMAGE_BACKDROP_READY, IMAGE_POSTER_READY, SOURCE_COMMITTED, TEXTURE_VISIBLE/NOT_VISIBLE; Latenz in ms.
- TV-/Movie-Suche sauber trennen; Titel und Alias normalisieren; Saison/Folge nur bei ausreichender EPG-Matchsicherheit zur Episoden-Still-Suche verwenden. Priorität vollständiges 16:9-Backdrop, danach passendes Still/Poster-Fallback.
- Testfälle: **Modern Family**, **Yuna & Stitch / Stitch!**, **Die Tribute von Panem – Mockingjay (1)**, **Harry Potter und der Feuerkelch**, **Die Croods: Alles auf Anfang**. Bei echten fehlenden Ergebnissen Status nachvollziehbar dokumentieren, keine Erfolgsmeldungen erfinden.
- HTTP-Zeitbudget, Inflight-Deduplikation, Backoff für Nichttreffer/Timeout, priorisierte Suche für fokussierten aktuellen Sender; art cache positive/negative pro Event/Edition. Token, URL mit Zugangsdaten und Provideridentität nie loggen.
- TMDB-Metadaten ggf. mit der korrekten Quelle ausweisen; bei gesetztem API-Zugang eigenen Pfad verwenden, nicht vom externen TMDB Helper oder defekten Kodi-MyVideos-Views abhängen.
- Filme-/Serien-Rails: **echte Providerposter beibehalten**, TMDB ergänzend für hochwertige große Heros und fehlende Poster; vorhandene gute Providerart nicht durch schlechtere TMDB-Resultate überschreiben.

**Gate P0-D:** Pro Beispiel-Event beweisbarer Request **oder** gültiger Cachetreffer **oder** erklärbarer Skip/No-Match; bestätigte Treffer müssen in die Anzeige gelangen und dort stabil bleiben. Keine Tokenexposition.

## 5. P1-A: BINGIE Full-bleed Hero für Live-TV, Filme und Serien

**Ist:** Croods mit schönem Bild, aber harter/enger rechter Textbereich; bei VOD nur kleines/schmal gezogenes Hochformatposter statt großflächigem Header. Serien in der Filmreihe akzeptabel, Header teils beschnitten. Layout bitte **nicht mit einem pauschalen stretch** lösen.

**Soll für Full-HD (1920×1080), zusätzlich 720p testen:**
- Header vollständig mit geeignetem Landscape/Backdrop über die nutzbare Breite. **Aspect Ratio bewahren**; falls Cropping nötig, intelligenter Center-/Subject-Ausschnitt, keine Dehnung.
- Auf dem Artwork rechts/unterhalb eine halbtransparente Infofläche (z. B. dunkler Verlauf mit Alpha), nicht separate massive schwarze halbe Bildfläche.
- Live: Senderlogo, Titel, Jetzt/Danach, Fortschritt, Kurzbeschreibung, Quelle; keine überlappenden Texte, Scroll-/Clipping-Bounds und Schriftgrößen korrekt.
- Filme/Serien: TMDB-backdrop/fanart statt kleinem Anbieterposter, sofern belegte gültige große Grafik vorhanden. **Falls nur Poster:** großes unbeschnittenes Hochformatposter im Vordergrund und breiter, passender gedimmter/unschärfer Hintergrund; Poster nie extrem verzerren; für Kacheln weiter Poster.
- Distanz zwischen den Film- und Serienleisten deutlich verkürzen; als **neue Gestaltungszielgröße** 16–32 px optischer Abstand zwischen Rails zuzüglich Überschrift bei 1080p, proportional bei 720p. Fokus-/Hover-Hitboxen, Zeilenscroll und Userwidgets nicht beschädigen.
- Die Filmreihe **bereits ohne Down/Fokus** sichtbar; die Serienreihe möglichst unmittelbar darunter. „Neu im Kino“/eigene BINGIE-Kategorien erhalten.
- Prüfe exakt skin_upgrade80.py, widget_skin80.py und relevante XCMate-XML-Includes mit originalen Digest Guards; Skin-Titan-BINGIE nicht global überschreiben, nur eigene bewiesene XCMate-Bereiche.

## 6. P1-B: Katalogscan unauffällig, korrekt und in niedriger Priorität

**Ist:** Große XCMate-`i`-Benachrichtigungen verdecken rechts im Hero fortlaufend Titel, EPG, Beschreibung; Nutzer sieht gruppenweise Katalog-/Speicherstatus. Währenddessen wechseln die bereits geladenen Poster.

**Technische Pfade:** catalog_progress73.py (insbesondere poll()/notification()), catalog_jobs73.py, catalog_sync.py, catalog_delta52.py, widget_refresh45.py, home_schedule75.py.

**Fix:**
- Normale Gruppen-/Delta-Updates **standardmäßig still**; höchstens kleine nicht überlagernde Statuszeile in einem reservierten oberen Bereich, optional abschaltbar.
- Nur bei tatsächlichem Abschluss und Nutzereinstellung zusammenfassende Meldung, ohne mehrfaches Popup je Gruppen-/Titelstatus.
- Einstellungs-/Katalogmanager erhält Job-ID/Status/zuletzt **wirklich erfolgreiche Provider-API-Aktualisierung** getrennt je Film/Serie, Anzahl verarbeitet/neu/geändert/unverändert/fehlgeschlagen; `Neu · 01.11.2026` ist ein Provider-Added-Datum, **nicht** nachgewiesene Last-Sync-Zeit.
- Etappenweise lesen und persistent speichern; kritische Home-Firstframe-Aufgabe priorisieren: lokal gecachtes EPG + Logo-Rail → erste fünf Sendungsbilder → übrige Live-Programme → VOD/Serien-Hero → restliche Cover. Keine Vollneupublikation bei Null-Diff.
- Kein Löschen zuvor vorhandener gültiger Titel/Art bei leerer oder fehlerhafter Provider-Teilantwort; echte Provider-Entfernung nach positiver, autoritativer Vollsynchronisierung weiterhin korrekt behandeln.

## 7. P1-C: Kodi-DB-/Lock- und EPG-Probleme nur sicher diagnostizieren

.80 zeigt weiterhin KODI_LIBRARY_MISSING_VIEWS (117 ART70-Status), einige native MyVideos131-View-Fehler und SQLITE_BUSY, EPG63 535 DATA_MISSING / 262 CACHE_UNAVAILABLE / 232 READY / 74 DB_BUDGET. Wiederholte Leseversuche sind keine einzigartigen Programme.

- Native Kodi-View-Existenz **nur read-only** prüfen; mögliche Herkunft separat erklären, keine SQLite-View-Generierung ohne Backup und konkretes Schema. Der Defekt ist **nicht** als Ursache sämtlicher TMDB-/Provider-Artworkergebnisse bewiesen.
- Kritischen XCMate-Home-/TMDB-Pfad **unabhängig von den Kodi-eigenen Views** halten, EPG-/Art-DB-Schreibzugriffe serialisieren/kurz halten und Retries begrenzen.
- Keine Datenbank-Lösch-/Reset-/Neuinstallations-"Lösung".

## 8. Testmatrix/Abnahmekriterien – Pflicht vor Fertigmeldung

| Gate | Testszenario | Erwartung |
|---|---|---|
| A1 | VOD-24er-Rail mit 3 Katalogzyklen & gleichzeitigem Skin-Poll, gleiche Source-Revision | Kein READY→PARTIAL für bereits bestätigte Art, keine Play-Icon-Regression |
| A2 | 88 Sender mit Fokuswechsel und EPG-/TMDB-Art-Jobs, Idle | Logo-Refs und sichtbare Kodi-Logos stabil; keine 88→41→32-Regression |
| A3 | Croods bei statischem Event / TMDB, XMLTV, Fehlversuch | Kein Schwarzbild und keine Quelle-Flatterei |
| A4 | Modern Family, Yuna & Stitch, Mockingjay, Harry Potter | Eindeutige eigene TMDB-Request-/Cache-/Skip-Diagnose, bestätigte Bilder sichtbar |
| A5 | Filme, Serien, Live-Hero je Landscape und nur Poster; 1080p/720p | Full-bleed, transparente Info, kein verzerrtes Poster, Reihen eng und sichtbar |
| A6 | Automatischer und expliziter Katalogscan | Keine riesigen Overlays, valide Poster/Logos bleiben, Last-Sync/Delta-Report korrekt |
| A7 | VOD80 vorhandener positiver Play-Pfad, Live-TV Start/Exit, NowNext und EPG | Kein neuer Hänger, kein Verlust von Userwidgets |
| A8 | Restart, Offline/Netzfehler/Timeout, ungültige Art, geänderte Event-ID | Fallback,last-good, Backoff und Cache-Schlüssel sauber und profilgetrennt |
| A9 | Kodi native .xml + Tests/CI, Test-ZIP/Paket-SHA256 | Reproduzierbare Ergebnisse, kein Android-PASS ohne reale Box |

**Achtung:** Host-CI PASS beweist **nicht** Android/GLES-2.0/Mali-450-Texture-VISIBLE. Bis tatsächlicher RK3528-Abnahme muss `ANDROID_NOT_TESTED` geführt werden.

## 9. Bestandsschutz, Release und Abschlussdokumentation

**Nicht ändern/löschen:** bestehendes Kodi-Profil, Kodi-MyVideos-/XCMate-/EPG-Datenbanken, Provider-/Portal-Logins, TMDB Read Access Token, EPG-Quellen und Mapping, Favoriten, SkinShortcuts, Titan-BINGIE-Mod-Benutzereinstellungen, Branding/Space Blue, GS Media Setup Wizard **0.5.26**, andere Addons. Keine Änderungen an regulären/Pilot/NeoDark3-Repo-Manifesten durch diesen Auftrag.

**Lieferobjekte:**
1. Branch z. B. `fix/xcmate-02981-android-artwork-stability`, gezielte Commits und Pull Request gegen `main`.
2. Ursache/Änderung **pro P0** im PR (Datei, Test, Log-Beleg, Residualrisiko), neue zielgerichtete Tests mit künstlichen parallel/fehlenden Bildresultaten und 1080p-/720p-XML-Checks.
3. Version **0.1.29.81** mit nachvollziehbarem Change-Log, reproduzierbarem Test-ZIP, Prüfsumme, Build-/CI-Links und Android-Matrix zum Nachtesten.
4. Issue #392 mit PR, Tests und verbleibenden P0s aktualisieren, #389 als Kontext referenzieren.

**Explizites Stop-Gate:** Dokumentieren + PR/Testpaket vorbereiten, **NICHT eigenständig auf main mergen und NICHT in GS Media regulär/Pilot/NeoDark3 veröffentlichen**; der Nutzer gibt Merge/Release separat frei.

### Codex-Startkommando in natürlicher Sprache

> Öffne zuerst diese Datei und die .80-Loganalyse auf main, bearbeite die P0s vollständig und kumulativ, baue XCMate 0.1.29.81 mit Regressionstests und PR. Lass Benutzerprofile, Token, Datenbanken, Installer und Repositories unangetastet und merge/release erst auf gesonderte Freigabe.
