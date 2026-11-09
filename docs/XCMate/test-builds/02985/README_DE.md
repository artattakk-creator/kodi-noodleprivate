# XCMate 0.1.29.85 – manueller Android-Testkandidat

**Draft-PR [#408](https://github.com/artattakk-creator/kodi-noodleprivate/pull/408). Kein Repository-Release.** Die regulären, Pilot- und NeoDark3-Kataloge bleiben bei der freigegebenen .84.

- [Installations-ZIP](https://github.com/artattakk-creator/kodi-noodleprivate/raw/refs/heads/fix/xcmate-02985-two-workstreams/docs/XCMate/test-builds/02985/plugin.video.xtreammate-0.1.29.85.zip)
- [SHA256-Datei](plugin.video.xtreammate-0.1.29.85.zip.sha256)
- [Android-Testplan](../../ANDROID_ABNAHME_02985_DE.md)
- [Testbericht](../../TESTBERICHT_02985_DE.md)
- [Implementierung und offene Punkte](../../IMPLEMENTIERUNG_02985_DE.md)

SHA256: `021689b4a4c48caa79107fdf04ede774e864fea0823b7df78c6f8eb0625ea1ff`

## Installation erst nach Freigabe des Testkandidaten

1. Nur auf der freigegebenen Testbox B testen; Box A unverändert lassen. Bestehende Kodi-Installation und Profile behalten.
2. ZIP herunterladen, SHA256 vergleichen. In Kodi **Add-ons → Aus ZIP-Datei installieren** die Datei auswählen. Dies aktualisiert die vorhandene Add-on-ID `plugin.video.xtreammate`; keine Deinstallation, keine Profil-/Cachebereinigung.
3. Angezeigte Add-on-Version .85 prüfen und den Android-Testplan ausführen. Bei Fehlern Test stoppen und konkrete Beobachtung mit redigierter Diagnose festhalten; keine privaten Rohlogs/Verbindungen auf GitHub veröffentlichen.
4. Regelmäßige Updates liefern .85 vor ausdrücklicher Merge-/Releasefreigabe noch nicht aus.

Alle echten Android-Gates stehen zunächst auf **ANDROID_NOT_TESTED**. Insbesondere tatsächliche Bilder, Fernbedienungsfokus und Persistenz bei der realen Speicherreserve können Hosttests nicht abnehmen. Der neue Cache kann eine echte Speicherblockade nicht durch Reserveabschaltung umgehen.
