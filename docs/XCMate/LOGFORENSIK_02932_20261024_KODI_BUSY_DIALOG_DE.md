# XCMate 0.1.29.32 – Android-Logforensik: EPG-Search RELEASE_TIMEOUT / Kodi Busy Dialog
**Stand:** 24.10.2026. **Status:** Fehlerursache deutlich eingegrenzt; **NO CODE FIX / Android .32 FAIL**.

**Verbindliche Grundlage:** reale [.32-Android-Abnahme](ANDROID_ABNAHME_02932_20261024_NUTZERERGEBNISSE_DE.md) mit **7 PASS / 10 FAIL**, davon NAVSEARCH-01–08 FAIL, REG-01 und REG-03 FAIL. [Issue #140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140), [Master #143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143), [gemergter PR #155](https://github.com/artattakk-creator/kodi-noodleprivate/pull/155). Add-on `plugin.video.xtreammate` auf `main` bei Analyse: **0.1.29.32**.

> **Datenschutz:** Die zwei vom Nutzer eingereichten Kodi-Rohlogs **bleiben privat**. Sie enthalten unter Umständen Anbieter-/SMB-/Provider-/Netzwerkinformationen. Hier nur redigierte Ereigniscodes, Zeitpunkte und Quellcodepfade. **Weder Rohlogs noch Suchbegriffe, Tokens, Passwörter, Stream-/SMB-URLs oder anbieterbezogene IDs hochladen.** Die unten angegebenen Logzeilennummern beziehen sich auf die ursprünglichen, nicht veröffentlichten Dateien; sie sind keine GitHub-Dateizeilen.

## 1. Zeitliche Trennung der zwei Dateien

- `kodi.old(8).log`: **30.692 Zeilen**, 24.10.2026 von **08:43:46–12:42:07**. **Keine Installation von .31/.32**, deshalb keine geeignete Basis für die neue .32-Race-Ursache; nur historischer Vergleich.
- `kodi(20261024-181608).log`: **6.999 Zeilen**, 24.10.2026 von **12:42:43–20:13:58**. Installation `.30` um **12:45:14**, `.31` um **16:10:46** und **`.32` um 18:26:13, Zeile 5.446** (Installationsereignis im vollen Log). **Nur der Abschnitt ab 18:26 ist hier beweiskräftig für Version .32.**
- Zielgerät: **Android TV 13, Rockchip RK3528 ARM32, Kodi 21.2 Omega, Titan BINGIE MOD 2.2.3, Full-HD**.

## 2. KRITISCH – EPG-Suche scheitert dreimal mit identischem Release-Timeout

Alle drei beobachteten Fälle betreffen `source=grid`, Kodi `handle=action`, das aktive große XCMate-Guide-Window (Window ID 13004/13005). Eingegebener Suchbegriff ist bewusst nicht öffentlich erfasst.

| Versuch | INITIATED | GUIDE_CLOSED / WAIT_RELEASE | RELEASE_TIMEOUT | Resultierender Zustand |
| --- | --- | --- | --- | --- |
| 1 | **18:57:36.020** (`SEARCH_NAV INTENT`, private Log-Zeile 5871) | **18:57:36.402–.404** (5876–77) | **18:57:38.554** (5880) | `window=10025 dialog=10138`; Navigation `RETURN`, **kein SEARCH_OPEN** |
| 2 | **18:58:49.370** (5934) | **18:58:49.935–.938** (5939–40) | **18:58:51.980** (5943) | `window=10025 dialog=10138`; RETURN, **kein SEARCH_OPEN** |
| 3 | **19:42:51.591** (6566) | **19:42:51.927–.931** (6571–72) | **19:42:53.968** (6575) | `window=10025 dialog=10138`; RETURN, **kein SEARCH_OPEN** |

**Beleg:** Der Kodi-Hauptfensterindex ist bei Timeout bereits **10025** (Guide war sichtbar geschlossen), aber der **aktive Dialogindex 10138**. Nach offizieller [Kodi-Window-ID-Tabelle](https://kodi.wiki/view/Window_IDs) ist **`10138 = WINDOW_DIALOG_BUSY / DialogBusy.xml`**. Die native Suche wird im Guide-Pfad **nie** mit `SEARCH_OPEN` erreicht, weil der Release-Check vorher scheitert.

### Direkter Quellcodebezug (main .32)

`src/plugin.video.xtreammate/resources/lib/search_navigation.py`, **Zeilen 76–88**:

```python
def released(router, source, session, window_id):
    mark('WAIT_RELEASE', router, source, session, owner=True)
    monitor = xbmc.Monitor()
    deadline = time.monotonic() + 2
    while True:
        if monitor.waitForAbort(.05): return False
        try:
            active = window_id is not None and int(xbmcgui.getCurrentWindowId()) == window_id
        except (AttributeError, RuntimeError, TypeError, ValueError):
            active = False
        if not active and not xbmc.getCondVisibility('System.HasActiveModalDialog'):
            mark('RELEASE_READY', router, source, session, owner=True)
            return True
        if time.monotonic() >= deadline:
            mark('RELEASE_TIMEOUT', router, source, session, owner=True)
            return False
```

`guide_flow()`, **Zeilen 91–105**, bricht bei `released(...)=False` sofort ab und **überspringt** das native `open_search()`. Dadurch gelangen gerade diese EPG-Versuche **nicht** zum eigentlichen Such-/EPG-Matcher. `window=10025` zusammen mit `dialog=10138` zum Timeout ist ein eindeutiger Nachweis für den blockierenden Release-Pfad. **Ob dieser Busy-Dialog während sämtlicher zwei Sekunden aktiv war und welche Kodi-Arbeit ihn erzeugt hat, ist bisher nicht gesondert aufgezeichnet.**

**Starke Root-Cause-Arbeitshypothese:** Die pauschale Forderung „kein aktiver modaler Dialog“ verwechselt eine transiente Kodi-interne Busy-Anzeige mit einem fremden, weiter offenen XCMate-/Keyboard-Modal. Es könnte ein gegenseitiges Warten vorliegen: Der Add-on-Callback wartet auf Kodis Busy-Dialog, während Kodi auf die Beendigung/GUI-Freigabe genau dieses Add-on-Aufrufs wartet. **Dieser Deadlock-Zyklus ist noch zu instrumentieren**, nicht als abschließend bewiesen darstellen.

**Verbotene Schnelllösung:** `System.HasActiveModalDialog` nicht pauschal ignorieren; **keine fremden Dialoge schließen**, keine unbedingte `ActivateWindow/Home`-Kette, kein ungebremstes Spinning und keine Timer, die Kodi außerhalb des Input-Owners navigieren. Eigene Modals und echte Player-/User-Dialogs müssen respektiert werden.

## 3. Zweiter, unabhängiger Suchpfad: Medien-Suche läuft, Fokusfehler bleiben

Ebenfalls **nach 18:26/.32**:

- **19:03:15.775** (private Zeile 6019): `[XCMate][SEARCH] SEARCH_INPUT_ACCEPTED` in `window=13004`.
- **19:03:16.834** (6021): `SEARCH_GUI_READY`; **19:03:16.922** (6022) `[SEARCH_NAV] SEARCH_OPEN source=media`; **19:03:22.035** (6025) `SEARCH_RESULT_READY`.
- Ein zweiter Medien-Suchlauf beginnt **19:18:03.438** (6147) und erreicht erneut `SEARCH_GUI_READY` (19:18:04.653, 6149), `SEARCH_OPEN source=media` (6150), viele `SEARCH_RESULT_READY`.
- **Wiederholte Kodi-Fehlermeldungen** `Control 120 in window 13004 has been asked to focus, but it can't` ab 19:02, insbesondere 19:17–19:19, parallel zu partiellen Such-Frames. **Weitere** Fokuswarnungen zu Control 312 in Guide Window 13004 um **18:54:07** und Window 13005 um **19:39:21**.

**Bewertung:** Native Input-, Window-Ready- und Result-Callback-Pipeline wird in Medienroute **tatsächlich ausgeführt**, also ist „alle Suchroutinen starten niemals“ widerlegt. **Nicht belegt:** ob die Treffer auf dem TV gerendert/fokussierbar waren; der Nutzer sagt ausdrücklich „Suche funktioniert überhaupt nicht“. Die Fokusfehler sind ein **zweiter** konkreter UI-/Fokus-Bugkandidat, nicht automatisch derselbe Busy-Gate-Fehler.

`media_window.py` `setFocusId`/`_resume_focus` und `media_search.py` `_open_search`, `_search_ready` sowie XML `XCMateMedia.xml` prüfen: Nicht sichtbare/disabled `Control 120` können noch über initiale Navigationsverknüpfungen, alte Landing-/Detail-Fokusereignisse oder asynchrone Animation adressiert werden. **Welcher Aufrufer den konkreten nativen 120-Fokusfehler setzt, ist noch NICHT mit Callstack belegt.** Trace um `setFocusId` und XML-Navigation erweitern (Focus-Ziel, Sichtbarkeit, Enabled, Modus, Session; keine Dateninhalte).

### EPG-Matcher-Daten erst nach GUI-Reparatur bewerten

- Ab ca. **19:17–19:19** enthält der .32-Log **64 `[XCMate][SEARCH_EPG]`-Events**, alle **`code=EPG_PARTIAL`**; im letzten sichtbaren Frame `scanned=344` von `channels=2764`, `programme_hits=0`, `name_hits=0`, `now_count=20`. Das sind **Teilstände**, kein abgeschlossener Katalogdurchlauf.
- **Keine** `EPG_FINAL`-Entscheidung in diesem abgegrenzten Abschnitt nachgewiesen. `programme_hits=0` ist dort **kein** Beweis für defekten finalen Matcher; ebenso ist ein `SEARCH_RESULT_READY`-Event nur ein UI-Batch-Commit und kein Beweis für einen auswählbaren Titel-Treffer.
- Vor-.31 gemeldete elf Sendernamen-Treffer dürfen nicht als .32-Programmtitel-Treffer gewertet werden.

## 4. Präziser Codex-Folgeauftrag für einen kumulativen Suchfix

### A. P0 – EPG-Window-Handoff/Busy-Gate nachweisbar richtig behandeln
1. In **`search_navigation.released()`** nicht einfach pauschal `System.HasActiveModalDialog` als alleinige Blockerquelle verwenden. **Differenziere den genauen nativen Dialogtyp/ID und tatsächlichen Window-Owner**: Kodi-interner `10138 BusyDialog` vs. Keyboard/eigenes Guide-Modal/fremde User-Dialogs. Halte Session-/Owner-Identität, Fokus, `getCurrentWindowId`, `getCurrentWindowDialogId` und Modal-Status vor/nach Guide-Schluss und vor Abbruch fest.
2. **Ende der Kodi-Callback-/GUI-Busy-Phase** sauber sicherstellen: ein **event-/owner-gesteuerter Handoff**, der keine Freigabe in derselben blockierenden Python-Ausführung fordert, wenn dadurch der Busy-Dialog nicht aufgelöst werden kann. Kodi-Action/DIALOG_LOCK-Verträge respektieren; Zeitpunkt `GUIDE_CLOSED`, `WAIT_RELEASE`, Busy offen/geschlossen, `RELEASE_READY`, `SEARCH_OPEN`, `SEARCH_GUI_READY` korrelieren.
3. Bei echtem fremden Modal, abgebrochenem Keyboard, gestoppter Kodi-Session oder Timeout **sicher nicht öffnen**, Fokus/Guide-Zustand wiederherstellen und einen datensparsamen `BLOCK_REASON` loggen; nicht durch gewaltsames Schließen von Kodi-/Fremddialogen „reparieren“.
4. Reproduziere den jetzigen Dreifach-Fall in Hosttests mit **`window=10025`, `dialog=10138`**, denn genau dieses Busy-Gate wird bisher von den 1.068 grünen Unit-/CI-Tests nicht hinreichend als echte Android-UX abgebildet.

### B. P1 – Medien-Suche / Fokus
5. Native Suchoberfläche öffnet sich nach Keyboard-OK direkt im richtigen Tab und bleibt bedienbar. Diagnose `Control 120 can't focus` auf konkrete `setFocusId`-/XML-Navigation-/Mode-Wechsel und Suchresultat-Neurendern herunterbrechen. Focus nur für **sichtbare und enabled Controls**; keine synthetische Fokus-Schleife im Worker.
6. `SEARCH_RESULT_READY`-Partial-/Final-Frames, `_valid_focus`, Back und erlaubten Treffer-OK auf echtem Android testen. Keine ungetestete Regel, dass jetzt jeder Sender-/Programmtitel in Datenbank gefunden sein muss. Zunächst **sichtbares, fokussierbares Fenster**.
7. Geringe CPU-/GUI-Last: inkrementelle Worker-Frames, gen/session-bindende UI-Callbacks, kein synchroner Vollscan/HTTP/SQLite im IR-Callback.

### C. Sicherer Liefer- und Testprozess
8. Nur ein **neuer kleiner Draft-PR kumulativ ab aktueller `main`-Version .32** (nächste freie Version prüfen, normalerweise .33); keine parallelen Altbranches, kein Downgrade, keine Deinstallation, keine Profile-/Portal-/EPG-/Favoriten-/Autoplay-/Artwork-Verluste. Filme/Serien, originale App-Icons, Live-Overlays erhalten. **Downloads und Recorder bleiben zurückgestellt.**
9. Automatentests: Dreifach-`RELEASE_TIMEOUT`-Fixture, Kodi-Busy vs. echte fremde Modals, langsame Freigabe, Guide-Restore, negatives/positives Handle, native GUI-Ready, Medien-Fokus 120/312, sichtbare Trefferliste, Session-/Back-/Dedupe; bisherige Regression unverändert. ZIP+SHA256 und nachvollziehbare anonyme Phasendiagnose.
10. **Android-Gate zunächst ausschließlich drei kurze Kernprüfungen:** aus großem EPG laufende Sendung suchen, Sendername suchen, Suche/Back mit Fokus im Medienbereich. Erweitertes NAVSEARCH/REG erst, **wenn diese drei PASS sind**. Keine 17-fache Fehlermatrix / kein Vierstundentest wiederholen. Status bis zur realen Android-Bestätigung **NOT_TESTED**.
11. **Kein selbstständiger Merge/Release / keine Schließung von #140**, bevor Nutzer Abnahme und Freigabe erteilt. Frühere .31 (9 PASS/8 FAIL/3 NOT_TESTED) und .32 (7 PASS/10 FAIL) unverändert dokumentiert.

**Kurzfazit:** Die neue `.32`-Evidenz ist wesentlich stärker als die alte `.31`-Handoff-Hypothese: Das Guide-Fenster wurde tatsächlich geschlossen, aber Kodi meldete an jedem RELEASE_TIMEOUT die eigene Busy-Dialog-ID **10138**, die das aktuelle `System.HasActiveModalDialog`-Gate blockieren kann. Medien-Suche erreicht GUI_READY, jedoch treten native Fokusfehler und nur partielle EPG-Trefferstände auf. **Erst Busy-/GUI-/Fokus-Handoff nachweislich reparieren, dann Matching und Komfortfunktionen testen.**
