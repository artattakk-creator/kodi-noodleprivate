# CODEX – VERBINDLICHE ÜBERGABE: XCMate 0.1.29.82
## Android-.81-Fehleranalyse, Artwork-Datenbank, Speicherreserve, monotone Bildreferenzen, Home-Latenz

**Stand:** 08.11.2026 · **Repository:** `artattakk-creator/kodi-noodleprivate`  
**Hauptauftrag:** [GitHub #395](https://github.com/artattakk-creator/kodi-noodleprivate/issues/395)  
**Voraufträge:** [#392](https://github.com/artattakk-creator/kodi-noodleprivate/issues/392), [#389](https://github.com/artattakk-creator/kodi-noodleprivate/issues/389)  
**Quellbasis:** `main` mit `plugin.video.xtreammate 0.1.29.81`, gemergter Source-PR #393 und Release-PR #394.  
**Ziel:** KUMULATIVE `0.1.29.82` als Branch, PR, getestetes ZIP und SHA256; **kein Merge/Release ohne neue Freigabe**.  
**Gerät:** Kodi 21.3 Omega / Android ARM 32-bit / RK3528 / Titan BINGIE MOD 2.2.3 / GS Media Installer 0.5.26.

> **Codex:** Beginne mit diesem Dokument und dem verknüpften Issue #395. Reproduziere den Datenbank-Pause-Ausnahmefall. Repariere erst den Artwork-Worker und die tatsächliche Speicherplatzprüfung, anschließend die Bild-/Widget-Lebenszyklen und die Home-Latenz. Bewahre alle Benutzerkonfigurationen und die bestätigte VOD-Wiedergabe.

### 0. Belege und Grenzen der Diagnose

Sechs private, vom Nutzer bereitgestellte Kodi-Logdateien vom 08.11.2026, mit **Duplikaten/Überlappungen**:
- Zwei identische `kodi.old(...201916/201928).log`: **16:38:36–19:55:18**, 74.740 Zeilen, XCMate `0.1.29.80`. **Nur historische Vergleichsbasis.**
- `kodi(...201914).log`: 19:55:40–20:01:20, 3.790 Zeilen, **Anfang** des nachfolgenden .81-Kodi-Laufs.
- `kodi(...201926).log`: 19:55:40–20:29:13, 66.182 Zeilen, **überlappt** mit der folgenden vollständigen .81-Sitzung.
- `kodi.old(...201933).log`: **19:55:40–20:31:18**, 70.588 Zeilen, `0.1.29.81`, erste maßgebliche .81-Sitzung.
- `kodi(...201932).log`: **20:32:26–21:15:07**, 30.593 Zeilen, `0.1.29.81`, zweite maßgebliche .81-Sitzung.

**Niemals diese sechs Dateien addieren!** Erste und zweite .81-Sitzung getrennt betrachten. Rohlogs, URLs, Portal-/Account-/Server-Identifikatoren, private Screenshots, Tokens, Hostnamen, IP-Adressen und Nutzerprofile **nicht in GitHub committen**; nur redigierte Messwerte und anonymisierte Korrelationen. Die folgenden Zahlen sind Log-Ereignisse, keine unabhängigen Filme/Sendungen und kein Beweis gerenderter Pixel.

### 1. P0-A – Crash-Schleife im neuen Artwork-Worker: bestätigt

**Erster .81-Lauf (19:55–20:31):**
- Ab **20:02:27** bis **20:31:16** enthält das vollständige Log **443 einzelne `Exception in thread`-Einträge**; alle 443 Trace-Kontexte enden in `XM-ARTWORK-DB-PAUSED`.
- **Root-Cause im aktuellen Code nachvollziehbar:** `widget_assets69._run()` startet `render_cache81.prepare(portal,kind,rows)`, danach `media_hero81.prepare(...)`, ehe es Provider-Artreferenzen veröffentlicht. `render_cache81.prepare -> store -> programme_art46.space -> art_store.used -> artwork_db.connect`; `artwork_db.connect()` wirft `ArtworkDBUnavailable('XM-ARTWORK-DB-PAUSED')`, wenn `retry_after` für unveränderte DB-Identität in der Zukunft liegt.
- `ArtworkDBUnavailable` ist `sqlite3.OperationalError`-Unterklasse; `render_cache81.prepare` fängt nur `OSError, ValueError, TypeError, RuntimeError, KeyError, SourceError`. **Die Datenbankausnahme passiert in einem darunterliegenden Call und entkommt.** `widget_assets69._run` besitzt `finally`, aber kein lokales `except`, das die Ausnahme abfängt. Der Daemon-Thread stirbt, beim nächsten Job wird ein neuer gestartet. Daher der Traceback-Sturm.
- **Zweiter .81-Lauf 20:32–21:15:** keine entsprechende Serie von Thread-Abstürzen. **Das widerlegt den Fehler nicht**; der Zustand der DB-Pause kann vom Neustart/Retry-Zeitfenster abhängen. Es beweist keine dauerhafte Behebung.

**Pflichtfix:**
1. `ArtworkDBUnavailable`/SQLite-Fehler einschließlich `PAUSED`, `BUSY`, Lock-Konflikt und Offlinezustand **gezielt** am Render-Worker und zentralem Job-Dispatcher behandeln; keine Fehler verschlucken, `MemoryError` und echte Programmierfehler nicht als Erfolg klassifizieren.
2. **Schutzpause respektieren:** bestehendes `retry_after`/diagnostic auslesen; bounded, idempotent backoff und Job erst nach Freigabe erneut versuchen; höchstens ein Worker/Job pro Content-/Art-Key aktiv und keine Thread-Reinitialisierung bei jedem Poll.
3. Wenn Art-DB pausiert, **last-good Poster/Logos/Hero behalten**; Fallback-RAM-Lesen nur, soweit bereits sicher vorhanden, und **keine neuen persistierten Writes ohne korrekte Freigabe**. Priorisierte GUI darf nicht auf DB warten.
4. Traceback-/Toast-Sturm unterbinden, aber einen kurzen strukturierten Status inklusive `PAUSE_UNTIL`, Retry-Grund und Worker-Gesundheit protokollieren; **kein** `ANDROID_PASS`, nur weil keine Exception mehr erscheint.
5. Den Auslöser für Artwork-DB-Pause, `_failures`-Eintrag und Recovery-/Integritätsdiagnostik **read-only und ohne ungefragte Reparatur** identifizieren. Schema-/WAL-/Migrationsänderungen nur nach expliziter, getesteter Notwendigkeit und datensicherem Plan.

**Reproduktionstest:** Inject `ArtworkDBUnavailable('XM-ARTWORK-DB-PAUSED')` in `art_store.used` und `artwork_db.connect` während `render_cache81.prepare`; auch `BUSY`/SQLite-Transient und parallele Katalog-/EPG-Polls simulieren. **Gate: 0 unhandled thread exceptions**, keine 443 Neuthreads, kontrollierte Wiederaufnahme nach Schutzpause; Covernachweis bleibt erhalten.

### 2. P0-B – Bildcache durch Speicherreserve blockiert

**Logs:**
- Zweiter .81-Lauf: **147× `[ART81] stage=CACHE code=RESERVE_BLOCKED`**; gemeldeter `free` im Bereich **53.825.536–58.871.808 Byte** (ca. 51–56 MiB), `reserve=1.073.741.824 Byte` (**1 GiB**), `budget=0`.
- Erste .81-Sitzung meldet ebenfalls `RESERVE_BLOCKED`, mit zeitweise noch geringerem `free`. Die konkrete Rückmeldung ist ein **Speicherplatz-/Reserve-Block**, nicht automatisch ein defekter Provider oder TMDB-HTTP-Aufruf.
- **Wichtige Semantik:** In `art_storage.budget()` bedeutet `budget=0` **kein zusätzlich konfiguriertes Bildbudgetlimit**, nicht „gesamter Speicher null“.
- Code: `render_cache81.root()` benutzt `programme_art46.root()`, also `utils.addon_data_dir()/programme_images46`. Das verweist auf `special://userdata/addon_data/plugin.video.xtreammate` nach Kodi-VFS-Auflösung. `art_storage.capacity(location)` verwendet `LocalArtworkStorage(location).free_or_unknown()`, welches `shutil.disk_usage` auf dem existierenden Ziel oder dem nächsten bestehenden Elternpfad ausführt. **Daraus allein folgt nicht, warum trotz anderweitig gemeldetem großem emulierten Speicher nur 24–59 MB erscheinen.** Möglich sind unterschiedliche Mount-/Bind-Informationen, Cache-Zielauswahl, Android-Speicherschichten und/oder falsche Pfadannahmen. **Den tatsächlichen Mount auf dem Gerät verifizieren statt zu raten.**
- `art_storage.reserve()` fordert mindestens 32 MiB und standardmäßig `media_art_reserve_mb=1024`. Ein globales Heruntersetzen auf 0 oder Streichung der Schutzprüfung ist **keine akzeptable Lösung**.

**Pflichtfix:**
1. Diagnose-Receipt ohne Pfade/Identifikatoren: **kanonischer Mount-/Backend-Typ**, physische `device_id`/Staging-Klasse (nur anonymisiert), tatsächlicher Free/Total aus derselben Speicherklasse, `reserve_policy` und effektive Reserve, Cache-Location-Klasse, anfordernde Bildrolle, angefragte Bytes und Blockcode. Prüfen, ob `shutil.disk_usage`, `statvfs` und tatsächlicher Schreibprobe-Pfad dasselbe Dateisystem meinen.
2. Prüfen, ob vorhandene Kodi-/XCMate-Profile bereits auf `/storage/emulated/0` liegen; **nicht** aus früherer Root/Emulated-Tabelle auf aktuellen realen Mount schließen. Nur geeignete, vom Gerät wirklich angebotene, intern verfügbare Storage-Backends verwenden.
3. **Bereits vorhandene lokal gespeicherte Art ohne Neuschreiben lesbar halten**, auch wenn Reserve neue Writes blockiert. Kein Herabstufen zu Placeholder wegen `RESERVE_BLOCKED`. Cache mit Last-good und GUI-Binding entkoppeln.
4. Adaptive Sicherheitsreserve ggf. **nur nach echten Montagedaten** und getesteter policy-gesteuerter Änderung anwenden; keine automatisierte beliebige Reservenullsetzung. Die Bilddatenbank und Kodi-eigene DB müssen geschützt bleiben.
5. Bei notwendigem Umzug auf größeren Speicher **separates optionales, kontrolliertes und reversibles Benutzerverfahren**; nur über Kodi/Netzwerk, **kein USB erforderlich**. Kein stiller Move, kein Überschreiben von TMDB-Token, Favoriten, Provider-Zugängen oder bestehenden Artfiles.
6. Korrekter Endzustand bei echter Speicherknappheit: klare einzelne Statusmeldung + Backoff + weiter funktionierende gecachte Icons/Heros, **kein Traceback-Sturm**.

**Gate:** Test mit (a) reichlich freiem emulierten Speicher, (b) vollem Zielvolume, (c) genau Reservegrenze, (d) unbekannter Kapazität und (e) zeitweise nicht erreichbarem Ziel. Prüfe physisches Android-Mount/Read-/Write-Verhalten. Keine falschen `DISK_FULL`-Schlüsse oder ungeschützte Schreibversuche.

### 3. P0-C – Senderlogo- und VOD-Poster-Flattern trotz .81-Last-good-Fixes

**Zweite .81-Sitzung (20:32–21:15), `[HOME74] reason=COMMIT`:**
- **VOD: 53 COMMITs bei jeweils derselben Source-Revision**, davon **26× `REFERENCE_READY → REFERENCE_PARTIAL`** und **27× `REFERENCE_PARTIAL → REFERENCE_READY`**. Das ist die direkte Fortsetzung der alten .80-Regression. Bereits angezeigte Filmcover können wieder als Play-Platzhalter erscheinen.
- **Live: 27 COMMITs bei gleicher Revision**, davon **7× READY→PARTIAL**, **7× PARTIAL→READY**, 9× READY→READY und 3× PARTIAL→PARTIAL (plus einmal EMPTY→PARTIAL). Die Senderliste selbst enthält weiterhin Sender, Bildrollen/Referenzen sind der Fehler.
- **Serie: 7× READY→READY**, diesen funktionierenden Pfad nicht regressieren.
- `RENDER_CACHE81`/Providerreferenzen und lokale Kodi-Texture-Lifetime getrennt von `source_revision` prüfen; derselbe Contentbestand darf kein neues teilweise leeres Skin-Frame erzeugen.

**Pflichtfix:**
- Echte atomare **Last-good-Revisionssemantik** je `portal_scope + stable stream/media ID + art_role + source_revision`; Karten, Senderlogos, Hero und Provider-/TMDB-Art strikt getrennt. Keine leere Teilantwort darf zuvor bestätigte Referenz verdrängen.
- `home_publication74.py`, `home_publication80.py`, `widget_refs74.py`, `widget_assets69.py`, `render_cache81.py`, `widget_refresh45.py`, `widget_skin80.py` und Kodi-ListItem-Art/GUIs prüfen.
- Atomic/UI-Publish mit minimalem Diff, ohne unnötigen globalen Home-Rail-Reset. Bei wirklichem Event-, Provider-, Profil- oder Gruppenwechsel **korrekt** invalidieren; kein fremdes altes Bild übernehmen.
- Wenn (schreibgeschützte oder pausierte) Art-DB nicht erreichbar ist: **read-only letzte bestätigte Texture**, kein kurzzeitiges `None`/schwarzer Hero. Mit `source_hash + cache_id + skin_control + generation + render_receipt` tokenfreie Korrelation.
- Tests der unveränderten 24er-Filmreihe und 88er-Sendergruppe, mehrfache EPG/Art/Katalog-Refreshzyklen, Skin-Neustart, App-Neustart. Echter sichtbarer Texturtest auf RK3528 notwendig.

**Gate:** Bei gleichbleibender Source-/Eventrevision **0 ungeklärte READY→PARTIAL-Abwertungen**, keine Disappearance/Placeholder-Regression; Serien-Cover, Live-TV-Exit und Filmwiedergabe bleiben funktionsfähig.

### 4. P0-D – Startseite nach Neustart viel zu langsam

**Zweite .81-Sitzung:** `HOME75 stage=LIVE_HOME_READY elapsed_ms=114611` (ca. 1m55s), `MOVIES_VISIBLE_READY elapsed_ms=1230977` (ca. **20m31s**), `SERIES_VISIBLE_READY elapsed_ms=1523127` (ca. **25m23s**). Das sind *interne Stages*, keine durch Kodi gemessenen sichtbaren Pixel.

**Soll:** erstes Render aus lokalem EPG, gespeicherten Logos und bestätigten Hero-Bildern; erste fünf Sendungen sofort priorisieren. Film- und Serienrails dürfen nicht auf Hintergrund-Vollscan oder geblockte Artwork-DB warten. Bild- und Katalogarbeiten inkrementell, begrenzt und außerhalb GUI-Thread. Distinkte Metriken `cached_items_ready`, `listitem_published`, `skin_control_active`, `image_decode_requested`, `actually_rendered_on_android` unterscheiden.

**Gate:** Keine 20–25 Minuten bis zum internen Rail-Ready; Performance-Budget erst nach Identifizierung echter Blockadepfade unter Android festlegen und mit kalt/warm gestartetem Gerät messen. Filmreihe ohne Pfeiltaste sichtbar. UI muss während Background-Scan bedienbar bleiben.

### 5. P1 – Eigene TMDB-Abfragen funktionieren; Matching/Anwendung bleibt offen

In der zweiten .81-Sitzung: **126 `[ART81] HTTP_REQUEST_SENT`**, **126 `HTTP_STATUS code=OK status=200`**, **19 `MATCH_CONFIRMED code=EXACT`**, **19 `IMAGE_BACKDROP_READY`** und **241 `MATCH_REJECTED code=NO_MATCH`** (mehrstufige, wiederholte Eventfälle). **TMDB wird also tatsächlich kontaktiert**; nicht erneut den alten Eindruck „TMDB überhaupt aus“ als Tatsache behaupten. API-HTTP-200 allein beweist kein Film-Match und kein im Skin sichtbares Bild.

**Pflicht:** Token- und Consent-/Optout-Schutz; reale Query-/Film-/TV-/Jahr-/Alias-Matches mit Modern Family, Yuna & Stitch/Stitch!, Croods, Harry Potter und Mockingjay; gültige Backdrop- und Posterrollen trennen; Quelle `TMDB/XMLTV/TVMaze/Provider` korrekt im UI; kein XMLTV↔TMDB-Flattern beim selben Event. Bestätigte Backdrops zur großen Live-/Movie-/Series-Hero-Fläche, proportionaler Portrait-Poster-Fallback auf gedimmtem Landscape-Hintergrund. Transparente Info-Tafel mit Jetzt/Danach/Progress. Echte VOD-Providerposter in Rails erhalten und nicht ungeprüft durch TMDB austauschen.

### 6. P1 – EPG, Kodi-native Views und Schutz

Zweiter .81-Lauf, **nur `EPG63 stage=DB_READ`:** 889 `EPG_DATA_MISSING`, 255 `READY`, 226 `EPG_CACHE_UNAVAILABLE`, 86 `EPG_DB_BUDGET`. Es sind **mehrfach wiederholte Leseereignisse**, keine 889 individuellen Programme. Native Kodi-Videodatenbank-Views `movie_view`, `tvshow_view`, `musicvideo_view` melden weiterhin Fehler und können Kodi-eigene Skinwidgets betreffen; **ausschließlich read-only Diagnose, kein blindes Rekonstruieren oder Löschen**. EPG-Quelle/Mapping manuell unverändert erhalten, globale Suche und Now/Next nicht regressieren.

### 7. GUI/UX und Bestandsschutz

- **Full-bleed-Hero** für Live/Filme/Serien, Landscape-Backdrop bevorzugt, Portrait-Poster vollständig und unverzerrt, halbtransparentes Overlay mit Fortschrittsbalken.
- Film-/Serienrails **enger**, Zielkorridor 16–32 px optische Distanz plus Überschrift bei 1080p (proportional auf 720p), Fokus-/Overscan-Hitboxen testen. Nur XCMate-spezifische Skinbereiche patchen, keine globalen BINGIE-Resets.
- **Katalog-Job still oder kleine Statuszeile**, nicht als große Kodi-Toastflut vor EPG-/Hero-Infos; Abschluss mit tatsächlich letzter Provider-Synchronisation und `neu/geändert/unverändert`. Nicht das Medien-Upload-Datum mit Sync-Zeit verwechseln.
- **Verbindlich unverändert:** Add-on-ID, vorhandene Kodi-Userdata, Provider-/Portal-Accounts, Favoriten, EPG-Quellen/-Mappings, TMDB-Read-Access-Token, SkinShortcuts, Space-Blue-Branding, funktionierende Live-TV/VOD-Wiedergabe und Serien-Autoplay sowie GS Media Setup Wizard **0.5.26**. Keine unaufgeforderte Speicher-Migration, kein USB, keine DB-Reset-/Kodi-Neuinstallation und keine Archive-Löschung. Ältere ZIPs erhalten.

### 8. Umsetzung / Tests / Release-Gates

| Gate | Kontrollfall | Pass-Kriterium |
|---|---|---|
| P0-A | DB bei `render_cache81.store` pausiert/busy und Widget-Job läuft | 0 unhandled Thread-Ausnahmen; bounded Backoff, Recovery, last-good sichtbar |
| P0-B | `free` unter bzw. über der tatsächlich gültigen Reserve, separater Mount | Korrekte sichere Kapazitätserkennung, kein Schein-Fehlalarm; kein Schutz-Bypass |
| P0-C | Unveränderte 24 Filme + Senderlogos, Idle/Katalog/Art-Neuladen | 0 unmotivierte READY→PARTIAL, keine Placeholder-/Logo-Ausfälle |
| P0-D | Kodi Warm-/Kaltstart, Homepage ohne Navigationsaktion | Film-/Serienrails und EPG zeitnah bereit; keine Minutenblockade; GUI frei |
| TMDB | Bekannte TV-/Filmtitel mit Cache, Treffer, No-Match, Timeout | Eigener Request nachgewiesen, richtige Artrolle, stabiler Full-bleed-Hero |
| GUI | 720p, 1080p, Fokus/Scroll, Katalogfortschritt | Kein verdeckter Hero-Text, Rails enger, echte Poster/Backdrops proportional |
| Regression | Live-TV, VOD `PLAYING` und Exit, Staffel-Autoplay, EPG | Bestehendes Verhalten unverändert |
| Release | CI, Python-Tests, Skin-XML, native Kodi, ZIP-CRC/SHA256 | geprüfter PR mit Test-ZIP, `ANDROID_NOT_TESTED` bis realem Gerät |

**Zu liefern:** Branch `fix/xcmate-02982-artwork-db-worker-storage`; Root-Cause-Notiz pro P0 mit Dateipfad und pseudonymisiertem Beleg, zielgerichtete Unit-/Integrationstests mit Dependency-Injection (PAUSED/BUSY/RESERVE_BLOCKED/RESET), geprüfter Paketbuild `plugin.video.xtreammate-0.1.29.82.zip`, SHA256, PR gegen `main`, Issue #395 aktualisiert.

**Freigaberegel:** Nur den .82-Branch, PR, Tests und ZIP erzeugen. **NICHT** ohne gesonderten Nutzerauftrag nach `main` mergen oder `addons.xml`/Pilot/NeoDark3 veröffentlichen. Host-/CI-PASS ist **nicht** Android-PASS.

## 9. Direktes Codex-Startkommando

> Lies GitHub-Issue #395 und diese Datei vollständig, verifiziere den .81-`ArtworkDBUnavailable`-Thread-Crash im konkreten Render-Worker, behebe danach DB-Pausen-/Retry-Semantik und tatsächliche Storage-/Reserve-Prüfung, dann atomare stabile Bildpublikation und die extremen Home-Latenzen. Die funktionierenden Playerpfade und alle Nutzerdaten schützen. Implementiere kumulativ XCMate 0.1.29.82 als PR mit Tests und ZIP/SHA256; kein automatischer Merge oder Release.
