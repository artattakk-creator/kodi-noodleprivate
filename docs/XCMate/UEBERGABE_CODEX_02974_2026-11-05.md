# CODEX-ÜBERGABE: XCMate 0.1.29.74 – P0 Home-Stabilität, Fokusrahmen, TVMaze/TMDB-Bilder

**Verbindlicher Entwicklungsauftrag | 05.11.2026**

- **Repository:** https://github.com/artattakk-creator/kodi-noodleprivate
- **Hauptissue:** https://github.com/artattakk-creator/kodi-noodleprivate/issues/361 (vollständige Ursprungsdiagnose und Nachträge lesen)
- **Ausgangsversion:** XCMate `0.1.29.73` (PR #360, gemergt)
- **Ziel:** nächstes kumulatives Release `0.1.29.74` (nur wenn `main` inzwischen nicht weiter ist)
- **Add-on:** `plugin.video.xtreammate`
- **Plattform:** Kodi 21.3 Omega, Android ARM32 / RK3528, Titan BINGIE MOD 2.2.3; Kodi 21.2 kompatibel halten
- **.70-Referenz:** `5eccd48c9605670e7fbd43a6406b241c3e7d8c70`. Box B wurde erfolgreich von `.70` auf `.73` aktualisiert; die **bestehenden** Widgets funktionieren. Eine frische `.73`-Widget-Auswahl funktioniert nach Nutzeraussage nicht zuverlässig.

## 0. Arbeitsregeln

1. **Sofort** aktuellen `main`, offene PRs, `addon.xml`, Issues #357/#358/#359/#361 und diesen Bericht auslesen. Auf aktuellem `main` einen Entwicklungsbranch erstellen; Version bei neuem Zwischenstand kumulativ anpassen.
2. **P0 zuerst**: A Fokusrahmen, B bereits vorhandene Home-Daten verschwinden, C echte Sendungsbilder, D Standardwidget-Auswahl. P1 Performance. Kein themenfremder Refactor oder unerledigtes Internationalisierungsfeature vor P0.
3. **Datenschutz/Bestandsschutz:** keine Deinstallation, kein Kodi-/Skin-Reset, keine ungefragte SkinShortcuts-Neuanlage, keine Provider-/EPG-/TMDB-Token-/Favoriten- oder Katalogmigration mit Datenverlust. Benutzerkonfiguration und `widget_live_start_group`, `widget_recent_vod`, `widget_recent_series`-Routen müssen identisch bleiben. Keine geheimen Pfade, Hostnamen, URLs, Tokens oder Rohlogs in GitHub committen.
4. **Skinänderungen** nur eng begrenzt, adapterversioniert und optional nach Vorher/Nachher-Sicherung, SHA-Baseline, expliziter Freigabe und Restore-Pfad. Update selbst darf Skin-XML und gespeicherte BINGIE-Bindings nicht überschreiben.
5. Tests (Host/CI) und **echte Android-Geräteabnahme** strikt getrennt; letzterer Status bis Bestätigung `ANDROID_NOT_TESTED`.
6. Liefere PR mit Tests, Diff, ZIP, SHA-256, Changelog, Verifikationsprotokoll. **Nicht automatisch nach main mergen und nicht veröffentlichen.**

## 1. Neue P0-Nutzerbeobachtungen (05.11.2026)

**P0-A Fokusrahmen:** Auf BINGIE-Home sitzt der sichtbare Fokusrahmen erneut deutlich zu tief, über **allen Widget-Reihen**. Rahmen muss immer das genau fokussierte Item in dessen Reihe umranden: Live-TV-Senderlogo, Filmcover oder Seriencover. Korrekte Geometrie nach Scrollen, vertikalem Reihenwechsel, Fokuswechsel, Reload, Kodi-Neustart und Hero-Aktualisierung bei 1920×1080; 720p mitprüfen.

**P0-B Datenverlust nur in der Anzeige:** Auf Home sind zuerst Live-Sendericons, Jetzt/Nächstes-EPG und Film-/Seriencover sichtbar. Ohne Nutzeraktion verschwinden im Idle nach einiger Zeit wieder Sendericons, EPG und einzelne Cover. **Nicht behaupten, die Datenbank werde gelöscht:** Evidenz deutet auf instabilen Snapshots, Refresh/TTL, ungültige Bild-Leases und unvollständige Wiederveröffentlichung. Erst die konkrete Ursache pro Pipeline bestätigen.

**P0-C Artwork:** TVMaze/TMDB/Provider/XMLTV-Sendungsbilder in Mini-EPG, großem EPG, Sendungsdetails und BINGIE-Live-TV-Hero zuverlässig darstellen; einen gemeinsamen eventgebundenen validierten Artwork-Datenfluss nutzen.

**P0-D Standardwidgets:** Die drei Standardquellen müssen ohne gesonderte XCMate-Freischaltung, Slot-Zuordnung oder Reparaturinteraktion direkt im nativen BINGIE-Widgetpicker auswählbar sein. Bestehende gespeicherte Widget-URLs und Layouts weiter unterstützen, keine Zwangsmigration.

## 2. Log-Evidenz (keine Rohlogs öffentlich stellen)

Neuer Nutzer-Log: `kodi(20261105-072251).log`, rund 30.389 Zeilen, Zeitraum 04.11.2026 20:44 bis 05.11.2026 08:22, Android ARM32, Kodi 21.3, XCMate .73, BINGIE 2.2.3. Zählwerte sind **Logereignisse**, keine unterschiedlichen Sendungen, und belegen nicht automatisch physischen Datenverlust:

| Signal | Ereignisse |
| --- | ---: |
| `WIDGET45 PUBLISHED` | 347 |
| `WIDGET45 BLOCKED_NO_RELOAD_HOOK` | 329 |
| `WIDGET41 BUDGET` | 163 |
| `WIDGET47 NATIVE_HOME_UNVERIFIED` | 45 |
| `EPG63 EPG_DATA_MISSING` | 2.196 |
| `EPG63 EPG_CACHE_UNAVAILABLE` | 1.650 |
| `EPG63 EPG_DB_BUDGET` | 349 |
| `EPG69 EPG_READ_TIMEOUT` | 192 |
| `PROGRAMME_DB69 SQLITE_BUSY_LOCKED` | 50 |
| Kodi `MyVideos131.db no such table: movie_view` | 936 |

Konkretes Beispiel: **07:33:53** `WIDGET47 kind=live stage=ASSETS code=NO_RENDERABLE_REFERENCE`, obwohl `selected=64`, `logo_sources=64`, `poster_sources=64`; Widget-Serienausgabe schwankt u. a. von 23 auf 9 und 24 auf 7 Items. Bei `NO_RENDERABLE_REFERENCE` Ursachen für Bildfreigabe/URL-Kontrolle ermitteln, statt Datenquelle als leer zu behandeln. Kodi-Videobibliothek nur diagnostizieren, keine fremde DB auf Verdacht löschen.

Frühere beiden Logs (siehe Hauptissue #361) enthalten `NO_CONFIRMED_IMAGE`, `HELPER_TIMEOUT`, `HELPER_BACKGROUND_UNAVAILABLE`, `BLOCKED_IMAGE_HOST_OR_URL` und EPG-/SQLite-Budgets. Privatdateien **nicht** ohne Bereinigung öffentlich hochladen.

## 3. P0-A Fokusrahmen – mögliche technische Ursachen und Fixauftrag

Referenzen:
- `resources/lib/widget_skin64.py`, `widget_skin66.py`, `widget_skin63.py`, `skin_upgrade63.py`, `widget_focus41.py`;
- Tatsächliches installiertes `skin.titan.bingie.mod/xml/IncludesHomeWidgets.xml`, `IncludesHomeBingie.xml`, ggf. `Home.xml` und generierte SkinShortcuts-XML/Properties.

`widget_skin66.py` ersetzt `SetFixedVerticalNavigationProps` durch `XCMate66.VerticalFocus` mit `Container(77777).CurrentItem` und modifiziert globale Sichtbarkeitsregeln. `widget_skin64.py` bindet Fokusbilder über `Control.HasFocus($PARAM[widgetid])`. **Hypothese, keine gesicherte Ursache:** vertikale Containerposition, Widget-ID und fokussiertes Item sind nicht konsistent, wodurch ein Frame an falscher Stelle sichtbar bleibt.

**Umsetzung:** exakten Patchstand/Adapter-SHA feststellen, originäre BINGIE-Fokusregeln und eigene zusätzlichen Frames auf konkurrierende Sichtbarkeit, Koordinatensysteme und Skin-Gruppen prüfen. Lokale Overlay-Frames nur dann anzeigen, wenn exakt die richtige Widgetreihe *und* das richtige Item den Fokus hat; Position/Größe aus dessen aktuellem Item-Layout ableiten, keine globalen Offset-Hacks. Bei skinabhängiger Abweichung kontrollierte minimale Patchmigration, Vorschau/Backup und Rollback; bei unbekanntem Skinstand nie blind ändern.

**Abnahme:** Start; vertikal alle drei Reihen; horizontal erste/mittlere/letzte Position; nach 15/30/60 Minuten Home-Idle, Scroll, Hero-Wechsel, Kodi-Neustart und manuell ausgelöstem Widget-Reload. Auf keiner Reihe bleibt ein Geisterrahmen.

## 4. P0-B Anzeige darf nicht wieder leer werden – Last-known-good und atomare Publikation

Prüfstellen:
- `widget_data41.py`: `snapshot()` mit 15-Sekunden-Cache, `BUDGET`-/`LOCKED`-Fallback, Index-/Revisionwechsel.
- `widget_assets69.py`: `read()` akzeptiert öffentlich validierte Bild-Leases aus `Window(10000)` nur **bis 30 s**; `prepare()` arbeitet asynchron.
- `widget_render47.py`: filtert VOD/Serien-Items ohne sofort `renderable(poster)`; `widget_refresh45.read()` filtert nochmals. Ein fehlender/abgelaufener Bild-Lease entfernt dadurch **ganze Titel**, statt ihre vorher gültigen Daten beizubehalten.
- `widget_fast69.py`: Snapshot- und Bildreferenz-Signaturen können bei transienten Referenzänderungen neu publizieren. `widget_refresh45.py` setzt Reload-Properties, sofern Hooks vorhanden.
- `widget_pages46.py`: Live-TV-Manifest/Generation, Seiten-Hash und Zwei-Slot-Atomizität auf zeitgleich lesende Consumer prüfen.
- `epg_handoff63.py`: Now/Next-Properties laufen nach **300 s** ab; `EPG_CACHE_UNAVAILABLE` und `EPG_CACHE_STALE` können auf Home zur leeren Darstellung führen. `epg_row64.py`, `hero_epg63.py`, `widget_group46.py`, `epg_status.py`, `local_epg.py`, `guide_store.py` folgen.

**Verbindliche Architekturregeln:**

1. **Keine Rückstufung von gut zu leer:** Ein Reader-Timeout, Cache-Lease-Ablauf, `NO_RENDERABLE_REFERENCE`, fehlender Reload-Hook oder temporärer Teilimport darf eine bereits gültig angezeigte Reihe nicht mit null/weniger Items oder fehlenden Covern überschreiben. Halte einen letzten vollständig validierten Snapshot (`last-known-good`) **pro Portal + Widgetart + Quellen/Revision** vor, bis ein neuer konsistenter Snapshot atomar bestätigt ist. Dabei keine dauerhaft veralteten/tatsächlich entfernten Inhalte konservieren: echte Providerlöschungen, Playlist-Gruppenwechsel, Berechtigungen und Zeitgrenzen müssen korrekt invalidieren.
2. **Artwork-Problem darf nicht die Datenzeile entfernen:** Titel/Logo/Cover-Daten und temporäre URL-Validierung separat behandeln. Bei kurzzeitig ungültiger Bildfreigabe Item und restliche gültige Anzeige erhalten, Bild nachladen oder sicheren Placeholder einsetzen; bei vorhandener zuvor geprüfter gleichidentischer Referenz begrenztes stale-while-revalidate mit Provenance/TTL.
3. **Kein EPG-Flackern:** Bereits bekanntes Jetzt/Nächstes derselben Portal-/Sender-/Event-/Start-/Endzeitquelle bis validiertem Nachfolger und Rollover behalten; falsche oder alte Senderbilder/-EPG vermeiden. Leere EPG-Cache-Lesung ist **kein Beweis** für Löschung des Programms.
4. **Publikation nur bei echten Änderungen:** Snapshot-Generationen, Fingerprint, Revision und Bildstatus sauber getrennt versionieren; `WIDGET45`-Publikationen und native Reload-Hooks coalescen/debouncen. Keine Polling-Schleife, die alle paar Sekunden dieselben Inhalte neu schreibt.
5. **EPG-Cache robust:** 300-s-Window-Property-Handoff darf nicht zur sichtbaren Leere führen, während die lokale Guide-DB weiterhin gültige Programme hat. Fehlende DB-Daten von SQLite-Lock-/Read-Budget unterscheiden; erneute Hintergrundanfrage, nicht blockierend auf Fokuswechsel. WAL/Reader/Writer-Fenster und Lock-Strategie prüfen.
6. Diagnose-Events mit anonymisierter `pid`/Widgetart/Event-ID, `old_generation`, `new_generation`, `old_count`, `new_count`, `source_revision`, `reason`, `old_art_status`, `new_art_status` ohne Geheimnisse. Falsch positive Löschung im Log vermeiden.

**Abnahme:** Widgets und Jetzt/Nächstes **15, 30, 60 Minuten unverändert auf Home** mit laufenden Hintergrundjobs; Refresh/SQLite-Busy/HTTP-Timeout/Lease-Ablauf provozieren. Bekannte Logos, Cover und EPG bleiben bestehen, ohne unzulässiges Sender-Mixing oder dauerhaft eingefrorene Programme. Auch echter Quellwechsel und bewusste Deaktivierung bleiben korrekt.

## 5. P0-C Sendungsbilder: TMDB/TVMaze → alle vier Oberflächen

Referenzen:
- `programme_sources57.py`, `programme_tvmaze67.py`, `tmdb_epg60.py`, `tmdb_access61.py`, `programme_helper57.py`, `programme_urls55.py`, `programme_image69.py`, `programme_art46.py`, `programme_requests68.py`, `programme_preview67.py`, `hero_epg63.py`, `mini_epg.py`, `guide_grid_window.py`, `programme_window46.py`.

**Konkrete bekannte Gates:** Eigene TMDB-Suche nur bei `programme_tmdb46` **und** `tmdb_research43`; TVMaze `programme_tvmaze67` standardmäßig FALSE und bewusst auf eindeutige Serienmatches begrenzt. Vorhandener erfolgreicher Tokenimport allein bedeutet nicht, dass Bildsuche aktiv ist. Opt-ins/Opt-outs respektieren; Nutzerfunktion `Verbindung / aktiver Bildabruf prüfen` mit verständlichen Ergebnissen bereitstellen.

Bilder priorisieren: vorhandenes exaktes XMLTV/Provider-Eventbild, eindeutiger TMDB Film/Serie/Episode, TVMaze für eindeutige Serie/Episode, vorhandene Kodi-/XCMate-Kataloge nur bei echter Identität. TMDB Helper nicht als alleinige Pflichtabhängigkeit; wiederholte `HELPER_TIMEOUT`/`HELPER_BACKGROUND_UNAVAILABLE` mit Backoff/Circuit-Breaker und sinnvoller Quellen-Fallback-Kette behandeln. Sport/Talk/Nachrichten oder zweideutige Live-Titel nicht blind als TMDB Film nachschlagen. Quelle, Identitätsbeweis, sichere URL, erlaubter Host, Preflight, Cache-Validität und Kodi-Image-Control getrennt diagnostizieren.

Eine valide Event-Art-Referenz muss sich in **Mini-EPG, großem EPG, Sendungsdetails und BINGIE-Hero** sichtbar niederschlagen. `mini_epg.py` und `guide_grid_window.py` haben schon `programme_preview67.Preview`; Guide-Preview derzeit nur **96×54 Pixel** und soll nach Layouttest sinnvoll größer werden. `hero_epg63.py` prüft strenge Eventidentität/Profil/Revision; bei Konflikten Root Cause korrigieren, nicht falsche Bilder zulassen.

Bei echtem No-Match ein seriöses Fallbackbild ohne erfundene Sendungszuordnung. TMDB/TVMaze-Lizenzbedingungen und Attribution erhalten.

## 6. P0-D Standardwidgets aus .70 als normale Kodi-Quellen

`widget_binding50.py` und `widget_sources49.py` enthalten bereits die drei bekannten Aktionen `widget_live_start_group`, `widget_recent_vod`, `widget_recent_series`; diese **funktionsfähigen Pfade nicht ersetzen**. Native BINGIE-Picker muss sie unter XCMate ohne XCMate-eigene Slot-/Link-/Freischaltungsdialoge anbieten. Standardwidgets in normale XCMate-Menüs integrieren, alte `widget_setup`-Kompatibilitäts-RunPlugin-Weiterleitung beachten. `widget_manager50.py`, `widget_ui45.py`, `widget_repair73.py` unnötige Konfigurationsschritte aus Standardnavigation entfernen, Diagnose bei Bedarf unter Experimentell isolieren. Keine Home-XML-Manipulation per regulärer Add-on-Installation.

Abnahme auf **frischem** BINGIE-2.2.3-Profil und auf **bestehendem .70→.73**-Profil mit drei funktionierenden Reihen; alte Widget-Pfade bleiben gültig, Film/Serienklick und Live-Tuning unverändert.

## 7. P1 Performance und Fehlerpriorisierung

- `EPG_DB_BUDGET`, `EPG_READ_TIMEOUT`, `SQLITE_BUSY_LOCKED` und `WIDGET41 BUDGET` ursachenbezogen analysieren: `EXPLAIN QUERY PLAN`, notwendige Indizes, WAL-Verhalten, Transaktionsumfang, Leser-/Schreiber-Zeitbudget, Batch-NowNext-Lookup, Snapshotcache/Cold-Start.
- Reihenfolge: Anzeige stabilisieren **vor** aggressivem Re-Query oder Cache-Clear; keine pauschal größeren Timeouts, keine unkoordinierte parallele DB-Vollabfrage.
- Kodi `MyVideos131.db` fehlende Views separat als Diagnose behandeln; keine unautorisierte Reparatur von Kodi-Core-Datenbanken oder Drittanbieter-Add-ons.
- Vergleiche Cold/Warm Latenzen (p50/p95) für Widget-Start, Senderwechsel, EPG-Fokus, Hero und großen Guide. Deutliche Verlangsamung gegenüber .73 als Regression werten.

## 8. Definition of Done / Testmatrix

**Erforderlich vor Bereitstellung der PR**:
- [ ] Home 60 Minuten Idle: Logos, Film-/Seriencover, EPG stabil, auch nach 30-s-Bildlease/300-s-EPG-TTL und Hintergrund-EPG-Refresh.
- [ ] Drei Standardwidgets nach frischer Einrichtung auswählbar; alte `.70`-Widgetverknüpfungen bleiben nach kumulativem Upgrade unverändert.
- [ ] Fokusrahmen pro Item pixelrichtig beim Wechsel zwischen jeder Widgetreihe/Scroll/Kodi-Neustart, kein zweiter Frame/vertikaler Offset.
- [ ] XMLTV-/TMDB-/TVMaze-Testsendungen mit sicheren Identitäten zeigen tatsächliches Bild auf Mini-EPG, großem EPG, Details und BINGIE-Live-TV-Hero (auf Gerät verifizieren).
- [ ] Belastungstest SQLite-Lock/Read-Timeout, Netz-403/404/429/Timeout, `NO_RENDERABLE_REFERENCE`, Widget-24→7, parallele Widget-Generation, ungültiges/stales EPG, tatsächliche Provider-Löschung, Event-Rollover, Senderwechsel.
- [ ] Keine Token-/Provider-/SkinShortcuts-/EPG-/Favoritendaten überschrieben.
- [ ] Host-Tests, Smoke-Tests, CI, reproduzierbares ZIP, SHA-256, Diff/Changelog, PR und offene Android-Tests dokumentiert; **keine erfolgreiche Android-Abnahme behaupten**.
- [ ] Keine Änderung an regulären/Pilot-Repository-Katalogen und kein Merge vor expliziter Freigabe.

## 9. Codex-Rückmeldung

Berichte konkrete Ursache jedes der vier P0-Probleme, geänderte Dateien, Vorher/Nachher-Logstatistik und Latenzen, Tests und offene Risiken, Prerequisites für optionalen BINGIE-Patch, PR-Link, ZIP-Link, SHA-256 und klare Meldung, ob `.74` zum Geräteabnahmetest bereit ist.

**Entwicklung direkt beginnen, keine weitere Aufgabenklärung erforderlich.**
