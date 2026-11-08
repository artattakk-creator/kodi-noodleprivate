# XCMate 0.1.29.79 – Codex-Übergabe nach Main-Merge und Update-Veröffentlichung

**Datum:** 08.11.2026 · **Status:** Source + reguläres GS Media + Pilot **VERÖFFENTLICHT**, Android-Geräteabnahme **OFFEN**.

## Aktueller GitHub-Stand (auf main überprüft)

- Repository: `artattakk-creator/kodi-noodleprivate`, Branch `main`.
- Implementierung: [PR #388](https://github.com/artattakk-creator/kodi-noodleprivate/pull/388) **gemergt**, Source-Merge **`34a9fcbe3d65764edd405d6d0fb62d457acd51da`**.
- Quellversion: `src/plugin.video.xtreammate/addon.xml` **0.1.29.79**, kumulativ auf .78.
- Originales geprüftes ZIP: `docs/XCMate/test-builds/02979/plugin.video.xtreammate-0.1.29.79.zip`. **3.460.002 Bytes / 749 Dateien**.
- SHA256 aller ZIP-Kopien: `cb68d09c84c7190bf1459d0d46532920d6c5a7dfea15a96a6d5e6cb4f244c20a`. Quell-/ZIP-/CRC-Parität laut Codex-Bericht geprüft; GitHub-Blobs in den veröffentlichten Pfaden identisch.
- **Regulärer Kanal / Kodi `addons.xml`: 0.1.29.79**, `addons.xml.md5` = `c6bbfd4a52af4c8d931d6c15a0559fcd`. Reguläres ZIP:
  `https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.79.zip`
  Release-Commit `6c9201092f4ed959c655062351e5e61a79a20856`.
- **GS Media Pilot / `online-test/addons.xml`: 0.1.29.79**, `online-test/addons.xml.md5` = `07d280ee07b9b904ce76d8f4bd4ca6cf`. Pilot-ZIP:
  `https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.79.zip`
  Release-Commit `78bb1cd119848a65833bd4e5a412382201a66fe3`.
- **NeoDark3-Flach-ZIP bleibt .78**, da für .79 nur regulärer Main- und installierter Pilot-Updateweg autorisiert und aktualisiert wurden. Nicht ohne Auftrag als .79 ausgeben.
- **Installer `script.gsmedia.setup` bleibt 0.5.26**, Installer-ZIP-Blobs unverändert `f8bfbbe032bcf11e2ddb713fd1325ed2599dfbb1`. Kein Installer-Neustart/Reset und keine Userdata-Migration.

## Was 0.1.29.79 gemäß PR #388 geändert hat

1. Native Widget-Consumer-/Directory-Acknowledgements für Live, Filme und Serien einschließlich paginierter Reihen und erneuter Frame-Ankündigung.
2. Kaltstart-/Last-good-Covercache: gültige Kodi-Thumbnails nur bei exakt passender Item-/Provider-/Profil-/Quellenidentität wiederverwenden und nicht durch unvollständige Generationen überschreiben.
3. Senderbezogene EPG-Read-Leases mit Backoff und konservativem Provider-/XMLTV-/manuellen Matching.
4. Read-only Diagnose der defekten oder fehlenden Kodi-Library-Views, **keine automatische Reparatur von `MyVideos131.db`**.
5. Bestehende Nutzer-Widgets einschließlich „Neu im Kino“, Space-Blue-Patch, TMDB-Read-Token, Provider-/EPG-/Favoritendaten und Installer unangetastet lassen.

## Test-Evidenz / Abgrenzung

- PR #388: 3.214 Hosttests PASS (31 neue .79-Fälle), zehn GitHub-CI-Workflows grün; native Linux-Kodi-/BINGIE-MOD-2.2.3-Tests für 720p und 1080p bestanden, jeweils zweimaliger Prozessneustart; 60 native Stop-/ACK-Zyklen (20 je Medientyp).
- **Nicht** auf der persönlichen RK3528/Android-ARM32-Box abgenommen. Echte TV-EPG-Bildidentität, Hero-/EPG-Texture-Sichtbarkeit, „Neu im Kino“ und andere persönliche Widget-Reihen, Fokus/Navigation, Serien-/Film-/Live-TV-Exit sowie beschädigte `MyVideos131.db`-Views bleiben geräteseitig zu verifizieren. Erfolg im Linux-Host ist kein `ANDROID_PASS`.
- Aus dem früheren .78-Android-Log: `NATIVE_HOME_EMPTY`, kurzzeitig 24/24 Cover-Placeholder bei Neustart, EPG_DATA_MISSING, fehlende Videolibrary-Views; diese Befunde sind **historische .78-Fehler**, nicht automatisch als in .79 behoben behaupten.
- Stand .79: `HOST_PASS`, `ANDROID_NOT_TESTED`.

## Geräteregression für die Testbox – unveränderte Kodi-Profile

1. Auf bestehender Kodi-21.3-Testbox aus **GS Media Pilot** oder regulärem GS Media XCMate von .78 auf **.79 aktualisieren** (ohne Deinstallation). Repository nach Updates suchen lassen, Version prüfen, Kodi einmal vollständig neu starten.
2. Ohne Streamstart: Startgruppe/88 Sender, Senderlogos, Jetzt/Nächste, großer unveränderter Hero und richtige Sendungsbilder prüfen. Ein reales Sendungsbild muss **sichtbar** im Hero und EPG für dieselbe Sendung sein, nicht nur IMAGE_DECODED im Log.
3. Filme/Serien: letzte und aktuelle Widget-Einträge samt Providerpostern; „Neu im Kino“ und zusätzliche Nutzerreihen; Fokusrahmen; zweimal Kodi-Neustart, Offline-Covercache/Last-good. Keine vollständige Rückkehr zu Placeholders.
4. Navigation: Home, Live-TV, Filme, Serien, Kino-/Nutzerwidgets, vertikal/horizontal, Zurück/OK; keine Hero-Schrumpfung und keine verschobenen Fokusrahmen.
5. Player-Exit: Serienepisoden, Filme, Live-TV separat spielen und verlassen; Stop-ACK und Rückkehr ohne Hänger. Kein Löschen der Kodi-Bibliotheksdatenbank als Diagnoseversuch.
6. Wenn Fehler bleiben: **sanitisierte** Kodi-Logs und je ein Bildschirmfoto der betroffenen Ansicht; keine Provider-URLs, Passwörter, Token, private Netzwerkinformationen ins öffentliche Issue.

## Codex-Rückmeldung bei Folgeauftrag

Arbeite anhand [Issue #387](https://github.com/artattakk-creator/kodi-noodleprivate/issues/387) und dieses Dokuments weiter. `main` enthält **.79**, Main- und Pilot-Repository bieten die Version an. **Nicht erneut .79 bauen oder mergen**. Erst tatsächliche RK3528-Geräteabnahme der .79 und neue Logbelege auswerten, dann neue kumulative Reparaturversion nur für weiterhin reproduzierbare P0-Fehler entwickeln. Kein voreiliger globaler Skin-Reset, Kodi-DB-Reset, Token-Reimport oder Installer-Update.
