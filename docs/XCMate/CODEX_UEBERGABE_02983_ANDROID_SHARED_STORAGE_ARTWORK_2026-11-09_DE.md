# CODEX – Verbindliche Übergabe für XCMate 0.1.29.83
## Android Shared Storage / Movies: Artwork-Zielwahl, Kapazitätsprüfung und sichere Auslagerung

**Datum:** 09.11.2026 · **Repository:** `artattakk-creator/kodi-noodleprivate`  
**Neuer P0-Arbeitsauftrag:** [#398](https://github.com/artattakk-creator/kodi-noodleprivate/issues/398)  
**Bisheriger Android-Masterauftrag:** [#395](https://github.com/artattakk-creator/kodi-noodleprivate/issues/395) · **Historischer Migrationsauftrag:** [#106](https://github.com/artattakk-creator/kodi-noodleprivate/issues/106)  
**Quellbasis:** `main`, XCMate 0.1.29.82 (Source-PR #396, Release-PR #397).  
**Nächstes Entwicklungsziel:** kumulative XCMate 0.1.29.83, **kein Merge und keine Veröffentlichung ohne ausdrückliche Nutzerfreigabe**.

## 0. Kurzfassung / Ziel
Auf Kodi 21.3 Omega, Android ARM32 RK3528, Titan BINGIE MOD 2.2.3 (Installer 0.5.26) ist der Artwork-Cache fast voll. Der Nutzer möchte Bilder/Logos in den **großen internen, gemeinsam genutzten Android-Speicher**, beispielsweise den bestehenden Ordner `Movies`, auslagern. **Kein USB, kein SMB, keine SD.** XCMate bietet bislang im Artwork-Picker nur USB/SMB und den manuellen Einstieg `/storage/`. Dieser Einstieg ist auf der Box nicht browsbar. Es ist **noch nicht bestätigt**, dass `Movies` ein anderes Volume/einen größeren Kapazitätspool darstellt oder mit Kodis Rechten beschreibbar ist.

**Kritischer Grundsatz:** Der Pfad `special://home/` liegt laut Kodi-Startlog bereits unter `/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi`, aber die Artwork-Diagnose misst nur **3,76 GiB Gesamtkapazität und etwa 46–56 MiB freien Speicher**. Der früher gemeldete Bereich von über 200 GB ist am konkreten Ziel noch unbestätigt. Die scheinbare Diskrepanz zuerst messen und erklären. Kein blindes Verschieben innerhalb derselben Partition, keine Sicherheitsreserve abschalten.

## 1. Forensischer Nachweis (redigierte Daten)
- Originale private Logs: `kodi.old(20261109-083357).log` und `kodi(20261109-083358).log`; **nicht** in GitHub hochladen. Zweites Log ab 09:06:36 bestätigt Version .82.
- **09:25:23.194:** `GetDirectory - Error getting /storage/`; `CGUIDialogFileBrowser::GetDirectory(/storage/) failed`. Die Fehlermeldung betrifft die **Dateibrowser-Auflistung**, nicht nachweislich Schreibrechte auf `Movies`. **Kein** `EACCES`/`Permission denied`/`TARGET_WRITE_FAILED` für den tatsächlichen Zielpfad nachgewiesen.
- **09:25:31:** `ART_STORAGE82`: `LOCAL`, `fuse`, `SAME_VOLUME_VERIFIED` (bisheriger Messkontext), `free=50.774.016`, `total=4.034.297.856`, `reserve=1.073.741.824`, `RESERVE_BLOCKED`.
- **09:32:45:** `free=46.706.688`, `reserve=80.685.957`, `reserve_policy82=adaptive`, weiterhin `RESERVE_BLOCKED`.
- Artwork-Status-Screenshot: **46/3.847 MiB frei/gesamt**, Reserve **76 MiB**, **102 `DISK_FULL`-Aufträge**, DB-Integritätsprüfung OK. `sqlite_code=5/OperationalError` in weiterem Diagnose-Screenshot ist SQLite `BUSY` (separates DB-Thema, keine nachgewiesene Storage-Permission).
- GUI-Screenshots: `METADATA_TARGET_REQUIRED`, `RENDER_NOT_VERIFIED`, `ARTWORK_OPERATION_FAILED`. Metadatenexport ist kein tatsächlicher Platzgewinn. Bei unveränderter Quellrevision werden weiterhin einzelne `REFERENCE_READY` zu `REFERENCE_PARTIAL`; Folgeproblem #395 bleibt offen.

## 2. Bestehende Codepfade
- `src/plugin.video.xtreammate/resources/lib/artwork_ui.py:_pick()`: `external_sources()` (USB) oder Kodi-SMB, fallback `/storage/`, `xbmcgui.Dialog().browseSingle(0,...)`; **kein expliziter `Interner Android-Speicher`-Picker**.
- `storage_sources.py:external_sources()` untersucht `/storage`, `/mnt/media_rw`, `/media`, filtert `emulated` aus USB. Andere UI `storage_sources.choose()` kennt bereits `/storage/emulated/0/` als lokale Auswahl – konsistent integrieren, aber nicht ungeprüft als schreibbar annehmen.
- `artwork_vfs.py:target_root(),prepare_target(),backend_for(),ExternalLocalStorage`: lokale absolute Ziele; `os.makedirs()` und Besitzer-Marker `open(...,'xb')` sind echte Schreiboperationen. Kodi-Picker/Dateiliste **erteilen keine Android-Scoped-Storage-Berechtigung**.
- `artwork_migration.py`: aufrufgebundene journalingbasierte Migration mit Copy, SHA256-Readback, Renderprüfung und Aktivierung; erhalten. `metadata_export.py`: nur zusätzliche Beschreibungskopien, **keine physische Auslagerung**.
- `art_storage.py`, `artwork_status.py`, `storage_diagnostics.py`, `artwork_config.py`, `utils.addon_data_dir()`, Kodi-Cachepfade zusätzlich inspizieren.

## 3. Verbindliche Implementierungsreihenfolge

### P0-A – Reale Quelle/Ziel-Speicheridentität
1. Für `programme_images46`, internes Artwork-Archiv, `special://home/`, `special://thumbnails/` und explizit ausgewähltes `Movies` **jeweils separat** kanonisches Ziel, Mount-Backend, anonymisierte Device-/Mount-Korrelation, `os.stat().st_dev`, `os.statvfs()` mit `f_bavail` und `f_bfree`, Gesamtkapazität und effektive Reserve vergleichen. Wo verfügbar Android Storage-/Mount-Abbildung prüfen; keine Rootpflicht. Bind/FUSE/Quota beachten.
2. Gleicher Pool oder unklare Zuordnung = `TARGET_SAME_CAPACITY_POOL` bzw. `TARGET_VOLUME_UNVERIFIED`, kein positiver Platzgewinn/automatischer Move. Historische 224 GB nicht als derzeit gemessenen Zielwert übernehmen.

### P0-B – Android-internen Zielspeicher wählbar machen
3. Separater, klar beschrifteter Picker für `Interner Android-Speicher`; USB und SMB beibehalten. Nur legitime, erreichbare bestehende Pfade anbieten; `/storage/` nicht blind als brauchbare Auswahlliste präsentieren. Bereits bekannte Kodi-Quellen verwenden, aber nicht als Berechtigungsgarantie.
4. Android API34 Scoped Storage berücksichtigen: `browseSingle`/Kodi-Dialog ist **kein** SAF-Grant. Falls Zugriff auf freigegebene Medienordner nicht möglich, eine tatsächlich unterstützte, dokumentierte Android-SAF/Kodi-VFS-Strategie umsetzen oder die Begrenzung klar erklären, **niemals Berechtigungen umgehen**. Keine Rootrechte, keine pauschale All-Files-Berechtigung verlangen.

### P0-C – Ziel prüfen, dann transaktional auslagern
5. Zielvorprüfung **ohne Datenänderung** (Existenz, Symlink/Traversal, Volume, Reserve, Schreibfähigkeit technisch plausibel). Optional nur nach expliziter Bestätigung des Nutzers ein kurzlebiger 4-KiB-Schreib-/Les-/Hash-/Löschtest **ausschließlich in XCMate-eigenem Unterverzeichnis**. Bei Fehler eindeutiger, lokalisierter Code: `TARGET_NOT_BROWSABLE`, `TARGET_NOT_WRITABLE`, `TARGET_SAF_REQUIRED`, `TARGET_OFFLINE`, `TARGET_RESERVE_BLOCKED`, `TARGET_SAME_CAPACITY_POOL`.
6. Bestehendes Migrationsjournal weiterverwenden: Inventory → Copy → SHA256-Readback → überprüfte Anzeige über Kodi → Aktivieren. Originals bleiben zunächst erhalten. Bei Abbruch, Offline, Zielkollision, Hash-Fail, Datenbank-BUSY oder Neustart sicher pausieren und fortsetzen; keine heimlichen Cache-Löschungen.
7. **Nur wenn** nach erfolgreicher Aktivierung und separater Nutzerfreigabe ein vollständig verifizierter Bereinigungsschritt erfolgt, darf tatsächlicher freier Quellspeicher als gewonnen gemeldet werden. Keine physische Metadaten-/SQLite-/Kodi-DB-Migration in diesem Fix.

### P1 – Fehlermeldungen und Diagnose
8. Eindeutiger Status statt `ARTWORK_OPERATION_FAILED`; Pfadklasse/Fehlerphase anonymisiert protokollieren, aber keine Rohpfade, Accounts, Tokens oder Provider-URLs auf GitHub. SQLite `BUSY` separat analysieren und begrenzt retryen; kein Schema-Rebuild aufgrund eines Permission-Problems.
9. Fehlende Logos, Sendungsbilder, TMDB-Matching, BINGIE Hero/Widget-Layout bleiben offene Punkte des Android-Masterauftrags #395. Nicht stillschweigend als behoben erklären.

## 4. Tests und harte Abnahmekriterien
- CI/Fault Injection: API34 `EACCES`, root `/storage` nicht listbar, reale Shared-Storage-Wahl, keine Schreibrechte, SAF fehlt, Symlinks, selbes st_dev, gleiche Speicherkapazität trotz unterschiedlicher Pfade, getrenntes Volume, insufficient reserve, Netzwerk/Volume offline, Copy-/SHA-/Render-Fail, Zeitüberschreitung/Abbruch/Resume, SQLite BUSY und unveränderte Benutzerdaten.
- **Auf Android-Testbox B tatsächlich** zuerst Quelle und konkretes `Movies`-Ziel prüfen: exakte anonymisierte Volume-Klasse, `free/total` vor/nach, 4-KiB-Test nur mit Bestätigung, sichtbares Testbild, danach erst Migration und Neustarts/Player-Regressions.
- Erfolg nur mit belegten **tatsächlich sichtbaren Bildern** und bei gewünschtem Platzgewinn nach belegter *anderer* Kapazitätsklasse und separat autorisierter Cleanup-Aktion. Kein `ANDROID_PASS` allein aufgrund grüner CI oder vorhandener Bild-URL.
- **Bestandsschutz:** Provider-/Login-Daten, TMDB-Token, EPG-Mappings, Favoriten, SkinShortcuts, Titan BINGIE MOD/Space Blue, Kodi-Datenbanken, Nutzerwidgets, Player-/Zurück-Verhalten, Installer 0.5.26. Box A unverändert; kein ungefragter Cache-Reset/Installerlauf.

## 5. Codex-Workflow und Release-Gate
- Neues Branch-Ziel: `fix/xcmate-02983-android-shared-storage`. Code-Fix, gezielte Tests, alle CI, Installations-ZIP und SHA256; PR gegen `main`. In #398 Diagnoseursache, Pfad-/Berechtigungsmodell, Testergebnisse, noch offene echte Android-Prüfungen dokumentieren.
- **Kein automatischer Merge nach `main`; keine Publikation in regulär, Pilot oder NeoDark3 ohne ausdrückliche Freigabe.** Die Dokumentation selbst kann auf `main` liegen; das ist keine Entwicklungsfreigabe.
- Wenn sich herausstellt, dass der große interne `Movies`-Ordner denselben Kapazitätspool nutzt und kein anderer sicherer Speicher erreichbar ist: **keine Scheinmigration**; die Einschränkung offen dokumentieren und einen separaten speichersparenden Lösungsweg zur Freigabe vorlegen.
