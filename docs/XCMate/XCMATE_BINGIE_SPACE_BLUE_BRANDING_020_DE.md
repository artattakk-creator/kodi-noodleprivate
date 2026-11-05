# XCMate BINGIE Space Blue Branding Add-on 0.2.0 (2026-11-05)

## Ziel
Eigenständiges optionales Kodi-Programm-Add-on, Add-on-ID `script.gsmedia.xcmate.branding`. Übernimmt **nach explizitem Aufruf** das userbereitgestellte 7,04-s-Video `XCMate-intro.mp4` mit Original-AAC-Sound, einen Videoframe-Splash, metallisches XCMate-Logo aus dem Moodboard und **Space-Blue-Palette** für BINGIE 2.2.3. Die bestehende XCMate-Version und drei Home-Widgets bleiben unverändert.

## Palette und Schichten
- Deep Space `#061322`, Navy `#0A2947`, Electric Blue `#159FEA`, Cyan Focus `#42D9FF`, Ice Text `#E6F5FF`.
- Kodi-Skin-Colorpicker-/`Skin.String`-Palette: Home, Menüs, Rahmenfarbe (keine Geometrie), Panels, Header, Footer, Sidebar, Dialoge, OSD, Scrollbars, Fortschritt, Status und zusätzliche benannte `colors/defaults.xml`-Werte.
- Nur klar verifizierte harte Rotwerte in Brand-XML ändern, keine Bildtexturen.xbt verändern, Warnungs-/Alterseinstufungsfarben bleiben funktional.
- Originalwerte werden vor Anwendung per Skin.String gesichert, Skin-Dateien einzeln im userdata-Backup gesichert. Wiederherstellung überprüft SHA-256 und schützt seit Patch geänderte fremde Werte/Dateien.

## Installationsablauf
1. ZIP in Kodi unter Add-ons → Aus ZIP-Datei installieren auswählen.
2. Add-on unter Programm-Add-ons starten → Status/Vorschau → `Space Blue + Intro installieren` bestätigen.
3. Kodi vollständig beenden/neustarten. Änderungen niemals allein beim ZIP-Install durchführen.
4. `Originalfarben, Logo & Intro wiederherstellen` nutzen, solange Add-on-Daten vorhanden.

## Status und wichtige Grenzen
- Host-Tests: **11 bestanden**, Archivstruktur und enthaltenes User-Video geprüft; Android/Kodi 21.3 Laufzeit/Spielbarkeit **ANDROID_NOT_TESTED**.
- Codec: Full HD H.264, AAC, Dauer 7.041667s; Originaleingabe SHA-256 `5ae825fe8b31ea4d5a747fa5c32ba1c056a7785b3b4251ea2938378225e067c0`.
- Lokale ZIP: `script.gsmedia.xcmate.branding-0.2.0.zip`, SHA-256: `afa32cd38df59e12cf9889f05e2e080f1358ee03a169c7ce6cb211cde2d0fdaa`, 20.44 MB.
- Das Logo stammt aus dem von uns erstellten Moodboard-Asset, **nicht nachweislich** aus einem historischen XCMate-Originaldateiarchiv. Vor dem endgültigen Branding auf das bestätigte Original umstellen, sobald dessen Binärdatei vorliegt.
- Unter `src/script.gsmedia.xcmate.branding` werden Textquellen und Manifest abgelegt; **BINÄRASSETS SIND ERST NACH SEPARATEM UPLOAD** vollständig. Keine Repository-Installation ohne ZIP und Katalogeintrag als fertig bezeichnen.
- Nicht in den regulären GS-Media-Katalog aufnehmen, bevor ZIP binär verifiziert und auf Box B auf dem Gerät getestet ist.
- Bereits bekannte Fokusrahmen-Geometrie- und EPG-Probleme der .74 sind getrennt; Farben dürfen Fokus-/Widget-Layout nicht manipulieren.
