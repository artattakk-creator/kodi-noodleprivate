# XCMate – 0.1.29.33 Android-Logforensik und verbindlicher Codex-Folgeauftrag

**Stand:** 24.10.2026, Kodi 21.2 Omega / Android TV 13 RK3528 ARM32 / Titan BINGIE MOD 2.2.3, IR-Remote.  
**Produktiver main-Stand bei Prüfung:** `plugin.video.xtreammate` 0.1.29.33, kumulativ aus [PR #156](https://github.com/artattakk-creator/kodi-noodleprivate/pull/156).  
**Reale .33-Nutzerabnahme:** [11 PASS / 3 FAIL / 1 NOT_TESTED](ANDROID_ABNAHME_02933_20261024_NUTZERERGEBNISSE_DE.md). Suche aus EPG A1 FAIL, Sendername/Guide-Start A2 FAIL, Medien-Suche A3 PASS; SEARCHUI-05 Poster-Retry FAIL, SEARCHUI-01 Live-Senderlogo/Jetzt-Programm NOT_TESTED. **Kein Release-/Suchabschluss.**

## 1. Private Logquellen und harte Versionsabgrenzung

**Keine vollständigen Kodi-Rohlogs auf GitHub hochladen.** Die Nutzereingaben umfassen:
- `kodi.old(9).log`: **30.692 Zeilen**, 24.10.2026 **08:43–12:42** Uhr. Bereits **.28**, Installation **.29 um 09:15:08**. **Keine .33-Events** und keine `SEARCH_NAV`-Events: ausschließlich historische Vergleichsbasis.
- `kodi(20261024-201342).log`: **9.080 Zeilen**, 24.10.2026 **12:42–22:13** Uhr. XCMate-Installationen: **.30 12:45:14 / .31 16:10:46 / .32 18:26:13 / .33 21:49:16** (private Originalzeile **7987**). **Für die .33-Bewertung ausschließlich ab Zeile 7987.**
- Zeitpunkte sind **Geräte-Logzeit**, keine auf GitHub zu übernehmenden Logdateiausschnitte. Kein Konto, Passwort, vollständiger Provider-/SMB-/Artwork-URI, Suchbegriff oder personenbezogener Film-/Stream-ID darf in Commits, Issues, PRs, Test-Logs erscheinen. Die Quelle kann vertrauliche Adressen/Tokens enthalten; deshalb nur **statische Ereignis-Codes, Zeitstempel, Window-/Dialog-IDs und Zählwerte** übertragen.

Die alte [.32-Logforensik](LOGFORENSIK_02932_20261024_KODI_BUSY_DIALOG_DE.md) diagnostizierte BusyDialog-Timeouts. Die **neuen .33-Gerätetraces beweisen**, dass die geänderte asynchrone Fortsetzung das Problem **in zwei echten Android-Tests noch nicht löst**.

## 2. P0 – EPG → Suche: nach .33-Busy-Deferral erneut reproduzierter Timeout

Beide Starts erfolgen im großen Grid-Guide bei `window=13006, dialog=9999`, `source=grid`. Der Guide wurde geschlossen und `getCurrentWindowId=10025`, aber Kodi setzte `getCurrentWindowDialogId=10138` (**Kodi BusyDialog**). Kein `SEARCH_OPEN source=grid`, kein `ASYNC_READY` in diesen beiden Sequenzen.

| ID | Start `INTENT` | Native Guide freigegeben | `BUSY_DEFERRED` / `ASYNC_QUEUED` | Reentrantes `WAIT_RELEASE` → `RELEASE_TIMEOUT` → `BLOCK_FOREIGN` | Private Logzeilen |
| --- | --- | --- | --- | --- | --- |
| **GSEARCH-1** | **22:02:31.704** | 22:02:32.100 | 22:02:32.330 / 22:02:32.384 | **22:02:40.565 → 22:02:42.651 → 22:02:42.949**, immer `window=10025,dialog=10138` | 8548–8585 |
| **GSEARCH-2** | **22:03:30.320** | 22:03:30.719 | 22:03:30.935 / 22:03:30.959 | **22:03:37.275 → 22:03:40.048 → 22:03:40.049**, immer `window=10025,dialog=10138` | 8620–8657 |

**Direkter Quellcodebezug in `.33`:**
- `resources/lib/search_navigation.py::released()`, Zeilen 93–107: bei BusyDialog wird nur bei **nicht asynchronem Owner** ein `BUSY_DEFERRED` erzeugt; in der späteren Owner-Fortsetzung wird weiterhin auf **kein `System.HasActiveModalDialog`** gewartet, dann nach 2 s abgebrochen.
- `resources/lib/search_navigation.py::guide_flow()`, Zeilen 110–150: schließt Guide und gibt bei Busy `SearchTransfer` zurück; `SEARCH_OPEN` wird **nie erreicht**.
- `resources/lib/search_handoff.py::schedule()`: asynchrone Fortsetzung durch `RunPlugin(plugin://plugin.video.xtreammate/?action=search_continue&token=...)`. `_ready()` verwendet wiederum `released(...)` und meldet bei dessen Timeout `BLOCK_FOREIGN`.
- Gleichzeitig erscheint für dieselbe Benutzerhandlung ein separater **`root`-Add-on-Dispatch und ein `OTHER`-/`search_continue`-Aufruf**. Beispiel 22:03:32–22:03:40: zwei parallele `BOOT ENTRY`, Hauptmenü lädt, während der Continuation-Owner auf Freigabe wartet. **Das ist eine zeitliche Korrelation; ob der root-/directory-Callback die BusyDialog-Lebensdauer verursacht, ist zu beweisen.**

**Nicht zulässig:** BusyDialog `10138` blind ignorieren, `System.HasActiveModalDialog` global aushebeln, beliebige fremde Modal-Dialoge schließen, unkontrolliert `ActivateWindow(Home)`/Kodi-Builtin-Aufrufe schichten oder nur den 2-s-Timeout hochsetzen. Der bisherige asynchrone `RunPlugin`-Transfer ist bei diesen Android-Tests **funktional nicht ausreichend** und darf nicht als erfolgreicher Fix gelten.

**P0-Codex-Plan:**
1. Den **tatsächlichen Kodi-Owner-/Busy-/Directory-Lifecycle** um Guide-Schließen und `search_continue` asynchron **ohne sensibles Payload-Logging** instrumentieren. `root`-Dispatch, `Container.IsUpdating`, `getCurrentWindowId`, `getCurrentWindowDialogId`, Session-/Owner-/Token-Gültigkeit, `Monitor.abortRequested` mit **niedriger Logfrequenz** erfassen; keine Konto-/Querydaten. Wieso überlebt BusyDialog in Continuation 6–10 s und wird dann fälschlich als „fremdes Modal“ klassifiziert?
2. Hand-off so ändern, dass **weder Origin-Kodi-Callback noch Continuation bei Busy auf sich selbst warten**. Erst wenn Kodi das native Busy-/Window-Freigabeereignis tatsächlich aufgelöst hat, SearchWindow mit gültigem Input-Owner öffnen. Separaten Root-Dispatch beim Guide-Ende untersuchen, jedoch **kein** globaler Home-Bypass, keine parallele Owner-Übernahme, keine Timer-Versuche ohne Kodi-Kontext.
3. Fremde modale Dialoge, Keyboard-Cancel und echten Abbruch weiter sicher respektieren, mit eigenständigem `BLOCK_REASON=BUSY_REENTRANT|FOREIGN_MODAL|WINDOW_ACTIVE|SESSION_CHANGED|CONTAINER_CHANGED|ABORT` (nur fix kodierte Klassen). `ASYNC_READY` muss vor tatsächlichem `SEARCH_OPEN` **in echten Logs** erscheinen.
4. Mehrere schnell nacheinander gestartete EPG-Suchen: alte Session kann kein neueres Fenster öffnen oder Guide-Zustand überschreiben. Guide-Sender-/Zeit-/Gruppen-/Fokusposition beim Abbrechen und Zurück vollständig erhalten.

## 3. P0 – EPG → Senderstart: VIER `GUIDE_HANDOFF SKIPPED`, nicht nur subjektiver Home-Wechsel

Vier nach der `.33`-Installation protokollierte User-Aktionen:
- **21:57:11.337 `QUEUED` → 21:57:14.147 `SKIPPED`** (Zeilen 8167/8186)
- **21:57:42.623 `QUEUED` → 21:57:45.262 `SKIPPED`** (8221/8240)
- **21:58:09.913 `QUEUED` → 21:58:12.418 `SKIPPED`** (8275/8294)
- **21:58:30.257 `QUEUED` → 21:58:32.964 `SKIPPED`** (8328/8347)

In allen vier Fällen: Guide schließt `window=10025, dialog=9999`; zeitlich unmittelbar danach startet **`BOOT ROUTE action=root`** und das XCMate-Hauptmenü, während der `GUIDE_HANDOFF` auf den entscheidenden Sendestart wartet. Im jeweiligen Ablauf **kein `RESOLVER_REQUEST` / `DISPATCHED`** des Guides. **Dies erklärt den beobachteten Rücksprung zur App-Startseite wesentlich besser als ein allgemeines IPTV- oder Codecproblem.**

**Getrennt bestätigt:** Ein **normaler** Live-TV-Start erreicht `[XCMate][LIVE_EXIT] START_RESOLVER` um **21:58:59.086**, anschließend Kodi `VideoPlayer::OpenFile` ab 21:59; Benutzer-Smoke **S4 PASS**. Nicht Player und Decoder pauschal neu bauen.

**Code:** `guide_playback.py::_handoff` (Zeilen 27–56) hat mehrere Exit-Gates, die bisher **alle** als `stage=SKIPPED` enden: falsche/stale ID, Abort, `window`-/`System.HasActiveModalDialog`-Freigabe-Timeout (2s), `player_state`-Mismatch, Reader/get_by_id/Portaltyp/Kanal nicht gefunden, `LiveSession` geändert oder verdeckte Exception. **WELCHE Bedingung im konkreten Fall FALSE ergibt, ist wegen der groben bisherigen Trace-Daten noch offen.** Sichtbarer root-Dispatch ist **Korrelation, nicht bewiesene alleinige Ursache**.

**P0-Codex-Plan:**
1. **Jede `SKIPPED`-Exit-Stelle auf festen, datensparsamen `GUIDE_HANDOFF reason=...` abbilden**, z. B. `BUSY_TIMEOUT`, `WINDOW_STILL_ACTIVE`, `PLAYER_STATE_CHANGED`, `LIVE_SESSION_CHANGED`, `PORTAL_UNAVAILABLE`, `CHANNEL_UNAVAILABLE`, `OWNER_ABORT`, `EXCEPTION_CLASS`; keine `getPlayingFile()`-Rohinhalte, Streaming-URLs, Provider- oder Sendernamen.
2. Den **2-s-Gate vs. root-Busy-/Kodi-Callback** durch identische Session-Korrelation mit vor/nach `window`, `dialog`, `player_state`, `LiveSession`, `Container.IsUpdating` untersuchen; weder blindes Warten noch direktes PlayMedia im WindowXML-Callback.
3. Gezielt gegen Kodi 21.2 Android nachstellen: ein Sender aus großem EPG starten, **ein** `RESOLVER_REQUEST → DISPATCHED`, PlayerVideo bzw. nachvollziehbarer Streamfehler; nie bloß Home. Ein zweiter Start nach Back/Guide-Reopen genauso. Fall „bereits anderer Player aktiv“ sicher nicht überschreiben.
4. Historische [EPG-Playback-Issues #121](https://github.com/artattakk-creator/kodi-noodleprivate/issues/121) / #89 als **alte Ursachen-/Regressionstests** lesen, **nicht** mangels .33-Trace identisch erklären oder ungefragt wiedereröffnen.

## 4. Positive und sekundäre .33-Befunde: Mediensuche, EPG-Partialstände, Bilder

### Mediensuche: tatsächlicher Lauf mit fokussierbarer Oberfläche

- `source=media` **`SEARCH_OPEN` dreimal** nach `.33`: **22:04:44.559**, **22:07:03.750**, **22:08:09.551** (Zeilen 8698/8821/8872).
- `SEARCH_INPUT_ACCEPTED` und `SEARCH_GUI_READY` ebenfalls je **3**; **82 `SEARCH_RESULT_READY`-Events** im `.33`-Abschnitt. `[XCMate][FOCUS]` 26 feste Meldungen, Zielcontrols 400/700/701/702 mit `semantic=1, visible=1, enabled=1`; keine erneute `Control 120 can't focus`-Meldung in diesem abgegrenzten `.33`-Abschnitt.
- **Geräte-Gates A3, SEARCHUI-02/03/04/06 PASS** laut Nutzer: **bewährte Medienroute und Poster-/Fokusergebnisse schützen**, nicht gleichzeitig umgestalten. `SEARCH_RESULT_READY` steht nur für Ergebnis-Commit, nicht für endgültige Programmtitelsuche.

### EPG-Scan in der Mediensuche: nur Teilstände

In `.33` enthält der Log **84 `[XCMate][SEARCH_EPG]`-Einträge**, alle `EPG_PARTIAL`, auf 3 Mediensuch-Sessions. Sichtbar jeweils `channels=2764`, mit **maximal 641 / 135 / 230 bereits gescannten Kanälen**, `programme_hits=0` im jeweils sichtbaren Teilstand. Die dritte Session hat `name_hits=1`, aber weiterhin `programme_hits=0`. **Keine abschließende `EPG_FINAL`-Meldung**. Die Werte beweisen **weder funktionierendes noch kaputtes finales Programmtitel-Matching**; sie lassen sich nicht mit den blockierten EPG-Einstiegen gleichsetzen. Der Matcher ist erst nach stabilem Fenster-Handoff sinnvoll abzunehmen. Für künftigen Test: finaler Scanstatus mit Abbruch-/Session-Grund und Trefferklasse, kein personenbezogener Querytext.

### Filmcover-Retry/Timeout: Nutzer-Fail, aber kein aussagekräftiger .33-Artwork-Trace

- Nutzer-Test **SEARCHUI-05 FAIL**: „Poster neu laden“ für fehlendes Filmcover ergibt sichtbare **Zeitüberschreitung**, Poster bleibt leer. Auf 22:09:31 ist im Log nur `DETAIL_MENU ACTION_SELECTED` (allgemeine Aktion, **keine sichere Zuordnung** zu exakt diesem Posterbutton); **keine dedizierte Artwork-/TMDb-/Retry-Fehlersequenz** belegt. Nicht als HTTP-Timeout oder TMDb-API-Ausfall behaupten.
- `media_art.py::poster_candidates(item)` zieht vorhandene `cover`, `stream_icon`, `movie_image`, `cover_big`. `retry_poster()` wählt nur aus **diesen vorhandenen Quellen**, `art_store.retry_one` setzt begrenzten Retry. **Keine TMDb-Nachsuche innerhalb dieses konkreten Buttons**; ein anderswo existierendes Metadaten-Enrichment ist separat zu prüfen.
- **Codex-Aufgabe #111:** je einem fehlenden Filmcover sichere `ART_RETRY`-/`ART_NETWORK`-Phasen mit `SOURCE_CLASS`, `TIMEOUT_STAGE`, Statusklasse (DNS/TLS/4xx/429/5xx/network/cancel/queue-limit), Backoff, getroffenen/fehlenden TMDb-Fallbackpfad, Session-/Cache-Refresh und korrekter Werkidentität (Typ/Titel/Jahr, ohne sensiblen Text im öffentlichen Log) protokollieren. Kein Cache-/Artwork-Vollreset, keine READY-Bilder löschen; TMDb-Schlüssel/Terms of Use befolgen. [#151](https://github.com/artattakk-creator/kodi-noodleprivate/issues/151) manuelle Bildsuche bleibt eigener Folgeauftrag.
- Kodi protokolliert nach der `.33`-Installation **vier 404-Schecks anderer Kodi-Repositories**; diese sind **kein** Beleg für XCMate-Posterprovider-Ausfall. Weitere Kodi-MediaCodec-Timeout-/Release-Warnungen um ca. 22:00–22:01 gehören in einen separaten Playback-Stabilitäts-Bucket, nicht als EPG-Handoff-Ursache deklarieren; **S4 PASS** bleibt erhalten.

### Systemlast: beobachten, keine voreilige OOM-Diagnose

22 `[XCMate][STABILITY]`-Samples nach .33: `rss_kib` ca. **1.137.596–1.202.636 KiB**, `os_threads` **114–130**, `pressure=false`, `portal_oom=0`, `portal_disk_reads=1`. Ein Bild-/RAM-Freeze ist daraus **nicht** bewiesen; auf dem ARM32-Gerät Speicherdruck und Worker-/Queue-Zahlen für längere Sessions weiterhin beobachten, ohne Thread-/Prozesszählung und RSS mit einem nachgewiesenen Leak gleichzusetzen.

## 5. Verbindliche Entwicklungsreihenfolge nach .33

**Priorität A: eng begrenzter P0/P1-Hotfix** für *beide* aktuell eindeutig blockierten Guide-Handoffs (#140):
1. **EPG→„Jetzt Sender ansehen“** und **EPG→globale Suche** unabhängig nachstellen, Zeit/Session/Owner mit unverwechselbaren, **nicht sensiblen** Phasencodes korrelieren. **Neue Tests der tatsächlichen BusyDialog-10138-Konstellation inklusive gleichzeitigem root-Directory-Dispatch** in Kodi-21-Hostmock; echte fremde Modals und andere laufende Player schützen.
2. Kleine robuste Handoff-Korrektur auf dann aktueller `main`-Basis **0.1.29.33** (nächste freie Version prüfen, voraussichtlich `0.1.29.34`), kein Revert/Downgrade. **Kein** generischer Player-/Artwork-/Skin-Umbau und keine globalen Keymap-Änderungen.
3. Zwei bis vier Android-Mini-Gates zuerst: **G1** Sender im großen EPG per „Jetzt Sender ansehen“ starten (mindestens zwei Versuche nach erneuter Guide-Öffnung), genau eine Wiedergabe; **G2** aktuelle Sendung im großen Guide suchen, `ASYNC_READY` + `SEARCH_OPEN` ohne `RELEASE_TIMEOUT`; **G3** passende echte Programmtitel-Ergebnisse vor Back und korrekte Auswahl; **G4** Filme-/Seriensuche, Poster/Fokus/Back-Regression weiterhin PASS. Alle zunächst **NOT_TESTED**.
4. Nur wenn G1–G4 auf Android PASS, restliche NAVSEARCH/SEARCHUI einschließlich **SEARCHUI-01 Senderlogo/Jetzt** durchführen. Bisherige .33-Werte erhalten.

**Priorität B: separater Poster-Timeout-/Fallback-Draft** (#111; fachliche Abhängigkeit #151):
5. Belege tatsächlichen Button→ArtStore→Provider→optionalen zulässigen TMDb-Fallback mit sicheren Diagnostics, lokalen Caches, selektivem Retry/Backoff und aktuellen Postern, **ohne** gespeicherte Originalbilder/Portale/Favoriten zu löschen.
6. Android-Mini-Gates **P1** zuvor fehlendes Poster nach gezieltem Retry **oder** eindeutige, verständliche permanente Fehlerdiagnose; **P2** anderer bereits vorhandener Film-/Seriencover bleibt nach Neustart unverändert; **P3** (nur bei implementiertem TMDb-Fallback) korrektes Film-/Serienwerk und Jahr ohne falsche Datenübernahme. **NOT_TESTED** bis echtes Gerät.

**Priorität C: Featureentwicklung nach stabiler Kernfunktion:**
7. [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98): EPG-Quelle und Kanal **direkt im großen Guide auswählen**, Vorschau nur read-only, eindeutiger Composite-Key, explizites Speichern/Abbrechen – bereits in [separatem Codex-Auftrag](CODEX_UEBERGABE_EPG_ZUWEISEN_IM_GUIDE_20261024_DE.md) dokumentiert. Noch **nicht** in diesem Hotfix, keine Verwechslung mit #140.
8. Weitere Space-Premium-/Design- oder Player-Extras **nach** Abschluss der Gate-Blocker; Downloads/Recorder weiterhin als letzte Roadmap-Themen.

## 6. Liefervertrag an Codex

- **Neuer eigenständiger Draft-PR** von der aktuell freigegebenen `main`-Version **.33** aus; kumulativ und ohne unbekannte Änderungen aus alten Drafts. Falls Version zwischenzeitlich weitergewandert ist, **nicht** .34 blind erzwingen, sondern nächstmögliche Version auf aktueller main prüfen.
- ZIP+SHA256, geänderte Dateiübersicht, reproduzierbare Hosttests für die tatsächlich beobachteten Handoff-Reasons, Rückkehr zu EPG-Gruppen-/Zeitposition, Single-dispatch, LiveSession-/Player-Schutz und optional fokussierte Artworktests. Ein 1.000+-Hosttest-PASS ersetzt **keinen realen Android-Nachweis**.
- **Kein eigenmächtiger Merge, Kodi-Repository-Publishing, Release, Reset, Deinstallation oder Downgrade.** Bei der nächsten Installation nur normal über das bestehende GS-Media-Repository aktualisieren, nachdem Nutzer Merge freigegeben hat.
- Bestehende Original-App-Icon, Space-Premium-Vorarbeiten, Portal-/Favourites-/EPG-XMLTV-/manuelle Zuordnung, große EPG-Bedienung, Live-Remote-Overlays, Filme/Serien, Autoplay, Resume und Artwork-/SQLite-Daten erhalten.
- **Rohlogs bleiben nur in diesem privaten Chat / lokaler Diagnose**. In öffentlichem PR/Issue/Doku keine vollständigen Links, Geheimnisse, Stream-/SMB-Pfade, Nutzerkennungen oder privaten Suchbegriffe.
- **Issues #140, #127, #111, #143 OPEN**, bis jeweils reale, vollständige Android-Abnahme und ausdrückliche Freigabe erfolgt. Historische Abnahmen `.31` 9/8/3, `.32` 7/10/0, `.33` **11 PASS / 3 FAIL / 1 NOT_TESTED** unverändert.

**Technischer Kern:** Die neue `.33` verschiebt den Such-Callback, aber beendet den Kodi-Busy-/Window-Lifecycle offenbar nicht zuverlässig; der Continuation-Owner läuft erneut in denselben Dialog und klassifiziert `10138` als `BLOCK_FOREIGN`. Parallel überspringt `guide_playback._handoff` vier Senderstarts **vor** `RESOLVER_REQUEST`, während normales Live-TV funktioniert. Genau diese beiden, im Android-Gerätelog dokumentierten Übergaben sollen jetzt mit eindeutigen Reasons und sicheren Kodi-native Lifecycle-Tests robust behoben werden; Medien-Suche/Poster-UI nicht regressieren.
