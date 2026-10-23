# XCMate 0.1.29.21 – Serien-Autoplay (#85)

**Android: NOT_TESTED.** Eigener Branch `feat/xcmate-02921-autoplay`, Draft-PR auf main.

## Befund und Verhalten

.20 speichert Fortschritt über `media_progress.poll`, besitzt aber keinen Ended/Stopped-Vertrag. Ein bloßes `isPlayingVideo()==False` kann Abbruch, Fehler, Senderwechsel oder eine Startlücke bedeuten und autorisiert keinen Folgestart.

Die neue Kette wird ausschließlich bei einer bewusst aus XCMate gestarteten gültigen Episode aktiviert. Sie ist im neuen Featuremodus für diese Sitzung standardmäßig **Ein**. Es werden keine bestehenden Kodi-/Addon-Einstellungen umgeschrieben oder Defaults migriert. Die eigene XCMate-Leiste zeigt nur bei verifizierten Episoden den Schalter **Autoplay: Ein/Aus**; die Einstellung gilt für die laufende Kette. Ausschalten während eines vorgemerkten Wechsels verwirft diesen. Ein neuer bewusster Episodenstart beginnt eine neue Sitzung.

Ein langlebiger `xbmc.Player`-Observer im Service bindet beim `onAVStarted` die tatsächliche eigene InfoTag-Identität an Session-Nonce und Portal/Serie. `onPlayBackEnded`, `onPlayBackStopped` und `onPlayBackError` legen ausschließlich begrenzte Ereignisse in eine gesperrte Inbox. Keine GUI-Steuerung, SQLite, HTTP oder Wiedergabestarts in diesen Callbacks. Überlauf, fehlendes Endevent und verlorene Eigentümerschaft brechen konservativ ab.

Der Service-Owner verarbeitet die Zustände `IDLE → PLAYING → ENDED_PENDING → STARTING → PLAYING`, alternativ `CANCELLED/FINISHED`. Zwischen Ended und Start liegt eine eigene Dispatch-Runde für Stop-Priorität, kein Bestätigungsdialog und kein Pflicht-Countdown. AVStart bestätigt die nächste Episode; eine ausgestellte Startabsicht bedeutet noch keine laufende Wiedergabe. Resolver/AVStart werden begrenzt erwartet (20 s), dann kein Retry. Fehler/fehlende Quelle führen zu einer festen, datensparsamen Meldung.

Ein Root-ID-Marker bindet die ganze Kette, jede neue Episode erhält einen frischen Resolver-Intent/Nonce. Stop veröffentlicht die Root-Sperre **vor** Checkpoint/Playerstop. Der Resolver prüft seine aktuelle Absicht nach dem Quellenbau erneut, anschließend die Kettensperre vor `setResolvedUrl`. Fremde oder manuell ersetzte Wiedergabe hat Vorrang. Späte doppelte Endcallbacks dürfen ein bereits spielendes Folgeitem nicht erneut beenden; doppelte Terminalereignisse erzeugen höchstens eine Startabsicht. Ein begrenzter Verlauf verhindert Mehrfachstarts. Kodi-Shutdown schließt den Observer und alle vorgemerkten Absichten.

Die lokale Folgenliste wird auf einem eigenen Worker cache-only aus demselben aktiven Portal/Serienkontext gelesen. `media_sequence.records/successor` bleiben die gemeinsame kanonische Ordnung für manuelles Next und Autoplay. Nummernlücken und Staffelwechsel sind erlaubt; Specials, widersprüchliche IDs/Positionen, fremde Portal-/Serienangaben und Serienende werden nicht automatisch gestartet. Kein Wiederanfang bei Folge 1. Der Resolver validiert auch automatisch gewählte IDs erneut gegen den lokalen Seriencache; keinen beliebigen URL-Parameter übernehmen.

Beim gesicherten natürlichen Ende wird die letzte bekannte Dauer als End-Checkpoint über die vorhandene `media_state.save_progress`-Logik geschrieben, bevor die nächste Episode startet. Ein älterer Poll-Sample kann ihn nicht wieder überschreiben. Der bisherige Mindestwert von 60 Sekunden in der Fortschrittsdatenbank bleibt erhalten: sehr kurze Testclips eignen sich deshalb nicht für eine Resume-Abnahme. Stop speichert weiterhin die echte Position. Die Medienansicht übernimmt aktuelle Episode/Staffel und stellt nach Kettenende ihre vorhandenen Owner-/Fokuswege wieder her; natürliches Zwischenende führt nicht zum Abbruch durch `onInit`.

## Selektive Kompatibilitätsprüfung PR #84

PR #84 bleibt unverändert und wurde **nicht gemergt**. Referenz: `b178721b5d35145f9b562f0030da3ec81b550ca2`, Basis .11. Selektiv übernommen wurden ausschließlich `media_actions.py`, `media_osd.py`, die zugehörigen 33001–33015-Übersetzungen und die gezielte Titel-/lokale-Poster-Anreicherung. Neu angepasst: Episode-Autoplay-Aktion, Root-Abbruch auch in Wiedergabelücken, exakte Tokenprüfung vor Stop und Service-Einbindung in heutige .20. Die nativen Kodi-21.2-Bedingungen `Player.PauseEnabled` und `Player.SeekEnabled` bleiben bestehen; kein ungültiges JSON-RPC-`canpause`.

Die Leiste übernimmt Pause, begrenztes Seek, Audio-/Untertitelwahl und Video-/Toneinstellungen mit erneuter Besitzprüfung. OK öffnet; Back bei sichtbarer Leiste blendet sie aus; Back ohne Leiste beendet die eigene Wiedergabe und die Kette. In einem laufenden Übergang beendet Back/Stop die vorgemerkte Fortsetzung. Fremde Dialoge werden nicht verdrängt. Manueller Next-Button und bestehende .19-Fernbedienungswege bleiben erhalten. Live-Overlay, Guide-Handoff und Artwork-Queue sind bytegleich zur Basis.

## Nachweise und Grenzen

46 neue Hosttests: 29 Koordinator-/Resolver-/Worker-/SQLite-/Fensterfälle plus 17 native OSD-Fälle, darunter 20 Film-/Episoden-Stop-Zyklen. Folge 1 → 2 → 4 → Staffel 2/Folge 3, Serienende, späterer bewusster Start, doppelte/späte Callbacks, beide Stop/Ended-Reihenfolgen, Stop im Übergang und während Resolverbau, Timeout/Fehler, fremde Sitzung, Specials/Mehrdeutigkeit, Toggle, Shutdown, fehlendes Endevent, Inbox-Überlauf, Persistenz und Rückkehrfokus. Echte SQLite-Dateien, lokaler Cache und native API-Modelle; keine echten Decoder-/Provider-/Android-Tests.

Vollständige Ergebnisse und Ausgabe stehen in `TESTERGEBNISSE_02921.json` und `TESTLOG_02921.txt`. Ursprüngliche Freeze-Baselines wurden nicht ersetzt: die autorisierten Autoplay-Hooks werden vor dem bisherigen Hash-/AST-Vergleich exakt herausgerechnet. Bestehende Fortschrittsspeicherung, Live-Routen, Ownership und Worker-Grenzen bleiben geprüft. ZIP-CRC, sämtliche Source-Bytes, Pfade, AST und unabhängige Byte-Reproduktion werden geprüft. Python-3.11-Grammatikprüfung unter Host-Python 3.12 ersetzt keinen 3.11-/ARM32-Gerätelauf.

Android-Abnahme: `ANDROID_TEST_02921_DE.md`. Bekannte Restunsicherheit: reale Kodi-Callback-Reihenfolge, Stream-/Decoderfehler, Fokus in Titan BINGIE MOD/Estuary und Stop genau im AVStart-Übergang benötigen das Gerät. Kein Android-PASS aus Simulationen ableiten.

## Gemeinsamer Stand und Schutz

Basis ist `main` 0.1.29.20, Commit `b6407e750470c2b8dc250e1030ee0fceb147791e`.
Android-Test 48 der .20: **10 PASS, 0 FAIL, 1 NOT_TESTED**. Bestätigt sind die tatsächlich geprüften Grundpfade, nicht alle EPG-Oberflächenanforderungen.
Nachtrag des Nutzers: **Kein erreichbarer Artwork-Downloadpause-Button vorhanden. Test E ist nicht durchführbar (BLOCKED_UI / NOT_TESTED)**. Der boolesche Backend-Schalter in der nativen `resources/settings.xml` ersetzt keinen sichtbaren Zugang im eigenen XCMate-Menü. `home_menu.settings(storage)` bietet Status, Wiederholung, DB-Zustand und weitere Speicherpunkte, aber keinen Pause-Schalter. Fast alle Bilder sind bereits heruntergeladen; kein Nachladen, Löschen oder Reset für diesen Test erforderlich. Dieser Menü-Nachtrag wird separat geführt und nicht in einen fachfremden Test-PR gemischt.

**Aktueller Updatepfad ab 23.10.2026:** .21 ist nach #109 in main integriert. .22 wird kumulativ darauf aufgebaut und erhält dieses Autoplay vollständig. Die frühere getrennte .22-Testentwicklung ist überholt; direkt .21 → .22 aktualisieren, kein Downgrade/Deinstallieren. Neuer Gesamtbericht `KUMULATIV_02922_DE.md`, verbindlich `UPDATEPFAD_02921_02922_DE.md`. .22 bleibt Draft ohne Veröffentlichungsfreigabe.
