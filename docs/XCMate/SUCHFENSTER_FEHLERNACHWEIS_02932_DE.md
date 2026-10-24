# XCMate 0.1.29.32 – Fehlernachweis und Suchfenster-Vertrag

Stand: 24.10.2026. Basis main `59085e94f78d0bc9d66e3f6561a6fecf100abdf5`, Add-on .31. Vollständige verbindliche Übergabe `CODEX_UEBERGABE_LOGFORENSIK_SUCHFENSTER_20261024_DE.md`, #140/#143 und tatsächliche .31-Abnahme gelesen. Auftrag ausschließlich Suchfenster; Live-OSD/Cover/Wizard und Downloads/Recorder bleiben getrennt.

## Nachweis am Ausgangscode

1. Der große horizontale Guide setzt bei Suchbutton 314 `_next_route=global_search`, schließt **im nativen Callback**, und `open_grid()` führt unmittelbar nach `open_owned_window()` `Container.Update(global_search)` aus. Zu diesem Zeitpunkt ist die äußere `window_navigation.open_route()`-Lease **noch gehalten**. Der ältere zweispaltige Guide schließt bei Aktion 117 und startet den gleichen Containerwechsel sogar direkt im Callback.
2. `app_routes.dispatch` schickt ausschließlich **negative** global_search-Handles an die native Suche; positive Handles gehen in `app_routes.search`, die alte Kodi-Verzeichnisdarstellung. Damit ist die unterschiedliche Suchoberfläche deterministisch im Code belegt. `search_section` ist der weiter kompatible Directory-/Widget-Pfad.
3. Root-`SearchWindow` erbt zuvor die Film-Landing-Initialisierung: `_initial`-Job, Watcher und Control 120 können vor dem eigentlichen Suchstartup aktiv werden. Native Root-Suche braucht keine Filmstartseite als Zwischenansicht.
4. Vor jeder Runtime-Reparatur vier neue Tests gegen unveränderten Ausgangscode ausgeführt: **4 FAIL / 0 ERROR**. Sie prüfen positive-Handle-Dispatch, Callback-Schluss im alten Guide, Callback-Schluss im großen Guide sowie Landing statt unmittelbarem Suchmodus. Danach sind dieselben vier Verhaltensprüfungen grün; weitere Tests sichern den vollständigen Ablauf. Beleg: `FEHLERNACHWEIS_02932.json`, vollständige neue Tests `tests/test_xcmate_search_navigation_02932.py`.

Das belegt die falschen Codepfade und Callback-Reihenfolge im Hostmodell. **Die genaue native Android-Race-Reihenfolge ist noch nicht vollständig bewiesen**: .31-Rohlogs enthalten keinen Handle und keine vollständige Kausalspur. Öffentliche Dokumentation übernimmt nur die anonymisierten Befunde des Masterdokuments, keine privaten Rohlogs. Android-PASS wird nicht aus Host-Tests abgeleitet.

## Neuer Ablauf

| Einstieg | Native Suchübergabe | Rückkehr |
| --- | --- | --- |
| Großer / alter Guide | Keyboard hält Guide; akzeptierte Query erzeugt nur In-Memory-Intent und UI-Snapshot. Pending Apply wird invalidiert. Callback kehrt zurück → vorhandener Owner-Pump schließt nach 150 ms → `run()` beendet → native Fenster-ID/modaler Status wird bis maximal 2 s auf Freigabe geprüft → bestehendes `open_search()` auf demselben Owner-Thread, unter derselben äußeren Navigation-Lease. **Kein Such-Containerwechsel, kein weiterer Home-Anker.** | Search-Back schließt über eigenen Pump. Nach nativer Freigabe frische Guide-Instanz mit Gruppe, Zeit/Tag, Seite/Zeile und Fokus aus UI-Snapshot. Keine Control-Abfragen an bereits geschlossenem Guide. |
| global_search Action-Handle | Vorhandener Home-Kontext bleibt; fremder Kontext bekommt höchstens einen kontrollierten bisherigen Home-Anker. Native Root-Suche direkt. | Vorbereiteter XCMate-Home-Unterbau. |
| global_search Directory-Handle | Aktuellen Directory-Auftrag **einmal** mit unverändertem vollständigem `home_menu.show()` erfüllen. Auf aktiven global_search-Container und `Container.IsUpdating=false` warten, Abort/5-s-Timeout beachten. Kein zweites gleichzeitiges Home-Update. Danach native Root-Suche. | Vollständiger Home-Unterbau statt leerer Ergebnismappe. |
| Film-/Seriendetail | Vorhandener SearchMixin innerhalb desselben nativen Medienfensters; kein neuer Window-/Directory-Owner. | Gespeicherter Detail-/Medienkontext. |
| search_section Widget/Legacy | Bestehende reine Verzeichnis-Suchroute. | Keine automatische Ersetzung eines Widgets durch SearchWindow. |

Native Root-Suche öffnet direkt `mode=search` und Live-Tab. Kein Landing-Job und kein Katalog-Watcher als konkurrierender Frame. Der vorhandene Suchworker bleibt inkrementell, ausschließlich lokal; Daten-/Mapping-/Cachemodule sind unverändert. Root-Suche nutzt weiterhin die vorhandenen Film-/Seriendetails bei expliziter Auswahl.

Ein Live-Treffer wird ausschließlich nach bewusster Auswahl als vorhandener `guide_playback`-Intent zurückgegeben. Der bestehende Caller spielt **erst nach Freigabe der äußeren Navigation-Lease**. Kein direkter Playeraufruf in der Such-/Guide-Klickfunktion. Vorhandene Session-/Portal-/Fremdplayerprüfungen bleiben unverändert.

## Fokus, Worker und Diagnose

- Bisherige `_valid_focus`-Prüfung des Medienfensters bleibt maßgeblich. Native Search-Visibility-Lags werden auf dem Owner-Pump höchstens zwei Sekunden nachgeprüft; kein Worker-GUI-Zugriff, keine Endlosschleife. Danach `FOCUS_TIMEOUT`, keine erzwungene Fokusierung unsichtbarer Controls.
- Der Grid-Guide prüft sichtbar/enabled vor nativer Fokussetzung (einschließlich 312). Pending Fokus wird im vorhandenen Pump nachgeholt und begrenzt. Der alte 120-Befund wird durch Wegfall der Root-Landing-Initialisierung und vorhandene Medien-Fokusprüfung adressiert, nicht durch globales Umschreiben der Kodi-Navigation.
- Bestehende Future-Generation bleibt. Zusätzlich akzeptiert Apply nur dieselbe zufällige Suchsession, Rubrik und Seite, solange das Fenster aktiv ist. Neue Suchphrase/Tab/Seite/Back/Close kann alte Ergebnisse nicht übernehmen.
- `SEARCH_NAV`: feste Phasen, Quelle guide/grid/route/media, Handle-Klasse, monotone Zeit, zufällige 32-Hex-Suchsession, Window-/Dialog-ID, Fokus-ID und Owner-Lease-Kontext. Im Guide wird dieselbe Suchsession bis in SearchWindow/SEARCH_EPG übernommen; bei neuen Suchphrasen neue Session. Keine Query, Portal-/Sender-ID, URL, Datei-/SMB-Pfade oder Exceptions mit privaten Inhalten.
- Native Close wird gesondert verifiziert (`WAIT_RELEASE → RELEASE_READY`, andernfalls `RELEASE_TIMEOUT`). Owner-Pump und Cross-Interpreter-Lock werden nicht ersetzt. Ein schon aktiver fremder Owner wird weiterhin nicht übergangen.

## Matching und Grenzen

Der Fehlerpfad wird vor jeder Matchingbewertung repariert. Bestehende Tests prüfen aktuelle Sendungstitel, manuelles Mapping, Aliase, gültigen Short-Now-Fallback, Mehrfachtreffer, fehlende Quellen und Abschluss nach dem früheren Zwei-Sekunden-Limit. **Kein Matching-/Schemafix auf Verdacht.** `programme_hits` ist ein separater anonymer Zähler; elf Sendernamen-Treffer sind kein Programmtitel-PASS. Die reale Abdeckung muss NAVSEARCH-01/08 auf dem Gerät beweisen.

Die Directory-Barriere und native Close-/Focus-Abfolge sind gezielt für Android/Kodi 21.2 zu prüfen; Hostmodelle bilden native Skin-Latenzen nicht vollständig ab. Bei einer fremden, nicht dargestellten global_search-Verzeichnisabfrage läuft die Barriere kontrolliert aus, statt eine unsichtbare Hintergrundabfrage zur GUI-Aktivierung zu missbrauchen; alte Widgetlisten sollen `search_section` verwenden. Kein Android-PASS vor Nutzerprüfung.

Playerstatus-Ausnahme und Update-Service-Stop aus der Übergabe bleiben **separate offene Auditbefunde**, nicht die bewiesene Suchursache. Dienst/Portal-/Artwork-/Download-/Recorder-Lifecycle wird hier nicht geändert. Deshalb kein neuer pauschaler Vierstundentest.
