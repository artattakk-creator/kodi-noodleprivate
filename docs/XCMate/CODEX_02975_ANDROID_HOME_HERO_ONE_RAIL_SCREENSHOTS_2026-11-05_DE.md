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

## 3. VERBINDLICHE KORREKTUR 05.11.2026 – LINKS GROSSES BILD, RECHTS EXKLUSIVE INFO-TABELLE

> **Dieses Kapitel ersetzt alle früheren allgemeinen Angaben über eine frei platzierbare Informationskarte.** Ausdrückliche Nutzerentscheidung: **Ausschließlich die RECHTE Hero-Seite** darf lange Beschreibungen, EPG-/Filmdetails, Fortschrittsanzeige und Quellenlogos enthalten. **LINKS möglichst nur das großflächige Bild**, allenfalls mit einem dezent eingeblendeten Titel. Die bestätigte **eine aktive horizontale Sender-/Cover-Leiste** direkt darunter bleibt bestehen.

### 3.1 Verbindliches Anordnungsmodell

```text
┌────────────────────────────── HERO, konstante Höhe ──────────────────────────┐
│   BILD LINKS (ca. 67 %)            │   INFO-TABELLE RECHTS (ca. 33 %)       │
│                                    │                                         │
│                                    │  [Senderlogo] Sender / Filmtitel       │
│   GROSSES, KORREKTES FANART        │  Jetzt       Titel / Zeit / Restzeit  │
│   ODER FORMATGETREUES POSTER       │  Fortschritt ████████░░░░░            │
│                                    │  Danach      Titel / Startzeit        │
│   [optional: dezenter Titel]       │  Inhalt      mehrzeilige Beschreibung │
│                                    │  Details     Genre / Jahr / Cast etc. │
│                                    │  ──────────────────────────────────── │
│                                    │  Bild: [TMDB] [TVMaze] [Provider]     │
│                                    │  (nur tatsächlich genutzte Quellen)  │
├──────────────────────────────────────────────────────────────────────────────┤
│ EINE AKTIVE HORIZONTALE ZEILE: Senderlogos ODER Filmcover ODER Seriencover │
└──────────────────────────────────────────────────────────────────────────────┘
```

- Hero-Rechteck **großflächig und in fester Höhe**, auch bei wiederholtem vertikalem Scrollen. Die eine horizontale Rail sitzt unterhalb; keine zweite gleichzeitige Cover-Reihe, keine schwebenden Überschriften oder Cover im Hero.
- Anfangswerte bei 1920×1080: linke Bildfläche ungefähr **66–70 %**, rechte Tabelle **30–34 %** der verfügbaren Hero-Breite. Für 1280×720 an reale Safe-Areas und Schriftgrößen anpassen; **keine starren Y-Pixelwerte** ohne gemessene Skinkoordinaten. Das Hintergrundbild darf hinter dem rechten Panel weiterlaufen, aber links darf **kein Tabelleninhalt** hineinragen.
- **Links** nur das thematisch korrekte breite Fanart/Backdrop bzw. ein unverzerrtes Poster mit gestaltetem farblich passendem Hintergrund. Falls gewünscht höchstens ein dezenter Titel am unteren Bildrand. **Ausgeschlossen links:** Beschreibung, Tabellenzeilen, „Jetzt/Danach“, Progress-Balken, Cast-Liste, TMDB-/TVMaze-Logos, große dunkle Infobox.
- **Rechts** eine optisch **tabellarisch gegliederte** Informationsfläche (Kodi-Skin-XML-Gruppen, zweispaltige Label/Wert-Zeilen und Textboxen; kein HTML erforderlich). Dunkel und **etwas transparenter als bisher**, vorgeschlagener Anfangswert ca. 60–75 % Deckkraft, bei gleichzeitig verlässlich lesbaren Texten. Space-Blue-Farben verwenden. Ein transparenter Verlauf an der linken Panelkante ist zulässig; nicht die linke Motivfläche abdunkeln.
- Panel muss in der festen Hero-Höhe bleiben: lange Titel und Beschreibungen in der **rechten** Box begrenzen/scrollen, nicht über Poster, Rail oder Quellenleiste malen. Wenn links ein Titel steht, darf die rechte Tabelle ihn im Header gern wiederholen, aber es dürfen nicht zwei unkoordinierte Titel-Layer überlappen.
- Kategorie- und Fokuswechsel müssen **atomar Bild, Tabelleninhalt, Quellenbeleg und Identity** wechseln. Keine Hero-Daten von altem Film/Sender bei Fokus auf neue Reihe; keine grenzüberschreitenden oder verschwundenen Elemente, auch wenn das Seitenmenü geöffnet wird.

### 3.2 Inhalt der rechten Tabelle je Hauptbereich

**Live-TV:** Tabellenkopf **echter Sendername und Senderlogo**, niemals nur der Gruppenname wie `###### GERMANY HEVC ######`. Gruppe **JETZT** mit Sendungstitel, Sendezeit, Restzeit, Fortschritt und Beschreibung; Gruppe **DANACH** mit nächstem Titel/Startzeit; danach nur belegte weitere Angaben: Untertitel, Genre, Jahr, Mitwirkende, Beschreibung. Die Live-EPG-Daten müssen **ohne vorherigen Senderstart** aus dem lokalen Snapshot geladen und sofort rechts gezeigt werden; der eventuelle Bildabruf darf Text niemals blockieren.

**Filme:** Rechts Titel, Jahr, Genre, Laufzeit, Altersfreigabe, Bewertung, Beschreibung, Cast, soweit Provider tatsächlich solche Fakten liefert. Links passendes breites Provider-Fanart oder qualitätsbewusstes Poster-Fallback. Vorhandene Provider-Bilder nicht durch ein generisches Bildsymbol ersetzen; externes TMDB/TVMaze nur, wenn passend und bereits erlaubt.

**Serien:** Rechts Titel, Jahr, Genre, Staffeln/Episoden, Beschreibung, verfügbare Mitwirkende und Bewertung; nur zum fokussierten Eintrag passende Daten. Links das korrekte Serien-/Episodenbild, nicht alte Film-/Live-TV-Identität.

Bei fehlenden Daten Felder ausblenden oder klar als unverfügbar kennzeichnen; keine erfundenen Inhalte oder fälschlichen Bewertungen. Die Informationstabelle ist **immer ausschließlich rechts**.

### 3.3 Feste Bildquellen-/Metadaten-Attribution im unteren RECHTEN Panel

Der Nutzer wünscht ausdrücklich **TMDB- und TVMaze-Logos**, falls diese Dienste genutzt wurden. Reserviere deshalb im **unteren Bereich der rechten Tabelle** einen kleinen eigenen Quellenstreifen, der auch bei langen Beschreibungen sichtbar bleibt.

- Visuell lesbare Logos **nur bei wirklich verwendeten, nachgewiesenen Quellen**. `Bild: TMDB`, `Bild: TVMaze`, `Bild: Provider`, `Bild: XMLTV`; separat `Daten: TMDB / TVMaze`, wenn darüber **Metadaten** statt Bilddaten stammen. Bietet die jeweilige Quelle keine Bild- oder Datenreferenz, **kein Logo nur als Dekoration** anzeigen.
- Original-/Branding- und Lizenzanforderungen für TMDB/TVMaze vor Verwendung von Logo-Assets prüfen; lokal gebündelte erlaubte Assets, **keine renderkritischen Logo-Hotlinks**. Falls Asset fehlt oder Nutzung unklar, gut lesbare **Textattribution** statt Fantasielogo. Die Nennung ist keine Partnerschaftsempfehlung.
- Quellenidentität zusammen mit Event-/Medien-ID, Titel, Art-Key und Cache-Generation **atomar** publizieren. Kein TMDB-Logo am aktuellen Providerbild allein weil ein früherer Sender TMDB benutzte. Bei mehreren tatsächlich genutzten Quellen konkrete Rolle zeigen; ungenutzte Logos ausblenden.
- Provider-Artwork bei Filmen/Serien priorisieren; Live-TV: XMLTV/Provider-Eventbild, erst danach korrektes TMDB-/TVMaze-Matching **unter bestehendem Opt-in**. Vorhandener TMDB-Token allein ist **keine aktive Einwilligung** zur Drittanbieter-Anfrage.
- **Keinerlei Logos auf der linken Hero-Bildfläche**. Quellenstreifen niemals über Cover-Leiste oder Live-TV-Fokus legen; Höhe innerhalb der rechten Tabelle reservieren.

### 3.4 Implementierungshinweise und Abnahmetests

Die bisherige Analyse aus #367 bleibt verbindlich: `hero_epg63.py` darf bei fehlendem Control `296301/296302` nicht die gesamte Text/Bild-Property-Publikation abbrechen; `IncludesXCMate64.xml` bindet Senderlogos an `XCMate.ProgrammeLogo46`, Titel an `XCMate.ProgrammeChannel46`; `widget_skin74.py` ist optional und deshalb der aktive Skin-Hash/Adapterzustand **read-only** zu prüfen. `home_publication74.py` muss vorhandene verifizierte Referenzen bei flüchtigen Cache-Fehlern behalten. Tatsächliche BINGIE-MOD-/Space-Blue-Includes und Z-Order prüfen statt ungefragt globalen Skin überschreiben.

| Test-ID | Szenario | Harte PASS-Regel |
|---|---|---|
| HERO75-R1 | Live-TV nach Kaltstart **ohne Senderstart** | Links korrektes Bild oder plausibler sicherer Fallback; rechts **alle verfügbaren Jetzt/Danach-Daten** und echte Senderidentität |
| HERO75-R2 | Film mit Fanart | Links nur Bild (+ optional Titel); **sämtliche ausführlichen Details nur rechts**; genau eine Filmcover-Zeile |
| HERO75-R3 | Film nur mit Hochkantposter | Links Poster unverzerrt auf ansprechendem Hintergrund, keine riesige Ersatzgrafik; Infos rechts |
| HERO75-R4 | Serie und mehrfacher Bereichswechsel | Hero/Tabellenidentität zum Fokus, keine alten VOD-/EPG-Daten, **eine Rail** |
| HERO75-R5 | TMDB- oder TVMaze-Bild-/Datenbeleg | Nur der reale Dienst als kleines Logo/Text im **rechten Panel-Footer**, richtige Rolle; bei reinem Providerbild kein falsches Logo |
| HERO75-R6 | 20+ horizontale/vertikale Scrolls und Seitenmenü auf/zu | Konstante Hero-Höhe, Fokusrahmen exakt am fokussierten Element, kein Beschriftungs-/Zeilen-Überlapp |
| HERO75-R7 | 1920×1080 und 1280×720 | Rechte Tabelle bleibt im Panel, Quelle sichtbar, vollständiges Hauptbild links, Beschreibung/Quelle nie links |
| HERO75-R8 | EPG-Timeout/kein Artwork verfügbar | Bereits vorhandener Eventtext rechts bleibt stabil, kein Leeren/falscher Sender, keine GUI-Blockade |

Als **FAIL** gelten ausdrücklich: ausführliche Texte oder TMDB-/TVMaze-Logos auf der **linken** Bildseite, gemischte Film-/Serien-Poster-Reihen, schrumpfender Hero, nach unten verschobener Rahmen, Symbol-Platzhalter trotz vorhandenem Poster, veraltete Daten/Quellenlabels, fehlende EPG-Texte bis zum ersten Tune. **Synthetische Renderings sind kein Android-PASS.** Auf der echten Kodi-21.3-Box Screenshots/kurzen Ablauf mit Fokus, einer Rail und stabiler rechter Tabelle erfassen. Vor Skinänderungen expliziter Backup-/Revert-Schutz. Keine Profildaten/Provider-/Token-/EPG-Mappings löschen.


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


## 8. P0 PRIORITÄTENPIPELINE – EPG zuerst, Senderlogos sofort, zuerst sichtbare 5 Sendungsbilder, Rest progressiv

**Neue ausdrückliche Nutzeranforderung vom 05.11.2026:** Nicht auf einen Live-TV-Tune warten. Sobald die Kodi-/BINGIE-Startseite öffnet, müssen die bereits lokal gespeicherten **Jetzt/Danach-EPG-Daten** und **Senderlogos** der Startgruppe sofort erscheinen. Erst danach soll ein Hintergrundskript für den ausgewählten Sender und die ersten ungefähr **fünf sichtbaren Sender** die zur jeweils laufenden Sendung passenden **Sendungsbilder aus lokalem Cache oder erlaubten Quellen** vorbereiten. Anschließend **weitere Sender progressiv im Hintergrund**, mit Fokus-Vorrang beim horizontalen Navigieren. Die Bilder sollen beim Fokuswechsel bereits griffbereit sein, soweit die Quelle tatsächlich korrekte Bilder liefert. Keine verlässliche externe Bildabdeckung behaupten, wenn z. B. Nachrichten/Sport/unsichere Matches keine zulässige Bildreferenz haben.

### 8.1 Verifizierte vorhandene Module – unbedingt wiederverwenden

- `src/plugin.video.xtreammate/resources/lib/programme_prefetch48.py`: bereitet bereits alle ca. 5 s wechselnde Batches von **8** Startgruppen-Sendern vor (fokussierter Sender plus rotierende andere), Now und auch zukünftige Sendungen, über die vorhandene bounded queue. **Ändern/optimieren, nicht einen zweiten unabhängigen Endlos-Prefetch-Thread starten.** Die bisherige Rotationsreihenfolge garantiert NICHT, dass die ersten sichtbaren fünf beim Start zuerst fertig sind.
- `src/plugin.video.xtreammate/resources/lib/live_warm68.py`: initialisiert erste acht Kanäle aus Live-Katalog mit `local_epg.now_next`; Startsignal aus dem bereits vorhandenen Service-Worker.
- `src/plugin.video.xtreammate/resources/lib/epg_coverage66.py`: `warm(portal,rows)` für ganze Startgruppe aus demselben lokalen Guide, ohne HTTP; diese Aktion muss **vor** schweren Artwork-Requests priorisiert werden, aber UI darf beim Lesen nicht blockieren.
- `src/plugin.video.xtreammate/resources/lib/epg_handoff63.py` und `epg_refresh74.py`: revision-/profil-/sendergebundene RAM-Handoffs, lokaler bounded NowNext-Refresh. Bei EPG-Kaltstart nur lokale Revision lesen, keinen neuen XMLTV-Download oder Tune erzwingen.
- `src/plugin.video.xtreammate/resources/lib/live_home62.py`, `live_items62.py`, `widget_home50.py`: startgruppenbasierte Senderreihenfolge und ListItem-Bau; `XCMate.ProgrammeLogo46` muss bereits beim ersten Widget-Aufbau korrekt auf eine existente, renderbare Logo-Referenz zeigen. `XCMate.ProgrammeChannel46` bleibt textlicher Fallback, falls für diesen Sender wirklich kein Logo existiert.
- `src/plugin.video.xtreammate/resources/lib/programme_requests68.py`: servicegebundene, cross-interpreter sichtbare Event-Intents mit `request(event,priority=True)`, Re-read aus lokalem Eventindex; `drain()` bewahrt Sender-/Profil-/Quellenidentität.
- `src/plugin.video.xtreammate/resources/lib/programme_urls55.py`: vorhandene **maximal 24 Jobs** umfassende Queue, **`priority68=True`**, Urgent-Burst-Fairness, worker-only DNS/HTTP/TMDB/TVMaze und deduplicated Eventjobs. `programme_art46.py` schützt private Bilddateien; Bildcache-Limit konfigurierbar, vorhandene Meta- und Bildreferenzen beibehalten.
- `src/plugin.video.xtreammate/resources/lib/hero_epg63.py`: fokussierten Sender aus RAM lesen, Intent mit Priority senden. Fehler `Non-Existent Control 296301/296302` aus #367 darf **nicht** NowNext/Bild-Fakt-Publikation verhindern.
- `src/plugin.video.xtreammate/resources/lib/programme_settings68.py`: **eigene TMDB-Suche ist standardmäßig deaktiviert**, erfordert `programme_tmdb46=true` **und** `tmdb_research43=true`; TVMaze ebenfalls opt-in über `programme_tvmaze67`. Ein bereits gespeicherter TMDB-Token alleine ist keine gültige Freigabe. Externe Lookups nur unter bestehender expliziter Einwilligung, keine stillschweigende Aktivierung beim Kaltstart.

**Abzugrenzende Ursache:** Ob auf der betroffenen Box EPG-Logos aufgrund fehlender Provider-Bildquelle, Texture-Pfad, fehlender BINGIE-Bindings oder blockierter Hintergrundworker fehlen, muss per sanitizierter Diagnose geklärt werden; die Existenz einer Queue beweist nicht, dass sie am Android-Gerät durchläuft oder dass Kodi die Bildreferenz tatsächlich anzeigt.

### 8.2 Erwartete Startreihenfolge als nicht-blockierende Zustandsmaschine

**PHASE 0 – bereits persistierte Daten sofort ausgeben (keine Netzanforderung auf GUI-Thread):**
1. Active profile/portal/start_group aus unveränderten User-Settings bestimmen. Bei Startseite bestehendes revisionsgebundenes, zuvor gültiges **lokales EPG-Snapshot** für `JETZT`/`DANACH` lesen, falls vorhanden; in die rechten Hero-Info-Felder veröffentlichen, **bevor** Artwork versucht wird. Bei noch laufendem erstem Lesen nur neutrale Ladeanzeige rechts, keine erfundenen/alten Fremdsenderdaten.
2. Die gesamte geordnete Startgruppen-Senderliste und korrekte Senderlogos aus vorhandenen lokalen/metadatengebundenen Bildreferenzen rendern. Senderlogoreferenzen unabhängig vom EPG-Artwork behandeln: Bildfehler darf die Senderliste/Logos nicht entfernen.
3. `PROFILE_ID, PORTAL_ID, GROUP_ID, CHANNEL_ID, EVENT_ID/start/end, GUIDE_REVISION, SOURCE/MAPPING_REVISION` der Anzeige erfassen. Nur Daten mit passender Identität veröffentlichen. Atomares Update, ohne bei transienten Budget-Timeouts ein gültiges Bild/EPG leerzuräumen.

**PHASE 1 – vorrangiger EPG/Logo-Warmup im Hintergrund:**
4. `epg_coverage66.warm` / `local_epg.now_next` für Startgruppe durchführen; erste 5 sichtbare Stationen sofort aus lokalem DB-Snapshot in RAM-Handoff seeden, danach gesamte Gruppe in begrenzten Batches (bis 16 bei bestehendem Reader); kein gleichzeitiger Vollimport auf GUI-Thread. Die tägliche externe XMLTV-Aktualisierung läuft separat; **erst eine vollständige neue Guide-Revision atomar umschalten**. Kein Warten auf einen neuen EPG-Download, wenn bereits ein gültiger Snapshot existiert.
5. Logo-Textur-Routen vor Veröffentlichung prüfen (Datei/URL zulässig und renderbar); ungültige Logo-Quelle separat diagnostizieren. EPG-Text und Logo müssen **ohne Tune** erscheinen.

**PHASE 2 – PRIORITY: fokussierter plus erste fünf sichtbare Sender:**
6. Die aktive Position im horizontalen Live-TV-Rail bestimmen; **PRIO 0 = aktuell fokussierter Sender**, **PRIO 1 = die verbleibenden ersten bis zu fünf tatsächlich sichtbaren Sender** (nicht willkürlich die ersten fünf der gesamten Providerliste, wenn der Nutzer bereits gescrollt hat). Zusätzlich das unmittelbar nächste Programm desselben fokussierten Senders niedrig priorisiert vorladen, damit der Wechsel bei Sendezeitgrenzen korrekt bleibt. Vorhandene EPG-Eventidentität liefert Titel/Jahr/Episode für die Bildsuche.
7. Für jeden dieser Events die nachweislich korrekte lokale XMLTV-/Provider-Eventbildreferenz oder bereits gecachtes Foto zuerst prüfen. Nur bei fehlendem Material und **aktiver Einwilligung** TMDB bzw. TVMaze mit exakter Event-/Film-/Episodenidentität aufrufen; keine unsicheren Titel-Similarities als Bilder ausgeben. Senderlogobild ist nicht das Sendungsbild.
8. Vorhandene `programme_requests68.request(..., priority=True)` → `programme_urls55.enqueue(priority68=True)` **weiterverwenden**; die Priorität in der tatsächlichen Worker-Queue und nicht nur in Status-Labels nachweisen. **Kein unbounded Parallelstart**. Bei bereits gefüllter 24er Queue nur bei bestehender sicherer Eviction-Regel niedriger priorisierte noch nicht aktive Jobs verdrängen, niemals laufende Jobs/Meta der falschen Session abbrechen. Vorhandene 2 Worker und Art-Cache-Budget respektieren.

**PHASE 3 – Rest der Startgruppe progressiv & fair:**
9. Nach initial sichtbarer Gruppe die nächsten nicht vorbereiteten Stationen schrittweise in vorhandener Rotations-Fairness bedienen. Beim Scrollen bekommt der neu fokussierte Event Vorrang, danach nächste sichtbare Sender. Verdrängte Sender bekommen später erneut Gelegenheit (kein Starvation). Nächste Sendungen vor Sendezeitwechsel opportunistisch vorladen, aber **nicht** den Erstaufbau von Logos/EPG und sichtbaren 5 Bildern verzögern.
10. Eventbild und tatsächlich verwendete Quelle (`XMLTV, Provider, TMDB, TVMaze`) mit `profile/portal/sid/start/stop/guide_revision` und Cache-Lease ablegen. Keine neuerliche Metadaten-/Bildsuche für denselben gültigen Event bei Fokus-Hin-und-her. Beim Eventwechsel alte Event-Referenz verwerfen, Logo/NowNext sofort korrekt weiterschalten, neue Artwork-Job-Priorität setzen. Doppelte Jobs deduplizieren und bei Source-/Profilwechsel korrekt canceln.
11. Nach fertigem Download/Cache-Commit native Home-Hero-Properties **nur für die noch aktuelle Eventidentität** aktualisieren; rechte Info-Tabelle, linkes Bild und rechte Attributions-/Logoleiste müssen zur gleichen Generation passen. Keine erzwungene Voll-Reload-Schleife, kein Flackern oder fragmentierte Cover. Mit Quellangabe nicht versehentlich alte TMDB-/TVMaze-Logos am neuen Providerbild stehen lassen.

**PHASE 4 – Safe Degradation/Backoff:**
12. Bei Offline/DNS/Rate-Limit/TMDB-disabled/Missing match: Text+Logos bleiben, die linke Hero-Fläche erhält einen ruhigen lokalen grafischen Fallback (vorhandenes sicheres Artwork, sofern eventidentisch, sonst neutraler Sender-Hintergrund). **Kein falsches Cover** und keine unendliche TMDB-Anfrage-Schleife. Negativ-Cache und Retry pro Fehlerklasse mit begrenztem TTL/Backoff, nach legitimer Opt-in-/Quellenänderung gezielt invalidieren, keine erfolgreiche Foto-Referenz löschen.
13. Keine Roh-Provider-/TMDB-URLs, Tokens oder private Kanalnamen ins öffentliche GitHub/CI-Log. Für Logdiagnosen nur gehashte Identitäten und Statuscodes; die private Android-Diagnose als separater Nutzerbeleg.

### 8.3 Reihenfolge darf keinen Kodi-Start blockieren

- EPG **nicht erst online beim Öffnen der Startseite downloaden**: lokaler gültiger Snapshot zuerst; die 24-h-Hintergrundaktualisierung bleibt separater Scheduler mit atomarem Publish.
- Der GUI-/Fokus-Thread darf auf **keine** SQLite-Dauerabfrage, DNS-/TMDB-Netzanforderung, Artwork-Download, Bild-Decode, Queue-Join oder Ganzgruppen-EPG-Import warten. Alles kleine snapshotbasierte Publikationen plus begrenzte Worker. Kein synchrones Verarbeiten von fünf Live-Bildanfragen auf dem Kodi-GUI-Thread.
- Keine rein zeitbasierte Sleep-Wartekette wie „erst 5 s EPG, dann 10 s Logos“. Besser ereignis-/revisionsbasierte Zustandsmaschine: `LOCAL_EPG_READY → LOGOS_READY → VISIBLE_ARTWARM → BACKGROUND_ROTATE` mit unabhängiger Fehler-/Fallback-Schiene, damit langsames Bild nicht EPG blockiert.
- Keine separate zweite Artwork-Datenbank: vorhandene Event-/Bildindex-/Cache-Generation und `programme_requests68`/URL-Queue korrekt koordinieren; Datei-/SQLite-Zugriffe sauber begrenzen. Keine Kopie auf anderen Datenträger ohne expliziten separaten Auftrag.

### 8.4 P0-Messwerte, Traces und reproduzierbare Tests

Traces mit relativem Zeitstempel seit Start (ohne sensitive Werte):
`START_GROUP_KNOWN`, `EPG_SNAPSHOT_READY`, `EPG_5_VISIBLE_READY`, `LOGOS_READY`, `ART_PREWARM_5_QUEUED`, `ART_1_READY`, `ART_5_RESULT`, `BACKGROUND_ROTATE`, `FOCUS_PRIORITIZED`, `EVENT_CHANGE_INVALIDATED`, `ART_RENDERED`, `ART_NO_MATCH`. Für jeden Step zählen: sichtbare Sender, mit gültigem EPG, mit Logo, mit passendem Bild, cache-hit, external-request, elapsed_ms, queue-length, response/code; nur gehashte IDs.

| ID | Szenario | Verbindliche Abnahme |
|---|---|---|
| PREFETCH75-1 | Kodi-Kaltstart, Startgruppe mit mindestens fünf EPG-gedeckten Sendern, kein Tune | Senderliste und verfügbare Logos sichtbar, Jetzt/Danach aus lokalem Cache ohne Streamstart; EPG-Textzeit unabhängig von Artwork protokolliert |
| PREFETCH75-2 | Bereits warmes EPG, Bilder leer, TMDB-Opt-in AN | Sichtbare fünf priorisiert vor Rest, echte passende Bilder wenn jeweilige Quelle eines liefert; keine Suche für EPG-unpassende Sport-/Nachrichtenprogramme erzwingen |
| PREFETCH75-3 | TMDB-Opt-in AUS und TVMaze AUS | **Null neue externe TMDB-/TVMaze-Anfragen**, dennoch vorhandene lokale/Provider-/XMLTV-Bilder nutzen; Text/Logos bleiben |
| PREFETCH75-4 | Benutzer scrollt nach rechts, während Background-Queue voll | Aktueller Fokus erhält PRIO 0, übrige sichtbare zuerst, Rest später (keine Starvation / Profil-Mischung) |
| PREFETCH75-5 | Mehrfach zwischen ersten fünf hin und her | Keine gleichen Netzwerkzugriffe/Downloads für unveränderte gültige Event-Keys, keine veralteten Quellenlogos; Bild/Meta aus Cache |
| PREFETCH75-6 | Um 20:15 Sendungswechsel / Guide-Revision oder Mapping-Change | Now/Next/Art wechselt zur neuen Event-ID atomar, altes Bild nicht irreführend übernommen, nächste Sendung vorab vorbereitet |
| PREFETCH75-7 | Offline, DNS-Timeout, Bildserver 429, Disk-Budget/SQLITE_BUSY | EPG-Text/Logos/Focus bleiben bedienbar, keine unendlichen Retries, keine doppelten Cover-/Senderleisten |
| PREFETCH75-8 | 1920×1080, 1280×720, 60-min Android-RK3528-Test | Eine Rail, links Bild/rechts Daten, stabiles Scrollen, sichtbares Hero-Bild für positiv matchbaren Film-Event, korrekte Quelle rechts, kein Tune erforderlich |

**Zielwerte, keine bisher gemessenen Garantien:** bei bereits warmem lokalem EPG P95 Zeit vom Home-Aufruf bis **Jetzt/Danach** möglichst <2 s; Logo-Texte so früh wie erste Live-Rail; bereits gecachtes Eventbild beim Fokus nahezu sofort; externe erste fünf Artwork-Requests im Hintergrund mit Status und tatsächlichen p50/p95-Latenzen. Netzwerkabhängige Bilddownloads nicht mit fixer Sekunden-Garantie versehen. Die Tests müssen zeigen, dass **EPG-Daten vor externen Bildabfragen** im UI erscheinen, nicht bloß, dass alle Worker am Ende irgendwann „READY“ melden.

**Definition of done ergänzt:** Codex setzt die vorhandenen bounded Worker/Queues mit expliziter sichtbarer 5er-Priorität um, wahrt Opt-in und Bild-Event-Sicherheit, liefert Testbericht+ZIP/SHA für XCMate `0.1.29.75` in Pilot-Testkanal. Regulären Katalog vor Android-Freigabe nicht aktualisieren. Die Layoutvorgabe **LINKS NUR BILD, RECHTS INFO-TABELLE/Quellenlogos, DARUNTER EINE RAIL** aus Kapitel 3 bleibt verbindlich.
