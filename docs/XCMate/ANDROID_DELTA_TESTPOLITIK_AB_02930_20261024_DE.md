# XCMate – Verbindliche Android-Delta-Abnahme ab Version 0.1.29.30
**Stand:** 24.10.2026 · **Master-Issue:** [#143](https://github.com/artattakk-creator/kodi-noodleprivate/issues/143) · **Inventur:** [ISSUE_AUDIT_KONSOLIDIERUNG_20261024_DE.md](ISSUE_AUDIT_KONSOLIDIERUNG_20261024_DE.md).

## Warum keine 28–50 Standard-Checkboxen mehr?
Die letzte reale Nutzerabnahme v0.1.29.29 ist vollständig dokumentiert: **12 PASS / 16 FAIL / 0 NOT_TESTED**. 28 Markierungen waren nicht 16 unabhängige Defekte: z. B. USB-/SMB-Zielwahl (LINK:38) blockierte späteres Film-/Folgen-Download-/Offline-End-to-End. Menü M01–M03 3/3 PASS, die neun übrigen Baseline-Tests A01/A02/A04–A08/REG01/REG02 PASS, **A03 FAIL**. Keine nachträglichen Änderungen an historischen Scores.

## Pro Testkandidat nur 5 kurze Grundprüfungen
**S1 START** – XCMate-Home startet, reagiert auf IR und lädt Portale ohne Freeze/Absturz; kein Account-Reset.
**S2 MEDIEN** – Filme und Serien öffnen → eine Detailansicht → Menü/Back/Fokus, keine blockierende Pop-up-Schleife.
**S3 LIVE** – Ein bekannter TV-Sender aus XCMate-Suche starten, Info-/Links-Grundbedienung, Stop/Back.
**S4 EPG-GUIDE** – Großer EPG öffnet, Sender über „Jetzt ansehen“ startbar und Wiedergabe beendet. **Dies ist nicht Test A03 der globalen Jetzt-Sendungstitelsuche!**
**S5 ERHALT** – Original-XCMate-Icon, bestehende Portale/Gruppen, EPG-Mappings, Favoriten, Resume und Staffelautoplay-Einstellung vorhanden (nur Sicht-/Persistenzprüfung, keine erneute ganze Serie abspielen).

**Status:** je `PASS`, `FAIL` oder `BLOCKED / NOT_TESTED` mit Versionsnummer/Datum. Bei fehlendem Gerätetest `NOT_TESTED`. Die fünf Smoke-Checks pro Kandidat sind die einzige wiederkehrende Basisprüfung.

## Delta-Matrix: nur geänderte Module sowie offene Fehlergates
| Geänderte Funktion / Issue | Zusätzlich zu S1–S5 **genau diese** Realgerätetests | Nicht routinemäßig wiederholen |
| --- | --- | --- |
| **#141 Portal MemoryError / service / scheduler** | D-MEM1 Kodi ARM32 Idle mehrere Stunden + RSS/PSS/Portal-Loads und 0 MemoryError; D-MEM2 Neustart/Service-Upgrade + UI-Start stabil | 20x normales Menü-/Back-Drücken ohne neuen Hinweis |
| **#136 Speicherpicker USB/SMB/Staging** | D-ST1 **Laufwerksübersicht direkt öffnen** / getrennte Aktionen Aufnahme-/Downloadziel; D-ST2 USB wählen, speichern, Kodi neu starten, Datei vollständig/lesbar; D-ST3 SMB-Quelle wählen, persistieren, echt übertragen/lesen; D-ST4 kein stiller interner Rückfall / klare `LINK:38`-Diagnose; D-ST5 sicherer Netzabbruch/Retry | Ganze EPG-/Autoplay-Matrix |
| **#135 & #63 Download/CDN/VOD-Worker** | Erst nach positivem Ziel: D-DL1 autorisierten Film mit CDN-Gate / Bytes >0 / COMPLETE; D-DL2 eine echte Folge / richtige Staffel/Nummer; D-DL3 Pause, Abbruch, Resume, Retry; D-DL4 Film/Folge lokal USB nach Neustart offline; SMB nur mit erreichbarem Server | Grund-Menüfunktion als separates 10er-Set |
| **#126 Direct-TS-Sofortaufnahme** | D-REC1 unterstützter MPEG-TS-Sender + geeigneter Aufnahmeordner → Bytes >0, ~2 Minuten; D-REC2 Stop/atomisch complete; D-REC3 lokale Wiedergabe und Offline; D-REC4 sichere Unterbrechung | CDN-Tests, sofern keine Source-/HTTP-Änderung |
| **#140 globale Suche nach NOW-EPG-Titel** | D-EPG1 Titel aktuell laufender Sendung im großen EPG ablesen, exakt im globalen Live-Suchbereich eingeben; D-EPG2 Treffer korrektem Sender zuordnen und starten; D-EPG3 fehlende EPG-/Quelle-Status und Zähler prüfen | 8 unveränderte Suchen nach `Upload` |
| **#111 Poster/Artwork** | D-ART1 ein wirklich fehlendes Poster gezielt retryen; D-ART2 reale alternative Provider-Bildadresse oder klarer Fehler; D-ART3 READY-Poster und Cache nach Neustart erhalten | Download-E2E ohne Source-/Speicherberührung |
| **#122 Lightweight-Hintergrund** | D-UI1 Home, D-UI2 Film, D-UI3 Serie, D-UI4 Suche und lesbarer Text mit identischem **Original**-Space-Splash; Icon/Offline bleibt | UI-Layout anderer Skin-Pakete |
| **#142 Sprachdatei** | D-I18N1 deutschen/englischen SMB-Prompt öffnen, keine `POParser`-Warnung; ausreichende Beschriftung / keine Credentials in Logs | Real-SMB-Transfer als Übersetzungsnachweis |
| **#43 Erststart-Wizard** | D-SETUP1 **frisches, isoliertes Kodi-Profil**, Xtream/M3U/Stalker, Gruppen/EPG/Artwork/Save, READY, Rollback; niemals produktive Nutzerkonten zurücksetzen | Auf produktiver Hauptinstallation ohne Backup neu aufsetzen |
| **#127 bebilderte Suche** | D-SRCH1 Logos/Now/Qualität bei echten Daten, D-SRCH2 Film-/Seriencover und verifizierte Metadaten, D-SRCH3 D-Pad/Performance; A03 #140 bleibt eigener Fehler | komplette Staffel-Autoplaysequenz bei reinem Layoutdiff |
| **#17/#79 Live-Overlay oder VOD-Player-Owner** | Geräte-IR mit 1×/2× OK/Links/Back, Fokus, realem Stop/Resume und fremdem Player; nur bei Änderung an Overlay/Player | alle EPG-Feeds aus unterschiedlichen Ländern |
| **#58/#60/#88/#98 Guide-Daten/-Zuordnung** | Quelle/Mapping/Now-Next/Fallback, eine konfliktbehaftete Kanal-ID, Guide-Raster-Start/Back, konkrete 7–10 Tage nur mit wirklichen Daten; niemals unspezifisches „EPG PASS“ für alle Kanäle | unberührte Film-/Serien-Downloads |

## Automatische PR-Risikokennzeichnung für Codex
Codex soll für jeden Draft-PR **Diff-basierte Impactliste** erstellen: betroffene Pfade `src/plugin.video.xtreammate/resources/lib/*.py`, Skin-XML, Sprachpaket, Packaging/Repopublish, Settings-/DB-Migrationen. Nur tatsächlich betroffene Delta-Gates aus Tabelle + S1–S5 als Android-Protokoll. Bei gemeinsamen Abhängigkeiten (z. B. Speicher-Backend für Capture und Downloads) beide relevanten Gatings aufnehmen; bei neuen P0-Abstürzen oder Player-/Profil-Migrationen Sicherheitsmatrix erweitern und schriftlich begründen.

**Status- und Schließregeln:** `ANDROID_PASS` nur nach echter Ausführung, `CI_ONLY` niemals PASS, `BLOCKED/NOT_TESTED` bei Vorbedingungsfehlern, `CLOSED_CONSOLIDATED` ist nur Tracking und nicht technische Fertigstellung. Geschlossene historische Issues (#42/#85/#131 und davor #67/#73/#97/#125) sind **eingefrorene Baseline**, nur neue reproduzierbare Regressionen lösen gezielten erneuten Gerätetest aus.

## Minimale Kopiervorlage für nachfolgende Nutzer-Tests
```
XCMate <Version> / Kodi 21.2 / Android 13 RK3528 – Delta-Abnahme
PR/Module: <Liste>
S1 START: PASS/FAIL/NOT_TESTED
S2 MEDIEN: PASS/FAIL/NOT_TESTED
S3 LIVE: PASS/FAIL/NOT_TESTED
S4 EPG-GUIDE: PASS/FAIL/NOT_TESTED
S5 ERHALT: PASS/FAIL/NOT_TESTED
Nur betroffene D-Tests: <IDs und Ergebnisse>
Vorblocker / Fehlercode: <ohne Portal-/SMB-/Personendaten>
NICHT erneut geprüft: <durch unveränderten Code geschützte Baseline>
```
**Kein Merge/Release ohne gesonderte Nutzerfreigabe und dokumentierte Android-Abnahme der für den Release relevanten P0-Gates.**
