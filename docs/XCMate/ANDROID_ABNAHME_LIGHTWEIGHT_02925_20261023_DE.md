# XCMate 0.1.29.25 – Android-Abnahme Lightweight / letzte Releases

**Stand:** 23.10.2026  
**Gerät:** Android 13 RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD 2.2.3, IR-Fernbedienung.  
**Installierte Testversion:** 0.1.29.25 (reguläres GS Media Repository), Basis .21–.25.  
**Umfang:** ausschließlich bestehender Lightweight-Core, Live, EPG, Filme, Serien, Artwork und Update-/Bestandssicherung. **Space Premium samt aller Grafiken/Artwork-Skin-Fokus-Typen komplett von der Abnahme ausgeschlossen.**

**Ergebnisformat:** pro Test **PASS, FAIL oder NOT_TESTED**, niemals ungeprüft PASS. Fehler mit Design (Lightweight), Uhrzeit, Ansicht und Taste beschreiben; private Provider-URLs und Zugangsdaten nicht in GitHub posten.

**Die Checkboxen hier sind ein offizieller Testplan, KEINE bereits bestandenen Tests.** Nach Nutzer-Rückmeldung in den zugeordneten Issues **Teilbefund** eintragen; Issue nur schließen, wenn vollständige Definition of Done erwiesen ist. Der eine Sammel-PASS des vorigen .24-Tests ersetzt keine Einzelabnahme.

## B – Basis, Update und Bestand

| ID | Prüfpunkt | PASS-Bedingung | Referenz |
|---|---|---|---|
| B01 | Version/Update | XCMate zeigt 0.1.29.25; normales Repository-Update, kein Installationsfehler | Release #116 |
| B02 | Datenbestand | Portale, aktivierte Gruppen, Favoriten und Resume sind weiterhin vorhanden | Regression |
| B03 | Original-Icon | Original-XCMate-Icon ist auf der Kodi-Add-on-Kachel korrekt | Issue #37 (Teilabnahme) |
| B04 | Start & Zurück | XCMate-Startseite, Filme, Serien und EPG öffnen; Back kehrt zuverlässig zur XCMate-Startseite zurück | Issue #59 |

## M – Filme/Serien im Lightweight-Design

| ID | Prüfpunkt | PASS-Bedingung | Referenz |
|---|---|---|---|
| M01 | Film-Navigation | Filmgruppen und Kachelraster mit D-Pad: ausgewähltes Poster eindeutig sichtbar | Issue #115 (nur Lightweight-Regressionsprüfung) |
| M02 | Film-Detail OK | Film öffnen und sofort OK drücken, auch während Metadaten nachladen: Aktion statt ungewollter Suche | Issue #115 |
| M03 | Weitere Detailaktionen | Favorit/Posterstatus gezielt wählen; OK führt genau die sichtbare Auswahl aus | Issues #115 / #111 |
| M04 | Suche | Suche öffnet ausschließlich bei bewusst markierter Suchfunktion; Rückkehr ohne Fokusverlust | Issue #115 |
| M05 | Serien-Navigation | Serie → Staffel → Episode: sichtbarer Fokus, richtige OK-Auswahl, Back je eine Ebene | Issue #115 |
| M06 | Zurück aus Player | Film/Episode stoppen: Detail-/Episodenansicht ist sofort wieder navigierbar | Issues #79 / #115 |
| M07 | Dateiauswahl | Kodi-Datei-/Ordnerbrowser für XCMate-Zielordner: Auswahl sichtbar; D-Pad/OK/Back funktionieren | Issue #115 (Systemdialog separat) |

## P – Wiedergabe und Live-TV

| ID | Prüfpunkt | PASS-Bedingung | Referenz |
|---|---|---|---|
| P01 | Filmwiedergabe | Filmstart, Pause, Fortsetzen und Resume nach Stop/Neustart funktionieren | Issue #79 / Regression |
| P02 | Autoplay Folge | Am natürlichen Episodenende startet automatisch die nächste verfügbare Folge derselben Staffel | Issue #85 (Teilabnahme) |
| P03 | Autoplay Stop | Aktives Stop/Zurück verhindert zuverlässig den Start der nächsten Episode | Issue #85 (Teilabnahme) |
| P04 | VOD-Bedienleiste | Während Film/Serie ist Player-OSD sichtbar/fokussierbar; unterstützte Player-Aktionen funktionieren | Issue #79 |
| P05 | Live-TV | Live-Startsender, OK-Infobar, Links-Sender/Gruppenliste, Hoch/Runter Senderwechsel und Back funktionieren | Live-Regression |

## E – Großes EPG und Quellen

| ID | Prüfpunkt | PASS-Bedingung | Referenz |
|---|---|---|---|
| E01 | Startgruppe | Großes EPG startet in konfigurierte Startgruppe mit korrektem Startsender | Issue #88 |
| E02 | Raster-Fokus | D-Pad vertikal Sender, horizontal Sendungen; Titel des fokussierten Programms bleibt sichtbar | Issues #57 / #92 |
| E03 | EPG-Kopfbuttons | Alle vorhandenen Tages-/Heute-/Uhr-/Senderkopfaktionen fokussierbar und korrekt bedienbar | Issue #92 |
| E04 | Gruppenwahl | Links zur Sendergruppenauswahl, neue Gruppe übernehmen, zurück zu korrektem EPG | Issue #88 |
| E05 | EPG OK-Aktion | OK zeigt passende Programm-Aktionen; Jetzt ansehen spielt richtigen Sender; Back ohne Kodi-Absturz | Issues #57 / #88 |
| E06 | Doppelte Einträge | Keine unbeabsichtigt doppelten Senderzeilen/Programmereignisse; legitime HD/UHD-Varianten bleiben | Issue #58 |
| E07 | EPG-Quellenstatus | EPG-Quellen/Status und jetzt/gleich-Daten bei ausgewählten Sendern plausibel; leere Sender kenntlich | Issue #60 (Teilabnahme) |

## A – Artwork und Diagnostik

| ID | Prüfpunkt | PASS-Bedingung | Referenz |
|---|---|---|---|
| A01 | Poster bleiben erhalten | Bereits geladene Poster bleiben nach Scrollen, Back und Kodi-Neustart erhalten | Issue #41 |
| A02 | Poster-Einzeldiagnose | Fehlenden Film öffnen (z. B. Aladdin 1992), Posterstatus zeigt aussagekräftigen Fehlercode statt pauschal Netzwerk | Issue #111 |
| A03 | Gezielter Einzelretry | Nur betroffenen Titel neu versuchen: Statuswechsel/Fortschritt sichtbar, gültige Quelle kann READY erreichen | Issue #111 |
| A04 | Artwork-DB/Queue | Artwork-Status ist erreichbar; DB_BUSY wird von Netzwerk/Platzfehlern getrennt und ohne Komplettreset behandelt | Issues #90 / #111 |

## Absichtlich nicht enthalten

- **Space Premium**: Navigation, Grafiken, Texturen, visueller Fokus und Theme-Vergleich – ausdrücklich ausgeklammert; #115 damit höchstens in allgemeinen Lightweight-Teilbereichen, **nicht vollständig** abnahmefähig.
- **B02 automatischer Staffelübergang** (Staffel N letzte Folge → nächste Staffel) weiterhin nicht getestet und kein Ausschlussgrund für P02 innerhalb einer Staffel.
- **Manuelle „EPG zuweisen“-Livevorschau #98**, solange Funktionalität nicht ausdrücklich verfügbar/nachgewiesen ist; nicht als PASS markieren.
- **Native Direct-TS #117 / EPG-Aufnahmetimer #62 / VOD-Downloads #63 / Meine Medien #113** sind noch nicht produktiv in .25 integriert; keine scheinbare Abnahme über Checkboxen.

## Ergebnisverarbeitung

- Jeder als PASS angegebene Test wird nach Nutzerübermittlung als **Android-PASS für genau diese Teilfunktion** in den entsprechenden GitHub-Issues kommentiert.
- Jeder FAIL bleibt offen und führt zu einem konkreten reproduzierbaren Fehlerbefund. NOT_TESTED ist kein PASS/FAIL.
- Sammel-Issues #37/#57/#60/#79/#85/#88/#92/#115 erst nach kompletter Abnahme ihrer Anforderungen schließen; PASS eines Teiltests bedeutet nicht „Issue vollständig behoben“.
- **Kein ungefragter Merge, Release, Designtausch oder globaler Cache-Reset während der Abnahme.**

**Anzahl Einzeltests: 27.**
