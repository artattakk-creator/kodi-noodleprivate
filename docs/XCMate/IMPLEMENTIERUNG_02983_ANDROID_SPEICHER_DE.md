# XCMate 0.1.29.83 – Android Shared Storage

Basis: `fdbcf96823760777d0a2f153d046389c3d1f1352` (`main`, .82).
Arbeitsbranch: `fix/xcmate-02983-android-shared-storage`.
Auftrag: #398; übergeordnete, weiterhin offene Android-Bildfehler: #395.

## Bestätigte Ursachen und Grenzen

Der bisherige Artwork-Picker bot USB/SMB an und begann die manuelle lokale
Auswahl ungeprüft bei `/storage/`. Die protokollierte Kodi-Directory-Fehlermeldung
beweist weder EACCES auf `Movies` noch einen tatsächlich größeren Speicherpool.
`prepare_target()` erzeugte Ordner und Marker vor einer gesonderten
Android-Zielprüfung. Das Migrationsjournal führte außerdem bei jedem Öffnen
`CREATE TABLE IF NOT EXISTS` aus. SQLite BUSY wurde in der Oberfläche nicht
zuverlässig von Speicher- oder Berechtigungsfehlern getrennt.

Die bekannten 46–56 MiB frei / 3,76 GiB gesamt betreffen den bisherigen
Messpfad. Ein historisch gemeldeter Bereich über 200 GB wird **nicht** als
Messwert des neuen Ziels übernommen. Ohne tatsächliche Messung auf der Box
bleiben Android-Kapazität, Rechte und sichtbare Bilddarstellung ungeprüft.

## Änderungen

- `android_storage83.py`: schreibfreie Einzelmessungen für Programmcache,
  internes Medienarchiv, Logos, Profil, Kodi-Home, Kodi-Texturen und gewähltes
  Ziel. Bestehende lokale Cachepfade werden bis zum vorhandenen Elternordner
  vermessen; das ausgewählte Ziel muss selbst existieren und auflistbar sein.
- Mountinfo einschließlich überlagerter Mountpoints, Dateisystemtyp,
  `st_dev`/Mount-major:minor-Korrelation, `statvfs.f_bavail` und `f_bfree`,
  Gesamtgröße und wirksame Reserve. Nur `f_bavail` zählt für Schreibzulassung.
  Private Pfade/Devices/Mountquellen bleiben lokal; öffentliche Receipts
  enthalten Rollen, Bytewerte und gehashte Korrelationskennungen.
- Gleiches `st_dev`, gleicher backing-major:minor oder identische Blockquelle
  gelten als gleicher Pool, auch bei unterschiedlichen Ordnernamen oder Quoten.
  Zwei nachweislich unterschiedliche Block-Dateisysteme können als getrennt
  bestätigt werden. Unterschiedliche FUSE-/sdcardfs-/esdfs-Geräte, unbekannte
  Mounts oder unbestätigte Namespace-Zuordnungen gelten **nicht** als Trennung.
  Gleiche oder verschiedene freie/gesamte Bytezahlen allein sind kein Beweis.
- `artwork_ui.py`: eigene Auswahl **Interner Android-Speicher** und separate
  Quell-/Zieldiagnose. Vorhandene erreichbare Android-Roots, Umgebungsangabe,
  Mounts und Kodi-Quellen werden verwendet. Kein blinder `/storage/`-Fallback.
  Ordnerdialog Typ 3; anschließende eigenständige Listing-/Sicherheitsprüfung.
  USB/SMB und Download-/Aufnahmerouting bleiben erhalten.
- Die Auswahl erteilt **keine Android-SAF-Freigabe**. Für Kodi 21/Python ist in
  diesem Projekt kein verifizierter SAF-Dateibaum-Bridge verfügbar. Verweigert
  Android den Zugriff, endet die Aktion mit `TARGET_SAF_REQUIRED`; es werden
  weder Root-/All-Files-Rechte angefordert noch Android-Beschränkungen umgangen.
- Nach erfolgreicher schreibfreier Vorprüfung zeigt die UI exakte Bytewerte.
  Erst nach einem gesonderten Ja werden der profilgebundene XCMate-Namespace
  und eine exklusive temporäre 4-KiB-Datei erstellt. Rücklesen, SHA256,
  Volume-Neuprüfung und Entfernen nur dieser Probe. Fremde Dateien und
  unmarkierte vorhandene Profilordner werden nicht übernommen/überschrieben.
- `artwork_migration.py`: bestehendes Journal und Dateiformat bleiben erhalten;
  Android-Volume-Nachweis wird im bestehenden privaten Transfer-Snapshot
  gespeichert. Vor Kopieren, Dateien und Aktivieren wird erneut geprüft.
  Vor dem Kopieren muss der noch ausstehende Gesamtbestand plus Reserve passen.
  Copy → SHA256-Readback → explizit bestätigte Kodi-Bildanzeige → Aktivieren.
  Keine automatische Aktivierung oder Bereinigung.
- SQLite BUSY/LOCKED: maximal drei fehlgeschlagene Statement-/Commitversuche,
  je 30 ms SQLite-Wartezeit, Backoff 20/50 ms. Keine Wiederholung ganzer
  Kopierjobs, keine neue Workerschleife. Bereits vorhandene Journal-Tabellen
  werden beim Öffnen nur gelesen; kein wiederholtes Schema-DDL. Beim Fehler
  bleiben Originale und journalisierter Fortschritt erhalten.
- `artwork_errors83.py`: lokalisierte Rechte-/SAF-/Reserve-/Pool-/BUSY-/SHA-/
  Renderfehler statt unverständlichem generischem Fehlertext. Interne
  Journalreserve wird ausdrücklich vom freien Zielspeicher unterschieden.
  Diagnose enthält nur feste Aktionsnummer und festen Code, keinen Rohpfad.
- Deutsche/englische PO-Texte; bestehender englischer Fallback für die weiteren
  Sprachen. Add-on-News/Changelog enthalten die sichtbaren Updateänderungen.

## Migrationsumfang und Bestandsschutz

Die bestehende Migration kopiert persistente `media_art_v1`-Bilder und
`tv_logos`. Konfigurationsmodus `external` bezeichnet weiterhin das Archiv
außerhalb des Add-on-Profils; dazu gehört auch ausgewählter interner
Android Shared Storage. Es wird kein neuer konkurrierender Archivtyp eingeführt.

`programme_images46`, Render-/Kodi-Texturcache, SQLite-/EPG-/Portal-Datenbanken
und Metadaten bleiben an ihren bisherigen Orten. Sie werden einzeln vermessen,
aber nicht heimlich umgezogen. Dieser Fix behauptet deshalb **keine vollständige
Auslagerung sämtlicher Cachebytes**. Metadatenexport bleibt eine zusätzliche
Kopie ohne behaupteten physischen Speichergewinn.

Originale werden weder bei Auswahl noch Kopieren/Prüfen/Aktivieren gelöscht.
Die vorhandene separate Bereinigung erfordert weiterhin zwei Bestätigungen,
aktiven Transfer und erneute vollständige Prüfung. Erst danach dürfen real
beobachtete freie Quellbytes als gewonnen berichtet werden. Wenn Movies
zum selben Pool gehört, wird diese Migration gar nicht begonnen.

Providerdaten, TMDB-Token, EPG-Zuordnungen, Favoriten, SkinShortcuts, persönliche
Widgets, Branding, Installer 0.5.26 sowie Player-/Back-Code sind unverändert.
Die Quellen-/Testschutzverträge sichern die kumulative .82-Basis und alle
bisherigen Testmethoden. Alle veröffentlichten .82-Kataloge und Pakete bleiben
byteidentisch. Kein Merge und keine Veröffentlichung durch diesen Auftrag.

## Weiterhin offen / BLOCKED

- Tatsächliche RK3528-/API34-Messung des konkreten Movies-Ziels:
  `ANDROID_NOT_TESTED`.
- SAF-Berechtigung für einen von Kodi nicht erreichbaren Ordner:
  **BLOCKED**, solange die Plattform keine verifizierte Bridge bereitstellt.
- FUSE-Pools ohne beweisbare backing-Zuordnung: **BLOCKED**
  (`TARGET_VOLUME_UNVERIFIED`), keine Scheinmigration.
- Gleicher Kapazitätspool: **BLOCKED** (`TARGET_SAME_CAPACITY_POOL`). Ein anderer
  Ordner allein vergrößert keinen Speicher. Keine Reserve wird abgeschaltet.
- Fehlende Senderlogos/Sendungsbilder, TMDB-Matching, Ready/Partial und
  Hero-/Widget-Darstellung in #395 sind damit **nicht Android-abgenommen**.
