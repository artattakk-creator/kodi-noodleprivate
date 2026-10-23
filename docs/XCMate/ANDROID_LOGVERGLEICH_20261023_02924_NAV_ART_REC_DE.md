# XCMate – Android-Logvergleich und verbindliche Prioritäten (23.10.2026)

**Quellen:** vom Nutzer privat übermittelte `kodi.old(2).log` (09:01–11:22, 9527 Zeilen) und `kodi(6).log` (11:22–13:54, 11451 Zeilen) auf Android TV 13 / RockChip RK3528 / ARM 32-bit, Kodi 21.2 Omega, Titan BINGIE MOD 2.2.3. **Die Original-Logs werden absichtlich nicht ins öffentliche GitHub-Repository hochgeladen**, da Logs Portal-/Sitzungs-IDs, Drittanbieter-URLs und andere potenziell vertrauliche Angaben enthalten können. Line-Referenzen sind aus den vom Nutzer hochgeladenen Originalen, nicht aus einer Datei in diesem Repo.

## Korrigierter Nutzerbefund (spätere Nachricht hat Vorrang)

- **Lightweight-Rückwechsel funktioniert doch**; zuvor gemeldeter Blocker **zurückgezogen / PASS**. Der Codepfad soll gegen verzögerte Aktivierung und Wiederanwendung nach Wiedergabe/Neustart regressionsgeprüft werden, ist aber **kein bestätigter P0-Funktionsausfall mehr**.
- **Space Premium**: Medien-/Seriencover und Datei-/Ordnerfenster lassen sich mit D-Pad scheinbar akustisch bedienen, aber der Fokus ist **nicht sichtbar**. In Film-/Seriendetails öffnet OK wiederholt **Suche**, nicht die gewünschte Aktion. Diese beiden UI-Probleme bleiben **P0**, unabhängig davon, ob die Designwahl zurück zum Core funktioniert.
- **Poster:** Fehler „Netzwerkfehler“ weiterhin gemeldet; gezielter Aktualisierungsversuch ohne Erfolg. Backend- und UI-Fehler getrennt bewerten.
- Nutzer beauftragt Codex zuerst mit Bedienungsfix, **optional zusätzlich einem kleinen nativen Direct-MPEG-TS-Aufnahmeprototyp**, sofern ohne Release-/Android-Regression sicher möglich.

## Versionsfenster (kodi.log-Ausgabe, nicht exakt Beginn jeder Codeausführung)

- `kodi.old(2).log`: Startup 09:01 `0.1.29.20` (L94); um 10:01 `.21` (L3193); um 11:01 `.22` (L8267).
- `kodi(6).log`: Startup 11:22 `.22` (L94); um 13:04 `.23` (L6500); um 13:22 `.24` (L8255). Dateien enden gegen 11:22 bzw. 13:54.
- Kodi meldet `FFmpeg version/source: 6.0.1-Kodi` beim Startup (beide Logs, L6) und installiertes `inputstream.ffmpegdirect`. **Das bedeutet einen intern von Kodi genutzten Decoder/Libav-Stack, nicht den Nachweis eines über `subprocess.Popen(['ffmpeg',...])` startbaren CLI-Recorders.**

## Quantitative Kodi-/XCMate-Befunde

| Phänomen | `kodi.old(2).log` | `kodi(6).log` | Interpretation |
|---|---:|---:|---|
| `XCMate artwork db: code=BUSY phase=QUERY sqlite=5` | **126** | **166** | Wiederkehrende `SQLITE_BUSY`-Abfragen; Log-Zeilen sind **nicht** zwingend getrennte Ausfälle von Artwork-Jobs. |
| `[XCMate][NAV] event=FOCUS_FALLBACK` | **7** (alle im .21-Abschnitt) | **26** (1 in .22, 9 in .23, **16 in .24**) | **16 nach .24**, sämtlich `mode=detail`, `window=13004`, Zeitraum ca. **13:39:26–13:41:10** (neuer Log L9807–L9974). Starker zeitlicher Zusammenhang mit dem realen Detail-/OK-Problem, **kein bereits bewiesener Root Cause**. |
| `Control ... has been asked to focus, but it can't` | 0 | **4** | Neuer Log L997, L1442, L6559, L6672: **vor .24** in .22/.23-Abschnitten, z. B. Control 312 Window 13001/13002, Control 9 Window 10146. Nicht fälschlich .24 allein zuschreiben. |
| XCMate `GetDirectory`-Fehler | 0 | **2** | Neuer Log L5734 = **12:58:16 unter .22**, L10036 = **13:41:37 unter .24**. Letzterer nach den Fokus-Fallbacks, aber Home-Dispatch meldete bereits DONE. Ursache gesondert ermitteln. |
| XCMate `service.py` „script didn't stop in 5 seconds“ | **2** | **1** (unter .22/.23-Update) | Alter Log L8244/L8952, neuer L6490; Update-/Stop-Lifecycle und Worker-Stop bei Kodi-Versionstausch absichern. Alter Log L8239 zusätzlich `Unknown addon id` während Update; alter Log L8957–L8969 `threading._shutdown`/`SystemExit`. |
| Pixel-/MediaCodec-Buffer-Warnings | vorhanden | vorhanden | Kein kausaler Beleg, dass dies Premium-Fokus verursacht. Beobachten, ohne fremde Player-/Decoder-Settings umzuschreiben. |

**Artwork BUSY nach Version im neueren Log:** .22 **103** Ereignisse, .23 **14**, .24 **50**. Wegen unterschiedlich langer Laufzeit keine belastbare Aussage über unterschiedliche *Raten* oder die Ursache eines bestimmten Posters.

**Quellcodebefund auf `main`, Stand 0.1.29.24:**
- `resources/lib/artwork_db.py::image_states()/image_details()` benutzen read-only `sqlite3.connect(..., timeout=.025)` und `status` circa 25ms, `connect()` circa 50ms; `image_states` klassifiziert Lock als `DB_BUSY`. Bei Contention können kurze Timeouts zu wiederholter Nichtverfügbarkeit führen. **Nicht blind längere Timeouts im GUI-Thread einführen**; Thread-Besitz, `BEGIN IMMEDIATE`, Transaktionsdauer, SQLite-WAL, Scheduling und gezielte bounded retries messen/überarbeiten.
- `theme_render.py::apply_xml()` ersetzt Media-Fokusgrafiken und fügt Dekoration in `itemlayout/focusedlayout` ein; `appearance.py::window_source()` generiert WindowXML mit Theme-Textur-/Alpha-Änderungen.
- `media_window.py`: `setFocusId` und `_valid_focus` können auf zulässige Controls zurückfallen; `onClick(400)` löst ausdrücklich Suche aus; `_show('detail')`, `_detail_ready()` sowie asynchrone Metadatenverarbeitung müssen echte Aktion `300` stabil fokussieren, nicht Suche `400`. **Bei .24-Premium wichtig:** `FOCUS_FALLBACK` im `detail`-Modus, aber aus den bisherigen Logzeilen lässt sich der konkret beabsichtigte Zielcontrol noch nicht ablesen. Darum gezielte datensparsame Instrumentierung.
- `recordings.py` ist nach wie vor ein alter externer FFmpeg-`subprocess`-Recorder; `guide_timers.py` stellt nur persistente Erinnerungen bereit und startet **keine** native Aufnahme.
- Kodi meldet `recording folder:` leer beim Startup; dies ist die **Kodi-eigene Startkonfiguration**, **kein Beweis**, dass der XCMate-Aufnahmeordner leer/falsch ist.
- Externe Kodi-Repositories `repository.bingie` (altes Repository-Schema), `repository.xvault` (HTTP-Downloads) und weitere werfen massenhaft Fehler/Warnungen; **nicht ohne Belege als Ursache für XCMate-Poster oder Fokus interpretieren**, keine eigenmächtigen Änderungen an fremden Add-ons.

## Verbindliche Arbeitsreihenfolge für Codex

**Gate P0:** Space-Premium-Navigation in Filme, Serien, Gruppen/Kacheln, Details, Staffel/Episode und Dateien/Ordnern sichtbar und IR-funktional machen; Klick auf gewählte Detailaktion arbeitet, Suche nur bei echter expliziter Suchauswahl. Vergleich Lightweight als Referenz und Premium als Differenzialtest. **Lightweight-Wechsel ist bereits vom Nutzer gelungen** – sichern, nicht als defekt deklarieren. Core-Fokustexturen notfalls im Premium erhalten. Sicherer Back/Fokus nach async Updates und Playback-Rückkehr. Eigene Kodifokus-Probes, keine globalen Keymap-/Skin-Modifikationen.

**Gate P1:** DB-BUSY und Art-Errorflow verbessern: kontrastreiche navigierbare UI bei Netzwerk-/DB-Fail; P1 #111/#41/#90. Keine Hostlogs mit URLs/Portalkennungen oder globaler Artwork-Cache-Löschung; diagnostiziere echten Bildstatus und einen Einzelretry, verwende eigene Logcodes `NETWORK_ERROR`, `DB_BUSY`, `HTTP_*...` getrennt.

**Gate P2 (optional in gesonderten Commit):** Native Direct-TS-Eignung und minimale 2–5-Minuten-Testaufnahme für DRM-freie und berechtigt aufzeichenbare echte MPEG-TS-HTTP(S)-Streams, keine FFmpeg-Binary oder separate App. Bei HLS/DASH/Eingangs-HTML explizit `UNSUPPORTED_FORMAT` statt Fake-`.ts`. Parallelstream-Beschränkung, Write-Probe, Raum/Kapazität, `.ts.part`→Finalisierung, Kodi-Wiedergabe, Fehler-/Stop-Handling. Der EPG-Timer mit Vorabmeldung/optionaler Umschaltung und `Meine Medien` sind geplant unter #62/#113, **nicht** durch bloßes TS-Prototyping als fertig melden. Falls P2 die P0-Freigabe gefährdet, TS als separaten Draft-PR zurückstellen.

**Abnahme-/Release-Guard:** XCMate Original-Icon PASS; EPG E01–E10 weiterhin PASS; Live/IR/Player-Baseline erhalten; Datenbank-/Portal-/Favoriten-/Resume- und Artwork-Bestand unangetastet; Standard-↔-Premium-Wechsel und Neustart; Android-Gerätefokus zuletzt durch Nutzer testen. Nutzer hatte Merge-/Publish-Wunsch für einen **validierten** Hotfix, niemals unfertige Änderungen mergen oder Gerätetest behaupten. Keine Änderung an Noodle Private. 

**Zugeordnete Issues:** [#115](https://github.com/artattakk-creator/kodi-noodleprivate/issues/115), [#111](https://github.com/artattakk-creator/kodi-noodleprivate/issues/111), [#41](https://github.com/artattakk-creator/kodi-noodleprivate/issues/41), [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90), [#62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62), [#113](https://github.com/artattakk-creator/kodi-noodleprivate/issues/113).
