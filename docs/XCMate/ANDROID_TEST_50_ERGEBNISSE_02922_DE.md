# XCMate Android-Test 50 – Ergebnisse 0.1.29.22 (23.10.2026)

**Realer Nutzerbericht vom Android-TV:** XCMate 0.1.29.22, Kodi 21.2 Omega, Android 13 RK3528 ARM32, Titan BINGIE MOD, IR-Fernbedienung. Direkte Aktualisierung von 0.1.29.21 über das GS-Media-Repository ist bestätigt.

**Gesamt: 16 PASS / 3 FAIL / 0 NOT_TESTED.** Der automatische Staffelwechsel B02 ist **auf Nutzerwunsch außerhalb dieser Teststrecke vertagt**, nicht als PASS oder FAIL zu zählen. Der separate, noch nicht implementierte Player-Timeline-Scrub (#79) ist keine zugesagte .22-Funktion und nicht Teil dieser .22-Abnahme.

| ID | Ergebnis | Nutzerbestätigung | Issues |
|---|---|---|---|
| I01 | **PASS** | Version 0.1.29.22 installiert | Update |
| I02 | **FAIL** | Original-XCMate-Icon nach Update nicht sichtbar | #37 |
| I03 | **FAIL** | Original-XCMate-Icon auch **nach Kodi-Neustart** nicht sichtbar | #37 |
| I04 | **PASS** | Bestehende Einstellungen erhalten | Update |
| E01 | **PASS** | EPG startet in der korrekten Startsendergruppe | #88 |
| E02 | **PASS** | Startsender und ursprüngliche Senderreihenfolge | #88 |
| E03 | **PASS** | Sender/Sendungen im EPG geordnet dargestellt | #88, #58 (nur Sichtbefund) |
| E04 | **PASS** | Links öffnet separate Sendergruppen | #88 |
| E05 | **PASS** | IR-Gruppenwahl und Gruppenfilter | #88 |
| E06 | **PASS** | Zurück-Navigation und Positionsspeicher | #88, #59 |
| E07 | **PASS** | Alle oberen EPG-Buttons per D-Pad erreichbar | #92 |
| E08 | **PASS** | Jetzt, 20:15, Vortag/Folgetag, Gruppen und Suche aufrufbar | #92, #93 |
| E09 | **PASS** | Fokus und fokussierte Sender-/Sendungsschrift lesbar | #92 |
| E10 | **PASS** | Scrollen, Refresh-/Gruppen-Navigation stabil | #88, #92, #93 |
| R01 | **PASS** | EPG-Aktion „Jetzt Sender ansehen“ ohne Kodi-Absturz | #89 |
| R02 | **PASS** | Live-TV, OK-/Links-Overlay, Stop – kein unerwünschter Startsenderneustart | #17, #97 (geschlossen) |
| R03 | **PASS** | Normales Serien-Autoplay aus .21 weiterhin funktionsfähig | #85; B02 vertagt |
| R04 | **PASS** | Film-/Serienplayer, Stop, kein Hintergrundton, Resume | #40, #79 |
| R05 | **FAIL** | Mehrere Filmcover fehlen, auch nach Update; konkreter Befund unten | #41, #90, #111 |

**Zusätzliche Nutzerbeobachtungen, exakt als Datenlage abgegrenzt:**
- Original-XCMate-Icon fehlt **an mehreren Stellen**, selbst nach Kodi-Neustart. Es ist **nicht geklärt**, ob Kodi ein altes Icon rendert, das neue Asset an der falschen Stelle verwendet oder ein Texture-/Cache-Problem besteht. **Quell-/ZIP-Prüfung aus .22-PR #110 PASS**, sichtbare Geräteanzeige **FAIL**. Die Originalquelle nicht neu generieren, keine Kodi-Thumbnail-Caches oder Add-on-Daten löschen.
- Es fehlen **mehrere Filmcover**. Konkretes Beispiel: **Disney-Filme → Aladdin (1992)**. Beim Öffnen steht unten **„Poster Netzwerkfehler“**. Das ist ein Nutzer-UI-Befund, kein automatisch verifizierter HTTP-, DNS-, URL- oder Speicherfehler. Es fehlen ein redigiertes aktuelles Log, eine konkrete HTTP-Fehlerklasse, Jobstatus/Versuchsanzahl und Nachweis, dass das Cover **vorher vorhanden** war. Somit nicht als bewiesene Datenlöschung oder pauschale Netzwerkstörung darstellen.

## Triage nach Gerätetest

### P1 – Neue / reproduzierte Fehler

1. **#37 (offen)**: Original-Icon sichtbar FAIL bei I02+I03 trotz nachgewiesenem eingebautem Originalasset, Kodi-Neustart erfolglos. Nachfolgende Diagnose: im Add-on-Infofenster/Kachel/Startansicht konkret altes vs. fehlendes Icon erfassen; sichere Original-Pfade und Kodi-Texturen prüfen, **ohne Cache-Reset oder Icon-Neuentwurf**.
2. **#111 (neu, offen)**: Konkrete Bildanforderung „Poster Netzwerkfehler“ bei Aladdin 1992, mehrere Cover fehlen. Separater gezielter Quell-/HTTP-/Jobstatus-/Retry-Diagnoseauftrag; bei `media_art.fetch` wird jeder andere als ValueError-HTTP-Exceptioncode als `NETWORK_ERROR` klassifiziert. `art_store.run_one` begrenzt Retries auf `attempts<3`; Ursache also noch offen. Keine globale `retry()`-/Queue-Rücksetzung.
3. **#41 (offen)**: Zuvor positive Normalpfade aus Test 47/49, jetzt R05 FAIL für fehlende Covers. Das widerlegt eine pauschal vollständige Cover-Abnahme; lokale bereits vorhandene Bilder haben keinen dokumentierten Datenverlust.
4. **#90 (offen)**: Artwork-Hintergrundsystem weiterhin nicht vollständig abgenommen, aber R05 alleine beweist keinen Rückfall der 512-MB-Sperre; reale Statuswerte fehlen. Kein Budget-Reset.

### EPG-Teilabnahme durch echte IR-Tests

- **#88**: E01–E06 und E09/E10 **PASS für Gruppen-/Startsender-/Senderreihenfolge und Navigation**. Ursprüngliches Issue umfasst zusätzlich per-Sender XMLTV-Quellenwechsel mit Vorschau (#98), EPG-Langdetails/Bilder, Ausnahme-/Logo-/Fallback-/mehrere-Skins-Tests. **Nicht vollständig abgeschlossen**; diese Nacharbeiten getrennt dokumentieren.
- **#92**: E07–E10 **PASS für ursprüngliche sichtbare Fokus-/Header-Störung** auf Ziel-Android mit BINGIE MOD. Dokumentierte Zusatzabnahme anderer Skins und Sonderfälle (Estuary, Tab/Context/Doppel-Back usw.) nicht gesondert nachgewiesen. **Funktioneller Kernfehler behoben; vor formalem Abschluss verbliebene DoD prüfen**, keine unberechtigte Behauptung mehr, Kopfbuttons seien im .22 nicht erreichbar.
- **#93**: E08/E10 PASS für Kopfbuttons/Scrollen, aber Quellhorizonte, +7-Tage-Programme, Zeitumstellung/leer/echt verfügbare XMLTV-Daten nicht geprüft → offen.
- **#58**: E03 PASS für geordnete aktuelle EPG-Sicht, aber Deduplikation mit identischen/überlappenden Rohereignissen aus mehreren Quellen nicht nachgewiesen → offen.
- **#59**: E06 und R04 PASS für normale Rücknavigation, aber nicht alle im ursprünglichen Issue definierten 20x Back-/Film-/Serien-/Estuary-Sonderwege nachgewiesen → offen.
- **#89**: R01 PASS zusätzlich zu früheren .17/.21 Erfolgsdurchläufen; besondere ungültige Streams/Back-Doppelaktionen/Fremdstream-/Fehlerfälle noch offen, kein neuer Absturz gemeldet.
- **#85**: R03 PASS, Staffelwechsel B02 **ausdrücklich vertagt**. Nutzerbestätigung irgendwann später genügt zum dokumentierten Schließen wie vereinbart.

## Maßnahmen und Freigabe

Testergebnisse und Fehler auf betroffenen Issues dokumentieren, vorhandene Issue-Texte erhalten. Nur Issues schließen, wenn **alle jeweils noch relevanten** Abnahmekriterien bestätigt sind; funktionale PASS-Teilbereiche nicht mit dem gesamten Issue verwechseln.

**Keine Codeänderung, keine neue Version, kein Merge, kein Release oder automatische Bereinigung ohne ausdrückliche Nutzerfreigabe.** Keine Zugangsdaten/Portal-URLs, Tokens oder ungefilterte `kodi.log` öffentlich ablegen.
