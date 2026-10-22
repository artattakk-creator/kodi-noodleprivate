# 0.1.29.13 – erste horizontale XCMate-Programmzeitschrift (#57)

**Veröffentlichungsstatus 22.10.2026:** [PR #82](https://github.com/artattakk-creator/kodi-noodleprivate/pull/82) auf ausdrückliche Nutzeranweisung nach `main` gemergt; [GitHub-Publish PASS](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39733665167); `addons.xml` meldet 0.1.29.13. **Android-Ersttest: Layout positiv, Gruppen-/Logo-/XMLTV-Korrekturen offen (Issue #88).**

Basis: 0.1.29.11 / Statusfix #80. Eigener Branch, nicht mit Player-OSD oder
Medien-UI kumuliert. Unter dem bestehenden Hauptmenüpunkt EPG öffnet die native
Action-Route guide_grid das neue Raster. guide_browser und die bisherige
GuideWindow bleiben als kompatible alte Route unverändert vorhanden. Keine
Änderung an Live-Overlay, Gruppenwahl, Startsender, Settings oder EPG-Mappings.

## Testbarer Funktionsumfang

Fixierte linke Spalte mit lokalem Senderlogo und mehrzeiligem vollständigem
Namen; rechts ein gemeinsames Drei-Stunden-Zeitfenster (896 Pixel), halbstündliche
Uhrzeiten oben, proportionale Sendungsblöcke und eine echte Jetzt-Linie. Links
bleibt beim horizontalen Scrollen stehen, alle Sender benutzen dieselbe UTC-Achse.
Ein 4-Pixel-Neonrahmen zeigt den ausgewählten sichtbaren nativen Button an.
Die Senderreihenfolge kommt aus den aktivierten vorhandenen Gruppen im Reader.

Acht Senderzeilen und ein fester Pool von 24 Programmbuttons pro Zeile bilden
nur den sichtbaren Ausschnitt ab. Der Testkatalog hat 2.501 Sender; diese werden
nicht alle als native Controls aufgebaut. Sehr dichte Listen zeigen einen
Hinweis; beim Erreichen weiterer Ereignisse wird exakt zum gewählten Beginn
geblättert, statt unerreichbare Programme oder eine Endlosschleife zu erzeugen.
Lücken haben ausdrücklich Keine Programmdaten, keine erfundenen Sendungen.

Hoch/Runter behält die Zeitposition und wechselt Sender, Links/Rechts wählt
Programme/verschiebt das gemeinsame Zeitfenster. Innerhalb des geladenen
Ausschnitts keine DB-/HTTP-Abfrage durch Richtungstasten. An Seiten-/Zeitgrenzen
lädt der vorhandene Owner-Worker die nächste kleine lokale Seite. Header:
Vortag, Folgetag, Jetzt, Gruppen, Suche und 20:15. Tageswechsel benutzt lokale
Kalenderdaten (auch 23-/25-Stunden-DST-Tage), Ereignisse bleiben UTC-Sekunden.
Bis zu zehn Kalendertage sind erreichbar, **nur tatsächliche Quelldaten** werden
gezeigt. Kein neues Versprechen einer flächendeckenden 7–10-Tage-Versorgung.

OK öffnet ein natives Aktionsmenü. Back darin schließt zuerst dieses Menü;
Back im Raster kehrt nach dem geschützten 150-ms-Owner-Abschluss zu Home zurück.
Schnelle weitere Back-Eingaben werden währenddessen ignoriert. Suchnavigation
wird erst nach Rückkehr aus dem Window-Owner ausgelöst, kein rekursiver Start.

Aktionen: Programmdetails/Quellenstatus, Sender jetzt ansehen, zukünftige
Erinnerung über guide_timers sowie bewusst bestätigtes Merken in einer eigenen
lokalen Bookmarkdatei. Die Merkliste ist im Aktionsmenü lesbar. Kontext/Menu 117
öffnet die senderbezogenen Infos/Aktionen als verlässlicher Long-OK-Fallback;
gerätespezifische Long-Press-Erkennung bleibt bei der Android-Abnahme zu prüfen.
Eine zukünftige Sendung schaltet mit Sender jetzt ansehen **nur auf den Sender
jetzt**, keine simulierte zukünftige Wiedergabe. Xtream benutzt play_live,
M3U/STB source_play; IDs kommen aus der aktiven Reader-Seite. Navigation allein
startet nie Wiedergabe. Recorder/Catch-up/TMDB sind nicht als fertige Aktionen
angeboten. Download/Aufnahme-/Engine-Ausbau bleibt ein eigener Auftrag.

## Daten und Hintergrundaktualisierung

Das Raster liest guide_v1.sqlite explizit mode=ro, begrenzt Warte-/Queryzeit und
maximal 100 Kandidaten je sichtbarem Sender. Es erzeugt/migriert/repariert keine
EPG-Datenbank. Manuelle Zuordnung bleibt maßgeblich, dann gespeicherte Aliase/
Provider-ID; bestehendes defensives Deduplizieren aus #58 wird wiederverwendet.
Die mehrdeutige/nicht vorhandene Zuordnung bleibt als solche sichtbar. Keine
automatischen neuen Treffer und kein Überschreiben bestehender Mappings (#60).
Der historische Wert 288/2764 ist keine aktuelle Coverage-Messung; der Footer
zählt nur sichtbare Sender mit realen Ereignissen im aktuellen Ausschnitt.

Ist kein Langzeitereignis vorhanden, darf im aktuellen Zeitfenster ausschließlich
bereits gecachtes Short-EPG als klar benannte Quelle dienen. Ein kleiner
Service-Hinweis kann acht sichtbare Short-Guides im Hintergrund vorbereiten;
keine Provider-Anfrage aus onAction. Alle Senderlogos kommen als lokale Pfade
oder neutraler Fallback aus dem vorhandenen persistenten Artwork-Cache. Der
Viewport-Worker kann dessen begrenzte Queue nutzen; der UI-Owner aktualisiert
fertige Bilder anhand der lokalen Revision. Kein neuer Cachepfad/Reset und
keine Übergabe geheimer Remote-Textur-URLs an Kodi.

Änderungen der Short-Guide-Revision und ein 30-Sekunden-Refresh aktualisieren
nur die sichtbare lokale Seite im Worker. Bei temporärem Fehler während eines
solchen Refreshs bleibt die vorherige Ansicht bedienbar. Fehlende DB oder
Daten bleiben ein ehrlicher Leer-/Fehlerzustand. Bestehende Service-Importe
arbeiten wie bisher; das neue Raster stößt keinen Vollimport an.

## Noch kein vollständiger Guide-Ausbau

Erweiterter Sender-Zuordnungseditor, Favoriten-/Genre-/Kalenderfilter, TMDB-
Enrichment und Sendungsbilder, Catch-up mit verifiziertem Archivfenster sowie
Aufnahmetimer nach echter Recorder-Capability bleiben Folgeschritte. Es werden
keine ungetesteten oder mangels Engine funktionslosen Aufnahmebuttons gezeigt.
Die SVG-Modellansicht verwendet synthetische Beispieldaten und ist ausdrücklich
**kein Kodi-/Android-Screenshot**. Echte Bild-/TV-Abnahme ist noch offen.

## Android-Ersttest – 22.10.2026 (nach Veröffentlichung)

**Layout positiv vom Nutzer bewertet**, horizontaler Guide angezeigt. **Funktionale Abnahme NICHT bestanden:** Die Sender aller aktivierten Gruppen werden beim Einstieg gemischt, weil `category=None` voreingestellt ist; Nutzer verlangt zuerst eine native Gruppenliste und anschließend EPG *nur der gewählten Gruppe*, Back/Links wieder zur Gruppenliste. Senderlogos erscheinen noch nicht (Cache-/Quelle-/Budgetursache überprüfen, Artwork 514/512 MB und viele SPACE_FULL-Jobs gemeldet). XMLTV-Zuordnung soll direkt aus dem Senderkontext des Rasters erreichbar sein; nur einige Sender haben EPG-Daten. Verbindlicher Auftrag [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88), Mapping-Kontext [#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60). Keine Mergefreigabe für Folgefix oder weitere Drafts ohne explizite Nutzerbestätigung.

## Android-Testplan (teilweise durchgeführt; weitere Abnahme offen)

1. Zuerst Statusfix 11 abnehmen, Profil sichern, dann nur dieses isolierte ZIP.
2. Hauptmenü EPG: feste Sendernamen/-logos links, echte Sendungen rechts,
   durchgehende Uhrzeitachse. Dauerverhältnisse und Jetzt-Linie kontrollieren.
3. Hoch/Runter über mehrere 8er-Seiten, Links/Rechts über Zeitgrenzen, Jetzt,
   20:15, mehrere Tage und Mitternacht. Zeitachse muss für alle Sender gleich sein.
4. Bei vielen Sendern und leeren Daten Reaktion/Memory beobachten. Native grüne
   Fokusmarkierung muss eindeutig sein. Keine Wiedergabe durch bloße Pfeile.
5. OK Details, Back nur aus Kontext. Sender jetzt ansehen bewusst wählen,
   auch bei zukünftiger Sendung: richtiger Account/Sender startet jetzt.
6. Zukünftige Erinnerung, bestätigtes Merken/Merkliste und Neustart prüfen.
   Timer verspricht keine Aufnahme/Auto-Tune/Wakeup. Ohne Recorder kein Button.
7. Menü/Long-OK, Gruppe wählen und Suche; zurück jeweils sinnvoll. Schnelles
   Doppel-Back ohne Spinner/Freeze. Alte guide_browser-Route weiter prüfen.
8. Manuell gemappte und ungemappte Sender sowie Short-/XMLTV-Fallback vergleichen;
   keine erfundenen Programme, legitime Varianten/Wiederholungen bleiben.
9. Während Hintergrundupdate weiter navigieren: passende Daten/Logos aktualisieren
   ohne Fokusdiebstahl. UI-Keys dürfen keinen synchronen HTTP-Aufruf auslösen.
10. Live-TV-OK/Senderliste/Gruppen, Film-/Serien-Back/Resume unverändert prüfen.
    Kodi 21.2 ARM32/BINGIE MOD, zusätzlich Estuary. Raster-/Kontext-Screenshots
    erstellen, tatsächliche Coverage und 20-Minuten-Stabilität protokollieren.

Nach expliziter Nutzerfreigabe in `main` veröffentlicht. Android-Ersttest des Rasters ergab offenen Gruppen-/Logo-/Mapping-Blocker (#88); vollständiger Android-Test steht aus. 0.1.29.11 bleibt die zuletzt auf Android funktional geprüfte Arbeitsversion (mit dokumentierten Restbefunden); 0.1.29.8 bleibt älterer stabiler Rückfallstand.

## Host-Verifikation

584/584 Tests PASS (81,848 s), darunter 16 neue Rasterfälle. Reale temporäre
SQLite-Dateien, 2.501 Sender, geclipte/proportionale Geometrie, autoritative
manuelle Zuordnung, fehlende DB/Daten, dichte Listen, schneller Back-Abschluss,
DST-Tageswechsel, kontrollierte Watch-Aktion, Merkliste und lokale Logo-Nachladung.
CRC/Pfade/Source-Bytes/Python-AST und unabhängige byteidentische ZIP-Reproduktion
PASS. Siehe TESTERGEBNISSE_02913_GUIDE_GRID.json und vollständiges Testlog.
Dies ist keine tatsächliche Android-GUI-/Langzeitabnahme und keine neue reale
Provider-Coverage-Messung.
