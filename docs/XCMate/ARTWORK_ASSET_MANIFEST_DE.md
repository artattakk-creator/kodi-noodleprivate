# XCMate – freigegebene Grafikquellen, Dateimanifest und Integrationsstatus

**Freigegebene Originale:** 14.10.2026; Design-Freeze bestätigt durch Nutzer.

| Datei im separaten Übergabepaket | Maße | SHA-256 | Status |
| --- | --- | --- | --- |
| `assets/XCMate_logo_approved_source.png` | 573×358 | `ab5fe7f60a200dda22aece2d326b077083915af0c7e3607fa92e145c45c7e693` | Freigegebenes Logo, exakte Nutzerdatei |
| `assets/XCMate_space_approved_source.png` | 1672×941 | `d845920c27f4c328768f833c01d30b0b78f3d4943db1cc8b79a6ae795d14f00e` | Freigegebenes Space-Bild |
| `assets/XCMate_icon_preview_512.png` | 512×512 | `242f41a1a2c5b3eb9b3b6d5e5808a2413ea4edb475f7405c7ac9865c1250ae03` | Abgeleiteter Icon-Entwurf; Freigabe im Kodi-UI noch ausstehend |
| `assets/XCMate_fanart_preview_1920x1080.jpg` | 1920×1080 | `747346927a5f75d60325eafdb405ec7c53bbfdfe5e091a7684af07938da45415` | Abgeleitetes Fanart; Freigabe im Kodi-UI noch ausstehend |
| `assets/XCMate_UI_panel_slate_1280x720.png` | 1280×720 | `63bea660b481d3ce156ba60e6196bdd1f12f04c4f6324080e2ee2f9fbc342cfa` | Abgeleiteter grauer Panel-Entwurf |

**Wichtig – Status:** Diese Datei speichert Bezeichnung und Prüfsummen auf GitHub, aber die im Chat übergebenen binären Originalbilder sind noch nicht über den GitHub-Connector hochgeladen. Das separate ZIP `XCMate_Projektuebergabe_2026-10-14.zip` enthält die vollständigen Rasterdateien. Dieses ZIP sicher lokal archivieren und seine `assets/`-Dateien zusätzlich in den Repo-Ordner `artwork/xcmate/` hochladen, danach über GitHub-Baum/Dateigrößen und SHA-256 verifizieren. **Nicht** behaupten, die Grafikquellen seien bereits auf GitHub, bevor dies geschieht.

### Empfohlene Integration in Kodi (eigener Release notwendig)

1. Das akzeptierte Space-Bild als Fanart `src/plugin.video.xtreammate/fanart.jpg` bzw. pipeline-kompatibles PNG übernehmen; tatsächliche `addon.xml`-Referenz und das build_repository.py-Verhalten kontrollieren.
2. Abgeleitetes Icon in `src/plugin.video.xtreammate/icon.png` integrieren, die volle XCMate-Wortmarke nicht abschneiden.
3. Graues UI-Panel als Xtream-TV-Overlay-Grundfläche verfügbar machen; initiales Farbschema Slate ist Standard.
4. Für den Übergang einen neuen Add-on-Versionssprung, CI-Tests und Android-Bildschirmvergleich durchführen. Kein stiller Ersatz im bestehenden 0.1.9.
5. Zuordnung zu Quellbildern per Prüfsumme nachhalten. Keine neue Bildkomposition eigenmächtig als „Original“ deklarieren.
