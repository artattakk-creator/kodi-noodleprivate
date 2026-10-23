# XCMate Android-Test 50 – kumulative Version 0.1.29.22

**Start 23.10.2026:** Nutzer bestätigt Installation von .22. **I01 PASS (Version installiert)**, **I02 FAIL (Original-XCMate-Icon in der bislang gesehenen Oberfläche nicht sichtbar)**. Für I02 ist der konkrete Anzeigeort noch nicht genannt; der erste Befund ist kein Beweis für einen fehlenden ZIP-Asset. Alle weiteren Testpunkte **NOT_TESTED**, bis Nutzer persönlich bestätigt.

**Zielgerät:** Android 13 RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung. PR #110 ist gemergt und .22 im GS-Media-Repository veröffentlicht; 785/785 Hosttests/CI PASS ist **kein** Android-UX-PASS. .22 ist kumulativ über .21 installiert. Unveränderte Add-on-ID `plugin.video.xtreammate`.

**Regeln:** Nur Nutzer-Gerätetest als PASS; Abweichungen FAIL; Ungeprüftes NOT_TESTED. Bei Absturz, festhängendem Stream oder anderen schweren Symptomen anhalten und das betroffene Teilproblem statt riskanter Wiederholung melden. Keine Deinstallation/Downgrades, Cachebereinigung, Portal-Resets, Artwork-Neudownloads, globale Kodi-Keymaps oder eigenmächtiger Merge. Aus Datenschutzgründen keine Provider-URLs/Logintokens in GitHub-Logs/Abbildungen.

## Block I – Installation, Icon, Bestand

| ID | Vorgang / erwartetes Ergebnis | Issues | Anfangsstatus |
|---|---|---|---|
| I01 | Installierte Add-on-Version ist **0.1.29.22**, aus GS-Media-Repository aktualisiert, kein zweites XCMate | Updatepfad | **PASS** |
| I02 | Sichtprüfung des **Original-XCMate-Icons** im bereits betrachteten Kodi-/Add-on-Bereich unmittelbar nach Update, nicht neues oder altes Platzhalter-Icon | #37 | **FAIL – Nutzer meldet nicht sichtbar** |
| I03 | Kodi **regulär neu starten**; Original-Icon in Add-on-Informationen und Add-on-Kachel anzeigen; Anzeigeort/aktuelles Icon beschreiben. Keinen Cache löschen | #37 | NOT_TESTED |
| I04 | Portale, konfigurierte Startgruppe/Startsender, EPG-Zuordnungen, Favoriten, gespeicherte Filme/Serien, Resume und Einstellungen unverändert | Update/Regression | NOT_TESTED |

## Block E – großes horizontales EPG

| ID | Vorgang / erwartetes Ergebnis | Issues | Anfangsstatus |
|---|---|---|---|
| E01 | EPG öffnen: **nur konfigurierte Startsendergruppe**, keine globale Mischung aktiver Gruppen | #88 | NOT_TESTED |
| E02 | Gespeicherter Startsender an seiner **ursprünglichen Senderposition** fokussiert, nicht künstlich ganz oben; Senderliste entspricht ursprünglicher Reihenfolge | #88 | NOT_TESTED |
| E03 | Senderzeilen und deren Programme klar getrennt, EPG-Sendungen pro Sender entlang der Zeitachse korrekt chronologisch; kein scheinbar ungeordnetes Vermischen | #88, #58 (nur Sichtbefund) | NOT_TESTED |
| E04 | D-Pad **Links** vom Programm zur Senderspalte, nochmals Links an Sendergrenze → **separate Gruppenliste** sichtbar | #88 | NOT_TESTED |
| E05 | Gruppenliste Hoch/Runter, OK → ausschließlich Sender der ausgewählten Gruppe; Reihenfolge und Fokus sichtbar konsistent | #88 | NOT_TESTED |
| E06 | Zurück **aus Gruppen** verwirft unbestätigte Wahl und stellt vorherige EPG-Sender-/Zeit-/Fokusposition wieder her; Zurück aus Raster → XCMate-Home | #88, #59 | NOT_TESTED |
| E07 | Im Raster **Hoch von oberster sichtbarer Programmzeile** → obere EPG-Button-Leiste; sechs Kopfbuttons mit Links/Rechts fokussierbar; Runter zurück | #92 | NOT_TESTED |
| E08 | Kopfaktionen **Jetzt, 20:15, Vortag, Folgetag, Gruppen, Suche** einzeln per OK auslösbar und sichtbar wirksam | #92, #93 | NOT_TESTED |
| E09 | Markierte Sender-/Sendungstitel bleiben gut lesbar; Neon-Fokus hinter Inhalt; auch kurze Balken, lange Titel und Logos | #92 | NOT_TESTED |
| E10 | Tief scrollen (mind. 8 Sender), zurück in Kopfzeile; nach 35 Sekunden EPG-Refresh bleibt Fokus; soweit problemlos, 20 Gruppenwechsel und Tagesgrenzen ohne Hänger | #88, #92, #93 | NOT_TESTED |

## Block R – Regression .21-Funktionen in .22

| ID | Vorgang / erwartetes Ergebnis | Issues | Anfangsstatus |
|---|---|---|---|
| R01 | EPG → OK → „Jetzt Sender ansehen“: korrekter Sender, **kein Kodi-Absturz**, kontrolliertes Stop/Zurück | #89 | NOT_TESTED |
| R02 | Live-TV-Sender starten, OK-Info/Links-Overlay, stoppen: Bild/Ton aus, **kein Startsender-Neustart** | #97 geschlossen, #17 | NOT_TESTED |
| R03 | Autoplay nach natürlichem Ende **einer oder zwei Folgen** beibehalten, Ein/Aus und Stop kontrollieren; **kein B02-Staffelwechseltest** | #85 | NOT_TESTED |
| R04 | Film/Serie abspielen, eigenes Player-OSD, Play/Pause/Stop und Resume; nach echtem Stop kein Hintergrundstream | #40, #79 | NOT_TESTED |
| R05 | Bereits gespeicherte Cover, Fanart und Logos bleiben nach Kodi-Neustart sichtbar; keine Neudownloads erforderlich | #41, #90 | NOT_TESTED |

**Verbindlich ausgeschlossene Prüfungen:**
- **B02 – echter Staffelwechsel** bleibt auf Nutzerwunsch bis zu dessen späterer spontaner Bestätigung aus der geführten Checkliste entfernt. Sobald Nutzer bestätigt, dass letzter Teil Staffel N → erste gültige Folge Staffel N+1 automatisch spielt, Nachweis mit Version/Datum dokumentieren und Issue #85 als completed schließen.
- **Player-Timeline-Scrubbing/Transport-Icons (#79)** sind eine neue separate Änderungsanforderung, nicht als Funktion von .22 voraussetzen und nicht als .22-FAIL werten.
- **EPG-Kontextmenü für manuelle Quellzuweisung (#98)** und vollständiges Space Premium sind separat; .22 nicht für dort noch fehlende Features abwerten.
- Artwork-Downloadpause bleibt `BLOCKED_UI / NOT_TESTED` aus Test 48, kein Neuladen zum Erzwingen einer Testbarkeit.

**Ergebnisübernahme:** Nutzer sendet alle IDs mit PASS/FAIL/NOT_TESTED und Beobachtungen; erst dann GitHub-Issues aktualisieren und **nur vollständig abgenommene** Issues schließen. Test 50 ersetzt frühere Erfolgsmeldungen nicht.
