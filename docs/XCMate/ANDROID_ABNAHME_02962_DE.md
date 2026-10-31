# XCMate .62 – zuerst Live-TV, danach privater TMDB-Test (Box B)

Alle folgenden Android-Gates sind **ANDROID_NOT_TESTED**. Pro Test PASS / FAIL / ÜBERSPRINGEN erfassen. Box A nicht ändern. Film-/Serienwidgets aus .61 sind bereits vom Nutzer PASS und bleiben Referenz; keine Neueinrichtung, Deinstallation oder Datenbereinigung.

Der Nutzer hat im aktuellen Chat den direkten Merge nach Prüfung freigegeben. Das ersetzt die ältere Nicht-Merge-Vorgabe in #289 und im Auftragsdokument. Dies ist keine Android-Abnahme und keine Freigabe zu automatischen Änderungen an fremden Add-ons.

## Installation / erste Senderkachel

Nach regulärem Kodi-Repository-Update auf .62 Versionsanzeige prüfen; alternativ bereitgestelltes ZIP als Update installieren. Startgruppe und vorhandene Bindungen behalten. BINGIE Home öffnen. **Kein Token und kein EPG-Bild nötig.**

| Gate | Prüfschritt | Status |
|---|---|---|
| B-62-01 | Mindestens eine kleine Live-Senderkachel auf echter BINGIE-Startseite sichtbar und fokussierbar | ANDROID_NOT_TESTED |
| B-62-02 | Gesamte konfigurierte Startgruppe (z.B. 88 Sender) in unveränderter Reihenfolge bis zum letzten Sender scrollbar | ANDROID_NOT_TESTED |
| B-62-03 | Fokus startet keinen Stream; OK startet genau den Sender, Zurück ohne Freeze | ANDROID_NOT_TESTED |
| B-62-04 | Ohne EPG/TMDB bleiben Sendername, Logo bzw. Textkachel und neutrales Hero-Bild sichtbar | ANDROID_NOT_TESTED |
| B-62-05 | Eigene tmdb_read_access_token.txt lokal/USB/Downloads importierbar; Status FILE_VALID | ANDROID_NOT_TESTED |
| B-62-06 | Echter /3/configuration-Test mit eigenem Token zeigt TMDB_OK oder konkreten Fehler | ANDROID_NOT_TESTED |
| B-62-07 | Nach regulärem Kodi-Neustart private Datei erhalten und erneut TMDB_OK möglich | ANDROID_NOT_TESTED |
| B-62-08 | Nach bewusster Aktivierung eindeutiges Film-/Episodenbild im gemeinsamen lokalen Cache und in EPG/Home | ANDROID_NOT_TESTED |
| B-62-09 | Abgenommene Film-/Serienreihen mit Postern, Scrollen und bisherigen Klickzielen weiter PASS | ANDROID_NOT_TESTED |
| B-62-10 | Nach gezielter bestätigter Skinshortcuts-Reparatur und Neustart keine getiterator-Ausnahme, alte Widgetbindungen erhalten | ANDROID_NOT_TESTED |

Wenn B-62-01 FAIL: feste Diagnosecodes aus HOME62 für GROUP_POLICY, DATABASE, HEAD, PAGE, PAYLOAD, RENDER und DIRECTORY notieren. Keine privaten IDs/URLs oder vollständigen Kodi-Rohlogs öffentlich posten. Ein Worker-PUBLISHED ist kein Nachweis sichtbarer Kacheln.

## Skinshortcuts nur bei bestätigtem Pythonfehler

XCMate → Einstellungen → Aussehen und Darstellung → BINGIE-Startseiten-Widgets einrichten → **Skinshortcuts: Python-Kompatibilität prüfen/reparieren**. Laufende Wiedergabe und Shortcut-Editor zuerst schließen. Gezeigt werden Diff und vorherige/neue SHA256 für exakt zwei Aufrufe in library.py der bekannten Version 2.1.0. Erst nach eigener ausdrücklicher Zustimmung speichern. Keine unbekannten Dateien überschreiben, kein globales Monkey-Patching und kein automatisches Fremd-Add-on-Update.

Danach Kodi regulär neu starten. Bei Bedarf **BINGIE-Home-Layout prüfen/vorbereiten** und die angebotene einmalige Neugenerierung ausdrücklich bestätigen. Kein Polling/Reload-Loop. Die bestehenden Film-/Serienbindings nicht neu anlegen. **Skinshortcuts-Sicherung wiederherstellen** rollt ausschließlich die passende unverändert verifizierbare library.py zurück; danach erneut Kodi normal starten. Die getrennte bestehende Layout-Wiederherstellung bleibt erhalten.

## TMDB ausschließlich mit deinem privaten Token

XCMate → Einstellungen → EPG → **TMDB-Zugang**. Am PC eine UTF-8-Datei `tmdb_read_access_token.txt` mit genau dem API Read Access Token erstellen, ohne Bearer, JSON, Anführungszeichen oder Kommentare. Über lokalen Kodi-Dateidialog auswählen. Lokale file:- und unterstützte special:-Pfade werden übersetzt, Symlinks/Traversal sowie SMB-/content:-Quellen werden abgewiesen. Bei Android eine direkt zugängliche gemountete USB-/Download-Datei wählen; keine Dateisystem-Umgehung.

Datei wird atomar im privaten XCMate-Profil gespeichert. FILE_VALID bestätigt das Format, **erst TMDB_OK bestätigt echte Authentifizierung**. Import schaltet keine Bildsuche ein; dafür getrennt aktivieren. Sichtbares **Zurück** (fünfte Position) schließt ohne Änderung; Deaktivieren steht als eigener letzter Eintrag mit Bestätigung bereit. Bestehende Datei wird nur nach Zustimmung ersetzt.

Token nie im Chat, GitHub, Screenshot oder Log veröffentlichen. Codex hat keine privaten TMDB-Zugangsdaten und keinen Zugriff auf Box B; dieser echte Test ist ausschließlich durch den Nutzer möglich. Keine fingierten Geräte-PASS.
