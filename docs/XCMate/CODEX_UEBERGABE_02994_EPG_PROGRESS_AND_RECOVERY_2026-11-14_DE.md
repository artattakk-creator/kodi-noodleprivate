# CODEX-MASTERÜBERGABE – XCMate 0.1.29.94: EPG, Mini-EPG, Speicher- und Stabilitätsabnahme

**Stand:** 14.11.2026, Europe/Berlin  
**Repository:** artattakk-creator/kodi-noodleprivate  
**Verbindlicher Ausführungsauftrag:** [Issue #458](https://github.com/artattakk-creator/kodi-noodleprivate/issues/458)  
**Vorheriger P0-Master:** [#454](https://github.com/artattakk-creator/kodi-noodleprivate/issues/454); aktuelle Android-Meldungen [#457](https://github.com/artattakk-creator/kodi-noodleprivate/issues/457), [#451](https://github.com/artattakk-creator/kodi-noodleprivate/issues/451)  
**Status dieses Dokuments:** reine Codex-Übergabe, **keine** neue XCMate-Version, kein Fix/PASS, kein Android-Gerätezugriff, keine Merge- oder Releasefreigabe.

## 0. Unmissverständliche Ausgangslage und Arbeitsgrenzen

- `main` wurde zu Beginn dieses Dokumentationslaufs als Commit `85c9f1b9dc4aafea6eae6a055961ff159ad6e254` verifiziert. Seine **Add-on-Quelle** unter `src/plugin.video.xtreammate/addon.xml` trägt **0.1.29.92**. Im Gegensatz dazu führt der bereits publizierte **Pilot-Katalog** seit [Pilot-Release-PR #456](https://github.com/artattakk-creator/kodi-noodleprivate/pull/456) das paketierte **0.1.29.93**. Das ist eine bewusst getrennte Source-/Pilot-Situation, kein Versionsbeweis auf dem Endgerät.
- Der vollständige .93-Quellstand liegt im weiterhin offenen **Draft-PR [#455](https://github.com/artattakk-creator/kodi-noodleprivate/pull/455)**, Branch `fix/xcmate-02993-player-epg-storage`, geprüfter Head `f2e87846fe63b75b16916f1b9121aaee49553a8e`. Das bereits getestete .93-Add-on- und ZIP-Artefakt hatte Build-Stand `0b842c16edf12647a3d012b06c478b4929ca99a3`; neuere Branch-Änderungen sind vor Beginn der .94-Implementierung **nochmals zu diffen**. **Nicht versehentlich .92-`main/src` als .94-Quellbasis verwenden und .93-Verbesserungen verlieren.**
- Im Pilot verwendete .93-ZIP-Prüfsumme: `48e0822827c2a8e8a854a812cbac0d0fb3407f6f6b9a5c3c2c2213f20fe77a95`. Die geschützte .90-Sicherheitsversion und ihre Prüfsumme `e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f` bleiben unangetastet.
- Regulärer Kanal und direkte NeoDark3-ZIP bleiben zunächst .91; GS Media Setup Wizard .5.26 bleibt bestehen, sofern nicht ein **separat geprüfter und freigegebener** Installer-PR folgt. Keine Profil-, EPG-, Token- oder Skin-Reset-Migration ohne Nachweis und Freigabe.
- **Zielversion 0.1.29.94** ist nur beauftragt. Alle mit `ANDROID_NOT_TESTED` oder `OPEN` gekennzeichneten Themen behalten diese Einstufung bis zu echten Nachweisen.

## 1. Chronologie und bestätigte bzw. offene Befunde

1. Nach Android-Werksreset und erfolgreicher Kodi-/GS-Media-Neuinstallation wurde bei der Xtream-Einrichtung keine gesonderte EPG-Quelle gewählt. Der Wizard beendete sich, danach konnte der Nutzer keine Live-Sender aufrufen. Exakter Wiedergabe-/Katalog-Fehler und installierte Geräteversion sind **noch nicht durch Kodi-Logs bestätigt**.
2. Der internationale EPG-Katalog bot nicht die erwarteten DACH-Presets; eine andere internationale Quelle meldete `TIMEOUT`. Die eingebauten Presets sind **nicht entfernt**: `epg_sources.py` bietet Kaimandura DE und EPGShare01 DE/AT/CH separat unter **EPG-Manager → Quellen hinzufügen → Deutschland / Österreich / Schweiz**; die internationale Länderfunktion verwendet einen anderen Katalog. Nutzer hat externe DACH-Quellen nachträglich erfolgreich in die **Quellenliste** aufgenommen – noch **kein** verifizierter DB-Import.
3. „Jetzt aktualisieren“ löste oben ein Blink-/Ladezeichen aus. Auch nach **ca. 15 Minuten** keine erkennbare Quelle mit hochzählenden Sendern, Sendungen oder bestätigtem Speichervorgang. Das beweist fehlende **Beobachtbarkeit**, aber ohne Geräte-Logs noch nicht, an welcher Pipelinephase die tatsächliche Arbeit steht.
4. Durch Quellcodeanalyse bestätigter **Konfigurationsdefekt**: `setup_draft.py` setzt `provider_epg=False` und `epg_sources=[]`, speichert folglich `provider_epg_enabled=False` und `epg_show=False`. Nachträgliche `epg_sources.add_source/add_presets` verändern diese globale Portal-Flag nicht. `stream_epg._refresh44` kehrt bei `epg_show=False` still zurück; `epg_schedule53.plan` plant dann keine Auto-Updates. `epg.request_refresh` meldet nur `REQUESTED`, kein Service-ACK oder bestätigten Datenbankerfolg.
5. Mini-EPG: Wechsel erste Live-Gruppe → **„Unterhaltung“** ergibt leere Senderliste. Derselbe Fehler wurde zuvor bei **„4K“** dokumentiert (#451). `live_overlay._list_content` nutzt `CatalogIndex.selection`, holt `live_group93.rows` aber nur bei `_catalog_partial46=True`; `tick` beachtet den Gruppen-Future ebenfalls nur in diesem Zustand. Dies ist eine **plausible ungeprüfte Android-Ursache**, nicht schon ein vollständig bewiesener Rootcause. Fehlende EPG-Daten dürfen Live-Gruppen niemals verbergen.
6. Frühere P0 bleiben: Android STOP/Back-Freeze vs. **separat** beobachteter ungeordneter Kodi-Prozessabbruch (#452); temporär verschwundene Kodi-Installation nach Reboot wurde gemeldet, die Ursache ungeklärt; Gala/Galileo XMLTV-Bild vorhanden, Details fehlen, manuelle TMDB-Zuordnung kann nicht persistieren (#433, #413); Speicher-/WAL-/Reserveprobleme (#443, #401); Startsender/partieller Katalog (#442, #451). Die .93-Linux-CI-Erfolge sind **kein** Rockchip-Hardwarebeweis.
7. Bereits bei früheren Tests weitgehend sichtbar funktionierend: BINGIE-Hero, lokale Senderlogos, sechs Home-Reihen inklusive MP3-Reihe, schnelleres VOD-Coverladen. Diese Pfade sind **No-Regression-Gates**, nicht neu zu entwerfen.

## 2. P0 – EPG-Konfiguration und Provider-Fallback

**Verbindliches Soll:** Bei einem neu angelegten Xtream-Account soll bei **fehlender bewusster externen EPG-Wahl** das Anbieter-EPG standardmäßig **aktiviert** und über die tatsächliche Portal-/Xtream-XMLTV-Adresse verwendet werden, sofern verfügbar. Die Adresse niemals erfinden. Nutzer darf Provider-EPG oder das gesamte EPG explizit abschalten; diese Absicht ist zu respektieren und ggf. separat vom „im Wizard übersprungen“-Zustand zu speichern.

- `epg_show` (globale Anzeige/Importfreigabe) und `provider_epg_enabled` (Provider-Quelle) getrennt, eindeutig und persistent modellieren. Beim späteren Hinzufügen/Aktivieren von EPGShare01/Kaimandura die globale Sperre aufheben bzw. bei bewusstem Opt-out eine verständliche Bestätigung „EPG wieder aktivieren?“ verlangen.
- Keine automatische Verdopplung identischer Provider-URLs als Fremdquelle; DACH-Paket mit DE Kaimandura + DE/AT/CH EPGShare01 idempotent nachrüstbar; internationale Auswahl klar als **anderer** Quellenkatalog kennzeichnen. Kein Verlust der bereits gespeicherten Profile.
- Live-TV darf bei 0 EPG-Quellen, noch nicht heruntergeladenen Daten, Offline-EPG, SOURCE_UNAVAILABLE oder deaktiviertem EPG normal Sender/Gruppen anzeigen und Streamplayback ermöglichen.
- Fokussierte Quellpfade: `setup_draft.py`, `wizard_ui54.py`, `wizard_epg54.py`, `portals.py`, `portal_manager.py`, `epg_sources.py`, `provider_epg58.py`, `epg_schedule53.py`, `stream_epg.py`.

## 3. P0 – durchgängiger EPG-Job mit realer Status-/Fortschrittsanzeige

**Ein** Importdienst, je Portal/Quelle und Lauf eine `job_id`, keine zweite EPG-Pipeline bauen. **Angefordert ≠ angenommen ≠ heruntergeladen ≠ geparst ≠ persistiert**. Die neue UI bindet vorhandene echte `epg_progress54.Progress`-, `stream_epg`-, `epg_status`- und `epg_report53`-Daten an den EPG-Manager.

| Stufe | Sichtbare Information | Prüfbeleg |
|---|---|---|
| QUEUED / SERVICE_ACK | „Aktualisierung angefordert“ → Dienst hat Auftrag übernommen; Quelle X/N | korrelierte `job_id`, ACK; bei fehlendem ACK klarer Fehler |
| CONNECTING / DOWNLOADING | Quelle, tatsächliche Bytes; %-Balken **nur** bei bestätigter Content-Length, sonst indeterminierter Balken | echte HTTP-/Stream-Lesevorgänge und `last_real_progress_at` |
| PARSING | Spinner, echte Zahl XMLTV-Sender und Programme | Parserereignisse, nicht erfundener Zeitfortschritt |
| MATCHING / STAGING | IPTV-Sender eindeutig zugeordnet; mehrdeutige/fehlende Zuordnung getrennt | Mapping-Resultat und Stagingzählung |
| SAVING / READBACK | geschriebene Datensätze, verifizierte Quelle/Revision, Zeitraum | DB-Commit **plus unabhängiges SQLite-Readback** |
| CLEANUP | tatsächlich entfernte entbehrliche Rohdateien/Bytes | Eigentum/Lock/Referenz-Checks, `statvfs` same-volume vorher/nachher |
| READY / PARTIAL_SUCCESS / FAILED / CANCELLED | finaler Zustand, je Quelle ein lesbarer Bericht mit Fehlerphase und Handlung | persistierter, widerspruchsfreier Abschluss |

- **Pro Quelle eine dauerhaft sichtbare Fortschrittszeile** mit Spinner/Balken, aktiver Phase, Byte- und Sendungszählern; global „Quelle X von N“. Bei 0 Matches explizit `NO_CHANNEL_MATCH` statt Leerlauf.
- Kein scheinbar endloser Spinner: wenn Dienst nicht annimmt, nach begrenzter ACK-Frist `SERVICE_NOT_CONFIRMED`; bei tatsächlichem Stillstand `STALLED` mit letzter belegter Aktivität, genauer Phase und sicherem Abbruch. Nicht eine feste Gesamtzeit zur Abbruchursache großer XMLTV-Dateien erklären.
- GUI bleibt per Fernbedienung bedienbar, verliert beim Aktualisieren weder Quellen-Auswahl noch Fokus und baut nicht alle 2s unnötig große Listen neu. Kodi-Mainthread führt keine HTTP- oder Voll-DB-Läufe aus. Dialogschließen ist **nicht automatisch** ein expliziter Job-Abbruch.
- `Abbrechen` muss unter Download/Parser/Staging sicher und wiederholbar sein; LastGood, Quelleinstellungen, manuelle Zuordnungen, aktive SQLite und Sicherungen bleiben erhalten. Unterbrochener Commit darf nie als READY angezeigt werden.
- Fehlermeldungen unterscheiden: `EPG_DISABLED`, `WAIT_ACTIVE_CATALOG`, `SOURCE_UNAVAILABLE`, DNS/TLS/HTTP/Timeout, ungültiges GZIP/XML, 0 Programme, 0 Matches, `SQLITE_BUSY`, `BACKUP_REQUIRED`, Speicherreserve, Serviceabsturz und Cancel. Sensible XMLTV-/Portal-URLs, User/Pass, Tokens nie loggen.

## 4. P0 – EPG-Rondell / rollierender Speicher / verifizierte Bereinigung

**Verbindlicher Prozess je fälligem Update, normalerweise 24 h, nur vorhandene Quelldaten:**

1. Quelle laden (Streaming/RAM vorziehen, keine künstliche Komplettdatei für Progress), Downloadintegrität/GZIP/XML prüfen.
2. XMLTV-Sendungen inklusive Zeitgrenzen/Quelle/EPG-IDs/Bildreferenzen parsen, Mehrquellen-Fallback/Deduplikation und konkrete Senderzuordnung durchführen.
3. Daten für **7 Tage zurück / bis 20 Tage voraus**, soweit tatsächlich vorhanden, transaktionssicher in die aktive Guide-Datenbank übernehmen; Quelle/Revision/Coverage unabhängig wiederlesen. Letztes gutes EPG bei Netzfehlern/Teilimport erhalten.
4. **Unmittelbar nach bewiesenem DB-Commit + Readback** ausschließlich eindeutig XCMate-eigene und nicht mehr referenzierte `.xml`, `.xml.gz`, `.zip`, `.part`- und Stage-Rohkopien entfernen. Sind Daten nur im RAM gestreamt worden, **0 Bytes Rohdateilöschung** korrekt melden. Eine fehlerhafte Quelle darf keine fremde oder aktive Quelle löschen.
5. Bereits vorhandene Altlasten einmalig, idempotent und journalbasiert inventarisieren; Symlinks, offene Dateien, Reader-/Writer-Locks, aktive Stages, unklare Herkunft und Verzeichnisse außerhalb der streng erlaubten XCMate-Pfade nicht löschen (`SKIPPED_UNPROVEN`).
6. Abgelaufene aktive EPG-Einträge begrenzt/zeitfenstergebunden bereinigen, dabei aktuellen Sendetermin, gespeicherte Zuordnungen, Fav/Reminder, Quellen-Metadaten, Bild-URLs und Offline-LastGood schützen. **SQLite DELETE bedeutet nicht automatische physische Dateisystemfreigabe**; Checkpoint/Compaction nur mit echter Reserve und Rollbackfähigkeit, nie blindes `VACUUM`.
7. `epg.py`-Diskcaches, `guide44_inputs`, `programmes`, `programme_store46`, `guide_backup44`, WAL/SHM und andere aktive DB/Indexkopien getrennt inventarisieren. Backuprotation ist **nicht** mit Raw-Datei-Cleanup identisch; mindestens **ein unabhängig geprüfter Wiederherstellungspunkt** erhalten.
8. **Echte Speicherbilanz** pro Klasse und gleicher Volume-ID: Anzahl Dateien, Bytes und `statvfs.bavail` vorher/nachher; 2 Folgeimporte dürfen keinen neuen vollständigen Raw-Filesumpf anlegen. Nicht behaupten, ein früherer Android-Backupbestand existiere nach Werksreset noch.

## 5. P0 – Mini-EPG-Gruppenwechsel und Live-TV ohne EPG

- Nach `Mini-EPG → Gruppen → Unterhaltung/4K/andere aktivierte Gruppe → OK` **sofort** deren lokale Sender zeigen oder einen echten, begrenzten gruppenspezifischen Reload starten. **Kein Abhängigkeits-Gate zu XMLTV/Now-Next**.
- Auf `_catalog_partial46` **allein** darf der Nachladepfad nicht beschränkt bleiben. Prüfen, ob vollständiger, aber für diese Gruppe unvollständiger/staler Index; falsche `category_id`-/enabled-ID; `GROUP_NOT_IMPORTED`; SQLite `BUSY`; fehlgeschlagenes Full-Index-Warmup oder Future-Resultat die tatsächliche Ursache ist.
- Klar unterscheiden: `LOADING_GROUP` (Sender werden geladen), `GROUP_READY` (N Sender), `GROUP_EMPTY_CONFIRMED` (echt leer), `GROUP_UNAVAILABLE` (Retry/Fehler). Echt leer nur mit geprüftem Katalog-/Providerbeleg.
- `A → B → A` schnell, Coldboot, >100 Sender pro Gruppe/Seitenwechsel, 4K, Unterhaltung, deaktivierte/neu aktivierte Kategorien, Multi-Portal, Offline-Provider mit validem lokalem Snapshot. Kein verspätetes Future-Ergebnis in die inzwischen andere Gruppe schreiben; single-flight und Ergebnisrevision beachten.
- Namen/Logos vollständig und fernbedienbar; OK spielt Live-Sender auch bei leerem EPG. Die Mini-EPG-Zeitleiste zeigt lediglich „Keine EPG-Daten“; Senderliste bleibt unabhängig.
- Relevante Pfade: `live_overlay.py`, `mini_epg.py`, `live_group93.py`, `live_catalog46.py`, `live_catalog.py`, `tv_data.py`, `catalog_sync.py`, `group_selection.py`.

## 6. P0-Abnahme: Bestehende Funktionen und Stabilität nicht verschlechtern

- **Player:** Bereits vorhandenen .93-STOP/ACK-Fix, BACK/Rücksprung, Player/Video ownership und 60 native Zyklen erhalten. STOP-Freeze auf RK3528 (#452/#442/#174) und **unabhängigen** unkontrollierten Kodi-Prozessabbruch getrennt als offen markieren, solange Android-`logcat`/ExitInfo fehlt. Ohne neue Hardware-Evidenz kein `FIXED_ANDROID`.
- **Startsender:** Konfigurierte Startgruppe/Startsender nicht wegen eines temporär unvollständigen Indexes löschen/zurücksetzen; nach Coldboot gruppenunabhängig korrekt laden (#442/#451).
- **Bilder:** XMLTV-Bild aus Mini-EPG muss in Details als sichere Fallback-Referenz erhalten bleiben; manuelle TMDB-/TVMaze-Zuordnung darf nicht still scheitern. Datensatz speichern und unabhängig wiederlesen, Status „Mapping gespeichert, Bilddownload ausstehend“ von „Speichern fehlgeschlagen“ unterscheiden (#433/#413). Kein versehentliches Überschreiben von Benutzer-TMDB-Token oder bewusst deaktivierten Diensten.
- **Home:** Persistente Senderlogos, Live-Hero, sechs BINGIE-Homereihen plus MP3-Reihe, vorhandene individuelle Widgetpfade und schnelle Film-/Seriencover schützen; keine großflächige BINGIE-Umgestaltung in diesem EPG-Stabilitäts-RC.
- **Speicher:** Altlastenbereinigung nur sichere belegte XCMate-eigene Dateien, keine Kodi-Core-Datenbanken, kein USB-/NAS-Original oder geheimen Token löschen; separate physische Kapazitätspools statt „Movies“ auf gleichem Speicherpool als Auslagerung auszugeben.
- **Kodi-App-Präsenz:** Nach Werksreset neu installierte Android-Kodi-App bei mehreren Coldboots prüfen; das einmal gemeldete vollständige Verschwinden aus Android-Apps nicht ohne Beleg XCMate zuschreiben oder als gefixt behaupten.

## 7. Arbeitsreihenfolge und Prüfgates

**Gate A – Baseline/branch:** #455 Source vs. getestetes .93-ZIP und `main` unterscheiden; Branch `fix/xcmate-02994-epg-observable-mini-groups` mit erhaltener .93-Funktionalität; P0-Tests, reproduzierbares Ausgangs-Fail und Android-Open-Matrix erstellen.

**Gate B – logischer Fix:** Xtream-Provider-Fallback und globale EPG-Freigabe inkl. bewusstem Opt-out; No-EPG-Live-Tests; DACH-Preset-Nachrüstung.

**Gate C – echte Importpipeline:** ACK, Stage-Telemetrie, pro-Quelle-Zeilen, ProgressBar/Spinner und Status/Readback; Cancel/Retry/stall/Offline; alle Zustände im UI sichtbar.

**Gate D – Speicher-GC:** rollierendes 7d/20d-Fenster, Raw-Cleanup nach Commit, Backups getrennt, messbare echte Volume-Freigabe und Safety-/Crash-Tests.

**Gate E – Gruppen:** Unterhaltung/4K/sonstige Gruppen im Mini-EPG ohne EPG, Fokus/Remote/Playback, Coldboot, 100+ Sender, Partial-/Full-Index, Busy.

**Gate F – No-Regression:** Player-Stop/Back/Crash-Evidenz, Bildzuordnung/Detail-Fallback, BINGIE-Reihen, Logos/Token, Kodi-Installer- und Repo-Kanaltrennung.

**Gate G – Native Kodi / Geräteabnahme:** 720p/1080p-Kodi-21.x-Pixel-/Fokusprüfungen, reproduzierbare Unit/Integration, Android/RK3528-Matrix zunächst `ANDROID_NOT_TESTED`; kein Android-PASS aus Linux-Test ableiten.

**Abzugeben:** isolierter Entwicklungsbranch/Draft-PR, Änderungs-/Ursachenmatrix je Issue, vollständige Unit-/Integrations-/native Testprotokolle, deterministisches `plugin.video.xtreammate-0.1.29.94.zip` mit SHA256 + ZIP-Integrität/Mitglieder-Check, Android-Abnahmeblatt (inkl. Testfällen ohne EPG), nachvollziehbare Raw-/DB-/Backup-Speicherbilanz und Rollback. **Kein Merge, keine Pilot-/Regulär-/NeoDark3-Veröffentlichung, keine bestehende .93/.90 löschen ohne gesonderte Nutzerfreigabe.**

## 8. Weitere To-dos – ausdrücklich im Blick, aber getrennt von .94-P0

Eine vollständige, priorisierte Issue-Liste inklusive der Themen USB/SMB, Artwork, Widget-Snapshots, Album-Neuheiten, Filmgruppenfilter, BINGIE-Design, Google Drive und TMDB-Zugang steht in [BACKLOG_PRIORISIERT_AB_02994_2026-11-14_DE.md](BACKLOG_PRIORISIERT_AB_02994_2026-11-14_DE.md). Diese Punkte **nicht als erledigt markieren** und nicht blind in das .94-Kernpaket mergen. Kleine Diagnose-/Regressionsergänzungen (#427, XMLTV-Fallback #433) sind erlaubt, komplette zusätzliche Subsysteme erst nach bestandenen P0-Gates und in isolierten PRs.

## 9. Codex-Startkommando

> Lies zuerst Issue #458 und diese vollständige Übergabe inkl. priorisiertem Backlog sowie #454/#451/#457. Prüfe die tatsächlichen SHA-/Versionstrennungen; beginne mit nachweisbaren P0-Fails. Baue XCMate **0.1.29.94** auf dem geprüften .93-Source-/ZIP-Stand. Implementiere **(1)** Provider-EPG-Default und nachträgliche Quellenaktivierung, **(2)** bestätigten EPG-Dienstjob mit durchgehend sichtbarem echtem Download-/Parser-/Mapping-/Commit-/Cleanup-Fortschritt, **(3)** rollierende Guide-Retention 7d/20d mit Rohdatenbereinigung nach Readback, **(4)** EPG-unabhängigen Mini-EPG-Gruppenwechsel für Unterhaltung/4K/alle aktiven Gruppen. Schütze Player/BINGIE/Artwork/Token/Startsender, teste die No-EPG- und Android-OPEN-Pfade, liefere Draft-PR + ZIP + SHA + Tests + Android-Abnahmematrix. Dokumentiere Restpunkte als offen. **Nicht mergen und keinen Kanal veröffentlichen, bevor der Nutzer ausdrücklich freigibt.**
