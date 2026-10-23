# XCMate – Vollständige Codex-Übergabe nach Android-Abnahme 0.1.29.25
**Stand: 23.10.2026** · **Projekt:** GS Media XCMate · **Repository:** https://github.com/artattakk-creator/kodi-noodleprivate · **Add-on-ID:** `plugin.video.xtreammate`

## Verbindliche Testumgebung und Release-Disziplin
- Nutzergerät: Android TV 13, Rockchip RK3528/ARM32, Kodi 21.2 Omega, Titan BINGIE MOD 2.2.3, IR-Fernbedienung.
- Produktiver Teststand: **XCMate 0.1.29.25 Lightweight**. Space Premium weiterhin nicht auf Android abgenommen. Das normale Live-TV-Overlay und viele Lightweight-Funktionen sind bestätigt.
- Kein Merge oder Release ohne ausdrückliche Freigabe und anschließende reale Android-Abnahme. Zuerst eigene Draft-PRs, automatisierte Tests, Test-ZIP plus SHA256 und Installations-/Changelog-Bericht. Vorhandene Portal-/EPG-/Favoriten-/Resume-/Artwork-Daten und Original-XCMate-Icon unverändert schützen. Kein globaler Kodi-Keymap-Eingriff, kein Cache-/DB-Reset.

## Aktualisierte 27-Punkte-Abnahme
**22 PASS / 4 FAIL / 1 NOT_TESTED** (Neubewertung: E05 jetzt FAIL statt früher PASS).

**Neu nach mündlichem Realgerätetest:**
1. **Serien-Autoplay auch über Staffelgrenzen vollständig erfolgreich – PASS (#85).** Letzte Folge der einen Staffel → nächste Staffel funktioniert laut Nutzer sehr gut. Autoplay und manueller Stop sind eingefrorene Regressionen. **Keine unnötige Änderung an `media_autoplay.py`, `media_sequence.py`, `media_window.py`-Autoplay-Teilen, `media_progress.py`**, anderen Playback-/Resume-Modulen. Erneut testen nur, wenn ein PR diese Pfade berührt. Dieser Nachweis erweitert den bestehenden P02-PASS, nicht die Anzahl der 27 Einzeltests.
2. **Jetzt/Danach im EPG – PASS (E07).** Beide Angaben sind korrekt und sollen unverändert bleiben.
3. **EPG-Senderstart – FAIL, neue Regression (E05, P0 #121).** Auswahl „Jetzt ansehen“/Sender aus dem großen EPG liefert laut Nutzer eine Fehlermeldung. **Fehlertext noch nicht übermittelt**. Der Nutzer kündigt ein aktuelles Kodi-Log an, das **bei Erstellung dieses Auftrags noch nicht verfügbar ist**. Den älteren E05-PASS NICHT beibehalten. Kein Beleg eines Kodi-Absturzes bei diesem aktuellen Fehler.
4. **Kodi-Datei-/Ordner-Auswahl – weiterhin NOT_TESTED (M07).** Realer Pfad: **XCMate → Einstellungen → Speicher → Aufnahmeordner**, `home_menu.py::recording_folder()` öffnet `xbmcgui.Dialog().browseSingle(0, ...)`. Alternativ: **Einstellungen → Darstellung & Sprache → XCMate-Designs → ZIP-Datei installieren**, `theme_ui.py` `browseSingle(1, ...)`. Ein Code-Nachweis ist kein Android-PASS; zu prüfen sind D-Pad-Fokus, OK, Back und sichere Abbruchmöglichkeit ohne Schreibvorgang.
5. Unverändert FAIL: **P0 globale Suche/Kodi-Absturz M04 #118**, **Posterdiagnose und Einzelretry A02/A03 #111**.
6. Separater FAIL **Skin-Live-TV-Shortcut #120**: Startkanal-Favorit lässt sich speichern, Live-TV-Kachel dreht aber 40+ s ohne Senderstart. Box bleibt bedienbar. Nicht mit EPG-Startregression verwechseln.

## P0 1 – #118 Globale Suche / Kodi-Prozessabsturz
Nach Suchbegriff `Upload` und OK springt XCMate zur Startseite, Kodi beendet sich vollständig. Vollständiger bereinigter Logvergleich:
`docs/XCMate/ANDROID_SUCHCRASH_LOGVERGLEICH_02925_20261023_DE.md`.
Vorhandenes Log belegt fast gleichzeitige `xcmate_home` + `global_search`-Dispatches, beide formal beendet, aber **keine bewiesene native Crash-Ursache**. Fenster-/Container-Owner und Post-Dispatch untersuchen. Sichere Einmalnavigation zu drei Ergebnisbereichen LIVE-TV/FILME/SERIEN (#25), einschließlich EPG-Jetzt-Suche, erst nach sicherem Crash-Fix. Kein unsicherer simultaner `Container.Update`-Versuch. Keine Provider-URLs/Tokens loggen.

## P0 2 – #121 EPG „Jetzt ansehen“ startet keinen Sender
**Codepfad main 0.1.29.25:** `guide_grid_window.py::_actions` setzt `_play_request` und lässt das Kodi WindowXML über Owner-Pump schließen; `open_grid()` liefert Intent; `app_routes.py::dispatch(guide_grid)` nutzt `open_route(...,after_close=guide_playback.handoff)`; `guide_playback.py::_handoff` prüft innerhalb 2s (Fenster/Modalzustand), Playerstatus, Portal-ID, Reader-Kanal, LiveSession; startet anschließend `PlayMedia(plugin... action=play_live)`. `guide_window.py` besitzt einen alternativen, separaten `self.close();PlayMedia()`-Pfad.
**Vorläufiger Altlog-Hinweis (nicht aktueller Fehlernachweis):** In `kodi.old(3).log` vom 23.10., 15:51:52 `GUIDE_HANDOFF QUEUED`, 15:51:54 `SKIPPED`; 15:52:42–15:52:44 später `QUEUED → RESOLVER_REQUEST → DISPATCHED`. Ursachen noch unbewiesen; alte Rohlogs NICHT ins GitHub kopieren.
**An Codex:**
- Zuerst neues Fehlerlog samt Zeitfenster, wenn verfügbar, datensparsam und privat prüfen: ist `GUIDE_HANDOFF` `SKIPPED` oder `DISPATCHED`? Späterer Fehler im Kodi-Resolver oder eigentlichem Stream?
- Eindeutige anonyme Handoff-Korrelation + präzise **Reason-Codes** für Ablehnungen: WINDOW_WAIT_TIMEOUT, MODAL_BLOCK, PLAYER_CHANGED, PORTAL_DISABLED, CHANNEL_NOT_FOUND, SESSION_CHANGED, RESOLVER_START_FAILED; nie `sid`/`pid`/Stream-URLs/Credentials loggen.
- Validierte Übergabe **nach** sauberem WindowXML-/Lock-Freigabe und nur einmal; keine Kodi-GUI-Aktionen aus Worker-Threads; Prüfung von 2s Deadline gegen echten Android-Window-Wechsel, Eventualitäten mit geöffneter Kodi-Startseite oder aktivem fremdem Player.
- Benutzerseitig getrennte Fehlermeldungen: „Sender konnte nicht übergeben werden“ versus „Wiedergabe konnte nicht gestartet werden“, wo tatsächlich unterscheidbar.
- Gerätetests: EPG Sendungszelle „Jetzt ansehen“, reine Senderzeile, anderer Sender/Gruppe, EPG→Play→Stop→EPG, bestehendes Live-TV, fremde Filme/Add-ons, fehlender EPG-Eintrag, Doppelklick und langsamer Skin. Kein Regression bei EPG Jetzt/Danach, Raster, Gruppen/IR/Startsender.

## P1 3 – #122 EIN Standard-Splash-Hintergrund für Lightweight
Nutzer fordert explizit das **bereits vorhandene originale Space-Premium-Splash-Bild** als neuen durchgängigen **Lightweight**-Hintergrund, vor allem **XCMate-Hauptseite sowie erste Film- und Serienübersichtsseite**, idealerweise alle XCMate-Seiten/Settings, konsistent.
**Exakter Quellpfad im GitHub-Repo:** `themes/xcmate/space-premium/assets/branding/splash-1920.jpg` (GS-Media-Originalasset). Nicht `fanart-1920.jpg`, `bg-movies.jpg` oder eine neue Bildgenerierung verwenden.
- `home_menu.py::show` gibt auf Kodi-Menükacheln derzeit `asset('background.home.'+name, ...)` aus. Lightweight-Fallback als einheitlichen Splash festlegen, damit die Startseite beim Fokuswechsel konsistent aussieht.
- `resources/skins/Default/720p/XCMateMedia.xml` Control 100 nutzt `media_neutral.png`; `media_window.py::_queue_art` nutzt fehlende Fanart als Neutral-Fallback. Film-/Serien-**Landing/erste Seite** muss direkt und ohne Netzanforderung das originale Splash als ruhigen Grund zeigen. Bei Medien-Details dürfen korrekte, gecachte echte Motive sinnvoll integriert werden, ohne Grundstil zu zerstören.
- Splash in das installierbare **Lightweight-Core-Artefakt** aufnehmen (oder ebenso zuverlässige lokale Paketquelle). Das Premium-ZIP ist optional und ab anderem Versionsbereich vorgesehen; nicht darauf verlassen, dass es auf .25 heruntergeladen/installiert ist.
- Vorhandene `theme_render.py`, `theme_store.py`, XML-Text-/Fokus-IDs sowie Licht-/Kontrast-Overlay verträglich anpassen. **Keine vollständige Space-Premium-Aktivierung, keine Änderung des bestehenden Premium-Fokus-Bugs #115.** Original-Icon #37 erhalten.
- Auch EPG-/Settings-Seiten konsistent behandeln, aber Priorität 1: Kodi-Hauptseite, Film-Landing, Serien-Landing.

## P1 4 – #123 EPG-Programmdetails wie Fernsehzeitschrift
Das aktuelle **`xbmcgui.Dialog().textviewer()`** in `guide_grid_window.py::_actions` und `guide_window.py` liefert Text/Plot statt einer hochwertigen Programm-Detailseite. Wunsch: **eigene visuell gestaltete, vollständig IR-fokussierbare Programmseite**.
- Sichtbare Hauptmetadaten: Senderlogo und -name, Programmtitel, Datum/Uhrzeit/Ende/Länge, Live-/Jetzt-Status, EPG-Quelle, Kurz- und Langbeschreibung; zusätzlich Genre, Format, Folge/Staffel, Jahr, Darsteller/Regie, Freigabe **nur wenn aus autoritativen Daten vorhanden**. Klare Aktionen „Jetzt ansehen“ und andere bereits funktionierende Menüpunkte; nicht unfertige Features als verfügbar markieren.
- Dynamisches Bild: vorhandenes lizenziertes Event-/Senderbild bevorzugen; bei echter eindeutig identifizierter Film-/Serien-Sendung ggf. überprüftes TMDB-Cover oder Backdrop. Vorsicht bei News/Sport/Talk/ähnlichen Titeln, Remakes/gleichnamigen Produktionen. Kein falsches Match; ohne Treffer gutes Default/Senderlogo. Bild + Herkunft lokal persistieren; nicht im Kodi-UI-Thread nachladen; begrenzte Timeouts, Retry/Cooldown, API-Key/Attribution/Lizenz prüfen. Keine ungeprüfte Annahme, dass Kodi-TMDB-Helper diese Daten bereitstellt.
- Eigene WindowXML-Seite bzw. gut fokussierbares Overlay, passend zu Splash als Basis, ausreichend große TV-Typografie, lesbare Struktur, Scroll und Fokus. `theme_render.py` hat bereits einen Schlüssel `background.epg.detail` für eine mögliche Programme-Ansicht, **aber eine fertige `XCMateProgramme.xml` existiert derzeit nicht**.
- Zurück bewahrt vorherige Sendergruppe, Zeitachse, Zelle und Selektion; die neue UI darf das P0-Handoff #121 nicht destabilisieren. Verknüpfung mit EPG-Rich-Details-Issue #88.

## P1 5 – weitere offene Aufgaben, nicht heimlich vergessen
- #120: Skin-Live-TV-Button/favorisierter „Startkanal“ muss ohne spinnernden Fehlaufruf starten; zuverlässig zurück zu XCMate-Home und EPG, Startlatenz kalt/warm messen. Andere Route als #121.
- #111: Provider-Posterdiagnose/Retry TIMEOUT; optional sauber lizenzierter TMDB-Fallback, ohne falsch zugeordnete Cover. Priorität nach P0-Regressionen.
- #98: manuelle EPG-Quellenzuordnung direkt im großen Guide mit Live-Preview bleibt P1, noch nicht Teil der .25-Abnahme.
- #62 Aufnahme/Timer, #63 Downloads, #113 Meine Medien und Space-Premium-Vollabnahme gehören NICHT ungeprüft in diese Hotfix-Korrektur.

## Codex-Arbeitsmodus / Deliverables
1. Offizielle Android-Abnahme lesen: `docs/XCMate/ANDROID_ABNAHMEERGEBNISSE_LIGHTWEIGHT_02925_20261023_DE.md`. Die letzte Benutzer-Rückmeldung hat Vorrang vor alten PASS.
2. Zuerst **P0 #121 EPG-Senderstart** und **P0 #118 Such-Kodi-Absturz** in kleinen, getrennt testbaren Änderungen. Reihenfolge abhängig von konkreter Loglage; keine neuen GUI-Designarbeiten in denselben Crash-Hotfix mischen.
3. Dann **P1 #122 Splash**, **P1 #123 Programm-Details**; #120 und #111 getrennt priorisieren. Nur Lightweight-Core; Original-Icon und funktionierender Autoplay **frozen**.
4. Zu jedem PR: reproduzierbare Ursachenanalyse (Fakt/Hypothese), begrenzter Diff, Regressionstests mit Kodi-21.2-WindowXML-Owner- und Android-ARM32-Aspekten, anonymisierte Debug-Ereignisse, Test-ZIP/SHA256, Testanleitung und Release-Notes.
5. Kein `main`-Merge/Release ohne Nutzerfreigabe und echten Android-Geräte-PASS. Kein kompletter DB-/Artwork-/EPG-Reset und keine Änderungen an aktiven Providerzugängen.

## Verknüpfte GitHub Issues
- **#85** Autoplay Staffelübergang PASS / schützen
- **#121** neuer P0-EPG-Senderstart FAIL
- **#118** P0 globale Suche/Kodi-Absturz
- **#122** Lightweight-Splash aus original Space-Premium-Asset
- **#123** Magazinartige EPG-Sendungsdetails (verknüpft mit #88)
- **#120** Skin-PVR-Live-TV-Shortcut FAIL
- **#111** Poster-Timeout/Retry-Fallback FAIL
- **#98** manuelle EPG-Zuordnung (separater offener Funktionswunsch)
