# XCMate – Codex-Übergabe: Provider-/CDN-Redirects und freie Download-Zielwahl
**Stand:** 24.10.2026 · **Produktiv:** `main`, XCMate **0.1.29.28** · **nächster *vorgeschlagener* Teststand:** `0.1.29.29` (nur sofern frei; Version vor Build erneut abgleichen).  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate · **Add-on-ID:** `plugin.video.xtreammate`.  
**Zielgerät:** Android TV 13 / RK3528 ARM32 / Kodi 21.2 Omega / Titan BINGIE MOD 2.2.3 / IR-Fernbedienung.  
**Ausgangscommit bei Erstellung:** `c3fcdfb5efc011ea5733b140b6a94ccd1279b2db`; vor Implementierung stets aktuellen `main`-HEAD und alle Draft-PRs neu lesen.

## 1. Priorität und gesicherte Gerätedaten (kein falscher PASS)
Der Nutzer hat ein **einseitiges privates PDF-Bild** des XCMate-Dialogs **„Downloads verwalten“** vorgelegt. Das Bild ist lesbar und zeigt mindestens **einen gescheiterten Download mit `0 / 0 MiB` und abgeschnittenem `REDIRECT_UNSU…`**. In `download_worker.py` existiert exakt `DownloadFailure('REDIRECT_UNSUPPORTED')` für Cross-Origin-Redirects. Weitere gescheiterte Downloadzeilen sind sichtbar, deren ganze Fehlercodes/Root Causes **nicht** vollständig im Bild enthalten. **Die PDF ist nicht öffentlich ins Repository hochzuladen**, weil Dateinamen und Inhalte personenbezogen/vertraulich sein können.

**Zusätzliche reale Nutzerbeobachtungen:**
- **Das linke Detailmenü lässt sich in .28 öffnen**; Fenster „Downloads verwalten“ ist sichtbar. **Teil-PASS** für Menü-Öffnung/Erreichbarkeit; weder vollständiger M01–M03-/#131-Abschluss noch Film-/Folgen-Downloads oder Poster-Fallback damit bewiesen.
- Der Nutzer möchte **USB-Stick** und **eingebundenes Samba/SMB-Laufwerk** als Speicherziel wählen. Der Auswahlvorgang akzeptiert diese Ziele nicht bzw. bietet wieder einen **internen System-/Kodi-Ordner** an. Keine nachgewiesene erfolgreich abgeschlossene externe Aufnahme oder Downloadübertragung.
- Externer Ziel-Fail und HTTP-`REDIRECT_UNSUPPORTED` sind **zwei getrennte Blocker**. Ein Redirect-Fehler wird nicht durch Umschalten des Speicherorts behoben; die Speicherzielreparatur beweist nicht, dass eine Medienquelle downloadfähig ist.
- Ältere vollständig übermittelte .27-Abnahme bleibt **13 PASS / 15 FAIL / 0 NOT_TESTED**; .28-Gerätecheckliste wurde noch **nicht vollständig ausgefüllt**. Kein künstlicher .28-Gesamtscore.
- .27 Search-Live-Reparatur **A01–A08 PASS** und #125 abgeschlossen; Benutzerportale, Gruppen, EPG, Favoriten, Resume, Serien-Staffelautoplay und Original-XCMate-Icon geschützt.

## 2. Vorhandene Issues
**P0 #135:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/135  
Download-Abbruch `REDIRECT_UNSUPPORTED` bei möglicherweise legitimer Provider→CDN-Weiterleitung. **Noch kein Redirect-Ziel oder Host-Trust bewiesen.**

**P1 (für Nutzer-Downloadablauf faktisch prioritätskritisch) #136:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/136  
USB-/SMB-Zielwahl und sichere Speichermodelle, bei Wunsch **separater Downloadordner**, kein stillschweigender interner Rückfall.

**Verwandt und weiter offen:** #63 Download-End-to-End; #126 Direct-TS-Sofortaufnahme; #131 Menü/Native-Fokus-Gesamtprüfung; #111 Poster-Fallback.  
Nachgeordnet, aber nicht vergessen: #127 Rich Search Results, #43 verbindlicher Plug-and-Play-Wizard, #120 Kodi-BINGIE-Live-Shortcut, #122 Lightweight-Splash, #123 EPG-Sendungsdetails, #98 manuelle EPG-Zuweisung, #115 Premium-Fokus.

## 3. P0-A: Download-Redirect reparieren – ohne Sicherheitsrückschritt
**Code:** `src/plugin.video.xtreammate/resources/lib/download_worker.py::SameOrigin.redirect_request`:
```py
validate(newurl); before,after=urlsplit(req.full_url),urlsplit(newurl)
if (before.scheme,before.netloc)!=(after.scheme,after.netloc):
    raise DownloadFailure('REDIRECT_UNSUPPORTED')
```
Das verweigert jede origin-übergreifende HTTP-Weiterleitung, auch falls der Provider tatsächlich einen autorisierten CDN-Host verwendet. Ein legitimer CDN-Zielhost ist **nicht** aus dem PDF zu erkennen. `download_sources.py::resolve/validate` und `download_worker.py::open_source/run_one` prüfen.

**Codex-Auftrag:**
1. **Anonymisierte Redirect-Telemetrie:** Ereignis `DOWNLOAD_REDIRECT`, Redirect-Statusklasse, Hop-Zahl, same-/cross-origin, Schema, konkrete Policy-Reason-Codes. **Keine vollständigen Quell-/Ziel-URLs, Hostnamen, Tokens, Query-Parameter, Benutzer-, Portal- oder Titel-IDs in öffentlichen GitHub-Logs.** Sensible Diagnose ausschließlich privat.
2. Implementiere eine **eng begrenzte, nachvollziehbare Vertrauensermittlung** für vom aktiven Anbieter tatsächlich autorisierte CDN-/Medienserver-Weiterleitungen (z. B. nachweislich aus Provider-Konfiguration/API stammende Allowlist oder explizite vertrauenswürdige Nutzerfreigabe für Zielhost). Keine pauschale `follow all redirects`-Freigabe. Benötigte Freigaben im UI verständlich, widerrufbar und portalbezogen.
3. Redirect-Kette begrenzen, Endziel nach jedem Hop validieren: nur `https` bzw. bewusst zulässiges `http` nach Sicherheitsvertrag; kein HTTPS→HTTP-Downgrade; kein `file:`/`ftp:`/`smb:`, kein Localhost/privates Netz/unsichere IP-Domain/DNS-Rebinding außer explizit autorisiertem vertrauenswürdigem LAN-Fall. **Cross-Origin nie automatisch Authorization, Cookies, BasicAuth oder vertrauliche Provider-Header übertragen; keine Credentials im Redirect-Ziel sammeln oder persistieren.** Header/Origin-Regeln pro Hop prüfen.
4. Response weiter über bestehende Content-Type-/Content-Length-/Dateiheader-, Magic-/DRM-/Container-, Dateigrößen-/Freiplatz-, Range/ETag-/Teilhash-, no-overwrite- und sichere Finalisierungsprüfungen leiten. Redirect mit fehlendem/mutierendem Validator darf nicht unkontrolliert an frühere Teildateien angehängt werden. Bei Blockade klarer Code z. B. `REDIRECT_UNTRUSTED_TARGET`, `REDIRECT_DOWNGRADE`, `REDIRECT_HOP_LIMIT`, `REDIRECT_PRIVATE_ADDRESS`, statt generischem UI-Text.
5. Tests mit Mock-/lokalem HTTP-Server: gültiger Cross-Origin-CDN-Redirect (ggf. ausdrücklich vertrauenswürdig), mehrfacher Hop, Loop, Cross-Origin-Header-Leak, private IP, Downgrade, relative Redirects, fehlender/ungültiger Content-Length, Quellwechsel, Resume-Validator, Download-Offline-Playback. **Host-CI-PASS ist kein Android-PASS.**

**Geräte-Gate RDX01:** Ein rechtmäßig herunterladbarer Testfilm über tatsächlich autorisierten Provider/CDN-Redirect erreicht nach zustimmungsbasierter Freigabe `RUNNING`, Bytes >0, `COMPLETE`; lokale Wiedergabe inkl. Neustart offline.  
**RDX02:** Eine einzelne Serieepisode aus gleichem Portal unter gleichen Regeln.  
**RDX03:** Unerlaubte Redirects werden ohne Header-/Token-Leak und ohne zweites Schreiben abgelehnt.

## 4. P1-B: USB- und Samba-Downloadziele nutzbar machen
**Bereits verifiziert in .28 `main`:**
- `home_menu.py::recording_folder()`: Kodi-`browseSingle(...,'files')`, `xbmcvfs.translatePath()`, `capture_target.probe()`. Bei Probe-FAIL wird `compatible_default()` angeboten – **internes Ziel**, nicht USB/SMB.
- `downloads.py::folder()` = `capture_target.configured()` = bisher einzige Einstellung `recordings_folder`. Kein getrenntes Downloadziel.
- `atomic_media.probe()`: verlangt absoluten POSIX-Pfad und native NoFollow-/fsync-/`RENAME_NOREPLACE`- oder sichere Hardlink-Publikation, verweigert URIs `'://'`.
- `media_files.py` hat grundlegende `xbmcvfs`-Reader/Writer, aber `probe()` und `rename()` sind in produktiven Downloadpfaden **weiterhin POSIX-only**. Ein passender Kodi-Browser-Eintrag oder einfacher VFS-Schreibtest reicht für sichere Atomizität/Resume auf SMB **nicht** aus.

**Auftrag:**
1. **Ziele getrennt anbieten:** Einstellungen „Aufnahmeziel“ (bestehende `recordings_folder` unverändert) und „Downloadziel“ (neue **optionale** Einstellung, kompatibler Standard = bisheriger gemeinsamer Ordner). Benutzer kann gezielt USB, SMB oder intern wählen. Das aktuelle Verhalten bestehender Installationen darf nicht automatisch umgestellt werden. Konfigurierbare Unterordner/Mediennamen sinnvoll. Kein Datenreset oder heimlicher Ordnerwechsel. Aufzeichnung und direkte Downloads brauchen je eigene ausgewiesene Fähigkeiten.
2. Kodi-Quellenbrowser mit sichtbaren **lokalen Volumes, USB und konfigurierten SMB-Freigaben**; wenn die Android-Dateizugriffsfreigabe/SAF/Mounts nicht erreichbar sind: deutliche, konkrete Diagnose und empfohlene Freigabeschritte statt erzwungener interner Standardordner.
3. **USB lokal**: Mount/Android-Berechtigungen, POSIX vs SAF, FAT32 4 GiB-Dateilimit, Schreibfähigkeit, freien Speicher, Nichtüberschreiben, Symlink-/Pfadschutz, sichere Finalisierung prüfen. Vermeide harte Annahme, jeder USB-Mount erlaube alle Linux-Operationen. Kann ein Volume den Vertrag nicht erfüllen, klaren Grund nennen und ggf. ein nachweislich sicheres, explizit bestätigtes Staging-Modell anbieten.
4. **SMB via Kodi-VFS**: VFS-URI getrennt von lokalen POSIX-Pfaden behandeln. Entwickle ein **eigenes sicheres SMB-Zielbackend** oder **lokales Staging und kontrollierte finale Übertragung**. Anforderungen: eindeutiger Zielname ohne Überschreiben, vorherige freie Kapazität für Staging, Größe + SHA256-Verifikation nach Netzwerkkopie, Resumesemantik bei Trennung, sauberes „partial/failed“ statt irreführendem COMPLETE, Kollisionsschutz bei parallelen Aufträgen, keine unbestätigte SMB-Atomic-Rename-Garantie. VFS-Kopiermethoden nur so verwenden, dass sie nachweislich auf Kodi 21.2 Android funktionieren. Prüf-/Verifikationsfehler = nicht freigeben.
5. **Download-UI**: Zieltyp und Backendfähigkeit verständlich anzeigen (`READ`, `WRITE`, `PUBLISH`, `CAPACITY`, file-size-limit, Offlinefähigkeit, Resume). Auswahl/Validierung und Einzeldownload tatsächlich auf gewählten USB/SMB persistent speichern. Keine Netzwerk-Passwörter oder Freigabe-/Provider-URLs in öffentlichen Logs. Option, abgeschlossene Dateien im Zielordner lokal bzw. über Kodi-VFS abzuspielen, ohne nicht vorhandenen Offline-Zugriff für SMB zu versprechen.
6. Aufnahmeengine #126 nicht unkontrolliert auf SMB umbiegen. Direct-TS benötigt ggf. ein anderes Backend; getrennte Verfügbarkeitskennzeichen, Test und explizite Einschränkung.

**Geräte-Gates:**
- **ST01:** Internes bestehendes Ziel wird unverändert übernommen, Einstellungen intakt.
- **ST02:** USB auswählen und persistent speichern; direkter Filmdownload >0 Bytes → COMPLETE; lokale Wiedergabe und nach Kodi-Neustart ohne Netzwerk (wenn physisch USB weiter angeschlossen).
- **ST03:** SMB-Share wählen, Zielordner behalten; direkter Filmdownload >0 Bytes → COMPLETE; aus Kodi/VFS abspielen; Netzwerkunterbrechung erzeugt nicht `COMPLETE`. **SMB ist netzabhängig und kann nicht ohne erreichbares Netzlaufwerk offline abgespielt werden.**
- **ST04:** Individueller Downloadzielordner unterscheidet sich vom Aufnahmeordner; beide validieren unabhängig, bestehende Aufnahmen/Downloads unverändert.
- **ST05:** FAT32 >4GiB, kein Platz, read-only, USB entfernt, SMB-Offline, Zielkollision und unautorisierter Pfad jeweils sichere, erklärende Fehlermeldung, keine Altdatei überschrieben.

## 5. Laufende .28-Geräteabnahme – differenziert fortführen
**Bestätigter Teilstand (keine vollständige 30/30-Auswertung):**
- Sichtbarer **Menü-/Downloads-Verwaltungsweg** funktioniert nach Nutzerangabe (früherer C01-Fail in .27). #131 als Teil-PASS dokumentiert, **nicht geschlossen** bis M01–M03/Poster-Menüfunktionen vollständig geprüft sind.
- Der konkrete `REDIRECT_UNSUPPORTED`-Fehler im Screenshot blockiert **mindestens einen** aktuellen Download. Die abgeschnittenen Fehlercodes anderer Zeilen nicht erraten.
- USB/SMB im Picker nicht als gespeichertes funktionierendes Ziel bestätigt.
- **NOT_TESTED (bzw. bisher nicht nachgewiesen)**: tatsächliches COMPLETE eines Films/einer Folge, Pause/Resume, Offline-Wiedergabe, 2-minütige Direct-TS-Aufnahme und Cover-Alternativretry. Kein Behaupten erfolgreicher Tests.
- Historisch .27 A01–A08 PASS, #125 geschlossen; **Originalicon, EPG-Guide/Sendestart, Live-IR/Overlay, Serien-Autoplay/Stop/Resume, Portal- und Gruppendaten** unverändert.

## 6. PRs, Auslieferung und Abnahme
1. Von aktuellem `main` **zwei kleine Draft-PRs** (#135 Redirect-Policy und #136 Storage-Backends) und bei Bedarf einen klar gekennzeichneten Integrations-/Testkandidaten. Keine ungeprüften WIP-/Premium-Branches mergen.
2. CI/Mocks plus reale, kontrollierte HTTP-Redirect- und Filesystem-/USB-/SMB-Test-Fixtures, ZIP mit vollständiger Quelle, SHA256, reproduzierbarer Build, Testbericht, Android-Checkliste mit **PASS/FAIL/NOT_TESTED**. Jede Ziel-/Verbindungsart explizit mit Capability dokumentieren. Host-Tests nicht als reale Android-Bewertung darstellen.
3. **Nächste Testversion voraussichtlich 0.1.29.29**, sofern frei; keine öffentliche Repository-Publikation und **kein Merge ohne erneute Nutzerfreigabe**. Bestehende .28-ZIP und Index nicht überschreiben. Benutzerinstallationen nicht deinstallieren/zurücksetzen.
4. Bei Scheitern reproduzierbarer Testschritt, sichtbarer `CODE@STAGE:ERRNO` oder Redirect-Reason, nur **anonymisierte** Stufen in öffentlichem Issue; Rohlogs und Bild-PDF privat belassen.
5. **Reihenfolge für Android:** Menü-Einstieg kontrollieren → separaten Downloadziel-Picker USB/SMB prüfen → Provider/CDN-Redirect-Download auf internem kompatiblen Speicher end-to-end bestätigen → Filmdownload auf USB/SMB → Einzelfolge / Retry / Pause / Resume / Dateigrenze → Aufnahme nach eigenen TS-Regeln → Poster-Retry → eingefrorene Suche-/EPG-/Autoplay-Regression.

## 7. Nicht vergessen: vollständige nächste Baureihe (eigene PRs)
- **#127 Pflicht:** visuelle Suchergebnis-Zeilen mit Senderlogos/Jetzt-EPG und kleinen Film-/Serienpostern, verifizierten Sprach-, Qualitäts-, Quellen-, Jahr-/Staffeldaten. D-Pad-schnell, Cache-first, bestehende Live-Suche PASS.
- **#43 Pflicht:** vollständiger automatisch startender Plug-and-Play-Wizard (Xtream/M3U/Stalker, Checkboxgruppen, nur ausgewählte Importe, Anbieter- und externe EPG/Matching, progressive Cover/Metadaten, Fortschritt, Startgruppe/-sender, sicherer Abschluss/Rollback; saubere frische Kodi-Neuinstallation als reales Test-Gate).
- **#120** schneller Titan-BINGIE-MOD Live-TV-Startknopf und korrekter Rücksprung.
- **#122** originaler Space-Splash als Lightweight-Hintergrund, Original-XCMate-Icon bewahren.
- **#123** EPG-Programmzeitschrift-Detailseite mit Poster/Senderlogo und Rücksprung zum selben EPG-Fokus.
- **#98** manuelle EPG-Quellenwahl je Sender, Vorschau vor verbindlicher Speicherung.
- **#111** selektiver Poster-Retry/Fallback, reale Android-Bildprüfung; **#115** Space-Premium Fokus/OK separat.
Diese Funktionen **nicht** aufgrund der .29-Download-Hotfixes als integriert oder fertig bezeichnen.

## 8. Direkt ausführbarer Codex-Auftrag
**Bitte jetzt mit Code, Tests und Draft-PRs beginnen, nicht nur erneut ein Konzept liefern:**  
(1) Issue #135: vertrauensgebundener, limitierter und credential-sicherer CDN-Redirect mit Android-Test.  
(2) Issue #136: vom Nutzer explizit wählbare interne, USB- und SMB-Downloadziele mit eigenständigen sicheren Capability-Prüfungen, getrennte Aufnahme-/Downloadzielwahl und testbarem Offline-/Netz-Verhalten.  
(3) Download vollständig über beide Fixes prüfen, jeweils ein Film und eine einzelne Folge.  
(4) Testergebnisse für #131/#126/#111 korrekt begrenzen; alle bisherigen PASS bewahren.  
(5) Anschließend Roadmap #127/#43/#120/#122/#123/#98/#115 in unabhängigen PRs vorbereiten/umsetzen.  
**Kein ungefragter Merge oder Release.**

---
**Verweise auf bestätigten Vorstand:** `docs/XCMate/ANDROID_TEST_02928_C_DE.md`, `docs/XCMate/ANDROID_ABNAHME_02927_20261023_NUTZERERGEBNISSE_DE.md`, `docs/XCMate/CODEX_UEBERGABE_02928_ANDROID_P0_DOWNLOADS_AUFNAHME_20261023_DE.md`, PR #134 (gemergte .28), Issues #135/#136.
