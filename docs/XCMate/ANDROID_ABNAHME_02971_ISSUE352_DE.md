# XCMate .71 / GS-Media-Setup .5.20 – Android-Abnahme #352

Ziel: TX60Pro, Allwinner, Android API 29, Kodi 21.3 ARM32. **Alle Gerätefälle zunächst NOT_TESTED.** Host-/Linux-Kodi-PASS darf hier nichts überschreiben.

Nur kumulatives ZIP-Update, keine Deinstallation, kein Downgrade, kein Profil-/Cache-Reset. Kodi-Datenpfad und alle 48 Komponenten erhalten. Zunächst Paket-SHA256 vergleichen; die Prüfsumme der äußeren GitHub-Artefaktdatei ist nicht die Prüfsumme des inneren Kodi-ZIPs.

Das Testpaket enthält plugin.video.xtreammate-0.1.29.71.zip und das getrennte script.gsmedia.setup-0.5.20.zip. XCMate zuerst regulär aus ZIP aktualisieren. Das Begleitupdate betrifft nur den Postboot-Service; den 48-Komponenten-Installer nicht erneut starten. Beide Versionsnummern kontrollieren. Keine Skin-Dateien oder Keymaps manuell ersetzen.

| ID | Ablauf / Nachweis | Status |
|---|---|---|
| SET71-01 | Vorher installierte Komponentenanzahl/Versionen, aktiven Skin, vorhandene Portale und Konfiguration feststellen. Nach Update gleiche 48 Komponenten, EPG, TMDB und Kodi-Einstellungen vorhanden. Änderungspopup .71 sichtbar. | NOT_TESTED |
| SET71-02 | Wizard starten: vorhandene Konfigurieren-Zugangsdaten übernehmen. Eine Anmeldung und anschließend Gruppenabruf; kein automatisches Wiederholen. AUTH/GROUPS-Marker und tatsächliche Gruppenanzahlen prüfen. | NOT_TESTED |
| SET71-03 | Live-, Film-, Seriengruppen einzeln an-/abwählen; Fokus und unabhängige Auswahl behalten. Button „Startgruppe“ mit der Fernbedienung erreichen; gewünschte ausgewählte Gruppe bestätigen. Abbrechen des Dialogs ändert nichts. | NOT_TESTED |
| SET71-04 | Weiter → Katalogprüfung → „Portal sicher speichern“. Erfolg nur mit READBACK_DONE/COMMIT_DONE und tatsächlich sichtbarer Auswahl. Backupmanifest vorhanden und Prüfsummen gültig. | NOT_TESTED |
| SET71-05 | Wizard verlassen, XCMate erneut öffnen, anschließend Kodi regulär neu starten. Genau dieselben Gruppen und Startgruppe sowie gleiche Provider-Verbindung vorhanden. Kein doppeltes Portal. | NOT_TESTED |
| SET71-06 | Drei kontrollierte Wiederholungen/Öffnungen und Speicherversuche; keine fortlaufende Discovery-Schleife und keine doppelten Portale. Vorhandene Daten nicht zum „Erstinstallations-Test“ löschen. | NOT_TESTED |
| SET71-07 | Erreichbarkeit des Testproviders kontrolliert unterbrechen / Timeout abwarten. Zurück, Abbrechen und Retry funktionieren; gespeicherte Verbindung und Auswahl bleiben erhalten. Keine Geheimnisse in Fehlermeldungen. | NOT_TESTED |
| SET71-08 | SETUP71 PROBE am tatsächlichen Kodi-Pfad auswerten: verfügbare Bytes, Backend, errno, Checkpointstatus und read-only quick_check. Root-Belegung nicht mit Datenpartition verwechseln. Kein Datenreset. | NOT_TESTED |
| SET71-09 | Lokalen Speicherfehler/DB-Lock nur mit einer separaten Testkonfiguration simulieren. Kein echter Datenträger wird vollgeschrieben. Fehler muss sichtbar bleiben, kein erfundener Save-PASS; alter Zustand lesbar. | NOT_TESTED |
| SET71-10 | Legacy-Übernahme dreimal auslösen, sofern entsprechende Einstellungen existieren. Kein Selbst-Refresh, keine doppelten Einträge, kein GetDirectory-Fehler. Fehlende Legacy-Einstellungen sind kein Fehler des Providers. | NOT_TESTED |
| SET71-11 | Kodi nach vorhandenem GS-Media-Restart-Marker starten: erst nach aktiver, stabiler BINGIE-GUI prüfen. Bei absichtlich anderer Skinwahl ausstehende Prüfung, keine erzwungene Umschaltung und kein erneuter Installationslauf. | NOT_TESTED |
| SET71-12 | Backup/Restore zunächst in isolierter Kopie prüfen; Manifest-SHA256 vergleichen. Kein automatisches Zurückspielen in das Produktivprofil und kein Löschen von Datenbanken. | NOT_TESTED |
| REG71-01 | Startsender, einmal Live-Back, erneut öffnen; bisheriger Decoder-/Kompatibilitätsmodus unverändert. | NOT_TESTED |
| REG71-02 | Großer EPG, Mini-EPG, manuelle Mappings, BINGIE-Live-/Film-/Serienwidgets und Suche auf offensichtliche Regression prüfen. Widget-Routen unverändert. | NOT_TESTED |
| REG71-03 | Film-/Serienstart und Rückkehr, Resume und staffelübergreifendes Autoplay prüfen. Cover und originales XCMate-Icon vorhanden. | NOT_TESTED |

Pro Fall Gerät, Version, lokale Uhrzeit, Beobachtung und PASS/FAIL/NOT_TESTED erfassen. Nur feste SETUP71-Diagnosezeilen mit Mengen und Fehlercodes weitergeben. Rohe Kodi-Logs, Provideradressen, Tokens und Verbindungsdetails nicht öffentlich hochladen.

## Sicherung und kontrollierter Restore

Unter dem unveränderten XCMate-Add-on-Datenpfad liegt setup_backup71/before-*/manifest.json. Das Manifest nennt Existenz, Länge und SHA256 der gesicherten Konfigurationsdateien. Token-/Providerdateien können vertraulich sein: den Backupordner nicht in GitHub oder Support-ZIPs hochladen.

Vor einem manuellen Restore Kodi beenden und zuerst den aktuellen Zustand separat sichern. Backup und Manifest in einer isolierten Kopie prüfen, beide Konfigurationsstände vergleichen; neuere Benutzereingaben dürfen nicht blind überschrieben werden. Nur nach ausdrücklicher Freigabe exakt verifizierte Konfigurationsdateien wiederherstellen. Die Add-on-Version bleibt neu; keine Deinstallation und kein Downgrade. Bei zuvor fehlenden Dateien keine automatischen Löschaktionen ausführen. Portale/Gruppen/EPG-Konfiguration möglichst gezielt übernehmen, keine SQLite-/Artwork-/Kodi-Texturecache-Dateien löschen oder austauschen.

Die Hosttests beweisen bytegenaues Backup und Cold-Readback einer synthetischen Konfiguration; ein echter Android-Restore ist NOT_TESTED. Bei unsicherem Backend oder fehlgeschlagener Verifikation abbrechen und Diagnose behalten.
