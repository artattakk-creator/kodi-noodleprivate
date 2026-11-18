# Android-Abnahme für XCMate 0.1.29.99

Status `ANDROID_NOT_TESTED`. Kandidat zu Issue #488 auf der kumulativen .98-Basis aus PR #487. Die Prüfung ist für eine echte RK3528-Box mit Android ARM32, Kodi 21.3 und BINGIE MOD vorgesehen. Installation des Prüfpakets und Tests mit einem bewusst beschädigten Profil setzen eine separate Freigabe voraus.

## Vorbereitung

- SHA256 des Installations-ZIPs gegen die beiliegende Datei prüfen. Version, Box, Architektur, Kodi-Build, Skin und Auflösung dokumentieren.
- Ein Wegwerfprofil oder eine private Kopie des Testprofils verwenden. Für Tests mit defektem XML und wenig Speicher muss sich die Testumgebung unabhängig vom Add-on wiederherstellen lassen.
- Vorab Portale, Token-Datei, EPG-Datenbanken, Zuordnungen, Favoriten, Senderlogos und Skin-Daten inventarisieren. Für statische Dateien Größe und SHA256 erfassen. Für Datenbanken die erwarteten Tabellen und Einträge erfassen, da reguläre EPG-Aktualisierungen nach der Reparatur neue Inhalte schreiben können.
- Protokolle nur auf Codes, Versionen, Dateigrößen und Zähler beschränken. Bildschirmfotos vor der Freigabe auf Zugangsdaten, Portaladressen, Token und persönliche Programmdaten prüfen.

## Reparatur und Neustart

| Test | Ausführung | Erwartung |
| --- | --- | --- |
| A99-01 Update und Abbruch | .99 über eine funktionsfähige .98 installieren. XCMate öffnen, die Reparatur auswählen und mit Nein oder Zurück abbrechen. Kodi neu starten. | Kein Reparaturmarker, keine neue Datei `settings99.before-reset.*.xml`. Benutzerwerte bleiben aktiv. |
| A99-02 Defekt ohne LastGood | Im Testprofil Kodi vollständig beenden. Jeweils abgeschnittenes XML, ungültiges UTF-8, doppelte Einstellungs-ID, falsches Wurzelelement und eine Datei jenseits des normalen XML-Leselimits prüfen. `settings96.lastgood.xml` fehlt. Unter EPG / Sendungsbilder die Aktion **XCMate-Einstellungen vollständig neu erzeugen (ohne LastGood)** bestätigen. | Der Neuaufbau ist erreichbar. `BACKUP_SAVED` und `RESTART_REQUIRED` erscheinen. Das Backup stimmt in Größe und SHA256 mit der bisherigen Datei überein. Im ursprünglichen Kodi-Prozess bleibt die aktive Datei erhalten. |
| A99-03 Wirklicher Prozesswechsel | Kodi über Beenden komplett schließen und neu öffnen. Die Android-Hometaste reicht für diesen Schritt nicht. Kodi-Einstellungen bis zum Abschluss geschlossen lassen. Kodi ein zweites Mal vollständig beenden und neu öffnen. | Erster neuer Prozess: `RESET_WRITTEN`, `READBACK_OK`, `RESTART_REQUIRED`. Zweiter neuer Prozess: `POST_RESTART_OK`. Auf Platte gültige Kodi-Benutzereinstellungen im Format 2. Die native Kodi-API liest den in der Datei gespeicherten Prüfwert und die erwarteten Einstellungen. |
| A99-04 Bestand, Startsender und Privatsphäre | Vor jeglicher erneuter Bildfreigabe Startsender und Live-TV in mehreren Gruppen einschließlich BINGIE-Widgets öffnen. Anbieter-EPG und bestehende manuelle Senderzuordnungen kontrollieren. Die drei optionalen Bildquellen im Status ansehen. | Anbieter-EPG verfügbar. XMLTV-Bilder, TMDB und TVMaze zeigen ihren tatsächlichen abgeschalteten Zustand. Portale, Token-Datei, EPG-Bestand, Zuordnungen, Favoriten und Logos sind vorhanden. |
| A99-05 Fehlende Datei und erneutes Öffnen | Separates Profil ohne `settings.xml` und ohne LastGood verwenden. Die Aktion bestätigen und beide Neustarts durchführen. Danach die Reparatur erneut auswählen, Kodi weiter starten und einen normalen Einstellungswert ändern. | Keine Originalkopie bei fehlender Datei. Konfiguration wird nach Bestätigung einmalig erzeugt. Weitere Starts und erneute Auswahl setzen die Konfiguration nicht zurück. Die normale Änderung bleibt beim nächsten Start erhalten. |
| A99-06 Fehler und Rückfall | Getrennte Profile mit schreibgeschütztem Speicher, Platzmangel, Symlink und einer konkurrierenden Änderung an der Einstellungsdatei verwenden. Den Prozessabbruch vor und nach dem Dateiaustausch in einer kontrollierten Testumgebung auslösen. | Fehlercode und private Originalkopie entsprechend der Phase. Bei Konflikt bleibt der unerwartete Dateistand erhalten. Ein nach Austausch unterbrochener Lauf kann die bereits geschriebene Datei nach vollständigem Neustart prüfen. Keine Erfolgsmeldung vor dem Post-Restart-Test. |
| A99-07 Native Einstellungen | Nach `POST_RESTART_OK` die Kodi-Einstellungen öffnen. Einen harmlosen Wert speichern und nach einem weiteren Kaltstart über Oberfläche, Datenträger und nativen Lesewert vergleichen. | Normale Einstellungen und Lesetests funktionieren. Kodi spielt keine alten Werte zurück. |

## Bildvergleich mit der Referenz .90

1. Dieselben autorisierten Testinhalte, Sender, Zeitfenster und auf die Quelle bezogenen Freigaben verwenden. Den Referenzstand aus `release/xcmate-02990-3channels-20261111` getrennt installieren.
2. Unter .99 erst nach `POST_RESTART_OK` XMLTV-Bilder, TMDB und TVMaze einzeln bewusst freigeben. Für jede Quelle Status, Hero, Details und Mini-EPG bei 720p und 1080p prüfen. Anbieter-EPG mit ausgeschalteten Optionen separat belegen.
3. Einen TMDB-Fall mit funktionierendem direkt zugeordnetem Backdrop und fehlerhaftem Galerieabruf prüfen. Im URL-Modus und bei bewusst gewählter lokaler Ablage die tatsächlich dargestellten Bilder kontrollieren. Zusätzlich einen funktionierenden, priorisierten Galeriepfad sowie manuell gewählte Bilder prüfen.
4. Reporte je Modus und Quelle mit Screenshots festhalten. Sichtbarkeit nach zwei Kaltstarts, längerer Standzeit, Kanal- und Gruppenwechsel, Decoderfehlern sowie Verhalten bei wenig Speicher prüfen. Eine URL, erfolgreiche HTTP-Antwort oder Host-Dekodierung allein reicht für die Android-Abnahme nicht aus.
