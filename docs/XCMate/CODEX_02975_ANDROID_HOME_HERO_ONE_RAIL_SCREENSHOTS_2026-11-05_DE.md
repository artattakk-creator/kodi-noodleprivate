# XCMate 0.1.29.75 – verbindlicher Android-UI-/EPG-Reparaturauftrag aus 6 Screenshots

**Datum:** 05.11.2026  
**Zustand:** Nachweis auf Kodi 21.3 Omega / Android ARM32 RK3528 / Titan BINGIE MOD 2.2.3 / Space Blue, XCMate 0.1.29.74. **Nur Diagnose/Auftrag; noch keine Reparatur und keine Android-Abnahme.**  
**Mutterissue:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/367  
**Event-Artwork:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/366  
**Live-TV-Exit:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/368  
**Auslieferung:** kumulativ auf 0.1.29.74 aufbauende 0.1.29.75; zunächst Pilot/Test, erst nach Gerätefreigabe regulär.

## 1. Evidenz aus sechs Nutzerfotos, in dieser Reihenfolge

**Foto 1 – Live-TV-Home (###### GERMANY HEVC ######):** Links im Hero erscheint nur ein blaues generisches Bild-Platzhaltersymbol. Rechts „Keine Programminformationen“, „JETZT“ mit leerem Balken und leeres „Danach“. In der horizontalen Live-TV-Leiste stehen abgeschnittene Sendertexte („DE| PROSIE…“, „DE| RTL…“) statt erkennbarer Senderlogos. Sendungsinformationen sind laut Nutzer nach langem Warten teilweise vorhanden, beim Kaltstart jedoch nicht sofort. Der Live-TV-Sender muss hierfür **nicht** zuerst getuned werden. Gruppentitel und ausgewählter Sender dürfen nicht als einander ersetzbare Identitäten verwendet werden.

**Foto 2 – Auswahl „Filme“, danach „Serien“:** Hero-Überschrift zum Film („Rojas Garcia (2026)“) erscheint, während rechts nur ein generischer Platzhalter statt einem vorhandenen Film-Artwork zu sehen ist. Unter dem Hero sind gleichzeitig Film- und Serien-Cover-Zeilen; der türkise Fokusrahmen hängt am ersten Seriencover, zum Teil über dem vorigen Filmcover, und fokussiertes Hero-/Cover-Item sind nicht erkennbar synchron. Filme-Cover an sich existieren – also bei Hero nicht einfach behaupten, Provider hätte kein Artwork.

**Foto 3 – Serien → „Im Kino“:** Hero-Text „DE - Loki (2021)“ steht oben, während der Fokusrahmen tiefer in/um das erste „Im Kino“-Cover liegt; Hero-Identität/Fokus stimmen nicht sicher überein. Wieder stehen mehrere Carousel-Zeilen übereinander und drängen den Hero nach oben.

**Foto 4 – „Im Kino“, Titel „Wildwood“:** Verifiziertes großes Hintergrundbild ist oben vorhanden; trotzdem überlagern sich die Film-Beschreibung, die Zeilenüberschrift „Im Kino“ und das erste Cover. Der Hero ist zu stark beschnitten, die Informationen sind nicht vollständig lesbar. Eine einfache erfolgreiche Bild-URL ist folglich **nicht** gleichbedeutend mit korrekter Hero-Geometrie.

**Foto 5 – Trend → „Disney Plus“:** Im Hero „DEAD-END JOB“ mit Hintergrundbild; die Beschreibung liegt teilweise über „Diese Woche im Trend“ und den Postern. Der Fokusrahmen sitzt zu tief und grenzt die neue Zeile anstatt das aktive Poster sauber ein. Weiteres Scrollen verkleinert den Nutzbereich sichtbar.

**Foto 6 – linkes Hauptmenü geöffnet:** Früher unterschiedliche Icons der vertikalen Navigation sind als sehr kleine, immer gleichartig wirkende Artefakte/Platzhalter sichtbar. Die horizontale Leiste mit Sender-/Providerbezeichnungen und Filmcovern läuft optisch durch andere Bereiche; Hero und Side-Menu stimmen in der Darstellung nicht sicher überein. Beim Öffnen/Schließen der Navigation dürfen keine alten Widget-Zeilen hinter fremde Bereiche durchscheinen. Detailhinweis: Der Nutzer meint mit „Provider-Icons“ zugleich sichtbar fehlende Senderlogos in der horizontalen Live-TV-Zeile; nach tatsächlicher Datenquelle für jedes Bild unterscheiden.

**Keine Fotos/Logs im öffentlichen Repo enthalten:** Nutzer hat Bilder privat im Chat geschickt. Oben werden nur die sichtbaren Sachverhalte dokumentiert; keine user-/gerätebezogenen Bilddateien oder URLs veröffentlichen.

## 2. Verbindlicher UX-Vertrag – **EINE AKTIVE RAIL**

Der Nutzer möchte **nicht zwei gleichzeitige Cover-Zeilen** auf der Startansicht. Das gewünschte Navigationsmodell ist:

1. Links Bereiche: **Live-TV (XCMate), Filme, Serien** sowie bestehende übrige Einträge. Ein Fokus-/Klickwechsel auf einen Bereich zeigt **nur die zu diesem Bereich gehörende aktive horizontale Cover-/Senderzeile** direkt unter dem Hero. Unterkategorien/weitere Empfehlungen sind über Navigation/Unterauswahl erreichbar, nicht als konkurrierende dauerhaft sichtbare Reihen auf derselben Ebene.
2. Ein einziges fokussiertes Element steuert **synchron** Hero-Bild, Titel, Beschreibung, Quelle, Jetzt/Danach bzw. Metadaten. Keine alte Hero-Identität nach Kategorienwechsel, Scroll, Cache-Miss oder verzögertem Ergebnis.
3. Der Hero bekommt ein **stabil reserviertes Rechteck** vom oberen sichtbaren Bildschirmrand bis knapp oberhalb der aktiven Rail. Beim vertikalen Wechsel **nicht schrumpfen, springen oder fortschreitend beschneiden**. Kein Poster/Header/Text darf in die Rail hineinragen.
4. Aktiver Fokusrahmen **itemlokal** (an exakt dem Cover-/Sender-Icon), richtige Y-Koordinate, gleiche Höhe wie aktives Item (ggf. gewünschter Fokuslift nur für aktives Poster). Kein doppelter globaler Rahmen oder Rahmen auf benachbarten Reihen. Beim Seitenmenü-Öffnen den aktiven Fokus auf die richtige Ebene setzen und Overlays eindeutig priorisieren.
5. Nicht nur XCMate-Widgetpfade prüfen, sondern das tatsächlich installierte BINGIE-/Space-Blue-Home-Layout, die jeweilige Skin-Revision, Include-Order und die aktuelle Widget-Definition/Skinkonfiguration.

## 3. Hero-Visuals – flächiges Bild plus lesbare, leichtere Info-Karte

- Hero **flächig** mit dem zum aktuell fokussierten Film/Serie/Sendung passenden Fanart/Backdrop. Bilder aus Film-/Serien-Provider-Metadaten bevorzugen; TVMaze/TMDB nur bei entsprechend verfügbarer zulässiger Sekundärquelle und bereits erteilter Datenübermittlungsfreigabe. Bei Live-TV: XMLTV/Provider-Ereignisbild zuerst, TMDB/TVMaze oder geeignete andere zugelassene Quellen mit sicherem Event-Matching und Opt-in. Kein irreführendes Bild.
- Wenn nur ein Hochkant-Poster und kein breites Fanart vorhanden ist: gestalterisch vollflächigen Hero-Hintergrund mit sauberer Skalierung/neutraler Blur- oder Verlaufsebene, **Poster sichtbar und unverzerrt**; niemals vorhandenes Poster durch ein riesiges leeres Platzhaltersymbol ersetzen. Kein unästhetisches Stretching oder übermäßiger Gesichtsbeschnitt.
- Die rechte/seitliche Informationskarte aus Foto 1 **erhalten**, aber **etwas transparenter** (Kontrast weiterhin lesbar). Darstellung darf als dunkler halbtransparenter Verlauf/Glass-Overlay auf das Hero-Bild gelegt werden, ohne das volle Bild zu verdecken.
- Live-TV-Karte: kleines Senderlogo, eindeutiger **Sendername** (keine Gruppenkennung), **Jetzt**: Titel, Start–Ende, Fortschritt/Restzeit, Untertitel, kurzer Beschreibungstext; **Danach**: Titel/Startzeit. Sofern vorhanden EPG-Genre, Produktionsjahr, Darsteller, Inhaltsangabe und verwendete Artwork-Quelle. Fehlende Felder weglassen statt falsche/alte Werte zeigen. Auch bei fehlendem Bild **EPG-Text nicht blockieren**.
- Film-/Serien-Karte: Titel, Jahr, Genre, Laufzeit/Staffel, Inhaltsangabe und verfügbare Cast-/Altersfreigabe-/Bewertungsdaten (nur wenn sicher vorhanden); Provider-Infos nicht durch andere Serien-/Filmdaten ersetzen. Eine klar lesbare kleine Attribution **„Bild: Provider / TMDB / TVMaze / XMLTV“** nur für tatsächlich genutzte Quelle, kein dekoratives falsches Anbieterlogo. Quellenanzeige kann Icon + Text sein, wenn lokale lizenzierte Assets vorliegen.
- Bildschirm 1920×1080 sowie 1280×720, lange deutsche Titel, Umlaut/Fallback-Fonts, Untertitel und lange Beschreibungen layouten; text wrapping/maxlines/ellipsize statt in Rail ragen.
- Das gleiche Hero-Konzept bei direktem Start, horizontalem Focus-Scroll, vertikalem Kategorienwechsel, Seitenmenü auf/zu und nach Kodi-Restart/Refresh.

## 4. P0 Datenpfad – EPG/Logos sofort nutzbar ohne Live-TV-Tuning

- Die Diagnose aus #367 ist aktiv: `EPG_DATA_MISSING`, `EPG_CACHE_UNAVAILABLE`, `EPG_DB_BUDGET`, `EPG_READ_TIMEOUT`, `NATIVE_HOME_UNVERIFIED`, `REFERENCE_PARTIAL`, `BLOCKED_NO_RELOAD_HOOK`, `Non-Existent Control 296301`; `movie_view/tvshow_view` fehlen im Kodi-DB-Schema. Nicht behaupten, jedes leere Bild müsse denselben Ursprung haben.
- EPG **aus lokalem atomarem Cache-Snapshot** zu Kodi-Home und Startgruppe vorladen; Datum/Zeit/Zeitzone/Provider-Mapping und event_id prüfen. Für jede station den tatsächlichen Jetzt/Nächste-Datensatz holen, **auch wenn nie getuned wurde**. Nach vollendetem Refresh Snapshot atomar umschalten und aktuell sichtbare Properties aktualisieren.
- `hero_epg63.py`: Fehlt Control `296301`/`296302`, darf `getControl().setPercent` die komplette Text-/Bildpublikation **nicht verhindern**. Sicherer fallback: Text/Quelle/Identität committen, Progress-Balken optional/ohne Bild blockierende Ausnahme; aber keine vermischten Generationen. Kontrolliere Original-Bank-Publikation und gültige Skin-Control-ID.
- Keine HTTP-/DNS-/SQL-Langläufer auf Kodi UI-/Fokus-Thread; Hintergrundvorladung (EPG, Artworks, Logos, Metadaten) begrenzt und priorisiert auf sichtbare Startgruppe. Bereits korrekt vorhandene Texte/Cover/Logos bei flüchtigen Timeout/Budget-Warnungen erhalten, nicht flackern/leer setzen. Erneute Verfügbarkeit nach Quelle/Mapping-/Opt-in-Änderung. Kein unnötiges Bild-Nachladen pro Focuswechsel.
- Horizonte: vorhandene 7 Tage rück/20 Tage vor DB-Strategie und tägliche 24-h-Erneuerung erhalten, soweit tatsächlich konfigurierte Quellen solche Daten liefern; keine erfundenen Termine.
- Live-Leiste: 1 kleine Logo-Kachel **pro Sender** der Startgruppe, horizontal scrollbar; korrekte Kodi-Texture-Sichtbarkeit und Image-Path/Provider-Mapping prüfen. Logo-Fallback zu lesbarem Sendertext nur wenn Logo für diesen Sender nachweislich fehlt; Logofehler separat diagnosieren (URL, Cache, Binding).
- EPG-/Art-Test auf **mehreren nicht zuvor wiedergegebenen Sendern** nach Kaltstart, danach 1/5/15/60 Minuten, Senderwechsel, mit/ohne Opt-in. Gemessene Latenz vom Home-Aufruf bis EPG-Text und Artwork getrennt loggen.

## 5. Links-Menü und Focus-Regressionspfad

- Icons der einzelnen Navigationspunkte wieder spezifisch und funktionierend: nicht mehrfach die gleiche unlesbare Platzhaltergrafik. Prüfe Skin-Icon-Sheet, Korrektheit der Texture-Pfade, Space-Blue-Asset-Installation, Includes, SkinShortcuts und Fokus-/Selection-States.
- `widget_skin74.py` ist ein **optionaler** Fokus-Adapter; es ist nicht bewiesen, dass dieser auf der betroffenen Box aktiviert oder zum installierten Skin-Hash kompatibel ist. Vor jeder XML-Modifikation **read-only** Skin-Hash, aktives Include und tatsächliche Frame-Controls erfassen. Patch nur mit bestehender Zustimmung/Backup/Revert, nicht stillschweigend bei Update überschreiben.
- `IncludesXCMate64.xml` LiveRow nutzt `XCMate.ProgrammeLogo46` im <image>-Texture-Property und `XCMate.ProgrammeChannel46` als Label; prüfen ob bei leeren Logos die Property leer, verboten/abgelaufen oder die Texture-Route fehlerhaft ist.
- `home_publication74.py` und `widget_refs74.py` dürfen bei transientem Artwork-Status die stabile Liste und verifizierte Cover nicht verlieren. `widget_focus41.py` bindet EPG an ausgewählten Live-Sender; Film-/Serien-Hero muss seine **eigene Medienidentität** statt Live-EPG-Werte erhalten.
- Im tatsächlich geladenen Layout CSS/XML-(Kodi Skin)-Maße vergleichen: Fokus-Y, `focusedlayout`-Objekt, `itemlayout`, `posx/posy`, Menü-Safe-Area, `visible`-Konditionen, Texture-/Overlay-Z-Order, Scroll-Animation, Film-/Serien-Unterkategorien; keinen pauschalen negativen Y-Offset, der nur ein Foto kaschiert.
- Konflikte mit bereits vorhandenen Kodi-Skin-Bindings/Space Blue UI vorzugsweise per reproduzierbar versionsgebundenem, rücksetzbarem Integrationspatch vermeiden.

## 6. Tests und Abnahme – nicht nur XML-Validierung

| ID | Prüffall | PASS-Kriterium |
|---|---|---|
| H75-01 | Kaltstart Home direkt auf Live-TV | Jetzt/Nächste für EPG-gedeckten Startsender ohne Wiedergabe, Senderlogos sichtbar, EPG-Text nicht von Artwork abhängig |
| H75-02 | Live-TV Fokus 10+ Sender, inklusive ohne Sendungsbild | Korrekte Titel/EPG-ID, unveränderte korrekte Logos, keine Fremdfanart, Fokus kein falsches Item |
| H75-03 | Wechsel Live-TV → Filme → Serien | Exakt 1 aktive Zeile; keine früheren Zeilen sichtbar; Hero/Poster/Metadaten atomar zum fokussierten Item |
| H75-04 | Horizontal 20+ Cover scrollen | Hero-Backdrop/Poster aus passendem Provider-Datensatz; Bild bleibt sichtbar und wechselnd, auch bei Cache-Miss nicht unnötig leer |
| H75-05 | Vertikal 20+ Navigations-/Unterkategorieschritte | Hero-Rechteck und Overlay behalten konstante Geometrie, keine Überschneidung mit Überschriften oder Covern |
| H75-06 | Fokusrahmen | Exakt ein Rahmen am wirklich fokussierten Element; kein Rahmen 50–150 px unter/zwischen Zeilen, kein verwaister Focus |
| H75-07 | Seitenmenü auf/zu | Alle unterschiedlichen Icons sichtbar, keine durchscheinenden falschen Reste von Live-/Film-Widgets |
| H75-08 | Real-Bild-Zuordnung | Film, Serie und EPG-Sendung je mit korrekter Quelle und passendem Poster/Backdrop; klare Attribution, keine falschen Titel |
| H75-09 | EPG-Wiederkehr und Offline | Snapshot bleibt stabil bei Timeout; Home startet ohne Tune, Fortschritt und Nachfolge nach Wiederherstellung korrekt |
| H75-10 | Android-/Kodi-Regression | 1920×1080 und 1280×720, Kodi 21.3, RK3528, 60 Minuten aktives Home/Scroll, Restart, keine Speicher- oder Profilverluste; Live-TV-Exit #368 separat weiter testen |

Zielwerte messbar vereinbaren: Warm-Cache-Home EPG-Text möglichst im ersten Home-Frame oder unter 2 s; beim Kaltstart für alle EPG-gedeckten Startgruppen-Sender ohne erzwungenes Tuning vorbereiten; tatsächliche Zeiten im Android-Log erfassen. Bild-Download darf Text nicht blockieren. **Synthetische Bilder, simulierte Eventdaten oder Einzelfälle reichen nicht als Android-PASS.**

## 7. Nicht verhandelbare Daten-/Release-Guardrails

- **Keine Neuinstallation/Reset** von Kodi, XCMate, XMLTV, EPG-Mapping, Caches, Fav-/Profil-/Providerdaten, TMDB-Token, SkinShortcuts, Space-Blue-Branding, Intro, Kodi-DB.
- Kein Auslesen oder Publizieren von geheimen Token/Provider-/Stream-URLs oder Nutzerbildern ins öffentliche GitHub-Repo.
- Drittanbieter-Artwork-Matching nur unter den bestehenden Freigaben und quellengebunden, nie stillschweigende Provider-Titeldatenübermittlung an externe Dienste.
- Kumulativer Versionspfad `.74 → .75`, mit Version, ZIP, SHA256, Tests und dokumentiertem Rückweg; zuerst Pilot-Testrepository. **Regulären Katalog vor Android-Freigabe nicht verändern.**
- Issues #366 (Live-/EPG-Art), #367 (allgemein Home/EPG/Hero), #368 (Live-Exit) zusammen in .75 integrieren; Installer 0.5.22 / Pilot-Quelle / Space Blue Installation als eigenständigen Track beibehalten. Keine offenen P0 unbemerkt überspringen.

**Definition of done:** Zwei unmittelbar nacheinander von derselben Android-Testbox aufgenommene Belege: (a) Live-TV-Hero mit sichtbar korrekter EPG-Information und Sendungsbild bei zuvor NICHT getuntem Sender und (b) Filme/Serien mit einzigem aktiven Rail, korrektem Hero, Fokus und Navigation, 20-mal scrollen ohne Überlagerung; vollständig erkennbarer Fokusrahmen und Quelle im Overlay. Android-Nachweis separat vom Host-/CI-Nachweis ausweisen.
