# XCMate 0.1.29.98 – unveröffentlichter Prüfkandidat

- Die Artwork- und manuellen EPG-Zuweisungsreparaturen aus PR #484 bleiben vollständig erhalten. Gegen dessen HEAD eb6c0857e4cb3abf20ffb94a0ed31e48b7daf59a ändern sich in den Produktdateien ausschließlich Version und Update-Hinweis der addon.xml.
- Vier aktuelle Versionsverträge erwarten ausdrücklich .98. Zwei historische .96-Pakettests laufen unverändert gegen ihren gepinnten .96-Quellstand in isolierten Prozessen; das tatsächlich aufbewahrte .96-ZIP und seine ursprüngliche SHA-Datei werden vorher geprüft.
- Ein eigener .98-Releasevertrag prüft vollständige Quellbytes, Dateimenge, CRC, SHA256, Manifest, Reproduzierbarkeit und unveränderte Veröffentlichungsbereiche. Manipulierte Pakete, Freigabebits und unzulässige Ausgabeorte werden abgewiesen.
- Der .98-Kodi-Runner übergibt den strikten aktuellen Paketprüfer ausdrücklich an die vorhandenen nativen Engines; der historische .96-Prüfer wird nicht global umgeschrieben.
- Vollständige pytest/unittest und native Linux-Kodi21.2-Tests mit 720p/1080p werden in einem nur leseberechtigten CI-Workflow geprüft. Echte Android-Tests bleiben separat offen.

Keine Änderung an Zugangsdaten, Einstellungen, EPG-Zuordnungen, Bildern, Benutzerwidgets oder veröffentlichten Paketen. Kein Merge und keine Veröffentlichung in diesem Auftrag.
