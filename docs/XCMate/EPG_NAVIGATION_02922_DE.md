# XCMate 0.1.29.22 – EPG-Startgruppe, Gruppenansicht und Fokus (#88/#92)

**Android: NOT_TESTED.** Kumulativer Branch `fix/xcmate-02922-guide-navigation`, Draft-PR #110 auf main .21 einschließlich Autoplay/Player und Original-Icon. Direkter Updatepfad .21 → .22; Gesamtbericht `KUMULATIV_02922_DE.md`.

## Diagnose und Umsetzung

Die .20 initialisiert `category=None`, wodurch `Reader.page` gruppenübergreifend liest. Das erklärt die globale Darstellung; **kein Nachweis für Dubletten**. #58 bleibt eigenständig. Native Buttons hatten keine expliziten Normal-/Fokusfarben und keine Route von der ersten Rasterzeile in die Kopfzeile. Das ist im Code belegt. Die exakte Ursache der Android-Overlayoptik ist ohne neuen Render-/Gerätetest nicht abschließend bewiesen; Sendername und Programmtitel werden ausdrücklich getrennt behandelt.

Der neue Worker-Einstieg liest ausschließlich aktivierte Gruppen. Eine gültige gespeicherte Startgruppe wird gewählt und der Startsender darin an seiner ursprünglichen ordinalen Position sichtbar gemacht. `Reader.position` zählt lokal die vorhergehenden eindeutigen Sender in genau dieser Gruppe; kein `pin`, keine Umsortierung, keine neue Senderdatenbank. Bei Widerspruch ist die erlaubte Gruppe des gespeicherten Startsenders der Fallback, anschließend die erste erlaubte Gruppe. Fehlt nur der Startsender, bleibt die gültige gespeicherte Gruppe mit erster Zeile erhalten. Keine aktivierten Gruppen ergeben eine klar benannte leere Gruppenansicht mit Home-Schaltfläche. Die gespeicherten Startparameter werden nie verändert.

Eine eigenständige native Gruppenliste zeigt nur aktivierte Gruppen in gespeicherter Reihenfolge, keinen automatisch gewählten „Alle“-Eintrag. OK öffnet ausschließlich die gewählte Gruppe. Während die neue lokale Seite lädt, wird nur der bisherige UI-Snapshot geleert, sodass keine Sender der alten Gruppe kurzzeitig unter dem neuen Gruppentitel stehen; Datenbanken/Bilder bleiben unangetastet. Offset, Senderzeile, Zeitcursor und Zeitausschnitt werden je Gruppe für dieses Fenster erhalten. Neu gewählte Gruppen übernehmen die aktuelle Zeitachse. Hintergrundarbeit ist weiterhin auf dem Owner-Dispatch/Worker begrenzt; überholte Raster-Abschlüsse werden beim Öffnen der Gruppen verworfen.

## Fernbedienungsvertrag

- Programme: Rechts/Links zwischen Sendungen. **Links am ersten sichtbaren Programm** wechselt ohne Zeitversatz in die Sender-Spalte; **nochmals Links** an dieser definierten Sendergrenze öffnet Gruppen. Rechts aus der Sender-Spalte zurück zum gewählten Programm. OK am Sender öffnet das bestehende Sendermenü.
- **Hoch aus der obersten sichtbaren Programmzeile → Kopfzeile**, unabhängig vom Senderoffset. Links/Rechts dort erreicht alle sechs nativen Buttons; **Runter → vorherige Rasterzeile**. Optional blaue Taste (`ACTION_BLUE=218`) direkt zur Kopfzeile, ausschließlich in diesem Fenster. Keine globale Keymap.
- Vorherige Senderseiten bleiben erreichbar: aus der Kopfzeile nochmals Hoch oder in der Sender-Spalte über die obere Seitengrenze. Runter am unteren Rand lädt wie bisher die nächste begrenzte Acht-Sender-Seite.
- **Zurück in Gruppen → vorherige EPG-Ansicht mit Sender-/Zeit-/Fokusposition**, **Zurück im Raster → XCMate Home**. Dies folgt dem neuen Arbeitsauftrag vom 23.10.2026. Ein unmittelbarer Back-Repeat nach Gruppenöffnung wird für 150 ms abgefangen; beim eigentlichen Schließen bleibt der Owner wie bisher noch drei Pump-Takte erhalten. Kein erneuter Playerstart.
- Hintergrundrefresh aktualisiert Daten/Logos, lässt den aktuellen Header-/Sender-Fokus stehen. Kopfaktionen bleiben in der Kopfzeile, bis der Nutzer Runter wählt. Die zugrunde liegende horizontale UTC-Achse, DST-Tage, Programmlücken und vorhandenen Playback-Handoff bleiben erhalten.

## Lesbarkeit und Schutz

Alle nativen Guide-Buttons bekommen explizit helle Normal-/Fokusfarben mit dunklem Schatten. Der tatsächliche Kodi-21.2-Omega-Code wurde zusätzlich gelesen: `Window.getControl` übernimmt XML-Labelinfo/Farben in den Python-Button; `ControlButton.setLabel` bewahrt nicht explizit überschriebene Farben. Quellen und Prüfergebnis: `KODI_212_GUIDE_FOCUS_02922.json`. Ein eigenes kleines PNG besitzt einen transparenten Mittelpunkt und neonfarbenen Rand. Senderrahmen und Sender-Button stehen **hinter** Logo und Sendertext, reichen nicht in Programmbereiche hinein. Der aktive Sender bleibt auch bei Programmfokus eingerahmt. Der Footer enthält immer vollständigen Sendernamen und ausgewählten Programmtitel mit Zeiten, auch bei sehr kurzen Blöcken. Ein Guide-spezifischer Guard erhält diese Kontrastfarben und Rahmen auch bei einer gespeicherten dunklen Text-/Fokusfarbe; andere Ansichten behalten ihre Appearance-Auswertung.

Die kleine Korrektur beim Schritt zurück in eine bereits sichtbare, am linken Rand abgeschnittene Sendung begrenzt deren Cursor auf den Fensterrand. Dadurch löst eine reine In-Viewport-Bewegung keinen unnötigen Datenreload aus; echte Zeitnavigation, Drei-Stunden-Wechsel und Lücken bleiben weiter geprüft.

Artwork-Module, bestehende lokale Logos/Queue, bestätigter Logo-Refresh, Guide-Datenbank-/Mapping-/XMLTV-Pfade, Player-/Live-Ownership und .20-Progress-/Medienfenster sind unverändert. Keine neuen Providerimporte, keine automatischen Mappings, keine UI-bedingte Änderung der Startsenderparameter. Rich-Details/manuelle XMLTV-Zuordnung und weitere Punkte von #88 bleiben eigene Aufgaben; dieses Paket behauptet keine Gesamtlösung von #88/#92 oder #58.

## Nachweise und Grenzen

26 EPG-Navigationstests (23 übernommene und drei neue Gruppen-Back-Fälle) mit echter SQLite und nativer Fokus-Simulation: 2.501 Sender, Startsender an Position 1.979 (Viewport 1.976, Zeile 3), keine Umordnung, falsche/fehlende Gruppen und Sender, leerer Zustand, reine Gruppenauswahl, 20 Wechsel mit exaktem Restore, alle sechs Header, Jetzt/20:15/Vortag/Folgetag, Blue, vorherige Senderseiten, Back-Repeat, stale Future, unveränderte Logos/DBs, Appearance-Kontrast und PNG-/XML-Layer. Der bestehende Guide-Back-Test bleibt auf direkter Home-Rückkehr aus dem Raster; der große Pagingtest berücksichtigt den nun tatsächlich fokussierten Startsender. Originale Freeze-Referenzen bleiben unverändert.

Vollständige Suite: `TESTERGEBNISSE_02922.json` / `TESTLOG_02922.txt`. ZIP/CRC/Sourcebytes/Reproduktion und Python-3.11-Grammatik werden separat geprüft. Screenshot-/Skin-/Decoderwirkung ist keine Leistung der Host-Simulation: **Android NOT_TESTED**. Neuer realer Test muss Sender- und Sendungstext ausdrücklich getrennt bestätigen.

## Kumulative Basis und Schutz

Aktueller main .21: `3307e006a9de9fd53236ec881191851291731c98`. Sämtliche .21-Autoplay-/Player-Funktionen bleiben erhalten, mit neuer EPG-Oberfläche und Original-Icon. Direktes Update von .21, kein Downgrade oder Deinstallieren. Frühere isolierte .22-ZIPs sind überholt. Siehe `KUMULATIV_02922_DE.md` und `UPDATEPFAD_02921_02922_DE.md`. Kein Reset, keine Portal-/EPG-Zuordnungsänderung oder Keymap-Änderung; Artwork-Pause weiterhin BLOCKED_UI / NOT_TESTED.
