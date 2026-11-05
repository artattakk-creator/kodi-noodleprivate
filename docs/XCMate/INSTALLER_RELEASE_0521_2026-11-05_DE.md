# XCMate Media Center Installer – Repository-Freigabe 0.5.21 (05.11.2026)

- **Add-on-ID:** `script.gsmedia.setup` (unverändert)
- **Kodi-Kategorie:** Programme (Extension `xbmc.python.script`)
- **Sichtbarer Name:** XCMate Media Center Installer
- **Version:** 0.5.21 (ersetzt Pilot-0.5.20 mit veraltetem sichtbaren Titel „XCMate Media Center Setup – v0.5.19 – Kodi 21.3 Omega“)
- **Paket:** `script.gsmedia.setup/script.gsmedia.setup-0.5.21.zip`
- **Pilot-Kopie:** `online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.21.zip`
- **Quellen:** gleiche bisherigen 31 sonstigen ZIP-Dateien, ausschließlich `script.gsmedia.setup/addon.xml` geändert; bisheriges Programm- und Installationsverhalten bleibt bestehen
- **Reguläres Repository:** `addons.xml` + `addons.xml.md5`, GS Media Repository 1.8.1
- **Pilot-Repository:** `online-test/addons.xml` + `online-test/addons.xml.md5`

## Wichtige Einschränkung

Der Installer wurde als **Entwicklungskandidat** übernommen. Eine vollständige Android-21.3-/BINGIE-2.2.3-Abnahme der Installationskette und aller externen Abhängigkeiten ist ausstehend. Bereits im Add-on enthaltene Schutz- und Zustimmungsvorgaben bleiben bestehen. Der Installer soll nicht automatisch starten oder bestehende Kodi-/XCMate-Profile überschreiben. Die Verfügbarkeit im regulären Repository bedeutet **nicht**, dass eine vollständige One-Click-Neuinstallation auf Android bereits erfolgreich bestätigt ist.

## Prüfung

Paketinneres `addon.xml` und beide Katalogeinträge tragen dieselbe ID, Version und den Namen; ZIP-Einträge sind gegenüber 0.5.20 bis auf dieses `addon.xml` unverändert. Kodi ordnet die Add-on-ID dank `xbmc.python.script` unter **Programme** ein. Katalog-MD5 neu berechnet; tatsächliche Installation auf der Box muss noch getestet werden.
