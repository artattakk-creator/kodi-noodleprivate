# XCMate .34 – Guide-/Such-Handoff

Basis: main `6bb96547ec469e62c5f69e23a928842021bab4c4`, Version 0.1.29.33. Vollständig berücksichtigt: `CODEX_UEBERGABE_LOGFORENSIK_02933_20261024_DE.md`, dokumentierte .33-Abnahme und Issues #140, #111, #127, #143. Kein Daten-/Provider-/Download-/Aufnahme-Umbau.

## Befund und Nachweisgrenze

Die zwei .33-Suchversuche endeten mit Busy 10138 bei Hauptfenster 10025; die zusätzliche asynchrone Fortsetzung aus #156 blieb ebenfalls blockiert. Beim Guide-Schließen liefen neue Root-Dispatches. Vier Guide-Starts endeten nach etwa 2,5–2,8 Sekunden SKIPPED, ohne Resolver. Normales Live-TV startete. Die alten Logs enthalten keinen differenzierten SKIPPED-Grund: dessen genaue jeweilige Gate-Bedingung lässt sich rückwirkend nicht beweisen.

Kodi 21.2 selbst unterscheidet die Oberflächen: `Window::close()` sendet `TMSG_GUI_PREVIOUS_WINDOW` an `iOldWindowId`. Damit wird das vorherige Medienfenster aktiviert, einschließlich möglicher Plugin-Verzeichnis-Neuberechnung. `WindowXMLDialog` delegiert show/close an `WindowDialogMixin`; dieser schließt den registrierten Dialog per `TMSG_GUI_PYTHON_DIALOG`, ohne PreviousWindow-Navigation. Quellen und SHA256 stehen in `KODI_212_WINDOW_LIFECYCLE_02934.json` (Tag 21.2-Omega).

Das gemeinsame Problem ist die Verwendung eines navigierenden WindowXML als vorübergehender Guide-/Suchoberfläche, obwohl danach innerhalb desselben Ablaufs weitergearbeitet werden soll. Das Hostmodell bildet den C++-Unterschied ausdrücklich ab: normales close startet einen zweiten Root und Busy; Dialog-close lässt den Elterncontainer bestehen. Die drei ursprünglichen Reproduktionstests scheiterten auf unverändertem .33 (Guide viermal blockiert, falscher Guide-/Suchfenstertyp) und bestehen mit .34. Zusätzlich werden zwei komplette Suchausflüge einschließlich Gruppen-/Zeit-/Fokus-Rückkehr geprüft.

Das ist Quellcodeanalyse plus reproduzierbares Hostmodell, **kein nativer Android-Lauf**. Auf diesem Host sind weder Kodi-Binary noch ein vorbereitetes Kodi-Containerimage vorhanden. Ob die konkrete Android-Reaktivierung damit vollständig entfällt, bestätigen erst G1–G4; parallele fremde Root-Aufrufe werden nicht unterdrückt. Neue anonymisierte ENTRY/RETURN-Snapshots zeigen deren tatsächliche Überlappung und Owner-Zuordnung.

## Umsetzung

- Beide Guides und nur die eigenständige Suche verwenden WindowXMLDialog. Der Owner-Pump mit show/Monitor und Threadkontrolle bleibt bestehen. Keine doModal-Schleife, kein GUI-Worker-Callback, kein erzwungenes Dialogschließen.
- Film-/Serienfenster bleiben WindowXML. Ihre gemeinsame Implementierung wird mechanisch in `MediaView` weiterverwendet; eingebettete Suche, Cover, Details, Autoplay und Fokusmethoden bleiben erhalten. Keine Vererbung von zwei unterschiedlichen nativen Kodi-Oberflächen.
- Ein Dialog wird anhand seiner eigenen Window-Property mit zufälligem Owner bestätigt. Native Dialog-ID und Hauptfenster-ID werden getrennt erfasst. Unbekannte Dialogidentität gilt als nicht freigegeben; 10025 ist kein Proxy für einen geschlossenen Dialog.
- Search-Continue bleibt als begrenzter, sessiongeschützter Kompatibilitätsweg erhalten. Busy 10138, echte fremde Modaldialoge, Container-Updates und Abort werden weiter respektiert; keine längeren Wartefristen als Ersatz für Ursachenbehebung.
- Guide-Start bleibt `PlayMedia` auf dem bestehenden `play_live`/`source_play`-Resolver. Nach Owner-/Lease-Freigabe werden Dialog-/Player-/Portal-/Senderzustand geprüft, nach dem lokalen Read nochmals Player/Session. Fremde laufende Medien werden nicht ersetzt. Der Einmalschutz bleibt auch beim dritten oder späteren Replay gesetzt.
- Neue Logs enthalten ausschließlich feste Phasen/Gründe, numerische Fensterzustände und zufällige Request-/Owner-/Lease-IDs. Keine Suchtexte, Sendernamen, Portal-IDs, Pfade, URL- oder Exceptiontexte.

## Feste Guide-Abbruchgründe

`INVALID_INTENT`, `REPLAY`, `OWNER_ABORT`, `OWNER_UNAVAILABLE`, `WINDOW_STILL_ACTIVE`, `BUSY_TIMEOUT`, `FOREIGN_MODAL`, `CONTAINER_UPDATING`, `PLAYER_UNAVAILABLE`, `PLAYER_STATE_CHANGED`, `FOREIGN_PLAYER`, `LIVE_SESSION_CHANGED`, `PORTAL_UNAVAILABLE`, `PORTAL_CHANGED`, `CHANNEL_UNAVAILABLE`, `UNSUPPORTED_PORTAL`, `EXCEPTION_CLASS`.

Hosttests prüfen vier unterschiedliche native Blockaden separat, keine nachträgliche Behauptung über die unbekannten vier .33-SKIPPED-Gates. Exceptiondiagnose beschränkt sich zusätzlich auf eine erlaubte Fehlerklasse.

## Matching, Poster und Folgearbeiten

Such-Matching, Jetzt-EPG-Scan, Renderer, bestehende Caches/Jobs und .33-Grafiken bleiben bytegleich. Elf Sendernamen-Hits sind weiterhin kein Programmtitel-Nachweis. #140 bleibt offen bis Android-Abnahme; neue G1–G4 alle NOT_TESTED.

#111: `media_art.retry_poster` wählt ausschließlich bekannte Provider-Bildadressen; `metadata_views` ist providerbasiert. Es existiert kein TMDb-Kandidatenabruf auf main. Für den gemeldeten Timeout gibt es im .33-Zeitraum keinen ausreichenden ART-/Netzfehlernachweis. Separate gezielte Diagnose/Reparatur, kein globaler Cache-/Jobreset und kein unbewiesener TMDb-Erfolg im Suchfix. #98 erst nach stabiler Suche/Guide-Start; Downloads/Aufnahmen nachrangig.
