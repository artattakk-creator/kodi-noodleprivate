# .92 Android-Abnahme – Kodi 21.2/21.3, RK3528 ARM32

Alle Zeilen zunächst ANDROID_NOT_TESTED. Box A bleibt unverändert. Nur auf ausdrücklich freigegebener Testbox kumulativ per ZIP aktualisieren; nicht deinstallieren. .90-ZIP/SHA und Profilbackup außerhalb der Bereinigungsziele sichern. Nicht den 48-Komponenten-Installer erneut ausführen.

Vor Beginn Version, Gerät, Android-/Kodi-Version, Montagezustand und Uhrzeit notieren. Keine privaten Rohlogs oder URLs auf GitHub hochladen. Inventur/Prüfberichte enthalten Kategorien und opaque Volume-IDs, keine Zugangsdaten.

| ID | Schritt und messbares Soll | Status |
|---|---|---|
| ST92-01 | Speicherinventur vor Update/Wartung: belegte/freie Bytes, Total, Mount/Volume, Bild-/EPG-/Cache-/Kodi-Klassen; Android-Quota bei Unbekannt klar kennzeichnen | ANDROID_NOT_TESTED |
| ST92-02 | Update .91→.92 und ältere freigegebene Bestandsinstallation: Portale, Token, Gruppen, EPG, Favoriten, Resume, persönliche/fremde Widgets und Space Blue unverändert | ANDROID_NOT_TESTED |
| ST92-03 | Automatische Wartung: Journalabschluss, exakte entfernte eigene Bytes, freie Bytes vorher/nachher. Kein Delta nicht als Gewinn ausgeben; alte nicht schrumpfbare DB deutlich ausweisen | ANDROID_NOT_TESTED |
| ST92-04 | Wartung abbrechen/Neustart/wiederholen; aktive DB/WAL, Reminder, Backups, Profile und .90-Fallback unverändert, keine Boot-Löschschleife | ANDROID_NOT_TESTED |
| USB92-01 | USB live messen; interner Movies-Ordner gleichen Pools muss abgelehnt werden. Rechtefehler, fehlendes USB und unbekannte Kapazität eindeutig | ANDROID_NOT_TESTED |
| USB92-02 | Probe ausdrücklich bestätigen. Maximal 1–2 GiB geeigneten Pilotbestand mit geschützter Reserve kopieren; SHA/Readback aller Dateien, Originale unverändert | ANDROID_NOT_TESTED |
| USB92-03 | Kopie unterbrechen, erneut öffnen, fortsetzen; Kollision/Dateiänderung blockiert Aktivierung. Bildprobe tatsächlich sichtbar bestätigen | ANDROID_NOT_TESTED |
| USB92-04 | Vor Kodi-Neustart Aktivierung verweigert; nach Neustart erneute SHA-Prüfung, Ziel aktiv. Abziehen/Neustart/Remount ersetzt keine Zielwahl stillschweigend | ANDROID_NOT_TESTED |
| USB92-05 | Erst gesondert doppelt bestätigen: interne Originale entfernen. Freie interne Bytes vor/nach sowie entfernte Bildbytes notieren. Keine DB-/Profil-Löschung | ANDROID_NOT_TESTED |
| NAS92-01 | Bestehenden NAS-Manager prüfen: Kapazität unbekannt nicht als bestätigt ausgeben; Offline bewahrt Wahl/Daten. .92-USB-Prüfung nicht mit NAS gleichsetzen | ANDROID_NOT_TESTED |
| SET92-01 | Nur neue freigegebene Setup-Testinstallation: .5.29 mit .92; Ja/Nein/Später und intern/USB/NAS/später, Abbruch/Wiederaufnahme, keine doppelte Abfrage | ANDROID_NOT_TESTED |
| EPG92-01 | Drei Quellen inkl. Provider, EPGShare/Kaimandura, Kollision mit manueller Quellen-ID; Home, Mini, Guide und Details vergleichen, Neustart | ANDROID_NOT_TESTED |
| EPG92-02 | Quellenoffline/verkürzter Feed/kaputtes Gzip: LastGood bleibt; Bildermetadaten bleiben nach Raw-Freigabe; 7d Vergangenheit/20d Zukunft soweit vorhanden, DST-Grenzen | ANDROID_NOT_TESTED |
| EPG92-03 | DB-/Cache-/WAL-Größen vor/nach mehreren Imports; keine volle zweite EPG-Diskkopie, Kurzcache begrenzt; keine SQL-Rowcount-Erfolgsmeldung als Platzgewinn | ANDROID_NOT_TESTED |
| MAP92-01 | Ghosts/Monk/TVMaze und bekannte Filmabfrage: suchen, wählen, gespeicherte Zuordnung per Readback, Details schließen/neu öffnen, Kodi-Neustart | ANDROID_NOT_TESTED |
| MAP92-02 | Nahe Reserve, schreibgeschützt, Profilbusy/SQLitebusy: eindeutiger Fehler, alte Zuordnung erhalten. Gespeichert mit noch ladendem Bild als getrennte Zustände | ANDROID_NOT_TESTED |
| HOME92-01 | Sechs .91-Reihen und fremde Widgets, Überschriften/Spinner, Fokus Down 2530→2540, zurück und Scrollen; keine setfocus()- oder Misplaced-[-Fehler | ANDROID_NOT_TESTED |
| HOME92-02 | Adult/Erotik/Sport/Boxen nur auf Film-Home ausblenden; Bibliothek weiterhin vollständig; unabhängiger Portalfilter, neue Gruppen nicht still aufnehmen | ANDROID_NOT_TESTED |
| HOME92-03 | DB-Timeout/offline; Home ohne vorherigen Senderstart; nach vollständigem Kodi-Neustart erste fünf Logos sofort und später die vollständige konfigurierte Startgruppe prüfen, keine neuen HTTP-Downloads bereits verifizierter Logos; Mini-/großes EPG, aktuelle Bilder fünf Minuten stehen lassen, Film-/Seriencover nach Neustart, Quellenattribution korrekt | ANDROID_NOT_TESTED |
| PLAY92-01 | Erst einmal Live-TV-Zurück im bestätigten Kompatibilitätsmodus. Nur bei PASS Film, Serie, Stop, natürliches Ende/Autoplay und 5/20 Zyklen | ANDROID_NOT_TESTED |
| PLAY92-02 | Fremder TMDB-Helper-Player bleibt fremd; Stop-ACK/Threads/Return getrennt notieren, kein automatischer Home-Sprung bei anderer Wiedergabe | ANDROID_NOT_TESTED |
| BOOT92-01 | Kaltstart vor/nach Pflege; AAC-Verfügbarkeit/CAddonMgr vor XCMate getrennt von dessen Profil-/Speicherstatus beurteilen | ANDROID_NOT_TESTED |

Bei FAIL die erste Abweichung, Uhrzeit, feste Diagnosecodes und Inventurwerte notieren. Keine weiteren destruktiven Versuche; keine Profilrücksetzung. Offene Player-/Bootstrap-/LongOK-/MP3-Arbeiten siehe Implementierungsbericht; nicht automatisch als bestanden markieren.
