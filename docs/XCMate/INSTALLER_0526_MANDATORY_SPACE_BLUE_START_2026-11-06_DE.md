# Installer 0.5.26 – verpflichtender Space-Blue-Patch und BINGIE-Start
Stand: 06.11.2026

## Status und Nachweise

- **CODE / HOST-CI / MERGE / KODI-KATALOGE: PASS**
- **ANDROID-GERÄTEABNAHME: NOT TESTED**, keine Behauptung eines echten 48/48-Installationserfolgs.
- Installer 0.5.26 ist **kumulativ** aufgebaut aus 0.5.21 → .22 → .23 → .24 → .25 → .26. Keine alten Fixes zurückgenommen.
- [Fix-PR #379](https://github.com/artattakk-creator/kodi-noodleprivate/pull/379), Merge-Commit `75017ad9acb2edcf2a4780e6b6fd00391d343ecd`
- [CI #42272858344](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/42272858344): **SUCCESS** für Hosttests (Paket, CRC, 48-Plan, 7 Pilot-Abhängigkeitsbrücken, Skin Icons, Brand-Manager-Origin, Logo/Intro/Splash-Assets und Abschlussregel).
- Veröffentlichung `main`: `dd284f5b3a43ee7406ec3cddcdb3c04cdfdb30a6`
- Installer-ZIP Git-Blob SHA identisch in allen drei Zugängen: `f8bfbbe032bcf11e2ddb713fd1325ed2599dfbb1`
- SHA256: `5aa5d101a57adda5dbb1f5d05319da1ec185676dc784817b25dea267322ae0af`

## Verbindliche Installationsfolge

1. Bisherige **48 Pflichtkomponenten** nach frischer Kodi-Inventur und Mindestversionen prüfen; bei bereits installiertem und aktiviertem gültigem Add-on *nicht neu installieren*.
2. Bei alten bzw. fehlenden freigegebenen Pilot-Abhängigkeiten quellspezifischen Parent-Bridge-Resolver aus **0.5.25** verwenden. Dieser löst den zuletzt fotografierten `KODI_CATALOG_VERSION_TOO_OLD:script.module.jurialmunkey`-Stopp bei 23/48 durch einen freigegebenen, vorhandenen 0.1.0-Pilot-Parent zur Originalversion >=0.2.35. Auch frühere Skin Shortcuts 2.1.0 und Skin Icons 1.0.5 Fixes bleiben eingebaut.
3. BINGIE MOD 2.2.3 und alle Skin-/Shortcut-Dateien **mit Originalhash und Backup** sicher patchen.
4. xVAULT und TMDB-Player prüfen; vorhandene Einstellungen nicht überschreiben.
5. **Neue verbindliche Extra-Komponente (nicht 49. alter Paketplan):** GS Media Pilot `script.gsmedia.xcmate.branding 0.2.0` muss installiert, aktiviert und von Kodi JSON-RPC bestätigt sein. Bei schon installiertem gültigem Paket wird nicht erneut InstallAddon aufgerufen.
6. Original-Titan-BINGIE-MOD-Skin aktivieren und dessen Aktivierungsstatus prüfen. Falls Kodi einen Aktivierungsdialog zeigt, muss dieser abgeschlossen sein.
7. Den bereits veröffentlichten, rückbaubaren **XCMate BINGIE Space Blue Manager 0.2.0** automatisch ohne zusätzlichen manuellen Add-on-Menüaufruf ausführen. User consent steht in den bestehenden Erststart-/Wiederaufnahme-Dialogen. Das Paketsicherungssystem erstellt Originalbackups, übernimmt Intro-Video, Splash-Fotos, XCMate-Logo, StartUp-Timing und Space-Blue-Farbpalette. Widget-Routen, EPG, Sender-/Film-/Seriendaten, Fokusgeometrie und Kodi-Userdata bleiben unangetastet.
8. **Pflicht-Abschlusskontrolle:** `branding_patch.status` muss `state=active`, `matched=total>0` für Dateien und `color_matched=color_total>0` für Skin-Farbwerte melden. Bereits erfolgreich installierter Branding-Patch = VERIFIED (idempotent). Bei beschädigter, unvollständiger oder fremder Branding-Konfiguration **sicher stoppen**, nie überbügeln oder fälschlich 100% melden. Bei explizit deaktiviertem Intro oder unbekanntem Intro-Modus ebenfalls sicher stoppen, nicht unbemerkt andere Skin-Preferences verändern.
9. Erst nach allen Bedingungen `mark_restart_pending`, Journal `stage=done`, 100%-Anzeige und Kodi `Quit`. **Android öffnet Kodi nicht eigenständig neu**; Nutzer startet die Kodi-App erneut. Der bereits aktivierte BINGIE-Skin soll dann mit Space-Blue-Logo/Palette und Intro hochfahren. Echten On-Device-Neustart als eigene Abnahme prüfen.

Die Vorgabe **kein Abbruch wegen bloß vorhandener Add-ons** gilt fort; nur nicht erfüllte Mindestversionen, fehlende Pakete, unbestätigte Integrität oder echte Konflikte dürfen einen begründeten Schutzstopp auslösen.

## Veröffentlichung

Drei nutzbare Installationspfade in **einem GitHub-Repository**, davon zwei Kodi-Kataloge + ein NeoDark3-Direktzugang:

- [Reguläres GS Media Installer 0.5.26](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip)
- [GS Media Pilot ZIP 0.5.26](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip)
- [NeoDark3 Direkt-ZIP 0.5.26](https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/online-test/script.gsmedia.setup-0.5.26.zip)
- Root `addons.xml` / `addons.xml.md5`: 0.5.26 / `488d434f45e2e41751a46df51b20cd86`
- Pilot `online-test/addons.xml` / `online-test/addons.xml.md5`: 0.5.26 / `ae0f324f94f367ed5222a55c730f3356`
- `online-test/manifest.json`: `wizard.version=0.5.26`
- Version 0.5.25 und ältere ZIP-Dateien bleiben erhalten.
- Space Blue Manager 0.2.0: Git-Blob `819eaba64ff715c7f90536fdd55dd05bc1bd2716`, im Pilot unverändert vorhanden.

## Android-Abnahme (offen!)

1. Kodi 21.3 Omega – auf bestehender Testbox Installer 0.5.26 aus regulärem oder Pilot-Katalog aktualisieren. GS Media Pilot muss installiert und aktiviert sein.
2. **Fortsetzen**, nicht zurücksetzen oder bestehende Add-ons deinstallieren.
3. Prüfen, ob der bekannte **23/48-Jurialmunkey**-Schritt nun die Version >=0.2.35 aktiviert bestätigt und die restlichen Schritte bis 48/48 laufen.
4. Am Ende muss Space Blue automatisch als weitere Abschlussbedingung installiert/übernommen und vollständig geprüft werden. Bei `SPACE_BLUE_*`-Stopp anhand Kodi-Log untersuchen. Keine falsche Erfolgsmeldung.
5. Auf Abschlussmeldung Kodi beenden lassen, danach Kodi **manuell neu starten**. Aktiven Skin, Intro-Video, Logo, Splash, Space-Blue-Menüs/OSD und EPG/Widgets prüfen. Erst dann Gerätetest PASS dokumentieren.

**Wichtig:** Dieses Update erstellt keine Android-Firmware und kein eigenständiges OS-Image. Es installiert den verifizierten BINGIE MOD plus Space Blue und richtet Kodi auf den Start damit ein.
