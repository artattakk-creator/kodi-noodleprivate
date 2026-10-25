# XCMate 0.1.29.35 – Android-Abnahme / Teststrecke (VORAB)

**Stand:** 25.10.2026. **Alle Tests bei Auftragserstellung NOT_TESTED**. Kodi 21.2 Omega · Android TV 13 · RK3528 ARM32 · Titan BINGIE MOD · IR-Fernbedienung.  
**Quellauftrag:** [CODEX_AUFTRAG_02935_SUCHPERFORMANCE_EPG_NAV_20261025_DE.md](CODEX_AUFTRAG_02935_SUCHPERFORMANCE_EPG_NAV_20261025_DE.md).

**Installation:** Nur reguläres **kumulatives Upgrade** vom letzten freigegebenen `main`-Release; kein Deinstallieren/Downgraden, keine Portale/Favoriten/EPG-Mappings/Artwork-Daten löschen. Test-ZIP erst nach Codex-Draft und ausdrücklichem Merge/Updateauftrag. Host-CI/ZIP/SHA sind kein Android-PASS.

**Statuswerte:** `PASS / FAIL / BLOCKED / NOT_TESTED`. Bei `BLOCKED` abhängige Tests nicht als FAIL markieren. Realer Messwert mit Zeitpunkt/Uhr und Cold/Warm notieren; keine Provider-URLs, Zugangsdaten oder Rohlogs öffentlich.

## A. Unverändertes Suchdesign + schnelle Live-Suchergebnisse (höchste Priorität)

| ID | Aktion | PASS nur wenn | Stand |
|---|---|---|---|
| V0 | Im Kodi-Add-on Versionsanzeige kontrollieren. | Tatsächlich installierte erwartete Folgeversion bestätigt, Daten/Portale/Originalicon vorhanden. | NOT_TESTED |
| PERF-01 | Aus großem EPG globale Suche öffnen, **Sendername** eingeben; dreimal kalt/warm, Tab Live-TV ggf. ausdrücklich anwählen. | Suchmaske sofort bedienbar; **erstes tatsächlich sichtbares, anwählbares Live-Namensresultat innerhalb weniger Sekunden** statt bisherigen 1–5 Minuten; unabhängig vom kompletten EPG-Scan. Exakte Zeit aufzeichnen, Engineering-Ziel <5 s warm / <10 s kalt soweit Gerät es erlaubt. | NOT_TESTED |
| PERF-02 | Echten im Guide sichtbaren „Jetzt“-Programmtitel eingeben, Ergebnis bewusst anwählen, ggf. Sender öffnen, Back. | Passender **echter** Programmtiteltreffer mit korrektem Sender, schneller als zuvor ~120 s; kein falsches Namensmatching; EPG/Back korrekt. | NOT_TESTED |
| PERF-03 | Selbes Query/gleicher Tab wiederholen; Live→Film→Serie→Live; während laufender Suche neues Query, Back und Guide-Reopen. | **Kein unnötiger Full-Scan bei reinem Tabwechsel**, kein verschleppter Treffer, kein Fokus-/Tab-/Scroll-Reset, keine einfrierende UI; nur echter Query-/Datenversionswechsel kann Neuscan erfordern. | NOT_TESTED |
| PERF-04 | Test mit fehlendem lokalen Jetzt-EPG / Provider-Short-EPG-Timeout (sofern reproduzierbar). | Sendernamenssuche trotzdem zügig; vorhandenes neutrales „keine EPG-Daten“, kein falscher Programmtitel; Fehler nicht minutenlang GUI-blockierend. | NOT_TESTED |

**Anmerkung:** Bei ersten Render-Events zwischen zwei Zeitstempeln ist `SEARCH_RESULT_READY` allein **kein** PASS: Ein **sichtbarer und bedienbarer Live-Treffer** muss auf dem Gerät vorhanden sein. Finale EPG-Vollscan-Zeit separat erfassen.

## B. Infobar → GROẞER Guide, Links → Mini-EPG

| ID | Aktion | PASS nur wenn | Stand |
|---|---|---|---|
| ROUTE-01 | Live-TV Vollbild → OK → zweites OK/Runter → Weitere → **EPG**. | **Großer horizontaler XCMate-Guide** sichtbar; nicht Mini-Senderliste, keine Kodi-Home-Reaktivierung. | NOT_TESTED |
| ROUTE-02 | Während Stream läuft Groß-EPG öffnen, ohne Senderwahl zurück. | Playback/Audio bleiben stabil, Back bringt Live-TV/Infobar-Kontext ohne neuen Playerstart, schwarzen Bildschirm oder Busy-Freeze. | NOT_TESTED |
| ROUTE-03 | Groß-EPG über Infobar öffnen, anderen Sender „Jetzt ansehen“, mehrfach wiederholen. | Genau ein korrekter Senderwechsel, IR/Infoleiste weiter nutzbar; kein `GUIDE_HANDOFF SKIPPED`. | NOT_TESTED |
| ROUTE-04 | Live-TV Vollbild/Info → **Links** (zweimal). | 1× Links **kleine** Sender-/Jetzt-EPG-Liste, 2× Links Gruppen; kein ungefragter großer EPG. | NOT_TESTED |

## C. Startgruppe / Mini-Senderfokus

| ID | Aktion | PASS nur wenn | Stand |
|---|---|---|---|
| GROUP-01 | XCMate/frisches Guide-Fenster → **großer EPG erstmals** öffnen. | **Konfigurierte aktivierte Startgruppe**, nicht „Alle aktivierten Sender“; Startsender in passender Gruppe fokussiert. | NOT_TESTED |
| GROUP-02 | Im Guide ausdrücklich andere Gruppe wählen, Back/Reopen; Test mit deaktivierter Startgruppe. | Explizite Auswahl bleibt im dafür vorgesehenen Ansichtskontext, Default/Fallback korrekt, **keine Änderung** der gespeicherten Startgruppen-/Startsender-Settings. | NOT_TESTED |
| MINI-01 | Live-Sender starten, Vollbild → Links; danach einen anderen Sender auch gruppenübergreifend starten und erneut Links. | Jeweils **wirklich laufender Sender** sichtbar markiert, in richtiger aktiver Gruppe und mit passendem Logo/Now; nicht erste Zeile/`*` aus reinem Fallback. | NOT_TESTED |

Falls C bewusst ausgegliedert wird, **GROUP-01/02 und MINI-01 als NOT_TESTED mit „nicht im .35-Candidate enthalten“**, nicht PASS, dokumentieren.

## D. Bestandsschutz / Medien / Abschluss

| ID | Aktion | PASS nur wenn | Stand |
|---|---|---|---|
| REG-01 | Film- und Seriensuche mit Postern; Details, Staffeln, Episoden, Zurück. | **Identische eingefrorene** 3-Tab-Suchmaske Live-TV/Filme/Serien, Cover/Logo-/Fokus-Platz, Mediennavigation und Back genau wie .34; schnelle Film-/Serientreffer. | NOT_TESTED |
| REG-02 | Serie abspielen, automatische nächste Episode, ggf. Staffelwechsel; Nutzer-Stop. | Autoplay/Resume/Staffelwechsel nicht regressiert. Früheres .34-Langzeit-PASS ist **historisch**, ersetzt keinen neuen Test wenn Codepfad beeinflusst wird. | NOT_TESTED |
| REG-03 | Großer Guide → Sender, Guide→Suche→Back, einfache Fernbedienung/Infooverlay, Original-Icon, gespeicherte Profile/Mappings. | EPG-Handoff .34 weiterhin zuverlässig; kein Busy10138, kein Home-Sprung, kein Verlust von Profilen/Favoriten/EPG-Zuordnungen. | NOT_TESTED |

## Dokumentationsregeln

- Angegebenen Zeitstempel/die Variante und **Latenz bis ersten bedienbaren Sender- oder Programmtreffer**, nicht nur Fensteröffnung, dokumentieren.
- Aus `.34` historisch: G1 EPG-Senderstart zuverlässig, G2 Navigation PASS/Performance FAIL, G3 echter Programmtitel gefunden/Performance FAIL, G4 inkl. über Nacht geschätzt 7–8 Folgen und Staffelwechsel PASS. `.33` historisch: **11 PASS / 3 FAIL / 1 NOT_TESTED**. Frühere Werte **nicht verändern**.
- Eine neue .35-Beta- oder Android-Gesamtfreigabe ist **erst nach echten Nutzerergebnissen** und ggf. verantworteter Restfehlerliste möglich.
- Live-TV-Performance, Infoleisten-Groß-EPG und Startgruppe dürfen nicht mit unfertigen Downloads/Recordern, großem Designwechsel, TMDb-Poster-Workflow, EPG-Quellenzuweisung oder Codec-Engine experimentell vermischt werden.


---

## ECHTER Android-TV-Test – Nutzer-Rückmeldung 25.10.2026 (nach Upgrade auf .35)

**Genaue Nutzer-Rückmeldung im Chat; keine nachträgliche Stoppuhrmessung, keine neuen Logfiles.** Kodi 21.2 Omega, Android TV 13, RK3528 ARM32, Titan BINGIE MOD, Fernbedienung. Diese Tabelle ist ein **separater tatsächlicher Gerätebericht**; der obige VORAB-Testplan bleibt als Sollbeschreibung erhalten.

**Checkbox-Bericht unverfälscht:** **14/15 bearbeitet**, **14× PASS**, **0× FAIL**, **0× BLOCKED**, **1× NOT_TESTED**. **Gesamtfreigabe noch nicht gegeben** wegen ungetestetem PERF-03 und qualitativer Performance-/Trefferabdeckungsauffälligkeiten.

| Gate | Vom Nutzer gesetzt | Beleg / wichtige Qualifikation |
| --- | --- | --- |
| V0 | **PASS** | Version/Profil/Konfiguration erhalten |
| PERF-01 | **PASS** | Sendernamensuche funktioniert und erscheint gegenüber .34 ausreichend beschleunigt; **keine Cold-/Warm-Sekundenwerte erfasst**, vorgeschlagene 3 Wiederholungen nicht als einzeln gemessen belegen |
| PERF-02 | **PASS** | **Eingeschränkte Trefferabdeckung:** erster eingegebener echter „Jetzt“-Sendungstitel (**Nutzer konnte Schreibweise nur annähernd als „Lost … Files“ wiedergeben**) wurde **nicht gefunden**. Zweite konkrete Suche **„MacGyver“** wurde nach merklicher Wartezeit erfolgreich gefunden. **Also: Suchfunktion funktioniert prinzipiell, aber nicht für beide geprüften Titel.** Keine Zeitmessung, keine Aussage, ob der erste Titel im lokalen EPG-/Provider-Cache tatsächlich vorhanden war; **Teilbefund Suche PASS mit offenem GENAUIGKEITS-/COVERAGE-Gate**. Nicht „alle EPG-Titel gefunden“ behaupten |
| PERF-03 | **NOT_TESTED** | Reiner Tabwechsel, Suchgeneration, erneute/ersetzte Query und Wiederaufbau des Fensters im konkreten Gerätezyklus nicht getestet |
| PERF-04 | **PASS** | Sendernamensuche ohne verfügbare EPG-Daten |
| ROUTE-01 | **PASS** | Infobar-EPG öffnet großen horizontalen Guide |
| ROUTE-02 | **PASS** | Back aus großem Guide führt zum laufenden Live-TV |
| ROUTE-03 | **PASS** | Guide-Senderwahl und Wechsel zuverlässig |
| ROUTE-04 | **PASS** | Links→Mini-Senderliste→Sendergruppen funktional richtig, **ABER** Infoleiste/Overlay benötigt nach Nutzerbeobachtung **sehr lange zum Öffnen**, danach Zugang zur Mini-Liste entsprechend träge. **OSD_REACTION_LATENCY = OFFEN**, nicht durch funktionales PASS wegmarkieren |
| GROUP-01 | **PASS** | Großer EPG startet in gespeicherter Startgruppe |
| GROUP-02 | **PASS** | Nutzer setzt korrekten Gruppenwechsel/Fallback; **keine separaten Messprotokolle** |
| MINI-01 | **PASS** | Aktueller Sender korrekt in Mini-EPG fokussiert |
| REG-01 | **PASS** | Unveränderte 3-Tab-Suchmaske, Filme/Serien/Cover/Staffeln |
| REG-02 | **PASS** | Automatischer Episodenwechsel; nicht unterstellen, dass in **diesem** .35-Lauf erneut 7–8 Folgen und Staffelübergang nachts protokolliert wurden (das war .34) |
| REG-03 | **PASS** | EPG-Suche/Back/Player/Bestandsschutz funktionieren |

**Weitere echte Gerätebeobachtung außerhalb der 15 Checkpoints:** **Startkanal aus XCMate-Menü startet**, benötigt aber **gefühlt länger** als zuvor/erwartet. **START_CHANNEL_FUNCTION = PASS, START_LATENCY = ungeklärt**, kein exakter Sekundenwert, kein belegter Crash/Fehler. Nicht mit tatsächlicher Streaming-Handshake-Zeit verwechseln, bis `HOME_START_CLICK → ROUTE/RESOLVER → PLAYBACK_STARTED → VIDEO_FRAME → OSD_READY` getrennt gemessen wird. Issue #120 / #35 beachten.

### Verbindliche Nacharbeiten, noch KEINE neue Releasefreigabe

1. **PERF-03 einzeln auf derselben .35 durchführen**: Suche mit Sendernamen öffnen, **ohne Suchtext zu ändern** nacheinander Live-TV → Filme → Serien → Live-TV; danach neues Query eingeben. Ergebnisse dürfen nicht minutenlang neu laden oder alten Query überdecken; Fokus und Back sollen stabil sein. **Status bis zum Nutzertest NOT_TESTED**.
2. **EPG-Titel-Fehlfund isolieren:** Den exakt im **großen EPG sichtbaren** Titel, Sender und angezeigte Start-/Endzeit (ohne private Portal-ID) notieren, unmittelbar danach exakt denselben Text in globale Suche eingeben; EPG-Quellmapping/Now-Cache vs Suchindex/Zeitfenster/Normalisierung vergleichen. Der zweite Treffer **„MacGyver“** beweist nur eine erfolgreiche konkrete Sendungstitelsuche, keine vollständige EPG-Abdeckung. Keine falsche PASS/FAIL-Festlegung ohne Repro.
3. **Startkanal-Pfad #120**: für Menü-Start `home_start` mit `time.monotonic_ns()` die Phasen `MENU_OK → RESOLVER → PLAY_REQUEST → FIRST_VIDEO → OSD_READY` und Cold/Warm/Cachezustand messen. Prüfen, ob Full-Live-Katalog, Portal-Handshake/NowEPG/Artwork blockiert; **keine** bestehenden Start-/Back-/LiveSession-/Fernbedienungsfunktionen umbauen.
4. **Infoleiste-/Mini-EPG-Latenz #17/#35**: `REMOTE_OK/LEFT → SERVICE_DISPATCH → NAVIGATOR_READY → FIRST_INFO_VISIBLE → MINI_READY`, Erstöffnung/Wiederöffnung getrennt. Nicht annehmen, dass langsame Infoleiste nur Streamstart ist. Keine ungemessenen Sekundenwerte erfinden. Lokal vorhandene EPG-/Senderlisten-Snapshots nutzen und UI-Zeit vor großem neuen Player-Design stabilisieren.
5. **Keine unautorisierte PR oder .36 Hotfix-Freigabe aus diesem Bericht**; bestehende UX-Roadmap Rail/Mini-2Spalten/Player-OSD und EPG Hub #161 bestehen als getrennte Folgeprojekte. `.35` bleibt installiert und funktional **weitgehend positiv gerätetesterprobt**.

**Exakte ursprüngliche Nutzer-Checkliste (14 PASS/1 NOT_TESTED) bleibt als echte gemeldete Beobachtung anerkannt.** Diese Hinweise sind zusätzliche Vorbehalte und dürfen nicht als rückwirkend vom Nutzer gesetztes FAIL umgedeutet werden.
