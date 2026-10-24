# XCMate – Verbindliche Codex-Projektübergabe: Kodi-Logforensik und Reparatur der EPG-/Sendersuche
**Stand:** 24.10.2026  
**Status:** Dokumentation / Entwicklung noch offen / Android-Q1–Q3 FAIL  
**Produkt:** GS Media XCMate, Kodi-Addon `plugin.video.xtreammate`  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Aktueller freigegebener Code:** `main`, XCMate **0.1.29.31**, [kumulativer Merge-PR #154](https://github.com/artattakk-creator/kodi-noodleprivate/pull/154).  
**Zielgerät:** Kodi **21.2 Omega**, Android TV **13**, Rockchip **RK3528 ARM32**, Titan **BINGIE MOD 2.2.3**, IR-Fernbedienung, 1920×1080.  
**Primäre Issues:** [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140) (EPG-/Sendersuche), [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143) (Master-Roadmap). Sekundär [#136](https://github.com/artattakk-creator/kodi-noodleprivate/issues/136) (USB/SMB), [#135](https://github.com/artattakk-creator/kodi-noodleprivate/issues/135) (Redirect), [#63](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63) (VOD-Download).

> **Kernentscheidung:** Zunächst **gezielter, kleiner P1-Fix für #140**. Danach die übrigen EPG-, Artwork-/Cover-, Player-OSD-, Icon-Rail- und Wizard-Themen aus #143. **Download und Live-TV-Aufnahmen ans Roadmap-Ende**. Keine Neuimplementierung von Download/Recorder in diesem Auftrag. Ohne neuen Geräte-PASS kein Issue schließen.

## 0. Tatsächliche Test-Baseline und Datenschutz

- Android-Test auf 0.1.29.31: **9 PASS / 8 FAIL / 3 NOT_TESTED** aus 20 Checkbox-Tests, siehe [tatsächlicher Nutzerbericht](ANDROID_ABNAHME_02931_20261024_NUTZERERGEBNISSE_DE.md). **V0/S1–S5 PASS; Q1/Q2/Q3 FAIL; Z1/Z2-USB/Z2-SMB PASS; D1/D2/D3-EU NOT_TESTED; D3-FU/D3-FS/D3-ES/D4/D5 FAIL**.
- Historische Android-0.1.29.30-Werte bleiben unverändert **12 PASS / 15 FAIL / 1 BLOCKED / 1 NOT_TESTED**. MEM1 (vier Stunden) und MEM2 (Service/Neustart) wurden zuvor bestanden; nicht pauschal vollständig wiederholen.
- Host-CI von [PR #154](https://github.com/artattakk-creator/kodi-noodleprivate/pull/154): **1.047 automatisierte Tests bestanden**. Diese Host-Tests haben die realen Android-Fenster-/IR-Fehler **nicht** ausgeschlossen.
- Grundlage dieser Forensik sind **zwei vom Nutzer privat überlassene Kodi-Logs**: `kodi.old(7).log` (ca. 08:43–12:42; .28/.29) und `kodi(20261024-152104).log` (ca. 12:42–17:20; .29/.30/.31). Insgesamt **35.228 Logzeilen**. **Die Original-Logs nicht nach GitHub hochladen**: sie enthalten potenziell private Provider-/Serveradressen und andere sensible Kontexte. Die hier verwendeten Zeilennummern beziehen sich auf die privaten Originaldateien und sind allein als gezielte, überprüfbare Fundstellen dokumentiert.
- **Versionsgrenze:** In der neueren Logdatei ab **Zeile 3193, 16:10:46** Installation der Version `0.1.29.31` bestätigt; frühere Ereignisse sind **nicht** auf .31 übertragbar. Dies gilt ausdrücklich für das frühe `EPG_PARTIAL` und die drei Download-Redirect-Denials.

## 1. Höchste Priorität: EPG- und Sendersuche (#140)

### 1.1 Auf Android reproduzierter Nutzerfehler – alle drei Delta-Gates FAIL
- **Q1 / laufende Sendung suchen:** Nach Suche aus dem großen EPG erscheint eine **schwarze, leere Kodi-artige Verzeichnisansicht** mit drei schwarzen Punkten und einem roten Balken statt der nativen XCMate-Ergebnisse.
- **Q2 / Sender suchen:** Es erscheint die **XCMate-Startseite ohne App-Icon und ohne Hintergrundgrafik**, statt der interaktiven Trefferansicht.
- **Q3 / Suchergebnis, erneute Suche, Back:** **Erst beim Verlassen/Zurückgehen** tauchen nachträglich **„Live TV 11 Treffer, Filme 0 Treffer, Serien 0 Treffer“** auf; diese sind nicht normal auswählbar. `11` belegt **keinen** aktuellen Sendungstitel-Match und `0` in Film/Serien keine separate Funktionsstörung ohne passende Suchphrase.

### 1.2 Konkrete Logevidenz (das ist belegt)
**Vor .31** in `kodi(20261024-152104).log`, **Zeile 864, 12:49:16**:
```text
[XCMate][SEARCH_EPG] ... code=EPG_PARTIAL ... channels=2764 ... now_count=192 ... name_hits=11 ... programme_hits=0
```
- Für diese vor-.31-Anfrage lieferte der alte Code **nur 11 Sendernamen-Matches, null Matches gegen laufende Sendungstitel**; bestehende EPG-Daten waren teilweise vorhanden. Kein Beweis über das .31-Programm-Matching.
- **Zeilen 857–859, 867:** Native `SEARCH_INPUT_ACCEPTED → SEARCH_GUI_READY → SEARCH_RESULT_READY` waren **vor .31** schon tatsächlich erreichbar. `GUIDE_HANDOFF QUEUED` und spätere Player-Aktionen müssen zeitlich getrennt und mit Nutzerabsicht abgeglichen werden.

**Ab .31**, **Zeile 3193 (16:10:46) und danach**, dieselbe Logdatei:
| Fundstelle | Ereignis | Relevanz |
| --- | --- | --- |
| Zeile **3854**, 17:02:43 | `ROUTE action=xcmate_home` | Home-Container wird gestartet |
| Zeile **3861**, 17:02:43 | `ROUTE action=global_search` | Suchroute zeitgleich mit Home |
| Zeilen **3878–3879** | `DIRECTORY_DONE / DISPATCH_DONE` für Such-Dispatch | **Kodi-Directory-Route** statt nachgewiesener nativer SearchWindow-Initialisierung |
| Zeilen **3941 / 3949**, 17:04:02 | erneutes Home/Search-Überlappen | Wiederholbarer Ablauf |
| Zeile **4176**, 17:10:28 | erneuter `global_search`-Dispatch | Dritter Suchaufruf |
| Gesamter `.31`-Abschnitt | **keine** `[XCMate][SEARCH] SEARCH_INPUT_ACCEPTED / SEARCH_GUI_READY / SEARCH_RESULT_READY` | Native SearchWindow-Pipeline in diesen Logs **nicht** belegt |

**Interpretation:** Im realen Fehlerfall läuft `global_search` als Kodi-Verzeichnisaktion. Zeitlich überlagerte `xcmate_home`-Navigation und ein zu später Ergebnisbildschirm passen zu einem **Window-/Directory-/Ownership-Race**. Dies ist eine **starke, durch Code und Logs begründete Arbeitshypothese**, aber ohne erfassten `router._handle` und vollständige GUI-Kausalspur noch kein vollständig bewiesener einzelner Race-Ablauf.

### 1.3 Entsprechende Quellcodestellen auf `main` (direkt geprüft)

`src/plugin.video.xtreammate/resources/lib/guide_window.py`, **Zeilen 166–170**:
```python
if key == 117:
    query = xbmcgui.Dialog().input(tr(32534))
    if query.strip():
        self.close()
        xbmc.executebuiltin(
            'Container.Update(' + self.router.url(
                action='global_search', pid=self.portal['id'], q=query[:200]
            ) + ')'
        )
```
(Darstellung der tatsächlich relevanten Statements, Formatierung geglättet.)

`src/plugin.video.xtreammate/resources/lib/app_routes.py`, **Zeilen 169–174**:
```python
elif action == 'global_search' and router._handle < 0:
    from media_window import open_search
    from media_search import handoff
    from window_navigation import open_route
    open_route(router,portal,lambda:open_search(router,portal,router._params.get('q')),after_close=handoff)
elif action in ('global_search','search_section'):
    search(router,portal)
```
- Das zweite `search(router,portal)` in **app_routes.py Zeilen 202–250** ist eine **andere, ältere Kodi-Directory-Suche**; nutzt `xbmcplugin.setContent(...,'files')`, `_end(router)` und bei fehlender Query einen weiteren `Container.Update(global_search)`-Aufruf.
- `src/plugin.video.xtreammate/resources/lib/window_navigation.py` `_anchor_home` (ca. **Zeilen 70–92**) hat selbst `Container.Update(xcmate_home,replace)` / `ActivateWindow(Videos,...,return)`, einen 5-s-Home-Ready-Check und einen eigenen Window-Owner-/Lockmechanismus.
- `media_search.py::SearchMixin._open_search` (**45 ff.**) sowie `_search_ready` (**80 ff.**) bieten die **eigentliche native Suchoberfläche** mit `[XCMate][SEARCH]`-Traces, Tabs 700–702, Trefferliste 710, asynchronem Worker und gerichtetem Fokus. Diese existierende Funktion **wiederverwenden** statt eine dritte Suche zu erstellen.
- `media_window.py::open_search` (**1042 ff.**) öffnet `SearchWindow` über `open_owned_window`, und `media_window.py::setFocusId / _resume_focus` enthält bereits deferrierte Fokuslogik. Nicht pauschal ersetzen.
- **Änderungsziel:** Kodi-Verzeichnissuche und native XCMate-Suche klar separieren, und sämtliche **interaktiven** Suchen (großer EPG, XCMate-Home, ggf. Medien-Details) sicher in die **native** `SearchWindow` führen.

### 1.4 Verbindlicher Arbeitsauftrag an Codex (#140)

1. **Zuerst minimalen Trace ergänzen / reproduzierbare Sequenz:** Je Suchanforderung aus EPG/Home/Detail erfassen, welcher Einstieg ausgeführt wird, ob `router._handle` ein **Directory-Handle (>=0)** oder **Action-Handle (<0)** ist, wann Guide/Dialog geschlossen, Home-Anker gesetzt und SearchWindow tatsächlich initialisiert ist; WindowId/DialogId, Search-Session-ID, Owner-Status, Fokus-ID und Dispatch-Phasen protokollieren. **Keine Query-Strings, Provider-Namen, URLs, Tokens, IDs oder Dateipfade** loggen.
2. **EPG-Handoff deterministisch machen:** `guide_window.py` darf **nicht** nach einfachem `self.close()` unkontrolliert per `Container.Update(global_search)` ins Kodi-Directory wechseln. Native SearchWindow-Öffnung erst **geordnet nach Freigabe des Guide-Owners / Modal-Fensters**, über vorhandene `owner_dispatch`-/`window_navigation`-Contracts. Keine gleichzeitigen Home-/Search-Window-Updates, keine zusätzliche globale Keymap.
3. **Handle-abhängige Legacy-Falle entschärfen:** Ein interaktiver `global_search`-Intent muss **auch bei einem zuvor positiven Kodi-Directory-Handle** sicher und bewusst an den nativen Window-Owner übergeben werden. Legacy-Such-URLs/Widgets dürfen weiter funktionieren, aber **nicht** versehentlich die native Suche ersetzen. Keine rekursive `Container.Update`-Kette.
4. **Treffer vollständig nutzbar machen:** Suche bleibt nach Keyboard-OK sichtbar; Tabs zeigen Partial-/Final-Status, die Trefferliste ist mit IR fokussierbar; erst bewusste Auswahl per OK startet Sender. `onAction` und `onClick` sauber deduplizieren; nach Back erwarteter EPG-/Home-/Detail-Kontext statt leerem Directory oder grafisch entkleideter XCMate-Startseite. Kein Playback ohne bewusste Auswahl.
5. **Danach erst Matching prüfen:** Wenn native GUI nachweislich funktioniert, Jetzt-Sendungstitel, Name, manuelle EPG-Zuordnung, Quellfallback und Short-Now-Cache gegen denselben großen EPG prüfen. `EPG_PARTIAL` und frühere `programme_hits=0` sind **vor-.31** beobachtet, nicht als repariert oder als aktueller .31-Root-Cause voraussetzen. Keine Datenbank-/EPG-Mappings zurücksetzen.
6. **Performance:** Keine synchrone 2.764-Sender-/SQLite-Komplettsuche auf Kodi-GUI-/IR-Thread. Vorhandenen inkrementellen Worker in `search_data.py` respektieren, Partial-/Final-Frames ohne Fensterwechsel zeigen, abgebrochene/neu gestartete Suchläufe generation-/session-bound machen; alte Callback-Ergebnisse dürfen nie eine neue oder geschlossene GUI neu befüllen.
7. **Fokus-Contract:** Nur sichtbare und enabled Controls fokussieren, `_valid_focus` und Kodi-Lag beachten; keine permanenten Focus-Retry-Schleifen und kein unbeabsichtigtes Kodi-OSD/Home. Auf RK3528 ARM32 mit Titan BINGIE MOD und Estuary testen.
8. **Kompatibilität:** Keine Änderungen an Original-XCMate-Icon, Space-Premium-Core/Artwork, Play/Pause/Live-TV, Staffel-Autoplay, Favoriten, Portalen, EPG-Mappings, Cache, Hintergrunddienst, Serien-Resume, Downloads/Recorder oder Repository-Konfiguration; keine Deinstallation/Downgrade/Profil-Reset. Fix **kumulativ auf dann freigegebenem `main` ab .31** entwickeln.

### 1.5 Automatisierte und reale Abnahmetests

| ID | Prüffall | Bestanden ausschließlich wenn … |
| --- | --- | --- |
| **NAVSEARCH-01 / Q1** | EPG: laufenden echten **Sendungstitel** suchen | Die **native** XCMate-Suche erscheint direkt, ohne schwarzen Kodi-Ordner/Home-Wechsel; nach Ergebnisabschluss echter Programmtreffer sichtbar |
| **NAVSEARCH-02 / Q2** | EPG: **Sendername** suchen | Treffer noch **vor Back/Exit** in interaktiver Suche, mit vollständigem Scan-/+Status, korrekt mit IR wählbar |
| **NAVSEARCH-03 / Q3** | 0 Treffer, Wiederholung, leere Eingabe, Abbrechen | Keine falsche Kodi-Seite; Back sauber an EPG/Home; kein unfreiwilliger Playerstart |
| **NAVSEARCH-04** | Suche aus XCMate-Home und Medien-Detail | Dieselbe native SearchWindow-Route, keine Directory-Variante als Seitenwechsel; bestehende Medienfunktionen stabil |
| **NAVSEARCH-05** | 20 IR-Sequenzen (Enter/Down/Left/Right/Back, schnelle Doppelklicks) | Keine doppelten Aktionen, Ghost-Fokus, unbeabsichtigter Return/Start |
| **NAVSEARCH-06** | Langsame/verspätete Worker-Callbacks, mehrere Suchsessions | Alte Ergebnisse überschreiben niemals neue Suche, fokussierter Tab bleibt erhalten |
| **NAVSEARCH-07** | Positiver Directory-Handle und negativer Action-Handle, Guide/Home/Fremd-Context | Explizit korrekter Owner/Route; keine `Container.Update`-Rekursion |
| **NAVSEARCH-08** | EPG mit echter manual mapping + Short-Now/Mehrfachtreffer | Sender-/Programme-Treffer und Name-/EPG-Status konsistent, keine Datenverfälschung |
| **REG-01** | Live-TV OK/Down/Back, Sender-/Gruppenliste, Startsender | Bereits funktionierende Navigation unverändert |
| **REG-02** | Film-/Seriendetails, Resume, Serienautoplay, Originalicon, Theme | Vorherige PASS bleiben PASS |
| **REG-03** | Großer EPG, EPG-Fallback/Quellen, Favoriten, gespeicherte Profile | Keine Datenverluste / keine doppelte Navigationsschicht |

**Abnahme-Status vor neuem Gerätetest:** Alle neuen NAVSEARCH-/REG-Gates **NOT_TESTED**. Host-Unit-Tests ersetzen diese Android-IR-Prüfungen nicht. Das alte `.31`-Q1–Q3 bleibt historisch **FAIL**, auch wenn ein zukünftiges Update besteht.

## 2. Sekundäre GUI-/Player-Befunde – nicht mit #140 gleichsetzen

- `kodi(...).log` in der `.31`-Phase: wiederholt `Control 120 ... has been asked to focus, but it can't`, teils `Control 312`, in `WindowXML`-Fenstern 13000/13002/13003. Fundstellen u. a. **3558, 3705, 3786, 3926, 4264–4316**. Beleg für **zeitweise ungültiges oder noch nicht fokussierbares Control**, nicht automatisch ein direkter Beweis für die Q1–Q3-Root-Cause. Diagnostik: Visibility/Enabled, zulässige Fokusliste, `FOCUS_DEFER/FOCUS_READY`, Owner-Wechsel, Skin/Window-Init und Remote-Mapping.
- **17:19:46**, **Zeile 4407**: `EXCEPTION: Kodi is not playing any media file` kurz nach Playerende / bei Serien-Window-Reinit. Nur als **separaten** Guard-Audit aufnehmen (z. B. `isPlaying`/Player-Ownership vor Statuszugriff); exakter Stacktrace-Aufrufer ist **nicht** bekannt. Kein unbelegter Zusammenhang mit EPG-Suche.
- **16:10:44**, **Zeile 3183**: Beim Add-on-Aktualisieren wurde `service.py` nach fünf Sekunden von Kodi gekillt (`script didn't stop in 5 seconds - let's kill it`). Der Vorfall geschah **beim Wechsel auf .31**, nicht als später belegter stabiler Service-Crash. Nur Lifecycle-Nachprüfung, nicht automatisch das Hauptproblem.
- Hohe Portal-/Worker-Aufrufzahlen in `[XCMate][STABILITY]`, **kein bewiesener Memory-Leak**. Performance später getrennt profilieren; frühere 4-h-PASS nicht ohne neue Symptome widerrufen.
- Externe Kodi-Repositories/Skin/Trakt und einzelne `POParser`-Warnungen sind aus dem Log ersichtlich, aber **keine belegte Ursache** für die falschen Suchfenster. Keine Ablenkung des P1-Fixes.

## 3. Speicher-Diagnostik #136 – gesicherter Teilerfolg, bewusst nachrangig

**Belegte `.31`-Fundstellen im neueren Kodi-Log:**
| Zeitpunkt / Zeile | Ereignis | Bedeutung |
| --- | --- | --- |
| ca. 17:06:13–25, Zeilen 4020–4025 | `GetDirectory(/storage/) failed`, `TARGET_PERMISSION OPEN_DIRECTORY errno=13` | Zugriff auf **einen** Browser-/Zielpfad nicht erlaubt, keine generelle USB-Unfähigkeit |
| 17:07:00, Zeile 4048; 17:07:48, Zeile 4086 | `TARGET_ATOMIC_PUBLISH_UNAVAILABLE LINK errno=38` | Native no-overwrite Hardlink-Publikation auf diesem Ziel nicht unterstützt |
| 17:07:14–15, Zeilen 4052–4053 | `TARGET_BOUND/PERSIST_OK USB` | USB-Ziel sicher gebunden/gespeichert |
| 17:07:48, Zeilen 4090–4091 | `TARGET_TEST_BEGIN USB_STAGE`, `TARGET_TEST_DONE USB count=1792` | **1.792-Byte-USB-Kurztest PASS** |
| 17:08:46, Zeilen 4114–4115 | `TARGET_BOUND/PERSIST_OK SMB` | SMB-Ziel gebunden/gespeichert |
| 17:09:15–16, Zeilen 4148–4151 | `TARGET_TEST_BEGIN SMB2`, `TARGET_TEST_DONE SMB count=1792` | **1.792-Byte-SMB-Kurztest PASS** |

Damit sind USB-/SMB-Zielauswahl und kleine Schreib-/Leseprüfungen auf echter Hardware nachgewiesen. **Nicht** nachgewiesen: vollständiger Film/Episode, Staging für große Dateien, Integrität nach Netzwerkunterbrechung, Offlinewiedergabe, Aufnahmefähigkeit. **#136 OPEN/PARTIAL**. Zielproben-PASS erhalten, keine unnötigen Retests ohne neuen Anlass; größere Medien-Transferfixes erst am Roadmap-Ende.

## 4. Download-Sicherheit #135 / VOD #63 – älterer Blocker, keine neuen Freigaben

**Nur .30-Phase** des neueren Logs, **Zeilen 1366–1367, 1595–1596, 1704–1705** (12:56:35, 12:59:58, 13:06:19):
```text
DOWNLOAD_REDIRECT status_class=3xx hop=1 cross=1 scheme=http reason=REDIRECT_UNTRUSTED_TARGET
DOWNLOAD stage=FAILED bytes=0
```
- Gesichert: Cross-Origin-HTTP-Redirect wurde **vor Datentransfer** durch Sicherheits-Policy abgelehnt. **Keine** pauschale Freigabe, kein TLS-Downgrade, kein Ausschalten von DNS/SSRF-/Token-Grenzen.
- **Nach .31-Installation keine ausreichenden `DOWNLOAD_REDIRECT`-/`DOWNLOAD stage=FAILED`-Traces** zu den vom Nutzer als FAIL gemeldeten kompletten Medienjobs in den übergebenen Dateien. D1/D2/D3-EU **NOT_TESTED**. D3-FU/D3-FS/D3-ES/D4/D5 **FAIL** nach Nutzerbericht; ohne Ursache/Phasencode nicht spekulativ als denselben alten Redirect-Fehler deklarieren.
- **#135/#63 bleiben OPEN**, keine neuen Download-/Aufnahme-PRs in dieser UI-Phase.

## 5. Codex-Lieferumfang, Branch-/Releasepolitik und Reihenfolge

### Sofort nächster freizugebender Entwicklungszyklus – NUR #140
1. **Root-Cause-Nachweis** im Code und Repro-/Test-Fix für falsche EPG-/Home-/Detail-Search-Window-Routen; Legacy-Handle-Integration. Zuerst Fokus/Owner-/Window-Lifecycle, danach Programmtitel-Matching.
2. **Kleiner kumulativer Draft-PR** ab freigegebenem `main`, dokumentierter Diff, keine Seiteneffekte auf laufendes TV/Spieler/Speicher/Theme/Services. **Kein Merge, Tag, Release oder Repo-Index-Publish ohne erneute ausdrückliche Nutzerfreigabe**. Kein Rückfall auf .30/.29, keine Deinstallation, keine Profildatenlöschung.
3. Automatisierte **Unit-/Integrationstests** für Directory-/Action-Handle, Guide-Search, Home-Search, Event-Reihenfolge, Focus-Lag, Dedupe, asynchrones Resultat nach Close/Restart, EPG-Now-/Name-Hits, Suche ohne Treffer, Original-Branding/Autoplay-Regression.
4. Version **strictly cumulative**, erst nach Bestimmung der nächsten freien Version; üblicher Pfad `.31 → .32`, keine parallele inkompatible Entwicklung auf älterem Ausgangsstand. **Android-Test-ZIP + SHA256**, Changelog, zielgerichtete Abnahmecheckliste mit allen o. g. Gates, Status NOT_TESTED bis Nutzer am Gerät testet.
5. **Keine pauschale Vollmatrix / kein erneuter vierstündiger Test** ohne konkreten neuen Befund. Kurzer S1–S5-Smoke und gezielte Q1–Q3/NAVSEARCH/Regressionen genügen zunächst.
6. Dokumentation aller Ergebnisse auf GitHub, aber **nur redigierte Event-/Phasencodes**; nicht die beiden Rohlogs. Offene Issues erst bei vollständigem echten Android-Nachweis schließen.

### Nach dem Suchfix (neue Roadmap #143)
- #111/#151 Cover-/Metadatenquellen, #17/#100 Info-/Player-OSD, #94/#150 Icon-Rail mit lizenzierter Tabler-Offline-Iconserie, #98 EPG-Quellenwechsel, #123 EPG-Programmdetail, #99 providerseitiger Catch-up, #43 Wizard/Space Premium, übrige Qualität/UX.
- Bereits hinterlegter [Codex-Auftrag für Live-Info-Status und Player-OSD](CODEX_AUFTRAG_LIVE_TV_STREAMSTATUS_PLAYER_OSD_20261024_DE.md) liegt derzeit auf **separatem Dokumentationsbranch** `docs/xcmate-live-tv-stream-player-osd-20261024`, nicht hier erneut implementieren.
- **Erst als letzte Phase:** #63, #135, #136 (große Dateiziele), #126, #62 sowie abhängige Aufnahme-/Download-Themen.

## 6. Freigabe-Check vor einer späteren .32-Integration
- [ ] Quellcode-Nachweis, welcher Handle-/Owner-/Directory-Pfad bei EPG und Home bislang falsch lief
- [ ] Reproduzierbarer Fix mit zeitlich korrekt geordnetem native SearchWindow-Handoff
- [ ] Alle automatisierten Tests grün, ZIP- und SHA256-Identität geprüft
- [ ] Gezielte Testliste **NAVSEARCH-01–08 + REG-01–03** dokumentiert, **Android noch NOT_TESTED**, bis echter Nutzer-PASS
- [ ] Keine Sicherungs-/Portal-/EPG-/Favoriten-/Artwork-/Resume-/Autoplay-Daten angerührt
- [ ] User bewertet reale Android-Q1–Q3, bevor Issue #140 abgeschlossen und eine weitere Version gemergt wird
- [ ] Alle übrigen Download-/Recorder-Issues weiter OPEN und im Roadmap-Endbereich

**Zusammenfassung:** Das konkrete Zusammenspiel aus `guide_window.py::self.close()+Container.Update(global_search)`, positivem Directory-Handle-Fallback in `app_routes.py` und nach .31 geloggtem `global_search + DIRECTORY_DONE + xcmate_home` ist der **klar abgegrenzte erste Reparaturansatz**. Das tatsächliche Race ist im nächsten gezielten Geräte-Trace zu bestätigen. **Nicht** die EPG-Daten oder alle Kodi-Menüs blind neu schreiben.
