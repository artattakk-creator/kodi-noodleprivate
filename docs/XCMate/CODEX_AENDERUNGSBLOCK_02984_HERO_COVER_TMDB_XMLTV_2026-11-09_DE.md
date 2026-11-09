# CODEX-ÄNDERUNGSBLOCK – XCMate .84: Hero vergrößern, Lesbarkeit, Cover und Bild-Fallbacks

**Stand:** 09.11.2026 · **Priorität:** P0 · **Repository:** `artattakk-creator/kodi-noodleprivate`  
**Einziger Entwicklungsbranch:** `fix/xcmate-02984-artwork-visible-first`  
**Laufender Draft-PR:** [#405](https://github.com/artattakk-creator/kodi-noodleprivate/pull/405) · **Master:** [#403](https://github.com/artattakk-creator/kodi-noodleprivate/issues/403)  
**Vorherige Handoff-Spezifikation:** [CODEX_UEBERGABE_02984_BILDER_ZUERST_2026-11-09_DE.md](CODEX_UEBERGABE_02984_BILDER_ZUERST_2026-11-09_DE.md)

## A. Dokumentierte visuelle Belege – vom Nutzer 10 Fotos, keine Originalfotos im Repository

Der Nutzer hat zehn Fotos von der XCMate/BINGIE-Oberfläche auf einer 1920×1080-Android-TV-Box bereitgestellt. Sie dokumentieren den **bisherigen Gerätestand vor Hardware-Abnahme der .84**; daraus darf **kein** Test-PASS für .84 abgeleitet werden. Die Fotos zeigen Privatumgebung und sollen **nicht** in GitHub, Code, Test-ZIPs oder CI veröffentlicht werden.

| Referenzfoto | Sichtbarer Istzustand | Konsequenz |
|---|---|---|
| 1, 7: **Im Reich des Blauwals** | Richtiges Walmotiv im Detail und BINGIE-Hero, sichtbare **TMDB**-Attribution/Film-ID. | Eigene TMDB-Kette funktioniert **selektiv bis zum tatsächlichen Bild**; positiven Pfad erhalten; kein pauschaler Token-Reset. |
| 2, 3, 8: **Entschlüsselt: Prophezeiungen der Geschichte** | XMLTV-Eventbild erscheint; relativ hochformatige Bildquelle im breiten Start-Hero auffällig vergrößert/beschnitten; Detailbild entspricht Format besser. | Portrait-/Landscape-Erkennung, kein Strecken oder aggressives Crop; getrennte Detail-/Hero-Darstellung. Auflösung des Originals nicht aus TV-Foto ableiten. |
| 4: **Expedition Unknown – Mythen auf der Spur** | Kein passendes Bild, Technikcode `KODI_LIBRARY_MISSING_VIEWS` wird Endnutzer angezeigt. | Bild-Fallback/Quellresolve von Kodi-Library-Views entkoppeln; Fehlercode nur im Diagnosemodus, native DB nur read-only prüfen. |
| 5: **Alle unter einem Dach** | XMLTV-Serienbild in Detailansicht vorhanden. | Erfolgreiche XMLTV-Eventbild-Zuordnung als Regressionstest. |
| 6: **Criminal Intent – Verbrechen im Visier** | Kein Bild, `KODI_LIBRARY_MISSING_VIEWS` in Dialogstatus. | Eigenständiger Kodibibliotheks-Fehler, keine automatische DB-Recreation; TV-/Serienbild-Fallback prüfen. |
| 9: **Die fünf Weltreligionen** | Passendes großes Bild im Hero; weiße Texte rechts über abwechslungsreichem hellen Bild nicht gut lesbar. | Dunklere feste Infofläche rechts; Bild nicht als Text-Hintergrund ohne Schutz verwenden. |
| 10: **Star Trek: Deep Space Nine** | Statt Serienbild füllt gelbes SYFY-Logo fast die ganze Hero-Fläche. | Senderlogo-Fallback beibehalten, aber begrenzen und für sauber **identifizierte Serie** TMDB/TVMaze-Serienhintergrund anbieten, ohne erfundene Episodenstills. |
| 7–10: Film-/Serien-Startwidgets | Große Standard-**Play-Symbole**, keine Cover; horizontale Sender-Logo-Leiste vorhanden. | Vollständige Provider-Poster-Lieferkette bis BINGIE `ListItem.Art(poster)` und Kodi-Textur prüfen; kein Bild-PASS durch bloße Quelle. |
| 7–10: Layout allgemein | Hero zu niedrig, seitliche Jetzt/Danach-Tabelle sehr transparent, viel vertikaler Leerraum zwischen Film- und Serienreihe. | Hero vergrößern, Senderleiste/Filmreihe nach unten, *gleichzeitig* Abstand Film↔Serie kleiner; rechte Infofläche abdunkeln. |

## B. Verbindlicher Korrekturauftrag (alle Punkte im **bestehenden .84-PR**)

### B1 – Breiter/höherer Hero und priorisiertes Logo-Fallback

1. Hero signifikant größer als beobachtete .83-Ansicht, ohne die 16:9-Bildfläche in Portrait-Bilder zu zwingen. Ein Layoutversuch für die **1080p-GUI** darf bei etwa **600–640 Kodi-Layoutpixel Höhe** statt `520` beginnen; **finale Werte nur anhand echter Box-B-Screenshots** festlegen, da Skin-Skalierung/Viewport und unbekannte User-Layout-Restwerte relevant sind.
2. Gemeinsames vertikales Verschieben von Hero-Unterkante / horizontaler Senderlogo-Leiste / nachfolgenden Film-/Serienwidgets. Die erste Filmreihe soll sichtbar und bedienbar bleiben; die Serienreihe muss durch normales Scrollen erreichbar sein. Kein Abschneiden, Z-Order-Overlay, Fokusrahmenversatz oder Zurück-/Player-Regression.
3. **Sofortige Senderlogo-Anzeige ist erwünscht!** Bei neuem Startsender/fokussiertem Kanal zuerst verifiziertes Senderlogo im Hero samt Jetzt/Danach/Progress anzeigen; danach exaktes Eventbild asynchron einblenden. Logo-Fallback **nicht auf Bildflächenbreite aufblasen** (SYFY-Screenshot); maximal begrenzter Bereich / `keep`/contain und visuell ruhige Fläche. Auch ohne Eventbild benutzerfreundlich.
4. Verifizierte widescreen-TMDB-Backdrops korrekt im großen Hero darstellen, hochformatiges XMLTV-Bild als passende Portrait-/Contained-Darstellung (ggf. abgestimmter neutraler/abgedunkelter Fill). **Keine falschen Proportionen, kein ungeregeltes Cropping, kein falsch zugeordnetes Bild.**

### B2 – Rechte EPG-Informationstafel besser lesbar

1. Eigenständiges stabiles **Navy-/Schwarz-Overlay** unter Sendername, aktuelle Sendung, Danach, Zeit, Fortschritt, Beschreibung und Quellenzeile; nicht die gesamte Hero-Grafik pauschal verdunkeln.
2. Als **Testvariante** ca. **85–92 % dunkel deckend** bzw. visuell gleichwertiger Kontrast. Unterschiedlich helle Originale (Blauwal, XMLTV-Portrait, SYFY-Logo) mit echten Screenshots testen und optisch feinjustieren. Optional weicher Gradient/links nach rechts, aber Textbereich bleibt selbst bei weißen Bildern lesbar.
3. Innenabstand, saubere Zeilenumbrüche, Quellenlabel und Progressbar auf 1920×1080 prüfen. Keine Text-Überlappungen, abgeschnittenen Programmtitel, übergroßen Labels oder verschwundenen Now/Next-Angaben.

### B3 – Film-/Seriencover korrigieren

1. Vom vorhandenen Provider-Katalog über `media_art.sources`, `widget_assets69`, `widget_art44`, `widget_items45` / `widget_skin81.XCMate81.PosterRow` bis `ListItem.Art(poster)` / Kodi Textur **Ende-zu-Ende** messen. Bei 24 Widgetelementen dürfen nicht schlicht alle generische Play-Symbole bleiben, wenn zugelassene reale Provider-Cover vorhanden sind.
2. Die bisherige `artwork_display84`-Logik bei Archiv-Reserve-Druck nutzen, aber keinen ungesicherten Provider-Passwortlink in ListItems, Logs oder HTTP-Renderer durchreichen; URL-/DNS-/TLS-/SSRF-Schutz erhalten.
3. Visible-only: Cover nur für gerade sichtbare Widgets und beim Scrollen/Detailöffnung nachladen, bestehende geprüfte Cachetreffer nutzen. Kein Download ganzer Film-/Serienkataloge beim Kodi-Start. Film↔Serie-Reihenabstand verkleinern; Höhe/Fokusrahmen des Posterkachels nicht verrutschen lassen.

### B4 – Star Trek, XMLTV und Serien-Fallback sauber abstimmen

1. Für **„Star Trek: Deep Space Nine“** und andere bekannte Serien begrenzten, asynchronen **verified series fallback** prüfen: eindeutige Serienidentität (einschließlich nachweisbarer offizieller Namensvarianten, Sprache/Jahr) → TV-Backdrop/Poster von TMDB oder TVMaze; `series_fallback` klar kennzeichnen. Ohne Staffel-/Folgenbeweis **kein erfundenes Episodenstandbild**.
2. `tmdb_epg60.py`, `programme_tv66.py`, `programme_tvmaze67.py`, `programme_sources57.py` auf Einstufung/Mismatch und Opt-out-Status untersuchen. Bestehendes striktes Match nicht pauschal lockern; stattdessen fest codierte anonymisierte Diagnosegründe.
3. XMLTV-Eventbild bei exakter Sendungszuordnung erhalten; bei Hochformat-Bild in Details gerne Portrait, im Hero contain statt Verzerren. TMDB-Serienbild als Alternativ-Backdrop nur, wenn korrekt zugeordnet und Qualitätsrolle passend.
4. `KODI_LIBRARY_MISSING_VIEWS` **nicht** als Endnutzer-Hero-/Detailtext darstellen. Kodi `MyVideos131.db` nur read-only diagnostizieren, keine DB-Löschung/Neuanlage. TMDB/TVMaze/XMLTV-Suche darf nicht vom defekten Bibliotheksschema abhängen.

### B5 – Dynamic/Reference-first bleibt verbindlich

- EPG-Eintrag importieren → TMDB/TVMaze/XMLTV **nur geprüfte Bild-Identität/URL-Metadaten** asynchron mit Deduplizierung und Backoff ermitteln; keinen Massendownload beim Import.
- Auf Home zunächst **maximal fünf sichtbare Sendungsbilder** priorisieren (Senderlogos separat), bei Fokus 1..5→2..6 nur Nummer 6 nachladen. Bei Rücknavigation vorhandenen gültigen Cache verwenden; aktive Eventbindungen vor Ablaufräumen schützen.
- Neu verwalteter temporärer XCMate-Bildcache mit hartem Byte-/Objektlimit, LRU, TTL/Sendungsende+Grace. Keine pauschale Löschung historischer Artwork-Dateien oder Kodi `Textures13.db`/`Thumbnails`. Kodi-Texturcache getrennt messen.
- Keine neue Cloud-Anbindung, keine Veränderung gespeicherter Provider/TMDB/EPG/Favoriten/Personal-Skin/Box A. Keine neuen .84-Parallelbranches.

## C. Code-Anker für gezielte sichere Änderung

- `src/plugin.video.xtreammate/resources/lib/widget_skin84.py` hat zum Stand 09.11. **exakt**: `XCMate50.Hero` (Gruppenhöhe 540), Bildheight 520, Panel 520, `IncludesHomeBingie.xml` Rail top 540; `verify()` prüft diese Werte. Änderungen nur über **bekannte owned Nodes, Digest-/Backup-/Rollback-Schutz** und mit aktualisierten Geometrie-Kontrakttests. **Keine globalen/persönlichen Skin-XML-Veränderungen**.
- `widget_skin81.py` enthält `XCMate81.PosterRow` (u.a. Posterrahmen/Fokus/Text) und ältere Rail-/Reihengeometrie. Hier prüfen, warum der große Film↔Serien-Abstand besteht; Layoutfenster nicht blind überlagern.
- `widget_art44.py` und `widget_assets69.py`: Poster-/Fanartquellen und genehmigte Anzeige-URIs, besonders im gespeicherten Artwork-Modus bei Reserve-Druck.
- `tmdb_epg60.py`, `programme_tv66.py`, `programme_tvmaze67.py`: Eventklassifikation, exakter Match, series_fallback. XMLTV-Quelle im Programmresolver.
- `programme_widgets46.py`, `widget_skin84.py`: richtige Quelle, Senderlogo-Fallback, Now/Next-Panel und BINGIE-Skin-Eigenschaften.

## D. Prüfmatrix / Definition of Done

| ID | Nachweis auf **Box B** | Mindest-Status |
|---|---|---|
| VIS84-01 | Kaltstart und Warmstart: echte Logos schnell; Startsenderlogo im Hero bis korrektes Eventbild erscheint, keine leere Fläche. | ANDROID_NOT_TESTED, bis Screenshot |
| VIS84-02 | TMDB-positiv **Im Reich des Blauwals**: richtiger widescreen-Hero plus Attribution und EPG, keine Bildverwechslung, 1080p. | ANDROID_NOT_TESTED |
| VIS84-03 | XMLTV **Entschlüsselt** (Portrait) und **Alle unter einem Dach**: keine verzerrten Gesichter; Detail-/Hero-Aspekt korrekt. | ANDROID_NOT_TESTED |
| VIS84-04 | **Star Trek: Deep Space Nine**: exakter Serien-Fallback wird versucht; falls verifiziert, korrekter Backdrop/Poster; sonst begrenztes SYFY-Logo und klarer Diagnosegrund, keine erfundene Episode. | ANDROID_NOT_TESTED |
| VIS84-05 | Film- und Serien-Widgets: sichtbare echte Poster/Fanart statt ausschließlich Play-Symbolen, richtige Medienzuordnung, keine Credentials in URL. | ANDROID_NOT_TESTED |
| VIS84-06 | Hero deutlich größer; horizontale Senderlogos/Filmreihe tiefer; **geringerer Abstand** Film↔Serie; scroll-, fokussier- und navigierbar. | ANDROID_NOT_TESTED |
| VIS84-07 | Rechte EPG-Tafel: Text auf hellstem Whale-/XMLTV-/Logo-Motiv gut lesbar, Uhrzeit/Now/Next/Progress vollständig und ohne Überschneidungen. | ANDROID_NOT_TESTED |
| VIS84-08 | EPG-Viewport 5→6 und zurück: keine Massendownloads/vertikale Layoutsprünge; passende Bilder und begrenzter Cache. | ANDROID_NOT_TESTED |
| VIS84-09 | `KODI_LIBRARY_MISSING_VIEWS` nicht im Endnutzerbild; Kodi-Datenbank unangetastet, separate Provider-Images unabhängig. | ANDROID_NOT_TESTED |
| VIS84-10 | Regression: Player start/exit, Back, Fokus, Skin-Safe Upgrade-Rollback, EPG, Serien-/Film-Details, Offline/Reload. | ANDROID_NOT_TESTED |

**Codex-Lieferung:** Änderungen im **bestehenden** PR #405 mit Testbericht, aktualisierten Screenshots von Box B erst bei realer Durchführung, ZIP+SHA256 neu erstellen wenn Code geändert, CI/Hosttests dokumentieren und ehrliche PASS/FAIL/NOT_TESTED-Tabelle. **Kein Merge nach main, kein Release auf Pilot/Original/NeoDark3 ohne separate Nutzerfreigabe.**
