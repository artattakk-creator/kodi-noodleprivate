# XCMate 0.1.29.91 – Android-Abnahme

Datum: 12.11.2026 (Europe/Berlin). Ziel: Box B, Kodi21.3/RK3528, Titan BINGIE MOD2.2.3. Alle echten Geräteprüfungen **ANDROID_NOT_TESTED**. Box A nicht verändern. Kein Profilreset, keine Neuinstallation, keine Installer-Ausführung, keine Cache-/Datenbanklöschung. Vorhandenen TMDB-Token nicht neu importieren.

## Sicherer Update-Test

1. Aktuelle Home-Reihen, persönliche Widgets, Fokus-/Skin-Einstellungen und manuelle Bildzuordnungen dokumentieren. Bestehende letzte gültige Sicherung erhalten.
2. ZIP und SHA256 aus test-builds/02991 beziehen und Prüfsumme vergleichen. Die veröffentlichten Repository-Kataloge enthalten weiterhin .90. Dieses RC-Paket ist noch nicht regulär oder im Pilot verfügbar.
3. Nur Box B über „Aus ZIP-Datei installieren“ auf .91 aktualisieren. Bestehendes Profil verwenden. Update-Pop-up muss „Installation erfolgreich“, .91 und die aktuellen fünf Änderungszeilen anzeigen.
4. Falls der neue Home-Adapter noch nicht installiert ist: bestehenden Pfad XCMate → Einstellungen → Aussehen und Darstellung → Widgets → BINGIE-Home-Layout prüfen/vorbereiten verwenden. Vorschau, Sicherung und Hashprüfung beachten; nur gewünschte Änderung ausdrücklich bestätigen. Keine gespeicherten Widgetpfade ersetzen, keine Skin-Dateien von Hand überschreiben.
5. Fehlt eine externe Quelle, deren Installation/Aktivierung separat prüfen. Der XCMate-TMDB-Token versorgt nicht automatisch den TMDB-Helper. Keine Zugangsdaten oder Rohlogs auf GitHub veröffentlichen.

## Prüfmatrix

Für jede Zeile PASS / FAIL / NOT_TESTED, tatsächliche Version, Laufzeit und knappe Beobachtung festhalten. Bei einem Freeze abbrechen und Logs privat sichern; keinen Kodi-Absturz als PASS werten.

| ID | Geräteprüfung | Status |
| --- | --- | --- |
| RC91-U1 | Bestehende .90 auf .91 aktualisieren; Einstellungen, Portal, EPG, Favoriten, Resume und Space Blue erhalten | ANDROID_NOT_TESTED |
| RC91-U2 | Update-Pop-up: Erfolg, richtige Version, tatsächliche Änderungen; keine erneute Tokenabfrage | ANDROID_NOT_TESTED |
| RC91-H1 | Großer Hero, Senderlogo-Leiste, lokales Jetzt/Danach und Fortschritt ohne vorherigen Senderstart | ANDROID_NOT_TESTED |
| RC91-R1 | Filme: Überschrift immer sichtbar, echter Spinner nur bei Arbeit, Cover, Fokus, Filmklick/Zurück | ANDROID_NOT_TESTED |
| RC91-R2 | Serien: Überschrift/Spinner, Cover, Staffel-/Episodenwahl, Resume und Autoplay unverändert | ANDROID_NOT_TESTED |
| RC91-R3 | Im Kino: echte now_playing/movie-Inhalte, Poster, Fokus und Klickziel | ANDROID_NOT_TESTED |
| RC91-R4 | Disney: gespeicherte Quelle/Discover337DE, echte Einträge, Cover und Klickziel | ANDROID_NOT_TESTED |
| RC91-R5 | Diese Woche im Trend: echtes trending_week/tv, richtige Überschrift und Klickziel; kein Bewertungsranking | ANDROID_NOT_TESTED |
| RC91-R6 | MP3s: echte Audioquelle, Music-Ordner, Titel abspielen/stoppen, anschließend weiter navigieren | ANDROID_NOT_TESTED |
| RC91-L1 | Jede Reihe: Header bei Laden/leer/Fehler, Spinner endet spätestens60s; Wartet ist kein Läuft | ANDROID_NOT_TESTED |
| RC91-L2 | Nur tatsächlich ladende Reihe dreht; kein globaler Reload und keine Löschung bei Quellfehler | ANDROID_NOT_TESTED |
| RC91-N1 | Links/Rechts/Oben/Unten durch alle Reihen, persönliche Zusatzwidgets erreichbar, Fokus korrekt | ANDROID_NOT_TESTED |
| RC91-N2 | Kodi dreimal regulär beenden und starten; alle sechs Reihen, Quellen und persönliche Widgets erhalten | ANDROID_NOT_TESTED |
| RC91-A1 | Bekannte gute TVMaze-Suche erneut durchführen und richtiges Serienbild bis zur sichtbaren Textur prüfen | ANDROID_NOT_TESTED |
| RC91-A2 | Bekannte gute TMDB-Film-/Seriensuche erneut prüfen; Token unverändert, keine Helper-Abhängigkeit der eigenen Suche | ANDROID_NOT_TESTED |
| RC91-A3 | Bilddownload in Sendungsdetails: echte Bytes, richtige Textur, Wiederöffnung und Kodi-Neustart | ANDROID_NOT_TESTED |
| RC91-A4 | Ghosts-Mehrdeutigkeit: richtigen UK/US-Treffer wählen, speichern, Dialog erneut öffnen, Kalt-Readback nach Neustart | ANDROID_NOT_TESTED |
| RC91-A5 | Bestehende manuelle Zuordnung korrigierbar; erfolgreiche last-good-Bilder/Mapping bleiben bei Fehler erhalten | ANDROID_NOT_TESTED |
| RC91-P1 | Metadaten-Refresh auf Home bei Hintergrund-Audio; Wiedergabe bleibt aktiv, Stop und weitere Navigation | ANDROID_NOT_TESTED |
| RC91-P2 | Live-/Film-/Serien-Exit nach jeweiligem sicheren Einzelstart; bei Hänger stoppen, historisches #174 offen halten | ANDROID_NOT_TESTED |
| RC91-B1 | Namen/Pfade/Reihenfolge sämtlicher Fremdwidgets, Provider, Token, EPG-Mappings, Favoriten und Kodi-Einstellungen vergleichen | ANDROID_NOT_TESTED |

Fehler-/Leer-/Timeout-Fälle nur in vorhandener geeigneter Testumgebung oder bei realem Auftreten prüfen. Keine Add-ons/Daten löschen, um sie zu erzwingen. Native Linux-Fixtures ersetzen keinen echten Anbieter- oder Android-PASS.

## Freigabestufen

SOURCE_MERGED und VERSION_BUMP sind getrennt von ZIP_VERIFIED/CI_PASS, REPOSITORY_STAGED und REPOSITORY_RELEASED zu behandeln. Pilot nur vorbereitet; Veröffentlichung und Merge dieses Release-PR benötigen separate Freigabe. Regulär/NeoDark3 bleiben bis zur ausdrücklichen Geräte-/Veröffentlichungsfreigabe unverändert. Keine globale Veröffentlichung aus dem RC-Status ableiten.
