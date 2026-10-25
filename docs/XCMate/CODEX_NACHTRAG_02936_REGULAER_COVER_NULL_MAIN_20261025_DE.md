# CODEX – Sofortiger Zusatzauftrag für den REGULÄREN XCMate 0.1.29.36-Testkandidaten

> **VERBINDLICHE ARTWORK-USB-SMB-SPEICHERARCHITEKTUR (25.10.2026):** Der Nutzer fordert, die Cover-Speicherung schon **bei der aktuellen .36-Reparatur so auszulegen, dass USB/SD/externe Festplatten UND Kodi-SMB/NAS als echte wählbare Bildziele möglich sind**. Der [**vollständige Implementierungsvertrag**](https://github.com/artattakk-creator/kodi-noodleprivate/blob/main/docs/XCMate/CODEX_ARTWORK_STORAGE_USB_SMB_BINDING_02936_02937_20261025_DE.md) hat für diese Frage Vorrang. **.36 PR #163:** Null-Cover-Reparatur + klar getestete backendneutrale Artwork-Storage-Schnittstelle (keine neue intern-POSIX-Hardcodierung), lokale Bilder-Funktion und sichere Status-/Kapazitätswerte. **.37 regulärer kumulativer Folge-Release:** echte USB- UND SMB-Speicherortauswahl, neue Downloads auf dem gewählten Ziel, Copy+Hash+Verify+Fortsetzungs-Migration vorhandener 18k+ READY-Dateien, externe Offline-Sicherheit, getrennte Löschbestätigung und Kodi21.2/21.3-Tests; #106 von alter .43-Phase **nach .37 vorgezogen**. Kodi-`smb://` braucht `xbmcvfs`, nicht `open/os.replace/shutil.disk_usage`. SQLite/EPG/Portale intern; keine Pseudounterstützung ohne TV-Test, kein Merge ohne Nutzerfreigabe.


**Verbindlicher Beschluss 25.10.2026:** Nutzer will **keinen separaten Wizard-Testbranch** mehr, sondern **einen regulären kumulativen Testkandidaten von main**; wichtiger Zusatzbefund: **auf neuer Android-/Kodi-21.3-Box wird kein einziges Film-/Serien-Cover geladen**. Vorherige Meldung einer vermeintlich vollen Speicherpartition ist mangels realem /data-Freiplatz **nicht bewiesen**.

**Repo:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Produktion beim Auftrag:** `main` Add-on-Version **0.1.29.35**, offizieller Repository-Index ebenfalls `.35`.  
**Bestehender regulärer Entwicklungs-PR:** [#163 „XCMate 0.1.29.36: Genresuche und Such-/Start-/OSD-/Stop-Stabilisierung“](https://github.com/artattakk-creator/kodi-noodleprivate/pull/163), **Draft, nicht gemergt**, Branch `fix/xcmate-02936-stabilization`. Zum Vorprüfungsmoment HEAD `656be1e73aff1c16b877880bde52f2384792677a`; CI/Hosttests **1.214 PASS** *vor dem hier beauftragten Cover-Fix*, Android Test **NOT_TESTED**. Existierendes Paket `plugin.video.xtreammate-0.1.29.36.zip` inklusive alter SHA ist **NICHT** der finale Kandidat nach diesem Auftrag und **muss neu gebaut werden**.

**Separates Wizard-Preview:** [#162](https://github.com/artattakk-creator/kodi-noodleprivate/pull/162) wurde auf ausdrücklichen Nutzerwunsch **CLOSED, UNMERGED**. Nicht benutzen, nicht rebased zum nächsten Kandidaten, keine Preview-Dateien in #163 importieren. Die reguläre Wizard-Funktion ist bereits in `main` und bleibt dort; seine offenen Safe-Save-/Progress-/Gruppen-/Branding-Probleme sind .37-Folgeumfang.

## 1. VOR CODE: zu lesen und gegen aktuellen HEAD zu prüfen

- [Voriger Hauptauftrag .36 (inkl. aktueller Priorität)](CODEX_AUFTRAG_02936_PERF_OSD_SEARCH_BACKLOG_20261025_DE.md).
- [Neuer P0-Einzelfall: KEINE Cover auf Kodi21.3-Box](https://github.com/artattakk-creator/kodi-noodleprivate/issues/168).
- [Box-B-Gerätedaten und korrekte Speicheranalyse](LOGFORENSIK_BOX_B_KODI213_WIZARD_STORAGE_20261025_DE.md).
- [Art-Space- und Queue-Issues](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90), [Poster-Netzwerkfehler #111](https://github.com/artattakk-creator/kodi-noodleprivate/issues/111), [SQLite-/Artwork-Migration #69](https://github.com/artattakk-creator/kodi-noodleprivate/issues/69), [Blockaden #91](https://github.com/artattakk-creator/kodi-noodleprivate/issues/91).
- [Verbindlicher Versionszug nach .35](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md) und Schutz-UI Freeze.

**Preflight:** `git status`, `git fetch`, Versionsnummer `main`, Repo-Publishing-Index, Dokumentationscommits auf `main`, PR #163 Konflikte. **Keine** veraltete `#162`-/`#157`-/`#78`-Branchbasis mergen. PR #163 **auf aktuelles main bringen** und darin weiterarbeiten. Selbst wenn #163 bereits ein Test-ZIP anbietet: dieses hat keine bestätigte neue Cover-Reparatur.

## 2. MUSS: Einzelnes tatsächliches Problem „0 heruntergeladene Cover“ lokalisieren und beheben

**Userbeobachtung:** Auf Box B unter XCMate `.35` funktioniert TV/EPG nach Wizard-Save-Kodi-Absturz zum Teil wieder; **kein einziges Cover** wird heruntergeladen. Kodi21.3/Omega ARM32 RK3528. Speichermeldung „voll“, aber kein `ENOSPC/BUDGET_FULL/DISK_FULL` in zwei damaligen Kodi-Logs, **Freier Flash in GiB nicht überliefert**. **Keine Beweisbehauptung:** dass Android tatsächlich keinen Platz hat, Provider-CDN generell down ist, Code-Queue defekt ist oder Cloud-TMDb blockiert – all das sind zunächst unterscheidbare Hypothesen.

**A. Read-only Statuskette (Phase IDs, keine Geheimnisse):**
1. Portal/Katalog: tatsächliche Film-/Serien-/Logo-Source vorhanden? Anbieterfelder `cover,stream_icon,movie_image,cover_big`, `NO_SOURCE/INVALID_SOURCE` vs gültige HTTPS-URL, nur bool/Feldname/Domain-Kategorie ohne URL.
2. UI: `media_art.local_art` / `media_art.request` bekommt Medienkacheln? Anfragen in `_inbox` und `MAX_INBOX` tatsächlich vorhanden? In-Menü-Anzeige und Hintergrund-Synchronisierung getrennt.
3. Queue: `art_store.enqueue()`, `artwork_db` transaktionale Persistenz; Status pro `PENDING,RUNNING,READY,SPACE_FULL,BUDGET_FULL,DISK_FULL,NETWORK_ERROR,TIMEOUT,TLS_ERROR,HTTP_RATE_LIMIT,INVALID_IMAGE,CACHE_ERROR,MIGRATION_FAILED,DB_BUSY`, `attempts`, `next_at`, `worker.until`, Anzahl READY-Dateien. **0 Daten vs alle Failed vs alle BLOCKED sauber trennen**.
4. Worker: `media_art_paused`, `xc_background_prefetch`, Worker gestartet? `_enrol_loop` und `_prefetch` (inkrementell) laufen? Timeout/Abort/Lease-State? Nicht Service-Hintergrundjobs mit GUI-Job-Auslösung verwechseln.
5. Speicher: echtes `art_storage.capacity().total/free` für XCMate-Art-Folder-Mount, Reservierung `art_storage.reserve()` **default 1.024 MiB**, Budget `art_storage.budget()` (0=ohne künstliches Limit), `art_store.used()`, `import_budget.RESERVE=32 MiB`, nächster 3-MiB-Download; bei tatsächlichem ENOSPC korrekt blockieren, bei reinem BUDGET_FULL keine irreführende „Flash voll“-Meldung, bereits gewählte Limits/Reserve schützen.
6. Netzwerk: `utils.http_get` unter 4s connect/6s Request-Gesamtlimit, TLS/DNS/HTTP/Auth/Timeout/RateLimit und Bildvalidierung getrennt, Providerquellen-Fallback nur belegbar; **keine** privaten URLs/Token im offenen Issue-Text/Export.

**B. Implementierung:**
- Root Cause **mit anonymisierter Messung beweisen**, nur passende minimal-invasive Pipeline-Teilstellen ändern. Wenn Artwork-Anfragen erzeugt, aber Hintergrundjob nicht startet: zuverlässiger persistenter Worker-Start, bounded Queue und Lease-SingleFlight. Wenn Quelle vorhanden, aber kein Download: sichere Fehlerklassifikation und gezielte autorisierte Retry-Policy.
- Wenn XCMate eine interne 512-MiB-Grenze bzw. die 1024-MiB-Reserve erreicht: explizit differenzieren; Default-limit nur datensicher anpassen, physische Reserve **nicht** blind deaktivieren. Ist der physische /data-Mount wirklich unter Reserve, klarer `BLOCKED_REAL_DISK` + Zahlen + erlaubtes sicheres Speicherziel, **nicht** „Cover-Fix erfolgreich“ ausgeben.
- Kein globales `art_store.retry()` für 17k Alt-Jobs; nur wenige konkrete `retry_one()`- oder Policy-Recovery-Jobs mit Bounded Backoff. Vorhandene `READY` und bereits gespeicherte `img` niemals löschen; SQLite/WAL bei Code #69 respektieren, keine `DROP TABLE`-Migration. Kein Komplett-/Full-TMDb-Indexing.
- **Erstes reales Ergebnis** muss im TV sichtbar sein: 3 Filmcover + 2 Seriencover + 2 Senderlogos aus lokal gespeicherten validen Dateien mit `READY` und Persistenz nach Kodi-Restart. Bei fehlenden Provider-Covern sollte die Anzeige ehrlicherweise `NO_SOURCE` ausweisen und den Fall getrennt dokumentieren, keine Phantom-READY mit Placeholder.
- Bereits bestehende gute `.36` Performance-/Genresuche-/Infobar-/Stop-Fixes **vollständig erhalten**.

## 3. Neu kombinierte Android-Testgates für EIN .36-Update

**Alt-Tests:** 15/15 Android-.35-Funktions-Baseline, komplette neue S36-01..12 und GENRE-01..07 aus `docs/XCMate/ANDROID_ABNAHME_02936_DE.md` – alle als **NOT_TESTED** bis echter Android-Messung.

**Neu zwingend dazu:** ART36-01 Status & physisch frei/reserve/Queue, ART36-02 **mindestens 3 echte Filmcover**, ART36-03 **2 Seriencover + 2 Senderlogos**, ART36-04 physisch voll vs intern budgetfrei, ART36-05 HTTP/TLS/RateLimit/DB-Fehler getrennt, ART36-06 alte READY auf Box A behalten, ART36-07 responsive IR & persistente Worker, ART36-08 keine Altfeatures/Autoplay/EPG-Regression. Vollständige Kriterien und Zero-False-PASS im [Issue #168](https://github.com/artattakk-creator/kodi-noodleprivate/issues/168).

**Verifikationsziel:** Box B **Kodi 21.3 ARM32** zusätzlich zu Box A **Kodi 21.2 ARM32**; beide bleiben auf ihren jeweiligen bestehenden Profilen. Keine neue Einrichtung, kein Cache-/Portal-/DB-Reset, kein Downgrade. Ein von Codex allein ausgeführter Simulator ist keine echte Android-Hardwarefreigabe.

## 4. Workflow/Deliverables – exakt

1. In **bestehendem PR #163** `fix/xcmate-02936-stabilization` weitere isolierte Commits für Artwork-Pipeline/Fehlerdiagnose/Tests; **kein Wizard-Sonderbranch**, kein neues .36-Parallelrelease. Wenn Branch nach neuen main-Doku-Commits Konflikte hat, sicher synchronisieren, **nicht** auf alten main zurücksetzen.
2. Neue `docs/XCMate/URSACHENANALYSE_02936_DE.md` bzw. Nachtragsabschnitt mit anonymisierten `0 COVER`-Statuswerten, Vorher/Nachher-Diagnose, Hardwaregrenzen und Nachweis welches Subsystem **wirklich** repariert wurde.
3. Regressionen: Kodi21.2/21.3 Mock, Netzwerk-/Disk-/Queue-/Pause-/Lease-/Concurrency-/SQLite-Busy Tests, 3/2/2 echte Bilder nur unter Android als Erfolg; Hosttests frisch ausführen, **grünes CI**.
4. Komplettes **neues reproduzierbares Installations-ZIP** `plugin.video.xtreammate-0.1.29.36.zip` plus neue **SHA256** und Dateikatalog/Testbericht, beide vom *neuesten* PR-HEAD; den bisherigen Hash `a7cd88...` nach Codeänderungen ausdrücklich verwerfen.
5. Android-Testplan um ART36-01..08 ergänzen, alles real vorher **NOT_TESTED**. Issue-Matrix #168 #90 #111 #69 #91 und die alten .36-Issues: `implementiert / testen / Teil-PASS / offen`.
6. Kein automatisches Merge, kein Release-Publishing und keine Installation/Profiländerung am Nutzersystem. **Benutzer gibt nach Download und echter Geräteabnahme Freigabe.**
7. Die reguläre `.37` erhält anschließend: bestehender Wizard #43 mit Kaltstart/Save-Crash #165/Group-Resync #166/EPG-Progress #164/Original-Icon+Hintergrund sowie lokale Geräteinformationen #167; alle real gefundenen offenen .36-Bugs aus ART36-Tests kommen **im gleichen .37-Paket** dazu. Keine Arbeit an experimental #162 nötig.

**STATUS BEI AUFTRAGSERSTELLUNG:** Hauptcode weiterhin `.35`; #163 Draft .36 bereits existiert, #162 Preview geschlossen ohne Merge; P0 „NULL Cover“ **gemeldet, noch nicht behoben**. Originalkatalog/Serie/EPG/Autoplay/Originalicon gesichert erhalten.
