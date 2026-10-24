# XCMate 0.1.29.29 – Reale Android-Abnahme und Codex-Fixauswertung
**Geräte-Testdatum:** 24.10.2026 (Nutzerangaben). **Gerät:** Android TV 13, Kodi 21.2 Omega, Titan BINGIE MOD, IR-Fernbedienung. **Software:** XCMate 0.1.29.29 aus kumulativem PR #139 / GS Media Kodi Repository.

## Verbindliches unverändertes Rohresultat
**12 PASS / 16 FAIL / 0 NOT_TESTED** aus **28 vollständig markierten Nutzerprüfungen**. Bewertungen exakt übernommen, insbesondere abhängige Nutzer-FAIL nicht nachträglich als NOT_TESTED umetikettieren. **Zusätzliche fachliche Interpretation:** Zahlreiche Folgefälle waren infolge einer scheiternden Zielprüfung **nicht unabhängig end-to-end prüfbar**; aus 16 Markierungen folgen keine 16 unabhängigen Root Causes.

| Testgruppe / Issue | PASS | FAIL | Nutzerbewertung |
| --- | ---: | ---: | --- |
| Menü/Fernbedienung (#131) | 3 | 0 | Alle PASS |
| USB/SMB/Downloadziel (#136) | 0 | 7 | Nicht abgenommen |
| CDN-Redirects und Downloads (#135/#63) | 0 | 5 | Nicht abgenommen |
| Aufnahme und Poster (#126/#111) | 0 | 3 | Nicht abgenommen |
| Suche/Regression (#140) | 9 | 1 | Nicht abgenommen |
| **GESAMT** | **12** | **16** | **0 NOT_TESTED** |

| Test-ID | Prüffeld | Vom Nutzer gewählt |
| --- | --- | --- |
| M01 | Menü bei Filmen und Serien | **PASS** |
| M02 | Fokus und Rücksprung | **PASS** |
| M03 | Alle Menüaktionen | **PASS** |
| ST01 | Bisherige Einstellungen behalten | **FAIL** |
| ST02 | USB-Speicher als Ziel | **FAIL** |
| ST03 | Samba-/SMB-Laufwerk | **FAIL** |
| ST04 | Zwei unabhängige Zielordner | **FAIL** |
| ST05 | Ungültige Speicherziele sicher ablehnen | **FAIL** |
| ST06 | Externe Zielkopie unterbrechen | **FAIL** |
| ST07 | SMB-Netzunterbrechung | **FAIL** |
| RDX01 | Film über CDN herunterladen | **FAIL** |
| RDX02 | Einzelne Serienepisode herunterladen | **FAIL** |
| RDX03 | Freigabe verweigern oder widerrufen | **FAIL** |
| RDX04 | Pause, Fortsetzen und Retry | **FAIL** |
| DL01 | Fertige Dateien offline | **FAIL** |
| CAP01 | Sofortaufnahme mindestens zwei Minuten | **FAIL** |
| CAP02 | Aufnahme abspielen und Fehler unterscheiden | **FAIL** |
| ART01 | Poster-Fallback und Cache | **FAIL** |
| A01 | Suche nach „Upload“ | **PASS** |
| A02 | Live-TV aus Suchtreffern | **PASS** |
| A03 | EPG-Sendung suchen | **FAIL** |
| A04 | Doppel-OK und Neustart | **PASS** |
| A05 | Live-TV-Fernbedienung | **PASS** |
| A06 | Player- und Sitzungswechsel | **PASS** |
| A07 | Großes EPG | **PASS** |
| A08 | Filme, Serien und Autoplay | **PASS** |
| REG01 | Weitere Player-Regressionen | **PASS** |
| REG02 | Originalicon und Benutzerdaten | **PASS** |

## Exakte neue Nutzerbeobachtung: Speicherziel / UI
Nutzer wählt einen USB-Stick und erhält Meldung **„Speicherziel nicht bereit, Rechte, Freiplatz und sichere Dateiveröffentlichung prüfen oder den geprüften internen Ordner wählen“** sowie **`TARGET_ATOMIC_PUBLISH_UNAVAILABLE at LINK:38`**. Für sein **bereits in Kodi eingebundenes und seiner Beobachtung nach beschreibbares Samba-Laufwerk** meldet er dieselbe beziehungsweise gleichartige Ablehnung. **Gewünschte UX:** Nach Start der Ordnerauswahl **zuerst Laufwerks-/Quellenübersicht statt internem Systemordner**, sichtbar „Externer Speicher“, „USB-Gerät“, „Samba-Verbindung“; vorhandene Kodi-SMB-Dateiquellen nutzen. Ziel explizit speichern, Auswahl nach Kodi-Neustart erhalten; **kein erzwungener stiller Fallback** auf intern.

**Fehlerpräzisierung:** `38` ist unter Linux/Android **ENOSYS** („Function not implemented“). In `atomic_media.py::publish()` wird nach fehlgeschlagenem `renameat2(RENAME_NOREPLACE)` ein Hardlink per `os.link(...,follow_symlinks=False)` als Fallback probiert. Bei nicht implementiertem `LINK` wird `StorageFailure('TARGET_ATOMIC_PUBLISH_UNAVAILABLE','LINK',38)` erzeugt. **Das beweist Ablehnung dieses nativ-atomaren Dateiveröffentlichungsverfahrens, nicht allgemeine Unbeschreibbarkeit des Mediums oder fehlende SMB-Kodi-Berechtigung.**
Wichtige Code-Differenz in .29:
- **Aufnahmeordner:** `home_menu.py::recording_folder()` → `capture_target.probe` → **nur native POSIX-Atomic-Probe**, ggf. interner Standard nach Bestätigung.
- **Neuer Downloadordner:** `home_menu.py` Abschnitt `storage` enthält getrennte Aktionen `download_folder` und `recording_folder`. `download_target_ui.py::choose()` verwendet `browseSingle(0,...,'files',defaultt=old)` (direkt im alten internen Verzeichnis), dann `download_targets.assess()`. `assess` soll nach `TARGET_ATOMIC_PUBLISH_UNAVAILABLE` bei lokalem Ziel über `_usb_probe` plus `stage_root()` auf sicheres `LOCAL_STAGE_VERIFY` ausweichen; bei `smb://` soll **separat** `_smb_probe` und `SMB2_STAGE_VERIFY` verwendet werden. **Weder ist nachgewiesen, welchen Menüpunkt der Nutzer tatsächlich betätigte, noch ob der SMB-Auswahldialog eine echte `smb://`-Adresse an den Adapter übergab.** Den gleichartigen `LINK:38`-Fehler bei beiden Zielen deshalb **nicht vorschnell als defekten USB- und SMB-Treiber** deklarieren: möglicherweise falsche Aufnahmeordner-Route, Picker-Typverwechslung, `stage_root`-Probe auf internem Systemziel, andere Ausnahmebehandlung oder voreiliger Fallback. Genaue Route/Caps/Step auf echter Box ermitteln, keine sensiblen Pfade im öffentlichen GitHub.
- **Zusatzschwäche:** `download_targets.stage_root()` sucht Kodi-intern oder app-private Staging-Pfade, nutzt wieder `atomic_media.probe`; wenn selbst der Staging-Pfad die Hardlink/rename-Fähigkeit nicht besitzt, ist staged USB/SMB ebenfalls blockiert. Klären, ob `STAGING_UNAVAILABLE` sauber getrennt diagnostiziert wird; keine ungesicherten Staging-/Datei-Schutz-Fallbacks.
- Der Nutzer meldet **ST01 FAIL**, aber **REG02 PASS (Originalicon und Benutzerdaten)**. Deshalb **keinen Datenverlust oder Account-Reset behaupten**; ST01 hat einen negativen Funktionstest bezüglich Default/Ziel-/Einstellungserhalt, der exakt untersucht werden muss.

## Codec/Download/Weiterleitung – Gate bleibt offen
- **RDX01–RDX04 und DL01 vom Nutzer als FAIL markiert**. Ohne erfolgreich akzeptiertes Downloadziel gibt es **keine unabhängig bestätigte tatsächliche Cross-Origin-/CDN-Freigabe- oder HTTP-Worker-Reproduktion** in dieser .29-Abnahme.
- Ein **früherer** .28-PDF-Screenshot zeigte `REDIRECT_UNSUPPORTED` 0/0 MiB. #135 hat nun Implementationscode, ist aber weder als **jetzt erfolgreich** noch als **jetzt fehlgeschlagen bei exakt diesem Grund** auf Android .29 bewiesen. Weiter offen.
- Zuerst Zielwahl herstellen; anschließend einen erlaubten Film intern, USB und SMB (wenn erreichbar) end-to-end mit Bytes/COMPLETE/Playback testen; dann gezielt autorisierte CDN-Freigabe, eine Einzelfolge, Pause/Resume/Retry/Offline prüfen. **SMB ist netzabhängig, nicht ohne verfügbares Netz offline.** Keine Provider-URLs/Passwörter im öffentlichen Issue.

## Aufnahme und Poster
- CAP01/CAP02, ART01 ausdrücklich **FAIL**. Kein belegter 2-minütiger TS-Mitschnitt mit Bytes>0, kein Play-PASS, kein erfolgreicher gezielter Poster-/Cache-Retry. Aufnahmemotor **#126** benutzt bewusst eigenes natives Zielmodell und ist nicht durch neuen Download-SMB-Adapter automatisch repariert. #111 bleibt offen, nicht ohne konkreten Bild-/Retry-Traces als technische Quelle bestimmen.

## Suchregression – neuer Bug #140
- A01/A02/A04–A08, REG01/REG02 **9 PASS**. **A03 „EPG-Sendung suchen“ FAIL** in .29; dieser konkrete Fall war in .27 **A03 PASS**. Großer EPG und Live aus Sendernamensuche bleiben PASS; **neu isolierte Regression** der EPG-Jetzt-Titelsuche.
- Quelle: `media_search.py::_search_ready` zeigt `_now_title` und `NO_EPG / EPG_UNAVAILABLE`; `search_data.py::live_matches` sucht in aktuellen `guide_store`-Programmen, nutzt `guide_alias`, Mapping, Portalbezug, normalisierte Tokens und SQLite-Deadline. **Keine konkrete EPG-Ursache ohne Log oder reproduzierbare Suchphrase bewiesen.** #140 separat bearbeiten, alle anderen neun PASS schützen.
- Original-XCMate-Icon, Portale, Favoriten, EPG-Zuordnungen, staffelübergreifendes Autoplay und IR im getesteten Umfang **PASS**. Ein isoliertes A03-FAIL widerspricht nicht dem allgemeinen EPG-Abnahme-PASS A07.

## Menü und Skin / neues verbindliches grafisches Gate
- **M01/M02/M03 alle PASS**: Menü bei Film und Serie, Fokus/Rücksprung und alle anwählbaren Menüaktionen im getesteten Umfang funktionieren. **Echte Downloaddateien, Poster-Fallback und Zielkopien sind dadurch nicht bewiesen.** Historischer Menüzugangsfehler #131 ist im .29-Gerätetest **positiv nachgetestet**; weitergehende #131-C03–C10-Akzeptanz, sofern als Scope betrachtet, hängt an #135/#136/#63/#111. Keine automatische Freigabe der Folgefunktionen.
- Nutzer reklamiert **ausdrücklich weiterhin falschen/uneinheitlichen XCMate-Hintergrund** und verlangt **für den nächsten Update-Zyklus zwingend Ersatz durch das originale einheitliche Hintergrundbild**. Existierendes **#122** ist weiterhin offen: unverändertes Repository-Asset `themes/xcmate/space-premium/assets/branding/splash-1920.jpg` lokal im Lightweight-Paket bündeln, Home, Film-/Serien-Landing, Suche sowie geeignete sonstige XCMate-Ansichten mit einheitlichem Basishintergrund; Textlesbarkeit, Performance/Offline. **Original-XCMate-App-Icon beibehalten**, Space Premium nicht ungefragt aktivieren.
- #43 vollständiger First-Run-Wizard und #127 Rich Search UI bleiben verpflichtender nächster vollständiger Release-Kandidat; nicht aus dem Hotfix als fertig markieren.

## Konkreter Codex-Fixauftrag
1. **P0 #136:** Für Aufnahme vs Download sichtbare unterschiedliche Einstellungen; Download-Auswahl **beginnend mit Quellen-/Laufwerksübersicht** (keine automatische alte interne defaultt-Position), Kategorien intern/USB/Samba, vorhandene Kodi-Dateiquellen, ggf. sichere Abgrenzung Kodi-VFS-URI vs eigenem SMB2-Backend. Pro tatsächlicher Auswahl strikte anonymisierte Marker `PICKER_ROUTE`, `SELECTED_TARGET_TYPE`, `CAPABILITY_NATIVE`, `CAPABILITY_STAGING`, `STAGING_TARGET_READY`, `SMB2_AUTH`, `TARGET_ACCEPTED`, `TARGET_REJECTED code/step/errno`, `PERSISTED_TARGET_TYPE`. Keine URL/Pfade/Hosts/Credentials loggen. **`LINK:38` mit Hardware reproduzieren** und den korrekt vorgesehenen safe USB-Stage-/SMB-Pfad ermöglichen, ohne NoOverwrite, O_EXCL, fsync/Hash/Integrity oder Zugriffsrechte abzuschalten.
2. **P0 #140:** Separater reproduzierbarer Fix für EPG-Jetzt-Programmsuche A03, nicht die globale Such-/Player-Basis destabilisieren. Demographisch sensible Details nicht loggen.
3. **P1 priorisiert #122:** Original-Space-Splash konsistent **im unmittelbar nächsten Testpaket** für Lightweight integrieren; visueller Android-Gate Home/Filme/Serien/Suche, ohne Premium-/Icon-Regression.
4. **#135/#63:** Nach funktionierendem Ziel echten Film und eine Episode über einen verifizierten Provider/CDN herunterladen, Dateien >0, COMPLETE/Abspielen; Pause/Resume/Cancel/Widerruf separat, SMB-Tests inklusive Verbindungsunterbrechung.
5. **#126/#111:** Aufnahme und Poster-Fallback weiterhin getrennt abnehmen, nur echte End-to-End-PASS abschließen.
6. Test-ZIP inkl. Version/SHA256, CI+Android-Anleitung, getrennte Draft-PRs / kumulativer Kandidat, **kein automatischer Merge/Release**, alte Konten/Daten/Original-Icon/Staffelautoplay/Guide-IR schützen.

## Issue-Status/Verweise
- #136 USB/SMB/Pickerauswahl **FAIL/OPEN**.
- #135 CDN-Redirect **User-FAIL / downstream blocked / OPEN**, neuer Fehlercode nicht nachgewiesen.
- #63 Downloads **FAIL/BLOCKED / OPEN**.
- #126 Sofortaufnahme **FAIL/OPEN**, #111 Poster-Fallback **FAIL/OPEN**.
- #131 Menü M01–M03 **PASS**; prüfen, ob ausschließlich Menü-Einstieg abgenommen oder weitergehender Scope offen bleibt. **Nicht** als Download-/Poster-Behoben interpretieren.
- #140 EPG-Suche **NEU/OPEN**.
- #122 Hintergrund **erneut Nutzer-Pflicht/OPEN**.
- #43/#127 Zukunft **OPEN/Pflicht**, #120/#123/#98/#115 weitere offene Roadmap.

**Quellen:** Voriger Android-Stand `docs/XCMate/ANDROID_ABNAHME_02927_20261023_NUTZERERGEBNISSE_DE.md`; .28 PDF privat, `docs/XCMate/ANDROID_TEST_02929_C_DE.md`; Integration PR #139; aktueller main-Code `atomic_media.py`, `download_target_ui.py`, `download_targets.py`, `search_data.py`. **Keine** privaten PDFs, SMB-Servernamen, internen Pfade, Tokens, Film-/Sendungstitel ins GitHub-Dokument übernehmen.
