# XCMate Media Center Installer 0.5.22 – Pilot-Release am 06.11.2026

**Status:** SOURCE/PACKAGE/CI PASS – **ANDROID NOT TESTED**.  
**Gerät:** Kodi 21.x Omega, insbesondere Kodi 21.3 / Android RK3528 erst am Zielgerät zu prüfen.  
**Installationskanal:** GS Media Pilot 1.9.12 + NeoDark3. Das reguläre GS-Media-Repository bleibt bei Installer 0.5.21.

## Lieferdateien

- **Kodi-Direkt-ZIP:** `online-test/script.gsmedia.setup-0.5.22.zip`
- **Pilot-Repo-Add-on-Datadir:** `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.22.zip`
- **SHA-256:** `66d98c8dc8061007f5dfbd82eeea483634730d915750e7677c9b6c0ff2fd8f91`
- **Checksum-Datei:** `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.22.zip.sha256`
- **Pilot-Index:** `online-test/addons.xml` + `online-test/addons.xml.md5`
- **Manifest:** `online-test/manifest.json`
- **Kodi-HTML:** `online-test/index.html`, sichtbarer Linkname exakt identisch mit href.
- **Download (GitHub raw):** https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup-0.5.22.zip
- **Test-Workflow:** https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42258842453 (**SUCCESS**).
- **Entwicklungs-PR:** https://github.com/artattakk-creator/kodi-noodleprivate/pull/371 (gemergt).
- **Merge-Commit:** `b034d99e7bc3e42cda97f93b46f1f492c3b8f30f`.
- **Pilot-Publikations-Commit:** `7181114d13edf39ccf072e60782c1354f4d2d8a4`.

## Konkrete Korrektur

In Installer `0.5.21` ersetzte `setup_auto_ui50.py` beim BINGIE-Repo-Schritt `InstallAddon(repository.titan.bingie.mod)` durch `InstallAddon(script.gsmedia.bingie.bootstrap)`. Dieser eigene Parent enthielt gleichzeitig `repository.titan.bingie.mod >=2.0.1` und `script.bingie.helper >=1.1.2`; Kodi-Omega-Origin-Auflösung konnte dessen abhängige Pakete nicht verlässlich erreichen.

`0.5.22` installiert zuerst das originale `repository.titan.bingie.mod` als **separates Paket**, bestätigt Kodi-Inventar, Aktivierung und Mindestversion, prüft `script.module.simplejson >=3.17.0`, und installiert danach den originalen `script.bingie.helper`. Neue Stop-Ursachen: `BINGIE_REPOSITORY_TOO_OLD`, `SIMPLEJSON_3_17_OFFICIAL_NOT_VERIFIED`, `KODI_CATALOG_VERSION_TOO_OLD`. Der zuvor gescheiterte Sammel-Bootstrap wird nicht mehr verwendet.

Bewahrt: bestehendes **Schema-2-Journal** und die 48 ursprünglichen Prüfschritte; vorhandene Profile, EPG-/Provider-Einstellungen, Skin-/Shortcut-Konfigurationen, TMDB-Zugang und Datenbanken; bestehender SlyGuy-Fix. Kein Downgrade, keine Deinstallation und kein Cache-Purge.

## Sicherer Test auf der Box

1. `repository.gsmedia.pilot` **1.9.12** bereits installiert/aktiv haben; andernfalls zuerst ZIP aus NeoDark3 installieren. Der Installer installiert das Pilot-Repo **nicht automatisch**.
2. In Kodi `Add-ons → Aus ZIP-Datei installieren → NeoDark3 → script.gsmedia.setup-0.5.22.zip`. Oder über `GS Media Pilot → Programm-Add-ons → XCMate Media Center Installer → Aktualisieren`.
3. Installer erneut öffnen und den **vorhandenen Installationslauf fortsetzen**; nicht neu starten, nicht zurücksetzen.
4. Zuerst `repository.titan.bingie.mod >= 2.0.1`, dann `script.module.simplejson >= 3.17.0`, dann `script.bingie.helper >= 1.1.2` und verbleibende Komponenten. Bei blockierter Quelle vollständigen Fehlertext und Kodi-Log der Testbox sichern.
5. Verifiziert ist der Host-Build und der Kodi-Katalog, **nicht** die tatsächliche Installation auf Android. Unverifiziertes BINGIE/Space-Blue-Postboot und weitere Paketabhängigkeiten dürfen nicht als PASS markiert werden.

## Bekannte Grenzen

- Ein fehlendes Pilot-Repository wird sicher angehalten; eine zuverlässige automatische Bootstrap-Nachinstallation ist **nicht** Bestandteil dieses Hotfixes.
- Bei altem/unbekanntem originalen BINGIE-Repo oder fehlender offizieller `simplejson`-Version hält die Installation kontrolliert statt ungesicherte Quellen zu nutzen; nötigenfalls Originalquelle in Kodi prüfen.
- Die gesondert dokumentierte vollständige automatische Space-Blue-Integration ist nicht durch diesen BINGIE-Abhängigkeits-Hotfix abgenommen.
- Funktionaler Android-Gerätetest / vollständiger 48/48-Wizard-Durchlauf bleibt **ANDROID_NOT_TESTED**.
- GitHub-Pages- und TinyURL-Redirect-Verfügbarkeit für NeoDark3 konnten extern nicht unabhängig bestätigt werden; die genannten `online-test`-Dateien sind aber auf `main` nachweislich vorhanden.

**Release-Bewertung:** Ein echter neuer, host-validierter **Pilot-Testkandidat**. Noch keine stabile Android-Freigabe oder Produktions-Release.
