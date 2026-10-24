# .31 – kurze Android-Delta-Abnahme

Vorheriger Stand .30 bleibt **12 PASS / 15 FAIL / 1 BLOCKED / 1 NOT_TESTED**.
MEM1 vier Stunden, MEM2 Service/Neustart, Hintergrund, Sprache und Grundfunktionen
sind bereits PASS. **Keinen erneuten Vierstundentest und keine 29er-Vollmatrix.**

## Installieren

ZIP + SHA256 von Draft #154 laden, Hash prüfen:
`sha256sum -c plugin.video.xtreammate-0.1.29.31.zip.sha256`.
Kodi → Addons → aus ZIP installieren → .31 über bestehende .30 installieren.
Keine Deinstallation, Profil-/Cache-/Bilder-/EPG-Löschung. Addoninfo muss .31 zeigen.
Die reguläre Repository-Veröffentlichung erfolgt erst nach Freigabe.

Einmal kurzer normaler Start-/IR-Durchlauf (S1–S5, ca. 3–5 Minuten): Home,
Film-/Seriendetails, bekannter Live-Start/Stop, großer EPG und vorhandene Daten/
Originalicon. Die früheren PASS werden dadurch nicht zurückgesetzt.

## Nur die geänderten Abläufe prüfen

| ID | Tatsächlicher Ablauf / erwartetes Ergebnis | .31 |
|---|---|---|
| Q1 | Aktuellen echten Sendungstitel im großen EPG ablesen, global suchen, OK der Texteingabe. Suchfenster bleibt, kein Auto-Player/Home-Sprung. | NOT_TESTED |
| Q2 | Live-Tab wählen, Suche zu Ende zählen lassen (+ bedeutet noch nicht fertig). Auch spät einsortierte Sender und derselbe Jetzt-Titel auf mehreren Sendern müssen korrekt erscheinen. Erst bewusst Down zum Treffer und OK startet den gewählten Sender. | NOT_TESTED |
| Q3 | Leere/fehlende EPG-Treffer, erneute Suche und Back; kein Fensterverlust oder falscher Fokus. Kurzzeit-EPG nach Entblockung ebenfalls prüfen. | NOT_TESTED |
| Z1 | Downloadordner wählen zeigt intern/USB/Kodi-SMB (bisher ST1 ungetestet). Vorhandene USB-Auswahl/Persistenz nicht zurücksetzen. | NOT_TESTED |
| Z2 | Speicher → „Gewähltes Downloadziel testen“ auf echtem USB und Kodi-SMB. Explizit bestätigen; Bytes/SHA256-Readback bestanden, eigene neue Testdatei entfernt. Kein Providerabruf und kein interner Ersatz. | NOT_TESTED |
| D1 | Einen durch REDIRECT_UNTRUSTED_TARGET gestoppten Job öffnen. Erste Aktion „Ziel prüfen/freigeben“. Zunächst „gesperrt lassen“: kein Start, keine Freigabe. | NOT_TESTED |
| D2 | Ausschließlich anhand eigener Anbieterinformationen unabhängig bestätigtes CDN-Ziel bewusst auswählen, private Source/Target-Origins prüfen/bestätigen. Zweite Bestätigung startet nur diesen Job erneut. Geänderte/abgelaufene Anfrage bleibt unfreigegeben. | NOT_TESTED |
| D3 | Autorisierten ganzen Film und eine ganze Folge auf USB und SMB speichern: Bytes >0, COMPLETE, richtige Datei/Staffel/Folge und Wiedergabe. Zieltest allein ersetzt das nicht. | NOT_TESTED |
| D4 | Pause/Fortsetzen, bewusster Abbruch/Retry und Kodi-Neustart. USB lokal auch offline abspielen; SMB benötigt erreichbaren Server. Keine falsche COMPLETE-Meldung. | NOT_TESTED |
| D5 | Freigabe im Downloadmanager gezielt widerrufen; nächster entsprechender Cross-Origin-Versuch wieder gesperrt. Unsichere/ungeklärte Ziele weiter ablehnen. | NOT_TESTED |

Bei vorgeschaltetem Fehler die abhängigen Tests BLOCKED/NOT_TESTED markieren,
nicht als mehrere neue Ursachen auslegen. TARGET_TEST-PASS beweist kleine echte
Zieldatei, kein vollständiges Medium und keine native Direct-TS-Aufnahme.

Nur anonyme SEARCH_EPG-/SEARCH-Lifecycle-/DOWNLOAD_PHASE-Codes und Zähler teilen.
Keine Suchbegriffe, Mediennamen, Portal-/Provider-/SMB-Adressen, Tokens oder private
Rohlogs ins öffentliche GitHub. Source-Redirect-Deny von Stage-/Zielkopie unterscheiden.

## Ergebnisblock

```text
XCMate .31 / Kodi 21.2 / Android RK3528 / Datum: ...
Kurzer Grund-Smoke S1–S5: ...
Q1 / Q2 / Q3: NOT_TESTED
Z1: NOT_TESTED
Z2 USB / SMB: NOT_TESTED
D1 / D2: NOT_TESTED
D3 Film / Folge, je USB / SMB: NOT_TESTED
D4 / D5: NOT_TESTED
Vorblocker / fester Fehlercode: ...
```

Nur nach echter Ausführung PASS/FAIL setzen. Unverändert offene Recorder-/Poster-
Fehler (#126/#111) jetzt nicht pauschal wiederholen; ihre Reparatur folgt separat.
#151/Bildsuche, Icon-Rail, Magazin-EPG, Catch-up und Wizard sind nicht Teil dieses
Hotfixes und gelten nicht als umgesetzt. Kein Merge/Release ohne Freigabe.
