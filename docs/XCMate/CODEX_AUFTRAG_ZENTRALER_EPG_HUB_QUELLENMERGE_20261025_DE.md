# XCMate – VERBINDLICHER Entwicklungsauftrag: zentraler EPG Hub, Mehrquellen-Merger, Historie und schnelle lokale Suche

**Beauftragt vom Nutzer am 25.10.2026.** **Ziel:** Nachweisbar verfügbare EPG-Daten aus Xtream/Provider, EPGShare01, Kaimandura und allen künftig bewusst aktivierten geeigneten Quellen in einem **eigenen konsistenten lokalen XCMate-Programmführer** zusammenführen. Die UI soll den zuletzt erfolgreich veröffentlichten Datenbestand **sofort lokal lesen**, statt beim Öffnen scheinbar Stück für Stück Daten nachzuladen. EPG-Historie **bis zu 7 Tage rückwärts** und Zukunft **bis zum tatsächlich verfügbarem Horizon** (innerhalb messbarer lokaler Grenzen) für den Guide bereithalten. Archiv-Wiedergabe/Catch-up nur bei realer Providerunterstützung.

**Produkt/Umgebung:** GS Media XCMate, Add-on `plugin.video.xtreammate`; Kodi 21.2 Omega; Android TV 13 RK3528 ARM32; Titan BINGIE MOD; IR-Remote. Repo: https://github.com/artattakk-creator/kodi-noodleprivate.

**PHASENSTOP:** Aktuellen .35-Entwicklungs-/Android-Abnahmezyklus zuerst abschließen. **DIES IST EIN SEPARATER VERBINDLICHER FOLGEAUFTRAG**, nicht Teil der aktuellen .35-Patches. Vor späterem Start aktuelle Hauptversion/PRs/Index prüfen, kumulativ vom bestätigten `main`, Draft-PRs, Android-Abnahme, kein autonomer Merge/Release/Downgrade/Reset. Architektur-Fortentwicklung vorzugsweise in **mehreren kleinen, testbaren PRs**, nicht in einem unkontrollierten Komplettrewrite. Keine jetzt fest reservierte Versionsnummer.

## 1. Nutzerbeobachtung und Zielbild, keine vorgetäuschte Root-Cause

Der große und kleine EPG wirken „zerstückelt“, als werde erst Quelle 1, danach Quelle 2, danach Quelle 3 geladen und das Bild ergänzt; Nutzer vermutet, ein vorab gebauter einheitlicher EPG beschleunige Anzeige und Suche. **Diese Wahrnehmung ist eine begründete Hypothese, nicht der technische Nachweis, dass jede GUI-Aktion alle Quellen neu lädt.** Mit tatsächlichen EPG-Revisionen/DB-Queries/Importphasen prüfen, ob sichtbare Teilergebnisse durch nacheinander importierte Quellen, Cache-Revisionen, fehlendes Matching oder getrennte Now/Next-/Guide-Cachepfade verursacht werden. Kein Design-Umbau ohne Laufzeitmessung.

**Ziel:**
- Drei + N Datenquellen unabhängig vom UI **im Hintergrund** laden, prüfen, normalisieren und **sicher** in einen pro Portal/Quellenprofil nutzbaren gemeinsamen EPG überführen.
- **Zeitintervall-genaue Zusammenführung** statt nur „Quelle mit irgendeinem Programm für diesen Sender gewinnt“. Fehlende Abschnitte aus anderen Quellen übernehmen, **keine** ungeprüfte Mischung widersprüchlicher Überschneidungen, falscher Sender/Regionen oder erfundener Programmtitel.
- **Quelle, Eingangsrevision, Priorität, Zeitpunkt, Zeitfenster, Konfliktgrund** nachvollziehbar halten; manuelle Benutzerzuweisung **hat Vorrang** und bleibt stabil.
- **Zuletzt validierten Guide als unveränderlichen lesbaren Snapshot** weiter anzeigen, während neue Quellen eingelesen werden; nach konsistenter Stage/Validierung atomar/eindeutig die veröffentlichte Generation wechseln. Es darf beim Refresh kein Zerfallen/Leeren/Flackern des gerade benutzten Guides auftreten. Nach Neustart persistenter Status.
- **Eine gemeinsame faktische Datenbasis** für großen EPG, Mini-EPG inklusive **rechter Sendungsliste „Vorher / JETZT / Danach“**, aktuelle Infoleiste/NowNext, Programmtitelsuche, XCMate-Widgets und spätere Catch-up-/Reminder-/Recorder-Funktionen.
- **Sofortige rein lokale Abfragen** beim Öffnen/IR-Hover; **kein HTTP, XMLTV-Parsing, Bulk-Import, pro-Sender-Providerabruf oder Gesamtscan im Fenster-/Key-Thread**. Daten dürfen als „letzter Stand vom …“ angezeigt werden, solange eine Hintergrundaktualisierung läuft.

## 2. Technischer IST-Zustand im main / XCMate 0.1.29.34 (Codebefund 25.10.2026)

**Bereits vorhanden und unbedingt wiederverwenden/erhalten:**
- `resources/lib/guide_store.py` besitzt die persistente SQLite-Datenbank **`guide_v1.sqlite`** mit `guide_alias`, `programmes(pid,cid,start,stop,title,description,source)`, `guide_meta`, `guide_window/guide_source/guide_expiry`-Indizes. Bisheriger Zukunftshorizont **< now+10 Tage**; `import_cache` und `stream_epg.import_source` entfernen historische Einträge bei **`stop < now-86400`**, und `import_cache` weist bereits abgelaufene Programme ab. Eine echte 7-Tage-Historie fehlt.
- `resources/lib/stream_epg.py`: Streaming-SAX/XMLTV in **staged SQLite**, Validierung und atomare Publikation der Quelle, gestaffelte Provider-/Feed-Imports, dedupliziert; fehlgeschlagene Quelle behält alte erfolgreiche Daten. **Dies ist bereits ein erheblicher Teil der gewünschten Architektur!** Bestehende Schutzgrenzen/SQLite-Staging/Timeout-Budget nicht verwerfen.
- `resources/lib/epg_sources.py::merge_sources()` als alternativer Kompatibilitätsweg übernimmt beim gleichen Kanal bisher überwiegend die **erste nichtleere Gesamtliste** (`if entries and not merged.get(channel_id)`), statt jedes Zeitloch sicher zu ergänzen. `stream_epg.py::import_source()` ergänzt neue Intervalle **nur unter Quellenpriorität und Nichtüberschneidungsregeln**; zu prüfen sind die jeweiligen Precedence-/Überlappungssemantiken, Lücken trotz anderer Quellen und beide Importpfade. **Nicht** behaupten, das System habe heute gar keinen zentralen Cache oder niemals atomare Imports.
- `resources/lib/epg_events.py::deduplicate()` bewertet Quellenpriorität und fast identische Sendungen; diese Regeln sind **nicht** automatisch eine konfliktfreie zeitintervallbasierte Quellenfusion.
- `resources/lib/epg_views.py` liest schnelle Now-/Next-Werte aus vorhandenem lokalem Cache; bei Bedarf nur **cache-only** Short-EPG-Fallback. `guide_grid_data.py` liest den persistenten Store kanal-/fensterweise. `search_data.LiveSearch` arbeitet dagegen teilweise über vollständigen Live-Katalog/EPG-Now-Snapshot. **Mehrere Lesewege müssen auf konsistente, schnell zugreifbare Daten vereinheitlicht werden**, ohne die bewährte laufende Wiedergabe zu stören.
- `epg_sources.py` speichert geordnete aktivierte externe Quellen und benutzereigene `mappings`. Einige aktuelle Identitäten/Tabellenschlüssel berücksichtigen **Quelle nicht als getrennten eindeutigen Bestandteil** (`guide_alias(pid,alias,cid)`, `programmes(pid,cid,start,stop)`); identische Upstream-Kanal-IDs verschiedener XMLTV-Feeds können semantisch kollidieren. **#98 manuelle Quell+Kanal-Zuordnung** als Architekturvorgabe berücksichtigen.
- `epg_status.py` enthält bereits pro Quelle Stufen-/Fehler-/Erfolgsstatus (datensparsam); künftige UI sollte dieselbe Quelle nutzen.
- **Android .34 Logbelege aus** `docs/XCMate/LOGFORENSIK_02934_20261025_ZWEI_LOGS_DE.md`: Guide-Handoff funktioniert, Live-/EPG-Suche aber Minuten, u. a. 94-s-Abstand zwischen Ergebniskommittierungen und wiederholte Katalog-Scans. **Ein EPG-Hub allein behebt diese unabhängigen Cursor-/Suchursachen nicht; .35 Performancefix schützen und separaten Suchindex einplanen.**

## 3. Neuer zentraler Daten-/Merge-Vertrag

### 3.1 Quellenspezifische, kanalgenaue Eingangsidentität

- Rohfeed/-Source-ID **stabil und getrennt** von Portal-ID sowie Upstream-Channel-ID: z. B. intern `(portal_id, source_id, upstream_channel_id)`; bei manuellem Mapping `(portal_id, stream_id) → (source_id, upstream_channel_id)`. Fallback für Legacy-String-ID ohne Datenverlust / deterministische Konfliktmarkierung; **keine stillschweigende automatische Neuverkabelung der Sender**.
- Konservative Zuordnung von Sendername, `tvg-id`, Anbieterkennung, Region, HD-/SD-Variante und manueller Zuordnung; **gleichnamige verschiedene Länder/Regionen nicht blind zusammenführen**. #98 manuelles Preview & Confirm respektieren.
- Quellen-/Eventprovenienz in Staging und im resultierenden Guide speichern, bei Bedarf Diagnose im EPG, niemals Provider-URLs/Credentials öffentlich protokollieren.

### 3.2 Zeitabschnittsweise Konfliktauflösung statt „ganzer Sender zuerst“

- Für **denselben nachweislich zugeordneten Sender** eingehende Events nach Start/Ende normalisieren, nach Quelle/Vertrauen/Aktualität priorisieren. Tatsächliche Lücken einer hochrangigen Quelle nur mit validen, zeitlich passenden Events niedriger Priorität ergänzen.
- **Keine künstlichen Sendepläne**; bei Überschneidungen/verschobenen Zeiten nicht in beliebige „Teil-Sendungen“ zerschneiden oder Programmzeiten ohne Quelle erfinden. Klare Regeln für Konflikt, Doppelbelegung, Uhrzeit-Toleranz, regionale Abweichung, Sendungsänderung, Kurz-EPG gegen verifizierte XMLTV-Eventdaten. Bei unauflösbarem Konflikt höher priorisierte belegte Darstellung und Diagnose statt Phantom-Merge.
- Für spätere Catch-up-Fähigkeit **Event-Identität und exakte belegte Start-/Endzeiten** schützen; bei Korrekturen zwischen alten und neuen Quellen die zuverlässige Zeit-/Archiv-Referenz nicht fälschlich überschreiben.
- Diagnose pro Sender/Tag: `coverage_minutes`, `gaps`, `overlaps`, `conflicts`, `selected_source`, `last_success`, `stale`; ohne private Namen/URLs im GitHub-Log. Testfälle für Lückenschluss nach wirklichen Zieldaten definieren.

### 3.3 Stage → validieren → atomar/snapshotkonsistent publizieren

- Einzelne Feeds **unabhängig im Worker** downloaden/parsen (nur aktivierte/zugelassene Quellen), CRC/gzip/XML-Sicherheit und Byte-/Zeit-/RAM-/Disk-Budgets aus bestehendem Code erhalten. Speichere validierte Stage oder pro-Source-Generation; unter Quellfehler bisherigen Snapshot und eventuelle andere erfolgreiche Quelle behalten.
- Bei Änderung **betroffener Kanal-/Tag-Fenster** vorab gemergte Daten aufbauen, plausibilisieren, atomar die aktive Revision veröffentlichen. **Pro Portal konsistente EPG-Revision** für gleichzeitige Now/Next-, Guide-/Mini- und Suchabfragen. Keine Schreib-Locks auf dem UI-Thread.
- Unterschied **„Import läuft“ vs „Index aktuell“ vs „letzte gültige Daten vorhanden“ vs „Quelle fehlgeschlagen“** dokumentieren; kein Rückfall auf leeren Guide, nur weil die neue Quelle gerade nicht erreichbar ist.
- Batch-Verarbeitung mit Priorisierung konfigurierter **Startgruppe/gerade aktivierter Sender** für schnelle Aktualität, **ohne** die sichtbare UI während der Aktualisierung zu blockieren oder einen falschen vollständigen Abschluss anzuzeigen.
- **Nicht** auf jeder Navigation EPG-Refresh triggern; zeitgesteuert etwa gemäß bestehendem `epg_refresh_hours` (default 12 h), beim Start nur wenn erforderlich, und explizites manuelles Refresh. Quell-ETag/Last-Modified optional mit sicherem Fallback; Fehler-Backoff und begrenzte Workeranzahl.

## 4. Zeitfenster: 7 Tage Historie, maximal belegte Zukunft, Catch-up separat

- **Wunschwert:** lokale EPG-Historie **bis 7 Kalendertage rückwärts**, soweit die Daten aus Feeds tatsächlich geliefert wurden oder XCMate sie zuvor gespeichert hat. **Nicht rückwirkend aus dem Nichts nachbefüllen**. Nach konfigurierbarem Fenster altmodische Daten sicher/priorisiert aufräumen; keine Datenbank-Wachstumslecks. Sommer-/Winterzeit DST und Zeitzonen anhand UTC-Zeitstempeln + lokaler Tagesgrenzen korrekt (23-/25-h-Tage).
- **Zukunft:** alle echten Programme bis zum **tatsächlichen Feed-Horizont**, soweit definierte sichere Speicher-/Event-/Disk-Grenzen dies zulassen; vorhandenes 10-Tage-Fenster ist **derzeit ein technischer Codevertrag**, nicht Beleg, dass alle drei Quellen 10 Tage senden. Ein Vorschlag: konfigurierbarer Zukunftshorizont min. heutige Standardzeit/7–14 Tage **nach** Ressourcenmessung, ohne feste Vollständigkeitsgarantie.
- **Catch-up:** Archiv-Wiedergabe ist nicht automatisch durch gespeicherten EPG möglich. Erst vorhandene **Provider-/Sender-Catch-up-Flags, Archivdauer und technisch zulässige Replay-URLs/Aktionen** validieren; niemals Download/Playback-Button nur aufgrund alter EPG-Zeile aktivieren. Rechts-/Lizenzbedingungen und Nutzungsrechte bei externen XMLTV-Daten separat vor Veröffentlichung prüfen.
- Speicherbudget auf Android RK3528: Zahl Kanäle (im .34-Test **2764**) × Programme pro Tag × Zeitfenster × optionale Langbeschreibung quantifizieren; großen historischen Cache nur diskbasiert/komprimiert/indiziert, mit config-/portalgruppenspezifischen Limits und Cache-Pruning. Nutzung über Netzwerk-USB/SMB nur wenn explizit konfiguriert und sicher zugänglich, Standard lokal.

## 5. Einheitlicher schneller Leseindex und geordnete Datenversion

- **Großer Guide:** paginiert / sichtbarer Kanal-/Zeitbereich `portal_id, channel_id, window_start, window_end`; eine Indexquery pro sichtbarem Fenster, kein X-Quellenloop, kein HTTP im UI.
- **Mini-EPG:** links Senderliste, rechts **ständig Sendungen vorher / markiertes echtes JETZT / danach** für den markierten Sender (#95). Zuverlässiges `current/future/past` aus demselben veröffentlichten Snapshot, keine Live-Stream-Umschaltung bei Senderhover; `Rechts` nur Fokuswechsel in die rechte Seite. **Links→Gruppen→Links→Rail**, bestehende Bedienkette laut letzter Nutzerkorrektur.
- **Jetzt/Danach in Live-Infobar und Widgets:** derselbe Sender-/Zeit-Snapshot, keine Diskrepanz „Mini sagt etwas anderes als großer Guide“; der lokale Cache darf eine Quelle ändern, aber alle neu geladenen Leser sehen dieselbe revidierte Generation.
- **Globale Suche:** EPG-Programmtitel nach Zeit/Gültigkeit und Normalisierung **indiziert** nach Kanal, Quelle, Zeit und Titel-Tokens; **erste nutzbare Treffer in Sekunden statt Minuten**; nicht jedes Mal alle 2764 Sender auf `cached_short_guide` durchgehen. **.35-Suchperformancefix und bestehende Titel-/Genre-Suche (#159) nicht regressieren**, UI mit drei Tabs streng unverändert.
- **Spätere Catch-up-/Timer-Funktionen:** zunächst nur Datenschnittstelle, kein autonomer Downloader/Recorder und keine Behauptung unterstützter Wiedergabe.
- **Quellabdeckungs-/Mapping-Status** darf die EPG-UI bei Bedarf anzeigen (Quelle/Zeitfenster/letzter Stand), aber kein neuer Pflichtdialog oder umfassendes visuelles Re-Design in der Daten-PR.

## 6. Technische Lieferung in gestuften Folge-Draft-PRs

**EPG-HUB-0 – zuerst Diagnose und Architektur (kein produktiver Reset):** Reproduzierbarer Satz anonymisierter Drei-Quellen-Fixtures mit echten Konstellationstypen (nicht echten privaten Sendungs-/Portal-IDs), Old/New-DB-Schema, Quell-ID-Kollision, Lücken, Überschneidung, Importabbruch, flackernder Revision; Telemetrie für Cachehit, Merge-Laufzeit, DB-Größe, Rendering und NowNext-Konsistenz. Messwert-Bericht Ist vs Soll.
**EPG-HUB-1 – Daten/Quelle/Merge:** rückwärtskompatible Quell-IDs+Kanal-IDs, verlustfreie Migration, per-Source-Staging, Zeitintervall-Merge inkl. manueller Quelle, Quellenstatus/Provenienz, Fehler-/Fallback- und Atomik-Tests.
**EPG-HUB-2 – Horizont/Index:** 7 Tage historische Retention soweit vorhanden, Feed-abhängige echte Zukunft mit messbaren Limits, DST/Catch-up-Markierungen nur validiert, Suchindex und leichte paginierte Fensterabfragen, DB-Index/Migrations-Performance.
**EPG-HUB-3 – gemeinsame Leser/Android:** Guide, Mini-EPG „vorher/jetzt/danach“, Infoleiste, globale Sendungstitelsuche lesen denselben Snapshot; automatische/zeitgesteuerte/forcierte Updates ohne neue Latenz; echte Android-RK3528-Performance- und Stabilitätsabnahme.

**Coding- und Integrationsgrenzen:**
- Verbindlich **kumulativ auf aktuellem freigegebenem `main`**, keine Deinstallation/Downgrade, keine Account-/EPG-Mapping-/Gruppen-/Favoriten-/Art-/Resume-Löschung.
- Vor PR-Konzeption konkurrierende laufende `.35`-Search-Patches sowie #98 manuelle EPG-Mapping- und #95 rechte Mini-EPG-Panels als **Integrationsabhängigkeiten** prüfen, kein Merge-Kampf der Quellen-IDs.
- Ausdrücklich nicht: Ersatz/Rewrite der Kodi-Player-Engine, UI-Redesign der vom Nutzer eingefrorenen **Live-TV | Filme | Serien**-Suche, Abschalten von XMLTV-/Inflate-/SQLite-Budgetgrenzen, automatischer Alt-Branch-Merge.
- Jeder PR: Design-/Migrationsnotizen, echte Code-/Host-Tests, überprüfte Android-Tests zunächst **NOT_TESTED**, ZIP+SHA und Änderungsbericht; **kein automatischer Merge/Pub/Release** ohne ausdrücklichen Nutzerauftrag.

## 7. Definition of Done / Tests (alles bis echte Abnahme NOT_TESTED)

| Gate | Beleg |
| --- | --- |
| HUB-01 | Bei Quelle A lückenhaft, B/C teilweise vorhanden: nur **richtige** fehlende Zeiträume werden ergänzt; Quelle und Konfliktgrund auswertbar. |
| HUB-02 | Überlappende/regionale oder zeitverschobene Sendungen werden nicht willkürlich zusammengeschnitten/vertäuscht; manuell gewählte **konkrete Quelle+Kanal-ID** schlägt Automatching. |
| HUB-03 | Gleiche externe Channel-ID aus zwei Feeds bleibt **quellenspezifisch**, keine gegenseitigen Programme; Legacy-Mapping migriert ohne Verlust/unerlaubte Umbelegung. |
| HUB-04 | Download-/Parse-Timeout, kaputtes gzip, Source offline, Neustart während Import: **letzter vollständiger publizierter Guide bleibt verfügbar**; spätere erfolgreiche Quelle kann trotzdem Daten beitragen. |
| HUB-05 | Historical EPG *bis zu* 7 Tage vorhanden, wenn zuvor aufgenommen/geliefert; abwesende historische Slots werden als fehlend markiert, **nicht** erfunden; alte Events werden nach Policy sicher entfernt. |
| HUB-06 | Zukunft bis echtem Quellenhorizont innerhalb Limits, Source-Abdeckung/Frische und Sync-Status sichtbar; 23-/25-h-DST-Tage korrekt. |
| HUB-07 | Groß-EPG, Mini-EPG, Infobar NowNext, Programmsuche und Widgets lesen **dieselbe Revision**; während Refresh kein Leerblitzen/Reordering/Fokusverlust und kein unkontrollierter Playerstart. |
| HUB-08 | EPG-GUIDE öffnet auf RK3528 schnell aus lokalem Store, rechte Mini-Programmansicht folgt Senderhover sofort, Programmtitel-Suche liefert erste nutzbare Ergebnisse **in Sekunden**; Zeit- und Quellen-Komplett-Scan läuft ausschließlich Hintergrund. |
| HUB-09 | Provider-Catch-up nur wo belegte Archivdaten/Flags, kein falsches Abspielen historischer EPG-Zeilen; Senderreihenfolge, Gruppenfilter, manuelle Zuordnung und Startsender unverändert. |
| HUB-10 | 2.764+ Sender, bis 7 Tage Historie und wirklicher Zukunftshorizont auf Android mit **DB-Größen, Peak-RAM, Importzeit und SQLite-Lock/Busy-Werten** dokumentiert, keine GUI-Blockade/OOM. |
| HUB-11 | Nicht-VOD-Player/Suchmasken-/LiveSession-/Serien-Autoplay-Regressionsprüfung, bestehende .34/.35-Android-PASS bewahrt; kein Wechsel von Kodi-Homescreen oder Fremdplayer-Stop. |

**Verwandte Arbeiten:** [#57](https://github.com/artattakk-creator/kodi-noodleprivate/issues/57) großer Guide; [#95](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95) rechte Mini-EPG-Programmspalte; [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98) Quell+Kanal manuell zuweisen; [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140) Suchperformance; [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143) Master-Roadmap; [#159](https://github.com/artattakk-creator/kodi-noodleprivate/issues/159) Genresuche. **Nächste konkrete Versionsnummer nicht vorzeitig belegen.**
