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

## Externe Bildspeicher – ausschließlich ANDROID_NOT_TESTED

- EXT89-01: Artwork-Verwaltung → externes Ziel: verfügbaren USB-/SD-Datenträger oder bestehende Kodi-Samba-Quelle auswählen. Berechtigungen/Anmeldung über Kodi, keine Zugangsdaten in Logs.
- EXT89-02: Zielprobe und Kopieren → SHA256 → sichtbare Bildprobe → Aktivierung ausdrücklich bestätigen. Vorher bleibt bisheriger Speicher aktiv.
- EXT89-03: Drei Senderlogos, fünf Filmcover, fünf Seriencover und zwei passende Sendungsbilder auf dem gewählten Ziel nachweisen. Native Darstellung getrennt vom Datei-/Hashbeleg prüfen.
- EXT89-04: Kodi-Neustart: gleiche Bilder aus bestätigten externen Dateien wiederverwenden; Provider- und EPG-Zuordnung sowie TMDB-Freigabe erhalten.
- EXT89-05: USB/SD entfernen oder NAS trennen: klare Nichterreichbarkeit, Zielwahl bleibt, keine heimliche interne Archivumschaltung. Nach Wiederverbinden kontrolliert fortsetzen.
- EXT89-06: Übertragung abbrechen und fortsetzen; unvollständige Kopien nicht als fertig veröffentlichen. Originaldateien und fremde Daten bleiben erhalten.
- EXT89-07: Echten Ziel-Freiraum, Sicherheitsreserve und eigenes Cachelimit unterscheiden. NAS-Freiraum UNKNOWN darf nicht als interner 27-MiB-Wert oder frei erfundene Zahl erscheinen.
- EXT89-08: Bestehende eigene Poster auf neues Ziel und zurück intern kopieren, Größen/Hash prüfen, erst danach aktivieren; Quellkopien unverändert erhalten.
- EXT89-09: Laufender Live-/Film-/Serienplayer, Remotefokus und Erinnerungsdialog weiter bedienbar, während im Hintergrund auf das Ziel geschrieben wird. Keine Verschiebung von EPG-/Katalog-/Kodi-/Timerdatenbanken.

## Realgerät-T01/T02: erste .89-Abnahme vom 11.11.2026 (FEHLGESCHLAGEN)

**Neuer tatsächlicher Nutzerbefund nach Installation und Neustart der veröffentlichten .89:**

- **T01 / A89-11 = FAIL:** Startseite baut sich sehr langsam auf, EPG-Home zeigt in fünf protokollierten `HOME_NOW_NEXT_READY`-Versuchen des Neustartlogs 0× READY (4× `EPG_CACHE_UNAVAILABLE`, 1× `EPG_DATA_MISSING`), 7 `EPG_READ_TIMEOUT`- und 7 `EPG_DB_BUDGET`-Events. Das ist **kein Beweis für vollständig verlorene EPG-Daten**.
- **T02 / A89-02/A89-03 = FAIL (noch nicht vollständig aufgebaut):** Unter dem neuen .89-Logo-Writer existieren tatsächlich 58 `PERSISTED_VERIFIED`-Events vor dem erneuten Neustart. Beim Neustart von 13:16:13 nach .89 beginnt `HOME86 LOGOS_LOCAL_READY` mit 59/88 (13:17:59) und steigt auf 68/88 (13:22:30). Kein vollständiger Verlust, jedoch sehr langsame Ergänzung; keine verifizierte 88/88-Ersthydration und damit noch kein fairer Zero-Download-88/88-Regressionstest. Der Nutzer verlangt eine sofort verfügbare, dauerhaft gespeicherte horizontale Navigation.
- **Weitere Befunde:** 4 `GUI86 CALLBACK_FAILED` im Portal-Lesepfad des Startseiten-/Widget-Callbacks, generischer nicht-logo-spezifischer Reservepfad weiterhin gesperrt. Durch die kombinierte Startup-/Worker-/DB-Belastung sind lange Startphasen technisch plausibel, aber ein Kodi-Freeze selbst nicht eindeutig nachgewiesen.
- **Korrekturversion:** [XCMate .90 P0-Hotfix, Issue #430](https://github.com/artattakk-creator/kodi-noodleprivate/issues/430); technische Übergabe [`CODEX_UEBERGABE_02990_ANDROID89_STARTUP_LOGO_EPG_2026-11-11_DE.md`](CODEX_UEBERGABE_02990_ANDROID89_STARTUP_LOGO_EPG_2026-11-11_DE.md).
- **Protokollintegrität:** 6 hochgeladene Logdateien, 5 unterschiedliche Byteinhalte und 3 überlappende Laufphasen; zwei ältere .88-Logs byteidentisch. Keine Rohlogs oder sensitive Provider-/Netzwerkdaten in GitHub gesichert.

**Alle anderen in den Tabellen aufgeführten Tests bleiben `ANDROID_NOT_TESTED`.** Die früheren Tabelleneinträge in diesem ursprünglichen Abnahmeplan wurden aus Gründen der Nachvollziehbarkeit nicht gelöscht; diese neue tatsächliche Realgerätmessung ersetzt für die genannten Fälle den vorherigen Status `ANDROID_NOT_TESTED`.


## Android-Abnahme .89 – weitere Nutzer-FAILs am 11.11.2026

Diese vier zusätzlichen Prüfungen beruhen auf der unmittelbaren Nutzerbeobachtung unter installierter `0.1.29.89`. **Für die einzelnen Aktionen liegen noch keine neuen Kodi-Logs bzw. konkrete Fehlermeldungstexte vor**; Codes und Ursachen bleiben unbewiesen. Nicht als Native-CI-Befund ausgeben.

| Test | Auf dem Gerät beobachtet | Ist | Erwartung nach Hotfix |
|---|---|---|---|
| T04 | Filme- und Serienreihen auf BINGIE-Home verschwunden bzw. leer | **FAIL** | Alle bestehenden Katalog-Widgets sichtbar, fünf Titel + vorhandene Cover pro Reihe; Restart-/DB-Busy-stabil |
| T05 | Widgets fremder Anbieter fehlen ebenfalls | **FAIL** | Gespeicherte Fremdwidget-Definitionen und -Controls sichtbar und bedienbar, keine SkinShortcuts-Daten löschen |
| T07 | Suche nach vergleichbaren TMDB/TVMaze-Sendungen liefert Treffer, aber gewählte Bildzuordnung kann nicht gespeichert werden; Fehlermeldung | **FAIL** | Nach Auswahl verifizierter atomarer SAVE und Readback, beim erneuten Öffnen und Kodi-Neustart weiterhin dieselbe Zuordnung |
| T11 | Live-TV → einmal LINKS Mini-EPG vorhanden → nochmals LINKS Gruppen manchmal fehlend; ausgewählte Gruppe teilweise ohne Sender | **FAIL** | Alle aktivierten Gruppen sichtbar, zugehörige Senderliste vollständig, Player/Fokus/OK-Umschalten stabil |

**P0** für alle vier. Eigene Testfälle **T90-09 bis T90-13** im [Nachfolge-Hotfix #430](https://github.com/artattakk-creator/kodi-noodleprivate/issues/430). Test T01/T02 bleiben FAIL, alle nicht geprüften Android-Funktionen offen. Wichtig: kein vollständiger Cache-Reset/Neuinstallation zum Reproduzieren, keine Nutzer- oder Token-Daten löschen.

Beobachtung zur Fehlerursache: `work_requests86`/ `programme_mapping85` Save/Readback/Deadline sowie `live_group68` kurze SQLite-Budgets sind **Code-Einstiegspunkte**, aber ohne einen passenden neuen Stacktrace keine eindeutig bestätigten Rootcauses.
