# XCMate 0.1.29.92 – Test- und Freigabebericht

Stand: 13.11.2026. Source-Draft-PR [#448](https://github.com/artattakk-creator/kodi-noodleprivate/pull/448), separater Installer-Draft-PR [#447](https://github.com/artattakk-creator/kodi-noodleprivate/pull/447). Basis: main `002ba995dc3ce6a6f72037261ad28c70e2d87d80` (.91). Aktueller Produktionscode: `95e3578e882ae28399d806557291b6424efec00a`. Gegenüber `6c52b6e0` geändert: ausschließlich storage_maintenance92.py und Changelog. Die zusätzliche SQLite-Korrektur ist mit 43 gezielten Speicher-/Pakettests bestätigt; die vollständige CI und exakte neue ZIP-Matrix laufen erneut. Ältere native Belege tragen weiterhin ihre ursprüngliche Paket-SHA und werden nicht als Test des neuen Pakets ausgegeben.

**Entwicklungskandidat mit offenen P0-Arbeiten, keine vollständige Freigabe.** Keine Android-Abnahme, kein Merge, keine Veröffentlichung. Funktionsumfang und offene Punkte stehen in [IMPLEMENTIERUNG_02992_DE.md](IMPLEMENTIERUNG_02992_DE.md).

## Paket und Bestandsschutz

- ZIP: `test-builds/02992/plugin.video.xtreammate-0.1.29.92.zip`, 4.696.994 Bytes, 867 Mitglieder.
- SHA256: `9c40329b0f4f66544a55df809d61c34b4e78b029517824d194db692fbe7917bd`.
- `python tools/release_candidate92.py --output docs/XCMate/test-builds/02992`: reproduzierbarer Build, jedes Source-Byte, Mitglied, CRC, Version/ID und Kanalschutz PASS. Keine privaten Logs, Profil-SQLites, Tokens oder pyc im Paket.
- Pilot-Vorbereitung liegt ausschließlich unter docs; kein aktiver Repository-Index geändert. Regulär, Pilot, NeoDark3, .90/.91 und alle drei vorhandenen .5.26-ZIPs unverändert. Bytebeleg: [published-preservation.json](reports02992/published-preservation.json).
- .90-Rückfall-SHA256: `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f`.
- Separater Installer-Entwurf .5.29: SHA256 `674eaea4254395a5963c24012b09f9a59632cb8bb57b29f652c65cf9f77ff30e`, 8 gezielte Tests und [CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43387039231) PASS; 31 unveränderte .5.26-Dateien. Nicht Teil dieses XCMate-ZIP, kein erneuter 48-Komponenten-Lauf.

## Hostprüfungen – PASS

Vorheriger Produktionsstand `6c52b6e0`: **3.914 Tests PASS**, lokal in **920,049 s**; vollständige [GitHub-CI](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43413915137) **3.914 PASS in 897,427 s**, zusätzlich 11 Branding-pytests und alle 17 PO-Kataloge PASS. Neue .92-Tests sind darin enthalten, keine Addition überlappender Auswahlen. Kompakter Beleg und SHA des nur lokal gespeicherten Volltextlogs: [host-tests.json](reports02992/host-tests.json).

Abgedeckt: Legacy-/echte Neuprofile; reserveschonende atomare Metadaten; Profil-/SQLite-Busy; verweigerte Initialisierung ohne leere DB; Reminder-/Legacy-Merkliste-Referenzen; Kalendergrenzen; verdichteter Now/Next-Cache mit 3.357 Kanälen; eigene Tempbereinigung und Schutz fremder Dateien; USB-Manifest/Abbruch/Hash/Originalerhalt/getrennte Originalbereinigung; Mapping-Cold-Readback; Portal-/Account-/Quellenisolierung; exakt reproduzierbares Paket und unbekannte Source-Änderungen.

Zusätzlich echte 88 Logo-Dateien nach RAM-/DNS-/HTTP-Freigabeverlust: kalter Widgetreader liefert die quell-/account-/hash-geprüften lokalen Dateien. Geänderte oder widerrufene Quellen bleiben gesperrt. Dies behebt einen nachgewiesenen Produktionsfehler: Der Worker vermied zu Recht neue Netzwerk-Leases für gute Dateien, der gemeinsame Leser übernahm deren unabhängiges Manifest bisher aber nicht.

Host-Volume-/Boot-Receipts sind simuliert. Kopie, SHA, SQLite und Readback werden tatsächlich ausgeführt; das beweist weder einen Android-Mount noch Zieltexturen auf der Box.

## Speicher- und Lastmessungen

[Physische Host-Freigabe](reports02992/host-physical-cleanup.json): eigene 16.777.216-Byte-Testdatei, exakt zulässiger Name, acht Tage alt, tatsächlich entfernt. Freie Bytes **2.446.802.944 → 2.463.571.968**, Nettozuwachs **16.769.024 Bytes**. Journal und Inventur benötigen selbst Platz. Eine fremde Datei bleibt bytegleich. **Linux-Testmessung, keine Android-Entlastungsmessung.** Null sicher entbehrliche Daten müssen auf dem Gerät null Freigabe ergeben.

Lokale Großlast PASS: 200.005 Filme und 200.005 Serien, jeweils 109.380.521 HTTP-Bytes, DB 309.526.528 / 621.731.840 Bytes, 27,404 / 27,409 s, Peak-RSS 33.008 KiB. XMLTV-Test mit mehr als 160.000 Programmen und 95 MB XML PASS. Synthetische lokale Dienste, keine realen Providerbenchmarks.

Zusätzliche [Zwischenkopie-Messung](reports02992/epg-cache-measurement.json) mit 3.357 synthetischen Sendern, je 30 Sendungen und 4.096-Zeichen-Beschreibung: vollständige JSON-Kopie **430.309.249 Bytes**, .92-Kurzsnapshot **4.651.720 Bytes** (rund 98,9 % kleiner). Tatsächliche eigene Testdateien geschrieben und per fsync bestätigt; Now/Next für alle Sender und die unveränderten Originalbeschreibungen geprüft. Snapshot-Ermittlung 84,981 ms, anschließende JSON-Kodierung 12,329 ms statt 3.022,145 ms. Peak-RSS 872.388 KiB umfasst ausdrücklich die große alte JSON-Vergleichsserialisierung und ist kein isolierter .92-Speicherbedarf. Keine Android- oder Quota-Messung, keine bestehende Nutzerdatenbank verändert. Der kleinere Cache wird nach einem erfolgreichen, zentral bestätigten neuen Import veröffentlicht; eine bereits vorhandene große Legacy-Kopie wird nicht ohne diesen Nachweis gelöscht. Diese Modellmessung behauptet deshalb auch keinen sofortigen Platzgewinn beim ersten Upgrade-Start.

Vor Wartung wird zwingend ein read-only Klassen-/Volume-Snapshot erstellt und vor erster Löschung im Journal per Readback bestätigt. USB-Vorbereitung und separat bestätigte Originalbereinigung erfassen ebenfalls die Inventur. Es gibt keine globale Cachebereinigung, kein WAL-Unlink und kein ungesichertes VACUUM. Die 32-MiB-Importreserve und globale 1-GiB-Bildreserve bleiben geschützt.

## Native Kodi-/BINGIE-Prüfungen – Paketstand vor letzter SQLite-Korrektur

[Exakter ZIP-Lauf einschließlich Gruppennavigation auf Produktionsstand `6c52b6e0`](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43420656693): **720p und 1080p PASS**. Testwerkzeug-Stand `0d2bf877`; je vier sichtbare Prüfzyklen mit drei vollständigen Kodi-Kaltstarts; native Container 1510/1520/1530 mit 88 Sendern, 24 Filmen, 24 Serien; sechs Reihen mit Überschriften/Spinnern, konkrete ListItem-/Coverpixel, Klickziele und echte Audio-PCM-Clock/ACK. Zusätzlich in beiden Auflösungen: 20 Gruppen mit je 137 Sendern, insgesamt 2.740 Katalogzeilen, Paging bis Index 136, 20 native Senderwechsel mit exakten C++-Item-Tags und gleichzeitig offenem WAL-Writer. Globales Links/Select/Down unverändert verwendet, keine gezielten Ersatzaktionen zum Bestehen. Belege: [720p](reports02992/native-exact92-1280x720.json), [1080p](reports02992/native-exact92-1920x1080.json).

**Grenzen:** echtes Linux-Kodi 21.2 mit Original-BINGIE/SkinShortcuts, aber synthetische Quellen/Bilder; Originaldienst in dieser isolierten GUI-Strecke deaktiviert und Testbrücke für vorbereitete Quellen. Alle 866 Nichtmanifestdateien des .92-ZIP bytegleich geprüft; Manifest/Entry-Handoff für die Fixture ausdrücklich angepasst. Kein realer Provider-/Erstinstallations-/Android-Nachweis.

[Native Medienprüfung](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43413915549): **60 echte Stop-/ACK-Zyklen PASS**, je 20 VOD/Episode/Live und genau ein Stop pro Zyklus. [Beleg](reports02992/native-stop92.json). Synthetisches 320-Pixel-Linuxvideo, kein Android-MediaCodec-Nachweis.

[Home75-Langlauf](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/43417534465) auf Produktionsstand `6c52b6e0`: **720p und 1080p PASS**. Tatsächliche native Down/Up-Folge enthält ausdrücklich **2530→2540**, keine Move-Mocks. Filmstart per echtem Detailbutton mit Video/Audio, Stop-ACK und Detailrückkehr PASS; Guide öffnet auf markiertem Sender 5 statt Startsender 1. In 720p zusätzlich **1.800,9 Sekunden Artwork-DB-Schutzpause**, 443 doppelte Polls, genau ein Worker, kontrollierte Wiederaufnahme desselben Workers und keine unbehandelte Ausnahme. Das ist eine gezielte Fehler-Injektion im echten Linux-Kodi, keine echte Android-Speicherblockade; der Live-Status ist in dieser Phase erwartbar PARTIAL. Drei tatsächliche Neustarts mit Ursprung offline und erhaltenen persönlichen Testwidgets PASS. Belege: [720p](reports02992/native-home75-1280x720.json), [1080p](reports02992/native-home75-1920x1080.json).

Die zusätzliche .89-Reserve-/Cold-Logo-Prüfung wird gesondert geführt; der oben grüne ZIP-/Home75-Lauf ersetzt sie nicht.

## Abschließende SQLite-Korrektur

Der kontrollierte Vergleich zeigt: `execute(PRAGMA incremental_vacuum(128))` bearbeitet allein nur eine Seite. Der begrenzte Cursor wird nun vollständig abgeholt; danach nochmals ausschließlich SQLite-eigenen TRUNCATE-Checkpoint anfordern. Ein echter Test prüft **128 Seiten / 524.288 Bytes tatsächliche Dateiverkleinerung** und `quick_check=ok`. Ein gleichzeitig offener Leser behält alle 1.600 ursprünglichen Zeilen, WAL bleibt vorhanden und Ergebnis ist `WAL_BUSY`. Die stärkeren Prüfungen ersetzen keine Tests und erhöhen keine Skips; **43 gezielte Tests PASS**. Alte nicht inkrementelle DBs werden weiterhin nicht konvertiert, keine Reserve entfernt, keine WAL-Datei manuell gelöscht.

## Ursachen und Korrekturen an den nativen Tests

- Lokale Wiedergabe war tatsächlich defekt: Kodi öffnete `navigation90.mp4|User-Agent=…` als Dateinamen. Produktionsfix hängt HTTP-Header jetzt ausschließlich HTTP(S) an; Netzwerk-Header und ISA bleiben erhalten.
- Gruppen-Fixture zeigte den Dialog zunächst vor Kodi-FullscreenVideo. Sie folgt jetzt der echten Service-Reihenfolge. Nach Senderwechsel kündigt Kodi das neue Item vor BusyDialog/AVStarted an; weitere Tasten dürfen erst bei stabiler eigener GUI/AV-Wiedergabe folgen. Keine größeren Timeouts, keine direkten Python-Callback-Mocks, keine Änderung des Live-Navigators.
- Nachgewiesener früher globaler Links-FAIL auf Sender 137: Zähler blieb 41; ausschließlich zur Diagnose direkt an das eigene Dialogfenster gesendetes Links erhöhte ihn auf 42 und öffnete die Senderliste. Dieser Diagnoseversuch blieb FAIL. Kein grünes Ergebnis durch Ersatz der globalen Navigation.
- Cold-Start-Fixture verlangte ein flüchtiges Reparatur-Receipt auch bei bereits unverändert installiertem Skin. Bei fehlendem Receipt prüft sie künftig ausschließlich beim Kaltstart die sechs tatsächlichen Kodi-Controls und Ready-Variable; nachfolgende Pixel-/Fokus-/Widgetprüfungen bleiben Pflicht.
- .89-Negativphase setzt absichtlich eine 60-Sekunden-Logo-Sperre bei injizierten 27 MiB. Die folgende positive Phase wartet auf diesen echten Backoff, statt 70 sofortige Aufrufe als Wiederaufnahme zu behaupten. Keine Retry-Uhr manipuliert und keine Reserve herabgesetzt.
- Pulse-Testcontainer: erzeugten Nullsink ausdrücklich binden, dessen Idle-Suspend nur innerhalb des Wegwerfcontainers deaktivieren. Reale PCM-Clock und Open-ACK bleiben Pflicht. Keine Android-/Benutzer-Audioeinstellung geändert.
- JSON-Bericht vom Produzenten atomar veröffentlichen, damit paralleler Auswerter keine leere Datei liest; zwei Tests für vollständige Sichtbarkeit/LastGood bei Publikationsfehler.

Frühere Exit-137-Läufe wurden nicht pauschal als OOM ausgegeben. Aktuelle Containerdiagnose enthält Zustand und cgroup memory_events. Lokaler Docker-Kodi-Lauf war vor App-Start durch zu wenig Test-Overlay-Platz blockiert; native Nachweise stammen aus GitHub Actions. Keine Benutzerdateien dafür bereinigt.

## Offene Freigabebedingungen

Alle 22 Geräteprüfungen in [ANDROID_ABNAHME_02992_DE.md](ANDROID_ABNAHME_02992_DE.md) bleiben **ANDROID_NOT_TESTED**, getrennt für Kodi 21.2/21.3. Box A unverändert. Reale Quota/Inventur, USB-Schreib-/Hash-/Render-/Reboot-/Offlineprüfung, tatsächlicher interner Platzgewinn, Mapping-Reboot sowie Player-Exit müssen auf der Testbox nachgewiesen werden.

**Weiterhin OPEN:** vollständige alte DB-/Quellkonsolidierung, externer XMLTV-Stream-Stage, sichere verwaiste Artwork-/Backupfreigabe, Kompaktierung alter nicht inkrementeller DBs; Android-Decoder-/StreamLoss-/AAC-Bootstrapursache; Long-OK in allen Ansichten, manuelle eventgebundene XMLTV-Bildwahl, MP3-Albumroute ([#450](https://github.com/artattakk-creator/kodi-noodleprivate/issues/450)), direkt bedienbare Quellenlinks/erweiterte Credits und endgültige Postermaße. Die längeren nativen Gates und diese offenen P0-Arbeiten verhindern eine vollständige Erledigungs- oder Merge-Empfehlung.
