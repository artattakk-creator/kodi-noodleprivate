# Codex-Übergabe: XCMate 0.1.29.90 – P0 Android-Hotfix aus tatsächlicher .89-Abnahme

**GitHub Masterissue:** [#430](https://github.com/artattakk-creator/kodi-noodleprivate/issues/430) (maßgeblich, vollständige sanitized Logs/Tests), Rückbezug auf .89-Master [#425](https://github.com/artattakk-creator/kodi-noodleprivate/issues/425), .89 Source-PR #426 und Release-PR #429.

**Releasebasis:** `plugin.video.xtreammate` Version `0.1.29.89` auf `main`, regulär, Pilot, NeoDark3; freigegebener Release-Commit `b364dc618c3bbd5385eeff97a450b62ff80abfe1` (bei Arbeitsbeginn aktuellen main-Head auf etwaige spätere Änderungen prüfen). Hotfixversion **0.1.29.90**, gesonderter Branch + Draft Pull Request, **keine automatische Veröffentlichung oder Merge**. GS Media Installer 0.5.26 und Installer-Draft #428 ausdrücklich nicht einbeziehen.

## 1. Gegenüberstellung der echten Android-Logphasen

Sechs vom Nutzer bereitgestellte Logs, **fünf verschiedene Byteinhalte und drei zusammenhängende Laufphasen** (nicht als sechs unabhängige Tests zählen). Identische `.88`-`kodi.old`-Dateien wurden zweimal hochgeladen, neuere `kodi.log`-Dateien und `kodi.old` sind jeweils überlappende/erweiterte Mitschnitte. Keine unbereinigten Originaldateien in GitHub!

| Logphase | Zeit in Kodi-Log | Version | maßgeblicher Befund |
|---|---|---|---|
| Altlauf | 10:56:24–12:43:43 | 0.1.29.88 | `LOGOS_LOCAL_READY` zuletzt 33/88, `LOGOS_RAM_READY` 55/88, klassische Logo-Reservesperre 58×; **nur Vergleich** |
| Installations-/Übergangslauf | 12:45:46–13:16:07 | zu Beginn .88; .89 ab 12:57:49 | 58 `LOGO89 PERSISTED_VERIFIED`, `HOME86 LOGOS_LOCAL_READY` 0→58/88; `EPG69 EPG_READ_TIMEOUT` 40×, `GUI86 CALLBACK_FAILED` 10× |
| erster sauberer .89-Neustart | 13:16:13–13:22:53 | 0.1.29.89 bestätigt | `HOME86 LOGOS_LOCAL_READY` 59/88 um 13:17:59 → 68/88 um 13:22:30, weitere 12 `LOGO89 PERSISTED_VERIFIED`, 32 `LOGO87 TEXTURE_CACHED` (keine Pixelbeweise); `EPG_READ_TIMEOUT` 7×, `EPG_DB_BUDGET` 7×, `EPG_CACHE_UNAVAILABLE` 14×, `GUI86 CALLBACK_FAILED` 4× |

**Wichtige Einordnung:** .89 **hat** eine funktionierende neue lokale Minicache-Persistenz für Logos, aber beim Neustart liegen längst noch nicht 88 verifizierte Dateien vor. 59/88→68/88 deutet **nicht** auf vollständiges Cachevergessen hin, sondern auf **unvollständigen/zu langsamen Erstaufbau**. Erst nach nachgewiesenem 88/88-Stand ist ein verbindlicher Zero-Download-Kaltstarttest valide. Einige der nominellen 88 Stationen können ggf. überhaupt keine valide Logoreferenz haben; pro SID sauber begründen statt 88/88 fälschen.

**EPG:** Bei fünf `EPG63 stage=HOME_NOW_NEXT_READY`-Aufrufen im reinen .89-Neustart: 4× `EPG_CACHE_UNAVAILABLE`, 1× `EPG_DATA_MISSING`; **0 READY**. Keine Behauptung, dass die EPG-Datenbank gelöscht worden wäre. `T01 Neustart` **FAIL**, `T02 Senderlogos` **FAIL/incomplete**, alle anderen Androidfälle bis expliziter Prüfung offen.

**GUI:** 4× `GUI86 CALLBACK_FAILED` im reinen .89-Neustart, Stack-Traces u.a. `widget_home50.render → live_rail86.values → live_text63._hero → station_logos88.reference → portals.get_by_id → portals._read` sowie `widget_entry46.dispatch → app_routes.widget → programme_assets47.read_many → portals.get_by_id → portals._read`. Das geloggte `exception=OTHER` ermöglicht **keine** Aussage über den konkreten Python-Ausnahmetyp. Auf aktiver Box im Hotfix zunächst sichere Fehlerkategorie und Lock/IO-Status zusätzlich erfassen, nie Credentialwerte.

**Bilder/Widgets:** Nach 13:16-Neustart 17× `WIDGET79 stage=CONTROL_EMPTY`, 5× `TEXTURE_PENDING`, 3× `TEXTURE_REQUESTED`, aber daraus keine eindeutige Aussage über optische Bildpixel. Ein neu vorhandener TMDB-Hit muss in der UI ausdrücklich nachgewiesen werden. `IMAGE77` hat 13 Phase-Events im Neustartlog, nicht 13 verschiedene Bilder.

**Speicher:** `ART_STORAGE82` zeigt das aktiv ausgewählte lokale FUSE-Volume mit 4.034.297.856 Bytes Gesamtkapazität; im .89-Übergangslauf freier Speicher ca. 132→115 MB; nach Neustart ~118 MB. Generische Artwork-Reserve 1 GiB blockiert Teile der nicht-logo-spezifischen Writes. Der **separate .89-Logo-Speicher** lässt unter kontrollierten Bedingungen eine Reserve von ~80,7 MB und 16 MiB Logo-Quota zu, `PERSISTED_VERIFIED` wird geloggt. Weder globalen 1-GiB-Schutz entfernen noch Bild-EPG an 2/6 GiB koppeln. Fehlende physische 256-GB-Volume-Zuordnung ist eine separate Datenträgerfrage, nicht blind ändern.

## 2. Präzise Codeeinstiege und Arbeitshypothesen

1. `resources/lib/station_logos88.py` `prepare()` Z. 94–150: **höchstens zwei neue Versuche pro Aufruf** (Z. 105–118), dedupliziert über _due 60s; jedes Mal `manifest_read(...)`/stable89-Check, ggf. 88er-Loop. Verifizieren, ob Nachlade-Reihenfolge und Retry die 18-Minuten-Ersthydration erklären.
2. `resources/lib/widget_assets69.py` `_run()` Z. 137–190: ein gemeinsamer Worker für Logo, VOD-/Seriencover, render cache und Hero; bei `kind=live` sind `station_logos87.recover`, `station_logos88.recover`, `logo_manifest86.prepare`, `station_logos88.recover` sequentiell; danach weitere Bild-/Art-Worker. Nachweisbare Engpassphase instrumentieren, **kein pro-Bild GUI-Thread und kein unbegrenzter zusätzlicher Threadpool**.
3. `resources/lib/logo_manifest86.py` `read()` Z. 33–76: liest Manifest, prüft stable identity, Fallback-Referenzen; pro Zeile Datei-`stat` und `logo_store89.valid_file` (erstmals SHA256). Manifest-JSON und Scope-Hash nicht pro einzelnen ListItem/Kodi-Callback erneut berechnen; **ein read-only Batch-Snapshot pro Portal+Profil+Groupgeneration** verwenden und gezielt invalidieren. Keine ungültigen/stale Bildreferenzen blind akzeptieren.
4. `resources/lib/logo_store89.py` `capacity()` Z. 34–54 und `persist()` Z. 71–98: pro Logo Validierung und Atomic-Write/Readback + kompletter Directory-Scan/Manifest-Commit. Cache begrenzte, vertrauenswürdige Stat-/Quota-Informationen nur dann, wenn externe Veränderungen/Volume-Identität sicher erkannt werden. Atomarität und Schutzfloor erhalten.
5. `resources/lib/live_rail86.py`, `widget_home50.py`, `home_status86.py`: Rail-Read-First, zuletzt gültige Artikelliste behalten, lokale Bildreferenzen in einer batchgeprüften `ListItem.Art`-Generation sofort setzen; Status `X / 88` nicht mit UI-Pixel-PASS gleichsetzen. Wiederholte `GROUP_READ_MS` 631/407/875 ms nach Neustart.
6. `resources/lib/portals.py` `_read()` und `portal_snapshot.py`: 4 `CALLBACK_FAILED` führen zu dem Profil-/Portal-Read; bereits verifizierten, unveränderlichen Portal-Snapshot an die Render-/Worker-Generation übergeben, bei Konfigurationsänderung/Portalwechsel invalidieren. Portals.json nicht pro Live-Hero-Pixel erneut auslesen; Fehlerursache erst nach safe instrumentation entscheiden.
7. `resources/lib/epg_single89.py`, `epg_poll77.py`, `epg_handoff63.py`, `epg_read69.py`, `local_epg.py`: Warm LastGood aus stabiler Event-ID vor GUI-Leseversuch anbieten, read-only SQLite-Routinen/Lockbudget separat prüfen. Kein sichtbar falscher Sender/alte Sendung nach Programmwechsel; kurzfristiger Busy darf zuletzt sicher gültige Home-Texte nicht leeren.
8. `widget_runtime79.py`, `widget_assets69.py`, `programme_assets47.py`: 17 CONTROL_EMPTY/5 TEXTURE_PENDING und 4 Callback-Fehler nach Restart mit tatsächlichem Kodi Control-/ListItem-/Texture-Receipt korrelieren; Fremdwidgets + Film/Serie nicht durch Live-Start-Fix verlieren.

## 3. Hotfix-Abnahme, Testfälle T90-01 bis T90-08

| ID | Verbindlicher Test |
|---|---|
| T90-01 | Startgruppe vorerst mit unvollständiger Logo-Menge laden: bekannte manifestgültige Icons **innerhalb 10s Zielwert** nach UI-ready korrekt anzeigen, Unvollständige im Hintergrund, kein blockierender N×Manifest-Scan; eindeutige Quelle pro Station |
| T90-02 | Einmaliger kompletter 88er-Bestand nachweisbar oder stationgenaue No-Logo-Fakten. Danach 2 komplette Kodi-Neustarts ohne Cache-Löschen: alle vorhandenen persistenten Icons **innerhalb 10s**, 0 erneute HTTP-Logo-Downloads/0 doppelte Manifest-Commits, Hash-/Volume-Identität verifiziert, 1080/720 Kodi-Pixeltest |
| T90-03 | 115-MB Low-Space + 80,7-MB Floor: fortlaufender Logo-Import innerhalb Schutzgrenzen, bei Unterlauf kontrolliert stoppen; bereits vorhandene Icons sichtbar, keine unzulässigen Neu-/URL-Writes oder Quota-Bypasses |
| T90-04 | Gültiger lokal vorhandener EPG Now-/Next-Snapshot vor Neustart: **bis 30 s Zielwert** korrekter Titel/Start/Ende in BINGIE Home; keine 0/5 Ready-Rückgaben bei lokalem Bestand; Event-/Senderwechsel korrekt, DB-Busy hält genau passenden LastGood |
| T90-05 | 15 Minuten Home + 20 Sender-/Fokuswechsel, 0 `CALLBACK_FAILED`, Portal-Lesewege safe; aktive Portale/Settings erhalten |
| T90-06 | Film-/Serienlisten und eigene/fremde BINGIE-Reihen nach Neustart sichtbar; Cover bleiben, kein Neuladen kompletter Listen im Vordergrund; keine Verschlechterung der .89-Erinnerungen/TVMaze-Hero-Logik |
| T90-07 | Relevante Worker-/URI-/Queue-/Profil-/DB-Zeitbudgets tracken: nachvollziehbar `MANIFEST_LOAD_MS`, `LOCAL_HIT`, `FIRST_RAIL_PIXELS_MS`, `REMOTE_FETCH_COUNT`, `PERSIST_COMMIT_MS`, `EPG_LASTGOOD_AGE`, `CALLBACK_FAIL_REASON`. Sanitized, ohne Token/URLs/Stammdaten |
| T90-08 | Regression: Kodi 21.3 Android ARM32 mit tatsächlichem Gerät **plus** native 720p/1080p und Host-CI; ZIP-Repro + SHA256 und Dateibestand; keine Löschung, Installer/Provider/Skin/-EPG-Daten unverändert |

Testziel 10s Logo-Display und 30s Now/Next ist **Abnahmekriterium, kein bereits nachgewiesener Wert**. Bei tatsächlich fehlenden Logos statt blindem Erfolg verständlich ausweisen. Diagnostische und tatsächliche Bildpixel-Tests getrennt.

## 4. GitHub-/Release-Workflow

1. Kontext prüfen: `main`, Issue #430, Doc hier und priorisiertes Wissen aus #425/#427. **Neue** Version 0.1.29.90 auf separatem Fix-Branch.
2. Profiling/Fehlerreproduktion über synthetische Android-nahe Tests (88 Logos, langsame Netzzeit, 115MB freies FUSE, 16MiB Quota, per-Station Missing URI, EPG-DB-Lock) und native Kodi-Testumgebung.
3. Gezielte technische Fixes plus Tests, die vor Fix rot und nach Fix grün sind; Verifizierung aller Kodi-Profile/Portale und LastGood-Identität.
4. Test-ZIP, SHA256, Dokumentation und **Draft-PR** erstellen; keine Änderung an `addons.xml`, regulär, Pilot, NeoDark3, `script.gsmedia.setup` ohne neue Nutzerfreigabe.
5. Echte Android-Abnahme bleibt `ANDROID_NOT_TESTED`, bis der Nutzer .90 auf der Box getestet hat. Kein automatischer Merge, keine Weitergabe von Raw-Kodi-Logs an GitHub.

## 5. Kompakter Codex-Startbefehl

```text
Erstelle XCMate 0.1.29.90 als P0-Android-Hotfix gemäß GitHub-Issue #430
und docs/XCMate/CODEX_UEBERGABE_02990_ANDROID89_STARTUP_LOGO_EPG_2026-11-11_DE.md.
Fixe die langsame, unvollständige Wiederherstellung der Senderlogos (59→68/88
nach Restart trotz 58 vorher persistierten Logos), die 0/5 READY EPG-Home-
Übergaben nach .89-Kaltstart und die Portal-CALLBACK_FAILED im Hero-/Widgetpfad.
Profil/EPG/Token/Benutzerwidgets erhalten, echte Ursache instrumentieren, keine
Globalreserve abschalten. Prüfe 88er-Ersthydration, Zero-Download-Kaltstart,
EPG-LastGood, 15-Minuten-GUI, Memory/Low-Space, native 720p/1080p und Android
als offen. Erstelle Branch + Draft-PR + reproduzierbares ZIP+SHA256.
KEIN MERGE, KEIN RELEASE ohne neue Freigabe.
```
