# XCMate – Codex-Startauftrag: Suchfehler nach realem Android-Fail .32
**Datum:** 24.10.2026  
**Issue:** [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140) · **Roadmap:** [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143)  
**Status:** Arbeitsauftrag – **nicht implementiert**, Android-Freigabe noch offen.

## 0. Vor dem Codieren zwingend vollständig lesen
1. [Aktuelle .32-Kodi-Logforensik (BusyDialog/Focus)](LOGFORENSIK_02932_20261024_KODI_BUSY_DIALOG_DE.md) – **maßgebliche neue Evidenz**.
2. [Android-Abnahme .32: 7 PASS / 10 FAIL](ANDROID_ABNAHME_02932_20261024_NUTZERERGEBNISSE_DE.md).
3. [Vorherige .31-Code-/Logforensik](CODEX_UEBERGABE_LOGFORENSIK_SUCHFENSTER_20261024_DE.md) – nur als Historie, **nicht** als bewiesene aktuelle Root Cause.
4. [Offizielle .32-Testmatrix](ANDROID_ABNAHME_02932_DE.md) und Issue #140.

## 1. Ausführen – Reihenfolge verbindlich

**Baseline:** GitHub-`main` mit `plugin.video.xtreammate` **0.1.29.32**. Vor Branch-Beginn aktuellen Main-Stand nochmals abgleichen, dann neuen **kumulativen Draft-PR** für nächste freie Version (voraussichtlich **0.1.29.33**) abzweigen. **Keine** früheren Drafts/Legacy-Branches verwenden.

**A. Reproduzierten Hauptfehler eingrenzen und gezielt fixen.** Drei Android-.32-Traces zeigen jeweils `SEARCH_NAV INTENT → GUIDE_CLOSED → WAIT_RELEASE → RELEASE_TIMEOUT` (18:57, 18:58, 19:42), beim Abbruch `window=10025, dialog=10138` (**Kodi Busy Dialog**). In `src/plugin.video.xtreammate/resources/lib/search_navigation.py::released()` wird höchstens 2 s auf `not System.HasActiveModalDialog` gewartet; `guide_flow()` kehrt dadurch **vor** `open_search()` zurück. Prüfe über anonyme Timing-/Window-ID-/Owner-/Session-Traces, ob die Busy-Dialog-Phase durch synchronen Plugin-/Modal-Callback verursacht wird. Sorge für einen **sequenzierten, Kodi-21.2-tauglichen Window-Handoff**, der den nativen Suchdialog wirklich öffnet. `System.HasActiveModalDialog` nicht einfach auskommentieren; **keine fremden Dialoge schließen** oder globales Keymapping ändern.

**B. Separaten Fokus-/Medien-Suchfehler eingrenzen.** Der Medienpfad erreicht `SEARCH_INPUT_ACCEPTED`, `SEARCH_GUI_READY`, `SEARCH_RESULT_READY`, dennoch zahlreiche `Control 120 ... can't focus` in `window 13004` und weitere `Control 312`-Fehler. Prüfe `media_search.py`, `media_window.py`, `XCMateMedia.xml`, `guide_grid_window.py`: nur tatsächlich sichtbare/aktivierte Controls fokussieren; keine ungültigen Navigation-Edges, Fokus-Retries, Worker-/Session-Races, keine ghost clicks. `RESULT_READY` beweist noch **keine bedienbare Trefferliste**.

**C. Match-Qualität erst nach sichtbarer funktionierender GUI bewerten.** .32-EPG-Traces sind lediglich `EPG_PARTIAL` (zuletzt 344 von 2.764 Kanälen) und beweisen noch keinen finalen Programmtitel-Fehler. Ein vollständiger Test muss Titel einer gerade laufenden EPG-Sendung vor Back zeigen, nicht bloß Sendernamen.

**D. Bestandsschutz:** Live-TV OK/Down/Back und Sender-/Gruppennavigation, große EPG-Position/Rückkehr, Portal-/Favoriten-/manuelle EPG-Zuordnungen, Cover, Original-App-Icon, Space-Premium-Vorarbeiten, Film/Serie/Resume/Autoplay erhalten. Kein eigenes Player-/Skin-Redesign in diesem Fix. Downloads/Recorder weiterhin **am Ende der Roadmap**; keine Arbeiten an #63/#135/#136/#126 ohne neuen Auftrag.

## 2. Pflichtnachweise für den Draft-PR
- Reproduzierbare minimale Kodi-21.2-Testsimulation für `dialog=10138` und freigegebene/nicht freigegebene Fenster, echte fremde Modal-Dialoge, korrektes Back, langsame GUI-Initialisierung, Action-/Directory-Handles.
- GUI-/XML-Fokus-Tests für Control 120/312 und Suchresultat-Commit, einschließlich mehrfacher/abgebrochener Suchläufe.
- Alle Host-Tests grün; kurzes Audit, dass der Fix **nicht** bloß aus `sleep(2)`, höherem Timeout oder blindem Modal-Bypass besteht.
- Getrennte **Android-Miniteststrecke zunächst nur drei Gates**: **A1** Jetzt-Sendung aus großem EPG → sofort sichtbare native, bedienbare Ergebnisliste; **A2** Sendername → wählbarer Treffer vor Back; **A3** Medien-Suche → Fokus/Back sauber, keine schwarze Kodi-Seite. Erst wenn **A1–A3 PASS**, den erweiterten NAVSEARCH-/REG-Lauf wiederholen. **Alle noch NOT_TESTED**.
- Separater **Draft-PR** mit ZIP, SHA256, Changelog, Diagnose/Root-Cause-Begründung, Testprotokoll und Android-Abnahme-Anleitung. Echte Android-Tests nicht behaupten.
- **Keinen Merge, keinen Release, kein OTA-Publishing und kein Schließen von #140 ohne ausdrückliche erneute Nutzerfreigabe.** Kein Downgrade, keine Deinstallation, keine Profildatenlöschung.

## 3. Datenschutz
Die Rohlogs `kodi.old(8).log` und `kodi(20261024-181608).log` verbleiben privat. **Nicht** in einen öffentlichen PR, GitHub-Issue, CI-Artifact oder Commit laden. Nur redigierte Ereignis-Codes/Window-IDs/Zeiten, keine Portale, Stream-/SMB-URLs, Credentials, Suchtexte oder Benutzerkennungen.
