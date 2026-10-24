# Codex-Auftrag: XCMate Live-/App-Icon-Rail, Catch-up und bebilderte EPG-Programmzeitschrift
**Stand:** 24.10.2026 · **Repository:** `artattakk-creator/kodi-noodleprivate` · **Ausgangsbasis:** `main`, installierte XCMate 0.1.29.30 nach kumulativem PR #149. **Keine automatische Versionsveröffentlichung oder Merge.**

## Bitte zuerst lesen
- [Privat bereinigter Log- und Code-Abgleich .30](KODI_LOGS_02930_NAV_CATCHUP_EPG_20261024_DE.md) (die privaten vollständigen Kodi-Logs sind NICHT im Repo, nur anonymisierte Fakten).
- [Delta-Teststrategie nach Issue-Audit](ANDROID_DELTA_TESTPOLITIK_AB_02930_20261024_DE.md).
- [#94 Live-Rail](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94), [#150 universelle Icon-Rail](https://github.com/artattakk-creator/kodi-noodleprivate/issues/150), [#99 Catch-up](https://github.com/artattakk-creator/kodi-noodleprivate/issues/99), [#123 EPG-Magazin](https://github.com/artattakk-creator/kodi-noodleprivate/issues/123), [#17 Live-Overlay](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#88 EPG](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88).
- P0-Fixes weiterhin unabhängig [#140 NOW-EPG-Suche](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140), [#135 Redirect-Trust](https://github.com/artattakk-creator/kodi-noodleprivate/issues/135), [#63 Download](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63), [#126 Direct-TS-Capture](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126), [#111 Poster](https://github.com/artattakk-creator/kodi-noodleprivate/issues/111).

## Gesicherte Gerätediagnose aus Kodi .30 (kein Rohlog veröffentlichen)
- `SEARCH_EPG`: **2764 Kanäle, 192 NOW (189 XMLTV, 3 Short), 391 Aliase, 11 Sendernamen-Matches, 0 NOW-Sendungstitel-Matches, `EPG_PARTIAL`**; danach WINDOW_CLOSED und Live-PLAYER_DISPATCHED. S4 groß EPG PASS, *globale NOW-Suche FAIL*. **Die beiden getrennt untersuchen**. Keine privaten Suchstrings im Log.
- **24** Kodi-Fokusfehler `Control 120 in window 13000–13002 ... can't` zwischen 12:47 und 13:20. Möglicher UI/Window-Control-Focus-Vertragsfehler; vor neuer Rail Ursache und sichere Fallback-Fokuskette prüfen.
- Drei Download-Redirect-Policy-Denials `REDIRECT_UNTRUSTED_TARGET` mit **0 Bytes**, keine E2E-Dateikopie bewiesen; **kein HTTPS-Sicherheitsmechanismus entfernen**. USB-Picker nutzt `USB_STAGE` nach `LINK/38`, internes Stage READY, USB-Ziel gespeichert. SMB2-Probe und SMB-Bind/Persist OK. Native Aufnahmezielprüfung `LINK/38` gesondert.
- Ein Artwork-SQLite-`BUSY/QUERY sqlite=5`, noch kein Kausalnachweis für Userposter-Timeout.
- Stabilitäts-Telemetrie .30 im lokalen 35-Minuten-Fenster: **1.140 Portal-Calls / 1 Diskread, 0 OOM, pressure=false**. Der separate vom Nutzer berichtete 4h-MEM1-PASS bleibt historisch bestehen.

## PR-Paket 1 – Stabilisierende fokussierte Bugfixes statt ungetesteter Full-Release
A) **#140** Suchtreffer 0 `programme_hits` trotz EPG NOW, zusammen mit potenziell fehlgeroutetem OK-/Player-Handoff, Window-Owner und Control 120 reparieren. *Test:* im großen EPG sichtbare tatsächlich laufende Sendung im Live-Search eingeben; korrekte EPG-Sendungstreffer statt Sendernamen, auch mehrere Sender bei gleichem Titel; Suchfenster bleibt offen bis explizite Auswahl/Zurück.
B) **#135/#63** zugänglicher bestehender portalgebundener Redirect-Trust-Workflow: geprüfte Quelle/Zielorigin, bewusste Freigabe, explizites Retry, Widerruf, sichere Denial bei untrusted; erst danach DRM-freier berechtigter Film/eine Episode auf USB/SMB vollständig + Hash + Replay; nicht automatisch Hosts freigeben.
C) **#126/#111** native Aufnahmeziel-/DirectTS-Test und Provider-Poster-Timeout/Artqueue-Lock getrennt; #111 gezielte offizielle TMDb-Poster-Fallbacks bei eindeutiger Film-/Serienidentität, nie allgemeiner Nachrichten-/Sendungs-Titel-Poster-Spiegel.

## PR-Paket 2 – gemeinsamer Navigationsvertrag #94 + #150
**Strikt exakte Live-Zustandsmaschine:**
```
FULLTV → [Links] Mini-EPG/Senderliste → [Links] Sendergruppen → [Links] schmale Icon-Rail
→ [Links] ausgeklappte Icon+Text-Rail → [Links] zurück zu FULLTV (Stream weiter).
```
Rechts und Zurück setzen kontextsensitiv jeweils die vorherige Ebene/fokussierte Auswahl zurück, keine ungewollte Senderumschaltung. Getrennt 1× OK Infobar und 2× OK/↓ Playback-Controls aus #17 schützen; im Mini-EPG Rechts auf markiertem Sender die echte Vorschau nach #95.

**Menü:** Suchen, Favoriten, Live-TV, Filme, Serien, Einstellungen, **Startkanal bewusst festlegen** (nur passend, Bestätigung), Verlassen → **XCMate Home**, nicht Kodi Home. Icon-only und Icon+Text; Hoch/Runter Fokus, OK bestehende Route, schneller IR Repeat dedupliziert.

**Appweit:** Ein einziger gemeinsamer `RailItem`-Kontrakt mit `icon,label,route,enabled,context,selected` und Kodi WindowXML-spezifischen Hooks. Geeignete Home-, Film-, Serien-, großes-EPG-, Suche-, Favoriten- und Medienmanager-Ansichten konsistent ausrüsten; vorhandene Links-Navigation im jeweiligen Grid/Zeitleiste nicht zerstören; natives Android-/Kodi-Dialog-Picker, Kodi player OSD und externe Addons unangetastet. Original-XCMate-Icon/Original-Splash, Lightweight-Basis, Premium optional.

## PR-Paket 3 – EPG als echte digitale Programmzeitschrift #123
Ersetze das `guide_grid_window._actions()`-Info-`textviewer()` durch eigene elegante, performante Kodi21-WindowXML-Sendungsdetailansicht: Senderlogo, Sendungsbild sofern tatsächlich korrekt vorhanden, Titel, Sendezeit, Dauer, Fortschritt, EPG-Plot mit Langbeschreibung, Genre, Staffel/Episode/Personen/Jahr **nur bei belegter Datenquelle**, Aktionen „Jetzt ansehen“, „Zurück“, „EPG zuordnen“, „Erinnern“ und ggf. Catch-up/Startover getrennt. **Back kehrt auf exakt selbe Guide-Zelle, Gruppe, Zeitachse**.

**Metadaten-Kaskade:** XMLTV/Portal → lizenzierte vertrauenswürdige TV-Programmdaten mit eindeutigem Event-/Sender-/Zeitbezug → TMDb **nur bei eindeutig identifiziertem Film oder Serie** (ID, Originaltitel/Jahr/Typ), nie ungeprüft Filmcover für News/Sport/Magazin. Keine synchronen API-Aufrufe im Key-Thread; lokaler begrenzter Cache/Timeouts/Attribution/API-Key-Geheimnisschutz, Offline-Fallback und Buttonstatus bei unvollständigen Daten.

## PR-Paket 4 – tatsächliches Catch-up / Replay #99
Guide-Kacheln nur bei echten Archivfenster-Metadaten `tv_archive/tv_archive_duration` und Eventtimestempeln mit Replay-Symbol; **sichtbarer Catch-up-Button** öffnet für dieses einzelne historische Programm einen nach Anbieter/Portal wirklich unterstützten Archivstream bei korrekt berechtigter Nutzung. Tatsächliche Replay-URI/Protokoll/Tokenfluss gegen verwendeten Provider prüfen, keine Credentials in Logs. Stimmt capability nicht oder Ereignis außerhalb Fenster: **kein aktiver Pseudo-Button**, genaue deaktivierte Erklärung. `Von Beginn` (Startover) für laufende Sendung als separate Capability. Keine Verwechslung mit geplanter Aufnahme (#62/#126) oder zeitspringendem EPG-Guide. Keine DRM-Umgehung. EPG-Magazin-Aktionen und Replay-Icon kommunizieren denselben Status.

## Auslieferung, Tests und Anti-Regression
1. Kleine **getrennte Draft-PRs** auf aktueller Main-Basis; optional gestapelt, aber kumulativ. Dokumentierte manuelle Prüfung, 100% relevanter CI, Dateipaket ZIP+SHA256, Versionsinkrement nur bei tatsächlich neuem Kandidaten; **keine eigenmächtigen Merges/OTA-Releases**.
2. **S1–S5** 1× je Gerätetestversion statt altes 29er-Komplettformular.
3. **RAIL1–RAIL5**: Live 5× Links, fokussierte visuelle Rail und bewusster Home/Startkanal-Action, keine Control120-Fehler; gleicher Rail-Contract in mindestens Home/Filme/Serien/EPG; 20 schnelle IR-Zyklen, kein falscher OK-Player, keine Keymap-/Kodi-OSD-Regressions.
4. **EPG-DETAIL1–3**: echtes Event, korrektes Sender-/Bild-/Text-Matching, Online-/Offline-Fallback, Back exakt zur Zelle, keine spurious Senderwechsel.
5. **CATCHUP1–4**: Archiv-Event spielt tatsächlich ab, 0 Archivfähigkeiten -> kein Replay-Fake, jenseits Archivfenster keine Aktion, Startover getrennt und nur wenn unterstützt. Provider ohne Archiv nicht als Produktausfall ausgeben, `NOT_SUPPORTED` sachgemäß anzeigen.
6. Auf Gerät **Android TV 13 / RK3528 ARM32 / Kodi 21.2 / Titan BINGIE MOD** prüfen, andere Skins opt-in. **Keine Portal-/EPG-/Favoriten-/Startsender-/Resume-/Autoplay-/Icon-Daten löschen oder neu initialisieren**.
