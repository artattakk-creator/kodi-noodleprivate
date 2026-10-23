# XCMate 0.1.29.26 – Bereinigter Kodi-Logvergleich nach Android-Abnahme
**Datum:** 23.10.2026 · **Nutzerdateien:** `kodi.old(4).log` und `kodi(8).log` (privat; **nicht hochgeladen**). **Hardware:** Rockchip DQ08/RK3528 ARM32, Android TV 13, Kodi **21.2**, Titan BINGIE MOD 2.2.3. **Nutzerabnahme:** `docs/XCMate/ANDROID_ABNAHME_02926_20261023_NUTZERERGEBNISSE_DE.md` (15 PASS, 6 FAIL, 0 NOT_TESTED).

## Zeitliche Versionstrennung
- **Altes Log:** 16:09:25 bis 18:53:37. Bei Kodi-Start um 16:09:26 war XCMate **0.1.29.25** installiert. Erst um **18:42:32** dokumentiert Kodi `plugin.video.xtreammate v0.1.29.26 installed`. **Frühere Fehler nicht pauschal .26 zuschreiben!**
- **Neues Log:** 18:54:05 bis 19:11:50. Kodi startet mit XCMate **0.1.29.26**.
- Alle Zeiten sind Geräte-Kodi-Logzeit. Entsprechende Privatdaten, Anbieter-URLs, Sender-/Portal-IDs und Dateipfade sind bewusst **aus diesem Bericht entfernt**.

## P0 #125: S06 Live-TV-Treffer aus globaler Suche – KRITISCHER KODI-ABBRUCH
**Harte Log-Beweiskette, altes Log bereits nach .26-Installation:**
- **18:53:30.288** `[XCMate][SEARCH] event=SEARCH_RESULT_READY`: Suchergebnisse vorhanden.
- **18:53:32.219** `[XCMate][GUIDE_HANDOFF] stage=QUEUED`: ein Suchergebnis wird als Wiedergabeauftrag vorbereitet.
- **18:53:32.561** `SEARCH_WINDOW_CLOSED` nach Verlassen WindowXML; zwischen 18:53:32.612 und .613 `[XCMate][WINDOW] view=MOVIES stage=CLOSE_BEGIN / CLOSE_DONE`; `[XCMate][NAV] event=RETURN`.
- **18:53:32.694–.695** `[XCMate][GUIDE_HANDOFF] stage=RESOLVER_REQUEST`, dann `stage=DISPATCHED`.
- **18:53:32.982** neuer XCMate-Python-Invoker beginnt `ENTRY / MAIN_IMPORT_BEGIN`.
- **18:53:33.097** **KODI-CRITICAL**: `Logic error due to two concurrent busydialogs, this is a known issue. The application will exit.`
- Danach weitere parallele `ENTRY`- und `ROUTE action=root/OTHER`-Verarbeitung im auslaufenden Kodi-Prozess. **18:54:05** neues Log mit frischem Kodi-Prozessstart.

**Schlussfolgerung (präzise):** Für den S06-FAIL gibt es einen eindeutig belegten fatalen Kodi-Ladedialog-Konflikt **unmittelbar nach** erfolgreich bis `DISPATCHED` kommendem Search→Live-Handoff. Die gezeigten Zeitstempel beweisen **Korrelation und Kodi-Fehlertyp**, nicht, welches Modul den zweiten Busy-Dialog öffnete. Ein genereller Provider-/Streamdefekt ist hier nicht belegt. Der Benutzer hat **S01 „Upload“-Suche PASS**, also ist die ursprüngliche Absturzart beim bloßen Such-OK in der getesteten .26-Situation **nicht** aufgetreten. **S06 ist jedoch ein eigener P0-Prozessabbruch-Kandidat**; nicht als bloße „kein Video“-Fehlfunktion herunterpriorisieren.

**Codex-Hotfix-Gate:** Kodi-Busy-/WindowXML-/Owner-Lifecycle untersuchen; sicherstellen, dass beim Search-Intent kein konkurrierender directory/root-Aufruf oder Busy-Dialog gleichzeitig mit `PlayMedia(play_live)` läuft. `media_search.py::handoff`, `guide_playback.py::_handoff`, `window_navigation.py::open_route`, `main.Router`, `live_exit.py` sowie tatsächliche Kodi-Plugin-Aufrufreihenfolge vergleichen. Kein nur zeitbasiertes Sleep-Workaround; einen einzigen gebündelten Übergabepfad und ein Exit-/Busy-Gate vor der Wiedergabe. Reproduktions-/Korrelationstests, speziell erst Suche `Upload`, dann einen echten Live-Treffer auswählen; auch wiederholtes Starten und Rückkehr. Nie Provider-URI/SID/PID/Account im Log.

## B05 erneut PASS: EPG→Live-Handoff (Issue #121)
**Neues Log** zeigt zwei Guide-Abläufe:
1. **18:57:13.803** QUEUED → GUIDE CLOSE_DONE **18:57:14.125** → RESOLVER_REQUEST / DISPATCHED **18:57:16.353–.354** → `[XCMate][LIVE_EXIT] stage=LIVE_RESOLVER` **18:57:17.303** → Kodi `VideoPlayer::OpenFile` des **XCMate `play_live`**-Plugins **18:57:19.149**. Die privaten URL-Argumente werden hier **nicht** übernommen.
2. **19:09:05.634** QUEUED → GUIDE CLOSE_DONE **19:09:05.949** → RESOLVER_REQUEST / DISPATCHED **19:09:07.988–.989**; später Codec-/Player-Aktivität im selben Ablauf.
Im neuen Log findet sich **kein** `two concurrent busydialogs`-CRITICAL. Dies stützt den zuletzt gemeldeten **B05-PASS** im EPG, **kein** Generalbeweis für jede Sender-/Streamkombination. Spezifische Such-S06- und EPG-B05-Routen getrennt behandeln.

## Aufnahme R03–R06: `FAILED / 0 MB / UNSUPPORTED_TARGET` (Issue #126)
**Gesicherte Nutzerbeobachtung, nicht aus dem Log:** Der Sofortaufnahme-Auftrag lässt sich in der UI auslösen (**R02 PASS**); anschließend meldet die Aufnahmeverwaltung **`FAILED / 0 MB / UNSUPPORTED_TARGET`** (**R03 FAIL**, nachgelagerte R04–R06 ebenfalls nutzerseitig FAIL). **In beiden übergebenen Kodi-Logs ist `UNSUPPORTED_TARGET` NICHT wörtlich enthalten** und es erscheinen keine expliziten `[XCMate][CAPTURE]`-/Recorder-Zielprobe-Reason-Codes. **Konkreter Zielpfad/Dateisystemtyp und fehlgeschlagener Syscall sind damit nicht bewiesen.**

**Quellcode-Bezug:** `home_menu.py::probe_directory` prüft Kodi-VFS-Schreiben/Lesen, `direct_ts.py::_probe_target` später aber POSIX-`os.link`/Hardlink (bei `OSError` → `Failure('UNSUPPORTED_TARGET')`), außerdem NoFollow/absolute POSIX-Pfade. Emuliertes Android-Storage `/storage/emulated/0` ist im Kodi-Umfeld vorhanden, aber das tatsächlich vom Nutzer eingestellte `recordings_folder` ist NICHT bekannt. Daher **keinen bestimmten Mount-Typ als bewiesene Ursache benennen**. Codex: dieselbe Recorder-Fähigkeitsprobe **vor** Jobannahme/Provider-`resolve`, nachvollziehbarer Statuscode und Fehlerkategorie/errno ohne privaten Pfad, geeignete sichere lokale Ziele anbieten.

## Skin Shortcuts #120: eigenständiger Python-3.11-Fehler im Zusatz-Add-on
Das **alte** Log enthält im Zeitraum ab **16:45:07** und erneut gegen **17:06:04** gehäuft (rund **684**) Tracebacks, die auf **`script.skinshortcuts`** (nicht `plugin.video.xtreammate`) zurückgehen:
`AttributeError: 'xml.etree.ElementTree.Element' object has no attribute 'getiterator'` im Funktionskontext `playlists` auf **Zeile 971**. Die veraltete `getiterator()`-API ist unter der Kodi-Python-Umgebung nicht vorhanden. Diese konkreten Fehler liegen **vor .26-Installation** und sind ein **separater Skin-Shortcuts-Kompatibilitätsbefund**. Können Shortcut-Aktionslisten/-Wiederaufbau stören; sie beweisen **nicht**, dass genau dies die ursprüngliche Live-TV-Hauptmenü-Kachel blockierte. Bitte den Skin-/script.skinshortcuts-Kompatibilitätsstand klären und XCMate-Startbutton separat prüfen, ohne das Kodi-Skin-Add-on im XCMate-PR eigenmächtig zu patchen.

**Neues Log:** Beim Live-TV-Exit um **19:11:08.287** `[XCMate][LIVE_EXIT] stage=HOME_REQUESTED`, dann `ROUTE action=xcmate_home` **19:11:09.183** mit `DIRECTORY_DONE`, allerdings meldet Kodi **19:11:10.599–.618** `GetDirectory`/ `CGUIMediaWindow::GetDirectory` für `xcmate_home` als **failed**. Weiterer Aufruf `xcmate_home` ab **19:11:11.808** wird verarbeitet. Das zeigt einen **intermittierenden/kontextabhängigen Rücksprung-Fehler** trotz scheinbar erfolgreichem Plugin-Verzeichnisabschluss. Erklärungsbedürftiger Navigation-/Container-Kontext, aber kein direkter Beleg, dass exakt die Skin-Live-TV-Kachel den Fehler ausgelöst hat.

## Sonstige nicht-verwechselbare Befunde
- Kodi 21.2, nicht ein bestätigtes Kodi 21.3/22-System. Keine daraus abgeleitete neuere Kodi-Kompatibilitätsfreigabe.
- Mehrere alte/invalide Repository-Metadaten anderer Kodi-Add-ons und Warnungen zu HTTP-Repositories im Log; das sind **andere Add-ons**, nicht automatisch Fehler des GS-Media-Repositories.
- Die zahlreichen `script.skinshortcuts`-Tracebacks erklären hohe Kodi-Log-Fehlerzahlen im **älteren** Log, nicht den genannten `UNSUPPORTED_TARGET`-Status.
- Keine vollständigen Nutzerlogs auf GitHub kopieren; diese können private Server/Account- und Player-IDs und Stream-Argumente enthalten. Für Unterstützung nur neutrale Zeitstempel, Stufen, Fehlercodes und Dateimodulnamen.

## Release-Gate
**Abnahme 0.1.29.26 weiterhin: 15 PASS / 6 FAIL / 0 NOT_TESTED.** S06 aufgrund des belegten CRITICAL besonders ernst; #126 Aufnahme bleibt blockiert. #120 Skinbutton FAIL; EPG-B05, Autoplay-B06 und übrige PASS strikt schützen. Erst getrennter Codex-Hotfix in Draft-PRs, automatisierte Tests + Android-Realgerät-PASS, kein unaufgeforderter Merge.
