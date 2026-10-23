# XCMate – Kumulativer Updatepfad .20 → .21 → .22

**Beschluss vom 23.10.2026 – verbindlich für Codex, Reviews und Android-Tests**

## 1. GitHub-Hauptstand und freigegebener Merge

Repository: https://github.com/artattakk-creator/kodi-noodleprivate  
Add-on-ID: `plugin.video.xtreammate` (unverändert)  
Kodi 21.2 Omega, Android TV 13 RK3528 ARM32, Skin Titan BINGIE MOD, IR-Fernbedienung.

- `0.1.29.20`: vorherige Hauptbasis; historische Rückfalloption, **kein Zwischenschritt für die .22-Abnahme**.
- `0.1.29.21`: PR #109 am 23.10.2026 auf ausdrückliche Nutzerfreigabe unverändert nach `main` gemergt. Merge-SHA `5a634043410b615d0e270a0d9fca2174690f78f1`. 756 Hosttests und CI PASS, Android weiterhin NOT_TESTED. Für Kodi über GS-Media-Repositoriumsindex `addons.xml` gelistet.
- `0.1.29.22`: PR #110 bleibt Draft und wird kumulativ auf aktuellem main .21 überarbeitet, einschließlich Repository-Publishing und dieser Updatepfadvorgabe. Neuer Gesamtbericht `KUMULATIV_02922_DE.md`; alle .21-Funktionen, EPG-Korrekturen und Original-Icon sind enthalten. **Frühere isolierte .22-ZIPs sind überholt und dürfen nicht als Update von .21 verwendet werden.**

**Ab sofort ausschließlich kumulative Versionierung und Updates:** .20 → .21 → .22 → weitere Versionen. Keine Deinstallation von .21, kein künstliches Zurückrollen auf .20, keine getrennten Feature-Releases, die Funktionen vorheriger Versionen entfernen.

## 2. Inhalt und Nachweis für .21

Serien-Autoplay nach natürlichem Episodenende; automatische Fortsetzung einschließlich Staffelwechsel, Stop-/Exit-/Fehlerpriorität, Verhinderung von Doppelstarts, Schalter im eigenen Player, erhaltener manueller Next-/Resume-/Gesehen-Status. Keine Autoplay-Ketten bei Film, Live-TV oder fremden Add-ons.

- PR: https://github.com/artattakk-creator/kodi-noodleprivate/pull/109
- Paket: `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.21.zip` auf `main`.
- SHA256: `f0b64934853f8510eed03679117789a43487a79eee6f7986f4db2dd2d5e1cfe3`.
- Testanleitung: `docs/XCMate/ANDROID_TEST_02921_DE.md`.

**Einschränkung:** Host- und CI-Erfolg sind kein bestandener echter Android-Test; Geräteabnahme bleibt erforderlich.

## 3. Korrigierter Entwicklungsauftrag für .22

1. PR #110 und seinen Branch `fix/xcmate-02922-guide-navigation` auf den **aktuellen `main`-Stand mit .21** stellen; gegebenenfalls frischen Integrationsbranch verwenden, statt ältere Branchstände oder ZIP-Binärdateien einfach zu übernehmen.
2. Sämtliche .21-Funktionen, insbesondere `media_autoplay.py`, Player-OSD, Service-Anbindung und Autoplay-Tests vollständig erhalten.
3. EPG-Verbesserungen aus dem bisherigen .22 isoliert übernehmen: Startgruppe, Startsenderposition, separate Gruppenansicht, Back-/Links-Navigation, sichtbare und lesbare Fokusmarkierung, IR-erreichbare Kopfbuttons. BINGIE MOD und Estuary überprüfen.
4. **Original-XCMate-Icon** verbindlich integrieren: reale 512×512-Originaldatei `themes/xcmate/space-premium/assets/branding/icon-512.png` aus PR #50, SHA256-Referenz `81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135`; Binärdatei und Prüfsumme erneut vergleichen und dann nach `src/plugin.video.xtreammate/icon.png` übernehmen. Kodi-Manifest, ZIP, Skinunabhängigkeit, Icon-Cache und Neustart prüfen. **Ein Original-Icon für Lightweight Core, Space Premium und weitere Themes.** Keine Neugestaltung und kein blinder Vollmerge von PR #50.
5. Version in `addon.xml`, Release-Artefakten, Changelog und allen versionsempfindlichen Tests konsequent `0.1.29.22`; Add-on-ID `plugin.video.xtreammate` und vorhandene Nutzerdatenpfade unverändert.
6. Kumulativen Testsatz aus .21 und .22 + frische GitHub-CI ausführen. Alle Paketbestandteile gegen Sourcebytes, CRC und Pfadsicherheit prüfen. **Altes `0.1.29.22.zip` und dessen alte Prüfsumme sind als überholt zu behandeln**; ein neues vollumfängliches ZIP mit neuer Prüfsumme, Changelog und deutscher Update-Testanleitung generieren.
7. Android-Testsequenz: Auf bereits installierter .21 ohne Deinstallation die neue .22 direkt darüber installieren; Autoplay einschließlich Staffelwechsel/Stop/Resume erneut prüfen; EPG-Fokus/Gruppennavigation/Startsender prüfen; Original-Icon nach Neustart prüfen; Portale, Gruppen, manuelle EPG-Zuordnungen, Favoriten, Artwork und Resume bleiben erhalten. PASS / FAIL / NOT_TESTED dokumentieren.
8. .22 bleibt Draft bis aktualisiertes ZIP, erfolgreiche CI und ausdrückliche Nutzerfreigabe vorliegen. Kein eigenmächtiger Merge, Release, OTA-Indexupdate oder Daten-Reset für .22.

## 4. Weitere geltende Projektvorgaben aus der Übergabe

- Der fehlende Artwork-Downloadpause-Button ist bereits **BLOCKED_UI / NOT_TESTED**: offen dokumentiert, **kein** neuer Artwork-Download, Cache-Löschen oder Rücksetzen nötig.
- Manuelle EPG-Zuordnung innerhalb des großen EPG inklusive Quellenwechsel, Programmdaten-Vorschau, Lang-OK/Context-Menü, quelleneindeutiger IDs und persistenter Portal/Sender-Bindung: Issue #98. Nicht stillschweigend als in .22 gelöst darstellen.
- Space Premium: eigener optionaler Download-/Theme-Installer, kein Kodi-Skin-Wechsel. Alten PR #50 nur selektiv nach Kompatibilitätsprüfung nutzen.
- Externer Artwork-Speicher, Streaming-Stabilität, kontrollierter Katalogabgleich bleiben eigenständige Arbeitspakete (#106, #107, #108).
- Kein Löschen von Portalen, Favoriten, Resume, EPG-Daten oder Caches; keine globalen Kodi-Keymap-Änderungen.

Referenzen: Issues #37 (Original-Icon), #85 (Autoplay), #88/#92 (EPG-Start/Fokus), #98 (EPG-Quellenwechsel), Draft #50 (Space Premium), PR #109 und #110.

## 5. Umsetzung im überarbeiteten Draft #110

Aktuelle Basis `3307e006a9de9fd53236ec881191851291731c98`; normaler Merge in den bestehenden Entwicklungsbranch, kein Force-Push. Sämtliche .21-Autoplay-/Player-/Service-/Artwork-Dateien und die zwei .21-Regressionstestdateien sind unverändert erhalten. Original-Icon SHA256 geprüft und binär übernommen. Aktuelle Zurück-Regel aus dem Nutzerauftrag: Gruppenübersicht schließen → vorige EPG-Ansicht wiederherstellen; Back im Raster → Home. Neue Snapshot-/Repeat-/Fallback-Tests und kumulative Icon-/Daten-/Player-EPG-Tests.

Neue vollständige Prüfnachweise stehen in `TESTERGEBNISSE_02922.json` und `TESTLOG_02922.txt`, aktuelle ZIP-Prüfsumme in `plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.22.zip.sha256` und gepinnter Download/CI-Nachweis in PR #110. Android-Anleitung `ANDROID_TEST_02922_DE.md` gilt für Installation direkt über .21. **Android NOT_TESTED, keine Merge-/Releasefreigabe.**
