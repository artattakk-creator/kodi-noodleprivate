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

Der bisherige .22-Draft PR #110 stammt aus der alten .20-Basis und ist **kein gültiges kumulatives Update**. Erst nach Neubau auf .21 und Test von Autoplay+EPG in .22 bewerten. Original-XCMate-Icon aus PR #50 bleibt obligatorischer Bestandteil von .22 (Issue #37).

### 3. Bekannter Artwork-Pause-Button

Fehlender Button bleibt aus Test 48 **BLOCKED_UI / NOT_TESTED**. Keine Daten löschen, Caches zurücksetzen oder Cover neu herunterladen.

## Issue-Triage nach Test 49

- **#97**: Historische Live-TV-Stop/Neustart-Regression. A02+B08 PASS in .21; zusätzliche ältere .17-Reproduktionsregressionen dokumentiert (Stop 4/4, anderer Sender/Back 1/1). **Gezielter Kernfehler auf realem Android wiederholt nicht reproduziert**. Kann als erledigt geschlossen werden; Hardware-Stopp-Taste ohne physische Taste NOT_TESTED und nicht künstlich verlangen.
- **#89**: A03 PASS, vorherige .17-Durchläufe 3/3 PASS; historischer Kodi-Crash auf geprüften Normalpfaden nicht mehr reproduziert. Für vollständige sehr breite DoD (Sonder-/Fehlerpfade, wiederholtes Back/OK, weitere Sender) **offen**, nicht einfach alles als getestet behaupten.
- **#40**: A04+B04 PASS; expliziter Film-/Serien-Stop funktioniert. Mehrfach-/Fremd-Ownership-/Back-Sonderwege bleiben zur vollständigen DoD offen.
- **#79**: Grund-OSD A05 PASS, aber neue seekbare D-Pad-Timeline/Transport-Icon-Anforderung fehlt; offen.
- **#85**: B01, B03–B08 PASS; B02 Staffelwechsel **NOT_TESTED**. Offen bis echte Staffelgrenze.
- **#88/#92**: A06 FAIL. EPG-Reihenfolge, Gruppenrouting, Headerfokus weiterhin offen.
- **#41/#90**: A07 PASS für Artwork/Bestand, jedoch nicht alle Speicher-/Fehlerfälle oder Button-UI abgenommen; offen.
- **#37**: Original-Icon nicht Bestandteil der .21; für korrigierte .22 verpflichtend; offen.

**Freigaben:** Keine weitere Version, kein Merge, kein Release, kein produktiver OTA-Index-Eingriff. Nachweis umfasst den Nutzerbericht, keine Implementierung/Fix-Zusage.
