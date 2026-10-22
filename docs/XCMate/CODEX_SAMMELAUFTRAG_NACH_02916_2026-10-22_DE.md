# XCMate – gebündelter Codex-Korrekturauftrag nach Android-Abnahme 0.1.29.16

**Verbindlicher Nutzerauftrag 22.10.2026:** Die vollständigen Android-Ergebnisse als PASS/FAIL/NOT_TESTED auf GitHub erfassen und einen **priorisierten gemeinsamen Änderungsvorschlag** für den nächsten Teststand ausarbeiten. **Keine automatische Integration, kein Merge, kein reguläres OTA/Release ohne neue ausdrückliche Freigabe.**

## 0. Rahmen, Basis, Ausgangslage

- Repository: https://github.com/artattakk-creator/kodi-noodleprivate
- Aktuelles produktives main: **XCMate 0.1.29.16** (PR #96 zuvor freigegeben und gemergt); Add-on-ID: plugin.video.xtreammate.
- Ziel: **nächster freier 0.1.29.x-Testkandidat** (voraussichtlich 0.1.29.17, zuvor Versions-/PR-Kollisionen prüfen). Neuen Feature-/Fix-Branch von **aktuellem main** erstellen, nicht auf historische Branches .11/.13/.14/.15 bauen.
- Prüfgerät: Android 13 / RK3528 ARM32 / Kodi 21.2 Omega / Titan BINGIE MOD 2.2.3, IR-Fernbedienung; möglichst zusätzlich Estuary.
- Bestehende validierte Teile bewahren: Live-TV-Startsender mit Bild/Ton, OK-Infoleiste + EPG, Links→Mini-EPG, Film-/Serienfenster/Back, großer horizontaler Guide, Zeitnavigation inzwischen über 14 Uhr, Diagnosefenster erreichbar, bestehende Hosttests.
- **Realer Testbericht:** [ANDROID_ABNAHME_02916_2026-10-22_DE.md](ANDROID_ABNAHME_02916_2026-10-22_DE.md), dort exakte Pass-/Teilfail-Abgrenzung. **602 PR-CI/Hosttests PASS ≠ Android-Gesamtabnahme.** Keine Logs/URLs mit Zugangsdaten publizieren.

## 1. P0 – Live-TV explizit beenden, kein automatischer Startsender-Loop (#97)

**IST auf realer Android-Box:** Hauptmenü → Startsender: PASS; Infoleiste inkl. EPG und Mini-EPG: PASS. Danach untere Info-/Steuerleiste → **Stop**: schwarzer Kodi-Ladebildschirm mit rotem Balken/drei Punkten, ursprünglicher Sender startet **ungefragt erneut** und Infoleiste öffnet sich. Erneutes normales Verlassen nicht möglich; **zweimal Back** verlässt Kodi komplett. **Das letzte Ereignis ist nicht als nativer Absturz erwiesen** (Android/Kodi-Exit vs Crash anhand Logcat prüfen).

**SOLL:** STOP/Verlassen setzt einen eindeutigen expliziten Exit-Intent, stoppt nur die eigene Wiedergabe, schließt eigenes Overlay/Sitzung konsistent und führt zur **XCMate-Hauptübersicht** ohne automatischen Neu-Start, ohne versteckte Audioausgabe und ohne Kodi zu beenden. Back-Hierarchie im Live-Betrieb bleibt kontrolliert; fremde Player nie stoppen.

**Code prüfen:** 
- src/plugin.video.xtreammate/resources/lib/live_overlay.py: _execute('controls',index==3), STOP-Key, long_back, LiveNavigator.close(), SESSION_KEY/Nonce.
- src/plugin.video.xtreammate/service.py: IPTVMasterService.run, Playback-Gap / pending_live_start, start_if_eligible, LiveSession/Overlay-Recovery, automatische Popup-Wiederherstellung.
- src/plugin.video.xtreammate/resources/lib/playback_exit.py: identity(), stop_owned(), poll(), Fullscreen-Exit/Media-Checkpoint.
- app_routes.py home_start; vorhandene Router-/Player-Startpfade und Kodi GUI-/Container-Navigation, mögliche Playlist-Wiederholung.
- XCMate-spezifische Action-/Session-Zustandsmaschine und Android-Back-Mapping.

**Vorgehen:** Sicheren, anonymen Eventtrace mit StopRequested/StopDone, Kodi.Player.isPlaying, Session-PID/SID nur gehasht, Owner/Nonce, DispatcherRoute, WindowID, Back/Stop-Action und Startgrund bauen, um **den realen erneuten Startaufruf** zu finden. Nicht behaupten, der Service starte neu, nur weil er Overlays wiederherstellt. Explizites STOP muss idempotent und ggf. als cancel marker über native Playback-Stop-Events/Service-Ticks bis zur bestätigten Terminierung bestehen. Richtige Rückroute erst nach dem Owner-Exit; nicht während offener WindowDialog-Callbacks neue Wiedergabe anstoßen. Abbruch/Recovery nach Senderwechsel, Live-Sessionwechsel, Offline und Kodi-Neustart abdecken. Keine globalen Keymap-Änderungen.

**Abnahme:** 1 normaler Start, 1 Stop→XCMate-Home, danach mindestens 10 Stop-/Back-Zyklen, mehrere Sender/Groups und Doppeldruck, ohne Replay/Audio/Player-Ownership-Leck/Kodi-Exit. Bei erneutem Prozessende Android-Gerätetest sofort stoppen; Logs **privat bereinigen**, keine Crash-Schleife. Kein Rewrite von Film-/Serien-Resume.

## 2. P0-Folgegate – EPG→„Jetzt Sender ansehen“ (#89)

Version .16 hat den nativen Window-Owner/Playback-Handoff aus PR #96 geändert, aber **dieser Weg wurde auf Android noch NICHT getestet**, weil STOP/Exit bereits scheitert. **Nicht als repariert melden.**

Nach Erfolg von Abschnitt 1 einen einzigen kontrollierten Start des **vorher über Live-TV bestätigten guten Senders** aus großem EPG→OK→„Jetzt Sender ansehen“ prüfen. Erwartet: genau ein Start über denselben bewährten Resolver, Kodi bleibt offen, Enden funktioniert. Danach 5 Wiederholungen, falls einzeln stabil. Bei erneutem Crash sofort Abbruch + Diagnose statt Schleife. Den bestehenden PR-96-Handoff **nicht vorsorglich erneut umbauen**; erst Fehlerbeleg oder Android-Ergebnis abwarten.

## 3. P1 – Guide-Fokus: Beschriftung lesbar; praxisnaher Header-Shortcut (#92, #57)

**IST:** Im horizontalen Guide verschwindet die Beschriftung des fokussierten Sendungsblocks. Header „Jetzt“/„20:15“ erfordert unrealistisches Hochscrollen durch zahlreiche Sender; der Nutzer lehnt das explizit ab.

**SOLL:** Jeder fokussierte Titel ist kontrastreich lesbar bei normaler/Neon-/Space-Premium-Fokusdarstellung; Fokus ist eindeutig, aber überschreibt keine Textlabels. Kodi-XML-Button Normal-/FocusedTextColor, Texturtransparenz, Z-Reihenfolge, BINGIE-Skin-Override und 720p/1080p prüfen. Der aktuell ausgewählte Titel sollte zusätzlich persistent im Footer/Lesezeile erscheinen, wenn Programmblock schmal ist.

**Direkter Shortcut:** Nutzer nennt **blaue Farbtaste** als bevorzugtes Beispiel, alternativ eine sinnvoll belegbare Taste oder sauber entprellter Doppeldruck. Empfohlen: konfigurierbares **Blau → Jetzt** oder **Blau → Header fokussieren** (UX klar definieren), nur bei aktivem XCMate-GuideWindow; nicht im Live-TV-Player fremde Tasten belegen. Mit kurzer Buttonhilfe / Footer anzeigen; bei Fernbedienungen ohne Farbtasten Fallback im OK-/Kontextmenü („Jetzt“, „20:15“, „Tag wählen“) oder eigener kurzer Zugriff. Kein Hochscrollen von 2.764 Sendern nötig. Native IR-Key-Codes und Bridge-Eventdedupe testen. Deaktivierte oder fremd belegte Farbtasten respektieren.

## 4. P1 – Links/Rechts **Sendungsblock → Sendungsblock**, Zeitachse bleibt frei (#93)

**Fakten:** Nutzer bestätigt unter 0.1.29.16 den Fortschritt **über 14:00** als PASS. PR #96 korrigierte den Cursor bei überlappenden Events; diese Verbesserung **nicht zurückbauen**.

**Wunsch:** Links/Rechts markiert standardmäßig das unmittelbar vorherige/nächste tatsächliche **Programm** des fokussierten Senders, nicht eine Serie freier 30-min-Schritte. Programmstart/-ende/Highlights dabei synchron. Falls kein Event im aktuellen 3h-Viewport vorhanden, asynchron und begrenzt im vorhandenen lokal gespeicherten Guide nach nächstem Event suchen; bei echten EPG-Lücken kontrollierten Fallback auf Zeitblättern anbieten. Überlappungen, identische Starts und Ereignisse über Mitternacht/DST müssen gerichtet, monoton und dedupliziert bleiben. Die sichtbare Zeitleiste nicht je Sender versetzen, Zeitsprünge transparent kennzeichnen. Keine SQLite-Abfragen/HTTP im Kodi-Key-Callback. Regressionstest speziell 12–15 Uhr langes Event plus kürzere 13/14-Uhr-Events.

## 5. P1 – Langzeitdiagnose zeigt nur Striche: Status **erklären** (#93, #60)

**IST:** Der neue Dialog „Senderdiagnose: Langzeit-EPG“ ist erreichbar und lesbar **PASS**, aber für den vom Nutzer markierten Sender lauten **First=—, Last=—, Days leer**. Dies beweist **nicht**, dass die zwei global READY XMLTV-Quellen keine Zukunftsdaten enthalten. Diagnose-/Alias-/Sender-Mapping- oder tatsächlich fehlende Programme sind zu unterscheiden.

**Code:** src/plugin.video.xtreammate/resources/lib/guide_grid_diagnostics.py: inspect(), List der IDs aus stream SID, provider_epg_channel_id und manuellem Mapping; lokal sqlite URI mode=ro, guide_alias, programmes, Timeout/Deadline, source status. Gegen exakt den **gleichen finalen kanonischen CID**, den guide_grid_data.page()/Guide-Viewport nutzt, abgleichen; prüfen, ob Alias-Kandidat vorhanden, SELECT 0 Zeilen, Quelle nicht im Cache, SQL_BUSY/Timeout oder SHORT_EPG_ONLY. Klare Anzeigen z. B. LONG_DATA_FOUND, NO_ALIAS_MATCH, NO_PROGRAMMES_FOR_CHANNEL, SHORT_EPG_ONLY, DB_BUSY, QUERY_FAILED mit ggf. empfohlenem manuellen Matching aus Kontext. Niemals unbekannte Coverage als leere Quelle präsentieren. Kein Credential-Logging, kein SQL-Write/Netzwerkimport im GUI.

**Abnahme:** Kontrollsender A mit mehrtägigem XMLTV, B ausschließlich SHORT_EPG, C mit ungültiger EPG-ID, D ohne Events, E DB-BUSY. Read-only SQL-/Datei-Bytegleichheit, Tagverteilungen, last stop, Quelle und getrennte Anzeige der Kurz-EPG-Daten.

## 6. P1 – Guide-Gruppenstart, Startsender-Fokus, Logos (#88, #90)

**IST:** Test 6 FAIL: alle Sendergruppen vermischt, Logos im neuen EPG fehlen. **Verbindliches Soll gemäß späterer Nutzerpräzisierung:** **nicht zuerst Gruppenliste**. Stattdessen EPG direkt mit dem horizontalen Raster der gespeicherten Startsendergruppe **und dem konfigurierten Startsender sichtbar fokussiert**, ohne die bestehende Reihenfolge umzuschreiben. **Links** aus Guide öffnet aktivierte Sendergruppen als echte Navigations-/Overlayebene, OK auf Gruppe → nur deren Sender/EPG. Back sauber gruppenbezogen, danach XCMate Home; Zeitachse und Fokus behalten, keine unbeabsichtigte Wiedergabe. EPG-Fernbedienungs-Links konfliktfrei mit der neuen Blocknavigation gestalten: **Links an definierter Sender-/linken Rasterkante oder eigener dedizierter Gruppenaktion** öffnet Gruppen; normale Links innerhalb Sendungsblöcken bedeutet vorheriges Programm. UI-Zustände und Key-Repeats testen.

Logos: Provider stream_icon/Reader-Payload, Priorität sichtbare Kanäle, lokaler media_art-Pfad, Bitmap/Fallback und Kodi-Texture-Control prüfen. 512-MiB-Artwork-Grenze ist plausibler Mitverursacher, **nicht bewiesene alleinige Ursache**; siehe Abschnitt 8.

## 7. P1 – EPG-Details ausbauen, „Plot“ ersetzen, echte Bilder (#88, #60)

**IST:** OK→Details öffnet und zeigt wenigstens Kurzbeschreibung **Teil-PASS**. Textviewer-Titel nur „Plot“, keine Bilder/Fanart, UI nicht zufriedenstellend.

**SOLL:** XCMate-eigene, hochwertige Kodi-Dialogansicht mit korrekt sichtbarem Sendungstitel, Senderlogo, Datum/Uhrzeit/Dauer, verfügbarer ausführlicher Beschreibung, Staffel/Folge/Genre und **passenden** Sendungs-/Episodenbildern. Bestehendes KurzEPG, XMLTV und gesicherte lokale Metadaten nutzen. Externe Ergänzung nur bei hinreichend sicherem Titel-/Staffel-/Folgen-Matching; keine irreführende fremde Grafik. Bei fehlenden Bildern Platzhalter und „keine Zusatzdaten“ statt behaupteter Einträge. Fokus/Back/IR-Funktion, spätere Integration mit Space Premium, Cache-Limits und Quellenberechtigungen berücksichtigen.

Zudem bleibt „EPG zuordnen/ändern“ direkt aus dem markierten Sender-Kontext nötig: aus gespeicherten XMLTV-Kanal-IDs auswählen, Vorschau, explizit bestätigen, persistieren/entfernen, nur betroffenen Bereich aktualisieren; kein automatisches Falschmapping und keine Gesamtimporte aus dem UI.

## 8. P1 dringend – Artwork 512 MiB entsperren und SQLite-/Queue-Engpässe lösen (#90, #91)

**Nutzerwunsch:** Alle **künstlichen** Sperren entfernen. Vorheriger Status: ca. 514/512 MiB Artwork, sehr viele SPACE_FULL-Jobs bei erheblichem physisch freiem Speicher. Bestehende .16 behebt weder 512-MiB-Default noch 4096-MiB-Clamp, versäumte Queue-Jobs oder SQLite-BUSY-Politik.

**SOLL:** Konfigurierbar „kein festes Artwork-Sammlungsbudget“ bzw. frei wählbare hohe Grenze, **echte physische Freiraumreserve** und sichere Datei-/Pixelgrößen/Concurrency weiterhin erzwingen. Vorhandene READY-Bilder unangetastet; bereits wegen künstlichen Budgets mit attempts>=3 blockierte SPACE_FULL-Jobs einmalig, kontrolliert und priorisiert (sichtbare Senderlogos zuerst) reaktivieren. Physisches DISK_FULL diagnostisch abtrennen von künstlichem BUDGET_FULL. Keine Massendownloads oder Datenbanklöschung.

**SQLite:** Keine Schutzlocks deaktivieren, **WAL/Transaktionen/ACID und Integritätsprüfung erhalten**. Stattdessen 50-ms-Gate-/SQLite-Wartezeiten, mehrsekündiges globales BUSY retry_after, Writer-/Reader-Konflikte, Katalog-Initialisierung und GUI-Snapshot-Deadlines differenziert überprüfen; moderate bounded retry/backoff, kurze Transaktionen, UI bei temporären Sperren nicht einfrieren. Keine pauschalen retries bei CORRUPT, READONLY, IO_ERROR. Maßnahmen aus bestehendem [CODEX_AUFTRAG_BREMSEN_ABBAU_2026-10-22_DE.md](CODEX_AUFTRAG_BREMSEN_ABBAU_2026-10-22_DE.md) einbeziehen. Hohe Jobmenge, 2.764 Live-Kanäle, Media-Import, Resume und TV-Live-Test unter RAM-/Disk-Druck prüfen.

Wenn dieser Abschnitt den P0-Fix verkompliziert, **als klar abhängige zweite Draft-PR** vorbereiten, statt ungeprüft in instabilen Player-Hotfix zu mischen. Der Nutzer wünscht dringend die spätere Aufhebung; nicht aus dem Projektplan streichen.

## 9. P2 – ältere Guide-Dubletten und neue Live-TV-Navigation

**#58:** Test 8 aktueller alter Programmführer **PASS**, aber unter .13 war \`SAT.1 HEVC\` mit „Richter Alexander Hold“ als zwei gleichzeitig aktive, nahezu vollständig überlappende Events fotografiert. .16 änderte die Dedup-Logik nicht. Echten alten Rohdatenfall in Testfixture reproduzieren, Sekundentoleranz und Alias/Quell-Priorisierung nur kanalbezogen korrigieren; legitime Wiederholungen/Regionalvarianten erhalten. #58 bis deterministischem Nachweis offen.

**#94 (nicht in .16 implementiert):** Live-TV-Links-Hierarchie: 1 Sender/Mini-EPG, 2 Gruppen, 3 vertikale schmale Icon-Leiste, 4 Icon-Leiste mit Text (Suchen, Favoriten, Live-TV, Filme, Serien, Einstellungen, Verlassen), 5 vollständiges Schließen aller Overlays bei weiterlaufendem TV. Menüpunkt „Verlassen“ führt zur XCMate-Hauptübersicht. **Erst nach korrigierter Stop-/Exit- und bestehender Live-Overlay-Navigation integrieren.**

**#95 (nicht in .16 implementiert):** Rechts auf im Mini-EPG **markiertem** Sender zeigt dessen Jetzt-/Danach-/zukünftige Sendungen, **nicht** zwingend des aktuell abgespielten Senders, ohne Auto-Tune; Back/Links zum identischen Fokus. Quellenhorizont ist feedabhängig.

Diese beiden Features gehören verbindlich zum **weiteren** Fahrplan. Wenn ihr Umfang sichere Android-Abnahme der ersten Fixwelle gefährdet, separat dokumentierte Draft-PRs mit klarer Integrationsreihenfolge liefern.

## 10. Entwicklungs-/Releasegate, technische Akzeptanz

1. **Keine Änderung am produktiven Stand durch diesen Auftrag.** Codex darf branchbasiert Änderungen, neue Tests, dokumentierte Diagnose und **Draft-PR(s)** erstellen, **nicht** nach main mergen, kein OTA-/Repository-Index-Update und keine bestehenden Benutzerdateien löschen/migrieren.
2. **P0 Stop/Exit zuerst** und als kleinsten verlässlich beurteilbaren Fix herausstellen. Danach lesbare und risikoarme EPG-Korrekturen modular testen. Mehrere Commitgruppen / PRs statt eines unüberschaubaren Big-Bang-Releases, aber ein **konsolidierter Integrationsplan** mit Testkandidaten und klaren Abhängigkeiten.
3. Auch bei vollständigen automatisierten Tests immer **Android=NOT_RUN**, bis Nutzer exakt diese Test-ZIP auf dem RK3528-Gerät bestätigt. Keine erfundenen PASS-Zahlen. Bestehende Tests zu .16 und .11 nicht nur auf neue Mock-Annahmen trimmen.
4. Tests für Kodi-Owner-/Service-/Player-Callbacks, Sessionmarker, UI-Thread-Reentrancy, Blue-Key/Doppel-Events, EPG-Blockscrolling/Lücken, .13-Overlaps/14-Uhr, Leerdaten und Alias, Kodi-XML-Fokus-Kontrast, EPG-Deduplizierung, Artwork-SPACE_FULL-Queue und konkurrierende SQLite-Zugriffe; systematisches Regression-Suite-Summary. ARM32/Kodi 21.2 Syntax, später Estuary.
5. Veröffentlichungskandidat: ZIP-Datei, SHA256, maschinenlesbarer Testreport, Installations-/Rückfallanleitung ohne Profil-Deinstallation, Route-/Dateidiff, Risiken und **bekannte noch offene Issues**. Vorversionen .11/.13/.16 und bestehende Profile bleiben unangetastet.
6. Sicherheit: keine Zugangsdaten oder personenbezogene/private URLs in Logs, Screenshots und öffentlichen Docs. Bei Kodi-Exit/crash nur **einmal** und dann Diagnose sichern, keine Endlosschleife.
7. Nutzerseitige nächste Android-Checkliste: Startsender → normale STOP-Funktion → XCMate Home, danach EPG-Play-Handoff einmal; erst dann weiterer Guide-/Artwork-/Navigationstest.

**Zugehörige Issues:** [#97](https://github.com/artattakk-creator/kodi-noodleprivate/issues/97), [#89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/89), [#92](https://github.com/artattakk-creator/kodi-noodleprivate/issues/92), [#93](https://github.com/artattakk-creator/kodi-noodleprivate/issues/93), [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88), [#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60), [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90), [#91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91), [#58](https://github.com/artattakk-creator/kodi-noodleprivate/issues/58), [#94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94), [#95](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95).
