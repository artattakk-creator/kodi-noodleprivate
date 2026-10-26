# XCMate 0.1.29.40 – Ursachenanalyse und verbleibende Grenzen

Stand: 26.10.2026. Basis `main` .39 `25a640869e3b4e178945ba4f549ad7e269dd292f`, Merge #198 `c5e5deb3f69fb5be3fc8f9d0904c943a03c18520`. Entwicklungsstand 0ab01d9e89dbf4114196fe1b8e048de975cb41d1. Nur anonymisierte öffentlich dokumentierte Logbefunde #201–#204 gelesen; keine privaten Original-Logs geöffnet oder hochgeladen. Die alte Datei beginnt unter .38; nur ab **16:04:55** bestätigte .39-Ereignisse als .39 werten. Historische .39-QA bleibt **10 PASS / 8 FAIL / 3 NOT_TESTED**, nicht durch Hosttests überschrieben.

## P0 #202 – unbeabsichtigter VOD-Stop reproduziert

Im .39-Code existieren zwei unabhängige automatische Stop-Auslöser ohne Benutzerintent:

1. `playback_exit.poll()` merkt schon nach einem einzelnen sichtbaren Fullscreen-Sample die eigene Session. Bei der nächsten Probe mit `fullscreen=False` fordert es Stop an. Weder AV-Start-Stabilität noch tatsächliche Back-Eingabe ist dafür erforderlich.
2. `media_window._poll_playback_return()` setzt `_playback_seen` bereits bei passender Video-InfoTag-ID und fordert bei nicht sichtbarem Fullscreen direkt Stop/Return an. Auch native `onInit` konnte im Legacy-Zweig einen Start canceln/stoppen.

**Gegenprobe auf unverändertem .39-main:** Dieselben zwei neuen Hosttests auf einem separaten Git-Archiv von `25a6408` schlagen jeweils fehl. `False → True → False` löst `exit_jobs` aus; im Owner-Poll entsteht ein `pending`-Stop ohne Benutzereingabe. In .40 bestehen beide Replays mit 20 Schleifen für Film und Episode. Dies ist ein konkreter Codefehlernachweis. Die neun Android-Stop-Intents nach 0,638–1,623 s passen dazu; da alte Logs keinen Reason enthalten, kann die konkrete Aufrufstelle jedes einzelnen Android-Ereignisses rückwirkend nicht bewiesen werden.

Korrektur: [playback_exit.py:105](../../src/plugin.video.xtreammate/resources/lib/playback_exit.py#L105) behandelt Fensterstatus ausschließlich als Beobachtung. Nur explizite Cancel-Intents werden hier gestoppt. [media_window.py:1084](../../src/plugin.video.xtreammate/resources/lib/media_window.py#L1084) stoppt nicht aufgrund eines Fensterwechsels und `onInit` cancelt keine Playback-Session. Back/Stop/Home aus den eigenen Eingabehandlern bleiben asynchron und sessiongeprüft. Jeder neue `EXIT_INTENT` trägt einen festen Reason; Titel/URLs/Portalnamen werden nicht geloggt.

`USER_STOP`, `USER_BACK`, `USER_HOME`, `AUTOPLAY_CANCEL`, `STARTUP_ABORT` sind aktive Ursachen. Die reservierten Codes `FULLSCREEN_EXIT`, `OWNER_CHANGED`, `PLAYBACK_ENDED` erlauben keine automatische Stop-Heuristik; natürlicher End-Callback ist kein Stop-Auftrag.

## P0 #203 – Stop-Quarantäne und native Fensterfreigabe

Belegt ist im .39-Zeitraum: Live Back → Stop-Worker → Kodi `CloseFile`/`OnExit`, danach kein protokolliertes `PLAYER_STOP_DONE` vor Log-Ende. Der exakte Kodi-/MediaCodec-Deadlock ist ohne native Threadstacks nicht festgestellt.

Im Code war Stop zwar im Worker, aber Service/Owner konnten währenddessen weiter `isPlayingVideo`/InfoTag abfragen. Solche Aufrufe sind keine Garantie für Nichtblockierung: Kodi kann denselben internen Playerlock halten. Zusätzlich war ein Timeout nach Interpreterwechsel ohne lokalen Threadhandle nicht ausreichend gegen einen erneuten manuellen Stop geschützt. Eine feste Wartezeit von 150 ms belegt auch keine tatsächliche native Dialogfreigabe.

- [exit_jobs.py:41](../../src/plugin.video.xtreammate/resources/lib/exit_jobs.py#L41): interpreterübergreifende Window-Property mit `stop_started`/`worker_done`. Timeout bleibt quarantänisiert, bis derselbe Worker sein Ende bestätigt. Keine Kill-/Retry-Schleife, kein zweiter Stop, auch bei fremdem/neuem Token nicht.
- [exit_jobs.py:100](../../src/plugin.video.xtreammate/resources/lib/exit_jobs.py#L100): Native Dialog-ID muss tatsächlich frei sein; fremde Modal-Fenster werden weder geschlossen noch ignoriert. Unerfüllte Freigabe läuft nach fünf Sekunden auf Timeout, ohne Stop zu starten.
- [service.py:160](../../src/plugin.video.xtreammate/service.py#L160): Stop-Poll/Quarantäne vor Navigation, Playertracking, Autoplay und Live-Recovery. Während blockiertem Stop tickt der Heartbeat weiter, aber fragt den Kodi-Player nicht ab. Bereits laufende Datenworker bleiben unabhängig; neue Playerstarts und Live-Preplay werden gesperrt.
- Live-Exit und Medienreturn lesen in dieser Phase ebenfalls keine Player-API. Eigenes Overlay wird vor Stop geschlossen und seine Controls werden geleert. Kein globales `Dialog.Close(all)`, kein Home-Navigieren über fremde Modals.

**Grenze:** Python kann einen in Kodi/C++/Treiber festhängenden `Player.stop()` nicht sicher abbrechen oder eine bereits blockierte Kodi-GUI entsperren. Die Änderungen vermeiden nachweislich die eigenen Folgeabfragen/Doppelstarts und warten auf native Freigabe; ein echter Android-Hängerfreiheit-PASS ist weiterhin zwingend. Falls `STOP_TIMEOUT` auftritt: keine wiederholten Stop-/Start-Versuche, Messung abbrechen und bereinigte Eventfolge melden. Kein Timeout als Erfolg ausgeben. #203/#192 bleiben offen.

## P0 #185 – Herkunft, Fehlerstart, Resume und Autoplay

Die Herkunft bleibt im RAM desselben nativen Owners. Der Such-XMLDialog wird vor dem VOD-Start auf seinem Ownerthread nativ ausgeblendet, ohne Close-/Cancel-Lifecycle oder Profiländerung. Nach Stop/Fehler wird genau dieses Objekt wieder angezeigt; auch eine zuvor unbekannte native Dialog-ID unterbindet die Wiederanzeige eines ausdrücklich selbst ausgeblendeten Objekts nicht.

[media_intent.py:81](../../src/plugin.video.xtreammate/resources/lib/media_intent.py#L81) veröffentlicht ein ausschließlich noncegebundenes `RESOLVER_FAILED`, wenn ein Resolver ohne erfolgreiches Item zurückkehrt. [app_routes.py](../../src/plugin.video.xtreammate/resources/lib/app_routes.py) verändert die bestehende Media-/Resume-Auflösung nicht. Ein nie angelaufener Decoder ohne expliziten Fehler führt nach 20 s nur dann zur kontrollierten Rückkehr, wenn **kein** Player aktiv ist; die Frist autorisiert keinen Stop eines initialisierenden/fremden Players. Unaufgelöster eigener Intent wird gecancelt, damit ein verspäteter Resolver nicht doch startet.

Vorhandene `media_progress`, `media_state`, `media_sequence`, `media_autoplay`, Decoder und Fernbedienungsprofile bleiben bytegleich zu .39. Bestehende Resume-/Gesehen-/Manual-Next-/Staffeltests bleiben enthalten. Ein Android-Autoplay-PASS ist erst nach erfolgreicher Grundwiedergabe möglich; das frühere 39-15 bleibt technisch BLOCKED durch #202.

## P1 #201/#190 – bestätigte Seiten statt flackernder Teilantworten

In .39 ersetzt `_search_ready` den gesamten Suchstand aus jeder Teilantwort. Ein leerer `INDEX_PENDING`-Teil überschreibt bestätigte Live-/Filmzeilen. Ein Reiterwechsel kann zusätzlich `_fill(710,[])` auslösen; Antworten für andere Seiten konnten die sichtbare Seite entwerten. Logs zeigen dazu passende Folgen 5→0 und 48→0→48.

[search_snapshot.py:13](../../src/plugin.video.xtreammate/resources/lib/search_snapshot.py#L13) speichert bis 24 Seiten in der Owner-Sitzung, getrennt nach Portal/Query/Generation/Kategorie sowie Kind und Offset. `_search_load` prüft Query-Session, Portal und Cancel. Antworten für eine andere Seite werden nur dort gespeichert. Temporäre Fehler/Pending und unfertige Live-Scans erhalten bestätigte Zeilen; ein endgültiger READY/DISABLED mit Total 0 leert korrekt. Kein Querytext/Portalzugang im neuen `SEARCH40`-Trace: nur zufällige Generation, Kind, Offset, Zeilen, Total, Code, Partial und Preservation.

[media_search.py:139](../../src/plugin.video.xtreammate/resources/lib/media_search.py#L139) vermeidet `ListItem.reset` bei gleichem Datenbestand. Bei identischen IDs werden nur geänderte Namen/EPG-Sekundärtexte aktualisiert; Cover und Fokus bleiben erhalten. Seiten-/Reiterwechsel zeigen nur den passenden Cache, nie Treffer einer anderen Query/Seite. Bestätigte Treffer bleiben während INDEX_PENDING bedienbar. Auf eine bisher unbekannte andere Seite kann die Liste erstmals leer/ladend sein; das ist kein gefälschter alter Seiteninhalt.

`search_data.search` publiziert zuerst lokale Sendernamen, im folgenden Worker die verfügbaren Film-/Serienseiten und erst danach die EPG-Vorbereitung. So warten Medien nicht auf diese Vorbereitung. Bestehende SQL-Zeitbudgets/48er-Seiten, lokale EPG-Indizes, Mappingpriorität und Safe-Cache-Fallback bleiben erhalten. Kein Indexwipe oder erzwungener Rescan als Reparatur. Android-39-s-Enrichment ist noch nicht als beseitigt gemessen.

## P1 OSD, Mini-EPG und Geistertexte

- Live-Recovery nach eigenem Standard-VideoOSD 12901 stellt bei versteckter Leiste zunächst `info` her; bisher sprang sie direkt zu `controls`. Damit bleibt erstes OK Info, zweites OK Player. VOD-Recovery erkennt den Standard-OSD auch bei kurzzeitig falschem Fullscreen-Flag. Fremde Dialoge werden weiterhin respektiert.
- Bestehende Live-Transport- und Optionszeilen haben mehr Abstand. Funktionen/Action-Indizes bleiben erhalten. Technische Details werden in einer nativen Kodi-Liste nach Bild/Ton/Untertiteln mit sieben lokalen Icon-Zeilen gruppiert; nur aus einem vorhandenen own-Player-Snapshot. Unbekannte Werte bleiben unbekannt, keine v22-Bitraten und kein vermutetes HDR/p/i. Keine neue Player-Engine.
- [mini_epg.py:64](../../src/plugin.video.xtreammate/resources/lib/mini_epg.py#L64): rechte Spalte 32 statt 38 Prozent, fünf sichtbare Programme mit nativen TextBoxen und maximal zwei expliziten Titelzeilen. NOW-Farbe und Fokusrahmen separat. Die Kodi-21.3-Signatur von `ControlTextBox(x,y,width,height,font,textColor)` ist gegen gepinnten Header `a3a448d.../Control.h` bestätigt und im strengen GUI-Test ergänzt. Echte BINGIE-Schrift-/Repaintdarstellung bleibt Geräteprüfung.
- [live_overlay.py:303](../../src/plugin.video.xtreammate/resources/lib/live_overlay.py#L303) leert alle versteckten/eigenen Listing- und Playertexte, auch beim Schließen/Suspend. Rail-Hide entfernt Breite/Fokusfähigkeit/Text und versetzt nur eigenen Rail-Fokus auf den eigenen Capture-Control. Vierstufige Gruppen-/Icon-Navigation bleibt erhalten.

## EPG/Latenz und Decodergrenzen

Gespeicherte `guide_v1.sqlite` und manuelle Zuordnung bleiben unverändert gemeinsame Basis. Mini, Infobar und großes EPG verwenden weiter den .39-Local-Reader; unterschiedliche Zukunftshorizonte sind erlaubt und kein Widerspruch von NOW/NEXT. Ein neuer Test hält den echten Guide-Worker im lokalen Snapshotzugriff an und führt währenddessen 20 IR-Wechsel/RAM-Lesevorgänge aus. Kein synchroner Providerimport durch Öffnen/Fokus; vorhandene Hintergrund-EPG-Publikation bleibt unabhängig.

Die .39-Werte Mini bis 16,2 s und Info bis 33,8 s sind Ende-zu-Ende, keine Render-CPU-Zeit. Bestehende UI39-/LIVE_TIMING-Phasen bleiben für Vorher/Nachher auf Box B erhalten. Weder Host-Millisekunden noch die Quarantäne beweisen eine neue Android-Latenz oder geheilte Rockchip-Treiber. .39-sichere Decoderzahlen laut #192: 8 OutputPicture-Timeouts, 2 InstanceGuard, 8 null-size, 3 ReleaseOutputBuffer; ältere 59 ActiveAE-Warnungen gehören zur .38-Phase und werden nicht .39 zugerechnet.

BINGIE-Widget-Now/Next/Rollover und echter Skin-Refresh bleiben Geräte-/Adaptergates aus #182, ohne ungefragte Skin-/Widgetkonfiguration. #98/#161, #195–#200, Portalverwaltung, Länder-/Playlist-/PIN-/Gesamticon-Vorhaben und Storage/Downloads bleiben separate Roadmap. Keine Freigabe oder Issue-Schließung durch diese Lieferung.
