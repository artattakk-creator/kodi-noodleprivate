# XCMate 0.1.29.31 – reale Android-Abnahme / Nutzerergebnisse vom 24.10.2026

**Status:** Auf dem Android-TV vom Nutzer geprüft. **9 PASS / 8 FAIL / 3 NOT_TESTED**, insgesamt 20 einzeln bewertete Prüfschritte.  
**Gerät / Kontext:** Android TV, Kodi 21.2, Rockchip RK3528 ARM32, Titan BINGIE MOD, IR-Fernbedienung (Projektgerät).  
**Build:** `plugin.video.xtreammate`, **0.1.29.31**, kumulativer [Merge-PR #154](https://github.com/artattakk-creator/kodi-noodleprivate/pull/154); auf `main` gemergt.  
**Soll-/Prüfliste:** [ANDROID_ABNAHME_02931_DE.md](ANDROID_ABNAHME_02931_DE.md). Diese Soll-Liste bleibt unverändert; die Zeilen **V0/S1–S5/Z2-USB/Z2-SMB/D3-…** waren eine in der interaktiven Abnahme angelegte Aufgliederung.  
**Beweismittel:** direkte Nutzer-Rückmeldung per Chat und Test-Checkboxen; keine technischen Rohlogs, Screenshots, Portal-URLs oder Zugriffsdaten übermittelt. Aussagen über Ursachen und nicht beobachtete Einzelschritte nicht als bewiesen markieren.

## 1. Einzelergebnisse – unverändert nach Nutzerangaben

| Gruppe | Test | Rückmeldung | Ergebnis |
| --- | --- | --- | --- |
| Installation | **V0** – Version .31 installiert | Anzeige 0.1.29.31 bestätigt | **PASS** |
| Smoke | **S1** – XCMate-Hauptseite | Nutzbar | **PASS** |
| Smoke | **S2** – Filmdetails | Nutzbar | **PASS** |
| Smoke | **S3** – Seriendetails | Nutzbar | **PASS** |
| Smoke | **S4** – Live-TV Start/Stop | Nutzbar | **PASS** |
| Smoke | **S5** – EPG und Bestandsdaten | Nutzbar | **PASS** |
| Suche | **Q1** – echte Jetzt-Sendung suchen, Suchansicht bleibt | Fehlnavigation/leere Ansicht | **FAIL** |
| Suche | **Q2** – vollständige Trefferliste, bewusst auswählen | Ergebnisanzeige erst nach dem Verlassen; nicht normal nutzbar | **FAIL** |
| Suche | **Q3** – fehlende Treffer/zweite Suche/Back/Fokus | Such-/Zurück-Navigation fehlerhaft | **FAIL** |
| Ziel | **Z1** – Ordnerauswahl | Interner Speicher/USB/SMB laut Nutzer-PASS auswählbar | **PASS** |
| Ziel | **Z2-USB** – kleine echte Zielprobe | USB-Zieltest vom Nutzer als bestanden markiert | **PASS** |
| Ziel | **Z2-SMB** – kleine echte Zielprobe | SMB-Zieltest vom Nutzer als bestanden markiert | **PASS** |
| Download | **D1** – Default-Deny/Prüfdialog | Kein Testnachweis | **NOT_TESTED** |
| Download | **D2** – bewusstes Prüfen/Freigeben CDN | Kein Testnachweis | **NOT_TESTED** |
| Download | **D3-FU** – ganzer Film USB | Keine vollständige bestandene Datei | **FAIL** |
| Download | **D3-EU** – ganze Folge USB | Kein Testnachweis | **NOT_TESTED** |
| Download | **D3-FS** – ganzer Film SMB | Keine vollständige bestandene Datei | **FAIL** |
| Download | **D3-ES** – ganze Folge SMB | Keine vollständige bestandene Datei | **FAIL** |
| Download | **D4** – Pause/Resume/Cancel/Neustart | Vom Nutzer als FAIL gemeldet; exakter Teilschritt/Ursache nicht spezifiziert | **FAIL** |
| Download | **D5** – CDN-Freigabe widerrufen | Vom Nutzer als FAIL gemeldet; trotz D1/D2 NOT_TESTED keine isolierte Schlussfolgerung über Grant-Mechanismus | **FAIL** |

**Summen:** 9 PASS, 8 FAIL, 3 NOT_TESTED = **20**. Keine BLOCKED-Rückmeldung. S1–S5 und V0 sind **nicht** unabhängig erneut labortechnisch überprüfte Einzelschritte, sondern nutzerbestätigte Geräteprüfungen.

## 2. Wörtlicher Kern des Nutzerberichts zur Suche (gekürzt, ohne private Daten)

- Suche **aus dem EPG nach einer Sendung**: statt der gewünschten Suchtreffer öffnet sich eine **leere schwarze Kodi-artige Verzeichnisansicht** mit drei dunklen Punkten und einem roten Balken. Kein normal bedienbares Ergebnis.
- Suche **nach einem Sender**: XCMate-Startseite erscheint **ohne App-Icon und Hintergrundgrafik**; offenbar falscher Ansichts-/Fokuswechsel.
- **Erst beim Herausgehen** erscheinen plötzlich Suchtreffer: **„Live TV 11 Treffer, Filme 0 Treffer, Serien 0 Treffer“**. Der Nutzer kann die Ergebnisse nicht regulär auswählen, sondern nur wieder herausgehen.
- Q1/Q2/Q3 deshalb **FAIL**. Die 11 nachträglich sichtbaren Treffer **beweisen keinen ordnungsgemäßen Sendungstitel-Match** und sind kein EPG-Suche-PASS. „0 Filme / 0 Serien“ ist lediglich die sichtbare Zählung, kein eigenständiger Nachweis einer Film-/Seriensuchstörung.

### Technische Einordnung / Codex-Folgeauftrag zu #140

**Beobachtung:** Aus dem Nutzerablauf folgt, dass der Fehler **nicht allein** mit „es wurden niemals Suchergebnisse berechnet“ beschrieben werden kann. Die Anzeige scheint nach einem fehlerhaften Window-/Landing-Handoff zeitversetzt aufzutauchen. **Mögliche** Kandidaten (nicht belegt): Fensterbesitz/Navigation-Stack, native `Container.Update`-/Directory-Abfolge, Fensterinitialisierung/Re-Init, Fokusübergabe, Ergebnis-Commit/Render-Reihenfolge und Back/OnClick-Race. Anhand der aktuellen Log-/Focus-Lifecycle-Events die Reihenfolge ermitteln; nicht blind die Suchindizierung neu aufbauen.

**Reproduktion:** Zwei isolierte Pfade mit IR aufnehmen, ohne private Titel/Adressen in GitHub zu kopieren: (A) aus großem EPG konkret jetzt laufende Sendung suchen; (B) Sendername suchen. Für beide Screens/Events `SEARCH_INPUT_ACCEPTED` → Ergebnis-Erstellung → Search-Window-Open/Focus → versuchte Rücknavigation → späterer Trefferstatus erfassen. Nach erfolgreichem Fix muss die Suche **direkt nach Eingabe in der aktiven Suchansicht** verbleiben, bei fertigem Scan Treffer **ohne Back/Exit** zeigen, erlauben zwischen ihnen zu navigieren und nur den bewusst ausgewählten Sender zu starten; 0-Treffer-/Back-Fälle ebenso.

**Keine Runtime-Änderung an PR #154 oder vorzeitige Erfolgsmeldung** durch diese Dokumentation. Neues zielgerichtetes Draft-PR nach Freigabe, Quell-/Regressionstests und echter Android-Geräteabnahme. Schutz: Film/Serie, Startgruppe, Original-Icon, EPG-Source-Mappings, Autoplay, unerwünschte Kodi-OSD-Fokus-/Player-Wechsel.

## 3. Status der Fach-Issues nach Vergleich mit ihrem vollständigen Scope

| Issue | Gesicherter Teilfortschritt / Mangel | Schlussfolgerung |
| --- | --- | --- |
| [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140) – EPG-Jetzt-Suche | Q1–Q3 FAIL; Ergebnisse teilweise erst **beim Verlassen** sichtbar, zwei falsche Landing-Ansichten | **OPEN / Android FAIL**; im neuen UI-/EPG-Roadmap-Zyklus vorrangig beheben |
| [#135](https://github.com/artattakk-creator/kodi-noodleprivate/issues/135) – sichere Download-Redirects | D1/D2 NOT_TESTED, D3-FU/-FS/-ES FAIL; ohne Fehlercode keine sichere Zuordnung der Ursache zu Redirect oder Speicher | **OPEN / E2E nicht bestanden**, neue Download-Reparaturen gemäß Roadmap nachrangig |
| [#136](https://github.com/artattakk-creator/kodi-noodleprivate/issues/136) – USB/SMB-Speicherziel | Z1, Z2-USB, Z2-SMB PASS; aber tatsächliche vollständige VOD-Transfers/Zielpublikation D3-FU/-FS/-ES FAIL | **OPEN / TEILFORTSCHRITT**, Zielprobe ist kein Film-/Folgen-Download-PASS |
| [#63](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63) – vollständiger Film-/Episodendownload | D3-FU/-FS/-ES FAIL, D3-EU NOT_TESTED, D4 FAIL; keine vollständige Offline-Datei erfolgreich bestätigt | **OPEN / Android E2E FAIL**, erst in letzter Roadmap-Phase weiterführen |
| [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143) – Master | Regression des Suchfensters trotz .31-Host-CI und 3 echte Speicherziel-PASS | **OPEN**; Fortschritt hier erfassen, nicht als Beta-Abnahme werten |

Der separate Live-Aufnahmerecorder [#126](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126) ist **nicht Teil dieser Testabnahme**. Kein Schluss auf dessen Lösung möglich.

## 4. Verbindliche Planentscheidung nach dem .31-Zyklus

1. **Jetzt Priorität #140:** Live-/EPG-Suche zeigt Ergebnisse auf derselben XCMate-Suchoberfläche; kein leerer Kodi-Ordner, keine Startseite ohne Assets, keine nur nach Back erscheinenden Treffer. Fokus-/Owner-/Lifecycle-Lösung gezielt nachweisen.
2. Danach die übrigen bereits priorisierten EPG-, Cover-/TMDb-, Info-/Player-OSD-, Icon-Rail-, Medienbrowser-/Wizard-Arbeiten aus #143.
3. **Download/USB-/SMB-Medienpublikation und TV-Aufnahme gemäß Nutzerentscheidung zuletzt.** Die drei erfolgreich bestätigten Speicherauswahl- und Kurz-Zieltests bleiben erhalten und müssen nicht erneut ohne Anlass durchlaufen werden. Download-Fehler trotzdem unverändert transparent als FAIL dokumentieren.
4. **Keine voreilige Issue-Schließung.** Historische `0.1.29.30`-Abnahme [ANDROID_ABNAHME_02930_20261024_NUTZERERGEBNISSE_DE.md](ANDROID_ABNAHME_02930_20261024_NUTZERERGEBNISSE_DE.md): **12 PASS / 15 FAIL / 1 BLOCKED / 1 NOT_TESTED**, bleibt **unverändert**. Bereits bestandene MEM1 vier Stunden/MEM2 Neustart nicht pauschal neu fordern.

**Privacy:** Diese Datei enthält bewusst weder Portal-/Provider-/SMB-URLs, Tokens, Passwörter, Sender- oder Medientitel noch Kodi-Rohlogs.
