# XCMate 0.1.29.79 – manueller Testkandidat

Basis main .78, Master #387. Kein Merge und keine Veröffentlichung in Updatekatalogen.

- Paket: `plugin.video.xtreammate-0.1.29.79.zip`; SHA256 in gleichnamiger `.sha256`-Datei.
- Reproduzierbar mit `python tools/package_xcmate71.py /tmp/xcmate79-package`.
- ZIP-CRC und vollständige Source-Parität geprüft; keine Profile, SQLite-Dateien, Logs oder Tokens im Paket.
- Ursachen/Bestandsschutz: `docs/XCMate/IMPLEMENTIERUNG_02979_DE.md`.
- Android: `docs/XCMate/ANDROID_ABNAHME_02979_DE.md`; alle Gates ANDROID_NOT_TESTED.
- Host-/Native-/CI-Bericht: `docs/XCMate/TESTBERICHT_02979_DE.md`; Rohbelege im Unterordner `evidence/`. Keine Android-Abnahme.

Installation nur auf freigegebener Testbox: ZIP herunterladen, SHA256 vergleichen, in Kodi „Add-ons → Aus ZIP-Datei installieren“ wählen und vorhandenes XCMate damit aktualisieren. Keine Deinstallation und kein Profilreset. Nicht den GS-Media-Installer erneut ausführen. Private Kodi-Rohlogs nicht öffentlich hochladen.
