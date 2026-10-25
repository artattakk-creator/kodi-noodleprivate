# XCMate – verbindliche UX-Roadmap nach .35: bildschirmhohe Rail, zweispaltiges Mini-EPG, echte Player-OSDs und Genresuche

> **NEU: WIZARD SOFORT ALS PARALLELSPUR – NEUESTE PRIORITÄT 25.10.2026:** Der Nutzer benötigt die Möglichkeit, eine **zweite Android-Box mit neuerem Kodi** per vollständigem #43-Wizard früh auszuprobieren. [parallel vorgezogener Wizard-/Neubox-Auftrag](CODEX_PARALLELAUFTRAG_WIZARD_NEUBOX_KODI21_22_20261025_DE.md). `.36` bleibt Performance+Genre, **`.37` jetzt Wizard**, **`.38` Mini-EPG rechts „Vorher/JETZT/Danach“ und volle Rail als DRITTE Links-Stufe NACH Gruppen**, **`.39` Live-TV-Player**, **`.40` VOD-Player**; ältere Ziffern dieses Dokuments sind historische Planvarianten. Keine Verschiebung der Mini/Gruppen/Rail-Semantik, nur zeitliche Priorität. Maßgeblich [verbindlicher neuer Versionszug](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md).


> **VERBINDLICHE RELEASE-PLANUNG 25.10.2026:** [Versionszug .36–.45 mit kombinierter Feature- und Vorversionsfehlerbehebung](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md). `.35` wurde Android-funktional **15/15 PASS** abgenommen. `.36`: Such-/Start-/OSD-Restperformance **plus echte Genre-Suche**; `.37`: **dauerhaft zweispaltiges Mini-EPG und bildschirmhohe Rail NACH Sendergruppen**; `.38`: Live-Player-OSD; `.39`: VOD-OSD; spätere separate EPG-/Artwork-/Storage-Phasen. Früher genannte anderslautende vorläufige Versionsnummern in diesem Dokument sind **nicht** maßgeblich; der aktuelle verbindliche Versionszug hat Vorrang. Der Links-Vertrag `Live→Mini→Gruppen→Rail` bleibt unantastbar.


> **NEUESTER ENTWICKLUNGSPLAN 25.10.2026, NACH BESTANDENER .35-ABNAHME:** Die früher in diesem Dokument beispielhaft genannte „.36 = Rail“-Versionsnummer war ausdrücklich nur **vorläufig** und wird durch die aktuelle [konkrete Codex-Stabilisierungsübergabe für den nächsten kumulativen Kandidaten](CODEX_AUFTRAG_02936_PERF_OSD_SEARCH_BACKLOG_20261025_DE.md) **nicht als Versionsversprechen fortgeführt**. ZUERST Such-/Startkanal-/Infoleisten-Performance und Stop/Home-Routing absichern, ggf. einzelne kleine #159/#111-Fixes. **Unmittelbar danach weiterhin verbindlich:** Mini-EPG mit rechter Programmspalte und **Links→Mini→SENDERGRUPPEN→vollhohe Rail**, danach echte Live-/VOD-Player-Buttons. Die [50-Issue-Triage](ISSUE_TRIAGE_NACH_02935_20261025_DE.md) steuert weitere getrennte PRs; [EPG Hub #161](CODEX_AUFTRAG_ZENTRALER_EPG_HUB_QUELLENMERGE_20261025_DE.md) bleibt eigenständig. **Keine Umkehr der vom Nutzer klargestellten Links-Kette.**


**Beschluss des Nutzers:** 25.10.2026. Produkt: XCMate GS Media, `plugin.video.xtreammate`; Kodi 21.2 Omega / Android TV 13 / RK3528 ARM32 / Titan BINGIE MOD; IR-Fernbedienung.

> „Wir machen jetzt auf jeden Fall die Version noch zu Ende. Aber bei den nächsten kommenden Versionen nach der Abnahme jetzt gleich möchte ich auf jeden Fall, dass wir diese neuen Navigationspunkte mit reinnehmen. Einmal diese vertikale Menüleiste, wenn man im Mini-EPG nach links drückt und auch die Player, dass die überarbeitet werden. Also ich möchte da diese richtigen Player-Buttons haben und sowas. Die Darstellung jetzt gefällt mir einfach nicht.“

**AKTUELLE NUTZERKORREKTUR (25.10.2026):** Anders als in einer vorigen Assistenzinterpretation bleibt die Sendergruppen-Ansicht zwischen Mini-EPG und Navigationsleiste erhalten. Zusätzlich volle Bildschirmhöhe für Rail, rechte Mini-EPG-Programmansicht und Genre-Treffer bei Filmen/Serien.

**ABSOLUTE PHASENGRENZE:** Den laufenden `.35`-Kandidaten aus [CODEX_AUFTRAG_02935_SUCHPERFORMANCE_EPG_NAV_20261025_DE.md](CODEX_AUFTRAG_02935_SUCHPERFORMANCE_EPG_NAV_20261025_DE.md) **erst implementieren, auf Android abnehmen und nur nach ausdrücklicher Freigabe nach main mergen**. NICHT eigenmächtig Navigation/Player-Redesign in laufenden `.35`-Branch injizieren. Die hier beschriebenen Arbeiten sind **nächste, separate kumulative Versionen nach .35**, Nummern erst nach dem dann tatsächlich aktuellen main festlegen.

## 1. Verbindliche KORREKTUR: Mini-EPG → Sendergruppen → bildschirmhohe Icon-Rail

**NEUESTE ausdrückliche Nutzerpräzisierung 25.10.2026 hat Vorrang:** Die zuvor von ChatGPT angenommene Direktfolge **Mini-EPG → Rail ist falsch und widerrufen**. Die bestehende Sendergruppen-Stufe muss erhalten bleiben:

`LIVE_FULL/INFO → [Links] MINI_EPG → [Links] SENDERGRUPPEN → [Links] NAV_RAIL_COMPACT → [Links] NAV_RAIL_EXPANDED`.

- Live-Vollbild/Info, **Links einmal**: bestehende Mini-EPG-Senderliste mit rechts eingebettetem Programmbereich und dem aktuellen Sender markiert.
- Mini-EPG mit **Senderlisten-Fokus**, **Links zweimal (ab Vollbild gezählt)**: **Sendergruppen**. Auswahl/Checkboxen/Fokus wie bisher, keine persistente Änderung der Startgruppe ohne ausdrücklich bestätigte Nutzeraktion.
- Aus **Sendergruppen** erneut **Links (drittes Links ab Vollbild)**: **vertikale XCMate-Navigationsleiste**. Kein Überspringen der Gruppen durch globale Weiterleitung.
- Schmale Rail → Links oder bewusst gewählter Aufklapp-Befehl: dieselbe **bildschirmhohe** Rail mit Icons und lesbaren deutschen Labels.
- Rail Back/Rechts → Gruppen → Back/Rechts → Mini-EPG → Back → Video; Fokus, SID, aktive Gruppe und Player bleiben erhalten.
- **Rechts in der linken Mini-EPG-Senderliste** betritt dagegen die ständig sichtbare **rechte Programmspalte** (nicht das große EPG); **Links/Back dort** geht erst zurück in die linke Senderliste, **nicht** zu Sendergruppen. Rechts/Links-Bedienung muss vom tatsächlichen Fokus abhängen, nicht nur `mode`.
- Großer EPG weiterhin **über Infobar-EPG-Button** (schon Teil des separaten `.35`-Auftrags). Kein ungewollter Kodi-Home-/Doppelplay-Routeneffekt.

**Vollbildhohe Rail – verbindlicher Entwurf:** Von oberem bis unterem sicheren Anzeigerand (1080p und 720p). **Alle Hauptmenüpunkte vertikal über die nutzbare volle Höhe verteilen**, mit gutem Abstand statt kompakter Box; schmal/dunkel/leicht transparent im eingeklappten Modus, groß lesbar im beschrifteten Modus, deutlich sichtbarer TV-Fokus, einheitliche lizensierte Tabler-Icons mit lokal gepackten Kodi-PNGs und Provenienz. Gleiche komplette Höhe beim Aufklappen, keine Überlappung mit Android-/Kodi-Safe-Area. Menü: Suchen, Favoriten, Live-TV, Sendergruppen, **großer EPG**, Filme, Serien, Einstellungen, XCMate-Home/Verlassen; verfügbare XCMate-Routen wiederverwenden, keine fiktiven aktiven Aktionen. **Original-XCMate-Logo nicht ersetzen**, Space Premium opt-in. Kein HTTP bei IR-Menünavigation, keine globale Kodi-Keymap.

**Rail-Abnahme NOT_TESTED:** RAIL-01 Live→Links Mini, RAIL-02 Mini→Links Gruppen, RAIL-03 Gruppen→Links volle Icon-Rail, RAIL-04 Icon-Rail kompakt/ausgeklappt gleicher vertikaler Bereich, RAIL-05 Kategorien und Menürouten korrekt, RAIL-06 Rechts/Back über alle Ebenen mit Fokus, RAIL-07 20 IR-Durchläufe ohne Playback-/Home-Regression, RAIL-08 720p/1080p/Estuary/BINGIE.

## 2. Mini-EPG mit genutzter RECHTER Programmansicht (#95)

**Neue verbindliche Nutzeranforderung:** Das derzeit zu breite Mini-EPG lässt seinen rechten Bereich ungenutzt. **Linke Spalte = Senderliste, rechte Spalte = immer sichtbarer chronologischer Programmverlauf des links markierten Senders** im selben XCMate-Fenster. **Kein zusätzliches Popup bei Rechts**.

- Bei Öffnen fokussiert die linke Senderliste den **tatsächlich laufenden SID** (bei Erststart Startsender), rechts erscheint **seine** verfügbare Programmfolge.
- **Hoch/Runter links** wechselt nur die *markierte Senderzeile*, nicht den Stream; **der rechte Verlauf aktualisiert sich sofort lokal für den markierten Sender**, nicht für den bisher laufenden. Keine synchronen Provider-Downloads, kein teurer Full-Guide-Scan pro IR-Aktion.
- Rechte Spalte zeigt **frühere Sendungen (wenn aus XMLTV/Cache verfügbar)** → die **jetzige Sendung visuell dominant hervorgehoben** (echte Zeit/Progress, sofern valide) → **folgende Sendungen** bis zum belegten EPG-Zeithorizont. Vergangenes nicht erfinden, keine implizite Replay-Fähigkeit behaupten. Fehlen EPG-Daten: ehrlich „Keine Programmdaten verfügbar“ oder „Nur Kurz-EPG“ und Senderliste bleibt sofort bedienbar.
- Solange die **linke Senderliste** den Eingabefokus besitzt, ist rechts die *aktuelle Sendung* **optisch markiert**, aber ihr D-Pad-Fokus ist **noch nicht** gestohlen. **Rechts** verlagert den steuerbaren Fokus zur **Jetzt-Zeile** in die rechte Spalte. Dort **Hoch/Runter** durch frühere/spätere Ereignisse, **OK** öffnet existierende Programmdetails, soweit real vorhanden, kein unbeabsichtigtes Umschalten. **Links/Back** rechts → nur zurück zu linker Liste, mit exakt dem vorigen Sender und Scrollpunkt.
- **Links links** → Sendergruppen → Links → Rail (siehe oben); D-Pad-Ebenen sauber unterscheiden. **OK links** stimmt auf gewählten Sender ab genau einmal, bestehende LiveSession-/IR-/Playbacklogik nicht ändern.
- Bestehende lokale `epg_views.py`/`guide_for_channel`-/XMLTV- und Provider-Short-EPG-Daten und Programme als Quelle. Kein Alias-Mismatch, doppelte Sendungen, erfundene Zeitfenster oder UI-Thread-HTTP; Play läuft im Hintergrund. Verwendete rechte Displayfläche statt immer breiter werdender linker Liste, klare Lesbarkeit aus TV-Abstand.
- **#95 alt „Rechts öffnet neue Programmansicht“ wird präzisiert/ersetzt**: Die rechte Programmansicht ist **dauerhaft zu sehen**, Rechts aktiviert **nur den Fokus**.
- **Abnahmen MINI-01..10 (NOT_TESTED)**: Split-Layout, laufender Sender/Startsender markiert, markierter anderer SID → rechte Events ohne Tune, Jetzt plus frühere/folgende echte Programme, Rechts→Jetzt-Fokus, Pfeile/OK Details, Links aus rechter Spalte nur zurück links, Links aus linker Spalte→Gruppen→Rail, fehlender/kurzer EPG ohne Phantomzeiten, 20 IR-Zyklen + 720p/1080p ohne Playbackregression.

## 3. Verbindliche PLAYER-UX-Überarbeitung: keine bloße Kosmetik, echte große Fernbedienungsbuttons

**Nutzerbewertung:** Die **derzeitige Player-Darstellung gefällt nicht und soll neu gestaltet werden**. Das ist ein **explizit autorisierter UI-Redesign-Scope der Player/OSD-Bereiche**, während die **globale dreigeteilte Suche** weiterhin [STRICT UI-FREEZE](SUCHMASKE_UI_FREEZE_02934_20261025_DE.md) bleibt.

**Zwei getrennte, visuell verwandte Player-Erfahrungen**, gleiche Icon-Sprache, große tapp-/fokussierbare Schaltflächen, echtes Transport-Feedback – aber unterschiedliche technische Fähigkeiten:

### A. Live-TV-Player / Infobar

- **1× OK** weiterhin kompakte **Infoleiste mit Senderlogo, Jetzt/Danach, echten Zeiten und Fortschritt**, keine versteckte Playeraktion beim ersten OK.
- **2× OK oder Runter** bringt einen **richtigen fokussierbaren Player-Controls-Balken** mit Play/Pause, Stop/Live-Ende, optisch klaren Aktionsbuttons, Tonspur, Untertitel, Bild-/Audioeinstellungen und **EPG-Button zum großen EPG** (mit `.35`-Routingbestätigung); mit Back nur Overlay schließen.
- **Play/Pause und ±10/30s bzw. Seek/FF/RW** nur dort aktiv, wo Kodi **belegte** Pause-/Timeshift-/Seek-Fähigkeit für den aktuellen Live-Stream meldet. Sonst deaktivieren/ausgrauen oder verständlich nicht anbieten, nicht vortäuschen. Kein beliebiges Springen in linearem Live-TV.
- Stream-Statussymbole **#100** für echte Auflösung/Codec/Audiokanäle/Untertitel in schlanker Reihe, nur technisch belegte Werte, keine 4K/Dolby-Erfindung aus Sendername. Der Umfang der Icons kann im gleichen Live-OSD-PR mitgenommen werden, sofern die IR-/Layouttests nicht überfrachtet werden.
- Direkte **Links**-Navigation aus Vollbild/Info bleibt Mini-EPG; neuer Links-Pfad Mini→Gruppen→Rail bleibt von der unteren Playerleiste unabhängig und kontextsauber.
- **Nicht** die darunterliegende Hardware-Decoder-/Kodi-Player-Engine austauschen, um eine bessere Optik zu erzielen. Bestehende XCMate-LiveSession / Guide-Handoff / Senderzapping schützen.

### B. Filme-/Serienplayer (VOD)

- Über kompatiblen **Kodi VideoPlayer** ein eigenes **XCMate-VOD-OSD**, keine Eigen-Decoder-Engine. Echte visuell hochwertige Buttons: Play/Pause zustandsabhängig, Stop, Rück-/Vorspulen, ±10/30s Sprünge, **Timeline mit aktueller und verbleibender Dauer**, Titel/Poster soweit vorhanden, Audio- und Untertitelspur, Bild-/Audioeinstellungen, Info; bei Serien ggf. „Nächste Folge“ **nur** unter bereits korrekt getesteten Autoplay-/Resume-Regeln.
- **Sehr wichtig:** Pause/Resume/Seek nur wenn der tatsächliche Player die Action unterstützt; tatsächliche `Player.PauseEnabled`/`Player.SeekEnabled` und Session-Ownership prüfen, keine nicht existierenden JSON-RPC-Felder. Back schließt nur das OSD; expliziter Stop beendet ausschließlich die aktuelle **XCMate-eigene** Session und sichert Resume. Nie fremde Kodi-Wiedergabe stoppen.
- **Nächtlicher Android-Autoplay-PASS** aus `.34`: geschätzt 7–8 Episoden inklusive Staffelwechsel, unbedingt als Regression-Gate erhalten. Kein unnötiger Eingriff in `media_progress.py`/Next-Episode-Pipeline.
- **#79/#84:** früheres VOD-OSD / historischer Draft als Konzept- und Code-Referenz prüfen, **nicht** alte Draft-Version .15 erneut mergen. Code gegen aktuelles main portieren, nicht alten Stand als Ausgangsbasis.

### Visuelle Abnahme vor finaler Implementation

Codex soll zunächst **2–3 konkrete TV-OSD-Anordnungen** (z. B. kompakte Transportbar + Icon-Aktionen, zweistöckige Playbackbar, Live-Info plus Transport) als **leicht prüfbare Designskizzen/Screenshots** aufbereiten und nach Original-XCMate-Theme/Space-Premium-Styling einordnen. Nutzer entscheidet den visuellen Stil **vor** dem vollständigen Player-UI-Merge. Keine Behauptung einer abgenommenen Optik allein wegen Host-CI. Icons gerne dieselbe gepinnte Tabler-Bibliothek; Hoch-/Runter-/Links-/Rechts-Fokus muss reproduzierbar sein, Symbole bei 2–3 m Betrachtungsabstand erkennbar.

**Player-Tests:** PLAY-01 1× OK Info, 2× OK Transport, PLAY-02 große echte Buttons/funktionierende Fokussteuerung, PLAY-03 unterstützte Pause/Seek vs nicht unterstütztes Live, PLAY-04 EPG-Button → großer Guide → Back zum laufenden Video, PLAY-05 VOD Pause/Seek/Stop/Resume/Audio/Untertitel, PLAY-06 Back ohne Streamstop, PLAY-07 Episoden-Autoplay inklusive Staffelübergang, PLAY-08 fremde Kodi-Player/Dialoge unberührt, PLAY-09 10x öffnen/schließen ohne Black/Busy/Root, PLAY-10 BINGIE und Estuary / 720p+1080p. Alle bis Android-Abnahme **NOT_TESTED**.

## 4. Genresuche in bestehender globaler Suche (#159)

**Statischer Code-Befund .34 auf main:** `library_index.FIELDS` enthält bereits `genre` (auch `plot`/`description`), und `search_results.secondary()` zeigt Genre bei Filmen und Serien an. `library_index.Reader.page()` durchsucht beim Token-`LIKE` aber lediglich das beim Import per `normalized(title)` gefüllte Feld `search`. `search_data.LiveSearch.step()` sucht Sendernamen und laufende Jetzt-Programmtitel, **nicht** Genre. Deshalb keine garantierte Genre-Treffersuche, auch wenn ein zufälliger Titel bereits „Western“ enthält.

**Nutzerwunsch:** Im bestehenden Suchfeld sollen `Sci-Fi`, `Science Fiction`, `Western`, `Thriller`, usw. **auch passende Filme/Serien anhand vorhandener Provider-Genre-Metadaten** liefern, selbst wenn kein Titelmatch existiert. Konservative Aliasse `Sci-Fi/Sci Fi/Science-Fiction/Science Fiction` usw. Ohne Provider-Genre keine erfundenen Treffer oder automatische Annahme, jede Provider-`category_id` sei ein Genre. Titel-Treffer sinnvoll vor Genre-Treffer, keine Duplikate; Provider-/Gruppenfilter beibehalten.

**Strikt unveränderte Suchmaske** Live-TV | Filme | Serien (UI-Freeze aus `SUCHMASKE_UI_FREEZE_02934_20261025_DE.md`). Umsetzung als effiziente, datenschonende lokale Suche per vorindizierten Genrebegriffen/geeigneter schema-kompatibler Migration, keine langsamen JSON-Vollscans, kein Reimport-/Profilreset. Live-TV-Suche und Now-/EPG-Latenzfix aus .35 müssen unverändert bleiben. Echte Genre-Auswertung von TV-Programmen **nur später und nur bei vorhandenen belegten EPG-Genre-Tags**.

**GENRE-01–07: Android NOT_TESTED**; eigener kleiner kumulativer Draft-PR nach .35, nicht unbemerkt in .35 oder das Rail-Redesign mischen. Siehe [#159](https://github.com/artattakk-creator/kodi-noodleprivate/issues/159).

## 5. Reihenfolge der Folgeversionen (Nummern nur vorläufig)

**Laufende Version .35 erst wie beauftragt abschließen und auf echter Android-Box abnehmen.** Bereits freigegeben: schnellere Live-TV-/EPG-Suche, Infobar-EPG-Button → großer Guide, Startgruppe und aktueller Senderfokus, kleine Short-EPG-Robustheit. **Die hier besprochenen UI-Umbauten und Genresuche ausdrücklich erst NACH .35**, keine laufende Codex-Arbeit unaufgefordert umwerfen.

1. **Voraussichtlich .36:** gebündelte **Mini-EPG-Zweispaltenansicht (#95)** und **bildschirmhohe Rail NACH der Gruppenebene (#94/#150)**, logisch getrennte Commits und separate Android-Gates. Falls zu riskant, Split in zwei kumulative Draft-PRs/Versionen statt ungeprüft zusammenzuwerfen.
2. **Darauffolgend:** **Live-TV-OSD/Player** mit echten funktionsfähigen Transport-/Audio-/Untertitelbuttons (#17/#100) und ausgewählter visueller Variante.
3. **Darauffolgend:** **Film-/Serien-VOD-OSD** mit Timeline/PlayerCapabilities/Resume und unverändertem Serien-Autoplay (#79/#84).
4. **Genre-Suche (#159):** kleiner unabhängiger PR nach .35, früher als oder zwischen den Player-UI-PRs, abhängig von Risiko; niemals um den Preis einer neuen mehrminütigen Suche.
5. Später: Rail für übrige Bereiche #150, EPG-Quellen-Mapping #98, Poster-Retry #111, weitere Downloader/Recorder nach eigener Abnahme.

**Alte widersprechende Anweisungen endgültig verworfen:** `Mini → direkt Rail` ist falsch, richtig ist `Mini → Sendergruppen → Rail`; Mini-Rechts öffnet **kein zweites Popup**, sondern aktiviert die **ständig sichtbare rechte EPG-Programmspalte**. Diese Nutzerpräzisierung ist jünger und verbindlich.

### Verbindlich zusätzlich beauftragt: zentraler EPG Hub / Mehrquellen-Merger (#161)

**Neuer ausdrücklicher Entwicklungsauftrag vom 25.10.2026:** **[Codex-Vollauftrag für EPG Hub](CODEX_AUFTRAG_ZENTRALER_EPG_HUB_QUELLENMERGE_20261025_DE.md)** · [GitHub-Issue #161](https://github.com/artattakk-creator/kodi-noodleprivate/issues/161).

- **Vorhandene lokale `guide_v1.sqlite` beibehalten und evolutionär erweitern** statt parallele zweite Datenbank aufzubauen. Bestehender Streaming-XMLTV-Stageimport und 10-Tage-Zukunftsfenster sind Ausgangspunkt.
- **Gesamt-EPG aus Anbieter, EPGShare01, Kaimandura etc.** nach quellenspezifischer Kanalidentität und **einzelnen Zeitintervallen** zusammenführen. Echte Lücken füllen, echte Konflikte priorisiert behandeln; manuelle Quell+Kanal-Zuordnung (#98) hat Vorrang.
- **Bis 7 Tage EPG-Historie** soweit aus Feed/vorherigen Aktualisierungen vorhanden, plus tatsächlich vorhandene Zukunft innerhalb validierter Budgetgrenzen. **Catch-up nur bei realer Anbieterfähigkeit**, niemals aus gespeichertem EPG allein behaupten.
- **Atomarer veröffentlichter Snapshot und Indizes** für großen Guide, zweispaltiges Mini-EPG (#95), Now/Next, Widgets und Programmtitelsuche, alle Abfragen lokal/sofort. Hintergrundaktualisierung darf UI nicht stückweise zerfallen lassen oder neue Minuten-Suchlatenzen erzeugen.
- **Erst vorhandene .35 fertigstellen/abnehmen**; danach **eigene Architektur-/Migrations-/UI-Anbindungsetappen HUB-0…3**, je kumulativer Draft mit Tests und Android-Abnahme. Dies ist wichtiger Infrastruktur-Unterbau für die kommenden UI-/Catch-up-/Timer-Funktionen; **nicht ungefragt die bereits zugesagten Rail-/Player-Features in einen Mega-PR hineinschieben**. Reihenfolge anhand aktueller `main`-Basis und Fachabhängigkeit priorisieren, keine fixe Versionsreservierung.
- Geschützte Basis: 3-Tab-Suchmaske, erfolgreicher Guide→Playback/Back, IR-Fokus, Starteinstellungen/Quellmapping, nächtlich bestätigtes staffelübergreifendes Serien-Autoplay, Originalicon.

## 6. Pflichtprozess

Pro Release genau **kumulativ auf der letzten bestätigten main-Version**, Add-on-ID stabil, neue Draft-PR, Host-/Kodi-/WindowXML-Regressionstests, ZIP + SHA256, Android-Testplan zunächst NOT_TESTED, echte IR-Abnahme durch Nutzer. **Kein automatischer Merge, kein Kodi-Reset, kein Downgrade, kein Theme-/Portal-/Icon-Wechsel als Nebeneffekt.** Roadmap- und Designabstimmung sind keine Implementierungsfreigabe für den laufenden Kandidaten.

**Quell-Issues:** [#94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94), [#150](https://github.com/artattakk-creator/kodi-noodleprivate/issues/150), [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#100](https://github.com/artattakk-creator/kodi-noodleprivate/issues/100), [#79](https://github.com/artattakk-creator/kodi-noodleprivate/issues/79), [#84](https://github.com/artattakk-creator/kodi-noodleprivate/issues/84), [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143).


**Neue Folgeissues:** [#95](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95) rechte Mini-EPG-Programmansicht; [#159](https://github.com/artattakk-creator/kodi-noodleprivate/issues/159) Genre-Suche.
