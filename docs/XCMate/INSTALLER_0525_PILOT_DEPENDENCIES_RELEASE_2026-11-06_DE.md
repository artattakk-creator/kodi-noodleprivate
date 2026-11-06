# GS Media Media Center Installer 0.5.25 – Pilot-Abhängigkeitsbrücken (06.11.2026)

## Status

- **GitHub-Paket, Hosttests, CI und Veröffentlichung: PASS.**
- **Android-Geräteabnahme: NOT TESTED**, insbesondere Fortsetzen der pausierten Einrichtung von 23/48 auf Kodi 21.3 Omega.
- Kumulatives Update mit allen Fixes aus 0.5.21 → 0.5.22 → 0.5.23 → 0.5.24 → **0.5.25**.
- Kein Löschen bestehender ZIPs, Userdata, EPG-Daten, Skins, Widgets, Profile oder Installationsjournale.

## Gemeldeter Android-Fehler

Bei **23 von 48 Komponenten** zeigt der pausierte Installer:

```text
XCMate – sicher angehalten
KODI_CATALOG_VERSION_TOO_OLD:script.module.jurialmunkey
Keine Daten gelöscht. Nach Korrektur wiederaufnehmen.
```

Die Fehlerbehandlung nutzte `Addons.GetAddons(installed=false)` für die globale Kodi-Version. Diese kann eine ältere Version als die originale, bereits im GS Media Pilot verfügbare Zielversion anzeigen. Der Pilot enthält **`script.module.jurialmunkey 0.2.35`** sowie den nativen Installationsparent **`script.gsmedia.upgrade.script.module.jurialmunkey 0.1.0`**. Beide ZIP-Dateien wurden im Repository vor dem Build geprüft. Die 0.5.24-Variante stoppte vor der Parent-Installation mit `KODI_CATALOG_VERSION_TOO_OLD`. Es fehlt für diesen konkreten Fall **keine Pilot-Katalogdatei**.

## Fix 0.5.25

`tools/gsmedia_setup0525/overlays/resources/lib/setup_auto_ui50.py` enthält eine reine, quellengebundene Auswahlfunktion `_native_pilot_bridge`. Nur `INSTALL_ADDON` / `INSTALL_UPGRADE` und nur folgende vorab geprüften, im Pilot-Katalog einschließlich Original-ZIP und Parent-ZIP vorhandenen Komponenten sind erlaubt:

1. `script.bingie.helper` (1.1.2)
2. `script.module.jurialmunkey` (0.2.35)
3. `script.module.resolveurl` (5.1.212)
4. `script.module.resolveurl.xxx` (2.1.44)
5. `plugin.audio.m3sr2019` (2026.1.0)
6. `script.ezmaintenanceplus` (2026.04.05.0)
7. `plugin.video.cumination` (1.1.206)

Für fehlende oder zu alte Komponenten wird der eindeutige GS-Media-Pilot-Installationsparent der Version **0.1.0** verwendet, dessen Dependency die geforderte Originalversion referenziert. Der Installer prüft die Parent-Version und nach Installationsversuch mittels **frischer Kodi-JSON-RPC-Inventur** die **tatsächlich installierte, aktivierte Zielversion** gegen das echte Mindestmaß. Nur danach wird der Schritt als erledigt gezählt; vorhandene korrekte Versionen werden übersprungen.

`tools/gsmedia_setup0525/overlays/resources/lib/setup_origin_guard52.py` erlaubt die temporäre Kodi-Quellenregel ausschließlich für diese sieben bereits geprüften IDs und die vorher vorhandenen explizit freigegebenen Skin-Shortcuts-, Skin-Icons- und SlyGuy-Ziele. Vor Änderung: atomare Sicherung der bisherigen Kodi-Einstellungen, automatische Updates vorübergehend aus, Zustimmungsdialog. Nach Abschluss, Fehler oder Neustart: Wiederherstellung der ursprünglichen Kodi-Einstellungen.

Bestehende Fixes bleiben erhalten: BINGIE-Repositories/Helper, Skin Shortcuts 2.1.0, originale Skin Icons 1.0.5, Wiederaufnahmejournal, vorhandene xVAULT-/xImage-Pakete, persönliche TMDB-Player-Einstellungen.

## GitHub-Nachweise

- [Fix-/Merge-PR #378](https://github.com/artattakk-creator/kodi-noodleprivate/pull/378)
- Merge SHA: `e863a8356a16d2c3ab5c74914d649c758abc5b56`
- [GitHub Actions Hosttest #42269250540](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42269250540): **SUCCESS**. Einschließlich sieben Parent-/Target-Pakete, 48er-Plan, fehlend/vorhanden/veraltet, Negativtests für nicht erlaubte Quellen, Original-Skin-Icons-Pin, Kodi-Katalogprüfung.
- Auto-Publish auf `main`: `d63be6e13a9b5abdd63630645cf0defd094cf3c5`
- **Alle drei Installer-ZIPs byteidentisch:** Git-Blob `4d2dab1c7ce4f85dc339f1b9344c32c69f51ca6e`
- ZIP SHA256: `0b3706a114e16869860b0842857cc670217a914f124d4ffaad7cae5a2f0a95aa`
- Root `addons.xml`: Installer 0.5.25, MD5 `aa9d1ce5db7ed49c62ea692893090b60`
- Pilot `online-test/addons.xml`: Installer 0.5.25, MD5 `f6e4643e6aa405331df6fc8a3c537e9c`
- `online-test/manifest.json`: `wizard.version=0.5.25`
- Original Skin Icons 1.0.5 im Pilot unverändert verfügbar.

## Bereitstellung (drei Kodi-Zugänge, nicht drei eigenständige GitHub-Repositories)

- [Reguläres GS Media ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/script.gsmedia.setup/script.gsmedia.setup-0.5.25.zip)
- [Pilot Add-on-Datadir](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.25.zip)
- [NeoDark3 Direkt-ZIP](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup-0.5.25.zip)

## Android-Abnahme

1. Auf der bestehenden Testbox Kodi 21.3 den GS Media Installer auf **0.5.25** aktualisieren; das GS Media Pilot Repository muss weiterhin installiert und aktiviert sein.
2. **Fortsetzen** wählen, Installationsjournal und bereits abgeschlossene 23 Komponenten nicht zurücksetzen.
3. `script.module.jurialmunkey >= 0.2.35` installiert + aktiviert nachweisen und kontrollieren, ob der Lauf mindestens zu 24/48 weitergeht.
4. Prüfen, ob die verbleibenden Schritte das gleiche Quellenproblem zeigen. Anderenfalls genaue Kodi-Fehlermeldung + Log erfassen; **48/48 real nicht behaupten**, solange nicht auf dem Gerät erreicht.
5. Nach Abschluss Kodi-Quellenregel, Skin, EPG, Widgets, xVAULT und persönliche Einstellungen kontrollieren.

Dieser Bericht ist die verbindliche Übergabe für spätere Codex-Arbeiten.
