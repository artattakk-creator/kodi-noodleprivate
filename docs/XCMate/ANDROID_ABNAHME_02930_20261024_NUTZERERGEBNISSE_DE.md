# XCMate – Android-Abnahme 0.1.29.30: 12 PASS / 15 FAIL / 1 BLOCKED / 1 NOT_TESTED
**Nutzerergebnis:** 24.10.2026. **Plattform:** Android TV 13, Kodi 21.2, Titan BINGIE MOD, IR-Fernbedienung. **Installiert:** XCMate 0.1.29.30, kumulativer Merge [PR #149](https://github.com/artattakk-creator/kodi-noodleprivate/pull/149).

## Unveränderte Originalbewertungen (29 Tests)
| Bereich | ID | Test | Nutzerbewertung |
| --- | --- | --- | --- |
| Grundprüfung / Smoke | S1 | XCMate startet | **PASS** |
| Grundprüfung / Smoke | S2 | Film- und Seriendetails | **PASS** |
| Grundprüfung / Smoke | S3 | Live-TV | **PASS** |
| Grundprüfung / Smoke | S4 | Großes EPG | **PASS** |
| Grundprüfung / Smoke | S5 | Benutzerdaten erhalten | **PASS** |
| Speicherziele / #136 | ST1 | Laufwerksübersicht erscheint | **NOT_TESTED** |
| Speicherziele / #136 | ST2 | USB-Stick wird gespeichert | **PASS** |
| Speicherziele / #136 | ST3 | Tatsächlicher USB-Dateizugriff | **FAIL** |
| Speicherziele / #136 | ST4 | Samba-Verbindung wird genutzt | **FAIL** |
| Speicherziele / #136 | ST5 | Fehler und Unterbrechung | **PASS** |
| Downloads / #135 #63 | DL1 | Film über erlaubten CDN-Redirect | **FAIL** |
| Downloads / #135 #63 | DL2 | Einzelne Serienfolge | **FAIL** |
| Downloads / #135 #63 | DL3 | Pause, Fortsetzen und Abbrechen | **FAIL** |
| Downloads / #135 #63 | DL4 | Offlinewiedergabe | **FAIL** |
| Downloads / #135 #63 | DL5 | Unsichere Weiterleitung blockieren | **FAIL** |
| EPG-Suche / #140 | EPG1 | Aktuellen Sendungstitel finden | **FAIL** |
| EPG-Suche / #140 | EPG2 | Kurzzeit-EPG-Fallback | **BLOCKED** |
| EPG-Suche / #140 | EPG3 | Richtiger Sender und Mapping | **FAIL** |
| Design und Sprache / #122 #142 | UI1 | Einheitliche Originalgrafik | **PASS** |
| Design und Sprache / #122 #142 | UI2 | Grafik dauerhaft und bedienbar | **PASS** |
| Design und Sprache / #122 #142 | PO1 | SMB-Dialog in Deutsch und Englisch | **PASS** |
| Aufnahme / #126 | REC1 | Live-TS-Aufnahme startet | **FAIL** |
| Aufnahme / #126 | REC2 | Aufnahme sicher stoppen | **FAIL** |
| Aufnahme / #126 | REC3 | Aufnahme bleibt erhalten | **FAIL** |
| Aufnahme / #126 | REC4 | Unterbrechung behandeln | **FAIL** |
| Poster / #111 | ART1 | Fehlendes Poster nachladen | **FAIL** |
| Poster / #111 | ART2 | Poster bleiben erhalten | **FAIL** |
| Stabilität / #141 | MEM1 | Vierstündiger Stabilitätstest | **PASS** |
| Stabilität / #141 | MEM2 | Service- und Neustartstabilität | **PASS** |

**Kontrollsumme:** 29 Tests, 12 PASS, 15 FAIL, 1 BLOCKED, 1 NOT_TESTED. Nicht rückwirkend korrigieren; Folgeblockaden zusätzlich separat erklären. Der **vorherige historische .29-Bericht** [12 PASS / 16 FAIL / 0 NOT_TESTED](ANDROID_ABNAHME_02929_20261024_NUTZERERGEBNISSE_DE.md) bleibt vollständig unverändert.

## Vom Nutzer zusätzlich berichtete reale Symptome
1. **Speicher/Downloads:** Auf USB und Kodi-Samba-Ziel wird das ausgewählte Speicherziel als **erreichbar und beschreibbar** erkannt. Bei Film-Download auf **beiden** Zielen sichtbare Meldung **`REDIRECT_UNTRUSTED_TARGET`**. **ST2 PASS** belegt explizite USB-Speicherung und Persistenz nach Neustart gemäß Testdefinition; **ST1 bleibt NOT_TESTED**, also noch keine eigenständige Bestätigung der vollständigen Laufwerks-Quellenübersicht. **ST3 und ST4 bleiben nutzerseitig FAIL**, aber **kein isolierter Write-/SMB-Protokollfehler** ohne tatsächliche Transferphase belegt. **ST5 PASS** gilt nur für den vom Nutzer als bestanden bewerteten Scope; keine unberichtete USB-Auszieh-/SMB-Netzunterbrechungs-Reproduktion erfinden.
2. **Redirect:** Im neuesten .30-Code `download_redirect.open_source()` ruft bei nicht autorisierter Cross-Origin-Verbindung `download_trust.remember(job_id,pid,source,target)`, markiert `REDIRECT_UNTRUSTED_TARGET` und bricht sicher ab. `download_trust` enthält **portal- und Quellorigin-gebundene pending/grants**, `grant/revoke`. Der Fehlertext ist daher **erwartetes Security-Deny bei bislang untrusted Zielhost** – nicht Beweis für defekte USB-/SMB-Speicherung, nicht automatisch ein Sicherheits-Fail und auch kein bestätigter legitimer CDN-Host. Nutzer hat **DL5 FAIL** markiert; offen bleibt die Bedienbarkeit/Verständlichkeit des Vertrauens-/Freigabe-/Widerrufs-Workflows sowie tatsächliche End-to-End-Transferfähigkeit. **Kein pauschales Erlauben aller Redirects, kein Abschalten von SSRF-/DNS-/TLS-/Credential-Schutz.** Externe Provider-Hosts und Tokens nicht öffentlich nennen.
3. **EPG-Suche:** Nutzer gibt einen **aktuell auf mehreren Sendern vorkommenden Sendungstitel** in die globale Suche ein und drückt OK: Ladeindikator, **Suchfenster verschwindet**, danach **XCMate-Startseite** statt sichtbarer Suchtreffer. **EPG1/EPG3 FAIL, EPG2 BLOCKED**. **Nicht** ausschließlich fehlendem Short-EPG/Mapping zuschreiben; GUI-/Window-Lifecycle und (stiller) Worker-/Search-Router-/Return-/Search-Handoff sowie `SEARCH_EPG`-Status prüfen. Baseline **S3/S4 PASS**: normaler Such-Live-Start und großer EPG grundsätzlich funktionieren.
4. **Poster:** **ART1 und ART2 FAIL**, konkreter Nutzertext **„Zeitüberschreitung der Anforderung“** nach einem Ladeversuch. Aktueller `media_art.fetch()` benutzt HTTP-Timeout/Budget; `retry_poster()` nur bereits **für denselben Eintrag gespeicherte Provider-Poster-URLs**. Nutzer verlangt künftig automatischen **TMDB-Fallback**, wenn kein eigenes valides Providerposter abrufbar ist. **Verbindliche neue funktionale Anforderung** nur bei **eindeutigem Film-/Serienmatch** mittels vertrauenswürdiger IDs bzw. Typ+Originaltitel+Jahr+weiterer Bestätigung; keine willkürliche Posterzuordnung bei Titelgleichheit, News, Live-Events, andere Staffeln/Remakes; TMDb-Lizenz, Attributions-/API-Bedingungen, API-Key-Schutz, Rate-Limit/Caching beachten. Fehlendes eindeutiges Match → ehrlich Platzhalter und Diagnose; kein globaler Cache-Reset, READY-Bilder bewahren. Auf IR-GUI keine synchronen API-Aufrufe. Der sichtbare Timeout muss diagnostisch in DNS/TLS/HTTP/Retry-Deadline unterschieden werden, ohne Provider-URLs zu loggen. **Aus dieser .30-Abnahme nicht ableiten, dass frühere READY-Poster tatsächlich gelöscht wurden**; ART2 FAIL ist Nutzerwertung, Details offen.
5. **Capture:** **REC1–REC4 FAIL**; kein bestätigtes Bytes>0/Stop/Replay. Beim .30-Fix ist USB-/SMB-Download-Staging ausdrücklich **nicht gleichbedeutend mit native Direct-TS-Capture-Publish**. Live-Senderformat und getrennte Capture-Zielprobe/Fehlergrund nicht ermittelt; nicht als vier unabhängige Root Causes interpretieren.
6. **Abgenommen:** S1–S5 **5/5 PASS**, Lightweight-Space-Splash+Persistenz+Icon **UI1/UI2 PASS** (#122), Deutsch/Englisch-SMB-Prompt **PO1 PASS** (#142), echte Nutzerangabe **MEM1 4 Stunden PASS und MEM2 Service-/Neustart PASS** (#141). CI-Hostprüfungen 1029 PASS aus PR #149 sind zusätzliche Evidenz, **kein** Ersatz für Android. **Kein numerischer privater RSS/PSS-/Portal-Read-/Thread-Snapshot wurde zusammen mit dieser Nachricht übermittelt.** Aussage über länger als vier Stunden unbelegte Stabilität vermeiden.

## Verbindliche technische Folgeaufträge
### P0 #135 / #63 – Freigabe und End-to-End
- Einen **untrusted Cross-Origin-Fall** aus dem privaten `download_trust.pending` vom UI sicher und ausdrücklich darstellen (nur nach Nutzerzugriff, klare Quelle/Zielorigin; keine URL-Pfade/Queries/Tokens). Herkunft und Vertrauenswürdigkeit unabhängig anhand Anbieterinformationen überprüfen; persistent **nur Portal+Source-Origin+Target-Origin** freigeben; gezielter Widerruf jederzeit. Aus Fehler `REDIRECT_UNTRUSTED_TARGET` keine automatische Generalliste oder blindes Allow bauen.
- Gerätetest: Film intern/USB/SMB, danach einzelne Episode, erlaubtes Cross-Origin-Redirect, Bytes>0/COMPLETE, SHA/Container/Replay, Pause/Resume und bewusstes Cancel; **DL5 separat** als untrusted->deny/grant/revoke prüfen. Ein Sicherheits-Deny kann korrekt sein, auch wenn kompletter Nutzerworkflow FAIL ist.
- Bei Download-Fehlerphase *vor* `TARGET_WRITE` USB/SMB nicht als Schreibdefekt verkaufen; backend_phase anonym `SOURCE_REDIRECT_DENIED` vs `STAGE_FAILED` vs `TARGET_COPY_FAILED` vs `COMPLETE` protokollieren.

### P0 #136 – Externe Speicherung
- **ST1 offen**: Sources-Root UI intern/USB/Kodi-SMB nachweisbar anzeigen und getrennte Aufnahme-/Download-Einstellung sichtbar. ST2 PASS schützen.
- Isolierten **kurzen erlaubten lokalen/vertrauenswürdigen HTTP-Testtransfer** ohne Cross-Origin-Abbruch auf ausgewähltes echtes USB und Kodi-SMB ausführen, Dateiexistenz/Größe/Hash/Wiedergabe prüfen. Erst das trennt Speicherbackend von Source-Trust. SMB nie als offline ohne Server bezeichnen, keine Gast-/SMB1-Rückstufung.
- ST3/ST4 nur nach echter Datei/Replay PASS; ST5-Randfälle ggf. gesondert. Sichere Stage-/NoOverwrite-Checks bewahren.

### P0 #140 – Globale Suche schließt und springt nach Home
- Beim Eingeben der EPG-Now-Sendung **direkt nach OK** auch Window-/Owner-/Prompt-`_search_root`/`_search_origin`-/`_closed`-/`_leaving`-Transitions, die `_request`-Workercompletion und **Suchansicht vs EPG-Now Matching** instrumentieren. `SEARCH_INPUT_ACCEPTED`, `SEARCH_GUI_READY`, `SEARCH_RESULT_READY`, `SEARCH_WINDOW_CLOSED`, `SEARCH_RETURN`, und anonyme NOW-Zähler mit gleichem Korrelationswert erfassen.
- GUI darf bei NULL-Treffern oder Timeout **sichtbar bleiben** und verständlich `NO_EPG`/`NO_CURRENT_EPG`/`EPG_UNAVAILABLE`/Fehler mit Retry zeigen; kein ungewolltes Schließen zur XCMate-Home. Keine geheimen Suchbegriffe/Provider-Kennungen im öffentlichen Log. EPG-Programmtreffer auf mehreren Sendern korrekt anzeigen, eine eindeutige Auswahl per IR ermöglichen.
- Tests für Root-Suche, aus Medien-Suche, Enter/OK aus Eingabedialog, langsame/abgebrochene Worker, Short-EPG-only, gleichnamige Jetzt-Sendungen auf mehreren Sendern, Back & Focus, Kodi21 Window Lifecycle. Grund-Smokes S1/S3/S4 schützen.

### P1 #111 – Provider-Timeout und TMDB-Bildfallback
- Pro konkretem ausgewählten Film Poster-Provider-Quellen/HTTP-Deadline/Versuchsanzahl privat datensparsam untersuchen; bei keinem tatsächlich nutzbaren Providerbild deterministischen **TMDb-Nachbezug** aus offizieller API mit exakter Identität/Film vs Serie/Jahr (bevorzugt TMDb-ID) und asynchroner begrenzter Queue anbieten. Bild nur nach eindeutigem Match; Provider-/TMDb-Cover samt Quelle separat cachen, Rate Limits/API-Attribution/Rechte achten; Alt-READY nie löschen.
- Realgerätetests: alter Timeout reproduzierbar, ein eindeutiges Film-Cover nach TMDb-Referenz korrekt geladen + Neustart, Titelgleichheit mit unterschiedlichem Jahr wird **nicht** falsch zugeordnet, unmappable bleibt neutral. Nicht fälschlich eine News-Sendung mit Kino-Poster versehen.

### P0 #126 – Recorder
- Native Capture-Zielvertrag ausdrücklich getrennt von Download-Staging; Direct TS unterstützt? Code/errno; Bytes>0 über ca. 2 Minuten, Stop/Finalisierung, Wiedergabe nach Neustart, Partfiles unter Unterbrechung. REC1–REC4 bleiben Nutzer-FAIL.

### Positiv / Abschlussbewertung
- **#122:** UI1/UI2 Android-PASS sowie Paket-/Originalimage-Hosttests und S2/S5-Smoke: Original-Background für Lightweight im Nutzerumfang abgenommen. Premium-Skin #115 bleibt eigenständig offen.
- **#142:** PO1 Android-PASS (DE/EN Prompt und Parserwarnungsfreiheit laut Nutzer-Testdefinition) plus aktueller Gettext-/PO-Validator CI PASS. SMB-Verbindung #136 dadurch nicht automatisch funktionsfähig.
- **#141:** MEM1/MEM2 Android-PASS laut Nutzer (4h und Service-/Neustart), Host-Profil-/OOM-/Shutdown CI PASS. **Nur 4h-Nutzerbericht, keine separaten RSS/PSS-/Callrate-Zahlen oder unabhängigen Logs**. Abschluss des ursprünglich sichtbaren akuten Root-Menü-/OOM-Fehlers kann auf diesen Nutzer-PASS begrenzt erfolgen; erweiterte 8h-/Varianten-/Trendwache auf Master #143, falls fachlich nötig. Unbekannte alte .28-Leak-Root-Cause nicht rückwirkend als bewiesen bezeichnen.
- **#143** Master bleibt offen; die 5 Smoke-PASS werden wiederverwendet, keine repetitiven 29-fach Vollrunden bei jedem Hotfix.

## Datensicherheit / Issue-Status
Bei Abschluss ausschließlich `state_reason=completed` nach belegter #122/#142 sowie enger #141-Geräte-PASS-Definition; Fach-Issues #136/#135/#63/#140/#126/#111 **bleiben OPEN**, trotz gemergter Implementierung und 1029 CI-PASS. Alle privaten Kodi-Logs, Portal-/SMB-Adressen, Media-IDs, Tokens, Usernamen, Bild-Screenshots im privaten Kanal belassen. **Kein weiterer Merge oder Release** durch diese Abnahme.
