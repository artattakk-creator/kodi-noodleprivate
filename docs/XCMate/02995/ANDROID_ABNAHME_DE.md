# XCMate .95 – Android-Abnahme, Box B / RK3528 / Kodi 21.3

Alle Geräteprüfungen unten: **ANDROID_NOT_TESTED**. Host- und Linux-Kodi-Ergebnisse sind keine Android-Abnahme. Box A bleibt unangetastet. Keine Veröffentlichung, kein Downgrade, keine Deinstallation, keine Daten-/Cache-Löschung.

## Installation und Sicherungsschutz

1. ZIP und `.sha256` aus Draft-PR #465 / `docs/XCMate/test-builds/02995/` herunterladen. SHA256 vor der Installation mit der Textdatei vergleichen.
2. Auf Box B über Kodi → Add-ons → Aus ZIP-Datei installieren kumulativ aktualisieren. Kein neues Repository hinzufügen und keinen Installer ausführen. Installierte Version in XCMate kontrollieren: 0.1.29.95. Bestehende Einstellungen und Kodi-Konfiguration behalten.
3. Vor dem Test Größe/Bestand der vorhandenen EPG-Datenbank, WAL/SHM und Sicherungen dokumentieren, soweit lesend möglich. Keine Dateien verschieben, löschen oder eine neue Sicherung nur auf Verdacht anlegen.
4. Provider-EPG, Kaimandura und CH wie im gemeldeten Test ausgeschaltet lassen; ausschließlich die bereits konfigurierten EPGShare01 DE+AT verwenden. Bestehende Zuordnungen nicht zurücksetzen.

## Kurze P0-Reihenfolge

| ID | Aktion / erwarteter Nachweis | Status |
|---|---|---|
| G95-01 | EPG-Einstellungen nach Update öffnen. Kein endloser Busy-Kreis, Portale und Quellen erhalten. | ANDROID_NOT_TESTED |
| G95-02 | Bestehende Sicherungsfunktion öffnen → „Importfreigabe prüfen – keine neue Sicherung“. Vergangenes BACKUP_VERIFIED und aktuelle Prüfung werden getrennt angezeigt. | ANDROID_NOT_TESTED |
| G95-03 | Vorhandener gültiger DB-/Receipt-/SHA-Nachweis führt zu IMPORT_AUTHORIZED. Kein neuer Sicherungsauftrag und keine neue Sicherungsdatei allein durch Prüfen. | ANDROID_NOT_TESTED |
| G95-04 | Nur DE+AT → Jetzt aktualisieren. Oberfläche bedienbar, Dienstbestätigung und echter Download-Bytezähler. Kein sofortiges pauschales BACKUP_REQUIRED bei Busy/Slow I/O. | ANDROID_NOT_TESTED |
| G95-05 | Pro Quelle echte Parser-/Mapping-/Staging-/Commit-/Readback-Zähler; Abschluss READY oder konkret erklärter Teil-Erfolg. Tatsächliche gespeicherte Zeiträume prüfen. | ANDROID_NOT_TESTED |
| G95-06 | Während eines weiteren Downloads gezielt abbrechen. Bisherige Programme, Quellen und Zuordnungen bleiben lesbar. Kein falsches READY für abgebrochene Quelle. | ANDROID_NOT_TESTED |
| G95-07 | Offline-Importversuch nach gültiger Sicherungsfreigabe. Verständlicher Quellfehler; vorheriger Guide weiter lesbar. | ANDROID_NOT_TESTED |
| G95-08 | Kodi regulär neu starten; vorhandene Autorisierung unabhängig neu prüfen, Guide und Sicherungen weiterhin vorhanden. | ANDROID_NOT_TESTED |

## Lock-, Inventur- und Regressionsteil

| ID | Aktion / erwarteter Nachweis | Status |
|---|---|---|
| L95-01 | EPG-Menü wiederholt während normaler Hintergrundarbeit öffnen. Bei kurzer Sperre sichere vorhandene Portalansicht oder begrenzter Wiederholungshinweis; kein leeres Profil. | ANDROID_NOT_TESTED |
| L95-02 | Erinnerung für zukünftige Sendung speichern, erneut öffnen, Benachrichtigung abwarten. Genau ein Dialog, „Jetzt umschalten“ oder „Verwerfen“, kein Snooze/Autotune. Merkliste erhalten. | ANDROID_NOT_TESTED |
| L95-03 | Im Leerlauf keine sekündliche Folge „ReminderMonitor: profile write busy“. Bei echter Sperre gedrosselter Code und anonyme Timingwerte. | ANDROID_NOT_TESTED |
| I95-01 | Großen vorhandenen EPG-Bestand anzeigen. Eine beschäftigte Quelle darf andere Quellen nicht entwerten; historische Zähler ausdrücklich als historisch markieren. | ANDROID_NOT_TESTED |
| I95-02 | Fehlende Daten und unbekannte Inventur unterscheiden. Kein „0 gespeichert“ allein wegen Timeout/BUSY. | ANDROID_NOT_TESTED |
| R95-01 | Startsender, aktivierte Gruppen, Mini-/Groß-EPG und Fernbedienung unverändert bedienbar. | ANDROID_NOT_TESTED |
| R95-02 | BINGIE-Hero, Logos, sechs Widget-Reihen und persönliche Zusatzwidgets erhalten. | ANDROID_NOT_TESTED |
| R95-03 | Film-/Serienstart, Resume, Autoplay und Live-TV-Zurück prüfen. Native Decoderprobleme separat protokollieren. | ANDROID_NOT_TESTED |
| R95-04 | TMDB-Token, eigene Bildsuche, TVMaze und manuelle Bildzuordnungen unverändert. | ANDROID_NOT_TESTED |
| R95-05 | Nach Hintergrundwartung Guide und alle bisherigen Backup-/Manifest-Dateien vorhanden; kein Pruning durch .95. | ANDROID_NOT_TESTED |

## Nicht auf der eingerichteten Box provozieren

Manipulierte/fehlende Manifeste, künstliche Schemafehler, Datenbank-Exklusivsperren, Low-Space, Archivverschiebungen und konkurrierende Datenbankänderungen werden automatisiert in Wegwerfprofilen getestet. Keine Beschädigung oder absichtliche Verschiebung produktiver Sicherungen für die Abnahme.

Bei Fehler: ID, Version, Zeitpunkt, sichtbaren Code, Dauer und vorhandene Zähler melden. Keine Zugangsdaten oder privaten Rohlogs öffentlich hochladen. Bei DB_BUSY/Timeout zuerst laufende Arbeit abwarten und unabhängig neu prüfen. Fehlende/abweichende Belege niemals umgehen.

## Rückfall und Freigabe

Die bisherigen .94- und .90-Pakete samt Prüfsummen bleiben unverändert erhalten. Kein automatischer Rückbau oder Wechsel des Kodi-Profils. Bei einem Fehler .95 nicht veröffentlichen; vorhandene DB/Backups sichern lassen und eine vorwärtskompatible Korrektur vorbereiten. Eine Rückinstallation wäre eine gesonderte, derzeit nicht autorisierte Maßnahme.

Merge und Repository-Veröffentlichung werden erst separat freigegeben. Auch ein grüner Host-/CI-Lauf erteilt diese Freigabe nicht.
