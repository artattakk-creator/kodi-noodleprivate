# XCMate 0.1.29.37 – VERBINDLICHER Android-/Host-Test- und Abnahmeplan

**Erstellung:** 25.10.2026, Europe/Berlin · **Status: PLAN; .37 bisher weder gebaut noch auf Android getestet.**  
**Hauptauftrag:** [CODEX_NEUAUFTRAG_02937_KUMULATIV_GESAMT_20261025_DE.md](CODEX_NEUAUFTRAG_02937_KUMULATIV_GESAMT_20261025_DE.md).  
**Repository:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Ausgangs-Release:** `0.1.29.36`, `main`/Kodi-Index · **Neuer Kandidat:** `0.1.29.37` aus neuem Draft-PR; Download **erst nach Codex-Artefakt-Build**.

## Legende, Testumgebung, Schutz

`PASS` = auf konkret benannter Testebene selbst geprüft, Beleg vorhanden; `FAIL` = erwarteter Ausgang nicht eingetreten; `BLOCKED` = äußere Voraussetzung fehlt/unsicher (z.B. tatsächlich kein verfügbarer SD-Slot); `NOT_TESTED` = noch nicht ausgeführt. **NICHT** Android PASS aus Host CI ableiten.

- **Box A:** bisher eingerichtete Box, viele Tausend Cover intern, Kodi21.2 laut bisherigen Logs, Skin Titan BINGIE MOD. **Höchster Schutzbedarf**; tatsächliche Add-on-Version und Kodi-Version vor jeder Aktion direkt ablesen. Nichts deinstallieren, nicht downgraden, keine Daten, Kodi-Textures oder XCMate-DB löschen. **Vor echtem A-Upgrade** Nutzereinwilligung + read-only Inventur mit Dateianzahl/Gesamtbytes/Hashstichprobe und Settings/Portale/EPG/Favoriten/Resume-Werten; Diagnose/Backup nur vertraulich, keine Portalpasswörter veröffentlichen. Am Anfang Host-Fixtures und kontrollierte Testbox B verwenden. Box A nicht zur automatischen Freigabe voraussetzen, solange Nutzer ihre Ausführung nicht autorisiert hat.
- **Box B:** neuere Box mit Kodi21.3, Nutzer-meldete `531/3847 MiB` freie/gesamte Datenpartition, Bildreserve `1024 MiB`, `97 DISK_FULL`, `21 PENDING`, `1 RUNNING`. Sie besitzt **bereits** Portal-/Profilkonfiguration und ist **kein echtes Fresh Install**. `.36`-Live-Back-Hänger beobachtet. Kein blindes Speicherreserve-Nullsetzen oder Reset.
- **Fresh-Fixture:** Separates synthetisches/leeres Kodi-Profil **nur im Hosttest oder mit einem explizit freigegebenen isolierten Testprofil**. Nicht eine bestehende Box als „neu“ behandeln, um den Wizard zu testen.
- **Live-Stabilitätsfolge:** Host-Fakes und Unit-/Integrationstests zuerst; dann echte Android-Exit-Vorsichtsprobe (einmal), Logs, nur dann Wiederholungen. Bei Freeze nicht weiter provozieren.
- **Nachrichtenprotokoll pro Gerät:** aktuelle Add-on-Version, Kodi/OS/ABI, ausgewählter Modus, Test-ID, Datum/Uhrzeit, Stopuhrwert, `PASS/FAIL/BLOCKED/NOT_TESTED`, neutrale Fehlerklasse und Repro ohne Stream-/Provider-URL/Kontendaten. **Video-/Foto-Notizen ohne Credentials**.

## A. Sicherheitsgates – P0, vor jeder Feature-Abnahme

| ID | Genaue Prüfschritte | Strikte PASS-Bedingung | Box A | Box B |
|---|---|---|---|---|
| SAFE-01 | Vor/nach autorisiertem `.36→.37`-Update Bestand lokal mit byte-count und Stichproben-Hashes, `media_art_v1`, `tv_logos`, Jobs/READY, Portal-, EPG-, Gruppen-, Favoriten-, Resume-/Autoplay-Einstellungen, Originalicon vergleichen. Nach Kodi-Neustart wiederholen. | **Box A bleibt intern**; alle vorher vorhandenen verifizierbaren Dateien/IDs/Settings ohne Mutation. Kein Autoscan/Reset/Mode-Wechsel. Box B ist ebenso Legacy; keine Portallöschung. | NOT_TESTED | NOT_TESTED |
| SAFE-02 | Bereits eingerichtetes Profil mit null READY und `DISK_FULL` simulieren und auf B prüfen; danach manuell `Dynamisch` wählen. | `.37` erkennt Legacy unabhängig vom READY-Count, Default bleibt `Intern`; nur Nutzerwechsel auf `Dynamisch`, Cover-URLs funktionieren ohne neuen Portal-Wizard. | NOT_TESTED | NOT_TESTED |
| SAFE-03 | Wirklich brandneues leeres isoliertes Profil mit fehlenden Legacy-Signalen starten. | Default `Dynamisch` ohne XCMate-Archivdownload; danach echte manuelle Wahl Intern/Extern und Persistenz. | NOT_TESTED | NOT_TESTED |
| SAFE-04 | A-ähnlichen 20k-Dateien-Hostbestand und separat echte A-Migrationsprobe nur nach Nutzerfreigabe: inventarisieren, kopieren, SHA/Decode, pause/restart/resume, aktivieren. | Ursprungsbestand 100 % intakt; Ziel korrekt; **0 automatische Löschungen** vor explizitem weiteren Dialog. | NOT_TESTED | NOT_TESTED |
| SAFE-05 | Nach 100 % verifizierter Migration eigenen `Originale intern entfernen`-Dialog bewusst auslösen, zuerst Nein/Abbruch, dann nur nach Freigabe Ja. | Nein erhält alles. Ja löscht nur verifizierte **XCMate-eigene** Original-Bilddateien, misst tatsächlich freigegebenen Speicher; nie Kodi-Thumbnails, SQLite, Portale. | NOT_TESTED | NOT_TESTED |
| SAFE-06 | Dieselbe Add-on-Version auf A und B, aber unterschiedliche lokal gespeicherte Artwork-Modi; USB/SMB ggf. gemeinsam genutzt. | Modi dauerhaft unabhängig je Kodi-Profil; kein anderer Box-Mode wird überschrieben, keine gemeinsamen Schreibkollisionen. | NOT_TESTED | NOT_TESTED |
| SAFE-07 | Upgrade-/Kodi-Restart/-Crash-Fixture mehrfach durchspielen; neuer `artwork_mode`-Wert bei Legacy-Settings fehlt. | Atomare/idempotente Einstellungs-Migration, explizite Altwahl bleibt, keine READY-Verluste, kein neues unbeabsichtigtes Preloading. | NOT_TESTED | NOT_TESTED |
| SAFE-08 | Nach Versionswechsel Programmstart, EPG, originaler IR-Keymap, Startgruppe, Originalicon, Serien-Autoplay, Favoriten, Resume prüfen. | Sämtliche funktionierenden .36-Eigenschaften vorhanden, ohne Setup-Neuanlage und ohne Migrationsnebeneffekt. | NOT_TESTED | NOT_TESTED |

## B. P0 Wiedergabe-/Exit-Gates – #169/#174

**Vorher-Befund:** Box B .36 Live-TV „Zurück“ → Hänger; Nutzer meldete später auch Film/Serie/Live beim Verlassen, **Gerät & installierte Version dieses späteren Berichts nicht sicher bestimmt**. Nicht aus .36-Historie einen .37-Erfolg machen.

| ID | Genaue Prüfschritte | Strikte PASS-Bedingung | Box A | Box B |
|---|---|---|---|---|
| EXIT-01 | Vom XCMate-Live-Suchtreffer Stream starten; bei verborgenem Overlay Back, nach vorheriger Hostprüfung zunächst einmal. | Wiedergabe kontrolliert beendet, XCMate Home reagiert, kein Kodi-/Box-Hänger und keine zweite Home-Route. | NOT_TESTED | NOT_TESTED |
| EXIT-02 | Film aus Liste/Detail starten, nach kurzem Abspielen Back/Stop; später Resume prüfen. | Kein Hänger, korrekter Bookmark und kein ungewolltes Autoplay. | NOT_TESTED | NOT_TESTED |
| EXIT-03 | Episode abspielen, per Back/Stop verlassen, Staffel-/Folge-Resume prüfen. | Kein Hänger, kein Episoden-Autoplay nach absichtlichem Stop, Resume bleibt. | NOT_TESTED | NOT_TESTED |
| EXIT-04 | Nach erfolgreichen Einzelproben je 10–20 sichere Zyklen: Info/OSD offen/zu, buffering, schneller Back, großes Guide-Handoff, Stop/Home. | Keine Deadlocks/Reentrancy/zweite Stop-/Directory-Route; unter Kodi21.2/21.3 reale Reaktion. | NOT_TESTED | NOT_TESTED |
| EXIT-05 | Fremdes Kodi-Video laufen lassen, dann XCMate-Navigation/Backgroundservice aktivieren. | Fremder Player wird nicht durch XCMate gestoppt und seine Dialoge nicht übernommen. | NOT_TESTED | NOT_TESTED |
| EXIT-06 | Kalt-/Warmstart nach Stop, normales Serienende mit nächster Episode, EPG→Live→Back, UI-Fokus/Keymap prüfen; Logs mit Phase-/Zeitkorrelation. | Natürliche Episode startet nächste nur falls aktiviert; manueller Stop nicht. Keine Endlosschleife und eindeutige Owner-Sessions. | NOT_TESTED | NOT_TESTED |

## C. Modi & dynamische Bilddarstellung – #172

| ID | Genaue Prüfschritte | Strikte PASS-Bedingung | Box A | Box B |
|---|---|---|---|---|
| MODE-01 | B manuell dynamisch wählen, drei echte Film-/zwei Serienposter und zwei Senderlogos aus gültigen Provider-URLs in Kodi sichtbar anfordern (ohne XCMate-Prefetch). | Motive sichtbar, keine neuen **XCMate**-persistenten Jobs, keine 1024-MiB-Archiv-Reserveblockade für reines URL-Rendern, keine behaupteten READY-Bilddateien. | NOT_TESTED | NOT_TESTED |
| MODE-02 | Dynamischer Cold-/Warm-Aufruf, Scroll/IR, Offline/HTTP404/DNS/Auth/Ablauf eines Bildlinks simulieren. | Platzhalter ohne Hänger; Time-to-first-image notiert, sichtbare Reihen reagieren, keine Auth-Tokens in Logs. | NOT_TESTED | NOT_TESTED |
| MODE-03 | Intern `Bei Bedarf`, dann bewusst `Alle laden` prüfen, Progress/Pause/Resume und Speicherreserve. | Echte lokale validierte READY-Bilder; alte vorhandene Dateien erhalten, nur erlaubte bounded Jobs. | NOT_TESTED | NOT_TESTED |
| MODE-04 | Dynamisch→Intern→Extern→Dynamisch und Kodi-Restart. | Manuelle Wahl bleibt, alte Bild-IDs/READY nicht gelöscht; keine automatische Rückmigration/Cache-Reset. | NOT_TESTED | NOT_TESTED |
| MODE-05 | Kodi `Thumbnails/Textures*.db` read-only im dynamischen Modus beobachten. | In UI/Dokumentation klar getrennt: **kein XCMate-Archiv, aber Kodi kann weiterhin Thumbnails cachen**. Kein Kodi-Texturecache-Löschen. | NOT_TESTED | NOT_TESTED |

## D. USB-/SD-/SMB-Ziel und vollständige Migration – #106

| ID | Genaue Prüfschritte | Strikte PASS-Bedingung | Box A | Box B |
|---|---|---|---|---|
| STOR-01 | Kodi-Ordnerbrowser auf realem USB-Stick, SSD/HDD, SD-Slot soweit vorhanden, Kodi-`smb://`-Freigabe. Berechtigungen testen. | Alle tatsächlich verfügbaren Typen werden erkannt, Fehler je Typ verständlich; nicht vorhandener SD-Slot = `BLOCKED`, nicht PASS. | NOT_TESTED | NOT_TESTED |
| STOR-02 | Gewähltes Ziel probehalber beschreiben/zurücklesen, SHA+Bildvalidierung, Standardordner `XCMate/Artwork/{media,logos,fanart}` automatisch anlegen. | Exakter Zielort, echte Write/Readback/Display-Prüfung, kein unkontrollierter Android-/SMB-Pfad und keine Klartext-Credentials. | NOT_TESTED | NOT_TESTED |
| STOR-03 | 3 Film-/2 Serien-/2 Senderlogo-Bilder nach Aktivierung **neu auf externem Ziel** laden, Kodi neu starten und dieselben Bilder anzeigen. | Dauerhaft aktive externe Pfade, verifizierte Bytes und Kodi-Rendering; kein intern verstecktes zweites Gesamtarchiv. | NOT_TESTED | NOT_TESTED |
| STOR-04 | Vorhandenen intern READY-Bestand inventarisieren, dann ausdrücklich `Bestand kopieren`; 20k-Dateien im Host plus sichere reale Stichprobe, bei vollem Bestand mit Zustimmung. | Fortschritt Dateien/Bytes; Hash für jede Zieldatei, inkrementelles Journal, Vollständigkeit und korrekter Zielpfad; Quellen bleiben. | NOT_TESTED | NOT_TESTED |
| STOR-05 | Während Migration USB abziehen oder SMB temporär trennen (erst im ungefährlichen Fixture); Kodi normal neustarten, später Medium wieder einbinden. | Fehlerstatus `STORAGE_OFFLINE`, Resume ohne Doppelkopien/DB-Korruption; alle Quelldateien unbeschädigt, TV/EPG/IR nutzbar. | NOT_TESTED | NOT_TESTED |
| STOR-06 | 100 % Migration verifizieren, Ziel ausdrücklich aktivieren, Medienlisten und EPG/Logos nutzen; später separate interne Löschoption verneinen. | Aktivierung nur bei verifiziertem Ziel, Bilder von extern gerendert, lokale Originale bleiben; kein Auto-Löschen. | NOT_TESTED | NOT_TESTED |
| STOR-07 | Nach ausdrücklicher gesonderter Bestätigung verifizierte interne XCMate-Bilder freigeben; freien Platz vor/nachher lesen. | Nur korrekte XCMate-Originalbilder gelöscht, **messbar mehr interner Freiraum**; niemals Kodi-Thumbnails/Kataloge/Portale/Resume. | NOT_TESTED | NOT_TESTED |
| STOR-08 | SMB-Ziel Kapazität `UNKNOWN` vs echten Wert; externe Bilddownloads trotz zu geringer interner Artwork-Reserve; lokaler SQLite-/Temp-Headroom gesondert. | Kein falsches `DISK_FULL` auf NAS, echte Reserve-/Permission-/Offline-Diagnose, lokaler sicherer Betrieb. | NOT_TESTED | NOT_TESTED |
| STOR-09 | Extern offline, zurück intern oder zu anderem USB/SMB-Ziel wechseln. | **Kein stiller Fallback/Redownload-Sturm**, sichere manuell bestätigte Migration und konsistente READY-/URL-Referenzen. | NOT_TESTED | NOT_TESTED |

## E. Metadaten, Wizard, Hardware, Geschwindigkeit

| ID | Genaue Prüfschritte | Strikte PASS-Bedingung | Box A | Box B |
|---|---|---|---|---|
| META-01 | Film-/Serienbeschreibungen, Staffel-/Episodendetails optional als `XCMate/Metadata/` auf externes Ziel speichern und zurücklesen. | Tatsächlich vorhandene Felder korrekt, keine Stream-URLs/Token/Passwörter; keine ganze SQLite-DB aufs SMB. | NOT_TESTED | NOT_TESTED |
| META-02 | Metadata-Ziel offline/Restart, Infos und Suche erneut öffnen, Vorher-/Nachher-Speicher vergleichen. | Kein Datenverlust/Kodi-Hänger; Platzgewinn **nur behaupten, wenn intern tatsächlich reduziert**. Andernfalls physischer Metadata-Offload = `BLOCKED`. | NOT_TESTED | NOT_TESTED |
| WIZ-01 | In **isoliertem neuen Testprofil** Xtream/M3U/Stalker WIZ-Flow mit Gruppenwahl, optional VOD/Serien/EPG, Logo/Hintergrund, Startkanal. | Keine bestehenden Profile verändert; Benutzer kann vor Massenimport Gruppen und Quellen auswählen, gültige Counts. | NOT_TESTED | NOT_TESTED |
| WIZ-02 | Wizard mit vier EPG-Quellen: Beginn 1/4, Wechsel der Quelle, Cancel/Fehler/Completion. | Aktivität von Anfang sichtbar, nie falsche Prozent; klare Fortschritts-/Fehleranzeige. | NOT_TESTED | NOT_TESTED |
| WIZ-03 | Wizard `Speichern` nach EPG-Scan, Kodi normal weiterbedienen, Neustart und bereits gespeichertes Portal prüfen. | Kein Crash, genau ein Portal und intakte SQLite/Katalogstruktur, ohne doppelte Wizard-Home-Navigation. | NOT_TESTED | NOT_TESTED |
| WIZ-04 | Nach Setup bislang deaktivierte Xtream-Sendergruppe aktivieren, daneben unveränderte Gruppe prüfen. | Neue Sender in der Gruppe delta-synchronisiert, kein kompletter Neuimport, Startsender/EPG bleiben. | NOT_TESTED | NOT_TESTED |
| SYS-01 | Wartung & Diagnose → Geräteinformationen, refresh, Kodi-Version/CPU/ABI/RAM via `/proc/meminfo`, realer Kodi-/Bildmount-Speicher, Kernel, Android SDK/Release prüfen. | Reale Werte und Unbekanntes getrennt, Firmware-Fake `16GB RAM/240GB` nicht blind übernehmen; Datenschutz in Export. | NOT_TESTED | NOT_TESTED |
| START-01 | XCMate Appstart **Taste→bedienbares Hauptmenü** 3× kalt und 3× warm messen, **separat** Startsender Taste→Video. | Zeitpunkte klar getrennt, `27s`-Altbefund als Vergleich, starke gemessene Verbesserung ohne UI-Blockade. | NOT_TESTED | NOT_TESTED |
| REG-01 | Bestehende `.36` global Live/Film/Serie-Suche und Genre `Horror/Sci-Fi/Western` mit realen Kategorien testen. | Gefundene Titel tatsächlich vorhanden, Tab-/Fokus-/Back-Design erhalten, keine Platzhalter als erfolgreiche Cover-Suche. | NOT_TESTED | NOT_TESTED |
| REG-02 | Großer EPG, Mini-EPG, Sender-/Gruppenlistennavigation, OK-OSD, Startgruppe/-kanal, Senderwechsel, Back. | Originale IR-Belegung, Auswahl und EPG-Mappings unverändert, keine Deadlocks. | NOT_TESTED | NOT_TESTED |
| REG-03 | Serien-Autoplay natürlicher Episodenübergang, bewusster Stop, Film-Resume, Details, Favoriten, Originalicon/Theme. | Stand `.36` nicht verschlechtert; keine unfreiwilligen Episodenstarts oder Profilresets. | NOT_TESTED | NOT_TESTED |

## F. Verbindliche automatisierte Tests vor der Android-Abnahme

**Codex schreibt Testcases und führt sie vollständig aus**; maximaler Realismus mit Fake-`xbmc`/`xbmcgui`/`xbmcvfs`, Test-SMB-Backend/Mounts, RAM-/Schreib- und SQLite-Fixtures, deterministischer Kodi21.2/21.3-ABI-Modelle.

| HOST-ID | Prüfen | Startstatus |
|---|---|---|
| HOST-01 | `.36` vorhandene 1.250 Tests erneut; neue .37-Tests ohne Regression, kein altes ZIP/Index-Main-Commit | NOT_TESTED |
| HOST-02 | Legacy-Profile mit vielen / null READY, Settings-Default und fehlendem Modusmarker; crash-idempotenter Migration-State | NOT_TESTED |
| HOST-03 | Live-/VOD-/Episoden-Exit bei Back/Stop/natürlichem Ende, schnelle IR-/Modal-Events, Foreign Player, Resume-SQLite-Busy | NOT_TESTED |
| HOST-04 | Dynamic URL valid/invalid/expired/HTTP/TLS, sichtbare Items, XCMate-Queue unverändert, Kodi-Texturecache getrennt | NOT_TESTED |
| HOST-05 | Local/USB/SD/SMB ArtworkStorageBackend, echtes Readback SHA/Decode, VFS-Fehler, Permission/Offline/Unknown-Capacity | NOT_TESTED |
| HOST-06 | Migrator 20k Bilder, Unterbrechung/Restart/Resume, gleiche Hashes/Bytes, Quell- und Zielbestand, zwei getrennte Benutzeraktionen für Activating/Deleting | NOT_TESTED |
| HOST-07 | Meta-Payload/Offline, XPath/URI Traversal, Credential-Log-Sanitizer, kein WAL/DB auf SMB, keine Kodi-Thumbnails-Löschung | NOT_TESTED |
| HOST-08 | Wizard Safe-Save/Cancel/Quellenprogress/Xtream Delta-Gruppensync, CPU/RAM-/FakeAndroid-Reporting, Startprofiling | NOT_TESTED |
| HOST-09 | Paket reproducible ZIP aus **neuem PR-HEAD**, Datei-/SHA256-Matrix, Manifest/PO/Python-Syntax, CI vollständig grün | NOT_TESTED |

Referenzkommando nach CI-Bootstrap:
```bash
python tools/build_repository.py
python tools/validate_kodi_po.py
python -m compileall -q src
python -m unittest discover -s tests -v
```
Exakten GitHub-`publish.yml`-Bootstrap mit vorhandenen pinnten Quellpaketen befolgen; Tests nur in sauberem Scratch/Branch. **CI-PASS ersetzt nicht Android-PASS.**

## G. Abschlussbericht – für Benutzer und Codex

```text
XCMate 0.1.29.37 – Android-Abnahme / Testbericht
PR URL: ... | HEAD SHA: ... | ZIP SHA256: ... | CI: ...
HARDWARE: Box A Kodi ... XCMate vorher ... nachher ...
          Box B Kodi ... XCMate vorher ... nachher ...
SAFE-01..08: ... [A] ... [B] ...
EXIT-01..06: ... [A] ... [B] ...
MODE-01..05: ... [A] ... [B] ...
STOR-01..09: ... [A] ... [B] ...
META-01..02: ... [A] ... [B] ...
WIZ-01..04: ... [isoliertes Testprofil] ...
SYS-01 / START-01 / REG-01..03: ... [A] ... [B] ...
HOST-01..09: ... Testanzahl: ... Fehler: ...
Art: intern ... Dateien / ... Bytes; extern ... Dateien / ... Bytes
USB/SD/SMB reales Zielprotokoll: ... / ... / ...
Kodi Freeze: ... | beobachtete Ausstiegslatenz: ... s
Appstart kalt: .../ .../ ... s; warm .../ .../ ... s
Vorher freier Datenspeicher: ... MiB; nach bestätigter Bildbereinigung: ... MiB
Blocker mit ID, Gerät, anonymisierter Uhrzeit, Ursache: ...
Produktiv-mergefähig? JA/NEIN; Nur Benutzer entscheidet.
```

**P0-Freigabe darf NICHT erfolgen**, solange aktueller Freeze, SAFE-01/02/07 (Bestandsschutz), Kodi21.2/21.3 IR-Exit und die für beide versprochenen Artwork-Modi extern/dynamisch nicht auf echter Hardware verifiziert wurden. Hardware ohne SD-Slot **kein** künstlicher PASS. Externes SMB/NAS muss real getestet sein, nicht nur Host-Mock. Keine automatischen Merges/Releases/Reset auf Nutzergeräten.
