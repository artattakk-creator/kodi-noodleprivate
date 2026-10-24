# XCMate – verbindliche Master-Projektübergabe / nächster Chat
**Stand:** 24.10.2026, ca. 13:35 Uhr Europe/Berlin. **Projekt:** GS Media XCMate, Add-on-ID `plugin.video.xtreammate`.  
**GitHub:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Produktiv über GS-Media-Repository erreichbar:** **0.1.29.30** (`src/plugin.video.xtreammate/addon.xml` **und** `addons.xml` auf `main` geprüft). Kumulativer Release-Merge [PR #149](https://github.com/artattakk-creator/kodi-noodleprivate/pull/149), Merge-Commit `3fcf275879350da2780b3a81fc813f3a04da87f3`; 1.029 CI-Tests PASS. **Keine neue Version oder Featureumsetzung durch diese Dokumentation**; alle offenen Arbeiten müssen separat von Codex entwickelt und auf Android getestet werden.

## 0. Sofortige Leseanweisung für den nächsten Chat/Codex
**Zuerst dieses Dokument lesen**, dann die verlinkten Quellberichte und aktuellen Issue-Inhalte. Danach **nicht bei Null anfangen**, sondern PR/Status prüfen und die unten festgelegte Arbeitsreihenfolge mit realen Android-Delta-Tests fortsetzen. **Nie** ohne explizite Anweisung eigenmächtig mergen, releasen, Add-on deinstallieren, Kodi-Profil resetten oder bestehende Portaldaten löschen. Roh-Kodi-Logs und private URLs nicht ins öffentliche Repository übertragen.

### Verbindliche Dokumente
1. [Android 0.1.29.30 Originalabnahme: 12 PASS / 15 FAIL / 1 BLOCKED / 1 NOT_TESTED](ANDROID_ABNAHME_02930_20261024_NUTZERERGEBNISSE_DE.md)
2. [Sanitisierte Diagnose aus zwei neuen Kodi-Logs – .28/.29/.30, Navigation/Catch-up/EPG](KODI_LOGS_02930_NAV_CATCHUP_EPG_20261024_DE.md)
3. [Vorherige Kodi-Logforensik .28/.29](KODI_LOGANALYSE_02928_02929_20261024_DE.md)
4. [Neue Delta-Testpolitik ab .30](ANDROID_DELTA_TESTPOLITIK_AB_02930_20261024_DE.md)
5. [Issue-Audit der ursprünglichen 73 offenen Issues](ISSUE_AUDIT_KONSOLIDIERUNG_20261024_DE.md) und [Master-Issue #143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143)
6. [Gesamter Codeauftrag nach Logs und .29](CODEX_AUFTRAG_02930_NACH_KODI_LOGS_20261024_DE.md) – historische Basis, bei Widersprüchen neuere .30-/aktuelle UX-Anforderungen maßgeblich
7. [Live-TV IR/OSD-Grundvertrag](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md)

## 1. Hardware, Runtime und geschützte Baseline
- Android-TV-Box **Rockchip RK3528 / ARM32**, Android TV **13**, **Kodi 21.2 Omega**, Skin **Titan BINGIE MOD 2.2.3**, IR-Fernbedienung. Gleiche Haupttests auch unter Estuary sinnvoll. Nicht von x86/Host-CI auf diese Hardware schließen.
- GS-Media-Repository **1.7.0** installiert; es publiziert XCMate .30 via `addons.xml`. **Original-XCMate-App-Icon unverändert**; Lightweight nutzt nun gewünschtes Original-Space-Splash (UI1/UI2 PASS); Space Premium optional und noch **#115 P0 Fokus/OK-FAIL**.
- Persistenz schützen: Xtream/M3U/Stalker-Portale, aktive Gruppen, Startgruppe und Startsender, EPG-Quellen und **manuelle Sender-Mappings**, Favoriten, Resume/Weitersehen/Gesehen, Staffel-Autoplay, Download-/Aufnahmeziel und Themes; keine unbestätigte Migration/Reset.
- Normale IR-, Live-, Film-/Serien- und große EPG-Grundpfade sind bereits Android-abgenommen. **Vorhandene Kernfunktionen nicht bei jedem Hotfix wieder mit 29 Tests vollständig abfragen.**
- Abgeschlossene Kern-Issues (**`completed`**, Stand Audit+neue .30 Abnahme): **#67, #73, #97, #125, #42, #85, #131, #122, #142, #141**. #141 gilt nur für vierstündige Stabilisierung und Service-/Neustart-PASS, nicht für unbegrenzte OOM-Freiheit. **22 historische Tickets `duplicate` heißen nur Verwaltungs-Konsolidierung, KEIN technischer PASS**; #66 `not_planned` (PiP).
- Live-GitHub-Abgleich unmittelbar vor Erstellung: **47 offene echte Issues**, einschließlich neuer universeller Rail **#150** und Master #143; **33 geschlossene = 10 completed + 22 duplicate + 1 not_planned**. Verändert sich durch künftige Arbeiten.

## 2. Letzte echte Android-Abnahme: XCMate 0.1.29.30
**29 Testfelder: 12 PASS / 15 FAIL / 1 BLOCKED / 1 NOT_TESTED.** Die frühere .29-Matrix **12 PASS / 16 FAIL / 0 NOT_TESTED** nicht überschreiben.

| Bereich | Status | Fachliche Konsequenz |
| --- | --- | --- |
| **S1–S5 Grund-Smoke** | **5/5 PASS** | Home/Film/Serie/Live/großes EPG/Datenerhalt grundsätzlich funktionsfähig |
| **ST1 Quellenübersicht** | **NOT_TESTED** | Root-Picker laut neuem Log zwar aufgerufen, aber vom Nutzer nicht visuell abgenommen |
| **ST2 USB wählen; ST5 Fehlerbehandlung** | **PASS/PASS** | Auswahl/Persistenz und getestete Fehlerrückmeldung, nicht fertige Übertragung |
| **ST3 USB-Datei; ST4 SMB-Datei** | **FAIL/FAIL** | End-to-End-Zieldatei fehlt; Source-Redirect-Deny vorgelagert |
| **DL1–DL5 Film/Folge/CDN/Pause/Offline/Sicherheit** | **5× FAIL** | `REDIRECT_UNTRUSTED_TARGET`, 0 Bytes, keine erfolgreiche Film-/Folgeübertragung |
| **EPG1 Sendungstitel, EPG3 Sender/Mapping** | **FAIL/FAIL** | Spinner → Suchfenster zu → Home/ungewollter Player-Übergang |
| **EPG2 nur Short-EPG** | **BLOCKED** | Nicht als unabhängiger Fehler zählen |
| **UI1/UI2 Splash, PO1 Sprache** | **3× PASS** | #122 und #142 abgeschlossen |
| **REC1–REC4 TS-Aufnahme** | **4× FAIL** | Start/Bytes/Stop/Wiedergabe/Unterbrechung nicht end-to-end bestanden |
| **ART1/ART2 Poster** | **2× FAIL** | Timeout, gezielter Retry und sicherer TMDb-Fallback weiterhin offen |
| **MEM1 4h / MEM2 Service-Neustart** | **2× PASS** | #141 akuter Incident abgeschlossen, begrenzter Geltungsbereich |

## 3. Zwei neue private Kodi-Logs: Versionsgrenzen und harte Befunde
Dateien im Chat: `kodi.old(6).log`, `kodi(10).log`. **Nur die sanitisierten Auszüge aus dem obigen GitHub-Diagnosebericht verwenden.** Rohdateien enthalten potenziell vertrauliche Netzwerk-/Provider-/Geräteinformationen.

- Altlog ca. **08:43–12:42 am 24.10.2026** (30.692 Zeilen): Start .28, Upgrade auf **.29 um 09:15:08**. Parser-#34718 und ältere Probe-Fehler sind **keine .30-Neu-Regressionsbeweise**.
- Neulog ca. **12:42–13:21** (2.305 Zeilen): startet .29, Upgrade auf **.30 um 12:45:14**. Keine neuen `POParser #34718` nach .30 nachgewiesen.
- **#140 Suche – 12:49:16:** `SEARCH_EPG code=EPG_PARTIAL`; **2764 Sender**, **192 aktuelle EPG-Events** (**189 XMLTV + 3 Short**), **2 Quellen**, **391 Alias**, **0 manuelle Zuordnungen in diesem Diagnosekontext**, **11 name_hits**, aber **0 programme_hits**. Elf Treffer betreffen **Sendernamen**, **nicht Sendungstitel**. Danach `SEARCH_WINDOW_CLOSED → OWNER_RELEASED → PLAYER_REQUEST → PLAYER_DISPATCHED`, obwohl Nutzer nach OK/Spinner auf Home landet. **Fokusrouting/EPG-NOW-Suchklassifikation und unerwarteter Player-Übergang** untersuchen; nicht einfach EPG-Abdeckung als alleinige Ursache behaupten.
- **#136 Zielpicker:** `PICKER_ROOT_LISTED count=3`; USB: `NATIVE LINK errno=38 → USB_STAGE → INTERNAL_STAGE → STAGING_READY → TARGET_BOUND → PERSIST_OK`. SMB: `SMB2 → TARGET_BOUND → PERSIST_OK`. **Das belegt vorhandene Backend-/Pickerpfade, keine echte fertige Datei.** Separate native Captureprobe mit `LINK:38` weiter vorhanden.
- **#135/#63 Downloads:** drei `DOWNLOAD_REDIRECT 3xx hop=1 cross=1 scheme=http reason=REDIRECT_UNTRUSTED_TARGET`, danach `DOWNLOAD FAILED bytes=0` (ca. **12:56:35, 12:59:58, 13:06:19**). **Sicherheitsbedingter Cross-Origin-Deny, kein nachgewiesener USB-/SMB-Schreibfehler.** Bei HTTP-Ziel ggf. Transport-Downgrade-/Credentialschutz prüfen. **Nie alle Redirects blind erlauben, TLS-/DNS-/SSRF-Schutz nicht entfernen.** Bestehende UI `Downloads verwalten → Redirect-Ziel für dieses Portal prüfen/freigeben → Erneut versuchen` nur nach unabhängiger Host-Vertrauensprüfung; Widerruf testen.
- **UI-/Fokusdiagnose:** **24×** `Control 120 in window 13000–13002 has been asked to focus, but it can't`; beim Rail-/Such-Fix vor jedem Fokuswechsel Sichtbar-/Aktiv-/Focusability prüfen. **Nicht behaupten, dies sei bereits durch das noch nicht implementierte Icon-Menü verursacht.**
- Einmal `artwork db: BUSY/QUERY/sqlite=5`, kein Poster-Timeout-Root-Cause-Beweis.
- Ca. **35 Minuten** Cachetelemetrie nach .30: `portal_calls=1140`, `portal_disk_reads=1`, `portal_oom=0`, `portal_read_errors=0`, kein `pressure`-Signal; guter Hinweis, aber **kein 24h-Beweis**. Echte 4h-MEM-Abnahme separat dokumentiert.

## 4. NOCH FEHLENDE, bereits lange vereinbarte Produktfunktionen – höchste UX-Priorität

### 4A. Catch-up / Replay direkt im großen EPG – [#99](https://github.com/artattakk-creator/kodi-noodleprivate/issues/99)
**Noch nicht implementiert:** Im großen EPG an vergangenen Sendungen bei **bestätigter Anbieter-/Kanal-/Zeitfenster-Archivfähigkeit** erkennbares Replay-Symbol anzeigen und **wirklichen, fokussierbaren Button „Catch-up abspielen“** anbieten. Ggf. eigene Funktion **„Von Beginn starten“/Startover**, falls Provider unterstützt.
- Anbieterkapazität, Stream/EPG-Timeslots, Berechtigung, korrekte URL-/Format-/Playerfähigkeit pro Portal und Sender prüfen. Kein Fake-Button aus XMLTV-Vergangenheit und keine DRM-Umgehung. Bei unbekannter/negativer Fähigkeit deaktiviert + nachvollziehbarer Hinweis.
- Archiv-Auswahl muss exakt Sender, Event und Zeitraum abspielen (nicht Live-Stream); Stop/Back soll dieselbe EPG-Zelle restaurieren; keine verfrühte Markierung als Android-PASS. EPG-Aufnahmetimer #62 ist getrennt.

### 4B. Reichhaltige Sendungsdetailseite wie eine TV-Zeitschrift – [#123](https://github.com/artattakk-creator/kodi-noodleprivate/issues/123), Guide [#88](https://github.com/artattakk-creator/kodi-noodleprivate/issues/88)
**Noch nicht implementiert:** Der aktuelle Code nutzt in `guide_grid_window.py::_actions()` und Mini-EPG `xbmcgui.Dialog().textviewer`, **nicht** die besprochene Magazinseite.
- Nach OK im großen/kleinen EPG: großes **verlässlich passendes Sendungsbild**, Senderlogo, Titel, Uhrzeit/Datum/Dauer/Progress, Genre, Beschreibung, Staffel-/Episodendaten und weitere tatsächlich belegte Metadaten, scrollbarer Text, Programmaktionen (ansehen, Catch-up sofern unterstützt, Erinnerung, Sender-EPG zuweisen).
- **Metadatenreihenfolge:** vorhandene EPG-/XMLTV-/Providerdaten/-Bild zuerst; optional *lizenzierter* externer TV-Programmdienst mit verifiziertem Event-/Sender-/Zeitmatch; **TMDb nur für eindeutig identifizierte Filme/Serien**, niemals per bloßem Titel irgendein News-/Sport-/Magazinposter. Bei Fehlen neutrales Senderlogo/Placeholder statt falscher Bebilderung. Asynchrone, rate-limitierte Cache-Worker statt HTTP in GUI-/IR-Routine. Quelle/Frische und Retry differenzieren.
- Rückkehr ohne Positionsverlust zur exakten Guide-Gruppe/Zelle/Timeline; keine Nebenwirkung auf Wiedergabe, Portal oder EPG-Mapping.

### 4C. Live: **dreimal Links → Icon-Rail**, danach ausklappen – [#94](https://github.com/artattakk-creator/kodi-noodleprivate/issues/94)
**Noch nicht implementiert:** Ist-Code `live_overlay.py::LiveNavigator._handle_command` schaltet `channels → groups → hidden`.
**Gewünschte echte Zustandsfolge:**
```
LIVE_FULL -- LINKS --> MINI_EPG/KANÄLE
          -- LINKS --> SENDERGRUPPEN
          -- LINKS --> NAV_ICONS (schmale vertikale Leiste NUR Icons)
          -- LINKS --> NAV_EXPANDED (gleiche Icons + lesbare Menünamen)
          -- LINKS --> LIVE_FULL (Overlay aus, laufender Stream bleibt)
```
Rechts/Zurück sinnvoll eine Ebene rückwärts, Up/Down innerhalb Rail **nur Fokus bewegen**, OK auf ausgewählten Eintrag. **Menüaktionen:** Suchen, Favoriten, Live-TV, Filme, Serien, Einstellungen, **Startkanal setzen (nur explizit mit Bestätigung; keinen zufälligen Startsenderwechsel)**, Zur XCMate-Home/Verlassen. Original-Icon/ruhiges Lightweight; Premium später optional. Live-IR ohne globale Kodi-Keymap-Änderung, keine Fake-Fokuselemente.

### 4D. Gemeinsame vertikale Icon-Rail auch außerhalb Live – [NEU #150](https://github.com/artattakk-creator/kodi-noodleprivate/issues/150)
**Neuer expliziter Auftrag:** dieselbe schmale/erweiterte Navigation als wiederverwendbares **XCMate-Framework** in **Home, großem EPG, Filme, Serien, Favoriten, Suche und sinnvollen Download-/Medienmanager-Ansichten**. Kontextuelle Menüpunkte, aktive Rubrik sichtbar, Sender-/EPG-/Katalog-/Scrollposition erhalten. Native Android-/Kodi-Speicherpicker und Texteingabe NICHT überschreiben; Live Links-Kette und IR-Rechts-/Back-Verhalten #94 / #95 respektieren.
- Kodi21/RK3528/Mali-450: eigene bedienbare Kodi Controls/WindowXML, sichtbarer Fokus; besonders Fokusfehler `Control 120` reproduzieren/beheben. Kein globaler Skin-Patch oder massive Texture-/RAM-Last. Für Premium #115 gesonderte Abnahme.

### 4E. Mini-EPG-Programmvorschau und bestehende EPG-Manager-Pflichten
- [#95](https://github.com/artattakk-creator/kodi-noodleprivate/issues/95): Mini-EPG mit **Rechts auf markierten Sender** → dessen echte kommende Programmliste, ohne laufenden Sender zu wechseln, Zurück restauriert die vorherige Senderzeile.
- [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98): im großen EPG pro Sender **EPG zuweisen/ändern**; aus EPGShare01/Kaimandura/Anbieter-XMLTV wählen; **Preview ohne Speichern**, erst Bestätigung persistiert Portal+Sender+Quell-ID+EPG-ID. Keine verwechselten IDs.
- [#60](https://github.com/artattakk-creator/kodi-noodleprivate/issues/60): bislang schwache Quell-/Senderabdeckung (historisch 288/2764 = 10,4% XMLTV), Quellen- und Kurz-EPG-Fallback verbessern; spätere .30-Suchdiagnose **192 aktive NOW-Events** beweist nicht dieselbe Mapping-Quote.
- [#62](https://github.com/artattakk-creator/kodi-noodleprivate/issues/62): EPG-Reminder, Auto-Tune und geplante Aufnahmen getrennt von Archiv-Replay.

## 5. Gegenwärtige P0/P1-Blocker – nicht durch UX vergessen
| Issue | Nachgewiesener Stand / nächste harte Voraussetzung |
| --- | --- |
| [#140](https://github.com/artattakk-creator/kodi-noodleprivate/issues/140) EPG-Programmtitelsuche | **0 programme_hits** bei 11 Sendernamenshits; Fenster schließt/Playerdispatch. Echtes NOW-Titel-Matching, sichtbare Liste und IR-OK-Fokus/Rücksprung korrigieren |
| [#135](https://github.com/artattakk-creator/kodi-noodleprivate/issues/135) CDN-Redirect | `REDIRECT_UNTRUSTED_TARGET` 3×, 0 Bytes; klarer **sicherer** Trust-/Grant-/Revoke-/Retry-UX, nur verifizierte Ziele |
| [#63](https://github.com/artattakk-creator/kodi-noodleprivate/issues/63) Downloads | vollendeter Film + einzelne Episode, Pause/Resume/Abbruch/Offline mit Dateiintegrität und tatsächlichem USB/SMB-Target erforderlich |
| [#136](https://github.com/artattakk-creator/kodi-noodleprivate/issues/136) USB/SMB | Picker wird geloggt, reale komplette USB-/SMB-Datei nicht; externer Zielordner/Backend final beweisen |
| [#126](https://github.com/artattakk-creator/kodi-noodleprivate/issues/126) DirectTS-Aufnahme | native Probe `LINK:38`, **keine** bestätigte 2min-Aufnahme/Stop/Playback. Download-Staging ist nicht automatisch Recording |
| [#111](https://github.com/artattakk-creator/kodi-noodleprivate/issues/111) Poster | Provider-Timeout; gezielter asynchroner Retry, sauberer Fehlergrund und **korrekt identifizierter TMDb-Fallback** für Filme/Serien; bestehende READY-Cover schützen |
| [#115](https://github.com/artattakk-creator/kodi-noodleprivate/issues/115) Space Premium | immer noch sichtbarer Fokus/OK-Routing Android FAIL; Lightweight-Rückwechsel PASS |
| [#43](https://github.com/artattakk-creator/kodi-noodleprivate/issues/43) Setup | Plug-and-Play Erststart Wizard (Portal-/Gruppen-/EPG-/Cover-Import, persistente Startkonfiguration), Beta-Pflicht |
| [#127](https://github.com/artattakk-creator/kodi-noodleprivate/issues/127) Rich Search | bebilderte Suchtreffer mit Logos/Film-/Seriencover und EPG-Metadaten, separat vom P0-#140 |
| [#102](https://github.com/artattakk-creator/kodi-noodleprivate/issues/102) Katalog | mehr als nur 24 Film-/Serientitel, Infinite Scroll/vollständiger Katalog |

## 6. Ab jetzt konkrete Codex-Reihenfolge ohne redundante Issues
**Phase A – P0-Stabilität und echte Mediennutzung:** #140 (falsches NOW-Matching/Window-Owner/Fokus), #135→#63→#136 (sicherer Redirectgrant, dann echter Film/Folge USB/SMB), #126 (Recorder separat), #111 (Poster Timeout + TMDb). Nur gezielte Codepaths, keine unsicheren Hotfixes.
**Phase B – gewünschte Bedienung:** #94 (Live-Icon-Rail mit Tastenstatus), danach **#150** (gemeinsamer Rail-Contract in EPG/Filme/Serien), **#95** Mini-Guide-Rechtsvorschau. Keine Code/Status-Regression am Player.
**Phase C – EPG als Programmzeitschrift:** #123 (bildreiche Sendungsinfo), #99 (Capability-gesicherter Catch-up-Button + echte Replay), #98/#60 (per-Kanal Mapping, Quellenqualität). EPG-UI und unabhängigen Inhalt/Archivfähigkeit unterscheiden.
**Phase D – RC/Beta:** #43 Wizard, #127 Rich Search, #102 Katalogabdeckung, #115 Premium-Fokus. Frühere Beta-Freigabe erst wenn essenzielle P0 und Geräteabnahme erfüllt.

**Codex-Lieferstandard:** kleine fachlich getrennte Draft-PRs, Tests und GitHub-CI, kumulatives Android-Installations-ZIP + SHA256/Changelog, wirklich auf RK3528/Kodi21.2 überprüfbare Tests; eigenmächtiges Merge/Release VERBOTEN. Keine neuen 20 Duplikat-Issues: bestehende **#94/#99/#123/#140** etc. gezielt kommentieren und mit #150/#143 koordinieren.

## 7. Delta-Testplan für nächstes Gerätetest-ZIP
**Immer nur S1–S5 je Release:** Start/IR, Film-/Seriendetail, Live aus Suche, großes EPG/Senderstart, Originalicon/Benutzerdaten. **Keine redundanten Wiederholungen der 29 Felder**, sofern die geänderten Codepfade diese nicht betreffen.
**Zusätzlich NUR je Code-Diff:**
- **NOW1/2:** exakten gültigen Jetzt-Sendungstitel aus großem EPG in globalem Suchfeld eingeben → **echte Programmtitel-Treffer** auf den richtigen Sendern, keine ungewollte Player-/Home-Umleitung.
- **DLOAD1/2/3:** bewusst bestätigter vertrauenswürdiger CDN-Redirect und widerrufbare Berechtigung, Film+Episode mit Bytes>0/COMPLETE auf USB/SMB, Playback/Offline lokal; untrusted/unsicher bleibt zu Recht blockiert.
- **REC1/2:** geeigneter TS-Stream: >0 Bytes für ~2 min, sicherer Stop und Datei-Playback, korrekte Ausgabe bei inkompatiblem Ziel.
- **ART1/2:** providerfehlerhaftes Poster lädt nur nach eindeutigem Film-/Serien-TMDb-Match, nach Neustart bereit; READY-Bilder unverändert, News/Mehrdeutigkeit kein Falschcover.
- **RAIL1–5:** Live **5× Links** korrekte Ebenen, sichtbare Icon-/Text-Fokusebene; Menürouten inkl. Startkanal mit expliziter Bestätigung; Home/Film/Serie/großer EPG kontextuell, 20 Fernbedienungszyklen/Back/Right, kein `Control 120`-Fokusfehler.
- **DETAIL1–3:** Film-/News-/Sport/fehlende EPG-Metadaten und Bild-Fallback, korrektes Gerätedetail und Rücksprung zu exakt derselben EPG-Zelle, keine GUI-Hänger.
- **CATCHUP1–4:** tatsächlich archivfähiger Kanal/Event im gültigen Fenster sichtbar und **abspielbar**; Kanal ohne Archiv oder Event außerhalb Fenster ohne Fake-Button; optional Startover separat; Stop/Back und Laufzeit korrekt.
- **MAPPING1/2:** Event-EPG-Quelle wechseln: rein visuelle Preview ohne Persistenz, erst Bestätigung gespeichert, Back verwirft Preview.
- **MEM:** wegen #141-Abschluss 4h nur bei Änderungen an Portal-/Service-/Katalog-/Thread-Lebensdauer erneut, sonst S1+gezielte Memory-Stichprobe.

**Statusführung:** Geräte-`PASS` nur nach echter Ausführung; CI-only ≠ Android PASS; Abhängigkeiten `BLOCKED` statt mehrere unabhängige FAILs; #143 bleibt Master; `CLOSED_CONSOLIDATED` ist kein technischer Abschluss. Nach bestätigtem Android-Vollscope einzelne Issues `completed` schließen.

## 8. Präzise nächste Chat-Anweisung
> Setze GS Media XCMate auf dem geprüften `main`-Stand 0.1.29.30 fort. Lies diese Master-Übergabe sowie die verlinkten Android-/Log-Berichte. Prüfe vor Codex-Aufgaben, ob inzwischen Draft-PRs für #140/#135/#94/#150/#123/#99 vorhanden sind. Priorisiere tatsächliche Bugfixes und die ausdrücklich vereinbarten Live-Icon-Rail-, Magazin-EPG- und echten Catch-up-Funktionen. Gib eine klare ausführbare Codex-Arbeitsanweisung und später eine schlanke Android-Delta-Abnahme. Nicht ohne ausdrückliche Freigabe mergen oder releasen; Nutzerdaten/Originalicon und bisherige PASS-Funktionen bewahren.
