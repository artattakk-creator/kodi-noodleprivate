# XCMate – Android .34: Live-Suchperformance und Infobar-EPG-Routing

**Stand:** 25.10.2026. **Verbindliche Beobachtungen des Nutzers**, Kodi 21.2 Omega / Android TV 13 / RK3528 ARM32 / Titan BINGIE MOD.  
**Aktueller geprüfter main-Stand:** `plugin.video.xtreammate` **0.1.29.34**. Für den folgenden Codex-Fix zunächst neueste main-Basis/Versionsfreiheit verifizieren.  
**Referenzen:** [UI-FREEZE](SUCHMASKE_UI_FREEZE_02934_20261025_DE.md), [Android-G1–G4](ANDROID_ABNAHME_02934_DE.md), Issues [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140), [#17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88), [#127](https://github.com/artattakk-creator/kodi-noodleprivate/issues/127), [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143), [#85](https://github.com/artattakk-creator/kodi-noodleprivate/issues/85).

## 1. Echtgerätetest .34 – neuester Sachstand, differenziert

**EPG → Wiedergabe** funktioniert nach mehrfacher Nutzung laut Nutzer **zuverlässig**. Ebenso funktionieren die **EPG-Suche, gefundener Sender, Start aus Treffer und Back aus der Suche zum EPG**. Das Hauptproblem ist **nicht** mehr der .33-BusyDialog-Abbruch. Diesen funktionierenden Handoff aus PR #158 unbedingt schützen; bereits gemeldete historische .33-FAIL-Werte nicht rückwirkend überschreiben. Exakte Anzahl der wiederholten Starts wurde diesmal nicht protokolliert.

**Massiver P1/P0-UX-Performance-Fail in Live-TV:**
- Sendernamensuche zunächst „gefühlt fast eine Minute“, jetzt beim erneuten **Anklicken der Rubrik Live-TV-Sender** nach gefühltem Start der eigentlichen Suche erst nach **ca. 3–5 Minuten** Ergebnisse. Die Vermutung, der Scan starte überhaupt erst beim Tabwechsel, ist **Nutzerhypothese**, keine nachgewiesene Mechanik.
- Suche nach einer **laufenden Sendung** zeigt tatsächlich einen Treffer, aber zuvor „gefühlt fast zwei Minuten“ bis zur Reaktion. **Titelmatching Teil-PASS, Latenz FAIL**.
- Film- und Seriensuche dagegen **relativ schnell**. Cover, Film-/Seriendetails, Staffeln/Episoden, Zurück zur Suche **PASS**.
- Serien-Autoplay **vollständig PASS** nach **nächtlichem Dauerlauf mit geschätzt 7–8 Folgen, einschließlich Staffelwechsel**. Dies ist echter Geräte-Nachweis, aber keine Zusicherung für alle Serien/Provider.
- **UI-FREEZE:** Nutzer sagt über die **drei dauerhaft sichtbaren Bereiche Live-TV | Filme | Serien**: „Diese Suchmaske finde ich super. Da darf nichts mehr dran geändert werden.“ Suchlayout, Tab-/Fokus-/Cover-/Logo-Position, Design und Rücksprung **nicht ändern**.
- Der große EPG öffnet laut vorausgehendem Android-Test beim Erstaufruf fälschlich mit „Alle aktivierten Sender“ statt konfigurierter Startgruppe (#88); Mini-EPG/Sidebar soll den **tatsächlichen aktuellen Sender bzw. Startsender** fokussieren (#17). Als **getrennte Navigationskorrekturen** beibehalten; nicht durch Performancefix regressieren.
- G1 funktionaler Start aus EPG vom Nutzer als **zuverlässig** gemeldet. G2 Navigation/Playback/Back **funktional PASS**, Performance FAIL. G3 echter Jetzt-Programmtitel gefunden **Teil-PASS**, Leistung FAIL, Treffer-OK und G3-Back im konkreten Lauf nicht eigens nachgewiesen. **G4 vollständig PASS**. Dies ersetzt nicht die komplette ursprüngliche Testmatrix und ist **keine Gesamtfreigabe**.

**Zu Messdaten:** 60 s / 120 s / 180–300 s sind **subjektive Geräteschätzungen**, keine mit Stoppuhr erfassten Kennzahlen. Noch keine `.34`-Logs zu diesem neuen 3–5-min-Lauf. Nicht aus Voreinstellungen oder Code auf endgültige Root Cause schließen.

## 2. Verbindliche neue Fernbedienungs-/Infobar-Regel – GROßER statt Mini-EPG

**Nutzeranforderung:** „Aus der Infoleiste heraus ... da steht ja auch EPG. Ich möchte, dass dieser Button auf das große EPG routet, nicht auf das kleine. Das kleine können wir über links ... aufrufen.“

| Benutzeraktion | Ziel | Verbindlicher UX-Vertrag |
| --- | --- | --- |
| Bei laufendem XCMate-Live-TV **OK** | Erste kompakte Infoleiste | Senderlogo, Jetzt/Danach, Fortschritt unverändert |
| Dort **OK erneut / Runter**, **Weitere/Einstellungen**, Menüpunkt **EPG** | **GROßER horizontaler EPG / `action=guide_grid`** | Öffnet den bestehenden nativen großen XCMate-Guide, **nicht** `LiveNavigator.mode='guide'` |
| Im Live-Vollbild bzw. der ersten Info-Ebene **Links** | **Mini-EPG = linke Senderliste** | Aktuellen Sender fokussieren, Now/Next aus lokalem Cache; Links nochmals → Sendergruppen; normale Back-Hierarchie erhalten |
| Rückkehr aus großem EPG per **Back** ohne Senderwahl | Fortlaufende bestehende Live-Wiedergabe / Info-/Video-Kontext | **Kein** Kodi-Home-Sprung, **kein** ungewollter Stopp, **kein** zweiter Playbackstart |
| Sender im großen EPG **„Jetzt Sender ansehen“** | Genau **eine** gültige Stream-Umschaltung | Vorhandenen Guide-Handoff benutzen; keine doppelten Player oder verloren gegangene Remote-Bindings |

**Codebezug main/.34, tatsächlich geprüft:**
- `src/plugin.video.xtreammate/resources/lib/live_overlay.py::LiveNavigator._execute(section='extras',index=3)` ruft `self._epg()`. **`_epg()` setzt `_guide_sid` und `self._switch('guide')`**, also **internen Mini-Programm-Dialog**. Auch `_handle_command('epg'/'guide')` und `long_menu` verweisen derzeit auf `_epg()`. **Änderung der sichtbaren EPG-Schaltfläche**, andere ggf. konfigurierbare Remote-Aktionen nur mit geklärter Semantik verändern.
- `app_routes.py` führt **`action='guide_grid'`** bereits auf `guide_grid_window.open_grid` und `window_navigation.open_route` zurück; mit `window_lifecycle` hat .34 eine sichere native Dialog-/Owner-Kette. **Nicht einfach `RunPlugin` oder `ActivateWindow` aus `WindowDialog.onControl` direkt feuern**, da frühere Versionen wegen Kodi-Window-/Busy-/Root-Konkurrenz scheiterten.
- `src/plugin.video.xtreammate/service.py::IPTVMasterService.run` verwaltet den **service-owned `LiveNavigator`**, die XCMate-LiveSession und das Playback; nach Schließen könnte der Service das Overlay neu aufbauen. Die neue Guide-Öffnung muss durch **einen One-shot-Intent / Service-Owner** mit klarer Session-/Tokenprüfung, Overlay-Freigabe und atomarem Rückkehrkontext erfolgen. **Die konkrete sichere Implementierung hat Codex mit Kodi-21.2-Lifecycle-/Android-Tests zu begründen**, nicht auf Zuruf eine unsichere Builtin-Folge verwenden.
- **Live-Stream im Hintergrund weiterlaufen lassen** beim großen EPG, soweit technisch auf Kodi 21.2 möglich; keine neue PlayMedia-Operation beim Guide-Öffnen. Native Fenster-/Overlay-Reihenfolge, Dialog-Sichtbarkeit und FocusOwner überwachen. Wenn Systemdialog oder anderes Playback übernommen hat: kontrolliert ablehnen/Benutzer informieren statt fremdes Fenster schließen.
- Für neu geöffneten **großen EPG** **Startgruppe** (#88) bzw. absichtlich aktivierte Gruppe nicht durch `None`/`'*'` global ersetzen; **Mini-Senderliste** fokussiert beim laufenden TV die aktuelle SID (#17), bei Erststart konfigurierten Startsender. Beide Routings logisch getrennt.

**Neue Android-Routing-Gates (alle bis Realgerät-Test NOT_TESTED):**
- **ROUTE-01:** Live-Vollbild → OK → zweites OK/Runter → Weitere → EPG öffnet tatsächlich **großes horizontales Raster** (nicht Mini-Programmzeilen).
- **ROUTE-02:** Live spielt weiter, Guide Back ohne Umschalten → korrektes Video/Info-/Bedienkontext; kein Home, Crash, Busy10138, paralleler Dialog/Neustart des Senders.
- **ROUTE-03:** In großem EPG anderer Sender per „Jetzt Sender ansehen“ starten → **genau ein** Wechsel, Fernbedienung/Infobar erneut nutzbar.
- **ROUTE-04:** **Links aus Vollbild/Info** zeigt schnelle Mini-Senderliste, **Links erneut** Gruppenliste, aktueller Sender fokussiert. Kein ungefragtes großes EPG durch Links.
- **ROUTE-05:** Guide→Suche→Back und wiederholtes EPG-Öffnen mindestens mehrfach, auch während laufendem Video; keinerlei .33 Root-/Busy-/Owner-Regression.

## 3. Suchperformance – Instrumentierung und minimaler Fix hinter UNVERÄNDERTER Oberfläche

**Bestätigter statischer Code, keine bewiesene Runtime-Ursache:**
- `search_data.LiveSearch.__init__`: liest bis **50.000** Live-Katalogeinträge, XMLTV-Aliase und aktive Jetzt-Events; `step(budget=.2)` maximal **64 Sender** pro Slice und `cached_short_guide` bei fehlenden gültigen XMLTV-Events.
- `media_search._search_load()` ruft `search(... incremental=True)`; bei `_continuation` wird die nächste Slice wieder angefordert. Diese Dispatches laufen auch bei Tab-Navigation durch vorhandene Suchmaskensteuerung; es **könnte** redundant erneut gesucht werden. Film-/Serienabschnitte werden parallel ausgewertet.
- Die **hypothetische** verspätete Suche erst nach Klick auf Live-TV ist zu prüfen über **Zeitpunkte von Query-Bestätigung, Klick auf Live-TV-Tab, Erzeugen des LiveSearch-Cursors, Start DB-Lookup, erstem Namensmatch, erstem Programm-Match, erstem sichtbaren Treffer und finalem EPG-Scan**. Evtl. Katalog-/EPG-Missing-Cache, Worker-Queue, SQLite-Full-Scans und asynchrone Update-Wellen differenzieren.
- Kein `http_get` oder EPG-Import im UI-Click/IR-Pfad. Kein Einsatz der vollen 64er-Katalogscans, wenn eine **lokal indexierte Sendernamensuche** sofort bedienbare Treffer liefern könnte. Für Programmtitel die vorhandene lokale Now-EPG-Indexstruktur und quellen-/portalspezifische IDs nutzen; keine falschen Mappings oder „Jetzt“-Programmdaten erfinden. Ergebnisse **inkrementell** in den **vorhandenen** Suchergebniszeilen ergänzen (keine Layoutänderung).
- Abbruch alter Suchgenerationen/Queries, keine mehrfachen alten Resultate nach Tabwechsel, keine Fokus-/Tab-/Scrollsprünge. Fehlende XMLTV-Daten melden, aber Namenstreffer nicht zurückhalten. Ergebnisse nach erneutem Klick auf Live-TV möglichst cachefähig.
- **Logs ausschließlich feste Phasen und monotone Dauern**, etwa `QUERY_ACCEPTED`, `TAB_LIVE_SELECTED`, `LIVE_CURSOR_STARTED`, `LIVE_INDEX_QUERY_DONE`, `FIRST_NAME_RESULT`, `FIRST_PROGRAMME_RESULT`, `FIRST_UI_RENDER`, `EPG_FINAL`, `CANCEL_STALE` plus anonyme Session. **Keine Suchbegriffe, Portal-/Senderkennungen, URLs, Tokens, Zugangsdaten oder Original-Kodi-Rohlogs auf GitHub**.

**Android-PERF-Gates:**
- **PERF-01:** Sendername über Guide→Suche, dann bewusst Live-TV-Tab; **Cold/Warm jeweils 3 Versuche**, Datum/Monotonic-Dauern bis erster anklickbarer Treffer und bis Scan-Ende getrennt. **Ziel: Sekunden statt 3–5 Minuten** auf RK3528; konkrete Grenze an reale Messung binden.
- **PERF-02:** im Guide sichtbaren echten laufenden Programmtitel suchen; echte Sendung samt richtigem Sender zuerst anzeigen, schneller als bisher ~2 min; Trefferbedienung und Back funktionieren.
- **PERF-03:** ohne eigenes Live-Tab-Reopen erneut gleiches Suchwort/Sender; Cache-/Progresszustand und keine Blockade. Fehlendes EPG bewirkt keinen leeren Sendernamen-Treffer.
- **REG-01:** Film-/Serien-Suche, Cover, Staffeln, Episoden, Back und **nachts bestätigtes staffelübergreifendes Autoplay** unverändert.
- **REG-02:** **suchmaskeninternes Layout 1:1** wie freigegeben: immer die drei Bereiche Live-TV | Filme | Serien, Logo-/Coverposition, Label, IR-Fokus, Details/Back. **Kein Redesign!**
- **REG-03:** EPG-Senderstart und EPG-Such-/Back-Handoff aus .34 weiter zuverlässig, keine neue `GUIDE_HANDOFF SKIPPED`-/`RELEASE_TIMEOUT`-Kette.

## 4. Umsetzung, Reihenfolge und Merge-Grenzen

1. Bestehenden aktuellen .34-Android-Zyklus als **Teil-/Pass-/Performance-Fail** dokumentieren. Historische `.33`-Abnahme **11 PASS / 3 FAIL / 1 NOT_TESTED** bleibt bestehen; erfolgreiche .34-Teilschritte nicht als Gesamtbeta-Freigabe werten.
2. **Codex** soll zuerst Performance-Profilergebnisse und sichere Infobar→großer EPG Owner-Konzeption vorlegen und **kleine kumulative PRs** planen. Vor Umsetzung neuer Scope-Konflikte mit aktuellem main prüfen. Eine klar getrennte Performance-PR und Routing-PR sind bevorzugt, sofern fachliche Abhängigkeiten nichts anderes erfordern.
3. **Code nur auf aktuellem main**, neue freie Version(en) prüfen, ZIP/SHA256, Schutz-/Hosttests, Android-Testanleitung und konkrete Root-Cause-Messungen liefern. Keine ZIP-Installation durch ChatGPT, kein autonomer Merge/Publish/Release, keine alten Drafts oder Datenrücksetzung.
4. **#88 Startgruppenöffnung und #17 Mini-EPG-Fokus** bleiben eigenständige UX-Abnahmepunkte; dürfen im Routingfix minimal angepasst werden, wenn isoliert getestet, aber **keine ungefragte globale Startgruppen-/Profilmutation**.
5. **#111 Poster-Retry/TMDb**, **#98 manuelle EPG-Zuweisung** und Downloads/Recorder sind andere Folgethemen, **nicht in diesen Performance-/Routing-Hotfix hineinziehen**.
