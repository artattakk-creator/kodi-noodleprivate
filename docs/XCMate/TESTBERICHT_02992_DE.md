# XCMate 0.1.29.92 – Test- und Übergabebericht

Stand: 13.11.2026. Source-Draft [#448](https://github.com/artattakk-creator/kodi-noodleprivate/pull/448), Installer-Draft [#447](https://github.com/artattakk-creator/kodi-noodleprivate/pull/447). Basis main `002ba995dc3ce6a6f72037261ad28c70e2d87d80` (.91); aktueller Produktionscode `c9b6bdf673f43331157e0a610ee4e78fb7dc2e96`.

**Testkandidat mit offenen P0-Arbeiten, keine vollständige Freigabe. Kein Merge, keine Veröffentlichung, keine Android-Abnahme.** Die [Issue-Matrix](ISSUE_MATRIX_02992_DE.md) unterscheidet FIXED_HOST, FIXED_NATIVE und OPEN.

## Maßgebliches Paket

- ZIP: `test-builds/02992/plugin.video.xtreammate-0.1.29.92.zip`, **4.697.322 Bytes**, **867 Mitglieder**.
- SHA256: **`1db07f87e1f1e84581868c1acced91a89017c332fc934caade7f785ffd88f3b4`**. Frühere .92-Prüfsummen sind überholt.
- Reproduzierbarer Canonical Build, jedes Source-Byte/ZIP-Mitglied, CRC, ID und Version geprüft. Keine privaten Logs, Profil-SQLites, pyc oder Tokens im Paket.
- `python tools/release_candidate92.py --output docs/XCMate/test-builds/02992` prüft zusätzlich den ausschließlich unter docs vorbereiteten Offline-Pilot-Overlay. Kein Live-Katalog verändert.
- [Kanalschutz](reports02992/published-preservation.json): regulär/Pilot, .90/.91 und alle drei vorhandenen Installer-.5.26-ZIPs bytegleich zur Basis. .90-Rückfall-SHA `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f`.

## Aktuelle automatisierte Nachweise

[Aktuelle vollständige CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43441528773) **PASS: 3.915 Tests in 642,602 s**, zusätzlich **11 Brandingtests in 0,28 s** und **17 PO-Kataloge PASS**. Getesteter Checkout `4152c7f4b13fddad4735aa93488d680bc4f9d3c4`, Produktionscode `c9b6bdf6`. [Maschinenlesbarer Beleg](reports02992/host-tests.json).

59 gezielte Profil-/Speicher-/Paket-/Harnessprüfungen PASS in 7,914 s; im vollständigen Lauf enthalten. Zusätzlich 20 Wiederholungen des vorhandenen 4-Thread-Erststarttests PASS. Neuer Test blockiert die GUI-Veröffentlichung und prüft drei weitere sofort lesbare, identische vollständige Marker bei dauerhaft gespeicherter Policy „Später“.

[Aktueller exakter ZIP-Lauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43441528517): **720p und 1080p PASS**, exakt SHA `1db07f87…`. Je Auflösung vier Prüfdurchgänge mit drei echten Kaltstarts, native Container 1510/1520/1530, sechs Reihen mit Überschrift/Spinner/Pixeln und Klickzielen, fremde Widgetdefinitionen, 20 Gruppen mit je 137 Sendern und 20 echte globale Senderwechsel bei gehaltenem WAL-Writer. Belege [720p](reports02992/native-exact92-1280x720.json), [1080p](reports02992/native-exact92-1920x1080.json).

Native Einschränkungen: Linux-Kodi 21.2 mit Original-BINGIE/SkinShortcuts, synthetischen Quellen/Bildern und deaktiviertem Originaldienst in der isolierten GUI-Strecke. Alle 866 Nichtmanifestdateien des Installationspakets unverändert geprüft; Manifest/Plugin-Entry-Handoff ausdrücklich für die Fixture angepasst. Keine realen Provider-/Android- oder kompletten Erstinstallationsnachweise. Die Scope-Angaben stehen in den JSON-Belegen.

## Bestätigte zusätzliche Laufzeitnachweise vor der letzten Erststartkorrektur

[Home75-Volllauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43434565300), Produktionsstand `cb8d297c`, Testwerkzeuge `9b0fd985`: **720p und 1080p PASS**. Tatsächliche native Down/Up-Folge einschließlich **2530→2540**, Filmstart per echtem Detailbutton mit Video/Audio, Stop-ACK und Detailrückkehr, Guide auf markiertem Sender 5 statt Startsender 1. Drei echte Kodi-Kaltstarts mit offline geschaltetem Ursprung und geschützten persönlichen Testwidgets. [720p](reports02992/native-home75-1280x720.json), [1080p](reports02992/native-home75-1920x1080.json).

In 720p **1.800,71 Sekunden** gezielte Artwork-DB-Pause: 443 doppelte Polls, genau ein Worker, Wiederaufnahme desselben Workers, keine unbehandelte Ausnahme. Live ist in dieser Phase erwartbar PARTIAL; bestehende Medienreferenzen bleiben verfügbar. Dies ist Fehler-Injektion im echten Linux-Kodi, keine reale Android-Quota-/ENOSPC-Situation.

[Kurzer initial-home-Gegenlauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43434586981): beide Auflösungen PASS; gewöhnlicher 180-Sekunden-Soak, alle sonstigen Home-/Playback-/Restartprüfungen, zusätzliche DB-Pause nur wenige Sekunden. Der normale Full-/PR-Lauf behält unverändert 1.800 Sekunden. Ein Kurzlauf wird nicht als 30-Minuten-Abnahme ausgegeben.

[60 native Stop-/ACK-Zyklen](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43434586981), je 20 VOD/Episode/Live, genau ein Stop je Zyklus; [Beleg](reports02992/native-stop92.json). Synthetisches 320-Pixel-Linuxvideo, kein Android-MediaCodec-Nachweis.

[Reserve-/Cold-Logo-Prüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43421851720): 720p und 1080p PASS auf noch früherem Komponentenstand. 88 echte eigene Logo-Dateien in nativen Kodi-Containern, fünf verschiedene lokale Film-/Serienposter, zwei echte Kaltstarts ohne erneute Logo-HTTP-Anfragen, Bildstabilität über 305 Sekunden, 13 fremde Widgetdefinitionen und Zweiaktions-Reminder. Kapazität ausdrücklich 27-MiB-Negativ-/218-MiB-Positivmodell, kein Android-Volume-Beweis. [Beleg inklusive früherem FAIL](reports02992/native-long92.json).

Diese älteren Laufzeitnachweise werden **nicht als erneute Gesamtpaketprüfung** des letzten ZIP ausgegeben. Seitdem wurden nur Erststart-Konfigurationssperre/Policy und Changelog im Add-on geändert; Laufzeit-Player-/Renderer-/Retentioncode blieb identisch. Fresh-Startup und vollständiges aktuelles Paket werden im oben getrennten Host-/ZIP-Lauf geprüft.

## Speicher- und Leistungsbelege

- [Physische Temp-Freigabe](reports02992/host-physical-cleanup.json): eigene exakt zulässige, acht Tage alte Datei 16.777.216 Bytes gelöscht; freie Bytes **2.446.802.944 → 2.463.571.968**, tatsächlicher Nettozuwachs **16.769.024 Bytes**. Journal/Inventur benötigen selbst Platz; fremde Datei bytegleich erhalten. Kein Android-Platzgewinn behauptet.
- [SQLite-Freigabe](reports02992/sqlite-compaction92.json): eigener inkrementeller Testguide **1.671.168 → 1.146.880 Bytes**, 128 Seiten/**524.288 Bytes** physisch frei, quick_check=ok. Ein gepinnter Leser behält alle 1.600 Zeilen, Hauptdatei bleibt unverändert und Ergebnis WAL_BUSY statt falschem Freigabe-PASS. Kein WAL-Unlink, kein erzwungenes VACUUM; alte nicht inkrementelle DBs werden nicht konvertiert. Arbeitsreserve berücksichtigt echte Seitengröße plus Pointer-/Index-/WAL-Overhead.
- [EPG-Zwischenkopie](reports02992/epg-cache-measurement.json): 3.357 synthetische Sender × 30 Sendungen × 4.096-Zeichen-Beschreibung; JSON **430.309.249 → 4.651.720 Bytes**, etwa 98,9 % kleiner. Now/Next und volle Originaltexte erhalten. Snapshot 84,981 ms, JSON 12,329 statt 3.022,145 ms. Peak-RSS 872.388 KiB umfasst die alte große Vergleichsserialisierung und ist kein isolierter .92-RAM-Bedarf. Eigene Testdateien tatsächlich geschrieben/fsync bestätigt. Kleinere Kopie erst nach bestätigtem zentralem Neuimport, keine blinde Löschung einer großen Legacy-Kopie beim Upgrade.
- Synthetische HTTP-Großlast im früheren vollständigen Hostlauf PASS: 200.005 Filme und 200.005 Serien, je 109.380.521 Bytes, DB 309.526.528 / 621.731.840 Bytes, etwa 27,4 s je Bereich, Peak-RSS 33.008 KiB. XMLTV mit 160.000+ Programmen und 95 MB ebenfalls PASS. Keine realen Providerbenchmarks.

Host-Volume-/Boot-Receipts in Migrationstests sind simuliert; Kopie, SHA, SQLite und Readback tatsächlich ausgeführt. Echter Android-Mount, Zieltextur und physische Entlastung bleiben Gerätetests.

## Ursachen und Regressionen

| Befund | Korrektur / Ergebnis |
|---|---|
| Cold-Logos verschwinden trotz guter eigener Dateien | Bildleser übernimmt das unabhängige account-/quell-/hash-geprüfte Manifest. 88 reale Dateien ohne DNS/RAM/HTTP-Freigaben getestet; widerrufene Quellen auch im Legacy-Fallback gesperrt |
| Inkrementelle Freigabe bearbeitet nur eine Seite | Begrenzten SQLite-Cursor vollständig abholen; zusätzlichen WAL-Arbeitsraum prüfen, danach nativen Checkpoint, physische Byteprüfung statt DELETE-Zahl |
| 4-Thread-Erststart liefert nur einen Marker | Bestätigt durch zwei breite FAIL-Läufe mit BlockingIOError. Kalte Policy-Imports vor Konfigurationssperre, GUI-Veröffentlichung danach, dauerhafte Policy vor Marker. Sperrfrist unverändert; neuer Slow-GUI-Test und 20 Parallelwiederholungen PASS |
| navigation90.mp4 wird mit HTTP-Headersuffix geöffnet | Produktionsfix hängt HTTP-Header ausschließlich HTTP(S) an, lokale/VFS-/RTSP-Pfade unverändert |
| Globales Links nach Senderwechsel zu früh gesendet | Native Fixture folgt echter Fullscreen-/Owner-Reihenfolge und wartet auf stabile AV-/Busy-Freigabe. Kein Test-PASS durch Ersatz mit direkt adressiertem Dialog; frühere Diagnose blieb FAIL |
| Früher Live-Screenshot EVENT_IMAGE_PIXELS | Tatsächliche EPG-/Texturvorbedingung innerhalb derselben vorhandenen fünf Sekunden wie Medien. Echte Live-Bereitschaft im kurzen Gegenlauf etwa 3,1 s; feste frühe Aufnahme zeigte legitim erst Fallback/No-Info |
| Sporadisches VOD80_BUTTON_NO_VIDEO | Diagnose zeigt nativen Zwischenzustand Play → leere Liste/Suche → Play. Vor einem einzigen globalen Select stabile sichtbare/aktivierte Eingabe verlangen; keine Playback-Retries. Danach beide kurzen und der reguläre volle Home75-Lauf PASS. Keine behauptete Android-Decoderreparatur; früherer FAIL bleibt [separat](reports02992/native-home75-failure92.json) |
| .90 liest unmittelbar alten Fokus | Kodi-Omega-Code setFocusId nutzt SendThreadMessage. Test wartet begrenzt auf Bestätigung des einen Auftrags, kein Nachfokussieren und keine Sollwertänderung |
| Initialer RPC-Reset/Exit 137 | Test-Neustart verlangt echten PID-Wechsel statt Ping auf schließenden Server. Containerzustand/memory.events/Konsole sichern; Exit 137 allein ist kein OOM-Beweis |
| Cold-Skin wartet auf fehlendes flüchtiges Reparatur-Receipt | Bei unverändert installiertem Skin reale sechs Controls/Ready-Variable prüfen; alle folgenden Pixel-/Fokusgates erhalten |
| Test-PCM/JSON-Publikationsrennen | Virtuellen Pulse-Sink nur im Wegwerfcontainer aktiv halten; echte PCM-Clock/ACK bleiben Pflicht. Berichts-JSON atomar publizieren, zwei Regressionen |

Keine Testmethoden entfernt, keine neuen Skips zur Fehlerverdeckung. Fehlerhistorie und Teilnachweise werden getrennt von aktuellen PASS-Ergebnissen geführt. Keine privaten Kodi-Rohlogs veröffentlicht; ausschließlich synthetische native Artefakte und kompakte Ergebnisprotokolle. Der lokale Volltext-Hostlog bleibt privat, nur dessen SHA archiviert.

## CI-Snapshot und dokumentarische Übergabe

Die beiden maßgeblichen aktuellen .92-Läufe sind vollständig grün. Andere automatisch gestartete historische Langmatrizen laufen zum dokumentierten Zeitpunkt teilweise noch; daraus wird kein Gesamt-PASS aller GitHub-Workflows abgeleitet. [Snapshot](reports02992/ci-status92.json). Die wiederholte aktuelle Home75-Matrix hat bereits 1080p und media77 bestanden; 720p-Langlauf noch nicht abgeschlossen. Der vollständige frühere 720p-Langnachweis ist oben separat belegt.

Nach dem getesteten Checkout werden ausschließlich Berichte ergänzt. Produktionscode, Tests, Werkzeuge und ZIP bleiben unverändert. Die unveränderlichen Run-Links und Quell-Commits sind maßgeblich; neu durch Dokumentationsänderungen gestartete oder abgebrochene historische Matrizen werden nicht rückwirkend als bestanden ausgewiesen.

## Installer und offene Freigabebedingungen

Separater .5.29-Entwurf in #447: 8 Tests und [CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43387039231) PASS, SHA `674eaea4254395a5963c24012b09f9a59632cb8bb57b29f652c65cf9f77ff30e`, 31 unveränderte .5.26-Dateien. Nicht Teil des XCMate-ZIP, kein erneuter 48-Komponenten-Lauf.

Alle 22 [Android-Gates](ANDROID_ABNAHME_02992_DE.md) bleiben **ANDROID_NOT_TESTED**, getrennt für Kodi 21.2/21.3. Box A unverändert. Zuerst einmal Live-TV-Zurück im bestätigten Kompatibilitätsmodus, danach weitere Gerätezyklen. Reale Quota/Inventur, USB-Probe/Kopie/SHA/Bild/Reboot/Offline, tatsächlicher Platzgewinn und Mapping-Reboot fehlen.

Weiterhin OPEN: vollständige alte EPG-/Quell-/DB-Konsolidierung, externer XMLTV-Stream-Stage, referenzsicherer Orphan-/Backup-GC, alte nicht inkrementelle DB-Kompaktierung; RK3528-Decoder-/StreamLoss-/AAC-Bootstrapursache; Long-OK in allen Ansichten, manuelle eventgebundene XMLTV-Bildwahl, MP3-Albumroute (#450), klickbare Quellenlinks/Credits und endgültige Postermaße. **Keine vollständige Master-Erledigung oder Merge-Empfehlung.**
