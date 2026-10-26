# XCMate 0.1.29.42 – P0 Live-Back, Nachweis und Evidenzgrenzen

Stand: 26.10.2026, Europe/Berlin. Basis `354afc1cc524ec3b01001770e6afe6aec5fea70c`, veröffentlichte .41. Auftrag #216, reale Android-Abnahme #215, ursprünglicher Fehler #203, Master #213. Nur Live-Exit und notwendige Diagnose-/Versions-/Testdateien. Private Rohlogs wurden weder geöffnet noch veröffentlicht; verwendet wurden die anonymisierten Issue-Auszüge.

**Status: konkreter opt-in Kompatibilitäts-/Diagnosekandidat, keine nachgewiesene Reparatur des nativen RK3528-Hängers. Android NOT_TESTED.** Ohne Aktivierung der neuen Option bleibt der bekannte .41-Stop-Pfad erhalten. Auf Box B deshalb vor einem erneuten Live-Test die Option gemäß Abnahmeplan einschalten. Box A bleibt ausgeschlossen.

## 1. Was der Android-Befund tatsächlich beweist

Aus #215: 22:36:43.378 STOP_REQUESTED, 43.380 Back action92, 43.848 EXIT_INTENT, 44.148 PLAYER_STOP_START, 44.152 NATIVE_STOP_POSTED, 44.153 CVideoPlayer::CloseFile, 44.157 waiting for threads, 44.383 deleting video codec, 48.971 STOP_TIMEOUT. Kein finished waiting, keine Stop-Barriere, kein PLAYER_STOP_DONE/STOP_DONE/HOME_REQUESTED. Hintergrundaktivität läuft bis22:38:32 weiter.

Damit sind Back-Erkennung, Intent und das Erreichen des nativen Close bestätigt. Die .41-Änderung hat den Gerätefehler nicht behoben. Eine stille Python-Queue oder falsche Keymap ist für diesen konkreten Ablauf keine passende Erklärung. Weiterlaufende Hintergrundarbeit beweist keine bedienbare Kodi-GUI.

Alle nativen Referenzen unten sind auf exakt Kodis Gerätebuild `a3a448d26b8d560a65655dab2cd122994dc4e146` gepinnt. Funktionsauszüge, Quellpfade und Zeilen stehen in [KODI_NATIVE_PROOF_02942.json](KODI_NATIVE_PROOF_02942.json); Kodi-Quellen bleiben unter ihrer GPL-Lizenz.

- `CApplication::StopPlaying`: ruft zuerst `ClosePlayer()` auf, erst nach dessen Rückkehr `PreviousWindow()`. .41 stoppt also bei weiterhin aktivem nativen FullscreenVideo.
- `CVideoPlayer::CloseFile`: setzt Abort, bricht Demuxer/Input ab, ruft **vor** „waiting for threads“ bereits `m_renderManager.UnInit()` auf. Danach wartet `StopThread()` auf den VideoPlayer-Hauptworker. Der Grafiklock wird dabei ausdrücklich per `CSingleExit` freigegeben. Eine pauschale Behauptung „Python/Stop hält immer den Grafiklock“ wäre falsch.
- `CVideoPlayer::OnExit`: schließt Audio und Video, registriert den Renderloop ab, räumt Renderer/Demuxer/Input auf und reicht Callbacks aus. Das Log erreicht nicht nachweislich das Ende dieser Funktion.
- `CVideoPlayerVideo::CloseStream`: **nach** Ende des Videodecode-Threads kommt „deleting video codec“, dann `m_pVideoCodec.reset()`. Beendete Audio-/Video-Threads beweisen somit nicht, dass der übergeordnete Playerworker fertig ist.
- `CDVDVideoCodecAndroidMediaCodec::Dispose`: Flush/Bufferpool, native `m_codec->stop()`/`release()`, SurfaceTexture- und gegebenenfalls VideoView-Freigabe. `surfaceDestroyed` kann ebenfalls Codec-Stop auslösen. Das passt zu einer möglichen nativen Freigabeblockade, ist ohne Stack aber kein Beweis für deren genaue Stelle.
- `CAESinkAUDIOTRACK::Deinitialize`: pause/flush/release. Die protokollierte AudioTrack-Reinitialisierung beweist weder erfolgreiche vollständige Playerfreigabe noch AudioTrack als Ursache.
- `CRenderManager::UnInit/Flush`: Mainthread-/Renderlock-Pfade vorhanden. Der bestätigte Logpunkt hinter UnInit begrenzt die Hypothese; nicht jeden Rendererpfad pauschal zum Schuldigen erklären.

**Gesichert:** Die vollständige native Close-/Mainqueue-Rückkehr fehlt. **Offen:** exakter wartender Thread, Lockhalter und Rolle von MediaCodec/Surface, Renderloop, AudioEngine, InputStream oder Treiber. Es gibt keinen Android-ANR-/Native-Thread-Dump. Einen ausschließlich nativen Rockchip-Defekt kann auch diese Codeanalyse noch nicht beweisen.

## 2. Gegenprüfung der Strategien

| Strategie | Mechanismus | Befund / Entscheidung |
|---|---|---|
| Alter synchroner `Player.stop()` | SendMsg und derselbe native Close | Gerätefehler bekannt; nicht wieder eingeführt |
| .41 direkter `PlayerControl(Stop)` | PostMsg, StopPlaying/ClosePlayer vor Fullscreen-Deinit, danach FIFO-Barriere | Android #215 FAIL; als unveränderter Standard-/Vergleichspfad erhalten, nicht erneut auf Box B provozieren |
| JSON-RPC `Player.Stop` allein | `PlayerOperations::Stop` postet TMSG_MEDIA_STOP | Andere Eintrittsstelle, aber kein nachgewiesener Ausweg aus demselben Close; nicht als Fix implementiert |
| .42 opt-in native Fullscreen-Deinit vor Stop | Overlay weg, normale modalbewusste Aktivierung von Videos, eigene Prepare-Barriere, sichtbare Fullscreen-Freigabe, danach einmal Stop mit bestehender echter Rückkehrbarriere | Implementiert, Hostverträge PASS; Android NOT_TESTED |
| Per-Item Softwaredecoder / anderer Demuxer | Nur mit auf Kodi21.3 belegter enger API sinnvoll | BLOCKED: `CODEC_FORCE_SOFTWARE` ist ein internes C++-Flag, keine hier belegte Python-/ListItem-Option. Kein erfundenes Property, kein pauschaler FFmpegDirect-Zwang, kein globales Ausschalten von Hardwaredecoding |

Der alternative Ablauf verändert **die native Lifecycle-Reihenfolge**. Er ist weder ein weiterer Python-Thread noch eine neue Bezeichnung für denselben direkten Queuepost. Er stellt aber keinen anderen nativen Decoder bereit: Wenn dessen Stop auch nach Fullscreen-Deinit hängt, kann Add-on-Python den fremden nativen Code nicht entklemmen.

Der Startsenderpfad `_startup_playable` fordert im vorhandenen Xtream-Code eine `.ts`-Adresse an. `build_playable_item` verwendet für erkanntes HLS/DASH gegebenenfalls InputStream Adaptive, für diesen TS-Pfad den bisherigen nativen Player. Eine Dateiendung beweist den tatsächlichen Inhalt nach Providerweiterleitung nicht. Ein anderes Demuxer-Add-on garantiert zudem keinen anderen Android-Videoausgabecodec. Deshalb keine spekulative `.ts`→`.m3u8`-URLumschreibung, kein neuer Providerrequest und keine ungefragte Installation von InputStream FFmpegDirect. Ein echter Transport-/Codecvergleich bleibt ohne Geräte-/Streamnachweis offen.

## 3. Konkrete Implementierung

`live_stop42.py`, Schalter `live_exit_fullscreen42`, Standard **false**. Lesen der Option schreibt keine bestehenden Einstellungen um. Aktivierung ausdrücklich nur auf Box B. Gültig für Android/Kodi21.3, nur per unveränderlicher Item-Identität verifiziertes eigenes Live-TV; Filme/Serien und Fremdplayer verwenden diesen Zweig nicht.

1. Bestehendes `live_exit.request` hält Back/Stop/Home als sitzungsgebundenes Intent fest; Overlays schließen weiterhin nur ihre Ebene. Der unveränderte Navigator wird vor nativer Vorbereitung geschlossen.
2. `exit_jobs` wartet auf tatsächliche Dialogfreigabe. Neue Vorbereitung prüft erneut Besitzer, Plattform, Version, Fenster und Modalstatus.
3. Einmal `ActivateWindow(Videos)` **ohne URL, force oder Fremd-Skin-Eingriff**, danach `SetProperty(XCMate.LivePrepareAck42,<Nonce>,home)`. Die normale Videos-Aktivierung verwirft im Kodi-Mainthread den Wechsel bei `HasModalDialog(true)`. Anders als direktes gezieltes Fullscreen-ShowGui umgeht sie diese native Modalprüfung nicht.
4. Ein eigener zufälliger Prepare-Nonce bestätigt nur die abgearbeitete Fensteroperation. Zusätzlich müssen FullscreenVideo unsichtbar und Home/Videos aktiv sein. Eine reine Queuequittung bei weiter sichtbarem Vollbild reicht ausdrücklich nicht.
5. Direkt vor Stop erneute Besitzer-/GUI-Prüfung. Erst danach der bestehende einmalige Live-Stop und **dessen separate** .41-Rückkehrbarriere. Frühe Callbacks, `isPlaying=False`, Prepare-ACK und beendeter Pythonworker sind kein Stop-Erfolg.
6. Bestehendes Fünf-Sekunden-Deadline unverändert; die Vorbereitung bekommt kein zusätzliches Zeitbudget. Bei unklarem Prepare-Post kein Wiederholen. Die laufende GUI-Operation bleibt bis zur passenden Barriere quarantänisiert, auch über Interpreterwechsel und Timeout hinweg.
7. Eine erst nach Deadline beobachtete Stop-Barriere bleibt TIMEOUT, auch wenn zuvor noch kein Timeout-Tick lief. Verspätete Prepare-/Stop-Rückkehr löst keine automatische Home-Erfolgsmeldung aus. Fehlgeschlagene Jobs können auch durch einen frühen Playback-Callback nicht zu STOP_DONE werden.

Der Zwischenwechsel kann Videos zeigen, während der Stream noch kurz vor dem einmaligen Stop läuft. **Das ist kein Abnahmeerfolg.** Erfolg verlangt native Stop-Rückkehr, keinen Hintergrundton und bedienbare Navigation. Bei anschließendem nativem Hänger bleibt der Test FAIL, selbst wenn ein Menü vorher sichtbar wurde.

## 4. Grenzen und sichere Fehlerfälle

- Mainqueue blockiert vor dem Fensterwechsel: kein Stop, kein Replay, Timeout; spät ausgeführte Vorbereitung bleibt ein fehlgeschlagener Versuch.
- Modal erscheint während die Aktivierung wartet: normale Kodi-Aktivierung kann sie auf dem Mainthread ablehnen; fehlende echte Fullscreen-Freigabe verhindert Stop. Kein `Dialog.Close(all)` oder Ignorieren eines aktiven Modals.
- Besitzerwechsel vor Vorbereitung oder vor Stop: kein fremder Stop. Kodi bietet dennoch keinen atomaren „vergleiche Session und führe queued GUI/Stop aus“-Token und keine sichere Rücknahme einer bereits geposteten Operation. Ein externer Playerübernahme-Race nach dem letzten Check ist nicht vollständig in Python eliminierbar; während der kurzen Geräteabnahme keine parallelen Add-ons/Player starten.
- Neue Aktivierung von Videos kann auf einem Skin selbst langsam laden. Bei überschrittener Deadline keine automatische zweite Aktivierung oder Stop-Scheinfreigabe. Aus einem solchen PREP-Timeout folgt noch keine Decoderdiagnose.
- Stop bleibt nach bestätigtem Fullscreen-Abbau hängen: Quarantäne, kein zweiter Stop, kein erzwungenes Home, kein automatischer Kodi-Neustart. Nicht weiter Freeze-Tests wiederholen.
- RAM-/Settings-Lesefehler vor Post: abgebrochener Job ohne nativen Aufruf. Keine neue SQLite-Tabelle, Journaldatei oder Profildatenmigration in .42.

Diagnoseereignisse sind feste Codes, gehashte Sitzung, Thread, monotone Zeit sowie Fenster-/Dialognummern. Keine Provideradresse, URL, Zugangsdaten, Portal-/Sender-ID oder unbekannte Exceptiontexte. Wichtige Grenzen: STRATEGY_FULLSCREEN42 → FULLSCREEN_EXIT_POSTED → FULLSCREEN_EXIT_RETURN → FULLSCREEN_READY → PLAYER_STOP_START → NATIVE_STOP_POSTED → PLAYER_STOP_DONE. Fehlt nach FULLSCREEN_READY die Stop-Rückkehr, wurde der eigene Dialog-/Fullscreen-Abbau wenigstens separat bestätigt.

## 5. Hostmodell ist kein Android-Beweis

Der Vergleichstest A modelliert absichtlich einen nativen Stop, der bei aktivem Fullscreen hängenbleibt. Test B räumt diesen Modellzustand vorher ab. Diese eingebaute Testannahme zeigt die veränderte Reihenfolge und deren Fehlerverträge; sie reproduziert keinen echten RK3528-Treiber. Ein weiterer Test lässt Stop **auch nach** Deinit dauerhaft hängen und verlangt weiterhin TIMEOUT/Quarantäne ohne Erfolgsnavigation. Separate Prüfungen decken Queue-Stau, beide Barrieren, falsche Nonces, späte Rückkehr, Modal-Races, Besitzerwechsel, Doppelklicks, Neustart des Pythoninterpreters, Speicherdruck, Shutdown und unveränderte VOD-Behandlung ab.

## 6. Wenn die eine Android-Probe weiter FAIL ist

Abnahme abbrechen und #216/#203 offen halten. Zur nächsten Eingrenzung werden native Main-/VideoPlayer-/Codec-/AudioEngine-Stacks während desselben Vorfalls benötigt, zusammen mit Version/Gerät, letztem .42-Phasencode und Android-ANR-/MediaCodec-Ereignissen. Das muss insbesondere zwischen JNI codec stop/release, Surfacefreigabe, Renderloop-Lock und übriger OnExit-Aufräumarbeit unterscheiden.

**Kein ADB, Root, Signal, globaler Codec-Umschalter oder Bugreport wurde ausgeführt.** Eine solche Erfassung erfordert einen gesondert freigegebenen, privaten Diagnoseweg. Wenn normales Android keine Stacks liefert, Kodi-/Firmware-Diagnosebuild beziehungsweise Herstelleranalyse als BLOCKED dokumentieren. Roh-Bugreports/Logs können Zugangsdaten enthalten und gehören nicht unbereinigt auf GitHub. Bis dahin bleibt die native Ursache offen; keine Behauptung, das Add-on habe den Rockchip-Decoder repariert.
