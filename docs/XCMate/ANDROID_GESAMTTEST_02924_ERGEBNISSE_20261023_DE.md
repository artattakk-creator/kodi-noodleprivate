# XCMate 0.1.29.24 – Android-Gesamttest: Ergebnisse

> **KRITISCHER NACHTEST vom 23.10.2026 (spätere Nutzerbeobachtung):** Das zuvor als PASS gemeldete Space Premium zeigt **P0-Fehler** beim Rückwechsel zu Lightweight, unsichtbaren Fokus in Filmen/Serien und Dateifenstern sowie OK→Suche statt fokussierter Detailaktion. Die früheren Sammel-PASS D/F gelten **nicht als Abnahme** dieser konkreten Funktionen. Artwork C bleibt FAIL. **[Nachtest / P0-Bericht](ANDROID_NACHTEST_02924_PREMIUM_P0_20261023_DE.md)** · [GitHub-Issue #115](https://github.com/artattakk-creator/kodi-noodleprivate/issues/115). Original-Icon und großes EPG wurden durch die neuen Angaben nicht widerrufen.

**Datum der Nutzer-Rückmeldung:** 23.10.2026  
**Produktive Version:** `0.1.29.24`, GS Media Kodi Repository, `plugin.video.xtreammate`  
**Gerät/Zielumgebung:** Android TV 13, RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung (bestehende Testumgebung).  
**Belegart:** vom Nutzer explizit übermittelte **sechs Sammelprüfbereiche A–F**; keine durch ChatGPT selbst durchgeführten Gerätetests.  
**Vorgängerbefund:** [Android-Test 50 / .22](ANDROID_TEST_50_ERGEBNISSE_02922_DE.md) (16 PASS, 3 FAIL).  
**Version .24:** [PR #114](https://github.com/artattakk-creator/kodi-noodleprivate/pull/114), gemergt, [Publikations-CI erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39944946987), `addons.xml` führt .24.  
**Einzeltest-Plan:** [ANDROID_TEST_02924_DE.md](ANDROID_TEST_02924_DE.md).

## Originale Android-Ergebnismeldung (inhaltlich unverändert)

| ID | Vom Nutzer bestätigter Bereich | Android-Ergebnis |
|---|---|---|
| A | Update und Datenbestand | **PASS** |
| B | Original-XCMate-Icon | **PASS** |
| C | Poster und Artwork | **FAIL** |
| D | Space Premium | **PASS** |
| E | Großes EPG | **PASS** |
| F | Wiedergabe und Fernbedienung | **PASS** |

**Gesamt:** **5 PASS / 1 FAIL (sechs Prüffelder)**; damit kein globales 100%-PASS, sondern **Android-Teilabnahme mit bekanntem Artwork-Fehler**.

### Interpretation – bewusst begrenzt auf Nutzerangaben

- **A PASS:** Normales Update und Bestand wurden vom Nutzer als erfolgreich bewertet. Keine Behauptung, jedes einzelne Konto/Favorit/Resume-Feld sei isoliert gemessen worden.
- **B PASS:** Original-XCMate-Icon ist erstmals nach .22 (dort I02/I03 FAIL) **im gruppierten Android-Gesamttest** als PASS bestätigt. Exakte Anzeigeorte, App-Neustart-Szenario, `branding.inspect`-Codes und Einzeltest T02/T06 wurden in dieser neuen Meldung **nicht getrennt genannt**. Branding in künftigen Releases weiter als Regression prüfen.
- **C FAIL:** **Poster/Artwork weiterhin fehlerhaft**. Vorbekannter reproduzierbarer Fall .22: **Disney-Filme → Aladdin (1992): „Poster Netzwerkfehler“**. **Nicht behaupten**, dass gerade dieses konkrete Bild/der gleiche Fehlercode für .24 erneut gemessen wurde: keine aktuelle Einzelbild-Diagnose, HTTP-Status, Foto/Log, Retry-Ergebnis, Anzahl betroffener Poster oder Verlust vormals funktionierender Cover übermittelt. P1 #111/#41/#90 und ggf. #69 **offen**.
- **D PASS:** Space-Premium-Integration/Designbereich laut Nutzer erfolgreich. Kein Beleg, dass alle 98 Assets einzeln betrachtet wurden oder T03–T11 inklusive Abbruch, Paketentfernung, Offline-Wechsel, Speichergrenze und Neustart-Teilschritte getrennt PASS sind.
- **E PASS:** Großes EPG im .24-Sammeltest als PASS bestätigt; bereits Test 50 (.22) hatte **E01–E10 sämtlich PASS**. Sammel-PASS beweist **nicht** automatisch manuelle EPG-Zuweisung mit Live-Vorschau #98, Quelle-Fallbacks/Rich-Details oder seltene DST-Grenzfälle.
- **F PASS:** Wiedergabe und Fernbedienung laut Nutzer weiterhin funktionsfähig. **Nicht** als Fertigstellung von Timeline/Scrubbing #79, EPG-Aufnahmen #62, Downloads #63 oder Staffelwechsel B02 aus #85 interpretieren.
- **Nicht einzeln berichtet**: alle detaillierten T01–T12 aus dem Entwickler-Android-Testplan; diese bleiben ohne gesonderte Nutzer-Rückmeldung **NOT_TESTED auf Einzeltest-Ebene**, auch wenn die zugehörige Sammelkategorie PASS ist.

## Zielgerichtete nächste Diagnose – Artwork C FAIL

1. **In .24 am Realgerät einen weiterhin fehlerhaften konkreten Titel** identifizieren. Vorbekanntes Beispiel: Disney → Aladdin (1992), ohne vorauszusetzen, dass es weiterhin exakt dieser ist.
2. Im Film-Detail vorhandene **Posterstatus-/Einzelretry-Funktion** aus .23/.24 abrufen. Privat sensible Daten nicht posten; protokollieren: Fehlerklasse, Feldtyp der Bildquelle, Kandidatenzahl, Versuchsanzahl, letzter Status/Retry/Cooldown, und ob tatsächliches Bild anschließend sichtbar ist. **Keine Provideradresse, Stream-URL, Token, Portal-Credentials oder Nutzerdaten in GitHub-Logs.**
3. Mechanismen unterscheiden: HTTP 403/404/429/5xx bzw. DNS/TLS/Timeout, nicht vorhandener Bildkandidat, falscher Metadatenbezug (Titel und Jahr), gesperrte Queue, Speicherbudget/SPACE_FULL, DB-BUSY, lokal vorhandene vs. fehlende Cachedatei.
4. Ein **einzelnes** betroffenen Poster sicher neu versuchen, cooldown-/retry-gedeckelt. Danach weitere betroffene Titel und vorhandene `READY`-Cover stichprobenweise überprüfen.
5. Kein globaler Retry für mehrere Tausend Jobs, keine Cache-Löschung, kein Kodi-Neuaufsetzen, keine stille Migration oder erzwungener Komplettscan.
6. Ziel eines nächsten separaten Fix-PR: reproduzierbare und datensparsame Diagnose, korrekter selektiver Fehlerpfad, tatsächlicher Android-**C PASS** oder klar klassifizierte externe Nichtverfügbarkeit. Hosttests/CI + deutsche Testanleitung erneut.

## GitHub-Entscheidungen

- **Bestätigte Fortschritte kommentieren** unter #37 (Original-Icon und Space Premium), #88/#92 (EPG-Regression), #79/#85 (Playbacksammel-PASS ohne offene Features zu schließen).
- **C FAIL protokollieren** unter #111, #41, #90. #69 nur bei realem DB-Indiz.
- **Issues nicht automatisch schließen**: #37 enthält weiteren Design-/Randfallumfang; #111/#41/#90 sind nicht repariert/abgenommen; #88/#92 haben offene erweiterte Randfälle; #85 Staffelübergang **B02 explizit vertagt**.
- **Keine Codeänderungen, keine neue Version, kein Merge/Release in diesem Dokumentationsschritt**.
