# .28-A – Detailmenü #131

Basis: main .27, Android **13 PASS / 15 FAIL / 0 NOT_TESTED** unverändert.
Such-/Live-Reparatur A01–A08 ist real PASS und bleibt unverändert.

Die .27-UI zeigte nur die Kindliste explizit und überließ die Elternsichtbarkeit
einer Window.Property-Info-Expression. Die bisherige Mock-UI modellierte deren
native Auswertung nicht. .28 zeigt und verbirgt Gruppe 800 **und** Liste 810
explizit. Bei verzögerter nativer Sichtbarkeit wird der Fokus über den bereits
vorhandenen Owner-Mechanismus nachgeholt. Der genaue alte Android-Pfad ist ohne
neuen Geräte-Trace nicht abschließend bewiesen.

Zusätzlich ist **Aktionen** auf jeder Film-/Seriendetailseite sichtbar; Rechts
von der bisherigen Aktionsliste führt dorthin. OK und Links öffnen dieselbe
Menükomponente. Fehlende Aktionsmetadaten oder ein alter Playback-Wartezustand
verstecken den Menüeinstieg nicht mehr. Ein Refresh derselben Detailseite lässt
ein bereits offenes Menü stehen. Keine globalen Keymaps oder Player-Änderungen.

Je Zeile PASS/FAIL/NOT_TESTED erfassen (neue Tests zunächst NOT_TESTED):

- [ ] M01 Film öffnen, Links: sichtbares Menü und Fokus auf erstem Eintrag.
- [ ] M02 Serie öffnen, Links: dasselbe Menü, reale Episodenauswahl erreichbar.
- [ ] M03 Film und Serie: sichtbaren Aktionen-Button mit Rechts/OK benutzen,
  unabhängig davon, ob die IR-Fernbedienung den Links-Callback liefert.
- [ ] M04 Rechts/Zurück schließt nur das Menü; gleiche Details/Aktionsposition.
- [ ] M05 Mehrfach öffnen/schließen, nach Stop/Resume und nach Detailrefresh.
- [ ] M06 Menüaktionen ausführen: gezielter Poster-Retry/Status und Downloads.
- [ ] M07 Erhaltene globale Suche, Such-Live, EPG, Live-IR, Staffelautoplay/Stop,
  Portale, Favoriten, Resume und Originalicon prüfen.

Anonyme `[XCMate][DETAIL_MENU]`-Stufen zeigen Linkseingang bzw. Button,
Eligibility, Eltern-/Listenanzeige, Fokusziel und Schließen. Keine Titel/IDs/URLs.
Kein Android-PASS aus Host-Tests ableiten. Aufnahme-/Download-Speicher und
Streamdiagnose folgen im separaten kumulativen .28-B-Draft.
