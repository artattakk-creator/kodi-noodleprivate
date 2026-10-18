# XCMate 0.1.20 – Cache-Ordner per Dateibrowser und Kodi-Stabilität

* Unter **Konfigurieren → Cache & Daten → Cache-Verzeichnis** öffnet OK den Kodi-Ordnerbrowser. Ausgewählter Ordner wird durch Kodi gespeichert; ein leeres Feld nutzt den internen XCMate-Cache.
* Nicht erreichbare ausgewählte Cache-Verzeichnisse fallen auf den internen Ordner zurück; gespeicherte Einstellungen werden nicht gelöscht.
* **Cache jetzt leeren** entfernt ausschließlich 32-stellige XCMate-Cache-Schlüssel (JSON), nicht fremde JSON-Dateien in einem gemeinsam genutzten Ordner.
* Neues Sicherheitsprofil: **EPG → Automatische Hintergrund-Downloads (EPG/Kataloge) erlauben** ist bei Neuinstallation standardmäßig AUS. Ein bestehender Anbieterzugang, manuelles EPG-Laden und das Overlay bleiben vorhanden.
* Das Hinzufügen eines DACH- oder Länder-Pakets löst keinen automatischen Massendownload mehr aus. Einzelne Quellen können gezielt manuell aktualisiert werden.
* Installieren erst, nachdem Kodi ohne XCMate wieder stabil läuft. Gespeicherte Portalzugänge und manuelle EPG-Zuordnungen werden nicht angefasst.

Der Update-Build auf GitHub ersetzt keinen Android-TV-Laufzeittest. Die Ursache eines global blockierten Kodi kann weiterhin außerhalb von XCMate liegen. Für gezielte Diagnose wird `special://logpath/kodi.log` benötigt (Zugangsdaten vor Weitergabe unkenntlich machen).
