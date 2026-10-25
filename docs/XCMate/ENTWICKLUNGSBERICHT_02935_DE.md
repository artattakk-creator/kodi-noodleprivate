# XCMate 0.1.29.35 – Suchperformance, Infobar-Guide, Gruppen und Fokus

25.10.2026. Basis `main` **030b81569d5b96b153ba1060be8525c24d27dcf3**, veröffentlichter Index und Add-on .34. Ziel .35 bei Preflight frei, keine offene .35-PR; ältere Drafts nicht übernommen. Verbindliche .35-Auftrags-/Abnahmedokumente, .34-Zwei-Log-Forensik, Detailbrief, UI-Freeze sowie Issues #140/#127/#143/#17/#88/#91 berücksichtigt. Aktuellere #127-Nutzerkommentare bestätigen G4 inklusive Nacht-Autoplay/Staffelwechsel; ältere historische Abnahmen bleiben unverändert.

## A – reproduzierte Suchkosten und Korrektur

Die .34-Logs belegen eine 94,082-s-Lücke zwischen Resultat-Commits und wiederholte Scans; die genaue Verteilung dieser 94 Sekunden auf dem Android-Gerät ist rückwirkend nicht bewiesen. Insbesondere ein früher `SEARCH_RESULT_READY` ist kein Nachweis eines sichtbaren Live-Treffers.

Host-Reproduktion mit echtem lokalem SQLite-Katalog, 2.764 Sendern und Treffern am Katalogende:

- .34 initialisiert vollständigen Katalog/Mapping/Now-EPG, bevor Namen geliefert werden. Anschließend stehen fehlende Cache-Lookups früher Sender vor einem Namens- oder Programmtreffer am Ende. Bei kontrolliert **40 ms synthetischen Kosten je lokalem Short-Cache-Lookup** wird der erste späte Namenstreffer erst nach **110,56 Modellsekunden** veröffentlicht. Es wird nicht behauptet, dass Android tatsächlich 40 ms je Lookup benötigt.
- .34 fragt pro Fortsetzung Filme und Serien erneut ab: im selben Modell **1.012 Reader.page-Abfragen**. Der Cursor wird während eines Workers aus der Fensterreferenz entnommen; Tabwechsel kann diesen Worker ersetzen und einen neuen Cursor starten. Ein Test bestätigt die Stornierung des laufenden Jobs bei reinem Tabklick.
- .35 liefert zuerst lokale Namensmatches aus dem bestehenden PID-/Gruppen-gefilterten SQL-Index, ohne EPG-Initialisierung oder Short-Cache-Lookups abzuwarten. Danach liest ein Worker lokale Now-Ereignisse/Aliase und ergänzt echte Programmtreffer in der vorhandenen Ergebniszeile. Erst anschließend werden fehlende, nicht manuell zugeordnete Short-Caches verarbeitet. Keine Provideranfrage im Suchpfad.
- Derselbe Cursor bleibt während des Jobs und beim Tabwechsel erhalten. Einmal gelesene Medienseiten werden in einem begrenzten Cache von maximal zwölf Seiten gehalten; im Modell nur **zwei** Medien-Seitenabfragen für den ganzen Live-Scan. Namensresultate können bereits gewählt werden, während die EPG-Fortsetzung noch wartet.
- Revisionsprüfung unterscheidet echte Katalog-/Guide-Veröffentlichungen von WAL-Bookkeeping und fremden Portalen. Änderungen der Film-/Serienkataloge invalidieren nur deren Seiten. Mappings/Gruppen und portalbezogene Short-EPG-Revisionsmarker werden berücksichtigt. Abgeschlossene Now-Snapshots werden bei bekanntem Programmende bzw. maximal einer Stunde erneuert; kein pauschaler 30-Sekunden-Vollscan bei jedem Tabwechsel. Eine ausdrücklich bestätigte neue Anfrage erzeugt eine neue Generation und verwirft alte Callbacks.
- Bestehende SQLite-Indizes für PID/Kanal/Zeit werden verwendet. Es gibt keine FTS-Abhängigkeit oder DB-Migration. Beliebige Teilwortsuche ist kein neu erfundener B-Tree-Volltextindex; selektive SQL liefert nur passende Payloads, statt für erste Namen den gesamten Katalog in Python zu prüfen. Bestehende 50.000-Kanal-Grenze, Query-Deadlines, WAL/Locks und read-only Guide bleiben erhalten.

`PERFORMANCE_02935_HOST.json` enthält Modell und reale Host-Wandzeiten. Drei frische Cursor lieferten das erste lokale Namensergebnis auf diesem Host in etwa **3,6–3,9 ms**. Das ist **weder kalter Android-Storage noch sichtbares Kodi-Rendering**. Im Modell bleibt der vollständige Short-Cache-Scan 110,56 Modellsekunden lang; die Verbesserung liegt in frühen bedienbaren Treffern, früher XML-Titelauswertung und vermiedener Nebenarbeit. Reale RK3528-Ziele <5 s warm / <10 s kalt und Programmtreffer deutlich unter 120 s bleiben Android-Gates NOT_TESTED.

Reproduktion: `python tools/benchmark_search_02935.py` (vollständige Git-Historie bzw. Basiscommit verfügbar, Host-Testabhängigkeiten). Keine echten Provider, Netzaufrufe, Sleeps, Profil- oder Cache-Löschung. Der Benchmark schreibt ausschließlich seinen Hostbericht neu. `test_xcmate_search_performance_02935.py` prüft zusätzlich die injizierte 94-Sekunden-EPG-Stufe, 50k-Grenze, tatsächlichen frühen Control-List-Klick, Programmreihenfolge, echte SQLite-Sperre, SQL-Queryplan, Portaltrennung, Revisionen, neue Queries und Datenschutz.

## Profiler und Aussagegrenzen

Feste Phasen `QUERY_ACCEPTED`, `TAB_LIVE_SELECTED`, `LIVE_CURSOR_INIT_BEGIN/END`, `INDEX_QUERY_BEGIN/END`, `MAPPING_BEGIN/END`, `EPG_NOW_SQL_BEGIN/END`, `SHORT_EPG_CACHE_BEGIN/END`, `SLICE_BEGIN/END`, `FIRST_NAME_MATCH`, `FIRST_PROGRAMME_MATCH`, `FIRST_LIVE_ROW_RENDERED`, `SCAN_FINAL`, `QUERY_CHANGED`, `STALE_CANCEL`; zusätzlich Worker-Queue und Row-Render. Monotonic-Nanosekunden werden als Millisekunden/Dauer ausgegeben; Zufalls-Generation und Fenster-Owner korrelieren die Phasen. Kein Query-Hash, Suchtext, Portal-/Sender-ID, URL, Pfad oder Exceptiontext.

Worker-/Renderereignisse aggregieren Anzahl und Warte-/Ausführungszeit; Slice-Spuren werden begrenzt, First-/Final-/Abbruchphasen bleiben. `FIRST_LIVE_ROW_RENDERED` bedeutet erfolgreich belegte native Ergebniszeilen im Host-/Kodi-Aufruf, **nicht** automatisch vom Benutzer gesehene oder abgenommene Treffer. Alle Gerätelatenzen werden separat in PERF-01–04 erfasst. Programmtreffer beziehen sich auf den gültigen Now-Snapshot der Anfrage; Namensmatches werden nicht als Programmtreffer gezählt.

## B – EPG aus der Infobar ohne Playback-Unterbrechung

Nur `_execute('extras',3)` erzeugt einen One-shot-Auftrag. Native Callback-/Doppel-SELECT-Ereignisse schließen kein Fenster und lösen weder RunPlugin noch Wiedergabe aus. Der Service prüft ursprüngliches Live-ListItem, Portal/SID/Nonce und seinen eigenen Dialog, suspendiert diesen ohne Löschen der LiveSession und wartet auf tatsächliche native Freigabe. Fremde Dialoge werden weder geschlossen noch ignoriert.

Danach startet der Service einen separaten `live_guide`-Aktionsaufruf mit zufälligem Token. Dieser übernimmt die vorhandene Navigation-Lease und öffnet `guide_grid_window.open_grid` **ohne Home-/Container-Anker**. Dialog-/Guide-/Search-Pump und der bewährte .34-Handoff bleiben bytegleich. Der Service pollt weiter Hintergrundarbeit, Resume und Serien-Autoplay; nur seine konkurrierende Live-Overlay-Neuerstellung und der Exit-Stop für das ursprüngliche Live-Item sind während der Exkursion gesperrt. Fremde Medien werden nicht übernommen.

Back ohne Senderwahl lässt den ursprünglichen Stream weiterlaufen und kann die bestehende Info-Ebene wiederherstellen. Auswahl eines Senders wird erst nach Guide- und Lease-Freigabe genau einmal an den unveränderten .34-Live-Resolver übergeben. Replay, Timeout, Shutdown, ungültige Session, fremde Modals und verlorene Plugin-Lease sind geprüft. Keine Suche/Player-Rewrites, keine neuen GUI-Dauerthreads. Links/Links bleibt Mini-Liste/Gruppen; konfigurierbare bisherige Mini-EPG-Aktionen bleiben erhalten.

Dieser neue Service-/Plugin-Übergang ist trotz Hosttests ein **gezieltes Android-Risiko**: ROUTE-01–04 und REG-03 sind verpflichtend. Eine echte Kodi-21.2-/ARM32-Ausführung ist auf diesem Host nicht verfügbar; strikte native API-/Owner-Modelle ersetzen keine Geräteabnahme.

## C – isoliert geprüfte Gruppen-/Fokuskorrekturen

Zwei konkrete Hostfehler gefunden: Eine gültige gespeicherte Gruppe wurde bei dort nicht vorhandenem Startsender trotzdem durch dessen andere Gruppe ersetzt. Außerdem wurde nach leerem Katalog-Erstaufruf die Startauswahl nicht erneut ausgeführt. Das erklärt überprüfbare Fehlerpfade, beweist aber nicht nachträglich jeden vom Nutzer als „Alle“ beschriebenen Bildschirm.

Jetzt bleibt eine gültige Startgruppe maßgeblich; Startsender wird nur darin markiert. Bei ungültiger/deaktivierter Gruppe folgt erlaubte Gruppe des Startsenders, dann erste aktivierte Gruppe, sonst expliziter Leerzustand. Ein anfangs fehlender Gruppenkatalog wird begrenzt im Worker nachgeprüft; nach Verfügbarkeit erfolgt die Startauswahl. Explizite Gruppenwahl und Guide-Rückkehr werden danach respektiert. Keine Start-/Gruppen-/Portalwerte gespeichert oder überschrieben. Anonyme INITIAL-Diagnose enthält ausschließlich Gruppenzahl, Auswahl-/Gültigkeitsflags, Zeilenanzahl und Kategorieklasse leer/Star.

Die Mini-Liste konnte ihre zuletzt besuchte Zeile behalten; bei identischem Listeninhalt wurde ein neuer aktueller Highlight nicht wieder auf das native ListItem übertragen. Explizites Links aus Vollbild/Info richtet jetzt Gruppe und sichtbare Position am tatsächlich laufenden portalgebundenen Live-Item aus und aktualisiert den nativen Selektionszustand. Ohne solchen Live-Besitz gilt der gültige Startkontext. Gruppenwechsel innerhalb der Liste bleibt eine Ansichtsauswahl. C ist enthalten und separat getestet; GROUP-01/02 und MINI-01 bleiben NOT_TESTED.

## D – kleine Härtung und Bestandsschutz

Ein fehlgeschlagener erweiterter Short-Cache verdeckt nicht mehr eine gültige Vier-Ereignis-Variante; umgekehrt bleibt die gültige erweiterte Variante erhalten. Beide nicht verfügbar: neutraler Zustand, keine zusätzlichen HTTP-Retries oder Dateischreibaktionen. Vorhandene Short-EPG-Netzgrenzen und Service-Backoff bleiben unverändert. Keine Decoder-/Kodi-Core-Fehlerunterdrückung.

Der harte UI-Freeze prüft **163** Dateien aus .34; darunter alle Such-/Guide-XMLs, Grafiken, Medienansicht, Ergebnisrenderer und der vorhandene Window-/Search-/Player-Handoff. Weitere Schutzprüfung: **245** unveränderte Add-on-Dateien, alle **98** Space-Premium-Bilder, **62** fremde WIP-Dateien. Live-Renderer/Player-Methoden und Guide-Render-/Play-Aktionen bleiben AST-identisch. Serien-Autoplay/Resume-/State-Dateien, Recorder/Downloads, Originalicon, Repository-Indizes, Release-Workflow und altes .34-ZIP unverändert. Keine behauptete Pixelabnahme ohne reale Referenzscreenshots.

Historische Freeze-Tests behalten ihre alten Digests; nur exakt geprüfte .35-Guide-/Fokus-Hooks werden für diese Vergleiche normalisiert. Ein alter Test „Startsender verdrängt gültige Gruppe“ wurde bewusst auf die neu verbindliche Startgruppenpriorität umgestellt; normale Fixtures verwenden jetzt einen konsistenten Startkontext. Separate Negativ-/Kaltstarttests behalten die Konfliktfälle.

## Lieferung und Freigabe

A/B/C/D sind in getrennten Commits reviewbar. Kumulativer Draft auf aktueller main-Basis, installierbares .35-ZIP, SHA256, vollständiger Host-/CI-Output, Paket-/Schutzbericht und vorhandene `ANDROID_ABNAHME_02935_DE.md`. Alle **15** Android-Gates V0/PERF/ROUTE/GROUP/MINI/REG sind NOT_TESTED. REG-03 deckt auch die im Detailbrief zusätzliche ROUTE-05-Wiederholung von Guide→Suche→Back ab. Keine erneute nächtliche Vollabnahme pauschal verlangt.

#111 Poster/TMDb, #98 EPG-Zuweisung, #95/#100, Codec-Rewrite, Downloads/Recorder und weitere Designarbeiten sind nicht enthalten. #140/#127/#17/#88/#143 bleiben offen. Kein Merge, Release, OTA, Installieren, Downgrade, Deinstallieren, Profilreset oder Datenlöschung durch Codex; Installation/Update erst nach ausdrücklicher Nutzerfreigabe.

Abschlussabgleich: main ist während der Entwicklung auf `e7202b5d824b9497188c7159eee8c5b58f2464aa` vorgerückt, ausschließlich durch die Folge-Roadmap `ROADMAP_NACH_02935_NAV_RAIL_PLAYER_OSD_20261025_DE.md`. Diese Dokumentation wurde in den Entwicklungsbranch übernommen; Source- und Test-Git-Trees blieben identisch. Rail, rechte Mini-Programmspalte, Genresuche und Player-Redesign ausdrücklich erst nach .35-Abnahme; nicht in diesem Paket implementiert. Finaler Draft ist kumulativ auf diesem aktuellen main; geprüfter Code/Teststand `4609a4b86902d797603315396dfcd6a6e33ef510`.
