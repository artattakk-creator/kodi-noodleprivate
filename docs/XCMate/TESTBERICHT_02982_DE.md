# XCMate .82 – Testbericht und reproduzierbare Nachweise

Auftrag #395 · Draft-PR [#396](https://github.com/artattakk-creator/kodi-noodleprivate/pull/396).
**ANDROID_NOT_TESTED** für sämtliche echten Gerätefälle. Keine Veröffentlichung.

## Paket

`docs/XCMate/test-builds/02982/plugin.video.xtreammate-0.1.29.82.zip`

SHA256: `7cc578fc6f3fe74a2e474df8b0fbe2804090951f75769d8d7fb0fa217120e263`

3.497.654 Bytes, 774 Dateien; ZIP-CRC und bytegenauer Vergleich mit dem
Quellbaum bestanden. Zwei unabhängige Builds erzeugen byteidentische Pakete.
Das Paket enthält keine Profile, Rohlogs oder Zugangsdaten. Die vier bereits
veröffentlichten .81-Paketkopien und Installer 0.5.26 bleiben unverändert.

## Hostprüfungen

- 23 neue .82-Testfälle: **PASS**, lokaler Lauf 2,245 s. Enthalten sind echte
  PNG-Decodes/SHA256, 88 Logos in sechs gebündelten Kodi-RPCs, 443 deduplizierte
  Polls im selben Worker, Pause/Recovery, fataler MemoryError ohne Respawning,
  direkte PAUSED-/BUSY-Injection an `artwork_db.connect` sowie `art_store.used`,
  Same-Volume-Prüfung, Reservegrenze, Offline/Unknown, sichere 4-KiB-Probe,
  unveränderte lokale Cover über Refreshzyklen und frühzeitige Cache-Publikation.
- Abbruch-/Workerprüfungen gemeinsam: **10 PASS**, 1,232 s. Der alte Abschalttest
  injiziert den Abbruch jetzt an der neuen read-only Inspektionsgrenze;
  versehentliches automatisches `maintain()` bleibt ein harter Fehler. Ein
  Watchdog verhindert ein unbegrenzt hängendes Test-Fixture.
- PO-Validierung: **17 Sprachkataloge PASS**, Deutsch/Englisch je 1.240 Kontexte.
- Python-Kompilation und Whitespaceprüfung: **PASS**.
- Betroffene Alt-Fixtures nach Bereinigung der Kodi-/Search-/EPG-Bindungen:
  **108 PASS**, 23,350 s. Modellfenster-Watcher werden vor dem Austausch der
  Prozess-Stubs beendet; es werden keine Produktassertions entfernt.
- Gesonderte pytest-Brandingprüfung: **11 PASS**. Die komplette CI installiert
  pytest ausdrücklich und führt diese funktionsbasierten Tests zusätzlich aus.
- Gesamter aktueller Testumfang: **3.298** Methoden, davon 3.275 bestehende und
  23 zusätzliche .82-Methoden. Methoden und vorhandene Skip-Bedingungen werden
  vollständig gegen die freigegebene .81-Basis geprüft.

Der maßgebliche vollständige Ergebnisbeleg ist der aktuelle `full-host`-Lauf
unter [PR #396 → Checks](https://github.com/artattakk-creator/kodi-noodleprivate/pull/396/checks).
Der Workflow **XCMate 82 complete host review (no publication)** liefert das
Artifact `xcmate82-complete-host` mit ungekürztem `tests.txt`, Paketmetadaten,
ZIP und SHA256. Nur dessen tatsächlicher Abschluss gilt als Vollsuite-PASS.
Die abschließenden konkreten Lauf-Links, Fehler-/Skipzahlen und Commit-ID
werden zusätzlich im [Master #395](https://github.com/artattakk-creator/kodi-noodleprivate/issues/395)
und in der PR-Beschreibung dokumentiert.

Reproduzieren:

```sh
python -m pip install 'Pillow>=11,<13' 'impacket==0.13.0' 'simpleeval==0.9.13'
python -m unittest discover -s tests -v
python tools/validate_kodi_po.py
python tools/package_xcmate71.py /tmp/xcmate82-package
```

Ein früher lokaler Vollsuiteversuch ohne Loopback-Netzwerkfreigabe wurde
abgebrochen. Ein weiterer wurde am veralteten Wartungs-Test-Doppel beendet
und nach dessen Anpassung vollständig neu gestartet. Diese Versuche werden
nicht als erfolgreiche Gesamtläufe gezählt. Ein dritter lokaler Lauf wurde vor
der zusätzlichen Absicherung des expliziten Schreibtests beendet; nach der
letzten Quelländerung wird erneut vollständig geprüft.

## Echter Kodi auf Linux, nicht Android

`tools/run_kodi_home82_contract.py` verwendet den gepinnten BINGIE-2.2.3-
Quellstand und einen isolierten Kodi-21-Prozess. Alle historischen Home-
Navigations-, Quellen-, Full-bleed-, Senderdetail-, HTTPS-Bilddecode-,
Film-Play-/Stop-ACK- und Kaltstartfälle bleiben enthalten. Echte Audio- und
Videostreams sowie tatsächliche Screenshotpixel werden geprüft. Die Quelle
der beiden HTTPS-Testbilder wird für zwei native Kaltstarts abgeschaltet.

Der zusätzliche .82-Fall injiziert eine **echte DB-Pause-Receipt** in den
isolierten Pythonprozess. 443 erneute Aufträge dürfen keinen zweiten Worker
erzeugen. Während der Pause werden Live-/Film-/Serienframes jede Minute mit
fehlender optionaler Artantwort neu publiziert; Referenzzustand und konkrete
Logo-Pixel dürfen nicht verschwinden. Anschließend muss derselbe Worker nach
Freigabe den Auftrag abschließen. Aufgerufene Hintergrundworker werden über
die regulären Shutdown-APIs beendet, bevor Kodi natürlich neu startet.
Keine künstliche Prozessbeendigung und kein verlängerter Restart-Timeout.

Wichtiges negatives Fixture: Sender 87 hat absichtlich kein Providerlogo.
Live startet deshalb als REFERENCE_PARTIAL; genau dieses eine fehlende Logo
darf nicht durch ein erfundenes Bild kaschiert werden. Die übrigen 87 werden
beibehalten, VOD und Serie bleiben REFERENCE_READY. Der separate 88-Logo-
Hostfall prüft 88 tatsächlich vorhandene Bilder.

Der CI-Workflow **XCMate 82 native Home and review** führt aus:

| Prüfung | Beleg |
|---|---|
| 1080p + 180 s normale Idle-Phase | `home75.json`, Screenshots, zwei Cold-Receipts |
| 720p + 180 s normal + **1.800 s echte Fault-Idle-Zeit** | `home75.json.stability82`, minütliche Frame-/Pixelreceipts |
| 20 native Stop-/ACK-Zyklen je Live, Film, Serie | `native77-media/live.json` |
| Docker-State/OOM/Exit, auch bei Fehler | `container82.json` |

Artifacts: `home75-1920x1080`, `home75-1280x720`, `native77-media`.
Ein virtueller 30-Minuten-Unit-Test ist ausdrücklich kein Ersatz für den
1.800-Sekunden-Kodi-Lauf. Auch Linux-Pixel-PASS ersetzt keinen RK3528-Test.

```sh
python tools/run_kodi_home82_contract.py --report-dir /tmp/kodi82-720 \
  --resolution 1280x720 --fault-idle-seconds 1800
python tools/run_kodi_home82_contract.py --report-dir /tmp/kodi82-1080 \
  --resolution 1920x1080
```

## Abnahmematrix und verbleibende Grenzen

| Bereich | Implementierung / Hostnachweis | Android |
|---|---|---|
| P0-A Workerpause, Deduplikation, Recovery, Fehlerklassen | Implementiert; neue Hostfälle PASS; native CI separat nachweisen | ANDROID_NOT_TESTED |
| P0-B Messpfad und Reservepolicy | Implementiert; Grenz-/Offline-/Probe-Fälle PASS | Physische Mountabweichung **BLOCKED bis Geräte-Receipt** |
| P0-C Last-good, Kodi-Cache und atomare Publikation | Implementiert; echte lokale Bildfälle PASS; native CI separat | ANDROID_NOT_TESTED |
| P0-D gecachte Reihen vor neuen Netzwerkjobs | Implementiert; Host-Publikationsfall PASS, native Erstframeprüfung | Kalt-/Warmzeiten ANDROID_NOT_TESTED |
| TMDB, Hero, enge Reihen, stiller Katalog | .81 kumulativ erhalten; vollständige Regressionen in CI | Bekannte Titel und Pixel ANDROID_NOT_TESTED |
| Live/Film/Serie, Resume/Autoplay, Einstellungen | Keine Player-/Datenmigration; vorhandene Regressionen in CI | ANDROID_NOT_TESTED |
| Kodi-native Videoviews | Nur bestehende read-only Diagnose; keine Rekonstruktion | Unverändert offen |

Keine neue Hardware-Performancezahl wird aus den historischen Ready-Stages
oder Linux-Laufzeiten abgeleitet. Die tatsächlichen Android-Mountwerte und
sichtbar korrekten Sendungsbilder bleiben verbindliche Geräte-Gates.
Siehe [Android-Testplan](ANDROID_ABNAHME_02982_DE.md) und
[Ursachenanalyse](IMPLEMENTIERUNG_02982_DB_STORAGE_HOME_DE.md).
