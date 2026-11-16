# XCMate .96 – Ursachen und Implementierung

Basis ist der vollständige .95-Quellstand c230fed998f4f2db0d9035068460cf26433e7ac4, ergänzt um main dfea6a72226b8c5fcccfce7d14e186e5e4007673. Main allein enthält weiterhin alten .92-Quellcode; seine Pilot-.95-Veröffentlichung bleibt unverändert.

## Bestätigte Host-Reproduktionen

- Eine einzelne Gruppe hing am Vollständigkeitscheck anderer aktivierter Gruppen. Der globale WidgetReader verbrauchte sein Zeitbudget bereits vor den eigentlichen Katalogseiten. Eine verspätete Auswahlantwort konnte den aktuellen Index ersetzen. Neuer gezielter, indizierter RO-Pfad prüft die Generation der Zielgruppe; der Besitzer umfasst Portal-/Kontokontext und Auswahl-Epoch. Maximal drei Versuche mit Backoff, LastGood und automatische Wiederaufnahme bei neuer Kataloggeneration.
- Ungültige/unlesbare settings.xml wurde in programme_consent77 als ausdrückliche Abwahl aller Quellen behandelt. Der neue bounded Native-Settings-Adapter unterscheidet Lesefehler, fehlende Datei und echte Entscheidungen, liest gesunde Werte/Defaults ohne wiederholte Kodi-getSetting-Aufrufe. Explizite Änderungen sichern, schreiben und lesen unabhängig zurück; bei fehlerhafter Fremdfeldänderung werden abgewiesene Bytes erhalten und der ursprüngliche Stand wiederhergestellt. Eine beschädigte Installation ohne geprüfte Sicherung bleibt BLOCKED; keine Rekonstruktion von Zugangsdaten aus geratenen Defaults.
- Der bisherige Migrationspfad aktivierte externe Quellen auch auf normalen frischen Profilen. .96 bewahrt bestehende Freigaben; weitere Aktivierung erfolgt ausdrücklich im zentralen Hub. Für die Testinstallation steht eine gemeinsame Aktion mit Token-Übernahme, Verbindungstest und gespeichertem Readback bereit. Es liegt keine eindeutige Gerätekennung für eine automatische Zuordnung vor.
- Eine deaktivierte manuelle TMDB-Zuordnung beendete die Kandidatenkette vor dem exakten XMLTV-Fallback. Der Fallback bleibt jetzt unabhängig. Die neue manuelle XMLTV-Auswahl nutzt nur vorhandene lokale Fakten, prüft Quelle/Kanal/Zeit/Titel/Revision, speichert atomar und bestätigt kalt. XMLTV-AUS widerruft die Anzeigezulassung, nicht die gespeicherten Bilddateien. Geänderte Fakten entwerten alte manuelle Proofs; frische lokale Kandidaten werden neu geprüft.
- Übergänge XMLTV→TMDB sowie Ausblenden→Automatisch wurden im unabhängigen Review als fehlerhaft reproduziert und mit monotonen Epochs/gezieltem Entfernen der überholten Auswahl korrigiert. Der Logo-Resolver verarbeitet auch bestätigte Overrides nach Position 512.

## Bestand und technische Grenzen

Die .95-Sicherungsfreigabe und der Schutz bestehender Guide-/WAL-/Backup-Dateien bleiben erhalten. Xtream-Provider-EPG ist gemäß neuem Vertrag Grundversorgung; die ursprünglichen vier EPG-Schalterwerte werden als Historie archiviert, optionale Feeds nicht ersetzt. Vorhandene Worker, Profiltransaktionen, Tokenimporte, URL-/DNS-/Decoderprüfungen und Migrationsjournale werden weiterverwendet.

Mini-EPG und großer Guide teilen den Zuordnungscontroller über echte Adapter. Vorschau schreibt keine Konfiguration; Save speichert genau Quelle+Kanal für den Sender und bestätigt per unabhängigem Readback. Die Zuordnung ersetzt weder Player noch Fernbedienungs-Keymap.

Der zentrale Speicherdialog bietet 32 MiB dynamischen Standard sowie bewusste Erweiterung. Dauerhafte Senderlogos und manuelle Bilder sind keine flüchtigen Cacheobjekte. Nur ausdrücklich bestätigte, belegbar abgelaufene temporäre Derivate sind bereinigbar; ein geringer interner Speicher wird nicht durch angeblichen Volumewechsel verschleiert.

Cinematic-Enrichment erfolgt nur nach unabhängiger Werkidentität im bestehenden begrenzten Worker. Bis zu fünf ausreichend große, sichere Backdrops werden nach Seitenverhältnis, Sprache, Größe, Bewertung und Stimmen gewichtet. Eindeutige Filmabfrage und vorhandene gültige Bilder bleiben bei Enrichment-Fehlern erhalten.

Die 1.470 echten Kodi-Settings-Ladefehler beweisen ohne Zugriff auf die private betroffene Datei keine einheitliche Hardwareursache. Host-Reproduktionen bestätigen konkrete Fehlerbehandlung und Persistenzgrenzen, nicht deren alleinige Erklärung auf dem Gerät. Tatsächliche Android-Speicherwerte, Gruppenwechsel mit Wiedergabe, Bilder, SMB-Zugriff, Lang-OK und Decoderfreigabe bleiben ANDROID_NOT_TESTED.

Kein Merge, kein Release, keine Änderung an Box A, Installer .5.26 oder den bestehenden Veröffentlichungskatalogen.
