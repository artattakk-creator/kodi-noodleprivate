# CODEX-MASTERÜBERGABE – XCMate 0.1.29.96
**Stand: 16.11.2026 · Verbindliche Produktvorgaben mit privater Kodi-Logauswertung**

**Startbasis:** `fix/xcmate-02995-backup-gate-profile-locks` (darin `src/plugin.video.xtreammate/addon.xml = 0.1.29.95`). Die Zweige `main` und `release/xcmate-02995-pilot-only-20261115` haben für `addon.xml` noch Stand .92 und sind **nicht** ohne Abgleich als neue Basis zu benutzen. Zielversion: **0.1.29.96**, **eigener Entwicklungsbranch, Draft-PR, Testpaket ZIP + SHA256, keine autonome Veröffentlichung oder Merge**. Das vorliegende Dokument/der Dokumentationszweig enthalten **keinen Codefix**.

## GitHub-Vertrag und Prioritäten
- **P0-A – Sendergruppenwechsel (Blocker):** [#467](https://github.com/artattakk-creator/kodi-noodleprivate/issues/467), [#451](https://github.com/artattakk-creator/kodi-noodleprivate/issues/451)
- **P0-B – EPG-Grundversorgung, belastbare Bilder, Settings-Readback:** [#464](https://github.com/artattakk-creator/kodi-noodleprivate/issues/464), [#468](https://github.com/artattakk-creator/kodi-noodleprivate/issues/468), [#433](https://github.com/artattakk-creator/kodi-noodleprivate/issues/433)
- **P1 – verbindlich für .96 – EPG-Zuweisung per Mini-EPG Lang-OK, zentrales Artwork-Menü, manuell skalierbarer Cache, Logo-Editor und Cinematic Hero:** [#469](https://github.com/artattakk-creator/kodi-noodleprivate/issues/469), [#98](https://github.com/artattakk-creator/kodi-noodleprivate/issues/98), [#427](https://github.com/artattakk-creator/kodi-noodleprivate/issues/427), [#443](https://github.com/artattakk-creator/kodi-noodleprivate/issues/443)
- EPG-Download/Fortschritt bereits beschrieben in [#458](https://github.com/artattakk-creator/kodi-noodleprivate/issues/458), vorhandene Pipeline wiederverwenden.

## 1. Menükonzept (kein zweites Einstellungsuniversum)
**EPG & Sendungsbilder → EPG:** Anbieter-/Xtream-EPG **immer Grundversorgung** (soweit der Provider Daten liefert), Zusatzquellen EPGShare/Kaimandura/XMLTV optional; kein erzwungener Bilderdienst, keine Kopplung von Senderliste an Programmdaten. Alle zusätzlichen Quellen individuell verwaltbar, eindeutige Senderabdeckung, LastGood behalten.

**EPG & Sendungsbilder → Artwork:** Für die konkrete Testinstallation **XMLTV AN · TMDB AN · TVMaze AN** und die Flags nach Set+Readback, Reboot und Upgrade tatsächlich wirksam; dort zentral genau **drei Schalter**, Status/Verbindungen prüfen, manuelle Bildzuweisung, **Senderlogos verwalten**, optional Bildqualität/Cinema-Hero, Tokenverwaltung. Keine versteckten zusätzlichen Schalter in anderen Menüs, die Bilder trotz AN blockieren. Bestehende per Nutzer bestätigte externe Datenzugriffe gelten für die Testinstallation; bei anderen Installationen keine ungefragte Einwilligung.

**Einstellungen → Speicher → Artwork & Cache:** einziges Schreibmenü für Cache-Budget/Speicherart/Ziel/Kapazität/Bereinigung. Aus dem Artwork-Menü nur Link auf *denselben* Speicherdialog. Anzeige in MiB: Ist-Verbrauch, Max-Budget, freier Platz auf tatsächlichem Zielvolume, notwendige kleine reale Schreibreserve und sicherer Status, Bild-EPG-URL-Anzeige trotz nicht aktivem Archiv.

## 2. P0 Gruppen – zuerst, unabhängig vom EPG
**Symptom:** Nach Wartezeit Programmtext der Startsendergruppe vorhanden, beim Wechsel zu aktiven anderen Sendergruppen werden zwar Gruppen angezeigt, aber **keine Sender** geladen; Live-EPG-Meldung gleichzeitig „EPG wird geladen“. Quellstand:
- `live_overlay._select()`: `category_id` und `live_group93.selected(self)`.
- `live_group93.rows()` besitzt bereits gruppen-spezifische Single-Flight-Worker, ruft `live_catalog46.read(portal, only=cid)`, behandelt aber Ausnahmen pauschal als `GROUP_UNAVAILABLE`, mit Retry. Revision/Worker-Ordering / UI-Refresh / Übernahme unvollständiger Teilindizes nachprüfen.
- `live_group68.read()`: vollständiges Iterieren der aktivierten Gruppen mit globalem **1,5-s-Readbudget**. Logs enthalten `GROUP_SQL_BUSY reason=BUDGET`; Budget ist eine starke Hypothese, nicht der bereits bewiesene einzige Fehler.

**Umsetzung:** Zielgruppen-spezifischer, priorisierter, bounded SQL-Read aus lokalem Katalog, verifizierte Generation/Portal-/Kategoriebindung; kein Blockieren der Senderliste durch EPG/Artwork. Bei fehlendem/teilweisem Index `Gruppe wird geladen`, gezieltes bounded Sync/Retry, nach Erfolg automatischer Fokus-erhaltender Render der Zielgruppe, vorherige asynchrone Gruppe darf aktuell ausgewählte nicht überschreiben. Tatsächlich leere Gruppe ≠ DB busy ≠ noch nicht importiert. Sender auch ohne Now/Next auswähl- und abspielbar. Bisherige Startkanal-, Favoriten- und Gruppenkonfiguration unverändert.

## 3. P0 EPG & XMLTV/TMDB/TVMaze-Bilder
- **EPG-Guide:** Provider-EPG als stetige Baseline, optionale XMLTV-Feeds ergänzen. Bei `EMPTY_GUIDE`/fehlgeschlagenem Import vorhandene verifizierte Daten beibehalten, gültigen Import-Backup-/Readback-Schutz gemäß #464 nicht umgehen. Reale Quelle, Import-Zeit und Zuordnungslage ausweisen, kein pauschal „kein EPG“ wegen Busy.
- **Bildquelle XMLTV verbindlich sichtbar:** `xmltv_stream.py` liest `<programme><icon src=…>` als `screenshot_uri`; `programme_store46.py` speichert `xmltv_image`; `programme_urls55.py` kennt `xmltv_event`. In Mini-EPG, großem EPG, Details und BINGIE-Hero denselben event- und source-verifizierten Bildkandidaten zeigen. Gültiges XMLTV-Bild bei TMDB-Fehler oder gesperrtem Diskcache nicht verlieren. Bildquelle „XMLTV“ korrekt kennzeichnen; keine unsicheren/credential URLs.
- **Manuelle Bildzuweisung:** Bestehende `work_manager86.py` Auswahl `TMDB TV / TMDB Movie / TVMaze TV` um **XMLTV** und Aktion **„XMLTV-Bilder erneut suchen“** in Details ergänzen. Suche lokal in bereits konfigurierten / vorhandenen XMLTV-Bild- und Sendungsinformationen nach Quell-ID, Kanal, Zeitraum, Titel/Episode; keine erneute 300-MB-XMLTV-Verarbeitung auf GUI-Thread. Vorschau, Speichern, atomarer Commit + unabhängiger Readback, Neustartbeständigkeit. Beim Wechsel Mini-EPG → Details darf bestätigtes XMLTV-Bild nicht verschwinden; Quelle/Revision validieren, negative Cache-Einträge korrekt invalidieren.
- **Drei Quellschalter in einem Dialog:** `programme_settings68.py`, `programme_consent77.py`, `programme_candidates85.py`, `storage_policy92.py` und Kodi `settings.xml` konsolidieren; TMDB-Flags `programme_tmdb46`, `tmdb_research43`, `programme_tmdb_optout77`; TVMaze `programme_tvmaze67`, `programme_tvmaze_optout77`. Bei unlesbarer `settings.xml` nicht „deaktiviert“ behaupten, sondern Fehlermeldung + sichere Diagnose/Readback; Token selbst nicht loggen.
- **TMDB erstmals aktivieren:** Nur bei fehlendem valider Token: `Token eingeben | Token-Datei auswählen | Abbrechen` (Kodi lokaler Browser und SMB, vorhandene `tmdb_access61.py`/`tmdb_import63.py`); danach verifizierter Verbindungstest und wirksames Opt-in. Bereits existierender gültiger Token wird übernommen, kein erneutes Importieren. TVMaze/ XMLTV funktionieren unabhängig.

## 4. Mini-EPG: OK lang → EPG zuweisen (P1 verbindlich .96)
**Genau auf markierter Senderzeile der linken Live-TV-Senderliste**, gültiger Stream-ID: **OK LANG** öffnet direkt `EPG zuweisen` für den Sender. **OK KURZ** schaltet weiter normal auf Sender; die rechte Mini-EPG-**Sendungsliste** hat kurzes OK für **Details**, nicht Kanal-Mapping. **Großes EPG:** bereits vereinbart **Senderzeile → OK KURZ → bestehendes Kontextmenü → EPG zuweisen**. Android-Geräte ohne zuverlässigen Lang-OK zusätzlich über das *bestehende* Kontextmenü bedienbar, ohne globale fremde Keymaps zu ersetzen.

**Verifizierter .95-Pfad:** `live_overlay._handle_command` behandelt `long_ok` bisher mit `more/menu` als Extras; `remote_control.build_keymap()` erzeugt optional `mod=longpress` → `long_ok`, `remote_bridge.py` verarbeitet es; `onAction(ACTION_SELECT=7)` ignoriert bewusst eine Doppelaktion nach `onControl`. Ziel: `long_ok` **nur bei mode channels + Senderlistenfokus + gültiger SID** vorrangig für Mapping verwenden, echtes Android-Longpressverhalten und Debounce/Click-Consume prüfen – niemals ungewollt den Sender vorher umschalten.

**Dialog-Controller wiederverwenden:** `guide_mapping48.MappingWindow48` hat Quellwahl, Suche, Programmzeiten/Beschreibung, reversiblen RAM-Preview und explizites Speichern, ist aber **hart an den großen Guide-Parent** (`rows[row]`, `origin`, `category`, `_focus_zone` etc.) gebunden. Nicht naiv mit `LiveNavigator` starten; Such-/Preview-/Save-Controller teilen und zwei UI-Adapter einbauen. Kandidaten `provider` und aktivierte XMLTV-Quellen, Quelle + EPG-Kanal-ID separat, kollisionsfrei, auch >100 Treffer. Preview/Abbrechen **null Datenänderungen**. Speichern **genau eine** `(profile, portal, stream-SID, source-ID, epg-ID)` Zuordnung plus Readback; gezielt Now/Next, Mini/großes EPG, Bilder und BINGIE aktualisieren. Laufender Live-Player bleibt erhalten.

## 5. Speicher / Cache: minimal starten, manuell erweiterbar (P1 verbindlich .96)
**Ist-Code .95:**
- `programme_art46.limit()` → `programme_art_budget46` mit 32/64/128/256 MiB, **Standard 64 MiB**.
- `art_storage.reserve()` → `media_art_reserve_mb` **Standard 1024 MiB** (mind. 32 MiB), `art_storage.capacity()` enthält ggf. nochmals 1024 MiB falls `programme_target87` konfiguriert; `android_artwork87.py` mit 1-GiB-Migrations-/Zielprüfung.
- `artwork_config.py`: `dynamic/internal/external`; `artwork_ui.py` besitzt Probe-/Migrations-/Zielbrowser; `storage_policy92.py` mit zusätzlichem Bild-EPG-Gate; `logo_store89.py` mit separater dauerhafter Minilogo-Quota; Kodi kennt ferner `media_art_budget_mb`, `programme_art_local69`, `cache_dir`.
**Soll:** dynamischer Modus/kleines bedarfsgesteuertes Diskbudget **32 MiB Standardgrenze**, nicht Vorabreservierung. 64/128/256 MiB optional (größer Advanced nur bei realem Kapazitätsnachweis). URL-/RAM-only-EPG-Bilder dürfen nicht an 1-GiB-*Archiv*-Reserve scheitern; **keine** generelle Deaktivierung sicherer SQLite-/Dateisystem-Schreibprüfungen. Nur 1–5 aktuelle Hero-Bilder vorziehen, ruhiger Bildwechsel, LRU+TTL bis mindestens Sendungsende. Das reale Zielvolume pro Datenklasse messen (Android FUSE ≠ großer scheinbarer interner Speicher). Stellt dynamischer Pfad bei Low Storage auf RAM-/Link-only um, dann niemals ungefragt auf volles intern zurückschreiben.

Persistenzschutz: EPG-Guide/LastGood, Datenbanken/WAL/SHM, Token, Sendergruppenkonfig, Senderlogo-Overrides, manuell zugewiesene Bilder und bestätigte Mappings **nicht** als flüchtigen Cache behandeln. Nur explizit bestätigte, nachweislich entbehrliche XCMate-Derivate bereinigen, vorher Anzahl/Bytes anzeigen; Kodi-Texture-Cache nicht ohne separates Einverständnis anfassen. Speicherauswahl dauerhaft, Ziel/Quota nach Reboot per Readback, kein doppeltes Settings-System.

## 6. Senderlogos selbst austauschen (P1 verbindlich .96)
`Artwork → Senderlogos verwalten`: Gruppe/Sender auswählbar **ohne EPG**, Provider-Logo als Vorschau → `Logo ersetzen` (lokale oder SMB-PNG/JPEG über Kodi-VFS, mit Bildprüfung), `Original wiederherstellen`, `Zurück`. Dauerhafter Override nur für `(Profil,Portal,Live-SID)`, Vorrang vor verifiziertem Provider-Logo; nicht die Roh-Provider-`stream_icon` dauerhaft umschreiben. Auf Transparenz/Aspect Ratio achten, Quelle/Schreibprüfung. Gemeinsamer Resolver für Senderleiste, Mini-EPG, Live-OSD, Guide, Details und BINGIE; persistiert über EPG-Refresh, Gruppenswitch und Reboot. Vorhandene `station_logos87/88.py`, `logo_manifest86.py`, `logo_store89.py` und `widget_logo84.py` nutzen, keinen Massen-Re-Download.

## 7. Cinema-Hero gemäß TMDb Helper ohne Pflichtabhängigkeit
Originalquellcode `jurialmunkey/plugin.video.themoviedb.helper` (`nexus`): `ArtFanart` verwendet TMDB-`backdrops` nach Rating, `ArtLandscape` Backdrops/Stills mit Sprachwahl; optional `fanart.tv` Fanart/Landscape nach Likes; Bildertypen Poster/Fanart/Landscape/ClearLogo getrennt. `itemmeta_factories/concrete_classes/basemedia.py` bietet Quellenpriorität und Sprach-/Regionalwahl. **Der Helper erzeugt keine Bilder selbst; BINGIE-Skin-Layout prägt die Wirkung.**

Für XCMate bei eindeutig erkanntem Werk mehrere TMDB-`/{tv|movie}/{id}/images`-Backdrops nach 16:9, Bildmaßen, Bewertung **und** Stimmenzahl bewerten (nicht nur einmaliges `backdrop_path`); nur 1–5 sichtbare Werke auflösen. Breitbild-Fanart für Hero, Landscape/Stills für quer, Poster für hochkant. Keine Poster-Verzerrung; ClearLogo der **Sendung** ≠ Logo des TV-**Senders**. Event-spezifisches XMLTV-/manuelles Bild mindestens als auswählbare Alternative und gültiger Fallback. `fanart.tv` optional später und nur nach eigener Lizenz-/API-/Einwilligungsprüfung, nicht als 4. Pflichtschalter. Gleiche bestätigte Eventbildidentität in Startseite/Mini/Details, keine flackernden Quellenwechsel.

## 8. Private Kodi-Logs – aufbereitete Befunde (NICHT öffentlich hochladen)
Vorliegende Dateien:
- `kodi.old(20261115-180911).log`: 15.11.2026 11:57:01–17:55:01, **47.431 Zeilen**.
- `kodi(20261115-180908).log`: 15.11.2026 17:55:51–18:44:48, **12.854 Zeilen**.

| Protokollmarker | Alt | Neu | Summe |
|---|---:|---:|---:|
| `GROUP_SQL_BUSY` | 6 | 57 | **63** |
| davon `reason=BUDGET` | 6 | 51 | **57** |
| `GROUP_SWITCH_PENDING` | 7 | 52 | **59** |
| `EPG_DB_BUDGET` | 266 | 41 | **307** |
| `EPG_DATA_MISSING` | 160 | 31 | **191** |
| XCMate-`settings.xml`-Load-Fehler | 1.194 | 276 | **1.470** |
| `TMDB_DISABLED` | 366 | 110 | **476** |
| `ART81 TOKEN_PRESENT=YES` | 407 | 80 | **487** |
| `ART81 ENABLED=NO` | 407 | 80 | **487** |
| `RESERVE_BLOCKED` | 642 | 86 | **728** |
| `IMAGE_DECODED` | 33 | 13 | **46** |

Alle Counts sind **Logereignisse**, nicht Anzahl unterschiedlicher Sender/Bilder/Benutzeraktionen. Insbesondere `TOKEN_PRESENT YES` und `ENABLED NO` belegen eine widersprüchliche Freigabe-Wirkung, **nicht allein deren Ursache**; `IMAGE_DECODED` ist **kein Render-PASS**; `GROUP_SQL_BUSY reason=BUDGET` weist auf das Zeitbudget hin, ohne alle Katalog-/UI-Ursachen zu beweisen. Ein echter `BACKUP_REQUIRED`-Importfall wurde in früheren Tests dokumentiert (#464), nicht aus diesen zwei Logs allein abzuleiten. **Keine Rohlogs, privaten Streams, SMB-Pfade, Hostnamen, Tokens, Passwörter, URLs oder Konten auf GitHub posten.**

## 9. Auslieferungs- und Test-Gates
1. Codebasis und Vorhandensein sämtlicher gespeicherter Zustände messen, bestehende .95-Daten **nicht** neu initialisieren; abgesicherte Rückwärtskompatibilität und Tests.
2. Erst **P0 Gruppenwechsel** auf echter RK3528-Box/Kodi 21.3/BINGIE: Startgruppe → Unterhaltung → weitere Gruppe; mehrfach, ohne/mit EPG, bei Busy, nach Kodi-Kaltstart; Sender **anzeigen und tatsächlich umschalten**. Bei FAIL kein Release.
3. EPG provider baseline, zusätzliche XMLTV-Quellen, LastGood, Readback, fehlende/abweichende Guide-Quelle und korrekte Datensparsamkeit überprüfen.
4. XMLTV-Bild (echtes `icon`) identisch im Mini-EPG, Detail, großem EPG und Hero; TMDB + TVMaze gültig; alle drei Schalter AN und nach Reboot noch wirksam; bei 1-GiB-Archiv-Reserve trotzdem link-/RAM-only-Hero. Dateien / URL/Decoder/GUI visuell nachweisen.
5. Mini-EPG: OK KURZ senderwechsel, OK LANG Sender-EPG-Zuweisung, rechts OK Details; großes EPG Sender OK KURZ Kontext; Preview 0 Write, Save+Readback über Reboot, Duplicate-ID-Quellen, Playback bleibt aktiv, keine doppelten Keyevents.
6. Senderlogo aus lokal + SMB ersetzen, sechs GUI-Flächen + Reboot, `Original wiederherstellen` korrekt. Cache 32/64/128/256 MiB, intern/extern/dynamisch, reale Speicherreservendiagnose, sichere selektive Bereinigung.
7. Mindestens Serie+Film+Episode bei TMDB-Multiple-Backdrop/16:9-Hero, kein hochkant gestrecktes Poster und keine Abhängigkeit von installiertem TMDbHelper.
8. CI und gezielte Android-Telemetrie (Zeitbudget, Gruppen-Revision, DB-Code, source-consent-readback, Cache free/reserve/used, Bildpipeline URL→Decode→GUI) datenschutzsicher dokumentieren; **`ANDROID_NOT_TESTED`** bis echter Gerätetest. Draft-PR + changelog + version .96 + Test-ZIP + SHA256; **kein Main-/Pilot-/Regular-/NeoDark3-Merge/Release ohne ausdrückliche Freigabe.**

**Codex-Auftrag:** Implementiere die oben beschriebenen Änderungen auf Grundlage von .95 in einer separaten .96-Entwicklungsrunde; beginne mit P0-Gruppenfix und EPG-/Artwork-Persistenz; liefere anschließend P1-UX und Cache. Bei Zielkonflikt priorisiere P0, dokumentiere offen nicht bestandene Tests; keine stillen riskanten Operationen an bestehenden Daten.
