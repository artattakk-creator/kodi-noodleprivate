# Codex-Masterübergabe – XCMate 0.1.29.88: Android-.87-Stabilität, Senderlogos, Artwork, EPG, BINGIE-Home / Details
**Stand:** 10.11.2026 (Benutzerabnahme nach Installation von 0.1.29.87)  
**Verbindlicher Master:** [Issue #421](https://github.com/artattakk-creator/kodi-noodleprivate/issues/421)  
**Projekt:** `artattakk-creator/kodi-noodleprivate`, Add-on-ID `plugin.video.xtreammate`  
**Ausgangsversion:** 0.1.29.87 (`main`, alle drei Kanäle, PRs #416/#420); neuer Entwicklungsbranch/PR für 0.1.29.88.  
**Status:** Spezifikation/Auftrag; die hier beschriebenen Fehler sind **NICHT als behoben anzusehen**.

## 0. Verbindliche Befehle an Codex (zuerst lesen)
1. **Keine automatische Veröffentlichung:** Implementiere die nächste Version **0.1.29.88** ausschließlich in einem eigenen Entwicklungsbranch; führe nachvollziehbare Tests aus, baue ein geprüftes ZIP samt SHA-256 und eröffne einen **Draft-PR**. **Kein Merge auf `main`; keine Aktualisierung von regulär, Pilot, NeoDark3 oder Release-Indices ohne neue ausdrückliche Benutzerfreigabe.**
2. **Kein Datenverlust:** Kodi-Profil, Portal-Konfiguration, Xtream-Zugangsdaten, EPG-Mappings/Quellen, Favoriten, Merkliste, Widgets/Skin Shortcuts, bestehende Datenbanken und manuell importierter TMDB-Read-Access-Token müssen bei Upgrade vollständig erhalten bleiben. Keine pauschale Profil-, Cache-, SQLite-, Textures- oder Add-on-Deinstallation.
3. **Keine Secrets im Code:** Kein echter TMDB-Token in Repo, ZIP, Screenshots oder Logs. Manueller Tokenimport bleibt Standard. Joomla-Gateway [#417](https://github.com/artattakk-creator/kodi-noodleprivate/issues/417) bleibt **BACKLOG**; GS Media Setup Wizard .5.26 unverändert, Draft .5.27 [PR #418](https://github.com/artattakk-creator/kodi-noodleprivate/pull/418) nicht einbeziehen.
4. **TMDB Helper ist KEINE Laufzeitabhängigkeit.** Das Programm `plugin.video.themoviedb.helper` darf als rein visuelle Inspiration dienen; alle TMDB/TVMaze-Abfragen über XCMates eigene Integrationen.
5. **Echte Android-Evidenz statt „Referenz vorhanden“:** Host-/Kodi-Linux-PASS ersetzt nicht sichtbare Bild-/Logo- und Remote-Tests auf RK3528/Kodi 21.3. Explizit `ANDROID_NOT_TESTED` dokumentieren, solange keine Geräteabnahme existiert. Tests vor Merge.
6. **Prioritätsreihenfolge:** Korrektheit/Logo-Fix → Speicher/Sticky-Artwork → EPG-Konsistenz → Widget-Stabilität → aufgewertete EPG-Details → Screenshot-4-Home → Branding/weitere Bildverbesserungen.

## 1. Benutzerziel & Referenzbilder (7 Chat-Anhänge)
Die Original-TV-Fotos wurden im Chat am 10.11.2026 geliefert. **Sie wurden hier aus Datenschutz-/Contentgründen NICHT als Originaldateien öffentlich ins GitHub-Repo hochgeladen.** Das folgende Bild-für-Bild-Protokoll ist die dauerhafte GitHub-Referenz. Für pixelnahe Abnahme **Screenshot 4 zusätzlich aus dem Chat als visuelle Referenz an Codex übergeben**, falls Codex keinen Zugriff auf die Chat-Anhänge hat.

| Nr. | Originalname im Chat | Verbindliche Beobachtung / Anforderung |
|---|---|---|
| **1** | `1000121111.jpg` | XCMate EPG-Details mit *Scrubs – Die Anfänger*. Programmfoto links, Beschreibung rechts, Text `DE| DISNEY...` im Bild. **Senderlogo statt Text** (Text nur Fallback), Fortschritts-Zeiten darunter, größere TMDB-Attribution/Rating, echte Aktionsbuttons. |
| **2** | `image-1794347765162.jpg` | Derselbe EPG-Dialog nach Erlöschen des bereits sichtbaren Bilds: Hinweis **„Bildprüfung nach 45 Sekunden ohne bestätigtes Ergebnis beendet“**. **Niemals ein zuvor gültiges Bild während gleicher Sendung/Ansicht durch negative Wiederprüfung leeren.** |
| **3** | `image-1794347915862.jpg` | BINGIE-MOD-Einstellungsseite mit großem rotem Branding unten rechts. Bereits vorhandenes freigestelltes **XCMate-Logo** an diese Stelle, eigene Navigation einheitlich. |
| **4 – HAUPTREFERENZ** | `1000121041.jpg` | Ästhetisch maßgebliche BINGIE-Home-Ansicht: filmischer **breiter Backdrop**, Motiv dominant rechts, **weicher Verlauf nach dunklem/transparentem Schwarz links**; darüber Titel-/Showlogo, Metadaten, Bewertung, Beschreibung. Direkt darunter sauberer horizontaler **Poster-Strip**, weitere Reihen sichtbar. **Diese Bildkomposition ist für die neue Home verbindlich.** |
| **5** | `image-1794348140016.jpg` | Aktuelle XCMate-Home während Ladens: schwarzer leerer Zentrumsteil, winzige/uneinheitliche Nav-Icons, nur einzelne Film-Poster, blaue Diagnosebox oben rechts, keine sichtbaren Logos. |
| **6** | `image-1794348184395.jpg` | Aktuelle XCMate-Home mit Rail: 88 Sender, **0/88 Logos**, viel leerer Raum, `Keine Programminformationen verfügbar` bei einer Gruppen-/Pseudozeile, fehlende zusätzliche Widgets. |
| **7** | `image-1794348219671.jpg` | Positivbeispiel: `Family Guy`-Bild sichtbar; **links große verschenkte schwarze Fläche**, rechts starre blaue Texttafel, Senderleiste nur Text und 0/88 Logos; TMDB-Logo zu klein. |

### Home-Designentscheidung / Auflösung alter Anforderungen
Eine ältere Arbeitsvorgabe beschrieb einen 70/30-Bereich **Bild links / Text rechts**. **Für die Home/Startseite gilt jetzt verbindlich Screenshot 4**: große fotografische Fanart-/Backdrop-Ebene, Bildmotiv überwiegend rechts; linke Bildseite wird mit einem dunklen, weichen horizontalen Alpha-Verlauf für Text/Logo/Rating überblendet. **Keine starre blaue Box rechts.** Der Hauptinhalt rückt bis nahe an die linke Navigationsleiste heran, mit sauberer, gleichmäßiger Padding-Zone; kein breiter leerer Schwarzstreifen. **Die EPG-Detailansicht** bleibt ein eigener, gut lesbarer **Bild-links/Informationen-rechts**-Dialog. Nutzerdefinierte Widgetreihen bleiben erhalten. Responsive 1920×1080 und 1280×720.

### Visuelles Text-Wireframe für Screenshot-4-Home
```text
┌─────────┬───────────────────────────────────────────────────────────────────────────────┐
│         │ ███ Dunkler Textbereich mit Verlauf  →   großes Fanart/Backdrop-Motiv rechts │
│ ICONS   │ [Senderlogo] [Sendungs-/Showlogo]                                         ▓▓▓ │
│ größer  │ Titel / TMDB 8.1/10 / Genre / Jahr / Quelle                                ▓▓▓ │
│         │ Jetzt 22:30–22:55 • Rest 14 Min.    Danach ...                            ▓▓▓ │
│         │ Beschreibung ...   ▰▰▰▰▰▱▱                                               ▓▓▓ │
│         ├───────────────────────────────────────────────────────────────────────────────┤
│         │ SENDER-RAIL: [ARD-Logo] [ZDF-Logo] [RTL-Logo] [...]  (Logo statt Text)      │
│         │ POSTER/WEITERE WIDGETS: [Cover] [Cover] [Cover] [...]                       │
│         │ BESTEHENDE FILM-/SERIEN-/SONSTIGE USER-WIDGETS BLEIBEN ERHALTEN              │
└─────────┴───────────────────────────────────────────────────────────────────────────────┘
```
Der Text ist nur eine strukturelle Hilfestellung; **Screenshot 4** bestimmt Komposition, Atmosphärik, Kontrast, Bildgröße und Abstände. Farbbasics XCMate-Blau statt Fremdbranding; die Foto-Bildebene soll dennoch den Hero bestimmen.

## 2. Log-Beleglage 10.11.2026
Analyse der beiden Kodi-Logs `kodi.old(20261110-214518).log` und `kodi(20261110-214519).log`. **Original-Logs enthalten potenziell private Kodi-/Netzwerk-/Providerinformationen; daher hier nur redigierte Befunde und keine Roh-Logs.** Zählungen bezeichnen **Logzeilen/Events**, nicht eindeutige Sender, Dateien oder Fehlerursachen.

| Befund (aktuelles Log) | Beobachtung | Schluss/Prüfauftrag |
|---|---|---|
| `HOME86 LOGOS_LOCAL_READY {"count":0,"total":88}` | 126-mal | 88 Sender vorhanden, **0 lokal für GUI bereitgestellte Logos**; UI-Screenshot 6/7 bestätigt visuelles Fehlen. |
| `LOGO87 URL_SCHEME_OR_HOST_BLOCKED` | 3.096-mal | Logo-URL-Schema oder Hostprüfung blockiert mehrfach; tatsächliche Provider-/Kodi-VFS-Quelltypen redigiert analysieren und sicher unterstützen. |
| `LOGO87 STORAGE_RESERVE_BLOCKED` | 510-mal | Zusätzliche persistente Logo-Speicherung blockiert. |
| `ART_STORAGE82` | `free=239800320; total=4034297856; reserve=1073741824; budget=0` auf ausgewähltem FUSE-Volume | Tatsächliches Volume/Backing Mount und Reservepolicy prüfen; nicht vom nominellen Gesamtspeicher auf freien Cache-Speicher schließen. |
| `DISPLAY84` | `RESERVE_BLOCKED` 106, `METADATA_WRITE_DEFERRED` 258, `RAM_ONLY` 57 | Weitergabe/Rendering nicht mit stabiler Persistenz gleichsetzen. |
| `WIDGET47 live ASSETS NO_RENDERABLE_REFERENCE` | 57 | Logos/Art-Quellen zwar gezählt, aber kein renderbares lokales Live-Asset. |
| `IMAGE77 IMAGE_DECODED`, `IMAGE_LEASE BOUND`, `LOCAL_CACHE RAM_ONLY` | Treffer sind vorhanden, nur Teil persistent | Ein sichtbares/validiertes Asset bei gleicher Event-Identität halten. |
| `WIDGET79 RELOAD_ACK` / `TEXTURE_REQUESTED` | 362 / 361 | Auf periodisch unnötigen GUI-Neubau prüfen, durch Generation/Asset-Hash deduplizieren. |
| `epg_refresh74.py:62` | wiederholte `AttributeError: 'Reader' object has no attribute 'close'` in `XCMate-local-EPG74` | Echte Thread-Exceptions, Lifecycle-Fix erforderlich. |
| `ART81 MATCH_REJECTED`, `ART70 NO_CONFIRMED_IMAGE` | viele Fälle (u. a. falsches Jahr/Alias) | Sichere Titel-/Serien-/Episode-Zuordnung ohne falsches Bild; fehlerfreier Logo-Fallback. |
| `BINGIE_SKIN_PROPERTY SOURCE_MISSING/BOUND`, `RENDER_CONTROL` | Wechsel bei aktiven/erneuten Bindungen | Negatives Zwischenergebnis darf bereits gerendertes gültiges Bild nicht ungültig machen. |

**Wichtige Trennung:** Die Logs beweisen `RAM_ONLY`, Blockaden und Thread-Exceptions; sie beweisen nicht für jede einzelne Sendung den genauen Grund, warum das Bild nach ca. 45 Sekunden verschwand. Die UI zeigt den 45-Sekunden-Abbruch; bitte den konkreten Expiry-/Lease-/Clear-Callsite instrumentieren. EPG-Crash macht Dateninkonsistenz plausibel, aber einen geteilten Datenfehler muss ein Integrationstest nachweisen.

## 3. P0-A: Senderlogo-Pipeline vom Provider bis zum sichtbaren Kodi-Control
**Ausgangslage:** Sender-Rail 88/88 Einträge, aber 0/88 sichtbare Logos auf Android. Log zeigt Schemas/Hosts geblockt und Speicherblockade.

**Implementierung:**
- Erfasse redigiert `channel_key`, Quelltyp (`https`, `http`, `special://`, `image://`, Kodi VFS, lokale Pfade), Normalisierung, Redirect-Kette, Auswahlgrund, Decodierung, local_cache result, Skin-Property, Kodi-Control und auf dem Gerät sichtbares Ergebnis. **Keine Roh-URLs mit Tokens loggen.**
- Bewahre seriöse SSRF- und Path-Traversal-Schutzregeln; legitime Provider-Logo-Referenzen dürfen nicht blanket `URL_SCHEME_OR_HOST_BLOCKED` sein. Kodi-VFS mittels geeigneter Kodi-API lesen, nicht unbekannte Schemas in HTTP verwandeln; HTTP(S)-Redirects restriktiv validieren; keine unkontrollierte private-IP-/Datei-URL-Freigabe.
- Mapping zwischen Startsender, Kanal-ID, Senderlogo und EPG-ID robust und stabil halten (Kanaldubletten/Regionvarianten). Providerlogos bevorzugen, dann sichere EPG-/lokale Fallbackquellen; keine globale Host-Allowlist-Erweiterung ohne Tests.
- **Render-Fallback:** Bei zu knappem Speicher trotzdem nur **sicher dekodierte** kleine Senderlogos in einer begrenzten Session-/RAM-Cache-Schicht oder Kodi-konformen referenzierten Quelle darstellen; kein falsches Erfolgssignal zur Persistenz. Bei fehlendem Motiv das Senderlogo auf dunkler gestalteter Fläche als großer Hero-Fallback, nie blankes Schwarz; falls auch Logo fehlt ein lesbarer Sendername.
- Logo an genau drei UI-Stellen: **(a) kleine horizontale Senderbuttons, (b) oben links im EPG-Foto-Overlay, (c) groß im Hero-Fallback.**
- Bei 88 Sendern Erfolgsquoten getrennt erfassen: Quelle verfügbar, sicher verifiziert, lokal gecacht, Kodi-Textur angefordert, wirklich gerendert. Ziel **alle vorhandenen gültigen Logos auf der Box sichtbar**, Fehlende als nachvollziehbare Ausnahme statt „88/88“ ohne reale Quelldaten. Sichttest durch Screenshot/Box statt nur `SOURCE_READY`.

## 4. P0-B: Artwork-Dauerhaftigkeit, RAM/Disk, „sticky valid image“
**Problem:** Treffer vorhanden, aber häufig `RAM_ONLY`, `METADATA_WRITE_DEFERRED` und erneute Prüfung; Bild verschwindet in Detailansicht.

**Zustandsmodell:**
1. `NO_ASSET` → `FETCHING` → `VERIFIED_VISIBLE` → `PERSISTED` (falls Schreiben möglich).
2. Ein **validiertes sichtbares Bild** erhält einen stabilen Key `portal/channel_id/event_start/event_end/asset_source/asset_id`, plus versions-/Hashkennung.
3. `SOURCE_MISSING`, neue Netzwerklatenz, fehlgeschlagene Cache-Schreiboperation oder 45-Sekunden-Worker-Timeout dürfen ein noch passendes und zuvor erfolgreich überprüftes Asset **nicht** auf leer zurücksetzen.
4. Bei gleicher Event-ID und aktiver Ansicht: zuletzt gültiges Bild bindungsstabil halten; Hintergrund-Revalidation **coalescen** und erst nach vorgesehener TTL, **kein unendliches Traffic-Loop**. Bei positivem und verifiziertem neuem Bild atomar austauschen; bei negativem Ergebnis das alte gültige Bild lassen und Fehler mit Backoff vermerken.
5. Bei echtem Event-Wechsel, manuell gewähltem anderem Kanal, View-Verlassen oder belegtem Sicherheits-/Integritätsfehler Cache-Pin kontrolliert lösen. Kein altes Bild eines anderen Senders/Events anzeigen. Beim Ende eines Events dürfen seine Quellen/Metadaten abhängig vom konfigurierten EPG-Aufbewahrungsfenster weitergecached werden; die UI wechselt jedoch auf die neue Sendung.
6. **Persistenz:** Speicherpfad mit `statvfs`, tatsächlicher Mount-ID/Backing Volume und Schreibbarkeit verifizieren, Herkunft des 4-GB-FUSE-Volumes vs. `/storage/emulated/0` klären, korrekte Reserve dort anwenden. Falls 1-GB-Reserve auf betroffenem Cache-Volume greift, nicht global abschalten; bei Bedarf sichere, bestätigte Migration auf tatsächlich größeres Volume gemäß bisherigen Storage-Issues (#398/#401). SQLite-Transaktionen, Metadatenverweise, temporäre Dateien und Recovery atomar halten. Begrenzt nutzbare RAM-Cache-Schicht bei Schreibblockaden.
7. Kodi Textures-/GPU-Freigabe nicht fälschlich als DB-Löschung deuten: getrennte Telemetrie für Referenz, lokales Bild, Dekodierung, Skin-Property, Textur und reale Anzeige.
8. **Artwork-Priorität:** EPG-Text → Senderlogos → Startsender-Hero → erste fünf sichtbare Sendungen → andere Logos/Bilder → VOD-/Seriencover; Limits für parallele Netzwerk-/DB-Arbeit.
9. Bildqualität: geeignete TMDB `backdrops`/Show-`stills` je nach korrekt identifizierter Sendung und passendem Seitenverhältnis, Bildkomposition/Schärfe/Auflösung/Sprachvarianten prüfen; keine falschen Matches zugunsten hübscher Bilder. TVMaze/Katalog/Provider/EPG-Fallback, keine Helper-Abhängigkeit.

**Verbindlicher Test:** In EPG-Details mit *Scrubs* oder anderem real matchbaren Event: mindestens mehrere Minuten unveränderte Ansicht, kein 45-Sekunden-Leerzustand, keine wiederholten Downloads desselben Bildes; bei Netzausfall/Reserveblockade bleibt einmal dekodiertes Bild während dieser Ansicht stabil, bei Senderwechsel korrekt ersetzt. Wiederstart zeigt persistent gespeicherte Bilder, soweit Disk verfügbar. Speicherlimits und sichere Fehlerbehandlung nachweisen.

## 5. P0-C: EPG-Refresh-Crash und vier Oberflächen konsistent halten
- Fehler `epg_refresh74.py:62 -> reader.close()` an der Quelle beheben. Nicht nur `hasattr` kleben: Reader-Typ/Context-Manager/ordentliche Schließmethoden, `try/finally`, Cancellation, Thread-Ownership und Locks prüfen, keine leaked threads.
- Refresh-Worker **single-flight pro Quelle/Profile**, idempotent und transaktional; keine wiederholten neuen Threads durch periodisches Home-Polling, keine halb sichtbaren Updates und kein Löschen alter gültiger Programme wegen transienter Fehler.
- Gemeinsame EPG-Ereignis-ID und normalisierte Zeitbasis verwenden; Sender-Startgruppe und XMLTV-ID-Provider-Matching nachvollziehbar; Protokoll der gewählten Quelle (Provider XMLTV vs. externe XMLTV, Match-Präzedenz und Fallback) ohne private URLs.
- **Gleiche aktuelle Sendung** muss in Mini-EPG, großem EPG, Home, EPG-Detailansicht identische Startzeit, Ende, Titel, Jetzt/Danach und Fortschritt haben; unterschiedliche Quellen nur mit nachvollziehbarer Provenienz und gewollter Fallbackpolitik.
- Bei fehlendem EPG (z. B. **Gruppenüberschrift** `##### GERMANY HEVC #####`) Group-Header nicht als tatsächlichen Sender behandeln; Header von Senderitems separieren; weder leere „Keine Programminformationen“-Hero noch falsches Bild als Default.
- Refresh interval/Cache 24 h beibehalten, EPG-Fenster (7 Tage zurück/20 Tage vor) nicht zerstören; übersichtliches Log, Error-Budget und Retry-Backoff.

## 6. P0-D: Widget-Erhalt und GUI-Refresh
- In Logs `WIDGET79 RELOAD_ACK`/ `TEXTURE_REQUESTED` sehr häufig; die eigentlichen Callsite-/Timer-/Generationsänderungen überprüfen. Unveränderte Daten **nicht** in Schleifen an Kodi-Control als neue Liste senden; nur delta/update beim wirklichen Generations-/Asset-/EPG-Wechsel. Rebinds niemals sichtbares valides Bild leeren.
- Bestehende XCMate-Reihen Live-TV Startgruppe, neueste Filme, neueste Serien: nach Update weiter korrekt. **Zusätzliche bereits konfigurierte BINGIE-/Fremd-Widgets** sind zu erhalten und auf ihren Zustand/Position zu prüfen; nicht durch einen Installer-Default überschreiben, nicht aus Home-Slots verdrängen.
- Navigationsfokus, Screenshot-Positionen, Kontroll-IDs, Remote-Links/Right/Up/Down und Skin-Einstellungen regressionstesten. Keine leeren Fokusrahmen, kein Sprung von horizontaler Senderleiste in unerwartete Fremdwidgets.
- Von der ersten sichtbaren UI bis finalem Artwork nutzbar bleiben; Diagnose-Hinweise kurz/unaufdringlich, nicht dauerhaft auf dem Hero.

## 7. P1-A: EPG-Detailansicht (Screenshots 1/2)
**Bild-/Textanordnung:** Saubere zweispaltige Ansicht wie Screenshot 1, aber mehr Platz für Foto, lesbare Beschreibung ohne übergroße Zwischenräume, unaufdringliche XCMate-Blautöne.
- **Overlay im Foto oben links:** Senderlogo auf dezenter dunkler Badge-/Scrimfläche, proportional skaliert (keine Verzerrung). Nur wenn keine zulässige rendervolle Logoreferenz existiert, **Sendername als Text**.
- Fortschrittsbalken unter dem Foto mit Uhrzeitinformationen, z. B. `22:30–22:55 · 25 Min. · noch 14 Min.`; vor Beginn `beginnt in …`, nach Ende `beendet`. Zeiten aus derselben EPG-Eventidentität, lokalisiert; Prozent = (now-start)/(end-start) geklemmt 0–100, kein negativer Rest.
- **TMDB-Logo prominenter, regelkonform**, Bewertung klar z. B. `TMDB 7,8/10` **nur bei verifiziertem passendem TMDB-Eintrag mit belastbarer vote_average**; fehlende Bewertung nicht erfinden. Quelle erkennbar; optional Genre, Jahr, Laufzeit, Staffel/Episode, Freigabe nur wenn tatsächlich vorhanden und passend. **TMDB-Serienbild nicht als Episodenstill ausgeben**, falls Quelle nur Serien-/Showbild.
- Textbereich: Sendungsbeschreibung, Start/Ende, Sender, Bildquelle, optional Cast/Director falls verifiziert und relevant. Kein Debugtext wie „Bildreferenz bereit; sichtbare Textur separat“ im normalen Nutzer-UI.
- **Drei echte Buttons** in Fokusreihenfolge: `Zurück` (Dialog schließen, Fokus zurück), `Sendung merken` (persistente idempotente Merkliste mit Kanal/Event-ID, Start-/Ende, Titel, späterer Wiederaufruf; erneutes Klicken wieder entfernt), `Jetzt umschalten` (tatsächliche Live-Wiedergabe des betreffenden echten Senders nach vorhandener XCMate-Playerlogik; nicht auf leeren Gruppenheader anwenden; bei nicht verfügbarem Stream klare Meldung). Ein späteres Sendungserinnerungs-Popup ist ohne eigene Freigabe **kein Muss**; Merkliste zunächst lokal.
- Remote-fokussierbar, Scrollbarkeit der Langbeschreibung und saubere Zurück-/OK-Logik.

## 8. P1-B: BINGIE Home / Startseite nach Screenshot 4
**Primärreferenz** ist ausschließlich **Foto 4 / `1000121041.jpg`**, nicht die defekte aktuelle Home.

1. **Breite heroische Fotoebene** mit starkem, möglichst passendem TMDB-/TVMaze-Backdrop und scharfem Motiv **rechts**, bei 16:9 Foto skaliert/geschnitten, ohne Gesichter zu verdecken; **links weicher schwarzer Verlauf**, der sich gegen rechts auflöst. Text links über dem Verlauf, nicht in starrem Panel rechts.
2. Linksbündig **Senderlogo** / falls passend Show-Titellogo, große Sendungsüberschrift, Quelle/Rating (nur verifiziert), Genre/Jahr, Jetzt/Danach, Start/Ende, Restzeit und Fortschrittsbalken, 2–4 Zeilen Beschreibung, gegebenenfalls „Weitere Details“. Logoplatzierung darf Bildmotiv nicht zudecken.
3. **Nach unten kompakt:** horizontale Reihe aller echten Startsender als **kleine Senderlogo-Buttons** mit sichtbarem cyan-/blauem Fokus; beschränkter Text nur wenn Logo fehlt, horizontal per Fernbedienung scrollend. Fokuswechsel aktualisiert Hero asynchron **ohne blanke Zwischenstufe**.
4. Anschließend vorhandene **sauber angeordneten Posterreihen** (XCMate „Neueste Filme“, „Neueste Serien“ und alle Benutzer-BINGIE-Widgets, die vor dem Upgrade da waren). Keine ungefragte Neuinitialisierung aller Menüs. Keine Erwachsenen-Cover in Logs/Screen-Testberichten, wenn nicht notwendig; Nutzerbibliothek unberührt.
5. **Kein Programmfoto:** animierungsarmer, dunkler blauer Hero-Hintergrund mit **großem Senderlogo**, ggf. leiser Gradient, vorhandene EPG-Texte; niemals reines Schwarz, solange Logo verfügbar. Ist auch Logo nicht verfügbar: Sendername als gut lesbarer Text.
6. **Leerraum beseitigen:** Hero/Rows bis an die normale innere Safe-Area nahe linker Navigation verschieben, keine riesige schwarze Zone. Rechter Informationsrand nicht als starre überbreite blaue Karte. Bild soll über die gesamte Hero-Fläche wirken.
7. Beschriftungen/Skalierung für 1920×1080 und 1280×720, Kontrast, Sichtbarkeit, Overscan-Safe-Area, Fernbedienungsfokus, lange Sendernamen/EPG-Descriptions.
8. Home-Hero und EPG-Detail nutzen dieselbe verifizierte Bildquelle/Rating-Provenienz, können **verschiedene Bildausschnitte** für Portrait/16:9 wählen, ohne zusätzliche API-Abfragen bei gleicher Sendung.

## 9. P1-C: Branding, linke Navigation, fremde Widgets
- Einstellungen (Foto 3): Schriftzug/Logo `BINGIE MOD` unten rechts ersetzen durch das bereits im GS Media Branding-Paket enthaltene **freigestellte XCMate-Logo**; Original-Asset nachweisen, nicht neu erfinden; reversible skin-spezifische Branding-Änderung, kein ungezieltes globales Überschreiben fremder Skin-Dateien.
- Linke vertikale Navigation: alle vorgesehenen Einträge mit **sichtbaren, größeren, kontrastreichen, stilistisch konsistenten Icons** (Suchen, Favoriten, Live-TV, Filme, Serien, Einstellungen, Verlassen; nur vorhandene Funktionen zeigen). Keine schwarzen/kaum sichtbaren Icons, Fokus cyan/blau deutlich. Label als Accessibility-Fallback beim Fokus; Remote und Zurück funktionieren.
- Respektiere ursprüngliche BINGIE-Funktionen, Startseiten-Widgets und Nutzeranpassungen. Wenn Skin-Patch separat installiert werden muss, in PR als abhängiges Artefakt/Testfall dokumentieren; kein automatisches Setup-Wizard-Release.

## 10. P2: Speicher-Altlasten (separater Wartungsbaustein)
Nur **read-only Bestandsaufnahme** verwaister XCMate-eigener Artwork-/Cache-Dateien inklusive Größen/Referenzen/Alter, ausgegeben in Wartungs-UI. Eine tatsächliche Bereinigung ausschließlich nach expliziter, doppelter Benutzerbestätigung mit Journal/Backup/Recovery und enger Pfad-Allowlist. **Keine automatische Löschung bei Update**; nicht Kodi Textures-/Profil-/Portal-/Token-/EPG-Daten oder andere Add-ons anfassen. Der eigentliche .88 P0-Logo-/Cache-Fix darf **nicht** von einem Cleanup-Lauf abhängen.

## 11. Abnahmeplan – automatisiert UND real auf Android
### Host / native / Architektur
- Für URL-/Host-/VFS-Varianten: gültiger Providerlogo-HTTP(S)/Kodi-VFS-Pfad, falscher Scheme, Redirect, externer Host, SSRF/private IP, Path-Traversal, Invalid JPEG/PNG/WebP, Null-Quelle. Prüfe Sicherheitsregeln und sichere Darstellung **ohne** globalen Allowlist-Bypass.
- Low-Space-Szenarien: `free<reserve`, anderer echter Mount, readonly/external/fuse, abgebrochene Migration, DB pausen/resume, Reboot, korrekte `PERSISTED` vs. `RAM_ONLY` Semantik.
- Sticky: 45s Negative-Recheck, Event bleibt identisch, Netzverlust, Gruppen-/Senderwechsel, Event-Ende, verifizierter Ersatz, invalidierte Bilddatei und UI-Schließen; keine falschen/alten Bilder.
- EPG: Reader ohne `close`, mit Kontextmanager, parallele Refreshes, Fehler während Commit, Stop/Kodi-Shutdown, Quelle ungültig, Duplikat-EPG, TZ/DST.
- Details: Senderlogo/Text-Fallback, Start/Ende/Rest, TMDB Rating korrekt oder weggelassen, Buttons Merken/Entmerken/Persistenz, direkte Senderumschaltung mit Player, Android Remote Fokus/Back.
- Keine Regression bei VOD-/Serienindexierung, vorhandenen und fremden Widgets, Sendergruppe, TMDB-Token-Import, Token-Persistenz und Kodi Start/Exit.
- Lint/Tests/build, exakte ZIP-Inhalte, SHA256, Paket-Signatur soweit Projektstandard; Schutz bestehender Installationspfade und kein ungetestetes Installerscript.

### Android-Abnahme – darf nicht simuliert werden
1. Vorher/Nachher-Bilder von der **gleichen realen Android TV RK3528 / Kodi 21.3 Box** für Home 1080p, Senderrail und EPG Details. Vergleiche Foto 4 visuell: hero motif rechts, Verlauf/Texte links, direkt anschließende Posterreihen, konsistente nav.
2. 88 tatsächliche Startgruppen-Sender-Items; gemessene Zahl **sicher verfügbarer UND sichtbar dargestellter Logos** (getrennt; ideal 88/88 sofern Quellen existieren), funktionierender Logo-Fallback im Hero und in der Detailansicht.
3. Ein verifiziertes Sendungsbild **mindestens fünf Minuten** in geöffneter Detailansicht ohne Ablaufwarnung oder Verschwinden; wiederholte Auswahl derselben Sendung ohne redundante HTTP/Decode-Schleife; Wechselkorrektheit.
4. Mini-EPG, großes EPG, Home und Details für gleiche echte Sender/Sendung: Titel/Now/Next/Start/End/Progress gleich. Keine neuen `XCMate-local-EPG74` Exceptions.
5. Fremde BINGIE-Widgets, XCMate Film-/Serienreihen und Fokus/Navigation nach Neustart/Upgrade sichtbar; Logo-Bottom-Right und linke Icons prüfen.
6. Test nach Kodi-Neustart/Update ohne Tokenverlust, ohne Daten-/Widgets-Reinitialisierung; beobachte Mehrfach-Reloads und GUI-Rendering.
7. `ANDROID_NOT_TESTED` solange echte Screenshots/Testergebnisse fehlen; `TEST_PASS` nur für tatsächlich ausgeführte Stufe.

## 12. Übergabe-Artefakte / Codex-Definition of Done
- Eigenständiger Branch und Draft PR für **XCMate 0.1.29.88**; verknüpfe PR explizit mit **#421**.
- Modul-/Dateiliste mit Root-Cause und Fix pro P0; Testergebnisse (Host / native Kodi / Android separat), vorher/nachher performance counters, Sanitized diagnostic snippets.
- Visuelles diff oder echte Screen-Captures 720p/1080p für Detail, Home, Navigation, Branding; ggf. fehlende private Referenz **Bild 4** gezielt vom Auftraggeber anfordern, **niemals durch Fantasie-PASS ersetzen**.
- Migrations-/Rollbackplan für Add-on/Skin, prüfbare Versionsnummer, `.zip` + SHA256 in zulässigem Testpfad, Schutz vorhandener Konfigurationen.
- Ergebnisbericht mit **noch ungelösten Restproblemen**, niemals „fixed“ ohne Beleg.
- **Bei Fertigstellung nur PR-/Testlinks mitteilen; keine eigenmächtige Main-/Repo-Veröffentlichung.**

## 13. Verknüpfte GitHub-Arbeiten
- [#421 – dieser neue Codex-Masterauftrag](https://github.com/artattakk-creator/kodi-noodleprivate/issues/421)
- [#415 – ursprünglicher .87-P0-Master](https://github.com/artattakk-creator/kodi-noodleprivate/issues/415)
- [#411 – BINGIE Original-Look](https://github.com/artattakk-creator/kodi-noodleprivate/issues/411)
- [#414 – Android 0/88 Senderlogos](https://github.com/artattakk-creator/kodi-noodleprivate/issues/414)
- [#413 – manuelle TMDB-Bildzuordnung](https://github.com/artattakk-creator/kodi-noodleprivate/issues/413)
- [#398/#401 – Shared-Storage / Artwork-Migration](https://github.com/artattakk-creator/kodi-noodleprivate/issues/401)
- [PR #416 – XCMate .87-Source](https://github.com/artattakk-creator/kodi-noodleprivate/pull/416)
- [PR #420 – .87-Releases in alle drei Kanäle](https://github.com/artattakk-creator/kodi-noodleprivate/pull/420)
- [#417 – Joomla-Gateway, zurückgestellt](https://github.com/artattakk-creator/kodi-noodleprivate/issues/417)

## 14. Kurzbefehl für Codex
> **Bearbeite Issue #421 anhand dieses Masterdokuments. Entwickle XCMate 0.1.29.88 auf eigenem Branch als Draft-PR: P0 Senderlogos 0/88, Speicher/Sticky-Artwork, EPG-Reader-Crash, Widget-/Skin-Refresh; P1 EPG-Details mit Logo/Zeiten/TMDB-Bewertung/Merken/Umschalten; BINGIE-Home nach Foto 4 (Backdrop rechts, Verlauf und Infos links, Logo-Rail, alle bestehenden Widgets); XCMate-Branding/Navigation. Tests und echte Android-Abnahme dokumentieren, ZIP+SHA256 erstellen. NICHT mergen oder veröffentlichen. Kein TMDB-Token in GitHub, Gateway bleibt Backlog.**
