# XCMate – verbindliche UX-Roadmap NACH Abnahme 0.1.29.35: vertikale Navigation und echte Player-OSDs

**Beschluss des Nutzers:** 25.10.2026. Produkt: XCMate GS Media, `plugin.video.xtreammate`; Kodi 21.2 Omega / Android TV 13 / RK3528 ARM32 / Titan BINGIE MOD; IR-Fernbedienung.

> „Wir machen jetzt auf jeden Fall die Version noch zu Ende. Aber bei den nächsten kommenden Versionen nach der Abnahme jetzt gleich möchte ich auf jeden Fall, dass wir diese neuen Navigationspunkte mit reinnehmen. Einmal diese vertikale Menüleiste, wenn man im Mini-EPG nach links drückt und auch die Player, dass die überarbeitet werden. Also ich möchte da diese richtigen Player-Buttons haben und sowas. Die Darstellung jetzt gefällt mir einfach nicht.“

**ABSOLUTE PHASENGRENZE:** Den laufenden `.35`-Kandidaten aus [CODEX_AUFTRAG_02935_SUCHPERFORMANCE_EPG_NAV_20261025_DE.md](CODEX_AUFTRAG_02935_SUCHPERFORMANCE_EPG_NAV_20261025_DE.md) **erst implementieren, auf Android abnehmen und nur nach ausdrücklicher Freigabe nach main mergen**. NICHT eigenmächtig Navigation/Player-Redesign in laufenden `.35`-Branch injizieren. Die hier beschriebenen Arbeiten sind **nächste, separate kumulative Versionen nach .35**, Nummern erst nach dem dann tatsächlich aktuellen main festlegen.

## 1. Verbindliche Änderung gegenüber älterem #94/#150-Navigationsplan

**Der neueste Nutzerwunsch hat bei Konflikten mit älteren Spezifikationen Vorrang.** Älter war die Kette:
`LIVE_FULL → [Links] CHANNEL_LIST → [Links] GROUPS → [Links] NAV_ICONS → [Links] NAV_EXPANDED → …`.

**JETZT VERBINDLICH nach .35:**
`LIVE_FULL / INFO → [Links] MINI_EPG_CHANNEL_LIST → [Links] NAV_RAIL_COMPACT → [Links] NAV_RAIL_EXPANDED`.

Damit ist die **direkte Gruppenliste als zweite Links-Ebene ersetzt**; Gruppen werden **über das ausdrückliche, sofort erreichbare Menü `Sendergruppen` in der Rail** geöffnet. Es darf kein weiterer versteckter Pflicht-Klick über die Gruppe nötig sein, ehe die Rail erscheint. Die Benutzeranweisung ist klar: **einmal Links zum Mini-EPG, noch einmal Links direkt zur vertikalen Navigation.**

**Vorschlag zur Back-/Rechts-Semantik, vor Implementierung im UI-Draft mit Android-Fokus bestätigen:**

| Zustand + Aktion | Ziel |
| --- | --- |
| Live-Vollbild → Links | Mini-EPG/Senderliste, **aktuell laufender Sender sichtbar markiert** |
| Mini-EPG → Links | **Schmale vertikale Menüleiste** (`nav_icons`), ohne Stream-Neustart |
| Schmale Leiste → Links oder OK auf bewusstem Menü-Ausklapp-Affordance | **Breite Rail mit Icons + Klartextlabels** (`nav_expanded`), kein Home-Sprung |
| Rail kompakt/ausgeklappt → Rechts/Back | zur zuletzt sichtbaren Mini-Senderliste **mit derselben Gruppen-/Sender-/Scrollposition** |
| Mini-EPG → Back | zurück zum unveränderten laufenden Live-TV; Back schließt UI statt Video |
| Rail → `Sendergruppen`-Menüpunkt → OK | **Gruppenliste**, dort eine erlaubte Gruppe wählen, zurück zur Senderliste dieser Gruppe |
| Rail → Suchen/Live-TV/Filme/Serien/Favoriten/Einstellungen/EPG | vorhandene XCMate-Router-/Kodi-Owner-sichere Route, Fokus/Return-Kontext erhalten |
| Rail → `XCMate-Home / Verlassen` | bewusster, explizit gekennzeichneter Ausstieg zu **XCMate Home**, niemals unabsichtlich Kodi-Home |
| Mini-EPG markierter Sender → Rechts | zukünftig optionale Programmvorschau **#95**, **nicht** in Rail-Draft integrieren, sofern nicht gesondert beauftragt |

**Rail-Icons und Information Architecture:** Gemeinsam gestaltete, nicht zufällig gemischte Symbole für **Suchen, Favoriten, Live-TV, EPG, Sendergruppen, Filme, Serien, Einstellungen, XCMate-Home**. Kontextabhängige Funktionen nur bei verfügbarer Route. Die Gruppe direkt auffindbar machen; das Original-XCMate-Branding-Icon nicht ersetzen. Schon dokumentierte [Tabler-Icon-Entscheidung in #94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94) (versionierte Tabler Icons, MIT-Hinweis/Asset-Provenienz, in Kodi-taugliche lokal mitgelieferte Texturen statt Runtime-CDN) wiederverwenden. Eine gemeinsame Rail-Basis später in EPG/Home/Filmen/Serien (#150) sinnvoll, **erst Live-Flow abnehmen**, andere Rubriken nachziehen.

**UX/Performance:** 1080p primär, 720p prüfen; schlanke grau/transparente Rail, klar kontrastierte große Icons und deutsche Labels, hochsichtbarer TV-Fokus (nicht nur Farbwechsel), keine asynchronen HTTP-Downloads oder Scan-Neustarts beim Öffnen. Fernbedienung: ↑↓ Einträge wechseln, OK ausführen, Rechts/Back zurück, kein Fokusdiebstahl und keine Doppelaktionen aus `onAction`/`onControl`; keine globalen Kodi-Keymap-Änderungen. Live-TV läuft beim bloßen Menüöffnen weiter; fremde Player-/Kodi-Systemdialoge nicht vereinnahmen.

**Künftige Rail-Tests:** RAIL-01 Live→Links Mini (aktuelle SID), RAIL-02 Mini→Links *sofort Rail*, RAIL-03 Rail↔beschriftete Rail↔Mini per Back/Rechts mit Fokus, RAIL-04 Gruppen via Rail und zurück, RAIL-05 jeden Menüpunkt nach XCMate-Router und zurück ohne Home/Player-Crash, RAIL-06 20 IR-Navigationszyklen, 720p/1080p, Estuary/BINGIE; alle bis Test auf Android **NOT_TESTED**.

## 2. Verbindliche PLAYER-UX-Überarbeitung: keine bloße Kosmetik, echte große Fernbedienungsbuttons

**Nutzerbewertung:** Die **derzeitige Player-Darstellung gefällt nicht und soll neu gestaltet werden**. Das ist ein **explizit autorisierter UI-Redesign-Scope der Player/OSD-Bereiche**, während die **globale dreigeteilte Suche** weiterhin [STRICT UI-FREEZE](SUCHMASKE_UI_FREEZE_02934_20261025_DE.md) bleibt.

**Zwei getrennte, visuell verwandte Player-Erfahrungen**, gleiche Icon-Sprache, große tapp-/fokussierbare Schaltflächen, echtes Transport-Feedback – aber unterschiedliche technische Fähigkeiten:

### A. Live-TV-Player / Infobar

- **1× OK** weiterhin kompakte **Infoleiste mit Senderlogo, Jetzt/Danach, echten Zeiten und Fortschritt**, keine versteckte Playeraktion beim ersten OK.
- **2× OK oder Runter** bringt einen **richtigen fokussierbaren Player-Controls-Balken** mit Play/Pause, Stop/Live-Ende, optisch klaren Aktionsbuttons, Tonspur, Untertitel, Bild-/Audioeinstellungen und **EPG-Button zum großen EPG** (mit `.35`-Routingbestätigung); mit Back nur Overlay schließen.
- **Play/Pause und ±10/30s bzw. Seek/FF/RW** nur dort aktiv, wo Kodi **belegte** Pause-/Timeshift-/Seek-Fähigkeit für den aktuellen Live-Stream meldet. Sonst deaktivieren/ausgrauen oder verständlich nicht anbieten, nicht vortäuschen. Kein beliebiges Springen in linearem Live-TV.
- Stream-Statussymbole **#100** für echte Auflösung/Codec/Audiokanäle/Untertitel in schlanker Reihe, nur technisch belegte Werte, keine 4K/Dolby-Erfindung aus Sendername. Der Umfang der Icons kann im gleichen Live-OSD-PR mitgenommen werden, sofern die IR-/Layouttests nicht überfrachtet werden.
- Direkte **Links**-Navigation aus Vollbild/Info bleibt Mini-EPG; neuer Links-Pfad Mini→Rail bleibt von der unteren Playerleiste unabhängig und kontextsauber.
- **Nicht** die darunterliegende Hardware-Decoder-/Kodi-Player-Engine austauschen, um eine bessere Optik zu erzielen. Bestehende XCMate-LiveSession / Guide-Handoff / Senderzapping schützen.

### B. Filme-/Serienplayer (VOD)

- Über kompatiblen **Kodi VideoPlayer** ein eigenes **XCMate-VOD-OSD**, keine Eigen-Decoder-Engine. Echte visuell hochwertige Buttons: Play/Pause zustandsabhängig, Stop, Rück-/Vorspulen, ±10/30s Sprünge, **Timeline mit aktueller und verbleibender Dauer**, Titel/Poster soweit vorhanden, Audio- und Untertitelspur, Bild-/Audioeinstellungen, Info; bei Serien ggf. „Nächste Folge“ **nur** unter bereits korrekt getesteten Autoplay-/Resume-Regeln.
- **Sehr wichtig:** Pause/Resume/Seek nur wenn der tatsächliche Player die Action unterstützt; tatsächliche `Player.PauseEnabled`/`Player.SeekEnabled` und Session-Ownership prüfen, keine nicht existierenden JSON-RPC-Felder. Back schließt nur das OSD; expliziter Stop beendet ausschließlich die aktuelle **XCMate-eigene** Session und sichert Resume. Nie fremde Kodi-Wiedergabe stoppen.
- **Nächtlicher Android-Autoplay-PASS** aus `.34`: geschätzt 7–8 Episoden inklusive Staffelwechsel, unbedingt als Regression-Gate erhalten. Kein unnötiger Eingriff in `media_progress.py`/Next-Episode-Pipeline.
- **#79/#84:** früheres VOD-OSD / historischer Draft als Konzept- und Code-Referenz prüfen, **nicht** alte Draft-Version .15 erneut mergen. Code gegen aktuelles main portieren, nicht alten Stand als Ausgangsbasis.

### Visuelle Abnahme vor finaler Implementation

Codex soll zunächst **2–3 konkrete TV-OSD-Anordnungen** (z. B. kompakte Transportbar + Icon-Aktionen, zweistöckige Playbackbar, Live-Info plus Transport) als **leicht prüfbare Designskizzen/Screenshots** aufbereiten und nach Original-XCMate-Theme/Space-Premium-Styling einordnen. Nutzer entscheidet den visuellen Stil **vor** dem vollständigen Player-UI-Merge. Keine Behauptung einer abgenommenen Optik allein wegen Host-CI. Icons gerne dieselbe gepinnte Tabler-Bibliothek; Hoch-/Runter-/Links-/Rechts-Fokus muss reproduzierbar sein, Symbole bei 2–3 m Betrachtungsabstand erkennbar.

**Player-Tests:** PLAY-01 1× OK Info, 2× OK Transport, PLAY-02 große echte Buttons/funktionierende Fokussteuerung, PLAY-03 unterstützte Pause/Seek vs nicht unterstütztes Live, PLAY-04 EPG-Button → großer Guide → Back zum laufenden Video, PLAY-05 VOD Pause/Seek/Stop/Resume/Audio/Untertitel, PLAY-06 Back ohne Streamstop, PLAY-07 Episoden-Autoplay inklusive Staffelübergang, PLAY-08 fremde Kodi-Player/Dialoge unberührt, PLAY-09 10x öffnen/schließen ohne Black/Busy/Root, PLAY-10 BINGIE und Estuary / 720p+1080p. Alle bis Android-Abnahme **NOT_TESTED**.

## 3. Umsetzungs-Reihenfolge / Versionsphasen (Nummern ausdrücklich vorläufig)

**PHASE JETZT:** `.35` aus bereits abgesprochenem Auftrag abschließen und Android G1–G4/PERF/ROUTE/GROUP testen. Auch die darin gewünschte einfache **Infobar-EPG→großes EPG**-Aktion **bleibt im .35-Scope**, weil sie bereits freigegeben wurde. **Nicht** die *optische Neugestaltung* oder die vertikale Rail in `.35` hineinziehen.

**NACH BESTANDENER .35-ABNAHME, in aufeinander folgenden kumulativen Hauptversionen:**

1. **Nächster UX-Release (voraussichtlich .36):** Primär **Live-Mini-EPG→Linke Icon-Rail (direkt)**, kompakt/aufklappbar, Sendergruppen-Menü über Rail. Abnahme, dann Nutzer-Merge-Freigabe.
2. **Darauffolgender UX-Release (voraussichtlich .37):** **Live-TV-Player-/Infobar-OSD-Redesign** mit echten Play/Pause-/Transport-/Ton-/Untertitel-Buttons und ggf. technisch belegten Statusicons; bestehende Live/EPG-Navigation bewahren. Designentscheidung möglichst vorher.
3. **Darauffolgender Medien-UX-Release (voraussichtlich .38):** **Film-/Serien-OSD** neu gestalten und echt funktionsfähig machen. Test von Resume/Autoplay, Staffeln und Kodi-Player-Ownership; ggf. ein früherer gemeinsamer PR **nur** falls weniger Risiko nachgewiesen ist.
4. **Danach:** gemeinsame Rail in anderen Rubriken (#150), Mini-EPG **Rechts→Programmvorschau** (#95), EPG-Zuordnung (#98), Artwork-Poster-Retry (#111), optionale Downloads/Aufnahme nach technischen Voraussetzungen. Keine ungefragte Aufblähung eines Releasepakets.

**Spezifisch ältere Konflikte auflösen:** #94 und #150 beschrieben früher **Mini→Gruppen→Rail**, und alte #17 erwähnte **Mini→Gruppen**. Diese Regeln **werden für künftige Rail-Versionen durch diese neuere Nutzeranweisung ersetzt**. Für `.35` gilt dessen früher explizit definierter Scope bis zur Abnahme; Codex soll diese neue Folge-Roadmap kennen, aber nicht unaufgefordert den laufenden .35-PR ändern.

## 4. Pflichtprozess

Pro Release genau **kumulativ auf der letzten bestätigten main-Version**, Add-on-ID stabil, neue Draft-PR, Host-/Kodi-/WindowXML-Regressionstests, ZIP + SHA256, Android-Testplan zunächst NOT_TESTED, echte IR-Abnahme durch Nutzer. **Kein automatischer Merge, kein Kodi-Reset, kein Downgrade, kein Theme-/Portal-/Icon-Wechsel als Nebeneffekt.** Roadmap- und Designabstimmung sind keine Implementierungsfreigabe für den laufenden Kandidaten.

**Quell-Issues:** [#94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94), [#150](https://github.com/artattakk-creator/kodi-noodleprivate/issues/150), [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#100](https://github.com/artattakk-creator/kodi-noodleprivate/issues/100), [#79](https://github.com/artattakk-creator/kodi-noodleprivate/issues/79), [#84](https://github.com/artattakk-creator/kodi-noodleprivate/issues/84), [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143).

