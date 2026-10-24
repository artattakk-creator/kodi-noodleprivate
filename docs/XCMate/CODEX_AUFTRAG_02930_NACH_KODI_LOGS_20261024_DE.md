# XCMate – Codex-Implementierungsauftrag nach zwei echten Android-Kodi-Logs
**Stand:** 24.10.2026 · **Basis:** `main` XCMate **0.1.29.29**; **vorgeschlagene nächste Testversion** 0.1.29.30 nur falls Versionsnummer frei. **Gerät:** Android TV 13, RK3528 ARM32, Kodi 21.2, Titan BINGIE MOD. **Kein ungefragter Merge/Release.**

## Unbedingt zuerst lesen
1. [Sanitisierte, datengetreue Kodi-Logforensik](KODI_LOGANALYSE_02928_02929_20261024_DE.md)
2. [Vollständige .29-Android-Abnahme](ANDROID_ABNAHME_02929_20261024_NUTZERERGEBNISSE_DE.md)
3. [#141](https://github.com/artattakk-creator/kodi-noodleprivate/issues/141), [#136](https://github.com/artattakk-creator/kodi-noodleprivate/issues/136), [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140), [#122](https://github.com/artattakk-creator/kodi-noodleprivate/issues/122), [#142](https://github.com/artattakk-creator/kodi-noodleprivate/issues/142)
**Die privaten Original-Kodi-Logs nicht auf GitHub speichern.** Diagnose nur ohne URLs, SMB-Servernamen, Dateipfade, Portal-/Anbieter-/Medientitel, Benutzernamen, Tokens oder Credentials.

## Phase A – P0: Speicher-/Portal-Ladeschleife und laufender .29-Regressionstest (#141)
- Altes .28-`kodi.old.log`: **22.526 `PORTALS_LOAD_BEGIN`**, ab 01:30 **16.981 `portals.load_all failed: MemoryError`**, um 08:43 **`ROOT_MENU_FAILED / DISPATCH_FAILED / START_FAILED`** plus Kodi-Verzeichnisfehler. Durch Logs gesichert.
- Neues .29-`kodi.log` nach Update um 09:15:08 hat **0** weitere MemoryErrors im ca. 37-minütigen Nachbeobachtungsfenster, aber **1.036** Portal-Load-Starts. **Kein Langzeit-PASS.**
- Aufrufquellen und Frequenz `portals.load_all()` im Idle, Live, Grid, Metadaten, EPG, Widgets identifizieren; nachweisbare Speicherzeitreihe (RSS/PSS) + Thread/Worker/Queue-/Handle-Zahlen, 4-MiB-Dateilese-/JSON-Wiederholung pro Request bewerten. Keine unbewiesene Memory-Leak-Ursache behaupten.
- Kohärente Profil-Snapshots, sinnvolles Rate-Limit/Backoff und kontrollierte Worker-Last nur nach Messung implementieren; Profiländerungen und Setup-Wizard müssen sofort invalidieren; keine alten Credentials, keine Account-/Gruppenverluste.
- `CPythonInvoker script didn't stop in 5 seconds - let's kill it` beim Upgrade .28→.29 und Service-Neustart/Shutdown auf hängende Worker prüfen. Kodi-/IR-/EPG-Kern erhalten.
- **Gate:** mehrere Stunden echter ARM32-Langzeitbetrieb inkl. Neustart, idle, Film/Serie, Live und Service-Update ohne MemoryError, Portal-Counts stabil begrenzt, Menüs zuverlässig erreichbar. Nur Android-Gerätetest = Geräte-PASS.

## Phase B – P0: USB-/SMB-Speicherziel und Laufwerksübersicht (#136; #126 separat)
- Neues .29-Log: `[XCMate][CAPTURE_TARGET]` **09:23:04 UNSUPPORTED_TARGET/PATH/0**, **09:23:11 READY/RENAME_NOREPLACE/0**, **09:23:43 TARGET_ATOMIC_PUBLISH_UNAVAILABLE/LINK/38**, **09:29:13 und 09:29:54 READY**. `LINK:38 = ENOSYS` für native Veröffentlichung. **MARKER SIND `CAPTURE_TARGET`**, *nicht* bestätigte `DOWNLOAD_TARGET`-/SMB2-Backend-Traces. Falscher Menüzweig, interne Staging-Probe oder Backend-Dispatch sind **Hypothesen** und gezielt zu diagnostizieren.
- **UI:** Bei `Downloadziel wählen` **zuerst Laufwerks-/Quellenübersicht** mit getrenntem **Kodi-intern / USB bzw. externer Speicher / bereits konfigurierte Kodi-Samba-Freigabe**. Aufnahmeziel separat kennzeichnen. Nicht mit `browseSingle(... defaultt=old)` im internen Pfad starten; interne Einstellung nach Ablehnung nicht stillschweigend als Ersatz übernehmen.
- Marker `PICKER_ACTION=DOWNLOAD|RECORD`, `TARGET_KIND`, `PROBE_BACKEND=NATIVE|USB_STAGE|SMB2|INTERNAL_STAGE`, `PROBE_CODE/STEP/ERRNO`, `TARGET_PERSISTED`; keinerlei Klarpfade/Provider-/SMB-Details öffentlich. Prüfe `download_target_ui.choose`, `home_menu.recording_folder`, `download_targets.assess/_usb_probe/_smb_probe/stage_root`, `atomic_media.probe/publish`.
- USB: O_EXCL-Kollision, FAT32 >4GiB, Android-Permissions/SAF, persistente Volume-Identität und dauerhafte sichere Ausgabe. SMB: vorhandene Kodi-Quelle und separate signierte SMB2-Schreibsitzung; Auth, Hash, Netzunterbrechung, Retry, bestätigtes Complete; kein Gast-/SMB1-Downgrade. Internes Stage-Volume muss **wirklich** die erforderliche sichere nooverwrite-Veröffentlichung tragen. Niemals `os.link`-/fsync-/Hash-Schutz blind aushebeln.
- **Gate:** echte USB-/SMB-Auswahl, Persistenz über Kodi-Neustart, tatsächliche Datei auf Ziel, Integritätsprüfung/Wiedergabe, Netztrennung korrekt behandelt. Aufnahmen gesondert mit kompatiblem Direct-TS-Ziel, Bytes>0, Stop, Playback. **Alle früheren ST01–ST07/CAP01–02 Rohurteile bleiben FAIL** bis neue Android-Abnahme.

## Phase C – P0: A03 EPG-Titelsuche (#140)
- .29-Suche loggt erfolgreich `SEARCH_GUI_READY / SEARCH_RESULT_READY / SEARCH_LIVE PLAYER_DISPATCHED`, passend zu A02 PASS. Sie loggt **nicht**, ob ein jetzt laufender EPG-Titel matcht. Nutzer A03 FAIL, .27 A03 historisch PASS.
- `search_data.live_matches` vs großes EPG: aktive Quelle/Programmzeit (UTC), `guide_alias`, manuelle Quellzuordnung, Portal/Kanal-ID, normalisierte Query-Tokens, SQLite-Timeout/Deadline/Index-Pending prüfen; nur Count-/Reason-Diagnose, keine gesuchten Programme oder IDs.
- **Gate:** Exakt jetzt laufende Sendung wird aus EPG-Jetzt-Titel im Live-Suchbereich gefunden und spielt den zugehörigen Sender. A01/A02/A04–A08, REG01/02 weiterhin PASS.

## Phase D – Verbindlich beim nächsten Testpaket: Hintergrund und PO-Fehler (#122, #142)
- **#122 Nutzerpflicht:** unverändertes Repo-Original `themes/xcmate/space-premium/assets/branding/splash-1920.jpg` als lokal mitgelieferte **einheitliche Lightweight-Grundfläche** in Home, Film- und Serien-Landing, Suche und geeigneten Menüs. Nicht durch generierte Bilder ersetzen; Textkontrast/Performance ARM32 sicherstellen, **Original-XCMate-App-Icon** behalten, Space-Premium-Theme nicht automatisch aktivieren.
- **#142 Bestätigt nach .29-Upgrade:** `POParser: warning, unhandled escape character` bei `#34718` (englisches SMB-Passwort-Label); ungültiges `\\u2013` im `msgid` der `.po` als korrektes UTF-8-Zeichen darstellen, deutsche/englische PO-Dateien CI-linten, Kodi-Dialog real anzeigen. Parserfehler nicht fälschlich als alleinige Speicherursache behaupten.

## Phase E – Danach die bereits dokumentierten Folge-Gates wieder öffnen
- **#135/#63:** .28-Log beweist `[XCMate][DOWNLOAD] stage=FAILED reason=REDIRECT_UNSUPPORTED bytes=0` am 24.10. 00:03; .29 hat **keine** neue beweisende Redirect-Worker-Aufzeichnung. Erst nach funktionsfähigem Speicherziel autorisierten CDN-Redirect, echten Film, einzelne Serienepisode, Pause/Resume/Retry, offline (nur lokal/USB) und Kodi-Neustart abnehmen. Kein pauschales Freigeben fremder CDN-Hosts.
- **#111:** Poster-Retry/Fallback noch vom Nutzer FAIL, kein konkreter neuer Artwork-Status; separat und ohne Datenverlust testen.
- **#131:** M01–M03 in .29 tatsächlich PASS, Menünavigation nicht destabilisieren; Inhalte/Downloads damit nicht automatisch vollständig PASS.
- **#43/#127:** Vollständiger Plug-and-Play-Wizard und bebilderte Rich Search mit Sender-Icon/EPG und Film-/Serienpostern weiterhin nächste größere Releasepflicht; nicht als bereits in .29 fertig ausweisen.
- Kodi-Log meldet außerdem Bingie-Repo mit veraltetem Schema und XVault-Repo mit HTTP-Download; **Drittanbieter-Warnungen**, nicht ungefragt andere Repositorys modifizieren.

## Lieferung
Jetzt **Codeänderungen, automatisierte Tests und Draft-PRs** für die obigen unabhängigen Fixes erstellen; danach **einen kumulativen Android-Testkandidaten** (voraussichtlich `0.1.29.30`, nur wenn Versionsnummer frei) mit vollständigem ZIP, SHA256, Changelog, anonymisierten Diagnose-Events, realer mehrstündiger Memory-/IR-/USB-/SMB-Testanleitung und PASS/FAIL/NOT_TESTED-Checkliste. Testgerät Kodi 21.2/RK3528. **Kein eigenmächtiger Merge/Release nach main; Portal-/Gruppe-/EPG-/Favoriten-/Resume-/Autoplay-/Icon-Daten bewahren.**
