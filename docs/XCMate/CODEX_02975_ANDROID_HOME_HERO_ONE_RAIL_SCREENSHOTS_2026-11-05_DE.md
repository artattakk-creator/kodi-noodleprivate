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
