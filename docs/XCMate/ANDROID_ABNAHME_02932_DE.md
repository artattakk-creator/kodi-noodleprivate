# XCMate 0.1.29.32 – gezielte Android-Abnahme

Stand: 24.10.2026. **Testkandidat / kein Release. Alle folgenden neuen Tests NOT_TESTED.**
Basis: main `59085e94f78d0bc9d66e3f6561a6fecf100abdf5` (.31). Kodi 21.2 / Android TV 13 / RK3528 ARM32 / Titan BINGIE MOD 2.2.3 / IR. Hauptlauf in BINGIE; kurzer Such-/Back-/Fokussmoke zusätzlich in Estuary. Skin und Auflösung im Ergebnis angeben.

## Installation und Ablauf

1. ZIP und gleichnamige `.sha256` aus diesem Draft beziehen. Prüfsumme mit Testbericht vergleichen (Windows `Get-FileHash -Algorithm SHA256`, Linux `sha256sum`).
2. In Kodi „Aus ZIP-Datei installieren“, bestehendes Add-on auf **0.1.29.32** aktualisieren. Keine Deinstallation, kein Downgrade, kein Profilreset. Unter Add-on-Information Version prüfen.
3. Einmal 3–5 Minuten S1–S5-Smoke: Home; Film-/Seriendetails per IR; Live-TV Start/Stop; EPG öffnen/Sender starten; Favoriten, Bestandsdaten und Originalicon vorhanden. Überschneidende REG-Prüfungen gemeinsam abhaken.
4. NAVSEARCH-01–08 und REG-01–03 unten durchführen. **Kein erneuter vierstündiger Test**, keine Download-/Aufnahme-Abnahme in diesem Zyklus.
5. Pro ID **PASS / FAIL / NOT_TESTED** notieren. Wenn ein vorausgehender Fehler weitere Schritte verhindert: NOT_TESTED mit dem blockierenden Test benennen. Alte .31-Q1–Q3 bleiben historisch FAIL.

## Neue Gates

| ID | Ausführbarer Ablauf | PASS ausschließlich bei | Status |
| --- | --- | --- | --- |
| NAVSEARCH-01 | Im großen EPG eine aktuell laufende Sendung eines zugeordneten Senders ablesen. Über „Suche“ exakt diesen Sendungstitel eingeben. Scanabschluss abwarten; in Live TV mit Down zur Liste. | Native XCMate-Suche direkt sichtbar, kein schwarzer Kodi-Ordner/Home-Wechsel. Echter Programmtitel-Treffer beim passenden Sender **vor Back**, keine bloßen Sendernamens-Treffer als Beleg. Bei `+` noch nicht final zählen. | NOT_TESTED |
| NAVSEARCH-02 | Aus großem EPG nach eindeutigem Sendernamen suchen. Zwischen Tabs wechseln; Live-Tab bestätigen; Trefferliste mit IR betreten. Erst dann bewusst OK auf dem Sender. | Treffer direkt bedienbar, Teil-/Endzählung korrekt, kein automatischer Start nach Keyboard-OK. Ein bewusster Start, keine Doppeltstarts. | NOT_TESTED |
| NAVSEARCH-03 | Nicht vorhandenen Begriff suchen; erneut suchen; Keyboard leer bestätigen bzw. abbrechen. Back aus fertiger Suche. | Kein falsches Kodi-Verzeichnis/ungefragter Start. Bei EPG-Rückkehr vorherige Gruppe, Zeit, Senderzeile und Fokus erhalten; Abbrechen vor Suche bleibt im Guide. | NOT_TESTED |
| NAVSEARCH-04 | Globale Suche über bestehendes XCMate-Menü (Einstellungen → Gruppen oder Wartung) öffnen. Zusätzlich Film-/Seriendetail öffnen und dort den Suchbutton nutzen; zurück. | Gleiche native Suchoberfläche. Home mit Originalassets; Detail kehrt zum selben Medium und gültigen Fokus zurück. Film-/Serien-Tabs weiter nutzbar. | NOT_TESTED |
| NAVSEARCH-05 | 20 kurze IR-Sequenzen Suche → Tabs links/rechts → Down/Up → Back; einzelne schnelle doppelte OK/Back. | Eine Aktion pro Absicht, kein Ghost-Fokus, keine versteckte Landing-Aktion, kein versehentlicher Playerstart. | NOT_TESTED |
| NAVSEARCH-06 | Bei großem Katalog während laufender Teilzählung neu suchen, Tab wechseln, Suche verlassen und erneut öffnen. | Ältere Ergebnisse überschreiben keine neue Suchsession und öffnen kein geschlossenes Fenster. Gewählter Tab und Fokus bleiben stabil. | NOT_TESTED |
| NAVSEARCH-07 | Normalen EPG-Handoff, Menü-Aktion (negativer Handle) sowie einen vorhandenen alten global_search-Verzeichnis-/Favoriten-Einstieg (positiver Handle) prüfen, soweit vorhanden. Zusätzlich aus fremdem Kodi-Kontext öffnen. Falls kein alter Einstieg vorhanden, diesen Teil NOT_TESTED lassen. | Native Suchansicht in allen geprüften interaktiven Wegen. Anonyme SEARCH_NAV-Traces zeigen `source=grid/guide/media/route`, `handle=action/directory`, Session und geordnete Freigabe. Kein Container.Update zur Suchroute/keine rekursive Home-Kette. Positiver Einstieg endet einmal mit vollständigem Home-Unterbau. | NOT_TESTED |
| NAVSEARCH-08 | Einen Sender mit **bereits vorhandener** manueller EPG-Zuordnung und gültiger Jetzt-Sendung wie NAVSEARCH-01 suchen; außerdem bestehende Short-Now-/Mehrfachtreffer testen, soweit vorhanden. Keine Zuordnungen für den Test überschreiben. | Titel und Sender stimmen mit dem EPG überein; Name-/Programmstatus unterscheidbar. Fehlendes EPG wird nicht als Programmbeleg ausgegeben; Mappings bleiben erhalten. | NOT_TESTED |
| REG-01 | Live-TV: einmal OK/Down/Back, Sender-/Gruppenliste, Startsender; anschließend aus Suchtreffer bewusst starten/Stop. | Bewährte Navigation und Playerübergabe stabil, kein fremder Player gestoppt. | NOT_TESTED |
| REG-02 | Film-/Seriendetails, vorhandenes Resume, manuelles Next und natürliches Episodenende/Autoplay einmal prüfen; Originalicon/Hintergrund/Cover ansehen. | Frühere Funktionen und Bestandsanzeigen erhalten; kein Fokus auf unsichtbare Controls 120/312. | NOT_TESTED |
| REG-03 | Großen EPG öffnen, vor Suche Gruppe/Zeit/Zeile merken, suchen und Back. Gespeicherte Profile/Favoriten und EPG-Zuordnungen vergleichen. | Keine zusätzlichen Navigationsschichten, Datenverluste oder geänderten Mappings. EPG-Lücken/Quellfallback weiterhin plausibel. | NOT_TESTED |

## Datensparsame Diagnose bei FAIL

Zeitpunkt, Test-ID, Skin, letzter sichtbarer Bildschirm und ob Fokus bedienbar war notieren. Für die Suche nur passende `[XCMate][SEARCH_NAV]`, `[XCMate][SEARCH]`, `[XCMate][SEARCH_EPG]`, `[XCMate][NAV]` und feste `[XCMate][WINDOW]`-Phasencodes verwenden. Die neuen Traces enthalten **keine** Suchphrase, Sender-/Portal-ID, URL, Token oder SMB-Daten. Zufällige Sessionkennungen verbinden INTENT/SEARCH_OPEN/SEARCH_GUI_READY/SEARCH_RESULT_READY. QUERY-Trefferzahlen erst nach Finalstatus auswerten.

**Keine privaten vollständigen Kodi-Rohlogs auf GitHub hochladen.** Der alte 11er-Name-Hit aus vor-.31 ist kein Beleg für erfolgreiche Programmsuche. Issue #140 bleibt bis zur tatsächlichen Nutzerabnahme offen; Merge/Release nur nach ausdrücklicher Freigabe.
