# XCMate 0.1.29.37 – Host-Testbericht und Android-Testkandidat

**Kein Release. Keine Android-Abnahme. Kein Merge.** Basis `origin/main` `ecf85f36537b79f88cc3dfaef0fc70b10836b848` (.36), Branch `feat/xcmate-02937-cumulative`. Code: `475d9b3`, vollständiger Hoststand einschließlich letzter Modellergänzung: `fe38c74`. Spätere Liefercommits ergänzen Berichte/Paket/Prüfwerkzeuge, nicht die getesteten Add-on-Quellen. Das Paket wurde in PR-CI vollständig aus dem PR-Merge-Ref erzeugt und geprüft. Das heruntergeladene CI-Artefakt enthält bytegenau dasselbe ZIP wie der GitHub-Download und die lokale Lieferung. Dieser Bericht und CI_02937.json dokumentieren den geprüften Paket-HEAD b368f0d; der folgende reine Dokumentationscommit verändert die geprüften Quellen nicht. Der neueste Check ist zusätzlich direkt am PR sichtbar.

## Ergebnis

| Prüfung | Beleg | Ergebnis |
|---|---|---|
| Vollständiger Hostlauf | [TESTLOG_02937.txt](TESTLOG_02937.txt), Python3.12.14 | **1.298 PASS, 0 Fehler, 0 übersprungen**, 166,339 s |
| Bestehende .36-Tests | Alle 1.250 historischen Methoden erhalten; keine Testdatei/-methode entfernt | PASS |
| Neue .37-Tests | [48 Fälle, sieben Module](NEUE_TESTS_02937.json) | PASS |
| Originalgrafiken | 98 Themebilder und Original-Icon/Fanart bytegleich | PASS |
| Bestehender UI-Vertrag | 156/163 Dateien unverändert; sieben ausdrücklich gepinnte .37-Ausnahmen, danach historische Verträge unverändert geprüft | PASS |
| Benutzerbestände | Legacy-/Null-READY-/20k-Fixtures, keine Verbindung zu Nutzerboxen | PASS auf Host; Android NOT_TESTED |
| Paket | 279 Dateien, 2.434.852 Bytes; CRC, Pfade, AST, Quelle==ZIP, reproduzierbare ZIP-Bytes | PASS |
| Sprachen/Syntax | Deutsch/Englisch je 841 eindeutige PO-Kontexte, compileall | PASS |
| Main/Updatekanal | `addons.xml`, Prüfsumme, .36-ZIP und Publish-Workflow unverändert | PASS |
| Andere lokale Arbeiten | 62 vorbestehende WIP-Dateien in zwei anderen Worktrees per SHA geprüft | PASS |
| GitHub-CI | [Run 40237211308](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/40237211308), [CI_02937.json](CI_02937.json) | **1.298 PASS**, 206,008 s, Publish SKIPPED |
| Android A/Kodi21.2 und B/Kodi21.3 | 39 Gates je Box, [Statusdatei](ANDROID_STATUS_02937.json) | **78× NOT_TESTED** |

Eine vorhandene Warnung in der unveränderten Vendor-Datei `xcmate_smb_vendor/smb/SMBProtocol.py` betrifft einen Docstring-Escape; Syntaxprüfung endet erfolgreich. Sie wurde nicht durch eine fremde Vendor-Änderung verdeckt.

## Abdeckung HOST-01 bis HOST-09

| Gate | Ausgeführt und Ergebnis | Grenze |
|---|---|---|
| HOST-01 | Vollständiger Suite-Lauf 1250+48 PASS, keine ausgelassenen Tests; alter Index/ZIP geschützt | Keine neuen Geräte-PASS |
| HOST-02 | Neun Profiltests: echte leere vs Legacy-/Null-READY-/vorhandene Bildbestände, explizite Wahl, atomarer Wiederanlauf | Benutzerprofile ausschließlich als temporäre synthetische Kopien |
| HOST-03 | Sieben neue Exit-Tests plus sämtliche bisherigen Exit/Autoplay/Resume/Live-Stop-/Overlay-Tests: blockierender nativer Stop, Foreign Player, DB-Busy, genau ein Stop, Overlay zuerst, begrenzter Retry | Kodi-C++-Hänger kann auf Host nur modelliert werden; Geräteursache unbestätigt |
| HOST-04 | Sechs Dynamic-Tests: sichtbare URLs/Logos, Credential-/private DNS-/Schema-Abweisung, Platzhalter, keine Archivjobs/Reserveprüfung | Native Kodi HTTP/TLS/abgelaufene URLs und tatsächliches Rendering erst MODE-01/02; DNS-Pinning fehlt in Kodi-Schnittstelle |
| HOST-05 | USB/SMB-VFS-Adapter, Permission/Offline/Unknown-Capacity/Collision/Symlink, SHA/Bildvalidierung; vorhandene echte signierte SMB2-Wire-Tests ebenfalls PASS | Neue Artwork-VFS-Strecke verwendet ein Kodi-VFS-Modell; echte Android-SMB-/USB-/SD-Abnahme offen |
| HOST-06 | 20.000 Cover + zwei Logos kopiert und nach Modulneustart vollständig verifiziert; Pause/Resume, korrupte Ziele, separate Aktivierung/Renderbestätigung/Cleanup | Tatsächliches Android-Medium und Kodi-Rendern nicht simuliert als PASS zählen |
| HOST-07 | Drei neue Metadata-Tests: redigierter Export, lokale Indizes unverändert, URI-/Offline-/Readback-Verhalten; keine Kodi-/DB-Löschung | **Physischer Metadata-Offload BLOCKED**, keine Platzersparnis behauptet |
| HOST-08 | Neun System- und zwei Delta-Tests plus bestehende Wizard-/Transactional-Save-/Source-Tests; native Wrapperfreigabe, vier Quellenstatus, reale Gruppenfilter, Firmware/API-Mismatch, Home | **Dauerhaftes Fortsetzen ungespeicherten Wizard-Scans nach Prozessende BLOCKED**; Geräte-Save-Crash und IR-Abnahme offen |
| HOST-09 | Isolierter Builder, vollständiger PO/Compile/Suite-Lauf, reproduzierbarer ZIP-Vergleich, [Dateikatalog](DATEIKATALOG_02937.json), [Schutzprüfung](SCHUTZPRUEFUNG_02937.json) | Grüner PR-Check wird separat nach Push erfasst; Produktions-Publish muss SKIPPED bleiben |

## Vorher/Nachher – sauber abgegrenzt

Sieben neue Python-Prozesse je Version, wechselnde Reihenfolge, tatsächlicher Entry/Import/temporäres Profil und sechs Menüeinträge; nur die Kodi-API ist modelliert. Dateisystemcache warm, Setup der Testumgebung außerhalb des Messintervalls. Gemessen wird `run()` bis einmalige Directory-Abgabe, **nicht** Android-Appstart bis bedienbares Bild oder Stream-First-Frame.

| Host-Messwert | .36 | .37 |
|---|---|---|
| Median | 20,336 ms | 19,277 ms |
| Min–Max | 17,743–26,628 ms | 18,338–21,358 ms |

Das sind nur etwa **5,2 %** Medianunterschied mit überlappenden Bereichen. **Kein Beweis einer deutlichen Android-Beschleunigung.** Die Änderung entfernt den Routerimport aus dem Home-Pfad; die realen 27 Sekunden auf Box B bleiben mit START-01 zu prüfen. Rohmessungen/Phasen: [HOST_MESSWERTE_02937.json](HOST_MESSWERTE_02937.json), reproduzierbar mit `tools/benchmark_xcmate_02937_home.py` und der veröffentlichten .36-Basis.

Exit vorher: synchroner nativer Stop konnte den Aufrufer unbegrenzt blockieren, SQLite-Standardwartezeit bis zwei Sekunden. Jetzt: GUI veröffentlicht nur Intent, Service startet nach Fensterfreigabe einen Worker; Checkpoint-Busytimeout 50 ms, einmaliger Stop mit fünf Sekunden Diagnosefrist, maximal drei nachgelagerte Checkpointversuche. Der blockierende Test hält den Stop gezielt fest und bestätigt weiterlaufende Polls und keine zweite Stop-Instanz. Das sind Host-/Policywerte, **keine gemessene Android-Ausstiegslatenz**.

## Testkandidat

[plugin.video.xtreammate-0.1.29.37.zip](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.37.zip) · [SHA256-Datei](../../plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.37.zip.sha256)

```text
31a9fed1a5c9fe4272bf041fe40155f7b524ebe863540976cd1ed3507ce891d3  plugin.video.xtreammate-0.1.29.37.zip
```

In GitHub über **Raw/Download raw file** herunterladen, nicht die HTML-Ansicht speichern. ZIP enthält genau einen Ordner `plugin.video.xtreammate`, Manifest .37 und alle kumulativen Quellen/Assets. Keine Profile, Logs, SQLite-Daten oder Zugangsdaten sind enthalten. Der produktive Updateindex bleibt .36. Nutzerboxen wurden weder installiert noch zurückgesetzt.

## Reproduktion

Sauberen neuen Scratch-Checkout des PR-HEAD verwenden. Pinned-Bootstrap und Apply-Schritte aus `.github/workflows/publish.yml`, danach:

```bash
python -m pip install 'Pillow>=11,<13' 'impacket==0.13.0'
python tools/build_repository.py
python tools/validate_kodi_po.py
python -m compileall -q src
for f in tests/test_addon.py tests/test_site.py tests/test_providers.py; do
  sed -i "s@'..', 'plugin.video.noodleprivate'@'..', 'src', 'plugin.video.noodleprivate'@g" "$f"
done
python -m unittest discover -s tests -v
```

Der Builder erzeugt auch andere Add-ons/Indizes; daher nie Ergebnisse aus einem Testbuild automatisch committen oder veröffentlichen. Lokaler Testlauf hatte die gepinnten SMB-Abhängigkeiten via PYTHONPATH. Netzwerkzugriff auf Loopback muss erlaubt sein. Ein erster eingeschränkter Lauf meldete erwartbare `PermissionError` für Testserver sowie zwei unvollständige Wizard-Control-Fakes; nach Ergänzung der echten `setHeight/setPosition`-API und erlaubtem Loopback wurde **die ganze Suite** erfolgreich wiederholt, keine Netzwerkfälle übersprungen. Historische Hashes bleiben bestehen; `.37` normalisiert ausschließlich exakt gepinnte erlaubte Hunks, anschließend laufen die alten Hash-/AST-Prüfungen weiter.

## Offene Freigabe

- **P0:** SAFE-01/02/07 und EXIT-01..06 beider Boxen sind noch NOT_TESTED. #174-Geräte-/Versionszuordnung bleibt unbekannt. Kein bestätigtes Android-Freeze-Fix behauptet.
- **BLOCKED:** physische Metadaten-Payload-Auslagerung und dauerhaftes ungespeichertes Wizard-Scanresume. Export und sicherer Laufzeit-Cancel ersetzen diese Teile nicht.
- **Gerätepflicht:** echte dynamische Motive, Neustart-Persistenz, USB/SMB/NAS, IR-Fokus sowie Wizard-Speichern. Fehlender SD-Slot nach Feststellung BLOCKED statt PASS.

Vollständige [Ursachenanalyse](URSACHENANALYSE_02937_DE.md), [Issue-Matrix](ISSUE_MATRIX_02937_DE.md) und [Android-Anleitung](ANDROID_ABNAHME_02937_DE.md). Erst vorsichtige Einzel-Exit-Proben im kontrollierten Profil/auf B, Box A nur nach ausdrücklicher Nutzerentscheidung und read-only Bestandsaufnahme. Interne Originale bei erster Abnahme behalten. Keine Merges, Releases, Downgrades, Deinstallationen oder automatischen Installationen.
