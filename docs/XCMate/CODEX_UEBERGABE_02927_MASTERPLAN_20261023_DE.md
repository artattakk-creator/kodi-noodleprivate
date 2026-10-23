# XCMate – Codex-Masterübergabe / nächste Entwicklung ab 0.1.29.27
**Datum:** 23.10.2026, nach neuer .26-Android-Abnahme und zwei Kodi-Gerätelogs
**Produkt:** GS Media XCMate · **Repository:** https://github.com/artattakk-creator/kodi-noodleprivate
**Add-on-ID:** `plugin.video.xtreammate` · **Repository:** `repository.gsmedia` 1.7.0
**Aktuell in main/Repository veröffentlichte Plugin-Version:** **0.1.29.26**
**Nächster vorgeschlagener Entwicklungsstand:** **0.1.29.27** (noch **kein** .27-Implementierungs-PR, keine neue ZIP, keine Android-Abnahme). Falls Codex Versionskonflikte findet, zuerst GitHub-Stand prüfen und die nächste freie Buildnummer nachvollziehbar verwenden.

## 0. Unveränderliche Fakten / Basis
- Android-Testbox: Rockchip RK3528, Android TV 13, Kodi **21.2 Omega** ARM32, Titan BINGIE MOD 2.2.3, IR-Fernbedienung; Kodi 21.3/22 noch **nicht** durch XCMate-Gerätetests freigegeben.
- Dokumentierter vollständiger .26-Nutzertest: **15 PASS / 6 FAIL / 0 NOT_TESTED** (21 Abnahmefelder). Quelle: `docs/XCMate/ANDROID_ABNAHME_02926_20261023_NUTZERERGEBNISSE_DE.md`.
- **PASS .26:** S01–S05, S07, R01–R02 (nur Aufnahme-Dialog und Jobanlage), B01–B07. S04 Film-/Serientreffer öffnen; S05 EPG-Jetzt-Suche; B03 direktes Live-TV/IR; B04 großer EPG + Jetzt/Danach; **B05 EPG→Senderstart PASS**; **B06 serien- und staffelübergreifendes Autoplay PASS**, unbedingt **nicht ändern**; B07 Poster/Einzelretry **im getesteten Umfang** PASS; Bestandsdaten/Icon intakt.
- **FAIL .26:** **S06 Suchtreffer→Live-TV** (#125); **R03–R06 Sofortaufnahme End-to-End** (#126); **B08 Skin-Live-TV-Kachel** (#120). Der Nutzer meldet beim Recorder `FAILED / 0 MB / UNSUPPORTED_TARGET`. R04/R05/R06 werden als vom Nutzer gemeldete FAIL **beibehalten**; ohne geschriebenen Stream sind keine separaten Defektursachen bewiesen.
- Neueres mündliches Nutzersignal „direkt starten hat schon funktioniert“ bezieht sich auf bisher funktionierende Suchtrefferaktionen, darf den **konkret dokumentierten S06-FAIL** und den **fatalen Kodi-Logeintrag** nicht ohne *neuen spezifizierten S06-Geräte-PASS* überschreiben.
- Gegenstand nur XCMate-Code und Projektassets, **kein** globaler Kodi-Keymap-/Skin-/Addon-Hack.
- Vorhandener **PR #124** ist **nur Dokumentation** und enthält eine ältere Hypothese/Planung, **keine lauffähige .27-Version**. Alte Aussagen zu EPG E05-FAIL und noch unbestätigter .26-Suche mit dieser **neueren** Abnahme reconciliieren, nicht ungeprüft übernehmen. **PR #117** ist ein isolierter experimenteller Direct-TS-Draft; nicht pauschal mergen, testen oder mit produktiver Recorder-Freigabe verwechseln.

### Sensible Diagnosequellen (nur bereinigten Inhalt verwenden)
- `docs/XCMate/ANDROID_LOGVERGLEICH_02926_20261023_NACH_ABNAHME_DE.md`
- `docs/XCMate/ANDROID_ABNAHME_02926_20261023_NUTZERERGEBNISSE_DE.md`
Privatlogdateien `kodi.old(4).log`, `kodi(8).log` **nicht** in GitHub hochladen, da Stream-URLs, Parameter und Benutzerinformationen enthalten sein können.

## A – P0 Hotfix: #125 Live-TV aus globalen Suchergebnissen stürzt Kodi ab
**Belegt durch .26-Log (nach Installation 18:42):**
- 18:53:30.288 `SEARCH_RESULT_READY`
- 18:53:32.219 `GUIDE_HANDOFF QUEUED`
- 18:53:32.561 `SEARCH_WINDOW_CLOSED`, ~18:53:32.613 `WINDOW/MOVIES CLOSE_DONE`
- 18:53:32.694–.695 `GUIDE_HANDOFF RESOLVER_REQUEST` → `DISPATCHED`
- **18:53:33.097 Kodi CRITICAL:** `Logic error due to two concurrent busydialogs, this is a known issue. The application will exit.`
- neue Kodi-Session ab 18:54:05. **Kritischer gleichzeitiger Kodi-Busy-Dialog-Zustand ist bewiesen, Auslöser des zweiten Dialogs noch nicht.**
**Zu prüfen:** `media_search.py::_search_click()/handoff()`, `guide_playback.py::_handoff()`, `window_navigation.py::open_route()`, `media_window.py`, `app_routes.py`, `live_exit.py`, Plugin-Invocations/`PlayMedia()` vs. Directory-/Root-Aufruf.
**Ziel:** Einmaliges, owner-sicheres Search-Window→Live-Player-Handoff; weder konkurrierender Root-`GetDirectory` noch zwei Busy-Dialoge; ohne Sleeps als Pseudofix; kein GUI aus Worker-Thread. Korrelierte, datensparsame Schritte vor/nach Window-Close und Resolver sowie eindeutige Reason-Codes; keine SID/PID/Stream-URL/Credentials im Log.
**Abnahme:** Suche `Upload` und EPG-Titel mehrfach, LIVE-Treffer startet echten Sender mit Bild/Ton, Info-/Gruppen-/IR-Overlay und Zurück stabil, kein Kodi-Absturz; Film-/Serientreffer und EPG→Live bleiben PASS. Andere Player-Sitzungen nicht übernehmen.

## B – P0 Hotfix: #126 Sofortaufnahme blockiert – `UNSUPPORTED_TARGET`
**Nutzer:** R01 Ordnerbrowser PASS, R02 „Auftrag starten“ PASS, R03 Status `FAILED / 0 MB / UNSUPPORTED_TARGET`, R04–R06 FAIL als nachgelagerte End-to-End-Prüfungen. Weder Aufnahmezieltyp noch errno aus aktuellen Logs bewiesen.
**Codebefund:** `home_menu.py::probe_directory` prüft Kodi-VFS-Lese-/Schreibfähigkeit, `capture_ui.py::_start` akzeptiert dann absoluten `translatePath`-Pfad, `capture_service.py::_run` resolvt Stream bereits vor Recorder-Zielprobe; `direct_ts.py::Recorder._probe_target` benötigt POSIX `os.open` mit O_DIRECTORY/O_NOFOLLOW, `os.link`/Hardlink, fsync/StatVFS. Hardlink-Fehler werden in `Failure('UNSUPPORTED_TARGET')` übersetzt. Android-Speicher `/storage/emulated/0` existiert, ist **nicht** als tatsächlich gewähltes Aufnahmeziel bewiesen.
**Ziel:** Vor *Anlegen/Zusage* des Auftrags und zwingend vor *zweiter Provider-Verbindung* genau die Recorder-Kompatibilität, verfügbaren Speicher/Reserve und Rechte prüfen, nicht nur Kodi-VFS. Geeigneten lokalen Standard-Ordner und verständliche Ordnerwahl anbieten; nicht kompatible Android-VFS/USB/SMB-Ziele sicher ablehnen oder gesondertes Backend mit korrektem Semantikmodell planen, **keine unsicheren Hardlink-Fallbacks**, keine silent permissions escalation. Unterschied „Auftrag vorgemerkt“ versus „Stream wird aufgezeichnet“ sichtbar machen. Anonyme Syscall-Kategorie/errno und Ziel-Fähigkeitscodes diagnostizieren, private Pfade/Streams nicht loggen.
**Abnahme:** R01–R06 nacheinander mit erlaubter zusätzlicher Anbieter-Verbindung und kompatiblem Speicher: Status `recording`, Bytes >0, manueller Stop/Finalisierung `complete`, aufzeichnungsbasierte Wiedergabe, kontrollierter Unterbrechungsfall `partial/failed` ohne Datenverlust. Nach frischer Kodi-Installation (#43) soll Aufnahmeziel vorab korrekt eingestuft werden.

## C – P1: #120 Titan-BINGIE-MOD-Kachel „Live TV“ direkt auf XCMate-Startkanal
- Skin-Menü/Favorit `Startkanal` kann gesetzt werden, aber **B08 weiterhin FAIL** (40+ Sekunden Spinner, kein TV); nicht mit S06 Search-Handoff oder B05 EPG-Handoff verwechseln.
- XCMate-spezifische, stabile Direkt-Entry-Route (z. B. `skin_live_start`) für den **aktuell konfigurierten** Startsender statt katalogbedingtem langsamem Root-Umweg. Kodi-Skin-Shortcut-Aktion/Form (`RunPlugin` vs. `PlayMedia`, Favoritenpfad) prüfen, Session/Owner, Modal/Busy-Kontext erhalten; keinen Startsender hardcoden.
- **Separater Zusatzbefund:** Im alten Log vor .26 findet sich wiederholt `script.skinshortcuts`-Traceback `Element.getiterator()` (nicht XCMate). Gegebenenfalls kompatibles SkinShortcuts-Update/Workaround dokumentieren, aber **keinen fremden Skin unaufgefordert im XCMate-Code patchen**.
- Im neuen Log nach Live-Ende: `LIVE_EXIT HOME_REQUESTED` ca. 19:11:08, anschließend trotz XCMate `DIRECTORY_DONE` Kodi `GetDirectory(xcmate_home)`-Fehler ca. 19:11:10. Navigation/Containerkontext zuverlässig machen.
- Akzeptanz: Skin-Live-TV-Kachel startet direkt live, Zurück beendet nur eigene Live-Session und öffnet XCMate-Home/EPG; IR OK/Links/Oben/Unten/Back behalten, kalt/warm Startzeiten messen.

## D – P1: #127 **Neue informative Suchergebnis-Ansicht**, unbedingt in kommende Baureihe
**Gerade neu vom Nutzer angefordert, eigenes vollständiges Issue #127, NACH P0 #125 oder darüber gestapelt.**
- `XCMateMedia.xml` aktuell Search-`<list id="710">` nur 60 px Textzeile; `media_search.py::_search_ready` ruft `_fill(710,rows)` und klebt Programmtitel an Text. **Kompakte mehrzeilige, optisch gestaltete Zeilen/Karten** mit kleinen Motiven und sinnvollem Fokus umsetzen, kein unübersichtlicher Großposter-Screen.
- **Live-TV:** Senderlogo links, Sendername; Jetzt-Titel, Sendezeiten, kurze EPG-Info, optional Danach/Fortschrittsbalken **nur wenn lokal bekannt**; neutraler Sender-Placeholder ohne EPG, keine Fake-Infos; OK muss abspielfähig sein (#125).
- **Film:** Mini-Cover links, Titel, Jahr, **Sprache**, **UHD/4K/HD/SD nur aus gesicherter Quality-Metadatenquelle**, gefundenes **Portal/Quellgruppe**, Genre/Kurzplot optional; sofort Film-Detail/Aktion im bewährten .26-Flow.
- **Serie:** Mini-Cover, Serienname, Sprache, Qualität, Portal/Gruppe, Anzahl Staffeln **nur belegt**, optional Genre/Plot; OK zu Staffel/Episoden-Auswahl; Autoplay nicht ändern.
- `search_data.py::search/live_matches`, `library_index.Reader.page`, `guide_store`, `media_art.local_art/request`, `media_window._fill/_refresh_art` als Datenquellen untersuchen; nicht blind Provider-/TMDB-Titelnamen als Matching vertrauen. Derzeit Suche nur innerhalb **aktiven Portals**: „Fundort“ nicht als cross-provider behaupten; Gruppenzuordnung nur falls echt vorhanden.
- Remote auf 720p-Kodi-Mock + 1080p Ausgabe, Scroll mit 20–100 Treffern, 48er-Pagination, Fokus- und Back-Wiederherstellung, Display-Mode, lange Namen, Sprach-/Qualitätsfeld ohne Daten, Offline-Fallback. **Keine** N+1-Netzabrufe je Treffer, keine UI-blockierenden TMDB-Requests; bestehende persistente Artwork-Queue/Caches mit throttled Refresh. Original-Icon behalten.
- Eigene Tests UX01–UX07 aus #127 und Android-S06-Hotfix als Go/No-Go-Gate.

## E – P1: #122 Einheitlicher Original-Splash-Hintergrund in **Lightweight**
- Genau das im Repo vorhandene, originale Space-Premium-Bild `themes/xcmate/space-premium/assets/branding/splash-1920.jpg` als Basisbackground für XCMate-Hauptseite, **erste FILME-Seite und erste SERIEN-Seite**, möglichst übrige XCMate-Settings/EPG und Suchansicht. Lokal in Lightweight-Installations-ZIP bündeln, **keine Theme-Abhängigkeit/Netz**. Lesbarkeit via dezentes Overlay.
- `home_menu.py`, `XCMateMedia.xml`, `media_window.py`, `theme_store.py`/`theme_render.py` prüfen; keine unsicheren Kodi-Global-Skin-Modifikationen.
- **Space Premium als Themesystem NICHT vollständig aktivieren**; #115 Fokus/OK-Problem im Premium ist noch FAIL. **Original-XCMate-Icon** im Lightweight und Premium unverändert.

## F – P1: #123 Magazinartig gestaltete **große EPG-Sendungsdetailansicht**
- `guide_grid_window.py::_actions()` zeigt heute u. a. `xbmcgui.Dialog().textviewer()`: durch eigene gut gestaltete TV-Programmzeitschrift-Detailseite ersetzen, optional `XCMateProgramme.xml`.
- Senderlogo, Sendezeit/Datum/Dauer/Status, kurzer + langer Plot, Genres/Staffel/Folge/Jahr, Darsteller/Regie, Bild/Fanart **nur soweit eindeutig verifiziert**, sonst Senderlogo/neutraler Fallback; Aktionen gut fokussierbar (Jetzt ansehen) ohne kaputten Handoff. Dynamic Artwork async/cache-first; TMDB-Matching nur bei eindeutigen Film-/Serien-Programmen, nicht automatisch News/Sport/Talk.
- Zurück zur **gleichen EPG-Senderzelle, Zeitachse und Gruppe**. B04/B05 PASS aus .26 unbedingt erhalten.

## G – P1: #98 EPG-Quellen **pro Sender direkt im großen EPG** zuordnen
- Im großen EPG auf Sender/Programmlinie **OK-Kontext oder lang OK** → „EPG zuweisen“: Quell- und EPG-Kanalliste + Suche, **Vorschau ohne Speichern**, erst danach verbindlicher Speichern-Button. Kein unerwarteter Sender-/Startkanalwechsel.
- Quellen: konfigurierter Provider-XMLTV, EPGShare01 (DE/AT/CH je gewählt), Kaimandura DE und eigene XMLTV-Quellen; keine neuen Quellen ungefragt aktivieren. Auto-Match bei eindeutiger ID/Name, **manuelle Zuordnung gewinnt**, klare Status/Cache-/Fallbacklogik, Cache-Aktualisierung. Quelle nicht erreichbar/keine Daten → verständlicher Rückfall ohne EPG-Nullen. Test für Sender ohne Provider-EPG und manuell gewählte Alternativquelle.
- Dieser Punkt gehört zum ursprünglich gewünschten vollen EPG-Manager, aber getrennt von den Hotfixes und UI-Themes entwickeln.

## H – **Pflicht im nächsten Update**: #43 vollständiger Plug-and-Play-Erststart auf einem **zweiten frischen Kodi-System**
Der Nutzer hat am 23.10. ausdrücklich „Das muss auf jeden Fall rein. Komplett.“ gesagt. **Nicht** auf eine undefinierte spätere Roadmap verschieben.
- Ohne konfiguriertes Portal **automatisch sichtbaren SetupWizard** bei erstem XCMate-Start öffnen, ohne durch Verzeichnismenü klicken zu müssen; wiederholbar, abbrechbar, niemals auf eingerichteter Installation ungefragt erneut starten.
- Xtream/M3U-Datei oder URL/Stalker Eingabe, Prüfung, Account-Benennung, Providerkategorien vor vollständigem Import entdecken; Live/Film/Serie Auswahl mit Checkboxen pro Gruppe und Alle/Keine; nur gewählte Kategorien importieren, keine Vollscans aller Fremdsprachen.
- Anbieter-EPG und wählbare externe XMLTV-Quellen, DE/AT/CH, Quellstatus, automatische eindeutige EPG-ID-/Name-Zuordnung, fehlende EPG-Matches zeigen, später pro Sender via #98 korrigierbar.
- Automatisches, progressives **Cover-/Fanart-/Metadaten-Nachladen** für gewählte Filme/Serien; UI sofort benutzbar, Artwork jobs cache-first und Neustart-resistent, Fehler/Retry sichtbar; lizenzierter, verifizierter TMDB-Fallback nur wenn real verfügbar (#111). Keine falschen Metadaten.
- Fortschritt und verlässliche Counts für Kategorien, Sender/Filme/Serien, EPG, Cover; kontrolliertes Speichern/Abbrechen/Rollback des neuen Accounts ohne Verlust bestehender Accounts; Startgruppe/Startsender wählen, eindeutiger Abschluss zur XCMate-Startseite. Keine Schleifen/Blockade. Aufnahme-Ordnerkompatibilität #126 berücksichtigt.
- End-to-End Android Abnahme auf **frisch installiertem** Kodi 21.x, auch Kodi 21.3 wenn verfügbar; **Kodi 22 erst nach separater Verifikation**, nicht ungeprüft als kompatibel deklarieren.
- Ein partiell funktionierender Wizard gilt **nicht als abgeschlossen**, keine „100 % Cover“-Behauptung ohne Artwork-Quellen/Providerrechte.

## I – P1: #111 Artwork/Poster-Fallback, #115 optionales Space Premium
- B07 bei .26 **im getesteten Fall** PASS, #111 spezieller Aladdin-/Provider-Pfail TIMEOUT noch offen; konkrete Quelle/Retry-Failure, bounded Backoff, Cache-Persistenz, korrekte Poster und ggf. vorsichtiges TMDB-Matching reparieren. Keine massenhaften Downloads beim Bildschirmwechsel.
- Space Premium #115 ist **nicht** Lightweight-Abnahme: Premium Fokus/OK führt teils auf Suche/unresponsive, separate Hotfix-/Android-Abnahme, kein ungefragter Theme-Wechsel. Gewünschtes Original-Icon in beiden Stilen zwingend.
- Poster/Artwork-Queue/Cache möglichst mit #127 und #43 wiederverwenden, ohne das ganze System neu zu bauen.

## J – Geparkte separate Themen, nicht versehentlich als fertig markieren
- #62 EPG-Aufnahmetimer/automatisches Umschalten ist **nicht** identisch mit manuellem Sofortaufnahme-Hotfix #126; nur nach eigener Planung und Nutzerfreigabe.
- #113 Medienmanager „Meine Medien“, Downloads sowie vollständiges Space-Premium-Themesystem sind separate Phasen/PRs; keine automatische Beta-Freigabe.
- Mehrportal-/anbieterübergreifende Suche wurde durch #127 **nicht** bestellt. Aktuelles XCMate sucht im aktiven Portal; keine Quellenbezeichnung erfinden.

## Verbindliche Arbeits-/Review-Reihenfolge
### Phase 1 – Sicherheit, Absturz und Aufnahme (Draft-PR 0.1.29.27 Core)
1. **#125** fatales Search→Live Busy-Dialog-Race beheben – eigener kleiner PR.
2. **#126** Recorder-Zielprüfungen/Android-kompatiblen Pfad und Aufnahme-End-to-End – eigener kleiner PR.
3. **#120** Startsender-Skin-Shortcut/Live-Exit-Rücksprung – eigener separater PR bzw. Teil der klar beschriebenen Entry-Routing-Arbeit, mit eigenem Android-Gate.
4. Beide alten funktionierenden Guides (B04/B05), Live-IR (B03), Search-UI (S01–S05/S07), Staffel-Autoplay (B06) und User-Daten müssen weiter PASS sein.

### Phase 2 – funktionale Vollständigkeit und Oberflächen (separate stapelbare Draft-PRs)
5. **#127** Such-Ergebniszeilen (TV Logos/EPG, Film/Serien Mini-Cover/Metadaten).
6. **#122** durchgängiges Lightweight-Original-Splash.
7. **#123** hochwertige EPG-Programmdetails.
8. **#98** EPG per Sender manuell wählen mit Preview.
9. **#43** vollständige Plug-and-Play-Neuinstallation als **verbindliches Release-Gate der nächsten Baureihe**, gern paralleler eigenständiger PR nach stabilem Core.
10. **#111** Artwork-Retry/Fallback und Integration in #127/#43, soweit nicht schon sauber in deren PRs behoben.

### Wann .27 veröffentlichen?
- **Nicht** alle Änderungen in einen unreviewbaren Mega-Diff pressen. Arbeite auf gemeinsamer .26-Basis, in **kleinen Draft-PRs**, mit sauberer Abhängigkeit/Integration. Die Buildnummer **0.1.29.27** ist der vorgeschlagene nächste Test-/Releasekandidat; Teil-ZIPs ggf. mit internen Testkennungen, ohne öffentliches Release.
- Der **nächste als vollständig verbesserte Baureihe freigegebene Releasekandidat** muss alle ausdrücklich als verpflichtend beauftragten Punkte – insbesondere **#43 vollständiger Wizard** und **#127 neue Suchansicht** – enthalten oder eine neue ausdrückliche Nutzerentscheidung zur Aufteilung bekommen; keine stillschweigende Verschiebung.
- Für jeden PR: konkrete Root-Cause-/Änderungserklärung, Modul-Diff, Kodi-Mock-Tests/CI, Datenschutz-/Loghygiene, Android-Test-ZIP + SHA256, manuell ausführbare Testanleitung, Regressionstest mit PASS/FAIL/NOT_TESTED. **Keine** willkürlichen Version-/Repo-Bumps, keine bereits veröffentlichte .26-Original-ZIP überschreiben.
- Auf `main` **keinen Code mergen**, keine aktive Release-/Repository-Publikation und keine installierte Nutzerkonfiguration verändern, bevor Benutzer dies ausdrücklich freigibt.

## Sofortiger erster Codex-Auftrag
1. Aktuellen `main`, offenen **Docs-Draft PR #124** und dieses neue Master-Dokument lesen; klären, dass #124 veraltete Test-Priorisierung enthält und **nicht** .27-Code ist.
2. **Priorisierte Root-Cause-Analyse für #125** (kritische Kodi BusyDialog-Kollision bei Search→Live), danach **#126** (POSIX/Hardlink-Zielprobe vor Start). Reviewbare minimale Fix-Drafts und begleitende Tests vorbereiten.
3. Den Rest (#120/#127/#122/#123/#98/#43/#111) **als konkrete PR-Stack-Planung** mit Risiken/Abhängigkeiten abbilden und dann schrittweise implementieren.
4. Android-Testplan in Checkbox-/PASS/FAIL-Schritte überführen; .26-Baseline 15/6 unverändert belassen, neue Features als **NOT_TESTED** bis auf echter Box bestätigt.
5. Kein ungefragter Merge/Release. **Gefroren: Serien-Staffelautoplay, Live-TV-IR/Overlay, bestehende Provider/Groups/Favoriten/Resume/EPG und Original-Icon.**

## Links
- #125: https://github.com/artattakk-creator/kodi-noodleprivate/issues/125
- #126: https://github.com/artattakk-creator/kodi-noodleprivate/issues/126
- #120: https://github.com/artattakk-creator/kodi-noodleprivate/issues/120
- #127: https://github.com/artattakk-creator/kodi-noodleprivate/issues/127
- #122: https://github.com/artattakk-creator/kodi-noodleprivate/issues/122
- #123: https://github.com/artattakk-creator/kodi-noodleprivate/issues/123
- #98: https://github.com/artattakk-creator/kodi-noodleprivate/issues/98
- #43: https://github.com/artattakk-creator/kodi-noodleprivate/issues/43
- #111: https://github.com/artattakk-creator/kodi-noodleprivate/issues/111
- #85: https://github.com/artattakk-creator/kodi-noodleprivate/issues/85
- #124 (docs only): https://github.com/artattakk-creator/kodi-noodleprivate/pull/124
