# 0.1.29.11 – Artwork-Status und SQLite-Konkurrenz (#75/#69)

Basis: main 9cc4211, produktiv und auf Android abgenommen: 0.1.29.8.
Diese Navigation/Owner-Steuerung bleibt unverändert. Keine Übernahme von
Speicherprofilen/Migration aus #78; keine Änderung von settings.xml, Budgets,
Cachepfaden, Accounts, Coverdateien oder bestehenden Datenbanken durch Tests.

## Ursache und Evidenz

Das neue private kodi(4).log belegt art_status DISPATCH_FAILED/START_FAILED
error=OTHER um 01:17:43 sowie 233 Artwork-DB-Warnungen, davon 198 SQLITE_BUSY.
Dies beweist Konkurrenz, keine Korruption und noch nicht die exakte Exception
dieses einzelnen Android-Aufrufs. Der Codepfad status→used konnte jedoch eine
schreibende Adoption alter Bilder mit weiterem Connect auslösen. Neue Plugin-
Interpreter initialisierten außerdem eine bereits vollständige SQLite-Struktur
per BEGIN IMMEDIATE. run_one nahm selbst bei leerer Queue eine Schreibsperre.
Diese konkreten Konkurrenzpfade sind mit echten SQLite-Sperren reproduziert.

## Änderung

Status benutzt einen einzelnen strikt lesenden Snapshot (mode=ro, query_only,
25-ms-BUSY-Timeout, 150-ms-SQL-Limit), ohne Adoption, Schemaanlage oder Reparatur.
Er läuft hinter einem sofort sichtbaren nativen Fortschrittsdialog im Worker,
mit höchstens einer kurzen 40-ms-Wiederholung. Budget, physische Kapazität und
letzter DB-Prüfstand bleiben unabhängig von der Statistik. BUSY/fehlende DB/
Korruption erscheinen als Teilstatus; keine Zahlen als erfolgreich gelesen
ausgeben, wenn sie unbekannt sind. Queue-Bytes schließen nicht registrierte
Altbilder ausdrücklich nicht ein. Kein neues Kapazitäts-/Speicherprofil.

Vollständige vorhandene Schemas werden nur gelesen; leere/anderweitig belegte
Queues brauchen keine Schreibtransaktion. Alte Adoption ermittelt neue Dateien
außerhalb der Schreibtransaktion und fügt nur fehlende IDs in kleinen Batches
ein. Transiente Completion-BUSY-Fehler lassen Dateien und endlichen Job-Lease
bestehen, statt Netzwerkversuche zu verbrauchen. BUSY-Warnungen werden im
vorhandenen privaten Health-Snapshot minutenweise gedrosselt; eine bestandene
Integritätsprüfung bleibt als eigener letzter Prüfstand erhalten und wird wegen
BUSY nicht ständig neu gestartet. Kein WAL-/Journalmoduswechsel eingeführt.

Die Boot-Diagnose kennt ArtworkDBUnavailable und SQLite-Fehlerklassen sowie
ART_STATUS_COUNTS_FAILED. Nur feste Klassen/Phasen, keine SQL-Texte/URLs/Tokens.
Legacy action=settings beendet ein positives Directory-Handle erfolgreich vor
openSettings; native Settings-Links sind Action-Items. Negative Handles enden
weiterhin kein Directory. Echte Fehlerpfade werden nicht pauschal erfolgreich.

## Android-Test – NOT_RUN

1. Nur dieses Test-ZIP auf der bestätigten 0.1.29.8-Basis installieren. Bestehendes
   Profil sichern; keine Portale neu importieren, kein Cache-/Queue-Reset.
2. Bei aktivem Hintergrunddienst 10× Bildspeicherstatus öffnen, mit Back schließen.
   Stets lesbarer Dialog, bei BUSY verständlicher Teilstatus, Budget sichtbar.
3. artwork_db_health, recording_capabilities, appearance_settings jeweils öffnen
   und schließen. Legacy Einstellungen aus mehreren Abschnitten öffnen, Back.
4. Keine neuen START_FAILED für art_status, keine GetDirectory(action=settings),
   keine Warnflut. Fehlerphase/-klasse prüfen, keine Korruption aus BUSY ableiten.
5. Filme/Serien je 10×, schnelles Doppel-Back, EPG und Live-TV wie 0.1.29.8 prüfen.
6. Cover/Jobs/Favoriten/Resume und Accounts bleiben erhalten. art_retry nicht
   unkontrolliert ausführen: altes 512-MiB-Budget und große Queue bleiben bestehen.

Kein Merge/Release. Bei Regression auf unverändertes 0.1.29.8 zurückfallen.
