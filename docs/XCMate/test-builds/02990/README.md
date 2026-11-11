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
