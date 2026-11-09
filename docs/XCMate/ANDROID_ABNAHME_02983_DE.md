# Android-Abnahme XCMate 0.1.29.83

Alle folgenden Geräteprüfungen: **ANDROID_NOT_TESTED**.
Box A unverändert lassen. Nur auf der freigegebenen Testbox B testen.
Keine Deinstallation, keine Daten-/Cache-Löschung und kein Installerlauf.
Installer 0.5.26 bleibt unverändert. Private Rohlogs nicht auf GitHub hochladen.

## Installation und Diagnose

1. SHA256 des Test-ZIP mit der beiliegenden Datei vergleichen. In Kodi
   „Aus ZIP-Datei installieren“ auf der bestehenden XCMate-Installation wählen.
   Updates aus regulär/Pilot/NeoDark3 bleiben .82 bis zu gesonderter Freigabe.
2. Version .83 im Updatehinweis/Addon prüfen. Provider, TMDB-Zugang,
   Sendergruppen, Favoriten, Film-/Serienfortschritt und persönliche Widgets
   müssen unverändert vorhanden sein. Keine Zugangsdaten veröffentlichen.
3. Artwork-Verwaltung → „Quell- und Zielspeicher prüfen (nur lesen)“.
   Anonymisierte Rollen mit `total`, `available`, `free`, `reserve`,
   `fs`, `volume`, `mount_key` erfassen. Bytewerte vollständig notieren.
4. „Interner Android-Speicher“ wählen. Vorhandenes Movies direkt über eine
   erreichbare Android-Quelle auswählen. `/storage/` muss dafür nicht listbar sein.

## Harte Gates

| Test | Ausführung / erwarteter Nachweis | Status |
|---|---|---|
| ST83-01 | Update auf .83, alte Konfiguration und alle persönlichen Widgets vorhanden | ANDROID_NOT_TESTED |
| ST83-02 | Quelle und konkretes Movies-Ziel: anonymisierte Volume-Korrelation, f_bavail/f_bfree, total, wirksame Reserve | ANDROID_NOT_TESTED |
| ST83-03 | Selber Pool → TARGET_SAME_CAPACITY_POOL; keine Migration, kein Platzgewinn, keine Zielaktivierung | ANDROID_NOT_TESTED |
| ST83-04 | Nicht nachweisbarer anderer FUSE-Pool → TARGET_VOLUME_UNVERIFIED; keine Scheinmigration | ANDROID_NOT_TESTED |
| ST83-05 | Ziel nicht listbar/fehlende API34-Rechte: verständlicher Code, kein SAF-Grant behauptet, kein /storage-Zwang | ANDROID_NOT_TESTED |
| ST83-06 | Nur bei getrennter verifizierter Kapazität: zunächst Schreibprobe mit Nein abbrechen; keine neuen Ziel-/Journaldateien | ANDROID_NOT_TESTED |
| ST83-07 | Danach ausdrücklich 4-KiB-Probe erlauben; Schreiben/Lesen/SHA/Entfernen erfolgreich, fremde Dateien unverändert | ANDROID_NOT_TESTED |
| ST83-08 | Bestand erfassen und kopieren; echte Anzahl/Bytes, Oberfläche bedienbar; Abbruch und Wiederaufnahme desselben Transfers | ANDROID_NOT_TESTED |
| ST83-09 | SHA256 vollständig prüfen; kopiertes Bild tatsächlich in Kodi sichtbar; Nein darf Aktivierung nicht freigeben | ANDROID_NOT_TESTED |
| ST83-10 | Nach ausdrücklicher sichtbarer Bestätigung aktivieren; Originale vollständig erhalten | ANDROID_NOT_TESTED |
| ST83-11 | Kodi kalt/warm neu starten: gespeichertes Ziel und dortige Bilder korrekt; kein stiller interner Rückfall | ANDROID_NOT_TESTED |
| ST83-12 | Live-TV/Film/Serie starten und mit Zurück verlassen; Resume/Autoplay/Favoriten unverändert | ANDROID_NOT_TESTED |
| ST83-13 | Bei BUSY/Speicherreserveblockade: spezifischer Code, kein Schema-Rebuild, nach Freigabe Fortschritt fortsetzbar | ANDROID_NOT_TESTED |

**Bei ST83-03/04/05 stoppen.** ST83-06 bis ST83-11 sind dann BLOCKED,
nicht PASS. Insbesondere beweist eine unzugängliche /storage-Auflistung keine
fehlenden Schreibrechte auf Movies. Für dessen tatsächlichen Zugriff ist die
eigene Zielvorprüfung maßgeblich.

Die Migration umfasst das bestehende persistente Medien-/Logoarchiv. Programm-
und Kodi-Texturcache sowie Datenbanken bleiben intern. Keine Bereinigung ist
Bestandteil dieser Abnahme. Ein späterer tatsächlicher Platzgewinn darf erst
nach separat freigegebener Originalbereinigung und gemessenen freien Quellbytes
bestätigt werden.

Ergebnis je Zeile mit PASS/FAIL/BLOCKED und anonymisierten exakten Werten
festhalten. Host-/CI-Tests sind kein Android-PASS und lösen #395 nicht automatisch.
