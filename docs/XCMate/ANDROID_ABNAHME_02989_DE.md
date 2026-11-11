# Android-Abnahme XCMate 0.1.29.89 – Box B

Alle Fälle **ANDROID_NOT_TESTED**. Keine Box A ändern; keine Neuinstallation, kein Löschen, kein Reset. Test-ZIP über „Add-ons → Aus ZIP-Datei installieren“ kumulativ über .88 einspielen. Normale Kanäle bleiben bei .88.

Vorher private Sicherung des Kodi-Profils; Senderzahl/Startgruppe, Provider, TMDB-Token, Favoriten/Merkliste, manuelle Bilder und alle eigenen/fremden Widgetnamen, Pfade und Reihenfolgen festhalten. Keine Zugangsdaten öffentlich posten.

| Fall | Ablauf / tatsächliches PASS-Kriterium | Status |
|---|---|---|
| A89-01 Speicher | Artwork-Diagnose: ausgewähltes Logo-Ziel, realer Mount/Volume, Total/Free/Reserve prüfen. Bei gleichem Pool keinen Speichergewinn behaupten. Quota-/Mindestfreiraum-/Berechtigungsfehler getrennt erkennbar. | ANDROID_NOT_TESTED |
| A89-02 Logos | Startgruppe ohne Senderstart öffnen. Erst fünf sichtbare Logos, dann alle verfügbaren 88 berücksichtigen. Rail, Hero-Fallback und EPG-Details zeigen richtige Logos. `PERSISTED_VERIFIED` nur nach Datei/Manifest-Readback; RAM gesondert. | ANDROID_NOT_TESTED |
| A89-03 Kaltstart | Kodi vollständig beenden, neu starten. Eigene verifizierte Logos sofort wiederverwenden; Netzstatistik für unveränderte Logos: 0 erneute Downloads. Tatsächlich sichtbare Logos zählen, nicht nur Manifestrecords. | ANDROID_NOT_TESTED |
| A89-04 Gruppen/Fehler | Gruppe wechseln/zurück; keine unveränderten Logos neu laden. Einzelne defekte Datei gezielt reparieren; kein Gesamtreset. Bei unzureichendem Platz kontrollierter RAM-Fallback ohne Datenverlust. | ANDROID_NOT_TESTED |
| A89-05 Manuell TV | Mini- und Groß-EPG → Details → Bild zuweisen → TMDB-TV und TVMaze: Suche bearbeiten, Seite/Poster ansehen, auswählen, ausdrücklich speichern. Richtige Grafik sichtbar; nach Neustart gleiche bestätigte Zuordnung. | ANDROID_NOT_TESTED |
| A89-06 Manuell Film | TMDB-Movie mit Jahr/Edition prüfen, gleichnamige Serie nicht verwechseln. Sender ohne automatisches Bild und bereits bebilderten Sender testen. Token unverändert. | ANDROID_NOT_TESTED |
| A89-07 Deadline/Cancel | Langsame Quelle, wartende Queue, Abbruch vor Commit, echter Eventwechsel und harmloser Refresh prüfen. Kein unbestätigtes Mapping, kein „Abgebrochen“ nach verifiziertem Commit. Diagnosephase und Result unterscheiden. | ANDROID_NOT_TESTED |
| A89-08 Sticky | Richtige Sendung mindestens fünf Minuten auf Home und im Detail stehen lassen. Kein 45-s-Bildverlust; echter Eventwechsel korrekt. TVMaze sowie XMLTV-/Provider-Fallback prüfen. | ANDROID_NOT_TESTED |
| A89-09 Fremdwidgets | Vorher tatsächlich eingerichtetes MP3-/SHOUTcast-/Kino-/Serienwidget plus drei XCMate-Reihen nach Neustart scrollend sichtbar und bedienbar. Fremde Reihe öffnen, Back/Fokus erhalten. Keine erfundenen oder neu gesetzten Standardreihen. | ANDROID_NOT_TESTED |
| A89-10 Widgetdiagnose | Bei fehlender Reihe privat Inventur prüfen: SAVED_NOT_GENERATED, Add-on MISSING/DISABLED, NATIVE_HIDDEN/EMPTY/UNKNOWN getrennt. Positive native Count ist noch kein Pixel-PASS. Private Pfade nicht auf GitHub stellen. | ANDROID_NOT_TESTED |
| A89-11 EPG | Mini, Grid, Hero, Details: gleicher Sender/Start/Ende/Titel. Bei kurzzeitigem Busy/Timeout gültige Daten behalten; keine Hover-Refreshschleife. | ANDROID_NOT_TESTED |
| A89-12 Bestandsschutz | Live/Film/Serie starten, Back/Stop, Autoplay/Resume testen. .88-Home-Design, Widgets, Provider, EPG-Mappings, TMDB-Token und Installer .5.26 unverändert. | ANDROID_NOT_TESTED |

Ergebnis je Fall mit PASS/FAIL/ANDROID_NOT_TESTED, Version, Gerät, Kodi-Version, Dauer und redigiertem Diagnosecode dokumentieren. Echte Android-Sichtbarkeit darf nicht aus Hosttests abgeleitet werden.
