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

## P0-F / P0-G – zusätzliche Pflichtfälle

| Fall | Ablauf / tatsächliches PASS-Kriterium | Status |
|---|---|---|
| A89-F1 | Passendes TMDB-Herobild sichtbar; später XMLTV-/negative Treffer nach 5/30/45/90 s, harmloser EPG-Refresh und Speicherblockade. Gleiche Sendung behält denselben verifizierten Bildinhalt über fünf Minuten. | ANDROID_NOT_TESTED |
| A89-F2 | Explizit neues Bild zuweisen, echte Programmgrenze, Kanal-/Profilwechsel und Quell-Opt-out: korrekter Austausch/Entsperren. Fehlerhafte Datei nicht stur festhalten. | ANDROID_NOT_TESTED |
| A89-G1 | Automatik aus: keinerlei heimlicher Vollscan. „Katalog aktualisieren“ manuell; zwei neue Filme/zwei neue Serien, geändertes Providercover. DB-Generation/Delta/Readback und echte Widgetanzeige unabhängig nachweisen. | ANDROID_NOT_TESTED |
| A89-G2 | Fünf Film- und fünf Seriencover stehen lassen. Nach 5/30/45/90 s sowie Fehlrefresh, SQL-Lock und METADATA_WRITE_DEFERRED dieselben lokalen Cover sichtbar. | ANDROID_NOT_TESTED |
| A89-G3 | Vollständiger Kodi-Neustart: dieselben fünf Poster je Reihe aus eigenem verifiziertem Cache verwenden. 218-MiB-Fall separat von großzügigem Speichervolume prüfen; RAM-only niemals als persistiert zählen. | ANDROID_NOT_TESTED |
| A89-G4 | Leere, abgebrochene, falsche oder ausgefallene Providerantwort: vorhandene Titel/Serien und Cover bleiben; Status zeigt Retention statt Erfolg einer leeren Generation. | ANDROID_NOT_TESTED |
| A89-G5 | Bestätigte neue Posterrevision betrifft nur richtigen Provider-SID/Medientyp; sichtbare Fremdwidgets, .88-Layout, Fokus und Benutzerkonfiguration unverändert. | ANDROID_NOT_TESTED |

## P0-H – Erinnerung (alle ANDROID_NOT_TESTED)

- H89-01: Zukünftige echte Sendung in Mini-/Groß-EPG-Details merken; genau ein Timer fünf Minuten vorher, Merkliste erhalten.
- H89-02: Mit laufendem Stream und IR-Fernbedienung genau zwei Aktionen lesen/fokussieren: Jetzt umschalten und Verwerfen. Ohne Wahl läuft der Stream weiter.
- H89-03: Jetzt umschalten startet exakt den gewählten Sender einmal über den bestehenden Resolver. Bei verschwundenem Sender/EPG-Zeitverschiebung klare Fehlermeldung, kein fremder Stream.
- H89-04: Verwerfen schließt und bleibt nach Kodi-Neustart erledigt; Merklisteneintrag bleibt erhalten.
- H89-05: Zurück, unbeantworteter Timeout und Skinwechsel bewirken kein Umschalten und keine Popup-Schleife.
- H89-06: Nicht mehr merken entfernt eigenen Eintrag und storniert ausstehenden/aktiven Timer; erneutes Merken erzeugt genau einen Timer.
- H89-07: Zwei gleichzeitig fällige Sendungen nacheinander behandeln; alte Guide-/Legacy-Erinnerung und neuer Detailbutton dürfen keine Dubletten erzeugen.
- H89-08: Laufende Sendung nur merken mit verständlichem Hinweis; beendete Alarme nach Neustart als verpasst behandeln. Kein Wake-up-Versprechen. Fremde Modaldialoge nicht schließen.
