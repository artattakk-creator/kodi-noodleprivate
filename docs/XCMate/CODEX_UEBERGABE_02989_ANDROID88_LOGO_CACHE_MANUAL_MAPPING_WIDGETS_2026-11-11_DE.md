# Codex-Masterübergabe: XCMate 0.1.29.89 – Android-.88-Nacharbeit

**Datum:** 11.11.2026 · **Status:** verbindlicher Implementierungsauftrag, **nicht bereits implementiert**  
**Master-Issue:** [#425](https://github.com/artattakk-creator/kodi-noodleprivate/issues/425)  
**Repository:** `artattakk-creator/kodi-noodleprivate` · **Add-on:** `plugin.video.xtreammate`  
**Baseline:** XCMate **0.1.29.88** auf `main` (zuletzt geprüfter SHA `f1078d2d99364d437be164dd1cb9f510047b56c5`); Source-PR [#422](https://github.com/artattakk-creator/kodi-noodleprivate/pull/422), Release-PR [#424](https://github.com/artattakk-creator/kodi-noodleprivate/pull/424). **Ziel:** neuer Branch/PR für **0.1.29.89**.

## 0. Verbindliche Freigabe und Auftragsscope

**Arbeite Issue #425 vollständig ab.** Implementiere 0.1.29.89 ausschließlich auf einem neuen dedizierten Entwicklungsbranch, führe die Tests aus, lege ein versioniertes Test-ZIP und eine SHA-256-Prüfsumme ab und öffne einen **Draft Pull Request**. **KEIN MERGE** nach `main`, **KEINE Veröffentlichung** in regulär, Pilot, NeoDark3, alten Verzeichnissen oder Kodi-Katalogen ohne eine **neue ausdrückliche Freigabe des Benutzers**. Das reine Auftragsdokument auf `main` ist kein Release.

**Weder Paket noch Profil destruktiv bearbeiten:** Xtream-Portale/Token, manuell importierter TMDB Read Access Token, EPG-Konfiguration und -Zuordnungen, `programme_manual85.json`, Favoriten, Merkliste, Artwork-Datenbank, SkinShortcuts, fremde Widgets und bisherige Versionen erhalten. **Keine echten Secrets in GitHub, ZIP, Screenshots oder Logs.** Der [Joomla TMDB-Gateway #417](https://github.com/artattakk-creator/kodi-noodleprivate/issues/417) ist ausdrücklich **BACKLOG**, kein .89-Feature; GS Media Setup Wizard **0.5.26 unverändert**; Pairing-Draft #418 nicht veröffentlichen. Keine Laufzeitabhängigkeit von `plugin.video.themoviedb.helper`. **Startseite aus .88 ist optisch vom Nutzer positiv abgenommen; Kino-Hero/Verlauf/BINGIE-Referenz Screenshot 4 aus [#421](https://github.com/artattakk-creator/kodi-noodleprivate/issues/421) beibehalten.** Kein experimentelles Layout-Redesign.

## 1. Android-Originalbelege vom 11.11.2026

**Benutzerdateien, in diesem Chat hochgeladen, nicht Teil des öffentlichen GitHub:**  
`kodi.old(20261111-070409).log` (ca. 206 KiB, 2161 Zeilen) enthält eine ältere .87-Startphase und einen Übergang zur .88-Installation.  
`kodi(20261111-070411).log` (ca. 2,3 MB, 16.246 Zeilen), Kodi 21.3, ARM32/RK3528, Android TV, 1080p, XCMate **0.1.29.88**. Rohlogs bei Übergabe nur über sicheren privaten Kanal; vor jeder GitHub-Ablage alle Netzadressen, Zugangsdaten, Quell-URLs, Portal-IDs, Device- und Benutzerpfade entfernen.

**Ereignisstatistik aus dem aktuellen .88-Log (Logzeilen/Events, nicht eindeutige Assets):**

| Tag | Anzahl | Schlussfolgerung / Vorsicht |
|---|---:|---|
| `LOGO87 DECODED_RAM_READY` | **88** | Logos lassen sich mittlerweile dekodieren. Das bestätigt **nicht** 88 persistierte oder sichtbare Dateien. |
| `LOGO87 STORAGE_RESERVE_BLOCKED` | **88** | Persistenter Logo-Speicher weiterhin faktisch blockiert. |
| `LOGO87 TEXTURE_CACHED` | **33** | Kodi-Texturcache enthält wiederverwendbare Referenzen, aber keine XCMate-Dauerhaftigkeitsgarantie. |
| `HOME86 LOGOS_LOCAL_READY` | letztes `33/88` | Zum Ende des Logs nur 33 lokale Referenzen; der Nutzer sieht teilweise Logos in Rail und Hero. |
| `ART_STORAGE82` | `free=228114432` / `total=4034297856` / `reserve=1073741824` / `budget=0` Bytes | Selektiertes `LOCAL`-Ziel: `mount=fuse` / `SAME_VOLUME_VERIFIED`-ähnlicher Status; gemeldetes Volume ~4 GB, nur ~218 MiB frei; keinesfalls mit nominell größerem Speicher gleichsetzen. |
| `EPG69 EPG_READ_TIMEOUT` | **84** | Reale verzögerte Lesefälle, teilweise mehrere hundert ms. |
| `EPG_DB_BUDGET` / `EPG_DATA_MISSING` / `EPG_CACHE_UNAVAILABLE` | **44 / 38 / 11** | Separat nach SQL/Lock/Quelle/Cacheursache gruppieren. |
| `GUI86 LIST_UNEXPOSED` | **504** | Betrifft u. a. `widget_recent_vod` und `control=1520`, `count=0`; nicht automatisch der Rootcause aller Fremd-Widgets. |
| `WIDGET79 CONTROL_EMPTY` | **26** | Native Control-/Binding-Status prüfen. |
| `DISPLAY84 METADATA_WRITE_DEFERRED` | **166** | Metadatenpersistenz verzögert. |
| `LOCAL_CACHE RAM_ONLY` | **99** | Nur Sitzungs-/RAM-Referenz; nicht persistent. |
| `IMAGE77 IMAGE_DECODED` | **46** | Gültige Bild-Dekodierungen erfolgen. |
| `ART70 source=tvmaze code=FOUND` | **mind. 1** | TVMaze-Fallback funktioniert prinzipiell. |

**Alter EPG-Absturz:** `AttributeError: 'Reader' object has no attribute 'close'` ist im alten Log (v.87) belegt, **nicht** im aktuellen .88-Log. Regressionsschutz beibehalten, keine falsche aktuelle Fehlerbehauptung.

**Manueller TMDB-/TVMaze-Abgleich:** Benutzer beobachtet bei Mini-EPG → Details → Bild selbst zuweisen die Meldung `Die Zeit für den Auftrag ist abgelaufen. Keine unbestätigte Zuordnung wurde gespeichert.` Im aktuellen Log ist **kein ausreichend eindeutiger eigener `REQUEST_TIMEOUT`-Trace für genau diesen Dialog** enthalten. Der Code in `work_manager86.py` / `work_requests86.py` belegt jedoch UI-Timeout 30 s, Worker-Budget 24 s, Requestalter unter 35 s und mehrstufigen Kandidaten-Recheck vor Speichern. Diagnose ohne Erfindung einer Einzelursache.

**Fremde Widgets:** BINGIE- und SkinHelper-Add-ons sind installiert und gestartet, die drei XCMate-Reihen liefern Daten. Andere zuvor konfigurierte BINGIE-Reihen sind nach Nutzeraussage weiterhin nicht sichtbar. Kein Beleg für Löschung der gespeicherten Einstellungen; Render-/Visibility-/SkinShortcuts-Pfad vollständig nachweisen.

## 2. Prioritäten und Invarianten

**Absolutes P0** für .89: (A) persistenter Logo-Cache auf echtem geeigneten Volume, (B) manuelle Zuordnung, (C) verlässliche Artwork-Persistenz, (D) Fremd-Widget-Sichtbarkeit, (E) EPG-Datenbankzugriff. **P1:** Start-/Renderlatenz und Log-/UX-Verbesserungen. Bisherige XCMate-Live-TV/Neueste Filme/Serien-Reihen, TVMaze-Fallback, neues Home-Hero-Design, Mini-EPG, großflächiges EPG, BINGIE-Navigation und Branding bleiben erhalten.

## 3. P0-A: Persistenter Senderlogo-Cache

**Referenzmodule:** `station_logos88.py`, `station_logos87.py`, `logo_cache.py`, `logo_manifest86.py`, `art_storage82.py`, `art_storage.py`, `artwork_migration.py`, `artwork_display84.py`, `widget_logo84.py`, `widget_skin88.py`.

**Sollablauf (nicht nur RAM-Sichtbarkeit):**
1. `logo source → sichere URI/Provider-VFS-Prüfung → validierte Bilddaten → eindeutiger Hash/Logo-ID → atomarer lokaler Dateieintrag + verifiziertes Manifest → Kodi-konforme Referenz`.
2. Bei jedem Start zuerst `manifest/disk cache` prüfen und **sofort** eigene Logo-Assets anzeigen (Startsender-Rail, Hero, EPG-Details), ohne Provider-/TMDB-Zugriff für unveränderte Bilder. Kodi Textures13 darf ergänzen, ersetzt aber nicht die eigene verlässliche Referenz.
3. Bei gültigem identischem Logo kein erneuter Download und kein unnötiger `Image.decode`. Bei Fehler/abgelaufenem Remote-Zugriff gültiges bisheriges Logo stehen lassen (`stale-while-revalidate`); kontrolliertes Refresh mit Backoff bei geändertem Senderlogo.
4. Eigenes Cache-Verzeichnis/Manifest müssen ein Update, Neustart, App-Wechsel und Benutzergruppenwechsel überdauern. Cache-Größe und Schreibanzahl begrenzen; nur tatsächliche deduplizierte Senderlogos zählen. Bei defekter Datei gezielt neu herunterladen, nicht alle 88 invalidieren.
5. Prioritäten: alle **bereits vorhandenen lokalen Logos** synchron anzeigen; die ersten sichtbaren fünf Sender, dann Rest im Hintergrund mit niedriger Konkurrenz zu EPG/manueller Benutzeraktion. Remote-Limits schützen, aber nicht jeden Start die 88 Logos wiederholen.

**Speicher-/1-GB-Reserve:** Nutzer fordert, die bisherige 1-GB-Sperre für wenige KB bis MB große Senderlogos zu überwinden. Implementiere **keine globale Reservedeaktivierung**. Prüfe auf realer Box Filesystem/Mount und freien Speicher für `special://home`, `special://profile`, XCMate-Profilordner und `/storage/emulated/0/Android/data/org.xbmc.kodi/files/...` inkl. tatsächlicher Schreibprobe, `statvfs`, Speicher-Mount-Kette und eindeutiger `st_dev`-ID. Das aktuelle selektierte FUSE-Volume meldet **nur ~218 MiB frei** und insgesamt ~4 GB, nicht die von einer anderen Box bekannten ~227 GB. Bei Nachweis eines anderen wirklich größeren geeigneten Volumes: benutzerkonfigurierbare, transaktionssichere, rollbackfähige Cache-Verlagerung. Sonst eine **hart begrenzte Mini-Asset-Ausnahmereserve ausschließlich für validierte Senderlogos**, mit dynamischem freiem Mindestplatz und Total-/Pro-Asset-Quota; bei Fehlplatz ohne Erfolgsmeldung graceful RAM-Cache. Keinesfalls DB oder Kodi-Speichersicherheit gefährden. Bestehendes EPG, Token, Textures13 und andere Add-ons unberührt lassen.

**Diagnose/Abnahme:** Pro Logo getrennte Quellverfügbarkeit, Dekompression, persistiertes File + Hash-Readback, Kodi-Referenz und tatsächlich sichtbarer Skin-Control; `33/88` nach erster Sitzung darf nicht bei jedem Neustart wieder bei 0 beginnen. Vollständiger Restart-Capture mit Netzstatistik (0 wiederholte Downloads unveränderter Logos), belegter freier Speicher vor/nach Cache und real sichtbare Anzahl (maximal die mit gültigen Quellen verfügbaren 88). Falsche Logs `PERSISTED` für RAM-only verboten.

## 4. P0-B: Manueller TMDB-/TVMaze-Match: Suche → Auswahl → Speichern → Anzeige

**Referenzmodule:** `work_manager86.py`, `work_requests86.py`, `work_search86.py`, `work_trace87.py`, `programme_mapping85.py`, `programme_candidates85.py`, `programme_window46.py`, `programme_deadline80.py`, `programme_actions88.py`, `epg_read69.py`.

**Aktuelle technische Kollisionen:**
- `work_manager86.wait`: UI `deadline=time.monotonic()+30`.
- `work_requests86.drain`: Task-Verfall `at` < 35 s, Worker-Limit 24 s, result/stop-Logik mit Cancellation.
- `work_search86.search`: Suche plus viele Kandidatendetails und Posterpreflight, Budget ca. 20–22 s, zusätzlich TMDB/TVMaze-Netz.
- Save prüft Kandidaten über `details()` erneut, revalidiert EPG/Quelle, dann `programme_mapping85.set_mapping` mittels kurzer `writing(timeout=.2)`-Sperre und anschließendem Readback. DB-/EPG-Last kann die Operation verlängern. **Das ist eine Hypothesenliste, nicht ein nachgewiesener einzelner Trigger.**

**Fixkriterien:**
1. Eindeutige Vorgangs-ID/Leases und schrittweiser Fortschritt: `ENQUEUED → PICKED → SEARCH_READY → CANDIDATE_SELECTED → SOURCE_REVERIFIED → EPG_SCOPE_REVALIDATED → WRITE_COMMITTED → WRITE_READBACK → UI_ACK`. Ein gemeinsames Ende-zu-Ende-Deadline-Budget inklusive tatsächlicher Queuing-Zeit; wenn Nutzer abbrechen darf, sind sichere Cancel-/Rollback-Semantiken nötig. Nicht durch blindes Erhöhen aller Timeouts „fixen“.
2. Benutzeraktion gegenüber Backgroundjobs priorisieren; 1 laufender Manual-Worker pro Profil/Ereignis, alte Vorschau-/Suchjobs deduplizieren, keine dauerhaft blockierte Workerqueue. Suche mit progressiven Kandidatenseiten und zeitgemäßer Bildvorschau; Referenzprüfung nur für ausgewählten Kandidaten, nicht unnötig für alle 8 Treffer.
3. Candidate-Auswahl/Manuell bestätigt **noch nicht gespeichert** bis atomarer Commit+Readback; bei einmal tatsächlich bestätigtem Write mit späterer UI-Zeitüberschreitung muss der Rückgabewert **SAVED** wiedergefunden werden. Keine ungültigen/verwaisten unbestätigten Zuordnungen persistieren. Kein „Erfolg“ allein aus GUI Property oder Thumbnail-URI.
4. EPG-Revision anhand stabiler `pid/channel sid/epg event identity/start/stop/title` validieren; bei harmlosen EPG-Refreshes gewählte Zuordnung nach erneuter Bestätigung korrekt rebindbar, bei echtem Identitätswechsel abbrechen mit verständlicher Retry-Funktion.
5. Manuelle TV-/Movie-/Showzuordnung muss nicht nur `TMDB-ID` speichern, sondern eine verified origin/role `poster/backdrop` und eine renderfähige Bildreferenz als Ergebnis nachliefern; wenn Datei-Persistenz blockiert, Metadaten-Commit im sicheren Zuordnungsspeicher von Bildcache unterscheiden. Benutzer kann Suchtext bearbeiten, Quelle TMDB/TVMaze wählen, Ergebnis ansehen, **Speichern** und nach Neustart verifizieren.
6. Aus Log/Journaldaten die Phase der bisherigen Meldung eindeutig aufschlüsseln (`REQUEST_TIMEOUT`, `WORKER_BUSY`, `NETWORK_TIMEOUT`, `EPG_REVISION_CHANGED`, `CANDIDATES_REJECTED`, `PERSISTENCE_BLOCKED`, `READBACK_FAILED`). Keine identifizierenden Portal-URLs/Tokens loggen.
7. **Sichere Quelle/Integrität:** keine Verwechslung von Filmen mit Serien, gleichnamige Sendungen, Edition/Jahr, falsche EPG-IDs, falsche Bilddatei; nur verifizierte TMDB-/TVMaze-Metadaten; bekannte TVMaze-Fallback-Funktion nicht abschalten.

**Reproduktion:** mehrere Sender/EPG-Sendungen mit bereits automatisch vorhandenem Bild, ohne Bild, TV-Serie, Film, identischen Titeln, erneute Auswahl; langsame TMDB-Antwort, 10s/25s/40s Suchzeiten, EPG-Refresh beim Speichern, gestresstes Cache-Volume, Kodi-Neustart. Endzustand `SAVED + tatsächlich angezeigtes Bild`, auch wenn externe Bildspeicherung vorübergehend blockiert ist; kein falscher Erfolg oder endloser Spinner.

## 5. P0-C: Beständige Artwork-/Metadatenverwaltung

Die aktuellen `RAM_ONLY` (99), `METADATA_WRITE_DEFERRED` (166), `RESERVE_BLOCKED`-Ereignisse dürfen nicht zu ständigen HTTP-Neuabfragen, verlorenen bestätigten Zuordnungen oder leerem Hero führen. **Persistenz vs. Sichtbarkeit** auseinanderhalten.

- Prüfe `artwork_db.py`, `event_art81.py`, `sticky_art88.py`, `artwork_display84.py`, `artwork_storage87.py`/tatsächlich existierende Storage-Module, `programme_image69.py`, `programme_requests68.py`. Folge pro Event `found→decoded→shown→written→readback→reused`.
- Gültige sichtbare Bildtextur bei identischer Event-ID behalten, auch wenn Hintergrund-Refresh misslingt; bei echtem Sender-/Event-Wechsel gezielt atomar ersetzen, keine falschen Bildfunde vorziehen. Kodis Texture-GPU-Cache und XCMate-Bildcache getrennt behandeln.
- Fallback: TMDB → TVMaze → gültige EPG-/Provider-Quelle → Senderlogo. Keine falschen Match-Inhalte. Der Nutzer hat echtes TVMaze-Bild beobachtet, das beibehalten werden muss.
- Falls physischer Speicher nur für einige kleine Logos reicht, dürfen Metadaten/Mapping nicht pauschal gelöscht werden; eigene begrenzte, nichtzerstörerische Cachepolicy mit Telemetrie. Keine false positive `PERSISTED`.

## 6. P0-D: Fehlende Fremdwidgets **sichtbar** zurückholen

**Referenzmodule:** `widget_inventory87.py` (read-only SkinShortcuts-Snapshot), `widget_skin88.py`, `widget_skin87.py`, `widget_skin80.py`, `widget_runtime79.py`, `widget_patch85.py`, `widget_hooks45.py`, `widget_reload78.py`, `widget_transaction50.py` sowie tatsächlich installierte BINGIE-`Home.xml`, `IncludesHomeBingie.xml`, `IncludesHomeWidgets.xml`, `script-skinshortcuts-includes.xml`.

**Die .88-Schreibschutzbehauptung bedeutet nur „nicht bewusst überschrieben“; sie beweist kein Render-PASS.** Prüfe von **gespeicherten User-Widgetdefinitionen** `addon_data/script.skinshortcuts` über alle Zwischenschritte bis zu tatsächlich sichtbaren Kodi-Controls:
- Inventar: für jedes Widget `menu/slot/order/name/route/widgetPath/external`, referenziertes Add-on vorhanden/aktiv, Containerliste > 0, gerenderte Zeile, Sichtbarkeitscondition, Parent-Control, Fokus.
- Vergleich: verfügbare echte Originaldefinitionen/Backups vs. jetzige `skin.titan.bingie.mod.properties`, generierte Includes, `Home.xml`, SkinShortcuts-Quellen/IDs. Keine blinde Rekonstruktion absent original widgets.
- XCMate-Eigenreihen `widget_live_start_group`, `widget_recent_vod`, `widget_recent_series` plus **alle vorher wirklich konfigurierten Fremdreihen** gleichzeitig sichtbar. XCMate darf nicht die komplette native BINGIE-Widgetbasis unterdrücken, z. B. durch zu breite Visibility Conditions, ID-Kollision, falschen Container-Bind oder überlagerndes Hero-Control.
- `GUI86 LIST_UNEXPOSED` 504× (`widget_recent_vod`, Control 1520), `WIDGET79 CONTROL_EMPTY` 26×: genaue eigene Ursachen/Video-Frame-/GUI-Thread-/Focus-Bedingungen ermitteln; nicht automatisch mit Fremdwidgets gleichsetzen. `script.skin.helper.widgets` startete laut Log; das ist ebenfalls kein Render-Nachweis.
- Skinupgrade nur minimal und atomar, Checksum/Backup/Restore der **eigenen** Patch-Nodes, benutzerdefinierte Settings/Widgets außerhalb unverändert. Kein Kodi-PVR-Screen-Reset, kein `Skin.Reset`, keine Neuinstallation fremder Add-ons. Vorher/Nachher-Screens + Widget-Snapshot mit ID/Anzahl/Route.

**Feldabnahme:** Mit einem vorher auf der Testbox konfigurierten nachweisbaren Fremdwidget sowie den 3 XCMate-Reihen, Kodi neu starten, auf Home alle Reihen scrollend/fokussierbar prüfen, fremdes Widget öffnen, zurückkehren, Fokus erhalten. Alte Startseitenlayout-Foto-4-Komposition nicht zerstören.

## 7. P0-E: EPG-Read-Timeouts, Cache- und Querystrategie

**Referenzen:** `epg_read69.py`, `epg_refresh74.py`, `epg_poll79.py`, `epg_snapshot75.py`, `epg_fallback67.py`, `library_index.py`, `local_epg.py`, `epg_merge44.py`, `programme_window46.py`, `guide_store.py`.

1. In Logs `EPG_READ_TIMEOUT` 84×, `EPG_DB_BUDGET` 44×, `EPG_DATA_MISSING` 38×, `EPG_CACHE_UNAVAILABLE` 11×. Query-Budget, Lock-/Wartedauer, Datenabdeckung, Cache-State und Input-Provenienz *getrennt* erfassen und beheben.
2. Gemeinsamer Snapshot pro Quelle/Sender/Event und genormte Zeitbasis, `single-flight`-Refresh, gezielte Batch-Queries, bounded retry/backoff, korrekt verwaltete Reader, keine GUI-Blockierung und keine Refresh-Schleifen beim Hover. **Gültiges EPG während transientem Read-/Netzfehler behalten.**
3. Gleiche EPG-Eventidentität/Titel/Start/Ende in Mini-EPG, großem Grid, Hero und Detailansicht. Bereits bestätigte manuelle Zuordnungen bei unverändertem Programm nicht durch Revision-Churn invalidieren.
4. Regression: `Reader.close()`-Absturz ist in .88 **nicht erneut aufgetreten**; Unit-Test für Reader-Lebenszyklus und mehrfache Source-Refreshes behalten.

## 8. P1: Startzeit, Prioritäten, Benutzerinteraktion

**Warm start:** Persistente EPG-/Logo-Referenzen zuerst (einfach rendern, ohne HTTP/SQL-Nachscan). **Cold start:** EPG/Startsender-ID → Rail-Logos → sichtbar ausgewählter Hero + erste 5 Sender → Restbilder → VOD/Serien-Cover → andere Widgetposter. Manuelle Suche/Speichern hat höhere Priorität als Background-Artwork. Limits auf ARMv7-4-Core/geringem RAM vorsichtig wählen, keine 88 gleichzeitigen HTTP-Anfragen. Gemessener VOD-Widget-Call aus Android-Log ca. 32,5 s; Poll-/GUI-Stalls reduzieren.

**BINGIE/Designschutz:** Aktuelle .88-Home von Nutzer positiv beurteilt. Hero rechts mit weichem dunklem Verlauf links, schmale Senderlogo-Rail, große Sidebar-Icons, vorhandenes XCMate-Branding und funktionierende Details/Merkliste/Player-Funktionen **regressionsfrei** bewahren. Keine Änderung des GS Media Setup Wizard oder fremder Skin-Widgetkonfigurationen außerhalb eines belegten, reversiblen Fixes.

## 9. Testmatrix (Host / native Kodi / echtes Android **getrennt**)

| Testfall | Automatisierbarer Teil | Echte Android-Abnahme |
|---|---|---|
| Logo erstmalig | HTTP(S)/Kodi VFS, Größe/Hash, atomar, Quota | Verfügbare Startgruppe-Logos erscheinen, sichtbar gemessen |
| Logo Warmstart | Mock-Zusammenführung Cache + Repo-Upgrade | Kodi vollständig beenden, Neustart **ohne erneuten Download** gleicher Logos, Rail/Hero/Details sofort da |
| Low-Space | 4GB FUSE, ~218 MiB frei, 1GB reserve; anderer `st_dev`, readonly | Kein Crash/DB-Verlust, kleinstmöglicher begrenzter Logo-Cache, auditierter freier Speicher |
| Manual TMDB / TVMaze | Search/pick/reverify/EPG scope/write/readback, 30s/24s race, negative cases | Auswahl wird angezeigt und bleibt nach Neustart, kein falscher Timeout |
| Artwork | Sticky valid image, positive/negative refresh, event switch | Kein 45-s-Verschwinden, richtiges Senderlogo bei fehlendem Bild |
| Fremdwidgets | Read-only inventory, SkinShortcuts Diff, Visibility/route unit checks | Mit *real konfiguriertem* Fremdwidget plus 3 XCMate-Reihen sichtbare und bedienbare Reihen |
| EPG | Reader-Lifecycle, Busy Locks, 4 View-Consistency, Recovery | Mini-EPG, Grid, Hero und Details stimmen für gleiche Sendung überein |
| Upgrade-Schutz | .88→.89→Rollback, Tokens/DB/Profile Widget-Diff | Nichts gelöscht/überschrieben, TMDB manuell importierter Token bleibt |
| Performance | Cold/Warm timings, Requests/Asset, Queuelänge, UI-Frame | Logo Warmstart rasch, Remote ohne Spinner/Focusverlust |

**Definition of Done:** Code-Fix mit Root-Cause pro P0, Testschlüssel/Lognotizen ohne Secrets, tatsächliche Belege für alle Android-Testfelder, A/B-Metriken `Logo Download N → nach Neustart 0`, aktives persistiertes Manifest, vollständige Widgetinventur, manuelle `SAVED/READBACK/VISIBLE`-Quittung, CI grün. Echte Android-Abnahme, die Codex nicht selbst durchführen kann, als **`ANDROID_NOT_TESTED`** kennzeichnen, **nie als simulierten PASS**.

## 10. Verbindliche Codex-Liefergegenstände

- Separater Branch, z. B. `fix/xcmate-02989-android88-p0-cache-mapping-widgets`, mit **Draft PR** gegen `main`, referenziert **#425**.
- Versionsbump `plugin.video.xtreammate` nach `0.1.29.89`. Bereitgestelltes Test-ZIP im bisherigen Standardtestpfad `docs/XCMate/test-builds/02989/` inkl. Datei/Hash-Readback und SHA-256.
- Änderungsbericht: Fehlerbild → belegte technische Ursache → Fix → Gegenprobe, pro P0 ein eigener Test-/Diagnoseabschnitt; explizit unterscheiden `HOST_PASS`, `NATIVE_KODI_PASS`, `ANDROID_NOT_TESTED`/Android-Feld-PASS.
- Keine eigenmächtige Veröffentlichung, kein Update anderer Add-ons oder der drei Kanäle, keine Bereinigung „überflüssiger Dateien“ bei Installation; sichere Datenhaltung vorrangig.
- Falls Screenshot-4-Bildvergleich oder die Original-Logs benötigt werden: Die Dateien liegen **nur im Chat** und nicht im öffentlichen Repository. Statt Daten zu erfinden: redigierte Testdaten verwenden oder bei echtem Android-Feldtest vorhandenes Material intern dem Benutzer zuordnen.

## 11. Projektverweise

[#425 – Masterauftrag .89](https://github.com/artattakk-creator/kodi-noodleprivate/issues/425) · [#421 – .88 Home/Details](https://github.com/artattakk-creator/kodi-noodleprivate/issues/421) · [#414 – Senderlogo-Probleme](https://github.com/artattakk-creator/kodi-noodleprivate/issues/414) · [#413 – manuelle TMDB-Zuordnung](https://github.com/artattakk-creator/kodi-noodleprivate/issues/413) · [#401 – Storage-Persistenz/Migration](https://github.com/artattakk-creator/kodi-noodleprivate/issues/401) · [#411 – Home-Referenz](https://github.com/artattakk-creator/kodi-noodleprivate/issues/411) · [#417 – Joomla-Gateway BACKLOG](https://github.com/artattakk-creator/kodi-noodleprivate/issues/417) · [#423 – .88 Releasefreigabe](https://github.com/artattakk-creator/kodi-noodleprivate/issues/423) · [PR #422](https://github.com/artattakk-creator/kodi-noodleprivate/pull/422) · [PR #424](https://github.com/artattakk-creator/kodi-noodleprivate/pull/424).

## 12. Direkter Kurzauftrag für Codex

> **Arbeite Issue #425 und dieses Masterdokument vollständig ab. Entwickle XCMate 0.1.29.89 mit P0: dauerhaft sichere Logo-Speicherung auf einem real verifizierten Volume / separatem Mini-Cache trotz bisheriger 1GiB-Blockade (ohne globalen Speicherschutz abzuschalten); zuverlässige manuelle TMDB/TVMaze-Bildzuordnung mit atomarem Commit und echtem Readback; persistentes/stabiles Artwork; alle real konfigurierten fremden BINGIE-Widgets zusätzlich zu den 3 XCMate-Reihen tatsächlich anzeigen; EPG-Timeouts beheben. Die neue .88-BINGIE-Home sowie Token/EPG/Benutzerdaten bewahren. Erstelle branch + Draft PR, umfassende Host/native Tests, Test-ZIP + SHA256; echte Android-Tests als offen kennzeichnen, sofern nicht ausgeführt. **KEIN Merge und KEINE Veröffentlichung** ohne neue Freigabe.**

## 13. P0-G: Film-/Serienkataloge und Cover auf BINGIE-Home (Benutzernachtrag 11.11.2026)

**Neuer echter Benutzerbefund zu installierter XCMate .88:** Filme und Serien auf BINGIE Home scheinen nicht zuverlässig aktualisiert zu werden. **Filmposter waren zunächst sichtbar, verschwanden später wieder**, obwohl der Benutzer keinen Wechsel der Filme/Serien ausgelöst hat. Das **ist ein Beobachtungsbericht, noch kein bewiesener eindeutiger Log-/Code-Rootcause**. Die .88-Hero-Optik soll unverändert bleiben. Dieser P0-G ist **verbindlicher Bestandteil von .89**, zusätzlich zu den bestehenden P0-A..E und dem P0-F-Hero-Quellen-Lock-on im Issue #425.

### A. Bestehender Code / belastbare Verdachtsmomente

- `src/plugin.video.xtreammate/resources/settings.xml`: `xc_background_prefetch` hat **default=false**. In `service.py` läuft `_maybe_warm_catalogs()` nur bei aktivierter Einstellung und freigegebener Netzwerkphase; dann wird höchstens alle **1800 Sekunden geprüft**, nicht garantiert alle 30 Minuten der gesamte Film-/Serienkatalog erfolgreich neu importiert. `epg_auto_refresh=true` und `epg_refresh_hours=24` betreffen das **EPG**, nicht automatisch die Film-/Serienlisten. **Tatsächliche Box-Einstellung ist unbekannt.**
- `catalog_jobs73.py` / `vodsync72.py` / `vodsync_store72.py`: Ein ausdrücklicher vollumfänglicher Kataloglauf besitzt persistente Jobs mit `last_api_success81`, `last_full_sync81`, `delta81(new/changed/unchanged/read)`, Commit-Readback und fehlertolerantem Generationenwechsel. `catalog_ui73.py` bietet den Dialog `Katalog aktualisieren`; **kein Erfolg annehmen, bevor neue Providerobjekte im lokalen Index sichtbar sind**.
- `latest_media.py` nutzt `first_seen` und Provider-`added`; im Widget ist die Reihenfolge **Neueste Filme / Neueste Serien** auf Quelle und Indexrevision zu prüfen, nicht blind bei jeder Sitzung „alle neu“ setzen.
- `widget_data41._snapshot84()`: VOD-/Seriensnapshots werden durch `WidgetReader`/SQLite und JSON-LastGood geladen; Speicherstatus oder SQL-/Lock-Budget kann zu `LOCKED / BUDGET / CACHE_UNWRITABLE / CACHE_STORAGE_FULL` führen; nach Quellen-Refresh dürfen gültige bisherige `rows` bei transientem Fehler nicht verschwinden.
- `widget_assets69.read()` / `_references82()`: Bildreferenzen hängen an einer **maximal 30 Sekunden** gültigen Provider-/DNS-Freigabe; `widget_cache82`, `widget_cache79`, `render_cache81`, `widget_refs74` versuchen lokale Wiederverwendung. **Ein ablaufender kurzlebiger Remote-URI ist nicht gleichbedeutend mit ungültigen bereits lokal verifizierten Bildbytes.** `_run()` bearbeitet `vod`/`series` nach GUI-/Background-Budgets und `artwork_health82.guard`. **Damit ist Coverflattern plausibel, aber nicht die genaue Ursache jedes vermissten Posters bewiesen.**
- `widget_render47.values()` beabsichtigt ausdrücklich, gültige Katalogzeilen auch bei fehlendem Artwork zu erhalten. Im .88-Log (vorheriger Prüfbericht) traten `GUI86 LIST_UNEXPOSED` **504×** (v. a. VOD-Control 1520), `WIDGET79 CONTROL_EMPTY` **26×**, `LOCAL_CACHE RAM_ONLY` **99×**, `METADATA_WRITE_DEFERRED` **166×** auf. **Das sind Log-Events und keine Zählung verschwundener Cover oder Beweis, dass derselbe Fehler die Katalogaktualisierung blockiert.** Beide Ebenen getrennt messen.

### B. Verbindliche Implementierung .89

1. **Katalog-Aktualität unabhängig vom Artwork:** Auf der Box pro Portal + `vod/series` die zuletzt *erfolgreich* abgeschlossene Provider-Abfrage, den letzten vollständigen Index-Commit und die aktive Generation anzeigen. Echte `new/changed/unchanged/deleted_or_retained`-Deltas und Fehlercode je Gruppe dokumentieren; keine rein kosmetische Anzeige von „aktualisiert“ aufgrund einer angestoßenen Anfrage. Zuordnung neuer Providerfilme/-serien und entsprechender Poster zum sichtbaren BINGIE-Widget nach erfolgreich bestätigtem Readback prüfen.
2. **Planbarer Aktualisierungslauf:** Klare Trennung von EPG 24h und VOD-/Serienkatalog-Refresh. Bereits vorhandene `Katalog aktualisieren`-Funktion muss vollständig funktionieren (Anforderung → Sicherung → Gruppenimport → transaktionaler Publish → Readback → Widget-Revision → Sichtkontrolle). Ein optionales, ausdrücklich konfiguriertes **inkrementelles Aktualisierungsintervall, z. B. 24 Stunden** (keine versteckten automatischen Massendownloads, bestehende `xc_background_prefetch`-Opt-out respektieren), kann für die ständigen neuen Providerinhalte ergänzt werden. Bei inaktivem automatischem Refresh Status/„manuell aktualisieren“ verständlich anzeigen.
3. **Nicht-destruktive Kataloggenerationen:** Niemals bei `SOURCE_EMPTY`, Timeout, Rate-Limit, Lesesperre, `RESERVE_BLOCKED`, Netzwerkunterbrechung oder falscher Revision eine vorher verifizierte Film-/Serienliste als leere Generation publizieren. Keine bereits vorhandenen IDs/Zeilen löschen, bloß weil ein einzelner Provider-Aufruf leer ist. Lokale Snapshot-/DB-Korruption sauber diagnostizieren und auf letzte gute verifizierte Revision zurückfallen. Änderungen von `added`, Kategorien und Provider-Metadaten deduplizieren; Nutzerfilter (inkl. explizit gewählter Gruppen), Favoriten und Startseitenlayout wahren.
4. **Sticky Movie/Series Poster:** Pro Portal + Medientyp + Providerobjekt-ID + Artwork-Rolle (Poster/Fanart) den **zuletzt verifizierten renderbaren lokalen Dateipfad/Hash** für ein identisches Widget-Item behalten, auch bei fokussiertem BINGIE-Widget und nach Rebind. Bei temporärem Ablauf der DNS-/Source-Lease, kurzzeitigem `SOURCE_MISSING`, fehlerhaftem Refresh, `RAM_ONLY` oder blockiertem Disk-Write sichtbares bereits gültiges Cover **nicht** durch leer ersetzen. Cover ersetzen nur bei belegter neuer Posterrevision, ausdrücklicher Benutzeränderung, echter Identitätsänderung, Integritätsfehler oder gültiger Quell-/Security-Revocation. Keine stale Remote-URL blind verlängern; **verifizierte lokale Bytes** per sicheren Cache-Mechanismus wiederverwenden.
5. **Dauerhafte Cover-Persistenz:** Gemeinsame Volumen-/Quota-Strategie mit P0-A/C, atomare Datei-/Manifest-Schreibvorgänge und Readback, Priorität **erst Logo/EPG/Hero und dann sichtbare Film-/Seriencover**, Rest Hintergrund. Kodi-Texturcache als Zusatz, nicht einzige garantierte Persistenz. Wenn Volume zu knapp: ehrlicher Session-Cache + kein False-`PERSISTED`; zuvor lokal vorhandene Cover nicht wegen `METADATA_WRITE_DEFERRED` leeren.
6. **Widget-/Skin-Binding:** Für jeden problematischen Posterplatz protokollieren: Katalog-ID/index revision, `WidgetReader`-Snapshot, `ListItem.Art(poster)`, XCMate Art-URI/Hash/Storage-Status, Skin Control-ID/Visibility/Item Count/Generation, Kodi Texture-Cache-Receipt und reale Display-Akzeptanz. Unveränderte Listen nicht bei jedem Poll als neue leere Liste setzen. Keine `LIST_UNEXPOSED`-Fälle als erfolgreich gerendertes Cover verbuchen. **Fremdwidgets aus P0-D bleiben zusätzlich erhalten.**
7. **Performance:** Vermeide parallele Massenscans bei Kodi-Start. Manuelle TMDB-Zuordnung und EPG-Priorität höher als VOD-Coverabrufe; inkrementelle Katalogprüfung und sichtbare erste Poster priorisieren. Einmal geladenes Cover darf bei Gruppen-/Hero-Fokuswechsel nicht erneut komplett bezogen werden.

### C. Abnahmetests für Codex und reale Android-Box

- **Katalog:** Provider simuliert 2 neue Filme, 2 neue Serien und geänderte Cover; `Katalog aktualisieren` führt zu neuem Index-Snapshot, mit `new/changed/unchanged`-Belegen und sichtbaren Widgets; bei leerer/abgebrochener Providerantwort bleiben vorherige Titel/Serien und deren Cover erhalten. Auch `xc_background_prefetch=false`, wiederaufgenommene Jobs und Update .88→.89 testen.
- **Cover-LastGood:** Ein bestätigtes BINGIE-Filmcover und Seriencover erscheinen; 5/30/45/90 Sekunden später bei Remote-Lease-Expiry, DNS-Fehler, SQLite-Lock und `METADATA_WRITE_DEFERRED` bleiben **dieselben Cover sichtbar**, kein leeres Platzhalterbild. Reale Provider-Coveränderung aktualisiert nur den betroffenen Eintrag nach erfolgreicher Prüfung. Kein neues Cover von falschem Item.
- **Neustart:** Mindestens fünf zuvor sichtbare Filmcover und fünf Seriencover nach vollständigem Kodi-Neustart aus verifiziertem lokaler Cache verfügbar, **sofern ausreichend Speicher vorhanden**; separate dokumentierte Low-Space-Abnahme bei nur ~218 MiB frei. Keine vorgetäuschte Disk-Persistenz bei nur RAM.
- **Widget:** XCMate Live-TV/Film/Serie plus ein vorher vorhandenes fremdes BINGIE-Widget sichtbar, Fokus/Scrolleigenschaften korrekt; keine anderen Benutzer-Widgets überschreiben.
- **End-to-End-Evidenz:** `SOURCE_FETCHED → CATALOG_COMMITTED → READBACK_OK → WIDGET_ITEMS_PRESENT → POSTER_LOCAL_VERIFIED → ART_PROPERTY_SET → TEXTURE_RENDER_CONFIRMED`, mit Zeiterfassung; Test auf tatsächlicher Android-RK3528-Box **getrennt** von Host/Linux-Test. Ohne echte Android-Abnahme Status `ANDROID_NOT_TESTED`, nicht PASS.

### D. Beziehungen zu anderen Aufträgen und Freigabe

Dieser P0-G ergänzt **#425** (XCMate .89) zusammen mit P0-F (Hero-Bild-Lock-on) und **#427** (manuelle EPG-Senderzuordnung *nach* .89). Für die Film-/Serienlisten gilt **kein Wechsel des ästhetisch gelungenen .88-Hero-Layouts**, kein GS-Media-Setup-Release, kein Joomla-Gateway, keine unaufgeforderte Löschung von Album-/Datenbank-/Coverresten.

**Freigabegrenze unverändert:** eigenständiger .89-Branch + Draft-PR, native Tests, ZIP+SHA256; **KEIN Merge und KEINE Veröffentlichung auf main/regulär/Pilot/NeoDark3** ohne explizite Freigabe.
