# XCMate .71 – Testbericht / Abnahmematrix #352

Basis main bcfe131becdaec86ba0d9880cc67ca8d524c5a4f. 681 vorherige Add-on-Dateien und 2868 vorhandene Host-Testmethoden bleiben durch Inventar und exakte Audit-Deltas geschützt. Keine Alt-Tests entfernt und keine neuen Skip-Bedingungen. Vier reine Versionsassertionen folgen der neuen Manifestversion .71.

## Reproduktionen und technische Prüfung

- Native Owner-Modell: eine Anmeldung, drei Kategorienabfragen, wiederholtes onInit erzeugt keinen zusätzlichen Discovery-Job. Tatsächlicher belegter Slot wird gezielt als BUSY gemeldet.
- Checkpointfehler nach Gruppenabfrage: lokales ENOSPC wird als Checkpoint-/Speicherfehler ausgegeben, nicht pauschal als Provider-Netzwerkfehler. Retry behält Eingaben und Auswahl.
- Simuliertes Android-App-Dateisystem mit nicht unterstütztem chmod/fchmod: echte Checkpoint- und Katalog-/Save-Writer erreichen den vollständigen Owner-Ablauf und Readback. Plattformklassifizierung, UID-/Pfadgrenzen und Symlink-/Fremdpfad-Abweisung sind separat getestet. **Kein Android-Hardware-PASS.**
- Echte Konfigurationsdateien und SQLite-Katalog: Startgruppe, Gruppen aller Arten und Zugang unverändert in einem unabhängigen Python-Prozess lesbar.
- Drei Speicherversuche veröffentlichen dieselbe neue Portal-ID genau einmal. Bestehendes Portal und Daten bleiben unverändert.
- Erzwungener Gruppenfehler und realer SQLite-Writer-Lock: kein erfolgreicher Save, kein Verlust des bestehenden Profils; Wiederholung nach behobenem Fehler möglich.
- Backups mit vollständigem Datei-Readback, Länge und SHA256, keine automatische Rücksicherung. Keine Providerdaten im Testreport; ausschließlich synthetische Testdaten.
- Legacy: drei Einstellungen werden mit einem atomaren Portallisten-Write übernommen. Ein Fehler nach Veröffentlichung macht keine weiteren Slots dauerhaft unsichtbar; wiederholter Import bei bestehenden Portalen schreibt nichts.
- Verzeichnis-/Aktionsvertrag: kein Container.Refresh des Importhandlers; positive Handles rendern ein Ergebnisverzeichnis, negative Handles erzeugen keinen endOfDirectory(-1)-Aufruf.
- Diagnosen geben errno, anonymen Sitzungscode und sichere Stackpositionen aus; keine Exceptiontexte, Provider-URLs, Passwort-/Tokeninhalte oder private Pfade.
- Speicherprobe entfernt ausschließlich ihre eigenen Testdateien; Datenbankprüfung read-only.
- GS-Media .5.19 enthält setup_catalog_0516. Reproduzierbarer .5.20-Build überprüft Importabschluss; alle Installerdateien außer Manifest/Service bleiben bytegleich, eine neue Readiness-Hilfe wird ergänzt. Fremde Skinwahl/Abort dürfen keinen BINGIE-PASS erzeugen.

## Finale Ergebnisse

Die vollständige Host-/Kodi-Regressionsserie bleibt verpflichtendes GitHub-CI-Gate. Der endgültige Commit, Testanzahl, Laufzeit, SHA256 und native Belege stehen im finalen PR und build-verification.json des Testartefakts. Vor dessen erfolgreicher Erzeugung wird kein vollständiger CI-PASS behauptet.

Lokal bestanden: 124 kombinierte neue/alte Setup-, Resume-, EPG- und Boot-Prüfungen sowie 94 kumulative Scope-/Bestandsschutzprüfungen. Die fokussierten .71-Prüfungen werden nach den letzten Zusatzfällen erneut ausgeführt; die finale Gesamtzahl kommt aus CI. Die historische Boot-Testmethode bleibt erhalten, ihre frühere Assertion „leeres Verzeichnis vor Migration beendet“ wurde auf den korrigierten Vertrag geändert: vor Migration kein Abschluss, danach genau ein Ergebnisabschluss und kein START_FAILED. Die zusätzlichen Tests starten den echten Entry-Dispatcher dreimal; kein Self-Refresh und unverändertes vorhandenes Portal.

Android-Prüfungen und reale Provider-/TX60Pro-Dateisystemwerte bleiben ohne Geräteversuch NOT_TESTED.

Die breite GUI-Regression erkannte zunächst einen neuen direkten Dialog.select-Aufruf im Startgruppen-Dialog. Dieser verwendet jetzt die bestehende menu_icons45-Komponente; die ursprüngliche Menüprüfung bleibt unverändert. Danach bestanden lokal 43 kombinierte Setup-/Legacy-/Menüprüfungen. Der finale vollständige CI-Lauf muss weiterhin grün sein.

Der erste vollständige .71-Lauf führte 2904 Tests aus und traf auf einen alten Branding-Test, der die Methode _root über ihre exakte Textsignatur suchte. Der neue optionale Legacy-Parameter machte diese Extraktion ungültig. Der Test liest jetzt denselben Methodenkörper per AST; die Autoplay-/EPG-/Startfehler-Assertions bleiben bestehen. Eine getrennte Kodi-Modellprüfung traf einmal auf ein fehlendes xbmcvfs-Testmodul; die exakt gleiche Gruppe mit 197 Tests bestand lokal ohne Änderung am Produktcode (mit Freigabe des lokalen HTTP-Testservers). Dieser Vorfall und die abschließende Wiederholung bleiben im CI-Verlauf nachvollziehbar.

| Anforderung | Umsetzung / Prüfstatus | Offene Geräteabnahme |
|---|---|---|
| Discovery-OSError / Checkpoint | Reproduzierte Speicher-Fehlerkette behoben; Fehlerklassen, Schutz vor zweitem Job, Retry-Daten erhalten | konkreter Geräte-errno und Backend NOT_TESTED |
| Gruppen / Startgruppe | explizite Wahl, Sicherung, Portal-Gate und frischer Prozess-Readback | Kodi-Neustart auf TX60Pro NOT_TESTED |
| Legacy-Loop / Directory | Self-Refresh entfernt; atomarer Batch, idempotente Wiederholung | Kodi-Menüablauf Android NOT_TESTED |
| GS-Media-Importmodul | .5.19 bereits vollständig; AST-Paketprüfung ergänzt | tatsächliche installierte Paketdateien NOT_TESTED |
| BINGIE-Postboot | getrenntes .5.20-Begleitupdate; stabile GUI abwarten, Skin nicht verändern | tatsächlicher Android-Boot NOT_TESTED |
| 48 Komponenten / Kodi / EPG / TMDB | kein Installer-Rerun, keine Skin-/Keymapänderungen, bestehende Dateien geschützt | vollständiger Gerätebestand NOT_TESTED |
| guisettings.xml / fremde Permission-Fehler | keine behauptete DB-Korruption; keine Root-/Partitionsreparatur | bei erneutem Auftreten separat diagnostizieren |

Kein automatischer Merge, Release, Repository-Index-Update oder Eingriff auf dem Gerät. Kein Schließen von Issue #352 vor tatsächlicher Geräteabnahme.
