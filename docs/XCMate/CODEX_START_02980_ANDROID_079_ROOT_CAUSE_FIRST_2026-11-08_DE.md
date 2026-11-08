# XCMate 0.1.29.80 – Android-.79-Befundanalyse und verbindliche Codex-Übergabe

**Datum:** 08.11.2026 | **Master-Issue:** [#389](https://github.com/artattakk-creator/kodi-noodleprivate/issues/389) | **Vorgänger:** [#387](https://github.com/artattakk-creator/kodi-noodleprivate/issues/387), [PR #388](https://github.com/artattakk-creator/kodi-noodleprivate/pull/388), #385, #366, #367, #368, #380.

**VERBINDLICHER STATUS:** XCMate **0.1.29.79 ist bereits auf `main` gemergt** und liegt in regulärem GS Media und GS Media Pilot als Update. **0.1.29.80 existiert noch nicht als implementierter/freigegebener Build.** Der Nutzer hat den 22-Punkte-Android-Abnahmetest gestoppt: .79 ist für die geplanten Startseiten-Tests noch nicht brauchbar. Erst Ursachen beheben; keine weiteren Features oder Layout-Experimente.

## I. Testbasis aus privaten Android-Logs

Gerät: Kodi 21.3 Omega, ARM 32-bit, RK3528, 1080p, Titan BINGIE MOD **2.2.3**, `script.gsmedia.setup 0.5.26`, `repository.gsmedia.pilot 1.9.12`.

**Sechs Dateien – aber drei Kodi-Starts, teilweise überlappende Snapshots:**

| Logdatei | Sitzungsbeginn / Aussage | Zählstatus |
|---|---|---|
| `kodi.old(20261108-110444).log`, `kodi.old(20261108-110453).log` | **Dieselbe Datei** und derselbe Start 11:09:11; erst .78, um 11:21:10 .79-Installationsereignis | Ein älterer Vergleichslauf, nicht als reiner .79-Kaltstart zählen |
| `kodi(20261108-110443).log` | 11:30:52 bis 11:32:52, .79 | Früher Ausschnitt der nächsten Sitzung |
| `kodi(20261108-110452).log` | 11:30:52 bis 11:47:41, .79 | Ebenfalls Ausschnitt derselben Sitzung |
| `kodi.old(20261108-110520).log` | 11:30:52 bis 12:01:41, .79 | **Vollständige Hauptzählbasis** |
| `kodi(20261108-110520).log` | 12:01:43 bis 12:05:06, .79 | Eigenständiger kurzer .79-Neustart |

Privat-Logdateien **niemals** vollständig in GitHub, ZIP, CI-Artefakte oder Issue-Kommentare kopieren. Logzeit, diagnostische Zähler, anonymisierte Statuscodes und Add-on-Versionen dürfen hier verwendet werden. Keine Zugangs-URLs, Token, Hostnamen, MAC-Adressen, geheimen Pfade oder Provider-IDs im Klartext.

### Fakten aus dem längeren reinen .79-Start (11:30–12:01)

| Komponente | Beobachtung | Bewertung |
|---|---|---|
| Kodi-Videobibliothek | Je 4 `no such table: movie_view`, 4 `tvshow_view`, 3 `musicvideo_view`; Kodi-Library-Queries schlagen fehl | **P0 / Android-FAIL** für native Library-Queries. Ursache noch ungeklärt |
| XCMate-Daten | Live **88** Items; Filme **24**; Serien **24**; VOD **18 lokale Bildreferenzen**, Serien **24** | Daten sind vorhanden; sichtbarer Skin-Consumer nicht erwiesen |
| Home/Art-Receipt | `WIDGET79 ACTIVE_CONTROL` **181**, `TEXTURE_REQUESTED` **150**, `TEXTURE_PENDING` **31**, `CONTROL_EMPTY` **7**, **0 protokollierte `TEXTURE_VISIBLE`** | Kein End-to-End-Renderbeweis. Abwesenheit eines Logcodes ist **kein Beweis dafür, dass gar keine Pixel sichtbar waren** |
| Native Home | `NATIVE_HOME_EMPTY` **4**, später `NATIVE_HOME_ITEMS` und `items=24` | Cold-start-/Widget-Reload-/Generation-Race möglich; genaue Ursache prüfen |
| EPG DB | `EPG_DATA_MISSING` **1.369** bei **18 eindeutigen Channel-Hashes**, `EPG_CACHE_UNAVAILABLE` **298**, `EPG_DB_BUDGET` **77**, `READY` **241** | Wiederholte Leseereignisse; keine Sender- oder Eventzahl |
| Datenbanklocks für Art | `PROGRAMME_DB69 SQLITE_BUSY_LOCKED` **9**, `PROGRAMME_DB46 PROGRAMME_DB_BUSY` **8** | Persistenz kann auf `LOCAL_CACHE RAM_ONLY` zurückfallen |
| Helper-/Bilderprobleme | `HELPER_TIMEOUT` **139**, `HELPER_BACKGROUND_UNAVAILABLE` **238**, `NO_CONFIRMED_IMAGE` **694**; TMDB Helper mit `JSONDecodeError` | Einzelne wiederholte Events, nicht unterschiedliche Bilder; Caller-Herkunft des externen Helper-Fehlers gesondert prüfen |
| Startzeit | `MOVIES_VISIBLE_READY elapsed_ms=68247`; `SERIES_VISIBLE_READY elapsed_ms=70060` | Interne Bereitschaftsmeldungen nach ~68/70 s, keine Pixelmessung |

**Abgrenzung nach Neustart (12:01–12:05):** `EPG_DATA_MISSING` **76**, `EPG_CACHE_UNAVAILABLE` **321**, `EPG_DB_BUDGET` **25**, `READY` **59**; erneut fehlende Kodi-Library-Views, `NATIVE_HOME_EMPTY` **5**, `WIDGET79 CONTROL_EMPTY` **10**, `TEXTURE_PENDING` **4**; weiterhin kein `TEXTURE_VISIBLE`-Receipt. `MOVIES_VISIBLE_READY elapsed_ms=67594`. Keine Schlussfolgerung über vollständige Startseitenabnahme möglich.

**Status vs. Annahmen:**
- **Belegt:** fehlende MyVideos131-Views, einzelne nicht verfügbare Widget-Consumer, wiederkehrende EPG-/Cache-Reads, DB-Locks, Helper-Ausfälle, späte interne Widget-Bereitschaft.
- **Noch zu beweisen:** Warum Kodi-Library-Views fehlen; ob „Neu im Kino“ als SkinShortcut physisch verschwunden oder nur funktionslos/unsichtbar ist; welcher Consumer/Texture-Fehler zu den leeren Widgets führt; ob die externen TMDB-Helper-JSON-Fehler unmittelbar von XCMate oder von anderen Skin-Widgets initiiert wurden; ob bestimmte Bilder bereits visuell korrekt angezeigt wurden.

## II. Kausale Reparaturreihenfolge für Codex

### P0-A – Kodi MyVideos131 / Native BINGIE-Library-Widgets, streng nicht destruktiv
1. Diagnosetool **read-only**: Existenz und Format `MyVideos131.db`, Kodi-Version, Version-/Schema-Katalog `sqlite_master`, ob `movie_view`, `tvshow_view`, `musicvideo_view` fehlen, `PRAGMA integrity_check`, tatsächlich aufrufende Kodi-Queries und Library-Widgets. Schema erwarteter Kodi-21.3-Installation gegen vorhandene DB-Metadaten vergleichen, ohne sensible Daten zu extrahieren.
2. **Keine DB-Deletion, kein Backup-Overwrite, keine automatische DB-Migration und keine generierten Ersatz-SQL-Views ohne verifizierte Ursache/Freigabe.** Vor jeder späteren mutierenden Korrektur Backup und transparentes separates Go/No-Go.
3. Die bisherigen SkinShortcuts und Widget-Zeilen, **„Neu im Kino“**, zusätzliche BINGIE-Reihen und das bestehende Space-Blue-Layout **READ-ONLY inventarisieren**. Provider-Widgets unabhängig von beschädigten Kodi-Library-Views nutzbar halten.

### P0-B – Native Home-Daten zu Kodi-Control/Texturen
1. Von `plugin://`-Route über Directory-Items/Art zu SkinShortcuts/Window-/Control-ID und Reload-ACK bis zur tatsächlichen Textur instrumentieren, Status **pro Widget/Generation/Quelle**. Eine `source_ready`-, `directory_ok`-, `ACTIVE_CONTROL visible=true`- oder `TEXTURE_REQUESTED`-Meldung ist **noch kein sichtbares Bild**.
2. `NATIVE_HOME_EMPTY` und `CONTROL_EMPTY` aus Gerätelog reproduzieren; `TEXTURE_PENDING` auf harte Failure-Reasons zurückführen; tatsächliche Skin-Property-/Texture-Pfade und Art-File-Lebensdauer prüfen. Kein endloses Refresh, keine generellen Skin-Datei-Überschreibungen.
3. **Last-good Cover Snapshot**: `HOME74`-Wechsel von `REFERENCE_READY` zurück auf `REFERENCE_PARTIAL` stabilisieren; niemals alte oder inkomplette Bildgeneration über gültige aktuelle schreiben; Provider-/Profil-/Inhalt-ID beibehalten, nachvollziehbare TTL.
4. Großer stabiler Live-Hero (korrektes Now/Next/Bild/Logo/Progress), kleine horizontale Logos, alle bisherigen VOD-/Serien-/Kino-/Nutzer-Reihen; Fokus und vertikale Navigation bleiben stabil.

### P0-C – EPG-Matching/Cache/Polling und SQLite-Lockdiagnose
1. Für 18 häufig fehlgeschlagene Kanal-Hashes verifizieren, ob `PROVIDER_ID` keine Daten hat, aber ein **exakt zutreffender** `STREAM_ALIAS` bzw. eine bereits gespeicherte manuelle XMLTV-Zuordnung gültige EPG-Events liefert. Fallback auf gesicherte Identität statt Titel-Heuristik. Keine falschen Now/Next-Sendungen.
2. **Negative Lookup-Caches**, in-flight request coalescing, revisionsbezogene Deduplizierung, Backoff und Entkopplung teurer SQL-/HTTP-Operationen von Kodi-GUI-Thread. Startgruppe zuerst, restliche Sender/Art nachrangig, aber keine vollständige Abschaltung der EPG-Quellen.
3. SQLite-Besitzer/Threads/Transaktionen für `PROGRAMME_DB_BUSY` instrumentieren und Lock-Contestion reduzieren; `RAM_ONLY` transparent halten und persistente Bilddaten erst nach bestätigtem Commit ausweisen.
4. Regionale XMLTV/Provider-EPG-Quellen, mehrere Quellen/Failover, tägliche Updates und gespeicherte EPG-Zuordnungen **bewahren**.

### P0-D – Externen Helper aus dem kritischen Pfad herausnehmen
1. `plugin.video.themoviedb.helper` hat `JSONDecodeError`; XCMate meldet Helper-Ausfall; **welcher Caller den Stacktrace erzeugt ist nicht belegt**. XCMate-Interaktion und aktive Opt-out-Einstellung nachvollziehen.
2. Für Filme/Serien **Provider-Poster/Fanart zuerst**, keine erforderliche Helper-Verfügbarkeit. Für TV-/EPG-Sendungen: gültige XMLTV-/Provider-Bilder, **eigener** TMDB-Read-Token (bestehend, niemals überschreiben/zeigen/loggen), TVMaze bei zulässiger Serienzuordnung als Fallback. Kein unkontrolliertes paralleles Mehrquellen-Fetch.
3. Ein ausgefallener/abgeschalteter Helper darf weder Haupt-UI noch Artwork-Bereitstellung blockieren. Kein globales Host-Whitelist-Wildcard, keine falschen Event-Images.

### P0-E – Ladepriorität und Performance
1. **Local-first**: zuerst verfügbare EPG-Events und Senderliste/Icon-Rail, danach Hero Now/Next/Bilder für erste 5 Sender, Rest im Hintergrund. VOD/Serien-Providerposter danach inkrementell mit Last-good-Cache.
2. Phasenmessung auf Hardware 1080p/ARM32: Kodi-Skin lädt, Widget-Directory, Kontrolle/Texture, erstes Senderhero, erstes Film-/Serienposter, EPG-Ready. `HOME75 *_VISIBLE_READY` nur nach überprüfbarer Bereitschaft, nicht voreilig als Pixelbeweis.
3. Stale/Pending/Busy-States bounded und erklärbar, keine permanente Poll-/Reload-Schleife. Test: kalter/wärmerer Start, teilweise offline, langsame Bild-CDNs, mehrere Widgets + hohe EPG-Last.

### P1 – Navigation/Player-Exit Regression
Ältere Fixes für `NAV ANCHOR_TIMEOUT`, `ActivateWindow`-Quoting, Player-Owner/Stop-ACK (Live, Film, Serien und Serien-Autoplay) nicht verlieren. Die neuen Logs liefern **keine vollständige .79-Android-Abnahme** für Exit.

## III. Umsetzung, CI, Versionierung, Release

1. Implementiere **nur die P0-Stabilisierung kumulativ auf `0.1.29.79`** in neuem Featurebranch für **`0.1.29.80`**, mit PR, kleinen testbaren Änderungen und dokumentierten Root-Cause-Entscheidungen. Vor großen Refactorings zuerst gezielte reproduzierbare Tests.
2. Tests: fehlende Videolibrary-Views und User-SkinShortcuts, BINGIE-Mod 2.2.3 Controls, leeres/veraltetes Home-Directory, `TEXTURE_PENDING`, Cover-State-Generationen, EPG-Provider-ID/Stream-Alias-Fallback, SQLite-Multiwriter-Lock, Helper-Timeout und eigenständige Bildprovider, 2 Kodi-Neustarts, Exit-Navigation, **niemals DB-Destruktionsfixes**.
3. Bauen: `plugin.video.xtreammate-0.1.29.80.zip` aus aktuellem `main` kumulativ, ZIP-CRC, Source-ZIP-Parität, SHA256, Version im `addon.xml`, CI/native Linux-Kodi-Tests. `HOST_PASS` != `ANDROID_PASS`.
4. **Wichtig – Veröffentlichung:** Es gibt hier die **Freigabe zur Implementierung/Vorbereitung** von .80, **nicht** die gesonderte Freigabe zu ungetestetem automatischem Merge/Veröffentlichung auf drei Kanälen. **Erstelle einen testbereiten PR**, übergebe Link, Testbericht, ZIP und mögliche Paketroute. Source-Merge/Update auf `main` und regulär/Pilot/NeoDark3 nur mit entsprechender späterer Nutzerentscheidung, die sich ausdrücklich auf .80 bezieht. Alte Freigaben für .78 oder .79 nicht wiederverwenden.
5. **Nicht verändern:** `script.gsmedia.setup 0.5.26`, bestehender TMDB-Token, Provider-/Favoriten-/EPG-/SkinShortcuts-/Kodi-/Space-Blue-Userdata. Bestehende Box-Kofiguration niemals durch „Neu aufsetzen“ retten.
6. **Android-Abnahme nach Fix nur drei Gates statt 22 Fragen:** A: Home, große Hero-Fläche und alle vorhandenen Reihen inkl. „Neu im Kino“; B: passende Film/Serien-Poster (auch nach Neustart); C: aktuelle Sendung plus Now/Next und korrektes sichtbares EPG-/Hero-Bild. Erst danach Navigation/Player-Exit, Langzeitcache, Performance und vollständigen PASS/FAIL-Plan.

## IV. Codex-Antwortformat

In [#389](https://github.com/artattakk-creator/kodi-noodleprivate/issues/389) dokumentieren: reproduzierte Fehler samt Messbeleg, Root-Cause pro P0, konkrete Dateien/Änderungen, CI-URL und Tests, Branch/PR, falls vorhanden testbares ZIP/SHA256, welche Kodi-/Benutzerdaten **nicht** mutiert wurden, Android-Status pro Gate (FAIL/NOT_TESTED/PASS nur mit Gerätbeweis), Blocker und nächste Abnahmeaktion.

**Qualitätsprinzip:** Keine positive Erfolgsmeldung allein durch `DIR_ITEMS=24`, Bild-URL, Cache-Zuordnung, aktives Control oder Hosttest. Ziel ist eine auf der tatsächlichen Android-Box bedienbare und sichtbar korrekt gefüllte BINGIE-Startseite.
