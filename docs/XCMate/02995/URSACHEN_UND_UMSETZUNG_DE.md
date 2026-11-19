# XCMate 0.1.29.95 – unabhängige Importfreigabe

Stand: 15.11.2026. Auftrag #464, Draft-PR #465. Keine Merge- oder Veröffentlichungsfreigabe.

## Kumulative Basis und unveränderte Veröffentlichungen

- .94-Quellbasis: PR #460, `9a78ab5a77ed9b0cf1ebe9122dfb545680ebf036`.
- Aktuelles main abgeglichen: `459817b43fe59664acbcccc68a757ecd946a5839`; Integration in `5562c2ee`. Dieser main-Stand enthält die bereits separat autorisierte Pilot-.94-Veröffentlichung. Sie ist keine Veröffentlichung von .95.
- Regulärer Katalog, Pilot-Katalog, NeoDark3, Installer 0.5.26 und geschütztes .90-Fallback bleiben unverändert. Der .95-Pilot-Vorschlag unter `test-builds/02995/pilot-proposal` ist ausschließlich eine lokale, nicht veröffentlichte Prüfablage.
- Source-PR #460 ist noch nicht in main. Der .95-PR enthält deshalb auch dessen vollständige Quelländerungen; die isolierte .95-Differenz ist gegen den oben genannten .94-Commit prüfbar.

## Bestätigte Host-Ursachen und Grenzen der Android-Logaussage

Zwei gezielte Regressionen scheiterten unverändert gegen .94: Ein realer SQLite-/WAL-Guide mit echter Sicherung wurde bei künstlich 80 ms verzögertem lokalem Zugriff sowie bei 150 vorangestellten Verzeichniseinträgen als `BACKUP_REQUIRED` abgelehnt. Beide Fälle bestehen mit .95. Zusätzlicher Test: gültiger Beleg hinter 150 anderen Sicherungsbelegen. Dies belegt konkrete fehlerhafte Codepfade; es beweist nicht, welcher davon auf der privaten Android-Box auftrat.

Die .94-Gate-Prüfung verwendete eine gemeinsame 50-ms-Grenze, SQLite-Timeout .05 s und maximal 128 Verzeichniseinträge. Unterschiedliche Fehler wurden pauschal BACKUP_REQUIRED. Die GUI zeigte zuletzt gespeichertes BACKUP_VERIFIED, ohne eine neue unabhängige Autorisierungsprüfung. Ein nachgewiesenes PROFILE_BUSY im EPG-Menü ist ein separater Befund; daraus wird keine unbelegte Kausalität zur Sicherungsfreigabe abgeleitet.

Der Reminder-Worker betrat auch im Leerlauf sekündlich den globalen Profilschreibbereich. Ein kalter Plugin-Aufruf ohne RAM-Snapshot konnte beim parallelen Lesen scheitern. Die frühere Bestandsanzeige verwarf bei einer einzigen fehlgeschlagenen globalen 1-s-Inventur alle historischen READY-Nachweise.

## Implementierung

### Unabhängige Sicherungsfreigabe

`epg_gate95.py`, `epg_gate46.py`, `guide_backup44.py`, `epg_manager53.py`, `owner_dispatch.py`, `ui_jobs86.py`:

1. Guide ausschließlich über SQLite `mode=ro`, query_only und eigene Lesetransaktion prüfen. Schema, gespeicherte Programme und letzter dauerhafter DB-Autorisierungs-SHA werden getrennt festgestellt.
2. Sicherung und Beleg ausschließlich aus demselben Add-on-Profilverzeichnis akzeptieren. Gültiger Beleg, exakter Dateiname, Dateigröße, tatsächlicher SHA256 und gegebenenfalls Quellkonfigurations-SHA müssen übereinstimmen. Symlinks werden nicht als Sicherung akzeptiert.
3. Abschließend aktuelle DB-Autorisierung und Dateiidentität unabhängig erneut lesen. Änderungen während der Prüfung sperren die Freigabe.
4. Verzeichnisprüfung auf 16.384 Einträge und insgesamt 30 s begrenzen; SQLite-Wartezeit .25 s und SQL-Teilbudget 3 s. Manuelle Neuprüfung ist möglich, ohne eine weitere Sicherung anzulegen.
5. Privater Locator ist ausschließlich ein Hinweis auf den früheren Dateinamen. Er ersetzt keinen Beleg, Hash oder DB-Nachweis. Hashcache ist auf 16 Einträge begrenzt und an Device/Inode/Größe/mtime/ctime gebunden. Auch gleich große veränderte Sicherungen werden abgelehnt.
6. BACKUP_VERIFIED beschreibt die vergangene Sicherungsarbeit. IMPORT_AUTHORIZED beschreibt nur eine tatsächlich bestandene unabhängige Gate-Prüfung. Historische GUI-Eigenschaften erteilen keine Freigabe.
7. GUI-Prüfung im vorhandenen Owner-Worker mit ausdrücklich auf 35 s begrenztem Jobbudget; andere Owner-Jobs behalten ihr bisheriges 4-s-Budget. Die Gate-Prüfung respektiert Fensterschließung, Generation und Kodi-Abbruch, damit nach Zurück kein verspäteter Importauftrag entstehen kann. Keine GUI-Verzeichnis-/Hashschleife. Einzelprobe ist single-flight. Eine alte Importanzeige darf einen neueren Gate-Fehler nicht überschreiben.

Diagnose enthält nur Code, Zeitpunkt, Dauer, geprüfte Dateianzahl, Bytezahl, gekürzten SHA und gegebenenfalls numerischen SQLite-Code. Keine privaten Pfade, Konten, Sendernamen oder Quelladressen. Dauerhafte Statusdatei ist eine datensparsame Beobachtung und keine Autorisierungsdatei. Neue Sidecars werden mit 0600 atomar gespeichert; ein Schreibfehler macht einen gültigen vorhandenen Sicherungsnachweis nicht ungültig.

Codes: DB_BUSY, BACKUP_GATE_TIMEOUT, DB_INTERRUPTED, BACKUP_MISSING, BACKUP_RECEIPT_MISMATCH, BACKUP_DIR_UNAVAILABLE, DB_SCHEMA_MISSING, DB_AUTHORIZATION_MISSING, DB_AUTHORIZATION_CHANGED, STORAGE_FULL, STORAGE_ACCESS_DENIED, STORAGE_IO, CANCELLED. Zeitweilige Fehler werden vom Scheduler begrenzt zurückgestellt, auch bei Ablehnung vor dem ersten Importbericht anhand des vorhandenen Refresh-Status; es wird keine neue Sicherung automatisch ausgelöst.

### Profilsperren und Erinnerungen

`reminder_runtime89.py`, `reminder_transaction95.py`, `reminder_bridge89.py`, `reminders.py`, `programme_actions88.py`, `profile_transaction.py`, `portal_snapshot.py`, `portal_proof95.py`, `app_routes.py`:

- Leerlauf-Prüfung des Erinnerungstimers erfolgt lesend. Keine leere Timer-DB und kein Profilschreiblock werden allein durch einen inaktiven Sekundentakt erzeugt.
- Alle Reminder-/Bookmark-Schreiber verwenden dieselbe eigene begrenzte, reentrante flock-Sperre statt den globalen Profilschreiblock. Bestehende Timerzustände, Abbruch, genau eine Benachrichtigung und zwei Dialogaktionen bleiben bestehen.
- Anonyme Warte-/Haltezeiten für globale Profil- und Reminder-Sperre, gedrosselte Meldungen. Wiederholte Fehler werden nicht mit privaten Exception-Texten ausgegeben.
- Kalte Leser warten weiterhin begrenzt auf den normalen Profil-Readlock. Nur bei Busy dürfen sie eine zuvor validierte und unveränderte Portaldatei anhand Dateiidentität und SHA lesen. Kein zweiter Zugangsdatenbestand, kein erfundenes leeres Profil, kein Rückfall auf eine ausgetauschte Dateigeneration.
- Ohne sicheren Snapshot erfolgt ein sauber beendeter Menüaufruf mit Wiederholungshinweis. Bestehende Medien-Resolver-Fehlerbehandlung bleibt erhalten. Widget-Routen bleiben unverändert.

### EPG-Bestandsprüfung und Bestandsschutz

`epg_inventory95.py`, `epg_report53.py`, `stream_epg.py`, `wizard_epg54.py`, `storage_maintenance92.py`:

- Read-only Inventur je Quelle mit PK-Seek-Paginierung in 2.048er-Blöcken. Standard: insgesamt 8 s, pro Quelle 2 s, höchstens 128 Quellen und eine Million geprüfte Zeilen pro Quelle. Unbekannte Mengen sind `None`, keine falsche Null.
- Unveränderte DB-/WAL-Generation wird in einem auf 16 Einträge begrenzten Cache wiederverwendet. Reale Änderungen erzwingen Neuprüfung.
- Aktuelle bestätigte Daten, beschäftigte Inventur, fehlende Tabellen und tatsächlich leere Daten sind getrennt. Historisch verifizierte Counts/Zeiträume werden als historisch ausgewiesen, nicht als frische Inventur ausgegeben.
- Importberichte übernehmen reale Commit-/Cold-Readback-Zähler. Hosttest mit 120.000 Quellzeilen sowie langsamer Einzelquelle.
- Die automatische Wartung fasst den bestehenden Guide und seine Backup-/Manifest-Dateien im .95-Testzyklus nicht an. Kein automatisches Pruning/Checkpointing dieser Daten. Explizit angeforderte Importe dürfen nach bestandener Freigabe weiterhin Daten veröffentlichen; explizit bestätigte Sicherung ist weiterhin eine getrennte Benutzeraktion.
- Verifikations-Tests prüfen DB-, WAL- und Backup-Dateiinhalte. SQLite kann beim normalen Lesen SHM-Lesermarken ändern; daraus wird keine byteidentische SHM-Zusage abgeleitet. SHM wird nicht gelöscht, ersetzt oder manuell verändert.

## Bewusst offen und getrennt

- Physischer DE/AT-Import, langsamer Android-Speicher und tatsächliche Menübedienung: ANDROID_NOT_TESTED.
- Öffentliche EPGShare-Endpunkte werden durch synthetische Quellen nicht als verfügbar zertifiziert. Auf der Testbox ausschließlich DE+AT aktiv, Provider/Kaimandura/CH aus.
- EPG_DB_BUDGET/EPG_DATA_MISSING in Wiedergabe-/Artwork-Pfaden, LOCAL_EVENT-Bilder und RESERVE_BLOCKED sind weiterhin getrennte P1-Arbeiten. Die neue Bestandsinventur beseitigt nicht sämtliche anderen EPG-Lesebudgets.
- Native RK3528-MediaCodec-/Player-Prozessfehler, fremde Skin-/SMB-Fehler sind P2 bzw. getrennte Befunde. Keine unbelegte Hardware-Reparatur.
- Keine Rohlogs veröffentlicht. Keine Sender-, Portal-, Token-, Mapping-, Favoriten- oder SkinShortcuts-Migration.

## Testvertrag und Paket

Reproduzierbarer Builder `tools/release_candidate95.py`; source-genaues ZIP, CRC, vollständige Mitgliederliste, jede Member-SHA und Rebuild-Bytegleichheit. Neue Delta-Fixture akzeptiert nur exakt geprüfte .95-Bytes; beliebige Änderungen passieren historische Scope-Gates nicht. Historische .94-Tests prüfen weiterhin die unveränderten .94-Artefakte in ihrem ursprünglichen Kontext. Entfernte alte Test-ZIPs werden ausschließlich in einem Wegwerf-Testclone aus unveränderlicher Git-Historie byteverifiziert bereitgestellt.

Vollständige Ergebnisse, Commit und CI-Links stehen im Testbericht dieses Verzeichnisses. Installations- und Geräteplan: `ANDROID_ABNAHME_DE.md`.
