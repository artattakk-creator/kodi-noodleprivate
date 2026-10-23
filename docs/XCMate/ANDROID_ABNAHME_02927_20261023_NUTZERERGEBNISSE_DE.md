# XCMate 0.1.29.27 – Reale Android-Abnahme vom 23.10.2026

**Gerät:** Android TV, Kodi 21.2 Omega, Titan BINGIE MOD (bestehende RK3528/ARM32-Testumgebung). **Installation:** 0.1.29.27 A+B+C aus gemergtem PR #130. Dieser Bericht basiert auf der **ausdrücklichen, vollständig ausgefüllten Nutzer-Rückmeldung**, nicht auf CI.

## Originalergebnis unverändert
**13 PASS / 15 FAIL / 0 NOT_TESTED** aus 28 Prüfpunkten (46,4 % PASS). Keine nachträgliche Umklassifizierung der Nutzer-FAILs; bei blockierten Folgeprüfungen zusätzliche fachliche Anmerkung statt Überschreiben.

| ID | Getestete Funktion | Vom Nutzer gewähltes Ergebnis |
|---|---|---|
| A01 | Globale Suche nach „Upload“ | **PASS** |
| A02 | TV-Sender aus Suchtreffern starten | **PASS** |
| A03 | Nach laufender Sendung suchen | **PASS** |
| A04 | Doppel-OK und erneuter Start | **PASS** |
| A05 | Fernbedienung nach Suchstart | **PASS** |
| A06 | Player- und Sitzungswechsel | **PASS** |
| A07 | Großes EPG unverändert | **PASS** |
| A08 | Filme, Serien und Autoplay unverändert | **PASS** |
| B01 | Aufnahmeordner auswählen | **PASS** |
| B02 | Nicht unterstütztes Speicherziel erkennen | **PASS** |
| B03 | Sofortaufnahme läuft wirklich | **FAIL** |
| B04 | Aufnahme manuell stoppen | **FAIL** |
| B05 | Aufnahme wiedergeben | **FAIL** |
| B06 | Offline und nach Kodi-Neustart | **FAIL** |
| B07 | Aufnahmeunterbrechung sicher behandeln | **FAIL** |
| B08 | Bestehende Funktionen erhalten | **PASS** |
| C01 | Linkes Seitenmenü öffnen | **FAIL** |
| C02 | Menü schließen und Fokus erhalten | **FAIL** |
| C03 | Poster gezielt erneut herunterladen | **FAIL** |
| C04 | Film-Download ablehnen | **FAIL** |
| C05 | Film herunterladen | **FAIL** |
| C06 | Einzelne Serienfolge herunterladen | **FAIL** |
| C07 | Download pausieren oder abbrechen | **FAIL** |
| C08 | Download fortsetzen oder wiederholen | **FAIL** |
| C09 | Heruntergeladenen Film und Folge abspielen | **FAIL** |
| C10 | Downloads offline wiedergeben | **FAIL** |
| C11 | Speicher-/Verbindungsfehler erkennen | **PASS** |
| C12 | Gesamter Regressionstest | **PASS** |

**Originalbeobachtung des Nutzers (wortgetreu):**
> es kommt die fehlermeldung das aufnahme nicht unterstützt wird. das linke menu in details wird nicht angezeigt - dadurch konnte ich die kompletten download aktivitäten nicht überprüfen. poster failback und erneuter download funzt nicht

## A – Suchreparatur: 8/8 PASS → #125 positiver Geräte-Nachtest
- A01 Suche `Upload` mehrfach funktioniert; A02 **Live-TV-Treffer starten funktioniert jetzt**; A03 Start auch über EPG-Jetzt-Suchtreffer; A04 schnell doppelt OK und erneuter Start; A05 XCMate-Fernbedienung und Overlay; A06 Player-/Session-Schutz; A07 großer EPG samt Senderstart; A08 Film-/Serienabläufe und **staffelübergreifendes Autoplay**.
- **Änderung zu .26:** S06 war **FAIL** mit fatalem Kodi-`two concurrent busydialogs`-Log. Das neue A02–A06-Android-Ergebnis ist **PASS** für den getesteten Search→Live-Handoff nach der .27-Reparatur. Kein erneuter Crash vom Nutzer gemeldet. Das ist ein realer positiver Nachtest für **Issue #125**, nicht nur CI-/Mock-Evidenz. Kein Crashursachen-Beweis über alle theoretischen Edge Cases.
- Die ältere .25-`Upload`-Regression **#118** ist im konkret getesteten Ablauf sowohl in .26 als auch .27 nicht wieder aufgetreten. Diese ältere Issue enthält weitergehende Edge-/Fallback-Anforderungen (leere Query/ohne EPG etc.), die das übermittelte Formular nicht alle gesondert bestätigt.
- EPG-Guide #121 nun erneut PASS im getesteten Standardablauf; sein umfassender technischer Edge-Gate ist noch nicht komplett separat dokumentiert, daher Status nicht automatisch als insgesamt abgeschlossen ändern.
- #127 **aufgewertete Suchzeilen mit Logos/Covern/Metadaten** sind noch **nicht** Teil von .27 und wurden nicht getestet; bleiben offen.

## B – Sofortaufnahme: 3 PASS / 5 FAIL → #126 weiterhin BLOCKER
- **B01 PASS**: Speicherordner auswählen.
- **B02 PASS**: inkompatibles Ziel wird erkannt / entsprechende Fehlermeldung und Fallback-Auswahl im Umfang des Formularfeldes positiv bewertet. Das bedeutet **nicht**, dass ein tatsächlich geeigneter Speicherpfad erfolgreich gefunden oder verwendet wurde.
- **B03 FAIL**: keine lauffähige Aufnahme; Nutzer erhält sinngemäß **„Aufnahme wird nicht unterstützt“**. Es ist **nicht** ausdrücklich derselbe technische Detailcode wie `UNSUPPORTED_TARGET` der .26-Abnahme; ohne aktuellen Screenshot/Log diesen Fehlercode für .27 **nicht behaupten**.
- **B04–B07 alle explizit vom Nutzer als FAIL markiert**, aber ohne erfolgreich startende Aufnahme sind Stop, fertige Datei, Offline-Abspielung und echte Unterbrechung **nicht unabhängig end-to-end validierbar**. Im Gerätebericht weiter FAIL; als **durch B03 blockierte Folgeprüfungen** für Codex interpretieren. Weder vier unabhängige Root Causes noch successful End-to-End als bewiesen behaupten.
- **B08 PASS**: Bestandsfunktionen bleiben erhalten.
- **Teilfortschritt .26→.27:** Früher erst später `FAILED / 0 MB / UNSUPPORTED_TARGET`; jetzt meldet UI früh, dass Aufnehmen nicht unterstützt wird, wobei kein kompatibles Ziel bzw. keine funktionierende Aufnahme nachgewiesen ist. Offen: Pfad, Syscall-Kategorie/errno, ob compatible_default angeboten wurde, Providerfähigkeit, Aufnahmeformat. `capture_target.py::probe()/probe_fd()/compatible_default()`, `capture_ui._start()`, `capture_service` datensparsam instrumentieren; kein Umbiegen auf unsichere Android-/USB-/VFS-Pfade.

## C – Detailmenü/Downloads: 2 PASS / 10 FAIL → neues P0 #131
- **C01 FAIL**: Links in Film-/Seriendetails öffnet **kein** sichtbares Seitenmenü.
- **C02–C10 nutzerseitig FAIL**, jedoch ausdrücklich „dadurch konnte ich die kompletten download aktivitäten nicht überprüfen“. **Bewertung:** direktes UI-Entry-Problem für C01 nachgewiesen; C02–C10 sind **blockiert (nicht unabhängig getestet)**. **Originalmarkierungen bleiben FAIL**, aber weder der HTTP-Downloadworker noch Range/Resume/Pause/Offline-Decoder gelten dadurch als separat defekt oder bestanden.
- **C03 zusätzliche explizite Beobachtung:** „poster failback und erneuter download funzt nicht“; zeigt fehlenden funktionsfähigen Nutzerweg/Artwork-Retry, weil Menü nicht erreichbar; auch **#111** separat offen. Falls der Nutzer das Poster aus anderem UI probierte, hier nicht annehmen – kein genauer Trace.
- **C11 PASS** und **C12 PASS** als Nutzerangaben übernommen: Fehlererkennung und untersuchte Bestandsregressionen bestanden. Dies validiert **nicht** C04–C10.
- Gemeinsamer Codepfad: `detail_menu.py::DetailMenuMixin._detail_menu_action` erfordert `key==1`, `mode=='detail'`, `self.actions` und `not self._playback_waiting`; `media_window.py::_handle_action` ruft sie zuerst. XML Gruppe **800** / Sichtbarkeitsproperty `XCMate.DetailMenu`, Liste **810**, Fokus via `_valid_focus`. Native Kodi-IR-Event, Eligibility, Window.Property und Sichtbarkeit müssen auf Gerät validiert werden. **Kein Root Cause ohne neues Kodi-Log behaupten**.
- Kein fertiger Download-Nachweis auf Android; nur der frühere Host-Test aus PR #130 ist ein unabhängiger Host-Nachweis. **PR-Merge ≠ Android-PASS.**

## Arbeits-/Issue-Entscheidungen
- **#125**: durch A01–A08 **positiv vollständig nachgetesteter Kern-Fix** – diese konkrete Search→Live-Regressionsreparatur darf als **Android PASS** dokumentiert werden; Issue abschließen, sofern nicht vorher neue Edge-Fails belegt werden. #127 als separate visuelle Weiterentwicklung.
- **#126**: **OPEN / P0**, echte Aufnahme B03–B07 bleibt unerfüllt.
- **#131**: **NEU / OPEN / P0**, linkes Detailmenü erscheint nicht; C02–C10 blockiert. Erst C01 auf realem Gerät beheben, danach alle abhängigen Tests.
- **#111**: **OPEN**, selektiver Poster-Retry/Fallback weiterhin nicht funktionstüchtig nach Nutzerbeobachtung.
- **#118/#121**: alter Fehler im üblichen Ablauf positiv nachgetestet, aber weitergehende spezifizierte Randbedingungen bisher nicht komplett separat abgenommen; **vorerst OPEN**.
- **#120**: Skin-Live-TV-Shortcut seit .26 FAIL, **in diesem .27-Test nicht ausdrücklich geprüft**; Status unverändert OPEN, kein erfundener .27-PASS.
- **#43/#127/#122/#123/#98** weiterhin offene / noch nicht als integriert bestätigte Anforderungen. Insbesondere vollständiger Plug-and-Play-Erststart #43 und schöne Suche #127 sind Gates des nächsten vollständigen Releases.
- **B08/C12/A07/A08** belegen den Bestandsschutz im getesteten Umfang: EPG, Original-Icon, Live-TV-Fernbedienung, Daten und Autoplay nicht regressieren.

## Reparatur-/Nachtestempfehlung
1. **P0 #131** Sichtbarkeit und Remote-Ereignisse des Detailmenüs auf der Android-Box prüfen; nach reproduzierbarem C01-PASS C02–C10 und gezielten Poster-Retry wieder testen.
2. **P0 #126** eine sichere, **wirklich verwendbare** native Android-Aufnahmezieldiagnose / kompatibles persistentes Ziel und klaren Error Reason schaffen; B03 echte Bytezunahme → B04 beenden → B05/B06 abspielen → B07 Unterbrechung.
3. 0.1.29.27 ist **nicht** vollständig abgenommen. Nächster Hotfix als Draft-PR, Test-ZIP/SHA256, gezielte Android-Nachtests, kein ungefragter Merge oder unbestätigter PASS.
4. Keine rohen Kodi-Logs, Xtream-/Provider-URLs, Nutzernamen oder Kennwörter nach GitHub schreiben.

## Quellen / Verweise
- Vorversion `docs/XCMate/ANDROID_ABNAHME_02926_20261023_NUTZERERGEBNISSE_DE.md` – 15 PASS / 6 FAIL / 0 NOT_TESTED aus 21 Tests.
- Android-Anleitungen `docs/XCMate/ANDROID_TEST_02927_A_DE.md`, `ANDROID_TEST_02927_B_DE.md`, `ANDROID_TEST_02927_C_DE.md`.
- PR [#130](https://github.com/artattakk-creator/kodi-noodleprivate/pull/130) – .27 A+B+C integriert; 942 CI PASS vor der Android-Abnahme.
- Issues: [#125](https://github.com/artattakk-creator/kodi-noodleprivate/issues/125), [#126](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126), [#131](https://github.com/artattakk-creator/kodi-noodleprivate/issues/131), [#111](https://github.com/artattakk-creator/kodi-noodleprivate/issues/111).
