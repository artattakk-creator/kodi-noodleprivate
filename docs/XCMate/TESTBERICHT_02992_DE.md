# XCMate 0.1.29.92 – Test- und Freigabebericht

Stand: 13.11.2026. Source-PR [#448](https://github.com/artattakk-creator/kodi-noodleprivate/pull/448), getrennter Installer-PR [#447](https://github.com/artattakk-creator/kodi-noodleprivate/pull/447). Basis main `002ba995dc3ce6a6f72037261ad28c70e2d87d80` (.91). Finale Codekorrektur `fa04b2710691845402de15c75eeaa84ca4ac80ef`.

**Keine Android-Abnahme, kein Merge und keine Repository-Veröffentlichung.** Die Matrix im Implementierungsbericht benennt insbesondere noch offene native Android-Playerfehler und nicht bewiesene Hardware-Platzentlastung. Ein ausführbarer RC ist keine vollständige P0-Freigabe.

## Paket und Reproduzierbarkeit

- `test-builds/02992/plugin.video.xtreammate-0.1.29.92.zip`, 4.695.958 Bytes, 867 Mitglieder.
- SHA256: `ab8715438aa1156a281e023ee42687c5cf480dd62707628231d214d545fadd6c`.
- Canonical Build und jeder Source-Byte/ZIP-Mitglied/CRC geprüft; keine Profil-SQLites, privaten Logs, pyc oder zusätzlichen Mitglieder. Manifest-ID und Version geprüft.
- `python tools/release_candidate92.py --output docs/XCMate/test-builds/02992` prüft zudem das **nur unter docs abgelegte Offline-Pilot-Proposal**. Live-Indizes sowie .90/.91- und .5.26-Pakete bleiben unverändert.
- Der separate Installer .5.29 ist kein Bestandteil des XCMate-ZIP: SHA256 `674eaea4254395a5963c24012b09f9a59632cb8bb57b29f652c65cf9f77ff30e`, PR #447, 8 gezielte Tests PASS und [Installer-CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43387039231) PASS. 31 unveränderte .5.26-Dateien, nur Versionsmanifest/UI plus neue Speicherbrücke. Kein erneuter 48-Komponenten-Lauf beauftragt.

## Hostprüfungen

Unveränderlicher Stand `62c2bc39`: **3.906 Tests PASS**, lokal 929,423 s und [vollständige GitHub-CI PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43401683846). Zusätzlich 11 Branding-pytests und alle 17 PO-Kataloge PASS. Die 36 neuen .92-Tests sind im Gesamtlauf enthalten, nicht hinzuzählen.

Letzter Stand `fa04b271`: 54 gezielte Speicher-/Kapazitäts-/HTTP-vs-Dateipfad-/Live-Transport-/Paketprüfungen PASS. Der vollständige Lauf mit zwei zusätzlichen Regressionen und die abschließenden CI-Gates werden unten nach Abschluss ergänzt. Keine Ausführung auf veränderten Source-Fixtures als Endabnahme verwenden.

Getestet werden unter anderem: Legacy-/echte Neuprofile, reserveschonende atomare Metadaten, Profil-/SQLite-Busy, Fehler ohne leere DB-Neuanlage, Erinnerungsreferenzen, Kalendergrenzen, verdichteter Now/Next-Cache, 3.357 Kanäle, eigenes Temp-Cleanup, geschützte fremde Dateien, USB-Manifest/Unterbrechung/Hash/Originalerhalt/separate Originalbereinigung, simulierte Volume- und Boot-Identität, manuelles Bildmapping samt kaltem Readback, Quelle/Portal/Profilisolierung und unbekannte unzulässige Source-Änderungen.

**Modellgrenze:** Host-Volume-/Boot-Receipts in Migrationstests sind simuliert. Dateikopie, SHA, SQLite und Readback laufen tatsächlich. Das beweist weder ein Android-USB-Mount noch eine sichtbare Zieltextur auf der Box.

## Tatsächliche physische Freigabe im Hostmodell

[`reports02992/host-physical-cleanup.json`](reports02992/host-physical-cleanup.json): eigens für den Test erstellte und acht Tage gealterte eigene Tempdatei, 16.777.216 Bytes, tatsächlich entfernt; freie Bytes 2.193.416.192 → 2.210.189.312, beobachteter Zuwachs **16.773.120 Bytes**. Journal und Metadaten beanspruchen selbst Speicher; deshalb nicht einfach gelöschte Dateigröße als freien Platz ausgeben. Fremde Testdatei bleibt bytegleich. Dies ist eine Linux-Testmessung, **keine Messung der Android-Box**. Bei null beweisbar entbehrlichen Daten muss die Geräteanzeige null melden.

Großlast lokal PASS: 200.005 Filme + 200.005 Serien, je 109.380.521 tatsächliche HTTP-Bytes, DB 309.526.528 / 621.731.840 Bytes, 27,404 / 27,409 s, Peak-RSS 33.008 KiB. XMLTV-Großlast im vollständigen Lauf: mehr als 160.000 Programme und 95 MB XML. Synthetische lokale Dienste, kein realer Providerbenchmark.

## Native Kodi-/BINGIE-Prüfungen

[Exakter ZIP-Lauf auf `62c2bc39`](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43401683715): **720p und 1080p PASS**. Tatsächliches Linux-Kodi 21.2 und Original-BINGIE/Skinshortcuts; native Container 1510/1520/1530, alle sechs Reihen, Überschriften, animierter Spinner, konkrete ListItem-/Coverpixel, Zielaufrufe und Audio-PCM-Clock sowie drei vollständige Kodi-Kaltstarts. 88 Sender/24 Filme/24 Serien erhalten; persönliche und fremde gespeicherte Widgetpfade bleiben erhalten.

Die Netzwerkquellen und Bilder im Nativtest sind ausdrücklich synthetisch; der aktive Originaldienst ist für diese isolierte GUI-Strecke deaktiviert und die Testbrücke steuert die vorbereiteten Quellen. Der Bericht ist **kein automatischer Erstinstallations-/echter Provider-/Android-Nachweis**. Auf dem .92-ZIP werden alle 866 Nichtmanifestdateien unverändert geprüft; der Fixture-Manifest/Entry-Handoff wird im Paketbeleg ausgewiesen.

Home75 auf `62c2bc39`: 1080p PASS; 720p mit 30-Minuten-Idle durch den anschließenden neuen Commit abgebrochen, nicht als bestanden gewertet. 60 tatsächliche Linux-Kodi-Stop/ACK-Zyklen (20 pro Medientyp) PASS. Finale Gates siehe Abschlussnachtrag.

Die Zusatzprüfungen .89/.90 sind eigenständige Gates, keine Ersatzmessungen für den ZIP-Sechsreihenlauf. Ihre Fehler werden ausdrücklich nicht versteckt:

- .89: `LOGO89_PERSISTENT_LOGOS_MISSING`, 39 statt 88. Das Artefakt enthält `LOGO_VOLUME_UNVERIFIED` während der ausdrücklich injizierten 27-MiB-Negativphase, kein Container-OOM (`oom_kill=0`). Die folgende positive Kapazitätsphase lief nur 70 unmittelbare Aufrufe bzw. wenige Sekunden; die reale 60-Sekunden-Retry-Sperre der ersten Phase war noch aktiv. Der Fixture wartet nun innerhalb 90 Sekunden auf den unveränderten echten Backoff und die reguläre Worker-Kadenz, ohne _due zu leeren oder die Uhr zu mocken. Davon getrennt ist die durch Hosttests abgesicherte, konservative Behandlung begrenzter realer Messwertbewegung auf demselben Volume. Keine Reserveabsenkung; fremde/große Widersprüche bleiben blockiert.
- .90: `GROUP90_NATIVE_VIDEO_NOT_OWNED`. Kodi öffnete `/root/navigation90.mp4|User-Agent=...` als lokalen Dateinamen; HTTP-Header werden jetzt ausschließlich HTTP(S)-URLs angehängt. Native Ownership-/Playerprüfung nicht gemockt, Timeouts nicht verlängert.
- Früherer 1080p-PCM-Initfehler im Testcontainer durch explizite Bindung an dessen erzeugten Pulse-Nullsink behoben; tatsächliche Audio-Clock/ACK weiterhin Pflicht, kein Abschwächen des Sollwerts.
- Frühere Exit-137-Läufe nicht pauschal als OOM oder Anwendungsfix behauptet; neuer Runner liefert Containerzustand, cgroup memory_events und RAM-Messung zur Diagnose.

Lokales Docker-Kodi war vor App-Start durch zu wenig Platz im Test-Overlay blockiert. Die nativen Läufe erfolgen deshalb in GitHub Actions; keine Docker-/Benutzerdateien oder Systemkonfigurationen dafür bereinigt.

## Historische Fehlversuche und Bestandsschutz

Erster vollständiger Stand `97555c1e`: 3.898 Tests, 27 FAIL aus veralteten Publish-/Freeze- und Reserve-Injection-Erwartungen nach der freigegebenen .91; korrigiert an exakt festgehaltener Main-/Archive-Baseline, keine Testmethoden entfernt, keine neuen Skips. Zwischenlauf während veränderter exakter Source-Fixture ungültig, nicht als reproduzierbarer PASS benutzt. Lokale Großlast anfangs wegen vollem eigenen /tmp fehlgeschlagen; nur eigene bereits gespeicherte Worktree-/fehlgeschlagene Testartefakte freigegeben, danach vollständiger Großlast-PASS. Publizierte .90/.91, .5.26, Kodi-Daten und Kanäle bleiben geschützt.

## Offene Freigabebedingungen

Alle 22 Schritte in [ANDROID_ABNAHME_02992_DE.md](ANDROID_ABNAHME_02992_DE.md) bleiben **ANDROID_NOT_TESTED**, getrennt für Kodi 21.2 und 21.3. Box A bleibt unverändert. Benötigt werden reale Inventur/Quota, USB-Schreib-/Hash-/Render-/Reboot-/Offlineprüfung und tatsächlicher interner Platzgewinn, Mapping-Reboot sowie die bekannten Player-Exit-Reproduktionen.

Noch OPEN: vollständige DB-/Quellfaktenkonsolidierung, externer XMLTV-Stream-Stage, sichere verwaiste Artwork-/Backup-Freigabe nach Referenznachweis, alte nicht inkrementelle DB-Kompaktierung, Android-Decoder-/StreamLoss-/AAC-Bootstrapursache; P1 Long-OK in allen Ansichten, manuelle eventgebundene XMLTV-Bildwahl, MP3-Alben-Anbindung und endgültige Postermaße. Details und Folge-Issues im Implementierungsbericht. **Keine vollständige P0-Erledigung oder Merge-Empfehlung.**
