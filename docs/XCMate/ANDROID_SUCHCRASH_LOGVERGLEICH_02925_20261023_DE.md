# XCMate 0.1.29.25 – Android-Suchabsturz: bereinigter Logvergleich
Stand: 23.10.2026. Bezug: Issue #118 (P0), Issue #25 (globale Suche), Abnahme M04 FAIL. Nur Lightweight; Space Premium und Grafiktests ausdrücklich ausgeschlossen.

## Quellen (privat; nicht ins öffentliche GitHub stellen)
- kodi.old(3).log: 2727 Zeilen, 287384 Bytes; Aufzeichnung 15:43:24 bis 16:08:06.
- kodi(7).log: 1046 Zeilen, 125089 Bytes; Aufzeichnung 16:09:25 bis 16:15:21.
Die Originale verbleiben privat, weil sie Informationen über Provider, Geräte und lokale Netzwerkumgebung enthalten können.

## Zeitachse, nach Logzeilen überprüft
- 16:07:15–16:07:17, alt L2623–2643: movies_home, NAV ENTRY/OPEN, Movies-Fenster SHOW_DONE/INIT_DONE.
- 16:07:56, alt L2677–2684: CLOSED_INPUT, CLOSE_BEGIN/CLOSE_DONE, NAV RETURN; Python-Invoker wartet auf einen Thread.
- 16:07:57, alt L2685–2688: zwei nahezu zeitgleiche XCMate-Plugin-Aufrufe auf verschiedenen Threads.
- 16:07:59, alt L2693: ROUTE action=xcmate_home.
- 16:07:59, alt L2706: ROUTE action=global_search.
- 16:08:03, alt L2713–2716: Home DIRECTORY_DONE / DISPATCH_DONE.
- 16:08:06, alt L2726–2727: Suche DIRECTORY_DONE / DISPATCH_DONE, Dauer 7182.7 ms.
- 16:09:25, neu L1–8: Kodi startet erneut. Neu L95: XCMate 0.1.29.25 installiert.

## Abgrenzung von Befund und Hypothese
Der Nutzer beobachtete: Suchfeld öffnet; Begriff "Upload" eingeben und OK drücken; XCMate zeigt kurz die Plugin-Startseite; anschließend komplette Kodi-Beendigung. Die Logs enthalten den Suchtext nicht.
Nachgewiesen ist die zeitliche Überlappung von Home und global_search sowie der spätere Kodi-Neustart. Beide Plugin-Routen melden formal einen normalen Dispatch-Abschluss. In diesen Dateien fehlt ein nativer Crash-Stack, Fatal-Signal, Python-Traceback oder eindeutiger regulärer Shutdown-Marker. Eine genaue Ursache kann hieraus nicht bestimmt werden.
Zu untersuchen sind insbesondere WindowXML-Besitzerwechsel, Container-Navigation, gleichzeitiger Home-/Such-Dispatch sowie Aktionen nach dem Dispatch und Thread-Cleanup. Ein konkretes Container-Race oder Thread-Leak ist derzeit nur eine Hypothese.

## Quellcode-Korrelation in main .25
- media_window.py::_search(): Eingabe via Kodi Dialog, danach _next_route für global_search und WindowXML close.
- media_window.py::open_media(): nach Rückkehr Container.Update mit der Suchroute.
- app_routes.py::search(): verwendet den lokalen Index und erstellt Kodi-Verzeichnisrubriken für live/vod/series; noch kein eigenständiges Suchergebnis-WindowXML.
- Legacy main.py::_search_results ist ein separater Suchpfad; nicht ungeprüft vermischen.

## Codex-Abnahme- und Reparaturauftrag
1. P0 #118 zuerst beheben, getrennte Entwicklung und Tests, kein ungetesteter Merge nach main.
2. Suche nach Dialog-OK mit nur einem gültigen Besitzer-/Container-Übergang und einer verlässlich sichtbaren Ergebnisansicht; auch Post-Dispatch-Phase untersuchen.
3. Sanitisiertes Trace mit anonymen IDs und Ereignissen SEARCH_INPUT_ACCEPTED, SEARCH_WINDOW_CLOSED, SEARCH_ROUTE_BEGIN, SEARCH_DIRECTORY_DONE, SEARCH_GUI_READY, SEARCH_RETURN; keine Suchtexte oder Zugangsdaten protokollieren.
4. Tests: "Upload", Nulltreffer, Abbruch, Back, mehrmalige schnelle OK-Bestätigung, langsamer/fehlender Index, SQLite-Verzögerung, Kodi-Neustart, Android Kodi 21.2 ARM32. Keine regressiven Änderungen an den 23 Lightweight-PASS.
5. Danach #25: fernbedienbare Ergebnisübersicht mit LIVE-TV, FILME, SERIEN, echten Trefferzahlen und korrekten Play-/Detailaktionen. Bei LIVE-TV auch passende aktuell laufende EPG-Programmtitel suchen, nicht nur Sendernamen.
6. Bei weiterem Prozessabsturz private Android-Crashdaten (logcat/tombstone) untersuchen; keine Rohdaten öffentlich veröffentlichen.

Ergebnis: M04 bleibt FAIL und #118 OPEN bis echte Android-Geräteabnahme. Space Premium nicht berühren. Die separaten Posterfehler A02/A03 bleiben FAIL; kein aus diesen Suchlogs gesicherter Zusammenhang.
