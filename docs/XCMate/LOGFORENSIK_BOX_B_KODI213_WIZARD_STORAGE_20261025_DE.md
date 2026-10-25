# XCMate – Testbox B: Kodi-21.3-Logforensik zu Wizard-Crash, Speicherwarnung und Gruppen-Nachimport

**Stand:** 25.10.2026. **Quelle ausschließlich die zwei PRIVAT eingereichten Logs** `kodi.old(20261025-132407).log` (870 Textzeilen, Ereignisse 13:30:20–13:55:42) und `kodi(20261025-132406).log` (1675 Textzeilen, Ereignisse 13:55:54–14:23:39). Logs/Originaltexte mit Hosts, URLs, Tokens, Portaladressen, SMB-Pfaden werden **nicht öffentlich hochgeladen**. Dieses Dokument enthält ausschließlich technische, anonymisierte Befunde.

## A. Tatsächliche Geräteangaben

- Kodi **21.3 Omega 32-bit ARM** mit Python 3.11.7, XCMate **0.1.29.35**, GS Media Repository 1.7.0.
- **Rockchip RK3528**, 4× ARMv7, GPU **Mali-450 MP / OpenGL ES 2.0**, 1920×1080@60Hz, Linux-Kernel 6.1.118, BINGIE MOD 2.2.3.
- Android-System meldet **`Android TV 16.0.0`, API-Level **34**. Die Angaben **widersprechen einander**: Android API34 entspricht Android **14**; echtes Android16 wäre API36. `Google_TV` Manufacturer/Brand/Model sind **generische Firmware-Kennungen**, kein verifizierter Marken-/Modellname. **Kodi 21.3 kompatibler Start ist beobachtet**, kein Android16-Kompatibilitätsbeweis.
- **Physischer RAM gesamt, Flash-Gesamtgröße, freier `/data`-Speicher in GiB sind in diesen Logs NICHT enthalten.** Die Kodi-Cache-Einstellung `Memory Size: 20 MB` ist **nur der Videopuffer**, nicht Hardware-RAM.
- Die **XCMate-STABILITY-Logger messen den gesamten Kodi-Prozess-RSS**, nicht physisch verfügbaren RAM oder XCMate-exklusive Belegung: Altes Log 25 Samples **240–354 MiB**, neues Log 26 Samples **209–405 MiB**, Median rund 253–256 MiB. Auf allen 51 Samples `pressure=false`, `portal_oom=0`, `portal_read_errors=0`. Kein belegtes OOM/Killer-Ereignis; der Speicherpeak allein schließt andere Android-Prozess-/Kernel-Kills nicht aus.
- **Streng überprüft:** In beiden Logs **0 Treffer** für `ENOSPC`, `No space left`, `errno 28`, `BUDGET_FULL`, `DISK_FULL`, `free space`/verwertbare tatsächliche Kapazitäten, `MemoryError`/OOM-Killer. **Speicher voll daher weder belegt NOCH widerlegt**; eine UI-Notification oder ein eigener Artwork-Hintergrundjob kann den Fehler ohne Kodi.log-Meldung zeigen.

## B. Exakte Abfolge Wizard/Speichern/Absturz

| Kodi-Logzeit | Nachweis |
| --- | --- |
| 13:35:53.271 | `[XCMate][BOOT] ROUTE action=setup_wizard` |
| 13:40:39.180 | Kodi lädt `XCMateSetup.xml` – native Wizard-Oberfläche, kein separates Preview-PR #162 |
| 13:55:38.306 | `[plugin.video.xtreammate] Portal added and verified` – erfolgreicher Konfigurations-Publish belegt |
| 13:55:41.210 | `[XCMate][BOOT] DISPATCH_DONE duration_ms=1187938.9` für Wizard (knapp **19m48s**, inklusive Benutzerinteraktion + Import; **keine** reine EPG-Downloadzeit) |
| 13:55:41.873 und 13:55:41.888 | Zwei neue fast parallele Kodi-Plugin-Invocations / BOOT ENTRY |
| 13:55:42.772 | eine Route erneut `action=setup_wizard` |
| 13:55:42.779 | gleichzeitig andere Route `action=portal_home`; `[ROUTE_STATE] ... modal=1` 13:55:42.837 |
| 13:55:42.837 | `kodi.old` endet **ABRUPT ohne normalen Exit, Python-Traceback, Signal oder Speicherfehler** |
| 13:55:54.389 | Neues `kodi.log` beginnt mit vollständigem Kodi-Start, etwa **11,55 s** nach letzter Zeile |

**Interpretation:** **Ungewöhnlicher simultaner Wizard-Reentry und Portal-Home-Handoff unmittelbar nach bereits verifiziertem Portal-Save**; spezifische, plausible Race-/Window-/Directory-/Modal-Lifecycle-Stelle für **P0 #165**. **Kein Root-Cause-Beweis** für Crash; für definitive Ursache zusätzlich Android `logcat` beim reproduzierbaren Save oder tombstone benötigt. Der neue Kodi-Start und der bereits gespeicherte Account passen zu einer **nach Commit liegenden** Instabilität; nicht behaupten, dass alle DB-Tables atomar/sicher veröffentlicht sind.

**Wichtig:** `Portal added and verified` ist ein positives Commit-Gate, aber es gibt keine einzelnen gemessenen `COPY_GUIDE`-/`COPY_CATALOG`-/`CLOSE`-Phasen oder Android-Crashcodes. Codex soll die Route `setup_wizard` nach Save **single-flight** absichern, Modal-Window schließen, nur einmal Portal-Home-Routing, und gesonderte veröffentlichte/indizierte Datenvalidität messen. Kein Reset/Downgrade.

## C. Verhalten nach dem Neustart

- 13:57:29–13:57:41: erster XCMate-Root-Aufruf nach Neustart **6,61 s DISPATCH**, allein `MAIN_IMPORT` 5,324 s und `HOME_MENU` 4,246 s; danach sind weitere XCMate-Warm-Root-Aufrufe teils um **1–1,5 s**. Eine frühe `GetDirectory`-Meldung bei 13:57:47 sollte unter Window-/Directory-Routing separat geprüft werden; diese Meldung stammt nicht automatisch vom Wizard-Save.
- 13:58:06–13:59:16: ein Plugin-Aufruf endet mit `Portal updated and verified` und braucht **69,609 s**. Das ist ein langsamer Portal-Verarbeitungs-/Einstellungsaufruf, **nicht** zwingend ein Katalog-Delta-Import.
- Ca. 13:59:25–13:59:41 Live-Start-Dispatch etwa **15,23 s**, danach tatsächliche Wiedergabe (User bestätigt Fernsehen). #120-Startlatenz gilt möglicherweise auch auf Box B.
- Zweimal `EXCEPTION: Kodi is not playing any media file` bei Player-/Stop-Wechseln, einzelne RK-MediaCodec-Sonderfälle; **keine** große Decoderfehlerflut, kein nachweisliches OOM. XCMate-Navigation funktioniert grundsätzlich.
- Alte und neue Logs sind durch Restart getrennt; Build XCMate regulär .35, **NICHT** Wizard-Test-PR #162.

## D. Nachträgliche Gruppen-Aktivierung

Nutzer bestätigt: nachträglich ausgewählte Live-Gruppe gespeichert, aber zeigt „keine aktiven Sender“. Aktuelle Logs zeigen **keinen aussagekräftigen `catalog_sync.request`-/`group-index-success`-Beleg**. Die schon zuvor statisch geprüfte `group_selection.choose_groups.commit()` ruft `catalog_sync.request` nach Save **nur für `m3u`/`stb`**, nicht für Xtream; als Codefehlerkandidat **#166** isolieren. Falls Nutzerportal `xtream`, zuerst *Delta der neuen aktivierten Gruppen → persistenter gruppenspezifischer Sync* triggern; danach PENDING/INDEXING/READY/EMPTY_SOURCE statt irreführendem „0“. Keine frische Portal-Neuanlage.

## E. „Speicher voll“ – zwei unterschiedliche Diagnosen verpflichtend

**Kein im Log gesichertes volles Flash-Laufwerk, keine verfügbare Gesamtspeicherzahl.** XCMate besitzt u. a. echte `disk_usage`-Preflight-Prüfung plus getrenntes Artwork-`BUDGET_FULL` und `DISK_FULL`. Eine Toast-Notification kann auftreten, ohne derzeit im Kodi.info-Log zu erscheinen. Codex soll **nur Metriken, keine Geheimnisse**, im Diagnose-Dialog und Debug-Log ausgeben:

- `storage_path` (generisch z. B. Kodi Profile/Artwork/Staging, **nicht** private Portal-URL), `total_bytes/free_bytes` aus tatsächlich beschreibbarem Kodi-`/data`-Filesystem, `expected_write_bytes`, `artwork_budget_bytes/used_bytes/reserved_bytes`.
- `storage_result` explizit `OK | BUDGET_FULL | DISK_FULL | PERMISSION_DENIED | SQLITE_BUSY | UNKNOWN`, zuerst einmalig deduplizieren, kein Toast-Spam, nie physische Reserve blind abschalten.
- RAM physisch via `/proc/meminfo` oder Android-Systemwerkzeug, Runtime via `getprop`, CPU ABI und korrekte Android API-Version; Diagnose bezieht sich auf das Geräteprofil, nicht Internet-Marketingdaten.
- **Zur externen Bestätigung ohne Reset**: Android **Einstellungen → Geräteeinstellungen/System → Speicher**, Screenshot `Gesamt/Verfügbar`; sofern ADB verbunden: `adb shell df -h /data /storage/emulated/0`, `adb shell cat /proc/meminfo`, `adb shell getprop ro.build.version.sdk`, `adb shell getprop ro.product.model`. Die angezeigte /data-Partitionsgröße muss nicht identisch mit aufgedrucktem gesamten Flash sein.

## F. Andere Kodi-/Skin-/Repo-Hinweise (separat)

`repository.bingie` meldet wiederholt **altes Repository-Schema** und fehlende Kodi21.3-Definition; das ist **nicht automatisch** `skin.titan.bingie.mod` selbst. Andere alte HTTP-Repos/404s und xVAULT Provider-DNS-Timeouts sowie gelegentliche `ListItem.setInfo`-Deprecation. Keine Beweise für den XCMate-Wizard-Crash, aber bei Kodi-21.3-Kompatibilität/Upgrades separat im Auge behalten. Auf einer neuen Testbox mit **Estuary** gegenprüfen, ohne Produktivbox oder alte Skin-Konfiguration zu löschen.

## G. Issues/Version und sichere Folgearbeiten

- **#165 P0 Save-/Close-/Home-Crash:** duale Wizard/Home-Routen bei 13:55:42 als Primärrepro; Android-logcat/tombstones; before-/after-save-Konsistenz; SingleFlight statt Doppel-Dispatch.
- **#166 P1 neue Xtream-Gruppe ohne Katalogimport:** fehlende Xtream-Sync-Anforderung als plausibler statischer Befund, Local-Queue/Worker-Protokollierung.
- **#164 P1 fehlender Fortschritt:** 1/4→2/4 ohne Activity, vor Schluss kein sichtbarer Fortschrittsbalken.
- **#90/#91 Speicher:** physischer Datenträger/Artwork-Budget/Reserve/SQLite strikt trennen, nicht „voll“ behaupten ohne Zahlen.
- **#43 Wizard:** beim Save/Reentry/Logo/Hintergrund/Kodi21.3 auf Testbox B im kumulativen nächsten Wizard-Release sicher machen.
- **#143 Master-Tracker**: echte Logs nun überprüft, keine privaten Kodi-Rohlogs GitHub-hochladen.
- [Verbindliche Versions-Roadmap](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md) behält nach aktueller `.36` den `.37`-Wizard inkl. Vorversionsreparaturen bei, kein unautorisierter Merge/Release.

**Kernurteil:** Echte Fehlermeldung über volle Speicherkapazität **nicht nachgewiesen**; Gerätetyp **Rockchip RK3528 (4-core ARMv7/Mali450)** statt identifizierbarer Google-Hersteller-Box; Android16/API34-Widerspruch. Wizard-Speicher-Crash korreliert mit **doppeltem Kodi-Plugin-Handoff nach bestätigtem Portal-Save**, aber ohne Android-Absturztrace ist die Ursache noch offen. Keine Datenlöschung als Debuggingmethode.
