# XCMate – Android-Test 49 | Version 0.1.29.21

**Testplan erstellt: 23.10.2026.** Alle Einzelergebnisse zunächst **NOT_TESTED**; Nutzer bestätigt ausschließlich reale Android-Beobachtungen. Dies sind keine automatisierten PASS-Claims.

**Zielplattform:** Android TV 13, RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung. Test-ID: 49.

**Version:** 0.1.29.21 aus `main`; PR #109 gemergt. PR #110 wurde inzwischen als **kumulative .22 auf .21** entwickelt und am 23.10.2026 auf ausdrückliche Freigabe nach `main` gemergt: Autoplay/Player bleiben erhalten, EPG-Korrekturen und Original-Icon sind enthalten. Die alten isolierten .22-ZIPs sind überholt. Für den neuen Kandidaten gelten der gepinnte ZIP/Hash in PR #110 und [die eigene .22-Direktupdate-Anleitung](ANDROID_TEST_02922_DE.md): direkt über .21 installieren, ohne Deinstallation oder Downgrade. Siehe [Updatepfad](UPDATEPFAD_02921_02922_DE.md).

## Abnahme: PASS / FAIL / NOT_TESTED

- PASS nur bei **real geprüftem** Erfolg aller beschriebenen Teilschritte.
- FAIL bei Abweichung (Symptom, reproduzierbare Schritte, Skin, sichtbare Meldung angeben).
- NOT_TESTED für ungeprüft, nicht zugänglich oder nicht sinnvoll provozierbare Fälle.
- Bei Kodi-Absturz, Black Screen mit blockierter Bedienung, ungewolltem Hintergrundstream oder Datenverlust: Teststrecke anhalten, Fehler dokumentieren; keine risikobehafteten Wiederholungen.
- Keine Datenbanken, Caches, Portal-/EPG-Konfigurationen löschen; Zugangsdaten, Provider-URLs und Tokens nicht in öffentliche GitHub-Logs/Screenshots.
- Kein Issue automatisch schließen: erst nach vollständiger Definition-of-Done + Regression + Nutzerfreigabe.

### Block A – Baseline und frühere P0-/P1-Regressionen

| ID | Prüfschritt | Relevante Issues | Ergebnis |
|---|---|---|---|
| A01 | .21 regulär über GS-Media-Repository oder verifiziertes ZIP installieren; Version bestätigen; Kodi neu starten; Portale/Einstellungen/Favoriten weiter vorhanden | Updatepfad | NOT_TESTED |
| A02 | Funktionierenden Live-TV-Sender öffnen: Bild/Ton; OK-Infobar und Links-Navigation; Stop beendet Wiedergabe, ohne Startsender automatisch wieder anzuschalten; Kodi bleibt offen | #97, #17 | NOT_TESTED |
| A03 | Im EPG gültige laufende Sendung mit OK und „Jetzt Sender ansehen“ starten; weder Kodi-Absturz noch Doppelstart; Stop/Zurück kontrolliert | #89 | NOT_TESTED |
| A04 | Film und Episode starten; OSD-Back schließt nur Leiste; explizites Verlassen/Stop beendet Bild und Ton vollständig, kein versteckter Hintergrundstream | #40, #79 | NOT_TESTED |
| A05 | Eigenes Film-/Serien-OSD per IR: Fokus, Pause/Play, Seek, Audio/Untertitel sofern verfügbar, Bild-Einstellungen, manueller Next; nur tatsächlich verfügbare Funktionen anzeigen | #79 | NOT_TESTED |
| A06 | EPG-Grundnavigation, Senderlogos, Jetzt/Danach; keine neue Behauptung über bereits reparierte Startgruppen/Header aus .22; bekannte #88/#92 bleiben offen | #88, #92 | NOT_TESTED |
| A07 | Schon geladene Cover und Senderlogos vor/nach Kodi-Neustart erhalten, Warteschlange ohne unnötiges Neuladen; fehlender Artwork-Pause-Button: BLOCKED_UI / NOT_TESTED, kein erneutes Herunterladen | #41, #90, #69 | NOT_TESTED |

### Block B – Serien-Autoplay .21

**B02 (automatischer Staffelwechsel) ist auf ausdrücklichen Nutzerwunsch vom 23.10.2026 aus der aktiven Teststrecke entfernt.** Historisches Ergebnis bleibt NOT_TESTED / VERTAGT, nicht FAIL. Der Nutzer prüft gelegentlich eigenständig und meldet den Erfolg. Danach die Meldung mit Version/Datum auf Issue #85 dokumentieren und das Issue ohne erneute Rückfrage schließen. Alle übrigen B-Tests aus Test 49 sind bereits als PASS gemeldet, siehe [Ergebnisbericht](ANDROID_TEST_49_ERGEBNISSE_02921_DE.md).

| ID | Prüfschritt | Relevante Issues | Ergebnis |
|---|---|---|---|
| B01 | Drei aufeinanderfolgende Episoden **natürlich** enden lassen: automatische neue echte Wiedergabe ohne OK (kein bloß wechselnder Titel); kurze Testfolgen bevorzugen | #85 | NOT_TESTED |
| B03 | Im eigenen Player Autoplay Ein → Aus, Folge natürlich enden lassen ohne Folgestart; in neuer Wiedergabe Ein, Fortsetzung wieder aktiv | #85, #79 | NOT_TESTED |
| B04 | Stop mitten in Episode und gestuftes Back (OSD schließen ≠ Stop); nach echtem Stop kein weiterer Stream/Hintergrundton | #85, #40 | NOT_TESTED |
| B05 | Fünf Stop-/Back-Versuche unmittelbar um Episodenende/Wechsel; kein unerwünschter oder doppelter Start; wenn Playback instabil, nicht weiter provozieren | #85 | NOT_TESTED |
| B06 | Letzte verfügbare Serienfolge natürlich beenden: kein Wraparound. Wenn regulär auftretende fehlende Quelle: verständlicher Abbruch, keine Startschleife | #85 | NOT_TESTED |
| B07 | Folge >1 min ansehen, stoppen, Kodi neu starten: Resume erhalten; natürlich beendete Folge als gesehen, Favoriten bleiben; Next im richtigen Portal und in richtiger Serie | #85 | NOT_TESTED |
| B08 | Film, Live-TV und fremdes Add-on starten keine Serien-Folgekette; Kodi regulär während Serienwiedergabe beenden und erneut starten: kein automatischer neuer Stream | #85, #97 | NOT_TESTED |

## Issue-Abschlussregeln

- **#89** nur nach A03 PASS und stabiler EPG-Wiedergabe auf dem Gerät, ohne andere EPG-Rückschritte.
- **#97** nur nach A02 PASS, kontrolliertem Stop und erneutem Start ohne Kodi-Beendigung.
- **#40** nur bei A04+B04 PASS einschließlich Film/Serie, Stop und kein Audio im Hintergrund.
- **#79** nur nach A04/A05/B03 und den weiteren vollständigen OSD-Abnahmekriterien; einzelne PASS sind zunächst Teilabnahme.
- **#85**: B01 und B03–B08 sind gemäß Ergebnisbericht PASS. B02 ist ausdrücklich VERTAGT und kein Bestandteil weiterer geführter Teststrecken. Nach der späteren ausdrücklichen Nutzerbestätigung des echten automatischen Staffelwechsels (Staffel N letzte Folge → Staffel N+1 erste Folge) diese mit Version/Datum auf GitHub dokumentieren und #85 selbstständig schließen.
- **#41/#90** nicht allein nach A07 schließen: physischer Speicherreserve-Schutz, alte Space-Full-Queue/Cache-Invarianten und gesonderte Tests bleiben relevant.
- **#88/#92/#37** erst mit kumulativer .22 erneut vollständig testen; in .21 nicht als erledigt markieren.
- **Artwork-Pause-Bedienelement** separat als `BLOCKED_UI/NOT_TESTED`, kein gezwungener Neudownload.

## Ergebnismeldung

Pro ID `PASS / FAIL / NOT_TESTED`, Version, Skin, ggf. Beobachtung/Fehlerzeitpunkt. Nach Nutzerbestätigung Ergebnisse auf GitHub dokumentieren, nur vollständig abgenommene Issues einzeln schließen. Alte historische Defekte sind nicht automatisch aktuell reproduziert.

**Wichtig:** Der in der älteren `ANDROID_TEST_02921_DE.md` empfohlene Downgrade auf .20 vor einem unabhängigen .22-Test ist durch den kumulativen Updatebeschluss überholt. Keine Rückinstallation zur normalen Testfolge.
