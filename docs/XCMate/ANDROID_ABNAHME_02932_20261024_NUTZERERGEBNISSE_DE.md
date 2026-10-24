# XCMate 0.1.29.32 – reale Android-Abnahme / Nutzerergebnisse vom 24.10.2026

**Status:** Version `0.1.29.32` auf Android-TV installiert und durch Nutzer getestet. **7 PASS / 10 FAIL / 0 NOT_TESTED**, insgesamt **17** separat markierte Punkte. **Android-Gesamtfreigabe: FAIL** (insbesondere Suchfunktion).  
**Umgebung:** Android TV 13, Rockchip RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung. Estuary wurde **nicht separat nachgewiesen**; Auflösung/Testzeitpunkt nicht angegeben.  
**Build/Integration:** `plugin.video.xtreammate` 0.1.29.32; [PR #155](https://github.com/artattakk-creator/kodi-noodleprivate/pull/155) ist gemergt.  
**Offizieller Soll-Testplan:** [ANDROID_ABNAHME_02932_DE.md](ANDROID_ABNAHME_02932_DE.md); seine ursprünglichen `NOT_TESTED`-Vorgaben sind die **Ausgangslage vor dem Nutzerlauf** und bleiben als Vorlage unverändert.  
**Evidenz:** Nutzerangaben aus dem ausgefüllten Chat-Testformular, **keine neuen Kodi-Rohlogs, Screenshots, Einzelzeitpunkte oder Stacktraces** im Rahmen dieser Abnahme. Keine Fehlerursache als technisch bestätigt ausgeben, die nicht aus Logs/Code/Tests belegt ist.

## 1. Alle 17 Nutzer-Testmarkierungen unverändert

| Bereich | ID | Test (entspricht interaktiver Abnahme) | Meldung |
| --- | --- | --- | --- |
| Installation | V0 | Version .32 installiert | **PASS** |
| Smoke | S1 | Hauptmenü und Fernbedienung | **PASS** |
| Smoke | S2 | Filmdetails | **PASS** |
| Smoke | S3 | Seriendetails | **PASS** |
| Smoke | S4 | Live-TV | **PASS** |
| Smoke | S5 | Großer EPG und Bestandsdaten | **PASS** |
| Suche | NAVSEARCH-01 | Jetzt-Sendung aus dem EPG suchen | **FAIL** |
| Suche | NAVSEARCH-02 | Sendername suchen | **FAIL** |
| Suche | NAVSEARCH-03 | Leere Suche und Back | **FAIL** |
| Suche | NAVSEARCH-04 | Globale Suche aus anderen Menüs | **FAIL** |
| Suche | NAVSEARCH-05 | 20 Fernbedienungszyklen | **FAIL** |
| Suche | NAVSEARCH-06 | Suche während laufender Ergebniszählung | **FAIL** |
| Suche | NAVSEARCH-07 | Unterschiedliche Sucheinstiege | **FAIL** |
| Suche | NAVSEARCH-08 | Manuelle EPG-Zuordnungen und Kurz-EPG | **FAIL** |
| Regression | REG-01 | Live-TV-Steuerung | **FAIL** |
| Regression | REG-02 | Medien, Autoplay und Originalgrafiken | **PASS** |
| Regression | REG-03 | EPG-Rückkehr und Benutzerdaten | **FAIL** |

**Summe:** 6 PASS aus Installation/Smoke, 1 PASS aus Regression = **7 PASS**. 8 FAIL aus allen NAVSEARCH-Prüfungen und 2 FAIL aus Regression = **10 FAIL**. **0 NOT_TESTED**, **0 BLOCKED** als tatsächliche Nutzer-Markierungen.

### Freitext des Nutzers

> suche funktioniert überhaupt nicht

Diese Aussage **ändert keine Einzelmarkierung**, beschreibt aber den übergreifenden Blocker. Für NAVSEARCH-03/05/06/07/08 wurden keine eigenständigen Einzelschritte oder isolierten Symptome berichtet: Die Tests sind **wie vom Nutzer markiert FAIL**, jedoch ist **nicht bewiesen**, dass alle jeweiligen Teilaktionen überhaupt separat ausführbar oder die zugrunde liegenden Funktionen unabhängig voneinander defekt waren. Insbesondere `NAVSEARCH-05 FAIL` ist **kein Beleg, dass sämtliche 20 Zyklen vollständig ausgeführt wurden**; `NAVSEARCH-07 FAIL` ist kein Beleg, dass auf dem Gerät tatsächlich ein Legacy-Sucheinstieg vorlag.

### Wichtige Scope-Abgrenzungen

- **S4 PASS** bedeutet, dass der kurze Live-TV-Grundtest nutzerseitig bestand. **REG-01 FAIL** bedeutet **nicht automatisch**, dass Start/Stop oder die gesamte Live-TV-Wiedergabe ausgefallen ist. Das REG-Gate verlangt außerdem OSD/Navigation/Suchtreffer-Playback; welcher Teil scheiterte, ist noch unbekannt und kann durch die nicht nutzbare Suche blockiert sein.
- **S5 PASS** zeigt, dass der große EPG und Bestandsdaten im Grundtest zugänglich waren. **REG-03 FAIL** kann bereits durch die Suche/Back-Rückkehr blockiert sein. **Kein Nachweis für den Verlust von Favoriten, Portalen oder EPG-Mappings.**
- **REG-02 PASS** und S2/S3 PASS belegen nutzerbestätigten Bestandsschutz für Medien-/Autoplay-/Originalgrafik-Prüfungen. Das ist **kein** gesamter regressionsfreier Release.
- `V0 PASS` bestätigt, dass die installierte Version tatsächlich `.32` anzeigte. Kein Downgrade-/Neuinstallationsauftrag.
- Downloads, Recorder, Speicherzieltransfers wurden in der `.32`-Abnahme **nicht erneut geprüft** und werden daraus **nicht** als PASS oder FAIL neu bewertet. Historische `.31`- und `.30`-Ergebnisse beibehalten.

## 2. Vergleich mit den offiziellen .32-Abnahme-Gates

Die offizielle [Android-Abnahme .32](ANDROID_ABNAHME_02932_DE.md) enthält **NAVSEARCH-01–08 und REG-01–03**. Alle elf wurden vom Nutzer bewertet: **10 FAIL, 1 PASS** (REG-02). Das ergänzende interaktive Formular enthält **V0/S1–S5**: **6 PASS**. Das Formular entspricht den Anforderungen aus der offiziellen Anleitung „Installation und Ablauf“.

Es wurde **kein** bestätigter Android-PASS für den Kernumfang von [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140) erreicht. Die im PR #155 dokumentierten **1.068 bestandenen Host-/CI-Tests** haben den realen Android-Fehler **nicht behoben oder nicht auf der Hardware nachweislich abgedeckt**. Das sind getrennte Testebenen, keine widersprüchlichen Zählungen.

## 3. Technische Konsequenz / Codex-Triage für die nächste Korrektur

**Priorität P0/P1 sofort: Suche aus dem großen EPG und globalen Menüs auf echtem Kodi 21.2/Android-BINGIE funktionsfähig machen.** Der im PR #155 gemergte Fix für native Fenster-/Owner-Übergabe ist **in der Android-Abnahme gescheitert**. Die exakte Ursache des jetzt auftretenden `.32`-Fehlers ist **aus diesem Testergebnis allein nicht bestimmbar**. Die frühere [.31-Logforensik](CODEX_UEBERGABE_LOGFORENSIK_SUCHFENSTER_20261024_DE.md) ist Ausgangshypothese, aber **nicht** als neue `.32`-Diagnose zu behaupten.

### Nächste Diagnose – klein, gezielt, vertraulich

1. **Zwei präzise Reproduktionsfälle** auf `.32`: (A) Suche nach einer laufenden Sendung aus großem EPG; (B) Suche nach eindeutigem Sendernamen aus der globalen XCMate-Suche. Jeweils Aufruf, Keyboard-Bestätigung, unmittelbar sichtbare GUI/Focus, Back-Verhalten und Ergebnisstatus unterscheiden. Nicht alle 17 Tests pauschal erneut verlangen.
2. **Wenn Logs verfügbar:** Nur die Zeitbereiche nach eindeutigem `.32`-Installationsnachweis und dem tatsächlichen Suchversuch auswerten. Anonyme `[XCMate][SEARCH_NAV]`, `[XCMate][SEARCH]`, `[XCMate][NAV]`, `[XCMate][WINDOW]`, `[XCMate][SEARCH_EPG]`, `DIRECTORY_DONE` und `script error/exception` nach Dispatch-/Session-ID korrelieren; tatsächliche native Fenster-ID, Ownership, handle=action/directory, `SEARCH_OPEN`/`GUI_READY`/`RESULT_READY`, Timeout und Back erfassen.
3. **Gezielt Codex-Änderungen aus PR #155 prüfen:** `src/plugin.video.xtreammate/resources/lib/search_navigation.py`, `guide_window.py`, `guide_grid_window.py`, `app_routes.py`, `window_navigation.py`, `media_search.py`, `media_window.py`. Insbesondere Guide-/Window-Owner-Lifecycle, Kodi-native Modal-Callback-Reihenfolge, positiver Directory-Handle, Suchfenster-Render-/Focus-Gültigkeit, ausbleibende Diagnosetraces, Race bei Return/Close/Result-Futures; zunächst reproduzieren, nicht denselben unbelegten Fix wiederholen.
4. **Hosttest-Lücke schließen:** Android-realistischer Test für echt sichtbaren Kodi-Container, Window-Freigabe, Skin-Fokus und native Callback-Latenz. Keine zweite, konkurrierende Suchoberfläche einführen. EPG-Titelmatching erst **nach** stabil sichtbarer und bedienbarer Suchoberfläche bewerten.
5. **REG-01/REG-03 gezielt auseinandernehmen:** Prüfen, ob sie an der nicht funktionsfähigen Suche scheitern, oder ob es eine separate echte Regression bei OSD/Live-Navigation beziehungsweise EPG-Back gibt. Keine Behauptung von Datenverlust.
6. **Versionierung:** Ein künftiger Kandidat baut strikt kumulativ auf aktuellem freigegebenem `main` (`.32`) auf. Kein Downgrade, kein Entfernen des Add-ons, kein Rücksetzen der Nutzerportale, kein selbständiger Merge/Release. Separater Draft-PR, Host-/Regressionstests, ZIP+SHA256, dann gezielter Android-Test.

## 4. GitHub-/Issue-Entscheidung

- **#140 OPEN / Android .32 FAIL**, da alle NAVSEARCH-01–08 FAIL. PR #155 ist **bereits gemergt**, aber die Implementierung ist **nicht** auf echter Android-Hardware abgenommen. Nicht schließen.
- **#143 OPEN** als Master; .32-Fortschritt und P1-Blocker protokollieren. UI-/EPG-Fehler vor anderen Projektthemen.
- **#63, #135, #136, #126, #62** und weitere Download-/Aufnahme-Issues bleiben für jetzt zurückgestellt. Keine erneute Reparatur/Wiederaufnahme ohne Auftrag.
- Die historische [.31-Nutzerabnahme](ANDROID_ABNAHME_02931_20261024_NUTZERERGEBNISSE_DE.md) bleibt **9 PASS / 8 FAIL / 3 NOT_TESTED** und wird nicht geändert; ältere `.30`-Testwerte und MEM1/MEM2 ebenfalls unverändert.
- **Keine privaten Kodi-Rohlogs** oder Portal-/Provider-/SMB-URLs veröffentlichen. Noch kein neuer Debug-Trace geliefert; auf GitHub nur das Nutzerergebnis und abstrahierte Diagnoseschritte festhalten.

**Fazit:** `0.1.29.32` ist installiert und die Kernfunktionen leben weiter, aber die Suchreparatur ist für die Android-Abnahme **FAIL**. Nur diese belegten Aussagen zählen; das technische Root-Cause bleibt bis zu einem gezielten .32-Diagnoseversuch offen.
