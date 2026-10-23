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

## Weitere abgeglichene Signale ohne gesicherte Absturzursache
- `GetDirectory - Error` tritt im alten Log 3-mal und im neuen 2-mal auf, jedoch nicht als direktes Endsignal des Such-Dispatch. Nicht automatisch der Suche zuordnen.
- XCMate-Artwork-DB `BUSY` ist im alten Log einmal vermerkt, im neuen keinmal. Kein nachweisbarer Zusammenhang zum Suchabsturz oder den separaten Poster-Timeouts (#111).
- Wiederholte Repository-Warnungen (BINGIE-Schema, fremde HTTP-Repositories) betreffen andere Add-ons. Keine Ursachenzuweisung an XCMate.
- Das neue Log enthält keine weitere `global_search`-Route: Es dokumentiert den Neustart und die anschließende Kodi-Nutzung.
- Der Eintrag `CPythonInvoker: waiting on thread` unmittelbar nach dem Medienfenster ist beobachtet, aber für sich kein Nachweis eines Thread-Leaks.
- Keine Nutzerdaten- oder Cache-Löschung für Tests erforderlich. Kein globaler Kodi-Keymap-Eingriff.

## Empfohlene zusätzliche Android-Abnahme nach Korrektur
- Texteingabe `Upload`, OK: Kodi bleibt offen; ein einzelner stabiler Ergebnis-Navigator erscheint.
- LIVE-TV / FILME / SERIEN mit getrennten Trefferzahlen und 0-Treffer-/Index-lädt-Zuständen; Live-TV-EPG-Jetzt-Titel-Matches dürfen nicht mit bloßen Sendernamen-Matches verwechselt werden.
- Leere Eingabe, Abbrechen, erneutes Öffnen, schnelle wiederholte OK-/Zurück-Aktionen, Wechsel in Filmdetails und zurück.
- Pause/Resume, Live-TV-Overlay, EPG-Guide, Favoriten, Original-Icon, Provider- und Persistenzdaten als bestehende Lightweight-Regressionen weiter PASS; keine Space-Premium-Abnahme.
- Erst ein echter Android-Gerätetest darf #118 von FAIL auf PASS setzen. Ein bestandener Unit-Test oder ein formaler `DISPATCH_DONE` genügt nicht.

## Referenzen
- [#118 – P0 Absturz nach Such-OK](https://github.com/artattakk-creator/kodi-noodleprivate/issues/118)
- [#25 – globale Suche über Live-TV/Filme/Serien](https://github.com/artattakk-creator/kodi-noodleprivate/issues/25)
- [Gesamtabnahme 0.1.29.25 Lightweight](ANDROID_ABNAHMEERGEBNISSE_LIGHTWEIGHT_02925_20261023_DE.md): 23 PASS / 3 FAIL / 1 NOT_TESTED
