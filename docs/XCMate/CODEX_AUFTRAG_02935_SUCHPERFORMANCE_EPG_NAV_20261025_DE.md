# Codex-Auftrag – XCMate 0.1.29.35: schnelle Live-/EPG-Suche, großes EPG aus Infobar, Startgruppe & Senderfokus

**Verbindliche Übergabe: 25.10.2026**  
**Produkt:** GS Media XCMate, Add-on-ID `plugin.video.xtreammate`  
**GitHub:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Gerät:** Android TV 13 / RK3528 ARM32 / Kodi 21.2 Omega / Titan BINGIE MOD, IR-Fernbedienung  
**Aktueller produktiver, auf main bestätigter Stand bei Beauftragung:** **0.1.29.34**  
**Nächster Kandidat:** **0.1.29.35**, sofern bei Arbeitsbeginn noch frei und `main` nicht vorgerückt ist. **Kein Update ohne explizite Nutzerfreigabe**, nicht mergen oder veröffentlichen.

## 0. Verbindliche Lektüre, Schutzverträge und Versionssicherheit

Vor Codeänderungen **diese Dokumente und die aktuellen offenen Issues vollständig lesen**:

1. [Zwei Kodi-Logs vom 24./25.10., datensparsame .34-Forensik](LOGFORENSIK_02934_20261025_ZWEI_LOGS_DE.md).
2. [Detailbrief Live-Suchperformance / Infobar-EPG](CODEX_BRIEF_02935_LIVE_EPG_PERFORMANCE_ROUTING_DE.md).
3. [VERBINDLICHER UI-FREEZE der globalen Suche](SUCHMASKE_UI_FREEZE_02934_20261025_DE.md).
4. [Android-Abnahme .34 G1–G4](ANDROID_ABNAHME_02934_DE.md), ergänzt durch Nutzerkommentare in [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140), [#127](https://github.com/artattakk-creator/kodi-noodleprivate/issues/127), [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143), [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88) sowie [#91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91).

**Preflight:** Prüfe `git rev-parse main`, version in `src/plugin.video.xtreammate/addon.xml`, den veröffentlichten Add-on-Index und sämtliche neuen/offenen PRs. Beim Auftrag existierte **noch kein .35-PR**; ältere Drafts (u. a. #157 und Space-Premium #50) sind **keine** Implementierungsbasis. Branch **von aktuellem main HEAD** erstellen, `.34 → .35` kumulativ; niemals alte Versionen zum Test installieren/deinstallieren oder bestehende Nutzer-Settings, Portale, Gruppen-Checkboxen, EPG-Mappings, Artwork-/SQLite-DBs, Resume-/Favoritenstände zurücksetzen.

**Bereits echtes Android-PASS und daher geschützt:**
- Großer Guide → Senderstart **zuverlässig**, `GUIDE_HANDOFF QUEUED → RESOLVER_REQUEST → DISPATCHED` mehrfach im .34-Log; Guide→Suche→Back zum Guide funktioniert. Den aus PR #158 reparierten WindowDialog-/Owner-/Busy-Lifecycle nicht zurückbauen.
- Die **bestehende Suchmaske bleibt optisch und im Bedienablauf eingefroren**: drei dauerhaft sichtbare Bereiche **Live-TV | Filme | Serien**, gleiche Reihenfolge, Layout, Senderlogos, Poster, Fokus-, Detail- und Back-Verhalten. **KEIN Redesign / keine neuen Tabs.**
- Filme/Serien reagieren relativ schnell, Cover/Details/Staffeln/Episoden und Rückkehr zur Suchmaske **PASS**.
- **Serien-Autoplay läuft über Nacht über geschätzt 7–8 Folgen, auch staffelübergreifend, PASS**; nicht an Player/Stop/Next/Resume/Staffelreihenfolge umbauen.
- Original-XCMate-Icon (Space Premium / Core), vorhandene Logos/Cover/Themes und Fernbedienungs-Overlays erhalten.

## 1. P0/P1 – Hauptaufgabe: Live-TV- und Programmtitel-Suchperformance (#140, #127)

**Reale Symptome .34:** Sendername findet Treffer und lässt sich aus Suche abspielen; Programmtitel einer tatsächlich laufenden Sendung ist auffindbar; aber Wartezeit laut Nutzer ca. **1 Minute (Sendersuche)**, **2 Minuten (Jetzt-Sendung)**, zuletzt **gefühlte 3–5 Minuten nach Auswahl des Live-TV-Tabs**. Diese Werte sind grobe Nutzerschätzungen, keine instrumentierten Messwerte. Film-/Serien-Suche ist deutlich schneller. Nicht behaupten, Tabwechsel starte die erste Suche – das ist eine zu überprüfende Benutzerhypothese.

**Harte Log-Evidenz nach Installation von .34 erst 25.10., 06:56:01:**
- Suchfenster 07:52:22 nutzungsbereit (`SEARCH_GUI_READY`), `SEARCH_RESULT_READY` 07:52:24.670; nächster solcher Commit 07:53:58.752, **94,082 s Pause**. Erster `SEARCH_EPG EPG_PARTIAL` nur um 07:53:58.191 bei **25/2764** geprüften Kanälen. Ein früher Result-Commit ist **nicht zwangsläufig ein sichtbarer Live-Treffer**.
- In anderen Sessions mehrfach neue kleine `scanned`-Zähler nach höherem Stand, mindestens ein vollständiger `READY scanned=2764 programme_hits=1`; nach einem weiteren vollständigen `READY scanned=2764` beginnt in derselben Suchfenster-/Dispatchgruppe erneut `EPG_PARTIAL scanned=14`. Ohne neue Query-/Tab-Generationsmarker **noch unklar**, ob legitime erneute Suche oder versehentlicher Restart.
- EPG-Now-Snapshot zeigte in vollständig gescannten Läufen ca. 104–108 aktuelle Programmtitel für 2764 Sender – **kein** Beleg, dass nur so wenige Provider-Programme existieren oder EPG-Import generell falsch ist.

**Konkreter Codeabgleich main .34:** `resources/lib/search_data.py::LiveSearch.__init__` liest Live-Kanäle/Mapping/EPG-Now-Snapshot, `_now_events()` fragt SQLite-Aliase/Programme, `LiveSearch.step(budget=.2)` maximal **64 Kanäle pro Slice** und potenziell `cached_short_guide` bei fehlendem XMLTV-Now. `resources/lib/media_search.py::_search_ready` plant bei `_continuation` erneut `_search_load`; `_search_click` reagiert auf Tab. **Alles prüfbare Kandidaten, noch keine bewiesene Root-Cause.** `library_index.py`, `epg_views.py` und SQLite-Konfiguration #91 nur so weit zur konkreten Messung relevant.

**Verbindliche Aufgaben:**
1. **Vor dem Fix reproduzieren und messbar instrumentieren** mit `time.monotonic_ns()`/monotonic ms und anonymem **Suchgenerations-/Window-Owner**: `QUERY_ACCEPTED`, `TAB_LIVE_SELECTED`, `LIVE_CURSOR_INIT_BEGIN/END`, `INDEX_QUERY_BEGIN/END`, `EPG_NOW_SQL_BEGIN/END`, `SHORT_EPG_CACHE_BEGIN/END`, `SLICE_BEGIN/END`, `FIRST_NAME_MATCH`, `FIRST_PROGRAMME_MATCH`, `FIRST_LIVE_ROW_RENDERED`, `SCAN_FINAL`, `QUERY_CHANGED`, `STALE_CANCEL`; Queue-Wartezeit vs SQL vs Mapping vs Kodi-UI klar trennen. **Keine privaten Suchbegriffe, Provider-IDs/URLs, Passwörter, echten Stream-IDs oder lokalen Pfade öffentlich protokollieren.**
2. Sicherstellen, dass **Sendernamen-Treffer aus lokalem Index frühzeitig bedienbar erscheinen**, unabhängig davon, ob vollständiges Now-EPG/Short-EPG geladen ist. Bei teilweisem/no EPG nur vorhandene neutrale Beschriftung innerhalb eingefrorener UI verwenden, **keinen fiktiven Jetzt-Titel**.
3. **Programmtitel-Suche** über **lokale, zeitlich gültige und indizierte** Now-/EPG-Ereignisse/Quellen-Mappings effizient machen. Nur dann Short-EPG-Fallback; keine blockierenden Provider-Requests, EPG-Downloads oder lang laufenden SQL-Jobs im Kodi-GUI-/IR-Thread. Keine versehentliche Vermischung verschiedener Portal-, Kanal- oder EPG-Source-IDs; manuelle Zuordnungen respektieren.
4. **Teure Cursor-Initialisierung und Vollscan-Wiederholungen** vermeiden: Suchgeneration bei reinem Tabwechsel **nicht grundlos neu initialisieren**, Cache/EPG-Revisionen beachten; echte geänderte Anfrage darf neue Generation erstellen, ältere Jobs müssen sauber abgebrochen werden. Bei spätem Worker-Ergebnis keine Ghost-Treffer, kein Überschreiben neuer Daten, kein Fokus-/Scrollbar-/Tab-Sprung.
5. `SQLite BUSY`/Worker-Queue und kurze `query_seconds`-Grenzen prüfen (#91); **keine** WAL-/Transaktions-/Dateilock-Sicherungen abschalten, keine unkontrollierten Parallel-Reader oder neuen Dauerlast-Threads.
6. **Präziser Test:** Nach Änderung erneut mit mindestens 2764 simulierten Kanälen und Android Cold-/Warm-Suchen testen. **Engineering-Ziel** zuerst nutzbare Sendernamens-Treffer typischerweise **unter 5 s warm / 10 s cold** (Ziel, nicht vorweggenommener PASS); erste Programm-Matches **deutlich unter 120 s**, ideal wenige Sekunden; kompletter Hintergrundscan darf länger dauern, darf aber UI/Playback/Back nicht blockieren. Zeitwerte real auf RK3528 erfassen und berichten.

**Nicht ändern:** `media_search`-Suchmaske, Visuals/Fokus/OSD-Elemente, Film-/Serien-Suchlogik und Autoplay, soweit nicht technisch unvermeidbar (dann isolierte Regressionstests). Kein pauschales Hochsetzen eines globalen Timeouts als Pseudo-Fix.

## 2. P1 – kleine zwingende UX-Änderung: Infobar-EPG-Button → GROẞER EPG (#17)

**Verbindlicher Nutzerwunsch:** Im laufenden TV soll **Infobar (OK) → zweite Bedienleiste (OK erneut oder Runter) → Weitere → EPG** den **GROSSEN horizontalen Guide** öffnen. Die **kleine** Sender-/EPG-Liste bleibt erreichbar über **Links** aus Vollbild/Info, Links erneut → Gruppen. Kein Umbau des zweistufigen Info-/OSD-Designs.

**Codefund:** In `resources/lib/live_overlay.py::LiveNavigator._execute('extras',index=3)` steht `self._epg()`; `_epg()` wechselt intern nach `mode='guide'` und **öffnet NICHT** `app_routes.action='guide_grid'`. Das große native Guide-Routing existiert bereits in `app_routes.py` mit `guide_grid_window.open_grid`.

**Umsetzung:**
- Nur die **EPG-Schaltfläche der Extra-/Info-Leiste** (und klar gleiche semantische Button-Aktion) auf native `guide_grid`-Route umleiten. `_epg()` **nicht** global unbedacht ersetzen, solange andere Keybindings/Miniguide-Verträge davon abhängen.
- Mit `service.py`-Owned-`LiveNavigator` / XCMate-LiveSession sichere **einmalige** Navigation arrangieren: Overlay-Dialog/Owner freigeben, anschließend großen EPG öffnen, Player **läuft im Hintergrund weiter**. Bei Back ohne neue Senderwahl zu ursprünglichem Live-Video/Infobar-Kontext; kein `RunPlugin` unmittelbar aus `onControl` oder konkurrierende native Dialoge/Root-Dispatches. **Kodi-21.2-Lifecycle und echtes Android testen.**
- Auswahl „Jetzt Sender ansehen“ im großen EPG muss **genau einen** bisherigen Resolver-/Player-Start auslösen; niemals ungewollter Home-Sprung/PlayerStop. Doppeltes Fernbedienungs-SELECT `onAction`/ `onControl` absichern. Fremde Modal-Dialoge respektieren.
- **Links** aus Live-Vollbild/Info muss weiterhin **Mini-EPG/Senderliste** öffnen, Links erneut Gruppen; nicht versehentlich auf großen Guide umstellen.

## 3. P2 – zwei kleine, gezielte Navigationskorrekturen (#88 / #17)

### 3a. Großer EPG startet in der gespeicherten Startgruppe

Beim **ersten** Öffnen des großen Guides zeigt das Gerät fälschlich „Alle aktivierten Sender“ statt **gespeicherter `start_group_id`**, obwohl `guide_grid_data.initial()` bereits Startgruppenauswahl versucht. **Zuerst tatsächlichen Runtime-Einstieg, aktivierte `Reader.groups('live')`, gespeicherte ID, Katalogbereitschaft, Index-ID-Feld und `Reader.page(category=...)` datensparsam vergleichen; keine Ursache raten.**

Soll: Beim ersten Aufruf direkt **nur Startgruppe**, Startsender markiert, wenn innerhalb vorhanden. Später explizit gewählte andere Gruppe im aktuellen Guide-Kontext respektieren, niemals ohne Benutzeraktion nach `'*'`/allen aktivierten Sendern springen. Wenn Startgruppe ungültig/deaktiviert, **sicherer Fallback** in aktivierte Gruppe des Startsenders, sonst erste aktivierte Gruppe, sonst expliziter Leerzustand; gespeicherte Einstellungen nicht überschreiben.

### 3b. Mini-Senderliste fokussiert aktuellen Sender

**Links aus laufendem Live-TV:** Mini-Senderliste fokussiert **tatsächlich spielende XCMate-`stream_id` (Portal beachten)** und scrollt diese Zeile sichtbar ins Viewport. Vor Erststart und ohne laufende XCMate-Sitzung den gespeicherten Startsender in seiner gültigen Startgruppe markieren. Bei Senderwechsel/Gruppenwechsel Liste konsistent aktualisieren; keine voreilige Alle-Sender-Ansicht. **Gruppenwechsel im Mini-EPG ist keine persistente Änderung der Startgruppe**. Cursornavigation/OK/Back/Infoleiste nicht regressieren.

**Scope-Gate:** Diese zwei Korrekturen in .35 aufnehmen, **sofern als isolierte, in Kodi-Tests überprüfbare Fixes möglich**. Werden sie architektonisch riskant für Handoff oder Player, **separat dokumentierten Folge-Draft-PR** vorbereiten, statt den Kernfix untestbar zu vermischen. Kein stilles Weglassen oder PASS ohne Gerät.

## 4. P2/P3 – zusätzliche kleine Robustheitsmaßnahmen ohne Funktionsumbau

- Aus echtem .34-Log **ein** `Xtream API get_short_epg ... TimeoutError` um 07:00:12. Prüfe **nur** den lokalen Fehler-/Fallbackpfad: begrenzter Retry/Backoff, Cached-Now-Werte erhalten, Suche nach Sendername darf nicht auf Short-EPG warten; fehlender Status als neutral/no EPG ausweisen. Kein großer EPG-Quellenwechsel, kein neuer Feed-Import oder unbegrenzte Netz-Retries.
- **Keine massiven Diagnoseschleifen von XCMate**: gleiche mehrfache Statusmeldung bei unveränderter Phase/Katalogzustand ggf. gedrosselt und aggregiert (Zahl + Gesamtzeit), aber wichtige Abbruchgründe/First-Result/FINAL erhalten. **Kodi-Core MediaCodec-Errors nicht unterdrücken**.
- Die **111.570 Kodi-Android-Decoder-dequeue-Fehler** im historischen **.33**-Log gehören in [#87](https://github.com/artattakk-creator/kodi-noodleprivate/issues/87). In .34 kein entsprechender Fehlersturm. **Kein Player-/Codec-Rewrite**, kein neuer Global-Codec-Override; als separate Diagnose lassen.
- **#111 Poster-Retry/TMDb-Fallback, #98 EPG-Quelle manuell zuweisen, #95 Rechts→Programm-Vorschau, #100 weitere Infobar-Technikdaten, #94/#150 Icon-Rail, Downloads/Recorder, Space Premium** gehören **nicht** in .35. Wichtige Ideen, aber riskanter Feature-Scope und keine Abhängigkeit zum Hotfix.

## 5. Pflicht-Tests, Liefervertrag, Abnahme und Veröffentlichungsverbot

In getrennten Commits/Git-Diffs liefern: **(A) Profiler + Search-Fix**; **(B) Infobar→großer EPG**; **(C) Gruppen-/Senderfokus-Fixes** (nur nach Risikoprüfung), **(D) nur kleine EPG-Timeout-/Logging-Härtung**. Erst A stabilisieren, B und C einzeln testen. Keine Design-Rewrites.

**Automatisierte Kodi-21.2-Hostregressionen:** Live-Katalog 2764 und 50k-Limit, Cold/Warm-Performance unter kontrollierbarer Clock, EPG-Now mit/ohne Daten, externe/manual Mappings und gleiche Sendernamen, gezieltes Cache-Timeout, Thread-/Queue-Cancel, Queries/Tabwechsel im Sekundenabstand; SearchWindow Fokuserhalt/3 Tabs, Guide-Dialog Ownership mit fremdem Busy, Service-/LiveSession-Single-Dispatch, Back→Video und Guide→Sender, Gruppenfallback und SID-Fokus, Video/Serien/NextEpisode/Staffelübergang, keine Datenänderung.

**Gerätetestliste (alle bei Draft Erstellung NOT_TESTED):** [ANDROID_ABNAHME_02935_DE.md](ANDROID_ABNAHME_02935_DE.md).

**PR muss enthalten:**
- Zielversion korrekt, neue **Draft-PR** ab aktueller `main`; Beschreibung Root-Cause-Vorher/Nachher samt echten Host-/später Android-Messdaten, getrennte Changelog-Bereiche.
- Paket `plugin.video.xtreammate-0.1.29.35.zip` (oder bei fortgeschrittener main-Version nächster freier Wert), SHA256, reproduzierbarer ZIP-Inhalt, Tests/CI und dokumentierte **gesicherte Schutzdateien**, Originalicon und Themeassets unverändert.
- **Explicit Android-Abnahme erforderlich:** Vor Testergebnis alles `NOT_TESTED`, erfolgreiche Hosttests nie als Android-PASS ausgeben. HISTORISCH: `.33` **11 PASS / 3 FAIL / 1 NOT_TESTED**; `.34` Such-/Player-Routing PASS bei extremer Latenz und G4 vollständigem PASS; keine retroaktiven Änderungen.
- **KEIN eigenmächtiger Merge, Release, OTA-Publishing, Settings-Reset, Kodi-Reinstallation oder Downgrade.** Nach Nutzerprüfung und ausdrücklichem Merge-Auftrag regulär über das bestehende GS-Media-Repository aktualisieren.

**Definition of Done:** bestehende hoch bewertete Suchmaske sieht gleich aus und reagiert gleich, Live-Namen/EPG-Titel werden schnell und korrekt angezeigt, Infoleisten-EPG öffnet großen Guide und Links weiterhin kleinen, Startgruppe/Senderfokus soweit risikolos mit eigener Abnahme, Autoplay und Film-/Serienbereiche bleiben stabil. **Andernfalls Draft und klare OFFEN-Markierungen, kein stiller Release.**
