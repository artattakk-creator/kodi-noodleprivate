# XCMate 0.1.29.37 – VERBINDLICHER NEUAUFTRAG AN CODEX (vollständige kumulative Entwicklung)

**Stand:** 25.10.2026. **Repo:** https://github.com/artattakk-creator/kodi-noodleprivate  
**Add-on-ID:** `plugin.video.xtreammate` · **letzte veröffentlichte Version:** `0.1.29.36` auf `main` und im offiziellen Kodi-`addons.xml`-Index. **Kein .37-PR oder .37-Build lag bei der letzten GitHub-Prüfung vor.**  
**Referenz-PR:** [#163 .36 gemergt](https://github.com/artattakk-creator/kodi-noodleprivate/pull/163). **Nicht übernehmen/mergen:** geschlossener Wizard-Preview #162, veralteter Artwork-PR #78, alte Space-Premium-Drafts.  
**Ziel:** `0.1.29.37` als **ein einziger neuer regulärer Draft-PR**, aus aktuellem `origin/main`, ohne irgendein Rewrite/Downgrade von `.36`; vollständige Test-ZIP/SHA256. **KEIN MERGE, KEIN MAIN-PUBLISHING, KEINE ÄNDERUNG AN ECHTEN BOXEN ohne ausdrückliche Nutzerfreigabe.**

## 0. VORAB – verpflichtender Preflight und Source of Truth

1. `git fetch origin`; `main`-SHA, Add-on-Version `.36`, Veröffentlichung und bestehende PRs abgleichen. Erstelle **einen neuen Branch** z.B. `feat/xcmate-02937-cumulative` von **dem aktuellsten `origin/main`**, keine alten PR-Headbases zusammenführen.
2. Lese diese bereits auf main gespeicherten verbindlichen Quellen vor dem Eingriff:  
   - [bestehender .37-Architektur-Hauptauftrag](CODEX_HAUPTAUFTRAG_02937_ARTWORK_DYNAMISCH_USB_SD_SMB_METADATA_BUGFIXES_20261025_DE.md)  
   - [Sicherer Artwork-Speichervertrag](CODEX_ARTWORK_STORAGE_USB_SMB_BINDING_02936_02937_20261025_DE.md)  
   - [.36 Box-B reale Zwischenabnahme](ANDROID_ZWISCHENABNAHME_02936_BOX_B_20261025_1852_DE.md)  
   - [.36 bestehende Android-Gates](ANDROID_ABNAHME_02936_DE.md)  
   - [verbindliche Roadmap](VERBINDLICHE_RELEASE_ROADMAP_AB_02935_20261025_DE.md).
3. Dieser **Neua u ftrag** [Schreibweise zur Eindeutigkeit: dieser NEUAUFTRAG] ist ein **vollständiges Konsolidat**, nicht bloß ein Nachtrag. Bei alten Widersprüchen gelten nachstehende Sicherheits- und Abnahmeregeln.
4. Lege **zusätzlich** den hier beschriebenen [neuen .37-Android-Abnahmeplan](ANDROID_ABNAHME_02937_DE.md) zugrunde; initial alle Gates `NOT_TESTED`. Konkrete reale Nutzerbeobachtungen als `OBSERVED_FAIL` protokollieren, **niemals** als bereits getesteten .37-Fix.

## 1. NICHT VERHANDELBAR: Bestandsbox erhalten – [P0 #173](https://github.com/artattakk-creator/kodi-noodleprivate/issues/173)

**Box A (bisherige Box):** Bestehendes XCMate-Profil mit vielen intern gespeicherten Bildern. **Bei Upgrade .36/Legacy → .37 bleiben Bilder und Logos im internen Speicher**, alle IDs/Hash-Namen/Datei-Bytes, `media_art_v1`, `tv_logos`, Artwork READY/Jobs, Portale, EPG samt manuellen Mappings, Gruppen, Startsender, Favoriten, Film-/Serienlisten, Watch-/Resume, Serien-Autoplay, Original-Icon, Skins, Keymaps und Einstellungen. **Keine automatische Migration/Default-Umschaltung, Daten-/Cache-Löschung, Medien-Neuimport oder Job-Reset**. Eine Änderung erst nach expliziter UI-Nutzeraktion.

**Box B (neue Kodi21.3-Box):** Ein **bereits eingerichtetes Legacy-Profil** mit aktuell kaum/keinen Covern, `531 / 3.847 MiB` frei/gesamt, Bildreserve `1.024 MiB`, `DISK_FULL=97`, `PENDING=21`, `RUNNING=1`. Auch sie gilt trotz fehlender READY-Bilder **NICHT als Neuinstallation**. Upgrade zunächst `INTERN`, aber der Nutzer kann im Menü **manuell** sofort `DYNAMISCH` oder `EXTERN` auswählen, ohne Portale/EPG/Setup zu verlieren. Ihre aktuellen Hardwarewerte sind **Beobachtungen**, keine amtlich verifizierte RAM-/Flashgröße.

**Echte neue Profile:** Als Standardeinstellung `DYNAMISCH` (schlank) ausschließlich, wenn ein sauberer **Never-Initialized-Profilzustand** verifiziert ist. **Technische Gefahr:** `artwork_mode` existiert in `.36` noch nicht. **Nicht** einfach neuen `settings.xml` Default `dynamic` für alle verwenden! Separaten persistenten `artwork_config_version`- oder vergleichbaren Marker, Legacy-Erkennung aus Portal-/Profilzustand, atomare und crash-idempotente Übergangsmigration, versionierte Settings-Tests. Vorhandene explizite Nutzerwahl hat stets Vorrang. Mode state geräte-/Kodi-profillokal, kein Crossbox-Autosync.

**SAFE-01..08** sind P0 Release-Blocker. Codex führt *zuerst* Offline-Hostmigrationstests auf geklonten Fixtures aus, nie heimlich auf Nutzerbox A. Für reale Box A erst Benutzerfreigabe und **read-only Vorher-Snapshot** von READY/Hashes/Settings; keine unerlaubte automatische Installation.

## 2. P0 Player/Back/Exit-Freeze – [#169](https://github.com/artattakk-creator/kodi-noodleprivate/issues/169) und [#174](https://github.com/artattakk-creator/kodi-noodleprivate/issues/174)

Reale Beobachtung: **Box B .36 Kodi21.3** startet Live-TV-Suchtreffer, aber **IR-Zurück lässt Kodi/Box hängen**. Weitere Beobachtung: auf **noch nicht eindeutig identifizierter Box und unbekannter installierter XCMate-Version** hängen beim Verlassen **Live-TV, Film und Serie**. **Nicht fälschlich** die beiden Geräte- oder Versionskontexte zusammenziehen und keine gemeinsame Ursache ohne neue Logs behaupten.

Untersuche systematisch:
- `playback_exit.py::poll/stop_owned/identity`, `media_progress.py`, `media_state.py`, `media_autoplay.py`, `live_exit.py::request/_poll`, `live_overlay.py`, `service.py`, Kodi-Window-/Directory-Dispatch und Keymapping;
- Kodi-Player `stop`, VOD/Serien-Resume/SQLite-Snapshot, Nutzer-Abbruch vs natürliches Episodenende, Live-OSD sichtbar/versteckt, Session Ownership, Fremdplayer, doppelte Service-/GUI-Exit-Events, Kodi Modal/Container.Update/Reentrancy;
- klar definierter single-flight bounded state machine `BACK→EXIT_INTENT→(progress snapshot)→STOP→PLAYER_STOPPED→XCMATE_HOME` ohne Deadlock; Kodi-UI-Thread keine blockierenden Netz-/DB-Warteaufrufe; explizite Exit-Timeout/diagnostische Failsafe ohne Retry-Schleife.

**P0 Tests zuerst auf Host-Fakes**, danach auf echter Hardware **zunächst je eine vorsichtige Exit-Probe pro Medientyp**; erst wenn kein Hänger, mehrfache IR-/Back-/Overlay-/Buffering- und schnelle Back-Tests. Keine 20-fache Freeze-Probe als Einstieg. Neue `kodi.log`/`kodi.old.log` und ggf. logcat privat anfordern; Sanitizer, keine Provider-URLs, Passwort-/Token-Leaks.

## 3. P0/P1 Cover-/Artwork-System – [#172](https://github.com/artattakk-creator/kodi-noodleprivate/issues/172), [#106](https://github.com/artattakk-creator/kodi-noodleprivate/issues/106), [#168](https://github.com/artattakk-creator/kodi-noodleprivate/issues/168), [#90](https://github.com/artattakk-creator/kodi-noodleprivate/issues/90)

Benutzeroberfläche: `XCMate → Einstellungen → Speicher → Artwork-Verwaltung`, TV-/IR-bedienbar, drei Betriebsarten, aktuelle Modus-/Ort-/Queue-/Capacity-Status mit Refresh:

**A. DYNAMISCH / speichersparend**: echtes Artwork aus **vorhandenen gültigen Provider-/Metadaten-HTTP(S)-URLs** in Kodi-Listen/Details/EPG direkt anzeigen **nur bei sichtbaren Items**, ohne XCMate-Archiv-/Prefetch-/neue persistente Downloadjobs. `XMLTV` liefert primär EPG und ggf. Logos; Xtream-Codes-Film-/Serienposter kommen typischerweise aus Katalog-API (z.B. `cover`, `movie_image`, `cover_big`). Fehlquellen/ausgefallener CDN = neutraler Platzhalter ohne UI-Hänger. Bestehende READY-Dateien bleiben, alte blocked Jobs nicht löschen. **Kodi-eigener Texturecache (`Thumbnails/Textures*.db`) bleibt auch dynamisch lokal**; `Dynamisch` ist **nicht 0 B / kein Netztraffic**. Keinen Kodi-Globalcache löschen. Fehlt Provider-Art-URL, nicht externes Cover erfinden.

**B. INTERN dauerhaft**: Die Originalpfade und der bestehende geprüfte lokale `.36`-Backend bleiben unverändert; `Bei Bedarf` oder bewusst `Alle verfügbaren Cover vorladen` (Downloadprogress, begrenzt, pausierbar), kein stiller globaler Retry alter fehlerhafter Jobs.

**C. EXTERN dauerhaft**: Unter `Kodi`-Ordnerbrowser auswählen: USB-Stick/HDD/SSD, SD/microSD, Samba/SMB2+-Share/NAS. Nach Prüfung unter Benutzerziel selbst `XCMate/Artwork/{media,logos,fanart}` erstellen. `Ziel prüfen` muss echte Schreib-/Leserückprüfung, Bild-Dekodierung und Kodi-Rendering testen. USB-Mountrechte real prüfen. SMB ist `smb://` **Kodi-VFS**, niemals `open()/os.replace()/shutil.disk_usage()` als lokaler Pfad missbrauchen; `xbmcvfs`-Datei-/Copy- und Sicherheitsadapter für `artwork_backend.ArtworkStorageBackend` bereitstellen. Kein Root, keine Klartext-Kennwörter in Add-on-Settings/Logs/Manifests.

**Migration BESTEHENDER Sammlungen – zwingender Zustandautomat, nicht bloß Copy-Button:** `Ziel→Probe→Inventur (N Dateien / Bytes)→Kopieren in Batches→je Datei Readback SHA256 + Bildvalidierung→Journal/Resume→100 % Gesamtprüfung→Test-Kodi-Darstellung→Benutzer-Aktivieren→optional separate Benutzer-Originale löschen`. Quelle darf während kopieren/Abbruch/USB-Entfernung/Kodi-Neustart niemals gelöscht werden. Aktivierungswechsel atomar und erst nach Verifikation; **kein Auto-Fallback mit Redownload aller Poster bei Offline-SMB**. Undo/Rückwechsel ermöglichen. Alle XCMate-Cover-/Backdrops-/Logos/Hash-Keys und `READY` erhalten; Bilddatei nach Zielwechsel persistiert über Neustart. Simuliere 20.000 Dateien und echte Android-Hardware-Teilmigration.

**Kapazität/Reserve:** Zielmount-spezifische Prüfung, externer freier SMB-Platz evtl. `UNKNOWN`; nie die interne `1024 MiB`-Bildreserve der Box auf externen Mount anwenden. Kleine lokale SQLite-/Staging-Sicherheitsreserve bleibt. Box B `531 < 1024 MiB` = `RESERVE_BLOCKED`, **NICHT** bewiesener physischer ENOSPC. UI muss diese Zahlen ehrlich zeigen und optional ein **sicheres**, bewusst konfigurierbares/kapazitätsabhängiges Reserveprofil anbieten; nicht blind auf 0 setzen. Echte `DISK_FULL/BUDGET_FULL/TLS/HTTP/DB_BUSY` getrennt, bounded Resume/Retry. Dynamic Mode darf keine XCMate-Archiv-Schreibreserveprüfung auslösen.

## 4. Film-/Serieninformationen optional extern – [#171](https://github.com/artattakk-creator/kodi-noodleprivate/issues/171)

Im ausgewählten Datenträger optional `XCMate/Metadata/` für vorhandene **beschreibende** Payloads (Plot, Beschreibung, Jahr, Genre, Episoden-/Staffeldaten soweit tatsächlich vorhanden). Kein Stream-, Credential- oder Portal-URL-Export. **`library_v1.sqlite` und `media_art_jobs_v1.sqlite` mit SQLite-WAL/Locks, kompakte Such-/Genre-/Gruppen-IDs und Kernindex bleiben lokal**, keinesfalls direkt auf SMB mounten. Externer versionierter Metadata-Store nur mit verifizierter Readback-/Fallback-/Offline-Logik. **Eine Kopie ist noch keine Platzersparnis:** tatsächliche interne Payload-Reduktion und Freiraumzuwachs nur nach beweisbarer sicherer DB-Migration deklarieren. Ist dieser Teil im gleichen Paket wegen möglicher Datenverluste nicht sicher lieferbar, Export/Format/Abnahme liefern, aber den eigentlichen physischen Metadata-Offload mit `BLOCKED` (nicht PASS) dokumentieren und vor Merge offen melden. **Cover-Migration hat Vorrang.**

## 5. Regulärer verpflichtender .37-Restumfang (nicht fallenlassen)

- [**#165 P0 Wizard-Save-Crash**](https://github.com/artattakk-creator/kodi-noodleprivate/issues/165): Wizard nach EPG-Scan `Speichern` darf Kodi nicht beenden; transaktionaler Save/Window-Lifecycle mit Restart/Interruption, keine Portaldaten verlieren. Nur im kontrollierten frischen Testprofil installieren/neu durchlaufen, NIE den funktionierenden Wizard auf Box A erneut erzwingen.
- [**#166 Xtream-Gruppe**](https://github.com/artattakk-creator/kodi-noodleprivate/issues/166): nachträglich aktivierte Xtream-Gruppe wird mittels delta-gesteuerter Katalogsynchronisierung mit echten Sendern gefüllt, ohne alle vorhandenen Gruppen neu zu scannen.
- [**#164 Wizard-Fortschritt**](https://github.com/artattakk-creator/kodi-noodleprivate/issues/164): ab Beginn Quelle 1/4..4/4 sichtbar, bei unbekannter Dauer echte Aktivität statt falscher Prozent, Cancel-/Resume, finale Fehlerliste.
- [**#43 Wizard und Branding**](https://github.com/artattakk-creator/kodi-noodleprivate/issues/43): Original-XCMate-Icon/Original-Hintergrund, Xtream/M3U/Stalker, Gruppenwahl vor Import, EPG-Quellen, Live/VOD/Serien-Auswahl, Startsender/Startgruppe, Counts. Keinen geschlossenen Preview-PR #162 mergen.
- [**#167 Gerätespezifikationen**](https://github.com/artattakk-creator/kodi-noodleprivate/issues/167): `Wartung & Diagnose → Geräteinformationen`, echte `/proc/meminfo` RAM/Verfügbarkeit, /proc CPU/Kernel, API-Level und gemeldete Firmware getrennt, Kodi-Version/ABI/Process RSS, reales Kodi-/Artwork-Dateisystem inkl. gewähltes USB/SMB getrennt, tatsächliche Werte vs beworbene '16 GB RAM / 240 GB Flash' als unverifiziert kennzeichnen; optional redigierter Export, read-only und IR-Fokus.
- [**#170 Startdauer**](https://github.com/artattakk-creator/kodi-noodleprivate/issues/170): **27 s XCMate-App-Start auf Box B**, genaue cold/warm-Pfadmessung bis erstes bedienbares Menü, Initialisierung/DB/Artwork/Guide/Widget getrennt; keine Synchron-Netzwerkarbeit im GUI-Start; konkrete Vorher-Nachher-Latenz. Nicht mit Zeit bis Stream-First-Frame verwechseln.
- **Unantastbar aus .36:** Global-Suche Live/Filme/Serien einschließlich Nutzerprobe „Horror“ (Teil-PASS), Genre Sci-Fi/Western/Horror/Thriller, großer EPG, Startsender/Startgruppe, Live-Info-/Mini-EPG/IR, Serien-Autoplay nach natürlichem Episodenende (aber NICHT nach Stop), Resume, Favoriten, Provider/Portale, Security, Original-Icon/Lightweight/Space-Premium-Legacy, PVR/Downloads und Repository-Updatepfad.

## 6. Verbindlicher Arbeitsablauf und Buildpaket

**Phasen im EINEN PR (Commits unabhängig testbar):**
1. Versions-/Profil-Preflight + Host-SAFE-Tests, P0 Exit/Stop-Hänger mit Beweisdiagnose und Fix; `.36`-Such-/TV-Bestand weiter PASS.
2. Drei Artwork-Modi; echte dynamische Bilddarstellung und Backendwahl; sichere Kopier-/Verify-/Resume-/Cleanup-Berechtigung; USB/SD-/SMB-Host-E2E (Mock/Kodi-VFS) und reale Android-Platzhalter-Gates noch offen.
3. Geräteinfo, Wizard-Safe-Save/Fortschritt/Gruppen-Nachimport, Branding, App-Startoptimierung; Metadaten-Payload-Export/-Ablage isoliert, keine riskante DB-Erzwungenheit.
4. Vollständige Regressionen, Code-/Sicherheitsreview und **neues `plugin.video.xtreammate-0.1.29.37.zip` + SHA256**, keine alte `.36`-Prüfsumme. ZIP reproduzierbar nur aus aktuellem PR-HEAD, genaue Liste geänderter Dateien und Status aller Issues.

**Host-Testkommandos analog .36 (im isolierten sauberen Checkout, keine Nutzerdateien):**
```bash
python tools/build_repository.py
python tools/validate_kodi_po.py
python -m compileall -q src
python -m unittest discover -s tests -v
```
Vorher Pinned-Bootstrap/Anwendungsschritte wie im CI-Workflow `.github/workflows/publish.yml` befolgen; 3 historische Noodle-Testpfade ggf. wie in CI normalize. Testvergleich mindestens **1.250 bestehende .36-Hosttests ohne Regression**, zusätzlich neu implementierte `.37`-Tests; keine Behauptung einer fixen neuen Gesamtzahl, bis tatsächlich ausgeführt. PR-CI grün, reproduzierbarer ZIP-Dateikatalog, Quell-/Profile-Unverändertheits-Hashes, kein ungewollter `addon_data`-/Tokeninhalt im Paket. CI-PASS ist **kein** Android-PASS.

**Android-Abnahme:** [`ANDROID_ABNAHME_02937_DE.md`](ANDROID_ABNAHME_02937_DE.md) vollständig, separate Status `PASS/FAIL/BLOCKED/NOT_TESTED` für **Box A/Kodi21.2** und **Box B/Kodi21.3**. Keine Android-Simulation als echtes Gerät werten. Meldungen aus `.36` (31s/27s, Back Freeze, Cover-reserve) bleiben Historie und werden nicht als `.37`-PASS überschrieben. **Zuerst auf sicher kontrolliertem Testprofil/Box B**, Bestandsbox A nur nach ausdrücklicher Benutzerentscheidung und Daten-Snapshot, keine unbeabsichtigte automatische OTA-Installation vor Freigabe.

**Jede offene/verzögerte Teilfunktion sichtbar als `BLOCKED: Grund + risikofreie Nacharbeit + konkreter Test` benennen.** Keine automatische Issue-Schließung/PR-Merge/Release, kein versteckter Featuredrop, kein künstliches Plus-Versionssprung. Nach PR-Erstellung URL, Branch/HEAD, CI/Hostberichte, ZIP/SHA, klare Tabelle `implementiert/host-verifiziert/Android-NOT_TESTED/blockiert` und konkrete sicheren Android-Testschritte zurückgeben.

**CODEX: Starte JETZT mit Implementierung und neuem .37-Draft-PR auf aktuellem main. Keine Rückfrage, außer echte Secrets/Hardwaredaten wären zwingend erforderlich; diese nie in öffentlichem PR anfordern.**
