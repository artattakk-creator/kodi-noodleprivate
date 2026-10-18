# XCMate – zentraler Projekteinstieg

**Status:** 18.10.2026: XCMate 0.1.22 ist veröffentlicht; Live-TV-Navigation und EPG-Liste scheitern laut bestätigtem Android-Test in Issue #12. Testkandidat **0.1.23** auf `fix/issue-12-live-session-diagnostics`: 200 lokale Tests bestanden; Android-Abnahme offen, keine neue Veröffentlichung.
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Kodi-Repository:** GS Media Kodi Repository 1.7.0  
**Angezeigter Add-on-Name:** XCMate  
**Technische ID:** `plugin.video.xtreammate` (aus Kompatibilitätsgründen NICHT ändern)

Diese Dateien sind die verbindliche Arbeitsgrundlage für spätere Chats und Entwickler. **Zuerst [`CODEX_STATUS_CURRENT_DE.md`](CODEX_STATUS_CURRENT_DE.md) für den aktuellen Stand lesen**, danach `KODI21_FIX_022_DE.md`, `PROJECT_HANDOFF_DE.md` und `ROADMAP_AND_QA_DE.md`. Ältere Dokumente enthalten historische Versionsstände.

**Verbindliche nächste Ausbaustufen:** [EPG-Status & Vorschau – Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) **vor** [XCMate Skin – Issue #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14). Beides geplant, noch nicht implementiert. Der Live-TV-Fernbedienungsfehler aus 0.1.22 bleibt in [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) offen.

## Dokumente

- [Aktueller Codex- und Release-Status (verbindlicher Einstieg)](CODEX_STATUS_CURRENT_DE.md)

- [0.1.22: Korrekturen, Testbericht und Android-Abnahme](KODI21_FIX_022_DE.md)

- [Projektübergabe / Architektur / aktueller Zustand](PROJECT_HANDOFF_DE.md)
- [Neue Serienfunktion: Fortsetzen, Gesehen-Status, nächste Folge](SERIES_PROGRESS_SPEC_DE.md)
- [Freigegebenes Design / UI-Themes / benötigte Grafikdateien](DESIGN_SYSTEM_DE.md)
- [TiviMate 5.3.3: statische Navigations- und Fernbedienungsanalyse](TIVIMATE_5_3_3_NAVIGATION_ANALYSIS_DE.md)
- [TiviMate 5.3.3: Fernbedienung Player, EPG, Suchoptionen – Nutzerfotos](TIVIMATE_REMOTE_REFERENCE_2026-10-14_DE.md)
- [TiviMate 5.3.3: TV-Overlay, EPG, Hauptmenü und Filmansichten – weitere Nutzerfotos](TIVIMATE_UI_SCREEN_REFERENCE_2026-10-14_DE.md)
- [TiviMate 5.3.3: Einstellungsstruktur, Allgemein, Wiedergabelisten, EPG und Optik – 10 Fotos](TIVIMATE_SETTINGS_SCREEN_REFERENCE_2026-10-14_DE.md)
- [TiviMate 5.3.3: Wiedergabe, Kindersicherung, Sonstiges, Suche, Aufnahme, VOD und Über – 10 weitere Fotos](TIVIMATE_SETTINGS_FOURTH_SERIES_2026-10-14_DE.md)
- [Fotoverifizierter Einstellungsvertrag als JSON (ohne persönliche Daten)](TIVIMATE_SETTINGS_CONTRACT_2026-10-14.json)
- [Originalgrafiken: Namen, SHA-256, ZIP und GitHub-Uploadstatus](ARTWORK_ASSET_MANIFEST_DE.md)
- [Popup-Entwicklungsplan 0.1.15–0.1.19 und Android-Abnahmekriterien](POPUP_UI_IMPLEMENTATION_PLAN_DE.md)
- [Roadmap, offene Fehler, Release- und Android-Testplan](ROADMAP_AND_QA_DE.md)
- [Kopierfertiger Einstiegstext für neuen Chat](NEW_CHAT_COPY_BLOCK_DE.md)

**Wichtig:** Dokumentierte Anforderungen sind nicht automatisch implementiert. Der Status jeder Funktion steht in Projektübergabe/Roadmap. Die endgültigen freigegebenen Rastergrafiken wurden im Chat bereitgestellt; prüfe vor einem Build, ob die Bilddateien im Repository liegen und ob das Add-on bereits darauf verweist. Niemals Zugangsdaten, komplette Xtream-URLs mit Zugangsdaten oder private Kodi-Profilordner committen.
