# Testbericht XCMate 0.1.29.83

Referenzen: #398, #395. Basis: `fdbcf96823760777d0a2f153d046389c3d1f1352`.

## Gezielte Ergebnisse auf dem Host

- **39/39 PASS**: neue Speicher-, Berechtigungs-, Migrations-, Journal- und
  Bestandsschutztests (`test_xcmate_shared_storage_02983.py`,
  `test_xcmate_scope_02983.py`). Die Laufzeit steht im vollständigen Host-/CI-Protokoll.
- **11/11 PASS**: separate pytest-Prüfung des BINGIE-Brandings.
- **17/17 PO-Kataloge PASS**, Deutsch/Englisch jeweils 1.264 Einträge.
- Python-Kompilierung und `git diff --check` bestanden. Eine vorhandene
  SyntaxWarning im unveränderten SMB-Vendorcode sowie eine pytest-Plugin-
  DeprecationWarning sind keine Android-Erfolgsnachweise.
- ZIP-CRC und Datei-für-Datei-Vergleich mit dem vollständigen Quellbaum PASS.
  Deterministische Paketierung über `tools/package_xcmate71.py`.

Der vollständige kumulative Hostlauf und die nativen Kodi-Läufe werden auf dem
unveränderten Code in GitHub Actions ausgeführt. Die **abschließenden Resultate,
Commit-ID, Run-/Artefaktlinks und eventuelle Einschränkungen** werden am PR und
in #398 dokumentiert. Keine CI- oder Android-Erfolge werden hier vorweggenommen.
Die bestehende CI enthält weiterhin die vollständige kumulative Suite, echte
Kodi-21-Home-Prüfungen in 720p/1080p einschließlich der 30-Minuten-Pausenprüfung
und die Stop-/ACK-Zyklen für Live-TV, Film und Serie.

## Reproduzierbare Befehle

```sh
python -m unittest discover -s tests -v
python -m pytest -q tests/test_xcmate_bingie_branding.py
python tools/validate_kodi_po.py
python -m compileall -q src/plugin.video.xtreammate
python tools/package_xcmate71.py /tmp/xcmate83-package
cmp /tmp/xcmate83-package/plugin.video.xtreammate-0.1.29.83.zip docs/XCMate/test-builds/02983/plugin.video.xtreammate-0.1.29.83.zip
python tools/release_channel75.py
```

Die vollständige Suite benötigt Loopback-Netzwerkzugriff für die isolierten
HTTP-/SMB-Testserver und ausreichend temporären Speicher für die großen
Streaming-/SQLite-Fixtures. Ein erster Lauf ohne Loopback-Rechte wurde
abgebrochen; dessen Netzwerkfehler gelten nicht als Codefehler oder PASS.
Ein weiterer lokaler Lauf führte 3.335 Tests durch: 3.334 PASS und ein
Umgebungsfehler (`database or disk is full`) im großen HTTP-Fixture. Fünf rekonstruierbare entpackte Skin-Kopien älterer Hostläufe
wurden entfernt; sämtliche Belege, Screenshots, JSONs und das gepinnte
Originalarchiv blieben erhalten. Der abschließende lokale Lauf verwendet zusätzlich ein eigenes
`SQLITE_TMPDIR` im Arbeitsbereich; die unveränderte CI hat ausreichend
Plattenplatz. Endgültige Wiederholungen werden separat am PR/#398 ausgewiesen. Keine Kodi-Benutzerdaten wurden bereinigt.

## Testumfang

Echte lokale Dateien und SQLite-Journale: Same-Pool-Block ohne Schreibzugriff,
statvfs `available`/`free`, Mount-/Namespace-/Bind-/FUSE-Abgrenzung, getrennte
Blockgeräte per Fault Injection, Reserve, EACCES/EROFS/ENOSPC/ENODEV,
fehlende SAF-Bridge, Symlink/Traversal, 4-KiB-Consent/Readback/SHA/Entfernung,
fremde Namespace-Kollisionen, sicherer Folderdialog, Abbruch/Neustart/Resume,
SHA-Korruption, Renderpflicht, Mountwechsel vor Aktivierung, Busy-Timeout und
Wiederaufnahme, kein wiederholtes Journal-DDL, Schutz von Originalen und
Konfiguration sowie eingefrorene Veröffentlichungskanäle und Playerquellen.

Die Kapazität getrennter Android-Volumes wird dabei **simuliert**, nicht als
Eigenschaft der RK3528-Box behauptet. Echte Hostdateien/SQLite und die
nachgelagerten nativen Kodi-Tests sind ausdrücklich keine Android-Abnahme.

## Abnahmematrix

| Bereich | Implementierung/Hostprüfung | Android |
|---|---|---|
| Android-Picker ohne /storage-Zwang | Implementiert; Fault Injection PASS | ANDROID_NOT_TESTED |
| Quelle/Ziel/Reserve, gleicher Pool | Implementiert; reale Hostmessung + Fault Injection PASS | ANDROID_NOT_TESTED |
| SAF-fremder Zugriff | Klare Grenze; keine Bridge/keine Rechteumgehung | BLOCKED bei Zugriffssperre |
| Unbestätigte FUSE-Kapazitätstrennung | Fail closed, TARGET_VOLUME_UNVERIFIED | BLOCKED bis Nachweis |
| Bestätigte Schreibprobe | Reale 4-KiB-Datei und SHA256 PASS | ANDROID_NOT_TESTED |
| Copy/Journal/SHA/Render/Aktivieren | Reale Dateien/SQLite + explizites Rendergate PASS | ANDROID_NOT_TESTED |
| SQLite BUSY/Reserve | Begrenzte Versuche, spezifischer Code, Resume PASS | ANDROID_NOT_TESTED |
| Originale/Profile/Installer/Widgets | Unveränderte Quellen/Kanäle + Schutztests PASS | ANDROID_NOT_TESTED |
| Bilder/Logos/TMDB/Hero aus #395 | Nicht als behoben oder Android-abgenommen erklärt | WEITERHIN OFFEN |
| Merge/regular/Pilot/NeoDark3 | Nicht autorisiert; bestehende .82-Kanäle bleiben bestehen | NICHT VERÖFFENTLICHT |

Android-Teststrecke: [ANDROID_ABNAHME_02983_DE.md](ANDROID_ABNAHME_02983_DE.md).
Ursachen und Dateiumfang: [IMPLEMENTIERUNG_02983_ANDROID_SPEICHER_DE.md](IMPLEMENTIERUNG_02983_ANDROID_SPEICHER_DE.md).
Paket: [plugin.video.xtreammate-0.1.29.83.zip](test-builds/02983/plugin.video.xtreammate-0.1.29.83.zip).
Prüfsumme: [SHA256](test-builds/02983/plugin.video.xtreammate-0.1.29.83.zip.sha256).
