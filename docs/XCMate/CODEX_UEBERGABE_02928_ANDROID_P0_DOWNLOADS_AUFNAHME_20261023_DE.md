# XCMate – Codex-Übergabe 23.10.2026, nach realer Android-Abnahme 0.1.29.27
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on:** `plugin.video.xtreammate`  
**Produktiver Ausgangspunkt:** `main`, XCMate **0.1.29.27**, PR #130 (Integration A+B+C, 942 CI-PASS vor Geräteprüfung).  
**Nächster Vorschlag:** isolierte Draft-Testbuilds **0.1.29.28** oder nächste tatsächlich freie versionskonforme Buildnummer. Keine Veröffentlichung ohne reale Android-Abnahme und ausdrückliche Freigabe.

## 1 – Maßgebliche Nutzer-Abnahme
Frischer Nutzerbericht `docs/XCMate/ANDROID_ABNAHME_02927_20261023_NUTZERERGEBNISSE_DE.md`: **13 PASS / 15 FAIL / 0 NOT_TESTED** (28 Benutzer-Checkboxen, unverändert).

- **Suchreparatur A01–A08: alle 8 PASS.** Live-TV aus Sendername und laufender EPG-Sendung startet; Doppel-OK/Session/IR/EPG/Staffel-Autoplay ebenfalls PASS. **#125 nach Android-PASS geschlossen**; diese Funktionen nicht anfassen.
- **Aufnahme B01/B02/B08 PASS**, B03–B07 **vom Nutzer FAIL**. Wörtliche Beobachtung: „es kommt die fehlermeldung das aufnahme nicht unterstützt wird“. Wegen B03 kein erfolgreicher aufgenommener Byte-Stream; B04–B07 zwar als FAIL bestätigt, aber **abhängig blockiert**, nicht als unabhängige Root Causes ausgegeben. **#126 bleibt P0 offen.**
- **Detail-/Download C01–C10 vom Nutzer FAIL**, C11/C12 PASS. „das linke menu in details wird nicht angezeigt - dadurch konnte ich die kompletten download aktivitäten nicht überprüfen. poster failback und erneuter download funzt nicht“. **C01 ist direkt sichtbarer Blocker #131**, C02–C10 noch nicht unabhängig end-to-end ausführbar. **Nicht behaupten**, HTTP-Downloader oder Codec sei defekt.
- Existierende Konto-/Portal-/Gruppen-/EPG-/Favoriten-/Resume-Daten und Original-XCMate-Icon erhalten. Kodi 21.2 Android 13 RK3528 ARM32 / Titan BINGIE MOD 2.2.3; Kodi 21.3 und Kodi 22 weiterhin nicht real zertifiziert.

## 2 – Was die Fehlermeldung wirklich bedeuten kann: zwei technisch unabhängige Gates
**Alte .26 Statusanzeige:** `FAILED / 0 MB / UNSUPPORTED_TARGET` heißt **nicht unterstütztes Speicherziel**, nicht Stream-Codec. **Neue .27 Meldung laut Nutzer:** „Aufnahme nicht unterstützt“ – **ohne exakten neuen Reason-Code oder neues Log**, daher Ursachenbeweis offen.

**Source-/Format-Gate:** `direct_ts.py` verwirft nichtdirekte TS-Streams/Manifeste z. B. mit `NOT_DIRECT_TS` und `UNSUPPORTED_MANIFEST`. HTTP-/DRM-/HLS-/DASH-Fälle getrennt von lokalen Target-Fehlern diagnostizieren. Xtream-Anbieter kann direkte TS-, HLS- oder andere Formate anbieten. **Nicht** allein aus der Anzeige folgern, dass der Anbieter keine Aufnahme erlaubt.

**Target-/Dateisystem-Gate:** `capture_target.py::probe()/probe_fd()` verlangt native POSIX/dir_fd, Schreib-Lese-Test, Hardlink (`os.link`), fsync/Verzeichnis-fsync und mindestens 64 MiB Reserve. Bei Android-VFS/USB/emuliertem Speicher kann das scheitern; welcher Pfad bzw. welcher Syscall auf der aktuellen Box fehlgeschlagen ist, ist noch **nicht** bekannt. `capture_ui.py::_start` prüft zuerst Target, bietet `compatible_default()` nur nach Zustimmung an; `capture_service.py` prüft erneut vor Provider-Resolve. Ein früher Target-Fail heißt: noch kein realer Streamtest.

### P0-A: #131 – *sofort zuerst* das linke Detailmenü und die Download-Bedienung reparieren
Reale Beobachtung: Film-/Seriendetails → **Links** zeigt **kein** Seitenmenü. Neue Kodi-UI wurde gemergt, aber nicht real abgenommen.

**Codepfade:** `resources/lib/detail_menu.py::DetailMenuMixin._detail_menu_action` (verlangt `ACTION_MOVE_LEFT`/key=1, `mode=='detail'`, `self.actions` wahr und `not _playback_waiting`), `media_window.py::onAction/_handle_action/_valid_focus/_show`, `XCMateMedia.xml` Gruppe id **800**, `Window.Property(XCMate.DetailMenu)`, Label **802**, ListControl **810**, Fokus/Native-Visibility/Key-Dispatch. Keine aus Host-Mocks abgeleitete Erfolgsgarantie.

**Auftrag:**
1. Ursache reproduzierbar nachweisen: neutraler Stage-Trace `DETAIL_LEFT_RECEIVED`, `MODE`-Kategorie, `DETAIL_ACTIONS_READY`, `PLAYBACK_WAITING`, `MENU_VISIBILITY`, `FOCUS_810`, `MENU_CLOSED`; **keine Titel, Portal/Sender/Account-IDs oder Stream-URLs** öffentlich.
2. Menü bei links auf **Film- UND Serien-Detailseite** sofort sichtbar/fokussiert; keine Fokusfalle oder unbeabsichtigte Suche. Rechts/Zurück schließt nur das Menü und stellt exakt die Detailposition wieder her. Ggf. einen **sichtbaren lokalen „Aktionen“-/Menü-Button als Fallback** in der Detailansicht vorsehen, falls Android/IR Links bereits durch Kodi-Navigation belegt ist; **keine globalen Keymaps**. Fallback und Links öffnen **dieselbe** funktionierende Menükomponente.
3. Aktionen: Film herunterladen, Einzel-Episode wählen/herunterladen, Downloads verwalten, **gezieltes** Poster erneut herunterladen, Posterstatus, Schließen. Buttons müssen tatsächlich ausgeführte Aktionen zeigen; korrekter Text (DE/EN), keine kaputten leeren Felder.
4. Nach C01/C02-Geräte-PASS **C03–C10** wirklich durchführen (siehe unten); nicht im PR als bestanden deklarieren, solange das Menü auf echter Box nicht sichtbar ist.
5. **#111** Posterdiagnose: Ziel-Poster auswählen, Cache-/Source-/Retrystatus anzeigen. Bestehende READY-Artwork-Einträge schützen, keine globalen Resets; echter Bildinhalt verifizieren und ggf. Quellen-URL erneuern, nur eindeutiges Metadatenmatching.

### P0-B: #126 – Recorder-Diagnose UND tatsächlich benutzbaren Android-Speicherpfad herstellen
1. **Stage- und Error-Codes in der UI unterscheiden:** **`TARGET_`** (PATH, MKDIR, OPEN_DIRECTORY, SPACE, OPEN_FILE, WRITE, FSYNC_FILE, LINK, READ, FSYNC_DIRECTORY), **`SOURCE_`/`NOT_DIRECT_TS`/`UNSUPPORTED_MANIFEST`**, **`HTTP_`/Providerlimits** und **`RECORDING_`-Runtime-Fehler**. Meldung auf Deutsch mit einfacher Lösung; bei Zielproblemen **vor** Zusatzverbindung stoppen. Diagnoselog: `[XCMate][CAPTURE_TARGET] code=… syscall=… errno=…`; nur Statuskategorien ohne Pfad/URL/AccessToken.
2. Verifizieren, ob **die Hardlinkpflicht** auf Android für das sichere Aufzeichnen grundsätzlich erforderlich ist oder eine **zu strenge Implementationsentscheidung**. Alternative nur entwickeln, **wenn** Nichtüberschreiben, eindeutige Dateinamen, O_EXCL, persistente Teildateien, sicheres atomisches Publish/Finalisieren und Cleanup nach Crash genauso sicher beweisbar sind. **Nicht einfach `os.replace` auf bestehende Dateien anwenden, keine unsichere/unkontrollierte Umgehung von Symlink-/Race- und Rechteprüfungen.** Getrennte Fähigkeiten `can_record_direct_ts`, `can_download_direct_media` erwägen. Keine unaufgeforderte zweite versteckte Downloadordnereinstellung.
3. Kandidaten für **persistenten, erlaubten app-internen Ordner** per Probe testen, nicht blind `/sdcard`, `/storage/emulated/0`, FAT32, SMB, SAF oder private Android-Pfade als unterstützt deklarieren. Nach **expliziter Zustimmung** gemeinsam gespeicherte Einstellung `recordings_folder` korrekt aktualisieren, keine Account-/Medienmigration oder Datenlöschung.
4. Auf echter Box mit bekannt erlaubtem **direktem TS-Sender** testen. Nach Target-PASS Streamtyp und HTTP-/Anbieterfähigkeit prüfen. Falls der Kanal HLS liefert, präzise `UNSUPPORTED_MANIFEST` anzeigen; einen anderen erlaubten Direct-TS-Testsender wählen. **HLS-/DASH-/DRM-Recording nicht stillschweigend versprechen und keine Schutzmaßnahmen umgehen.**
5. **B03** Start `recording` + Bytes >0; **B04** stoppen und `complete` mit vollständig finalisierter TS; **B05** lokale Datei Bild/Ton; **B06** nach Kodi-Neustart offline; **B07** kontrolliert unterbrechen: `partial/failed` mit brauchbaren Daten und ohne Verlust fremder Dateien.
6. Aufnahme und Download sind **zwei verschiedene Engines**: TS-Sofortaufnahme vs. direkter VOD-Dateidownload (MP4/MKV/AVI/TS soweit wirklich unterstützt). Nicht den Download-Worker automatisch sperren, **nur weil** der Direct-TS-Recorder eine *streamformatbezogene* Einschränkung meldet. Für dasselbe gewählte `recordings_folder` eindeutige, getrennt sichere Target-Capabilities und Statushinweise; **kein** DRM-/HLS-Umgehungs-Workaround.

### P0-C: Endlich echte Film- und Serien-Downloads auf Android testen
Abhängigkeiten: funktionierendes #131-Menü und für den Download **wirklich verwendbares persistentes Ziel**; Direct-TS-Recorder muss hierfür nicht zwingend erfolgreich sein, sofern Download-Engine + Speichermodell unabhängig sicher funktionieren.

1. **Film herunterladen:** einen Anbieter-Film wählen, der einen erlaubten *direkten* HTTP(S)-Container (z. B. MP4/MKV) bereitstellt; vor zusätzlicher Verbindung bestätigen, Fortschritt `RUNNING`/MiB wächst, Status `COMPLETE`.
2. **Einzelne Folge herunterladen:** echte Staffel+Folge wählen, richtige Serie/SxxExx, keine ungefragten ganzen Staffeln oder Portalwechsel.
3. Pausieren, Abbrechen, Retry, Fortsetzen (Range nur mit überprüftem Validator/Teilhash, sonst sicherer Neuanfang), Speicherende, Kodi-Neustart, Downloads-Queue.
4. Fertigen Film und eine Folge **aus Downloads verwalten** lokal und offline mit Bild/Ton starten; vorhandene Aufnahmen und READY-Poster unangetastet.
5. UI unterscheiden: „Download nicht unterstützt“ **mit konkretem Grund** (`UNSUPPORTED_SOURCE`, `PROTECTED_SOURCE`, `INVALID_MEDIA`, `TARGET_*`, Provider-/HTTP-Code, kein Content-Length) statt pauschalem „Aufnahme nicht unterstützt“.
6. Nutzer wollte **Downloads im selben gewählten Aufnahmeordner**, mit Kennzeichnung „Download - …“. **Kein** zweiter versteckter Ordner, kein heimlicher Speicherortwechsel. Bei fehlender Ziel-Fähigkeit transparent ablehnen/einen geprüften kompatiblen Zielordner anbieten; kein unvalidiertes Überschreiben.

## 3 – Weiterentwicklung in separaten, prüfbaren PRs
Nach funktionierenden P0-Downloads und Speicherzielen **parallel für den nächsten vollständigen Releasekandidaten** arbeiten:

- **#127** informativ gestaltete Suchergebnisse: **Senderlogo + Jetzt/EPG-Zeiten**, bei Filmen/Serien **kleine Poster + Titel, Jahr, Sprache, belegte HD/4K-Qualität, Quelle/Portal, ggf. Anzahl Staffeln/Plot**. Schön, D-Pad-lesbar, cache-first; Such-Live-Fix **#125 A01–A08 PASS einfrieren**.
- **#120** Titan BINGIE MOD Live-TV-Button → konfigurierter XCMate-Startsender direkt und schnell, richtiger Live-Exit/Home-Rücksprung; externen `script.skinshortcuts`-`getiterator`-Fehler separat, ohne fremden Skin global zu patchen.
- **#122** unverändertes Space-Premium-Original-Splash-Bild lokal als **Lightweight**-Hintergrund durchgängig einschließlich Home, Filme-/Serien-Landing und Suche; **Original-XCMate-Icon immer erhalten**; kein Premium-Aktivierungszwang.
- **#123** hochwertige EPG-Sendungsdetailseite wie Programmzeitschrift: Senderlogo/Zeiten/Dauer/Plot/optional verifiziertes Artwork, fernbedienbar, exakter Fokus-/Guide-Rücksprung.
- **#98** EPG-Quelle/Channel direkt pro Sender im großen EPG mit **Preview ohne Speichern**, Auswahl Anbieter-/EPGShare01-/Kaimandura-/eigenes XMLTV, erst nach OK dauerhaft speichern; manuelle Auswahl vor Auto-Matching.
- **#111** (neben P0-Retry) robuste Coverquelle/-Fallback mit gesicherter Zuordnung, begrenzte Retries; keine falschen Cover.
- **#43** **verbindlicher vollständiger Plug-and-Play-Erststart im nächsten vollständigen Releasekandidaten**: frisches Kodi, Wizard automatisch, Xtream/M3U/Stalker, Importauswahl Live/Film/Serie-Gruppen per Checkbox, EPG-Quellen/Auto-Matching/fehlende Matches, progressive Artwork-/Metadaten-Jobs, Anzeige des Importfortschritts, Startgruppe/Startsender, Save/Rollback, sofort benutzbares Home. Nicht durch vorgezogene Hotfix-ZIP als „fertig“ deklarieren. Von bestehender Installation keine Daten überschreiben.
- **#115 Space Premium** Fokus/OK-Bugs getrennt bearbeiten und auf Android testen, ohne funktionierendes Lightweight zu destabilisieren.
- **#63** Downloadumfang mit bestehendem sicheren Einzel-Film-/Folgen-Download abgleichen. Eigenständiger Media-Manager #113 und programmierte Timer #62 bleiben gesonderte Aufträge; keinen ungeprüften Scope hinzufügen.

## 4 – Verbindliches Vorgehen/Deliverables
1. Aktuellen main prüfen, alle genannten Issues samt .27-Bericht lesen. Kein altes .26-E05-Fail zum jüngsten Status erklären, **A07/B08/C12 und #125 A01–A08 sind PASS**.
2. **Zuerst** Review-/Draft-Hotfix für #131 mit Android-reproduzierbarer sichtbarer Menükomponente und Fallback. **Parallel** #126 exakte Recorder-Ziel- vs. Formatdiagnose und sichere Android-Dateistrategie.
3. Kleines **Test-ZIP (voraussichtlich 0.1.29.28, sofern frei)** mit eindeutiger SHA256, Changelog, Android-Checkliste mit PASS/FAIL/NOT_TESTED und Log-Reasoncodes; **kein automatischer Merge, keine GS-Media-Repo-Veröffentlichung**. Echte Android-Tests vor Freigabe.
4. Danach zielgerichtete C01–C10 / B03–B07-Nachtests. Neue Fehlerscreenshots/Logs **nur privat**; GitHub ausschließlich redigierte technische Spuren. Von der Nutzerabnahme .27 **13 PASS / 15 FAIL / 0 NOT_TESTED nicht ändern**.
5. Weitere getrennte Draft-PRs für #127/#120/#122/#123/#98/#111/#43; priorisierte Tests, sichtbare Fortschrittsberichte, alle Abhängigkeiten nennen. **#43 und #127 bleiben verpflichtende Gates der nächsten vollständigen Baureihe.**
6. Alte stabil geprüfte Kodi-Live-IR-/Overlay/Startgruppe, EPG-Guide und B05-A07 Senderstart, Suchen, **staffelübergreifendes Serien-Autoplay inklusive manuellem Stop**, Portale/EPG-Gruppen/Artwork/Favoriten/Resume und Originalicon unverändert bewahren. Kein Benutzer-Reset, keine globalen Keymaps, keine Datenbankmigration ohne gesicherten Plan.

**Jetzt mit #131 und #126-Code-/Geräte-Hotfix beginnen und anschließend einen echten Film- und Folgen-Download auf Android zur Geräteabnahme bereitstellen. Nicht nur eine weitere Konzeptanalyse liefern.**
