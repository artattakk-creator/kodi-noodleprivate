# XCMate – zentraler Projekteinstieg

> **Lizenz-/Herkunfts-Audit 19.10.2026:** [Vollständiger Datei-/Codevergleich XCMate 0.1.25 und unabhängiger V2-Umbauplan](CODE_ORIGIN_LICENSE_AUDIT_025_DE.md) · [Rechteklärungs-Issue #19](https://github.com/artattakk-creator/kodi-noodleprivate/issues/19). Der früheste GS-Media-Fork-Snapshot (13.10.) verglichen mit 0.1.25 ergibt 6 Python-Module bytegenau unverändert und teils hohe Altzeilen-Überlappung in `main.py`, `player.py`, `epg.py`. **Dringender offener Rechtekonflikt:** Upstream-`addon.xml` deklariert GPL-2.0-only, aber mr-evil1s Root-`LICENSE` vom 01.10.2026 sagt „Alle Rechte vorbehalten“ und untersagt Kopieren/Modifizieren ohne schriftliche Genehmigung. **Kein rechtsgültiger Schluss zugunsten einer Lizenzvariante; keine Umstellung auf proprietär, keine Entfernung der Herkunftshinweise.** Externe juristische Prüfung der Rechtekette und Original-ZIP-Vergleich erforderlich. Dieses Audit ist separat von der XCMate-0.1.25-Android-Abnahme; **Produktionscode und Lizenzdateien unverändert**.

> **RELEASE-STATUS 18.10.2026 – VERBINDLICH:** **XCMate 0.1.25 ist über `main` im GS Media Kodi Repository veröffentlicht.** [PR #18](https://github.com/artattakk-creator/kodi-noodleprivate/pull/18) gemergt (Merge `601c421b004f746341ecf3a8c0f7bf1200a7c84d`), [237 CI-Tests bestanden](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39155542397), [Publish-Workflow erfolgreich](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39156573306); `addons.xml` = `0.1.25`. ZIP `plugin.video.xtreammate/plugin.video.xtreammate-0.1.25.zip` vorhanden, SHA-256 **`0022633e056940fb6a338b1d5ccb01ce2585d6093652242e7579b0b5b7418ae3`** unabhängig verifiziert. **Android-TV-Abnahme 0.1.25 steht aus**: EPG, zwei OK-Stufen, Fokus, Logo, Fortschritt, schnelle linke Liste und andere Add-ons am Fernseher prüfen. Aussagen „0.1.25 nur Testkandidat / produktiv 0.1.24“ darunter sind **historische Entwicklungsangaben**. [Implementierungsbericht](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md), [aktueller Status](CODEX_STATUS_CURRENT_DE.md).

**Aktuelle Entwicklung 0.1.25:** [Entwurfs-PR #18](https://github.com/artattakk-creator/kodi-noodleprivate/pull/18), GitHub-CI erfolgreich.  [Implementierung, 237 Tests, Paket und Android-Testplan](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md) auf `fix/xcmate-infobar-epg-navigation`. Zweistufige TV-Bedienung und lokale EPG-/Quellenvorschau implementiert. **Noch nicht auf main / nicht am Android-TV abgenommen; produktiv bleibt 0.1.24.**

**Status:** 18.10.2026: **XCMate 0.1.24 ist auf `main` und im GS Media Kodi Repository veröffentlicht** ([PR #16](https://github.com/artattakk-creator/kodi-noodleprivate/pull/16), 213 GitHub-CI-Tests erfolgreich; [Publish-Workflow](https://github.com/artattakk-creator/kodi-noodleprivate/actions/runs/39143872867) erfolgreich). Der reale Android-TV-Test zeigt erstmals eine sichtbare XCMate-Sidebar mit Fokus und unterem OSD; **nicht vollständig abgenommen**, da EPG und Fernbedienung noch nicht stabil sind. Issue #12 offen. EPG-Quellfehler genauer diagnostiziert, vollständige Vorschau Issue #13 und XCMate Skin Issue #14 bleiben offen.
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Kodi-Repository:** GS Media Kodi Repository 1.7.0  
**Angezeigter Add-on-Name:** XCMate  
**Technische ID:** `plugin.video.xtreammate` (aus Kompatibilitätsgründen NICHT ändern)

Diese Dateien sind die verbindliche Arbeitsgrundlage für spätere Chats und Entwickler. **Zuerst [`CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md`](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md) als aktuellen Codex-Arbeitsauftrag und [`CODEX_STATUS_CURRENT_DE.md`](CODEX_STATUS_CURRENT_DE.md) für den Release-/Projektstand lesen**, danach `KODI21_FIX_022_DE.md`, `PROJECT_HANDOFF_DE.md` und `ROADMAP_AND_QA_DE.md`. Ältere Dokumente enthalten historische Versionsstände.

**Verbindliche nächste Ausbaustufen:** [EPG-Status & Vorschau – Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13) **vor** [XCMate Skin – Issue #14](https://github.com/artattakk-creator/kodi-noodleprivate/issues/14). Beides geplant, noch nicht implementiert. Der Live-TV-Navigationsfehler wurde auch mit 0.1.23 bestätigt und bleibt in [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) offen.

**Aktuelle Bearbeitung:** [0.1.24 Kodi-21-Fix, 213 Tests und Android-Abnahmeplan](KODI21_FIX_024_DE.md) über [gemergten PR #16](https://github.com/artattakk-creator/kodi-noodleprivate/pull/16). **Normales Kodi-Repositoryupdate ist verfügbar**; Android-Abnahme noch offen. Issue #12 und #13 nicht schließen.

**NEUER Android-TV-Praxistest zu 0.1.24 (18.10.):** Echte XCMate-Senderliste, Fokusmarkierung, untere OSD-Leiste und Zusatzmenü werden erstmals sichtbar über laufendem TV dargestellt. **Noch nicht abgenommen:** zuverlässiger D-Pad-Kanalwechsel/Bedienung und EPG-Titel. Der `XCMate · EPG`-Modus zeigt derzeit nur die Senderliste ohne Jetzt/Danach; Codex soll fehlenden Kurz-EPG-Fallback und Quellenstatus untersuchen. [Gerätetest und Folgeauftrag](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md) · [Issue #12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12) · [Issue #13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13).

**Neue verbindliche Bedienvorgabe:** [TV-OSD/EPG/Performance-Spezifikation](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md) und [Umsetzungs-Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17). **1× OK:** Senderinfo mit Icon, Jetzt/Danach, Laufzeit/Fortschritt. **2× OK bzw. Runter bei geöffneter Info:** untere Player-Bedienleiste. **Links:** schneller lokaler Senderkatalog mit Jetzt, Von–bis und EPG-Fortschritt. Erst funktionsfähige EPG-Daten, dann finaler UI-/Skin-Ausbau. Noch nicht implementiert.

**AKTUELLER CODEX-ARBEITSAUFTRAG:** [CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md](CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md) – verbindlich zuerst lesen. 
**Gerätestand 0.1.24:** Echte TV-Senderliste, sichtbarer Fokus und untere Steuerung sind erstmals bestätigt; **EPG und Navigation noch nicht stabil**, Senderliste langsam. Ziel: 1× OK Infobar, 2× OK/Runter Bedienleiste, Links EPG-Senderliste. [Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17), [#13](https://github.com/artattakk-creator/kodi-noodleprivate/issues/13), [#12](https://github.com/artattakk-creator/kodi-noodleprivate/issues/12).

## Dokumente

- [0.1.25: implementierter TV-/EPG-Testkandidat und vollständige Android-Abnahme](IMPLEMENTIERUNG_025_TV_INFOBAR_EPG_DE.md)

- [**Codex-Arbeitsanweisung: Infobar, EPG-/Menüstabilisierung, schnelle Senderliste**](CODEX_ARBEITSAUFTRAG_025_TV_INFOBAR_EPG_STABILISIERUNG_DE.md) – **verbindlicher Einstieg**.


- [NEU: verbindliche TiviMate-orientierte XCMate-Infobar, EPG-Liste, Tastenkonzept und Performance](TV_OSD_EPG_REMOTE_UX_SPEC_DE.md) – [Issue #17](https://github.com/artattakk-creator/kodi-noodleprivate/issues/17)

- [NEU: Android-TV-Test 0.1.24 – Overlay sichtbar, Navigation teilweise, EPG leer](ANDROID_DEVICE_TEST_024_EPG_NAV_DE.md)

- [0.1.24: implementierte Korrekturen, getrennte EPG-Analyse, Paket und Android-Abnahme](KODI21_FIX_024_DE.md)

- [Vollständige Android-TV-Codex-Übergabe 0.1.23 / P0 TypeError und EPG](CODEX_HANDOFF_ANDROID_023_P0_EPG_DE.md) – **erste Lektüre für Codex; bestätigte Gerätewerte, Kodi-ControlList-API und Abnahmetests**.

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
