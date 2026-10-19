# CODEX-ARBEITSAUFTRAG – XCMate 0.1.28
## Performance, EPG, Medienkataloge, Live-TV-Preloading und UI-Einstellungen

**Projekt:** XCMate – GS Media Kodi IPTV Add-on  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Aktuelle Produktivversion:** 0.1.27  
**Zielversion:** 0.1.28  
**Add-on-ID:** `plugin.video.xtreammate`  
**Zielplattform:** Kodi 21 Omega / Android-TV / Titan BINGIE MOD  
**Auftrag:** Fehlerbehebung, Performance-Optimierung und Erweiterung der bestehenden Installation.

---

## 1. Verbindliche Ausgangslage

XCMate 0.1.27 ist bereits auf dem Android-TV installiert und wurde real getestet.

### Erfolgreich getestete Funktionen – FREEZE

- Live-TV-Wiedergabe grundsätzlich funktionsfähig
- Fernbedienung funktioniert
- OK-/D-Pad-/Links-/Zurück-Navigation funktioniert
- Bestehende Live-TV-Overlays und Bedienebenen funktionieren
- Startsender und vorhandene Einstellungen bleiben erhalten

**Diese funktionierende Basis darf nicht beschädigt werden.**

### Festgestellte Probleme

1. EPG-Aktualisierung schlägt bei mehreren Quellen fehl.
2. Filmkatalog öffnet nicht korrekt; Kodi-Fehlerton und langer Spinner.
3. Serienkatalog zeigt nach langer Wartezeit `Data Unavailable ValueError`.
4. Meldung `Index-Katalog nicht verfügbar` bei Filmen und Serien.
5. Globale Xtream-Kataloge sind für die aktuelle Verarbeitung zu groß.
6. Suche aus dem Filmbereich liefert keine Ergebnisse.
7. Sehr lange Ladezeiten, teilweise minutenlang.
8. Auch nach Verlassen von Live-TV kann ein Spinner lange bestehen bleiben.
9. EPG lädt nicht vorrangig die Startsendergruppe.
10. Die untere Live-TV-Statusleiste erscheint erst verspätet.
11. Keine XCMate-eigene Sprachauswahl.
12. Keine Einstellmöglichkeiten für Skin, Farben, Grafiktransparenz und Schrift.

### Verbindliche GitHub-Issues

- #17 – Live-TV-Fernbedienung / OSD-Freeze
- #25 – Gemeinsame Suche
- #29 – Sprachverwaltung
- #30 – Lightweight Core / optionale Erweiterungen
- #31 – Skin und Darstellung
- #32 – EPG-Importfehler
- #33 – Große Film-/Serienkataloge, ValueError und Spinner
- #34 – Startgruppe priorisieren, nur aktivierte Gruppen laden
- #35 – Live-TV-Statusleiste vor Streamstart

Alle Issues und die aktuelle Projektdokumentation vor der Implementierung lesen.

---

# PHASE A – P0: KATALOGVERARBEITUNG GRUNDLEGEND REPARIEREN

## 2. Globale Größenbeschränkungen ersetzen

Der aktuelle Code verwendet unter anderem:

- `network_io.MAX_HTTP_BYTES = 80 MiB`
- `epg_io.MAX_XML_BYTES = 80 MiB`
- `library_index.MAX_ROWS = 200000`
- SQLite-Indexbudget von ungefähr 64 MiB

Diese Grenzen verhindern beziehungsweise gefährden die Verarbeitung umfangreicher Provider-Kataloge.

**Neue Vorgabe: Die Gesamtgröße des verfügbaren Film-, Serien- und Senderbestands darf nicht durch diese pauschalen Grenzen ausgeschlossen werden.**

Die Grenzwerte jedoch nicht einfach unbeschränkt erhöhen oder ersatzlos entfernen.

Stattdessen implementieren:

1. Streaming-Verarbeitung großer HTTP-Antworten.
2. Stückweises JSON-Parsing ohne vollständiges Laden in den Arbeitsspeicher.
3. Inkrementelle Verarbeitung und Speicherung in SQLite.
4. Batch-Insert mit begrenzter Transaktionsgröße.
5. Unabhängige Indizes für Live-TV, Filme und Serien.
6. Belastbare Speicherung auch bei sehr großen Katalogen.
7. Kontrollierte Speicher- und Plattenplatzbudgets.
8. Sichere Wiederaufnahme beziehungsweise erneute Synchronisierung nach Unterbrechungen.
9. Atomare Aktualisierungen und Erhalt des letzten funktionierenden Datenbestands.
10. Keine unkontrollierte RAM-Belegung auf schwachen Android-TV-Sticks.

Ziel ist die vollständige Verarbeitung **aller vom Nutzer aktivierten Gruppen**, soweit Datenträger und technische Ressourcen tatsächlich ausreichen.

Die Speicherbegrenzung soll einzelne Verarbeitungsschritte schützen, nicht die gesamte Mediensammlung künstlich abschneiden.

Besonders untersuchen:

- `network_io.py`
- `utils.py`
- `xtream.py`
- `library_index.py`
- `app_services.py`
- `media_window.py`

Den konkreten Auslöser der gemeldeten `ValueError`-Exceptions anhand von Tests und aussagekräftiger, datenschutzkonformer Fehlerdiagnostik ermitteln.

## 3. Nur aktivierte Gruppen laden

Verbindliche Grundregel:

**Deaktivierte Gruppen werden nicht unnötig heruntergeladen, indiziert oder aktualisiert.**

Diese Regel gilt getrennt für:

- Live-TV-Sendergruppen
- Filmgruppen
- Seriengruppen

Die gespeicherte Gruppenauswahl ist die maßgebliche Quelle.

### Neue Datenladereihenfolge

1. Aktivierte Gruppen des jeweiligen Medientyps feststellen.
2. Zuerst die ausgewählte beziehungsweise bevorzugte Gruppe laden.
3. Vorhandene lokale Datensätze sofort anzeigen.
4. Weitere aktivierte Gruppen schrittweise im Hintergrund ergänzen.
5. Deaktivierte Gruppen ignorieren.
6. Änderungen der Gruppenauswahl gezielt übernehmen, ohne den gesamten Katalog neu aufzubauen.

Für Xtream Codes möglichst die bereits unterstützten Kategorieparameter nutzen:

- `get_live_streams(category_id)`
- `get_vod_streams(category_id)`
- `get_series(category_id)`

Prüfen, ob der jeweilige IPTV-Anbieter die serverseitige Filterung tatsächlich unterstützt.

Wenn nicht, kontrollierte Streaming-Verarbeitung und lokales Filtern einsetzen.

## 4. Medienfenster sofort bedienbar machen

Beim Öffnen von „Filme“ darf nicht gleichzeitig ein kompletter Neuaufbau aller Live-TV- und Serienkataloge stattfinden.

Analog darf „Serien“ nicht unnötig den Film- und Live-TV-Katalog mitverarbeiten.

Die aktuelle Medieninitialisierung über `media_window._initial()` und `library_index.refresh()` gezielt überarbeiten.

Sollverhalten:

- Fenster erscheint sofort.
- Bereits vorhandene Gruppen und Cover werden direkt dargestellt.
- Fehlende Daten werden im Hintergrund geladen.
- Sichtbare Gruppe hat Vorrang.
- Nachfolgende Gruppen werden portionsweise ergänzt.
- Spinner blockiert weder Navigation noch Zurück.
- Wiederholtes Öffnen startet keine identische Vollindexierung.
- Bei Fehler erscheint eine verständliche Meldung mit Wiederholoption.
- Bestehende Favoriten, Resume-Daten und Indexstände bleiben erhalten.

Große Medienbestände müssen paginiert dargestellt und durchsuchbar bleiben.

### Performance

Ladezeiten anhand echter Messwerte dokumentieren:

- Klick bis Fenster sichtbar
- Klick bis erste benutzbare Kategorie
- Klick bis erstes Poster
- Dauer der Hintergrundindexierung
- Speicherverbrauch
- Dauer des Schließens
- Reaktion auf Zurück während eines laufenden Imports

Sowohl Kaltstart als auch Start mit vorhandenem Cache testen.

Keine minutenlangen Spinner als regulären Betriebszustand akzeptieren.

---

# PHASE B – P0: EPG REPARIEREN UND PRIORISIEREN

## 5. Bestehende Importfehler beheben

Reale Android-TV-Diagnose aus Version 0.1.27:

| Quelle | Fehler |
|---|---|
| Anbieter-XMLTV | `HTTP_INPUT_BYTES_LIMIT` |
| Deutschland Kaimandura | `PARSE_FAILED / TypeError` |
| Deutschland EPGShare01 | `PARSE_FAILED / TypeError` |
| Österreich EPGShare01 | `INVALID_XMLTV / ValueError` |

Gerätestatus:

- 3.149 aktivierte Xtream-Sender
- 413 XMLTV-Zuordnungen
- 2.736 Sender ohne XMLTV-Zuordnung
- Nur vier gültige Programme innerhalb der nächsten 48 Stunden
- Kein bestätigter erfolgreicher Import für die angezeigten Quellen

Aufgaben:

1. XMLTV-TypeError reproduzieren und beheben.
2. Sichere GZIP-/XML-Verarbeitung prüfen.
3. Echte ungültige XML-Dateien von Parserfehlern unterscheiden.
4. Große Anbieter-EPGs mittels begrenzter Streaming-Verarbeitung unterstützen.
5. Erfolgreiche Teildaten erhalten, auch wenn einzelne Quellen scheitern.
6. Manuellen Refresh mit echtem Status und Abschlussergebnis versehen.
7. XMLTV-Matching nach Sender-ID und Namen verbessern.
8. Bestehende manuelle Zuordnungen erhalten.
9. Fehlerhafte Imports dürfen den letzten funktionierenden EPG-Cache nicht zerstören.

Sicherheitsprüfungen für XML-Entities, Speicherverbrauch und ungültige Daten beibehalten.

## 6. Startsendergruppe hat absolute Priorität

Der Nutzer hat einen Startsender und eine aktivierte Startgruppe definiert.

Diese Gruppe wird außerdem im Startseiten-Widget verwendet.

Deshalb gilt folgende EPG-Priorität:

**P0:** Startsender – Jetzt/Danach  
**P1:** Sichtbare Sender der Startgruppe  
**P2:** Übrige Sender der aktivierten Startgruppe  
**P3:** Weitere aktivierte Sendergruppen  
**P4:** Nur bei Bedarf andere Daten, jedoch niemals deaktivierte Gruppen aktualisieren

Implementierung:

- Vorhandenen EPG-Cache sofort verwenden.
- Für Startsender und sichtbare Sender bei Bedarf gezielte Xtream-Short-EPG-Abfragen durchführen.
- Die Daten im lokalen Cache beziehungsweise passenden Snapshot speichern.
- Startseite, Live-TV-Infoleiste, Senderliste und EPG verwenden dieselben Daten.
- Kein separater vollständiger Download bei jeder Anzeige.
- Keine HTTP-Abfragen auf dem Fernbedienungs-/GUI-Thread.
- XMLTV-Gesamtfeeds nur dann vollständig übertragen, wenn die Quelle keine selektive Alternative ermöglicht und dies ausdrücklich erforderlich ist.
- Aus Gesamtfeeds nur relevante Programme für aktivierte Sender persistieren, soweit die Quelle dies technisch zulässt.

Der Startsender soll seine EPG-Daten möglichst bereits vor dem Öffnen von Live-TV verfügbar haben.

---

# PHASE C – P0: LIVE-TV-PRELOADING UND SOFORTIGE STATUSLEISTE

## 7. Neue Senderstart-Reihenfolge

Der Nutzer möchte nicht mehr warten, bis das Videobild aufgebaut ist, bevor die XCMate-Statusleiste erscheint.

### Verbindlicher Ablauf

**Schritt 1 – Sender auswählen**

Sender über Live-TV-Liste, Startgruppe, Startsender oder Fernbedienung auswählen.

**Schritt 2 – XCMate-Info-/Statusleiste sofort anzeigen**

Die untere Leiste soll bereits sichtbar sein, bevor Kodi den eigentlichen Stream fertig aufgebaut hat.

Anzeigen:

- Senderlogo
- Sendername
- Aktuelle Sendung, sofern im Cache verfügbar
- Nächste Sendung, sofern verfügbar
- Programmfortschritt bei gültigen EPG-Daten
- Verbindungsstatus: „Verbinde …“ / „Puffert …“

Fehlende Daten ehrlich kennzeichnen.

**Schritt 3 – Stream starten**

Danach die bestehende Kodi-Player-Auflösung durchführen, ohne die sichtbare Oberfläche unnötig zu blockieren.

**Schritt 4 – Wiedergabe aktiv**

Nach bestätigter Wiedergabebereitschaft die Statusleiste aktualisieren und nach der regulären Anzeigedauer ausblenden.

### Technischer Auftrag

Die aktuelle Prüfung in `live_overlay.start_if_eligible()` setzt `Player.isPlayingVideo()` voraus.

Diese Abhängigkeit für eine neue, sichere **Pre-Play-Anzeige** auflösen.

Zu prüfen:

- `live_overlay.py`
- `service.py`
- `player.py`
- `main.py`
- Session-Marker und Playback-Ownership
- Kodi-21-Player-Handshake
- Fokus-/Z-Order-Verhalten

Wichtig: Der eigentliche Player darf nicht durch eine unsachgemäße Thread- oder Dialogsteuerung beschädigt werden.

Falls das bestehende LiveNavigator-Fenster vor Wiedergabebeginn nicht zuverlässig geöffnet werden kann, ein leichtgewichtiges Pre-Play-Fenster entwickeln und nach dem Videostart kontrolliert an den bestehenden Navigator übergeben.

### Hintergrundvorbereitung

Bereits vor Senderstart lokal bereitstellen:

- Aktive Startgruppe
- Startsender-Metadaten
- Logos der sichtbaren Sender
- Now/Next-EPG
- Kleine Senderindex-Snapshots
- Notwendige Overlay-UI-Komponenten

Nicht alle tausend Senderbilder auf einmal dekodieren.

**Keine zusätzlichen versteckten IPTV-Videostreams zum Vorpuffern starten.**

### Fernbedienungs-FREEZE

Unverändert erhalten:

- Einmal OK → Infobar
- Nochmals OK / Runter → Player-Bedienung
- Weitere Ebene → Einstellungen
- Links → Senderliste
- Links erneut → Gruppenliste
- Hoch/Runter im Vollbild → Senderwechsel
- Zurück → korrekte vorherige Ebene
- Stop → Wiedergabe beenden

Während des Streamaufbaus müssen Zurück und Abbrechen ebenfalls funktionieren.

---

# PHASE D – P0: SUCHE UND SPINNER

## 8. Gemeinsame Suche reparieren

Die globale Suche aus dem Filmbereich liefert auf dem Android-TV derzeit keine brauchbaren Ergebnisse.

Aktuell arbeitet sie mit dem lokalen Index aus `library_index.Reader`.

Bei fehlendem Index entsteht deshalb eine unbrauchbare Suche.

Sollverhalten:

- Suche über aktivierte Live-TV-, Film- und Seriengruppen.
- Vorhandene Treffer sofort anzeigen.
- Fehlende aktivierte Kategorien bei Bedarf nachindizieren.
- Echte Trefferzahlen je Bereich.
- Kein Unterschied zwischen Indexfehler und null Treffern verschleiern.
- Suchergebnisse paginieren.
- Neue Ergebnisse aus laufender Indexierung verfügbar machen.
- Umlaute, Groß-/Kleinschreibung und unterschiedliche Schreibweisen beachten.
- Kein unnötiger vollständiger Katalogdownload für jede Suchanfrage.

## 9. Endlosspinner verhindern

Alle betroffenen Abläufe überprüfen:

- Verlassen von Live-TV mit Zurück
- Wechsel zur Startseite
- Öffnen von Filme
- Öffnen von Serien
- Öffnen des EPG
- Globale Suche
- Hintergrundaktualisierung
- Schließen von WindowXML-Oberflächen

Anforderungen:

- Keine blockierenden langen Arbeiten im GUI-Thread.
- Hintergrundjobs begrenzen und bei identischen Anfragen zusammenführen.
- Sichtbare Fortschritts-/Fehlerzustände.
- Sicherer Abbruch.
- Keine Updates an bereits geschlossene Fenster.
- Keine mehrfach laufenden Vollindizierungen.
- Bestehenden Cache wiederverwenden.
- Thread- und SQLite-Synchronisierung zuverlässig gestalten.

Die funktionierende Live-TV-Steuerung darf dadurch nicht beeinträchtigt werden.

---

# PHASE E – P1: LANGUAGE UND SKIN

## 10. XCMate-eigene Sprachauswahl

**Verbindlicher Wunsch:** Deutsch und Englisch sollen innerhalb von XCMate auswählbar sein, unabhängig von der globalen Kodi-Sprache.

Einstellungsbereich:

`Einstellungen → Sprache → XCMate-Sprache`

Optionen:

- Deutsch
- English
- Kodi-Sprache übernehmen

Die vorhandenen deutschen und englischen Sprachdateien weiterverwenden.

Englisch bleibt technische Fallbacksprache.

Bestehende deutsche Installationen dürfen nicht ungefragt umgestellt werden.

Die IPTV-Sprachfilterung `lang_priority` bleibt davon unabhängig.

Weitere Sprachen werden später als optionale Language Packs nachinstallierbar; sie müssen nicht in die Grundinstallation.

## 11. Vollständiger Bereich „Skin & Darstellung“

Verbindliche Planung aus Issue #31 umsetzen beziehungsweise in einem eigenständigen, anschlussfähigen Modul vorbereiten.

Gewünschte Einstellmöglichkeiten:

- Standarddesign auswählen
- Optionale Designs installieren und aktivieren
- Hintergrundtransparenz / Deckkraft
- Menü-/Paneltransparenz
- Icon-/Overlaytransparenz
- UI-Hintergrundfarben
- Akzentfarben
- Auswahl-/Fokusfarben
- Schriftfarben
- Schriftgrößen
- Vorschau
- Einstellungen übernehmen oder verwerfen
- Standardwerte wiederherstellen
- Einstellungen dauerhaft speichern

**Lightweight Core bleibt verbindlich.**

Große Space-Premium-Grafikpakete gehören nicht standardmäßig in die Grundinstallation.

Die 98 Space-Premium-Grafikpositionen sind ein separates, fortlaufendes Designprojekt. Der aktuelle Freigabestand ist 16/98.

Das Theme darf nicht automatisch installiert werden.

Kodi-Systemskin und Titan BINGIE MOD bleiben unverändert.

Bei technischen Einschränkungen der Kodi-Font-/WindowXML-Verwaltung diese dokumentieren und eine kompatible Lösung implementieren, statt eine nur scheinbar funktionierende Einstellung anzubieten.

---

# PHASE F – TESTS, DOKUMENTATION UND RELEASE

## 12. Verbindliche Qualitätskontrolle

Mindestens testen:

1. Große Xtream-Filmkataloge.
2. Große Xtream-Serienkataloge.
3. Mehr als 200.000 globale Provider-Einträge.
4. HTTP-Antworten über 80 MiB.
5. Aktivierte und deaktivierte Gruppen.
6. Erste Gruppe sofort bedienbar.
7. Vollständige schrittweise Indexierung aktivierter Gruppen.
8. SQLite-Speicherung bei umfangreichen Katalogen.
9. Unterbrochene Downloads.
10. Speichermangel.
11. Offlinebetrieb mit bestehendem Cache.
12. Suche während laufender Indexierung.
13. Film-/Serien-Favoriten und Resume.
14. EPG-Import mit den bisherigen deutschen und österreichischen Quellen.
15. Startgruppen-EPG und Now/Next.
16. Pre-Play-Statusleiste.
17. Senderwechsel mit Fernbedienung.
18. Zurück/Stop während Streamaufbau.
19. Komplette bisherige Live-TV-OSD-Regression.
20. Deutsch/Englisch-Sprachauswahl.
21. Skin-Einstellungen und deren Persistenz.
22. Kodi-Neustart mit vorhandenen Daten.
23. Android-TV-Gerätetestplan.
24. Kodi-21-API-Konformität, Syntax, ZIP und CI.

Alle bisherigen erfolgreichen Regressionstests erhalten.

Tests nicht künstlich vereinfachen oder entfernen, nur um CI grün zu bekommen.

### Performance-Messungen

Vorher/Nachher-Ladezeiten dokumentieren.

Besonders:

- Live-TV-Statusleiste
- Erste Senderdarstellung
- Filme-Startseite
- Serien-Startseite
- Erste Posteranzeige
- EPG-Startsender
- Globale Suche
- Zurück aus Live-TV

Wo echte Hardwaremessungen fehlen, ausdrücklich als nicht getestet markieren.

## 13. Projekt- und Versionsmanagement

Entwicklungsbasis ist ausschließlich der aktuelle Stand von `main` mit XCMate 0.1.27.

Vor Arbeitsbeginn GitHub-Status, offene PRs, relevante Issues und letzte Commits prüfen.

Arbeiten in einem neuen Entwicklungsbranch für 0.1.28 durchführen.

Vorhandene Datenstrukturen migrationssicher weiterentwickeln.

### Unbedingt schützen

- Portal-Accounts und Zugangsdaten
- Favoriten
- Startsender
- Aktivierte/deaktivierte Gruppen
- EPG-Quellen
- Manuelle EPG-Zuordnungen
- Spracheinstellungen
- Remote-Mappings
- Film-/Serien-Fortschritt
- Bestehende Cache-Daten

Keine automatischen Resets oder Löschaktionen als vermeintliche Fehlerbehebung.

Andere Add-ons und BINGIE MOD nicht verändern.

### Verbindliche Freigaberegel

**Kein eigenmächtiger Merge nach main.**

**Keine automatische Veröffentlichung von 0.1.28.**

**Keine Änderung des produktiven Repository-Index auf 0.1.28 ohne ausdrückliche Freigabe.**

Entwicklung und Tests auf dem Branch abschließen, Draft-PR erstellen und zur Prüfung bereitstellen.

Es soll später weiterhin **eine einzige reguläre XCMate-Installation** geben, keine parallele Beta-Add-on-ID.

---

## 14. Erwarteter Abschlussbericht

Codex soll nach Bearbeitung melden:

**A. Analyse**
- Tatsächliche Ursachen des Katalog-ValueError
- Ursache des Film-Startfehlers
- Ursachen der Suchprobleme
- Ursachen der Verzögerungen
- EPG-Parserfehler und Datenlimits

**B. Implementierung**
- Geänderte Dateien
- Neue Architektur für große Kataloge
- Gruppenpriorisierung
- Streaming/SQLite-Batching
- EPG-Korrekturen
- Live-TV-Preloading
- Sprach-/Skin-Implementierungsstand

**C. Tests**
- Anzahl bestandener Tests
- Fehlgeschlagene Tests
- CI-Run-Link
- Performance-Vergleich
- Kodi-21-Kompatibilität
- Noch offene Android-TV-Tests

**D. GitHub**
- Branch
- Commit-SHA
- PR-Link
- Versionsstand
- Offene Restaufgaben

**E. Freigabe**
- Was vollständig fertig ist
- Was nur teilweise fertig ist
- Welche Punkte echte Android-TV-Abnahme benötigen
- Ob der PR technisch mergefähig ist

## 15. Arbeitsanweisung

**Beginne jetzt mit der technischen Bestandsaufnahme und setze die Aufgaben strukturiert um.**

Die Priorisierung lautet:

1. Große Kataloge zuverlässig verarbeiten.
2. Film- und Serienoberflächen reparieren.
3. Ladezeiten und Endlosspinner beseitigen.
4. Suche wieder funktionsfähig machen.
5. EPG-Import reparieren und Startgruppe priorisieren.
6. Live-TV-Statusleiste vor Streamstart und Preloading umsetzen.
7. Separate XCMate-Sprachauswahl integrieren.
8. Skin-&-Darstellungsverwaltung ergänzen.
9. Vollständige Regressionstests und Dokumentation.

Wenn einzelne Phasen nicht sicher innerhalb eines PRs abgeschlossen werden können, die Arbeiten in nachvollziehbare Commits beziehungsweise untergeordnete PRs aufteilen und Abhängigkeiten dokumentieren. Die priorisierten Stabilitätsfehler dürfen nicht durch halbfertige Designfunktionen verzögert werden.

**WICHTIG: Die in 0.1.27 bereits funktionierende Fernbedienungs- und Live-TV-Navigation ist ausdrücklich eingefroren.**

Alle Änderungen vorbereiten und testen, aber bis zur ausdrücklichen Nutzerfreigabe nicht produktiv veröffentlichen.