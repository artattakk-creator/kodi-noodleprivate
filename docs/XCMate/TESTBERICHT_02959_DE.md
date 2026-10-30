# .59 – Testbericht und offene Gerätebefunde

Auftrag #281, Referenzen #277/#276. Kumulative Basis main `5fa6166e884ecced4c28ae303c7f88fc374a0446`, .58. Add-on-Source-Build `5c620642723312bd6a348f255dbd3f061a9edd8c`. Alle Android-Ergebnisse des neuen Kandidaten NOT_TESTED; Box A/B unangetastet. Kein Merge/Release.

## Vollständiger Hostlauf

**2491 Tests PASS in 336.153 s**, 0 Fehler, 0 Fehlschläge, 0 Skips. Alle 2.463 bisherigen Methoden/Skipbedingungen erhalten, 28 neue. Unveränderlicher git-archive-Stand; komplettes TESTLOG_02959.txt und maschinenlesbare Ergebnisse beigefügt.

Build: gepinnter Bootstrap und Upgrade 0.1.1/0.1.2/0.1.5, Repositorybau, beide gettext-Dateien, 92 Icons/Lizenzen, Compile und Source-AST PASS. Die bekannte SyntaxWarning zur Escape-Sequenz im unveränderten vendorten SMBProtocol.py ist kein neuer .59-Code.

612 Add-on-Dateien: 594 vorherige byteidentisch, 15 exakt nachvollziehbare Änderungen, drei additive Module; keine Datei entfernt. Native Stop-Implementierungen, .42-Einstellung, Media-Exit/Resume/Autoplay, Wizard, Root-Routen, gespeicherte Widgetquellen und Skinwriter unverändert. Die Fast-Widget-Route erhält ausschließlich einen nichtfatalen erlaubten BOOT-Logmarker. Alte Scopeprüfungen normalisieren nur exakte reviewte .59-Deltas; neue Scopeprüfungen frieren den aktuellen Bestand separat ein. Andere laufende Entwicklungsstände: 62 Prüfsummen unverändert.

## Tatsächlicher nativer Widgetvertrag

Echter isolierter Kodi 21.2/Linux, vollständige echte XCMate-default.py-/Directory-Ausführung mit synthetischem Provider. Beide existierenden Medien-URLs liefern jeweils 24 echte native ListItems, 24 unterschiedliche Posterreferenzen und richtige pid/kind/sid-Detailziele. Posterreferenz wird gegen den Hash der exakten synthetischen Provider-URL geprüft. Zwei native Kodi-Container laden die Quellen; Screenshotprüfung weist je zehn korrekt zugeordnete, untereinander unterschiedliche dekodierte Poster-Pixelbereiche nach. Kein Playerstart.

Der neue CI-Schritt führt `tools/run_kodi_widget59_contract.py` zusätzlich zum bisherigen echten Kodi-Transportvertrag aus. Screenshot/JSON werden als CI-Artefakt gesichert. Testprofil, Providerbilder und Skriptstarter sind ausschließlich synthetische Hostfixtures, nicht Teil des installierten Add-ons. Der Harness wartet auf native GUI-Freigabe und eine vollständig geschriebene Screenshotdatei. Nur der bekannte frische Testprofil-Dialog Disabled add-ons wird auf Nein bestätigt; kein entsprechender Produktionspfad und kein Schließen fremder Gerätedialoge.

**Das ist keine BINGIE-/Android-Pixelabnahme.** Die tatsächliche Box-B-Ursache bleibt UNVERIFIED. Fehlender nativer Aufruf, falsches gespeichertes Profil, generiertes Include und versteckter Consumer müssen anhand realer Home-Beobachtungen getrennt werden; vorhandene Bindungen werden nicht gelöscht oder verändert. Generische Skinshortcuts-Typen video/videos/mixed werden nicht mehr falsch abgewiesen. Source-Metadaten und Cover bleiben ausschließlich Provider.

## Gezielte neue Regressionen

- Offener Wizard-EPG-Checkpoint: reguläres Jetzt aktualisieren bleibt offen und fordert den echten Serviceweg an; Fortsetzung separat; kein Checkpointverlust.
- Bereits laufender Portalworker: neue Aktualisierungs-Nonce wird nicht still verbraucht, frischer gespeicherter Anbieterstatus wird verwendet.
- Neuere Fortschrittszähler gegenüber älterem Erfolgsbericht; klare Quelle/Netz/XML/Leerfeed/Zuordnungsfehler und sichere HTTP-Statusfelder.
- Bestätigter nativer Stop, ursprüngliche Frist abgelaufen, vorübergehendes Modal oder Dialog-ID: warten und nach Freigabe genau einmal zurück. Kein erneuter Stop; neuer/fremder Player und Owner-Lease bleiben geschützt. Vorübergehender Player-API-Fehler nach ACK wird nicht endgültig failed. Paralleler abgeschlossener Return wird nicht überschrieben. Fehlende echte FIFO-ACK bleibt unbestätigt.
- Fehlende Ereignisdaten gegenüber fehlendem Bild, blockierte Adresse und referenzbereite Grafik getrennt, kein Pixel-PASS aus READY.
- Home-Sampling nur auf aktivem Home ohne fremden Dialog; keine Dateien, SQL oder Playerarbeit im GUI-Sampler. Unbekannt/leer/versteckt/Einträge getrennt, tatsächliches Dekodieren unverifiziert.
- Vollständiges Source-/Methodeninventar, unveränderte URLs/Routen/Skins/Wizard/native Stops, kein TVmaze-Experiment und keine Lösch-/Settings-Operationen in neuen Helfern.

Die vorhandenen großen XMLTV-/Katalog-, Mapping-, EPG-Rastervorschau-/Abbruch-, HTTP-/SQLite-, Artwork-, Medien-, Fernbedienungs-, Resume- und staffelübergreifenden Autoplay-Regressionsprüfungen bleiben Bestandteil des vollständigen Laufs. Hostdaten sind keine privaten Providerantworten.

## Paket

`plugin.video.xtreammate-0.1.29.59.zip`, 3171981 Bytes, 612 Dateien. CRC, sichere Pfade, sämtliche Sourcebytes, Python-AST und unabhängiger deterministischer Neuaufbau PASS.

SHA256: `b6d6969ee9a424f5a4f65c7e57f1668402e13bd5bd043dab356f56400ec57280`.

GitHub-CI muss am finalen Draft-PR-HEAD grün sein; konkreter Lauf, Job-/Paketnachweis und Artefaktlink werden im PR dokumentiert. Der Produktionsschritt Commit and publish generated archives muss für den PR SKIPPED sein. SHA des äußeren CI-Artefaktcontainers ist nicht die SHA des inneren Installations-ZIPs.

## Reproduzieren

```sh
python tools/bootstrap_xtreammate.py
python tools/apply_xtreammate_upgrade.py
python tools/apply_xtreammate_012.py
python tools/apply_xtreammate_015.py
python tools/build_repository.py
python tools/validate_kodi_po.py
python tools/build_xcmate_nav_icons.py --check
python -m compileall -q src
python -m unittest discover -s tests -v
python tools/run_kodi_helper57_contract.py --report-dir helper-contract
python tools/run_kodi_widget59_contract.py --report-dir widget-contract
```

Frisches Checkout, Python 3.12, Pillow, impacket 0.13.0 und simpleeval 0.9.13 gemäß CI. Native Verträge benötigen Docker und eine Kodi-21-Linux-Umgebung aus dem gepinnten Testimage. Keine Benutzerprofile in Fixtures kopieren.

## Abnahmegrenzen

Reale Film-/Serienreihen auf BINGIE Home: UNVERIFIED/NOT_TESTED. Tatsächlicher Providerimport, Bilder/Zuordnung/Neustart auf Box B: NOT_TESTED. Der konkrete ACK→Modal→dauerhaft failed-Defekt ist im Host repariert; reale GUI-Rückkehr und eigenständige native Rockchip-Hänger ohne ACK bleiben Geräteprüfungen. Keine vollständige P0-DoD oder Android-PASS behauptet. Kurze neue Abnahme erst mit fertigem Paket gemäß ANDROID_ABNAHME_02959_DE.md, später PASS/FAIL/ÜBERSPRINGEN. Bei Freeze keine weiteren Belastungszyklen.
