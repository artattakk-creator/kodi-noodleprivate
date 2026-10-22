# XCMate 0.1.29.19 – kompakte Poster und manuelle nächste Folge

Stand 22.10.2026, Europe/Berlin. Basis **main `ce8d99c` / 0.1.29.18**, Branch `feat/xcmate-02919-manual-next`. .19 vorab ohne vorhandenes ZIP/Tag/Branch geprüft. Testkandidat, kein Merge, Release oder produktives Indexupdate.

## Beweislage und Umfang

Die Nutzerübergabe und aktuelle Kommentare in #74/#44 bestätigen .18-Android-Tests 34–39 für die tatsächlich geprüften Teilfunktionen. Test 37: sechs funktionale PASS, zusätzlich neuer Designwunsch „Poster etwa ein Drittel kleiner, Schrift weiter lesbar, deutlich umrahmte aktive Cover“. Das ist keine rückwirkende Umdeutung der PASS. Test 38: Augen/Legende/Seen sieben PASS. Test 39: Continue-Ausblendung sechs PASS, Mehrportalprüfung NOT_TESTED. Test 40: sechs PASS für Einzelwiedergabe, natürliche Rückkehr/Fokus, Back, Stop von Bild/Ton und Resume; manuelle Next-Aktion FAIL. Diagnose 40E: Nachfolger existiert, Aktion fehlt sowohl im Detail als auch in der Episodenliste. Konkrete Serie/Folge und damaliger Historienzustand unbekannt.

Code bestätigt die unzureichende Konstruktion `watched and unseen → unseen[0]` und das Fehlen eines Next-Buttons in der Folgenliste. Der genaue Geräte-Trigger ist damit nicht nachträglich bewiesen.

## Implementiert zu #74

- Poster **108×162** statt 164×246: ungefähr ein Drittel kleiner, exakt 2:3; Filme und Serien verwenden dasselbe XML für Rails 110/111/112 und Kategorien 210.
- `font13`, Textbreite mindestens 164, Titelhöhe 60/64 bleiben unabhängig von der Postergröße. Kachelbreiten 180/190 bleiben für Lesbarkeit erhalten. Railgruppen schrumpfen von 368 auf 288, Kategorie-Kachelhöhe von 318 auf 248. 720p-Koordinaten skaliert Kodi auf 1080p; kein behaupteter echter Renderingtest.
- Fokusrahmen direkt um das Bild statt um die gesamte hohe Kachel. Bestehendes `xcmate_focus_neon.png` unverändert und mit Nine-Slice verwendet: dunkler äußerer Rand, danach Neonrahmen, dann das Poster. Die Textur hat einen dunklen, nahezu opaken Innenbereich und muss deshalb **hinter** dem Poster liegen. Rahmen bleibt außerhalb des Bildes sichtbar; keine überdeckende Vollbild-Textur. `Control.HasFocus(id)` markiert nur die aktive Rail/das aktive Panel, kein Maus-Hover.
- Header, Reihenfolge Continue → Favoriten → Neuheiten, 4/6 Kategorie-Spalten, 24er-Batches, 240er-Fenster und Detail-Back bleiben erhalten. Dadurch keine neue Spalten-/Paging-Umstellung.

## Implementiert zu #44

`media_sequence.py` ist ein read-only Modul ohne Netzwerk, Speicherung oder Playeraufruf. Vor der bisherigen Episodennormalisierung werden explizite fremde Portal-/Serienkennzeichen ausgeschlossen. Die gewöhnliche Folgenliste darf Specials enthalten; Next verwendet nur positive, ganzzahlige Staffel-/Folgenwerte. Numerische Sortierung, Lücken und Staffelwechsel funktionieren. Doppelte IDs oder gleiche Staffel/Folge mit mehreren IDs sind keine eindeutigen Next-Kandidaten. Ungültige Metadaten bleiben auch nach einer Fenster-Reinitialisierung ausgeschlossen.

**Bezugsregel:** In der Episodenliste ist die tatsächlich markierte Folge maßgeblich. Bei Rückkehr nach eigenem Start bleibt die gestartete Folge samt Staffel und Cursor der Bezug. In der Serien-Detailansicht gilt eine lokale Auswahl-/Wiedergabereferenz derselben Portal-/Serien-ID; beim neuen Fenster alternativ die jüngste reale gespeicherte Wiedergabe mit Position. Reine manuelle Seen-Markierungen sind keine Wiedergabe. Ohne Historie/Auswahl gilt die erste gültige Folge als anfänglicher Bezug; Next benennt deren Nachfolger. Ein ungültiger bestehender Bezug wird nicht durch eine beliebige erste ungesehene Folge ersetzt. Am tatsächlichen Serienende gibt es keine Next-Aktion, keinen Wrap-around.

**Bedienorte:** Serien-Detailaktionsliste und eigener Button **340** oberhalb der Folgenliste, rechts neben der Augenlegende. Die Aktion nennt Staffel/Folge des Ziels. In der Folgenliste **Rechts → Next**, ohne die markierte Folge zu wechseln; alternativ zur ersten Zeile hoch, nochmals Hoch → Next; von der Suche Down → Next; Next Down → Folgenliste. Die Folgenliste bleibt vollständig bedienbar. Auswahländerungen aktualisieren den Button auf dem Owner-Thread, auch wenn Kodi ein natives Ereignis konsumiert; stationäre Owner-Polls sortieren die Liste nicht erneut. Kein Providerzugriff auf D-Pad.

Nur ein expliziter Klick startet Next. Vorher wird der lokale Kontext erneut validiert; während einer ausstehenden eigenen Wiedergabe keine zweite Next-Anforderung. Der vorhandene Startpfad/Resolver bleibt erhalten. Bei Staffelwechsel merken wir Zielstaffel, Staffelcursor und Episodencursor für die bestehende .18-Rückkehrlogik. Back zur Serien-Detailansicht aktualisiert deren Next-Aktion. **Kein automatischer Start bei natürlichem Ende, Stop oder Back.**

## Schutz, Prüfungen und Restpunkte

Keine Änderungen an `media_progress.py`, `media_state.py`, `media_intent.py`, `playback_exit.py`, OwnerDispatch, Service, Live-TV, EPG, Katalogindex, Artwork-Downloader/Budget oder globalen Keymaps. Keine DB-Migration/neue persistente Referenzdatei. Bestehende Augen, Continue-Hidden-Store, Resume/Favoriten/Gesehen bleiben unverändert. Frühere ZIPs und produktive Indexdateien bleiben bytegleich. 35 fremde WIP-Dateien werden separat kontrolliert.

Neue Tests prüfen Layout/Layering, native Rail-Auswahl/Back für Filme und Serien, alle Seen-Konstellationen, numerische Reihenfolge, Staffelgrenzen, Serienende/fehlende Folgen, Portal-/Serienvalidierung, doppelte/ungültige Metadaten, lokale Fortschrittsreferenz, natürliche Rückkehr mit/ohne onInit, kein automatischer Start und persistente Zustandsdaten. Die vorhandenen .18-Paginationtests einschließlich 24/48/240/1.703 synthetischer Titel und Stop-/Back-/Resume-Suites laufen unverändert in der Gesamtsuite mit. Nur die ausdrücklich geänderten Größen-/Kontrast-/Controlzahl-Verträge wurden angepasst; Baseline-Hashes bleiben erhalten.

**#74 bleibt offen:** subjektive TV-Lesbarkeit/Postergröße, Rahmen auf hellen/dunklen Postern, 720p/1080p, BINGIE/Estuary und optionales Theme auf Gerät abnehmen. **#44 bleibt offen:** neue manuelle Next-Funktion auf Android, Mehrportal-Isolation, Offline-/Providerfehler und übrige Sonderfälle. Die .18-Teil-PASS bleiben gültig; sie ersetzen keine .19-Abnahme. Artwork-Budget #90/#91/#69 und Catch-up/Guide bleiben eigene Pakete.

Alle neuen .19-Funktionen Android **NOT_TESTED**. [Android-Checkboxen](ANDROID_TEST_02919_DE.md), [Autoplay-Folgeplan](AUTOPLAY_FOLGEPLAN_NACH_02919_DE.md). Vollständiger Testbericht und ZIP-SHA werden mit dem Paket ergänzt.
