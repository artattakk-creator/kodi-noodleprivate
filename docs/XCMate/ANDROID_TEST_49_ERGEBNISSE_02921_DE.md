# XCMate Android-Test 49 – Nutzerergebnisse (0.1.29.21)

**Datum:** 23.10.2026  
**Plattform:** Android-TV, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung (Projektgerät)  
**Basis:** XCMate `0.1.29.21` (PR #109 bereits gemergt).  
**Quelle:** Vom Nutzer übermittelte 15 Einzelbewertungen und Freitextbeobachtungen. Keine neu durch den Assistenten ausgeführten Gerätetests.

**Gesamtergebnis: 13 PASS / 1 FAIL / 1 NOT_TESTED.**

| Test | Status | Prüfpunkt | Issue(s) |
|---|---|---|---|
| A01 | PASS | Installation und Datenbestand | Update-Sicherheit |
| A02 | PASS | Live-TV, Overlays und Stop | #97, #17 |
| A03 | PASS | EPG → Jetzt Sender ansehen | #89 |
| A04 | PASS | Film-/Serien-Stop ohne Hintergrundton | #40, #79 |
| A05 | PASS | Eigene Playeroberfläche und Fernbedienung gemäß bestehender Checkliste | #79 |
| A06 | **FAIL** | EPG-Grundnavigation | #88, #92 |
| A07 | PASS | Artwork und lokaler Bildcache | #41, #90 (Teilprüfung) |
| B01 | PASS | Drei Folgen automatisch hintereinander | #85 |
| B02 | **NOT_TESTED** | Automatischer Staffelwechsel | #85 |
| B03 | PASS | Autoplay-Schalter Ein/Aus | #85, #79 |
| B04 | PASS | Manueller Stop und Zurück | #85, #40 |
| B05 | PASS | Stop während Episodenwechsel | #85 |
| B06 | PASS | Serienende und fehlende Folge | #85 |
| B07 | PASS | Resume, Gesehen und Favoriten | #85 |
| B08 | PASS | Keine unerwünschte Autoplay-Kette | #85, #97 |

## Zusätzliche direkte Nutzerbeobachtungen (über die PASS-Checkboxen hinaus)

### 1. Film-/Serienplayer – Bedienoberfläche noch unzureichend (#79)

Obwohl A05 die **bisher vorhandenen** Grundfunktionen als PASS bewertet, fordert der Nutzer eine **grundlegende Player-Überarbeitung**:

- Der laufende Fortschritts-/Zeitbalken muss ein **echtes fokussierbares Seek-Control** sein.
- D-Pad: Fokus auf Timeline bringen; **Links/Rechts** verschieben eine sichtbare vorläufige Positionsmarke rückwärts/vorwärts, **OK** bestätigt den Seek zur gewählten Zeit; Back darf die Vorschau verwerfen. Zeitposition/Vorschau klar anzeigen.
- Eindeutige, übliche Player-Symbole statt rein textlastiger bzw. unverständlicher Darstellung: Play (Dreieck), Pause (Doppelbalken), Stop (Quadrat), Rück-/Vorspulen, Anfang/Ende-Sprung sowie Next, sofern tatsächlich verfügbar.
- Nur seekbare Streams bedienen. Audio-/Untertitel-/Bildoptionen und funktionierendes Autoplay schützen. Kein unerwünschtes Seek/Stop durch bloße Navigation, keine fremde Playback-Session beeinflussen.
- Die korrekte zeitbasierte Umsetzung, Positionserhalt/Resume und Android-IR-Fokus benötigen **neue Gerätetests**. A05 PASS darf **nicht** als Abnahme dieser neuen Funktionen ausgelegt werden.

### 2. Großes EPG – weiterhin FAILED UX (#88 / #92)

Nutzerbericht: EPG zeigt Sendergruppen und Sender weiterhin **ungeordnet/vermengt**, die Gruppen-Navigation ist nicht sinnvoll erreichbar; Kopfbuttons (beispielsweise **Jetzt** oder Navigation zu folgenden Sendungen) sind per IR nicht erreichbar. Der Nutzer kann nicht durch die Gruppen navigieren; Inhalte wirken quer durcheinander.

Erforderliche Folgearbeiten: Startsendergruppe direkt und **nur diese** im Guide anzeigen; ursprüngliche Gruppe-/Senderreihenfolge erhalten; Gruppenliste per Links-Grenze erreichbar machen; ausgewählte Gruppe filtern; zeitliche Programme innerhalb der Senderzeile korrekt sortieren; Kopfbuttons via Hoch-Routing fokussierbar und per OK auslösbar; lesbarer Fokus und gestufter Back-Pfad. Das gemeldete Ungeordnetsein beweist **noch keine** doppelten XMLTV-Rohdatensätze (#58), keine spekulative Fehlerursache behaupten.

**Nachtrag, aktueller GitHub-Stand:** PR #110 wurde während der Test-49-Auswertung tatsächlich kumulativ auf die .21-Basis portiert (Commit `13f1e27423b47fa3b0915cec7faa1869be0d27e0`). Der neue Draft meldet **785/785 Host- und CI-Tests PASS** und ein geprüftes Original-XCMate-Icon, das auf echte Android-Verifikation wartet. **Der veraltete, isolierte .22-Teststand bleibt ungültig** und darf nicht über .21 installiert werden. Der neue kumulative .22-Kandidat ist [in PR #110](https://github.com/artattakk-creator/kodi-noodleprivate/pull/110) dokumentiert, **auf ausdrückliche Nutzerfreigabe am 23.10.2026 in `main` gemergt und über das GS-Media-Repository veröffentlicht**. Android-Abnahme für .22 bleibt **NOT_TESTED**. Die Fehlerbeobachtung **A06 FAIL betrifft weiterhin die getestete .21**, nicht den noch ungetesteten neuen .22-Code; Startgruppen-/Header-/Focus-Abnahme in .22 steht offen.

### 3. Bekannter Artwork-Pause-Button

Fehlender Button bleibt aus Test 48 **BLOCKED_UI / NOT_TESTED**. Keine Daten löschen, Caches zurücksetzen oder Cover neu herunterladen.

## Issue-Triage nach Test 49

- **#97**: Historische Live-TV-Stop/Neustart-Regression. A02+B08 PASS in .21; zusätzliche ältere .17-Reproduktionsregressionen dokumentiert (Stop 4/4, anderer Sender/Back 1/1). **Gezielter Kernfehler auf realem Android wiederholt nicht reproduziert**. Kann als erledigt geschlossen werden; Hardware-Stopp-Taste ohne physische Taste NOT_TESTED und nicht künstlich verlangen.
- **#89**: A03 PASS, vorherige .17-Durchläufe 3/3 PASS; historischer Kodi-Crash auf geprüften Normalpfaden nicht mehr reproduziert. Für vollständige sehr breite DoD (Sonder-/Fehlerpfade, wiederholtes Back/OK, weitere Sender) **offen**, nicht einfach alles als getestet behaupten.
- **#40**: A04+B04 PASS; expliziter Film-/Serien-Stop funktioniert. Mehrfach-/Fremd-Ownership-/Back-Sonderwege bleiben zur vollständigen DoD offen.
- **#79**: Grund-OSD A05 PASS, aber neue seekbare D-Pad-Timeline/Transport-Icon-Anforderung fehlt; offen.
- **#85**: B01, B03–B08 PASS; B02 Staffelwechsel **NOT_TESTED / auf Nutzerwunsch aus der aktiven Teststrecke genommen**. Nutzer wird den Staffelwechsel bei Gelegenheit melden; nach ausdrücklich bestätigtem Erfolg Ergebnis mit Version/Datum dokumentieren und #85 ohne neue Rückfrage schließen.
- **#88/#92**: A06 FAIL. EPG-Reihenfolge, Gruppenrouting, Headerfokus weiterhin offen.
- **#41/#90**: A07 PASS für Artwork/Bestand, jedoch nicht alle Speicher-/Fehlerfälle oder Button-UI abgenommen; offen.
- **#37**: Original-Icon nicht Bestandteil der getesteten .21; im mittlerweile in `main` gemergten .22 laut Binär-/CI-Prüfung integriert. Sichtprüfung auf Android weiterhin offen.

**Historische Abgrenzung:** Test 49 ist ausschließlich ein realer Gerätetest von .21, keine vorgezogene .22-Abnahme. Inzwischen erfolgten mit ausdrücklicher Nutzerfreigabe Merge und Repository-Veröffentlichung von .22 über PR #110. Die Android-Tests für .22 sind weiterhin offen; die gemeldeten .21-EPG-Fehler A06 dürfen nicht als bereits in .22 repariert oder noch vorhanden behauptet werden.
