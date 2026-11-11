# XCMate 0.1.29.90 – ausschließlich Testkandidat

Draft-PR: https://github.com/artattakk-creator/kodi-noodleprivate/pull/431
Master: https://github.com/artattakk-creator/kodi-noodleprivate/issues/430

Kein Merge, kein Repository-Release. Die veröffentlichte .89 und Installer 0.5.26 bleiben unverändert.

- Paket: [plugin.video.xtreammate-0.1.29.90.zip](plugin.video.xtreammate-0.1.29.90.zip)
- Prüfsumme: [SHA256](plugin.video.xtreammate-0.1.29.90.zip.sha256)
- [Android-Testplan](../../ANDROID_ABNAHME_02990_DE.md): sämtliche echten Gerätetests ANDROID_NOT_TESTED.
- [Host-Messwerte](host-measurements90.json): synthetischer Linux-Host, ausdrücklich keine Android-Ladezeiten.

Kumulativ auf der Testbox über „Aus ZIP-Datei installieren“ einspielen, keine Neuinstallation und keine Daten-/Cache-Löschung. Box A nicht verändern. Installation/Update zeigt Version und Änderungen über den bestehenden XCMate-Hinweisablauf. Vorhandene Skin-Dateien werden nicht unbemerkt ersetzt; eine ggf. angebotene Adapterkorrektur erfordert den vorhandenen Vorschau-/Backup-/Bestätigungsablauf.

Build reproduzieren:

```sh
python tools/package_xcmate71.py /tmp/xcmate90-repro
cmp /tmp/xcmate90-repro/plugin.video.xtreammate-0.1.29.90.zip docs/XCMate/test-builds/02990/plugin.video.xtreammate-0.1.29.90.zip
cd docs/XCMate/test-builds/02990
sha256sum -c plugin.video.xtreammate-0.1.29.90.zip.sha256
```

Der endgültige CI-/Native-Status wird im PR und Testbericht festgehalten; ein vorhandenes ZIP allein bedeutet keine vollständige P0-Abnahme.

Aktueller Produktcommit: `1c8cc4eb0d3208a976a67bc984cb06c12d8eb59c`.
SHA256: `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f`.

Abschluss des lokalen Hostlaufs: **3.802 PASS, 0 Fehler, 0 Skip, 640,171 s**.
[Testergebnis JSON](host-final90.json) · [vollständiger synthetischer Hosttest-Log](host-tests90.txt.gz).
GitHub-CI und native Gesamtabnahme **BLOCKED_CI** (queued ohne Jobs); Android **ANDROID_NOT_TESTED**. Noch nicht merge-/veröffentlichungsbereit. Ältere .90-Prüfsummen sind überholt.
